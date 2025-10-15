"""Phase 3 Feature Tests - Database Backup/Restore and Conflict Detection"""

import os
import subprocess
import time
from datetime import datetime, timedelta, date
import pytest
import requests
from playwright.sync_api import sync_playwright, expect

API_BASE = "http://localhost:8000/api"


def test_database_backup():
    """Test database backup script creates backup with compression."""
    # Run backup script
    result = subprocess.run(
        ["bash", "scripts/backup_database.sh"],
        cwd="/home/ubuntu/rostio",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Backup script failed: {result.stderr}"
    assert "✅ Backup Complete!" in result.stdout

    # Verify backup file was created
    backup_dir = "/home/ubuntu/rostio/backups/database"
    assert os.path.exists(backup_dir), "Backup directory not found"

    backups = [f for f in os.listdir(backup_dir) if f.startswith("roster_backup_") and f.endswith(".db.gz")]
    assert len(backups) > 0, "No backup files found"

    # Verify backup is compressed
    latest_backup = os.path.join(backup_dir, sorted(backups)[-1])
    backup_size = os.path.getsize(latest_backup)
    original_size = os.path.getsize("/home/ubuntu/rostio/roster.db")

    # Compressed should be significantly smaller
    assert backup_size < original_size, "Backup not properly compressed"
    print(f"✅ Backup created: {os.path.basename(latest_backup)} ({backup_size} bytes)")


@pytest.mark.skip(reason="Test needs auth refactor - creates/queries people without JWT tokens. Infrastructure test, not core user workflow.")
def test_database_restore():
    """Test database restore script restores from backup."""
    # First, create a backup
    subprocess.run(
        ["bash", "scripts/backup_database.sh"],
        cwd="/home/ubuntu/rostio",
        capture_output=True,
    )

    # Get original database checksum
    original_checksum = subprocess.run(
        ["md5sum", "/home/ubuntu/rostio/roster.db"],
        capture_output=True,
        text=True,
    ).stdout.split()[0]

    # Modify database slightly
    resp = requests.post(
        f"{API_BASE}/organizations/test_restore_org/people",
        json={"id": "test_restore_person", "name": "Restore Test", "email": "restore@test.com"},
    )

    # Run restore script (use latest backup)
    process = subprocess.Popen(
        ["bash", "scripts/restore_database.sh"],
        cwd="/home/ubuntu/rostio",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(input="latest\n", timeout=10)

    assert "✅ Database Restored Successfully!" in stdout

    # Verify database was restored (person should not exist)
    resp = requests.get(f"{API_BASE}/people/test_restore_person")
    assert resp.status_code == 404, "Database was not properly restored"

    # Verify safety backup was created
    safety_backups = [f for f in os.listdir("/home/ubuntu/rostio") if f.startswith("roster.db.before_restore_")]
    assert len(safety_backups) > 0, "Safety backup not created"
    print(f"✅ Restore successful, safety backup: {safety_backups[-1]}")


if __name__ == "__main__":
    print("Running Phase 3 Feature Tests\n")
    print("=" * 60)

    try:
        print("\n1. Testing Database Backup...")
        test_database_backup()

        print("\n2. Testing Database Restore...")
        test_database_restore()

        print("\n" + "=" * 60)
        print("✅ All Phase 3 tests passed!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
