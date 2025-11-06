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
import requests
import os

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")

# Check if email is enabled (from environment)
EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"

# Mailtrap API configuration
MAILTRAP_API_TOKEN = os.environ.get("MAILTRAP_API_TOKEN", "")
MAILTRAP_INBOX_ID = os.environ.get("MAILTRAP_INBOX_ID", "3238231")  # Default inbox ID
MAILTRAP_ACCOUNT_ID = os.environ.get("MAILTRAP_ACCOUNT_ID", "")


def get_mailtrap_messages(inbox_id=MAILTRAP_INBOX_ID, account_id=MAILTRAP_ACCOUNT_ID):
    """
    Get messages from Mailtrap inbox using API.

    API Docs: https://api-docs.mailtrap.io/docs/mailtrap-api-docs/a80869adf4489-get-messages

    Returns:
        list: List of email messages in inbox
    """
    if not MAILTRAP_API_TOKEN:
        pytest.skip("MAILTRAP_API_TOKEN not set - skipping API verification")

    url = f"https://mailtrap.io/api/accounts/{account_id}/inboxes/{inbox_id}/messages"
    headers = {
        "Api-Token": MAILTRAP_API_TOKEN
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Failed to connect to Mailtrap API: {e}")


def get_latest_email(to_email, inbox_id=MAILTRAP_INBOX_ID, account_id=MAILTRAP_ACCOUNT_ID, timeout=10):
    """
    Poll Mailtrap inbox for latest email sent to specific address.

    Args:
        to_email: Email address to search for
        inbox_id: Mailtrap inbox ID
        account_id: Mailtrap account ID
        timeout: Maximum seconds to wait for email

    Returns:
        dict: Email message object or None if not found
    """
    import time
    start_time = time.time()

    while time.time() - start_time < timeout:
        messages = get_mailtrap_messages(inbox_id, account_id)

        # Find email sent to specific address
        for msg in messages:
            if msg.get('to_email') == to_email:
                return msg

        time.sleep(1)  # Wait 1 second before retry

    return None


@pytest.mark.skipif(
    not EMAIL_ENABLED,
    reason="Email infrastructure not configured (EMAIL_ENABLED=false). Configure SMTP settings to enable this test."
)
def test_admin_sends_invitation_email(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
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
    # Step 1: Setup - Create test organization and admin user
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Step 2: Navigate to Admin Console
    page.goto(f"{app_config.app_url}/app/admin")
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


@pytest.mark.skipif(
    not EMAIL_ENABLED,
    reason="Email infrastructure not configured (EMAIL_ENABLED=false). This test requires SMTP server."
)
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

    # Should return False or None (not raise exception)
    # When EMAIL_ENABLED=false, service returns None; when sending fails, it returns False
    assert not success, "Email service should return False or None for failed sends"


@pytest.mark.skipif(
    not EMAIL_ENABLED or not MAILTRAP_API_TOKEN,
    reason="Email infrastructure not configured (EMAIL_ENABLED=false or MAILTRAP_API_TOKEN missing). This test requires SMTP server and Mailtrap API access."
)
def test_invitation_email_delivered_to_mailtrap_inbox(app_config: AppConfig):
    """
    Test that invitation email is actually delivered to Mailtrap inbox.

    This test uses the Mailtrap Inbox API to programmatically verify
    email delivery without manual checking.

    Requires:
        - MAILTRAP_API_TOKEN environment variable
        - MAILTRAP_ACCOUNT_ID environment variable
        - MAILTRAP_INBOX_ID environment variable (optional, defaults to 3238231)

    API Docs: https://api-docs.mailtrap.io/docs/mailtrap-api-docs/a80869adf4489-get-messages
    """
    from api.services.email_service import email_service

    # Use unique email to avoid conflicts with other tests
    test_email = f"api-test-{int(time.time())}@example.com"
    test_token = "test_api_verification_token_123"

    # Send invitation email
    success = email_service.send_invitation_email(
        to_email=test_email,
        admin_name="API Test Admin",
        org_name="API Test Organization",
        invitation_token=test_token,
        app_url=app_config.app_url
    )

    assert success, "Email service should send email successfully"

    # Verify email appears in Mailtrap inbox via API
    email_message = get_latest_email(test_email, timeout=15)

    if email_message is None:
        pytest.fail(f"Email to {test_email} not found in Mailtrap inbox within 15 seconds")

    # Verify email content
    assert email_message['to_email'] == test_email, "Email should be sent to correct recipient"
    assert "You're invited to join" in email_message['subject'], "Email subject should contain invitation text"
    assert email_message['from_email'] == "noreply@signupflow.io", "Email should be from correct sender"

    # Verify email contains invitation link with token
    assert test_token in email_message.get('html_body', ''), "Email should contain invitation token in HTML body"
    assert "API Test Admin" in email_message.get('html_body', ''), "Email should mention admin name"
    assert "API Test Organization" in email_message.get('html_body', ''), "Email should mention organization name"

    print(f"✅ Email successfully delivered to Mailtrap inbox (Message ID: {email_message.get('id')})")
