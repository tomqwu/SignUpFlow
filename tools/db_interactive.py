#!/usr/bin/env python3
"""Interactively inspect an explicit SQLite database in read-only mode."""

from __future__ import annotations

import argparse
import sqlite3
import sys

from sqlite_readonly import (
    connect_read_only,
    print_rows,
    quote_identifier,
    require_database,
    require_read_query,
    require_table,
    table_names,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db", help="Existing SQLite database path; symlinks are refused")
    args = parser.parse_args()

    try:
        path = require_database(args.db)
        with connect_read_only(path) as connection:
            tables = table_names(connection)
            print(f"Database (read-only): {path}")
            print("Commands: table name, schema <table>, sql <read query>, quit")
            while True:
                try:
                    command = input("signupflow-db> ").strip()
                except EOFError:
                    break
                if command.lower() in {"exit", "quit", "q"}:
                    break
                if command.lower().startswith("schema "):
                    table = require_table(connection, command.split(maxsplit=1)[1])
                    rows = connection.execute(
                        f"PRAGMA table_info({quote_identifier(table)})"
                    ).fetchall()
                    print_rows(("id", "name", "type", "notnull", "default", "pk"), rows)
                elif command.lower().startswith("sql "):
                    cursor = connection.execute(require_read_query(command[4:]))
                    headers = [column[0] for column in cursor.description or []]
                    print_rows(headers, cursor.fetchmany(1000))
                elif command in tables:
                    cursor = connection.execute(
                        f"SELECT * FROM {quote_identifier(command)} LIMIT 20"
                    )
                    headers = [column[0] for column in cursor.description or []]
                    print_rows(headers, cursor.fetchall())
                elif command:
                    print(f"Unknown read-only command or table: {command}", file=sys.stderr)
    except (sqlite3.Error, ValueError) as exc:
        print(f"Database inspection refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
