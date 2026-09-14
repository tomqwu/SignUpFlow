"""Solution-scope migration preserves legacy rows without inventing scope."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRE_SCOPE_REVISION = "d6e8f0a2b4c6"


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


@pytest.mark.integration
def test_scope_migration_keeps_legacy_solution_explicitly_unscoped(tmp_path):
    database_path = tmp_path / "solution-scope-migration.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", PRE_SCOPE_REVISION)

    with sqlite3.connect(database_path) as connection:
        connection.execute("INSERT INTO organizations (id, name) VALUES ('org', 'Organization')")
        connection.execute(
            """
            INSERT INTO solutions
                (org_id, solve_ms, hard_violations, soft_score, health_score,
                 is_published, metrics)
            VALUES ('org', 1.0, 0, 1.0, 100.0, 0, '{}')
            """
        )
        connection.commit()

    _run_alembic(database_url, "upgrade", "head")

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT scope_start, scope_end, scope_event_ids, scope_fingerprint
            FROM solutions
            """
        ).fetchone()
        assert row == (None, None, None, None)

    _run_alembic(database_url, "downgrade", PRE_SCOPE_REVISION)
    with sqlite3.connect(database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(solutions)")}
        assert "scope_start" not in columns
        assert connection.execute("SELECT COUNT(*) FROM solutions").fetchone() == (1,)

    _run_alembic(database_url, "upgrade", "head")
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT scope_event_ids FROM solutions").fetchone() == (None,)
