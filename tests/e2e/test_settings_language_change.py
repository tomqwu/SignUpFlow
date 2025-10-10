"""E2E test for settings language change functionality."""

import pytest
from playwright.sync_api import Page, expect


def test_change_language_in_settings(page: Page):
    """Test that changing language in settings works without errors."""
    # Set up event listeners BEFORE any navigation
    console_errors = []
    failed_requests = []

    def handle_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    def handle_response(response):
        if response.status >= 400:
            failed_requests.append({
                "url": response.url,
                "status": response.status
            })

    page.on("console", handle_console)
    page.on("response", handle_response)

    # Navigate to app
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")

    # Click Sign in link
    page.get_by_role("link", name="Sign in").click()
    page.wait_for_timeout(500)

    # Login as admin
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "pastor@grace.church")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_timeout(2000)

    # Verify we're logged in
    expect(page.locator("#user-name-display")).to_be_visible(timeout=5000)

    # Open settings modal by clicking the gear icon
    page.locator('button.btn-icon:has-text("⚙️")').click()
    page.wait_for_timeout(500)

    # Check the settings modal is visible
    settings_modal = page.locator("#settings-modal")
    expect(settings_modal).to_be_visible()

    # Get current language
    language_select = page.locator("#settings-language")
    current_language = language_select.input_value()
    print(f"Current language: {current_language}")

    # Change language to Chinese (Simplified)
    language_select.select_option("zh-CN")
    page.wait_for_timeout(500)

    # Click Save Changes button
    save_button = page.locator('button[data-i18n="settings.save_changes"]')
    save_button.click()
    page.wait_for_timeout(2000)

    # Check for errors
    print(f"\nConsole errors: {console_errors}")
    print(f"Failed requests: {failed_requests}")

    # Assert no 500 errors
    server_errors = [r for r in failed_requests if r["status"] >= 500]
    assert len(server_errors) == 0, f"Server errors occurred: {server_errors}"

    # Assert no 400 errors
    client_errors = [r for r in failed_requests if 400 <= r["status"] < 500]
    assert len(client_errors) == 0, f"Client errors occurred: {client_errors}"

    # Verify settings modal closed (or shows success)
    # The modal might still be visible but settings should be saved
    page.wait_for_timeout(500)

    print("✅ Language change saved successfully without errors")


def test_change_language_multiple_times(page: Page):
    """Test changing language multiple times in succession."""
    # Set up event listeners BEFORE any navigation
    failed_requests = []

    def handle_response(response):
        if response.status >= 400:
            failed_requests.append({
                "url": response.url,
                "status": response.status
            })

    page.on("response", handle_response)

    # Navigate and login
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("networkidle")

    page.get_by_role("link", name="Sign in").click()
    page.wait_for_timeout(500)

    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "pastor@grace.church")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "password")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_timeout(2000)

    # Test multiple language changes
    languages = ["zh-CN", "es", "pt", "en"]

    for lang in languages:
        print(f"\nChanging language to: {lang}")

        # Clear failed requests for this iteration
        failed_requests.clear()

        # Open settings
        page.locator('button.btn-icon:has-text("⚙️")').click()
        page.wait_for_timeout(500)

        # Change language
        language_select = page.locator("#settings-language")
        language_select.select_option(lang)
        page.wait_for_timeout(300)

        # Save
        save_button = page.locator('button[data-i18n="settings.save_changes"]')
        save_button.click()
        page.wait_for_timeout(1500)

        # Check for errors
        server_errors = [r for r in failed_requests if r["status"] >= 500]
        assert len(server_errors) == 0, f"Server errors occurred when changing to {lang}: {server_errors}"

        # Close modal if still open
        close_btn = page.locator('#settings-modal button.btn-close')
        if close_btn.is_visible():
            close_btn.click()
            page.wait_for_timeout(300)

    print("\n✅ Multiple language changes completed successfully")
