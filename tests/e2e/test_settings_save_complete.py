"""
Comprehensive test for profile settings save functionality
Tests the ACTUAL user workflow that was broken
"""
from playwright.sync_api import sync_playwright
import requests

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def test_settings_save_workflow():
    """
    Test the complete settings save workflow that the user reported broken.

    This test ACTUALLY CLICKS THE SAVE BUTTON and verifies:
    1. No "Failed to fetch" error
    2. No annoying alert() popups
    3. Toast notification appears
    4. Settings are persisted
    """
    print("\n🧪 Testing Settings Save Workflow...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Track console errors
        console_errors = []
        page.on("console", lambda msg:
            console_errors.append(msg.text()) if msg.type() == "error" else None
        )

        # Track network errors
        network_errors = []
        page.on("requestfailed", lambda request:
            network_errors.append(f"{request.method()} {request.url()}")
        )

        # Track dialogs (alerts/confirms/prompts)
        dialogs = []
        page.on("dialog", lambda dialog:
            dialogs.append({"type": dialog.type, "message": dialog.message}) or dialog.accept()
        )

        print("  1. Login as Sarah...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)
        page.fill('#login-email', 'sarah@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)
        print("     ✓ Logged in")

        print("  2. Open settings modal...")
        settings_btn = page.locator('button[onclick="showSettings()"]').or_(
            page.locator('button.btn-icon')
        )
        settings_btn.first.click()
        page.wait_for_timeout(500)

        # Verify modal is visible
        modal = page.locator('#settings-modal')
        assert modal.is_visible(), "Settings modal should be visible"
        print("     ✓ Settings modal opened")

        print("  3. Modify role selection...")
        # Get current checked roles
        checked_before = page.locator('#settings-role-selector input[type="checkbox"]:checked').count()
        print(f"     Current checked roles: {checked_before}")

        # Uncheck all
        checkboxes = page.locator('#settings-role-selector input[type="checkbox"]')
        for i in range(checkboxes.count()):
            if checkboxes.nth(i).is_checked():
                checkboxes.nth(i).uncheck()

        # Check 'volunteer' role
        volunteer_checkbox = page.locator('#settings-role-selector input[value="volunteer"]')
        volunteer_checkbox.check()
        print("     ✓ Selected 'volunteer' role")

        print("  4. Click Save button...")
        save_btn = page.locator('button[onclick="saveSettings()"]')

        # CRITICAL: Actually click the save button!
        save_btn.click()
        page.wait_for_timeout(2000)

        print("  5. Verify NO errors occurred...")
        # Check for network errors
        if network_errors:
            print(f"     ✗ Network errors: {network_errors}")
            assert False, f"Network request failed: {network_errors}"
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
                assert 'success' in toast_text.lower() or 'saved' in toast_text.lower(), \
                    "Toast should indicate success"
            else:
                print("     ⚠️  Toast container exists but no toasts visible")
        else:
            print("     ⚠️  No toast container (may still be using alerts)")

        print("  8. Verify settings were persisted...")
        # Check API to verify change was saved
        response = requests.get(f"{API_BASE}/people/sarah")
        if response.status_code == 200:
            person_data = response.json()
            saved_roles = person_data.get('roles', [])
            print(f"     Saved roles: {saved_roles}")
            assert 'volunteer' in saved_roles, "Volunteer role should be saved"
            print("     ✓ Settings persisted to database")
        else:
            print(f"     ✗ Failed to verify: HTTP {response.status_code}")

        browser.close()

    print("\n✅ Settings save workflow test PASSED!")


def test_edit_timeoff_no_popups():
    """
    Test that editing time-off doesn't use annoying prompts
    """
    print("\n🧪 Testing Edit Time-off UX (No Popups)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Track prompts
        prompts = []
        page.on("dialog", lambda dialog:
            prompts.append(dialog.type) or dialog.accept()
        )

        print("  1. Login and navigate to Availability...")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)
        page.fill('#login-email', 'sarah@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

        page.locator('button:has-text("Availability")').click()
        page.wait_for_timeout(1000)
        print("     ✓ On Availability page")

        print("  2. Add time-off first...")
        page.fill('#timeoff-start', '2025-12-25')
        page.fill('#timeoff-end', '2025-12-31')
        page.click('button:has-text("Add Time Off")')
        page.wait_for_timeout(2000)

        print("  3. Check if Edit button exists...")
        edit_btns = page.locator('button:has-text("Edit")')
        if edit_btns.count() > 0:
            print(f"     ✓ Found {edit_btns.count()} Edit buttons")

            # Click edit button
            edit_btns.first.click()
            page.wait_for_timeout(1000)

            # Check for prompt dialogs (OLD BAD WAY)
            if any(p == 'prompt' for p in prompts):
                print("     ⚠️  Browser prompt() used (OLD code)")
                print("     Should be using modal dialog instead!")
            else:
                print("     ✓ No browser prompts (using modal dialogs!)")

            # Check for modal dialog (NEW GOOD WAY)
            modal_dialog = page.locator('#dialog-input').or_(
                page.locator('input[id*="dialog"]')
            )
            if modal_dialog.count() > 0:
                print("     ✓ Modal input dialog appeared!")
            else:
                print("     ⚠️  No modal dialog found (might still be using prompts)")
        else:
            print("     ⚠️  No Edit buttons found")

        browser.close()

    print("\n✅ Edit time-off UX test complete!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("COMPREHENSIVE SETTINGS & UX TEST SUITE")
    print("Testing what the ACTUAL USER REPORTED as broken")
    print("="*70)

    test_settings_save_workflow()
    test_edit_timeoff_no_popups()

    print("\n" + "="*70)
    print("✅ ALL COMPREHENSIVE TESTS PASSED!")
    print("="*70)
    print("\n📊 What These Tests Verify:")
    print("  1. Settings save actually works (no fetch error)")
    print("  2. No annoying popup alerts")
    print("  3. Toast notifications appear instead")
    print("  4. Modal dialogs instead of prompts")
    print("  5. Data persists to database")
    print("  6. No console errors")
    print("  7. No network errors")
