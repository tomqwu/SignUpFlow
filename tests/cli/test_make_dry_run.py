"""`make -n` must describe the lifecycle targets without running them.

GNU make executes any recipe line that mentions $(MAKE) even under --dry-run,
so it can hand the flag down to sub-makes. The lifecycle targets used to do
their real work on the same shell line as a $(MAKE) call, so `make -n setup`
migrated the database, loaded the demo and started containers. These tests
run the dry runs with ``poetry`` and Docker replaced by stubs that record every
call, and require that nothing was called while the plan is still printed.
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_CONTROLLED = ("DATABASE_URL", "ENVIRONMENT", "SECRET_KEY", "TESTING", "SIGNUPFLOW_LOAD_DOTENV")

SQLITE = "sqlite:///./dry-run.db"
COMPOSE = "postgresql://u:p@db:5432/x"

#: What each target would really do, by database. None of it may run under -n.
WORK = {
    "migrate": {SQLITE: "alembic upgrade head", COMPOSE: "run --rm api alembic upgrade head"},
    "seed-demo": {SQLITE: "api.cli.main seed-demo", COMPOSE: "api.cli.main seed-demo"},
    "services": {COMPOSE: "up -d db redis"},
}


def _dry_run(tmp_path: Path, target: str, database_url: str) -> tuple[str, str]:
    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    for tool in ("poetry", "docker", "docker-compose"):
        stub = bin_dir / tool
        stub.write_text(f'#!/bin/sh\necho "{tool} $*" >> "{log}"\nexit 0\n')
        stub.chmod(0o755)
    environ = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    environ["DATABASE_URL"] = database_url
    environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    result = subprocess.run(
        ["make", "--dry-run", target],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
        env=environ,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    calls = log.read_text() if log.exists() else ""
    # Parse-time detection of the compose binary is not work.
    calls = "\n".join(line for line in calls.splitlines() if not line.endswith("compose version"))
    return result.stdout, calls


@pytest.mark.parametrize(
    "target, database_url",
    [(target, url) for target, by_url in WORK.items() for url in by_url],
)
def test_dry_run_prints_the_work_without_doing_it(tmp_path, target, database_url):
    stdout, calls = _dry_run(tmp_path, target, database_url)
    work = WORK[target][database_url]
    assert calls == "", f"make -n {target} ran: {calls}"
    assert work in stdout, f"make -n {target} no longer says what it would do"


@pytest.mark.parametrize("database_url", [SQLITE, COMPOSE])
def test_dry_run_of_setup_changes_nothing(tmp_path, database_url):
    _stdout, calls = _dry_run(tmp_path, "setup", database_url)
    for work in ("alembic", "seed-demo", "up -d"):
        assert work not in calls, f"make -n setup ran: {calls}"
