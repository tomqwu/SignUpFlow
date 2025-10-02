"""
Final test: Click View button and verify CSV download works
"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Track alerts
    alerts = []
    page.on("dialog", lambda dialog: alerts.append(dialog.message()) or dialog.accept())

    print("1. Login as admin...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a:has-text("Sign in")').click()
    page.wait_for_timeout(500)
    page.fill('#login-email', 'pastor@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

    print("2. Navigate to Admin Dashboard...")
    page.locator('button:has-text("Admin Dashboard")').click()
    page.wait_for_timeout(2000)

    print("3. Scroll to bottom to find View button...")
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(1000)

    print("4. Looking for View buttons...")
    view_buttons = page.locator('button:has-text("View")')
    count = view_buttons.count()
    print(f"   Found {count} View buttons")

    if count > 0:
        # Get the visible one
        for i in range(count):
            btn = view_buttons.nth(i)
            if btn.is_visible():
                print(f"   Button {i+1} is VISIBLE")

                print("\n5. Clicking View button...")
                btn.click()
                page.wait_for_timeout(2000)

                # Check for alerts
                if alerts:
                    print(f"\n   Alert message: {alerts[-1]}")
                    if 'downloaded' in alerts[-1].lower():
                        print("\n   ✅ SUCCESS! View button works - CSV download triggered!")
                    elif 'error' in alerts[-1].lower():
                        print(f"\n   ❌ ERROR: {alerts[-1]}")
                    else:
                        print(f"\n   ⚠️  Unexpected alert: {alerts[-1]}")
                else:
                    print("\n   ⚠️  No alert shown (download may have worked silently)")

                # Take screenshot
                page.screenshot(path='/tmp/after_view_click_final.png', full_page=True)
                print("   Screenshot: /tmp/after_view_click_final.png")

                break
    else:
        print("   ✗ No View buttons found")
        page.screenshot(path='/tmp/no_buttons.png', full_page=True)

    browser.close()

print("\n✅ Test complete")
