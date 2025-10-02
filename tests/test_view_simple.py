"""
Simple test: Click View button and check what happens
"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Track alerts
    alert_messages = []
    def handle_dialog(dialog):
        alert_messages.append(dialog.message)
        dialog.accept()
    page.on("dialog", handle_dialog)

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

    print("3. Scroll to Generated Schedules section...")
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(1000)

    print("4. Click View button...")
    view_buttons = page.locator('button:has-text("View")')
    count = view_buttons.count()
    print(f"   Found {count} View buttons")

    # Find visible button
    clicked = False
    for i in range(count):
        btn = view_buttons.nth(i)
        if btn.is_visible():
            print(f"   Clicking button {i+1}...")
            btn.click()
            clicked = True
            break

    if not clicked:
        print("   ✗ No visible buttons found")
    else:
        print("   ✓ Button clicked!")

        # Wait for response
        page.wait_for_timeout(3000)

        # Check alerts
        if alert_messages:
            print(f"\n✅ Alert shown: '{alert_messages[-1]}'")
            if 'downloaded' in alert_messages[-1].lower():
                print("✅ SUCCESS! CSV download works!")
            elif 'error' in alert_messages[-1].lower():
                print(f"❌ ERROR: {alert_messages[-1]}")
        else:
            print("\n⚠️  No alert (may have worked silently or failed)")

    browser.close()

print("\n✅ Test complete")
