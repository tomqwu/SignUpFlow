#!/usr/bin/env python3
"""Quick database viewer - non-interactive."""

import sqlite3
import sys
import tabulate as tab_module


def show_database(db_path='cricket_roster.db', table=None, query=None, limit=20):
    """Show database contents."""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n📊 Database: {db_path}\n")

    # Show all tables if no specific query
    if not table and not query:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print("Tables:")
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            print(f"  • {tbl:30s} {count:3d} rows")

    # Execute custom query
    elif query:
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            headers = [description[0] for description in cursor.description]
            print(tab_module.tabulate(results, headers=headers, tablefmt='grid'))
            print(f"\n{len(results)} rows")
        else:
            print("No results")

    # Show specific table
    elif table:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total = cursor.fetchone()[0]

        cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
        results = cursor.fetchall()

        if results:
            headers = [description[0] for description in cursor.description]
            print(f"📋 {table} (showing {len(results)} of {total} rows):\n")
            print(tab_module.tabulate(results, headers=headers, tablefmt='grid'))
        else:
            print(f"No rows in {table}")

    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='View SQLite database')
    parser.add_argument('db', nargs='?', default='cricket_roster.db', help='Database file path')
    parser.add_argument('-t', '--table', help='Show specific table')
    parser.add_argument('-q', '--query', help='Execute SQL query')
    parser.add_argument('-l', '--limit', type=int, default=20, help='Limit rows (default: 20)')

    args = parser.parse_args()

    show_database(args.db, args.table, args.query, args.limit)
