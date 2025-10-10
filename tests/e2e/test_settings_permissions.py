"""E2E test for settings permission display."""

import pytest
from playwright.sync_api import Page, expect


def test_settings_permission_display_no_object_object(page: Page):
    """Test that settings permission display doesn't show [object Object]."""
    # Navigate to app
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")

    # Click Sign in link
    page.get_by_role("link", name="Sign in").click()
    page.wait_for_timeout(500)

    # Login as admin
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "pastor@grace.church")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_timeout(2000)

    # Verify we're logged in
    expect(page.locator("#user-name-display")).to_be_visible(timeout=5000)

    # Open settings modal by clicking the gear icon
    page.locator('button.btn-icon:has-text("⚙️")').click()
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
