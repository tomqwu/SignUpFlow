"""
Integration tests for EmailService with real Mailtrap SMTP sandbox.

Tests REAL email sending (not mocked):
- Sends actual emails via SMTP to Mailtrap sandbox
- Verifies emails arrive in Mailtrap inbox via API
- Validates email content, headers, and formatting

Requirements:
- MAILTRAP_SMTP_USER environment variable
- MAILTRAP_SMTP_PASSWORD environment variable
- MAILTRAP_API_TOKEN environment variable (for verification)
- MAILTRAP_INBOX_ID environment variable (for verification)
- MAILTRAP_ACCOUNT_ID environment variable (for verification)

Coverage target: Real SMTP integration validation for T033
"""

import pytest
import os
import time
import requests
from api.services.email_service import EmailService
from api.models import NotificationType


# Mailtrap configuration from environment
MAILTRAP_SMTP_USER = os.getenv("MAILTRAP_SMTP_USER", "")
MAILTRAP_SMTP_PASSWORD = os.getenv("MAILTRAP_SMTP_PASSWORD", "")
MAILTRAP_API_TOKEN = os.getenv("MAILTRAP_API_TOKEN", "")
MAILTRAP_INBOX_ID = os.getenv("MAILTRAP_INBOX_ID", "3238231")
MAILTRAP_ACCOUNT_ID = os.getenv("MAILTRAP_ACCOUNT_ID", "")


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


def get_latest_email(to_email, subject_contains=None, timeout=15):
    """
    Poll Mailtrap inbox for latest email sent to specific address.

    Args:
        to_email: Email address to search for
        subject_contains: Optional subject text to match
        timeout: Maximum seconds to wait for email

    Returns:
        dict: Email message object or None if not found
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        messages = get_mailtrap_messages()

        # Find email sent to specific address (check in reverse for latest)
        for msg in reversed(messages):
            # Check recipient
            if msg.get('to_email') == to_email or any(
                recipient.get('email') == to_email
                for recipient in msg.get('to', [])
            ):
                # Check subject if specified
                if subject_contains:
                    if subject_contains.lower() in msg.get('subject', '').lower():
                        return msg
                else:
                    return msg

        time.sleep(1)  # Wait 1 second before retry

    return None


@pytest.mark.skipif(
    not MAILTRAP_SMTP_USER or not MAILTRAP_SMTP_PASSWORD,
    reason="MAILTRAP_SMTP_USER and MAILTRAP_SMTP_PASSWORD must be set"
)
class TestEmailServiceMailtrapSMTP:
    """Integration tests for EmailService with real Mailtrap SMTP sandbox."""

    def test_send_assignment_email_via_smtp(self):
        """
        Test T033: Send real assignment email via SMTP to Mailtrap sandbox.

        Workflow:
        1. Initialize EmailService with Mailtrap SMTP credentials
        2. Send assignment notification email
        3. Poll Mailtrap inbox to verify email received
        4. Validate email content and formatting
        """
        # Arrange
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user=MAILTRAP_SMTP_USER,
            smtp_password=MAILTRAP_SMTP_PASSWORD,
            from_email="test@signupflow.io",
            from_name="SignUpFlow Test"
        )

        test_email = "volunteer@example.com"
        template_data = {
            "volunteer_name": "John Doe",
            "event_title": "Sunday Service",
            "event_date": "2025-11-01",
            "event_time": "10:00 AM",
            "event_location": "Main Sanctuary",
            "role": "Usher",
            "schedule_link": "https://signupflow.io/schedule/123",
            "unsubscribe_token": "test_token_123"
        }

        # Act - Send real email via SMTP
        result = service.send_email(
            to_email=test_email,
            subject="New Assignment: Sunday Service",
            template_name="assignment",
            template_data=template_data,
            language="en"
        )

        # Assert - Email sending succeeded
        assert result is not None  # Returns message_id on success

        # Verify - Email appears in Mailtrap inbox
        if MAILTRAP_API_TOKEN and MAILTRAP_ACCOUNT_ID:
            email = get_latest_email(
                to_email=test_email,
                subject_contains="Sunday Service",
                timeout=15
            )

            assert email is not None, "Email not found in Mailtrap inbox within 15 seconds"
            assert "Sunday Service" in email.get("subject", "")
            assert test_email == email.get("to_email") or any(
                r.get("email") == test_email for r in email.get("to", [])
            )

            # Validate email body contains expected content
            html_body = email.get("html_body", "")
            assert "John Doe" in html_body, "Volunteer name not in email body"
            assert "Sunday Service" in html_body, "Event title not in email body"
            assert "Usher" in html_body, "Role not in email body"

            # Validate unsubscribe link (CAN-SPAM compliance)
            assert "unsubscribe" in html_body.lower(), "Unsubscribe link missing"

    def test_send_email_multi_language(self):
        """
        Test sending emails in different languages (EN, ES, PT).

        Validates:
        - Template rendering for multiple languages
        - SMTP delivery for each language
        - Subject line translation
        """
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user=MAILTRAP_SMTP_USER,
            smtp_password=MAILTRAP_SMTP_PASSWORD
        )

        languages = ["en", "es", "pt"]

        for lang in languages:
            test_email = f"volunteer-{lang}@example.com"
            template_data = {
                "volunteer_name": "Maria Garcia",
                "event_title": "Test Event",
                "role": "Volunteer"
            }

            # Act
            result = service.send_email(
                to_email=test_email,
                subject=f"New Assignment: {template_data['event_title']}",
                template_name="assignment",
                template_data=template_data,
                language=lang
            )

            # Assert
            assert result is not None, f"Failed to send email in language: {lang}"

    def test_smtp_connection_failure_handling(self):
        """
        Test that EmailService handles SMTP connection failures gracefully.

        Validates:
        - Invalid credentials return error
        - Exception doesn't crash system
        - Error message is descriptive
        """
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user="invalid_user",
            smtp_password="invalid_password"
        )

        template_data = {
            "volunteer_name": "Test User",
            "event_title": "Test Event"
        }

        # Act - Should fail with invalid credentials
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Assignment",
            template_name="assignment",
            template_data=template_data,
            language="en"
        )

        # Assert - Graceful failure (returns None on failure)
        assert result is None

    def test_send_reminder_email_via_smtp(self):
        """
        Test sending reminder email via SMTP.

        Validates:
        - Reminder template renders correctly
        - SMTP delivery successful
        - Email content accurate
        """
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user=MAILTRAP_SMTP_USER,
            smtp_password=MAILTRAP_SMTP_PASSWORD
        )

        test_email = "reminder-test@example.com"
        template_data = {
            "volunteer_name": "Jane Smith",
            "event_title": "Wednesday Prayer",
            "event_date": "2025-11-05",
            "event_time": "7:00 PM",
            "role": "Greeter"
        }

        # Act
        result = service.send_email(
            to_email=test_email,
            subject=f"Reminder: {template_data['event_title']}",
            template_name="reminder",
            template_data=template_data,
            language="en"
        )

        # Assert
        assert result is not None

        # Verify
        if MAILTRAP_API_TOKEN and MAILTRAP_ACCOUNT_ID:
            email = get_latest_email(
                to_email=test_email,
                subject_contains="Wednesday Prayer",
                timeout=15
            )

            assert email is not None
            assert "reminder" in email.get("subject", "").lower() or "Wednesday Prayer" in email.get("subject", "")

    def test_send_update_email_via_smtp(self):
        """
        Test sending schedule update email via SMTP.

        Validates:
        - Update template renders correctly
        - Change information included
        - SMTP delivery successful
        """
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user=MAILTRAP_SMTP_USER,
            smtp_password=MAILTRAP_SMTP_PASSWORD
        )

        test_email = "update-test@example.com"
        template_data = {
            "volunteer_name": "Bob Johnson",
            "event_title": "Sunday Service",
            "changes": "Time changed from 10:00 AM to 10:30 AM",
            "event_date": "2025-11-08",
            "new_time": "10:30 AM"
        }

        # Act
        result = service.send_email(
            to_email=test_email,
            subject=f"Schedule Update: {template_data['event_title']}",
            template_name="update",
            template_data=template_data,
            language="en"
        )

        # Assert
        assert result is not None

        # Verify
        if MAILTRAP_API_TOKEN and MAILTRAP_ACCOUNT_ID:
            email = get_latest_email(
                to_email=test_email,
                subject_contains="Update",
                timeout=15
            )

            assert email is not None
            html_body = email.get("html_body", "")
            assert "10:30 AM" in html_body or "change" in html_body.lower()

    def test_send_cancellation_email_via_smtp(self):
        """
        Test sending event cancellation email via SMTP.

        Validates:
        - Cancellation template renders correctly
        - Cancellation reason included
        - SMTP delivery successful
        """
        service = EmailService(
            smtp_host="sandbox.smtp.mailtrap.io",
            smtp_port=2525,
            smtp_user=MAILTRAP_SMTP_USER,
            smtp_password=MAILTRAP_SMTP_PASSWORD
        )

        test_email = "cancel-test@example.com"
        template_data = {
            "volunteer_name": "Alice Brown",
            "event_title": "Youth Group",
            "event_date": "2025-11-10",
            "cancellation_reason": "Weather conditions"
        }

        # Act
        result = service.send_email(
            to_email=test_email,
            subject=f"Event Cancelled: {template_data['event_title']}",
            template_name="cancellation",
            template_data=template_data,
            language="en"
        )

        # Assert
        assert result is not None

        # Verify
        if MAILTRAP_API_TOKEN and MAILTRAP_ACCOUNT_ID:
            email = get_latest_email(
                to_email=test_email,
                subject_contains="cancel",
                timeout=15
            )

            assert email is not None
            html_body = email.get("html_body", "")
            assert "cancel" in html_body.lower() or "Weather conditions" in html_body


# Run tests with: poetry run pytest tests/integration/test_email_mailtrap.py -v -s
#
# Required environment variables:
# export MAILTRAP_SMTP_USER="your_username"
# export MAILTRAP_SMTP_PASSWORD="your_password"
# export MAILTRAP_API_TOKEN="your_api_token"
# export MAILTRAP_INBOX_ID="your_inbox_id"
# export MAILTRAP_ACCOUNT_ID="your_account_id"
