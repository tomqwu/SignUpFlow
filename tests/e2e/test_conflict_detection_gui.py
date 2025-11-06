"""
E2E tests for Conflict Detection GUI.

Tests:
- View scheduling conflicts
- Resolve conflicts manually
- Auto-detect overlapping assignments
- Conflict resolution suggestions
- Export conflicts report

Priority: HIGH - Schedule validation and conflict management

STATUS: Tests implemented but SKIPPED - Conflict Detection GUI not yet implemented
Backend API complete (api/routers/conflicts.py), frontend pending

Backend API Endpoints:
- POST /api/conflicts/check - Check for conflicts before assignment
  Request: person_id, event_id
  Response: has_conflicts, conflicts[], can_assign

Conflict Types Detected:
- already_assigned: Person already assigned to this event
- time_off: Person has time-off period overlapping with event
- double_booked: Person assigned to another event at the same time

Conflict Response Structure:
- has_conflicts (bool): Whether any conflicts detected
- conflicts (array): List of ConflictType objects
  * type (str): Conflict type (already_assigned, time_off, double_booked)
  * message (str): Human-readable conflict message
  * conflicting_event_id (str, optional): ID of conflicting event
  * start_time (datetime, optional): Conflict start time
  * end_time (datetime, optional): Conflict end time
- can_assign (bool): Whether assignment should be allowed despite conflicts
  * Blocks on: already_assigned, time_off
  * Warns but allows: double_booked

UI Gaps Identified:
- No Conflicts tab/view in admin console (/app/admin)
- No conflicts dashboard display (#conflicts-dashboard, .conflicts-section)
- No conflicts list/table (#conflicts-list, .conflicts-table)
- No conflict detection trigger in event assignment UI
- No conflict warning modal/dialog when assigning
- No manual conflict resolution UI
- No "Resolve" button for each conflict
- No resolution options display (reassign, override, cancel)
- No auto-detect toggle or settings
- No conflict suggestions panel (#conflict-suggestions)
- No suggested resolutions display (alternative people, times)
- No export conflicts button (#export-conflicts)
- No export format options (CSV, PDF)
- No conflict filtering (by type, event, person, date range)
- No conflict sorting (by severity, date, person)
- No conflict visualization (timeline, calendar view)
- No conflict statistics (total conflicts, by type, resolution rate)
- currentOrg not properly initialized in localStorage

Once Conflict Detection GUI is implemented in frontend/js/app-admin.js, unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time
from datetime import datetime, timedelta

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def admin_login(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Login as admin for conflict detection tests."""
    # Setup: Create test organization and admin user
    org = api_client.create_org()
    admin = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Login as admin
    login_via_ui(page, app_config.app_url, admin["email"], admin["password"])
    expect(page.locator('#main-app')).to_be_visible(timeout=10000)

    # Navigate to admin console
    page.goto(f"{app_config.app_url}/app/admin")
    page.wait_for_timeout(1000)

    # Click Conflicts tab (if exists)
    conflicts_tab = page.locator('button:has-text("Conflicts"), button:has-text("Validation"), [data-i18n*="conflicts"]')
    if conflicts_tab.count() > 0:
        conflicts_tab.first.click()
        page.wait_for_timeout(500)

    return page


@pytest.mark.skip(reason="Conflict Detection GUI not implemented - backend API exists but frontend pending")
def test_view_scheduling_conflicts(admin_login: Page):
    """
    Test viewing all detected scheduling conflicts.

    User Journey:
    1. Admin navigates to Conflicts tab
    2. Dashboard displays all detected conflicts
    3. Admin sees conflict list with details (type, person, event, time)
    4. Admin sees conflict counts by type
    5. Admin can filter conflicts by type, person, event
    6. Admin can sort conflicts by date, severity
    """
    page = admin_login

    # Create test data - conflicting assignments
    # Person 1 with time-off period
    person1_response = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create person
            const personResponse = await fetch(`${window.location.origin}/api/people/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: 'Test Volunteer With Time Off',
                    email: 'conflict1@test.com',
                    org_id: currentOrg.id,
                    roles: ['volunteer']
                })
            });

            const person = await personResponse.json();

            // Add time-off period via API
            const today = new Date();
            const nextWeek = new Date(today);
            nextWeek.setDate(nextWeek.getDate() + 7);

            const availResponse = await fetch(`${window.location.origin}/api/availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    person_id: person.id,
                    org_id: currentOrg.id,
                    start_date: today.toISOString().split('T')[0],
                    end_date: nextWeek.toISOString().split('T')[0],
                    reason: 'Vacation'
                })
            });

            return person;
        })();
    """)
    page.wait_for_timeout(500)

    # Create 2 overlapping events for double-booking
    event1_id = f"event_conflict_1_{int(time.time() * 1000)}"
    event2_id = f"event_conflict_2_{int(time.time() * 1000)}"

    for i, event_id in enumerate([event1_id, event2_id]):
        page.evaluate(f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                tomorrow.setHours(10, 0, 0, 0);

                await fetch(`${window.location.origin}/api/events/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        id: '{event_id}',
                        org_id: currentOrg.id,
                        type: 'Worship Service {i+1}',
                        start_time: tomorrow.toISOString(),
                        end_time: new Date(tomorrow.getTime() + 2 * 60 * 60 * 1000).toISOString()
                    }})
                }});
            }})();
        """)
        page.wait_for_timeout(200)

    # Reload to refresh conflicts data
    page.reload()
    page.wait_for_timeout(1000)

    # Navigate to Conflicts tab (if not already there)
    conflicts_tab = page.locator('button:has-text("Conflicts"), button:has-text("Validation"), [data-i18n*="conflicts"]')
    if conflicts_tab.count() > 0:
        conflicts_tab.first.click()
        page.wait_for_timeout(500)
    else:
        # Try navigating directly
        page.goto(f"{app_config.app_url}/app/admin#conflicts")
        page.wait_for_timeout(1000)

    # Verify conflicts dashboard is visible
    conflicts_dashboard = page.locator('#conflicts-dashboard, .conflicts-section, .conflicts-panel')
    expect(conflicts_dashboard).to_be_visible(timeout=5000)

    # Verify conflicts list/table
    conflicts_list = page.locator('#conflicts-list, .conflicts-table, .conflict-items')
    expect(conflicts_list).to_be_visible(timeout=5000)

    # Verify conflict counts by type
    expect(page.locator('text=/Total Conflicts:|Conflicts Found:/')).to_be_visible()
    expect(page.locator('text=/Time-Off Conflicts:|Time Off:/')).to_be_visible()
    expect(page.locator('text=/Double-Booked:|Double Booked:/')).to_be_visible()

    # Verify individual conflict cards/rows
    conflict_items = page.locator('.conflict-item, .conflict-row, [data-conflict-id]')
    expect(conflict_items.first).to_be_visible(timeout=5000)

    # Verify conflict details displayed
    expect(page.locator('text=/Conflict Type:|Type:/')).to_be_visible()
    expect(page.locator('text=/Person:|Volunteer:/')).to_be_visible()
    expect(page.locator('text=/Event:|Service:/')).to_be_visible()
    expect(page.locator('text=/Time:|Date:/')).to_be_visible()

    # Verify filter controls
    filter_dropdown = page.locator('#conflict-filter, select[name="filter"], .filter-type')
    if filter_dropdown.count() > 0:
        expect(filter_dropdown.first).to_be_visible()

        # Try filtering by type
        filter_dropdown.first.select_option(label="Time-Off Conflicts")
        page.wait_for_timeout(500)
        expect(conflicts_list).to_be_visible()

    # Verify sort controls
    sort_dropdown = page.locator('#conflict-sort, select[name="sort"], .sort-by')
    if sort_dropdown.count() > 0:
        expect(sort_dropdown.first).to_be_visible()


@pytest.mark.skip(reason="Conflict Detection GUI not implemented - backend API exists but frontend pending")
def test_resolve_conflicts_manually(admin_login: Page):
    """
    Test manually resolving a conflict.

    User Journey:
    1. Admin views conflict list
    2. Admin selects a specific conflict
    3. Admin clicks "Resolve" button
    4. System shows resolution options (reassign, override, cancel)
    5. Admin chooses resolution action
    6. Admin confirms resolution
    7. Conflict is removed from list
    """
    page = admin_login

    # Create test conflict - person assigned to event with time-off
    conflict_data = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create person
            const personResponse = await fetch(`${window.location.origin}/api/people/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: 'Person To Resolve',
                    email: 'resolve@test.com',
                    org_id: currentOrg.id,
                    roles: ['volunteer']
                })
            });
            const person = await personResponse.json();

            // Create event
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(14, 0, 0, 0);

            const eventResponse = await fetch(`${window.location.origin}/api/events/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    id: 'event_resolve_' + Date.now(),
                    org_id: currentOrg.id,
                    type: 'Service To Resolve',
                    start_time: tomorrow.toISOString(),
                    end_time: new Date(tomorrow.getTime() + 1.5 * 60 * 60 * 1000).toISOString()
                })
            });
            const event = await eventResponse.json();

            // Add time-off overlapping with event
            const availResponse = await fetch(`${window.location.origin}/api/availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    person_id: person.id,
                    org_id: currentOrg.id,
                    start_date: tomorrow.toISOString().split('T')[0],
                    end_date: tomorrow.toISOString().split('T')[0],
                    reason: 'Conflict Test'
                })
            });

            return { person, event };
        })();
    """)
    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find the conflict in list
    conflict_item = page.locator('.conflict-item, .conflict-row').first
    expect(conflict_item).to_be_visible(timeout=5000)

    # Click Resolve button
    resolve_button = conflict_item.locator('button:has-text("Resolve"), button[title="Resolve"]')

    if resolve_button.count() == 0:
        # Try clicking on conflict to reveal resolve option
        conflict_item.click()
        page.wait_for_timeout(300)
        resolve_button = page.locator('button:has-text("Resolve"), button[title="Resolve"]')

    expect(resolve_button.first).to_be_visible(timeout=5000)
    resolve_button.first.click()
    page.wait_for_timeout(500)

    # Verify resolution options modal/dialog
    resolution_dialog = page.locator('#resolution-dialog, .resolution-modal, .resolve-options')
    expect(resolution_dialog).to_be_visible(timeout=5000)

    # Verify resolution options displayed
    expect(page.locator('text=/Reassign to another person|Reassign/')).to_be_visible()
    expect(page.locator('text=/Override conflict|Override/')).to_be_visible()
    expect(page.locator('text=/Cancel assignment|Cancel/')).to_be_visible()

    # Choose cancel assignment option
    cancel_option = page.locator('button:has-text("Cancel assignment"), input[value="cancel"]')
    if cancel_option.count() > 0:
        cancel_option.first.click()
        page.wait_for_timeout(300)

    # Confirm resolution
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Apply"), button[type="submit"]')
    expect(confirm_button.first).to_be_visible()
    confirm_button.first.click()

    page.wait_for_timeout(2000)

    # Verify conflict removed or marked as resolved
    # Either disappears from list or shows "Resolved" status
    resolved_status = page.locator(f'text="Resolved", text="✓", .conflict-resolved')
    # Conflict might be hidden or show resolved status


@pytest.mark.skip(reason="Conflict Detection GUI not implemented - backend API exists but frontend pending")
def test_auto_detect_overlapping_assignments(admin_login: Page):
    """
    Test auto-detection of conflicts when assigning person to event.

    User Journey:
    1. Admin navigates to event assignment view
    2. Admin selects person for assignment
    3. System automatically checks for conflicts via API
    4. If conflict detected, warning modal appears
    5. Modal shows conflict details and resolution options
    6. Admin can choose to proceed or cancel
    7. If blocking conflict (time-off), assignment prevented
    8. If warning conflict (double-booked), admin can override
    """
    page = admin_login

    # Create test data - person with time-off
    test_data = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create person
            const personResponse = await fetch(`${window.location.origin}/api/people/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: 'Auto Detect Person',
                    email: 'autodetect@test.com',
                    org_id: currentOrg.id,
                    roles: ['volunteer']
                })
            });
            const person = await personResponse.json();

            // Create event
            const nextWeek = new Date();
            nextWeek.setDate(nextWeek.getDate() + 7);
            nextWeek.setHours(9, 0, 0, 0);

            const eventResponse = await fetch(`${window.location.origin}/api/events/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    id: 'event_autodetect_' + Date.now(),
                    org_id: currentOrg.id,
                    type: 'Auto Detect Event',
                    start_time: nextWeek.toISOString(),
                    end_time: new Date(nextWeek.getTime() + 2 * 60 * 60 * 1000).toISOString()
                })
            });
            const event = await eventResponse.json();

            // Add time-off overlapping with event
            await fetch(`${window.location.origin}/api/availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    person_id: person.id,
                    org_id: currentOrg.id,
                    start_date: nextWeek.toISOString().split('T')[0],
                    end_date: nextWeek.toISOString().split('T')[0],
                    reason: 'Auto Detect Test'
                })
            });

            return { person, event };
        })();
    """)
    page.wait_for_timeout(1000)

    # Navigate to Events tab
    page.goto("http://localhost:8000/app/admin#events")
    page.wait_for_timeout(1000)

    events_tab = page.locator('button:has-text("Events"), [data-i18n*="events"]')
    if events_tab.count() > 0:
        events_tab.first.click()
        page.wait_for_timeout(500)

    # Find the test event
    event_card = page.locator('text="Auto Detect Event"').first
    if event_card.count() > 0:
        expect(event_card).to_be_visible(timeout=5000)

        # Click to assign person
        event_card.click()
        page.wait_for_timeout(500)

        # Look for assign button
        assign_button = page.locator('button:has-text("Assign"), button:has-text("Add Person")')
        if assign_button.count() > 0:
            assign_button.first.click()
            page.wait_for_timeout(300)

            # Select the person with time-off
            person_select = page.locator('select[name="person"], #person-select, .person-dropdown')
            if person_select.count() > 0:
                # Select option containing "Auto Detect Person"
                person_select.first.select_option(label="Auto Detect Person")
                page.wait_for_timeout(500)

            # Try to submit assignment - should trigger conflict detection
            submit_button = page.locator('button:has-text("Assign"), button[type="submit"]')
            if submit_button.count() > 0:
                submit_button.first.click()
                page.wait_for_timeout(1000)

                # Verify conflict warning modal appears
                conflict_modal = page.locator('#conflict-modal, .conflict-warning, .conflict-dialog')
                expect(conflict_modal).to_be_visible(timeout=5000)

                # Verify conflict details shown
                expect(page.locator('text=/Conflict Detected|Scheduling Conflict/')).to_be_visible()
                expect(page.locator('text=/time-off|Time Off|vacation/')).to_be_visible()
                expect(page.locator('text="Auto Detect Person"')).to_be_visible()

                # Verify blocking message (cannot proceed)
                expect(page.locator('text=/Cannot assign|Assignment blocked/')).to_be_visible()

                # Only option should be Cancel
                cancel_button = page.locator('button:has-text("Cancel"), button:has-text("Close")')
                expect(cancel_button.first).to_be_visible()


@pytest.mark.skip(reason="Conflict Detection GUI not implemented - backend API exists but frontend pending")
def test_conflict_resolution_suggestions(admin_login: Page):
    """
    Test viewing conflict resolution suggestions.

    User Journey:
    1. Admin views a specific conflict
    2. System displays suggested resolutions
    3. Suggestions include:
       - Alternative people who are available
       - Alternative time slots for the event
       - Automatic reassignment options
    4. Admin can select a suggestion
    5. System applies the suggested resolution
    """
    page = admin_login

    # Create conflict scenario with multiple volunteers
    test_data = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create conflicted person
            const conflictedPersonResponse = await fetch(`${window.location.origin}/api/people/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: 'Conflicted Volunteer',
                    email: 'conflicted@test.com',
                    org_id: currentOrg.id,
                    roles: ['volunteer']
                })
            });
            const conflictedPerson = await conflictedPersonResponse.json();

            // Create 2 alternative volunteers (available)
            const alternatives = [];
            for (let i = 0; i < 2; i++) {
                const altResponse = await fetch(`${window.location.origin}/api/people/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        name: `Alternative Volunteer ${i+1}`,
                        email: `alternative${i+1}@test.com`,
                        org_id: currentOrg.id,
                        roles: ['volunteer']
                    })
                });
                alternatives.push(await altResponse.json());
            }

            // Create event
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(11, 0, 0, 0);

            const eventResponse = await fetch(`${window.location.origin}/api/events/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    id: 'event_suggestions_' + Date.now(),
                    org_id: currentOrg.id,
                    type: 'Service With Suggestions',
                    start_time: tomorrow.toISOString(),
                    end_time: new Date(tomorrow.getTime() + 1.5 * 60 * 60 * 1000).toISOString()
                })
            });
            const event = await eventResponse.json();

            // Add time-off for conflicted person
            await fetch(`${window.location.origin}/api/availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    person_id: conflictedPerson.id,
                    org_id: currentOrg.id,
                    start_date: tomorrow.toISOString().split('T')[0],
                    end_date: tomorrow.toISOString().split('T')[0],
                    reason: 'Suggestions Test'
                })
            });

            return { conflictedPerson, alternatives, event };
        })();
    """)
    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Navigate to Conflicts tab
    conflicts_tab = page.locator('button:has-text("Conflicts"), [data-i18n*="conflicts"]')
    if conflicts_tab.count() > 0:
        conflicts_tab.first.click()
        page.wait_for_timeout(500)

    # Find conflict
    conflict_item = page.locator('text="Conflicted Volunteer"').first
    if conflict_item.count() > 0:
        expect(conflict_item).to_be_visible(timeout=5000)
        conflict_item.click()
        page.wait_for_timeout(500)

    # Verify suggestions panel/section
    suggestions_panel = page.locator('#conflict-suggestions, .suggestions-panel, .resolution-suggestions')
    expect(suggestions_panel).to_be_visible(timeout=5000)

    # Verify suggested alternatives section
    expect(page.locator('text=/Suggested Alternatives|Alternative People|Available Volunteers/')).to_be_visible()

    # Verify alternative people listed
    expect(page.locator('text="Alternative Volunteer 1"')).to_be_visible()
    expect(page.locator('text="Alternative Volunteer 2"')).to_be_visible()

    # Verify "Select" or "Apply" button for each suggestion
    select_buttons = page.locator('button:has-text("Select"), button:has-text("Apply"), button:has-text("Use This")')
    if select_buttons.count() > 0:
        expect(select_buttons.first).to_be_visible()

        # Click first suggestion
        select_buttons.first.click()
        page.wait_for_timeout(500)

        # Verify confirmation dialog
        confirm_dialog = page.locator('#confirm-suggestion, .confirm-dialog')
        if confirm_dialog.count() > 0:
            expect(confirm_dialog).to_be_visible()

            confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Apply")')
            if confirm_button.count() > 0:
                confirm_button.first.click()
                page.wait_for_timeout(1000)


@pytest.mark.skip(reason="Conflict Detection GUI not implemented - backend API exists but frontend pending")
def test_export_conflicts_report(admin_login: Page):
    """
    Test exporting conflicts report.

    User Journey:
    1. Admin views conflicts dashboard
    2. Admin clicks "Export" button
    3. System shows export format options (CSV, PDF)
    4. Admin selects format
    5. Export file downloads
    6. Report contains all conflict details:
       - Conflict type
       - Person name/email
       - Event name/time
       - Conflict reason
       - Resolution status
    """
    page = admin_login

    # Create multiple conflicts for export
    for i in range(3):
        page.evaluate(f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                // Create person
                const personResponse = await fetch(`${window.location.origin}/api/people/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        name: 'Export Test Person {i+1}',
                        email: 'export{i+1}@test.com',
                        org_id: currentOrg.id,
                        roles: ['volunteer']
                    }})
                }});
                const person = await personResponse.json();

                // Create event
                const future = new Date();
                future.setDate(future.getDate() + {i+1});
                future.setHours(13, 0, 0, 0);

                const eventResponse = await fetch(`${window.location.origin}/api/events/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        id: 'event_export_{i}_' + Date.now(),
                        org_id: currentOrg.id,
                        type: 'Export Test Event {i+1}',
                        start_time: future.toISOString(),
                        end_time: new Date(future.getTime() + 2 * 60 * 60 * 1000).toISOString()
                    }})
                }});

                // Add time-off
                await fetch(`${window.location.origin}/api/availability', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        person_id: person.id,
                        org_id: currentOrg.id,
                        start_date: future.toISOString().split('T')[0],
                        end_date: future.toISOString().split('T')[0],
                        reason: 'Export Test'
                    }})
                }});
            }})();
        """)
        page.wait_for_timeout(300)

    # Reload to refresh conflicts
    page.reload()
    page.wait_for_timeout(1000)

    # Navigate to Conflicts tab
    conflicts_tab = page.locator('button:has-text("Conflicts"), [data-i18n*="conflicts"]')
    if conflicts_tab.count() > 0:
        conflicts_tab.first.click()
        page.wait_for_timeout(500)

    # Find Export button
    export_button = page.locator('button:has-text("Export"), button:has-text("Download"), #export-conflicts')
    expect(export_button.first).to_be_visible(timeout=5000)
    export_button.first.click()
    page.wait_for_timeout(500)

    # Verify export format options
    format_dropdown = page.locator('select[name="format"], #export-format')
    if format_dropdown.count() > 0:
        expect(format_dropdown.first).to_be_visible()

        # Verify CSV and PDF options
        csv_option = page.locator('option:has-text("CSV")')
        pdf_option = page.locator('option:has-text("PDF")')
        expect(csv_option).to_be_visible()
        expect(pdf_option).to_be_visible()

        # Select CSV
        format_dropdown.first.select_option(label="CSV")
        page.wait_for_timeout(300)

    # Confirm export
    confirm_export = page.locator('button:has-text("Export"), button:has-text("Download"), button[type="submit"]')
    if confirm_export.count() > 0:
        # Expect download
        with page.expect_download() as download_info:
            confirm_export.first.click()
            page.wait_for_timeout(1000)

        download = download_info.value
        # Verify filename contains 'conflicts'
        assert 'conflict' in download.suggested_filename.lower()

    # Verify success message
    success_message = page.locator('text=/Export completed|Download started|Successfully exported/')
    if success_message.count() > 0:
        expect(success_message.first).to_be_visible(timeout=5000)
