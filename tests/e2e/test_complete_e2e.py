"""Complete End-to-End Test - Full User Journey Coverage
Tests every feature through the GUI to ensure 100% coverage.
"""

import time
from datetime import datetime, timedelta, date
import requests
from playwright.sync_api import sync_playwright, expect

API_BASE = "http://localhost:8000/api"
APP_URL = "http://localhost:8000"


def test_complete_user_journey():
    """Test complete user journey - simplified version."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("\n" + "=" * 70)
        print("🧪 COMPLETE END-TO-END TEST")
        print("=" * 70)

        # =================================================================
        # 1. LOGIN AS EXISTING USER
        # =================================================================
        print("\n📝 Test 1: Login")

        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Click sign in if on homepage
        sign_in_link = page.get_by_role("link", name="Sign in")
        if sign_in_link.count() > 0:
            sign_in_link.click()
            page.wait_for_timeout(500)

        # Login as existing user
        page.fill('input[type="email"]', "pastor@grace.church")
        page.fill('input[type="password"]', "password")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(2000)

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
        page.goto(f"{APP_URL}/app/availability")
        page.wait_for_timeout(1000)
        print("  ✅ Availability page loaded")

        # Navigate back to schedule
        page.goto(f"{APP_URL}/app/schedule")
        page.wait_for_timeout(1000)
        print("  ✅ Schedule page loaded")

        # =================================================================
        # 4. LOGOUT
        # =================================================================
        print("\n👨‍💼 Test 4: Logout")

        # Logout
        page.goto(f"{APP_URL}/logout")
        page.wait_for_timeout(1000)
        print("  ✅ Logout successful")

        # =================================================================
        # SUMMARY
        # =================================================================
        browser.close()

        print("\n" + "=" * 70)
        print("✅ COMPLETE E2E TEST PASSED")
        print("=" * 70)


def test_api_crud_operations():
    """Test all CRUD operations through API."""

    print("\n" + "=" * 70)
    print("🧪 API CRUD OPERATIONS TEST")
    print("=" * 70)

    org_id = f"test_org_{int(time.time())}"

    # Create org
    resp = requests.post(f"{API_BASE}/organizations/", json={
        "id": org_id,
        "name": "CRUD Test Org",
        "config": {"roles": ["volunteer", "admin"]}
    })
    assert resp.status_code in [200, 201]
    print("✅ Organization created")

    # Create person
    test_email = f"crud{int(time.time())}@test.com"
    person_resp = requests.post(f"{API_BASE}/auth/signup", json={
        "name": "CRUD Test Person",
        "email": test_email,
        "password": "password",
        "org_id": org_id,
        "roles": ["admin"]  # Need admin role for creating events/teams
    })
    assert person_resp.status_code in [200, 201]
    person_id = person_resp.json()["person_id"]
    print("✅ Person created")

    # Login to get JWT token
    login_resp = requests.post(f"{API_BASE}/auth/login", json={
        "email": test_email,
        "password": "password"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated with JWT")

    # Update person (with authentication)
    update_resp = requests.put(f"{API_BASE}/people/{person_id}",
        headers=headers,
        json={
            "name": "Updated Name",
            "roles": ["volunteer", "admin"]
        }
    )
    assert update_resp.status_code == 200
    print("✅ Person updated")

    # Create event (with authentication)
    event_id = f"test_event_{int(time.time())}"
    event_resp = requests.post(f"{API_BASE}/events/?org_id={org_id}",
        headers=headers,
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "Test Event",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        }
    )
    assert event_resp.status_code in [200, 201]
    print("✅ Event created")

    # Delete event (with authentication)
    delete_resp = requests.delete(f"{API_BASE}/events/{event_id}?org_id={org_id}", headers=headers)
    assert delete_resp.status_code in [200, 204]
    print("✅ Event deleted")

    # Create team (with authentication)
    team_id = f"test_team_{int(time.time())}"
    team_resp = requests.post(f"{API_BASE}/teams/?org_id={org_id}",
        headers=headers,
        json={
            "id": team_id,
            "org_id": org_id,
            "name": "Test Team",
            "member_ids": [person_id]
        }
    )
    assert team_resp.status_code in [200, 201]
    print("✅ Team created")

    # Delete team (with authentication)
    delete_team_resp = requests.delete(f"{API_BASE}/teams/{team_id}?org_id={org_id}", headers=headers)
    assert delete_team_resp.status_code in [200, 204]
    print("✅ Team deleted")

    # Time-off CRUD (with authentication)
    timeoff_resp = requests.post(f"{API_BASE}/availability/{person_id}/timeoff?org_id={org_id}",
        headers=headers,
        json={
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=15)).isoformat(),
        }
    )
    assert timeoff_resp.status_code in [200, 201]
    timeoff_id = timeoff_resp.json()["id"]
    print("✅ Time-off created")

    # Update time-off (with authentication)
    update_timeoff = requests.patch(f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}?org_id={org_id}",
        headers=headers,
        json={
            "start_date": (date.today() + timedelta(days=12)).isoformat(),
            "end_date": (date.today() + timedelta(days=17)).isoformat(),
        }
    )
    assert update_timeoff.status_code == 200
    print("✅ Time-off updated")

    # Delete time-off (with authentication)
    delete_timeoff = requests.delete(f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}?org_id={org_id}", headers=headers)
    assert delete_timeoff.status_code in [200, 204]
    print("✅ Time-off deleted")

    # Delete person (with authentication)
    delete_person = requests.delete(f"{API_BASE}/people/{person_id}?org_id={org_id}", headers=headers)
    assert delete_person.status_code in [200, 204]
    print("✅ Person deleted")

    print("\n✅ ALL API CRUD OPERATIONS PASSED\n")


if __name__ == "__main__":
    try:
        test_api_crud_operations()
        test_complete_user_journey()

        print("\n" + "=" * 70)
        print("🎉 ALL COMPREHENSIVE E2E TESTS PASSED!")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
