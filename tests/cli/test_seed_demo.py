"""`signupflow seed-demo` is what `make setup` runs to print a working login.

Run as a subprocess against a throwaway SQLite file, from a directory with no
.env, so the command sees only the configuration each test gives it.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from api.models import Base

REPO_ROOT = Path(__file__).resolve().parents[2]

_CONTROLLED = ("DATABASE_URL", "ENVIRONMENT", "SECRET_KEY", "TESTING", "SIGNUPFLOW_LOAD_DOTENV")


def run_seed(tmp_path: Path, database: Path, **overrides: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    env["DATABASE_URL"] = f"sqlite:///{database}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.update(overrides)
    return subprocess.run(
        [sys.executable, "-m", "api.cli.main", "seed-demo"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=tmp_path,
        env=env,
    )


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "demo.db"
    Base.metadata.create_all(create_engine(f"sqlite:///{path}"))
    return path


def test_it_prints_the_logins_after_loading(tmp_path, database):
    result = run_seed(tmp_path, database)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Demo organization loaded" in result.stdout
    assert "admin@example.com" in result.stdout
    assert "worship-leader-a@example.com" in result.stdout
    assert "DemoPass123!" in result.stdout


def test_a_second_run_still_prints_the_logins(tmp_path, database):
    """Setup can be re-run; the login it prints must not disappear."""
    run_seed(tmp_path, database)
    result = run_seed(tmp_path, database)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "already loaded" in result.stdout
    assert "admin@example.com" in result.stdout


def test_it_points_at_the_configured_app_url(tmp_path, database):
    result = run_seed(tmp_path, database, APP_URL="http://localhost:9999")
    assert "http://localhost:9999" in result.stdout


def test_production_is_refused_without_writing(tmp_path, database):
    result = run_seed(tmp_path, database, ENVIRONMENT="production")
    assert result.returncode != 0
    assert "DemoPass123!" not in result.stdout
    engine = create_engine(f"sqlite:///{database}")
    with engine.connect() as conn:
        assert conn.exec_driver_sql("select count(*) from organizations").scalar() == 0


def _run_make_with_stubs(tmp_path: Path, target: str, **env: str) -> str:
    """Run a real make target with ``poetry`` and Docker replaced by stubs.

    Not ``--dry-run``: make still executes any recipe line containing $(MAKE)
    under -n, so a dry run of these targets would really write to a database.
    The stubs only record how they were called, which is the routing decision.
    """
    bin_dir = tmp_path / "stub-bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    for tool in ("poetry", "docker", "docker-compose"):
        stub = bin_dir / tool
        stub.write_text(f'#!/bin/sh\necho "{tool} $*" >> "{log}"\nexit 0\n')
        stub.chmod(0o755)
    environ = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    environ.update(env)
    environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    result = subprocess.run(
        ["make", target],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
        env=environ,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return log.read_text() if log.exists() else ""


class TestMakeRoutesTheSeedLikeMigrations:
    """The seed writes to the database migrations just created, so it has to run
    in the same place: on the host for SQLite, inside compose for 'db'."""

    SEED = "python -m api.cli.main seed-demo"

    def test_sqlite_seeds_on_the_host(self, tmp_path):
        calls = _run_make_with_stubs(tmp_path, "seed-demo", DATABASE_URL="sqlite:///./x.db")
        assert f"poetry run {self.SEED}" in calls
        assert "docker-compose.dev.yml run" not in calls

    def test_compose_database_seeds_inside_compose(self, tmp_path):
        calls = _run_make_with_stubs(
            tmp_path, "seed-demo", DATABASE_URL="postgresql://u:p@db:5432/x"
        )
        # Either compose spelling, whichever the Makefile detected.
        assert f"-f docker-compose.dev.yml run --rm api {self.SEED}" in calls
        assert f"poetry run {self.SEED}" not in calls


def _setup_recipe() -> list[str]:
    lines = (REPO_ROOT / "Makefile").read_text().splitlines()
    start = lines.index("setup:")
    recipe = []
    for line in lines[start + 1 :]:
        if not line.startswith("\t"):
            break
        recipe.append(line)
    return recipe


def test_setup_seeds_after_migrating_unless_skipped():
    recipe = _setup_recipe()
    migrate = next(i for i, line in enumerate(recipe) if "$(MAKE) migrate" in line)
    seed = next(i for i, line in enumerate(recipe) if "seed-demo" in line)
    assert migrate < seed
    assert '"$(SEED_DEMO)" != "false"' in recipe[seed]
