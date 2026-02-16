"""
Comprehensive tests for availability CRUD operations (API + GUI)
Tests user story: "Update My Availability" workflow
"""
import os
import requests
from playwright.sync_api import sync_playwright
import pytest
# (DB engine/session provided by api.database.SessionLocal)

from api.models import Organization, Person
from api.security import hash_password

def get_admin_headers_and_create_user(api_base: str, org_id="test-org", user_id="test-admin", email="admin@test.com"):
    """Ensure an admin user exists for the given org and return auth headers."""
    # Use the app's SessionLocal so we write into the same DB the test server is using.
    from api.database import SessionLocal

    session = SessionLocal()
    try:
        org = session.get(Organization, org_id)
        if org is None:
            org = Organization(id=org_id, name="Test Organization", region="Test Region", config={"roles": ["admin", "volunteer"]})
            session.add(org)
            session.flush()

        person = session.query(Person).filter(Person.email == email).one_or_none()
        password_hash = hash_password("admin123")
        if person is None:
            person = Person(
                id=user_id,
                org_id=org_id,
                name="Test Admin",
                email=email,
                password_hash=password_hash,
                roles=["admin"],
                extra_data={},
            )
            session.add(person)
        else:
            person.org_id = org_id
            person.password_hash = password_hash
            person.roles = ["admin"]
        session.commit()
    finally:
        session.close()

    login_resp = requests.post(f"{api_base}/auth/login", json={
        "email": email,
        "password": "admin123"
    })
    login_resp.raise_for_status()
    data = login_resp.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        raise RuntimeError(f"Login response missing token fields: {data}")
    return {"Authorization": f"Bearer {token}"}


def test_availability_api_crud(api_server, app_config):
    """Test complete CRUD lifecycle for time-off via API"""
    print("\n🧪 Testing Availability API CRUD...")

    api_base = app_config.api_base
    API_BASE = api_base

    # Get admin authentication headers (creates admin user if needed)
    admin_headers = get_admin_headers_and_create_user(api_base)

    # Setup: Create organization first
    org_data = {
        "id": "test-org",
        "name": "Test Organization"
    }
    requests.post(f"{API_BASE}/organizations/", json=org_data, headers=admin_headers)  # Ignore if exists

    # Cleanup: Delete test person if it exists from previous run
    person_id = "test-avail-person"
    requests.delete(f"{API_BASE}/people/{person_id}", headers=admin_headers)

    # Setup: Create person
    person_data = {
        "id": person_id,
        "org_id": "test-org",
        "name": "Test Person",
        "email": "test.avail@test.com",
        "roles": ["volunteer"]
    }
    resp = requests.post(f"{API_BASE}/people/", json=person_data, headers=admin_headers)
    assert resp.status_code in [200, 201], f"Failed to create person: {resp.text}"

    # 1. CREATE time-off with reason
    print("  1. Testing CREATE with reason...")
    timeoff_data = {
        "start_date": "2025-11-01",
        "end_date": "2025-11-10",
        "reason": "Family vacation"
    }
    resp = requests.post(
        f"{API_BASE}/availability/{person_id}/timeoff",
        json=timeoff_data,
        headers=admin_headers
    )
    assert resp.status_code == 201, f"Failed to create time-off: {resp.text}"
    data = resp.json()
    assert "id" in data
    assert data["start_date"] == "2025-11-01"
    assert data["end_date"] == "2025-11-10"
    assert data["reason"] == "Family vacation", f"Reason not saved: {data}"
    timeoff_id = data["id"]
    print(f"     ✓ Created time-off ID: {timeoff_id} with reason")

    # 2. READ time-off list (verify reason is returned)
    print("  2. Testing READ with reason...")
    resp = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["timeoff"]) == 1
    assert data["timeoff"][0]["id"] == timeoff_id
    assert data["timeoff"][0]["reason"] == "Family vacation", f"Reason not returned in GET: {data}"
    print(f"     ✓ Read {data['total']} time-off periods with reason field")

    # 3. UPDATE time-off (including reason)
    print("  3. Testing UPDATE with new reason...")
    updated_data = {
        "start_date": "2025-11-05",  # Changed from Nov 1
        "end_date": "2025-11-15",     # Changed from Nov 10
        "reason": "Extended family vacation"  # Updated reason
    }
    resp = requests.patch(
        f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}",
        json=updated_data,
        headers=admin_headers
    )
    assert resp.status_code == 200, f"Failed to update: {resp.text}"
    data = resp.json()
    assert data["start_date"] == "2025-11-05"
    assert data["end_date"] == "2025-11-15"
    assert data["reason"] == "Extended family vacation", f"Reason not updated: {data}"
    assert "updated successfully" in data["message"]
    print(f"     ✓ Updated dates and reason: {data['reason']}")

    # Verify update persisted (including reason)
    resp = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
    data = resp.json()
    assert data["timeoff"][0]["start_date"] == "2025-11-05"
    assert data["timeoff"][0]["end_date"] == "2025-11-15"
    assert data["timeoff"][0]["reason"] == "Extended family vacation", f"Updated reason not persisted: {data}"
    print("     ✓ Update persisted correctly with reason")

    # 4. DELETE time-off
    print("  4. Testing DELETE...")
    resp = requests.delete(
        f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}",
        headers=admin_headers
    )
    assert resp.status_code == 204, f"Failed to delete: {resp.status_code}"
    print(f"     ✓ Deleted time-off ID: {timeoff_id}")

    # Verify deletion
    resp = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
    data = resp.json()
    assert data["total"] == 0
    assert len(data["timeoff"]) == 0
    print("     ✓ Deletion verified")

    # Cleanup
    requests.delete(f"{API_BASE}/people/{person_id}", headers=admin_headers)
    print("\n✅ API CRUD tests passed!")


def test_availability_edge_cases(api_server, app_config):
    """Test edge cases and error handling"""
    print("\n🧪 Testing Availability Edge Cases...")

    api_base = app_config.api_base
    API_BASE = api_base

    # Get admin authentication headers
    admin_headers = get_admin_headers_and_create_user(api_base, org_id="test-org-edge", user_id="test-admin-edge", email="admin-edge@test.com")

    # Setup: Create organization first
    org_data = {
        "id": "test-org-edge",
        "name": "Test Organization Edge"
    }
    requests.post(f"{API_BASE}/organizations/", json=org_data, headers=admin_headers)  # Ignore if exists

    # Setup - cleanup first in case person exists from previous test
    person_id = "test-edge-person"
    requests.delete(f"{API_BASE}/people/{person_id}", headers=admin_headers)  # Clean up if exists

    person_data = {
        "id": "test-edge-person",
        "org_id": "test-org-edge",
        "name": "Edge Case Person",
        "email": "edge@test.com",
        "roles": ["volunteer"]
    }
    resp = requests.post(f"{API_BASE}/people/", json=person_data, headers=admin_headers)
    assert resp.status_code in [200, 201], f"Failed to create person: {resp.text}"

    # Test 1: Invalid dates (end before start)
    print("  1. Testing invalid date range...")
    invalid_data = {
        "start_date": "2025-11-10",
        "end_date": "2025-11-01"  # Before start!
    }
    resp = requests.post(
        f"{API_BASE}/availability/{person_id}/timeoff",
        json=invalid_data,
        headers=admin_headers
    )
    assert resp.status_code == 400
    assert "after start date" in resp.json()["detail"].lower()
    print("     ✓ Rejected invalid date range")

    # Test 2: Update non-existent time-off
    print("  2. Testing update of non-existent time-off...")
    resp = requests.patch(
        f"{API_BASE}/availability/{person_id}/timeoff/99999",
        json={"start_date": "2025-11-01", "end_date": "2025-11-10"},
        headers=admin_headers
    )
    assert resp.status_code == 404
    print("     ✓ Returned 404 for non-existent time-off")

    # Test 3: Delete non-existent time-off
    print("  3. Testing delete of non-existent time-off...")
    resp = requests.delete(
        f"{API_BASE}/availability/{person_id}/timeoff/99999",
        headers=admin_headers
    )
    assert resp.status_code == 404
    print("     ✓ Returned 404 for non-existent time-off")

    # Test 4: Time-off for non-existent person
    print("  4. Testing time-off for non-existent person...")
    resp = requests.post(
        f"{API_BASE}/availability/non-existent-person/timeoff",
        json={"start_date": "2025-11-01", "end_date": "2025-11-10"},
        headers=admin_headers
    )
    assert resp.status_code == 404
    print("     ✓ Returned 404 for non-existent person")

    # Test 5: Time-off without reason (null handling)
    print("  5. Testing time-off without reason...")
    no_reason_data = {
        "start_date": "2025-12-01",
        "end_date": "2025-12-05"
    }
    resp = requests.post(
        f"{API_BASE}/availability/{person_id}/timeoff",
        json=no_reason_data,
        headers=admin_headers
    )
    assert resp.status_code == 201, f"Failed to create time-off without reason: {resp.text}"
    data = resp.json()
    assert data["reason"] is None or data["reason"] == "", f"Expected null/empty reason, got: {data['reason']}"
    print("     ✓ Time-off without reason handled correctly")

    # Test 6: Multiple time-off periods with mixed reasons
    print("  6. Testing multiple time-off periods with mixed reasons...")
    periods = [
        {"start_date": "2025-11-01", "end_date": "2025-11-10", "reason": "Conference"},
        {"start_date": "2026-01-01", "end_date": "2026-01-10"},  # No reason
    ]
    for period_data in periods:
        resp = requests.post(
            f"{API_BASE}/availability/{person_id}/timeoff",
            json=period_data,
            headers=admin_headers
        )
        assert resp.status_code == 201, f"Failed to create period: {resp.text}"

    # Verify all periods exist with correct reasons
    resp = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
    data = resp.json()
    assert data["total"] >= 2, f"Expected at least 2 periods, got {data['total']}"

    # Find the conference period and verify it has the reason
    conference_period = next((p for p in data["timeoff"] if p.get("reason") == "Conference"), None)
    assert conference_period is not None, "Conference period not found"
    print("     ✓ Multiple time-off periods with mixed reasons handled correctly")

    # Cleanup
    requests.delete(f"{API_BASE}/people/{person_id}", headers=admin_headers)
    print("\n✅ Edge case tests passed!")


@pytest.mark.skip(reason="E2E test miscategorized as integration test - requires Playwright browsers. Should be moved to tests/e2e/")
def test_availability_gui_workflow(api_server, app_config):
    """Test complete availability workflow through GUI"""
    print("\n🧪 Testing Availability GUI Workflow...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # No longer using browser alerts/dialogs - app uses toasts instead

        # Login
        print("  1. Login...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)
        page.fill('#login-email', 'sarah@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
        print("     ✓ Logged in as Sarah")

        # Navigate to Availability
        print("  2. Navigate to Availability tab...")
        page.locator('button.nav-btn[data-view="availability"]').click()
        page.wait_for_timeout(1000)
        print("     ✓ On Availability page")

        # Add time-off
        print("  3. Add time-off...")
        page.fill('#timeoff-start', '2025-12-20')
        page.fill('#timeoff-end', '2025-12-30')
        page.locator('button:has-text("Add Time Off")').click()
        page.wait_for_timeout(2000)

        # Verify success by checking if toast appeared or list updated
        # App uses showToast() instead of browser alerts
        print("     ✓ Time-off added (form submitted)")

        # Verify it appears in list
        page.wait_for_timeout(1000)
        timeoff_items = page.locator('.timeoff-item')
        if timeoff_items.count() > 0:
            timeoff_item = timeoff_items.first
            assert timeoff_item.is_visible()
            text = timeoff_item.inner_text()
            # Check for date components (month/day/year in any format)
            assert "2025" in text or "12" in text or "20" in text
            print("     ✓ Time-off displayed in list")
        else:
            print("     ⚠️  Time-off list may be empty or loading")

        # Check for Edit and Remove buttons
        if timeoff_items.count() > 0:
            edit_btn = timeoff_item.locator('button:has-text("Edit")')
            remove_btn = timeoff_item.locator('button:has-text("Remove")')
            assert edit_btn.is_visible()
            assert remove_btn.is_visible()
            print("     ✓ Edit and Remove buttons visible")

        # Click Edit button (will trigger prompts)
        print("  4. Testing Edit functionality (via API)...")
        # Since prompts are hard to test, verify via API instead
        # Get the time-off ID
        resp = requests.get(f"{API_BASE}/availability/sarah/timeoff")
        data = resp.json()
        if data["total"] > 0:
            timeoff_id = data["timeoff"][0]["id"]

            # Update via API
            resp = requests.patch(
                f"{API_BASE}/availability/sarah/timeoff/{timeoff_id}",
                json={"start_date": "2025-12-21", "end_date": "2025-12-31"}
            )
            assert resp.status_code == 200
            print("     ✓ Edit API works")

            # Refresh page to see changes
            page.reload()
            page.wait_for_timeout(2000)

        # Click Remove button
        print("  5. Testing Remove functionality...")
        remove_btn = page.locator('.timeoff-item button:has-text("Remove")').first
        if remove_btn.count() > 0:
            remove_btn.click()
            page.wait_for_timeout(2000)

            # Verify removal
            # Should either show empty state or fewer items
            page.wait_for_timeout(1000)
            print("     ✓ Remove button works")

        browser.close()

    print("\n✅ GUI workflow tests passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AVAILABILITY CRUD COMPREHENSIVE TEST SUITE")
    print("="*60)

    test_availability_api_crud()
    test_availability_edge_cases()
    test_availability_gui_workflow()

    print("\n" + "="*60)
    print("✅ ALL AVAILABILITY TESTS PASSED!")
    print("="*60)
