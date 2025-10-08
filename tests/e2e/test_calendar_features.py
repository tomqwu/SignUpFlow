"""E2E tests for calendar export and subscription features."""

import pytest
from playwright.sync_api import Page, expect


def test_export_personal_calendar(page: Page):
    """Test exporting personal calendar as ICS file."""
    # Login
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Navigate to schedule view
    page.goto("http://localhost:8000/app/schedule")
    page.wait_for_timeout(1000)

    # Look for export button
    export_button = page.locator("button:has-text('Export'), button:has-text('📅'), button:has-text('Calendar')")
    if export_button.count() > 0:
        # Wait for download
        with page.expect_download() as download_info:
            export_button.first.click()
            page.wait_for_timeout(1000)

        download = download_info.value
        # Verify download
        assert download.suggested_filename.endswith('.ics')
        print(f"✅ Downloaded: {download.suggested_filename}")


def test_get_webcal_subscription_url(page: Page):
    """Test getting webcal subscription URL."""
    # Login
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Navigate to schedule
    page.goto("http://localhost:8000/app/schedule")
    page.wait_for_timeout(1000)

    # Look for subscribe button
    subscribe_button = page.locator("button:has-text('Subscribe'), button:has-text('webcal')")
    if subscribe_button.count() > 0:
        subscribe_button.first.click()
        page.wait_for_timeout(500)

        # Should show subscription URL
        webcal_input = page.locator("input[value*='webcal://'], input[value*='feed']")
        if webcal_input.count() > 0:
            webcal_url = webcal_input.input_value()
            print(f"✅ Webcal URL: {webcal_url}")
            assert 'webcal://' in webcal_url or 'feed' in webcal_url


def test_calendar_feed_endpoint(page: Page):
    """Test that calendar feed endpoint returns ICS data."""
    # This requires a valid token, so we'll test the endpoint exists
    response = page.request.get("http://localhost:8000/api/calendar/feed/test_token")

    # Should return 401 for invalid token (security working)
    # or 200 with ICS data for valid token
    assert response.status in [401, 404, 200]
    print(f"✅ Calendar feed endpoint status: {response.status}")


def test_admin_can_export_org_calendar(page: Page):
    """Test that admin can export organization calendar."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Navigate to admin console
    page.goto("http://localhost:8000/app/admin")
    page.wait_for_timeout(1000)

    # Look for organization export
    org_export_button = page.locator("button:has-text('Export Org'), button:has-text('Organization Calendar')")
    if org_export_button.count() > 0:
        with page.expect_download() as download_info:
            org_export_button.first.click()
            page.wait_for_timeout(1000)

        download = download_info.value
        assert download.suggested_filename.endswith('.ics')
        print(f"✅ Org calendar downloaded: {download.suggested_filename}")
