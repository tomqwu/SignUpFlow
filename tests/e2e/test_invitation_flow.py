"""E2E tests validating invitation acceptance workflows."""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import (
    AppConfig,
    ApiTestClient,
    complete_invitation_signup,
    open_invitation,
)


pytestmark = pytest.mark.usefixtures("api_server")


def test_invitation_acceptance_complete_journey(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
) -> None:
    """Invited user can accept the invitation and reach the main application."""
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Invitation Admin",
        roles=["admin"],
    )

    invitee_name = "Invited User"
    invitee_email = f"{admin['person_id']}@example.com"
    invitation = api_client.create_invitation(
        admin_token=admin["token"],
        org_id=org["id"],
        email=invitee_email,
        name=invitee_name,
        roles=["member", "volunteer"],
    )

    open_invitation(page, app_config.app_url, invitation["token"])

    name_input = page.locator("#user-name")
    email_input = page.locator("#user-email")

    expect(name_input).to_have_value(invitee_name)
    expect(email_input).to_have_value(invitee_email)
    assert name_input.evaluate("el => Boolean(el.readOnly || el.disabled)")
    assert email_input.evaluate("el => Boolean(el.readOnly || el.disabled)")

    roles_display = page.locator("#invitation-roles-display")
    if roles_display.count():
        expect(roles_display).to_contain_text("member")
        expect(roles_display).to_contain_text("volunteer")

    timezone_input = page.locator("#user-timezone")
    if timezone_input.count():
        expect(timezone_input).not_to_have_value("")

    invitee_password = "InvitedUserPass123!"
    response = complete_invitation_signup(page, invitee_password)
    assert response.status in (200, 201)

    user_display = page.locator("#user-name-display")
    expect(user_display).to_be_visible()
    expect(user_display).to_have_text(invitee_name)

    auth_token = page.evaluate("() => window.localStorage.getItem('authToken')")
    assert auth_token, "Auth token not stored after completing invitation"


def test_invitation_with_invalid_token(page: Page, app_config: AppConfig) -> None:
    """Invalid invitation token should not authenticate the user."""
    page.goto(f"{app_config.app_url}/join?token=INVALID_TOKEN_12345", wait_until="networkidle")

    expect(page.locator("#main-app")).not_to_be_visible()

    error_locators = [
        page.locator(".toast.error"),
        page.locator("#invitation-error"),
        page.locator("#join-screen"),
    ]
    error_visible = any(
        locator.locator(":visible").count() > 0 for locator in error_locators
    )
    assert error_visible, "Invalid invitation token did not surface an error state"
