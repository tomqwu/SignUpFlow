"""End-to-end test for login flow using Playwright."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


def test_login_page_loads(page: Page):
    """Test that the login page loads and displays correctly."""
    # Navigate to home page
    page.goto("http://localhost:8000/")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Take screenshot of home page
    page.screenshot(path="/tmp/01-home-page.png")

    # Check if we see the onboarding screen
    onboarding = page.locator("#onboarding-screen")
    print(f"Onboarding visible: {onboarding.is_visible()}")

    # Look for "Sign in" link (use role to be specific)
    sign_in_link = page.get_by_role("link", name="Sign in")
    print(f"Sign in link found: {sign_in_link.count()}")

    # Click "Sign in" link
    if sign_in_link.count() > 0:
        sign_in_link.click()
        page.wait_for_timeout(1000)  # Wait 1 second

        # Take screenshot after clicking
        page.screenshot(path="/tmp/02-after-sign-in-click.png")

        # Check URL
        print(f"Current URL: {page.url}")

        # Check if login screen is visible
        login_screen = page.locator("#login-screen")
        print(f"Login screen visible: {login_screen.is_visible()}")

        # Check all screens visibility
        screens = page.locator(".screen").all()
        for i, screen in enumerate(screens):
            screen_id = screen.get_attribute("id")
            classes = screen.get_attribute("class")
            is_visible = screen.is_visible()
            print(f"Screen {i}: {screen_id}, classes: {classes}, visible: {is_visible}")


def test_login_form_submission(page: Page):
    """Test submitting the login form."""
    # Navigate directly to login page
    page.goto("http://localhost:8000/login")
    page.wait_for_load_state("networkidle")

    # Take screenshot
    page.screenshot(path="/tmp/03-login-page-direct.png")

    # Check if login form is visible
    login_screen = page.locator("#login-screen")
    print(f"Login screen visible: {login_screen.is_visible()}")

    # Check if form fields exist
    email_input = page.locator("#login-email")
    password_input = page.locator("#login-password")
    print(f"Email input visible: {email_input.is_visible()}")
    print(f"Password input visible: {password_input.is_visible()}")

    if email_input.is_visible() and password_input.is_visible():
        # Fill in the form
        email_input.fill("pastor@grace.church")
        password_input.fill("password")

        # Take screenshot before submit
        page.screenshot(path="/tmp/04-login-form-filled.png")

        # Click submit button
        submit_button = page.get_by_role("button", name="Sign In")
        submit_button.click()

        # Wait for navigation or error
        page.wait_for_timeout(2000)

        # Take screenshot after submit
        page.screenshot(path="/tmp/05-after-login-submit.png")

        # Check current URL
        print(f"After login URL: {page.url}")

        # Check for error messages
        error_div = page.locator("#login-error")
        if error_div.is_visible():
            print(f"Login error: {error_div.text_content()}")

        # Check if we're on the main app
        main_app = page.locator("#main-app")
        print(f"Main app visible: {main_app.is_visible()}")


def test_check_console_logs(page: Page):
    """Test and capture console logs during login."""
    console_messages = []

    def handle_console(msg):
        console_messages.append(f"{msg.type}: {msg.text}")

    page.on("console", handle_console)

    # Navigate to home
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")

    # Click sign in (use role to be specific)
    sign_in_link = page.get_by_role("link", name="Sign in")
    if sign_in_link.count() > 0:
        sign_in_link.click()
        page.wait_for_timeout(1000)

    # Print all console messages
    print("\n=== Console Messages ===")
    for msg in console_messages:
        print(msg)
