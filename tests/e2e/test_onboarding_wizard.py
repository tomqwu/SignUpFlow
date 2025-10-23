"""
E2E tests for onboarding wizard functionality.

Tests the complete 4-step wizard flow:
- Step 1: Organization Profile
- Step 2: First Event
- Step 3: First Team
- Step 4: Invite Volunteers
"""

import pytest
from playwright.sync_api import Page, expect


def test_wizard_complete_flow(page: Page):
    """
    Test complete wizard flow from start to finish.

    Scenario:
      Given a new user signs up
      When they complete all 4 wizard steps
      Then they should see the success message
      And be redirected to onboarding dashboard
      And wizard progress should be saved as completed
    """
    # Navigate to signup
    page.goto("http://localhost:8000/")
    page.locator('button:has-text("Get Started")').click()

    # Fill signup form
    page.locator('#signup-org-name').fill("SAMPLE - Test Church")
    page.locator('#signup-location').fill("Test City, ST")
    page.locator('#signup-timezone').select_option("America/New_York")
    page.locator('#signup-name').fill("Test Admin")
    page.locator('#signup-email').fill(f"wizard.test.{int(page.evaluate('Date.now()'))}@example.com")
    page.locator('#signup-password').fill("TestPassword123!")
    page.locator('#signup-confirm-password').fill("TestPassword123!")

    # Submit signup
    page.locator('button[type="submit"]:has-text("Create")').click()

    # Wait for wizard to load
    expect(page.locator('.onboarding-wizard')).to_be_visible(timeout=5000)

    # Verify Step 1 visible
    expect(page.locator('h2:has-text("Organization Profile")')).to_be_visible()
    expect(page.locator('#step-indicator')).to_contain_text("Step 1 of 4")

    # Step 1: Organization Profile (already filled from signup)
    # Organization name should be pre-filled
    org_name_value = page.locator('#org-name').input_value()
    assert org_name_value == "SAMPLE - Test Church"

    # Location should be pre-filled
    org_location_value = page.locator('#org-location').input_value()
    assert org_location_value == "Test City, ST"

    # Timezone should be pre-filled
    org_timezone_value = page.locator('#org-timezone').input_value()
    assert org_timezone_value == "America/New_York"

    # Click Continue to Step 2
    page.locator('#wizard-continue').click()

    # Wait for Step 2
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible(timeout=3000)
    expect(page.locator('#step-indicator')).to_contain_text("Step 2 of 4")

    # Step 2: First Event
    page.locator('#event-title').fill("Sunday Service 10am")

    # Set date to next Sunday
    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)
    page.locator('#event-date').fill(next_sunday)
    page.locator('#event-time').fill("10:00")

    # Click Continue to Step 3
    page.locator('#wizard-continue').click()

    # Wait for Step 3
    expect(page.locator('h2:has-text("Create Your First Team")')).to_be_visible(timeout=3000)
    expect(page.locator('#step-indicator')).to_contain_text("Step 3 of 4")

    # Step 3: First Team
    page.locator('#team-name').fill("Greeters")
    page.locator('#team-role').fill("greeter")

    # Click Continue to Step 4
    page.locator('#wizard-continue').click()

    # Wait for Step 4
    expect(page.locator('h2:has-text("Invite Volunteers")')).to_be_visible(timeout=3000)
    expect(page.locator('#step-indicator')).to_contain_text("Step 4 of 4")

    # Step 4: Invite Volunteers
    page.locator('#invite-emails').fill("volunteer1@example.com\nvolunteer2@example.com\nvolunteer3@example.com")

    # Click Continue to complete wizard
    page.locator('#wizard-continue').click()

    # Wait for success message
    expect(page.locator('.wizard-success')).to_be_visible(timeout=3000)
    expect(page.locator('h1:has-text("Setup Complete!")')).to_be_visible()

    # Wait for redirect to onboarding dashboard
    expect(page.locator('#onboarding-dashboard')).to_be_visible(timeout=5000)
    expect(page.locator('h1:has-text("Welcome to SignUpFlow")')).to_be_visible()


def test_wizard_resume_after_logout(page: Page):
    """
    Test wizard resume after logging out mid-flow.

    Scenario:
      Given a user completes Step 1 and Step 2 of wizard
      When they save and log out
      And log back in
      Then wizard should resume at Step 3
      And previous data should be preserved
    """
    # Navigate to signup
    page.goto("http://localhost:8000/")
    page.locator('button:has-text("Get Started")').click()

    # Fill signup form
    unique_email = f"wizard.resume.{int(page.evaluate('Date.now()'))}@example.com"
    page.locator('#signup-org-name').fill("SAMPLE - Resume Test Org")
    page.locator('#signup-location').fill("Resume City, ST")
    page.locator('#signup-timezone').select_option("America/Chicago")
    page.locator('#signup-name').fill("Resume Test User")
    page.locator('#signup-email').fill(unique_email)
    page.locator('#signup-password').fill("TestPassword123!")
    page.locator('#signup-confirm-password').fill("TestPassword123!")

    # Submit signup
    page.locator('button[type="submit"]:has-text("Create")').click()

    # Wait for wizard
    expect(page.locator('.onboarding-wizard')).to_be_visible(timeout=5000)

    # Complete Step 1
    expect(page.locator('h2:has-text("Organization Profile")')).to_be_visible()
    page.locator('#wizard-continue').click()

    # Complete Step 2
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible(timeout=3000)
    page.locator('#event-title').fill("Test Event for Resume")
    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)
    page.locator('#event-date').fill(next_sunday)
    page.locator('#event-time').fill("14:00")
    page.locator('#wizard-continue').click()

    # Now at Step 3 - click "Save & Continue Later"
    expect(page.locator('h2:has-text("Create Your First Team")')).to_be_visible(timeout=3000)
    page.locator('#wizard-save-later').click()

    # Should be redirected to dashboard
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)

    # Log out
    page.locator('button:has-text("⚙️")').click()  # Settings button
    page.wait_for_timeout(500)
    # Find logout button (might be in settings modal or menu)
    page.locator('button:has-text("Logout")').or_(page.locator('button:has-text("Sign Out")')).first.click()

    # Should be back at onboarding screen
    expect(page.locator('#onboarding-screen')).to_be_visible(timeout=3000)

    # Log back in
    page.locator('a:has-text("Sign in")').click()
    page.locator('#login-email').fill(unique_email)
    page.locator('#login-password').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Sign In")').click()

    # Wait for wizard to load
    expect(page.locator('.onboarding-wizard')).to_be_visible(timeout=5000)

    # Should resume at Step 3
    expect(page.locator('h2:has-text("Create Your First Team")')).to_be_visible(timeout=3000)
    expect(page.locator('#step-indicator')).to_contain_text("Step 3 of 4")

    # Progress bar should show 75% (step 3 of 4)
    progress_bar_width = page.locator('#wizard-progress-bar').evaluate("el => el.style.width")
    assert "75" in progress_bar_width  # Should be 75%


def test_wizard_back_button_navigation(page: Page):
    """
    Test wizard back button allows navigation to previous steps.

    Scenario:
      Given user is on Step 3 of wizard
      When they click Back button
      Then they should navigate to Step 2
      And previous data should still be filled
    """
    # Navigate to signup
    page.goto("http://localhost:8000/")
    page.locator('button:has-text("Get Started")').click()

    # Quick signup
    page.locator('#signup-org-name').fill("SAMPLE - Back Test Org")
    page.locator('#signup-location').fill("Test City, ST")
    page.locator('#signup-timezone').select_option("America/New_York")
    page.locator('#signup-name').fill("Back Test User")
    page.locator('#signup-email').fill(f"wizard.back.{int(page.evaluate('Date.now()'))}@example.com")
    page.locator('#signup-password').fill("TestPassword123!")
    page.locator('#signup-confirm-password').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Create")').click()

    # Wait for wizard
    expect(page.locator('.onboarding-wizard')).to_be_visible(timeout=5000)

    # Step 1 -> Continue
    page.locator('#wizard-continue').click()

    # Step 2 -> Fill and Continue
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible(timeout=3000)
    page.locator('#event-title').fill("Back Test Event")
    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)
    page.locator('#event-date').fill(next_sunday)
    page.locator('#event-time').fill("11:00")
    page.locator('#wizard-continue').click()

    # Now at Step 3
    expect(page.locator('h2:has-text("Create Your First Team")')).to_be_visible(timeout=3000)

    # Back button should be visible
    expect(page.locator('#wizard-back')).to_be_visible()

    # Click Back
    page.locator('#wizard-back').click()

    # Should be at Step 2
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible(timeout=3000)
    expect(page.locator('#step-indicator')).to_contain_text("Step 2 of 4")

    # Previous data should still be filled
    event_title_value = page.locator('#event-title').input_value()
    assert event_title_value == "Back Test Event"


def test_wizard_validation_prevents_empty_submission(page: Page):
    """
    Test wizard validation prevents proceeding with empty required fields.

    Scenario:
      Given user is on Step 2 with empty required fields
      When they click Continue
      Then validation error should appear
      And wizard should not proceed to next step
    """
    # Navigate to signup
    page.goto("http://localhost:8000/")
    page.locator('button:has-text("Get Started")').click()

    # Quick signup
    page.locator('#signup-org-name').fill("SAMPLE - Validation Test Org")
    page.locator('#signup-location').fill("Test City, ST")
    page.locator('#signup-timezone').select_option("America/New_York")
    page.locator('#signup-name').fill("Validation Test User")
    page.locator('#signup-email').fill(f"wizard.validation.{int(page.evaluate('Date.now()'))}@example.com")
    page.locator('#signup-password').fill("TestPassword123!")
    page.locator('#signup-confirm-password').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Create")').click()

    # Wait for wizard
    expect(page.locator('.onboarding-wizard')).to_be_visible(timeout=5000)

    # Step 1 -> Continue
    page.locator('#wizard-continue').click()

    # Step 2 -> Don't fill any fields, try to continue
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible(timeout=3000)

    # Click Continue with empty fields
    page.locator('#wizard-continue').click()

    # Should show alert (validation error)
    page.wait_for_timeout(500)

    # Should still be on Step 2
    expect(page.locator('h2:has-text("Create Your First Event")')).to_be_visible()
    expect(page.locator('#step-indicator')).to_contain_text("Step 2 of 4")
