"""Notification outbox migration preserves existing intent rows."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRE_OUTBOX_REVISION = "a9c2e4f6b8d0"


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
def test_outbox_migration_preserves_pending_intent_and_round_trips(tmp_path) -> None:
    database_path = tmp_path / "notification-outbox.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", PRE_OUTBOX_REVISION)

    with sqlite3.connect(database_path) as connection:
        connection.execute("INSERT INTO organizations (id, name) VALUES ('org', 'Organization')")
        connection.execute(
            """
            INSERT INTO people
                (id, org_id, name, roles, timezone, language, status,
                 is_sample, refresh_token_version)
            VALUES ('person', 'org', 'Member', '["volunteer"]', 'UTC', 'en',
                    'active', 0, 0)
            """
        )
        connection.execute(
            """
            INSERT INTO notifications
                (org_id, recipient_id, type, status, retry_count, delivery_key)
            VALUES ('org', 'person', 'reminder', 'pending', 0, 'operation:1')
            """
        )
        connection.commit()

    _run_alembic(database_url, "upgrade", "head")
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT status, delivery_attempts, delivery_lease_token, next_attempt_at
            FROM notifications
            """
        ).fetchone()
        assert row == ("pending", 0, None, None)

    _run_alembic(database_url, "downgrade", PRE_OUTBOX_REVISION)
    with sqlite3.connect(database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(notifications)")}
        assert "delivery_attempts" not in columns
        assert connection.execute("SELECT COUNT(*) FROM notifications").fetchone() == (1,)
