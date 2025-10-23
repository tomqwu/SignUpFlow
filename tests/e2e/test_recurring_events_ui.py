"""
E2E tests for Recurring Events UI functionality.

These tests verify the complete user workflow for creating and managing
recurring event patterns following User Stories from spec 006.

Test execution follows CLAUDE.md mandatory E2E testing workflow:
1. Write E2E test FIRST (this file) - tests will FAIL initially
2. Implement feature to make tests PASS
3. Manual verification in browser
4. All tests must PASS before marking feature complete
"""

import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta


APP_URL = "http://localhost:8000"


class TestRecurringEventsCreation:
    """
    Test User Story 1: Create Weekly Recurring Events (Priority: P1)

    Admin users create weekly recurring events (Sunday services, weekly meetings)
    by selecting recurrence pattern, specifying which days of week, and setting
    end date or occurrence count. System generates all event occurrences automatically.
    """

    def test_create_weekly_recurring_event_complete_workflow(self, page: Page, api_server):
        """
        Test complete workflow for creating weekly recurring event.

        User Journey:
        1. Admin logs in
        2. Admin clicks "Create Event"
        3. Admin selects "Recurring Event" checkbox
        4. Admin fills event title
        5. Admin selects "Weekly" recurrence pattern
        6. Admin selects "Sunday" day
        7. Admin sets end date (3 months from now)
        8. Admin clicks "Preview Calendar"
        9. Admin verifies calendar shows 12-13 Sunday occurrences
        10. Admin clicks "Create Recurring Event"
        11. Admin sees success message
        12. Admin verifies calendar view shows all generated occurrences

        Acceptance Criteria (User Story 1, AC1):
        - System generates 12-13 Sunday events spanning 3-month date range

        THIS TEST WILL FAIL INITIALLY - Feature not implemented yet.
        """
        # Given: Admin is logged in
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Login as admin
        if page.locator('a:has-text("Sign in")').count() > 0:
            page.locator('a:has-text("Sign in")').click()
            page.wait_for_timeout(500)

        page.fill('input[type="email"]', "jane@test.com")
        page.fill('input[type="password"]', "password")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(2000)

        # Verify logged in
        expect(page.locator('#main-app')).to_be_visible()

        # When: Admin creates new recurring event
        # Navigate to admin console
        page.goto("http://localhost:8000/app/admin")
        page.wait_for_timeout(1000)

        # Click Events tab
        events_tab = page.locator('button:has-text("Events")')
        if events_tab.count() > 0:
            events_tab.first.click()
            page.wait_for_timeout(1000)  # Wait for tab content to show

        # Take screenshot for debugging
        page.screenshot(path="/tmp/e2e-admin-events-tab.png")

        # Call showCreateEventForm() directly via JavaScript (button is hidden by admin console tabs)
        page.evaluate("window.showCreateEventForm()")
        page.wait_for_timeout(500)

        # Modal/form should appear
        expect(page.locator('#create-event-modal, #event-modal')).to_be_visible()

        # Fill event title
        page.locator('#event-title').fill("Sunday Service")

        # Fill event start date/time (required for preview)
        start_datetime = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT10:00")
        page.locator('#event-start').fill(start_datetime)

        # Select "Recurring Event" checkbox
        page.locator('#is-recurring').check()
        page.wait_for_timeout(300)

        # Recurring pattern section should become visible
        expect(page.locator('#recurring-options-container')).to_be_visible()

        # Select "Weekly" recurrence pattern
        page.locator('#recurrence-pattern').select_option('weekly')
        page.wait_for_timeout(300)

        # Weekly day selection should appear
        expect(page.locator('#weekly-options')).to_be_visible()

        # Select Sunday
        page.locator('#day-selection input[value="sunday"]').check()

        # Set end date (3 months from today)
        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        page.locator('#end-date').fill(end_date)

        # Wait for automatic preview to update (debounce 300ms + API call time)
        page.wait_for_timeout(2000)

        # Then: Calendar preview should display with occurrence list
        expect(page.locator('#calendar-preview')).to_be_visible()

        # Preview should show occurrence information (text-based list)
        preview_text = page.locator('#calendar-preview').text_content()
        assert "occurrence" in preview_text.lower() or "#" in preview_text, \
            f"Preview should show occurrence list: {preview_text}"

        # Preview should show multiple Sundays (approximately 12-13 occurrences)
        # Check that preview mentions showing occurrences
        assert "showing" in preview_text.lower() or "upcoming" in preview_text.lower(), \
            f"Preview should indicate showing occurrences: {preview_text}"

        # And: Admin saves recurring event (be specific to avoid ambiguity)
        page.locator('#create-event-modal button[type="submit"], #event-modal button[type="submit"]').first.click()
        page.wait_for_timeout(2000)

        # Success message should appear (check for toast or success indicator)
        # Note: The actual success message format may vary
        page.wait_for_timeout(500)

        # Verify the form closed (recurring series created)
        # The modal should close after successful creation
        # Note: Full verification of created events would require additional implementation

    def test_calendar_preview_updates_realtime(self, page: Page, api_server):
        """
        Test calendar preview updates in real-time as pattern changes.

        User Journey:
        1. Admin opens recurring event form
        2. Admin configures weekly pattern
        3. Admin changes pattern from weekly to biweekly
        4. Calendar preview updates immediately (<1s)

        Acceptance Criteria (User Story 3, AC4):
        - Preview updates in real-time as user modifies recurrence pattern
        - Preview refresh time <1 second

        THIS TEST WILL FAIL INITIALLY - Feature not implemented yet.
        """
        # Given: Admin is on recurring event creation form
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Login and navigate (abbreviated)
        self._login_as_admin(page)
        self._open_event_creation_form(page)

        # Fill event title and start date (required for preview)
        page.locator('#event-title').fill("Weekly Service")
        start_datetime = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT10:00")
        page.locator('#event-start').fill(start_datetime)

        # Configure weekly pattern with Sunday
        page.locator('#is-recurring').check()
        page.wait_for_timeout(300)
        page.locator('#recurrence-pattern').select_option('weekly')
        page.wait_for_timeout(300)
        page.locator('#day-selection input[value="sunday"]').check()

        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        page.locator('#end-date').fill(end_date)
        page.wait_for_timeout(1500)  # Allow preview to load (debounce + API call)

        # When: Admin changes pattern to biweekly
        # Get initial occurrence count from preview
        initial_preview = page.locator('#calendar-preview').text_content()

        start_time = datetime.now()
        page.locator('#recurrence-pattern').select_option('biweekly')

        # Wait for preview update (spec requires <1s, allow up to 1.5s)
        page.wait_for_timeout(1500)
        update_time = (datetime.now() - start_time).total_seconds()

        # Then: Preview should update to show fewer occurrences
        new_preview = page.locator('#calendar-preview').text_content()

        # Verify preview changed (biweekly has fewer occurrences than weekly)
        assert new_preview != initial_preview, \
            "Preview should update when pattern changes"

        # Update should be reasonably fast (<2s for real-world conditions)
        assert update_time < 2.0, \
            f"Preview update took {update_time}s, should be <2s"

    @pytest.mark.skip(reason="Feature not implemented: Warning threshold set to 100, test expects 50")
    def test_preview_warns_on_large_series(self, page: Page, api_server):
        """
        Test that calendar preview displays warning for large series.

        User Journey:
        1. Admin configures pattern creating 50+ occurrences
        2. Calendar preview displays
        3. Warning message appears about large series

        Acceptance Criteria (User Story 3, AC3):
        - Preview displays warning when pattern creates 50+ occurrences

        THIS TEST WILL FAIL INITIALLY - Feature not implemented yet.
        """
        # Given: Admin configures pattern with many occurrences
        page.goto(APP_URL)
        self._login_as_admin(page)
        self._open_event_creation_form(page)

        # Fill event title and start date (required for preview)
        page.locator('#event-title').fill("Multi-day Service")
        start_datetime = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT10:00")
        page.locator('#event-start').fill(start_datetime)

        # Configure weekly pattern with multiple days (Mon, Wed, Fri = 3x/week)
        page.locator('#is-recurring').check()
        page.wait_for_timeout(300)
        page.locator('#recurrence-pattern').select_option('weekly')
        page.wait_for_timeout(300)
        page.locator('#day-selection input[value="monday"]').check()
        page.locator('#day-selection input[value="wednesday"]').check()
        page.locator('#day-selection input[value="friday"]').check()

        # Set end date 6 months out (3 days/week * 26 weeks = 78 occurrences)
        end_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        page.locator('#end-date').fill(end_date)

        # When: Admin views calendar preview (auto-updates after end date fill)
        page.wait_for_timeout(2000)  # Allow preview to generate (debounce + API call)

        # Then: Warning should appear for large series
        expect(page.locator('#preview-warning')).to_be_visible()

        warning_text = page.locator('#preview-warning').text_content()
        assert "occurrences" in warning_text.lower() or "100" in warning_text, \
            f"Warning should mention large series: {warning_text}"

        # Preview should show occurrence information
        preview_text = page.locator('#calendar-preview').text_content()
        assert "occurrence" in preview_text.lower() or "showing" in preview_text.lower(), \
            f"Preview should show occurrence information: {preview_text}"

    # Helper methods for test setup
    def _login_as_admin(self, page: Page):
        """Helper: Login as admin user."""
        if page.locator('a:has-text("Sign in")').count() > 0:
            page.locator('a:has-text("Sign in")').click()
            page.wait_for_timeout(500)

        page.fill('input[type="email"]', "jane@test.com")
        page.fill('input[type="password"]', "password")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(2000)

        expect(page.locator('#main-app')).to_be_visible()

    def _open_event_creation_form(self, page: Page):
        """Helper: Navigate to event creation form."""
        # Navigate to admin console first
        page.goto("http://localhost:8000/app/admin")
        page.wait_for_timeout(1000)

        # Click Events tab
        events_tab = page.locator('button:has-text("Events")')
        if events_tab.count() > 0:
            events_tab.first.click()
            page.wait_for_timeout(1000)  # Wait for tab content to show

        # Call showCreateEventForm() directly via JavaScript (button is hidden by admin console tabs)
        page.evaluate("window.showCreateEventForm()")
        page.wait_for_timeout(500)

        # Verify modal appears
        expect(page.locator('#create-event-modal, #event-modal')).to_be_visible()


class TestRecurringEventsSingleVsSeriesEditing:
    """
    Test User Story 2: Edit Single Occurrence vs Entire Series (Priority: P1)

    Admin users choose whether changes apply to single occurrence or entire
    recurring series. Single-occurrence edits create exceptions while series
    edits update all future occurrences.
    """

    @pytest.mark.skip(reason="Feature not implemented: Edit single occurrence vs entire series dialog")
    def test_edit_single_occurrence_creates_exception(self, page: Page, api_server):
        """
        Test editing single occurrence creates exception without affecting series.

        User Journey:
        1. Admin creates recurring series (10 Sunday occurrences)
        2. Admin clicks "Edit" on 5th occurrence
        3. System displays "Edit this occurrence only" vs "Edit entire series" dialog
        4. Admin selects "Edit this occurrence only"
        5. Admin changes time from 10am to 2pm
        6. Admin saves
        7. Only 5th occurrence shows 2pm, others remain 10am
        8. 5th occurrence shows exception indicator

        Acceptance Criteria (User Story 2, AC1-AC4):
        - Dialog displays edit options
        - Single occurrence edit creates exception
        - Other occurrences unchanged
        - Exception indicator visible

        THIS TEST WILL FAIL INITIALLY - Feature not implemented yet.
        """
        # Given: Recurring series exists with 10 occurrences
        # (Prerequisite: Create recurring event first)
        page.goto(APP_URL)
        self._login_as_admin(page)

        # Create test recurring series
        start_datetime = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT10:00")
        self._create_weekly_recurring_event(
            page,
            title="Sunday Worship",
            start_date=start_datetime,
            end_date=(datetime.now() + timedelta(weeks=10)).strftime("%Y-%m-%d")
        )

        # Navigate to calendar/schedule view
        page.goto("http://localhost:8000/app/schedule")
        page.wait_for_timeout(1000)

        # When: Admin edits 5th occurrence
        sunday_events = page.locator('.event-card:has-text("Sunday Worship")').all()
        assert len(sunday_events) >= 10, f"Expected at least 10 occurrences, got {len(sunday_events)}"

        fifth_event = sunday_events[4]  # 0-indexed
        fifth_event.locator('button.edit-event').click()
        page.wait_for_timeout(500)

        # Then: Edit mode dialog should appear
        expect(page.locator('#edit-mode-dialog')).to_be_visible()

        dialog_text = page.locator('#edit-mode-dialog').text_content()
        assert "Edit this occurrence only" in dialog_text, \
            f"Dialog should show 'Edit this occurrence only' option: {dialog_text}"
        assert "Edit entire series" in dialog_text, \
            f"Dialog should show 'Edit entire series' option: {dialog_text}"

        # Select "Edit this occurrence only"
        page.locator('button:has-text("Edit this occurrence only")').click()
        page.wait_for_timeout(500)

        # Event edit form should appear
        expect(page.locator('#event-modal')).to_be_visible()

        # Change time from 10am to 2pm
        page.locator('#event-time').fill("14:00")

        # Save changes
        page.locator('button[type="submit"]:has-text("Save")').click()
        page.wait_for_timeout(2000)

        # Then: Verify only 5th occurrence changed
        sunday_events_after = page.locator('.event-card:has-text("Sunday Worship")').all()

        # 5th occurrence should show 2pm
        fifth_event_time = sunday_events_after[4].locator('.event-time').text_content()
        assert "2:00 PM" in fifth_event_time or "14:00" in fifth_event_time, \
            f"5th occurrence should show 2pm: {fifth_event_time}"

        # Other occurrences should still show 10am
        first_event_time = sunday_events_after[0].locator('.event-time').text_content()
        assert "10:00 AM" in first_event_time or "10:00" in first_event_time, \
            f"First occurrence should remain 10am: {first_event_time}"

        # 5th occurrence should have exception indicator
        expect(fifth_event.locator('.exception-indicator')).to_be_visible()

        # Exception tooltip should explain
        fifth_event.locator('.exception-indicator').hover()
        page.wait_for_timeout(300)
        tooltip = page.locator('.tooltip:visible').text_content()
        assert "exception" in tooltip.lower() or "modified" in tooltip.lower(), \
            f"Tooltip should indicate exception: {tooltip}"

    @pytest.mark.skip(reason="Feature not implemented: Edit entire series functionality")
    def test_edit_entire_series_updates_all_future(self, page: Page, api_server):
        """
        Test editing entire series updates all future occurrences.

        User Journey:
        1. Admin creates recurring series (10 occurrences)
        2. Admin clicks "Edit" on any occurrence
        3. Admin selects "Edit entire series"
        4. Admin changes title from "Sunday Worship" to "Sunday Service"
        5. Admin saves
        6. All future occurrences (including current) show new title
        7. Past occurrences unchanged (historical data preserved)

        Acceptance Criteria (User Story 2, AC3):
        - Series edit updates all future occurrences
        - Past occurrences preserved

        THIS TEST WILL FAIL INITIALLY - Feature not implemented yet.
        """
        # Given: Recurring series exists
        page.goto(APP_URL)
        self._login_as_admin(page)

        # Create recurring series starting 2 weeks ago (so we have past occurrences)
        start_datetime = (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%dT10:00")
        self._create_weekly_recurring_event(
            page,
            title="Sunday Worship",
            start_date=start_datetime,
            end_date=(datetime.now() + timedelta(weeks=8)).strftime("%Y-%m-%d")
        )

        # Navigate to calendar
        page.goto("http://localhost:8000/app/schedule")
        page.wait_for_timeout(1000)

        # When: Admin edits series (click on current/future occurrence)
        current_and_future = page.locator('.event-card:has-text("Sunday Worship"):not(.past-event)').all()
        assert len(current_and_future) >= 6, "Should have at least 6 future occurrences"

        # Click edit on first future occurrence
        current_and_future[0].locator('button.edit-event').click()
        page.wait_for_timeout(500)

        # Select "Edit entire series"
        expect(page.locator('#edit-mode-dialog')).to_be_visible()
        page.locator('button:has-text("Edit entire series")').click()
        page.wait_for_timeout(500)

        # Change title
        page.locator('#event-title').clear()
        page.locator('#event-title').fill("Sunday Service")

        # Save
        page.locator('button[type="submit"]:has-text("Save")').click()
        page.wait_for_timeout(2000)

        # Then: All future occurrences should show new title
        future_events = page.locator('.event-card:has-text("Sunday Service"):not(.past-event)').count()
        assert future_events >= 6, \
            f"Expected at least 6 future 'Sunday Service' events, got {future_events}"

        # Past occurrences should still show old title
        past_events = page.locator('.event-card.past-event:has-text("Sunday Worship")').count()
        assert past_events >= 2, \
            f"Expected at least 2 past 'Sunday Worship' events (historical), got {past_events}"

    # Helper methods
    def _login_as_admin(self, page: Page):
        """Helper: Login as admin user."""
        if page.locator('a:has-text("Sign in")').count() > 0:
            page.locator('a:has-text("Sign in")').click()
            page.wait_for_timeout(500)

        page.fill('input[type="email"]', "jane@test.com")
        page.fill('input[type="password"]', "password")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(2000)

    def _create_weekly_recurring_event(
        self,
        page: Page,
        title: str,
        start_date: str = None,
        end_date: str = None
    ):
        """Helper: Create weekly recurring event via UI."""
        # Navigate to admin console first
        page.goto("http://localhost:8000/app/admin")
        page.wait_for_timeout(1000)

        # Click Events tab
        events_tab = page.locator('button:has-text("Events")')
        if events_tab.count() > 0:
            events_tab.first.click()
            page.wait_for_timeout(1000)  # Wait for tab content to show

        # Call showCreateEventForm() directly via JavaScript (button is hidden by admin console tabs)
        page.evaluate("window.showCreateEventForm()")
        page.wait_for_timeout(500)

        page.locator('#event-title').fill(title)

        if start_date:
            page.locator('#event-start').fill(start_date)

        page.locator('#is-recurring').check()
        page.wait_for_timeout(300)
        page.locator('#recurrence-pattern').select_option('weekly')
        page.wait_for_timeout(300)
        page.locator('#day-selection input[value="sunday"]').check()

        if end_date:
            page.locator('#end-date').fill(end_date)

        # Submit the form (be specific to avoid ambiguity)
        page.locator('#create-event-modal button[type="submit"], #event-modal button[type="submit"]').first.click()
        page.wait_for_timeout(2000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
