"""Strict tests for admin console functionality and UI elements."""
import os
import pytest
from playwright.sync_api import Page, expect
from tests.e2e.helpers import AppConfig, ApiTestClient, login_via_ui

# Use the test port defined in conftest.py (or default to 8001 if running standalone)
APP_URL = os.getenv("E2E_APP_URL", "http://localhost:8001")

@pytest.fixture(scope="function")
def admin_page(
    page: Page,
    api_server,
    app_config: AppConfig,
    api_client: ApiTestClient,
):
    """
    Setup for Admin tests:
    1. Set Viewport
    2. Create an Org
    3. Create an Admin User
    4. Login via UI
    5. Navigate to Admin Console
    """
    # 0. Set Viewport to Desktop
    page.set_viewport_size({"width": 1920, "height": 1080})

    # 1. Create Org
    org = api_client.create_org(name="Strict Test Org")
    
    # 2. Create Admin
    admin = api_client.create_user(
        org_id=org["id"],
        name="Strict Admin",
        roles=["admin"]
    )
    
    # 3. Login
    login_via_ui(page, APP_URL, admin["email"], admin["password"])
    
    # 4. Navigate to Admin
    # Wait for dashboard first to ensure login complete
    page.wait_for_url("**/app/schedule")
    
    # Click Admin nav button (strictly verify it exists)
    admin_btn = page.locator('button[data-view="admin"]')
    expect(admin_btn).to_be_visible()
    admin_btn.click()
    
    # Verify Admin Console loaded
    expect(page.locator('#admin-view')).to_be_visible()
    
    # Wait for network idle to ensure sidebar is rendered
    page.wait_for_load_state("networkidle")
    
    return page

def test_admin_tabs_strict(admin_page: Page):
    """Strictly verify all admin tabs exist and are clickable."""
    # 3. Verify tabs exist (Admin View in User App)
    # Tabs found in index.html: events, roles, solver, people, reports, teams
    tabs = ["events", "roles", "solver", "people", "reports", "teams"]
    
    for tab in tabs:
        btn = admin_page.locator(f'button[data-tab="{tab}"]')
        expect(btn).to_be_visible()
        
    # Verify we are on default tab (likely organizations or events) or can switch
    # We don't enforce which one is active initially, just that they exist
        expect(btn).to_be_enabled()

def test_people_tab_strict(admin_page: Page):
    """Strictly verify People tab content."""
    # Click People tab
    admin_page.locator('button[data-tab="people"]').click()
    
    # Verify tab content visible
    # In index.html, the ID is admin-tab-people
    expect(admin_page.locator('#admin-tab-people')).to_be_visible()
    expect(admin_page.locator('#admin-tab-people')).to_have_class(r"admin-tab-content active")
    
    # Verify Dropdown (Added in fix)
    dropdown = admin_page.locator('#people-org-filter')
    expect(dropdown).to_be_visible()
    expect(dropdown).to_contain_text("Strict Test Org", timeout=5000)

    # Verify People List
    expect(admin_page.locator('#admin-people-list')).to_be_visible()
    
    # Verify "Invite User" button (from index.html)
    add_btn = admin_page.locator('#admin-tab-people button[onclick="showInviteUserModal()"]')
    expect(add_btn).to_be_visible()
    
    # Verify Invite Modal
    add_btn.click()
    expect(admin_page.locator('#invite-user-modal')).to_be_visible()
    expect(admin_page.locator('#invite-email')).to_be_visible()
    
    # Close modal
    admin_page.locator('#invite-user-modal .btn-close').click()
    expect(admin_page.locator('#invite-user-modal')).not_to_be_visible()

def test_teams_tab_strict(admin_page: Page):
    """Strictly verify Teams tab content and dropdown."""
    # Click Teams tab
    admin_page.locator('button[data-tab="teams"]').click()
    
    # Verify tab content
    expect(admin_page.locator('#admin-tab-teams')).to_be_visible()
    
    # Verify Dropdown (this one exists in index.html)
    dropdown = admin_page.locator('#teams-org-filter')
    expect(dropdown).to_be_visible()
    # We expect it to contain the org name because app-admin.js should populate it
    # But we need to wait for population
    expect(dropdown).to_contain_text("Strict Test Org", timeout=5000)
    
    # Verify "Create Team" button
    add_btn = admin_page.locator('button[onclick="showCreateTeamForm()"]')
    expect(add_btn).to_be_visible()
    
    # Note: Create Team form might be a modal or inline, checking index.html...
    # It seems showCreateTeamForm() is not explicitly in index.html as a modal, 
    # but there is a button. Let's check if there is a modal or if it shows a form.
    # index.html doesn't show a #create-team-modal. It might be dynamically created or I missed it.
    # For now, just check the button exists.

def test_events_tab_strict(admin_page: Page):
    """Strictly verify Events tab content."""
    # Click Events tab
    admin_page.locator('button[data-tab="events"]').click()
    
    # Verify tab content
    expect(admin_page.locator('#admin-tab-events')).to_be_visible()
    
    # Verify Dropdown (Added in fix)
    dropdown = admin_page.locator('#events-org-filter')
    expect(dropdown).to_be_visible()
    expect(dropdown).to_contain_text("Strict Test Org", timeout=5000)

    # Verify Events List
    expect(admin_page.locator('#admin-events-list')).to_be_visible()
    
    # Verify "Create Event" button
    add_btn = admin_page.locator('button[onclick="showCreateEventForm()"]')
    expect(add_btn).to_be_visible()
    
    # Click Add Event and verify modal
    add_btn.click()
    expect(admin_page.locator('#create-event-modal')).to_be_visible()
    expect(admin_page.locator('#event-title')).to_be_visible()
    
    # Close modal
    admin_page.locator('#create-event-modal .btn-close').click()
    expect(admin_page.locator('#create-event-modal')).not_to_be_visible()
