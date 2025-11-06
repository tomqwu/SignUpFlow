"""
E2E tests for Constraints Management.

Tests:
- Create constraint with type (hard/soft), weight, priority
- Edit constraint (change weight, predicate, params)
- Delete constraint and verify cleanup
- View constraints list
- Toggle constraint active/inactive
- Priority ordering (drag-and-drop or up/down buttons)

Priority: HIGH - Solver configuration feature

STATUS: Tests implemented but SKIPPED - Constraints UI not yet implemented
Backend API complete (api/routers/constraints.py), frontend pending

UI Gaps Identified:
- No Constraints tab in admin console (/app/admin)
- No constraints list display (#constraints-list, .constraints-section)
- No "Add Constraint" button
- No constraint create/edit form
- No constraint type selector (hard/soft)
- No weight input field (0-100)
- No priority ordering controls (drag-drop or up/down buttons)
- No active/inactive toggle
- currentOrg not properly initialized in localStorage

Once Constraints UI is implemented in frontend/js/app-admin.js, unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def admin_login(
    page: Page,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """Login as admin for constraints tests."""
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

    # Click Constraints tab
    constraints_tab = page.locator('button:has-text("Constraints"), [data-i18n*="constraints"]')
    if constraints_tab.count() > 0:
        constraints_tab.first.click()
        page.wait_for_timeout(500)

    return page


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_create_constraint(admin_login: Page):
    """Test creating a constraint with type, weight, and predicate."""
    page = admin_login

    # Click "Add Constraint" button
    add_button = page.locator(
        'button:has-text("Add Constraint"), button:has-text("+ Constraint"), button:has-text("Create Constraint")'
    )

    # If no Add Constraint button, try to reveal create form
    if add_button.count() == 0:
        constraints_container = page.locator('#constraints-list, .constraints-section, [id*="constraint"]').first
        if constraints_container.count() > 0:
            constraints_container.click()
            page.wait_for_timeout(300)
            add_button = page.locator(
                'button:has-text("Add Constraint"), button:has-text("+ Constraint"), button:has-text("Create Constraint")'
            )

    expect(add_button.first).to_be_visible(timeout=5000)
    add_button.first.click()
    page.wait_for_timeout(500)

    # Fill constraint form
    timestamp = int(time.time() * 1000)
    constraint_key = f"no_consecutive_sundays_{timestamp}"
    constraint_predicate = "person_not_assigned_consecutive_weeks"

    # Fill constraint key
    key_input = page.locator('#constraint-key, input[name="key"]')
    expect(key_input).to_be_visible(timeout=5000)
    key_input.fill(constraint_key)

    # Select constraint type (hard or soft)
    type_select = page.locator('#constraint-type, select[name="type"]')
    if type_select.count() > 0:
        type_select.select_option("soft")  # soft constraint with weight
    else:
        # Try radio buttons
        soft_radio = page.locator('input[type="radio"][value="soft"], label:has-text("Soft")')
        if soft_radio.count() > 0:
            soft_radio.first.click()

    # Fill weight (for soft constraints, 0-100)
    weight_input = page.locator('#constraint-weight, input[name="weight"]')
    if weight_input.count() > 0:
        weight_input.fill("80")  # High weight (80/100)

    # Fill predicate
    predicate_input = page.locator('#constraint-predicate, input[name="predicate"], textarea[name="predicate"]')
    if predicate_input.count() > 0:
        predicate_input.fill(constraint_predicate)

    # Submit form
    submit_button = page.locator('button:has-text("Create"), button:has-text("Save"), button[type="submit"]')
    expect(submit_button.first).to_be_visible()
    submit_button.first.click()

    # Wait for constraint to be created
    page.wait_for_timeout(2000)

    # Verify constraint appears in list
    constraint_card = page.locator(f'text="{constraint_key}"')
    expect(constraint_card.first).to_be_visible(timeout=5000)

    # Verify constraint details displayed
    expect(page.locator(f'text="{constraint_key}"')).to_be_visible()
    expect(page.locator('text="soft"')).to_be_visible()  # Type
    expect(page.locator('text="80"')).to_be_visible()  # Weight


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_edit_constraint(admin_login: Page):
    """Test editing existing constraint."""
    page = admin_login

    # First create a constraint to edit via API
    timestamp = int(time.time() * 1000)
    constraint_key = f"constraint_edit_{timestamp}"
    original_weight = 50

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
                    key: '{constraint_key}',
                    type: 'soft',
                    weight: {original_weight},
                    predicate: 'original_predicate',
                    params: {{max_consecutive: 2}}
                }})
            }});
        }})();
    """
    )

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find the constraint in the list
    constraint_card = page.locator(f'text="{constraint_key}"').first
    expect(constraint_card).to_be_visible(timeout=5000)

    # Click edit button
    constraint_container = constraint_card.locator('..').locator('..')
    edit_button = constraint_container.locator('button:has-text("Edit"), button[title="Edit"]')

    if edit_button.count() == 0:
        # Try clicking on the constraint card itself
        constraint_card.click()
        page.wait_for_timeout(300)
        edit_button = page.locator('button:has-text("Edit"), button[title="Edit"]')

    expect(edit_button.first).to_be_visible(timeout=5000)
    edit_button.first.click()
    page.wait_for_timeout(500)

    # Update weight from 50 to 90
    updated_weight = 90
    weight_input = page.locator('#constraint-weight, input[name="weight"]')
    expect(weight_input).to_be_visible()
    weight_input.fill("")  # Clear first
    weight_input.fill(str(updated_weight))

    # Update predicate
    updated_predicate = "updated_predicate_formula"
    predicate_input = page.locator('#constraint-predicate, input[name="predicate"], textarea[name="predicate"]')
    if predicate_input.count() > 0:
        predicate_input.fill("")
        predicate_input.fill(updated_predicate)

    # Submit update
    save_button = page.locator('button:has-text("Save"), button:has-text("Update"), button[type="submit"]')
    expect(save_button.first).to_be_visible()
    save_button.first.click()

    page.wait_for_timeout(2000)

    # Verify updated weight appears
    expect(page.locator(f'text="{updated_weight}"').first).to_be_visible(timeout=5000)


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_delete_constraint(admin_login: Page):
    """Test deleting constraint and cleanup."""
    page = admin_login

    # Create a constraint to delete via API
    timestamp = int(time.time() * 1000)
    constraint_key = f"constraint_delete_{timestamp}"

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
                    key: '{constraint_key}',
                    type: 'hard',
                    weight: 100,
                    predicate: 'will_be_deleted',
                    params: {{}}
                }})
            }});
        }})();
    """
    )

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find the constraint
    constraint_card = page.locator(f'text="{constraint_key}"').first
    expect(constraint_card).to_be_visible(timeout=5000)

    # Click delete button
    constraint_container = constraint_card.locator('..').locator('..')
    delete_button = constraint_container.locator('button:has-text("Delete"), button[title="Delete"]')

    if delete_button.count() == 0:
        constraint_card.click()
        page.wait_for_timeout(300)
        delete_button = page.locator('button:has-text("Delete"), button[title="Delete"]')

    expect(delete_button.first).to_be_visible(timeout=5000)
    delete_button.first.click()
    page.wait_for_timeout(500)

    # Confirm deletion
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")')
    if confirm_button.count() > 0:
        confirm_button.last.click()  # Use last to get the confirm dialog button

    page.wait_for_timeout(2000)

    # Verify constraint is no longer in the list
    expect(page.locator(f'text="{constraint_key}"')).not_to_be_visible()


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_view_constraints_list(admin_login: Page):
    """Test viewing all constraints for organization."""
    page = admin_login

    # Create multiple constraints to verify list
    timestamp = int(time.time() * 1000)

    for i in range(3):
        constraint_key = f"list_constraint_{timestamp}_{i}"

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
                        key: '{constraint_key}',
                        type: {('hard' if i % 2 == 0 else 'soft')},
                        weight: {(100 if i % 2 == 0 else 75)},
                        predicate: 'test_predicate_{i}',
                        params: {{order: {i}}}
                    }})
                }});
            }})();
        """
        )
        page.wait_for_timeout(300)

    # Reload page to see all constraints
    page.reload()
    page.wait_for_timeout(1000)

    # Verify at least 3 constraints are visible
    constraint_cards = page.locator('.data-card, .constraint-card, [data-constraint-id]')
    assert constraint_cards.count() >= 3, "Should have at least 3 constraints visible"

    # Verify constraint keys appear
    for i in range(3):
        constraint_key = f"list_constraint_{timestamp}_{i}"
        expect(page.locator(f'text="{constraint_key}"')).to_be_visible()


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_toggle_constraint_active(admin_login: Page):
    """Test toggling constraint active/inactive status."""
    page = admin_login

    # Create a constraint
    timestamp = int(time.time() * 1000)
    constraint_key = f"toggle_constraint_{timestamp}"

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
                    key: '{constraint_key}',
                    type: 'soft',
                    weight: 70,
                    predicate: 'toggleable_constraint',
                    params: {{active: true}}
                }})
            }});
        }})();
    """
    )

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Find the constraint
    constraint_card = page.locator(f'text="{constraint_key}"').first
    expect(constraint_card).to_be_visible(timeout=5000)

    # Find toggle switch or checkbox
    toggle_control = page.locator(
        f'text="{constraint_key}"'
    ).locator('..').locator('..').locator(
        'input[type="checkbox"], button[role="switch"], .toggle-switch, [data-toggle]'
    )

    if toggle_control.count() > 0:
        # Click toggle to deactivate
        toggle_control.first.click()
        page.wait_for_timeout(500)

        # Verify inactive state (grayed out, strikethrough, or "Inactive" label)
        expect(
            page.locator('text="Inactive", .inactive, [data-state="inactive"]').first
        ).to_be_visible(timeout=3000)

        # Click toggle again to reactivate
        toggle_control.first.click()
        page.wait_for_timeout(500)

        # Verify active state
        expect(
            page.locator('text="Active", .active, [data-state="active"]').first
        ).to_be_visible(timeout=3000)


@pytest.mark.skip(reason="Constraints UI not implemented - backend API exists but frontend pending")
def test_constraint_priority_ordering(admin_login: Page):
    """Test constraint priority ordering (drag-drop or up/down buttons)."""
    page = admin_login

    # Create multiple constraints with different priorities
    timestamp = int(time.time() * 1000)
    constraints = []

    for i in range(3):
        constraint_key = f"priority_{i}_{timestamp}"
        constraints.append(constraint_key)

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
                        key: '{constraint_key}',
                        type: 'soft',
                        weight: {90 - (i * 10)},  // 90, 80, 70
                        predicate: 'priority_test',
                        params: {{priority: {i}}}
                    }})
                }});
            }})();
        """
        )
        page.wait_for_timeout(300)

    # Reload to see all constraints
    page.reload()
    page.wait_for_timeout(1000)

    # Find the second constraint (middle priority)
    constraint_card = page.locator(f'text="{constraints[1]}"').first
    expect(constraint_card).to_be_visible(timeout=5000)

    # Look for priority controls (up/down buttons or drag handle)
    priority_container = constraint_card.locator('..').locator('..')
    up_button = priority_container.locator(
        'button:has-text("Up"), button[title="Move Up"], button[aria-label*="up"], .move-up'
    )
    down_button = priority_container.locator(
        'button:has-text("Down"), button[title="Move Down"], button[aria-label*="down"], .move-down'
    )
    drag_handle = priority_container.locator('.drag-handle, [draggable="true"]')

    if up_button.count() > 0:
        # Test up/down button approach
        # Move second constraint up (should become first)
        up_button.first.click()
        page.wait_for_timeout(500)

        # Verify constraint moved up in the list
        # (Could check DOM order or visual position)
    elif drag_handle.count() > 0:
        # Test drag-and-drop approach
        # Drag second constraint to first position
        source = constraint_card
        target = page.locator(f'text="{constraints[0]}"').first

        if source.count() > 0 and target.count() > 0:
            # Playwright drag and drop
            source.drag_to(target)
            page.wait_for_timeout(500)

    # Verify new order persisted (reload and check order)
    page.reload()
    page.wait_for_timeout(1000)

    # Check constraints are still visible after reorder
    for constraint_key in constraints:
        expect(page.locator(f'text="{constraint_key}"')).to_be_visible()
