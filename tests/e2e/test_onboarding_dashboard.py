"""
E2E tests for Onboarding Dashboard.

Tests:
- Onboarding dashboard displays with all components
- Checklist widget interaction and progress tracking
- Video grid displays and playback modal
- Sample data generation controls
- Feature unlock progression system
- Tutorial overlay system (Intro.js integration)
- Complete onboarding system integration

Priority: MEDIUM - First-time user experience and guided setup

STATUS: Tests implemented but SKIPPED - Onboarding Dashboard GUI not yet implemented
Backend API complete (api/routers/onboarding.py), frontend pending

Backend API Endpoints:
- GET /api/onboarding/progress - Get current user's onboarding progress
  Returns: wizard_step_completed (0-4), wizard_data, checklist_state, tutorials_completed,
           features_unlocked, videos_watched, onboarding_skipped, checklist_dismissed, tutorials_dismissed
  Default: Creates initial progress record with all fields initialized to default values

- PUT /api/onboarding/progress - Update onboarding progress (partial updates supported)
  Fields: wizard_step_completed (0-4), wizard_data (dict), checklist_state (dict),
          tutorials_completed (list), features_unlocked (list), videos_watched (list),
          onboarding_skipped (bool), checklist_dismissed (bool), tutorials_dismissed (bool)
  Validation: wizard_step_completed must be 0-4

- POST /api/onboarding/skip - Skip onboarding completely
  Sets wizard_step_completed to 4 (completed) and onboarding_skipped flag to true

- POST /api/onboarding/reset - Reset onboarding progress for re-enabling
  Clears all progress and allows user to go through onboarding again

- POST /api/onboarding/sample-data/generate - Generate sample data (admin only, query param org_id)
  Creates: 5 sample events, 3 sample teams, 10 sample volunteers
  All data prefixed with "SAMPLE - " for easy identification
  Returns: created IDs for all generated entities
  Error: 409 Conflict if sample data already exists

- DELETE /api/onboarding/sample-data - Remove all sample data (admin only, query param org_id)
  Deletes all entities prefixed with "SAMPLE - "
  Returns: counts of deleted entities by type

- GET /api/onboarding/sample-data/status - Get sample data status (query param org_id)
  Returns: has_sample_data flag and summary of existing sample data counts

OnboardingProgress Model Fields:
- wizard_step_completed: Integer 0-4 (0=not started, 4=completed)
- wizard_data: Free-form dict from wizard (org, event, team, invitations data)
- checklist_state: Dict of checklist items {"complete_profile": True, "add_first_event": False, ...}
- tutorials_completed: List of completed tutorial IDs ["getting_started", "creating_events", ...]
- features_unlocked: List of unlocked feature IDs ["advanced_scheduling", "team_management", ...]
- videos_watched: List of watched video IDs ["getting_started", "event_creation", ...]
- onboarding_skipped: Boolean flag for users who skipped onboarding
- checklist_dismissed: Boolean flag for users who dismissed checklist widget
- tutorials_dismissed: Boolean flag for users who dismissed all tutorials

Checklist Items (6 total):
1. complete_profile - Complete user profile
2. add_first_event - Create first event
3. invite_volunteers - Invite first volunteer
4. create_team - Create first team
5. set_availability - Set availability preferences
6. generate_schedule - Run solver to generate first schedule

Sample Data Generation:
- 5 sample events with "SAMPLE - " prefix
- 3 sample teams with "SAMPLE - " prefix
- 10 sample volunteers with "SAMPLE - " prefix
- All deletable with single cleanup endpoint
- Prevents duplicate generation (409 Conflict)

Quick Start Videos (4 total):
1. getting_started - Introduction to SignUpFlow
2. event_creation - How to create and manage events
3. volunteer_management - Managing volunteers and teams
4. scheduling_automation - Using the AI solver

Tutorial Overlays:
- Powered by Intro.js library
- Guided step-by-step tours for each feature
- Can be triggered manually or auto-trigger on first use
- window.startTutorial(), window.dismissTutorial(), window.showTutorialList()

Feature Unlocking:
- Progressive feature disclosure based on usage milestones
- Unlocks based on: event count, volunteer count, schedule generation, etc.
- window.checkUnlockConditions() validates and unlocks features

UI Gaps Identified:
- No Onboarding Dashboard route in SPA router (/app/onboarding-dashboard)
- No onboarding dashboard container (#onboarding-dashboard, .onboarding-dashboard)
- No checklist widget component (.onboarding-checklist)
- No checklist item elements (.checklist-item)
- No checklist item action buttons (.item-action)
- No video grid container (#dashboard-video-grid)
- No video card elements (.video-card)
- No video thumbnail elements (.video-thumbnail)
- No video playback modal (.video-modal)
- No video player element (#video-player)
- No sample data controls container (#dashboard-sample-data-controls)
- No "Generate Sample Data" button
- No "Clean Up Sample Data" button
- No sample data status display
- No Intro.js library integration in frontend
- No tutorial overlay system (window.startTutorial, window.triggerTutorialIfFirstUse, etc.)
- No feature unlock notification system
- No feature unlock modal or banner
- No onboarding dashboard navigation in main menu
- No wizard_step_completed tracking in frontend
- No checklist state synchronization with backend
- No videos_watched tracking
- No features_unlocked display in UI

JavaScript Functions Missing:
- window.renderChecklist() - Render checklist widget
- window.updateChecklistItem() - Update checklist item state
- window.playVideo() - Open video playback modal
- window.markVideoWatched() - Mark video as watched
- window.startTutorial() - Start guided tutorial
- window.triggerTutorialIfFirstUse() - Auto-trigger tutorial for new users
- window.dismissTutorial() - Dismiss tutorial overlay
- window.showTutorialList() - Show list of available tutorials
- window.checkUnlockConditions() - Check and unlock features based on milestones
- window.renderSampleDataControls() - Render sample data generation controls

Once Onboarding Dashboard is implemented in frontend (frontend/index.html, frontend/js/onboarding-dashboard.js,
and Intro.js library integrated), unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def admin_login(page: Page, app_config: AppConfig):
    """Login as admin for onboarding dashboard tests."""
    page.goto(f"{app_config.app_url}/login")
    page.wait_for_load_state("networkidle")

    # Verify login screen is visible
    expect(page.locator("#login-screen")).to_be_visible(timeout=5000)

    # Fill login form with admin credentials
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")

    # Submit login
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Verify logged in successfully
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    return page


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_onboarding_dashboard_displays(admin_login: Page, app_config: AppConfig):
    """
    Test that onboarding dashboard displays with all components.

    User Journey:
    1. Admin is logged in
    2. Admin navigates to onboarding dashboard
    3. Admin sees checklist widget with 6 items
    4. Admin sees video grid with 4 videos
    5. Admin sees sample data generation controls
    6. All components render without errors

    Backend Integration:
    - Frontend should call GET /api/onboarding/progress to load user's onboarding state
    - Frontend should display checklist items based on checklist_state
    - Frontend should display videos and mark watched videos based on videos_watched
    """
    page = admin_login

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)  # Let dashboard initialize

    # Verify onboarding dashboard container is visible
    onboarding_dashboard = page.locator('#onboarding-dashboard, .onboarding-dashboard')
    expect(onboarding_dashboard).to_be_visible(timeout=5000)

    # Verify checklist widget displays
    checklist_widget = page.locator('.onboarding-checklist')
    expect(checklist_widget).to_be_visible()

    # Verify checklist title
    checklist_title = page.locator('h3[data-i18n="onboarding.checklist.title"]')
    expect(checklist_title).to_be_visible()

    # Verify 6 checklist items are present
    checklist_items = page.locator('.checklist-item')
    expect(checklist_items).to_have_count(6)

    # Verify video grid displays
    video_grid = page.locator('#dashboard-video-grid, .video-grid')
    expect(video_grid).to_be_visible()

    # Verify 4 video cards are present
    video_cards = page.locator('.video-card')
    expect(video_cards).to_have_count(4)

    # Verify sample data controls display
    sample_data_controls = page.locator('#dashboard-sample-data-controls, .sample-data-controls')
    expect(sample_data_controls).to_be_visible()

    # Verify "Generate Sample Data" button
    generate_button = page.locator('button:has-text("Generate Sample Data"), button[data-i18n="onboarding.sample_data.generate"]')
    expect(generate_button.first).to_be_visible()


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_checklist_widget_interaction(admin_login: Page, app_config: AppConfig):
    """
    Test checklist widget tracks completion state and enables navigation.

    User Journey:
    1. Admin navigates to onboarding dashboard
    2. Admin sees checklist with 6 items (all incomplete initially)
    3. Admin clicks "Start" button on first checklist item
    4. Admin is redirected to appropriate page (e.g., profile page)
    5. After completing action, checklist item is marked as complete
    6. Admin returns to dashboard and sees updated checklist state

    Backend Integration:
    - Frontend calls GET /api/onboarding/progress to load checklist_state
    - When user clicks "Start", frontend navigates to appropriate page
    - When user completes action, frontend calls PUT /api/onboarding/progress
      with updated checklist_state: {"complete_profile": true, ...}
    - Backend saves updated checklist_state and returns updated progress
    """
    page = admin_login

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Verify 6 checklist items
    checklist_items = page.locator('.checklist-item')
    expect(checklist_items).to_have_count(6)

    # Verify first item has action button (e.g., "Start", "Go to", "View")
    first_item = checklist_items.first
    first_item_button = first_item.locator('.item-action, button')
    expect(first_item_button).to_be_visible()

    # Get button text to verify it says "Start" or similar action word
    button_text = first_item_button.inner_text()
    assert any(word in button_text for word in ["Start", "View", "Go", "Create"]), \
        f"Expected action button text to contain action word, got: {button_text}"

    # Verify checklist items have distinct IDs or data attributes
    first_item_id = first_item.get_attribute('data-checklist-item') or \
                    first_item.get_attribute('id')
    assert first_item_id, "Checklist items should have data-checklist-item or id attribute"

    # Expected checklist item IDs (based on backend schema)
    expected_items = [
        "complete_profile",
        "add_first_event",
        "invite_volunteers",
        "create_team",
        "set_availability",
        "generate_schedule"
    ]

    # Verify all expected items exist
    for item_id in expected_items:
        item = page.locator(f'[data-checklist-item="{item_id}"], #{item_id}')
        expect(item).to_be_visible()


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_video_grid_playback(admin_login: Page, app_config: AppConfig):
    """
    Test video grid displays and video playback modal opens correctly.

    User Journey:
    1. Admin navigates to onboarding dashboard
    2. Admin sees 4 quick start videos in grid
    3. Admin clicks on video thumbnail
    4. Video playback modal opens with video player
    5. Video starts playing (or ready to play)
    6. Admin closes modal
    7. Video is marked as watched in backend

    Backend Integration:
    - Frontend calls GET /api/onboarding/progress to get videos_watched list
    - Videos in videos_watched list show "Watched" badge or checkmark
    - When user plays video, frontend calls PUT /api/onboarding/progress
      with updated videos_watched: ["getting_started", ...]
    """
    page = admin_login

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Verify 4 video cards
    video_cards = page.locator('.video-card')
    expect(video_cards).to_have_count(4)

    # Verify first video has data-video-id attribute
    first_video = video_cards.first
    video_id = first_video.get_attribute('data-video-id')
    assert video_id in ["getting_started", "event_creation", "volunteer_management", "scheduling_automation"], \
        f"Video should have valid data-video-id, got: {video_id}"

    # Verify video thumbnail is visible and clickable
    first_thumbnail = first_video.locator('.video-thumbnail, img, .play-button')
    expect(first_thumbnail).to_be_visible()

    # Click video thumbnail to open modal
    first_thumbnail.click()
    page.wait_for_timeout(500)  # Wait for modal animation

    # Verify video playback modal opens
    video_modal = page.locator('.video-modal, #video-modal, [role="dialog"]')
    expect(video_modal).to_be_visible()

    # Verify video player element exists
    video_player = page.locator('#video-player, video, iframe')
    expect(video_player).to_be_visible()

    # Verify modal has close button
    close_button = video_modal.locator('button:has-text("Close"), button[aria-label="Close"], .close-button')
    expect(close_button.first).to_be_visible()


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_sample_data_generation(admin_login: Page, app_config: AppConfig):
    """
    Test sample data generation controls work correctly.

    User Journey:
    1. Admin navigates to onboarding dashboard
    2. Admin sees "Generate Sample Data" button
    3. Admin clicks button
    4. Backend API is called to generate sample data
    5. Success message is displayed
    6. Sample data is created (5 events, 3 teams, 10 volunteers)
    7. Admin can see SAMPLE badges on generated entities
    8. Admin can clean up sample data with "Clean Up" button

    Backend Integration:
    - Frontend calls GET /api/onboarding/sample-data/status?org_id={org_id} to check if sample data exists
    - If exists, show "Clean Up Sample Data" button instead of "Generate"
    - On Generate click: POST /api/onboarding/sample-data/generate?org_id={org_id}
    - On Clean Up click: DELETE /api/onboarding/sample-data?org_id={org_id}
    - Backend returns created/deleted IDs in response
    """
    page = admin_login

    # Get current org_id from localStorage
    org_id = page.evaluate("JSON.parse(localStorage.getItem('currentOrg')).id")

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Verify sample data controls are visible
    sample_data_controls = page.locator('#dashboard-sample-data-controls, .sample-data-controls')
    expect(sample_data_controls).to_be_visible()

    # Verify "Generate Sample Data" button (or "Clean Up" if sample data exists)
    generate_button = page.locator(
        'button:has-text("Generate Sample Data"), '
        'button[data-i18n="onboarding.sample_data.generate"]'
    )

    cleanup_button = page.locator(
        'button:has-text("Clean Up Sample Data"), '
        'button:has-text("Remove Sample Data"), '
        'button[data-i18n="onboarding.sample_data.cleanup"]'
    )

    # Either generate or cleanup button should be visible (not both)
    assert generate_button.count() > 0 or cleanup_button.count() > 0, \
        "Should have either Generate or Clean Up button visible"

    # If "Generate" button is visible, click it
    if generate_button.count() > 0:
        expect(generate_button.first).to_be_visible()
        generate_button.first.click()

        # Wait for API call to complete
        page.wait_for_timeout(3000)

        # Verify success message appears
        success_message = page.locator(
            'text=/Sample data generated successfully/i, '
            '.success-message, .toast-success'
        )
        expect(success_message.first).to_be_visible(timeout=5000)

        # Navigate to admin console to verify sample data was created
        page.goto(f"{app_config.app_url}/app/admin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Look for SAMPLE badges or prefixes in data
        # (This verification depends on how sample data is displayed in admin console)
        sample_indicators = page.locator('text=/SAMPLE/i, .sample-badge')
        # Should have multiple sample indicators (events, teams, volunteers)
        assert sample_indicators.count() >= 3, \
            "Should see multiple SAMPLE indicators in admin console"


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_feature_unlock_progression(admin_login: Page, app_config: AppConfig):
    """
    Test that features unlock based on usage milestones.

    User Journey:
    1. Admin is on onboarding dashboard
    2. Admin completes actions that trigger feature unlocks
       - Create 3 events → Unlocks "Advanced Scheduling"
       - Add 5 volunteers → Unlocks "Team Management"
       - Run solver once → Unlocks "Constraint Editor"
    3. Feature unlock notification appears
    4. Feature becomes visible/enabled in UI
    5. Unlocked features are persisted to backend

    Backend Integration:
    - Frontend calls window.checkUnlockConditions() after each milestone action
    - window.checkUnlockConditions() checks:
      - Event count, volunteer count, solver runs, etc.
    - If milestone reached, frontend calls PUT /api/onboarding/progress
      with updated features_unlocked: ["advanced_scheduling", ...]
    - Backend saves features_unlocked list
    - On next load, GET /api/onboarding/progress returns features_unlocked
    - Frontend enables features based on this list

    Note: This is a simplified test. Full feature unlock requires
    meeting specific conditions (3 events, 5 volunteers, etc.)
    For this test, we just verify the unlock system is loaded and functional.
    """
    page = admin_login

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Verify feature unlock system is loaded (JavaScript function exists)
    unlock_system_loaded = page.evaluate(
        "typeof window.checkUnlockConditions === 'function'"
    )
    assert unlock_system_loaded, "Feature unlock system (window.checkUnlockConditions) not loaded"

    # Verify unlock notification container exists
    unlock_notification = page.locator(
        '.feature-unlock-notification, '
        '#feature-unlock-modal, '
        '[role="alert"][data-type="feature-unlock"]'
    )
    # Container should exist (even if hidden initially)
    assert unlock_notification.count() > 0, "Feature unlock notification container should exist"

    # Verify that feature unlock data structure is initialized
    features_unlocked = page.evaluate("""
        (async () => {
            // Try to get onboarding progress from API
            try {
                const authToken = localStorage.getItem('authToken');
                const response = await fetch('/api/onboarding/progress', {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const data = await response.json();
                return data.features_unlocked || [];
            } catch (e) {
                return [];
            }
        })()
    """)

    assert isinstance(features_unlocked, list), \
        "features_unlocked should be a list from backend API"


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_tutorial_overlay_system(admin_login: Page, app_config: AppConfig):
    """
    Test that tutorial overlay system (Intro.js) is properly integrated.

    User Journey:
    1. Admin navigates to onboarding dashboard
    2. Tutorial overlay system is loaded (Intro.js library)
    3. Admin can trigger tutorials manually
    4. Tutorials guide through features with step-by-step overlays
    5. Admin can dismiss tutorials
    6. Tutorial completion is tracked in backend

    Backend Integration:
    - Frontend loads Intro.js library from CDN or local copy
    - Frontend defines tutorial steps for each feature
    - window.startTutorial(tutorialId) starts a specific tutorial
    - window.triggerTutorialIfFirstUse() auto-triggers on first visit
    - When tutorial is completed, frontend calls PUT /api/onboarding/progress
      with updated tutorials_completed: ["getting_started", ...]
    - Backend saves tutorials_completed list
    - GET /api/onboarding/progress returns tutorials_completed
    - Frontend skips auto-trigger if tutorial ID in tutorials_completed

    Note: Intro.js library needs to be loaded for full testing.
    This test verifies the integration is set up correctly.
    """
    page = admin_login

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Verify Intro.js library is loaded (window.introJs exists)
    introjs_loaded = page.evaluate("typeof window.introJs === 'function'")
    assert introjs_loaded, "Intro.js library not loaded (window.introJs not found)"

    # Verify tutorial system functions are exposed
    tutorial_functions_loaded = page.evaluate("""
        typeof window.startTutorial === 'function' &&
        typeof window.triggerTutorialIfFirstUse === 'function' &&
        typeof window.dismissTutorial === 'function' &&
        typeof window.showTutorialList === 'function'
    """)
    assert tutorial_functions_loaded, \
        "Tutorial overlay functions not properly exposed to window object"

    # Verify that tutorial completion is tracked in backend
    tutorials_completed = page.evaluate("""
        (async () => {
            try {
                const authToken = localStorage.getItem('authToken');
                const response = await fetch('/api/onboarding/progress', {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const data = await response.json();
                return data.tutorials_completed || [];
            } catch (e) {
                return [];
            }
        })()
    """)

    assert isinstance(tutorials_completed, list), \
        "tutorials_completed should be a list from backend API"

    # Verify tutorial overlay elements exist in DOM (even if hidden)
    tutorial_overlay = page.locator(
        '.introjs-overlay, '
        '.tutorial-overlay, '
        '[class*="intro"]'
    )
    # At least the Intro.js styles should create overlay element
    # (It may not be visible until tutorial is triggered)


@pytest.mark.skip(reason="Onboarding Dashboard GUI not implemented - backend API exists but frontend pending")
def test_onboarding_complete_integration(admin_login: Page, app_config: AppConfig):
    """
    Test complete onboarding system integration.

    Comprehensive integration test covering all onboarding components:
    1. Dashboard loads successfully
    2. All widgets display (checklist, videos, sample data)
    3. All JavaScript modules loaded correctly
    4. Backend API integration works
    5. No console errors
    6. All window.* functions are available

    This test verifies the entire onboarding system is properly wired together:
    - Frontend components render
    - Backend API is accessible
    - JavaScript modules are loaded
    - No errors in console
    - All features are integrated
    """
    page = admin_login

    # Set up console error listener
    console_errors = []

    def log_console_error(msg):
        if msg.type == 'error':
            console_errors.append(msg.text)

    page.on('console', log_console_error)

    # Navigate to onboarding dashboard
    page.goto(f"{app_config.app_url}/app/onboarding-dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)  # Let all components initialize

    # Verify all window.* functions are loaded
    all_functions_loaded = page.evaluate("""
        typeof window.renderChecklist === 'function' &&
        typeof window.updateChecklistItem === 'function' &&
        typeof window.playVideo === 'function' &&
        typeof window.markVideoWatched === 'function' &&
        typeof window.startTutorial === 'function' &&
        typeof window.triggerTutorialIfFirstUse === 'function' &&
        typeof window.dismissTutorial === 'function' &&
        typeof window.showTutorialList === 'function' &&
        typeof window.checkUnlockConditions === 'function' &&
        typeof window.renderSampleDataControls === 'function' &&
        typeof window.introJs === 'function'
    """)
    assert all_functions_loaded, \
        "Onboarding JavaScript modules not fully loaded (missing window.* functions)"

    # Verify all dashboard components are visible
    onboarding_dashboard = page.locator('#onboarding-dashboard, .onboarding-dashboard')
    expect(onboarding_dashboard).to_be_visible()

    checklist_widget = page.locator('.onboarding-checklist')
    expect(checklist_widget).to_be_visible()

    video_grid = page.locator('#dashboard-video-grid, .video-grid')
    expect(video_grid).to_be_visible()

    sample_data_controls = page.locator('#dashboard-sample-data-controls, .sample-data-controls')
    expect(sample_data_controls).to_be_visible()

    # Verify backend API is accessible and returns valid data
    onboarding_progress = page.evaluate("""
        (async () => {
            try {
                const authToken = localStorage.getItem('authToken');
                const response = await fetch('/api/onboarding/progress', {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                return await response.json();
            } catch (e) {
                return { error: e.message };
            }
        })()
    """)

    # Verify onboarding progress has all expected fields
    assert 'wizard_step_completed' in onboarding_progress, \
        "Backend API response missing wizard_step_completed"
    assert 'checklist_state' in onboarding_progress, \
        "Backend API response missing checklist_state"
    assert 'tutorials_completed' in onboarding_progress, \
        "Backend API response missing tutorials_completed"
    assert 'features_unlocked' in onboarding_progress, \
        "Backend API response missing features_unlocked"
    assert 'videos_watched' in onboarding_progress, \
        "Backend API response missing videos_watched"

    # Verify no JavaScript errors in console
    if console_errors:
        pytest.fail(f"Console errors detected: {console_errors}")

    # Verify sample data status API is accessible
    org_id = page.evaluate("JSON.parse(localStorage.getItem('currentOrg')).id")
    sample_data_status = page.evaluate(f"""
        (async () => {{
            try {{
                const authToken = localStorage.getItem('authToken');
                const response = await fetch('/api/onboarding/sample-data/status?org_id={org_id}', {{
                    headers: {{ 'Authorization': `Bearer ${{authToken}}` }}
                }});
                return await response.json();
            }} catch (e) {{
                return {{ error: e.message }};
            }}
        }})()
    """)

    assert 'has_sample_data' in sample_data_status, \
        "Sample data status API response missing has_sample_data"
