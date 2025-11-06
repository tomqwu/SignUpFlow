"""
Complete end-to-end test for full organization creation flow.
Tests: Create org -> Fill profile -> Create admin user -> Login -> See main app
"""
import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig


pytestmark = pytest.mark.usefixtures("api_server")


def test_complete_org_creation_and_signup_flow(
    page: Page,
    app_config: AppConfig,
):
    """Test the complete flow from creating org to being logged in."""

    # Use unique timestamp-based data
    timestamp = int(time.time())
    org_name = f"Test Org {timestamp}"
    user_name = f"Test Admin {timestamp}"
    user_email = f"admin{timestamp}@test.com"
    user_password = "TestPassword123"

    print(f"\n{'='*80}")
    print(f"TESTING COMPLETE ORG CREATION FLOW")
    print(f"{'='*80}")
    print(f"Org Name: {org_name}")
    print(f"Admin Name: {user_name}")
    print(f"Admin Email: {user_email}")
    print(f"{'='*80}\n")

    # Step 1: Navigate to app
    print("Step 1: Loading app...")
    page.goto(app_config.app_url)
    page.wait_for_load_state("networkidle")

    # Step 2: Click Get Started
    print("Step 2: Clicking 'Get Started'...")
    get_started_btn = page.locator('button:has-text("Get Started")')
    expect(get_started_btn).to_be_visible()
    get_started_btn.click()
    page.wait_for_timeout(500)

    # Should be on join screen
    expect(page.locator('#join-screen')).to_be_visible()
    print("✓ Navigated to join screen")

    # Step 3: Click Create New Organization
    print("Step 3: Clicking 'Create New Organization'...")
    create_org_btn = page.locator('button:has-text("Create New Organization")')
    expect(create_org_btn).to_be_visible()
    create_org_btn.click()
    page.wait_for_timeout(500)

    # Create org form should appear
    create_org_section = page.locator('#create-org-section')
    expect(create_org_section).not_to_have_class('hidden')
    print("✓ Create org form is visible")

    # Step 4: Fill in organization details
    print(f"Step 4: Filling org details - '{org_name}'...")
    page.locator('#new-org-name').fill(org_name)
    page.locator('#new-org-region').fill("Test City")

    # Step 5: Submit org creation
    print("Step 5: Submitting org creation...")
    submit_btn = create_org_section.locator('button[type="submit"]')
    submit_btn.click()

    # Wait for navigation to profile screen
    page.wait_for_timeout(2000)

    # Should navigate to profile screen
    try:
        expect(page.locator('#profile-screen')).to_be_visible(timeout=5000)
        print("✓ Navigated to profile screen")
    except Exception as e:
        print(f"✗ Failed to navigate to profile screen: {e}")
        # Take screenshot for debugging
        page.screenshot(path="/tmp/org_creation_failed.png")
        raise

    # Step 5b: Verify UI state on profile screen
    print("Step 5b: Verifying profile screen UI fixes...")

    # Check timezone auto-detection
    timezone_select = page.locator('#user-timezone')
    selected_timezone = timezone_select.input_value()
    print(f"  Timezone selected: {selected_timezone}")
    if selected_timezone == "UTC":
        print("  ⚠️  Warning: Timezone is UTC (auto-detection may not have worked)")
    else:
        print(f"  ✓ Timezone auto-detected to: {selected_timezone}")

    # Check that "Your Assigned Roles" section is hidden
    roles_section = page.locator('#invitation-roles-display')
    if roles_section.count() > 0:
        is_visible = roles_section.is_visible()
        if is_visible:
            print("  ✗ 'Your Assigned Roles' section should be hidden but is visible")
            raise AssertionError("Roles section should be hidden for new org creators")
        else:
            print("  ✓ 'Your Assigned Roles' section is hidden")
    else:
        print("  ✓ 'Your Assigned Roles' element not found (expected)")

    # Step 6: Fill in user profile
    print(f"Step 6: Filling user profile - '{user_name}', '{user_email}'...")
    page.locator('#user-name').fill(user_name)
    page.locator('#user-email').fill(user_email)
    page.locator('#user-password').fill(user_password)

    # Step 7: Submit profile/signup
    print("Step 7: Submitting user signup...")
    profile_form = page.locator('#profile-screen form')
    submit_profile_btn = profile_form.locator('button[type="submit"]')

    # Track network requests
    signup_requests = []
    def handle_response(response):
        if '/auth/signup' in response.url:
            signup_requests.append({
                'url': response.url,
                'status': response.status,
                'body': response.text() if response.status != 200 else None
            })
    page.on("response", handle_response)

    submit_profile_btn.click()

    # Wait for signup to complete
    page.wait_for_timeout(3000)

    # Step 8: Verify we're logged in and on main app
    print("Step 8: Verifying login and main app...")

    # Check for signup requests
    if signup_requests:
        last_signup = signup_requests[-1]
        print(f"Signup request status: {last_signup['status']}")
        if last_signup['status'] not in [200, 201]:
            print(f"✗ Signup failed: {last_signup['body']}")
            page.screenshot(path="/tmp/signup_failed.png")
            raise AssertionError(f"Signup failed with status {last_signup['status']}: {last_signup['body']}")
        else:
            print("✓ Signup successful")

    try:
        # Should be on main app screen
        expect(page.locator('#main-app')).to_be_visible(timeout=5000)
        print("✓ Main app is visible")

        # User name should be displayed
        user_display = page.locator('#user-name-display')
        expect(user_display).to_have_text(user_name)
        print(f"✓ User name '{user_name}' is displayed")

        # Should have auth token in localStorage
        auth_token = page.evaluate("() => localStorage.getItem('authToken')")
        assert auth_token is not None, "Auth token not found in localStorage"
        print("✓ Auth token saved to localStorage")

        print(f"\n{'='*80}")
        print("✅ COMPLETE ORG CREATION FLOW TEST PASSED")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"✗ FAILED AT FINAL VERIFICATION")
        print(f"{'='*80}")
        print(f"Error: {e}")

        # Debug info
        print("\nCurrent URL:", page.url)
        print("\nVisible screens:")
        for screen_id in ['onboarding-screen', 'join-screen', 'profile-screen', 'main-app']:
            screen = page.locator(f'#{screen_id}')
            is_visible = screen.is_visible()
            print(f"  {screen_id}: {'visible' if is_visible else 'hidden'}")

        # Take screenshot
        page.screenshot(path="/tmp/final_verification_failed.png")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
