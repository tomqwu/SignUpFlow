"""Tests for verifying the teams dropdown functionality."""
import os
import json
import pytest
from playwright.sync_api import sync_playwright, expect, Page
from tests.e2e.helpers import AppConfig, ApiTestClient

APP_URL = os.getenv("E2E_APP_URL", "http://localhost:8001")
API_URL = f"{APP_URL}/api"

@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        browser.close()

def test_teams_dropdown_populated(page: Page, app_config: AppConfig, api_client: ApiTestClient):
    """
    Test teams dropdown population.

    Verifies that the teams dropdown is correctly populated with the teams
    created in the organization.
    """
    # Setup data
    org = api_client.create_org()
    APP_URL = app_config.app_url
    API_URL = app_config.api_base
    
    # 1. Setup: Create Org and User via API
    org_id = f"test-org-teams-{os.urandom(4).hex()}"
    org_name = "Test Org Teams"
    
    # Create Org
    page.request.post(f"{API_URL}/organizations/", data={
        "id": org_id,
        "name": org_name,
        "slug": org_id
    })
    
    # Create User
    email = f"test_teams_{os.urandom(4).hex()}@example.com"
    password = "password123"
    
    page.request.post(f"{API_URL}/auth/signup", data={
        "email": email,
        "password": password,
        "name": "Test User Teams",
        "org_id": org_id
    })
    
    # 2. Login
    page.goto(APP_URL)
    
    # Click Sign In if present (landing page might show signup by default)
    if page.locator('a:has-text("Sign in")').count() > 0:
        page.locator('a:has-text("Sign in")').click()
        
    page.wait_for_selector('#login-email')
    page.fill('#login-email', email)
    page.fill('input[type="password"]', password)
    
    # Use robust click for sign in
    try:
        page.click('form button[type="submit"]', timeout=5000)
    except:
        page.click('form button[type="submit"]', force=True)
    
    # Wait for dashboard
    try:
        page.wait_for_url("**/app/schedule", timeout=10000)
        page.wait_for_load_state("networkidle")
    except:
        # Debug if login fails
        print(f"Login failed? URL: {page.url}")
        print(page.content())
        raise
    
    # 3. Navigate to Admin -> Teams
    print("Navigating to Admin (direct URL)...")
    page.goto(f"{APP_URL}/app/admin")
    try:
        page.wait_for_selector('#admin-view', timeout=10000)
        print("Admin view loaded")
    except:
        print("Admin view NOT loaded")
        print(page.content())
        raise
    
    # Click Teams tab
    print("Clicking Teams tab...")
    page.click('button[data-tab="teams"]')
    try:
        page.wait_for_selector('#admin-tab-teams.active', timeout=5000)
        print("Teams tab active")
    except:
        print("Teams tab NOT active")
        print(page.content())
        raise
    
    # 4. Verify Dropdown
    dropdown = page.locator('#teams-org-filter')
    expect(dropdown).to_be_visible()
    
    # Check content
    # It should have the org name
    content = dropdown.inner_text()
    print(f"Dropdown content: {content}")
    
    assert org_name in content, f"Dropdown should contain '{org_name}'"
    assert "Select Organization" not in content or org_name in content, "Dropdown should not ONLY show 'Select Organization'"
    
    # Check value
    value = dropdown.input_value()
    assert value == org_id, f"Dropdown value should be '{org_id}'"
    
    print("Teams dropdown verification passed!")
