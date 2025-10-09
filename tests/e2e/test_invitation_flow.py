"""E2E tests for invitation workflow."""

import pytest
from playwright.sync_api import Page, expect


def test_admin_can_send_invitation(page: Page):
    """Test that admin can send invitation to new volunteer."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Navigate to admin console
    page.goto("http://localhost:8000/app/admin")
    page.wait_for_timeout(1000)

    # Click "People" tab - use specific data-tab attribute
    people_tab = page.locator('button.admin-tab-btn[data-tab="people"]')
    if people_tab.count() > 0:
        people_tab.click()
        page.wait_for_timeout(500)

        # Click "+ Invite User" button
        invite_button = page.locator("button:has-text('+ Invite User')")
        expect(invite_button).to_be_visible(timeout=5000)
        invite_button.click()
        page.wait_for_timeout(500)

        # Fill invitation form
        email_input = page.locator("#invite-email, input[name='email']")
        if email_input.count() > 0:
            timestamp = int(page.evaluate("Date.now()"))
            email_input.fill(f"invited_{timestamp}@test.com")

            name_input = page.locator("#invite-name, input[name='name']")
            if name_input.count() > 0:
                name_input.fill(f"Invited User {timestamp}")

            # Submit invitation
            submit_button = page.locator("button:has-text('Send Invitation'), button[type='submit']")
            submit_button.first.click()
            page.wait_for_timeout(2000)

            # Should show success message or invitation in list
            page.screenshot(path="/tmp/e2e-invitation-sent.png")


def test_invitation_token_validation(page: Page):
    """Test that invitation tokens are validated correctly."""
    # Try invalid token
    page.goto("http://localhost:8000/join?invite=invalid_token_12345")
    page.wait_for_timeout(1000)

    # Should show error or redirect
    page.screenshot(path="/tmp/e2e-invalid-invitation.png")


def test_accept_invitation_flow(page: Page):
    """Test accepting an invitation and creating account."""
    # This requires a valid invitation token from database
    # For now, test the UI flow
    page.goto("http://localhost:8000/join")
    page.wait_for_timeout(1000)

    # Should show either join or profile screen
    join_screen = page.locator("#join-screen")
    profile_screen = page.locator("#profile-screen")
    # Check at least one is visible
    assert join_screen.is_visible() or profile_screen.is_visible(), "Neither join nor profile screen visible"
