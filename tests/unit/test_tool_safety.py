"""Keep repository tools explicit, read-only by default, and scoped to owned resources."""

from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RETIRED_TOOLS = (
    "scripts/QUICK_DEMO.sh",
    "scripts/backup_database.sh",
    "scripts/build-binary.sh",
    "scripts/cleanup_maintenance.sh",
    "scripts/cleanup_servers.sh",
    "scripts/migrate_add_role_to_assignments.py",
    "scripts/migrate_assignments.py",
    "scripts/migrate_invitations.py",
    "scripts/migrate_passwords_to_bcrypt.py",
    "scripts/migrate_timezone.py",
    "scripts/migrate_vacation_reason.py",
    "scripts/restore_database.sh",
    "scripts/seed_sms_templates.py",
    "scripts/test_docker_setup.sh",
    "scripts/validate_email_system.sh",
)
INVENTORIED_TOOLS = (
    "scripts/QUICK_DEMO.sh",
    "scripts/backup_database.sh",
    "scripts/build-binary.sh",
    "scripts/agent_runner.py",
    "scripts/agent_tool_guard.py",
    "scripts/capture_playbook_screenshots.py",
    "scripts/check_test_docstrings.py",
    "scripts/check_test_status.sh",
    "scripts/cleanup_and_test.sh",
    "scripts/cleanup_maintenance.sh",
    "scripts/cleanup_servers.sh",
    "scripts/email_smoke.py",
    "scripts/migrate_add_role_to_assignments.py",
    "scripts/migrate_assignments.py",
    "scripts/migrate_invitations.py",
    "scripts/migrate_passwords_to_bcrypt.py",
    "scripts/migrate_timezone.py",
    "scripts/migrate_vacation_reason.py",
    "scripts/ralph-loop-gemini.sh",
    "scripts/ralph-loop.sh",
    "scripts/restore_database.sh",
    "scripts/retired_tool.py",
    "scripts/run_local_validation.py",
    "scripts/seed_sms_templates.py",
    "scripts/test_docker_setup.sh",
    "scripts/validate_email_system.sh",
    "tools/db_interactive.py",
    "tools/db_viewer.py",
    "tools/sqlite_readonly.py",
)


def _command(path: Path, *arguments: str) -> list[str]:
    if path.suffix == ".py":
        return [sys.executable, str(path), *arguments]
    return [str(path), *arguments]


@pytest.mark.parametrize("relative", RETIRED_TOOLS)
def test_retired_tools_refuse_without_touching_unowned_files(tmp_path, relative):
    sentinel_db = tmp_path / "roster.db"
    sentinel_log = tmp_path / "unrelated.log"
    sentinel_db.write_bytes(b"database sentinel")
    sentinel_log.write_text("log sentinel")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}

    result = subprocess.run(
        _command(ROOT / relative),
        cwd=tmp_path,
        env={**os.environ, "DATABASE_URL": f"sqlite:///{sentinel_db}"},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "retired" in (result.stdout + result.stderr).lower()
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


@pytest.mark.parametrize(
    "relative", ["scripts/cleanup_and_test.sh", "scripts/check_test_status.sh"]
)
def test_supported_test_wrappers_are_dry_runnable_and_have_no_global_cleanup(relative):
    path = ROOT / relative
    source = path.read_text()
    for unsafe in ("pkill", "lsof -ti", "/tmp/", "rm -f", "kill -9"):
        assert unsafe not in source

    result = subprocess.run(
        [str(path), "--dry-run"], cwd=ROOT, text=True, capture_output=True, check=False
    )

    assert result.returncode == 0
    assert "make test-" in result.stdout


def test_email_smoke_requires_explicit_live_send_before_loading_credentials():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/email_smoke.py"), "--to", "nobody@example.com"],
        cwd=ROOT,
        env={**os.environ, "EMAIL_ENABLED": "true", "SENDGRID_API_KEY": "sentinel"},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--allow-live-send" in result.stdout + result.stderr
    assert "backend:" not in result.stdout


@pytest.mark.parametrize("tool", ["tools/db_viewer.py", "tools/db_interactive.py"])
def test_database_viewers_require_an_existing_explicit_database(tool, tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / tool)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert not (tmp_path / "cricket_roster.db").exists()


def test_database_viewer_is_read_only_and_refuses_symlinks(tmp_path):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sentinel VALUES ('unchanged')")
    link = tmp_path / "linked.db"
    link.symlink_to(database)

    mutation = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/db_viewer.py"),
            str(database),
            "--query",
            "DELETE FROM sentinel",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    symlink = subprocess.run(
        [sys.executable, str(ROOT / "tools/db_viewer.py"), str(link)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert mutation.returncode == 2
    assert "read-only" in mutation.stdout + mutation.stderr
    assert symlink.returncode == 2
    assert "symlink" in symlink.stdout + symlink.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT value FROM sentinel").fetchone() == ("unchanged",)


def test_database_viewers_read_successfully_without_creating_sidecars(tmp_path):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE "odd""name" (value TEXT NOT NULL)')
        connection.execute('INSERT INTO "odd""name" VALUES (\'visible\')')

    viewer = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/db_viewer.py"),
            str(database),
            "--table",
            'odd"name',
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    interactive = subprocess.run(
        [sys.executable, str(ROOT / "tools/db_interactive.py"), str(database)],
        input='sql SELECT value FROM "odd""name"\nquit\n',
        text=True,
        capture_output=True,
        check=False,
    )

    assert viewer.returncode == 0, viewer.stderr
    assert interactive.returncode == 0, interactive.stderr
    assert "visible" in viewer.stdout
    assert "visible" in interactive.stdout
    assert sorted(path.name for path in tmp_path.iterdir()) == ["owned.db"]


def test_docstring_checker_preserves_success_and_failure_exit_codes(tmp_path):
    good = tmp_path / "test_good.py"
    good.write_text('"""Documented module."""\n\ndef test_ok():\n    """Pass."""\n')
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_test_docstrings.py"), str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0

    bad = tmp_path / "test_bad.py"
    bad.write_text("def test_missing():\n    pass\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_test_docstrings.py"), str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "test_missing" in result.stdout


def test_tool_ledger_classifies_every_entry_point():
    ledger = (ROOT / "docs/TOOLS.md").read_text()

    for relative in INVENTORIED_TOOLS:
        assert f"`{relative}`" in ledger
    assert "supported" in ledger.lower()
    assert "retired" in ledger.lower()
    assert "internal support" in ledger.lower()


def test_every_shell_tool_has_valid_bash_syntax():
    shell_tools = sorted((ROOT / "scripts").glob("*.sh"))
    result = subprocess.run(
        ["bash", "-n", *map(str, shell_tools)], text=True, capture_output=True, check=False
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "target",
    ["stop", "restart", "clean", "clean-weekly", "clean-all", "clean-docker", "clean-docker-all"],
)
def test_retired_make_cleanup_targets_refuse_without_running_global_commands(target):
    result = subprocess.run(
        ["make", "-s", target], cwd=ROOT, text=True, capture_output=True, check=False
    )

    assert result.returncode != 0
    assert "Retired:" in result.stdout
    assert "pkill" not in result.stdout + result.stderr


def test_interrupted_validator_stops_only_its_owned_child_and_keeps_log(tmp_path):
    child_pid_path = tmp_path / "child.pid"
    artifact_path = tmp_path / "artifacts"
    child_code = (
        "import os, pathlib, time; "
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(os.getpid())); "
        "time.sleep(30)"
    )
    driver_code = (
        "import json, pathlib, sys; "
        "from scripts.run_local_validation import run_tier; "
        "tier={'id':'interrupt','label':'Interrupt','paths':[],"
        f"'command':[{sys.executable!r},'-c',{child_code!r}]}}; "
        f"result=run_tier(tier, artifact_dir=pathlib.Path({str(artifact_path)!r})); "
        "print(json.dumps(result))"
    )
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    driver = subprocess.Popen(
        [sys.executable, "-c", driver_code],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        for _ in range(100):
            if child_pid_path.is_file():
                break
            time.sleep(0.05)
        assert child_pid_path.is_file()
        child_pid = int(child_pid_path.read_text())

        os.kill(driver.pid, signal.SIGINT)
        stdout, stderr = driver.communicate(timeout=10)
        result = json.loads(stdout.strip().splitlines()[-1])

        assert driver.returncode == 0, stderr
        assert result["status"] == "failed"
        assert result["exit_code"] == 130
        assert result["interrupted"] is True
        assert "stopping owned test process" in Path(result["artifacts"]["log"]).read_text()
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)
        assert unrelated.poll() is None
    finally:
        if driver.poll() is None:
            driver.terminate()
            driver.wait(timeout=5)
        unrelated.terminate()
        unrelated.wait(timeout=5)
