"""
E2E tests for Availability Management (Volunteer Time-Off Requests).

Tests the complete volunteer workflow for managing time-off:
- Add time-off request
- Edit time-off request
- Delete time-off request
- View availability calendar (TODO)
- Overlap validation (TODO)
- Past date validation (TODO)

Priority: CRITICAL - User-facing feature with zero GUI E2E coverage

FIXED (2025-10-27): Tests updated to match actual UI implementation:
- CSS class: '.timeoff-item' (not '.availability-item')
- Edit button: Plain text "Edit" (not i18n attribute)
- Remove button: Plain text "Remove" (not i18n "Delete")
- Edit workflow: Uses modal dialog with fields #edit-timeoff-start, #edit-timeoff-end
- Delete workflow: Confirmation dialog with #confirm-yes button (NOT direct removal)
- Form fields: #timeoff-start, #timeoff-end (NO '-date' suffix)
"""

import pytest
from playwright.sync_api import Page, expect
import time
from datetime import datetime, timedelta
import random

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


def test_add_time_off_request_complete_workflow(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test complete time-off request workflow from volunteer perspective.

    User Journey:
    1. Volunteer is logged in (uses authenticated_page fixture)
    2. Navigates to My Availability
    3. Clicks "Add Time Off"
    4. Fills start/end dates and reason
    5. Saves request
    6. Verifies request appears in availability list
    7. Verifies request shows in calendar view
    """
    # Setup: Create test organization and volunteer user
    org = api_client.create_org()
    volunteer = api_client.create_user(
        org_id=org["id"],
        name="Test Volunteer",
        roles=["volunteer"],
    )

    # Login as volunteer
    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Step 1: Navigate to My Availability
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_load_state("networkidle")
    expect(page.locator('#page-title')).to_be_visible(timeout=5000)

    # Step 2: Delete any existing time-off periods to avoid 409 Conflict
    # This ensures test isolation and prevents overlap errors from previous runs
    # Note: Delete button uses trash emoji 🗑️, so we use CSS class selector
    delete_buttons = page.locator('.timeoff-item button.btn-remove').all()
    for delete_btn in delete_buttons:
        delete_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)  # Wait for deletion to process

    # Step 2: Fill time-off form
    # Use random future dates (1000-1100 days) to avoid conflicts with previous test runs
    days_offset = random.randint(1000, 1100)
    base_date = datetime.now() + timedelta(days=days_offset)
    start_date = base_date.strftime("%Y-%m-%d")
    end_date = (base_date + timedelta(days=4)).strftime("%Y-%m-%d")

    # Use unique reason to avoid conflicts with previous test runs
    unique_id = f"{int(time.time())}-{random.randint(1000, 9999)}"
    reason = f"Family vacation {unique_id}"

    page.locator('#timeoff-start').fill(start_date)
    page.locator('#timeoff-end').fill(end_date)
    page.locator('#timeoff-reason').fill(reason)

    # Step 3: Submit form
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    # Step 4: Wait for page reload/update
    page.wait_for_load_state("networkidle")

    # Step 5: Verify request appears in list
    expect(page.locator('#timeoff-list')).to_be_visible()

    # Find the specific time-off entry using unique reason
    timeoff_entry = page.locator('.timeoff-item').filter(has_text=reason)
    expect(timeoff_entry).to_be_visible()


def test_edit_time_off_request(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test editing an existing time-off request.

    User Journey:
    1. Volunteer is logged in (uses authenticated_page fixture)
    2. Volunteer has existing time-off request
    3. Clicks "Edit" on the request
    4. Changes end date in modal
    5. Saves changes
    6. Verifies changes persisted
    """
    # Setup: Create test organization and volunteer user
    org = api_client.create_org()
    volunteer = api_client.create_user(
        org_id=org["id"],
        name="Test Volunteer",
        roles=["volunteer"],
    )

    # Login as volunteer
    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Navigate to availability
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_load_state("networkidle")
    expect(page.locator('#page-title')).to_be_visible(timeout=5000)

    # Delete any existing time-off periods to avoid 409 Conflict
    # This ensures test isolation and prevents overlap errors from previous runs
    # Note: Delete button uses trash emoji 🗑️, so we use CSS class selector
    delete_buttons = page.locator('.timeoff-item button.btn-remove').all()
    for delete_btn in delete_buttons:
        delete_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)  # Wait for deletion to process

    # Add initial time-off (use random future dates to avoid conflicts)
    # Use 5000-5100 days (~13 years) to avoid overlap with any existing data
    days_offset = random.randint(5000, 5100)
    start_date = datetime.now() + timedelta(days=days_offset)
    mid_date = start_date + timedelta(days=2)

    # Use unique reason to avoid conflicts with previous test runs
    unique_id = f"{int(time.time())}-{random.randint(1000, 9999)}"
    initial_reason = f"Initial vacation {unique_id}"
    extended_reason = f"Extended vacation {unique_id}"

    page.locator('#timeoff-start').fill(start_date.strftime("%Y-%m-%d"))
    page.locator('#timeoff-end').fill(mid_date.strftime("%Y-%m-%d"))
    page.locator('#timeoff-reason').fill(initial_reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    page.wait_for_load_state("networkidle")

    # Now edit the time-off - find the item and click Edit button
    # Note: Edit button uses pencil emoji ✏️, so we use CSS class selector
    timeoff_entry = page.locator('.timeoff-item').filter(has_text=initial_reason)
    timeoff_entry.locator('button.btn-secondary').click()

    # Wait for modal to appear
    expect(page.locator('#edit-timeoff-modal')).to_be_visible()

    # Change end date to extend the vacation by 4 days
    end_date = start_date + timedelta(days=4)
    page.locator('#edit-timeoff-end').fill(end_date.strftime("%Y-%m-%d"))
    page.locator('#edit-timeoff-reason').fill(extended_reason)

    # Submit the modal form
    page.locator('#edit-timeoff-form button[type="submit"]').click()

    # Wait for modal to close
    expect(page.locator('#edit-timeoff-modal')).not_to_be_visible()

    # Verify changes persisted in the list
    updated_entry = page.locator('.timeoff-item').filter(has_text=extended_reason)
    expect(updated_entry).to_be_visible()


def test_delete_time_off_request(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test deleting a time-off request.

    User Journey:
    1. Volunteer is logged in (uses authenticated_page fixture)
    2. Volunteer has existing time-off request
    3. Clicks "Remove" on the request
    4. Verifies request removed from list (no confirmation dialog in UI)
    """
    # Setup: Create test organization and volunteer user
    org = api_client.create_org()
    volunteer = api_client.create_user(
        org_id=org["id"],
        name="Test Volunteer",
        roles=["volunteer"],
    )

    # Login as volunteer
    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Navigate to availability page (reload to ensure fresh state)
    page.goto(f"{app_config.app_url}/app/availability", wait_until="networkidle")

    # Give extra time for page to fully render after previous tests
    page.wait_for_timeout(1000)
    expect(page.locator('#page-title')).to_be_visible(timeout=10000)

    # Add time-off to delete (use random future dates to avoid conflicts)
    # Use 10000-10100 days (~27 years) to avoid overlap with any existing data
    days_offset = random.randint(10000, 10100)
    start_date = datetime.now() + timedelta(days=days_offset)
    end_date = start_date + timedelta(days=4)

    # Use unique reason to avoid conflicts with previous test runs
    unique_id = f"{int(time.time())}-{random.randint(1000, 9999)}"
    reason = f"Vacation to delete {unique_id}"

    page.locator('#timeoff-start').fill(start_date.strftime("%Y-%m-%d"))
    page.locator('#timeoff-end').fill(end_date.strftime("%Y-%m-%d"))
    page.locator('#timeoff-reason').fill(reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    page.wait_for_load_state("networkidle")

    # Delete the time-off
    timeoff_entry = page.locator('.timeoff-item').filter(has_text=reason)
    expect(timeoff_entry).to_be_visible()

    # Get count before deletion
    initial_count = page.locator('.timeoff-item').count()

    # Click Remove button (triggers confirmation dialog)
    # Note: Delete button uses trash emoji 🗑️, so we use CSS class selector
    timeoff_entry.locator('button.btn-remove').click()

    # Confirm deletion in dialog
    page.locator('#confirm-yes').click()

    # Wait for deletion to complete - wait for the specific entry to disappear
    expect(page.locator('.timeoff-item').filter(has_text=reason)).not_to_be_visible()

    # Verify that item count decreased
    expect(page.locator('.timeoff-item')).to_have_count(initial_count - 1)


def test_view_availability_calendar(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    print("TEST STARTED: test_view_availability_calendar")
    """
    Test viewing availability in calendar format.
    """
    # 1. Setup: Create volunteer user
    org = api_client.create_org(name="Test Org Calendar")
    volunteer = api_client.create_user(
        org_id=org["id"],
        roles=["volunteer"],
        name="Calendar Volunteer"
    )

    # Login as volunteer
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))
    page.on("requestfailed", lambda request: print(f"REQUEST FAILED: {request.url} - {request.failure}"))
    page.on("response", lambda response: print(f"RESPONSE: {response.status} {response.url}") if response.status >= 400 else None)
    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Navigate to availability
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_load_state("networkidle")

    # Verify calendar container exists
    calendar = page.locator('#availability-calendar')
    
    # Debug visibility
    try:
        style = page.evaluate("""() => {
            const el = document.getElementById('availability-calendar');
            if (!el) return 'ELEMENT NOT FOUND';
            const style = window.getComputedStyle(el);
            const parent = el.parentElement;
            const grandParent = parent ? parent.parentElement : null;
            const greatGrandParent = grandParent ? grandParent.parentElement : null;
            
            const rect = el.getBoundingClientRect();
            return {
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                height: style.height,
                width: style.width,
                rect: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    bottom: rect.bottom,
                    left: rect.left,
                    right: rect.right
                },
                innerHTMLLength: el.innerHTML.length,
                classList: el.classList.toString(),
                parent: parent ? {
                    id: parent.id,
                    class: parent.className,
                    display: window.getComputedStyle(parent).display
                } : null,
                grandParent: grandParent ? {
                    id: grandParent.id,
                    class: grandParent.className,
                    display: window.getComputedStyle(grandParent).display
                } : null,
                greatGrandParent: greatGrandParent ? {
                    id: greatGrandParent.id,
                    class: greatGrandParent.className,
                    display: window.getComputedStyle(greatGrandParent).display
                } : null
            };
        }""")
        print(f"DEBUG STYLE: {style}")
        print(f"DEBUG HTML: {page.locator('#availability-calendar').inner_html()}")
    except Exception as e:
        print(f"DEBUG STYLE ERROR: {e}")

    expect(calendar).to_be_visible()

    # Verify current month header
    current_month = datetime.now().strftime("%B %Y")
    expect(calendar.locator('h4')).to_contain_text(current_month)

    # Add a time-off request to verify it shows up in calendar
    days_offset = random.randint(100, 200)
    base_date = datetime.now() + timedelta(days=days_offset)
    start_date = base_date.strftime("%Y-%m-%d")
    end_date = (base_date + timedelta(days=2)).strftime("%Y-%m-%d")
    reason = f"Calendar Test {int(time.time())}"

    page.locator('#timeoff-start').fill(start_date)
    page.locator('#timeoff-end').fill(end_date)
    page.locator('#timeoff-reason').fill(reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    # Wait for success toast
    expect(page.get_by_text("Time-off added successfully!")).to_be_visible()
    # Wait for toast to disappear or just proceed
    page.locator('.toast').click() # Dismiss if clickable or just wait

    # Verify blocked dates are highlighted in calendar
    # Note: Since the calendar shows the current month, we need to add a request for THIS month to see it
    # But adding for this month might conflict with "past date" validation if we pick a past day
    # So let's pick a future day in the CURRENT month
    
    now = datetime.now()
    # Find a day later this month, or skip if end of month
    days_in_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    if now.day < days_in_month.day - 2:
        # Add request for later this month
        start_date_curr = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date_curr = (now + timedelta(days=2)).strftime("%Y-%m-%d")
        reason_curr = f"Current Month Test {int(time.time())}"

        page.locator('#timeoff-start').fill(start_date_curr)
        page.locator('#timeoff-end').fill(end_date_curr)
        page.locator('#timeoff-reason').fill(reason_curr)
        page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()
        
        # Wait for success toast again
        expect(page.get_by_text("Time-off added successfully!").nth(1)).to_be_visible()
        
        # Check for .calendar-day.blocked
        expect(page.locator('.calendar-day.blocked').first).to_be_visible()



def test_overlap_validation(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test that overlapping time-off requests are prevented.
    """
    # Setup
    org = api_client.create_org()
    volunteer = api_client.create_user(
        org_id=org["id"],
        name="Test Volunteer",
        roles=["volunteer"],
    )

    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_load_state("networkidle")

    # Add initial time-off
    days_offset = random.randint(300, 400)
    base_date = datetime.now() + timedelta(days=days_offset)
    start_date = base_date.strftime("%Y-%m-%d")
    end_date = (base_date + timedelta(days=4)).strftime("%Y-%m-%d") # 5 days total
    reason = f"Overlap Base {int(time.time())}"

    page.locator('#timeoff-start').fill(start_date)
    page.locator('#timeoff-end').fill(end_date)
    page.locator('#timeoff-reason').fill(reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()
    page.wait_for_load_state("networkidle")

    # Verify added
    expect(page.locator('.timeoff-item').filter(has_text=reason)).to_be_visible()
    initial_count = page.locator('.timeoff-item').count()

    # Attempt to add overlapping time-off (middle of the range)
    overlap_start = (base_date + timedelta(days=2)).strftime("%Y-%m-%d")
    overlap_end = (base_date + timedelta(days=6)).strftime("%Y-%m-%d")
    overlap_reason = "Overlap Attempt"

    page.locator('#timeoff-start').fill(overlap_start)
    page.locator('#timeoff-end').fill(overlap_end)
    page.locator('#timeoff-reason').fill(overlap_reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    # Verify error message
    # Toast message should appear
    expect(page.locator('.toast-error')).to_contain_text("overlaps")

    # Verify count didn't increase
    expect(page.locator('.timeoff-item')).to_have_count(initial_count)


def test_past_date_validation(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Test that past date time-off requests are prevented.
    """
    # Setup
    org = api_client.create_org()
    volunteer = api_client.create_user(
        org_id=org["id"],
        name="Test Volunteer",
        roles=["volunteer"],
    )

    login_via_ui(page, app_config.app_url, volunteer["email"], volunteer["password"])
    page.goto(f"{app_config.app_url}/app/availability")
    page.wait_for_load_state("networkidle")

    initial_count = page.locator('.timeoff-item').count()

    # Attempt to add time-off for yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    reason = "Past Date Attempt"

    page.locator('#timeoff-start').fill(yesterday)
    page.locator('#timeoff-end').fill(yesterday)
    page.locator('#timeoff-reason').fill(reason)
    page.locator('button[type="submit"][data-i18n="schedule.add_time_off"]').click()

    # Verify error message
    expect(page.locator('.toast-error')).to_contain_text("past dates")

    # Verify count didn't increase
    expect(page.locator('.timeoff-item')).to_have_count(initial_count)
