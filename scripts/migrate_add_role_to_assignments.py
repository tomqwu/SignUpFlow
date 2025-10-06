#!/usr/bin/env python3
"""
Migration: Add role field to assignments table

This migration adds an event-specific role field to assignments,
allowing people to be assigned to events with specific roles
(e.g., "usher", "greeter", "sound_tech") rather than just generic assignment.

Usage:
    python scripts/migrate_add_role_to_assignments.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from roster_cli.db.models import Base
from api.database import engine, SessionLocal


def migrate():
    """Add role column to assignments table."""

    print("🔄 Starting migration: Add role to assignments")
    print("=" * 60)

    # Check if column already exists
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(assignments)"))
        columns = [row[1] for row in result.fetchall()]

        if 'role' in columns:
            print("✅ Migration already applied - 'role' column exists")
            return

    print("📝 Adding 'role' column to assignments table...")

    # Add the new column
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE assignments
            ADD COLUMN role TEXT
        """))
        conn.commit()

    print("✅ Column added successfully")

    # Verify the migration
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(assignments)"))
        columns = {row[1]: row[2] for row in result.fetchall()}

        if 'role' in columns:
            print(f"✅ Verified: 'role' column exists (type: {columns['role']})")
        else:
            print("❌ Error: 'role' column not found after migration")
            sys.exit(1)

    # Show sample data
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM assignments"))
        count = result.scalar()
        print(f"📊 Existing assignments: {count}")
        print("   Note: Existing assignments will have NULL role (can be updated later)")
    finally:
        db.close()

    print("=" * 60)
    print("✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update API endpoints to accept role parameter")
    print("2. Update frontend to allow role selection when joining events")
    print("3. Run tests to verify functionality")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
