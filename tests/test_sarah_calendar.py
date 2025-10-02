"""
Test what Sarah Johnson actually sees in her calendar
"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    print("1. Loading homepage...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')

    print("2. Clicking 'Sign in'...")
    signin_link = page.locator('a:has-text("Sign in")')
    signin_link.click()
    page.wait_for_timeout(500)

    print("3. Logging in as Sarah Johnson...")
    page.fill('#login-email', 'sarah@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')

    print("4. Waiting for main app...")
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

    print("5. Waiting for calendar to load...")
    page.wait_for_timeout(3000)

    # Take screenshot
    page.screenshot(path='/tmp/sarah_calendar.png', full_page=True)
    print("   Screenshot saved to /tmp/sarah_calendar.png")

    # Check what's displayed
    print("\n6. Checking calendar content...")
    calendar_html = page.locator('#calendar-grid').inner_html()

    if "Loading" in calendar_html:
        print("   ⚠️  Calendar still loading...")
    elif "No schedule" in calendar_html or "No events" in calendar_html:
        print("   ❌ Calendar shows 'No schedule/events'")
    else:
        # Count calendar items
        items = page.locator('.calendar-day, .calendar-event')
        count = items.count()
        print(f"   ✓ Found {count} calendar items")

        # Show first few
        for i in range(min(5, count)):
            item_text = items.nth(i).inner_text()
            print(f"     {i+1}. {item_text[:100]}")

    print("\n7. Checking solutions API response...")
    import requests
    response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
    solutions = response.json()
    print(f"   Solutions: {solutions['total']}")
    for sol in solutions['solutions']:
        print(f"     - Solution {sol['id']}: {sol['assignment_count']} assignments")

    print("\n8. Press Enter to close browser...")
    input()

    browser.close()
