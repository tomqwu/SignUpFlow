"""
E2E tests for Solver Workflow.

Tests the complete user journey for running the OR-Tools constraint solver:
- Run solver with constraints
- View solver results
- Manual schedule adjustments
- Solver conflict resolution
- Solver with different constraint priorities
- Solver performance with large datasets
- Solver optimization settings

Priority: CRITICAL - Core product feature with zero E2E coverage
"""

import pytest
from playwright.sync_api import Page, expect
import time


def test_run_solver_with_constraints_complete_workflow(page: Page):
    """
    Test complete solver workflow from admin perspective.

    User Journey:
    1. Admin logs in
    2. Creates events requiring volunteers
    3. Creates volunteers and assigns to teams
    4. Adds constraints (max assignments per person, fairness)
    5. Runs solver
    6. Views generated schedule
    7. Verifies schedule meets constraints
    """
    # Step 1: Admin login
    page.goto("http://localhost:8000/")
    page.locator('button[data-i18n="auth.get_started"]').click()

    # Fill signup form
    page.locator('#signup-name').fill("Solver Admin")
    page.locator('#signup-email').fill(f"solver_admin_{int(time.time())}@test.com")
    page.locator('#signup-password').fill("password123")
    page.locator('#signup-org-name').fill(f"Solver Test Org {int(time.time())}")

    # Submit signup
    page.locator('button[data-i18n="common.buttons.create"]').click()

    # Wait for schedule page (logged in)
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Step 2: Navigate to admin console
    page.locator('a[href="/app/admin"]').click()
    expect(page.locator('h2[data-i18n="admin.title"]')).to_be_visible(timeout=5000)

    # Step 3: Create events (at least 3 events with different roles)
    page.evaluate("""
        () => {
            const adminEventsTab = document.querySelector('[data-i18n="admin.tabs.events"]');
            if (adminEventsTab) adminEventsTab.click();
        }
    """)
    time.sleep(1)

    # Create Event 1: Sunday Service - Greeter
    page.locator('button[data-i18n="admin.buttons.create_event"]').click()
    page.locator('#event-title').fill("Sunday Service")
    page.locator('#event-date').fill("2025-11-01")
    page.locator('#event-time').fill("10:00")
    page.locator('#event-duration').fill("120")

    # Add role requirement (Greeter: 2 people)
    page.locator('#add-role-requirement').click()
    page.locator('#role-requirement-role-0').fill("Greeter")
    page.locator('#role-requirement-count-0').fill("2")

    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Create Event 2: Sunday Service - Usher
    page.locator('button[data-i18n="admin.buttons.create_event"]').click()
    page.locator('#event-title').fill("Sunday Service")
    page.locator('#event-date').fill("2025-11-01")
    page.locator('#event-time').fill("10:00")
    page.locator('#event-duration').fill("120")

    # Add role requirement (Usher: 3 people)
    page.locator('#add-role-requirement').click()
    page.locator('#role-requirement-role-0').fill("Usher")
    page.locator('#role-requirement-count-0').fill("3")

    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Create Event 3: Wednesday Prayer Meeting - Leader
    page.locator('button[data-i18n="admin.buttons.create_event"]').click()
    page.locator('#event-title').fill("Wednesday Prayer Meeting")
    page.locator('#event-date').fill("2025-11-05")
    page.locator('#event-time').fill("19:00")
    page.locator('#event-duration').fill("90")

    # Add role requirement (Leader: 1 person)
    page.locator('#add-role-requirement').click()
    page.locator('#role-requirement-role-0').fill("Leader")
    page.locator('#role-requirement-count-0').fill("1")

    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Step 4: Create volunteers (at least 6 people)
    page.evaluate("""
        () => {
            const adminPeopleTab = document.querySelector('[data-i18n="admin.tabs.people"]');
            if (adminPeopleTab) adminPeopleTab.click();
        }
    """)
    time.sleep(1)

    for i in range(1, 7):
        page.locator('button[data-i18n="admin.buttons.add_person"]').click()
        page.locator('#person-name').fill(f"Volunteer {i}")
        page.locator('#person-email').fill(f"volunteer{i}_{int(time.time())}@test.com")
        page.locator('button[data-i18n="common.buttons.save"]').click()
        time.sleep(0.5)

    # Step 5: Create teams (Greeter Team, Usher Team, Leader Team)
    page.evaluate("""
        () => {
            const adminTeamsTab = document.querySelector('[data-i18n="admin.tabs.teams"]');
            if (adminTeamsTab) adminTeamsTab.click();
        }
    """)
    time.sleep(1)

    # Create Greeter Team
    page.locator('button[data-i18n="admin.buttons.create_team"]').click()
    page.locator('#team-name').fill("Greeter Team")
    page.locator('#team-role').fill("Greeter")
    # Add members (Volunteer 1, 2, 3)
    page.locator('#team-member-1').check()
    page.locator('#team-member-2').check()
    page.locator('#team-member-3').check()
    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Create Usher Team
    page.locator('button[data-i18n="admin.buttons.create_team"]').click()
    page.locator('#team-name').fill("Usher Team")
    page.locator('#team-role').fill("Usher")
    # Add members (Volunteer 3, 4, 5)
    page.locator('#team-member-3').check()
    page.locator('#team-member-4').check()
    page.locator('#team-member-5').check()
    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Create Leader Team
    page.locator('button[data-i18n="admin.buttons.create_team"]').click()
    page.locator('#team-name').fill("Leader Team")
    page.locator('#team-role').fill("Leader")
    # Add members (Volunteer 5, 6)
    page.locator('#team-member-5').check()
    page.locator('#team-member-6').check()
    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Step 6: Navigate to Solver tab
    page.evaluate("""
        () => {
            const adminSolverTab = document.querySelector('[data-i18n="admin.tabs.solver"]');
            if (adminSolverTab) adminSolverTab.click();
        }
    """)
    time.sleep(1)

    # Step 7: Configure solver constraints
    # Add constraint: Max 2 assignments per person per week
    page.locator('#add-constraint').click()
    page.locator('#constraint-type').select_option("max_assignments_per_person")
    page.locator('#constraint-value').fill("2")
    page.locator('#constraint-period').select_option("week")
    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Add constraint: Fairness (distribute assignments evenly)
    page.locator('#add-constraint').click()
    page.locator('#constraint-type').select_option("fairness")
    page.locator('#fairness-weight').fill("0.8")
    page.locator('button[data-i18n="common.buttons.save"]').click()
    time.sleep(1)

    # Step 8: Run solver
    page.locator('button[data-i18n="solver.buttons.run_solver"]').click()

    # Wait for solver to complete (show loading indicator, then results)
    expect(page.locator('[data-i18n="solver.status.running"]')).to_be_visible(timeout=5000)
    expect(page.locator('[data-i18n="solver.status.completed"]')).to_be_visible(timeout=30000)

    # Step 9: Verify solver results displayed
    expect(page.locator('[data-i18n="solver.results.title"]')).to_be_visible()

    # Verify schedule table shows assignments
    expect(page.locator('#solver-results-table')).to_be_visible()

    # Verify at least 5 assignments generated (3 events with different requirements)
    assignments = page.locator('#solver-results-table tbody tr').count()
    assert assignments >= 5, f"Expected at least 5 assignments, got {assignments}"

    # Step 10: Verify constraints are met
    # Check max 2 assignments per person constraint
    volunteer_assignments = {}
    rows = page.locator('#solver-results-table tbody tr').all()
    for row in rows:
        volunteer_name = row.locator('td.volunteer-name').text_content()
        volunteer_assignments[volunteer_name] = volunteer_assignments.get(volunteer_name, 0) + 1

    for volunteer, count in volunteer_assignments.items():
        assert count <= 2, f"Volunteer {volunteer} has {count} assignments (max 2 allowed)"

    # Step 11: Verify all events have required number of volunteers
    event_assignments = {}
    for row in rows:
        event_name = row.locator('td.event-name').text_content()
        role = row.locator('td.role-name').text_content()
        event_role_key = f"{event_name}:{role}"
        event_assignments[event_role_key] = event_assignments.get(event_role_key, 0) + 1

    # Verify Sunday Service - Greeter has 2 volunteers
    assert event_assignments.get("Sunday Service:Greeter", 0) == 2

    # Verify Sunday Service - Usher has 3 volunteers
    assert event_assignments.get("Sunday Service:Usher", 0) == 3

    # Verify Wednesday Prayer Meeting - Leader has 1 volunteer
    assert event_assignments.get("Wednesday Prayer Meeting:Leader", 0) == 1


def test_solver_results_display_correctly(page: Page):
    """
    Test that solver results are displayed in a user-friendly format.

    Verifies:
    - Results table shows event name, date, time, volunteer name, role
    - Color coding for different roles
    - Export results button exists
    - Results can be filtered by event or volunteer
    """
    # This test would follow similar setup as above, then focus on UI display
    # For now, marking as TODO - needs implementation
    pytest.skip("TODO: Implement solver results display test")


def test_manual_schedule_adjustment_after_solver(page: Page):
    """
    Test that admin can manually adjust solver-generated schedule.

    User Journey:
    1. Run solver (generates schedule)
    2. Admin clicks "Edit" on an assignment
    3. Changes volunteer for that assignment
    4. Saves change
    5. Verifies change persisted
    6. Verifies solver doesn't overwrite manual changes on next run
    """
    pytest.skip("TODO: Implement manual schedule adjustment test")


def test_solver_conflict_resolution(page: Page):
    """
    Test that solver detects and reports conflicts.

    User Journey:
    1. Create overlapping events (same time)
    2. Create volunteer with limited availability
    3. Run solver
    4. Verify solver shows conflicts in results
    5. Verify conflicts are highlighted in red
    6. Admin resolves conflict manually
    """
    pytest.skip("TODO: Implement solver conflict resolution test")


def test_solver_with_different_constraint_priorities(page: Page):
    """
    Test that solver respects constraint priority ordering.

    User Journey:
    1. Add multiple constraints with different priorities
    2. Run solver
    3. Verify higher priority constraints are satisfied first
    4. Verify lower priority constraints are best-effort
    """
    pytest.skip("TODO: Implement constraint priority test")


def test_solver_performance_with_large_dataset(page: Page):
    """
    Test solver performance with 100+ people and 50+ events.

    Verifies:
    - Solver completes within 60 seconds
    - Results are still correct
    - UI remains responsive
    - Progress indicator updates during solving
    """
    pytest.skip("TODO: Implement solver performance test (requires large dataset)")


def test_solver_optimization_settings(page: Page):
    """
    Test that solver optimization settings can be configured.

    User Journey:
    1. Admin opens solver settings
    2. Configures optimization goals:
       - Fairness (even distribution)
       - Coverage (fill all roles)
       - Preferences (respect volunteer preferences)
    3. Runs solver
    4. Verifies schedule optimized according to settings
    """
    pytest.skip("TODO: Implement solver optimization settings test")
