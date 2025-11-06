"""
End-to-end test for organization creation user flow.
Tests the exact steps a user would take to create an organization.
"""
import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


def test_create_organization_complete_flow(page: Page, app_config: AppConfig):
    """Test the complete organization creation flow from landing page."""

    # Navigate to the app
    page.goto(f"{app_config.app_url}/")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Click "Get Started" on onboarding screen
    get_started_btn = page.locator('button:has-text("Get Started")')
    get_started_btn.click()

    # Should now be on join screen
    expect(page.locator('#join-screen')).to_be_visible()

    # Click "Create New Organization" button
    create_org_btn = page.locator('button:has-text("Create New Organization")')
    create_org_btn.click()

    # Wait for the create org section to become visible
    time.sleep(0.5)
    create_org_section = page.locator('#create-org-section')
    expect(create_org_section).not_to_have_class('hidden')

    # Fill in organization name
    org_name_input = page.locator('#new-org-name')
    org_name_input.fill(f"Test Org {int(time.time())}")

    # Fill in optional location
    org_region_input = page.locator('#new-org-region')
    org_region_input.fill("Test City, CA")

    # Click the "Create & Continue" button in the form
    submit_btn = create_org_section.locator('button[type="submit"]')

    # Listen for any console errors
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    # Listen for network requests
    requests = []
    def handle_request(request):
        if '/organizations/' in request.url:
            requests.append({
                'url': request.url,
                'method': request.method,
                'post_data': request.post_data
            })
    page.on("request", handle_request)

    # Submit the form
    submit_btn.click()

    # Wait for navigation to profile screen or error
    try:
        # Should navigate to profile screen on success
        page.wait_for_selector('#profile-screen:not(.hidden)', timeout=10000)
        print("✅ Successfully navigated to profile screen")

        # Verify timezone auto-detection
        timezone_select = page.locator('#user-timezone')
        selected_timezone = timezone_select.input_value()
        print(f"✅ Timezone auto-detected: {selected_timezone}")

        # Verify it's not UTC (unless that's actually the browser timezone)
        if selected_timezone != "UTC":
            print(f"   → Confirmed timezone detection is working (not UTC)")

        # Verify roles section is hidden
        roles_section = page.locator('#invitation-roles-display')
        if roles_section.count() > 0 and roles_section.is_visible():
            raise AssertionError("❌ Roles section should be hidden for new org creators")
        print("✅ 'Your Assigned Roles' section is properly hidden")

        # Check if org was created
        print(f"\n✅ Organization creation flow completed successfully!")
        print(f"Network requests made: {len(requests)}")
        for req in requests:
            print(f"  - {req['method']} {req['url']}")
            print(f"    Data: {req['post_data']}")

    except Exception as e:
        # Check for error messages
        error_toasts = page.locator('.toast.error').all_text_contents()
        print(f"\n❌ Error occurred: {e}")
        print(f"Error toasts: {error_toasts}")
        print(f"\nConsole messages:")
        for msg in console_messages:
            print(f"  {msg}")
        print(f"\nNetwork requests made: {len(requests)}")
        for req in requests:
            print(f"  - {req['method']} {req['url']}")
            print(f"    Data: {req['post_data']}")
        raise


def test_create_organization_validates_empty_form(page: Page, app_config: AppConfig):
    """Test that empty form shows validation error."""

    page.goto(f"{app_config.app_url}/")
    page.wait_for_load_state("networkidle")

    # Click through to join screen
    page.locator('button:has-text("Get Started")').click()
    expect(page.locator('#join-screen')).to_be_visible()

    # Click "Create New Organization"
    page.locator('button:has-text("Create New Organization")').click()
    time.sleep(0.5)

    # Try to submit without filling anything
    create_org_section = page.locator('#create-org-section')
    submit_btn = create_org_section.locator('button[type="submit"]')
    submit_btn.click()

    # HTML5 validation should prevent submission
    # The form should still be visible
    expect(create_org_section).to_be_visible()

    # Check that we haven't navigated away
    expect(page.locator('#join-screen')).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
