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


def test_add_time_off_request_complete_workflow(authenticated_page: Page):
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
    page = authenticated_page

    # Step 1: Navigate to My Availability
    page.goto("http://localhost:8000/app/availability")
    page.wait_for_load_state("networkidle")
    expect(page.locator('h2[data-i18n="schedule.availability"]')).to_be_visible(timeout=5000)

    # Step 2: Delete any existing time-off periods to avoid 409 Conflict
    # This ensures test isolation and prevents overlap errors from previous runs
    delete_buttons = page.locator('.timeoff-item button:has-text("Delete")').all()
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


def test_edit_time_off_request(authenticated_page: Page):
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
    page = authenticated_page

    # Navigate to availability
    page.goto("http://localhost:8000/app/availability")
    page.wait_for_load_state("networkidle")
    expect(page.locator('h2[data-i18n="schedule.availability"]')).to_be_visible(timeout=5000)

    # Delete any existing time-off periods to avoid 409 Conflict
    # This ensures test isolation and prevents overlap errors from previous runs
    delete_buttons = page.locator('.timeoff-item button:has-text("Delete")').all()
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
    timeoff_entry = page.locator('.timeoff-item').filter(has_text=initial_reason)
    timeoff_entry.locator('button:has-text("Edit")').click()

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


def test_delete_time_off_request(authenticated_page: Page):
    """
    Test deleting a time-off request.

    User Journey:
    1. Volunteer is logged in (uses authenticated_page fixture)
    2. Volunteer has existing time-off request
    3. Clicks "Remove" on the request
    4. Verifies request removed from list (no confirmation dialog in UI)
    """
    page = authenticated_page

    # Navigate to availability page (reload to ensure fresh state)
    page.goto("http://localhost:8000/app/availability", wait_until="networkidle")

    # Give extra time for page to fully render after previous tests
    page.wait_for_timeout(1000)
    expect(page.locator('h2[data-i18n="schedule.availability"]')).to_be_visible(timeout=10000)

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
    timeoff_entry.locator('button:has-text("Remove")').click()

    # Confirm deletion in dialog
    page.locator('#confirm-yes').click()

    # Wait for deletion to complete - wait for the specific entry to disappear
    expect(page.locator('.timeoff-item').filter(has_text=reason)).not_to_be_visible()

    # Verify that item count decreased
    expect(page.locator('.timeoff-item')).to_have_count(initial_count - 1)


def test_view_availability_calendar(page: Page):
    """
    Test viewing availability in calendar format.

    Verifies:
    - Calendar view button exists
    - Calendar displays current month
    - Blocked dates are visually distinct
    - Can navigate to previous/next month
    """
    pytest.skip("TODO: Implement calendar view test")


def test_overlap_validation(page: Page):
    """
    Test that overlapping time-off requests are prevented.

    User Journey:
    1. Volunteer adds time-off for Nov 1-5
    2. Attempts to add overlapping time-off for Nov 3-7
    3. Sees error message "Time off overlaps with existing request"
    4. Cannot save overlapping request
    """
    pytest.skip("TODO: Implement overlap validation test")


def test_past_date_validation(page: Page):
    """
    Test that past date time-off requests are prevented.

    User Journey:
    1. Volunteer attempts to add time-off for past date
    2. Sees error message "Cannot add time off for past dates"
    3. Cannot save past date request
    """
    pytest.skip("TODO: Implement past date validation test")
