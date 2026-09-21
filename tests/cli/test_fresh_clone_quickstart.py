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

    def test_make_migrate_refuses_rather_than_raising_psycopg2(self, fresh_clone):
        """Without the guard this dies inside alembic naming neither cause nor fix."""
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
        assert "only resolves inside docker compose" in result.stdout
