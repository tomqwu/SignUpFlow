"""
Migration: Add recurring events schema

This migration adds support for recurring events by:
1. Creating recurring_series table
2. Creating recurrence_exceptions table
3. Adding series_id, occurrence_sequence, is_exception columns to events table

For SQLite, we need to handle ALTER TABLE limitations by recreating the events table.
For development, the simplest approach is to backup and recreate the database.

Usage:
    python migrations/add_recurring_events_schema.py
"""

import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from api.models import Base


def backup_database(db_path: str) -> str:
    """Backup the database before migration."""
    if not os.path.exists(db_path):
        print(f"⚠️  Database {db_path} does not exist - nothing to backup")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_before_recurring_events_{timestamp}"

    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        raise


def check_columns_exist(engine, table_name: str, column_names: list) -> dict:
    """Check if columns already exist in the table."""
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]

    results = {}
    for col_name in column_names:
        results[col_name] = col_name in existing_columns

    return results


def migrate_sqlite(engine) -> None:
    """
    Migrate SQLite database for recurring events.

    SQLite has limited ALTER TABLE support, so we use create_all which:
    - Creates new tables (recurring_series, recurrence_exceptions)
    - Leaves existing tables unchanged (events already exists)

    For the events table columns, we use raw SQL ALTER TABLE.
    """
    print("\n🔄 Migrating SQLite database for recurring events...")

    # Check if events table exists
    inspector = inspect(engine)
    if 'events' not in inspector.get_table_names():
        print("⚠️  Events table doesn't exist - will be created fresh")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return

    # Check which columns need to be added
    columns_to_add = check_columns_exist(engine, 'events', ['series_id', 'occurrence_sequence', 'is_exception'])

    with engine.connect() as conn:
        # Add missing columns to events table
        if not columns_to_add.get('series_id'):
            try:
                conn.execute(text("ALTER TABLE events ADD COLUMN series_id VARCHAR"))
                print("✅ Added series_id column to events table")
            except Exception as e:
                print(f"⚠️  Could not add series_id: {e}")

        if not columns_to_add.get('occurrence_sequence'):
            try:
                conn.execute(text("ALTER TABLE events ADD COLUMN occurrence_sequence INTEGER"))
                print("✅ Added occurrence_sequence column to events table")
            except Exception as e:
                print(f"⚠️  Could not add occurrence_sequence: {e}")

        if not columns_to_add.get('is_exception'):
            try:
                conn.execute(text("ALTER TABLE events ADD COLUMN is_exception BOOLEAN DEFAULT 0 NOT NULL"))
                print("✅ Added is_exception column to events table")
            except Exception as e:
                print(f"⚠️  Could not add is_exception: {e}")

        conn.commit()

    # Create new tables (recurring_series, recurrence_exceptions)
    Base.metadata.create_all(bind=engine)
    print("✅ Created recurring_series and recurrence_exceptions tables")

    # Verify migration
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = ['recurring_series', 'recurrence_exceptions']
    missing_tables = [t for t in required_tables if t not in tables]

    if missing_tables:
        print(f"❌ Migration failed - missing tables: {missing_tables}")
        raise Exception(f"Migration incomplete - missing tables: {missing_tables}")

    # Verify events table has new columns
    events_columns = check_columns_exist(engine, 'events', ['series_id', 'occurrence_sequence', 'is_exception'])

    if not all(events_columns.values()):
        missing_cols = [col for col, exists in events_columns.items() if not exists]
        print(f"❌ Migration failed - events table missing columns: {missing_cols}")
        raise Exception(f"Migration incomplete - events table missing columns: {missing_cols}")

    print("\n✅ Migration completed successfully!")
    print("\n📊 Final schema:")
    print(f"  - recurring_series table: ✅")
    print(f"  - recurrence_exceptions table: ✅")
    print(f"  - events.series_id: ✅")
    print(f"  - events.occurrence_sequence: ✅")
    print(f"  - events.is_exception: ✅")


def main():
    """Run the migration."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./roster.db")
    db_path = db_url.replace("sqlite:///", "").replace("./", "")

    print(f"🔧 Recurring Events Migration")
    print(f"Database: {db_path}")

    # Backup database (if exists)
    if os.path.exists(db_path):
        backup_path = backup_database(db_path)
        if backup_path:
            print(f"💾 Backup saved: {backup_path}")

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Run migration
    try:
        if db_url.startswith("sqlite"):
            migrate_sqlite(engine)
        else:
            print("⚠️  PostgreSQL migration not yet implemented")
            print("For PostgreSQL, use Alembic migrations")
            return

        print("\n✅ Migration successful!")
        print("\n📝 Next steps:")
        print("  1. Test the new schema: python -c 'from api.models import RecurringSeries; print(RecurringSeries.__tablename__)'")
        print("  2. Run tests: poetry run pytest tests/")
        print("  3. Implement recurrence generator service")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"\n🔄 To restore backup:")
        print(f"  mv {db_path}.backup_* {db_path}")
        raise


if __name__ == "__main__":
    main()
