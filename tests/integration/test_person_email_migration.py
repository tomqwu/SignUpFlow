"""Migration acceptance for globally unique login emails."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _run_alembic(database_url: str, *arguments: str, check: bool = True):
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    environment["TESTING"] = "true"
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=check,
        capture_output=True,
        text=True,
    )


@pytest.mark.integration
def test_person_email_migration_enforces_uniqueness_and_rejects_legacy_duplicates(tmp_path):
    database_path = tmp_path / "email-migration.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "head")

    with sqlite3.connect(database_path) as connection:
        connection.execute("INSERT INTO organizations (id, name) VALUES ('org', 'Organization')")
        connection.execute(
            """
            INSERT INTO people
                (id, org_id, name, email, timezone, language, status, is_sample,
                 refresh_token_version)
            VALUES
                ('first', 'org', 'First', 'duplicate@example.com', 'UTC', 'en',
                 'active', 0, 0)
            """
        )
        connection.commit()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO people
                    (id, org_id, name, email, timezone, language, status, is_sample,
                     refresh_token_version)
                VALUES
                    ('second', 'org', 'Second', 'duplicate@example.com', 'UTC', 'en',
                     'active', 0, 0)
                """
            )

    _run_alembic(database_url, "downgrade", "b4e6f8a2c5d3")
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO people
                (id, org_id, name, email, timezone, language, status, is_sample,
                 refresh_token_version)
            VALUES
                ('second', 'org', 'Second', 'duplicate@example.com', 'UTC', 'en',
                 'active', 0, 0)
            """
        )
        connection.commit()

    rejected = _run_alembic(database_url, "upgrade", "head", check=False)
    assert rejected.returncode != 0
    assert "Cannot enforce unique person emails" in rejected.stderr
