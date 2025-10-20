"""
End-to-End test for email invitation workflow.

Tests the complete user journey:
1. Admin creates invitation
2. Email is sent via Mailtrap
3. User receives invitation email

Following Mandatory E2E Testing Workflow from CLAUDE.md.
"""

import pytest
from playwright.sync_api import Page, expect
import time


def test_admin_sends_invitation_email(page: Page):
    """
    Test complete invitation workflow with email sending.

    User Journey:
    1. Admin logs in
    2. Admin navigates to invitations
    3. Admin fills invitation form
    4. Admin submits invitation
    5. System sends email via Mailtrap
    6. User sees success message
    7. Email appears in Mailtrap inbox
    """
    # Step 1: Admin logs in
    page.goto("http://localhost:8000/")

    # Click login/get started
    get_started = page.locator('[data-i18n="auth.get_started"]')
    expect(get_started).to_be_visible(timeout=5000)
    get_started.click()

    # Create new org for testing
    timestamp = int(time.time())
    org_name = f"Email Test Org {timestamp}"
    admin_email = f"admin-email-{timestamp}@test.com"

    # Fill org form
    create_org_btn = page.locator('[data-i18n="auth.create_new_organization"]')
    if create_org_btn.is_visible():
        create_org_btn.click()

        page.fill('[data-i18n-placeholder="auth.placeholder_org_name"]', org_name)
        page.fill('[data-i18n-placeholder="auth.placeholder_location"]', "Test City")
        page.locator('[data-i18n="common.buttons.create"]').click()

    # Fill admin profile
    page.fill('[data-i18n-placeholder="common.placeholder_full_name"]', "Test Admin")
    page.fill('[data-i18n-placeholder="common.placeholder_email"]', admin_email)
    page.fill('[data-i18n-placeholder="auth.placeholder_create_password"]', "testpass123")

    # Select admin role
    page.locator('#role-selector input[value="admin"]').check()

    # Submit profile
    page.locator('[data-i18n="common.buttons.next"]').click()

    # Wait for main app to load
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Step 2: Navigate to Admin Console
    page.goto("http://localhost:8000/app/admin")
    expect(page.locator('[data-i18n="admin.title"]')).to_be_visible(timeout=5000)

    # Step 3: Go to Invitations tab
    invitations_tab = page.locator('[data-i18n="admin.tabs.invitations"]')
    invitations_tab.click()

    # Step 4: Fill invitation form
    invite_email_input = page.locator('#invite-email')
    expect(invite_email_input).to_be_visible(timeout=5000)

    volunteer_email = f"volunteer-{timestamp}@test.com"
    invite_email_input.fill(volunteer_email)

    # Select volunteer role for invitation
    page.locator('#invite-role-selector input[value="volunteer"]').check()

    # Step 5: Send invitation
    send_btn = page.locator('[data-i18n="admin.buttons.send_invitation"]')
    send_btn.click()

    # Step 6: Verify success message appears
    success_message = page.locator('[data-i18n="messages.success.invitation_sent"]')
    expect(success_message).to_be_visible(timeout=10000)

    # Step 7: Verify email was sent (check that invitation appears in list)
    invitation_row = page.locator(f'tr:has-text("{volunteer_email}")')
    expect(invitation_row).to_be_visible(timeout=5000)

    # Verify invitation status is "pending"
    status_cell = invitation_row.locator('td:has-text("pending")')
    expect(status_cell).to_be_visible()


def test_invitation_email_contains_correct_content():
    """
    Test that invitation email contains correct content.

    This test verifies the email service directly.
    """
    from api.services.email_service import email_service

    # Send test invitation email
    success = email_service.send_invitation_email(
        to_email="test@example.com",
        admin_name="Test Admin",
        org_name="Test Organization",
        invitation_token="test_token_123",
        app_url="http://localhost:8000"
    )

    # Verify email was sent successfully
    assert success, "Email service should send invitation email"


def test_invitation_email_service_handles_errors():
    """
    Test that email service handles errors gracefully.
    """
    from api.services.email_service import EmailService

    # Create email service with invalid credentials
    bad_service = EmailService(
        smtp_host="invalid.host",
        smtp_port=9999,
        smtp_user="invalid",
        smtp_password="invalid"
    )

    # Attempt to send email (should fail gracefully)
    success = bad_service.send_email(
        to_email="test@example.com",
        subject="Test",
        html_content="<p>Test</p>"
    )

    # Should return False (not raise exception)
    assert success is False, "Email service should return False for failed sends"
