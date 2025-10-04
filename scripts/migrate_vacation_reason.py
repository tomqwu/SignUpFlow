"""Migration: Add reason column to vacation_periods table."""

import sqlite3

def migrate():
    """Add reason column to vacation_periods table."""
    conn = sqlite3.connect('roster.db')
    cursor = conn.cursor()

    print("Adding reason column to vacation_periods table...")

    # Add reason column (SQLite supports ALTER TABLE ADD COLUMN for nullable columns)
    try:
        cursor.execute("""
            ALTER TABLE vacation_periods ADD COLUMN reason TEXT
        """)
        conn.commit()
        print("✅ Migration complete! reason column added to vacation_periods.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ Column 'reason' already exists. Skipping migration.")
        else:
            raise

    conn.close()

if __name__ == "__main__":
    migrate()
