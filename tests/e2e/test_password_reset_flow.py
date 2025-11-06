"""
E2E tests for password reset flow.

Tests the complete user journey:
1. User forgets password and requests reset
2. User clicks reset link (in dev, auto-navigates)
3. User sets new password
4. User logs in with new password
"""

import pytest
import requests
import time
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


def test_password_reset_complete_journey(page: Page, app_config: AppConfig):
    """
    Test complete password reset flow from forgot password to login with new password.

    User Journey:
    1. Create test user with known password
    2. Navigate to forgot password screen
    3. Enter email and request reset
    4. System shows reset screen (dev mode auto-navigates)
    5. Set new password
    6. Login with new password
    7. Verify logged in successfully
    """

    print("\n" + "="*80)
    print("TESTING PASSWORD RESET USER JOURNEY")
    print("="*80)

    # Setup: Create test user via API
    print("\nSetup: Creating test user...")
    timestamp = int(time.time())
    test_org_id = f"org_password_reset_{timestamp}"
    test_email = f"resetuser{timestamp}@test.com"
    old_password = "OldPassword123"
    new_password = "NewPassword456"
    test_name = f"Reset User {timestamp}"

    # Create organization
    org_response = requests.post(
        f"{app_config.app_url}/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Password Reset Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201], f"Failed to create org: {org_response.text}"

    # Create user with known password
    signup_response = requests.post(
        f"{app_config.app_url}/api/auth/signup",
        json={
            "email": test_email,
            "password": old_password,
            "name": test_name,
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201, f"Failed to create user: {signup_response.text}"
    print(f"✓ User created: {test_email}")

    # Step 1: Navigate to forgot password screen
    print("\nStep 1: User navigates to forgot password screen...")
    page.goto(f"{app_config.app_url}/login")

    # Click "Forgot password?" link
    page.locator('a[data-i18n="auth.forgot_password"]').click()

    # Verify on forgot password screen
    expect(page.locator('#forgot-password-screen')).to_be_visible(timeout=3000)
    print("  ✓ Forgot password screen visible")

    # Step 2: Request password reset
    print("\nStep 2: User requests password reset...")
    email_input = page.locator('#forgot-email')
    email_input.fill(test_email)
    print(f"  Email entered: {test_email}")

    # Submit form
    page.locator('#forgot-password-screen button[type="submit"]').click()

    # Wait for success message
    success_message = page.locator('#forgot-success')
    expect(success_message).to_be_visible(timeout=5000)
    print("  ✓ Success message displayed")

    # Step 3: Auto-navigate to reset password screen (dev mode)
    print("\nStep 3: Waiting for auto-navigation to reset password screen (dev mode)...")
    # In dev mode, the app auto-navigates after 2 seconds
    expect(page.locator('#reset-password-screen')).to_be_visible(timeout=5000)
    print("  ✓ Reset password screen visible")

    # Verify token is pre-filled (hidden field)
    token_field = page.locator('#reset-token')
    token_value = token_field.input_value()
    assert token_value, "Reset token should be pre-filled"
    print(f"  ✓ Reset token pre-filled: {token_value[:20]}...")

    # Step 4: Set new password
    print("\nStep 4: User sets new password...")
    password_input = page.locator('#reset-password')
    confirm_input = page.locator('#reset-password-confirm')

    password_input.fill(new_password)
    confirm_input.fill(new_password)
    print(f"  New password entered: {'*' * len(new_password)}")

    # Submit form
    page.locator('#reset-password-screen button[type="submit"]').click()

    # Wait for success message
    reset_success = page.locator('#reset-success')
    expect(reset_success).to_be_visible(timeout=5000)
    print("  ✓ Password reset success message displayed")

    # Step 5: Auto-redirect to login screen
    print("\nStep 5: Waiting for auto-redirect to login...")
    expect(page.locator('#login-screen')).to_be_visible(timeout=5000)
    print("  ✓ Redirected to login screen")

    # Step 6: Login with new password
    print("\nStep 6: User logs in with new password...")
    page.locator('#login-email').fill(test_email)
    page.locator('#login-password').fill(new_password)
    print(f"  Email: {test_email}")
    print(f"  Password: {'*' * len(new_password)}")

    page.locator('#login-screen button[type="submit"]').click()

    # Step 7: Verify login successful
    print("\nStep 7: Verifying login successful...")
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ Main app visible")

    # Verify user name displayed
    user_display = page.locator('#user-name-display')
    expect(user_display).to_have_text(test_name)
    print(f"  ✓ User name displayed: '{test_name}'")

    # Verify auth token saved
    auth_token = page.evaluate("() => localStorage.getItem('authToken')")
    assert auth_token is not None, "Auth token not saved"
    print(f"  ✓ Auth token saved to localStorage")

    print("\n" + "="*80)
    print("✅ PASSWORD RESET FLOW TEST PASSED")
    print("="*80)


def test_password_reset_with_mismatched_passwords(page: Page, app_config: AppConfig):
    """
    Test that mismatched passwords show an error.

    User Journey:
    1. User is on reset password screen
    2. User enters different passwords
    3. User sees error message
    4. Password is not reset
    """

    print("\n" + "="*80)
    print("TESTING PASSWORD MISMATCH VALIDATION")
    print("="*80)

    # Setup: Create test user and get reset token
    print("\nSetup: Creating test user and getting reset token...")
    timestamp = int(time.time())
    test_org_id = f"org_mismatch_{timestamp}"
    test_email = f"mismatchuser{timestamp}@test.com"
    test_password = "TestPassword123"

    # Create organization
    org_response = requests.post(
        f"{app_config.app_url}/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Mismatch Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201]

    # Create user
    signup_response = requests.post(
        f"{app_config.app_url}/api/auth/signup",
        json={
            "email": test_email,
            "password": test_password,
            "name": f"Mismatch User {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201

    # Request password reset via API
    reset_response = requests.post(
        f"{app_config.app_url}/api/auth/forgot-password",
        json={"email": test_email}
    )
    reset_data = reset_response.json()
    token = reset_data["reset_link"].split("token=")[1]
    print(f"✓ Reset token obtained: {token[:20]}...")

    # Navigate to reset password screen with token
    print("\nStep 1: Navigating to reset password screen...")
    page.goto(f"{app_config.app_url}/reset-password?token={token}")

    # Debug: Wait for page to load and check which screen is visible
    page.wait_for_timeout(1000)  # Give router time to process

    # Check all screens
    screens = ['onboarding-screen', 'login-screen', 'forgot-password-screen', 'reset-password-screen', 'join-screen', 'profile-screen', 'main-app']
    visible_screen = None
    for screen_id in screens:
        if page.locator(f'#{screen_id}').is_visible():
            visible_screen = screen_id
            break

    # Debug: Check if router detected the token
    url_info = page.evaluate("""() => {
        return {
            pathname: window.location.pathname,
            search: window.location.search,
            hasRouter: typeof router !== 'undefined',
            resetToken: document.getElementById('reset-token')?.value || 'NOT SET'
        };
    }""")
    print(f"  Debug: URL pathname = {url_info['pathname']}")
    print(f"  Debug: URL search = {url_info['search']}")
    print(f"  Debug: Router exists = {url_info['hasRouter']}")
    print(f"  Debug: Reset token field value = {url_info['resetToken']}")
    print(f"  Debug: Visible screen = {visible_screen}")

    expect(page.locator('#reset-password-screen')).to_be_visible(timeout=3000)
    print("  ✓ Reset password screen visible")

    # Verify token is pre-filled by router
    token_field = page.locator('#reset-token')
    token_value = token_field.input_value()
    assert token_value == token, "Reset token should be pre-filled by router"
    print(f"  ✓ Token pre-filled: {token_value[:20]}...")

    # Step 2: Enter mismatched passwords
    print("\nStep 2: Entering mismatched passwords...")
    page.locator('#reset-password').fill("NewPassword123")
    page.locator('#reset-password-confirm').fill("DifferentPassword456")
    print("  Password: NewPassword123")
    print("  Confirm: DifferentPassword456")

    # Submit form
    page.locator('#reset-password-screen button[type="submit"]').click()

    # Step 3: Verify error message displayed
    print("\nStep 3: Verifying error message...")
    error_message = page.locator('#reset-error')
    expect(error_message).to_be_visible(timeout=3000)
    error_text = error_message.text_content()
    print(f"  ✓ Error message displayed: '{error_text}'")
    assert "match" in error_text.lower() or "same" in error_text.lower(), "Error should mention password mismatch"

    # Verify still on reset password screen
    expect(page.locator('#reset-password-screen')).to_be_visible()
    print("  ✓ Still on reset password screen (not redirected)")

    print("\n" + "="*80)
    print("✅ PASSWORD MISMATCH VALIDATION TEST PASSED")
    print("="*80)


def test_password_reset_with_invalid_token(page: Page, app_config: AppConfig):
    """
    Test that invalid reset token shows an error.

    User Journey:
    1. User navigates to reset password with invalid/expired token
    2. User tries to reset password
    3. User sees error message
    4. Password is not reset
    """

    print("\n" + "="*80)
    print("TESTING INVALID TOKEN HANDLING")
    print("="*80)

    # Navigate to reset password screen with invalid token
    print("\nStep 1: Navigating to reset password screen with invalid token...")
    invalid_token = "invalid_token_12345678901234567890"
    page.goto(f"{app_config.app_url}/reset-password?token={invalid_token}")
    expect(page.locator('#reset-password-screen')).to_be_visible(timeout=3000)
    print(f"  ✓ Reset password screen visible")

    # Verify invalid token is pre-filled by router
    token_field = page.locator('#reset-token')
    token_value = token_field.input_value()
    assert token_value == invalid_token, "Token should be pre-filled by router"
    print(f"  ✓ Invalid token pre-filled: {token_value[:20]}...")

    # Step 2: Try to reset password
    print("\nStep 2: Attempting to reset password with invalid token...")
    page.locator('#reset-password').fill("NewPassword123")
    page.locator('#reset-password-confirm').fill("NewPassword123")

    # Submit form
    page.locator('#reset-password-screen button[type="submit"]').click()

    # Step 3: Verify error message displayed
    print("\nStep 3: Verifying error message...")
    error_message = page.locator('#reset-error')
    expect(error_message).to_be_visible(timeout=5000)
    error_text = error_message.text_content()
    print(f"  ✓ Error message displayed: '{error_text}'")
    assert "invalid" in error_text.lower() or "expired" in error_text.lower(), "Error should mention invalid token"

    # Verify still on reset password screen
    expect(page.locator('#reset-password-screen')).to_be_visible()
    print("  ✓ Still on reset password screen")

    print("\n" + "="*80)
    print("✅ INVALID TOKEN HANDLING TEST PASSED")
    print("="*80)
