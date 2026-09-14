"""SQLite development databases are private to their owning user."""

from __future__ import annotations

from api.database import _prepare_sqlite_file


def test_prepare_sqlite_file_uses_owner_only_permissions(tmp_path):
    database = tmp_path / "nested" / "roster.db"

    _prepare_sqlite_file(database, f"sqlite:///{database}")

    assert database.stat().st_mode & 0o777 == 0o600
