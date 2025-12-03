"""E2E test for settings permission display."""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui


pytestmark = pytest.mark.usefixtures("api_server")


def test_settings_permission_console_logs(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Test to capture console logs and see actual role data structure."""
    # Setup: Create test organization and admin user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin", "volunteer"],
    )

    # Capture console messages
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    # Login
    login_via_ui(page, app_config.app_url, user["email"], user["password"])

    # Verify we're logged in
    expect(page.locator("#user-name-display")).to_be_visible(timeout=5000)

    # Open settings modal by clicking the gear icon
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(1000)

    # Print all console messages related to showSettings
    print("\n" + "="*80)
    print("CONSOLE LOGS (DEBUG showSettings):")
    print("="*80)
    for msg in console_messages:
        if "showSettings" in msg or "role" in msg.lower() or "DEBUG" in msg:
            print(msg)
    print("="*80)

    # Also check what's in localStorage
    current_user = page.evaluate("JSON.parse(localStorage.getItem('currentUser'))")
    print("\nLocalStorage currentUser.roles:")
    print(current_user.get('roles') if current_user else None)


def test_settings_permission_display_no_object_object(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Test that settings permission display doesn't show [object Object]."""
    # Setup: Create test organization and admin user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin", "volunteer"],
    )

    # Login
    login_via_ui(page, app_config.app_url, user["email"], user["password"])

    # Verify we're logged in
    expect(page.locator("#user-name-display")).to_be_visible(timeout=5000)

    # Open settings modal by clicking the gear icon
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(500)

    # Check the settings modal is visible
    settings_modal = page.locator("#settings-modal")
    expect(settings_modal).to_be_visible()

    # Get the permission display text
    permission_display = page.locator("#settings-permission-display")
    expect(permission_display).to_be_visible()

    permission_text = permission_display.text_content()
    print(f"Permission display text: {permission_text}")

    # Verify no [object Object] appears
    assert "[object Object]" not in permission_text, f"Found [object Object] in permission display: {permission_text}"

    # Verify admin role is displayed correctly
    assert "Administrator" in permission_text or "admin" in permission_text.lower(), f"Admin role not found in: {permission_text}"

    # Check inner HTML to verify badge structure
    permission_html = permission_display.inner_html()
    print(f"Permission display HTML: {permission_html}")

    # Verify no [object Object] in HTML
    assert "[object Object]" not in permission_html, f"Found [object Object] in permission HTML: {permission_html}"

    # Count role badges - should be at least 1
    role_badges = permission_display.locator("span")
    badge_count = role_badges.count()
    print(f"Role badge count: {badge_count}")
    assert badge_count >= 1, "Expected at least 1 role badge"

    # Get all badge texts
    badge_texts = []
    for i in range(badge_count):
        badge_text = role_badges.nth(i).text_content()
        badge_texts.append(badge_text)
        print(f"Badge {i}: {badge_text}")

        # Verify each badge doesn't contain [object Object]
        assert "[object Object]" not in badge_text, f"Badge {i} contains [object Object]: {badge_text}"

    # Verify at least one badge shows Administrator
    admin_found = any("Administrator" in text or "admin" in text.lower() for text in badge_texts)
    assert admin_found, f"No Administrator badge found in: {badge_texts}"

    print(f"✅ Settings permission display is correct: {badge_texts}")
