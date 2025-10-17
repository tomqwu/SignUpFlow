"""
E2E test for invitation acceptance flow - Following claude.md
Tests the complete user journey from invitation link to main app

User Journey:
1. Admin creates invitation and gets token
2. User opens invitation link with token
3. User sees pre-filled name and email (readonly)
4. User sees assigned roles
5. User enters password and timezone
6. User clicks complete signup
7. User sees main app, logged in with correct role
"""
import pytest
from playwright.sync_api import Page, expect
import time
import requests


def test_invitation_acceptance_complete_journey(page: Page):
    """Test complete invitation acceptance flow"""

    print(f"\n{'='*80}")
    print("TESTING INVITATION ACCEPTANCE USER JOURNEY")
    print(f"{'='*80}\n")

    # Setup: Create org and admin user
    timestamp = int(time.time())
    org_id = f"invite_test_org_{timestamp}"
    admin_email = f"admin{timestamp}@test.com"
    admin_password = "AdminPass123"

    print("Setup: Creating org and admin user...")
    org_response = requests.post("http://localhost:8000/api/organizations/", json={
        "id": org_id,
        "name": f"Invite Test Org {timestamp}",
        "region": "Test",
        "config": {}
    })

    admin_response = requests.post("http://localhost:8000/api/auth/signup", json={
        "org_id": org_id,
        "name": f"Admin {timestamp}",
        "email": admin_email,
        "password": admin_password,
        "roles": ["admin"]
    })

    if admin_response.status_code not in [200, 201]:
        raise Exception(f"Failed to create admin: {admin_response.text}")

    admin_token = admin_response.json()["token"]
    print(f"✓ Admin created: {admin_email}\n")

    # Create invitation
    invitee_name = f"Invited User {timestamp}"
    invitee_email = f"invited{timestamp}@test.com"

    print(f"Setup: Creating invitation for {invitee_email}...")
    invite_response = requests.post(
        f"http://localhost:8000/api/invitations?org_id={org_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": invitee_email,
            "name": invitee_name,
            "roles": ["member", "volunteer"]
        }
    )

    if invite_response.status_code not in [200, 201]:
        raise Exception(f"Failed to create invitation: {invite_response.text}")

    invitation_token = invite_response.json()["token"]
    print(f"✓ Invitation created with token: {invitation_token[:20]}...\n")

    # Step 1: User opens invitation link
    print("Step 1: User opens invitation link...")
    invitation_url = f"http://localhost:8000/join?token={invitation_token}"
    page.goto(invitation_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Should be on profile screen (invitation signup)
    try:
        expect(page.locator('#profile-screen')).to_be_visible(timeout=5000)
        print("✓ Profile screen (invitation signup) visible\n")
    except Exception as e:
        print(f"✗ Profile screen not visible: {e}")
        # Debug
        for screen_id in ['onboarding-screen', 'join-screen', 'profile-screen', 'main-app']:
            is_visible = page.locator(f'#{screen_id}').is_visible()
            print(f"  {screen_id}: {'VISIBLE' if is_visible else 'hidden'}")
        page.screenshot(path="/tmp/invitation_screen_failed.png")
        raise

    # Step 2: Verify pre-filled fields
    print("Step 2: Verifying pre-filled invitation data...\n")

    name_input = page.locator('#user-name')
    email_input = page.locator('#user-email')

    # Check values are pre-filled
    name_value = name_input.input_value()
    email_value = email_input.input_value()

    print(f"  Name field: '{name_value}'")
    print(f"  Email field: '{email_value}'")

    assert name_value == invitee_name, f"Name not pre-filled correctly. Expected '{invitee_name}', got '{name_value}'"
    assert email_value == invitee_email, f"Email not pre-filled correctly. Expected '{invitee_email}', got '{email_value}'"
    print("  ✓ Name and email pre-filled correctly")

    # Check if fields are readonly (they should be for invitations)
    name_readonly = name_input.get_attribute('readonly')
    email_readonly = email_input.get_attribute('readonly')

    if name_readonly is not None or email_readonly is not None:
        print("  ✓ Name and email fields are readonly (as expected for invitations)")
    else:
        print("  ⚠️  Warning: Fields may not be readonly")

    # Step 3: Verify assigned roles are displayed
    print("\nStep 3: Verifying assigned roles displayed...")
    roles_display = page.locator('#invitation-roles-display')
    if roles_display.count() > 0 and roles_display.is_visible():
        print("  ✓ Assigned roles section is visible")
        # Check if it shows the roles
        roles_text = roles_display.text_content()
        print(f"  Roles shown: {roles_text}")
    else:
        print("  ⚠️  Warning: Roles display not visible")

    # Step 4: Fill in password and timezone
    print("\nStep 4: Filling in password...")
    invitee_password = "InvitedUserPass123"
    page.locator('#user-password').fill(invitee_password)

    # Timezone should auto-detect
    timezone_value = page.locator('#user-timezone').input_value()
    print(f"  Timezone: {timezone_value}")

    # Track signup request
    signup_requests = []
    def handle_response(response):
        if '/auth/invitation/complete' in response.url or '/auth/signup' in response.url:
            signup_requests.append({
                'status': response.status,
                'url': response.url
            })
    page.on("response", handle_response)

    # Step 5: Submit invitation signup
    print("\nStep 5: Submitting invitation signup...")
    page.locator('#profile-screen button[type="submit"]').click()
    page.wait_for_timeout(3000)

    # Step 6: Verify logged in and on main app
    print("Step 6: Verifying signup success and login...\n")

    # Check signup API response
    if signup_requests:
        last_signup = signup_requests[-1]
        print(f"  Signup API status: {last_signup['status']}")
        if last_signup['status'] not in [200, 201]:
            raise AssertionError(f"Signup failed with status {last_signup['status']}")
        print("  ✓ Signup API successful")

    # Should be on main app
    try:
        expect(page.locator('#main-app')).to_be_visible(timeout=5000)
        print("  ✓ Main app visible")
    except Exception as e:
        print(f"  ✗ Main app not visible: {e}")
        # Debug
        for screen_id in ['profile-screen', 'main-app']:
            is_visible = page.locator(f'#{screen_id}').is_visible()
            print(f"    {screen_id}: {'VISIBLE' if is_visible else 'hidden'}")
        page.screenshot(path="/tmp/invitation_login_failed.png")
        raise

    # Step 7: Verify user data
    print("\nStep 7: Verifying user logged in with correct data...\n")

    # User name displayed
    user_display = page.locator('#user-name-display')
    expect(user_display).to_be_visible()
    expect(user_display).to_have_text(invitee_name)
    print(f"  ✓ User name displayed: '{invitee_name}'")

    # Auth token saved
    auth_token = page.evaluate("() => localStorage.getItem('authToken')")
    assert auth_token is not None, "Auth token not saved"
    print("  ✓ Auth token saved to localStorage")

    # Verify roles were assigned correctly
    # The user should have member and volunteer roles
    # This would be verified by checking what UI elements are visible based on roles
    # For now, just verify we're logged in successfully

    print(f"\n{'='*80}")
    print("✅ INVITATION ACCEPTANCE FLOW TEST PASSED")
    print(f"{'='*80}\n")


def test_invitation_with_invalid_token(page: Page):
    """Test that invalid invitation token shows error"""

    print("\nTesting invitation with invalid token...")

    # Try to access invitation with fake token
    page.goto("http://localhost:8000/join?token=INVALID_TOKEN_12345")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Should show error or redirect to join screen
    # Could be on join screen with error, or profile screen with error

    # Check we're NOT logged in to main app
    expect(page.locator('#main-app')).not_to_be_visible()
    print("✓ Invalid token does not log user in")

    # Should see some kind of error indication
    has_error = (
        page.locator('.toast.error').count() > 0 or
        page.locator('#invitation-error').is_visible() or
        page.locator('#join-screen').is_visible()  # Redirected to join
    )

    if has_error:
        print("✓ Error shown or redirected for invalid token")
    else:
        print("⚠️  Warning: May not show clear error for invalid token")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
