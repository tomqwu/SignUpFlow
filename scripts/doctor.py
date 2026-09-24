#!/usr/bin/env python3
"""Report the environment this machine will actually start SignUpFlow with.

This deliberately uses nothing but the standard library and imports nothing
from ``api``. Its whole job is to explain why setup fails, so it has to run
*before* ``make setup`` has created a virtualenv. A diagnostic that needs the
dependencies it is diagnosing is useless at the only moment it is needed.

Run it directly (``python3 scripts/doctor.py``), through ``make doctor``, or as
``signupflow doctor`` once the package is installed.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

#: Ambient variables that change how the app starts. Anything set here comes
#: from outside the repository, so a fresh clone cannot make it go away and a
#: contributor has no way to see it without being told to look.
AMBIENT_VARS = (
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

#: A Sentry DSN embeds its client key, so it is treated as a secret too.
_SECRET_PARTS = ("SECRET", "TOKEN", "PASSWORD", "KEY", "DSN")

#: The shape sentry_sdk accepts: a key, a host and a numeric project id.
_SENTRY_DSN = re.compile(r"^https?://[^@/\s]+@[^/\s]+/(?:\S*/)?\d+/?$")

#: Compose service names. A URL pointing at one of these resolves only inside
#: the compose network, so on the host it cannot be reached at all.
_COMPOSE_HOSTS = {"db", "redis", "postgres"}

#: The compose database the Makefile routes through Docker (its
#: COMPOSE_DB_PATTERNS). With Docker usable, ``make setup`` and ``make up`` run
#: inside compose, so this host is the Docker path rather than a mistake.
_ROUTED_COMPOSE_HOST = "db"

MIN_PYTHON = (3, 11)
MAX_PYTHON = (3, 13)


#: Query parameters that carry a credential. A URL can hold one outside the
#: userinfo part entirely, which the userinfo pattern below would walk past.
_SECRET_PARAMS = re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api[-_]?key|auth)=([^&#\s]+)")

#: The userinfo credential. The username is optional on purpose: a Redis URL
#: with a password and no user is spelled ``redis://:secret@host``, and a
#: pattern demanding a username skips it and prints the password in full.
_URL_CREDENTIAL = re.compile(r"://([^:/@]*):[^@/]*@")


def redact(name: str, value: str) -> str:
    """Never print a credential, and never print a password inside a URL.

    The report is written to be pasted into an issue, so this has to hold for
    whatever shape the value arrives in, not only the common one. What survives
    is everything needed to diagnose the value: scheme, user, host, port, path.
    """
    if any(part in name for part in _SECRET_PARTS):
        return f"<set, {len(value)} chars>"
    masked = _URL_CREDENTIAL.sub(r"://\1:***@", value)
    return _SECRET_PARAMS.sub(r"\1=***", masked)


def dotenv_values(path: Path) -> dict[str, str]:
    """Parse .env well enough to report it, tolerating export and quotes."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        key, sep, value = line.partition("=")
        if not sep:
            continue
        values[key.strip()] = _dotenv_value(value.strip())
    return values


def _dotenv_value(value: str) -> str:
    """Read one value the way python-dotenv does.

    A quoted value keeps everything inside its quotes, ``#`` included. An
    unquoted value ends at whitespace followed by ``#``, which starts a comment.
    """
    if value[:1] in {"'", '"'}:
        closing = value.find(value[0], 1)
        if closing != -1:
            return value[1:closing]
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def docker_usable() -> bool:
    """Match the Makefile's require-docker: a binary and a live daemon."""
    docker = shutil.which("docker")
    if docker is None:
        return False
    try:
        return subprocess.run([docker, "info"], capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def poetry_python(root: Path) -> tuple[str, str] | None:
    """The interpreter and version of this project's Poetry environment, if any.

    The app runs there, not on whichever ``python3`` launched this script, so
    that is the version that has to be in range.
    """
    poetry = shutil.which("poetry")
    if poetry is None:
        return None
    try:
        found = subprocess.run(
            [poetry, "env", "info", "--executable"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=root,
        )
        executable = found.stdout.strip()
        if found.returncode != 0 or not executable:
            return None
        probed = subprocess.run(
            [executable, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    version = probed.stdout.strip()
    if probed.returncode != 0 or not re.fullmatch(r"\d+\.\d+", version):
        return None
    return executable, version


def database_url_findings(value: str, source: str) -> tuple[list[str], list[str]]:
    """Explain a DATABASE_URL on a compose host. Returns (problems, notes)."""
    # The scheme may carry a driver and digits, as in postgresql+psycopg2://.
    host = re.sub(r"^[A-Za-z0-9+.\-]+://(?:[^@/]*@)?", "", value).split("/")[0].split(":")[0]
    if host not in _COMPOSE_HOSTS:
        return [], []
    if source == "shell":
        fix = (
            "It is exported in your shell, so it survives a fresh clone and overrides "
            ".env. Run 'unset DATABASE_URL' and remove the export from your shell "
            "profile."
        )
    else:
        fix = "Set DATABASE_URL=sqlite:///./roster.db in .env, or delete .env."

    if host == _ROUTED_COMPOSE_HOST and docker_usable():
        return [], [
            f"DATABASE_URL names the compose database '{host}', so 'make setup' and "
            "'make up' run the database and the app inside docker compose. Host-only "
            "commands such as 'make serve' cannot reach it. The value came from your "
            f"{source}. For a host-only setup instead: {fix}"
        ]

    reason = (
        "Docker is unavailable, so 'make setup' cannot route it through compose. "
        if host == _ROUTED_COMPOSE_HOST
        else ""
    )
    return [
        f"DATABASE_URL host '{host}' is a docker-compose service name and resolves only "
        f"inside that network, so it cannot be reached from the host. {reason}"
        f"The value came from your {source}. {fix} "
        "To use a real PostgreSQL server from the host, point at its published port."
    ], []


def report(root: Path | None = None) -> int:
    """Print the environment report. Returns the intended process exit code."""
    root = root or Path.cwd()
    problems: list[str] = []
    notes: list[str] = []

    print("SignUpFlow environment report")
    print("=" * 60)

    environment = poetry_python(root)
    if environment is not None:
        executable, version = environment
        print(f"\nPython {version} (Poetry environment: {executable})")
    else:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"\nPython {version} ({sys.executable}; no Poetry environment yet)")
    running = tuple(int(part) for part in version.split("."))
    if not MIN_PYTHON <= running <= MAX_PYTHON:
        problems.append(
            f"Python {version} is outside the supported "
            f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]} to {MAX_PYTHON[0]}.{MAX_PYTHON[1]} range."
        )

    env_path = root / ".env"
    file_values = dotenv_values(env_path)
    print(f".env: {'present' if env_path.exists() else 'absent (fine; SQLite is the default)'}")

    print("\nEffective configuration")
    print("-" * 60)
    reported = False
    for name in AMBIENT_VARS:
        shell_value = os.environ.get(name)
        if shell_value is not None:
            source, value = "shell", shell_value
        elif name in file_values:
            source, value = ".env", file_values[name]
        else:
            continue
        reported = True
        print(f"  {name} = {redact(name, value)}   [from {source}]")
        if name == "SENTRY_DSN" and value and not _SENTRY_DSN.match(value):
            problems.append(
                f"SENTRY_DSN is set but is not a valid Sentry DSN, so startup fails "
                f"closed when it initialises error reporting. The value came from your "
                f"{source}. Leave it empty to turn error reporting off, or paste the "
                "DSN from your Sentry project settings."
            )
        if name == "DATABASE_URL":
            db_problems, db_notes = database_url_findings(value, source)
            problems.extend(db_problems)
            notes.extend(db_notes)
    if not reported:
        print("  (nothing set; every default applies)")

    if os.environ.get("ENVIRONMENT", file_values.get("ENVIRONMENT", "")) == "production":
        notes.append(
            "ENVIRONMENT=production makes startup fail-closed. It requires an explicit "
            "SECRET_KEY and rejects a SQLite database. Unset it for local development."
        )

    print("\nVerdict")
    print("-" * 60)
    for note in notes:
        print(f"  note: {note}")
    if problems:
        for problem in problems:
            print(f"  problem: {problem}")
        print("\nThe app will not start until the problems above are resolved.")
        return 1
    print("  No blocking problems found.")
    if not notes:
        print("  'make setup' then 'make up' should work on this machine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(report())
