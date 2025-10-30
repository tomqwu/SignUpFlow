"""Debug test to understand why settings modal isn't showing."""

from playwright.sync_api import sync_playwright, expect
import time

BASE_URL = "http://localhost:8000"

def test_debug_settings_modal():
    """Debug test for settings modal visibility."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless mode for Docker
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Track console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # Track errors
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("\n🔍 Debug: Login as pastor@grace.church")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')
        page.get_by_role("link", name="Sign in").click()
        page.wait_for_timeout(500)

        page.fill('#login-email', 'pastor@grace.church')
        page.fill('#login-password', 'password')
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

        print("✓ Logged in successfully")

        # Check currentUser and currentOrg in JavaScript context
        print("\n🔍 Debug: Check JavaScript globals")
        current_user = page.evaluate("() => window.currentUser")
        current_org = page.evaluate("() => window.currentOrg")

        print(f"currentUser: {current_user}")
        print(f"currentOrg: {current_org}")

        # Check if modal exists
        print("\n🔍 Debug: Check if modal exists in DOM")
        modal_exists = page.evaluate("() => document.getElementById('settings-modal') !== null")
        print(f"Modal exists: {modal_exists}")

        if modal_exists:
            modal_classes = page.evaluate("() => document.getElementById('settings-modal').className")
            print(f"Modal classes BEFORE click: {modal_classes}")

        # Check if showSettings function exists
        print("\n🔍 Debug: Check if showSettings function exists")
        function_exists = page.evaluate("() => typeof window.showSettings")
        print(f"showSettings function type: {function_exists}")

        # Find settings button
        print("\n🔍 Debug: Find settings button")
        settings_btn = page.get_by_role("button", name="⚙️")
        is_visible = settings_btn.is_visible()
        print(f"Settings button visible: {is_visible}")

        # Take screenshot BEFORE clicking
        print("\n📸 Screenshot BEFORE clicking settings button")
        page.screenshot(path="/tmp/before_settings_click.png")

        # Click settings button
        print("\n🔍 Debug: Click settings button")
        settings_btn.click()
        page.wait_for_timeout(1000)

        # Check modal classes AFTER click
        if modal_exists:
            modal_classes_after = page.evaluate("() => document.getElementById('settings-modal').className")
            print(f"Modal classes AFTER click: {modal_classes_after}")

            # Check if modal is displayed
            modal_display = page.evaluate("() => window.getComputedStyle(document.getElementById('settings-modal')).display")
            print(f"Modal display style: {modal_display}")

        # Take screenshot AFTER clicking
        print("\n📸 Screenshot AFTER clicking settings button")
        page.screenshot(path="/tmp/after_settings_click.png")

        # Print console messages
        print("\n🔍 Debug: Console messages:")
        for msg in console_messages[-20:]:  # Last 20 messages
            print(f"  {msg}")

        # Print errors
        if errors:
            print("\n❌ Errors detected:")
            for err in errors:
                print(f"  {err}")

        browser.close()

        # Final analysis
        print("\n" + "="*60)
        print("ANALYSIS:")
        if errors:
            print("❌ JavaScript errors found - this is likely the issue")
        elif modal_classes_after and 'hidden' in modal_classes_after:
            print("⚠️  Modal still has 'hidden' class after clicking")
            print("   This means showSettings() is NOT removing the hidden class")
        else:
            print("✅ Modal classes look correct")
        print("="*60 + "\n")

if __name__ == "__main__":
    test_debug_settings_modal()
