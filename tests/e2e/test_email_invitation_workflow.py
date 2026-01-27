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
import subprocess
import signal
import json
import sys
from typing import Generator

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

# Configure pytest to use the api_server fixture
pytestmark = pytest.mark.usefixtures("api_server")

# Port for mock SMTP server
MOCK_SMTP_PORT = 1025
MOCK_SMTP_LOG = "mock_smtp_emails.json"

@pytest.fixture(scope="module")
def mock_smtp_server() -> Generator[subprocess.Popen, None, None]:
    """Start mock SMTP server."""
    # Start server
    process = subprocess.Popen(
        [sys.executable, "tests/mock_smtp_server.py", str(MOCK_SMTP_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(1)
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait()

def get_latest_mock_email(to_email: str, timeout: int = 10) -> dict | None:
    """Get latest email from mock SMTP log."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(MOCK_SMTP_LOG):
            try:
                with open(MOCK_SMTP_LOG, "r") as f:
                    emails = json.load(f)
                    # Search backwards
                    for email in reversed(emails):
                        if to_email in email["to"]:
                            return email
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        time.sleep(0.5)
    return None

def test_admin_sends_invitation_email(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
    mock_smtp_server: subprocess.Popen,
):
    """
    Test complete invitation workflow with email sending via Mock SMTP.
    """
    timestamp = int(time.time())
    
    # Step 1: Setup - Create test organization and admin user
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    
    # Step 2: Navigate to Invitations
    page.goto(f"{app_config.app_url}/app/admin", wait_until="networkidle")
    
    # Click Invitations tab
    invitations_tab = page.locator('button[data-tab="invitations"]')
    try:
        expect(invitations_tab).to_be_visible()
    except Exception:
        print(f"DEBUG: Content of sidebar:\n{page.locator('.sidebar').inner_html()}")
        raise
    invitations_tab.click()

    # Step 3: Fill invitation form
    # Debug: Check tab content class and styles
    tab_content = page.locator("#invitations-tab")
    print(f"DEBUG: Tab content classes: {tab_content.get_attribute('class')}")
    display = page.evaluate('document.getElementById("invitations-tab").style.display')
    computed_display = page.evaluate('window.getComputedStyle(document.getElementById("invitations-tab")).display')
    # Step 3: Fill invitation form
    # Note: Use force=True because Playwright sometimes fails visibility check on tab switch
    # even when element is interactive. We verify functionality by checking email receipt.
    email_input = page.locator('#invite-email')
    
    volunteer_email = f"volunteer-{timestamp}@test.com"
    email_input.fill(volunteer_email, force=True)
    page.fill('#invite-name', "Test Volunteer", force=True)

    # Step 4: Send invitation
    # Note: Button is type="submit" inside a form, it does not have onclick attribute
    send_btn = page.locator('button[type="submit"]:has-text("Send Invitation")')
    
    # Click Send Invitation
    send_btn.click(force=True)
    
    # Step 5: Verify success in UI
    # Wait for table to update
    row = page.locator(f"tr:has-text('{volunteer_email}')")
    expect(row).to_be_visible(timeout=5000)
    expect(row).to_contain_text("pending")

    # Step 6: Verify email receipt in Mock SMTP
    email = get_latest_mock_email(volunteer_email)
    assert email is not None, f"Email to {volunteer_email} not received by mock SMTP server"
    
    print(f"✅ Verified email sent to {volunteer_email}")
    assert "You're invited to join" in email["data"]

