#!/usr/bin/env python3
"""Add invitations table and update people table with invitation-related fields."""

import sqlite3

# Connect to database
conn = sqlite3.connect('/home/ubuntu/rostio/roster.db')
cursor = conn.cursor()

print("Starting migration for invitations system...\n")

# 1. Check if people table needs updates
cursor.execute("PRAGMA table_info(people)")
columns = [col[1] for col in cursor.fetchall()]

# Add status column
if 'status' not in columns:
    print("Adding status column to people table...")
    cursor.execute("ALTER TABLE people ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
    conn.commit()
    print("✅ Status column added successfully")
else:
    print("⏭️  Status column already exists")

# Add invited_by column
if 'invited_by' not in columns:
    print("Adding invited_by column to people table...")
    cursor.execute("ALTER TABLE people ADD COLUMN invited_by TEXT")
    conn.commit()
    print("✅ Invited_by column added successfully")
else:
    print("⏭️  Invited_by column already exists")

# Add last_login column
if 'last_login' not in columns:
    print("Adding last_login column to people table...")
    cursor.execute("ALTER TABLE people ADD COLUMN last_login TIMESTAMP")
    conn.commit()
    print("✅ Last_login column added successfully")
else:
    print("⏭️  Last_login column already exists")

# Add calendar_token column
if 'calendar_token' not in columns:
    print("Adding calendar_token column to people table...")
    cursor.execute("ALTER TABLE people ADD COLUMN calendar_token TEXT")
    conn.commit()
    print("✅ Calendar_token column added successfully")
else:
    print("⏭️  Calendar_token column already exists")

# 2. Check if invitations table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invitations'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    print("\nCreating invitations table...")
    cursor.execute("""
        CREATE TABLE invitations (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            roles TEXT NOT NULL,
            invited_by TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations(id),
            FOREIGN KEY (invited_by) REFERENCES people(id)
        )
    """)
    conn.commit()
    print("✅ Invitations table created successfully")

    # Create indexes
    print("Creating indexes on invitations table...")
    cursor.execute("CREATE INDEX idx_invitations_org_id ON invitations(org_id)")
    cursor.execute("CREATE INDEX idx_invitations_email ON invitations(email)")
    cursor.execute("CREATE INDEX idx_invitations_token ON invitations(token)")
    cursor.execute("CREATE INDEX idx_invitations_status ON invitations(status)")
    conn.commit()
    print("✅ Indexes created successfully")
else:
    print("\n⏭️  Invitations table already exists")

# 3. Create indexes on people table if they don't exist
print("\nCreating indexes on people table...")
try:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_people_email ON people(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_people_status ON people(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_people_calendar_token ON people(calendar_token)")
    conn.commit()
    print("✅ People table indexes created successfully")
except Exception as e:
    print(f"⚠️  Error creating indexes: {e}")

# Verify people table
print("\n=== People table structure ===")
cursor.execute("PRAGMA table_info(people)")
for col in cursor.fetchall():
    print(f"  - {col[1]} ({col[2]})")

# Verify invitations table
print("\n=== Invitations table structure ===")
cursor.execute("PRAGMA table_info(invitations)")
for col in cursor.fetchall():
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\n✅ Migration complete!")
