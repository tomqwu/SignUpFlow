"""
E2E tests for Onboarding Wizard.

Tests:
- Complete 4-step wizard flow (signup → org profile → first event → first team → invite volunteers)
- Wizard resume after logout (save progress and continue later)
- Wizard back button navigation (navigate between steps)
- Wizard validation prevents empty submission (form validation)

Priority: HIGH - Critical first-time user experience

STATUS: Tests implemented but SKIPPED - Onboarding Wizard GUI not yet implemented
Backend API complete (api/routers/onboarding.py), frontend pending

Backend API Endpoints:
- GET /api/onboarding/progress - Get current user's onboarding progress
  Returns: wizard_step_completed (0-4), wizard_data (dict), checklist_state, etc.
  - wizard_step_completed: 0=not started, 1=org profile, 2=first event, 3=first team, 4=completed
  - wizard_data: Stores all wizard form data (org info, event info, team info, invitation emails)

- PUT /api/onboarding/progress - Update onboarding progress (partial updates supported)
  Body: {
    "wizard_step_completed": 0-4,  # Integer 0-4 for wizard step tracking
    "wizard_data": {
      "org_name": "Grace Community Church",
      "org_location": "Toronto, ON",
      "org_timezone": "America/Toronto",
      "event_title": "Sunday Service",
      "event_date": "2025-11-02",
      "event_time": "10:00",
      "team_name": "Greeters",
      "team_role": "greeter",
      "invitation_emails": ["vol1@example.com", "vol2@example.com"]
    }
  }
  Validation: wizard_step_completed must be 0-4

- POST /api/onboarding/skip - Skip onboarding completely
  Sets wizard_step_completed to 4 (completed) and onboarding_skipped flag

Wizard Flow (4 Steps):
Step 0: Not started (wizard_step_completed = 0)
Step 1: Organization Profile (wizard_step_completed = 1)
  - Organization name (pre-filled from signup)
  - Location (pre-filled from signup)
  - Timezone (pre-filled from signup)
  - Optionally editable

Step 2: Create First Event (wizard_step_completed = 2)
  - Event title (required)
  - Event date (required)
  - Event time (required)
  - Duration (optional, default 60 minutes)

Step 3: Create First Team (wizard_step_completed = 3)
  - Team name (required)
  - Team role (required)
  - Description (optional)

Step 4: Invite Volunteers (wizard_step_completed = 4)
  - Email addresses (newline-separated, optional)
  - Send invitation emails on completion

Wizard Features:
- Progressive disclosure: Show one step at a time
- Progress bar: Visual indicator (0%, 25%, 50%, 75%, 100%)
- Step indicator: "Step X of 4"
- Navigation: Continue, Back (disabled on Step 1), Save & Continue Later
- Validation: Required fields must be filled before proceeding
- Data persistence: All wizard_data saved to backend on each step
- Resume capability: User can log out and resume where they left off
- Skip option: "Skip Setup" button to bypass wizard
- Success screen: Shown on completion before redirect to dashboard

UI Gaps Identified:
- No onboarding wizard route in SPA router (/wizard or embedded in signup flow)
- No wizard container element (.onboarding-wizard)
- No wizard step indicator (#step-indicator)
- No wizard progress bar (#wizard-progress-bar)
- No step headings (h2 for "Organization Profile", "Create Your First Event", etc.)
- No wizard navigation buttons (#wizard-continue, #wizard-back, #wizard-save-later)
- No signup form integration with wizard trigger
- No wizard Step 1 form (#org-name, #org-location, #org-timezone)
- No wizard Step 2 form (#event-title, #event-date, #event-time, #event-duration)
- No wizard Step 3 form (#team-name, #team-role, #team-description)
- No wizard Step 4 form (#invite-emails textarea)
- No wizard success screen (.wizard-success, h1 "Setup Complete!")
- No wizard skip button (#wizard-skip, "Skip Setup")
- No form validation for required fields
- No wizard data persistence logic (save to backend on each step)
- No wizard resume logic (load wizard_step_completed and wizard_data on login)
- No automatic redirect to dashboard after wizard completion

JavaScript Functions Missing:
- window.initWizard() - Initialize wizard state and load progress from backend
- window.wizardContinue() - Validate current step and proceed to next step
- window.wizardBack() - Navigate to previous step
- window.wizardSaveLater() - Save progress and redirect to dashboard
- window.wizardSkip() - Skip wizard and mark as completed
- window.validateWizardStep() - Validate required fields for current step
- window.saveWizardProgress() - Save wizard_data and wizard_step_completed to backend
- window.loadWizardProgress() - Load wizard state from backend API
- window.updateWizardUI() - Update step indicator, progress bar, button states
- window.showWizardSuccess() - Display completion message and redirect

Signup Form Integration:
- Signup form data (org_name, org_location, org_timezone, name, email) should pre-populate wizard Step 1
- After successful signup, user should be automatically redirected to wizard Step 1
- wizard_step_completed should be initialized to 1 (org profile) after signup

Once Onboarding Wizard is implemented in frontend (frontend/index.html with embedded wizard flow,
frontend/js/onboarding-wizard.js for logic), unskip these tests.
"""

import pytest
import re
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


def test_wizard_complete_flow(page: Page, app_config: AppConfig):
    """
    Test complete 4-step wizard flow from signup to completion.
    """
    # Clear session/localStorage to ensure clean state
    page.goto(f"{app_config.app_url}/")
    page.evaluate("localStorage.clear()")
    page.evaluate("sessionStorage.clear()")
    
    # Navigate to landing page again
    page.goto(f"{app_config.app_url}/")
    page.wait_for_load_state("networkidle")

    # Verify Get Started button visible
    get_started_button = page.locator('button:has-text("Get Started →"), a:has-text("Get Started →")')
    expect(get_started_button.first).to_be_visible(timeout=5000)
    get_started_button.first.click()

    # Should navigate to join page
    page.wait_for_timeout(1000)
    join_screen = page.locator('#join-screen')
    expect(join_screen).to_be_visible(timeout=5000)

    # Click Create New Organization
    create_org_btn = page.locator('button:has-text("Create New Organization")')
    create_org_btn.click()
    
    # Fill create org form
    unique_suffix = int(page.evaluate('Date.now()'))
    org_name = f"SAMPLE - Church {unique_suffix}"
    page.locator('#new-org-name').fill(org_name)
    page.locator('#new-org-region').fill("Toronto, ON")
    
    # Use the button in create-org-section
    page.locator('#create-org-section button[type="submit"]').click()

    # Should navigate to profile screen
    page.wait_for_timeout(1000)
    profile_screen = page.locator('#profile-screen')
    expect(profile_screen).to_be_visible(timeout=5000)

    # Fill profile info
    unique_email = f"wizard.complete.{unique_suffix}@example.com"
    page.locator('#user-name').fill("Complete Test Admin")
    page.locator('#user-email').fill(unique_email)
    page.locator('#user-password').fill("TestPassword123!")
    page.locator('#user-timezone').select_option("America/Toronto")

    # Submit signup
    submit_button = page.locator('#profile-screen button[type="submit"]')
    expect(submit_button.first).to_be_visible()
    submit_button.first.click()

    # Wait for wizard to load (should redirect automatically after signup)
    page.wait_for_timeout(2000)

    # Verify wizard container visible
    wizard_container = page.locator('#wizard-screen')
    expect(wizard_container).to_be_visible(timeout=5000)

    # Step 1: Organization Profile
    step1_heading = page.locator('h2:has-text("Organization Profile"), h1:has-text("Organization")')
    expect(step1_heading).to_be_visible(timeout=3000)

    step_indicator = page.locator('#step-indicator, .step-indicator')
    expect(step_indicator).to_contain_text("Step 1 of 4")

    # Verify pre-filled data from signup
    org_name_input = page.locator('#wizard-org-name')
    org_name_value = org_name_input.input_value()
    assert str(unique_suffix) in org_name_value

    org_location_input = page.locator('#wizard-org-location')
    org_location_value = org_location_input.input_value()
    assert "Toronto" in org_location_value

    org_timezone_input = page.locator('#wizard-org-timezone')
    org_timezone_value = org_timezone_input.input_value()
    assert "America/Toronto" in org_timezone_value

    # Progress bar should show 25% (Step 1 of 4)
    progress_bar = page.locator('#wizard-progress-bar, .progress-bar')
    if progress_bar.count() > 0:
        progress_width = progress_bar.evaluate("el => el.style.width || el.getAttribute('style')")
        assert "25" in progress_width  # Should be 25%

    # Click Continue to Step 2
    continue_button = page.locator('#wizard-continue')
    expect(continue_button).to_be_visible()
    continue_button.click()

    # Step 2: Create Your First Event
    page.wait_for_timeout(1000)
    step2_heading = page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')
    expect(step2_heading).to_be_visible(timeout=3000)
    expect(step_indicator).to_contain_text("Step 2 of 4")

    # Fill event details
    page.locator('#wizard-event-title').fill("Sunday Service 10am")

    # Calculate next Sunday
    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];  // Returns YYYY-MM-DD
        }
    """)

    page.locator('#wizard-event-date').fill(next_sunday)
    page.locator('#wizard-event-time').fill("10:00")

    # Optional duration field
    duration_input = page.locator('#wizard-event-duration')
    if duration_input.count() > 0:
        duration_input.fill("60")  # 60 minutes

    # Progress bar should show 50% (Step 2 of 4)
    if progress_bar.count() > 0:
        progress_width = progress_bar.evaluate("el => el.style.width || el.getAttribute('style')")
        assert "50" in progress_width

    # Click Continue to Step 3
    continue_button.click()

    # Step 3: Create Your First Team
    page.wait_for_timeout(1000)
    step3_heading = page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')
    expect(step3_heading).to_be_visible(timeout=3000)
    expect(step_indicator).to_contain_text("Step 3 of 4")

    # Fill team details
    page.locator('#wizard-team-name').fill("Greeters")
    page.locator('#wizard-team-role').fill("greeter")

    # Optional description
    team_description = page.locator('#wizard-team-description')
    if team_description.count() > 0:
        team_description.fill("Welcome team for Sunday services")

    # Progress bar should show 75% (Step 3 of 4)
    if progress_bar.count() > 0:
        progress_width = progress_bar.evaluate("el => el.style.width || el.getAttribute('style')")
        assert "75" in progress_width

    # Back button should be visible on Step 3
    back_button = page.locator('#wizard-back')
    expect(back_button).to_be_visible()

    # Click Continue to Step 4
    continue_button.click()

    # Step 4: Invite Volunteers
    page.wait_for_timeout(1000)
    step4_heading = page.locator('h2:has-text("Invite Volunteers"), h1:has-text("Invite")')
    expect(step4_heading).to_be_visible(timeout=3000)
    expect(step_indicator).to_contain_text("Step 4 of 4")

    # Fill invitation emails (newline-separated)
    invite_emails_textarea = page.locator('#wizard-invite-emails')
    expect(invite_emails_textarea).to_be_visible()
    invite_emails_textarea.fill("volunteer1@example.com\nvolunteer2@example.com\nvolunteer3@example.com")

    # Progress bar should show 100% (Step 4 of 4)
    if progress_bar.count() > 0:
        progress_width = progress_bar.evaluate("el => el.style.width || el.getAttribute('style')")
        assert "100" in progress_width

    # Click Continue to complete wizard
    continue_button.click()

    # Wait for completion message to show (Step 5 celebration)
    page.wait_for_timeout(1000)

    # Verify success screen/message is visible
    success_msg = page.locator('#wizard-success')
    expect(success_msg).to_be_visible(timeout=5000)

    # Wait for automatic redirect to onboarding dashboard (happens after 2 seconds)
    expect(page).to_have_url(re.compile(r".*/app/onboarding-dashboard"), timeout=15000)

    # Verify the onboarding dashboard content is showing
    onboarding_view = page.locator('#onboarding-dashboard-view')
    expect(onboarding_view).to_have_class(re.compile(r".*active.*"), timeout=10000)

    welcome_heading = page.locator('#onboarding-dashboard-view .onboarding-dashboard h1')
    expect(welcome_heading).to_be_visible(timeout=10000)

    # Verify checklist container exists
    expect(page.locator('#onboarding-checklist-container')).to_be_visible(timeout=5000)


def test_wizard_resume_after_logout(page: Page, app_config: AppConfig):
    """
    Test wizard resume functionality after logging out mid-flow.

    User Journey:
    1. User signs up and starts wizard
    2. User completes Step 1 (Organization Profile)
    3. User completes Step 2 (First Event)
    4. User clicks "Save & Continue Later" on Step 3
    5. User is redirected to main app
    6. User logs out
    7. User logs back in
    8. Wizard automatically loads at Step 3 (where user left off)
    9. Previous data from Steps 1-2 is preserved
    10. User can complete remaining steps

    Backend Integration:
    - PUT /api/onboarding/progress saves wizard_data and wizard_step_completed=2 after Step 2
    - User clicks "Save & Continue Later" → PUT updates wizard_step_completed to 2 (stays at current step)
    - On logout → no backend call needed (data already saved)
    - On login → GET /api/onboarding/progress returns wizard_step_completed=2, wizard_data={...}
    - Frontend checks wizard_step_completed on login:
      * If 0-3: Redirect to wizard at that step
      * If 4: Wizard completed, redirect to dashboard normally
    - GET /api/onboarding/progress returns wizard_data with event_title, event_date, event_time saved

    Assertions:
    - Wizard resumes at correct step (Step 3)
    - Step indicator shows "Step 3 of 4"
    - Progress bar shows 75%
    - Previous data from Step 2 is preserved in wizard_data
    - User can navigate back to Step 2 and see filled data
    - User can complete wizard from Step 3 onward
    """
    # Navigate to signup
    page.goto(f"{app_config.app_url}/")
    page.wait_for_load_state("networkidle")

    # Click Get Started
    page.locator('button:has-text("Get Started")').first.click()
    page.wait_for_timeout(1000)

    # Fill signup form with unique email
    unique_email = f"wizard.resume.{int(page.evaluate('Date.now()'))}@example.com"

    page.locator('#signup-org-name, input[name="org_name"]').fill("SAMPLE - Resume Test Organization")
    page.locator('#signup-location, input[name="location"]').fill("Calgary, AB")
    page.locator('#signup-timezone, select[name="timezone"]').select_option("America/Edmonton")
    page.locator('#signup-name, input[name="name"]').fill("Resume Test User")
    page.locator('#signup-email, input[name="email"]').fill(unique_email)
    page.locator('#signup-password, input[name="password"]').fill("TestPassword123!")

    # Submit signup
    page.locator('button[type="submit"]:has-text("Create"), button:has-text("Sign Up")').first.click()
    page.wait_for_timeout(2000)

    # Verify wizard loads
    wizard_container = page.locator('.onboarding-wizard, #wizard-container')
    expect(wizard_container).to_be_visible(timeout=5000)

    # Step 1: Organization Profile - Click Continue (data already pre-filled)
    expect(page.locator('h2:has-text("Organization Profile")')).to_be_visible()
    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Step 2: Create First Event - Fill and Continue
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible(timeout=3000)

    page.locator('#event-title, input[name="event_title"]').fill("Test Event for Resume")

    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)

    page.locator('#event-date, input[name="event_date"]').fill(next_sunday)
    page.locator('#event-time, input[name="event_time"]').fill("14:00")

    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Now at Step 3 - Click "Save & Continue Later"
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')).to_be_visible(timeout=3000)

    save_later_button = page.locator('#wizard-save-later, button:has-text("Save & Continue Later")')
    expect(save_later_button).to_be_visible(timeout=5000)
    save_later_button.click()

    # Should be redirected to main app (schedule view)
    page.wait_for_timeout(2000)
    main_app = page.locator('#main-app, .app-container')
    expect(main_app).to_be_visible(timeout=5000)

    # Log out
    # Look for settings/profile menu button
    settings_button = page.locator('button:has-text("⚙️"), button:has-text("Settings"), #settings-button')
    if settings_button.count() > 0:
        settings_button.first.click()
        page.wait_for_timeout(500)

    # Find logout button (in settings modal or menu)
    logout_button = page.locator(
        'button:has-text("Logout"), '
        'button:has-text("Sign Out"), '
        'button:has-text("Log Out"), '
        'a:has-text("Logout")'
    )
    expect(logout_button.first).to_be_visible(timeout=5000)
    logout_button.first.click()

    # Should be back at onboarding/login screen
    page.wait_for_timeout(2000)
    expect(page.locator('#onboarding-screen, #login-screen')).to_be_visible(timeout=5000)

    # Log back in
    sign_in_link = page.locator('a:has-text("Sign in"), a:has-text("Sign In"), button:has-text("Sign In")')
    if sign_in_link.count() > 0:
        sign_in_link.first.click()
        page.wait_for_timeout(500)

    page.locator('#login-email, input[name="email"]').fill(unique_email)
    page.locator('#login-password, input[name="password"]').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Sign In"), button:has-text("Login")').first.click()

    # Wait for wizard to reload
    page.wait_for_timeout(2000)

    # Wizard should automatically load and resume at Step 3
    expect(wizard_container).to_be_visible(timeout=5000)
    expect(page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')).to_be_visible(timeout=3000)

    # Verify step indicator shows Step 3
    step_indicator = page.locator('#step-indicator, .step-indicator')
    expect(step_indicator).to_contain_text("Step 3 of 4")

    # Verify progress bar shows 75%
    progress_bar = page.locator('#wizard-progress-bar, .progress-bar')
    if progress_bar.count() > 0:
        progress_width = progress_bar.evaluate("el => el.style.width || el.getAttribute('style')")
        assert "75" in progress_width  # Should be 75% (Step 3 of 4)

    # Verify Back button works - navigate back to Step 2
    back_button = page.locator('#wizard-back, button:has-text("Back")')
    expect(back_button).to_be_visible()
    back_button.click()

    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible(timeout=3000)

    # Verify previous data is still filled
    event_title_value = page.locator('#event-title, input[name="event_title"]').input_value()
    assert event_title_value == "Test Event for Resume"

    event_time_value = page.locator('#event-time, input[name="event_time"]').input_value()
    assert event_time_value == "14:00"


def test_wizard_back_button_navigation(page: Page, app_config: AppConfig):
    """
    Test wizard back button allows navigation to previous steps.

    User Journey:
    1. User signs up and starts wizard
    2. User completes Step 1 → Step 2
    3. User completes Step 2 → Step 3
    4. User clicks Back button on Step 3
    5. User is taken back to Step 2
    6. User's previously entered data is still filled in
    7. User can edit data and continue forward again
    8. User can navigate back and forth between steps
    9. Back button is disabled on Step 1

    Backend Integration:
    - PUT /api/onboarding/progress saves wizard_data after each step
    - Back button does NOT call backend (data already saved)
    - Frontend maintains wizard_data in memory during navigation
    - Only Continue button triggers backend save
    - wizard_step_completed is updated only when moving forward, not backward

    Assertions:
    - Back button visible on Steps 2-4, hidden/disabled on Step 1
    - Clicking Back navigates to previous step (UI update only, no backend call)
    - Step indicator and progress bar update correctly
    - Previous data is preserved in form fields
    - User can edit previous data and continue forward
    - Continue button re-saves updated data to backend
    """
    # Navigate to signup
    page.goto(f"{app_config.app_url}/")
    page.wait_for_load_state("networkidle")

    # Quick signup
    page.locator('button:has-text("Get Started")').first.click()
    page.wait_for_timeout(1000)

    unique_email = f"wizard.back.{int(page.evaluate('Date.now()'))}@example.com"

    page.locator('#signup-org-name, input[name="org_name"]').fill("SAMPLE - Back Nav Test Org")
    page.locator('#signup-location, input[name="location"]').fill("Vancouver, BC")
    page.locator('#signup-timezone, select[name="timezone"]').select_option("America/Vancouver")
    page.locator('#signup-name, input[name="name"]').fill("Back Nav User")
    page.locator('#signup-email, input[name="email"]').fill(unique_email)
    page.locator('#signup-password, input[name="password"]').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Create")').first.click()

    # Wait for wizard
    page.wait_for_timeout(2000)
    wizard_container = page.locator('.onboarding-wizard, #wizard-container')
    expect(wizard_container).to_be_visible(timeout=5000)

    # Step 1: Verify Back button is hidden or disabled
    expect(page.locator('h2:has-text("Organization Profile")')).to_be_visible()

    back_button = page.locator('#wizard-back, button:has-text("Back")')
    # Back button should either not exist or be disabled on Step 1
    if back_button.count() > 0:
        is_disabled = back_button.is_disabled()
        assert is_disabled, "Back button should be disabled on Step 1"

    # Step 1 → Continue to Step 2
    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Step 2: Fill event details
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible(timeout=3000)

    page.locator('#event-title, input[name="event_title"]').fill("Back Nav Test Event")

    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)

    page.locator('#event-date, input[name="event_date"]').fill(next_sunday)
    page.locator('#event-time, input[name="event_time"]').fill("11:00")

    # Verify Back button is now visible on Step 2
    expect(back_button).to_be_visible()
    expect(back_button).to_be_enabled()

    # Step 2 → Continue to Step 3
    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Step 3: Verify we're on Step 3
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')).to_be_visible(timeout=3000)

    step_indicator = page.locator('#step-indicator, .step-indicator')
    expect(step_indicator).to_contain_text("Step 3 of 4")

    # Verify Back button visible
    expect(back_button).to_be_visible()

    # Click Back to return to Step 2
    back_button.click()

    # Should be back at Step 2
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible(timeout=3000)
    expect(step_indicator).to_contain_text("Step 2 of 4")

    # Verify previous data is still filled
    event_title_value = page.locator('#event-title, input[name="event_title"]').input_value()
    assert event_title_value == "Back Nav Test Event"

    event_time_value = page.locator('#event-time, input[name="event_time"]').input_value()
    assert event_time_value == "11:00"

    # Edit data and continue forward again
    page.locator('#event-title, input[name="event_title"]').fill("Edited Event Title")
    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Should be back at Step 3
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')).to_be_visible(timeout=3000)

    # Navigate back to Step 2 again to verify edited data was saved
    back_button.click()
    page.wait_for_timeout(1000)

    event_title_value = page.locator('#event-title, input[name="event_title"]').input_value()
    assert event_title_value == "Edited Event Title"


def test_wizard_validation_prevents_empty_submission(page: Page, app_config: AppConfig):
    """
    Test wizard validation prevents proceeding with empty required fields.

    User Journey:
    1. User signs up and starts wizard
    2. User completes Step 1 → Step 2
    3. User leaves required fields empty on Step 2
    4. User clicks Continue
    5. Validation error appears (alert or inline error message)
    6. Wizard does NOT proceed to Step 3
    7. User fills required fields
    8. User clicks Continue
    9. Wizard proceeds to Step 3 successfully

    Backend Integration:
    - Frontend validation prevents Continue button from calling backend if fields empty
    - window.validateWizardStep() checks required fields:
      * Step 1: org_name, org_location, org_timezone (should be pre-filled)
      * Step 2: event_title, event_date, event_time (required)
      * Step 3: team_name, team_role (required)
      * Step 4: No required fields (invitation emails optional)
    - If validation passes → PUT /api/onboarding/progress
    - If validation fails → Show error message, stay on current step
    - Backend also validates (422 Unprocessable Entity if invalid data)

    Assertions:
    - Continue button disabled if required fields empty (optional)
    - OR clicking Continue shows validation error
    - Error message displays (alert dialog or inline .error-message)
    - Wizard remains on same step (step indicator unchanged)
    - Filling required fields clears error
    - Continue button enabled after filling fields
    - Wizard proceeds to next step after validation passes
    """
    # Navigate to signup
    page.goto(f"{app_config.app_url}/")
    page.wait_for_load_state("networkidle")

    # Quick signup
    page.locator('button:has-text("Get Started")').first.click()
    page.wait_for_timeout(1000)

    unique_email = f"wizard.validation.{int(page.evaluate('Date.now()'))}@example.com"

    page.locator('#signup-org-name, input[name="org_name"]').fill("SAMPLE - Validation Test Org")
    page.locator('#signup-location, input[name="location"]').fill("Montreal, QC")
    page.locator('#signup-timezone, select[name="timezone"]').select_option("America/Montreal")
    page.locator('#signup-name, input[name="name"]').fill("Validation Test User")
    page.locator('#signup-email, input[name="email"]').fill(unique_email)
    page.locator('#signup-password, input[name="password"]').fill("TestPassword123!")
    page.locator('button[type="submit"]:has-text("Create")').first.click()

    # Wait for wizard
    page.wait_for_timeout(2000)
    wizard_container = page.locator('.onboarding-wizard, #wizard-container')
    expect(wizard_container).to_be_visible(timeout=5000)

    # Step 1: Continue (org data pre-filled, should pass)
    expect(page.locator('h2:has-text("Organization Profile")')).to_be_visible()
    page.locator('#wizard-continue, button:has-text("Continue")').click()

    # Step 2: Try to continue with empty required fields
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible(timeout=3000)

    step_indicator = page.locator('#step-indicator, .step-indicator')
    expect(step_indicator).to_contain_text("Step 2 of 4")

    # Ensure fields are empty (clear any pre-filled data)
    event_title_input = page.locator('#event-title, input[name="event_title"]')
    event_title_input.fill("")

    event_date_input = page.locator('#event-date, input[name="event_date"]')
    event_date_input.fill("")

    event_time_input = page.locator('#event-time, input[name="event_time"]')
    event_time_input.fill("")

    # Click Continue with empty fields
    continue_button = page.locator('#wizard-continue, button:has-text("Continue")')
    continue_button.click()

    # Wait for validation error
    page.wait_for_timeout(500)

    # Check for error message (could be alert dialog or inline error)
    # Option 1: Alert dialog
    # (Playwright auto-dismisses alerts, but we can check if one appeared)

    # Option 2: Inline error message
    error_message = page.locator('.error-message, .validation-error, [role="alert"]')
    if error_message.count() > 0:
        expect(error_message.first).to_be_visible()

    # Verify wizard is still on Step 2 (did not proceed)
    expect(page.locator('h2:has-text("Create Your First Event"), h1:has-text("First Event")')).to_be_visible()
    expect(step_indicator).to_contain_text("Step 2 of 4")

    # Now fill required fields correctly
    event_title_input.fill("Valid Event Title")

    next_sunday = page.evaluate("""
        () => {
            const today = new Date();
            const daysUntilSunday = (7 - today.getDay()) % 7 || 7;
            const nextSunday = new Date(today.getTime() + daysUntilSunday * 24 * 60 * 60 * 1000);
            return nextSunday.toISOString().split('T')[0];
        }
    """)

    event_date_input.fill(next_sunday)
    event_time_input.fill("10:00")

    # Click Continue again
    continue_button.click()

    # Should now proceed to Step 3
    page.wait_for_timeout(1000)
    expect(page.locator('h2:has-text("Create Your First Team"), h1:has-text("First Team")')).to_be_visible(timeout=3000)
    expect(step_indicator).to_contain_text("Step 3 of 4")
