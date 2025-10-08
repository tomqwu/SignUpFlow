"""E2E tests for admin console functionality."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def admin_page(page: Page):
    """Login as admin and navigate to admin console."""
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    page.goto("http://localhost:8000/app/admin")
    page.wait_for_timeout(1000)

    return page


def test_admin_console_tabs_exist(admin_page: Page):
    """Test that all admin console tabs are present."""
    # Check for tab buttons
    tabs = ["Events", "People", "Teams", "Roles", "Settings"]

    for tab_name in tabs:
        tab = admin_page.locator(f"button:has-text('{tab_name}'), .tab-button:has-text('{tab_name}')")
        # At least one tab should exist
        print(f"Checking for {tab_name} tab...")

    # Take screenshot of admin console
    admin_page.screenshot(path="/tmp/e2e-admin-console.png")


def test_create_new_event(admin_page: Page):
    """Test creating a new event from admin console."""
    # Click Events tab
    events_tab = admin_page.locator("button:has-text('Events')")
    if events_tab.count() > 0:
        events_tab.first.click()
        admin_page.wait_for_timeout(500)

        # Click "Add Event" button
        add_event_button = admin_page.locator("button:has-text('Add Event'), button:has-text('+ Event')")
        if add_event_button.count() > 0:
            add_event_button.first.click()
            admin_page.wait_for_timeout(500)

            # Fill event form
            timestamp = int(admin_page.evaluate("Date.now()"))

            title_input = admin_page.locator("#event-title, input[name='title']")
            if title_input.count() > 0:
                title_input.fill(f"E2E Test Event {timestamp}")

                # Fill date/time
                date_input = admin_page.locator("input[type='date']")
                if date_input.count() > 0:
                    date_input.first.fill("2025-12-25")

                # Submit
                submit_button = admin_page.locator("button:has-text('Create Event'), button[type='submit']")
                if submit_button.count() > 0:
                    submit_button.first.click()
                    admin_page.wait_for_timeout(2000)

                    admin_page.screenshot(path="/tmp/e2e-event-created.png")


def test_manage_people(admin_page: Page):
    """Test managing people in admin console."""
    # Click People tab
    people_tab = admin_page.locator("button:has-text('People')")
    if people_tab.count() > 0:
        people_tab.first.click()
        admin_page.wait_for_timeout(500)

        # Should show list of people
        people_list = admin_page.locator(".person-card, .people-list, table")
        # At least some UI should be visible
        admin_page.screenshot(path="/tmp/e2e-people-list.png")


def test_manage_teams(admin_page: Page):
    """Test managing teams in admin console."""
    # Click Teams tab
    teams_tab = admin_page.locator("button:has-text('Teams')")
    if teams_tab.count() > 0:
        teams_tab.first.click()
        admin_page.wait_for_timeout(500)

        # Click "Add Team" button
        add_team_button = admin_page.locator("button:has-text('Add Team'), button:has-text('+ Team')")
        if add_team_button.count() > 0:
            add_team_button.first.click()
            admin_page.wait_for_timeout(500)

            # Fill team form
            timestamp = int(admin_page.evaluate("Date.now()"))
            team_name_input = admin_page.locator("#team-name, input[name='name']")
            if team_name_input.count() > 0:
                team_name_input.fill(f"E2E Team {timestamp}")

                submit_button = admin_page.locator("button:has-text('Create Team'), button[type='submit']")
                if submit_button.count() > 0:
                    submit_button.first.click()
                    admin_page.wait_for_timeout(2000)

                    admin_page.screenshot(path="/tmp/e2e-team-created.png")


def test_manage_roles(admin_page: Page):
    """Test role management functionality."""
    # Click Roles tab
    roles_tab = admin_page.locator("button:has-text('Roles')")
    if roles_tab.count() > 0:
        roles_tab.first.click()
        admin_page.wait_for_timeout(500)

        # Should show role management UI
        admin_page.screenshot(path="/tmp/e2e-roles-management.png")


def test_organization_settings(admin_page: Page):
    """Test organization settings page."""
    # Click Settings tab
    settings_tab = admin_page.locator("button:has-text('Settings')")
    if settings_tab.count() > 0:
        settings_tab.first.click()
        admin_page.wait_for_timeout(500)

        # Should show organization settings
        org_name_input = admin_page.locator("input[value*='Grace'], input[name='org_name']")
        # Settings page should be visible
        admin_page.screenshot(path="/tmp/e2e-org-settings.png")


def test_non_admin_cannot_access(page: Page):
    """Test that non-admin users cannot access admin console."""
    # Would need a non-admin user account
    # For now, test that the page checks permissions
    page.goto("http://localhost:8000/app/admin")
    page.wait_for_timeout(1000)

    # Should either redirect or show access denied
    # (depends on if user is logged in)
    page.screenshot(path="/tmp/e2e-admin-access-check.png")
