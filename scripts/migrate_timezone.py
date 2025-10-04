#!/usr/bin/env python3
"""Add timezone column to people table."""

import sqlite3

# Connect to database
conn = sqlite3.connect('/home/ubuntu/rostio/roster.db')
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(people)")
columns = [col[1] for col in cursor.fetchall()]

if 'timezone' not in columns:
    print("Adding timezone column to people table...")
    cursor.execute("ALTER TABLE people ADD COLUMN timezone TEXT NOT NULL DEFAULT 'UTC'")
    conn.commit()
    print("✅ Timezone column added successfully")
else:
    print("⏭️  Timezone column already exists")

# Verify
cursor.execute("PRAGMA table_info(people)")
print("\nPeople table columns:")
for col in cursor.fetchall():
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\n✅ Migration complete!")
