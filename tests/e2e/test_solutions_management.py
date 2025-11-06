"""
E2E tests for Solutions Management.

Tests:
- Save solver solution to history
- Load previous solution from history
- Compare two solutions side-by-side
- Rollback to previous solution
- Delete solution from history
- View solution metadata (metrics, timestamps)

Priority: MEDIUM - Schedule versioning and history management feature

STATUS: Tests implemented but SKIPPED - Solutions Management UI not yet implemented
Backend API complete (api/routers/solutions.py), frontend pending

Backend API Endpoints:
- GET /api/solutions/?org_id={org_id} - List all solutions for org
- GET /api/solutions/{solution_id} - Get single solution with assignment_count
- GET /api/solutions/{solution_id}/assignments - Get all assignments for solution
- POST /api/solutions/{solution_id}/export?format={csv|json|pdf} - Export solution
- DELETE /api/solutions/{solution_id} - Delete solution (cascade deletes assignments)

Solution Model:
- id, org_id, created_at
- hard_violations, soft_score, health_score, solve_ms
- metrics (JSON: fairness, stability data)
- assignment_count (calculated)

UI Gaps Identified:
- No Solutions tab in admin console (/app/admin)
- No solutions history list display (#solutions-list, .solutions-section)
- No solution cards showing metrics (hard_violations, health_score, solve_ms)
- No "Compare Solutions" button for multi-select
- No solution comparison view (side-by-side diff)
- No "Load Solution" button to restore assignments
- No "Rollback" confirmation dialog
- No "Delete Solution" button with confirmation
- No solution metadata panel (#solution-metadata, .solution-details)
- No export format dropdown (CSV, JSON, PDF)
- No "Export Solution" button
- Solver UI doesn't save solutions automatically after generation
- No pagination controls for solution history list
- currentOrg not properly initialized in localStorage

Once Solutions Management UI is implemented in frontend/js/app-admin.js, unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def admin_login(page: Page, app_config: AppConfig):
    """Login as admin for solutions management tests."""
    # Navigate directly to login page
    page.goto(f"{app_config.app_url}/login")
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
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    # Navigate to admin console
    page.goto(f"{app_config.app_url}/app/admin")
    page.wait_for_timeout(1000)

    # Click Solutions tab (if exists)
    solutions_tab = page.locator('button:has-text("Solutions"), button:has-text("History"), [data-i18n*="solutions"]')
    if solutions_tab.count() > 0:
        solutions_tab.first.click()
        page.wait_for_timeout(500)

    return page


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_save_solver_solution(admin_login: Page):
    """
    Test that solver automatically saves solution to history.

    User Journey:
    1. Admin navigates to Solver tab
    2. Admin configures constraints and runs solver
    3. Solver generates schedule successfully
    4. Solution is automatically saved to history
    5. Admin navigates to Solutions tab
    6. Admin sees new solution in history list with metrics
    """
    page = admin_login

    # Navigate to Solver tab
    solver_tab = page.locator('button:has-text("Solver"), [data-i18n*="solver"]')
    if solver_tab.count() > 0:
        solver_tab.first.click()
        page.wait_for_timeout(500)
    else:
        # Try navigating directly
        page.goto("http://localhost:8000/app/admin#solver")
        page.wait_for_timeout(1000)

    # Run solver (create minimal schedule)
    run_solver_button = page.locator('button:has-text("Run Solver"), button:has-text("Generate Schedule")')
    if run_solver_button.count() > 0:
        run_solver_button.first.click()
        page.wait_for_timeout(3000)  # Wait for solver to complete

    # Navigate to Solutions tab
    solutions_tab = page.locator('button:has-text("Solutions"), button:has-text("History"), [data-i18n*="solutions"]')
    expect(solutions_tab.first).to_be_visible(timeout=5000)
    solutions_tab.first.click()
    page.wait_for_timeout(500)

    # Verify solutions list is visible
    solutions_list = page.locator('#solutions-list, .solutions-section, .solution-history')
    expect(solutions_list).to_be_visible(timeout=5000)

    # Verify at least one solution card appears
    solution_cards = page.locator('.solution-card, [data-solution-id], .data-card')
    expect(solution_cards.first).to_be_visible(timeout=5000)

    # Verify solution displays key metrics
    # Should show: created_at, hard_violations, health_score, solve_ms
    expect(page.locator('text=/Created:|Timestamp:/')).to_be_visible()
    expect(page.locator('text=/Violations:|Hard Violations:/')).to_be_visible()
    expect(page.locator('text=/Health Score:|Score:/')).to_be_visible()
    expect(page.locator('text=/Solve Time:|Duration:/')).to_be_visible()


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_load_previous_solution(admin_login: Page):
    """
    Test loading assignments from previous solution.

    User Journey:
    1. Admin views solutions history list
    2. Admin clicks on a previous solution
    3. Solution details panel appears
    4. Admin clicks "Load Solution" button
    5. Current schedule is replaced with solution's assignments
    6. Success message shows: "Schedule loaded from {timestamp}"
    """
    page = admin_login

    # Create test solution via API
    timestamp = int(time.time() * 1000)
    solution_response = page.evaluate(f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            // Create solution
            const solutionResponse = await fetch('http://localhost:8000/api/solutions/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    org_id: currentOrg.id,
                    hard_violations: 0,
                    soft_score: 95.5,
                    health_score: 98.2,
                    solve_ms: 1234,
                    metrics: {{
                        fairness: {{"gini_coefficient": 0.15}},
                        stability: {{"changes_from_previous": 2}}
                    }}
                }})
            }});

            return await solutionResponse.json();
        }})();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find solution in list
    solution_cards = page.locator('.solution-card, [data-solution-id]')
    expect(solution_cards.first).to_be_visible(timeout=5000)

    # Click on solution card
    solution_cards.first.click()
    page.wait_for_timeout(500)

    # Verify solution details panel appears
    solution_details = page.locator('#solution-details, .solution-metadata-panel, [data-panel="solution"]')
    expect(solution_details).to_be_visible(timeout=5000)

    # Verify metrics are displayed
    expect(page.locator('text=/Health Score.*98.2/')).to_be_visible()
    expect(page.locator('text=/Solve Time.*1234/')).to_be_visible()

    # Click "Load Solution" button
    load_button = page.locator('button:has-text("Load Solution"), button:has-text("Restore"), button:has-text("Apply")')
    expect(load_button.first).to_be_visible(timeout=5000)
    load_button.first.click()
    page.wait_for_timeout(500)

    # Confirm if dialog appears
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Load")')
    if confirm_button.count() > 0:
        confirm_button.last.click()

    page.wait_for_timeout(2000)

    # Verify success message
    success_message = page.locator('text=/Schedule loaded|Solution loaded|Successfully loaded/')
    expect(success_message).to_be_visible(timeout=5000)


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_compare_solutions(admin_login: Page):
    """
    Test comparing two solutions side-by-side.

    User Journey:
    1. Admin views solutions history list
    2. Admin selects checkbox on two different solutions
    3. "Compare Solutions" button becomes enabled
    4. Admin clicks "Compare Solutions"
    5. Comparison view appears showing:
       - Metrics comparison (violations, scores, solve time)
       - Assignment differences (who got added/removed)
       - Fairness comparison
    """
    page = admin_login

    # Create two test solutions via API
    for i in range(2):
        page.evaluate(f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

                await fetch('http://localhost:8000/api/solutions/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        org_id: currentOrg.id,
                        hard_violations: {i},
                        soft_score: {95 - i * 5},
                        health_score: {98 - i * 2},
                        solve_ms: {1000 + i * 500},
                        metrics: {{
                            fairness: {{"gini_coefficient": {0.15 + i * 0.05}}},
                            stability: {{"changes_from_previous": {2 + i}}}
                        }}
                    }})
                }});
            }})();
        """)
        page.wait_for_timeout(300)

    page.reload()
    page.wait_for_timeout(1000)

    # Select first solution
    solution_checkboxes = page.locator('input[type="checkbox"][data-solution-id], .solution-card input[type="checkbox"]')
    expect(solution_checkboxes.nth(0)).to_be_visible(timeout=5000)
    solution_checkboxes.nth(0).check()
    page.wait_for_timeout(300)

    # Select second solution
    solution_checkboxes.nth(1).check()
    page.wait_for_timeout(300)

    # Verify "Compare Solutions" button is enabled
    compare_button = page.locator('button:has-text("Compare Solutions"), button:has-text("Compare")')
    expect(compare_button.first).to_be_visible(timeout=5000)
    expect(compare_button.first).to_be_enabled()

    # Click compare button
    compare_button.first.click()
    page.wait_for_timeout(1000)

    # Verify comparison view appears
    comparison_view = page.locator('#solution-comparison, .comparison-view, [data-view="comparison"]')
    expect(comparison_view).to_be_visible(timeout=5000)

    # Verify comparison shows metrics for both solutions
    expect(page.locator('text=/Solution 1|First Solution/')).to_be_visible()
    expect(page.locator('text=/Solution 2|Second Solution/')).to_be_visible()

    # Verify metrics comparison visible
    expect(page.locator('text=/Violations/')).to_be_visible()
    expect(page.locator('text=/Health Score/')).to_be_visible()
    expect(page.locator('text=/Solve Time/')).to_be_visible()


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_rollback_to_previous_solution(admin_login: Page):
    """
    Test rollback functionality to restore previous solution.

    User Journey:
    1. Admin has current active schedule
    2. Admin views solutions history
    3. Admin clicks "Rollback" button on previous solution
    4. Confirmation dialog appears with warning message
    5. Admin confirms rollback
    6. Current schedule is replaced with previous solution
    7. Success message shows: "Rolled back to solution from {timestamp}"
    8. Solution is marked as "Active" in history
    """
    page = admin_login

    # Create test solution via API
    solution_response = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            const solutionResponse = await fetch('http://localhost:8000/api/solutions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    org_id: currentOrg.id,
                    hard_violations: 0,
                    soft_score: 95.0,
                    health_score: 97.5,
                    solve_ms: 1500,
                    metrics: {
                        fairness: {"gini_coefficient": 0.18},
                        stability: {"changes_from_previous": 3}
                    }
                })
            });

            return await solutionResponse.json();
        })();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find solution in list
    solution_cards = page.locator('.solution-card, [data-solution-id]')
    expect(solution_cards.first).to_be_visible(timeout=5000)

    # Find and click "Rollback" button
    rollback_button = page.locator('button:has-text("Rollback"), button:has-text("Restore"), button[title="Rollback"]')

    if rollback_button.count() == 0:
        # Try clicking on solution first to reveal rollback option
        solution_cards.first.click()
        page.wait_for_timeout(300)
        rollback_button = page.locator('button:has-text("Rollback"), button:has-text("Restore")')

    expect(rollback_button.first).to_be_visible(timeout=5000)
    rollback_button.first.click()
    page.wait_for_timeout(500)

    # Verify confirmation dialog appears
    confirm_dialog = page.locator('.modal, .dialog, [role="dialog"]')
    expect(confirm_dialog).to_be_visible(timeout=5000)

    # Verify warning message
    expect(page.locator('text=/This will replace your current schedule|Warning|Are you sure/')).to_be_visible()

    # Confirm rollback
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Rollback")')
    expect(confirm_button.last).to_be_visible()
    confirm_button.last.click()

    page.wait_for_timeout(2000)

    # Verify success message
    success_message = page.locator('text=/Rolled back|Successfully restored|Schedule restored/')
    expect(success_message).to_be_visible(timeout=5000)

    # Verify solution is marked as active
    active_badge = page.locator('text=/Active|Current/', '.badge.active, [data-status="active"]')
    expect(active_badge.first).to_be_visible()


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_delete_solution(admin_login: Page):
    """
    Test deleting solution from history.

    User Journey:
    1. Admin views solutions history list
    2. Admin clicks "Delete" button on a solution
    3. Confirmation dialog appears
    4. Admin confirms deletion
    5. Solution is removed from history list
    6. Success message shows: "Solution deleted"
    7. All assignments for that solution are also deleted (cascade)
    """
    page = admin_login

    # Create test solution via API
    timestamp = int(time.time() * 1000)
    solution_id = f"solution_delete_{timestamp}"

    page.evaluate(f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            await fetch('http://localhost:8000/api/solutions/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    id: '{solution_id}',
                    org_id: currentOrg.id,
                    hard_violations: 1,
                    soft_score: 90.0,
                    health_score: 95.0,
                    solve_ms: 2000,
                    metrics: {{}}
                }})
            }});
        }})();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find the solution
    solution_cards = page.locator('.solution-card, [data-solution-id]')
    expect(solution_cards.first).to_be_visible(timeout=5000)

    # Click delete button
    delete_button = solution_cards.first.locator('button:has-text("Delete"), button[title="Delete"]')

    if delete_button.count() == 0:
        # Try clicking on solution first to reveal delete option
        solution_cards.first.click()
        page.wait_for_timeout(300)
        delete_button = page.locator('button:has-text("Delete"), button[title="Delete"]')

    expect(delete_button.first).to_be_visible(timeout=5000)
    delete_button.first.click()
    page.wait_for_timeout(500)

    # Confirm deletion
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")')
    if confirm_button.count() > 0:
        confirm_button.last.click()

    page.wait_for_timeout(2000)

    # Verify solution no longer appears in list
    # Count should be one less than before
    remaining_cards = page.locator('.solution-card, [data-solution-id]')
    # Note: Can't assert exact count without knowing initial state
    # Just verify the deleted solution ID is not visible
    expect(page.locator(f'[data-solution-id="{solution_id}"]')).not_to_be_visible()

    # Verify success message
    success_message = page.locator('text=/Solution deleted|Successfully deleted|Removed/')
    expect(success_message).to_be_visible(timeout=5000)


@pytest.mark.skip(reason="Solutions Management UI not implemented - backend API exists but frontend pending")
def test_view_solution_metadata(admin_login: Page):
    """
    Test viewing detailed solution metadata.

    User Journey:
    1. Admin views solutions history list
    2. Admin clicks on a solution card
    3. Solution metadata panel appears showing:
       - Created timestamp
       - Hard violations count
       - Soft score
       - Health score
       - Solve time (milliseconds)
       - Fairness metrics (Gini coefficient)
       - Stability metrics (changes from previous)
       - Assignment count
    4. Admin can export solution in different formats (CSV, JSON, PDF)
    """
    page = admin_login

    # Create test solution with rich metadata
    solution_response = page.evaluate("""
        (async () => {
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('currentOrg'));

            const solutionResponse = await fetch('http://localhost:8000/api/solutions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    org_id: currentOrg.id,
                    hard_violations: 2,
                    soft_score: 92.3,
                    health_score: 96.8,
                    solve_ms: 1876,
                    metrics: {
                        fairness: {
                            "gini_coefficient": 0.16,
                            "max_assignments": 8,
                            "min_assignments": 3,
                            "avg_assignments": 5.2
                        },
                        stability: {
                            "changes_from_previous": 5,
                            "new_assignments": 3,
                            "removed_assignments": 2
                        }
                    }
                })
            });

            return await solutionResponse.json();
        })();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Click on solution card
    solution_cards = page.locator('.solution-card, [data-solution-id]')
    expect(solution_cards.first).to_be_visible(timeout=5000)
    solution_cards.first.click()
    page.wait_for_timeout(500)

    # Verify metadata panel appears
    metadata_panel = page.locator('#solution-metadata, .solution-details, [data-panel="metadata"]')
    expect(metadata_panel).to_be_visible(timeout=5000)

    # Verify all metadata fields are displayed

    # Core metrics
    expect(page.locator('text=/Created:|Timestamp:/')).to_be_visible()
    expect(page.locator('text=/Hard Violations.*2/')).to_be_visible()
    expect(page.locator('text=/Soft Score.*92.3/')).to_be_visible()
    expect(page.locator('text=/Health Score.*96.8/')).to_be_visible()
    expect(page.locator('text=/Solve Time.*1876|1.9 seconds/')).to_be_visible()

    # Fairness metrics
    expect(page.locator('text=/Fairness|Gini Coefficient/')).to_be_visible()
    expect(page.locator('text=/0.16/')).to_be_visible()
    expect(page.locator('text=/Max Assignments.*8/')).to_be_visible()
    expect(page.locator('text=/Min Assignments.*3/')).to_be_visible()

    # Stability metrics
    expect(page.locator('text=/Stability|Changes/')).to_be_visible()
    expect(page.locator('text=/5.*change/')).to_be_visible()

    # Assignment count (if displayed)
    expect(page.locator('text=/Assignments|Total Assignments/')).to_be_visible()

    # Verify export options
    export_dropdown = page.locator('select[name="export-format"], #export-format, .export-format-select')
    if export_dropdown.count() > 0:
        expect(export_dropdown).to_be_visible()
        # Verify format options exist
        expect(page.locator('option[value="csv"], option:has-text("CSV")')).to_be_visible()
        expect(page.locator('option[value="json"], option:has-text("JSON")')).to_be_visible()
        expect(page.locator('option[value="pdf"], option:has-text("PDF")')).to_be_visible()

    # Verify export button
    export_button = page.locator('button:has-text("Export"), button:has-text("Download")')
    if export_button.count() > 0:
        expect(export_button.first).to_be_visible()
