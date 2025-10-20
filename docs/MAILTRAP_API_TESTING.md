# Mailtrap API Testing Guide

## Overview

This guide explains how to use the Mailtrap Inbox API to programmatically verify email delivery in automated tests, eliminating the need for manual inbox checking.

## Prerequisites

### 1. Mailtrap Account Setup

1. Sign up at [Mailtrap.io](https://mailtrap.io/)
2. Create an inbox (or use the default sandbox inbox)
3. Get your API credentials:
   - **API Token**: Found in Settings → API Tokens
   - **Account ID**: Found in URL when viewing inbox (`/accounts/{ACCOUNT_ID}/inboxes/...`)
   - **Inbox ID**: Found in URL when viewing inbox (`/inboxes/{INBOX_ID}`)

### 2. Environment Variables

Set these environment variables for automated testing:

```bash
export MAILTRAP_API_TOKEN="your_api_token_here"
export MAILTRAP_ACCOUNT_ID="your_account_id"
export MAILTRAP_INBOX_ID="3238231"  # Optional, defaults to 3238231
```

Or add to your `.env` file:

```bash
MAILTRAP_API_TOKEN=your_api_token_here
MAILTRAP_ACCOUNT_ID=your_account_id
MAILTRAP_INBOX_ID=3238231
```

## API Documentation

- **Get Messages**: https://api-docs.mailtrap.io/docs/mailtrap-api-docs/a80869adf4489-get-messages
- **Get Inbox Attributes**: https://api-docs.mailtrap.io/docs/mailtrap-api-docs/432a39abe34b3-get-inbox-attributes

## Test Implementation

### Automated Email Verification Test

The test `test_invitation_email_delivered_to_mailtrap_inbox()` in `tests/e2e/test_email_invitation_workflow.py` demonstrates automated email verification:

```python
def test_invitation_email_delivered_to_mailtrap_inbox():
    """
    Test that invitation email is actually delivered to Mailtrap inbox.

    This test:
    1. Sends an invitation email via EmailService
    2. Polls Mailtrap Inbox API for the email (15 second timeout)
    3. Verifies email content (recipient, subject, body, token)
    """
    from api.services.email_service import email_service

    # Send email
    test_email = f"api-test-{int(time.time())}@example.com"
    success = email_service.send_invitation_email(
        to_email=test_email,
        admin_name="API Test Admin",
        org_name="API Test Organization",
        invitation_token="test_token_123",
        app_url="http://localhost:8000"
    )

    assert success, "Email should send successfully"

    # Verify delivery via Mailtrap API
    email_message = get_latest_email(test_email, timeout=15)

    assert email_message is not None, "Email should appear in inbox"
    assert email_message['to_email'] == test_email
    assert "You're invited to join" in email_message['subject']
    assert "test_token_123" in email_message['html_body']
```

### Helper Functions

#### `get_mailtrap_messages(inbox_id, account_id)`

Fetches all messages from Mailtrap inbox.

**Returns**: `list` of email message objects

**Example**:
```python
messages = get_mailtrap_messages(
    inbox_id="3238231",
    account_id="1234567"
)

for msg in messages:
    print(f"From: {msg['from_email']}")
    print(f"To: {msg['to_email']}")
    print(f"Subject: {msg['subject']}")
```

#### `get_latest_email(to_email, timeout=10)`

Polls Mailtrap inbox for email sent to specific address.

**Arguments**:
- `to_email`: Email address to search for
- `timeout`: Maximum seconds to wait (default: 10)

**Returns**: Email message object or `None` if not found

**Example**:
```python
email = get_latest_email("user@example.com", timeout=15)

if email:
    print(f"Email found: {email['subject']}")
    print(f"HTML body: {email['html_body']}")
    print(f"Message ID: {email['id']}")
```

## Running the Tests

### Run Email API Test Only

```bash
# With API credentials
export MAILTRAP_API_TOKEN="your_token"
export MAILTRAP_ACCOUNT_ID="your_account"
poetry run pytest tests/e2e/test_email_invitation_workflow.py::test_invitation_email_delivered_to_mailtrap_inbox -v

# Without API credentials (test will be skipped)
poetry run pytest tests/e2e/test_email_invitation_workflow.py::test_invitation_email_delivered_to_mailtrap_inbox -v
```

### Run All Email Tests

```bash
poetry run pytest tests/e2e/test_email_invitation_workflow.py -v
```

**Expected Output**:

```
tests/e2e/test_email_invitation_workflow.py::test_invitation_email_contains_correct_content PASSED
tests/e2e/test_email_invitation_workflow.py::test_invitation_email_service_handles_errors PASSED
tests/e2e/test_email_invitation_workflow.py::test_invitation_email_delivered_to_mailtrap_inbox PASSED
✅ Email successfully delivered to Mailtrap inbox (Message ID: 123456789)
```

## Email Message Object Structure

The Mailtrap API returns email messages with this structure:

```json
{
  "id": 123456789,
  "inbox_id": 3238231,
  "subject": "You're invited to join Test Organization on SignUpFlow",
  "from_email": "noreply@signupflow.io",
  "from_name": "SignUpFlow",
  "to_email": "user@example.com",
  "to_name": null,
  "html_body": "<html>...</html>",
  "text_body": "Plain text version...",
  "created_at": "2025-10-20T15:30:00.000Z",
  "updated_at": "2025-10-20T15:30:00.000Z",
  "is_read": false,
  "sent_at": "2025-10-20T15:30:00.000Z"
}
```

## Troubleshooting

### Test Skipped: "MAILTRAP_API_TOKEN not set"

**Problem**: Environment variables not configured

**Solution**: Set the required environment variables:

```bash
export MAILTRAP_API_TOKEN="your_token"
export MAILTRAP_ACCOUNT_ID="your_account"
```

### Test Failed: "Email not found in Mailtrap inbox"

**Problem**: Email delivery delayed or credentials incorrect

**Solutions**:
1. Check Mailtrap inbox manually to verify email was delivered
2. Increase timeout in `get_latest_email(timeout=30)`
3. Verify SMTP credentials in `api/services/email_service.py`
4. Check Mailtrap inbox ID and account ID are correct

### API Request Failed: 401 Unauthorized

**Problem**: Invalid API token

**Solution**:
1. Go to Mailtrap Settings → API Tokens
2. Generate new token if needed
3. Update `MAILTRAP_API_TOKEN` environment variable

### API Request Failed: 404 Not Found

**Problem**: Incorrect inbox ID or account ID

**Solution**:
1. Check Mailtrap inbox URL: `https://mailtrap.io/accounts/{ACCOUNT_ID}/inboxes/{INBOX_ID}`
2. Update `MAILTRAP_ACCOUNT_ID` and `MAILTRAP_INBOX_ID` environment variables

## Best Practices

### 1. Use Unique Email Addresses

Generate unique test emails to avoid conflicts:

```python
test_email = f"test-{int(time.time())}@example.com"
```

### 2. Reasonable Timeouts

Use appropriate timeouts based on email service latency:

```python
# Fast SMTP delivery (Mailtrap)
email = get_latest_email(test_email, timeout=10)

# Slower email services
email = get_latest_email(test_email, timeout=30)
```

### 3. Cleanup After Tests

Mailtrap automatically cleans inbox, but you can manually delete messages:

```python
# Delete test messages via API (future enhancement)
# DELETE https://mailtrap.io/api/accounts/{account_id}/inboxes/{inbox_id}/messages/{message_id}
```

### 4. Graceful Skipping

Tests should skip gracefully when API credentials unavailable:

```python
if not MAILTRAP_API_TOKEN:
    pytest.skip("MAILTRAP_API_TOKEN not set - skipping API verification")
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Email Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          poetry install --no-root

      - name: Run email tests
        env:
          MAILTRAP_API_TOKEN: ${{ secrets.MAILTRAP_API_TOKEN }}
          MAILTRAP_ACCOUNT_ID: ${{ secrets.MAILTRAP_ACCOUNT_ID }}
          MAILTRAP_INBOX_ID: ${{ secrets.MAILTRAP_INBOX_ID }}
        run: |
          poetry run pytest tests/e2e/test_email_invitation_workflow.py -v
```

## See Also

- **Email Service Implementation**: `api/services/email_service.py`
- **Email Integration Plan**: `docs/saas/EMAIL_INTEGRATION_PLAN.md`
- **E2E Test Suite**: `tests/e2e/test_email_invitation_workflow.py`
- **Mailtrap API Docs**: https://api-docs.mailtrap.io/

---

**Last Updated**: 2025-10-20
**Status**: ✅ Complete
**Test Coverage**: 3 email tests (100% passing with API credentials)
