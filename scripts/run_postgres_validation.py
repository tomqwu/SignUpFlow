#!/usr/bin/env python3
"""Run PostgreSQL acceptance in an owned, ephemeral local Docker container."""

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

IMAGE = "postgres:16-alpine"
OWNERSHIP_LABEL = "io.signupflow.test-run"
RUN_ID_PATTERN = re.compile(r"^[a-f0-9]{8}$")
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PostgresTestTarget:
    """Identifiers and commands for one disposable PostgreSQL test process."""

    run_id: str
    password: str

    def __post_init__(self) -> None:
        if not RUN_ID_PATTERN.fullmatch(self.run_id):
            raise ValueError("PostgreSQL test run ID must be eight lowercase hex characters")
        if not self.password:
            raise ValueError("PostgreSQL test password must not be empty")

    @property
    def container_name(self) -> str:
        return f"signupflow-pgtest-{self.run_id}"

    @property
    def database_name(self) -> str:
        return f"signupflow_test_{self.run_id}"

    @property
    def upgrade_database_name(self) -> str:
        return f"{self.database_name}_upgrade"

    @property
    def username(self) -> str:
        return "signupflow_test"

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
            "/var/lib/postgresql/data:rw,noexec,nosuid,size=512m",
            "--env",
            f"POSTGRES_DB={self.database_name}",
            "--env",
            f"POSTGRES_USER={self.username}",
            "--env",
            f"POSTGRES_PASSWORD={self.password}",
            "--publish",
            "127.0.0.1::5432",
            IMAGE,
        ]

    def database_url(self, port: int, *, upgrade: bool = False) -> str:
        database = self.upgrade_database_name if upgrade else self.database_name
        return (
            f"postgresql://{self.username}:{quote_plus(self.password)}"
            f"@127.0.0.1:{port}/{database}"
        )


def parse_loopback_port(raw: str) -> int:
    """Parse Docker's published-port output and require a loopback binding."""
    match = re.fullmatch(r"(?:127\.0\.0\.1|\[::1\]):([0-9]{1,5})", raw.strip())
    if not match:
        raise ValueError(f"PostgreSQL test port is not loopback-only: {raw!r}")
    port = int(match.group(1))
    if not 1 <= port <= 65535:
        raise ValueError(f"PostgreSQL test port is invalid: {port}")
    return port


def verify_owned_container(target: PostgresTestTarget, inspect_data: Any) -> None:
    """Refuse lifecycle operations unless Docker still reports our exact ownership."""
    if not isinstance(inspect_data, list) or len(inspect_data) != 1:
        raise RuntimeError("Cannot verify PostgreSQL test container ownership")
    record = inspect_data[0]
    labels = record.get("Config", {}).get("Labels", {})
    if record.get("Name") != f"/{target.container_name}":
        raise RuntimeError("PostgreSQL test container name no longer matches")
    if labels.get(OWNERSHIP_LABEL) != target.run_id:
        raise RuntimeError("PostgreSQL test container ownership label no longer matches")


def _run(
    command_line: list[str],
    *,
    environment: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command_line,
        cwd=ROOT,
        env=environment,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def _inspect(target: PostgresTestTarget) -> list[dict[str, Any]]:
    result = _run(["docker", "inspect", target.container_name], capture_output=True)
    value = json.loads(result.stdout)
    if not isinstance(value, list):
        raise RuntimeError("Docker inspect returned an unexpected payload")
    return value


def _wait_until_ready(target: PostgresTestTarget) -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        result = subprocess.run(
            [
                "docker",
                "exec",
                target.container_name,
                "pg_isready",
                "--username",
                target.username,
                "--dbname",
                target.database_name,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            return
        time.sleep(0.5)
    raise RuntimeError("Owned PostgreSQL test container did not become ready within 60 seconds")


def _test_environment(primary_url: str, upgrade_url: str) -> dict[str, str]:
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
            "BILLING_ENABLED": "false",
            "DATABASE_URL": primary_url,
            "EMAIL_ENABLED": "false",
            "ENVIRONMENT": "development",
            "SENTRY_DSN": "",
            "SIGNUPFLOW_LOAD_DOTENV": "false",
            "SIGNUPFLOW_POSTGRES_TEST_URL": primary_url,
            "SIGNUPFLOW_POSTGRES_UPGRADE_TEST_URL": upgrade_url,
            "SIGNUPFLOW_TEST_DATABASE_URL": primary_url,
            "SKIP_TEST_DB_FIXTURES": "true",
            "SMS_ENABLED": "false",
            "TESTING": "true",
        }
    )
    return environment


def _junit_counts(junit_path: Path) -> dict[str, int]:
    if not junit_path.exists():
        return {"tests": 0, "passed": 0, "failures": 0, "errors": 0, "skipped": 0}
    root = ElementTree.parse(junit_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise RuntimeError("PostgreSQL JUnit report does not contain a testsuite")
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


def _write_report(
    *,
    run_dir: Path,
    target: PostgresTestTarget,
    server_version: str,
    started_at: str,
    outcome: str,
    junit_path: Path,
) -> Path:
    source_sha = _run(["git", "rev-parse", "HEAD"], capture_output=True).stdout.strip()
    report = {
        "source_sha": source_sha,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "outcome": outcome,
        "test_counts": _junit_counts(junit_path),
        "database": {
            "engine": "PostgreSQL",
            "server_version": server_version,
            "image": IMAGE,
            "container_name": target.container_name,
            "database_name": target.database_name,
            "host": "127.0.0.1",
            "storage": "ephemeral tmpfs",
        },
    }
    destination = run_dir / "report.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    """Create, validate, and remove one owned PostgreSQL test container."""
    started_at = datetime.now(UTC).isoformat()
    target = PostgresTestTarget(run_id=secrets.token_hex(4), password=secrets.token_urlsafe(24))
    run_dir = (
        ROOT
        / "test-artifacts"
        / "postgres-validation"
        / f"{started_at.replace(':', '').replace('+', '-')}-{os.getpid()}-{target.run_id}"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    junit_path = run_dir / "junit.xml"
    created = False
    outcome = "failed"
    server_version = "unavailable"
    report_path: Path | None = None
    exit_code = 1

    try:
        _run(["docker", "info"], capture_output=True)
        _run(target.docker_run_command(), capture_output=True)
        created = True
        verify_owned_container(target, _inspect(target))
        _wait_until_ready(target)

        port_result = _run(
            ["docker", "port", target.container_name, "5432/tcp"], capture_output=True
        )
        port = parse_loopback_port(port_result.stdout)
        primary_url = target.database_url(port)
        upgrade_url = target.database_url(port, upgrade=True)

        _run(
            [
                "docker",
                "exec",
                target.container_name,
                "createdb",
                "--username",
                target.username,
                target.upgrade_database_name,
            ]
        )
        server_version = _run(
            [
                "docker",
                "exec",
                target.container_name,
                "psql",
                "--username",
                target.username,
                "--dbname",
                target.database_name,
                "--tuples-only",
                "--no-align",
                "--command",
                "SHOW server_version;",
            ],
            capture_output=True,
        ).stdout.strip()

        environment = _test_environment(primary_url, upgrade_url)
        _run([sys.executable, "-m", "alembic", "upgrade", "head"], environment=environment)
        _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/postgres",
                "-q",
                "--tb=short",
                f"--junitxml={junit_path}",
            ],
            environment=environment,
        )
        outcome = "passed"
        exit_code = 0
    except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
        print(f"PostgreSQL validation failed: {exc}", file=sys.stderr)
    finally:
        if created:
            try:
                verify_owned_container(target, _inspect(target))
                _run(["docker", "stop", "--timeout", "5", target.container_name])
            except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
                outcome = "failed"
                exit_code = 1
                print(
                    f"Refused or failed PostgreSQL container cleanup; inspect "
                    f"{target.container_name}: {exc}",
                    file=sys.stderr,
                )
        report_path = _write_report(
            run_dir=run_dir,
            target=target,
            server_version=server_version,
            started_at=started_at,
            outcome=outcome,
            junit_path=junit_path,
        )
        print(f"PostgreSQL validation report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
