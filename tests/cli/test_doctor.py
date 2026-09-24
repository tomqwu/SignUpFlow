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
import shutil
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
    "SENTRY_DSN",
)


def docker_stub(directory: Path, *, usable: bool) -> str:
    """A PATH whose ``docker`` answers ``docker info`` as a live or dead daemon.

    Doctor mirrors the Makefile, which routes a compose database through
    Docker, so whether Docker works decides the verdict. A stub makes that
    deterministic on any machine instead of depending on the test runner's.
    """
    bin_dir = directory / ("docker-up" if usable else "docker-down")
    bin_dir.mkdir(exist_ok=True)
    stub = bin_dir / "docker"
    stub.write_text(f"#!/bin/sh\nexit {0 if usable else 1}\n")
    stub.chmod(0o755)
    return f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"


def run_doctor(
    cwd: Path, *, docker: bool | None = None, **overrides: str
) -> subprocess.CompletedProcess:
    """Run doctor with a clean environment plus only the named overrides.

    ``docker`` stubs a usable (True) or unusable (False) Docker; None leaves
    the runner's own PATH alone.
    """
    env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    env.update(overrides)
    if docker is not None:
        env["PATH"] = docker_stub(cwd, usable=docker)
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


def poetry_stub(directory: Path, *, version: str) -> str:
    """A PATH whose ``poetry`` reports an environment running ``version``."""
    bin_dir = directory / f"poetry-{version}"
    bin_dir.mkdir(exist_ok=True)
    interpreter = bin_dir / "env-python"
    interpreter.write_text(f"#!/bin/sh\necho {version}\n")
    interpreter.chmod(0o755)
    poetry = bin_dir / "poetry"
    poetry.write_text(f"#!/bin/sh\necho {interpreter}\n")
    poetry.chmod(0o755)
    return f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"


class TestDoctorChecksThePythonTheAppRunsOn:
    """The app runs in Poetry's environment, not on whatever ``python3`` is.

    ``make doctor`` runs under the system ``python3``, which may be newer than
    the project supports while the Poetry environment is fine. Judging the
    wrong interpreter blocks a working machine.
    """

    def test_a_supported_poetry_environment_passes(self, workdir):
        result = run_doctor(workdir, PATH=poetry_stub(workdir, version="3.12"))
        assert "Python 3.12" in result.stdout
        assert "Poetry environment" in result.stdout
        assert "outside the supported" not in result.stdout
        assert result.returncode == 0, result.stdout

    def test_an_unsupported_poetry_environment_fails(self, workdir):
        result = run_doctor(workdir, PATH=poetry_stub(workdir, version="3.14"))
        assert "Python 3.14 is outside the supported" in result.stdout
        assert result.returncode == 1


class TestDoctorCatchesTheComposeHost:
    """A DATABASE_URL on the compose host with no Docker to route it through.

    ``make setup`` and ``make up`` send a compose database through Docker, so
    this is only fatal when Docker cannot be reached. That is the case covered
    here; the Docker path itself is ``TestDoctorFollowsTheDockerPath``.
    """

    COMPOSE_URL = "postgresql://signupflow:hunter2@db:5432/signupflow"

    def test_exported_compose_host_fails(self, workdir):
        result = run_doctor(workdir, docker=False, DATABASE_URL=self.COMPOSE_URL)
        assert result.returncode == 1
        assert "docker-compose service name" in result.stdout
        assert "Docker is unavailable" in result.stdout

    def test_exported_value_is_attributed_to_the_shell(self, workdir):
        """Attribution decides the remedy, so it has to be right."""
        result = run_doctor(workdir, docker=False, DATABASE_URL=self.COMPOSE_URL)
        assert "[from shell]" in result.stdout
        assert "came from your shell" in result.stdout

    def test_exported_value_is_told_to_unset_not_to_edit_dotenv(self, workdir):
        """Editing .env cannot fix an exported variable: dotenv will not override it."""
        result = run_doctor(workdir, docker=False, DATABASE_URL=self.COMPOSE_URL)
        assert "unset DATABASE_URL" in result.stdout

    def test_dotenv_value_is_attributed_to_the_file(self, workdir):
        (workdir / ".env").write_text(f"DATABASE_URL={self.COMPOSE_URL}\n")
        result = run_doctor(workdir, docker=False)
        assert result.returncode == 1
        assert "[from .env]" in result.stdout
        assert "came from your .env" in result.stdout

    def test_dotenv_value_is_told_to_edit_or_delete_the_file(self, workdir):
        (workdir / ".env").write_text(f"DATABASE_URL={self.COMPOSE_URL}\n")
        result = run_doctor(workdir, docker=False)
        assert "sqlite:///./roster.db" in result.stdout
        assert "delete .env" in result.stdout

    def test_shell_wins_over_dotenv(self, workdir):
        """python-dotenv does not override an existing variable, so neither does doctor."""
        (workdir / ".env").write_text("DATABASE_URL=sqlite:///./roster.db\n")
        result = run_doctor(workdir, docker=False, DATABASE_URL=self.COMPOSE_URL)
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
        assert run_doctor(workdir, docker=False, DATABASE_URL=url).returncode == 1

    def test_other_compose_service_names_fail_even_with_docker(self, workdir):
        """Only 'db' is routed through compose; 'postgres' resolves nowhere."""
        result = run_doctor(workdir, docker=True, DATABASE_URL="postgresql://u:p@postgres:5432/x")
        assert result.returncode == 1
        assert "docker-compose service name" in result.stdout


class TestDoctorFollowsTheDockerPath:
    """The README's Docker path sets DATABASE_URL to the compose host on purpose.

    With Docker usable, ``make setup`` and ``make up`` run the database and the
    app inside compose, so doctor must not call that configuration broken. It
    still says which commands can and cannot reach the database.
    """

    COMPOSE_URL = "postgresql://signupflow:hunter2@db:5432/signupflow"

    def test_compose_database_with_docker_passes(self, workdir):
        result = run_doctor(workdir, docker=True, DATABASE_URL=self.COMPOSE_URL)
        assert result.returncode == 0, result.stdout
        assert "No blocking problems found" in result.stdout

    def test_it_names_the_commands_that_work(self, workdir):
        result = run_doctor(workdir, docker=True, DATABASE_URL=self.COMPOSE_URL)
        assert "make setup" in result.stdout
        assert "make up" in result.stdout
        assert "docker compose" in result.stdout

    def test_it_still_explains_the_host_only_alternative(self, workdir):
        (workdir / ".env").write_text(f"DATABASE_URL={self.COMPOSE_URL}\n")
        result = run_doctor(workdir, docker=True)
        assert "came from your .env" in result.stdout
        assert "sqlite:///./roster.db" in result.stdout


class TestDoctorCatchesAPlaceholderSentryDsn:
    """Any SENTRY_DSN turns error reporting on, and startup fails closed on a
    DSN the SDK cannot parse, so an old .env placeholder stops the app."""

    PLACEHOLDER = "https://your_sentry_dsn_here@sentry.io/project_id"
    VALID = "https://0123456789abcdef@o1.ingest.sentry.io/4506"

    def test_placeholder_dsn_is_a_blocking_problem(self, workdir):
        (workdir / ".env").write_text(f"SENTRY_DSN={self.PLACEHOLDER}\n")
        result = run_doctor(workdir)
        assert result.returncode == 1
        assert "SENTRY_DSN" in result.stdout
        assert "not a valid Sentry DSN" in result.stdout

    def test_valid_dsn_passes(self, workdir):
        result = run_doctor(workdir, SENTRY_DSN=self.VALID)
        assert result.returncode == 0, result.stdout

    def test_empty_dsn_means_reporting_is_off(self, workdir):
        (workdir / ".env").write_text("SENTRY_DSN=\n")
        assert run_doctor(workdir).returncode == 0

    def test_dsn_key_is_never_printed(self, workdir):
        result = run_doctor(workdir, SENTRY_DSN=self.VALID)
        assert "0123456789abcdef" not in result.stdout
        assert "SENTRY_DSN = <set," in result.stdout


class TestDoctorReadsDotenvLikeTheApp:
    def test_inline_comment_is_not_part_of_the_value(self, workdir):
        """python-dotenv drops ' # ...' from unquoted values, so doctor must too."""
        (workdir / ".env").write_text(
            "ENVIRONMENT=development  # Options: development, staging, production\n"
        )
        result = run_doctor(workdir)
        assert "ENVIRONMENT = development   [from .env]" in result.stdout
        assert "Options" not in result.stdout

    def test_hash_inside_quotes_is_kept(self, workdir):
        (workdir / ".env").write_text('APP_URL="http://localhost:8000/#top"\n')
        result = run_doctor(workdir)
        assert "APP_URL = http://localhost:8000/#top   [from .env]" in result.stdout

    def test_inline_production_comment_still_counts_as_production(self, workdir):
        (workdir / ".env").write_text("ENVIRONMENT=production # live\n")
        result = run_doctor(workdir)
        assert "fail-closed" in result.stdout


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

    def test_password_with_no_username_is_masked(self, workdir):
        """Redis URLs carry the password alone, with an empty username.

        A pattern that requires at least one character before the colon skips
        these entirely and prints the password in full, which is exactly the
        shape the default Redis URL takes once it is given a password.
        """
        result = run_doctor(workdir, REDIS_URL="redis://:s3cr3t@localhost:6379/0")
        assert "s3cr3t" not in result.stdout
        assert "***" in result.stdout

    def test_password_in_a_query_parameter_is_masked(self, workdir):
        """Not every credential sits in the userinfo part of a URL."""
        result = run_doctor(
            workdir,
            DATABASE_URL="postgresql://someone@localhost:5432/x?password=s3cr3t",
        )
        assert "s3cr3t" not in result.stdout

    def test_masking_keeps_enough_of_the_url_to_diagnose_it(self, workdir):
        """Redaction that hid the host would defeat the point of the report."""
        result = run_doctor(workdir, DATABASE_URL="postgresql://someone:s3cr3t@db:5432/x")
        assert "s3cr3t" not in result.stdout
        assert "someone" in result.stdout
        assert "db:5432" in result.stdout


class TestDoctorExplainsProductionMode:
    def test_production_environment_is_called_out(self, workdir):
        """Production startup is fail-closed, which surprises people locally."""
        result = run_doctor(workdir, ENVIRONMENT="production")
        assert "fail-closed" in result.stdout

    def test_development_environment_is_not_called_out(self, workdir):
        result = run_doctor(workdir, ENVIRONMENT="development")
        assert "fail-closed" not in result.stdout
        assert result.returncode == 0


@pytest.fixture
def make_checkout(tmp_path: Path) -> Path:
    """The Makefile and doctor script alone, with no .env.

    Running `make doctor` from the repository root would read the developer's
    own .env, so a machine set up for Docker would fail the "clean" case.
    Doctor imports nothing from ``api``, so these two files are all it needs.
    """
    (tmp_path / "scripts").mkdir()
    shutil.copy(REPO_ROOT / "Makefile", tmp_path / "Makefile")
    shutil.copy(REPO_ROOT / "scripts" / "doctor.py", tmp_path / "scripts" / "doctor.py")
    return tmp_path


def run_make_doctor(
    cwd: Path, *, docker: bool | None = None, **overrides: str
) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in _CONTROLLED}
    env.update(overrides)
    if docker is not None:
        env["PATH"] = docker_stub(cwd, usable=docker)
    return subprocess.run(
        ["make", "doctor"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=cwd,
        env=env,
    )


class TestMakeDoctorMatchesTheCli:
    """The README tells people to run `make doctor`, so that path must work too."""

    def test_make_doctor_passes_on_a_clean_environment(self, make_checkout):
        result = run_make_doctor(make_checkout)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "No blocking problems found" in result.stdout

    def test_make_doctor_fails_on_the_compose_host(self, make_checkout):
        result = run_make_doctor(
            make_checkout, docker=False, DATABASE_URL="postgresql://u:p@db:5432/x"
        )
        assert result.returncode != 0
        assert "docker-compose service name" in result.stdout

    def test_make_doctor_reads_dotenv_from_the_checkout(self, make_checkout):
        (make_checkout / ".env").write_text("DATABASE_URL=postgresql://u:p@db:5432/x\n")
        result = run_make_doctor(make_checkout, docker=False)
        assert result.returncode != 0
        assert "came from your .env" in result.stdout
