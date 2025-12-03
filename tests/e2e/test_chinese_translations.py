"""E2E test for Chinese language translations in settings."""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


def test_chinese_permission_level_label(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Test that permission level label displays correctly in Chinese."""
    # Setup: Create test organization and admin user
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Open settings modal
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(500)

    # Change to Chinese (Simplified)
    language_select = page.locator("#settings-language")
    language_select.select_option("zh-CN")
    page.wait_for_timeout(500)

    # Click Save Changes to apply the language change
    save_button = page.locator('button[data-i18n="settings.save_changes"]')
    save_button.click()
    page.wait_for_timeout(1500)  # Wait for save and translation to apply

    # Re-open settings to verify the translation
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(500)

    # Find the permission level label
    permission_label = page.locator('label[data-i18n="settings.permission_level"]')

    # Get the text content
    label_text = permission_label.text_content()
    print(f"Permission label text in Chinese: '{label_text}'")

    # Verify it's Chinese and not [object Object] or untranslated
    assert label_text == "权限级别", f"Expected '权限级别' but got '{label_text}'"
    assert "[object Object]" not in label_text, "Found [object Object] in permission label"
    assert "Permission Level" not in label_text, "Label not translated to Chinese"

    # Verify the permission display area has no [object Object]
    permission_display = page.locator("#settings-permission-display")
    display_text = permission_display.text_content()
    print(f"Permission display text: '{display_text}'")

    assert "[object Object]" not in display_text, "Found [object Object] in permission display"

    print("✅ Chinese permission level label displays correctly")


def test_chinese_traditional_permission_level_label(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Test that permission level label displays correctly in Traditional Chinese."""
    # Setup: Create test organization and admin user
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Open settings modal
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(500)

    # Change to Chinese (Traditional)
    language_select = page.locator("#settings-language")
    language_select.select_option("zh-TW")
    page.wait_for_timeout(500)

    # Click Save Changes to apply the language change
    save_button = page.locator('button[data-i18n="settings.save_changes"]')
    save_button.click()
    page.wait_for_timeout(1500)  # Wait for save and translation to apply

    # Re-open settings to verify the translation
    page.locator('button.action-btn:has-text("Settings")').click()
    page.wait_for_timeout(500)

    # Find the permission level label
    permission_label = page.locator('label[data-i18n="settings.permission_level"]')

    # Get the text content
    label_text = permission_label.text_content()
    print(f"Permission label text in Traditional Chinese: '{label_text}'")

    # Verify it's Traditional Chinese and not [object Object] or untranslated
    assert label_text == "權限級別", f"Expected '權限級別' but got '{label_text}'"
    assert "[object Object]" not in label_text, "Found [object Object] in permission label"
    assert "Permission Level" not in label_text, "Label not translated to Traditional Chinese"

    # Verify the permission display area has no [object Object]
    permission_display = page.locator("#settings-permission-display")
    display_text = permission_display.text_content()
    print(f"Permission display text: '{display_text}'")

    assert "[object Object]" not in display_text, "Found [object Object] in permission display"

    print("✅ Traditional Chinese permission level label displays correctly")
