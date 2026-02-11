"""
E2E tests for volunteer schedule viewing after assignment.

Tests the complete workflow:
1. Admin creates event and assigns volunteer
2. Volunteer logs in and sees assignment in schedule
"""

import pytest
import requests
import time
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


def test_volunteer_sees_assigned_event_in_schedule(page: Page, app_config: AppConfig):
    """
    Test complete workflow from admin assigning volunteer to volunteer seeing it in schedule.

    User Journey:
    1. Create test organization with admin and volunteer users
    2. Admin creates an event
    3. Admin assigns volunteer to the event
    4. Volunteer logs in
    5. Volunteer navigates to schedule view
    6. Volunteer sees the assigned event in their schedule
    """

    print("\n" + "="*80)
    print("TESTING VOLUNTEER SCHEDULE VIEW AFTER ASSIGNMENT")
    print("="*80)

    # Setup: Create test organization, admin, and volunteer
    print("\nSetup: Creating test organization, admin, and volunteer...")
    timestamp = int(time.time())
    test_org_id = f"org_schedule_test_{timestamp}"
    admin_email = f"admin{timestamp}@test.com"
    volunteer_email = f"volunteer{timestamp}@test.com"
    test_password = "Password123"

    # Create organization
    org_response = requests.post(
        f"{app_config.app_url}/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Schedule Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201], f"Failed to create org: {org_response.text}"

    # Create admin user
    admin_signup = requests.post(
        f"{app_config.app_url}/api/auth/signup",
        json={
            "email": admin_email,
            "password": test_password,
            "name": f"Admin {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert admin_signup.status_code == 201
    admin_id = admin_signup.json()["person_id"]
    admin_token = admin_signup.json()["token"]

    # Set admin role
    requests.put(
        f"{app_config.app_url}/api/people/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"roles": ["admin", "volunteer"]}
    )

    # Create volunteer user
    volunteer_signup = requests.post(
        f"{app_config.app_url}/api/auth/signup",
        json={
            "email": volunteer_email,
            "password": test_password,
            "name": f"Volunteer {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert volunteer_signup.status_code == 201
    volunteer_id = volunteer_signup.json()["person_id"]
    print(f"✓ Admin created: {admin_email}")
    print(f"✓ Volunteer created: {volunteer_email}")

    # Step 1: Admin creates an event
    print("\nStep 1: Admin creates event via API...")

    event_id = f"service_{timestamp}"
    event_type = "Sunday Service"
    # Create start time 7 days from now at 10:00 AM
    start_time = time.strftime("%Y-%m-%dT10:00:00", time.localtime(time.time() + 7*24*60*60))
    # End time is 2 hours later
    end_time = time.strftime("%Y-%m-%dT12:00:00", time.localtime(time.time() + 7*24*60*60))

    event_response = requests.post(
        f"{app_config.app_url}/api/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "id": event_id,
            "org_id": test_org_id,
            "type": event_type,
            "start_time": start_time,
            "end_time": end_time
        }
    )
    assert event_response.status_code == 201, f"Failed to create event: {event_response.text}"
    print(f"  ✓ Event created: {event_id}")
    print(f"  ✓ Event type: {event_type}")
    print(f"  ✓ Start time: {start_time}")

    # Step 2: Admin assigns volunteer to the event
    print("\nStep 2: Admin assigns volunteer to event...")

    assignment_response = requests.post(
        f"{app_config.app_url}/api/events/{event_id}/assignments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "person_id": volunteer_id,
            "action": "assign",
            "role": "usher"
        }
    )
    assert assignment_response.status_code == 200, f"Failed to assign: {assignment_response.text}"
    print(f"  ✓ Volunteer assigned to event as 'usher'")

    # Step 3: Volunteer logs in
    print("\nStep 3: Volunteer logs in...")

    login_via_ui(page, app_config.app_url, volunteer_email, test_password)

    # Verify logged in
    if "/wizard" in page.url:
        page.goto(f"{app_config.app_url}/app/schedule")
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ Volunteer logged in successfully")

    # Step 4: Navigate to schedule view (should be default view)
    print("\nStep 4: Verifying schedule view is visible...")

    schedule_view = page.locator('#schedule-view')
    expect(schedule_view).to_be_visible(timeout=3000)
    print("  ✓ Schedule view visible")

    # Step 5: Verify assigned event appears in schedule
    print("\nStep 5: Checking for assigned event in schedule...")

    # Wait for schedule to load
    page.wait_for_timeout(3000)

    # Look for the event in the schedule
    # The event should show the event type
    event_card = page.locator(f'text="{event_type}"').first
    expect(event_card).to_be_visible(timeout=5000)
    print(f"  ✓ Event '{event_type}' appears in volunteer's schedule")

    # Check for role display (role is translated/capitalized: "usher" → "Usher")
    # Role is displayed as: 📋 Role: <strong>Usher</strong>
    role_text = page.locator('text="Usher"').first
    expect(role_text).to_be_visible(timeout=3000)
    print("  ✓ Role 'Usher' displayed in schedule")

    # Step 6: Verify assignment via API
    print("\nStep 6: Verifying assignment via API...")

    volunteer_login = requests.post(
        f"{app_config.app_url}/api/auth/login",
        json={"email": volunteer_email, "password": test_password}
    )
    volunteer_token = volunteer_login.json()["token"]

    assignments_response = requests.get(
        f"{app_config.app_url}/api/events/assignments/all?org_id={test_org_id}",
        headers={"Authorization": f"Bearer {volunteer_token}"}
    )
    assert assignments_response.status_code == 200

    assignments_data = assignments_response.json()
    volunteer_assignments = [a for a in assignments_data["assignments"] if a["person_id"] == volunteer_id]

    assert len(volunteer_assignments) > 0, "Volunteer should have at least one assignment"
    assert any(a["event_id"] == event_id for a in volunteer_assignments), "Volunteer should be assigned to created event"
    print(f"  ✓ Assignment verified via API")
    print(f"  ✓ Total assignments for volunteer: {len(volunteer_assignments)}")

    print("\n" + "="*80)
    print("✅ VOLUNTEER SCHEDULE VIEW TEST PASSED")
    print("="*80)


def test_volunteer_sees_empty_schedule_when_not_assigned(page: Page, app_config: AppConfig):
    """
    Test that volunteer sees empty state when not assigned to any events.

    User Journey:
    1. Create organization and volunteer user
    2. Volunteer logs in
    3. Volunteer sees empty schedule message
    """

    print("\n" + "="*80)
    print("TESTING VOLUNTEER EMPTY SCHEDULE")
    print("="*80)

    # Setup: Create test organization and volunteer
    print("\nSetup: Creating test organization and volunteer...")
    timestamp = int(time.time())
    test_org_id = f"org_empty_{timestamp}"
    volunteer_email = f"volunteer{timestamp}@test.com"
    test_password = "Password123"

    # Create organization
    org_response = requests.post(
        f"{app_config.app_url}/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Empty Schedule Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201]

    # Create volunteer user
    volunteer_signup = requests.post(
        f"{app_config.app_url}/api/auth/signup",
        json={
            "email": volunteer_email,
            "password": test_password,
            "name": f"Volunteer {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert volunteer_signup.status_code == 201
    print(f"✓ Volunteer created: {volunteer_email}")

    # Step 1: Volunteer logs in
    print("\nStep 1: Volunteer logs in...")

    login_via_ui(page, app_config.app_url, volunteer_email, test_password)

    # Verify logged in
    if "/wizard" in page.url:
        page.goto(f"{app_config.app_url}/app/schedule")
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ Volunteer logged in successfully")

    # Step 2: Verify empty schedule state
    print("\nStep 2: Verifying empty schedule state...")

    # Wait for schedule to load
    page.wait_for_timeout(2000)

    # Check that upcoming count is 0
    upcoming_count = page.locator('#upcoming-count')
    expect(upcoming_count).to_have_text("0", timeout=5000)
    print("  ✓ Upcoming count is 0 (no assignments)")

    print("\n" + "="*80)
    print("✅ EMPTY SCHEDULE TEST PASSED")
    print("="*80)
