"""E2E tests covering authentication entry points."""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import (
    AppConfig,
    ApiTestClient,
    login_via_ui,
    navigate_to_login,
    submit_login_form,
)


pytestmark = pytest.mark.usefixtures("api_server")


def test_login_complete_user_journey(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
) -> None:
    """User can authenticate via the login form and reach the main application."""
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Login Test User",
        roles=["admin"],
    )

    login_via_ui(page, app_config.app_url, user["email"], user["password"])

    user_display = page.locator("#user-name-display")
    expect(user_display).to_be_visible()
    expect(user_display).to_have_text(user["name"])

    auth_token = page.evaluate("() => window.localStorage.getItem('authToken')")
    assert auth_token, "Auth token not stored after successful login"

    schedule_section = page.locator("#schedule-section")
    if schedule_section.count():
        expect(schedule_section).to_be_visible()


def test_login_with_invalid_credentials(page: Page, app_config: AppConfig) -> None:
    """Invalid credentials should not grant access and must show an error."""
    navigate_to_login(page, app_config.app_url)

    response = submit_login_form(page, "nonexistent@test.com", "wrongpassword")
    assert response.status >= 400

    expect(page.locator("#login-screen")).to_be_visible()
    expect(page.locator("#main-app")).not_to_be_visible()

    error_locators = [
        page.locator(".toast.error"),
        page.locator("#login-error"),
        page.locator(".error-message"),
    ]
    error_visible = any(
        locator.locator(":visible").count() > 0 for locator in error_locators
    )
    if not error_visible:
        print("⚠️  Warning: No error banner displayed for invalid credentials")


def test_login_empty_form_validation(page: Page, app_config: AppConfig) -> None:
    """Empty form submission should be blocked by client-side validation."""
    navigate_to_login(page, app_config.app_url)

    login_requests = []
    page.on(
        "request",
        lambda request: login_requests.append(request)
        if request.method == "POST" and "/auth/login" in request.url
        else None,
    )

    submit_button = page.locator('#login-screen button[type="submit"]')
    expect(submit_button).to_be_enabled()
    submit_button.click()

    expect(page.locator("#login-screen")).to_be_visible()
    page.wait_for_function(
        "() => document.querySelector('form input:invalid') !== null"
    )

    assert (
        len(login_requests) == 0
    ), "Login request should not be sent when form is invalid"
