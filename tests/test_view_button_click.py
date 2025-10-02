"""
Test clicking the View Schedule button to see what error appears
"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Capture console errors
    errors = []
    page.on("console", lambda msg: errors.append(f"[{msg.type()}] {msg.text()}") if msg.type() == "error" else None)
    page.on("pageerror", lambda err: errors.append(f"[PAGE ERROR] {err}"))

    print("1. Login as admin...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a:has-text("Sign in")').click()
    page.wait_for_timeout(500)
    page.fill('#login-email', 'pastor@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

    print("2. Go to Admin Dashboard...")
    page.locator('button:has-text("Admin Dashboard")').click()
    page.wait_for_timeout(2000)

    print("3. Run solver to create a schedule...")
    page.locator('button:has-text("Generate")').click()
    page.wait_for_timeout(6000)

    print("4. Looking for View button...")
    # The View button should now be visible in the schedules list
    view_buttons = page.locator('button:has-text("View")')
    count = view_buttons.count()
    print(f"   Found {count} View buttons")

    if count > 0:
        print("5. Clicking View button...")
        # Click the first View button
        view_buttons.first.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        view_buttons.first.click()
        page.wait_for_timeout(3000)

        # Take screenshot
        page.screenshot(path='/tmp/after_view_click.png', full_page=True)
        print("   Screenshot: /tmp/after_view_click.png")

        # Check for errors
        if errors:
            print(f"\n❌ JavaScript Errors Found:")
            for err in errors:
                print(f"   {err}")

        # Check for error messages in the page
        error_elements = page.locator('[class*="error"], .alert-danger')
        if error_elements.count() > 0:
            print(f"\n❌ Error Elements Found:")
            for i in range(error_elements.count()):
                text = error_elements.nth(i).inner_text()
                print(f"   {text}")

        # Check what's displayed
        body_text = page.inner_text('body')
        if "Error" in body_text:
            print(f"\n⚠️  Page contains 'Error' text")
            # Find the error message
            lines = body_text.split('\n')
            for line in lines:
                if 'Error' in line or 'error' in line:
                    print(f"   {line}")

    browser.close()

print("\n✅ Test complete")
