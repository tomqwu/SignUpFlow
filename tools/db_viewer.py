#!/usr/bin/env python3
"""Inspect an explicitly selected SQLite database without allowing writes."""

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
    parser.add_argument("-t", "--table", help="Show one table")
    parser.add_argument("-q", "--query", help="Run a read-only SELECT, WITH, or EXPLAIN query")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Rows to show (1-1000)")
    args = parser.parse_args()

    try:
        if args.table and args.query:
            raise ValueError("Choose either --table or --query, not both.")
        if not 1 <= args.limit <= 1000:
            raise ValueError("--limit must be between 1 and 1000.")
        path = require_database(args.db)
        query = require_read_query(args.query) if args.query else None
        with connect_read_only(path) as connection:
            print(f"Database (read-only): {path}")
            if query:
                cursor = connection.execute(query)
                headers = [column[0] for column in cursor.description or []]
                print_rows(headers, cursor.fetchmany(args.limit))
            elif args.table:
                table = require_table(connection, args.table)
                cursor = connection.execute(
                    f"SELECT * FROM {quote_identifier(table)} LIMIT ?", (args.limit,)
                )
                headers = [column[0] for column in cursor.description or []]
                print_rows(headers, cursor.fetchall())
            else:
                for table in table_names(connection):
                    count = connection.execute(
                        f"SELECT COUNT(*) FROM {quote_identifier(table)}"
                    ).fetchone()[0]
                    print(f"{table}\t{count}")
    except (sqlite3.Error, ValueError) as exc:
        print(f"Database inspection refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
