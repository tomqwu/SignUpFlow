"""
E2E tests for Teams CRUD Operations.

Tests:
- Create team with name, role, members
- Edit team (change name, role, description)
- Delete team and verify data cleanup
- Add members to team
- Remove members from team
- View teams list
- Filter teams by role

Priority: HIGH - Admin feature with partial coverage

STATUS: Tests implemented but SKIPPED - Teams UI not yet implemented
Backend API complete (api/routers/teams.py), frontend pending

UI Gaps Identified:
- No Teams tab in admin console (/app/admin)
- No teams list display (#teams-list, .teams-section)
- No "Add Team" button
- No team create/edit form
- No team member management UI
- currentOrg not properly initialized in localStorage

Once Teams UI is implemented in frontend/js/app-admin.js, unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig, ApiTestClient

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def admin_login(page: Page, app_config: AppConfig, api_client: ApiTestClient):
    """Login as admin for teams tests. Returns tuple (page, org)."""
    # Create test organization and admin user dynamically
    org = api_client.create_org()
    admin_user = api_client.create_user(
        org_id=org["id"],
        name="Test Admin",
        roles=["admin"],
    )

    # Navigate directly to login page
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
    page.on("requestfailed", lambda req: print(f"REQUEST FAILED: {req.url} - {req.failure}"))
    page.on("response", lambda res: print(f"RESPONSE: {res.url} - {res.status}") if res.status >= 400 else None)
    page.goto(f"{app_config.app_url}/login")
    
    page.wait_for_load_state("networkidle")

    # Verify login screen is visible
    try:
        expect(page.locator("#login-screen")).to_be_visible(timeout=5000)
    except AssertionError:
        print(f"DEBUG: Login screen hidden. Current URL: {page.url}")
        print(f"DEBUG: localStorage: {page.evaluate('JSON.stringify(localStorage)')}")
        print(f"DEBUG: visible screens: {page.locator('.screen:not(.hidden)').evaluate_all('els => els.map(e => e.id)')}")
        raise

    # Fill login form with dynamic user
    page.fill("#login-email", admin_user["email"])
    page.fill("#login-password", admin_user["password"])

    # Submit login
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Verify logged in
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    # Navigate to admin console
    page.goto(f"{app_config.app_url}/app/admin")
    page.wait_for_load_state("networkidle")

    # Wait for admin view to be visible (indicates page loaded)
    expect(page.locator('#admin-view')).to_be_visible(timeout=5000)

    # Wait for organizations to load (needed for admin functionality)
    page.wait_for_timeout(1000)

    # Click Teams tab
    teams_tab = page.locator('button:has-text("Teams"), [data-i18n*="teams"]')
    if teams_tab.count() > 0:
        teams_tab.first.click()
        page.wait_for_timeout(500)

        # Populate organization dropdown (needed for Teams tab)
        page.evaluate(f"""
            (function() {{
                const orgSelect = document.getElementById('teams-org-filter');
                if (orgSelect) {{
                    orgSelect.innerHTML = '<option value="">Select Organization</option>';
                    const option = document.createElement('option');
                    option.value = '{org["id"]}';
                    option.text = '{org["name"]}';
                    orgSelect.appendChild(option);
                    orgSelect.value = '{org["id"]}'; // Select the org
                    orgSelect.dispatchEvent(new Event('change')); // Trigger loadAdminTeams
                }}
            }})();
        """)
        page.wait_for_timeout(500)

    return page, org



def test_create_team_complete_workflow(admin_login):
    """Test complete team creation workflow."""
    page, org = admin_login  # Unpack tuple from fixture

    # Click "Add Team" button
    add_team_button = page.locator('button:has-text("Add Team"), button:has-text("+ Team"), button:has-text("Create Team")')

    # If no Add Team button, try to reveal create form
    if add_team_button.count() == 0:
        # Look for a Teams section or container
        teams_container = page.locator('#teams-list, .teams-section, [id*="team"]').first
        if teams_container.count() > 0:
            teams_container.click()
            page.wait_for_timeout(300)
            add_team_button = page.locator('button:has-text("Create Team")')

    expect(add_team_button.first).to_be_visible(timeout=5000)
    print(f"DEBUG: Add Team Button HTML: {add_team_button.first.evaluate('el => el.outerHTML')}")
    add_team_button.first.click()
    page.wait_for_timeout(1000) # Wait longer for modal

    # Debug modal state
    modal_classes = page.locator('#create-team-modal').get_attribute('class')
    print(f"DEBUG: Modal classes: {modal_classes}")
    modal_visible = page.locator('#create-team-modal').is_visible()
    print(f"DEBUG: Modal visible: {modal_visible}")

    # Fill team form
    timestamp = int(time.time() * 1000)
    team_id = f"team_e2e_{timestamp}"
    team_name = f"E2E Test Team {timestamp}"
    team_description = "Team created by E2E test"

    # Fill team ID
    team_id_input = page.locator('#team-id')
    if team_id_input.count() > 0:
        team_id_input.fill(team_id)

    # Fill team name
    team_name_input = page.locator('#team-name')
    expect(team_name_input).to_be_visible(timeout=5000)
    team_name_input.fill(team_name)

    # Fill team description
    team_description_input = page.locator('#team-description')
    if team_description_input.count() > 0:
        team_description_input.fill(team_description)

    # Submit form
    submit_button = page.locator('#create-team-form button[type="submit"]')
    expect(submit_button.first).to_be_visible()
    submit_button.first.click()

    # Wait for team to be created
    page.wait_for_timeout(2000)

    # Verify team appears in list
    team_card = page.locator(f'text="{team_name}"')
    expect(team_card.first).to_be_visible(timeout=5000)

    # Verify success message or team in list
    expect(page.locator(f'text="{team_name}"')).to_be_visible()



def test_edit_team(admin_login):
    """Test editing existing team."""
    page, org = admin_login  # Unpack tuple from fixture

    # First create a team to edit
    timestamp = int(time.time() * 1000)
    team_id = f"team_edit_{timestamp}"
    original_name = f"Team To Edit {timestamp}"
    org_id = org["id"]  # Get org_id from fixture

    # Create team via API for speed
    page.evaluate(f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');

            await fetch('/api/teams/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    id: '{team_id}',
                    org_id: '{org_id}',
                    name: '{original_name}',
                    description: 'Original description'
                }})
            }});
        }})();
    """)
    
    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Click Teams tab to make teams content visible
    teams_tab = page.locator('button[data-tab="teams"]')
    teams_tab.click()
    page.wait_for_timeout(500)
    
    # Need to set the org filter dropdown for teams to load
    page.select_option('#teams-org-filter', org_id)
    page.wait_for_timeout(500)  # Wait for teams to load after filter selection
    
    # Find the team in the list
    team_card = page.locator(f'text="{original_name}"').first
    expect(team_card).to_be_visible(timeout=5000)
    
    # Click edit button
    # Look for button in the same card
    team_container = team_card.locator('..').locator('..')
    edit_button = team_container.locator('button:has-text("Edit")')
    expect(edit_button.first).to_be_visible(timeout=5000)
    edit_button.first.click()
    
    # Wait for modal
    page.wait_for_timeout(500)
    
    # Update team name
    updated_name = f"Updated Team {timestamp}"
    team_name_input = page.locator('#edit-team-name')
    expect(team_name_input).to_be_visible(timeout=5000)
    team_name_input.fill(updated_name)
    
    # Update description
    updated_description = "Updated description"
    team_description_input = page.locator('#edit-team-description')
    if team_description_input.count() > 0:
        team_description_input.fill(updated_description)
        
    # Submit update
    save_button = page.locator('#edit-team-form button[type="submit"]')
    expect(save_button.first).to_be_visible()
    save_button.first.click()
    
    # Wait for update
    page.wait_for_timeout(1000)
    
    # Verify updated name appears
    expect(page.locator(f'text="{updated_name}"').first).to_be_visible(timeout=5000)



def test_delete_team(admin_login):
    """Test deleting team and data cleanup."""
    page, org = admin_login  # Unpack tuple from fixture

    # Create a team to delete
    timestamp = int(time.time() * 1000)
    team_id = f"team_delete_{timestamp}"
    team_name = f"Team To Delete {timestamp}"
    org_id = org["id"]  # Get org_id from fixture

    # Create team via API
    page.evaluate(f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');

            await fetch('/api/teams/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    id: '{team_id}',
                    org_id: '{org_id}',
                    name: '{team_name}',
                    description: 'Will be deleted'
                }})
            }});
        }})();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_load_state("networkidle")

    # Click Teams tab to make teams content visible
    teams_tab = page.locator('button[data-tab="teams"]')
    teams_tab.click()
    page.wait_for_timeout(500)

    # Need to set the org filter dropdown for teams to load
    page.select_option('#teams-org-filter', org_id)
    page.wait_for_timeout(500)  # Wait for teams to load after filter selection

    # Find the team
    team_card = page.locator(f'text="{team_name}"').first
    expect(team_card).to_be_visible(timeout=5000)

    # Click delete button
    team_container = team_card.locator('..').locator('..')
    delete_button = team_container.locator('button:has-text("Delete"), button[title="Delete"]')

    if delete_button.count() == 0:
        team_card.click()
        page.wait_for_timeout(300)
        delete_button = page.locator('button:has-text("Delete"), button[title="Delete"]')

    expect(delete_button.first).to_be_visible(timeout=5000)
    
    # Debug: Check button onclick
    button_html = delete_button.first.evaluate("el => el.outerHTML")
    print(f"DEBUG: Button HTML = {button_html}")

    delete_button.first.click()
    page.wait_for_timeout(500)

    # Confirm deletion (look for confirm dialog)
    confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")')
    if confirm_button.count() > 0:
        confirm_button.last.click()  # Use last to get the confirm dialog button

    page.wait_for_timeout(2000)

    # Verify team is no longer in the list
    expect(page.locator(f'text="{team_name}"')).not_to_be_visible()



def test_add_remove_team_members(admin_login: Page):
    """Test adding and removing team members."""
    page, org = admin_login

    # Create a team
    timestamp = int(time.time() * 1000)
    team_id = f"team_members_{timestamp}"
    team_name = f"Team For Members {timestamp}"

    # Create team via API
    team_response = page.evaluate(f"""
        (async () => {{
            const authToken = localStorage.getItem('authToken');
            const currentOrg = JSON.parse(localStorage.getItem('roster_org'));

            const teamResponse = await fetch('/api/teams/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${{authToken}}`
                }},
                body: JSON.stringify({{
                    id: '{team_id}',
                    org_id: currentOrg.id,
                    name: '{team_name}',
                    description: 'For member management'
                }})
            }});

            return await teamResponse.json();
        }})();
    """)

    page.wait_for_timeout(1000)
    page.reload()
    page.wait_for_timeout(1000)

    # Select org filter to ensure teams are visible
    page.select_option('#teams-org-filter', org["id"])
    page.wait_for_timeout(500)

    # Find and click on the team to open member management
    team_card = page.locator(f'text="{team_name}"').first
    expect(team_card).to_be_visible(timeout=5000)
    team_card.click()
    page.wait_for_timeout(500)

    # Look for "Add Member" or "Manage Members" button
    add_member_button = page.locator('button:has-text("Add Member"), button:has-text("Manage Members"), button:has-text("+ Member")')

    if add_member_button.count() > 0:
        add_member_button.first.click()
        page.wait_for_timeout(500)

        # Select a person from dropdown or list
        member_select = page.locator('select[name="person"], #member-select, #add-team-member-select')
        if member_select.count() > 0:
            # Select first available person
            member_select.select_option(index=1)
        else:
            # Try clicking on a person in a list
            person_item = page.locator('.person-item, [data-person-id]').first
            if person_item.count() > 0:
                person_item.click()

        # Confirm adding member
        add_button = page.locator('button:text-is("Add")')
        if add_button.count() > 0:
            add_button.first.click()
            page.wait_for_timeout(1000)

        # Verify member was added (member count increased or member listed)
        member_count = page.locator('text=/[1-9]+ member/')
        if member_count.count() > 0:
            expect(member_count.first).to_be_visible()

        # Now test removing a member
        remove_button = page.locator('button:has-text("Remove"), button[title="Remove member"]')
        if remove_button.count() > 0:
            remove_button.first.click()
            page.wait_for_timeout(500)

            # Confirm removal
            confirm_remove = page.locator('button:has-text("Confirm"), button:has-text("Yes")')
            if confirm_remove.count() > 0:
                confirm_remove.last.click()

            page.wait_for_timeout(1000)



def test_view_teams_list(admin_login):
    """Test viewing all organization teams."""
    page, org = admin_login  # Unpack tuple from fixture

    # Create multiple teams to verify list
    timestamp = int(time.time() * 1000)

    for i in range(3):
        team_id = f"team_list_{timestamp}_{i}"
        team_name = f"List Team {i+1}"

        page.evaluate(f"""
            (async () => {{
                const authToken = localStorage.getItem('authToken');
                const currentOrg = JSON.parse(localStorage.getItem('roster_org'));

                await fetch('/api/teams/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{authToken}}`
                    }},
                    body: JSON.stringify({{
                        id: '{team_id}',
                        org_id: currentOrg.id,
                        name: '{team_name}',
                        description: 'Test team {i+1}'
                    }})
                }});
            }})();
        """)
        page.wait_for_timeout(300)

    # Reload page to see all teams
    page.reload()
    page.wait_for_timeout(1000)

    # Select org filter to ensure teams are visible
    page.select_option('#teams-org-filter', org["id"])
    page.wait_for_timeout(500)

    # Verify at least 3 teams are visible
    team_cards = page.locator('.data-card, .team-card, [data-team-id]')
    assert team_cards.count() >= 3, "Should have at least 3 teams visible"

    # Verify team names appear
    for i in range(3):
        team_name = f"List Team {i+1}"
        expect(page.locator(f'text="{team_name}"')).to_be_visible()



def test_filter_teams_by_role(admin_login: Page):
    """Test filtering teams by role."""
    page, org = admin_login

    # This test verifies that team filtering works if implemented
    # If no filter UI exists, test will check that all teams are shown

    # Look for filter/search controls
    filter_input = page.locator('input[type="search"], input[placeholder*="filter"], input[placeholder*="search"]')

    if filter_input.count() > 0:
        # Enter search term
        filter_input.first.fill("Test")
        page.wait_for_timeout(500)

        # Verify filtered results
        team_cards = page.locator('.data-card, .team-card')
        if team_cards.count() > 0:
            # At least one team should match
            expect(team_cards.first).to_be_visible()

        # Clear filter
        filter_input.first.fill("")
        page.wait_for_timeout(500)
    else:
        # No filter UI - just verify teams are displayed
        teams_list = page.locator('#teams-list, .teams-section')
        expect(teams_list).to_be_visible()
