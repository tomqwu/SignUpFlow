"""Shared validation and rendering helpers for read-only SQLite inspection tools."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from pathlib import Path


def require_database(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ValueError(f"Refusing symlink database path: {path}")
    if not path.is_file():
        raise ValueError(f"Database must be an existing regular file: {path}")
    return path.resolve(strict=True)


def connect_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def require_read_query(query: str) -> str:
    statement = query.strip()
    first_word = statement.split(maxsplit=1)[0].upper() if statement else ""
    if first_word not in {"SELECT", "WITH", "EXPLAIN"}:
        raise ValueError("Custom SQL is read-only; use SELECT, WITH, or EXPLAIN.")
    return statement


def table_names(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return [str(row[0]) for row in rows]


def require_table(connection: sqlite3.Connection, value: str) -> str:
    if value not in table_names(connection):
        raise ValueError(f"Unknown table: {value}")
    return value


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def print_rows(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    print("\t".join(headers))
    for row in rows:
        print("\t".join("" if value is None else str(value) for value in row))
