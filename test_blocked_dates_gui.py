"""GUI test to verify blocked date warnings appear in Event Management."""

import sys
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, expect

API_BASE = "http://localhost:8000/api"
APP_URL = "http://localhost:8000"

def setup_test_scenario():
    """Set up Jane Smith with a blocked date on Oct 11, and an event on Oct 11."""
    print("\n" + "="*60)
    print("SETTING UP TEST SCENARIO")
    print("="*60)

    # Get Jane Smith's person_id
    jane_response = requests.get(f"{API_BASE}/people/?org_id=test_org")
    people = jane_response.json()['people']
    jane = next((p for p in people if p['email'] == 'jane@test.com'), None)

    if not jane:
        print("❌ Could not find Jane Smith")
        return None

    print(f"✅ Found Jane Smith: {jane['id']}")

    # Add blocked date for Jane on Oct 11, 2025
    blocked_start = "2025-10-11"
    blocked_end = "2025-10-11"
    timeoff_data = {
        "start_date": blocked_start,
        "end_date": blocked_end,
        "reason": "Testing blocked dates GUI"
    }

    # First, clear any existing timeoff
    existing_response = requests.get(f"{API_BASE}/availability/{jane['id']}/timeoff")
    if existing_response.status_code == 200:
        existing = existing_response.json().get('timeoff', [])
        for t in existing:
            if t['start_date'] == blocked_start or blocked_start in t['start_date']:
                requests.delete(f"{API_BASE}/availability/{jane['id']}/timeoff/{t['id']}")
                print(f"🗑️  Deleted existing timeoff {t['id']}")

    # Add new timeoff
    timeoff_response = requests.post(
        f"{API_BASE}/availability/{jane['id']}/timeoff",
        json=timeoff_data
    )

    if timeoff_response.status_code in [200, 201]:
        print(f"✅ Added blocked date for Jane: {blocked_start}")
    else:
        print(f"⚠️  Timeoff response: {timeoff_response.status_code} - {timeoff_response.text}")

    # Create an event on Oct 11, 2025 (or find existing event_001)
    event_start = datetime(2025, 10, 11, 10, 0)
    event_end = datetime(2025, 10, 11, 12, 0)

    event_data = {
        "id": "event_oct11_test",
        "org_id": "test_org",
        "type": "Test Event",
        "start_time": event_start.isoformat(),
        "end_time": event_end.isoformat(),
        "extra_data": {
            "role_counts": {
                "admin": 1,
                "volunteer": 1
            }
        }
    }

    # Try to create event (may already exist)
    event_response = requests.post(f"{API_BASE}/events/", json=event_data)
    if event_response.status_code in [200, 201]:
        print(f"✅ Created event on Oct 11: event_oct11_test")
    elif event_response.status_code == 409:
        print(f"ℹ️  Event already exists: event_oct11_test")
    else:
        print(f"⚠️  Event creation failed: {event_response.status_code}")

    # Assign Jane to this event
    assignment_data = {
        "person_id": jane['id'],
        "action": "assign"
    }

    assign_response = requests.post(
        f"{API_BASE}/events/event_oct11_test/assignments",
        json=assignment_data
    )

    if assign_response.status_code in [200, 201]:
        print(f"✅ Assigned Jane to event on her blocked date")
    elif "already assigned" in assign_response.text:
        print(f"ℹ️  Jane already assigned to event")
    else:
        print(f"⚠️  Assignment response: {assign_response.status_code} - {assign_response.text}")

    return {
        'jane_id': jane['id'],
        'event_id': 'event_oct11_test',
        'blocked_date': blocked_start
    }

def test_blocked_date_warnings():
    """Test that blocked date warnings appear in Event Management GUI."""
    scenario = setup_test_scenario()

    if not scenario:
        print("❌ Failed to set up test scenario")
        return False

    print("\n" + "="*60)
    print("STARTING GUI TEST")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Collect console messages
        page.on("console", lambda msg:
            print(f"[CONSOLE {msg.type}] {msg.text}") if msg.type in ["error", "warning", "log"] else None
        )

        try:
            # Login as Jane (admin)
            print("\n📱 Opening app and logging in as Jane...")
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            # Click sign in
            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            # Login
            page.fill('input[type="email"]', "jane@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            print("✅ Logged in successfully")

            # Navigate to Admin Dashboard
            print("\n📊 Navigating to Admin Dashboard...")
            admin_btn = page.locator('button[data-view="admin"]')
            if admin_btn.count() > 0:
                admin_btn.click()
                page.wait_for_timeout(2000)
                print("✅ Admin Dashboard opened")
            else:
                print("❌ Admin button not found")
                return False

            # Wait for events to load
            page.wait_for_timeout(3000)

            # Find the test event in the list
            print(f"\n🔍 Looking for event 'event_oct11_test' in Event Management...")

            # Take screenshot for debugging
            page.screenshot(path="/tmp/blocked_dates_gui_test.png")
            print("📸 Screenshot saved to /tmp/blocked_dates_gui_test.png")

            # Check if event exists in the list
            event_card = page.locator(f'[data-event-id="event_oct11_test"]')

            if event_card.count() == 0:
                print("⚠️  Event card not found - checking HTML content...")
                events_html = page.locator('#admin-events-list').inner_html()
                print(f"Events list HTML (first 500 chars): {events_html[:500]}")

                # Try alternative selector
                all_events = page.locator('.event-card').all()
                print(f"Found {len(all_events)} event cards total")

                for i, card in enumerate(all_events[:3]):
                    card_text = card.inner_text()
                    print(f"Event {i}: {card_text[:100]}")

                return False

            print(f"✅ Found event card")

            # Click "View Assignments" button to open assignment modal
            print("\n📋 Opening assignment modal...")
            view_btn = event_card.locator('button:has-text("View Assignments"), button:has-text("Assign People")')

            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_timeout(1500)
                print("✅ Clicked View Assignments")
            else:
                print("⚠️  View Assignments button not found in event card")
                card_html = event_card.inner_html()
                print(f"Event card HTML: {card_html[:300]}")

            # Check for blocked date warning in the assignment modal or event card
            print("\n🔍 Checking for BLOCKED warnings...")

            # Check in modal
            modal = page.locator('#assignment-modal')
            if modal.is_visible():
                modal_text = modal.inner_text()
                print(f"Modal content (first 500 chars): {modal_text[:500]}")

                if "BLOCKED" in modal_text or "blocked" in modal_text.lower():
                    print("✅ FOUND 'BLOCKED' warning in assignment modal!")
                    return True
                else:
                    print("❌ No 'BLOCKED' warning found in modal")
            else:
                print("⚠️  Assignment modal not visible")

            # Check in event card itself
            card_text = event_card.inner_text()
            print(f"Event card text: {card_text}")

            if "BLOCKED" in card_text or "blocked" in card_text.lower():
                print("✅ FOUND 'BLOCKED' warning in event card!")
                return True
            else:
                print("❌ No 'BLOCKED' warning found in event card")

            # Check for specific badge
            blocked_badge = page.locator('.event-blocked-badge, .schedule-badge-blocked')
            if blocked_badge.count() > 0:
                print(f"✅ FOUND {blocked_badge.count()} blocked badge(s)!")
                badge_text = blocked_badge.first.inner_text()
                print(f"Badge text: {badge_text}")
                return True
            else:
                print("❌ No blocked badge elements found")

            return False

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            browser.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BLOCKED DATES GUI TEST")
    print("="*60)

    success = test_blocked_date_warnings()

    print("\n" + "="*60)
    if success:
        print("✅ TEST PASSED: Blocked date warnings are visible in GUI")
        sys.exit(0)
    else:
        print("❌ TEST FAILED: Blocked date warnings NOT found in GUI")
        print("\nThis likely means:")
        print("1. Browser cache is serving old JavaScript (v<28)")
        print("2. The timestamp cache busting needs to take effect")
        print("3. Hard refresh required (Ctrl+Shift+R)")
        sys.exit(1)
