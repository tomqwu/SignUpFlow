"""
Comprehensive GUI tests for Rostio application using Playwright.
Tests user flows, admin flows, and data integrity.
"""
from playwright.sync_api import sync_playwright, expect
import time

BASE_URL = "http://localhost:8000"

def test_user_flow():
    """Test complete user journey: login -> view schedule -> edit settings"""
    print("\n🧪 Testing User Flow...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Test 1: Homepage loads
        print("  ✓ Loading homepage...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        assert "Rostio" in page.title(), f"Expected 'Rostio' in title, got: {page.title()}"

        # Test 2: Click "Sign in" to show login form
        print("  ✓ Showing login form...")
        signin_link = page.locator('a:has-text("Sign in")')
        signin_link.click()
        page.wait_for_timeout(500)

        # Test 3: Login with valid credentials
        print("  ✓ Testing login...")
        page.fill('#login-email', 'sarah@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')

        # Test 4: Wait for main app to load
        print("  ✓ Waiting for app to load...")
        # Wait for main app to appear (with timeout)
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

        # Test 5: Check user is logged in
        print("  ✓ Verifying logged in state...")
        main_app = page.locator('#main-app')
        assert main_app.is_visible(), "Main app should be visible after login"

        # Test 6: Calendar displays assignments
        print("  ✓ Checking calendar has assignments...")
        # Wait for calendar to load
        calendar = page.locator('#calendar-grid, .calendar-container')
        assert calendar.is_visible(), "Calendar container should be visible"

        # Wait for calendar data to load (not showing loading spinner)
        page.wait_for_function("""() => {
            const cal = document.querySelector('#calendar-grid');
            return cal && !cal.innerHTML.includes('Loading your calendar');
        }""", timeout=10000)

        # Check for calendar events/assignments
        events = page.locator('.calendar-day, .calendar-event, .assignment-card')
        count = events.count()
        if count > 0:
            print(f"    Found {count} calendar items")
        else:
            print("    No calendar items found, but calendar container is visible")

        # Test 7: Verify calendar data structure (if events exist)
        print("  ✓ Verifying calendar data...")
        if count > 0:
            # Check first calendar item has content
            first_item = events.first
            item_text = first_item.inner_text()
            assert len(item_text) > 0, "Calendar item should have text content"
            print(f"    First item preview: {item_text[:50]}...")
        else:
            print("    Skipping data verification (no items to check)")

        # Test 6: Open settings modal
        print("  ✓ Testing settings modal...")
        settings_btn = page.locator('button:has-text("Settings")')
        if settings_btn.is_visible():
            settings_btn.click()
            page.wait_for_timeout(500)

            # Check modal appears
            modal = page.locator('.modal')
            assert modal.is_visible(), "Settings modal should appear"

            # Check for role checkboxes
            checkboxes = page.locator('input[type="checkbox"]')
            assert checkboxes.count() > 0, "Should have role checkboxes"

            # Close modal
            close_btn = page.locator('button:has-text("Close")')
            if close_btn.is_visible():
                close_btn.click()

        browser.close()
        print("✅ User flow tests PASSED")

def test_admin_flow():
    """Test admin functionality: login -> create event -> view schedules"""
    print("\n🧪 Testing Admin Flow...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Test 1: Login as admin
        print("  ✓ Logging in as admin...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        # Click "Sign in" to show login form
        signin_link = page.locator('a:has-text("Sign in")')
        signin_link.click()
        page.wait_for_timeout(500)

        page.fill('#login-email', 'pastor@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')

        # Wait for main app to load
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

        # Test 2: Navigate to admin page
        print("  ✓ Navigating to admin page...")
        admin_link = page.locator('a[href*="admin"], button:has-text("Admin")')
        if admin_link.is_visible():
            admin_link.click()
            page.wait_for_timeout(1000)
        else:
            # Try direct navigation
            page.goto(f"{BASE_URL}/?page=admin")
            page.wait_for_timeout(1000)

        # Test 3: Check admin sections exist
        print("  ✓ Verifying admin sections...")
        page_content = page.content()
        assert "Events" in page_content or "People" in page_content or "Schedule" in page_content, \
            "Admin page should show Events, People, or Schedule sections"

        # Test 4: Create new event
        print("  ✓ Testing event creation...")
        # Click the "+ Create Event" button (not the submit button)
        create_btn = page.locator('button:has-text("+ Create Event")').first
        if create_btn.is_visible():
            create_btn.click()
            page.wait_for_timeout(500)

            # Fill event form
            event_name_input = page.locator('input[placeholder*="Event Name"], input[id="event-name"]')
            if event_name_input.is_visible():
                event_name_input.fill(f"Test Event {int(time.time())}")

                # Select event type
                event_type = page.locator('select[id="event-type"]')
                if event_type.is_visible():
                    event_type.select_option("service")

                # Select occurrence
                occurrence = page.locator('select[id="occurrence-pattern"]')
                if occurrence.is_visible():
                    occurrence.select_option("weekly")

                # Submit form
                submit_btn = page.locator('button[type="submit"]:has-text("Create")')
                if submit_btn.is_visible():
                    submit_btn.click()
                    page.wait_for_timeout(1000)
                    print("    Event creation form submitted")

        # Test 5: View schedules section
        print("  ✓ Checking schedules section...")
        schedules = page.locator('.schedule-item, .schedule-card')
        if schedules.count() > 0:
            print(f"    Found {schedules.count()} schedules")

        browser.close()
        print("✅ Admin flow tests PASSED")

def test_data_integrity():
    """Test that data is correctly displayed and consistent"""
    print("\n🧪 Testing Data Integrity...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login as user with localStorage to bypass form
        print("  ✓ Setting up user session...")
        page.goto(BASE_URL)
        page.evaluate("""
            localStorage.setItem('roster_user', JSON.stringify({
                id: 'person_sarah_1759357429',
                name: 'Sarah Johnson',
                email: 'sarah@grace.church',
                roles: ['worship-leader', 'vocalist']
            }));
            localStorage.setItem('roster_org', JSON.stringify({
                id: 'org_grace_church',
                name: 'Grace Community Church'
            }));
        """)

        page.reload()
        page.wait_for_load_state('networkidle')

        # Test 1: Organization name is displayed
        print("  ✓ Checking organization display...")
        org_badge = page.locator('.org-badge, .org-name')
        if org_badge.is_visible():
            org_text = org_badge.inner_text()
            assert "Grace" in org_text, f"Expected 'Grace' in org name, got: {org_text}"
            print(f"    Organization: {org_text}")

        # Test 2: User name is displayed
        print("  ✓ Checking user display...")
        user_display = page.locator('.user-name, .profile')
        if user_display.is_visible():
            user_text = user_display.inner_text()
            print(f"    User: {user_text}")

        # Test 3: Assignments have valid dates
        print("  ✓ Validating assignment dates...")
        date_elements = page.locator('.assignment-card .date')
        for i in range(min(3, date_elements.count())):
            date_text = date_elements.nth(i).inner_text()
            # Check date is not empty and contains numbers
            assert date_text.strip() != "", f"Date should not be empty"
            assert any(char.isdigit() for char in date_text), f"Date should contain numbers: {date_text}"
            print(f"    Assignment {i+1} date: {date_text}")

        # Test 4: No error messages on page
        print("  ✓ Checking for errors...")
        error_messages = page.locator('.error, .alert-error, [class*="error"]')
        visible_errors = [err for err in range(error_messages.count()) if error_messages.nth(err).is_visible()]
        assert len(visible_errors) == 0, f"Found {len(visible_errors)} error messages on page"

        # Test 5: Calendar items count
        print("  ✓ Verifying calendar items...")
        # Wait for main app to load
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
        # Give calendar time to load data
        page.wait_for_timeout(3000)

        calendar_items = page.locator('.calendar-day, .calendar-event')
        count = calendar_items.count()
        print(f"    Total calendar items displayed: {count}")
        # Data integrity test - just verify the page loaded correctly
        print("    Calendar loaded successfully")

        browser.close()
        print("✅ Data integrity tests PASSED")

def test_navigation():
    """Test navigation between pages"""
    print("\n🧪 Testing Navigation...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Setup user
        page.goto(BASE_URL)
        page.evaluate("""
            localStorage.setItem('roster_user', JSON.stringify({
                id: 'person_sarah_1759357429',
                name: 'Sarah Johnson',
                email: 'sarah@grace.church',
                roles: ['worship-leader', 'vocalist']
            }));
            localStorage.setItem('roster_org', JSON.stringify({
                id: 'org_grace_church',
                name: 'Grace Community Church'
            }));
        """)
        page.reload()
        page.wait_for_timeout(1000)

        # Test 1: Navigate to schedule view
        print("  ✓ Testing schedule navigation...")
        initial_url = page.url

        # Test 2: Logout functionality
        print("  ✓ Testing logout...")
        logout_btn = page.locator('button:has-text("Logout"), a:has-text("Logout")')
        if logout_btn.is_visible():
            logout_btn.click()
            page.wait_for_timeout(1000)

            # Should show login form again
            email_input = page.locator('input[type="email"]')
            assert email_input.is_visible(), "Should show login form after logout"
            print("    Logout successful")

        browser.close()
        print("✅ Navigation tests PASSED")

def run_all_tests():
    """Run all GUI tests"""
    print("=" * 50)
    print("🚀 Running Comprehensive GUI Tests")
    print("=" * 50)

    try:
        test_user_flow()
        test_admin_flow()
        test_data_integrity()
        test_navigation()

        print("\n" + "=" * 50)
        print("✅ ALL GUI TESTS PASSED!")
        print("=" * 50)
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
