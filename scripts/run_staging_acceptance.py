#!/usr/bin/env python3
"""Run guarded Church/Basketball acceptance against an authorized staging origin."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import secrets
import socket
import ssl
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit, urlunsplit

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from scripts.local_tls_rehearsal import verify_cookie_security
from tests.playbooks.registry import BUILTIN_DIRECTORY, PlaybookSpec, discover_playbooks
from tests.playbooks.runtime import Playbook
from tests.playbooks.workflows import run_six_week_roster

ROOT = Path(__file__).resolve().parents[1]
SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")
REQUIRED_BROWSER_HEADERS = {
    "content-security-policy",
    "strict-transport-security",
    "x-content-type-options",
    "x-frame-options",
}


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def validate_staging_target(
    value: str,
    *,
    allow_authorized_remote: bool = False,
) -> str:
    """Require an origin-only URL and an explicit opt-in for remote traffic."""
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Staging target must be an HTTP(S) origin")
    if parsed.username or parsed.password:
        raise ValueError("Staging target must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Staging target must be an origin only")

    loopback = _is_loopback(parsed.hostname)
    if parsed.scheme != "https":
        raise ValueError("Staging targets must use HTTPS")
    if not loopback and not allow_authorized_remote:
        raise ValueError("Remote staging requires explicit authorization")
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


def validate_approval_reference(value: str) -> str:
    """Require a bounded HTTPS receipt rather than an ambiguous approval word."""
    value = value.strip()
    parsed = urlsplit(value)
    if (
        not value
        or len(value) > 500
        or parsed.scheme != "https"
        or not parsed.hostname
        or parsed.path in {"", "/"}
    ):
        raise ValueError("A specific HTTPS approval reference is required")
    return value


def _validate_release_sha(value: str) -> str:
    if not SHA_PATTERN.fullmatch(value):
        raise ValueError("Expected release SHA must be an exact lowercase 40-character Git SHA")
    return value


def _run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _tracked_source_identity() -> tuple[str, bool]:
    source_sha = _validate_release_sha(_run_git("rev-parse", "HEAD"))
    clean = not bool(_run_git("status", "--porcelain", "--untracked-files=no"))
    return source_sha, clean


def _require_release_header(response: httpx.Response, expected_release_sha: str) -> None:
    observed = response.headers.get("X-Release-SHA", "")
    if observed != expected_release_sha:
        raise RuntimeError(
            "Target release identity mismatch: "
            f"expected {expected_release_sha}, observed {observed or 'missing'}"
        )


def verify_target_identity(
    client: httpx.Client,
    expected_release_sha: str,
) -> dict[str, Any]:
    """Fail before data writes unless liveness, readiness and source identity agree."""
    expected_release_sha = _validate_release_sha(expected_release_sha)
    health = client.get("/health")
    if health.status_code != 200:
        raise RuntimeError(f"Target health returned HTTP {health.status_code}")
    _require_release_header(health, expected_release_sha)

    ready = client.get("/ready")
    if ready.status_code != 200:
        raise RuntimeError(f"Target readiness returned HTTP {ready.status_code}")
    _require_release_header(ready, expected_release_sha)
    return {
        "health_status": health.status_code,
        "readiness_status": ready.status_code,
        "observed_release_sha": expected_release_sha,
    }


def verify_browser_session(
    client: httpx.Client,
    *,
    email: str,
    password: str,
    expected_release_sha: str,
) -> dict[str, Any]:
    """Verify production browser-cookie and security-header behavior."""
    login_form = client.get("/auth/login")
    if login_form.status_code != 200:
        raise RuntimeError(f"Browser login form returned HTTP {login_form.status_code}")
    _require_release_header(login_form, expected_release_sha)
    csrf_cookie = verify_cookie_security(
        login_form.headers.get_list("set-cookie"),
        "signupflow_csrf",
        http_only=False,
    )
    csrf_token = client.cookies.get("signupflow_csrf")
    if not csrf_token:
        raise RuntimeError("Browser login did not retain the CSRF cookie")

    origin = str(client.base_url).rstrip("/")
    login = client.post(
        "/auth/login",
        data={"email": email, "password": password, "csrf_token": csrf_token},
        headers={"Origin": origin},
    )
    if login.status_code != 303 or login.headers.get("location") != "/a/dashboard":
        raise RuntimeError(f"Browser login returned HTTP {login.status_code}")
    _require_release_header(login, expected_release_sha)
    session_cookie = verify_cookie_security(
        login.headers.get_list("set-cookie"),
        "signupflow_session",
        http_only=True,
    )

    dashboard = client.get("/a/dashboard")
    if dashboard.status_code != 200:
        raise RuntimeError(f"Authenticated dashboard returned HTTP {dashboard.status_code}")
    _require_release_header(dashboard, expected_release_sha)
    missing_headers = sorted(REQUIRED_BROWSER_HEADERS - set(dashboard.headers))
    if missing_headers:
        raise RuntimeError(f"Dashboard is missing security headers: {', '.join(missing_headers)}")
    return {
        "login_form_status": login_form.status_code,
        "login_status": login.status_code,
        "dashboard_status": dashboard.status_code,
        "csrf_cookie": csrf_cookie,
        "session_cookie": session_cookie,
        "security_headers": sorted(REQUIRED_BROWSER_HEADERS),
    }


def _inspect_tls(origin: str, *, ca_file: Path | None, timeout: float) -> dict[str, Any]:
    parsed = urlsplit(origin)
    if parsed.scheme != "https" or not parsed.hostname:
        return {"status": "not_applicable", "reason": "loopback HTTP target"}
    context = ssl.create_default_context(cafile=str(ca_file) if ca_file else None)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    with socket.create_connection((parsed.hostname, parsed.port or 443), timeout=timeout) as raw:
        with context.wrap_socket(raw, server_hostname=parsed.hostname) as wrapped:
            certificate_bytes = wrapped.getpeercert(binary_form=True)
            if certificate_bytes is None:
                raise RuntimeError("TLS peer did not provide a certificate")
            certificate = x509.load_der_x509_certificate(certificate_bytes)
            cipher = wrapped.cipher()
            return {
                "status": "verified",
                "protocol": wrapped.version(),
                "cipher": cipher[0] if cipher else None,
                "certificate_sha256": certificate.fingerprint(hashes.SHA256()).hex(),
                "certificate_not_after": certificate.not_valid_after_utc.isoformat(),
            }


def _select_playbooks(
    directories: list[Path],
    selected_ids: list[str],
) -> list[PlaybookSpec]:
    specs = discover_playbooks(directories)
    if not selected_ids:
        return specs
    requested = set(selected_ids)
    available = {spec.id for spec in specs}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(f"Unknown playbook IDs: {', '.join(unknown)}")
    return [spec for spec in specs if spec.id in requested]


def _run_playbooks(
    client: httpx.Client,
    specs: list[PlaybookSpec],
) -> tuple[list[dict[str, Any]], Playbook]:
    results: list[dict[str, Any]] = []
    first: Playbook | None = None
    workflow_runner = cast(Callable[..., Playbook], run_six_week_roster)
    for spec in specs:
        password = f"Aa1!{secrets.token_urlsafe(36)}"
        playbook = workflow_runner(client, spec, password=password)
        first = first or playbook
        results.append(
            {
                "id": spec.id,
                "organization_id": playbook.org,
                "people_created": len(playbook.people),
                "events_created": len(playbook.events),
                "workflow": spec.workflow,
                "outcome": "passed",
            }
        )
    if first is None:
        raise RuntimeError("No staging playbooks were selected")
    return results, first


def _write_report(run_dir: Path, report: dict[str, Any]) -> Path:
    path = run_dir / "report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url")
    parser.add_argument("--expected-release-sha")
    parser.add_argument("--approval-reference")
    parser.add_argument("--allow-authorized-remote", action="store_true")
    parser.add_argument("--ca-file", type=Path)
    parser.add_argument("--playbook", action="append", default=[])
    parser.add_argument("--playbook-dir", action="append", type=Path, default=[])
    parser.add_argument("--request-timeout", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.dry_run:
        print(
            "Staging acceptance is opt-in. Remote execution requires an HTTPS origin, "
            "exact deployed SHA, specific approval reference, and --allow-authorized-remote."
        )
        return 0
    if not args.base_url or not args.expected_release_sha or not args.approval_reference:
        parser.error("--base-url, --expected-release-sha, and --approval-reference are required")
    try:
        base_url = validate_staging_target(
            args.base_url,
            allow_authorized_remote=args.allow_authorized_remote,
        )
        expected_release_sha = _validate_release_sha(args.expected_release_sha)
        approval_reference = validate_approval_reference(args.approval_reference)
        if args.request_timeout <= 0 or args.request_timeout > 120:
            raise ValueError("--request-timeout must be greater than zero and at most 120")
        if args.ca_file and not args.ca_file.is_file():
            raise ValueError("--ca-file must identify a readable certificate file")
    except ValueError as exc:
        parser.error(str(exc))

    started_at = datetime.now(UTC)
    run_id = secrets.token_hex(4)
    run_dir = (
        ROOT
        / "test-artifacts"
        / "staging-validation"
        / f"{started_at.strftime('%Y%m%dT%H%M%S.%fZ')}-{run_id}"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "outcome": "failed",
        "target": {
            "base_url": base_url,
            "expected_release_sha": expected_release_sha,
            "approval_reference": approval_reference,
        },
        "external_providers": (
            "not configured or contacted by this runner; deployment configuration "
            "must keep them disabled"
        ),
    }
    exit_code = 1
    try:
        source_sha, tracked_tree_clean = _tracked_source_identity()
        if not tracked_tree_clean:
            raise RuntimeError("Commit tracked changes before running staging acceptance")
        specs = _select_playbooks(
            [BUILTIN_DIRECTORY, *args.playbook_dir],
            args.playbook,
        )
        tls = _inspect_tls(base_url, ca_file=args.ca_file, timeout=args.request_timeout)
        verify: bool | str = str(args.ca_file) if args.ca_file else True
        with httpx.Client(
            base_url=base_url,
            timeout=args.request_timeout,
            follow_redirects=False,
            trust_env=False,
            verify=verify,
        ) as client:
            identity = verify_target_identity(client, expected_release_sha)
            playbooks, first = _run_playbooks(client, specs)
            browser = verify_browser_session(
                client,
                email=first.email,
                password=first.password,
                expected_release_sha=expected_release_sha,
            )
        report.update(
            {
                "harness_source_sha": source_sha,
                "tracked_tree_clean": tracked_tree_clean,
                "tls": tls,
                "identity": identity,
                "playbooks": playbooks,
                "browser": browser,
                "outcome": "passed",
            }
        )
        exit_code = 0
    except (
        AssertionError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
        httpx.HTTPError,
        ssl.SSLError,
    ) as exc:
        report["error"] = {
            "type": type(exc).__name__,
            "message": "Staging acceptance failed; inspect correlated target logs",
        }
        print(f"Staging acceptance failed: {type(exc).__name__}", file=sys.stderr)
    finally:
        report["finished_at"] = datetime.now(UTC).isoformat()
        report_path = _write_report(run_dir, report)
        print(f"Staging acceptance report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
