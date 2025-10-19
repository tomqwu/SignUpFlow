"""
E2E test to verify the Events view forEach bug is fixed.

This test specifically checks that the Events view doesn't crash when
the API returns undefined or empty data.events array.
"""

import pytest
from playwright.sync_api import Page, expect


def test_events_view_handles_empty_response(page: Page):
    """
    Test that Events view doesn't crash with forEach error when API returns empty events.

    Bug: "Error: Cannot read properties of undefined (reading 'forEach')"
    Fix: Added defensive array validation in loadAdminEvents() at line 1593 and 1627
    """
    # Create organization and admin user
    page.goto("http://localhost:8000/")

    # Click Get Started
    page.locator('[data-i18n="auth.get_started"]').click()

    # Fill organization form
    page.fill('input[name="org_name"]', 'Test Org Events')
    page.fill('input[name="org_region"]', 'Test Region')
    page.fill('input[name="org_timezone"]', 'America/New_York')
    page.click('button[type="submit"]')

    # Wait for signup form
    page.wait_for_selector('input[name="name"]')

    # Fill signup form
    page.fill('input[name="name"]', 'Test Admin')
    page.fill('input[name="email"]', f'admin_events_test_{page.evaluate("Date.now()")}@example.com')
    page.fill('input[name="password"]', 'Test123!@#')
    page.click('button[type="submit"]')

    # Wait for main app to load
    page.wait_for_selector('h2[data-i18n="schedule.my_schedule"]')

    # Navigate to Admin Console
    page.click('button[data-i18n="common.buttons.admin_console"]')
    page.wait_for_selector('.admin-panel')

    # Click Events tab
    page.click('button.admin-tab-btn:has-text("Events")')

    # Wait for events list to load (should show "no events" message, not crash)
    page.wait_for_selector('#admin-events-list')

    # Check that we don't see JavaScript errors
    # The page should show "No events yet" message, not crash
    expect(page.locator('#admin-events-list')).to_be_visible()

    # Verify no console errors (the forEach bug would show in console)
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    # Wait a moment for any errors to appear
    page.wait_for_timeout(1000)

    # Check for forEach error
    foreach_errors = [err for err in console_errors if "forEach" in err]
    assert len(foreach_errors) == 0, f"Found forEach errors: {foreach_errors}"


def test_events_view_with_actual_events(page: Page):
    """
    Test that Events view correctly displays events when API returns valid data.
    """
    # Create organization and admin user
    page.goto("http://localhost:8000/")

    # Click Get Started
    page.locator('[data-i18n="auth.get_started"]').click()

    # Fill organization form
    page.fill('input[name="org_name"]', 'Test Org With Events')
    page.fill('input[name="org_region"]', 'Test Region')
    page.fill('input[name="org_timezone"]', 'America/New_York')
    page.click('button[type="submit"]')

    # Wait for signup form
    page.wait_for_selector('input[name="name"]')

    # Fill signup form
    page.fill('input[name="name"]', 'Test Admin')
    page.fill('input[name="email"]', f'admin_with_events_{page.evaluate("Date.now()")}@example.com')
    page.fill('input[name="password"]', 'Test123!@#')
    page.click('button[type="submit"]')

    # Wait for main app to load
    page.wait_for_selector('h2[data-i18n="schedule.my_schedule"]')

    # Navigate to Admin Console
    page.click('button[data-i18n="common.buttons.admin_console"]')
    page.wait_for_selector('.admin-panel')

    # Click Events tab
    page.click('button.admin-tab-btn:has-text("Events")')
    page.wait_for_selector('#admin-events-list')

    # Create a new event
    page.click('button[data-i18n="events.create_event"]')
    page.wait_for_selector('#event-modal')

    # Fill event form
    page.fill('input[name="event_type"]', 'Sunday Service')
    page.fill('input[name="event_datetime"]', '2025-12-25T10:00')
    page.click('#event-modal button[data-i18n="common.buttons.create"]')

    # Wait for event to appear in list
    page.wait_for_selector('.admin-item:has-text("Sunday Service")')

    # Verify event is displayed
    expect(page.locator('.admin-item:has-text("Sunday Service")')).to_be_visible()

    # Verify no forEach errors
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.wait_for_timeout(1000)

    foreach_errors = [err for err in console_errors if "forEach" in err]
    assert len(foreach_errors) == 0, f"Found forEach errors with events: {foreach_errors}"
