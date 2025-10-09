"""Phase 3 Feature Tests - Database Backup/Restore and Conflict Detection"""

import os
import subprocess
import time
from datetime import datetime, timedelta, date
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


def test_conflict_detection_already_assigned():
    """Test conflict detection when person is already assigned to event."""
    org_id = f"test_org_{int(time.time())}"

    # Create test organization
    resp = requests.post(
        f"{API_BASE}/organizations/",
        json={
            "id": org_id,
            "name": "Test Org",
            "config": {"roles": ["player"]},
        },
    )
    assert resp.status_code in [201, 200]

    # Create person
    person_id = f"test_person_{int(time.time())}"
    resp = requests.post(
        f"{API_BASE}/people/",
        json={
            "id": person_id,
            "name": "Test Person",
            "email": f"test{int(time.time())}@test.com",
            "org_id": org_id,
        },
    )
    assert resp.status_code in [201, 200], f"Failed to create person: {resp.text}"

    # Create event
    event_id = f"test_conflict_event_{int(time.time())}"
    event_start = datetime.now() + timedelta(days=7)
    event_end = event_start + timedelta(hours=2)

    resp = requests.post(
        f"{API_BASE}/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "Conflict Test Match",
            "start_time": event_start.isoformat(),
            "end_time": event_end.isoformat(),
        },
    )
    assert resp.status_code == 201, f"Failed to create event: {resp.text}"

    # Create solution and assignment
    solution_id = f"test_solution_{int(time.time())}"
    resp = requests.post(
        f"{API_BASE}/solutions/",
        json={
            "id": solution_id,
            "org_id": org_id,
            "name": "Conflict Test Solution",
            "health_score": 100,
        },
    )
    assert resp.status_code == 201, f"Failed to create solution: {resp.text}"

    resp = requests.post(
        f"{API_BASE}/solutions/{solution_id}/assignments",
        json={
            "person_id": person_id,
            "event_id": event_id,
            "role": "player",
        },
    )
    assert resp.status_code == 201, f"Failed to create assignment: {resp.text}"

    # Check conflicts - should detect already assigned
    resp = requests.post(
        f"{API_BASE}/conflicts/check",
        json={"person_id": person_id, "event_id": event_id},
    )
    assert resp.status_code == 200, f"Conflict check failed: {resp.text}"
    data = resp.json()

    assert data["has_conflicts"] == True
    assert data["can_assign"] == False  # Blocking conflict
    assert any(c["type"] == "already_assigned" for c in data["conflicts"])
    print(f"✅ Already assigned conflict detected: {data['conflicts'][0]['message']}")
    return org_id, person_id  # Return for cleanup or reuse


def test_conflict_detection_time_off():
    """Test conflict detection when person has time-off."""
    org_id = "cricket_league"
    person_id = "pastor"

    # Add time-off period
    time_off_start = date.today() + timedelta(days=14)
    time_off_end = time_off_start + timedelta(days=7)

    resp = requests.post(
        f"{API_BASE}/availability/{person_id}/timeoff",
        json={
            "start_date": time_off_start.isoformat(),
            "end_date": time_off_end.isoformat(),
        },
    )
    assert resp.status_code in [201, 200], f"Failed to add time-off: {resp.text}"

    # Create event during time-off period
    event_id = f"test_timeoff_event_{int(time.time())}"
    event_start = datetime.combine(time_off_start + timedelta(days=2), datetime.min.time()) + timedelta(hours=10)
    event_end = event_start + timedelta(hours=2)

    resp = requests.post(
        f"{API_BASE}/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "Time-off Conflict Match",
            "start_time": event_start.isoformat(),
            "end_time": event_end.isoformat(),
        },
    )
    assert resp.status_code == 201

    # Check conflicts - should detect time-off
    resp = requests.post(
        f"{API_BASE}/conflicts/check",
        json={"person_id": person_id, "event_id": event_id},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["has_conflicts"] == True
    assert data["can_assign"] == False  # Blocking conflict
    assert any(c["type"] == "time_off" for c in data["conflicts"])
    print(f"✅ Time-off conflict detected: {data['conflicts'][0]['message']}")


def test_conflict_detection_double_booked():
    """Test conflict detection when person is assigned to overlapping events."""
    org_id = "cricket_league"
    person_id = "rohit"

    # Create first event
    event1_id = f"test_event1_{int(time.time())}"
    event1_start = datetime.now() + timedelta(days=10)
    event1_end = event1_start + timedelta(hours=3)

    resp = requests.post(
        f"{API_BASE}/events/",
        json={
            "id": event1_id,
            "org_id": org_id,
            "type": "Double Book Event 1",
            "start_time": event1_start.isoformat(),
            "end_time": event1_end.isoformat(),
        },
    )
    assert resp.status_code == 201

    # Create second event that overlaps
    event2_id = f"test_event2_{int(time.time())}"
    event2_start = event1_start + timedelta(hours=1)  # Overlaps with event1
    event2_end = event2_start + timedelta(hours=2)

    resp = requests.post(
        f"{API_BASE}/events/",
        json={
            "id": event2_id,
            "org_id": org_id,
            "type": "Double Book Event 2",
            "start_time": event2_start.isoformat(),
            "end_time": event2_end.isoformat(),
        },
    )
    assert resp.status_code == 201

    # Assign person to first event
    solution_id = f"test_doublebook_solution_{int(time.time())}"
    resp = requests.post(
        f"{API_BASE}/solutions/",
        json={
            "id": solution_id,
            "org_id": org_id,
            "name": "Double Book Test",
            "health_score": 100,
        },
    )
    assert resp.status_code == 201

    resp = requests.post(
        f"{API_BASE}/solutions/{solution_id}/assignments",
        json={
            "person_id": person_id,
            "event_id": event1_id,
            "role": "batsman",
        },
    )
    assert resp.status_code == 201

    # Check conflicts for second event - should detect double booking
    resp = requests.post(
        f"{API_BASE}/conflicts/check",
        json={"person_id": person_id, "event_id": event2_id},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["has_conflicts"] == True
    assert data["can_assign"] == True  # Warning but allow (non-blocking)
    assert any(c["type"] == "double_booked" for c in data["conflicts"])
    print(f"✅ Double-booked conflict detected: {data['conflicts'][0]['message']}")


def test_conflict_detection_no_conflicts():
    """Test conflict detection when there are no conflicts."""
    org_id = "cricket_league"
    person_id = "bumrah"

    # Create event in the future (no conflicts)
    event_id = f"test_noconflict_event_{int(time.time())}"
    event_start = datetime.now() + timedelta(days=30)
    event_end = event_start + timedelta(hours=2)

    resp = requests.post(
        f"{API_BASE}/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "No Conflict Match",
            "start_time": event_start.isoformat(),
            "end_time": event_end.isoformat(),
        },
    )
    assert resp.status_code == 201

    # Check conflicts - should be clear
    resp = requests.post(
        f"{API_BASE}/conflicts/check",
        json={"person_id": person_id, "event_id": event_id},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["has_conflicts"] == False
    assert data["can_assign"] == True
    assert len(data["conflicts"]) == 0
    print(f"✅ No conflicts detected - ready to assign")


def test_conflict_detection_gui():
    """Test conflict detection in GUI workflow."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Login as Sarah (has time-off)
        page.goto("http://localhost:8000")
        page.locator('[data-i18n="auth.sign_in_link"]').click()
        page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "pastor@grace.church")
        page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "password")
        page.locator('[data-i18n="auth.sign_in"]').click()
        page.wait_for_timeout(1000)

        # Verify conflict detection script is loaded
        conflict_script = page.evaluate("typeof window.checkConflicts")
        assert conflict_script == "function", "Conflict detection script not loaded"

        # Test conflict detection function
        result = page.evaluate("""
            async () => {
                const result = await window.checkConflicts('pastor', 'match_001');
                return result;
            }
        """)

        assert result is not None, "Conflict check function failed"
        print(f"✅ Conflict detection GUI integration working")

        browser.close()


if __name__ == "__main__":
    print("Running Phase 3 Feature Tests\n")
    print("=" * 60)

    try:
        print("\n1. Testing Database Backup...")
        test_database_backup()

        print("\n2. Testing Database Restore...")
        test_database_restore()

        print("\n3. Testing Conflict Detection - Already Assigned...")
        test_conflict_detection_already_assigned()

        print("\n4. Testing Conflict Detection - Time Off...")
        test_conflict_detection_time_off()

        print("\n5. Testing Conflict Detection - Double Booked...")
        test_conflict_detection_double_booked()

        print("\n6. Testing Conflict Detection - No Conflicts...")
        test_conflict_detection_no_conflicts()

        print("\n7. Testing Conflict Detection GUI...")
        test_conflict_detection_gui()

        print("\n" + "=" * 60)
        print("✅ All Phase 3 tests passed!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
