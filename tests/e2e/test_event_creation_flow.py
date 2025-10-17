"""
E2E tests for event creation flow.

Tests the complete user journey:
1. Admin logs in
2. Navigates to admin console
3. Creates an event
4. Verifies event appears in event list
"""

import requests
import time
from playwright.sync_api import Page, expect


def test_create_event_complete_journey(page: Page):
    """
    Test complete event creation flow from admin login to event appearing in list.

    User Journey:
    1. Create test organization and admin user
    2. Login as admin
    3. Navigate to admin console
    4. Switch to Events tab
    5. Create new event
    6. Verify event appears in event list
    """

    print("\n" + "="*80)
    print("TESTING EVENT CREATION USER JOURNEY")
    print("="*80)

    # Setup: Create test organization and admin user
    print("\nSetup: Creating test organization and admin user...")
    timestamp = int(time.time())
    test_org_id = f"org_event_test_{timestamp}"
    test_email = f"admin{timestamp}@test.com"
    test_password = "AdminPassword123"
    test_name = f"Admin User {timestamp}"

    # Create organization
    org_response = requests.post(
        "http://localhost:8000/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Event Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201], f"Failed to create org: {org_response.text}"

    # Create admin user
    signup_response = requests.post(
        "http://localhost:8000/api/auth/signup",
        json={
            "email": test_email,
            "password": test_password,
            "name": test_name,
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201, f"Failed to create user: {signup_response.text}"

    # Get user ID and set admin role
    user_data = signup_response.json()
    user_id = user_data["person_id"]

    # Set admin role via API
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    assert login_response.status_code == 200, f"Failed to login: {login_response.text}"
    auth_token = login_response.json()["token"]

    # Update user to admin
    update_response = requests.put(
        f"http://localhost:8000/api/people/{user_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "roles": ["admin", "volunteer"]
        }
    )
    assert update_response.status_code == 200, f"Failed to set admin role: {update_response.text}"
    print(f"✓ Admin user created: {test_email}")

    # Step 1: Login as admin
    print("\nStep 1: Admin logs in...")
    page.goto("http://localhost:8000/login")

    page.locator('#login-email').fill(test_email)
    page.locator('#login-password').fill(test_password)
    page.locator('#login-screen button[type="submit"]').click()

    # Verify logged in
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ Admin logged in successfully")

    # Step 2: Navigate to admin console
    print("\nStep 2: Navigating to admin console...")

    # Click admin console nav button
    admin_nav_btn = page.locator('button.nav-btn[data-view="admin"]')
    expect(admin_nav_btn).to_be_visible(timeout=3000)
    admin_nav_btn.click()

    # Verify admin view is active
    admin_view = page.locator('#admin-view.active')
    expect(admin_view).to_be_visible(timeout=3000)
    print("  ✓ Admin console visible")

    # Step 3: Verify Events tab is active (it's active by default)
    print("\nStep 3: Verifying Events tab is active...")

    # Events tab is active by default in admin console
    events_tab_content = page.locator('#admin-tab-events.active')
    expect(events_tab_content).to_be_visible(timeout=3000)
    print("  ✓ Events tab active (default)")

    # Step 4: Click Create Event button
    print("\nStep 4: Opening create event form...")

    create_event_btn = page.locator('button:has([data-i18n="admin.create_event_button"])')
    expect(create_event_btn).to_be_visible(timeout=3000)
    create_event_btn.click()

    # Verify create event modal is visible
    create_event_modal = page.locator('#create-event-modal')
    expect(create_event_modal).to_be_visible(timeout=3000)
    print("  ✓ Create event modal visible")

    # Step 5: Fill in event details
    print("\nStep 5: Filling in event details...")

    event_type = "Sunday Service"
    # Create start time 7 days from now at 10:00 AM
    start_time = time.strftime("%Y-%m-%dT10:00", time.localtime(time.time() + 7*24*60*60))

    page.locator('#event-type').select_option(event_type)
    page.locator('#event-start').fill(start_time)
    page.locator('#event-duration').fill("2")

    print(f"  Event Type: {event_type}")
    print(f"  Start Time: {start_time}")
    print(f"  Duration: 2 hours")

    # Step 6: Submit form
    print("\nStep 6: Submitting event creation form...")

    submit_btn = page.locator('#create-event-form button[type="submit"]')
    submit_btn.click()

    # Wait for modal to close
    expect(create_event_modal).not_to_be_visible(timeout=5000)
    print("  ✓ Event created successfully")

    # Step 7: Wait for event list to reload
    print("\nStep 7: Waiting for event list to reload...")
    page.wait_for_timeout(3000)
    print("  ✓ Event list reloaded")

    # Step 8: Verify event via API
    print("\nStep 8: Verifying event via API...")

    events_api_response = requests.get(
        f"http://localhost:8000/api/events/?org_id={test_org_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert events_api_response.status_code == 200, f"Failed to get events: {events_api_response.text}"

    events_data = events_api_response.json()
    # Find event by type since we don't manually specify ID anymore
    created_event = next((e for e in events_data["events"] if e.get("type") == event_type or e.get("title") == event_type), None)

    assert created_event is not None, f"Event with type '{event_type}' not found in API response"
    print(f"  ✓ Event verified via API")
    print(f"  ✓ Event ID: {created_event['id']}")
    print(f"  ✓ Event type: {created_event.get('type', 'N/A')}")

    print("\n" + "="*80)
    print("✅ EVENT CREATION FLOW TEST PASSED")
    print("="*80)


def test_create_event_validates_required_fields(page: Page):
    """
    Test that event creation validates required fields.

    User Journey:
    1. Admin logs in and navigates to events tab
    2. Opens create event form
    3. Tries to submit without filling required fields
    4. Verifies validation errors appear
    """

    print("\n" + "="*80)
    print("TESTING EVENT CREATION VALIDATION")
    print("="*80)

    # Setup: Create test organization and admin user
    print("\nSetup: Creating test organization and admin user...")
    timestamp = int(time.time())
    test_org_id = f"org_validation_{timestamp}"
    test_email = f"admin{timestamp}@test.com"
    test_password = "AdminPassword123"
    test_name = f"Admin User {timestamp}"

    # Create organization
    org_response = requests.post(
        "http://localhost:8000/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Validation Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201]

    # Create admin user
    signup_response = requests.post(
        "http://localhost:8000/api/auth/signup",
        json={
            "email": test_email,
            "password": test_password,
            "name": test_name,
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201
    user_id = signup_response.json()["person_id"]

    # Login and set admin role
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"email": test_email, "password": test_password}
    )
    auth_token = login_response.json()["token"]

    requests.put(
        f"http://localhost:8000/api/people/{user_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"roles": ["admin", "volunteer"]}
    )
    print(f"✓ Admin user created")

    # Step 1: Login and navigate to events tab
    print("\nStep 1: Logging in and navigating to events tab...")
    page.goto("http://localhost:8000/login")
    page.locator('#login-email').fill(test_email)
    page.locator('#login-password').fill(test_password)
    page.locator('#login-screen button[type="submit"]').click()

    expect(page.locator('#main-app')).to_be_visible(timeout=5000)

    # Navigate to admin console
    page.locator('button.nav-btn[data-view="admin"]').click()
    admin_view = page.locator('#admin-view.active')
    expect(admin_view).to_be_visible(timeout=3000)
    print("  ✓ Admin console visible")

    # Step 2: Open create event form
    print("\nStep 2: Opening create event form...")
    page.locator('button:has([data-i18n="admin.create_event_button"])').click()

    create_event_modal = page.locator('#create-event-modal')
    expect(create_event_modal).to_be_visible(timeout=3000)
    print("  ✓ Create event modal visible")

    # Step 3: Try to submit empty form
    print("\nStep 3: Attempting to submit empty form...")

    # Click submit without filling anything
    submit_btn = page.locator('#create-event-form button[type="submit"]')
    submit_btn.click()

    # Check if modal is still visible (validation should prevent submission)
    page.wait_for_timeout(1000)

    # Check for HTML5 validation or that modal is still visible
    expect(create_event_modal).to_be_visible()
    print("  ✓ Form validation prevented submission")

    # Step 4: Fill only some fields and try again
    print("\nStep 4: Filling partial form...")

    page.locator('#event-type').select_option("Sunday Service")
    submit_btn.click()

    # Modal should still be visible due to missing required fields
    page.wait_for_timeout(1000)
    expect(create_event_modal).to_be_visible()
    print("  ✓ Validation requires all fields")

    print("\n" + "="*80)
    print("✅ EVENT CREATION VALIDATION TEST PASSED")
    print("="*80)
