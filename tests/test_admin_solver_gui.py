"""
Comprehensive admin GUI test - Tests the "Run Solver" button and verifies schedules list
"""
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:8000"

def test_admin_run_solver():
    """Test admin can run solver and see schedule with correct assignment count"""
    print("\n🧪 Testing Admin Run Solver Workflow\n")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Enable console logging to debug
        page.on("console", lambda msg: print(f"  [CONSOLE] {msg.text()}"))

        # Step 1: Login as admin
        print("\n1️⃣ Logging in as admin...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        signin_link = page.locator('a:has-text("Sign in")')
        signin_link.click()
        page.wait_for_timeout(500)

        page.fill('#login-email', 'pastor@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')

        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
        print("   ✓ Logged in successfully")

        # Step 2: Check current solutions count
        print("\n2️⃣ Checking existing solutions...")
        import requests
        response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
        initial_solutions = response.json()
        initial_count = initial_solutions['total']
        print(f"   Initial solutions: {initial_count}")
        for sol in initial_solutions['solutions']:
            print(f"     - Solution {sol['id']}: {sol['assignment_count']} assignments")

        # Step 3: Look for admin panel/solver button in the page
        print("\n3️⃣ Looking for admin interface...")
        page.wait_for_timeout(2000)

        # Take screenshot to see what's visible
        page.screenshot(path='/tmp/admin_after_login.png')
        print("   Screenshot saved to /tmp/admin_after_login.png")

        # Check for admin-specific elements
        page_html = page.content()

        # Look for solver/generate schedule button
        solver_buttons = page.locator('button:has-text("Generate"), button:has-text("Run Solver"), button:has-text("Solve")')
        button_count = solver_buttons.count()
        print(f"   Found {button_count} solver-related buttons")

        # Look for admin tabs/navigation
        admin_tabs = page.locator('[data-view], .nav-btn, .tab')
        tab_count = admin_tabs.count()
        print(f"   Found {tab_count} navigation tabs/buttons")

        if tab_count > 0:
            print("   Tabs found:")
            for i in range(min(5, tab_count)):
                tab_text = admin_tabs.nth(i).inner_text()
                print(f"     - {tab_text}")

        # Step 4: Navigate to Admin Dashboard first
        print("\n4️⃣ Navigating to Admin Dashboard...")
        admin_tab = page.locator('button:has-text("Admin Dashboard"), [data-view="admin"]')
        if admin_tab.count() > 0:
            admin_tab.first.click()
            page.wait_for_timeout(1000)
            print("   ✓ Clicked Admin Dashboard tab")

        # Step 5: Try to click Run Solver if found
        if button_count > 0:
            print("\n5️⃣ Clicking solver button...")
            solver_button = solver_buttons.first
            solver_button.click()
            page.wait_for_timeout(5000)  # Wait for solver to complete

            # Check for success message
            page.screenshot(path='/tmp/admin_after_solve.png')
            print("   Screenshot saved to /tmp/admin_after_solve.png")

            # Check API for new solution
            response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
            after_solutions = response.json()
            after_count = after_solutions['total']
            print(f"\n   Solutions after clicking solver: {after_count}")
            for sol in after_solutions['solutions']:
                print(f"     - Solution {sol['id']}: {sol['assignment_count']} assignments")

            if after_count > initial_count:
                print(f"\n   ✅ SUCCESS: New solution created!")
                new_solution = after_solutions['solutions'][0]  # Latest solution
                assert new_solution['assignment_count'] > 0, \
                    f"❌ FAIL: New solution has 0 assignments"
                print(f"   ✅ New solution has {new_solution['assignment_count']} assignments")
            else:
                print(f"\n   ⚠️  WARNING: No new solution created")
        else:
            print("\n4️⃣ No solver button found - checking if we need to navigate")

            # Try clicking on "Admin" or "Schedule" tab
            admin_link = page.locator('button:has-text("Admin"), a:has-text("Admin"), [data-view="solver"], [data-view="admin"]')
            if admin_link.count() > 0:
                print("   Found admin navigation, clicking...")
                admin_link.first.click()
                page.wait_for_timeout(1000)
                page.screenshot(path='/tmp/admin_panel.png')
                print("   Screenshot saved to /tmp/admin_panel.png")

        # Step 6: Check schedules list
        print("\n6️⃣ Checking schedules list in UI...")
        schedule_items = page.locator('.schedule-item, .schedule-card, .solution-card')
        schedule_count = schedule_items.count()
        print(f"   Found {schedule_count} schedule items displayed")

        if schedule_count > 0:
            for i in range(min(3, schedule_count)):
                item_text = schedule_items.nth(i).inner_text()
                print(f"\n   Schedule {i+1}:")
                print(f"   {item_text[:300]}")

                # Check if it shows assignment count
                if "Assignments: 0" in item_text:
                    print(f"   ⚠️  WARNING: Schedule {i+1} shows 0 assignments")
                elif "Assignments:" in item_text:
                    print(f"   ✓ Schedule {i+1} shows assignment count")
        else:
            print("   ⚠️  No schedule items found in UI")
            print("   Checking page content for clues...")
            if "schedule" in page_html.lower():
                print("   Page contains 'schedule' text")
            if "solution" in page_html.lower():
                print("   Page contains 'solution' text")

        browser.close()

    print("\n" + "=" * 70)
    print("✅ Admin solver GUI test completed")
    print("=" * 70)

if __name__ == "__main__":
    test_admin_run_solver()
