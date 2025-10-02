"""
Test View Schedule functionality - Click on schedule and verify it displays
"""
from playwright.sync_api import sync_playwright
import requests

BASE_URL = "http://localhost:8000"

def test_view_schedule():
    print("\n" + "="*70)
    print("🧪 Testing View Schedule Button")
    print("="*70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login as admin
        print("\n1️⃣ Logging in as admin...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)
        page.fill('#login-email', 'pastor@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
        print("   ✓ Logged in")

        # Navigate to Admin Dashboard
        print("\n2️⃣ Navigating to Admin Dashboard...")
        admin_tab = page.locator('button:has-text("Admin Dashboard")')
        admin_tab.click()
        page.wait_for_timeout(1500)
        print("   ✓ On Admin Dashboard")

        # Check solutions in API
        print("\n3️⃣ Checking available solutions...")
        response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
        solutions = response.json()
        print(f"   Found {solutions['total']} solutions:")
        for sol in solutions['solutions']:
            print(f"      - Solution {sol['id']}: {sol['assignment_count']} assignments")

        # Look for schedule items in the UI
        print("\n4️⃣ Looking for schedule list items...")
        page.wait_for_timeout(1000)

        # Try different selectors for schedule items
        schedule_items = page.locator('.schedule-item, .schedule-card, .solution-item, [class*="schedule"], [class*="solution"]')
        count = schedule_items.count()
        print(f"   Found {count} potential schedule elements")

        # Take screenshot to see what's displayed
        page.screenshot(path='/tmp/admin_schedules_list.png', full_page=True)
        print("   📸 Screenshot saved: /tmp/admin_schedules_list.png")

        # Look for "View Schedule" or "View" buttons
        print("\n5️⃣ Looking for View buttons...")
        view_buttons = page.locator('button:has-text("View Schedule"), button:has-text("View"), a:has-text("View")')
        view_count = view_buttons.count()
        print(f"   Found {view_count} View buttons")

        if view_count > 0:
            print("\n6️⃣ Clicking first View button...")
            view_buttons.first.click()
            page.wait_for_timeout(2000)

            page.screenshot(path='/tmp/schedule_detail_view.png', full_page=True)
            print("   📸 Screenshot saved: /tmp/schedule_detail_view.png")

            # Check what's displayed
            page_text = page.inner_text('body')

            if "assignment" in page_text.lower():
                print("   ✓ Page contains 'assignment' text")

            if "schedule" in page_text.lower():
                print("   ✓ Page contains 'schedule' text")

            # Look for assignment details
            assignments = page.locator('.assignment, [class*="assignment"]')
            asn_count = assignments.count()
            print(f"   Found {asn_count} assignment elements")

            if asn_count > 0:
                print(f"\n   ✅ SUCCESS: Schedule view shows {asn_count} assignments")
                for i in range(min(3, asn_count)):
                    text = assignments.nth(i).inner_text()
                    print(f"      {i+1}. {text[:100]}")
            else:
                print(f"\n   ⚠️  No assignment elements found in view")
        else:
            print("\n   ⚠️  No View buttons found")
            print("   Checking page HTML for clues...")

            # Get page content
            content = page.content()
            if "solution" in content.lower():
                print("   Page HTML contains 'solution'")

            # Check if there's a table or list
            tables = page.locator('table')
            lists = page.locator('ul, ol')
            print(f"   Tables: {tables.count()}, Lists: {lists.count()}")

        browser.close()

    print("\n" + "="*70)
    print("✅ View Schedule Test Complete")
    print("="*70)

if __name__ == "__main__":
    test_view_schedule()
