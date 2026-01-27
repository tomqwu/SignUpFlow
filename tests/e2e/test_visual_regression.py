"""
E2E tests for Visual Regression Testing.

Tests:
- Login page visual appearance (full page + login form)
- Schedule view visual appearance (full view + event cards)
- Admin console visual appearance (tabs: people, events, teams)
- Settings modal visual appearance

Priority: MEDIUM - Visual regression testing to catch unintended UI changes

STATUS: Tests implemented but SKIPPED - Baseline snapshots not yet created
All UI features exist in frontend, backend API complete
Need to establish baseline images before enabling pixel-perfect comparison

Visual Regression Testing Overview:
Visual regression testing compares screenshots of UI components against baseline images
to detect unintended visual changes (CSS bugs, layout shifts, styling regressions).

How It Works:
1. **Baseline Creation**: First test run creates baseline screenshot for each test
   - Baselines stored in: tests/e2e/__snapshots__/{test-name}.png
   - Example: __snapshots__/login-page.png, __snapshots__/schedule-view.png

2. **Comparison**: Subsequent runs compare current screenshots against baselines
   - Current screenshots: __snapshots__/__current__/{test-name}.png
   - If identical: Test passes, current screenshot deleted
   - If different: Test fails, generates diff image

3. **Diff Generation**: When mismatch detected:
   - Diff image: __snapshots__/__diffs__/{test-name}.png (red highlights changes)
   - Actual image: __snapshots__/__diffs__/actual-{test-name}.png
   - Review diffs to determine if change is intentional or bug

4. **Baseline Update**: If change is intentional:
   - Delete old baseline: rm tests/e2e/__snapshots__/{test-name}.png
   - Run test again to create new baseline

Tools Used:
- Playwright screenshot API: locator.screenshot(path=...)
- PIL (Python Imaging Library): Image comparison and diff generation
- filecmp: Binary file comparison for exact match detection
- ImageChops.difference: Pixel-by-pixel comparison
- Custom _assert_snapshot() function: Baseline creation and comparison logic

Test Preparation:
Before each test:
- Disable CSS animations and transitions (prevents timing-based failures)
- Wait for page load: wait_until="networkidle"
- Wait for dynamic content: page.wait_for_function() for client-side rendering
- Provision test data via API (org, admin user, events, assignments)

Why Skipped:
- Baseline snapshots not yet created (first run needed)
- Visual regression testing requires stable UI (no active development changes)
- Best enabled after UI freeze or in stable release branches
- Useful for detecting unintended regressions, not for testing new features

Enabling Tests (3 Steps):
1. **Create Baselines**: Remove skip decorator, run tests once to create baselines
   - docker-compose -f docker-compose.dev.yml exec -T api pytest tests/e2e/test_visual_regression.py -v
   - Baselines saved to __snapshots__/*.png

2. **Commit Baselines**: Add baseline images to git
   - git add tests/e2e/__snapshots__/*.png
   - git commit -m "Add visual regression baseline snapshots"

3. **Enable in CI**: Tests will now fail if UI changes unexpectedly
   - Review diffs in __snapshots__/__diffs__/ when tests fail
   - Update baselines if changes are intentional

UI Coverage (4 Screens):
1. **Login Page** (2 snapshots):
   - Full page: login-page.png (entire body)
   - Login form: login-form.png (#login-screen element)

2. **Schedule View** (2 snapshots):
   - Full view: schedule-view.png (entire body with schedule list)
   - Event card: schedule-event-card.png (single .schedule-item)

3. **Admin Console** (4 snapshots):
   - Main console: admin-console.png (#admin-view)
   - People tab: admin-people-tab.png
   - Events tab: admin-events-tab.png
   - Teams tab: admin-teams-tab.png

4. **Settings Modal** (1 snapshot):
   - Modal: settings-modal.png (#settings-modal)

Total: 9 baseline snapshots

Frontend Selectors Used:
- #login-email - Email input on login page
- #login-screen - Login form container
- #main-app - Main app container
- h2[data-i18n="schedule.my_schedule"] - Schedule page heading
- #schedule-list .schedule-item - Schedule event cards
- #admin-view - Admin console container
- button[data-tab="people|events|teams"] - Admin tab buttons
- #settings-modal - Settings modal container
- button[name="⚙️"] - Settings button (gear emoji)

Backend API Integration:
Visual regression tests use backend API to provision test data:
- POST /api/organizations/ - Create test organization
- POST /api/people/ - Create admin user with roles=["admin", "volunteer"]
- POST /api/events?org_id=... - Create test events
- POST /api/events/{event_id}/assignments - Assign people to events

Helper Functions:
- _disable_animations(page) - Inject CSS to disable animations/transitions
  Prevents timing-based test failures from in-progress animations

- _provision_admin(api_client, name) - Create org + admin user
  Returns: (org dict, admin dict) with tokens for API calls

- _assert_snapshot(locator, name) - Compare screenshot against baseline
  Logic:
  1. Take screenshot of locator → __current__/{name}.png
  2. If baseline doesn't exist → Create baseline, delete current, print message
  3. If baseline exists and matches → Delete current (test passes)
  4. If baseline exists and differs → Generate diff, fail test with message

- _write_image_diff(baseline, current, target) - Generate visual diff
  Algorithm:
  1. Open both images in RGB mode
  2. Calculate pixel-by-pixel difference
  3. Highlight changes in red (255 for different pixels, 0 for same)
  4. Overlay red highlights on current image
  5. Save combined diff image

Best Practices:
1. **Stable Environment**: Run visual tests in consistent environment (same OS, browser version, screen size)
2. **Deterministic Content**: Use fixed test data (no timestamps, random values in visible content)
3. **Disable Animations**: Always disable CSS animations to prevent timing issues
4. **Wait for Content**: Wait for dynamic content to fully load before screenshot
5. **Review Diffs Carefully**: Visual changes might indicate bugs OR intentional design updates
6. **Baseline Management**: Keep baselines in git for team-wide consistency
7. **CI Integration**: Run on stable branches (not feature branches with frequent UI changes)

Common Issues:
- **Font Rendering**: Different OS/browsers may render fonts slightly differently
  Solution: Use headless=False and specific viewport size for consistency

- **Animation Timing**: Screenshots during animations cause false failures
  Solution: _disable_animations() helper function

- **Dynamic Content**: Timestamps, random data cause unnecessary failures
  Solution: Use fixed test data, hide dynamic elements before screenshot

- **Browser Version**: Different browser versions may have subtle rendering differences
  Solution: Pin Playwright browser version in CI

- **Screen Resolution**: Different resolutions cause layout differences
  Solution: Set consistent viewport size: page.set_viewport_size({"width": 1920, "height": 1080})

Snapshot Directory Structure:
tests/e2e/
├── __snapshots__/                # Baseline images (committed to git)
│   ├── login-page.png
│   ├── login-form.png
│   ├── schedule-view.png
│   ├── schedule-event-card.png
│   ├── admin-console.png
│   ├── admin-people-tab.png
│   ├── admin-events-tab.png
│   ├── admin-teams-tab.png
│   └── settings-modal.png
├── __snapshots__/__current__/    # Current test screenshots (not committed, auto-deleted on match)
│   └── [same files as above]
└── __snapshots__/__diffs__/      # Diff images when mismatch detected (not committed)
    ├── login-page.png            # Diff with red highlights
    ├── actual-login-page.png     # Current screenshot for comparison
    └── [same pattern for other snapshots]

Once baseline snapshots are created and committed, unskip these tests.
"""

from pathlib import Path
from typing import Tuple
import filecmp

import pytest
from PIL import Image, ImageChops
from playwright.sync_api import Page, expect

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui


pytestmark = [
    pytest.mark.usefixtures("api_server"),

]


def _disable_animations(page: Page) -> None:
    """
    Disable CSS animations and transitions to prevent timing-based test failures.

    Why: Screenshots taken during animations may capture intermediate states,
    causing false positives in visual regression tests.

    How: Inject CSS that overrides all transitions and animations with !important.

    Example failure without this:
    - Button hover animation mid-transition → screenshot differs from baseline
    - Modal fade-in animation → opacity varies between test runs
    - Page transition slide → elements at different positions

    Solution: Force all animations to complete instantly.
    """
    page.add_style_tag(
        content="*,*::before,*::after{transition:none!important;animation:none!important;}"
    )


def _provision_admin(api_client: ApiTestClient, name: str) -> Tuple[dict, dict]:
    """
    Create test organization and admin user for visual regression tests.

    Args:
        api_client: API test client with helper methods
        name: Admin name (e.g., "Visual Schedule Admin")

    Returns:
        Tuple of (org dict, admin dict)
        - org dict: {"id": "visual_schedule_admin_org", "name": "Visual Schedule Admin", ...}
        - admin dict: {"person_id": "...", "email": "...", "token": "...", "password": "..."}

    Backend API Calls:
    1. POST /api/organizations/ - Create org with name converted to slug
    2. POST /api/people/ - Create admin user with:
       - roles: ["admin", "volunteer"]
       - email: {slug}@example.com
       - password: "VisualPass123!"

    Example:
        org, admin = _provision_admin(api_client, "Visual Schedule Admin")
        # org["id"] = "visual_schedule_admin_org"
        # admin["email"] = "visual_schedule_admin@example.com"
        # admin["token"] = "eyJ0eXAi..." (JWT token for API calls)
    """
    slug = name.lower().replace(" ", "_")
    org = api_client.create_org(org_id=f"{slug}_org", name=name)
    admin_email = f"{slug}@example.com"
    admin = api_client.create_user(
        org_id=org["id"],
        name=name,
        roles=["admin", "volunteer"],
        email=admin_email,
        password="VisualPass123!",
    )
    return org, admin



def test_login_page_visual(page: Page, app_config: AppConfig) -> None:
    """
    Test login page visual appearance (full page + login form).

    User Journey:
    1. Navigate to login page
    2. Wait for page to fully load (network idle)
    3. Verify login form is visible
    4. Disable animations to ensure consistent screenshots
    5. Take full page screenshot
    6. Take login form screenshot

    Snapshots Created (2):
    1. login-page.png - Full page screenshot (body element)
    2. login-form.png - Login form screenshot (#login-screen element)

    Why 2 Snapshots:
    - Full page: Catches changes to header, footer, background, overall layout
    - Login form: Focused on form elements, buttons, input fields

    Common Visual Regressions Caught:
    - CSS framework update changes button styles
    - Header/footer layout shifts
    - Background color changes
    - Form input styling changes
    - Button hover states (if animations not disabled)
    - Font size/weight changes
    - Spacing/padding adjustments

    Baseline Location:
    - tests/e2e/__snapshots__/login-page.png
    - tests/e2e/__snapshots__/login-form.png
    """
    page.goto(f"{app_config.app_url}/login", wait_until="networkidle")
    expect(page.locator("#login-email")).to_be_visible()

    _disable_animations(page)

    # Full page screenshot
    _assert_snapshot(page.locator("body"), "login-page.png")

    # Login form screenshot
    login_screen = page.locator("#login-screen")
    expect(login_screen).to_be_visible()
    _assert_snapshot(login_screen, "login-form.png")



def test_schedule_view_visual(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
) -> None:
    """
    Test schedule view visual appearance (full view + event cards).

    User Journey:
    1. Create test organization and admin user via API
    2. Create test event via API ("Sunday Service")
    3. Assign admin to event as "usher"
    4. Login as admin via UI
    5. Navigate to schedule page
    6. Wait for schedule list to load
    7. Disable animations
    8. Wait for schedule items to render (client-side)
    9. Take full schedule view screenshot
    10. Take single event card screenshot

    Snapshots Created (2):
    1. schedule-view.png - Full schedule page (body element)
    2. schedule-event-card.png - Single schedule event card (.schedule-item)

    Why 2 Snapshots:
    - Full view: Catches changes to page header, navigation, overall layout
    - Event card: Focused on event card styling, date formatting, role badges

    Backend API Integration:
    - POST /api/events?org_id={org_id} - Create "Sunday Service" event
    - POST /api/events/{event_id}/assignments - Assign admin as "usher"
    - GET /api/events/assignments/all - Fetch schedule (waited for in test)

    Common Visual Regressions Caught:
    - Event card styling changes (border, shadow, padding)
    - Date formatting changes (e.g., "Nov 2" → "11/02")
    - Role badge styling (color, size, font)
    - Event title truncation behavior
    - Time display format changes
    - Schedule list spacing/gaps
    - Header/footer changes

    Baseline Location:
    - tests/e2e/__snapshots__/schedule-view.png
    - tests/e2e/__snapshots__/schedule-event-card.png
    """
    # Provision admin user and create test data
    org, admin = _provision_admin(api_client, "Visual Schedule Admin")
    event = api_client.create_event(
        admin_token=admin["token"],
        org_id=org["id"],
        event_type="Sunday Service",
    )
    api_client.assign_person_to_event(
        admin_token=admin["token"],
        org_id=org["id"],
        event_id=event["id"],
        person_id=admin["person_id"],
        role="usher",
    )

    # Login and navigate to schedule
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    with page.expect_response(
        lambda r: "/events/assignments/all" in r.url and r.request.method == "GET"
    ):
        page.goto(f"{app_config.app_url}/app/schedule", wait_until="networkidle")

    # Wait for schedule page to load
    # Verify schedule view is visible
    expect(page.locator("#schedule-view")).to_be_visible()
    # Check for Overview card instead of non-existent header
    expect(page.locator('[data-i18n="schedule.overview"]')).to_be_visible()

    _disable_animations(page)

    # Wait for schedule items to render (client-side React/Vue rendering)
    page.wait_for_function(
        "() => document.querySelectorAll('#schedule-list .schedule-item').length > 0"
    )
    schedule_item = page.locator('#schedule-list .schedule-item').first
    expect(schedule_item).to_be_visible()

    # Take screenshots
    _assert_snapshot(page.locator("body"), "schedule-view.png")
    _assert_snapshot(schedule_item, "schedule-event-card.png")



def test_admin_console_visual(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
) -> None:
    """
    Test admin console visual appearance (main console + 3 tabs).

    User Journey:
    1. Create test organization and admin user via API
    2. Login as admin via UI
    3. Navigate to admin console (/app/admin)
    4. Wait for admin view to load
    5. Disable animations
    6. Take main admin console screenshot
    7. Click each tab (People, Events, Teams) and take screenshots

    Snapshots Created (4):
    1. admin-console.png - Main admin console view (#admin-view)
    2. admin-people-tab.png - People tab view
    3. admin-events-tab.png - Events tab view
    4. admin-teams-tab.png - Teams tab view

    Why 4 Snapshots:
    - Main console: Catches changes to sidebar, header, overall layout
    - Each tab: Catches changes to tab content, tables, buttons, forms

    Admin Console Tabs:
    - People: List of organization members, add/edit/delete buttons
    - Events: List of events, create event button, event management
    - Teams: List of teams, team creation, member management

    Common Visual Regressions Caught:
    - Tab styling changes (active state, hover, borders)
    - Table styling (headers, rows, alternating colors)
    - Button styling (primary, secondary, danger buttons)
    - Form styling (inputs, labels, validation messages)
    - Modal styling (if modals open)
    - Admin sidebar changes
    - Data grid/table layout changes

    Baseline Location:
    - tests/e2e/__snapshots__/admin-console.png
    - tests/e2e/__snapshots__/admin-people-tab.png
    - tests/e2e/__snapshots__/admin-events-tab.png
    - tests/e2e/__snapshots__/admin-teams-tab.png
    """
    _, admin = _provision_admin(api_client, "Visual Admin Console")

    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    page.goto(f"{app_config.app_url}/app/admin", wait_until="networkidle")

    admin_view = page.locator("#admin-view")
    expect(admin_view).to_be_visible()

    _disable_animations(page)

    # Main admin console screenshot
    _assert_snapshot(admin_view, "admin-console.png")

    # Click each tab and take screenshots
    tab_definitions = [
        ("people", "People"),
        ("events", "Events"),
        ("teams", "Teams"),
    ]
    for tab_key, tab_label in tab_definitions:
        # Try to find tab by data-tab attribute OR by text content
        tab_button = page.locator(
            f'button[data-tab="{tab_key}"], .admin-tab-btn:has-text("{tab_label}")'
        )
        if tab_button.count():
            tab_button.first.click()
            # Take screenshot of tab content
            _assert_snapshot(admin_view, f"admin-{tab_key}-tab.png")



def test_settings_modal_visual(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
) -> None:
    """
    Test settings modal visual appearance.

    User Journey:
    1. Create test organization and admin user via API
    2. Login as admin via UI
    3. Wait for app to load
    4. Click settings button (gear emoji ⚙️)
    5. Wait for settings modal to appear
    6. Disable animations
    7. Take settings modal screenshot

    Snapshots Created (1):
    1. settings-modal.png - Settings modal (#settings-modal)

    Settings Modal Content:
    - User profile settings (name, email)
    - Language selection dropdown
    - Timezone selection dropdown
    - Notification preferences
    - Password change form
    - Logout button

    Common Visual Regressions Caught:
    - Modal backdrop styling (overlay, opacity)
    - Modal border/shadow changes
    - Form input styling
    - Dropdown styling
    - Button layout/spacing
    - Modal header/footer changes
    - Close button styling
    - Field validation styling

    Baseline Location:
    - tests/e2e/__snapshots__/settings-modal.png
    """
    _, admin = _provision_admin(api_client, "Visual Settings User")

    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])

    # Click settings button (gear emoji)
    settings_button = page.locator('button.action-btn[onclick="showSettings()"]')
    expect(settings_button).to_be_visible()
    settings_button.click()

    # Wait for settings modal to appear
    settings_modal = page.locator("#settings-modal")
    expect(settings_modal).to_be_visible()

    _disable_animations(page)

    # Take modal screenshot
    _assert_snapshot(settings_modal, "settings-modal.png")


# Snapshot directory structure
SNAPSHOT_DIR = Path(__file__).parent / "__snapshots__"
CURRENT_DIR = SNAPSHOT_DIR / "__current__"
DIFF_DIR = SNAPSHOT_DIR / "__diffs__"

# Create directories if they don't exist
for directory in (SNAPSHOT_DIR, CURRENT_DIR, DIFF_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def _assert_snapshot(locator, name: str) -> None:
    """
    Compare screenshot against baseline, create baseline if missing, fail if different.

    Algorithm:
    1. Take screenshot of locator → __current__/{name}
    2. If baseline doesn't exist:
       - Copy current → baseline
       - Delete current
       - Print "Created baseline snapshot for {name}"
       - Test passes (baseline created)
    3. If baseline exists and current matches baseline:
       - Delete current (test passes, no diff needed)
    4. If baseline exists and current differs:
       - Generate diff image with red highlights
       - Save actual image to __diffs__/actual-{name}
       - Fail test with message pointing to diff and actual images

    Args:
        locator: Playwright locator to screenshot (e.g., page.locator("body"))
        name: Snapshot filename (e.g., "login-page.png")

    Raises:
        pytest.fail: If screenshot differs from baseline

    Files Created:
        - Baseline: __snapshots__/{name} (committed to git)
        - Current: __snapshots__/__current__/{name} (temporary, deleted on match)
        - Diff: __snapshots__/__diffs__/{name} (red highlights, not committed)
        - Actual: __snapshots__/__diffs__/actual-{name} (current screenshot, not committed)

    Example Workflow:
        # First run (baseline creation)
        _assert_snapshot(page.locator("body"), "login-page.png")
        # Output: "Created baseline snapshot for login-page.png"
        # Files: __snapshots__/login-page.png (baseline created)

        # Second run (match)
        _assert_snapshot(page.locator("body"), "login-page.png")
        # Output: (none, test passes silently)
        # Files: __current__/login-page.png deleted (matched baseline)

        # Third run (mismatch - button color changed)
        _assert_snapshot(page.locator("body"), "login-page.png")
        # Output: pytest.fail("Snapshot mismatch for login-page.png. Updated diff saved to ...")
        # Files:
        #   - __diffs__/login-page.png (diff with red highlights)
        #   - __diffs__/actual-login-page.png (current screenshot)
        # Developer reviews diff, decides if bug or intentional change
        # If intentional: rm __snapshots__/login-page.png; rerun to create new baseline
    """
    baseline_path = SNAPSHOT_DIR / name
    current_path = CURRENT_DIR / name

    # Take screenshot of locator
    locator.screenshot(path=current_path)

    # Baseline creation path
    if not baseline_path.exists():
        baseline_path.write_bytes(current_path.read_bytes())
        current_path.unlink(missing_ok=True)
        print(f"Created baseline snapshot for {name}")
        return

    # Comparison path - binary file comparison first (fast)
    if filecmp.cmp(baseline_path, current_path, shallow=False):
        # Exact match - delete current screenshot and pass
        current_path.unlink(missing_ok=True)
        return

    # Mismatch detected - generate diff image and fail
    diff_path = DIFF_DIR / name
    _write_image_diff(baseline_path, current_path, diff_path)

    # Save actual screenshot for comparison
    actual_path = DIFF_DIR / f"actual-{name}"
    current_path.replace(actual_path)

    # Fail test with helpful message
    pytest.fail(
        f"Snapshot mismatch for {name}. Updated diff saved to {diff_path} and actual frame to {actual_path}."
    )


def _write_image_diff(baseline: Path, current: Path, target: Path) -> None:
    """
    Generate visual diff image with red highlights for changed pixels.

    Algorithm:
    1. Open baseline and current images in RGB mode
    2. Calculate pixel-by-pixel difference using ImageChops.difference()
       - Returns new image where each pixel value is |baseline - current|
       - 0 = identical pixels, >0 = different pixels
    3. Create highlight mask:
       - For each pixel in diff image: 255 if pixel > 0, else 0
       - Results in binary mask: white where different, black where same
    4. Overlay red highlights on current image:
       - Add highlight mask to current image
       - Converts mask to RGB (red channel only)
       - Results in current image with red overlay on changed areas
    5. Save combined diff image

    Args:
        baseline: Path to baseline image
        current: Path to current screenshot
        target: Path to save diff image

    Example Output:
        Baseline: Blue button
        Current: Red button
        Diff: Current screenshot with red highlights around button area

    PIL Operations:
        - Image.open(): Load image from file
        - .convert("RGB"): Ensure consistent RGB color mode
        - ImageChops.difference(): Pixel-by-pixel subtraction
        - .point(lambda px: ...): Map each pixel value through function
        - ImageChops.add(): Pixel-by-pixel addition (overlay highlights)
        - .save(): Save result to file
    """
    with Image.open(baseline).convert("RGB") as base_img, Image.open(current).convert("RGB") as curr_img:
        # Calculate pixel-by-pixel difference
        diff = ImageChops.difference(base_img, curr_img)

        # Highlight changes in red overlay for quick scanning
        # Convert diff to binary mask: 255 for any change, 0 for no change
        highlight = diff.point(lambda px: 255 if px > 0 else 0)

        # Add red overlay to current image
        diff_image = ImageChops.add(curr_img, highlight.convert("RGB"))

        # Save diff image
        diff_image.save(target)
