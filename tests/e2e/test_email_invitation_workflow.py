"""E2E test for invitation creation workflow (email disabled).

Current product decision: creating an invitation should succeed and persist the
invitation record even when outbound email sending is disabled.

This test verifies the admin UI flow creates a pending invitation.
"""

import os
import time

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

# Ensure email sending is disabled for this module
os.environ["EMAIL_ENABLED"] = "false"

pytestmark = pytest.mark.usefixtures("api_server")


def test_admin_creates_invitation_record(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    timestamp = int(time.time())

    # Setup: org + admin
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])

    # Navigate to Invitations
    page.goto(f"{app_config.app_url}/app/admin", wait_until="networkidle")

    invitations_tab = page.locator('button[data-tab="invitations"]')
    expect(invitations_tab).to_be_visible()
    invitations_tab.click()

    tab_content = page.locator("#admin-tab-invitations")

    open_modal_btn = tab_content.locator(
        'button:has-text("+ Send Invitation"), button:has-text("Send Invitation")'
    ).first
    expect(open_modal_btn).to_be_visible(timeout=5000)
    open_modal_btn.click()

    # Fill form
    volunteer_email = f"volunteer-{timestamp}@test.com"

    email_input = page.locator("#invite-email")
    expect(email_input).to_be_visible(timeout=5000)
    email_input.fill(volunteer_email)

    name_input = page.locator("#invite-name")
    if name_input.count() > 0:
        name_input.fill("Test Volunteer")

    # Select at least one role
    role_checkbox = page.locator('#invite-role-selector input[type="checkbox"]').first
    expect(role_checkbox).to_be_visible(timeout=5000)
    role_checkbox.check()

    # Submit
    send_btn = page.locator('button[type="submit"]:has-text("Send Invitation")')
    expect(send_btn).to_be_visible(timeout=5000)
    send_btn.click()

    # Verify invitation record appears as pending
    item = page.locator(f".invitation-item:has-text('{volunteer_email}')")
    expect(item).to_be_visible(timeout=5000)
    expect(item).to_contain_text("pending")
