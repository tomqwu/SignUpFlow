"""
Test clicking the View button to download CSV
"""
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Capture console messages and errors
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type()}] {msg.text()}"))

    print("1. Login as admin...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a:has-text("Sign in")').click()
    page.wait_for_timeout(500)
    page.fill('#login-email', 'pastor@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
    print("   ✓ Logged in")

    print("\n2. Navigate to Admin Dashboard...")
    admin_btn = page.locator('button:has-text("Admin Dashboard")')
    admin_btn.click()
    page.wait_for_timeout(1000)
    print("   ✓ Clicked Admin Dashboard")

    # Check if admin tab content is visible
    admin_content = page.locator('#admin-panel')
    if admin_content.count() > 0 and admin_content.is_visible():
        print("   ✓ Admin panel is visible")
    else:
        print("   ✗ Admin panel NOT visible")
        page.screenshot(path='/tmp/admin_not_visible.png')

    print("\n3. Wait for schedules to load...")
    page.wait_for_timeout(2000)

    # Check the schedules list element
    solutions_list = page.locator('#admin-solutions-list')
    if solutions_list.count() > 0:
        html = solutions_list.inner_html()
        print(f"   Solutions list HTML ({len(html)} chars):")
        print(f"   {html[:500]}")

        # Check if it contains schedule items
        if 'Schedule' in html and 'View' in html:
            print("   ✓ Schedules loaded with View buttons")
        elif 'Loading' in html:
            print("   ⚠ Still loading...")
        elif 'No schedules' in html:
            print("   ⚠ No schedules message shown")
        else:
            print("   ⚠ Unexpected content")

    print("\n4. Looking for View buttons...")
    view_buttons = page.locator('button:has-text("View")')
    count = view_buttons.count()
    print(f"   Found {count} View buttons")

    if count > 0:
        print("\n5. Clicking first View button...")
        btn = view_buttons.first

        # Scroll into view
        try:
            btn.scroll_into_view_if_needed()
            print("   ✓ Scrolled to button")
        except Exception as e:
            print(f"   ✗ Scroll failed: {e}")
            page.screenshot(path='/tmp/scroll_failed.png')

        page.wait_for_timeout(500)

        # Check if visible
        is_visible = btn.is_visible()
        print(f"   Button visible: {is_visible}")

        if is_visible:
            # Set up download listener
            download_promise = page.expect_download(timeout=5000)

            # Click the button
            btn.click()
            print("   ✓ Clicked View button")

            # Wait for download
            try:
                download = download_promise.value
                print(f"   ✓ Download started: {download.suggested_filename}")

                # Save the download
                download.save_as('/tmp/downloaded_schedule.csv')
                print(f"   ✓ Saved to /tmp/downloaded_schedule.csv")

                # Read and verify content
                with open('/tmp/downloaded_schedule.csv', 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"\n   CSV Content ({len(lines)} lines):")
                    for line in lines[:5]:
                        print(f"   {line}")

                    if 'Event ID' in content and 'Sarah Johnson' in content:
                        print("\n   ✅ CSV export WORKS!")
                    else:
                        print("\n   ⚠ CSV content unexpected")

            except Exception as e:
                print(f"   ✗ Download failed: {e}")
                page.screenshot(path='/tmp/download_failed.png')
        else:
            print("   ✗ Button not visible, taking screenshot")
            page.screenshot(path='/tmp/button_not_visible.png', full_page=True)
    else:
        print("\n   ✗ No View buttons found")
        page.screenshot(path='/tmp/no_view_buttons.png', full_page=True)

    # Print console messages
    if console_msgs:
        print("\n📝 Console messages:")
        for msg in console_msgs[-10:]:
            print(f"   {msg}")

    browser.close()

print("\n✅ Test complete")
