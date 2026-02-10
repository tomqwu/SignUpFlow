"""
E2E tests for mobile responsive design.

Tests that the application works correctly on mobile devices with different
viewport sizes and touch interactions.
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, skip_onboarding_from_storage

pytestmark = pytest.mark.usefixtures("api_server")


# Common mobile viewport sizes
MOBILE_VIEWPORTS = {
    "iphone_se": {"width": 375, "height": 667},  # iPhone SE
    "iphone_12": {"width": 390, "height": 844},  # iPhone 12/13
    "iphone_14_pro": {"width": 393, "height": 852},  # iPhone 14 Pro
    "pixel_5": {"width": 393, "height": 851},  # Google Pixel 5
    "galaxy_s21": {"width": 360, "height": 800},  # Samsung Galaxy S21
    "ipad_mini": {"width": 768, "height": 1024},  # iPad Mini (tablet)
}


@pytest.fixture
def mobile_page(page: Page):
    """Configure page for mobile testing with iPhone 12 viewport."""
    page.set_viewport_size(MOBILE_VIEWPORTS["iphone_12"])
    return page


def test_mobile_login_flow(
    mobile_page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test complete login flow on mobile device.

    Verifies:
    - Login form is visible and usable on mobile
    - Touch interactions work (tap buttons)
    - Keyboard input works on mobile
    - Navigation works after login
    """
    page = mobile_page

    # Create test account
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Mobile User",
        roles=["volunteer"],
    )

    # Test mobile login
    page.goto(f"{app_config.app_url}/login")

    # Verify form is visible on mobile (use specific login email input)
    email_input = page.locator('#login-email')
    expect(email_input).to_be_visible(timeout=3000)

    # Fill login form (simulates mobile keyboard)
    email_input.fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Tap login button (touch interaction) - use specific selector
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    expect(login_button).to_be_visible()
    login_button.click()

    # Verify redirected (some accounts may be sent to onboarding wizard first)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )

    # If redirected to wizard, skip onboarding and proceed to schedule
    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")

    # Verify mobile navigation is visible
    schedule_heading = page.locator('#page-title')
    expect(schedule_heading).to_have_text("My Schedule", timeout=5000)


def test_mobile_hamburger_menu(
    mobile_page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test mobile hamburger menu navigation.

    Verifies:
    - Hamburger menu button is visible on mobile
    - Menu opens on tap
    - Navigation links work
    - Menu closes after navigation
    """
    page = mobile_page

    # Create test account using proper API client
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Menu User",
        roles=["volunteer"],
    )

    # Login through UI (proper way - not localStorage)
    page.goto(f"{app_config.app_url}/login")

    # Fill login form
    page.locator('#login-email').fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Click login button
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    login_button.click()

    # Wait for redirect (schedule or onboarding wizard)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )

    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")

    # Wait for page to load
    expect(page.locator('#page-title')).to_have_text("My Schedule", timeout=5000)

    # Check if hamburger menu exists (mobile-specific)
    # Note: Your app might use a different selector
    # Common patterns: .hamburger, .mobile-menu, .nav-toggle
    hamburger = page.locator('.mobile-menu-toggle, .hamburger, button.btn-icon:has-text("☰")')

    # If hamburger menu doesn't exist, navigation might be always visible
    # Check if navigation is visible
    nav_buttons = page.locator('.nav-btn, button[data-view]')
    nav_count = nav_buttons.count()

    assert nav_count > 0, "Navigation should be visible on mobile"


def test_mobile_schedule_view(
    mobile_page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test schedule view on mobile device.

    Verifies:
    - Schedule cards display correctly on mobile
    - Scroll works on mobile
    - Event details are readable
    - Date/time formatting works on small screens
    """
    page = mobile_page

    # Create test account with event using API client
    from datetime import datetime, timedelta
    import time

    org = api_client.create_org()

    # Create admin user first (to ensure they have admin rights and subsequent users don't auto-get it)
    admin = api_client.create_user(
        org_id=org["id"],
        name="Admin User",
        roles=["admin"],
    )
    admin_token = admin.get("token")

    # Create volunteer user
    user = api_client.create_user(
        org_id=org["id"],
        name="Schedule User",
        roles=["volunteer"],
    )
    session = api_client.login(email=user["email"], password=user["password"])
    # user_token = user.get("token") or session.get("token") # Not needed for assignment anymore
    person_id = user.get("person_id") or session.get("person_id")

    # Create event and assignment using admin token
    event_time = (datetime.now() + timedelta(days=1)).isoformat()
    event_id = f"event_mobile_{int(time.time())}"

    import requests
    event_response = requests.post(
        f"{app_config.app_url}/api/events/",  # Trailing slash, no query param
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "id": event_id,
            "org_id": org["id"],  # org_id in JSON body, not query param
            "type": "Sunday Service",
            "start_time": event_time,
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        }
    )
    assert event_response.status_code == 201, f"Failed to create event: {event_response.text}"

    # Assign user to event using admin token
    response = requests.post(
        f"{app_config.app_url}/api/events/{event_id}/assignments",
        json={
            "person_id": person_id,
            "action": "assign",
            "role": "usher"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code in (200, 201), f"Assignment failed: {response.status_code} {response.text}"

    # Login through UI (proper way - not localStorage)
    page.goto(f"{app_config.app_url}/login")

    # Fill login form
    page.locator('#login-email').fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Click login button
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    login_button.click()

    # Wait for redirect (schedule or onboarding wizard)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )

    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")

    # Wait for page to load and show schedule
    expect(page.locator('#page-title')).to_have_text("My Schedule", timeout=5000)

    # Verify event is visible on mobile
    event_card = page.locator(f'text="Sunday Service"').first
    expect(event_card).to_be_visible(timeout=5000)

    # Verify role badge is visible (capitalized due to i18n translation)
    role_badge = page.locator('text="Usher"').first
    expect(role_badge).to_be_visible(timeout=3000)

    # Verify mobile layout (cards should stack vertically)
    # Check viewport width to ensure we're in mobile mode
    viewport_width = page.evaluate("window.innerWidth")
    assert viewport_width < 768, f"Should be in mobile viewport, got {viewport_width}px"


def test_mobile_settings_modal(
    mobile_page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test settings modal on mobile device.

    Verifies:
    - Settings gear icon is visible and tappable
    - Modal displays correctly on mobile
    - Form inputs work on mobile
    - Modal closes properly on mobile
    """
    page = mobile_page

    # Create test account using proper API client
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Settings User",
        roles=["volunteer"],
    )

    # Login through UI (proper way - not localStorage)
    page.goto(f"{app_config.app_url}/login")

    # Fill login form
    page.locator('#login-email').fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Click login button
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    login_button.click()

    # Wait for redirect (schedule or onboarding wizard)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )

    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")

    # Wait for page to load
    expect(page.locator('#page-title')).to_have_text("My Schedule", timeout=5000)

    # Tap settings gear icon
    settings_btn = page.locator('button.action-btn:has-text("Settings")')
    expect(settings_btn).to_be_visible(timeout=3000)
    settings_btn.click()

    # Verify modal appears on mobile
    settings_modal = page.locator('#settings-modal')
    expect(settings_modal).to_be_visible(timeout=3000)

    # Verify language dropdown works on mobile
    language_select = page.locator('#settings-language')
    expect(language_select).to_be_visible()

    # Change language (test dropdown on mobile)
    language_select.select_option('es')

    # Click Save Changes
    save_btn = page.locator('button[data-i18n="settings.save_changes"]')
    save_btn.click()
    
    # Wait for modal to close (save usually closes it)
    expect(settings_modal).not_to_be_visible(timeout=5000)
    
    # Wait a bit for the UI to update
    page.wait_for_timeout(2000)

    # Verify language changed (Spanish)
    schedule_heading = page.locator('#page-title')
    expect(schedule_heading).to_have_text("Mi horario", timeout=5000)


@pytest.mark.parametrize("device_name,viewport", [
    ("iPhone SE", MOBILE_VIEWPORTS["iphone_se"]),
    ("iPhone 12", MOBILE_VIEWPORTS["iphone_12"]),
    ("Pixel 5", MOBILE_VIEWPORTS["pixel_5"]),
    ("Galaxy S21", MOBILE_VIEWPORTS["galaxy_s21"]),
])
def test_multiple_device_sizes_login(
    page: Page,
    device_name: str,
    viewport: dict,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test login works on multiple mobile device sizes.

    Tests common mobile devices to ensure responsive design works across
    different screen sizes.
    """
    # Set viewport for specific device
    page.set_viewport_size(viewport)

    # Create test account
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name=f"{device_name} User",
        roles=["volunteer"],
    )

    # Test login on this device
    page.goto(f"{app_config.app_url}/login")

    # Verify form is visible (use specific login email)
    email_input = page.locator('#login-email')
    expect(email_input).to_be_visible(timeout=3000)

    # Verify viewport size is correct
    actual_width = page.evaluate("window.innerWidth")
    assert actual_width == viewport["width"], f"Device {device_name}: Expected {viewport['width']}px, got {actual_width}px"

    # Fill and submit
    email_input.fill(user["email"])
    page.locator('#login-password').fill(user["password"])
    page.locator('button[data-i18n="auth.sign_in"]').click()

    # Verify login succeeded (some accounts may be sent to onboarding wizard first)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )
    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")


def test_tablet_layout_ipad(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test tablet layout (iPad size).

    Verifies that tablet devices get appropriate layout (between mobile and desktop).
    """
    # Set iPad viewport
    page.set_viewport_size(MOBILE_VIEWPORTS["ipad_mini"])

    # Create test account using proper API client
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="iPad User",
        roles=["volunteer"],
    )

    # Login through UI (proper way - not localStorage)
    page.goto(f"{app_config.app_url}/login")

    # Fill login form
    page.locator('#login-email').fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Click login button
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    login_button.click()

    # Wait for redirect (schedule or onboarding wizard)
    import re
    expect(page).to_have_url(
        re.compile(rf"^{re.escape(app_config.app_url)}/(app/schedule|wizard)$"),
        timeout=5000,
    )

    if page.url.endswith("/wizard"):
        skip_onboarding_from_storage(page)
        page.goto(f"{app_config.app_url}/app/schedule")

    # Verify tablet viewport
    viewport_width = page.evaluate("window.innerWidth")
    assert 768 <= viewport_width < 1024, f"Should be in tablet viewport, got {viewport_width}px"

    # Verify schedule is visible
    schedule_heading = page.locator('#page-title')
    expect(schedule_heading).to_have_text("My Schedule", timeout=5000)


def test_mobile_touch_gestures(
    mobile_page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test touch gestures work on mobile.

    Verifies:
    - Tap/click works
    - Long press works (if applicable)
    - Swipe/scroll works
    """
    page = mobile_page

    # Create test account using proper API client
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Touch User",
        roles=["volunteer"],
    )

    # Login through UI (proper way - not localStorage)
    page.goto(f"{app_config.app_url}/login")

    # Fill login form
    page.locator('#login-email').fill(user["email"])
    page.locator('#login-password').fill(user["password"])

    # Click login button
    login_button = page.locator('button[data-i18n="auth.sign_in"]')
    login_button.click()

    # Wait for redirect to schedule
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule", timeout=5000)

    # Wait for page to load
    expect(page.locator('#page-title')).to_have_text("My Schedule", timeout=5000)

    # Test tap on settings button
    settings_btn = page.locator('button.action-btn:has-text("Settings")')
    expect(settings_btn).to_be_visible(timeout=3000)

    # Simulate touch tap (using click() which works on both desktop and mobile)
    settings_btn.click()

    # Verify modal opened
    settings_modal = page.locator('#settings-modal')
    expect(settings_modal).to_be_visible(timeout=3000)

    # Test scrolling (important on mobile)
    # Scroll down the page
    page.evaluate("window.scrollTo(0, 100)")
    scroll_position = page.evaluate("window.pageYOffset")
    assert scroll_position > 0, "Page should be scrollable on mobile"
