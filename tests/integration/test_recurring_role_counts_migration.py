"""Existing recurring occurrences gain the role key the solver reads.

Occurrences created before the fix stored their roles as ``role_requirements``
and were silently unschedulable. The migration moves them to ``role_counts``
without touching events that already have role counts or have no roles.
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRE_FIX_REVISION = "b0d3f6a8c1e2"


def _run_alembic(database_url: str, *arguments: str) -> None:
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


def _extra(connection, event_id):
    raw = connection.execute("SELECT extra_data FROM events WHERE id = ?", (event_id,)).fetchone()
    return None if raw[0] is None else json.loads(raw[0])


@pytest.mark.integration
def test_migration_moves_occurrence_roles_to_role_counts(tmp_path) -> None:
    database_path = tmp_path / "recurring-roles.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", PRE_FIX_REVISION)

    rows = {
        "legacy-occurrence": {"location": "Hall", "role_requirements": {"usher": 2}},
        "hand-made": {"role_counts": {"sound": 1}},
        "both-keys": {"role_counts": {"usher": 1}, "role_requirements": {"usher": 4}},
        "no-roles": {"location": "Hall", "role_requirements": None},
        "no-extra": None,
    }
    with sqlite3.connect(database_path) as connection:
        connection.execute("INSERT INTO organizations (id, name) VALUES ('org', 'Organization')")
        for event_id, extra in rows.items():
            connection.execute(
                """
                INSERT INTO events (id, org_id, type, start_time, end_time, is_sample,
                                    is_exception, extra_data)
                VALUES (?, 'org', 'Service', '2030-01-06 10:00:00', '2030-01-06 11:00:00',
                        0, 0, ?)
                """,
                (event_id, None if extra is None else json.dumps(extra)),
            )
        connection.commit()

    _run_alembic(database_url, "upgrade", "head")
    with sqlite3.connect(database_path) as connection:
        assert _extra(connection, "legacy-occurrence") == {
            "location": "Hall",
            "role_counts": {"usher": 2},
        }
        assert _extra(connection, "hand-made") == {"role_counts": {"sound": 1}}
        # Counts someone already set win over the stale series copy.
        assert _extra(connection, "both-keys") == {"role_counts": {"usher": 1}}
        assert _extra(connection, "no-roles") == {"location": "Hall"}
        assert _extra(connection, "no-extra") is None

    # Downgrade is a no-op for data: older code reads role_counts too.
    _run_alembic(database_url, "downgrade", PRE_FIX_REVISION)
    with sqlite3.connect(database_path) as connection:
        assert _extra(connection, "legacy-occurrence")["role_counts"] == {"usher": 2}
