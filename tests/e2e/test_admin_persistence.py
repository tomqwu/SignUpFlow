"""E2E test for admin panel persistence on page refresh.

Following TDD/BDD - test the bug before fixing it.
"""

import re
import pytest
from playwright.sync_api import Page, expect


def test_admin_panel_persists_on_refresh(page: Page):
    """Test that admin panel is visible after page refresh.

    BUG: When admin user refreshes the page while on /app/admin,
    the admin panel disappears because router.handleRoute() doesn't
    call the code that shows admin-only elements.
    """
    # Navigate to app
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")

    # Login as admin
    page.get_by_role("link", name="Sign in").click()
    page.wait_for_timeout(500)

    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "pastor@grace.church")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_timeout(2000)

    # Verify we're logged in
    expect(page.locator("#user-name-display")).to_be_visible(timeout=5000)

    # Click Admin button in navigation
    admin_nav_btn = page.locator('button.nav-btn[data-view="admin"]')
    expect(admin_nav_btn).to_be_visible(timeout=2000)

    print("✅ Admin button visible before refresh")

    admin_nav_btn.click()
    page.wait_for_timeout(500)

    # Verify we're on admin page
    admin_view = page.locator("#admin-view")
    expect(admin_view).to_be_visible()
    expect(admin_view).to_have_class(re.compile(r"active"))

    # Verify admin tabs are visible
    admin_tabs = page.locator(".admin-tabs")
    expect(admin_tabs).to_be_visible()

    events_tab = page.locator('button.admin-tab-btn[data-tab="events"]')
    expect(events_tab).to_be_visible()

    print("✅ Admin panel visible before refresh")
    print(f"Current URL: {page.url}")

    # REFRESH THE PAGE
    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    print(f"URL after refresh: {page.url}")

    # BUG: After refresh, admin navigation button disappears
    # The admin-only elements have class 'hidden' instead of 'visible'

    # Verify admin button is still visible after refresh
    admin_nav_btn_after = page.locator('button.nav-btn[data-view="admin"]')
    expect(admin_nav_btn_after).to_be_visible(timeout=5000)

    print("✅ Admin button visible after refresh")

    # Verify we're still on admin page
    admin_view_after = page.locator("#admin-view")
    expect(admin_view_after).to_be_visible(timeout=5000)

    # Verify admin tabs are still visible
    admin_tabs_after = page.locator(".admin-tabs")
    expect(admin_tabs_after).to_be_visible()

    events_tab_after = page.locator('button.admin-tab-btn[data-tab="events"]')
    expect(events_tab_after).to_be_visible()

    print("✅ Admin panel persists after page refresh")
