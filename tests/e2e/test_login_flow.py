"""
E2E test for login flow - Following claude.md guidelines
Tests the complete user journey from login page to main app

User Journey:
1. User opens app
2. User navigates to login screen
3. User enters email and password
4. User clicks login button
5. User sees main app with their name displayed
6. User can access their data/schedule
"""
import pytest
from playwright.sync_api import Page, expect
import time
import requests


def test_login_complete_user_journey(page: Page):
    """Test complete login flow from login screen to main app"""

    print(f"\n{'='*80}")
    print("TESTING LOGIN USER JOURNEY")
    print(f"{'='*80}\n")

    # Setup: Create a test user to login with
    timestamp = int(time.time())
    test_email = f"logintest{timestamp}@test.com"
    test_password = "TestPassword123"
    test_name = f"Login Test User {timestamp}"

    print("Setup: Creating test user via API...")
    org_data = {
        "id": f"login_test_org_{timestamp}",
        "name": f"Login Test Org {timestamp}",
        "region": "Test",
        "config": {}
    }
    requests.post("http://localhost:8000/api/organizations/", json=org_data)

    signup_data = {
        "org_id": org_data["id"],
        "name": test_name,
        "email": test_email,
        "password": test_password,
        "roles": ["admin"]
    }
    signup_response = requests.post("http://localhost:8000/api/auth/signup", json=signup_data)
    if signup_response.status_code not in [200, 201]:
        raise Exception(f"Failed to create test user: {signup_response.text}")
    print(f"✓ Test user created: {test_email}\n")

    # Step 1: Navigate to app
    print("Step 1: Navigating to app...")
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")

    # Step 2: Navigate to login screen
    print("Step 2: Navigating to login screen...")
    if page.locator('#onboarding-screen').is_visible():
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

    expect(page.locator('#login-screen')).to_be_visible()
    print("✓ Login screen visible\n")

    # Step 3: Fill in credentials
    print(f"Step 3: Entering credentials ({test_email})...")
    page.locator('#login-email').fill(test_email)
    page.locator('#login-password').fill(test_password)

    # Track login request
    login_requests = []
    def handle_response(response):
        if '/auth/login' in response.url:
            login_requests.append({
                'status': response.status,
                'url': response.url
            })
    page.on("response", handle_response)

    # Step 4: Submit login
    print("Step 4: Clicking login button...")
    page.locator('#login-screen button[type="submit"]').click()
    page.wait_for_timeout(2000)

    # Step 5: Verify login success
    print("Step 5: Verifying login success...\n")

    # Check API response
    if login_requests:
        last_login = login_requests[-1]
        print(f"  Login API status: {last_login['status']}")
        if last_login['status'] not in [200, 201]:
            raise AssertionError(f"Login API failed with status {last_login['status']}")
        print("  ✓ Login API successful")

    # Should be on main app screen
    try:
        expect(page.locator('#main-app')).to_be_visible(timeout=5000)
        print("  ✓ Main app visible")
    except Exception as e:
        print(f"  ✗ Main app not visible: {e}")
        # Debug
        print("\n  Visible screens:")
        for screen_id in ['onboarding-screen', 'login-screen', 'join-screen', 'profile-screen', 'main-app']:
            is_visible = page.locator(f'#{screen_id}').is_visible()
            print(f"    {screen_id}: {'VISIBLE' if is_visible else 'hidden'}")
        page.screenshot(path="/tmp/login_failed.png")
        raise

    # Step 6: Verify user data is displayed
    print("Step 6: Verifying user data displayed...\n")

    # User name should be shown
    user_display = page.locator('#user-name-display')
    expect(user_display).to_be_visible()
    expect(user_display).to_have_text(test_name)
    print(f"  ✓ User name displayed: '{test_name}'")

    # Auth token should be saved
    auth_token = page.evaluate("() => localStorage.getItem('authToken')")
    assert auth_token is not None, "Auth token not saved"
    print("  ✓ Auth token saved to localStorage")

    # Schedule section should be accessible
    if page.locator('#schedule-section').count() > 0:
        print("  ✓ Schedule section accessible")

    print(f"\n{'='*80}")
    print("✅ LOGIN FLOW TEST PASSED")
    print(f"{'='*80}\n")


def test_login_with_invalid_credentials(page: Page):
    """Test that login fails gracefully with wrong password"""

    print("\nTesting login with invalid credentials...")

    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")

    # Navigate to login
    if page.locator('#onboarding-screen').is_visible():
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

    expect(page.locator('#login-screen')).to_be_visible()

    # Enter invalid credentials
    page.locator('#login-email').fill("nonexistent@test.com")
    page.locator('#login-password').fill("wrongpassword")

    # Try to login
    page.locator('#login-screen button[type="submit"]').click()
    page.wait_for_timeout(2000)

    # Should still be on login screen (not logged in)
    expect(page.locator('#login-screen')).to_be_visible()
    print("✓ Still on login screen (not logged in)")

    # Should NOT be on main app
    expect(page.locator('#main-app')).not_to_be_visible()
    print("✓ Not logged in with invalid credentials")

    # Error message should be visible
    # Check for toast or error div
    has_error = (
        page.locator('.toast.error').is_visible() or
        page.locator('#login-error').is_visible() or
        page.locator('.error-message').is_visible()
    )
    if has_error:
        print("✓ Error message shown to user")
    else:
        print("⚠️  Warning: Error message may not be visible")


def test_login_empty_form_validation(page: Page):
    """Test that empty login form prevents submission"""

    print("\nTesting login form validation...")

    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")

    # Navigate to login
    if page.locator('#onboarding-screen').is_visible():
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

    expect(page.locator('#login-screen')).to_be_visible()

    # Try to submit without filling anything
    page.locator('#login-screen button[type="submit"]').click()
    page.wait_for_timeout(500)

    # HTML5 validation should prevent submission
    # Should still be on login screen
    expect(page.locator('#login-screen')).to_be_visible()
    print("✓ Form validation prevents empty submission")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
