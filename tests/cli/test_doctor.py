"""`signupflow doctor` must be trustworthy, because it is what a stuck
contributor is told to run.

The app reads its configuration from the environment, so two people on the same
commit can get different behaviour with nothing in the repository to explain it.
An exported variable survives a fresh clone and overrides `.env`, so "re-clone
and try again" does not clear it and editing `.env` does not help. `doctor`
exists to make that visible instead of guessed at.

These tests run it as a subprocess with an explicitly controlled environment,
which is the only way to prove what it reports: an inherited variable from the
test runner would otherwise leak in and make the result meaningless.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Everything doctor inspects, cleared so each case starts from a known state.
_CONTROLLED = (
    "DATABASE_URL",
    "ENVIRONMENT",
    "SECRET_KEY",
    "REDIS_URL",
    "RATE_LIMIT_STORAGE",
    "RATE_LIMIT_REDIS_URL",
    "APP_URL",
    "FRONTEND_URL",
    "TESTING",
    "TENANCY_GUARD",
    "RELEASE_SHA",
    "SIGNUPFLOW_LOAD_DOTENV",
    "EMAIL_ENABLED",
    "SMS_ENABLED",
    "BILLING_ENABLED",
)


def run_doctor(cwd: Path, **overrides: str) -> subprocess.CompletedProcess:
    """Run doctor with a clean environment plus only the named overrides."""
    env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    env.update(overrides)
    return subprocess.run(
        [sys.executable, "-m", "api.cli.main", "doctor"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd,
        env=env,
    )


@pytest.fixture
def workdir(tmp_path: Path) -> Path:
    """A directory with no .env, so file state is explicit per test."""
    return tmp_path


class TestDoctorOnAHealthyMachine:
    def test_clean_environment_passes(self, workdir):
        """Nothing set anywhere is the supported default, and must exit 0."""
        result = run_doctor(workdir)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "No blocking problems found" in result.stdout

    def test_clean_environment_says_defaults_apply(self, workdir):
        """Silence is ambiguous; say explicitly that nothing is overriding."""
        result = run_doctor(workdir)
        assert "nothing set; every default applies" in result.stdout

    def test_reports_the_python_version_it_is_running(self, workdir):
        """The version gate is a common first-run failure, so name the version."""
        result = run_doctor(workdir)
        running = f"Python {sys.version_info.major}.{sys.version_info.minor}"
        assert running in result.stdout

    def test_absent_dotenv_is_not_reported_as_a_problem(self, workdir):
        """No .env is the normal case; it must not read as something missing."""
        result = run_doctor(workdir)
        assert "SQLite is the default" in result.stdout
        assert result.returncode == 0


class TestDoctorCatchesTheComposeHost:
    """The reported failure: a DATABASE_URL only resolvable inside compose."""

    COMPOSE_URL = "postgresql://signupflow:hunter2@db:5432/signupflow"

    def test_exported_compose_host_fails(self, workdir):
        result = run_doctor(workdir, DATABASE_URL=self.COMPOSE_URL)
        assert result.returncode == 1
        assert "docker-compose service name" in result.stdout

    def test_exported_value_is_attributed_to_the_shell(self, workdir):
        """Attribution decides the remedy, so it has to be right."""
        result = run_doctor(workdir, DATABASE_URL=self.COMPOSE_URL)
        assert "[from shell]" in result.stdout
        assert "came from your shell" in result.stdout

    def test_exported_value_is_told_to_unset_not_to_edit_dotenv(self, workdir):
        """Editing .env cannot fix an exported variable: dotenv will not override it."""
        result = run_doctor(workdir, DATABASE_URL=self.COMPOSE_URL)
        assert "unset DATABASE_URL" in result.stdout

    def test_dotenv_value_is_attributed_to_the_file(self, workdir):
        (workdir / ".env").write_text(f"DATABASE_URL={self.COMPOSE_URL}\n")
        result = run_doctor(workdir)
        assert result.returncode == 1
        assert "[from .env]" in result.stdout
        assert "came from your .env" in result.stdout

    def test_dotenv_value_is_told_to_edit_or_delete_the_file(self, workdir):
        (workdir / ".env").write_text(f"DATABASE_URL={self.COMPOSE_URL}\n")
        result = run_doctor(workdir)
        assert "sqlite:///./roster.db" in result.stdout
        assert "delete .env" in result.stdout

    def test_shell_wins_over_dotenv(self, workdir):
        """python-dotenv does not override an existing variable, so neither does doctor."""
        (workdir / ".env").write_text("DATABASE_URL=sqlite:///./roster.db\n")
        result = run_doctor(workdir, DATABASE_URL=self.COMPOSE_URL)
        assert result.returncode == 1
        assert "[from shell]" in result.stdout

    @pytest.mark.parametrize(
        "url",
        [
            "postgresql://u:p@db:5432/x",
            "postgresql://u:p@db/x",
            "postgresql+psycopg2://u:p@db:5432/x",
        ],
    )
    def test_compose_host_spellings_are_all_caught(self, workdir, url):
        """A port, a bare path, and a driver-qualified scheme are the same mistake."""
        assert run_doctor(workdir, DATABASE_URL=url).returncode == 1


class TestDoctorDoesNotCryWolf:
    """A diagnostic that false-positives gets ignored, which is worse than silence."""

    @pytest.mark.parametrize(
        "url",
        [
            "sqlite:///./roster.db",
            "postgresql://u:p@localhost:5432/x",
            "postgresql://u:p@127.0.0.1:5432/x",
            "postgresql://u:p@dbserver.example.com:5432/x",
            "postgresql://u:p@mydb:5432/x",
        ],
    )
    def test_reachable_hosts_are_accepted(self, workdir, url):
        result = run_doctor(workdir, DATABASE_URL=url)
        assert result.returncode == 0, f"{url} was wrongly rejected:\n{result.stdout}"


class TestDoctorProtectsCredentials:
    """Output is meant to be pasted into an issue, so it must be safe to paste."""

    def test_password_in_a_url_is_masked(self, workdir):
        result = run_doctor(workdir, DATABASE_URL="postgresql://someone:s3cr3t@localhost:5432/x")
        assert "s3cr3t" not in result.stdout
        assert "***" in result.stdout

    def test_secret_key_value_is_never_printed(self, workdir):
        result = run_doctor(workdir, SECRET_KEY="super-secret-signing-key")
        assert "super-secret-signing-key" not in result.stdout
        assert "<set," in result.stdout

    def test_the_variable_name_is_still_shown(self, workdir):
        """Redaction must not hide which variable is set, only its value."""
        result = run_doctor(workdir, SECRET_KEY="super-secret-signing-key")
        assert "SECRET_KEY" in result.stdout


class TestDoctorExplainsProductionMode:
    def test_production_environment_is_called_out(self, workdir):
        """Production startup is fail-closed, which surprises people locally."""
        result = run_doctor(workdir, ENVIRONMENT="production")
        assert "fail-closed" in result.stdout

    def test_development_environment_is_not_called_out(self, workdir):
        result = run_doctor(workdir, ENVIRONMENT="development")
        assert "fail-closed" not in result.stdout
        assert result.returncode == 0


class TestMakeDoctorMatchesTheCli:
    """The README tells people to run `make doctor`, so that path must work too."""

    def test_make_doctor_passes_on_a_clean_environment(self):
        env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
        result = subprocess.run(
            ["make", "doctor"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO_ROOT,
            env=env,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "No blocking problems found" in result.stdout

    def test_make_doctor_fails_on_the_compose_host(self):
        env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
        env["DATABASE_URL"] = "postgresql://u:p@db:5432/x"
        result = subprocess.run(
            ["make", "doctor"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO_ROOT,
            env=env,
        )
        assert result.returncode != 0
        assert "docker-compose service name" in result.stdout
