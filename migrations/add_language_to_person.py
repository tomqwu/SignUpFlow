"""
Migration: Add language column to people table

This migration adds a language preference field to store user's preferred language.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "sqlite:///roster.db"

def run_migration():
    """Add language column to people table."""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(people);"))
        columns = [row[1] for row in result.fetchall()]

        if 'language' not in columns:
            print("Adding language column to people table...")
            conn.execute(text(
                "ALTER TABLE people ADD COLUMN language VARCHAR DEFAULT 'en' NOT NULL;"
            ))
            conn.commit()
            print("✅ Successfully added language column")
        else:
            print("⚠️ Language column already exists, skipping")

if __name__ == "__main__":
    run_migration()
