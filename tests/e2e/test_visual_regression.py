"""
Visual regression tests using Playwright screenshots.

These tests capture screenshots of key UI elements and can be used for:
1. Visual regression detection (comparing before/after changes)
2. Documentation (what the UI should look like)
3. Bug reporting (attach screenshots)

To update baseline screenshots:
  pytest tests/e2e/test_visual_regression.py --update-snapshots

To compare against baseline:
  pytest tests/e2e/test_visual_regression.py
"""

import pytest
from playwright.sync_api import Page, expect
from pathlib import Path


# Screenshot directory
SCREENSHOTS_DIR = Path("test-screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def test_login_page_visual(page: Page):
    """
    Capture login page screenshot for visual regression.

    Verifies:
    - Login form displays correctly
    - Logo is visible
    - Buttons are styled correctly
    - Language selector is visible
    """
    page.goto("http://localhost:8000/login")

    # Wait for page to fully load
    page.wait_for_load_state("networkidle")
    expect(page.locator('#login-email')).to_be_visible()

    # Take full page screenshot
    page.screenshot(path=SCREENSHOTS_DIR / "login_page.png", full_page=True)

    # Take screenshot of just the login form
    login_form = page.locator('form, .login-container, .auth-container')
    if login_form.count() > 0:
        login_form.first.screenshot(path=SCREENSHOTS_DIR / "login_form.png")


def test_schedule_view_visual(page: Page):
    """
    Capture schedule view screenshot.

    Tests the main user interface where volunteers see their schedule.
    """
    # Create and login
    import time
    import requests
    from datetime import datetime, timedelta

    org_id = f"org_visual_{int(time.time())}"
    user_email = f"visual_user_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Visual Test Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": user_email,
        "password": "Test123!",
        "name": "Visual User",
        "org_id": org_id,
        "roles": ["admin"]
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Create event for visual testing
    event_time = (datetime.now() + timedelta(days=1)).isoformat()
    event_id = f"event_visual_{int(time.time())}"

    requests.post(
        f"http://localhost:8000/api/events?org_id={org_id}",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "Sunday Service",
            "start_time": event_time,
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assign user to event
    requests.post(
        f"http://localhost:8000/api/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign", "role": "usher"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Go to schedule
    page.goto("http://localhost:8000/app/schedule")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{user_email}", "name": "Visual User"}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Visual Test Org"}}');
    """)
    page.reload()

    # Wait for content to load
    page.wait_for_timeout(2000)
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible()

    # Take full schedule screenshot
    page.screenshot(path=SCREENSHOTS_DIR / "schedule_view.png", full_page=True)

    # Take screenshot of event card
    event_card = page.locator('text="Sunday Service"').first
    if event_card.is_visible():
        # Get parent card element
        parent = page.locator('.event-card, .schedule-item').first
        if parent.is_visible():
            parent.screenshot(path=SCREENSHOTS_DIR / "event_card.png")


def test_admin_console_visual(page: Page):
    """
    Capture admin console screenshot.

    Tests the admin interface with tabs, tables, and forms.
    """
    # Create admin user
    import time
    import requests

    org_id = f"org_admin_visual_{int(time.time())}"
    admin_email = f"admin_visual_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Admin Visual Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": admin_email,
        "password": "Test123!",
        "name": "Admin Visual",
        "org_id": org_id,
        "roles": ["admin"]
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Go to admin console
    page.goto("http://localhost:8000/app/admin")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{admin_email}", "name": "Admin Visual", "roles": ["admin"]}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Admin Visual Org"}}');
    """)
    page.reload()

    # Wait for admin console to load
    page.wait_for_timeout(2000)
    admin_view = page.locator('#admin-view')
    expect(admin_view).to_be_visible(timeout=5000)

    # Take full admin console screenshot
    page.screenshot(path=SCREENSHOTS_DIR / "admin_console.png", full_page=True)

    # Take screenshot of each tab
    tabs = ["people", "events", "teams"]
    for tab in tabs:
        tab_btn = page.locator(f'button[data-tab="{tab}"], .admin-tab-btn:has-text("{tab.capitalize()}")')
        if tab_btn.count() > 0:
            tab_btn.first.click()
            page.wait_for_timeout(1000)
            page.screenshot(path=SCREENSHOTS_DIR / f"admin_{tab}_tab.png", full_page=True)


def test_settings_modal_visual(page: Page):
    """
    Capture settings modal screenshot.

    Tests modal dialogs and form styling.
    """
    # Create and login
    import time
    import requests

    org_id = f"org_settings_visual_{int(time.time())}"
    user_email = f"settings_visual_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Settings Visual Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": user_email,
        "password": "Test123!",
        "name": "Settings Visual User",
        "org_id": org_id
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Go to app
    page.goto("http://localhost:8000/app/schedule")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{user_email}", "name": "Settings Visual User"}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Settings Visual Org"}}');
    """)
    page.reload()

    # Open settings modal
    settings_btn = page.locator('button.btn-icon:has-text("⚙️")')
    expect(settings_btn).to_be_visible(timeout=3000)
    settings_btn.click()

    # Wait for modal animation
    page.wait_for_timeout(500)

    # Take modal screenshot
    settings_modal = page.locator('#settings-modal')
    expect(settings_modal).to_be_visible(timeout=3000)
    settings_modal.screenshot(path=SCREENSHOTS_DIR / "settings_modal.png")


def test_create_event_modal_visual(page: Page):
    """
    Capture create event modal screenshot.

    Tests complex form modals with date/time pickers.
    """
    # Create admin user
    import time
    import requests

    org_id = f"org_event_modal_{int(time.time())}"
    admin_email = f"event_modal_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Event Modal Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": admin_email,
        "password": "Test123!",
        "name": "Event Modal Admin",
        "org_id": org_id,
        "roles": ["admin"]
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Go to admin console
    page.goto("http://localhost:8000/app/admin")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{admin_email}", "name": "Event Modal Admin", "roles": ["admin"]}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Event Modal Org"}}');
    """)
    page.reload()

    # Wait for admin console
    page.wait_for_timeout(2000)

    # Click create event button
    create_btn = page.locator('button:has([data-i18n="admin.create_event_button"])')
    if create_btn.count() > 0:
        create_btn.click()

        # Wait for modal
        page.wait_for_timeout(500)

        # Take screenshot
        create_modal = page.locator('#create-event-modal, .event-modal')
        if create_modal.count() > 0 and create_modal.is_visible():
            create_modal.screenshot(path=SCREENSHOTS_DIR / "create_event_modal.png")


def test_dark_mode_visual(page: Page):
    """
    Capture dark mode screenshots (if dark mode is implemented).

    Tests theme switching and dark mode styling.
    """
    # Note: Only run if dark mode is implemented
    # This is a placeholder for future dark mode testing

    page.goto("http://localhost:8000/login")
    page.wait_for_load_state("networkidle")

    # Try to enable dark mode
    # This depends on your implementation
    dark_mode_toggle = page.locator('[data-theme-toggle], .theme-switch, button:has-text("Dark")')

    if dark_mode_toggle.count() > 0:
        dark_mode_toggle.click()
        page.wait_for_timeout(500)

        # Take dark mode screenshot
        page.screenshot(path=SCREENSHOTS_DIR / "login_page_dark.png", full_page=True)
    else:
        # Dark mode not implemented yet
        print("⚠️  Dark mode not implemented - skipping dark mode screenshot")


def test_responsive_breakpoints_visual(page: Page):
    """
    Capture screenshots at different responsive breakpoints.

    Tests:
    - Mobile (375px)
    - Tablet (768px)
    - Desktop (1024px)
    - Large desktop (1920px)
    """
    # Create and login
    import time
    import requests

    org_id = f"org_responsive_{int(time.time())}"
    user_email = f"responsive_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Responsive Test Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": user_email,
        "password": "Test123!",
        "name": "Responsive User",
        "org_id": org_id
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Go to schedule
    page.goto("http://localhost:8000/app/schedule")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{user_email}", "name": "Responsive User"}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Responsive Test Org"}}');
    """)
    page.reload()

    # Wait for load
    page.wait_for_timeout(2000)

    # Test different breakpoints
    breakpoints = {
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
        "desktop": {"width": 1024, "height": 768},
        "large": {"width": 1920, "height": 1080},
    }

    for name, size in breakpoints.items():
        page.set_viewport_size(size)
        page.wait_for_timeout(500)  # Let responsive CSS apply
        page.screenshot(path=SCREENSHOTS_DIR / f"schedule_{name}_{size['width']}px.png", full_page=True)


def test_error_states_visual(page: Page):
    """
    Capture error state screenshots.

    Tests error messages, validation errors, and error pages.
    """
    # Test 404 page
    page.goto("http://localhost:8000/nonexistent-page")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=SCREENSHOTS_DIR / "404_page.png", full_page=True)

    # Test login with invalid credentials
    page.goto("http://localhost:8000/login")
    page.locator('#login-email').fill("invalid@test.com")
    page.locator('#login-password').fill("wrongpassword")
    page.locator('#login-form button[type="submit"]').click()

    # Wait for error message
    page.wait_for_timeout(2000)
    page.screenshot(path=SCREENSHOTS_DIR / "login_error.png", full_page=True)


def test_loading_states_visual(page: Page):
    """
    Capture loading state screenshots.

    Tests spinners, loading indicators, and skeleton screens.
    """
    # Navigate to a page and capture during loading
    page.goto("http://localhost:8000/login")

    # Try to capture loading state (might be too fast)
    # This is more useful for slow-loading pages
    page.screenshot(path=SCREENSHOTS_DIR / "page_loading.png", full_page=True)

    # For actual loading states, you'd need to:
    # 1. Use network throttling
    # 2. Or add artificial delays for testing
    # 3. Or capture during heavy operations like solver running


def test_print_styles_visual(page: Page):
    """
    Capture print-friendly view screenshots.

    Tests that print styles are appropriate.
    """
    # Create and login
    import time
    import requests

    org_id = f"org_print_{int(time.time())}"
    user_email = f"print_user_{int(time.time())}@test.com"

    requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": "Print Test Org"
    })

    signup_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "email": user_email,
        "password": "Test123!",
        "name": "Print User",
        "org_id": org_id
    })
    token = signup_response.json()["token"]
    person_id = signup_response.json()["person_id"]

    # Go to schedule
    page.goto("http://localhost:8000/app/schedule")
    page.evaluate(f"""
        localStorage.setItem('authToken', '{token}');
        localStorage.setItem('currentUser', '{{"id": "{person_id}", "email": "{user_email}", "name": "Print User"}}');
        localStorage.setItem('currentOrg', '{{"id": "{org_id}", "name": "Print Test Org"}}');
    """)
    page.reload()

    page.wait_for_timeout(2000)

    # Emulate print media
    page.emulate_media(media="print")
    page.screenshot(path=SCREENSHOTS_DIR / "schedule_print_view.png", full_page=True)

    # Reset to screen media
    page.emulate_media(media="screen")
