#!/usr/bin/env python3
"""Run Redis rate-limit acceptance in an owned local Docker container."""

from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from xml.etree import ElementTree

IMAGE = "redis:7-alpine"
OWNERSHIP_LABEL = "io.signupflow.redis-test-run"
RUN_ID_PATTERN = re.compile(r"^[a-f0-9]{8}$")
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RedisTestTarget:
    run_id: str
    password: str

    def __post_init__(self) -> None:
        if not RUN_ID_PATTERN.fullmatch(self.run_id):
            raise ValueError("Redis test run ID must be eight lowercase hex characters")
        if not self.password:
            raise ValueError("Redis test password must not be empty")

    @property
    def container_name(self) -> str:
        return f"signupflow-redistest-{self.run_id}"

    def docker_run_command(self) -> list[str]:
        return [
            "docker",
            "run",
            "--detach",
            "--rm",
            "--name",
            self.container_name,
            "--label",
            f"{OWNERSHIP_LABEL}={self.run_id}",
            "--tmpfs",
            "/data:rw,noexec,nosuid,size=64m",
            "--publish",
            "127.0.0.1::6379",
            IMAGE,
            "redis-server",
            "--requirepass",
            self.password,
            "--save",
            "",
            "--appendonly",
            "no",
        ]

    def redis_url(self, port: int) -> str:
        return f"redis://:{quote_plus(self.password)}@127.0.0.1:{port}/0"


def parse_loopback_port(raw: str) -> int:
    match = re.fullmatch(r"(?:127\.0\.0\.1|\[::1\]):([0-9]{1,5})", raw.strip())
    if not match:
        raise ValueError(f"Redis test port is not loopback-only: {raw!r}")
    port = int(match.group(1))
    if not 1 <= port <= 65535:
        raise ValueError(f"Redis test port is invalid: {port}")
    return port


def _run(command: list[str], *, environment=None, capture_output=False):
    return subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def _inspect(target: RedisTestTarget) -> list[dict[str, Any]]:
    result = _run(["docker", "inspect", target.container_name], capture_output=True)
    return json.loads(result.stdout)


def verify_owned_container(target: RedisTestTarget, records: Any) -> None:
    if not isinstance(records, list) or len(records) != 1:
        raise RuntimeError("Cannot verify Redis test container ownership")
    record = records[0]
    labels = record.get("Config", {}).get("Labels", {})
    if record.get("Name") != f"/{target.container_name}":
        raise RuntimeError("Redis test container name no longer matches")
    if labels.get(OWNERSHIP_LABEL) != target.run_id:
        raise RuntimeError("Redis test container ownership label no longer matches")


def _wait_until_ready(target: RedisTestTarget) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        result = subprocess.run(
            [
                "docker",
                "exec",
                target.container_name,
                "redis-cli",
                "--no-auth-warning",
                "-a",
                target.password,
                "ping",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "PONG":
            return
        time.sleep(0.25)
    raise RuntimeError("Owned Redis test container did not become ready within 30 seconds")


def _counts(junit_path: Path) -> dict[str, int]:
    if not junit_path.exists():
        return {"tests": 0, "passed": 0, "failures": 0, "errors": 0, "skipped": 0}
    root = ElementTree.parse(junit_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise RuntimeError("Redis JUnit report does not contain a testsuite")
    tests = int(suite.attrib.get("tests", 0))
    failures = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    skipped = int(suite.attrib.get("skipped", 0))
    return {
        "tests": tests,
        "passed": tests - failures - errors - skipped,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }


def main() -> int:
    started_at = datetime.now(UTC).isoformat()
    target = RedisTestTarget(secrets.token_hex(4), secrets.token_urlsafe(24))
    run_dir = (
        ROOT
        / "test-artifacts"
        / "redis-validation"
        / (f"{started_at.replace(':', '').replace('+', '-')}-{os.getpid()}-{target.run_id}")
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    junit_path = run_dir / "junit.xml"
    created = False
    outcome = "failed"
    version = "unavailable"
    exit_code = 1
    try:
        _run(["docker", "info"], capture_output=True)
        _run(target.docker_run_command(), capture_output=True)
        created = True
        verify_owned_container(target, _inspect(target))
        _wait_until_ready(target)
        port = parse_loopback_port(
            _run(["docker", "port", target.container_name, "6379/tcp"], capture_output=True).stdout
        )
        version = (
            _run(
                [
                    "docker",
                    "exec",
                    target.container_name,
                    "redis-cli",
                    "--no-auth-warning",
                    "-a",
                    target.password,
                    "INFO",
                    "server",
                ],
                capture_output=True,
            )
            .stdout.split("redis_version:", 1)[1]
            .splitlines()[0]
            .strip()
        )
        environment = dict(os.environ)
        for key in (
            "OLLAMA_API_KEY",
            "SENDGRID_API_KEY",
            "SENTRY_DSN",
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
        ):
            environment.pop(key, None)
        environment.update(
            {
                "SIGNUPFLOW_LOAD_DOTENV": "false",
                "SIGNUPFLOW_REDIS_TEST_URL": target.redis_url(port),
                "TESTING": "true",
            }
        )
        _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/redis",
                "-q",
                "--tb=short",
                f"--junitxml={junit_path}",
            ],
            environment=environment,
        )
        outcome = "passed"
        exit_code = 0
    except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
        print(f"Redis validation failed: {exc}", file=sys.stderr)
    finally:
        if created:
            try:
                verify_owned_container(target, _inspect(target))
                _run(["docker", "stop", "--timeout", "5", target.container_name])
            except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
                outcome = "failed"
                exit_code = 1
                print(f"Refused or failed Redis container cleanup: {exc}", file=sys.stderr)
        source_sha = _run(["git", "rev-parse", "HEAD"], capture_output=True).stdout.strip()
        report = {
            "source_sha": source_sha,
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
            "outcome": outcome,
            "test_counts": _counts(junit_path),
            "redis": {
                "server_version": version,
                "image": IMAGE,
                "container_name": target.container_name,
                "host": "127.0.0.1",
                "storage": "ephemeral tmpfs",
            },
        }
        report_path = run_dir / "report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Redis validation report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
