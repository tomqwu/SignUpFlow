"""
E2E tests for Availability Management (Volunteer Time-Off Requests).

Tests the complete volunteer workflow for managing time-off:
- Add time-off request
- Edit time-off request
- Delete time-off request
- View availability calendar
- Overlap validation
- Past date validation

Priority: CRITICAL - User-facing feature with zero GUI E2E coverage
"""

import pytest
from playwright.sync_api import Page, expect
import time
from datetime import datetime, timedelta


def test_add_time_off_request_complete_workflow(page: Page):
    """
    Test complete time-off request workflow from volunteer perspective.

    User Journey:
    1. Volunteer logs in
    2. Navigates to My Availability
    3. Clicks "Add Time Off"
    4. Fills start/end dates and reason
    5. Saves request
    6. Verifies request appears in availability list
    7. Verifies request shows in calendar view
    """
    # Step 1: Volunteer signup/login
    page.goto("http://localhost:8000/")
    page.locator('button[data-i18n="auth.get_started"]').click()

    # Fill signup form
    page.locator('#signup-name').fill("Volunteer Timeoff")
    page.locator('#signup-email').fill(f"volunteer_timeoff_{int(time.time())}@test.com")
    page.locator('#signup-password').fill("password123")
    page.locator('#signup-org-name').fill(f"Timeoff Test Org {int(time.time())}")

    # Submit signup
    page.locator('button[data-i18n="common.buttons.create"]').click()

    # Wait for schedule page
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Step 2: Navigate to My Availability
    page.locator('a[href="/app/availability"]').click()
    expect(page.locator('h2[data-i18n="availability.title"]')).to_be_visible(timeout=5000)

    # Step 3: Click "Add Time Off" button
    page.locator('button[data-i18n="availability.buttons.add_timeoff"]').click()

    # Step 4: Fill time-off form
    # Calculate dates: next week Monday to Friday
    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    next_friday = next_monday + timedelta(days=4)

    start_date = next_monday.strftime("%Y-%m-%d")
    end_date = next_friday.strftime("%Y-%m-%d")

    page.locator('#timeoff-start-date').fill(start_date)
    page.locator('#timeoff-end-date').fill(end_date)
    page.locator('#timeoff-reason').fill("Family vacation")

    # Step 5: Save request
    page.locator('button[data-i18n="common.buttons.save"]').click()

    # Wait for success toast
    expect(page.locator('.toast.success')).to_be_visible(timeout=5000)
    expect(page.locator('.toast.success')).to_contain_text("Time off added successfully")

    # Step 6: Verify request appears in list
    expect(page.locator('.availability-list')).to_be_visible()

    # Find the specific time-off entry
    timeoff_entry = page.locator('.availability-item').filter(has_text="Family vacation")
    expect(timeoff_entry).to_be_visible()

    # Verify dates are displayed correctly
    expect(timeoff_entry).to_contain_text(next_monday.strftime("%b %d, %Y"))
    expect(timeoff_entry).to_contain_text(next_friday.strftime("%b %d, %Y"))

    # Step 7: Verify request shows in calendar view
    page.locator('button[data-i18n="availability.buttons.calendar_view"]').click()
    expect(page.locator('.calendar-view')).to_be_visible()

    # Verify calendar shows blocked dates
    calendar_blocked_dates = page.locator('.calendar-date.blocked').count()
    assert calendar_blocked_dates >= 5, f"Expected at least 5 blocked dates (Mon-Fri), got {calendar_blocked_dates}"


def test_edit_time_off_request(page: Page):
    """
    Test editing an existing time-off request.

    User Journey:
    1. Volunteer has existing time-off request
    2. Clicks "Edit" on the request
    3. Changes end date
    4. Saves changes
    5. Verifies changes persisted
    """
    # Setup: Create volunteer with existing time-off
    page.goto("http://localhost:8000/")
    page.locator('button[data-i18n="auth.get_started"]').click()

    page.locator('#signup-name').fill("Edit Timeoff User")
    page.locator('#signup-email').fill(f"edit_timeoff_{int(time.time())}@test.com")
    page.locator('#signup-password').fill("password123")
    page.locator('#signup-org-name').fill(f"Edit Timeoff Org {int(time.time())}")
    page.locator('button[data-i18n="common.buttons.create"]').click()

    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Navigate to availability
    page.locator('a[href="/app/availability"]').click()
    expect(page.locator('h2[data-i18n="availability.title"]')).to_be_visible(timeout=5000)

    # Add initial time-off
    page.locator('button[data-i18n="availability.buttons.add_timeoff"]').click()

    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    next_wednesday = next_monday + timedelta(days=2)

    page.locator('#timeoff-start-date').fill(next_monday.strftime("%Y-%m-%d"))
    page.locator('#timeoff-end-date').fill(next_wednesday.strftime("%Y-%m-%d"))
    page.locator('#timeoff-reason').fill("Initial vacation")
    page.locator('button[data-i18n="common.buttons.save"]').click()

    expect(page.locator('.toast.success')).to_be_visible(timeout=5000)

    # Now edit the time-off
    timeoff_entry = page.locator('.availability-item').filter(has_text="Initial vacation")
    timeoff_entry.locator('button[data-i18n="common.buttons.edit"]').click()

    # Change end date to next Friday
    next_friday = next_monday + timedelta(days=4)
    page.locator('#timeoff-end-date').fill(next_friday.strftime("%Y-%m-%d"))
    page.locator('#timeoff-reason').fill("Extended vacation")

    page.locator('button[data-i18n="common.buttons.save"]').click()

    # Verify changes persisted
    expect(page.locator('.toast.success')).to_contain_text("Time off updated")

    updated_entry = page.locator('.availability-item').filter(has_text="Extended vacation")
    expect(updated_entry).to_be_visible()
    expect(updated_entry).to_contain_text(next_friday.strftime("%b %d, %Y"))


def test_delete_time_off_request(page: Page):
    """
    Test deleting a time-off request.

    User Journey:
    1. Volunteer has existing time-off request
    2. Clicks "Delete" on the request
    3. Confirms deletion
    4. Verifies request removed from list
    5. Verifies calendar no longer shows blocked dates
    """
    # Setup: Create volunteer with time-off
    page.goto("http://localhost:8000/")
    page.locator('button[data-i18n="auth.get_started"]').click()

    page.locator('#signup-name').fill("Delete Timeoff User")
    page.locator('#signup-email').fill(f"delete_timeoff_{int(time.time())}@test.com")
    page.locator('#signup-password').fill("password123")
    page.locator('#signup-org-name').fill(f"Delete Timeoff Org {int(time.time())}")
    page.locator('button[data-i18n="common.buttons.create"]').click()

    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    page.locator('a[href="/app/availability"]').click()
    expect(page.locator('h2[data-i18n="availability.title"]')).to_be_visible(timeout=5000)

    # Add time-off to delete
    page.locator('button[data-i18n="availability.buttons.add_timeoff"]').click()

    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    next_friday = next_monday + timedelta(days=4)

    page.locator('#timeoff-start-date').fill(next_monday.strftime("%Y-%m-%d"))
    page.locator('#timeoff-end-date').fill(next_friday.strftime("%Y-%m-%d"))
    page.locator('#timeoff-reason').fill("Vacation to delete")
    page.locator('button[data-i18n="common.buttons.save"]').click()

    expect(page.locator('.toast.success')).to_be_visible(timeout=5000)

    # Delete the time-off
    timeoff_entry = page.locator('.availability-item').filter(has_text="Vacation to delete")
    expect(timeoff_entry).to_be_visible()

    timeoff_entry.locator('button[data-i18n="common.buttons.delete"]').click()

    # Confirm deletion dialog
    page.locator('button[data-i18n="common.buttons.confirm"]').click()

    # Verify removal
    expect(page.locator('.toast.success')).to_contain_text("Time off deleted")
    expect(timeoff_entry).not_to_be_visible()

    # Verify calendar no longer shows blocked dates
    page.locator('button[data-i18n="availability.buttons.calendar_view"]').click()
    calendar_blocked_dates = page.locator('.calendar-date.blocked').count()
    assert calendar_blocked_dates == 0, f"Expected 0 blocked dates after deletion, got {calendar_blocked_dates}"


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
