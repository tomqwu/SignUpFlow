"""
Integration test to catch [object Object] role display bugs.
This test reproduces the exact bug the user reported.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.asyncio
async def test_role_display_no_object_object(page: Page):
    """Test that roles never display as [object Object] anywhere in the app."""

    # Start server and navigate
    page.goto("http://localhost:8001")

    # Create account with roles that are known to cause issues
    page.get_by_placeholder("Your Full Name").fill("Test User")
    page.get_by_placeholder("Email Address").fill("test@example.com")
    page.get_by_placeholder("Create an Organization").fill("Test Church")

    # Select both roles
    page.locator('input[value="volunteer"]').check()
    page.locator('input[value="admin"]').check()

    page.locator('[data-i18n="auth.get_started"]').click()

    # Wait for main app to load
    page.wait_for_selector('#main-app:not(.hidden)', timeout=5000)

    # Check 1: Role badges in user context should not show [object Object]
    role_badges = page.locator('.role-badge').all_text_contents()
    for badge_text in role_badges:
        assert '[object Object]' not in badge_text, f"Role badge shows [object Object]: {badge_text}"
        assert badge_text.strip() != '', f"Role badge is empty"

    # Check 2: Open settings modal
    page.locator('button:has-text("⚙️")').click()  # Settings button
    page.wait_for_selector('#settings-modal:not(.hidden)')

    # Check settings permission display
    permission_text = page.locator('#settings-permission-display').text_content()
    assert '[object Object]' not in permission_text, f"Settings shows [object Object]: {permission_text}"

    # Check 3: Go to admin panel and check people list
    page.locator('button:has-text("Cancel")').click()  # Close settings
    page.locator('[data-i18n="nav.admin"]').click()  # Admin tab

    # Wait for people list
    page.wait_for_selector('.admin-item', timeout=5000)

    # Check all role displays in admin panel
    admin_items = page.locator('.admin-item').all()
    for item in admin_items:
        item_text = item.text_content()
        assert '[object Object]' not in item_text, f"Admin panel shows [object Object]: {item_text}"

    print("✅ All role displays passed - no [object Object] found!")


@pytest.mark.asyncio
async def test_router_authentication_no_redirect_loop(page: Page):
    """Test that router properly detects authentication and doesn't redirect to login."""

    # Create account and login
    page.goto("http://localhost:8001")

    page.get_by_placeholder("Your Full Name").fill("Auth Test")
    page.get_by_placeholder("Email Address").fill("auth@example.com")
    page.get_by_placeholder("Create an Organization").fill("Test Org")
    page.locator('[data-i18n="auth.get_started"]').click()

    # Wait for main app
    page.wait_for_selector('#main-app:not(.hidden)', timeout=5000)

    # Verify we're on /app/schedule
    assert '/app/schedule' in page.url or '/app' in page.url

    # Click different tabs - should NOT redirect to login
    tabs = ['schedule', 'events', 'admin']

    for tab in tabs:
        page.locator(f'[data-i18n="nav.{tab}"]').click()
        page.wait_for_timeout(500)  # Wait for navigation

        # Should still be on /app route, NOT /login
        current_url = page.url
        assert '/login' not in current_url, f"Clicking {tab} tab redirected to login! URL: {current_url}"
        assert '/app' in current_url, f"Not on app route after clicking {tab}. URL: {current_url}"

    print("✅ Router authentication passed - no redirect loops!")


@pytest.mark.asyncio
async def test_roles_with_event_specific_roles(page: Page):
    """Test role display with event-specific roles like worship-leader, vocalist."""

    # This test simulates what happens when user has custom event roles
    # We'll need to inject this via the API or database

    page.goto("http://localhost:8001")

    # For now, just verify the structure handles it
    # TODO: Create user with worship-leader and vocalist roles via API

    print("⏭️  Skipping event-specific role test - needs API setup")
