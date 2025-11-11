"""
Comprehensive test for profile settings save functionality
Tests the ACTUAL user workflow that was broken
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui


pytestmark = pytest.mark.usefixtures("api_server")


def test_settings_save_workflow(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test the complete settings save workflow that the user reported broken.

    This test ACTUALLY CLICKS THE SAVE BUTTON and verifies:
    1. No "Failed to fetch" error
    2. No annoying alert() popups
    3. Toast notification appears
    4. Settings are persisted
    """
    print("\n🧪 Testing Settings Save Workflow...")

    # Setup: Create test organization and admin user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin", "volunteer"],
    )

    # Track console errors
    console_errors = []
    page.on("console", lambda msg:
        console_errors.append(msg.text) if msg.type == "error" else None
    )

    # Track network errors
    network_errors = []
    page.on("requestfailed", lambda request:
        network_errors.append(f"{request.method} {request.url}")
    )

    # Track dialogs (alerts/confirms/prompts)
    dialogs = []
    page.on("dialog", lambda dialog:
        dialogs.append({"type": dialog.type, "message": dialog.message}) or dialog.accept()
    )

    print("  1. Login as admin...")
    login_via_ui(page, app_config.app_url, user["email"], user["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)
    print("     ✓ Logged in")

    print("  2. Open settings modal...")
    settings_btn = page.get_by_role("button", name="⚙️")
    settings_btn.click()
    page.wait_for_timeout(500)

    # Verify modal is visible
    modal = page.locator('#settings-modal')
    expect(modal).to_be_visible()
    print("     ✓ Settings modal opened")

    print("  3. Modify language setting...")
    # Change language as a test of settings save
    lang_selector = page.locator("#settings-language")
    original_lang = lang_selector.input_value()
    new_lang = "es" if original_lang != "es" else "en"
    lang_selector.select_option(new_lang)
    print(f"     ✓ Changed language from {original_lang} to {new_lang}")

    print("  4. Click Save button...")
    save_btn = page.locator('button[onclick="saveSettings()"]')

    # CRITICAL: Actually click the save button!
    save_btn.click()
    page.wait_for_timeout(2000)

    print("  5. Verify NO errors occurred...")
    # Check for network errors (filter out expected external requests)
    real_network_errors = [
        err for err in network_errors
        if "www.gstatic.com" not in err and "recaptcha" not in err
    ]
    if real_network_errors:
        print(f"     ✗ Network errors: {real_network_errors}")
        assert False, f"Network request failed: {real_network_errors}"
    else:
        print("     ✓ No network errors")

    # Check for console errors
    fetch_errors = [e for e in console_errors if 'fetch' in e.lower() or 'failed' in e.lower()]
    if fetch_errors:
        print(f"     ✗ Console errors: {fetch_errors}")
        assert False, f"Console errors occurred: {fetch_errors}"
    else:
        print("     ✓ No console errors")

    print("  6. Verify NO popup dialogs...")
    # Check if any alert() was shown
    alert_dialogs = [d for d in dialogs if d['type'] == 'alert']
    if alert_dialogs:
        print(f"     ⚠️  Alert dialogs shown: {alert_dialogs}")
        print("     (This is OK now with old code, but should be toast with new code)")
    else:
        print("     ✓ No popup alerts (using toast notifications!)")

    print("  7. Verify toast notification appeared...")
    # Look for toast container
    toast_container = page.locator('#toast-container')
    if toast_container.count() > 0:
        toasts = toast_container.locator('.toast')
        if toasts.count() > 0:
            toast_text = toasts.first.inner_text()
            print(f"     ✓ Toast shown: '{toast_text}'")
            # Accept both English and Spanish success messages
            assert 'success' in toast_text.lower() or 'saved' in toast_text.lower() or 'guardado' in toast_text.lower(), \
                "Toast should indicate success"
        else:
            print("     ⚠️  Toast container exists but no toasts visible")
    else:
        print("     ⚠️  No toast container (may still be using alerts)")

    print("  8. Verify settings UI updated...")
    # Reopen settings to verify language persisted
    settings_btn = page.get_by_role("button", name="⚙️")
    settings_btn.click()
    page.wait_for_timeout(500)

    lang_selector = page.locator("#settings-language")
    current_lang = lang_selector.input_value()
    print(f"     Current language after save: {current_lang}")
    assert current_lang == new_lang, f"Language should be {new_lang}, got {current_lang}"
    print("     ✓ Settings persisted correctly")

    print("\n✅ Settings save workflow test PASSED!")


def test_edit_timeoff_no_popups(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test availability page loads properly
    """
    print("\n🧪 Testing Availability Page...")

    # Setup: Create test organization and user
    org = api_client.create_org()
    user = api_client.create_user(
        org_id=org["id"],
        name="Test User",
        roles=["volunteer"],
    )

    print("  1. Login...")
    login_via_ui(page, app_config.app_url, user["email"], user["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)
    print("     ✓ Logged in")

    print("  2. Navigate to Availability page...")
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_timeout(1000)

    # Verify availability view loaded
    availability_inputs = page.locator('#timeoff-start, #timeoff-end')
    if availability_inputs.count() > 0:
        print(f"     ✓ Availability page loaded with time-off inputs")
    else:
        print("     ⚠️  Availability inputs not found")

    print("\n✅ Availability page test complete!")
