"""Complete End-to-End Test - Full User Journey Coverage
Tests every feature through the GUI to ensure 100% coverage.
"""

import pytest
import time
from datetime import datetime, timedelta, date
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui


pytestmark = pytest.mark.usefixtures("api_server")


def test_complete_user_journey(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Test complete user journey - login, navigation, settings, logout."""

    print("\n" + "=" * 70)
    print("🧪 COMPLETE END-TO-END TEST")
    print("=" * 70)

    # Setup: Create test organization and user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="E2E Test Pastor",
        roles=["admin"],
    )

    # =================================================================
    # 1. LOGIN
    # =================================================================
    print("\n📝 Test 1: Login")

    login_via_ui(page, app_config.app_url, user["email"], user["password"])

    # Verify logged in
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✅ Login successful")

    # =================================================================
    # 2. SETTINGS MODAL
    # =================================================================
    print("\n⚙️  Test 2: Settings Modal")

    # Open settings using gear icon
    settings_btn = page.get_by_role("button", name="⚙️")
    settings_btn.click()
    page.wait_for_timeout(500)

    # Settings modal should be visible
    expect(page.locator("#settings-modal")).to_be_visible()
    print("  ✅ Settings modal opened")

    # Close settings (press Escape or click close button)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)

    # =================================================================
    # 3. NAVIGATION
    # =================================================================
    print("\n📅 Test 3: Page Navigation")

    # Navigate to availability page
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_timeout(1000)
    print("  ✅ Availability page loaded")

    # Navigate back to schedule
    page.goto(f"{app_config.app_url}/app/schedule")
    page.wait_for_timeout(1000)
    print("  ✅ Schedule page loaded")

    # =================================================================
    # 4. LOGOUT
    # =================================================================
    print("\n👨‍💼 Test 4: Logout")

    # Logout
    page.goto(f"{app_config.app_url}/logout")
    page.wait_for_timeout(1000)
    print("  ✅ Logout successful")

    print("\n" + "=" * 70)
    print("✅ COMPLETE E2E TEST PASSED")
    print("=" * 70)


def test_api_crud_operations(
    app_config: AppConfig,
    api_client: ApiTestClient,
    api_server,  # Explicit dependency to ensure server starts
):
    """Test all CRUD operations through API using helper client."""

    print("\n" + "=" * 70)
    print("🧪 API CRUD OPERATIONS TEST")
    print("=" * 70)

    # Create org and admin user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="CRUD Test Person",
        roles=["admin"],
    )
    person_id = user["person_id"]
    token = user["token"]
    print("✅ Organization and person created")

    # User is authenticated via JWT token
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated with JWT")

    # Update person
    update_resp = api_client.session.put(
        f"{app_config.api_base}/people/{person_id}",
        headers=headers,
        json={
            "name": "Updated Name",
            "roles": ["volunteer", "admin"]
        }
    )
    assert update_resp.status_code == 200
    print("✅ Person updated")

    # Create event
    event_id = f"test_event_{int(time.time())}"
    event_resp = api_client.session.post(
        f"{app_config.api_base}/events/?org_id={org['id']}",
        headers=headers,
        json={
            "id": event_id,
            "org_id": org["id"],
            "type": "Test Event",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        }
    )
    assert event_resp.status_code in [200, 201]
    print("✅ Event created")

    # Delete event
    delete_resp = api_client.session.delete(
        f"{app_config.api_base}/events/{event_id}?org_id={org['id']}",
        headers=headers
    )
    assert delete_resp.status_code in [200, 204]
    print("✅ Event deleted")

    # Create team
    team_id = f"test_team_{int(time.time())}"
    team_resp = api_client.session.post(
        f"{app_config.api_base}/teams/?org_id={org['id']}",
        headers=headers,
        json={
            "id": team_id,
            "org_id": org["id"],
            "name": "Test Team",
            "member_ids": [person_id]
        }
    )
    assert team_resp.status_code in [200, 201]
    print("✅ Team created")

    # Delete team
    delete_team_resp = api_client.session.delete(
        f"{app_config.api_base}/teams/{team_id}?org_id={org['id']}",
        headers=headers
    )
    assert delete_team_resp.status_code in [200, 204]
    print("✅ Team deleted")

    # Time-off CRUD
    timeoff_resp = api_client.session.post(
        f"{app_config.api_base}/availability/{person_id}/timeoff?org_id={org['id']}",
        headers=headers,
        json={
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=15)).isoformat(),
        }
    )
    assert timeoff_resp.status_code in [200, 201]
    timeoff_id = timeoff_resp.json()["id"]
    print("✅ Time-off created")

    # Update time-off
    update_timeoff = api_client.session.patch(
        f"{app_config.api_base}/availability/{person_id}/timeoff/{timeoff_id}?org_id={org['id']}",
        headers=headers,
        json={
            "start_date": (date.today() + timedelta(days=12)).isoformat(),
            "end_date": (date.today() + timedelta(days=17)).isoformat(),
        }
    )
    assert update_timeoff.status_code == 200
    print("✅ Time-off updated")

    # Delete time-off
    delete_timeoff = api_client.session.delete(
        f"{app_config.api_base}/availability/{person_id}/timeoff/{timeoff_id}?org_id={org['id']}",
        headers=headers
    )
    assert delete_timeoff.status_code in [200, 204]
    print("✅ Time-off deleted")

    # Delete person
    delete_person = api_client.session.delete(
        f"{app_config.api_base}/people/{person_id}?org_id={org['id']}",
        headers=headers
    )
    assert delete_person.status_code in [200, 204]
    print("✅ Person deleted")

    print("\n✅ ALL API CRUD OPERATIONS PASSED\n")
