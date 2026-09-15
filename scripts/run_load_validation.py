#!/usr/bin/env python3
"""Run a bounded, source-identified load profile against an authorized target."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import secrets
import socket
import subprocess
import sys
import time
from collections.abc import Iterator, Mapping
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from ipaddress import ip_address
from pathlib import Path
from threading import Lock
from typing import Any, cast
from urllib.parse import urlsplit, urlunsplit

import httpx

from tests.test_environment import build_test_environment

ROOT = Path(__file__).resolve().parents[1]
SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")
SUPPORTED_OPERATIONS = (
    "health",
    "ready",
    "login",
    "people",
    "events",
    "solutions",
    "solve",
)
EXPECTED_STATUS = {name: 200 for name in SUPPORTED_OPERATIONS}


def _positive_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return float(value)


def _bounded_number(value: Any, name: str, *, maximum: float) -> float:
    number = _positive_number(value, name)
    if number > maximum:
        raise ValueError(f"{name} must not exceed {maximum:g}")
    return number


def _bounded_integer(value: Any, name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} through {maximum}")
    return int(value)


@dataclass(frozen=True)
class LoadProfile:
    """Validated workload and threshold contract."""

    name: str
    evidence_tier: str
    approval_reference: str | None
    duration_seconds: float
    concurrency: int
    target_requests_per_second: float
    request_timeout_seconds: float
    people: int
    events: int
    operations: tuple[tuple[str, int], ...]
    minimum_requests: int
    maximum_error_rate: float
    maximum_p95_ms: float
    minimum_throughput_rps: float

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> LoadProfile:
        """Reject misspelled or unbounded profile fields before network access."""
        allowed = {
            "name",
            "evidence_tier",
            "approval_reference",
            "duration_seconds",
            "concurrency",
            "target_requests_per_second",
            "request_timeout_seconds",
            "dataset",
            "operations",
            "thresholds",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise ValueError(f"Unknown load profile fields: {', '.join(unknown)}")

        name = raw.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{2,63}", name):
            raise ValueError("name must be a lowercase profile identifier")

        evidence_tier = raw.get("evidence_tier")
        if evidence_tier not in {"local_smoke", "release_candidate"}:
            raise ValueError("evidence_tier must be local_smoke or release_candidate")
        approval_reference = raw.get("approval_reference")
        if approval_reference is not None and not isinstance(approval_reference, str):
            raise ValueError("approval_reference must be a string")
        if evidence_tier == "release_candidate" and not (approval_reference or "").strip():
            raise ValueError("release_candidate profiles require approval_reference")

        dataset = raw.get("dataset")
        if not isinstance(dataset, Mapping) or set(dataset) != {"people", "events"}:
            raise ValueError("dataset must contain only people and events")
        people = _bounded_integer(dataset["people"], "dataset.people", minimum=2, maximum=1000)
        events = _bounded_integer(dataset["events"], "dataset.events", minimum=1, maximum=1000)

        operations_raw = raw.get("operations")
        if not isinstance(operations_raw, Mapping) or not operations_raw:
            raise ValueError("operations must be a non-empty mapping")
        operations: list[tuple[str, int]] = []
        for operation, weight in operations_raw.items():
            if operation not in SUPPORTED_OPERATIONS:
                raise ValueError(f"Unsupported load operation: {operation}")
            operations.append(
                (
                    operation,
                    _bounded_integer(
                        weight,
                        f"operations.{operation}",
                        minimum=1,
                        maximum=1000,
                    ),
                )
            )

        thresholds = raw.get("thresholds")
        threshold_keys = {
            "minimum_requests",
            "maximum_error_rate",
            "maximum_p95_ms",
            "minimum_throughput_rps",
        }
        if not isinstance(thresholds, Mapping) or set(thresholds) != threshold_keys:
            raise ValueError(f"thresholds must contain exactly {sorted(threshold_keys)}")
        maximum_error_rate = thresholds["maximum_error_rate"]
        if (
            isinstance(maximum_error_rate, bool)
            or not isinstance(maximum_error_rate, int | float)
            or not 0 <= maximum_error_rate <= 1
        ):
            raise ValueError("thresholds.maximum_error_rate must be from 0 through 1")

        return cls(
            name=name,
            evidence_tier=evidence_tier,
            approval_reference=(approval_reference or None),
            duration_seconds=_bounded_number(
                raw.get("duration_seconds"), "duration_seconds", maximum=3600
            ),
            concurrency=_bounded_integer(
                raw.get("concurrency"), "concurrency", minimum=1, maximum=200
            ),
            target_requests_per_second=_bounded_number(
                raw.get("target_requests_per_second"),
                "target_requests_per_second",
                maximum=1000,
            ),
            request_timeout_seconds=_bounded_number(
                raw.get("request_timeout_seconds"),
                "request_timeout_seconds",
                maximum=120,
            ),
            people=people,
            events=events,
            operations=tuple(operations),
            minimum_requests=_bounded_integer(
                thresholds["minimum_requests"],
                "thresholds.minimum_requests",
                minimum=1,
                maximum=10_000_000,
            ),
            maximum_error_rate=float(maximum_error_rate),
            maximum_p95_ms=_positive_number(
                thresholds["maximum_p95_ms"], "thresholds.maximum_p95_ms"
            ),
            minimum_throughput_rps=_positive_number(
                thresholds["minimum_throughput_rps"],
                "thresholds.minimum_throughput_rps",
            ),
        )

    @property
    def operation_names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.operations)

    @property
    def total_weight(self) -> int:
        return sum(weight for _, weight in self.operations)

    def public_dict(self) -> dict[str, Any]:
        """Return the profile without inventing approval or execution state."""
        return {
            "name": self.name,
            "evidence_tier": self.evidence_tier,
            "approval_reference": self.approval_reference,
            "duration_seconds": self.duration_seconds,
            "concurrency": self.concurrency,
            "target_requests_per_second": self.target_requests_per_second,
            "request_timeout_seconds": self.request_timeout_seconds,
            "dataset": {"people": self.people, "events": self.events},
            "operations": dict(self.operations),
            "thresholds": {
                "minimum_requests": self.minimum_requests,
                "maximum_error_rate": self.maximum_error_rate,
                "maximum_p95_ms": self.maximum_p95_ms,
                "minimum_throughput_rps": self.minimum_throughput_rps,
            },
        }


@dataclass(frozen=True)
class RequestSample:
    """One raw request outcome retained in the report."""

    operation: str
    latency_ms: float
    status_code: int | None
    error: str | None = None


@dataclass(frozen=True)
class SeededTarget:
    """Synthetic tenant state used by supported load operations."""

    org_id: str
    email: str
    password: str
    token: str
    from_date: str
    to_date: str


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _sample_summary(samples: list[RequestSample]) -> dict[str, Any]:
    latencies = [sample.latency_ms for sample in samples]
    return {
        "request_count": len(samples),
        "error_count": sum(sample.error is not None for sample in samples),
        "p50_ms": round(_percentile(latencies, 50), 3),
        "p95_ms": round(_percentile(latencies, 95), 3),
        "p99_ms": round(_percentile(latencies, 99), 3),
        "maximum_ms": round(max(latencies, default=0), 3),
    }


def evaluate_samples(
    profile: LoadProfile,
    samples: list[RequestSample],
    *,
    duration_seconds: float,
) -> dict[str, Any]:
    """Evaluate the complete sample set without dropping failed operations."""
    summary = _sample_summary(samples)
    request_count = cast(int, summary["request_count"])
    error_count = cast(int, summary["error_count"])
    error_rate = error_count / request_count if request_count else 1.0
    throughput = request_count / duration_seconds if duration_seconds > 0 else 0.0
    failures: list[str] = []
    if request_count < profile.minimum_requests:
        failures.append(
            f"request count {request_count} is below minimum {profile.minimum_requests}"
        )
    if error_rate > profile.maximum_error_rate:
        failures.append(
            f"error rate {error_rate:.6f} exceeds maximum {profile.maximum_error_rate:.6f}"
        )
    if cast(float, summary["p95_ms"]) > profile.maximum_p95_ms:
        failures.append(
            f"p95 {summary['p95_ms']:.3f}ms exceeds maximum {profile.maximum_p95_ms:.3f}ms"
        )
    if throughput < profile.minimum_throughput_rps:
        failures.append(
            f"throughput {throughput:.3f}rps is below minimum "
            f"{profile.minimum_throughput_rps:.3f}rps"
        )

    operations: dict[str, dict[str, Any]] = {}
    for operation in profile.operation_names:
        operation_samples = [sample for sample in samples if sample.operation == operation]
        operations[operation] = _sample_summary(operation_samples)
        if not operation_samples:
            failures.append(f"operation {operation} produced no samples")

    return {
        "outcome": "passed" if not failures else "failed",
        **summary,
        "error_rate": round(error_rate, 6),
        "throughput_rps": round(throughput, 3),
        "duration_seconds": round(duration_seconds, 3),
        "operations": operations,
        "failures": failures,
    }


def validate_target_url(value: str, *, allow_authorized_remote: bool = False) -> str:
    """Require an origin-only HTTP URL and loopback unless remote use is explicit."""
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Load target must be an HTTP(S) origin")
    if parsed.username or parsed.password:
        raise ValueError("Load target URL must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Load target must be an origin only, without path, query, or fragment")
    host = parsed.hostname
    loopback = host == "localhost"
    if not loopback:
        try:
            loopback = ip_address(host).is_loopback
        except ValueError:
            loopback = False
    if not loopback and not allow_authorized_remote:
        raise ValueError("Load target must be loopback unless authorized remote use is explicit")
    if not loopback and parsed.scheme != "https":
        raise ValueError("Authorized remote load targets must use HTTPS")
    normalized = urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    return normalized.rstrip("/")


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _tracked_source_sha() -> str:
    source_sha = _run_git("rev-parse", "HEAD")
    if not SHA_PATTERN.fullmatch(source_sha):
        raise RuntimeError("Git HEAD is not a full lowercase commit SHA")
    if _run_git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Commit tracked changes before running load validation")
    return source_sha


def _reserve_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return cast(int, listener.getsockname()[1])


@contextmanager
def _owned_local_server(run_dir: Path, source_sha: str) -> Iterator[str]:
    """Start and stop only the exact local process created by this run."""
    port = _reserve_loopback_port()
    base_url = f"http://127.0.0.1:{port}"
    database_path = run_dir / "load.sqlite3"
    environment = build_test_environment(
        os.environ,
        database_url=f"sqlite:///{database_path}",
        secret_key=secrets.token_urlsafe(48),
        frontend_url=base_url,
    )
    environment.update(
        {
            "DEBUG": "false",
            "DEBUG_RETURN_RESET_TOKEN": "false",
            "DISABLE_RATE_LIMITS": "false",
            "DISABLE_USAGE_LIMITS": "false",
            "RELEASE_SHA": source_sha,
            "TESTING": "false",
        }
    )
    log_path = run_dir / "server.log"
    with log_path.open("w", encoding="utf-8") as log_stream:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=ROOT,
            env=environment,
            stdout=log_stream,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("Owned load server exited before becoming ready")
                try:
                    response = httpx.get(f"{base_url}/ready", timeout=1)
                    if response.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.2)
            else:
                raise RuntimeError("Owned load server did not become ready within 45 seconds")
            yield base_url
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def _expect(response: httpx.Response, status_code: int, operation: str) -> dict[str, Any]:
    if response.status_code != status_code:
        raise RuntimeError(f"{operation} returned HTTP {response.status_code}")
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError(f"{operation} returned a non-object response")
    return cast(dict[str, Any], value)


def _seed_target(client: httpx.Client, profile: LoadProfile, run_id: str) -> SeededTarget:
    org_id = f"load-{run_id}"
    email = f"owner-{run_id}@load.example"
    password = "OwnedLoad123!"
    signup = _expect(
        client.post(
            "/api/v1/auth/signup",
            json={
                "org_id": org_id,
                "org_name": "Owned load validation",
                "region": "CA-ON",
                "name": "Load owner",
                "email": email,
                "password": password,
                "timezone": "America/Toronto",
            },
        ),
        201,
        "signup",
    )
    token = signup.get("token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Signup did not return an access token")
    headers = {"Authorization": f"Bearer {token}"}
    people = [
        {
            "id": f"load-person-{run_id}-{index}",
            "org_id": org_id,
            "name": f"Load person {index}",
            "email": f"person-{run_id}-{index}@load.example",
            "roles": ["volunteer", "usher"],
            "timezone": "America/Toronto",
        }
        for index in range(profile.people)
    ]
    imported = _expect(
        client.post(
            "/api/v1/people/bulk",
            params={"org_id": org_id},
            headers=headers,
            json={"items": people},
        ),
        200,
        "bulk people setup",
    )
    if imported.get("created") != profile.people:
        raise RuntimeError("Load setup did not create the requested people dataset")

    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=14)
    for index in range(profile.events):
        event_start = start + timedelta(days=index)
        _expect(
            client.post(
                "/api/v1/events/",
                headers=headers,
                json={
                    "id": f"load-event-{run_id}-{index}",
                    "org_id": org_id,
                    "type": "Load scheduling event",
                    "start_time": event_start.isoformat(),
                    "end_time": (event_start + timedelta(hours=2)).isoformat(),
                    "extra_data": {"role_counts": {"usher": 1}},
                },
            ),
            201,
            "event setup",
        )
    to_date = (start + timedelta(days=profile.events - 1)).date().isoformat()
    _expect(
        client.post(
            "/api/v1/solver/solve",
            headers=headers,
            json={
                "org_id": org_id,
                "from_date": start.date().isoformat(),
                "to_date": to_date,
                "mode": "strict",
                "change_min": False,
            },
        ),
        200,
        "initial solve",
    )
    return SeededTarget(
        org_id=org_id,
        email=email,
        password=password,
        token=token,
        from_date=start.date().isoformat(),
        to_date=to_date,
    )


def _send_operation(
    client: httpx.Client,
    operation: str,
    target: SeededTarget,
    solve_lock: Lock,
) -> httpx.Response:
    headers = {"Authorization": f"Bearer {target.token}"}
    if operation == "health":
        return client.get("/health")
    if operation == "ready":
        return client.get("/ready")
    if operation == "login":
        return client.post(
            "/api/v1/auth/login",
            json={"email": target.email, "password": target.password},
        )
    if operation == "people":
        return client.get("/api/v1/people/", params={"org_id": target.org_id}, headers=headers)
    if operation == "events":
        return client.get("/api/v1/events/", params={"org_id": target.org_id}, headers=headers)
    if operation == "solutions":
        return client.get("/api/v1/solutions/", params={"org_id": target.org_id}, headers=headers)
    if operation == "solve":
        with solve_lock:
            return client.post(
                "/api/v1/solver/solve",
                headers=headers,
                json={
                    "org_id": target.org_id,
                    "from_date": target.from_date,
                    "to_date": target.to_date,
                    "mode": "strict",
                    "change_min": False,
                },
            )
    raise RuntimeError(f"Unsupported load operation reached execution: {operation}")


def _run_load(
    base_url: str,
    profile: LoadProfile,
    target: SeededTarget,
) -> tuple[list[RequestSample], float]:
    operation_names = list(profile.operation_names)
    operation_weights = [weight for _, weight in profile.operations]
    solve_lock = Lock()
    started = time.monotonic()
    deadline = started + profile.duration_seconds
    per_worker_interval = profile.concurrency / profile.target_requests_per_second

    def worker(worker_id: int) -> list[RequestSample]:
        samples: list[RequestSample] = []
        randomizer = random.Random(f"{target.org_id}-{worker_id}")
        next_request = time.monotonic()
        with httpx.Client(base_url=base_url, timeout=profile.request_timeout_seconds) as client:
            while time.monotonic() < deadline:
                operation = randomizer.choices(
                    operation_names,
                    weights=operation_weights,
                    k=1,
                )[0]
                request_started = time.perf_counter()
                status_code: int | None = None
                error: str | None = None
                try:
                    response = _send_operation(client, operation, target, solve_lock)
                    status_code = response.status_code
                    expected = EXPECTED_STATUS[operation]
                    if status_code != expected:
                        error = f"unexpected status {status_code}; expected {expected}"
                except httpx.HTTPError as exc:
                    error = type(exc).__name__
                latency_ms = (time.perf_counter() - request_started) * 1000
                samples.append(RequestSample(operation, latency_ms, status_code, error))
                next_request += per_worker_interval
                delay = next_request - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
        return samples

    with ThreadPoolExecutor(max_workers=profile.concurrency) as executor:
        worker_results = list(executor.map(worker, range(profile.concurrency)))
    duration = time.monotonic() - started
    return [sample for result in worker_results for sample in result], duration


def _verify_target_identity(
    client: httpx.Client,
    expected_release_sha: str,
) -> str:
    response = client.get("/health")
    if response.status_code != 200:
        raise RuntimeError(f"Target health returned HTTP {response.status_code}")
    observed = response.headers.get("X-Release-SHA", "")
    if observed != expected_release_sha:
        raise RuntimeError(
            "Target release identity mismatch: "
            f"expected {expected_release_sha}, observed {observed or 'missing'}"
        )
    ready = client.get("/ready")
    if ready.status_code != 200:
        raise RuntimeError(f"Target readiness returned HTTP {ready.status_code}")
    return str(observed)


def _load_profile(path: Path) -> tuple[LoadProfile, str]:
    payload = path.read_bytes()
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid load profile JSON: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise ValueError("Load profile root must be an object")
    return LoadProfile.from_mapping(raw), hashlib.sha256(payload).hexdigest()


def _write_report(run_dir: Path, report: dict[str, Any]) -> Path:
    destination = run_dir / "report.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--start-local", action="store_true")
    target.add_argument("--base-url")
    parser.add_argument("--expected-release-sha")
    parser.add_argument("--allow-authorized-remote", action="store_true")
    args = parser.parse_args()

    started_at = datetime.now(UTC)
    run_id = secrets.token_hex(4)
    run_dir = (
        ROOT
        / "test-artifacts"
        / "load-validation"
        / f"{started_at.strftime('%Y%m%dT%H%M%S.%fZ')}-{os.getpid()}-{run_id}"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "outcome": "failed",
        "external_providers": "disabled for owned local runs; not contacted by the harness",
    }
    exit_code = 1
    try:
        source_sha = _tracked_source_sha()
        profile, profile_sha256 = _load_profile(args.profile)
        report.update(
            {
                "source_sha": source_sha,
                "profile": profile.public_dict(),
                "profile_sha256": profile_sha256,
            }
        )
        if args.start_local:
            if args.expected_release_sha:
                raise ValueError("--expected-release-sha is derived for --start-local")
            if args.allow_authorized_remote:
                raise ValueError("--allow-authorized-remote cannot be used with --start-local")
            if profile.evidence_tier != "local_smoke":
                raise ValueError("An owned source server cannot produce release_candidate evidence")
            expected_release_sha = source_sha
            server_context = _owned_local_server(run_dir, source_sha)
        else:
            if not args.expected_release_sha or not SHA_PATTERN.fullmatch(
                args.expected_release_sha
            ):
                raise ValueError("--base-url requires an exact --expected-release-sha")
            if args.allow_authorized_remote and profile.evidence_tier != "release_candidate":
                raise ValueError("Remote load requires an approved release_candidate profile")
            expected_release_sha = args.expected_release_sha

            @contextmanager
            def supplied_target() -> Iterator[str]:
                yield validate_target_url(
                    args.base_url,
                    allow_authorized_remote=args.allow_authorized_remote,
                )

            server_context = supplied_target()

        with server_context as base_url:
            with httpx.Client(base_url=base_url, timeout=profile.request_timeout_seconds) as client:
                observed_release_sha = _verify_target_identity(client, expected_release_sha)
                seeded = _seed_target(client, profile, run_id)
            samples, actual_duration = _run_load(base_url, profile, seeded)
            evaluation = evaluate_samples(
                profile,
                samples,
                duration_seconds=actual_duration,
            )
            report.update(
                {
                    "target": {
                        "base_url": base_url,
                        "expected_release_sha": expected_release_sha,
                        "observed_release_sha": observed_release_sha,
                        "scope": (
                            "owned local source server"
                            if args.start_local
                            else "explicitly supplied target"
                        ),
                    },
                    "dataset": {
                        "organization": seeded.org_id,
                        "people": profile.people,
                        "events": profile.events,
                    },
                    "evaluation": evaluation,
                    "samples": [asdict(sample) for sample in samples],
                    "outcome": evaluation["outcome"],
                    "release_evidence": profile.evidence_tier == "release_candidate",
                }
            )
            exit_code = 0 if evaluation["outcome"] == "passed" else 1
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.CalledProcessError,
        httpx.HTTPError,
    ) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        print(f"Load validation failed: {exc}", file=sys.stderr)
    finally:
        report["finished_at"] = datetime.now(UTC).isoformat()
        report_path = _write_report(run_dir, report)
        print(f"Load validation report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
