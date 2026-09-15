#!/usr/bin/env python3
"""Run the owned local SQLite backup and restore acceptance drill."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from alembic import command
from alembic.config import Config
from scripts.sqlite_recovery import (
    create_backup,
    generate_key,
    initialize_workspace,
    restore_backup,
)
from tests.test_environment import PROVIDER_ENVIRONMENT_KEYS, build_test_environment

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "test-artifacts" / "recovery-drill"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _source_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def _working_tree_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    ignored = {"?? .claude/scheduled_tasks.lock"}
    return any(line not in ignored for line in result.stdout.splitlines())


def _run_directory() -> Path:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now().strftime("%Y%m%dT%H%M%S.%fZ")
    path = ARTIFACT_ROOT / f"{stamp}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    path.mkdir()
    return path


def _migrate(path: Path) -> None:
    url = f"sqlite:///{path}"
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    previous_url = os.environ.get("DATABASE_URL")
    previous_dotenv = os.environ.get("SIGNUPFLOW_LOAD_DOTENV")
    os.environ["DATABASE_URL"] = url
    os.environ["SIGNUPFLOW_LOAD_DOTENV"] = "false"
    try:
        command.upgrade(config, "head")
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url
        if previous_dotenv is None:
            os.environ.pop("SIGNUPFLOW_LOAD_DOTENV", None)
        else:
            os.environ["SIGNUPFLOW_LOAD_DOTENV"] = previous_dotenv


def _junit_counts(path: Path) -> dict[str, int]:
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    return {
        "tests": tests,
        "passed": max(0, tests - failures - errors - skipped),
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }


def _test_environment(database_url: str) -> dict[str, str]:
    environment = build_test_environment(
        os.environ,
        database_url=database_url,
        secret_key="recovery-drill-only-secret-key-32-chars",
    )
    environment.update(
        {
            "SIGNUPFLOW_TEST_DATABASE_URL": database_url,
            "TESTING": "true",
        }
    )
    return environment


def _run_tests(run_dir: Path) -> dict[str, Any]:
    junit = run_dir / "junit.xml"
    log = run_dir / "pytest.log"
    database_url = f"sqlite:///{run_dir / 'pytest.sqlite'}"
    command_line = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_sqlite_recovery.py",
        "tests/integration/test_sqlite_recovery_acceptance.py",
        "-q",
        f"--junitxml={junit}",
    ]
    started = time.monotonic()
    result = subprocess.run(
        command_line,
        cwd=ROOT,
        env=_test_environment(database_url),
        text=True,
        capture_output=True,
        check=False,
    )
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    counts = (
        _junit_counts(junit)
        if junit.is_file()
        else {
            "tests": 0,
            "passed": 0,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
        }
    )
    return {
        "command": command_line,
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": result.returncode,
        "counts": counts,
        "junit": str(junit),
        "log": str(log),
        "provider_credentials_present": sorted(
            key for key in PROVIDER_ENVIRONMENT_KEYS if key in _test_environment(database_url)
        ),
    }


def run_drill() -> tuple[dict[str, Any], Path]:
    run_dir = _run_directory()
    work_dir = run_dir / "owned-work"
    work_dir.mkdir(mode=0o700)
    source = work_dir / "source.sqlite"
    workspace = work_dir / "workspace"
    key = work_dir / "recovery.key"
    started_at = _utc_now()
    report: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "source_sha": _source_sha(),
        "working_tree_dirty": _working_tree_dirty(),
        "started_at": started_at.isoformat(),
        "scope": "owned fictional local SQLite only",
        "cutover": "not attempted",
        "external_providers": "disabled and not contacted",
    }
    writer: sqlite3.Connection | None = None
    try:
        _migrate(source)
        writer = sqlite3.connect(source)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("CREATE TABLE recovery_drill_sentinel (value TEXT NOT NULL)")
        writer.execute("INSERT INTO recovery_drill_sentinel VALUES ('base')")
        writer.commit()
        writer.execute("INSERT INTO recovery_drill_sentinel VALUES ('committed-in-wal')")
        writer.commit()
        wal_size = Path(f"{source}-wal").stat().st_size

        initialize_workspace(workspace)
        generate_key(key)
        backup_started = time.monotonic()
        backup = create_backup(workspace, source, key, "drill")
        backup_duration = round(time.monotonic() - backup_started, 3)
        writer.close()
        writer = None

        restore = restore_backup(workspace, backup.bundle_path, key, "drill")
        restore_receipt = json.loads(restore.receipt_path.read_text(encoding="utf-8"))
        with sqlite3.connect(restore.database_path) as connection:
            rows = connection.execute(
                "SELECT value FROM recovery_drill_sentinel ORDER BY rowid"
            ).fetchall()
            migration_head = connection.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()[0]
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

        report["recovery"] = {
            "backup_id": backup.backup_id,
            "backup_duration_seconds": backup_duration,
            "plaintext_sha256": backup.plaintext_sha256,
            "wal_bytes_before_backup": wal_size,
            "restored_rows": [row[0] for row in rows],
            "migration_head": migration_head,
            "integrity_check": integrity,
            "restore_duration_ms": restore_receipt["restore_duration_ms"],
            "recovery_point_age_seconds": restore_receipt["recovery_point_age_seconds"],
            "state": restore_receipt["state"],
            "outbound_delivery": restore_receipt["outbound_delivery"],
        }
        report["tests"] = _run_tests(run_dir)
        tests = report["tests"]
        recovered = report["recovery"]
        report["outcome"] = (
            "passed"
            if tests["exit_code"] == 0
            and tests["counts"]["failures"] == 0
            and tests["counts"]["errors"] == 0
            and not tests["provider_credentials_present"]
            and recovered["restored_rows"] == ["base", "committed-in-wal"]
            and recovered["integrity_check"] == "ok"
            else "failed"
        )
    except BaseException as exc:
        report["outcome"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if writer is not None:
            writer.close()
        if key.exists():
            key.unlink()
        report["key_destroyed"] = not key.exists()
        report["finished_at"] = _utc_now().isoformat()
        report_path = run_dir / "report.json"
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if work_dir.exists():
            shutil.rmtree(work_dir)
    return report, report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "scope": "owned fictional local SQLite only",
                    "artifacts": str(ARTIFACT_ROOT),
                    "tests": [
                        "tests/unit/test_sqlite_recovery.py",
                        "tests/integration/test_sqlite_recovery_acceptance.py",
                    ],
                    "cutover": False,
                    "external_providers": False,
                    "mutates": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    try:
        report, path = run_drill()
    except (OSError, RuntimeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"Recovery drill failed: {exc}", file=sys.stderr)
        return 1
    print(f"Recovery drill outcome: {report['outcome']}")
    print(f"Recovery drill report: {path}")
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
