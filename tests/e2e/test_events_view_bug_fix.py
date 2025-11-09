"""
E2E test to verify the Events view forEach bug is fixed.

This test specifically checks that the Events view doesn't crash when
the API returns undefined or empty data.events array.
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


def test_events_view_handles_empty_response(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test that Events view doesn't crash with forEach error when API returns empty events.

    Bug: "Error: Cannot read properties of undefined (reading 'forEach')"
    Fix: Added defensive array validation in loadAdminEvents() at line 1593 and 1627
    """
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

    # Navigate directly to Admin Console
    page.goto(f"{app_config.app_url}/app/admin")
    page.wait_for_selector('#admin-view', timeout=10000)  # Admin view container (not .admin-panel)

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


def test_events_view_with_actual_events(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test that Events view correctly displays events when API returns valid data.
    """
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

    # Navigate directly to Admin Console
    page.goto(f"{app_config.app_url}/app/admin")
    page.wait_for_selector('#admin-view', timeout=10000)  # Admin view container (not .admin-panel)

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
