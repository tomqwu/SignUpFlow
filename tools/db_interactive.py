#!/usr/bin/env python3
"""Interactive database viewer for roster SQLite database."""

import sqlite3
import sys
import tabulate as tab_module


def view_database(db_path='cricket_roster.db'):
    """View database contents interactively."""

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return

    print(f"\n📊 Database: {db_path}\n")

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    print("Available Tables:")
    for i, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {i:2d}. {table:30s} ({count} rows)")

    print("\nCommands:")
    print("  • Type table number or name to view")
    print("  • 'sql <query>' to run custom SQL")
    print("  • 'schema <table>' to see table structure")
    print("  • 'exit' or 'quit' to exit")

    while True:
        try:
            print("\n" + "="*70)
            cmd = input("roster-db> ").strip()

            if cmd.lower() in ['exit', 'quit', 'q']:
                break

            # Schema command
            if cmd.lower().startswith('schema '):
                table = cmd.split(maxsplit=1)[1]
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                headers = ['ID', 'Name', 'Type', 'NotNull', 'Default', 'PK']
                print(f"\n📋 Schema for {table}:")
                print(tab_module.tabulate(columns, headers=headers, tablefmt='simple'))
                continue

            # SQL command
            if cmd.lower().startswith('sql '):
                query = cmd[4:]
                try:
                    cursor.execute(query)
                    if query.strip().upper().startswith('SELECT'):
                        results = cursor.fetchall()
                        if results:
                            headers = [description[0] for description in cursor.description]
                            print(tab_module.tabulate(results, headers=headers, tablefmt='simple'))
                            print(f"\n{len(results)} rows")
                        else:
                            print("No results")
                    else:
                        conn.commit()
                        print(f"✓ Query executed")
                except sqlite3.Error as e:
                    print(f"❌ Error: {e}")
                continue

            # Table selection by number
            if cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(tables):
                    cmd = tables[idx]
                else:
                    print(f"Invalid table number. Choose 1-{len(tables)}")
                    continue

            # Show table contents
            if cmd in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {cmd}")
                total = cursor.fetchone()[0]

                cursor.execute(f"SELECT * FROM {cmd} LIMIT 20")
                results = cursor.fetchall()

                if results:
                    headers = [description[0] for description in cursor.description]
                    print(f"\n📋 {cmd} (showing {len(results)} of {total} rows):\n")
                    print(tab_module.tabulate(results, headers=headers, tablefmt='simple'))
                else:
                    print(f"No rows in {cmd}")
            else:
                print(f"Unknown command or table: {cmd}")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    conn.close()
    print("\n👋 Goodbye!\n")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'cricket_roster.db'

    # Check if tabulate is available
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate for better display...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        import tabulate

    view_database(db_path)
