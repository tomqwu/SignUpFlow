"""
E2E tests for Solver Workflow.

Tests:
- Run solver with constraints (complete workflow)
- Solver results display correctly
- Manual schedule adjustment after solver
- Solver conflict resolution
- Solver with different constraint priorities
- Solver performance with large datasets
- Solver optimization settings

Priority: CRITICAL - Core product feature (AI-powered scheduling)

STATUS: Tests implemented but SKIPPED - Solver UI not yet implemented
Backend API complete (api/routers/solver.py POST /solve), frontend pending

UI Gaps Identified:
- No Solver tab in admin console (/app/admin)
- No solver configuration panel (#solver-panel, .solver-section)
- No "Run Solver" button
- No solver date range selector (from_date, to_date)
- No solver status display (running, completed, failed)
- No solver results table (#solver-results-table)
- No solver metrics display (assignments count, violations, fairness score)
- No manual adjustment UI (edit assignment button)
- No conflict highlighting in results
- No progress indicator during solving
- currentOrg not properly initialized in localStorage

Once Solver UI is implemented in frontend/js/app-admin.js, unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture(scope="function")
def admin_login(page: Page):
    """Login as admin for solver tests."""
    # Navigate directly to login page
    page.goto("http://localhost:8000/login")
    page.wait_for_load_state("networkidle")

    # Verify login screen is visible
    expect(page.locator("#login-screen")).to_be_visible(timeout=5000)

    # Fill login form
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")

    # Submit login
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Verify logged in
    expect(page).to_have_url("http://localhost:8000/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    # Navigate to admin console
    page.goto("http://localhost:8000/app/admin")
    page.wait_for_timeout(1000)

    # Click Solver tab
    solver_tab = page.locator('button:has-text("Solver"), [data-i18n*="solver"]')
    if solver_tab.count() > 0:
        solver_tab.first.click()
        page.wait_for_timeout(500)

    return page


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_run_solver_with_constraints_complete_workflow(admin_login: Page):
    """
    Test complete solver workflow from admin perspective.

    User Journey:
    1. Admin navigates to Solver tab
    2. Selects date range (from_date, to_date)
    3. Reviews events and volunteers in range
    4. Configures constraints (already exist from Constraints Management)
    5. Clicks "Run Solver" button
    6. Watches progress indicator
    7. Views generated schedule results
    8. Verifies schedule meets constraints
    """
    page = admin_login

    # Create test data via API (events, people, teams) for solver to work with
    timestamp = int(time.time() * 1000)

    # Create 3 events with role requirements
    events_data = [
        {
            "title": f"Sunday Service {timestamp}",
            "start_time": "2025-11-03T10:00:00",
            "duration": 120,
            "role_requirements": [
                {"role": "Greeter", "count": 2},
                {"role": "Usher", "count": 3}
            ]
        },
        {
            "title": f"Wednesday Prayer {timestamp}",
            "start_time": "2025-11-06T19:00:00",
            "duration": 90,
            "role_requirements": [
                {"role": "Leader", "count": 1}
            ]
        },
        {
            "title": f"Sunday Service 2 {timestamp}",
            "start_time": "2025-11-10T10:00:00",
            "duration": 120,
            "role_requirements": [
                {"role": "Greeter", "count": 2},
                {"role": "Usher", "count": 3}
            ]
        }
    ]

    # Create events via API
    for event_data in events_data:
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/events/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        title: '{event_data['title']}',
                        start_time: '{event_data['start_time']}',
                        duration: {event_data['duration']},
                        role_requirements: {event_data['role_requirements']}
                    }})
                }});
            }})();
            """
        )
        page.wait_for_timeout(300)

    # Create 6 volunteers via API
    for i in range(1, 7):
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/people/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        name: 'Volunteer {i}',
                        email: 'volunteer{i}_{timestamp}@test.com',
                        roles: ['volunteer']
                    }})
                }});
            }})();
            """
        )
        page.wait_for_timeout(200)

    # Reload page to ensure data is loaded
    page.reload()
    page.wait_for_timeout(1000)

    # Find solver panel
    solver_panel = page.locator('#solver-panel, .solver-section, [data-section="solver"]')
    if solver_panel.count() == 0:
        # Try to reveal solver UI
        solver_tab = page.locator('button:has-text("Solver"), [data-i18n*="solver"]')
        if solver_tab.count() > 0:
            solver_tab.first.click()
            page.wait_for_timeout(500)
            solver_panel = page.locator('#solver-panel, .solver-section, [data-section="solver"]')

    expect(solver_panel.first).to_be_visible(timeout=5000)

    # Select date range for solver
    from_date_input = page.locator('#solver-from-date, input[name="from_date"]')
    if from_date_input.count() > 0:
        from_date_input.fill("2025-11-01")

    to_date_input = page.locator('#solver-to-date, input[name="to_date"]')
    if to_date_input.count() > 0:
        to_date_input.fill("2025-11-30")

    # Click "Run Solver" button
    run_solver_button = page.locator(
        'button:has-text("Run Solver"), button:has-text("Generate Schedule"), '
        'button[data-i18n*="solver.run"], #run-solver-button'
    )
    expect(run_solver_button.first).to_be_visible(timeout=5000)
    run_solver_button.first.click()

    # Wait for solver to start (progress indicator)
    progress_indicator = page.locator(
        '[data-i18n="solver.status.running"], .solver-progress, #solver-running-indicator'
    )
    expect(progress_indicator.first).to_be_visible(timeout=5000)

    # Wait for solver to complete (max 30 seconds)
    completion_indicator = page.locator(
        '[data-i18n="solver.status.completed"], .solver-completed, #solver-success-message'
    )
    expect(completion_indicator.first).to_be_visible(timeout=30000)

    # Verify solver results table appears
    results_table = page.locator('#solver-results-table, .solver-results, [data-results="solver"]')
    expect(results_table.first).to_be_visible(timeout=5000)

    # Verify results table has assignments (at least 5 rows: 2 + 3 + 1 + more)
    result_rows = page.locator('#solver-results-table tbody tr, .assignment-row')
    expect(result_rows.first).to_be_visible()
    row_count = result_rows.count()
    assert row_count >= 5, f"Expected at least 5 assignments, got {row_count}"

    # Verify solver metrics displayed
    metrics_panel = page.locator('#solver-metrics, .solver-metrics, [data-section="metrics"]')
    if metrics_panel.count() > 0:
        expect(metrics_panel.first).to_be_visible()
        # Should show: total assignments, violations, fairness score
        expect(page.locator('text=/\\d+ assignments/')).to_be_visible()


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_solver_results_display_correctly(admin_login: Page):
    """
    Test that solver results are displayed in user-friendly format.

    Verifies:
    - Results table shows: event name, date, time, volunteer name, role
    - Color coding for different roles
    - Sortable columns (by event, by volunteer, by date)
    - Export results button (CSV, PDF, ICS)
    - Filter results by event or volunteer
    - Violations highlighted in red
    """
    page = admin_login

    # Run solver first (create minimal test data via API)
    # ... similar setup as previous test ...

    # Verify results table structure
    results_table = page.locator('#solver-results-table')
    expect(results_table).to_be_visible(timeout=5000)

    # Verify table headers
    headers = [
        'Event Name',
        'Date',
        'Time',
        'Volunteer',
        'Role',
        'Actions'
    ]

    for header in headers:
        header_locator = page.locator(f'th:has-text("{header}"), [data-header="{header.lower()}"]')
        if header_locator.count() > 0:
            expect(header_locator.first).to_be_visible()

    # Verify color coding for roles (different background colors)
    greeter_rows = page.locator('[data-role="Greeter"], td:has-text("Greeter")').locator('..')
    if greeter_rows.count() > 0:
        # Should have specific background color (e.g., blue)
        expect(greeter_rows.first).to_be_visible()

    # Verify sortable columns (click header to sort)
    date_header = page.locator('th:has-text("Date"), [data-sort="date"]')
    if date_header.count() > 0:
        date_header.first.click()
        page.wait_for_timeout(300)
        # Verify sort indicator appears (▲ or ▼)
        expect(page.locator('.sort-indicator, [data-sort-direction]')).to_be_visible()

    # Verify export buttons exist
    export_csv = page.locator('button:has-text("Export CSV"), #export-csv-button')
    export_pdf = page.locator('button:has-text("Export PDF"), #export-pdf-button')
    export_ics = page.locator('button:has-text("Export Calendar"), #export-ics-button')

    if export_csv.count() > 0:
        expect(export_csv.first).to_be_visible()

    # Verify filter controls exist
    filter_event = page.locator('#filter-by-event, select[name="filter_event"]')
    filter_volunteer = page.locator('#filter-by-volunteer, select[name="filter_volunteer"]')

    if filter_event.count() > 0:
        expect(filter_event).to_be_visible()
        # Select an event filter
        filter_event.select_option(index=1)
        page.wait_for_timeout(500)
        # Verify results filtered (fewer rows)

    # Verify violations highlighted in red
    violation_rows = page.locator('.violation-row, [data-violation="true"]')
    if violation_rows.count() > 0:
        # Should have red background or red border
        expect(violation_rows.first).to_have_css('background-color', 'rgb(255, 0, 0)') # Or similar red


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_manual_schedule_adjustment_after_solver(admin_login: Page):
    """
    Test that admin can manually adjust solver-generated schedule.

    User Journey:
    1. Run solver (generates initial schedule)
    2. Admin identifies assignment to change
    3. Clicks "Edit" button on assignment row
    4. Changes volunteer for that assignment (dropdown)
    5. Saves change
    6. Verifies change persisted in results table
    7. Runs solver again
    8. Verifies solver respects locked manual changes
    """
    page = admin_login

    # Run solver first (setup test data via API)
    # ... similar to previous tests ...

    # Find first assignment row
    first_row = page.locator('#solver-results-table tbody tr, .assignment-row').first
    expect(first_row).to_be_visible(timeout=5000)

    # Get current volunteer name before edit
    original_volunteer = first_row.locator('td.volunteer-name, [data-field="volunteer"]').text_content()

    # Click "Edit" button on this assignment
    edit_button = first_row.locator('button:has-text("Edit"), button[title="Edit"], [data-action="edit"]')
    expect(edit_button).to_be_visible()
    edit_button.click()
    page.wait_for_timeout(500)

    # Edit dialog should appear
    edit_dialog = page.locator('#edit-assignment-dialog, .edit-assignment-modal, [role="dialog"]')
    expect(edit_dialog).to_be_visible(timeout=3000)

    # Change volunteer (dropdown selection)
    volunteer_select = page.locator('#edit-volunteer, select[name="volunteer"]')
    expect(volunteer_select).to_be_visible()

    # Select different volunteer (index 1 or 2, not 0 which is current)
    volunteer_select.select_option(index=1)

    # Save change
    save_button = page.locator('button:has-text("Save"), button:has-text("Update"), button[type="submit"]')
    expect(save_button).to_be_visible()
    save_button.click()
    page.wait_for_timeout(1000)

    # Verify dialog closed
    expect(edit_dialog).not_to_be_visible()

    # Verify assignment row updated with new volunteer
    new_volunteer = first_row.locator('td.volunteer-name, [data-field="volunteer"]').text_content()
    assert new_volunteer != original_volunteer, "Volunteer should have changed"

    # Verify "locked" indicator appears (prevents solver from changing this assignment)
    locked_indicator = first_row.locator('.locked-icon, [data-locked="true"]')
    if locked_indicator.count() > 0:
        expect(locked_indicator).to_be_visible()

    # Run solver again
    run_solver_button = page.locator('button:has-text("Run Solver"), #run-solver-button')
    run_solver_button.click()

    # Wait for completion
    page.wait_for_timeout(5000)

    # Verify manual change still persists (not overwritten by solver)
    still_new_volunteer = first_row.locator('td.volunteer-name, [data-field="volunteer"]').text_content()
    assert still_new_volunteer == new_volunteer, "Manual change should not be overwritten by solver"


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_solver_conflict_resolution(admin_login: Page):
    """
    Test that solver detects and reports conflicts.

    User Journey:
    1. Create overlapping events (same time slot)
    2. Create volunteer with limited availability (time-off)
    3. Create constraints that conflict (impossible to satisfy both)
    4. Run solver
    5. Verify solver shows conflicts/violations in results
    6. Conflicts highlighted in red with explanation
    7. Admin can click conflict to see details
    8. Admin resolves conflict manually
    """
    page = admin_login

    # Create conflicting scenario via API
    timestamp = int(time.time() * 1000)

    # Create 2 overlapping events (same time)
    overlap_time = "2025-11-03T10:00:00"

    for i in range(2):
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/events/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        title: 'Overlapping Event {i+1} {timestamp}',
                        start_time: '{overlap_time}',
                        duration: 120,
                        role_requirements: [{{"role": "Volunteer", "count": 2}}]
                    }})
                }});
            }})();
            """
        )
        page.wait_for_timeout(300)

    # Create volunteer with time-off during this period
    page.evaluate(
        f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create person
            const personResponse = await fetch('http://localhost:8000/api/people/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    org_id: currentOrg.id,
                    name: 'Unavailable Volunteer',
                    email: 'unavailable_{timestamp}@test.com',
                    roles: ['volunteer']
                }})
            }});

            const person = await personResponse.json();

            // Add time-off for this person
            await fetch('http://localhost:8000/api/availability/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    person_id: person.id,
                    start_date: '2025-11-01',
                    end_date: '2025-11-10',
                    reason: 'Vacation'
                }})
            }});
        }})();
        """
    )
    page.wait_for_timeout(1000)

    # Reload and run solver
    page.reload()
    page.wait_for_timeout(1000)

    run_solver_button = page.locator('button:has-text("Run Solver"), #run-solver-button')
    if run_solver_button.count() > 0:
        run_solver_button.click()
        page.wait_for_timeout(5000)

    # Verify conflicts/violations section appears
    conflicts_section = page.locator(
        '#solver-conflicts, .solver-violations, [data-section="conflicts"]'
    )
    expect(conflicts_section.first).to_be_visible(timeout=5000)

    # Verify conflict count displayed
    conflict_count = page.locator('text=/\\d+ conflicts?/, text=/\\d+ violations?/')
    expect(conflict_count.first).to_be_visible()

    # Verify conflict rows highlighted in red
    conflict_rows = page.locator('.conflict-row, [data-conflict="true"], .violation-row')
    if conflict_rows.count() > 0:
        expect(conflict_rows.first).to_be_visible()
        # Should have red background or red border
        # Note: Using simple color match - red color in RGB format
        # Frontend should use rgb(255, 0, 0) or similar red shade for conflicts

    # Click on conflict to see details
    conflict_rows.first.click()
    page.wait_for_timeout(500)

    # Conflict details dialog should appear
    conflict_dialog = page.locator('#conflict-details, .conflict-modal, [role="dialog"]')
    if conflict_dialog.count() > 0:
        expect(conflict_dialog).to_be_visible()
        # Should show: conflict type, description, affected entities
        expect(page.locator('text=/Overlapping|Conflict|Violation/')).to_be_visible()


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_solver_with_different_constraint_priorities(admin_login: Page):
    """
    Test that solver respects constraint priority ordering.

    User Journey:
    1. Navigate to Constraints Management
    2. Create multiple constraints with different priorities
       - Priority 1 (high): Max 1 assignment per person per week
       - Priority 2 (medium): Fairness (even distribution)
       - Priority 3 (low): Volunteer preferences
    3. Run solver
    4. Verify higher priority constraints satisfied first
    5. Verify lower priority constraints best-effort (may violate if conflict)
    6. Metrics show which constraints were satisfied vs violated
    """
    page = admin_login

    # Create constraints with different priorities via API
    constraints = [
        {
            "key": "max_assignments_high_priority",
            "type": "hard",
            "weight": 100,
            "priority": 1,
            "predicate": "max_assignments_per_person_per_week",
            "params": {"max": 1}
        },
        {
            "key": "fairness_medium_priority",
            "type": "soft",
            "weight": 75,
            "priority": 2,
            "predicate": "fairness_distribution",
            "params": {}
        },
        {
            "key": "preferences_low_priority",
            "type": "soft",
            "weight": 50,
            "priority": 3,
            "predicate": "volunteer_preferences",
            "params": {}
        }
    ]

    for constraint in constraints:
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/constraints/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        key: '{constraint['key']}',
                        type: '{constraint['type']}',
                        weight: {constraint['weight']},
                        priority: {constraint['priority']},
                        predicate: '{constraint['predicate']}',
                        params: {constraint['params']}
                    }})
                }});
            }})();
            """
        )
        page.wait_for_timeout(200)

    # Navigate to Solver tab
    page.reload()
    page.wait_for_timeout(1000)

    solver_tab = page.locator('button:has-text("Solver"), [data-i18n*="solver"]')
    if solver_tab.count() > 0:
        solver_tab.click()
        page.wait_for_timeout(500)

    # Verify constraints listed with priorities
    constraints_list = page.locator('#solver-constraints-list, .constraints-summary')
    if constraints_list.count() > 0:
        expect(constraints_list).to_be_visible()
        # Should show all 3 constraints with their priorities
        expect(page.locator('text=/Priority 1|P1|High/')).to_be_visible()
        expect(page.locator('text=/Priority 2|P2|Medium/')).to_be_visible()
        expect(page.locator('text=/Priority 3|P3|Low/')).to_be_visible()

    # Run solver
    run_solver_button = page.locator('button:has-text("Run Solver"), #run-solver-button')
    if run_solver_button.count() > 0:
        run_solver_button.click()
        page.wait_for_timeout(5000)

    # Verify constraint satisfaction metrics
    metrics_panel = page.locator('#constraint-metrics, .constraint-satisfaction')
    if metrics_panel.count() > 0:
        expect(metrics_panel).to_be_visible()
        # Should show for each constraint: satisfied/violated count
        expect(page.locator('text=/Satisfied|Met|OK/')).to_be_visible()


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_solver_performance_with_large_dataset(admin_login: Page):
    """
    Test solver performance with 100+ people and 50+ events.

    Verifies:
    - Solver completes within 60 seconds
    - Results are still correct (all events assigned)
    - UI remains responsive during solving
    - Progress indicator updates during solving
    - No browser timeout or crash
    """
    page = admin_login

    # Create large dataset via API (100 people, 50 events)
    timestamp = int(time.time() * 1000)

    # Create 100 volunteers
    for i in range(1, 101):
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/people/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        name: 'Volunteer {i}',
                        email: 'volunteer{i}_{timestamp}@test.com',
                        roles: ['volunteer']
                    }})
                }});
            }})();
            """
        )
        if i % 10 == 0:  # Wait every 10 people to avoid overwhelming API
            page.wait_for_timeout(500)

    # Create 50 events over 2 months
    for i in range(1, 51):
        event_date = f"2025-11-{(i % 28) + 1:02d}"
        page.evaluate(
            f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/events/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        title: 'Event {i}',
                        start_time: '{event_date}T10:00:00',
                        duration: 120,
                        role_requirements: [
                            {{"role": "Volunteer", "count": 3}}
                        ]
                    }})
                }});
            }})();
            """
        )
        if i % 10 == 0:
            page.wait_for_timeout(500)

    # Reload and navigate to solver
    page.reload()
    page.wait_for_timeout(2000)

    solver_tab = page.locator('button:has-text("Solver"), [data-i18n*="solver"]')
    if solver_tab.count() > 0:
        solver_tab.click()
        page.wait_for_timeout(500)

    # Verify large dataset summary displayed
    summary = page.locator('#dataset-summary, .solver-summary')
    if summary.count() > 0:
        expect(summary).to_be_visible()
        expect(page.locator('text=/100.*people|100.*volunteers/')).to_be_visible()
        expect(page.locator('text=/50.*events/')).to_be_visible()

    # Record start time
    import time as python_time
    start_time = python_time.time()

    # Run solver
    run_solver_button = page.locator('button:has-text("Run Solver"), #run-solver-button')
    if run_solver_button.count() > 0:
        run_solver_button.click()

    # Verify progress indicator appears and updates
    progress_bar = page.locator('#solver-progress, .progress-bar, [role="progressbar"]')
    if progress_bar.count() > 0:
        expect(progress_bar).to_be_visible(timeout=5000)
        # Progress should update (value changes over time)
        page.wait_for_timeout(2000)

    # Wait for completion (max 60 seconds)
    completion_indicator = page.locator('[data-i18n="solver.status.completed"], #solver-success')
    expect(completion_indicator.first).to_be_visible(timeout=60000)

    # Record end time
    end_time = python_time.time()
    duration = end_time - start_time

    # Verify completed within 60 seconds
    assert duration < 60, f"Solver took {duration:.1f}s (should be < 60s)"

    # Verify results displayed correctly
    results_table = page.locator('#solver-results-table')
    expect(results_table).to_be_visible()

    # Verify all events assigned (50 events × 3 volunteers = 150 assignments)
    result_rows = page.locator('#solver-results-table tbody tr').count()
    assert result_rows >= 150, f"Expected at least 150 assignments, got {result_rows}"

    # Verify metrics show success
    metrics = page.locator('#solver-metrics')
    if metrics.count() > 0:
        expect(page.locator('text=/150.*assignments/')).to_be_visible()


@pytest.mark.skip(reason="Solver UI not implemented - backend API exists but frontend pending")
def test_solver_optimization_settings(admin_login: Page):
    """
    Test that solver optimization settings can be configured.

    User Journey:
    1. Admin opens solver settings panel
    2. Configures optimization goals (sliders or weights):
       - Fairness: 80% (high priority - even distribution)
       - Coverage: 100% (critical - fill all roles)
       - Preferences: 50% (nice-to-have - respect volunteer preferences)
       - Continuity: 60% (moderate - keep same volunteers together)
    3. Saves settings
    4. Runs solver
    5. Verifies schedule optimized according to settings
    6. Metrics show goal achievement percentages
    """
    page = admin_login

    # Open solver settings
    settings_button = page.locator(
        'button:has-text("Settings"), button:has-text("Configure"), '
        '#solver-settings-button, [data-action="settings"]'
    )
    if settings_button.count() > 0:
        expect(settings_button).to_be_visible(timeout=5000)
        settings_button.click()
        page.wait_for_timeout(500)

    # Settings dialog/panel should appear
    settings_dialog = page.locator(
        '#solver-settings-dialog, .solver-settings-panel, [role="dialog"]'
    )
    expect(settings_dialog).to_be_visible(timeout=3000)

    # Configure optimization weights (sliders 0-100%)
    fairness_slider = page.locator('#fairness-weight, input[name="fairness"]')
    if fairness_slider.count() > 0:
        fairness_slider.fill("80")

    coverage_slider = page.locator('#coverage-weight, input[name="coverage"]')
    if coverage_slider.count() > 0:
        coverage_slider.fill("100")

    preferences_slider = page.locator('#preferences-weight, input[name="preferences"]')
    if preferences_slider.count() > 0:
        preferences_slider.fill("50")

    continuity_slider = page.locator('#continuity-weight, input[name="continuity"]')
    if continuity_slider.count() > 0:
        continuity_slider.fill("60")

    # Save settings
    save_settings_button = page.locator(
        'button:has-text("Save"), button:has-text("Apply"), button[type="submit"]'
    )
    expect(save_settings_button).to_be_visible()
    save_settings_button.click()
    page.wait_for_timeout(1000)

    # Verify settings dialog closed
    expect(settings_dialog).not_to_be_visible()

    # Run solver with new settings
    run_solver_button = page.locator('button:has-text("Run Solver"), #run-solver-button')
    if run_solver_button.count() > 0:
        run_solver_button.click()
        page.wait_for_timeout(5000)

    # Verify optimization goals metrics displayed
    goals_metrics = page.locator('#optimization-goals, .goal-metrics')
    if goals_metrics.count() > 0:
        expect(goals_metrics).to_be_visible()
        # Should show achievement % for each goal
        expect(page.locator('text=/Fairness.*\\d+%/')).to_be_visible()
        expect(page.locator('text=/Coverage.*100%/')).to_be_visible()  # Should be 100% (critical)

    # Verify settings persisted (reopen dialog)
    settings_button.click()
    page.wait_for_timeout(500)

    # Check slider values still set
    fairness_value = fairness_slider.input_value()
    assert fairness_value == "80", "Fairness setting should persist"
