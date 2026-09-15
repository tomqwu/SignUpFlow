#!/usr/bin/env python3
"""Run source and exact-image security validation with a pinned Trivy container."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "test-artifacts" / "security-validation"
SCANNER_IMAGE = (
    "ghcr.io/aquasecurity/trivy@"
    "sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969"
)
SCANNER_VERSION = "0.74.0"
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
BLOCKING_SEVERITIES = {"HIGH", "CRITICAL"}
INVENTORY_PATHS = (
    ".dockerignore",
    "Dockerfile",
    "Dockerfile.dev",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    "pyproject.toml",
    "poetry.lock",
    "mobile/pubspec.yaml",
    "mobile/pubspec.lock",
    "mobile/Gemfile",
    "mobile/Gemfile.lock",
    "mobile/ios/Podfile",
    "mobile/ios/Podfile.lock",
    "mobile/android/settings.gradle.kts",
    "mobile/android/build.gradle.kts",
    "mobile/android/app/build.gradle.kts",
    "mobile/android/gradle/wrapper/gradle-wrapper.properties",
    "web/static/js/alpine.min.js",
    "web/static/js/htmx.min.js",
    ".github/workflows/pages.yml",
    "security/trivy-secret.yaml",
)


class SecurityValidationError(RuntimeError):
    """Raised when local security evidence cannot be trusted or accepted."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory_inputs(root: Path) -> dict[str, dict[str, Any]]:
    """Hash every declared dependency, artifact, vendored, and workflow input."""
    inventory: dict[str, dict[str, Any]] = {}
    for relative in INVENTORY_PATHS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise SecurityValidationError(f"Required security input is missing: {relative}")
        inventory[relative] = {"sha256": _sha256(path), "bytes": path.stat().st_size}
    return inventory


def validate_exceptions(
    payload: dict[str, Any], *, now: datetime | None = None
) -> list[dict[str, Any]]:
    """Validate exact, owned, expiring exception records."""
    if payload.get("schema_version") != 1 or not isinstance(payload.get("exceptions"), list):
        raise SecurityValidationError("Security exception ledger has an unsupported schema")
    current = now or datetime.now(UTC)
    required = {"id", "finding_key", "owner", "rationale", "mitigation", "expires_at"}
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_keys: set[str] = set()
    for record in payload["exceptions"]:
        if not isinstance(record, dict) or required - record.keys():
            raise SecurityValidationError("Every security exception requires all policy fields")
        if not all(isinstance(record[key], str) and record[key].strip() for key in required):
            raise SecurityValidationError("Security exception fields must be non-empty strings")
        if record["id"] in seen_ids or record["finding_key"] in seen_keys:
            raise SecurityValidationError("Security exception IDs and finding keys must be unique")
        if not DATE_PATTERN.fullmatch(record["expires_at"]):
            raise SecurityValidationError("Security exception expiry must be YYYY-MM-DD")
        try:
            expiry = datetime.fromisoformat(record["expires_at"]).replace(tzinfo=UTC)
        except ValueError as exc:
            raise SecurityValidationError("Security exception expiry must be YYYY-MM-DD") from exc
        if expiry.date() < current.date():
            raise SecurityValidationError(f"Security exception {record['id']} is expired")
        seen_ids.add(record["id"])
        seen_keys.add(record["finding_key"])
        result.append(dict(record))
    return result


def _finding_key(
    scope: str,
    target: str,
    kind: str,
    finding_id: str,
    package_name: str,
    installed_version: str,
) -> str:
    return "|".join(
        (scope, target, kind, finding_id, package_name or "-", installed_version or "-")
    )


def sanitize_trivy_report(raw: dict[str, Any], *, scope: str) -> list[dict[str, Any]]:
    """Keep finding identity and remediation data while dropping matched source content."""
    findings: list[dict[str, Any]] = []
    for result in raw.get("Results") or []:
        target = str(result.get("Target") or "unknown")
        for item in result.get("Vulnerabilities") or []:
            finding_id = str(item.get("VulnerabilityID") or "unknown")
            package_name = str(item.get("PkgName") or "")
            installed = str(item.get("InstalledVersion") or "")
            severity = str(item.get("Severity") or "UNKNOWN").upper()
            findings.append(
                {
                    "key": _finding_key(
                        scope, target, "vulnerability", finding_id, package_name, installed
                    ),
                    "scope": scope,
                    "target": target,
                    "kind": "vulnerability",
                    "finding_id": finding_id,
                    "package_name": package_name,
                    "installed_version": installed,
                    "fixed_version": str(item.get("FixedVersion") or ""),
                    "severity": severity,
                    "status": str(item.get("Status") or "unknown"),
                    "primary_url": str(item.get("PrimaryURL") or ""),
                    "blocking": scope == "image" and severity in BLOCKING_SEVERITIES,
                }
            )
        for item in result.get("Secrets") or []:
            finding_id = str(item.get("RuleID") or "unknown")
            severity = str(item.get("Severity") or "UNKNOWN").upper()
            findings.append(
                {
                    "key": _finding_key(scope, target, "secret", finding_id, "", ""),
                    "scope": scope,
                    "target": target,
                    "kind": "secret",
                    "finding_id": finding_id,
                    "category": str(item.get("Category") or "unknown"),
                    "severity": severity,
                    "blocking": True,
                }
            )
        for item in result.get("Misconfigurations") or []:
            finding_id = str(item.get("ID") or "unknown")
            severity = str(item.get("Severity") or "UNKNOWN").upper()
            findings.append(
                {
                    "key": _finding_key(scope, target, "misconfiguration", finding_id, "", ""),
                    "scope": scope,
                    "target": target,
                    "kind": "misconfiguration",
                    "finding_id": finding_id,
                    "title": str(item.get("Title") or ""),
                    "severity": severity,
                    "resolution": str(item.get("Resolution") or ""),
                    "primary_url": str(item.get("PrimaryURL") or ""),
                    "blocking": severity in BLOCKING_SEVERITIES,
                }
            )
    return sorted(findings, key=lambda item: item["key"])


def apply_exceptions(
    findings: list[dict[str, Any]], exceptions: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply exact finding exceptions and return accepted and still-blocking findings."""
    by_key = {record["finding_key"]: record["id"] for record in exceptions}
    accepted: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for finding in findings:
        exception_id = by_key.get(finding["key"])
        if exception_id:
            accepted.append({**finding, "exception_id": exception_id, "blocking": False})
        elif finding.get("blocking"):
            blocked.append(finding)
    unused = sorted(set(by_key) - {finding["key"] for finding in findings})
    if unused:
        raise SecurityValidationError("Exception ledger contains findings absent from this scan")
    return accepted, blocked


def component_names(sbom: dict[str, Any]) -> set[str]:
    """Return stable package name/version identities from a CycloneDX document."""
    return {
        f"{component.get('name', 'unknown')}@{component.get('version', 'unknown')}"
        for component in sbom.get("components") or []
        if isinstance(component, dict)
    }


def license_inventory(sbom: dict[str, Any]) -> list[dict[str, Any]]:
    """Return reviewable component licenses without guessing missing declarations."""
    inventory: list[dict[str, Any]] = []
    for component in sbom.get("components") or []:
        if not isinstance(component, dict):
            continue
        licenses: set[str] = set()
        for record in component.get("licenses") or []:
            if not isinstance(record, dict):
                continue
            expression = record.get("expression")
            if isinstance(expression, str) and expression.strip():
                licenses.add(expression.strip())
            license_record = record.get("license")
            if isinstance(license_record, dict):
                identifier = license_record.get("id") or license_record.get("name")
                if isinstance(identifier, str) and identifier.strip():
                    licenses.add(identifier.strip())
        inventory.append(
            {
                "component": (
                    f"{component.get('name', 'unknown')}@{component.get('version', 'unknown')}"
                ),
                "licenses": sorted(licenses) or ["UNKNOWN"],
            }
        )
    return sorted(inventory, key=lambda item: item["component"])


def _run(
    command: list[str], *, check: bool = True, timeout: float = 900
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env={
            "HOME": os.environ.get("HOME", ""),
            "PATH": os.environ.get("PATH", ""),
            "DOCKER_HOST": os.environ.get("DOCKER_HOST", ""),
        },
    )
    if check and result.returncode != 0:
        operation = " ".join(command[:3])
        raise SecurityValidationError(f"{operation} failed with exit code {result.returncode}")
    return result


def _source_sha() -> str:
    source_sha = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    if not SHA_PATTERN.fullmatch(source_sha):
        raise SecurityValidationError("Git HEAD is not a full commit SHA")
    dirty = _run(["git", "status", "--porcelain", "--untracked-files=no"]).stdout.strip()
    if dirty:
        raise SecurityValidationError("Commit tracked changes before security validation")
    return source_sha


def _docker_base(*, network: bool, mounts: list[tuple[Path, str, bool]]) -> list[str]:
    command = ["docker", "run", "--rm", "--cap-drop", "ALL", "--security-opt", "no-new-privileges"]
    if not network:
        command.extend(["--network", "none"])
    for source, target, read_only in mounts:
        mount = f"type=bind,source={source.resolve()},target={target}"
        if read_only:
            mount += ",readonly"
        command.extend(["--mount", mount])
    command.extend([SCANNER_IMAGE, "--cache-dir", "/cache"])
    return command


def _ensure_scanner() -> dict[str, Any]:
    inspect = _run(["docker", "image", "inspect", SCANNER_IMAGE], check=False)
    if inspect.returncode != 0:
        raise SecurityValidationError(
            f"Pinned scanner is unavailable; pull exactly {SCANNER_IMAGE}"
        )
    version = _run(["docker", "run", "--rm", "--network", "none", SCANNER_IMAGE, "--version"])
    if f"Version: {SCANNER_VERSION}" not in version.stdout:
        raise SecurityValidationError("Pinned scanner returned an unexpected version")
    records = json.loads(inspect.stdout)
    return {
        "name": "Trivy",
        "version": SCANNER_VERSION,
        "image": SCANNER_IMAGE,
        "image_id": records[0].get("Id"),
    }


def _prepare_database(cache_dir: Path) -> dict[str, Any]:
    command = _docker_base(network=True, mounts=[(cache_dir, "/cache", False)])
    command.extend(["image", "--download-db-only"])
    _run(command)
    version_command = _docker_base(network=False, mounts=[(cache_dir, "/cache", False)])
    version_command.extend(["--version", "--format", "json"])
    version_payload = json.loads(_run(version_command).stdout)
    database = version_payload.get("VulnerabilityDB")
    if not isinstance(database, dict) or not database.get("UpdatedAt"):
        raise SecurityValidationError("Scanner advisory database is unavailable after download")
    files = {
        str(path.relative_to(cache_dir)): {"sha256": _sha256(path), "bytes": path.stat().st_size}
        for path in sorted(cache_dir.rglob("*"))
        if path.is_file()
    }
    if not files:
        raise SecurityValidationError("Scanner advisory cache is empty after download")
    return {"metadata": database, "files": files}


def _scan_json(command: list[str]) -> dict[str, Any]:
    result = _run(command, check=False)
    if result.returncode != 0:
        raise SecurityValidationError(f"Scanner failed with exit code {result.returncode}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SecurityValidationError("Scanner did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise SecurityValidationError("Scanner returned an unexpected JSON document")
    return payload


def _fixture_drills(work_dir: Path, cache_dir: Path, secret_config: Path) -> dict[str, Any]:
    fixture_dir = work_dir / "fixture"
    fixture_dir.mkdir(mode=0o700)
    fake_secret = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    secret_file = fixture_dir / "generated-synthetic-credential.env"
    secret_file.write_text(f"token={fake_secret}\n", encoding="utf-8")
    command = _docker_base(
        network=False,
        mounts=[
            (fixture_dir, "/fixture", True),
            (cache_dir, "/cache", False),
            (secret_config, "/policy/trivy-secret.yaml", True),
        ],
    )
    command.extend(
        [
            "filesystem",
            "--quiet",
            "--scanners",
            "secret",
            "--secret-config",
            "/policy/trivy-secret.yaml",
            "--exit-code",
            "23",
            "--format",
            "json",
            "/fixture",
        ]
    )
    detected = _run(command, check=False)
    try:
        detected_payload = json.loads(detected.stdout)
    except json.JSONDecodeError as exc:
        raise SecurityValidationError("Secret fixture scan returned invalid JSON") from exc
    detected_findings = sanitize_trivy_report(detected_payload, scope="fixture")
    if detected.returncode != 23 or not detected_findings:
        raise SecurityValidationError("Known harmless secret fixture did not fail the scanner")
    secret_file.unlink()
    clean = _run(command, check=False)
    clean_payload = json.loads(clean.stdout)
    if clean.returncode != 0 or sanitize_trivy_report(clean_payload, scope="fixture"):
        raise SecurityValidationError("Removed secret fixture did not produce a clean result")

    empty_cache = work_dir / "empty-cache"
    empty_cache.mkdir(mode=0o700)
    missing_db = _docker_base(
        network=False,
        mounts=[(fixture_dir, "/fixture", True), (empty_cache, "/cache", False)],
    )
    missing_db.extend(
        ["filesystem", "--quiet", "--scanners", "vuln", "--skip-db-update", "/fixture"]
    )
    missing = _run(missing_db, check=False)
    if missing.returncode == 0:
        raise SecurityValidationError(
            "Missing advisory database was incorrectly reported successful"
        )
    return {
        "known_secret": {"failed_as_expected": True, "finding_count": len(detected_findings)},
        "removed_secret": {"passed": True, "finding_count": 0},
        "missing_database": {"blocked_as_expected": True, "exit_code": missing.returncode},
    }


def _extract_committed_source(destination: Path) -> None:
    archive = destination.parent / "source.tar"
    with archive.open("wb") as stream:
        result = subprocess.run(
            ["git", "archive", "--format=tar", "HEAD"],
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.PIPE,
            check=False,
        )
    if result.returncode != 0:
        raise SecurityValidationError("git archive failed")
    destination.mkdir(mode=0o700)
    with tarfile.open(archive) as bundle:
        if any(member.issym() or member.islnk() for member in bundle.getmembers()):
            raise SecurityValidationError("Committed source archive contains links")
        bundle.extractall(destination, filter="data")
    archive.unlink()


def _source_scans(source_dir: Path, cache_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mounts = [(source_dir, "/source", True), (cache_dir, "/cache", False)]
    vulnerability = _docker_base(network=False, mounts=mounts)
    vulnerability.extend(
        [
            "filesystem",
            "--quiet",
            "--scanners",
            "vuln",
            "--skip-db-update",
            "--format",
            "json",
            "/source",
        ]
    )
    secret = _docker_base(network=False, mounts=mounts)
    secret.extend(
        [
            "filesystem",
            "--quiet",
            "--scanners",
            "secret",
            "--secret-config",
            "/source/security/trivy-secret.yaml",
            "--format",
            "json",
            "/source",
        ]
    )
    misconfiguration = _docker_base(network=False, mounts=mounts)
    misconfiguration.extend(["config", "--quiet", "--format", "json", "/source"])
    sbom_command = _docker_base(network=False, mounts=mounts)
    sbom_command.extend(["filesystem", "--quiet", "--format", "cyclonedx", "/source"])
    raw_reports = (
        _scan_json(vulnerability),
        _scan_json(secret),
        _scan_json(misconfiguration),
    )
    findings = [
        finding for raw in raw_reports for finding in sanitize_trivy_report(raw, scope="source")
    ]
    return sorted(findings, key=lambda item: item["key"]), _scan_json(sbom_command)


def _artifact_from_report(report_path: Path, source_sha: str) -> tuple[str, dict[str, Any]]:
    if not report_path.is_file() or report_path.is_symlink():
        raise SecurityValidationError("Artifact report must be an existing regular file")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("outcome") != "passed" or report.get("source_sha") != source_sha:
        raise SecurityValidationError("Artifact report is not a passing result for Git HEAD")
    image_ref = report.get("retained_image")
    expected_id = report.get("image", {}).get("image_id")
    if not isinstance(image_ref, str) or not isinstance(expected_id, str):
        raise SecurityValidationError("Artifact report has no retained image identity")
    inspected = json.loads(_run(["docker", "image", "inspect", image_ref]).stdout)
    if len(inspected) != 1 or inspected[0].get("Id") != expected_id:
        raise SecurityValidationError("Retained artifact no longer matches its report")
    revision = (
        inspected[0].get("Config", {}).get("Labels", {}).get("org.opencontainers.image.revision")
    )
    if revision != source_sha:
        raise SecurityValidationError("Retained artifact revision does not match Git HEAD")
    return image_ref, {
        "image_ref": image_ref,
        "image_id": expected_id,
        "repo_digests": report.get("image", {}).get("repo_digests") or [],
        "artifact_report": str(report_path.resolve()),
        "artifact_report_sha256": _sha256(report_path),
    }


def _image_scans(
    image_ref: str, work_dir: Path, cache_dir: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    image_archive = work_dir / "image.tar"
    with image_archive.open("wb") as stream:
        saved = subprocess.run(
            ["docker", "image", "save", image_ref],
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.PIPE,
            check=False,
        )
    if saved.returncode != 0:
        raise SecurityValidationError("Exact artifact image could not be saved for scanning")
    mounts = [(work_dir, "/scan", True), (cache_dir, "/cache", False)]
    scan = _docker_base(network=False, mounts=mounts)
    scan.extend(
        [
            "image",
            "--quiet",
            "--scanners",
            "vuln,secret",
            "--skip-db-update",
            "--format",
            "json",
            "--input",
            "/scan/image.tar",
        ]
    )
    sbom_command = _docker_base(network=False, mounts=mounts)
    sbom_command.extend(["image", "--quiet", "--format", "cyclonedx", "--input", "/scan/image.tar"])
    findings = sanitize_trivy_report(_scan_json(scan), scope="image")
    sbom = _scan_json(sbom_command)
    image_archive.unlink()
    return findings, sbom


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _latest_artifact_report(source_sha: str) -> Path:
    root = ROOT / "test-artifacts" / "artifact-validation"
    candidates = sorted(root.glob("*/report.json"), reverse=True) if root.exists() else []
    for candidate in candidates:
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("source_sha") == source_sha and payload.get("outcome") == "passed":
            return candidate
    raise SecurityValidationError(
        "No passing artifact report matches Git HEAD; run make test-artifact first"
    )


def run_security_validation(artifact_report: Path | None = None) -> tuple[Path, dict[str, Any]]:
    started_at = datetime.now(UTC)
    run_id = f"{started_at.strftime('%Y%m%dT%H%M%S.%fZ')}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    run_dir = ARTIFACT_ROOT / run_id
    run_dir.mkdir(parents=True, mode=0o700)
    report_path = run_dir / "report.json"
    report: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "status": "error",
        "external_providers": "not contacted",
        "host_install": False,
        "docker_socket_mounted": False,
    }
    try:
        source_sha = _source_sha()
        report["source_sha"] = source_sha
        report["inputs"] = inventory_inputs(ROOT)
        report["scanner"] = _ensure_scanner()
        ledger_path = ROOT / "security" / "exceptions.json"
        exceptions = validate_exceptions(json.loads(ledger_path.read_text(encoding="utf-8")))
        report["exception_ledger"] = {
            "path": str(ledger_path.relative_to(ROOT)),
            "sha256": _sha256(ledger_path),
            "active_count": len(exceptions),
        }
        selected_report = artifact_report or _latest_artifact_report(source_sha)
        image_ref, image_identity = _artifact_from_report(selected_report, source_sha)
        report["artifact"] = image_identity
        with tempfile.TemporaryDirectory(prefix="work-", dir=run_dir) as temporary:
            work_dir = Path(temporary)
            cache_dir = work_dir / "cache"
            cache_dir.mkdir(mode=0o700)
            report["advisory_database"] = _prepare_database(cache_dir)
            source_dir = work_dir / "source"
            _extract_committed_source(source_dir)
            report["fixture_drills"] = _fixture_drills(
                work_dir, cache_dir, source_dir / "security" / "trivy-secret.yaml"
            )
            source_findings, source_sbom = _source_scans(source_dir, cache_dir)
            image_findings, image_sbom = _image_scans(image_ref, work_dir, cache_dir)
        _write_json(run_dir / "source.sbom.cdx.json", source_sbom)
        _write_json(run_dir / "image.sbom.cdx.json", image_sbom)
        all_findings = sorted(source_findings + image_findings, key=lambda item: item["key"])
        accepted, blocked = apply_exceptions(all_findings, exceptions)
        source_components = component_names(source_sbom)
        image_components = component_names(image_sbom)
        report["inventory_reconciliation"] = {
            "source_component_count": len(source_components),
            "image_component_count": len(image_components),
            "image_only_component_count": len(image_components - source_components),
            "image_only_components": sorted(image_components - source_components),
        }
        source_licenses = license_inventory(source_sbom)
        image_licenses = license_inventory(image_sbom)
        report["license_inventory"] = {
            "policy": "inventory-only; owner review is required before release acceptance",
            "source": source_licenses,
            "image": image_licenses,
            "source_unknown_count": sum(
                record["licenses"] == ["UNKNOWN"] for record in source_licenses
            ),
            "image_unknown_count": sum(
                record["licenses"] == ["UNKNOWN"] for record in image_licenses
            ),
        }
        report["findings"] = all_findings
        report["accepted_findings"] = accepted
        report["blocking_findings"] = blocked
        report["status"] = "blocked" if blocked else "passed"
        report["finished_at"] = datetime.now(UTC).isoformat()
        _write_json(report_path, report)
        if blocked:
            raise SecurityValidationError(
                f"{len(blocked)} unaccepted finding(s) block release acceptance"
            )
        return report_path, report
    except Exception as exc:
        report["error"] = str(exc)
        report["finished_at"] = datetime.now(UTC).isoformat()
        _write_json(report_path, report)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-report", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "scanner": SCANNER_IMAGE,
                    "host_install": False,
                    "docker_socket": False,
                    "source": "committed git archive",
                    "artifact": "exact retained image from a same-SHA passing report",
                    "external_providers": False,
                    "mutates": False,
                },
                indent=2,
            )
        )
        return 0
    try:
        path, report = run_security_validation(args.artifact_report)
    except (
        SecurityValidationError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        print(f"Security validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Security validation outcome: {report['status']}")
    print(f"Security validation report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
