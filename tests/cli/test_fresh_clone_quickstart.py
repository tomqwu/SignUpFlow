"""The README's Quick Start must work on a machine that has never run this.

Every previous claim that setup worked was made from a checkout that had
already been built, in a shell with nothing set. That is not the situation a
new contributor is in, and it is exactly why a broken Quick Start survived: the
thing being verified was never the thing being documented.

These tests clone the repository into a temporary directory and run the
documented commands there, with the environment controlled explicitly. They are
slow and marked so, but they are the only evidence that the first page of the
README is true.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_CONTROLLED = (
    "DATABASE_URL",
    "ENVIRONMENT",
    "SECRET_KEY",
    "TESTING",
    "SIGNUPFLOW_LOAD_DOTENV",
    "SIGNUPFLOW_TEST_DATABASE_URL",
)

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(shutil.which("git") is None, reason="git is required to clone"),
]


def _docker_is_usable() -> bool:
    """Match the Makefile: the binary existing is not the same as a live daemon."""
    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode == 0


def clean_env(**overrides: str) -> dict:
    """The environment a new contributor has: none of ours, plus any overrides."""
    env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    env.update(overrides)
    return env


@pytest.fixture(scope="module")
def fresh_clone(tmp_path_factory) -> Path:
    """A clone of the repository at HEAD, with no build artifacts and no .env.

    This clones the committed state, not the working tree, which is deliberate:
    a contributor gets what was committed. It does mean a fix must be committed
    before these tests can see it, so a failure here on freshly edited code
    usually means the change is still uncommitted rather than wrong.
    """
    target = tmp_path_factory.mktemp("quickstart") / "SignUpFlow"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(REPO_ROOT), str(target)],
        check=True,
        capture_output=True,
        timeout=300,
    )
    # A clone carries committed files only, so prove the premises of the docs.
    assert not (target / ".env").exists(), "a fresh clone must not carry a .env"
    assert not (target / "roster.db").exists(), "a fresh clone must not carry a database"
    return target


class TestFreshCloneStartsClean:
    def test_clone_has_no_ambient_configuration(self, fresh_clone):
        """The premise of the whole Quick Start: nothing is configured yet."""
        assert not (fresh_clone / ".env").exists()

    def test_doctor_reports_a_healthy_machine(self, fresh_clone):
        """Step 1 tells the reader to run this first, so it must pass here."""
        result = subprocess.run(
            [sys.executable, "-m", "api.cli.main", "doctor"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=fresh_clone,
            env=clean_env(),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "No blocking problems found" in result.stdout

    def test_alembic_creates_the_database_from_nothing(self, fresh_clone):
        """What `make setup` ends with, run directly so the failure is legible."""
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=fresh_clone,
            env=clean_env(),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert (fresh_clone / "roster.db").exists(), "migrations did not create roster.db"


class TestFreshCloneSurfacesAmbientState:
    """The failure a new contributor actually hits, reproduced from a clone."""

    def test_exported_compose_host_is_caught_before_migrating(self, fresh_clone):
        """An exported variable survives cloning, so cloning again cannot fix it."""
        result = subprocess.run(
            [sys.executable, "-m", "api.cli.main", "doctor"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=fresh_clone,
            env=clean_env(DATABASE_URL="postgresql://u:p@db:5432/x"),
        )
        assert result.returncode == 1
        assert "survives a fresh clone" in result.stdout

    @pytest.mark.skipif(
        _docker_is_usable(),
        reason="asserts the branch taken when Docker cannot be reached",
    )
    def test_make_migrate_refuses_rather_than_raising_psycopg2(self, fresh_clone):
        """Without the guard this dies inside alembic naming neither cause nor fix.

        A compose hostname resolves only inside that network, so migrating from
        the host could never work. With Docker present the migration is routed
        into the container instead, which is why this only covers the case
        where Docker is unavailable.
        """
        result = subprocess.run(
            ["make", "migrate"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=fresh_clone,
            env=clean_env(DATABASE_URL="postgresql://u:p@db:5432/x"),
        )
        assert result.returncode != 0
        assert "could not translate host name" not in result.stdout + result.stderr
        # Wrapped across lines for the terminal, so compare on the words alone.
        assert "only resolves inside docker compose" in " ".join(result.stdout.split())

    @pytest.mark.skipif(
        _docker_is_usable(),
        reason="asserts the branch taken when Docker cannot be reached",
    )
    def test_services_refuses_rather_than_starting_half_a_stack(self, fresh_clone):
        """An unreachable Docker must stop setup, not be reported as success.

        This exists because it did not: the guard ran inside a shell ``case``
        whose subsequent commands kept going, so the target printed its failure
        and then its success line and exited zero, and ``make setup`` carried on
        to migrate against a database that was never started.
        """
        result = subprocess.run(
            ["make", "services"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=fresh_clone,
            env=clean_env(DATABASE_URL="postgresql://u:p@db:5432/x"),
        )
        assert result.returncode != 0
        assert "Backing services are up" not in result.stdout


class TestLifecycleIsTwoCommands:
    """``make setup`` prepares the environment; ``make up`` runs the app.

    Both follow DATABASE_URL rather than the name of the target, so neither can
    be typed into the wrong path. These assert the routing without starting
    anything, which is what keeps them runnable on a machine without Docker.

    ``--dry-run`` still descends into sub-makes, so the branch that was taken is
    visible. It is read from the command the chosen branch would run, not from
    the branch names, because make echoes the whole ``case`` either way.
    """

    UVICORN = "uvicorn api.main:app"
    COMPOSE_UP = "docker-compose.dev.yml up -d"

    def _dry_run_up(self, cwd, **env: str) -> str:
        result = subprocess.run(
            ["make", "--dry-run", "up"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=cwd,
            env=clean_env(**env),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    def test_up_serves_on_the_host_when_no_compose_database_is_configured(
        self, fresh_clone
    ):
        """The default path must not reach for Docker at all."""
        stdout = self._dry_run_up(fresh_clone)
        assert self.UVICORN in stdout
        assert self.COMPOSE_UP not in stdout

    def test_up_routes_into_compose_when_the_database_lives_there(self, fresh_clone):
        stdout = self._dry_run_up(fresh_clone, DATABASE_URL="postgresql://u:p@db:5432/x")
        assert self.COMPOSE_UP in stdout
        assert self.UVICORN not in stdout

    def test_setup_points_at_up_rather_than_leaving_the_app_unstarted(
        self, fresh_clone
    ):
        """Setup stops short of serving, so it has to say what comes next."""
        makefile = (fresh_clone / "Makefile").read_text(encoding="utf-8")
        assert "Run 'make up' to start the app." in makefile
