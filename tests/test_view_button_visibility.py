"""
Test View button visibility in admin dashboard
"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

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

    # Take screenshot of admin dashboard
    page.screenshot(path='/tmp/admin_dashboard.png', full_page=True)
    print("   Screenshot: /tmp/admin_dashboard.png")

    print("\n3. Checking schedules section...")
    # Check if schedules section exists
    schedules_section = page.locator('#admin-schedules')
    if schedules_section.count() > 0:
        print(f"   ✓ Schedules section exists")
        is_visible = schedules_section.is_visible()
        print(f"   Visibility: {is_visible}")
    else:
        print(f"   ✗ Schedules section NOT FOUND")

    print("\n4. Checking schedule items...")
    # Check for schedule items
    schedule_items = page.locator('.schedule-item')
    count = schedule_items.count()
    print(f"   Found {count} schedule items")

    if count > 0:
        for i in range(count):
            item = schedule_items.nth(i)
            text = item.inner_text()
            is_visible = item.is_visible()
            print(f"   Schedule {i+1}: visible={is_visible}")
            print(f"   Text: {text[:100]}...")

    print("\n5. Checking View buttons...")
    view_buttons = page.locator('button:has-text("View")')
    count = view_buttons.count()
    print(f"   Found {count} View buttons in DOM")

    if count > 0:
        for i in range(count):
            btn = view_buttons.nth(i)
            is_visible = btn.is_visible()
            is_enabled = btn.is_enabled()
            box = btn.bounding_box()
            print(f"   Button {i+1}: visible={is_visible}, enabled={is_enabled}, box={box}")

    print("\n6. Checking for Export buttons as alternative...")
    export_buttons = page.locator('button:has-text("Export")')
    count = export_buttons.count()
    print(f"   Found {count} Export buttons")

    print("\n7. Looking for any schedule-related buttons...")
    all_buttons = page.locator('#admin-schedules button')
    count = all_buttons.count()
    print(f"   Found {count} total buttons in schedules section")
    for i in range(min(count, 5)):
        btn = all_buttons.nth(i)
        text = btn.inner_text()
        is_visible = btn.is_visible()
        print(f"   Button {i+1}: '{text}' visible={is_visible}")

    print("\n8. Checking page HTML structure...")
    # Get the schedules section HTML
    if schedules_section.count() > 0:
        html = schedules_section.inner_html()
        print(f"   Schedules HTML length: {len(html)} chars")
        # Check if 'View' appears in the HTML
        if 'View' in html:
            print(f"   ✓ 'View' text found in HTML")
            # Find the context
            idx = html.find('View')
            snippet = html[max(0, idx-100):min(len(html), idx+100)]
            print(f"   Context: ...{snippet}...")
        else:
            print(f"   ✗ 'View' text NOT in HTML")

    browser.close()

print("\n✅ Investigation complete")
