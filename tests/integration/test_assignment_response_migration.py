"""Migration preserves allocations without inventing historical acknowledgements."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRE_RESPONSE_REVISION = "c5d7e9f1a3b4"


def _run_alembic(database_url: str, *arguments: str):
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    environment["TESTING"] = "true"
    subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.integration
def test_upgrade_marks_legacy_confirmed_assignment_unanswered(tmp_path):
    database_path = tmp_path / "assignment-response-migration.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", PRE_RESPONSE_REVISION)

    with sqlite3.connect(database_path) as connection:
        connection.execute("INSERT INTO organizations (id, name) VALUES ('org', 'Organization')")
        connection.execute(
            """
            INSERT INTO people (id, org_id, name, email, timezone, language, status, is_sample,
                                refresh_token_version)
            VALUES ('member', 'org', 'Member', 'member@example.com', 'UTC', 'en', 'active', 0, 0)
            """
        )
        connection.execute(
            """
            INSERT INTO events
                (id, org_id, type, start_time, end_time, is_sample, extra_data, is_exception)
            VALUES ('event', 'org', 'service', '2030-01-01 10:00:00',
                    '2030-01-01 11:00:00', 0, '{}', 0)
            """
        )
        connection.execute(
            """
            INSERT INTO assignments (event_id, person_id, role, status)
            VALUES ('event', 'member', 'usher', 'confirmed')
            """
        )
        connection.commit()

    _run_alembic(database_url, "upgrade", "head")

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT status, response_status, responded_by_person_id, responded_at,
                   commitment_revision, response_revision
            FROM assignments
            """
        ).fetchone()
        assert row == ("confirmed", "pending", None, None, 1, None)

    _run_alembic(database_url, "downgrade", PRE_RESPONSE_REVISION)
    with sqlite3.connect(database_path) as connection:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(assignments)").fetchall()
        }
        assert "response_status" not in columns
        assert connection.execute("SELECT status FROM assignments").fetchone() == ("confirmed",)

    _run_alembic(database_url, "upgrade", "head")
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT status, response_status, commitment_revision FROM assignments"
        ).fetchone()
        assert row == ("confirmed", "pending", 1)
