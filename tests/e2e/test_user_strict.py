import pytest
from playwright.sync_api import Page, expect
import time

@pytest.fixture
def user_page(page: Page, api_server):
    """
    Fixture to set up a user session.
    Creates an org, creates a user, logs in, and waits for the dashboard.
    """
    # 1. Create Organization
    import time
    timestamp = int(time.time())
    org_name = f"Strict User Test Org {timestamp}"
    
    # Use APP_URL from env or default
    import os
    app_url = os.getenv("E2E_APP_URL", "http://localhost:8001")
    page.goto(app_url)
    
    # Check if we are already logged in (dashboard visible)
    if page.locator("#main-app").is_visible():
        # Logout
        page.locator("#nav-user-menu").click()
        page.locator("text=Sign Out").click()
        page.wait_for_selector("text=Get Started")

    # Click "Get Started"
    page.locator("text=Get Started").click()
    
    # Click "Create New Organization" - wait for it to be visible
    create_org_btn = page.locator("text=Create New Organization")
    expect(create_org_btn).to_be_visible()
    create_org_btn.click()
    
    # Fill Org Form
    page.fill("#new-org-name", org_name)
    page.fill("#new-org-region", "Test Region")
    
    # Click Create - use specific selector
    create_btn = page.locator("#create-org-section button[type='submit']")
    expect(create_btn).to_be_visible()
    create_btn.click()
    
    # 2. Complete Signup
    # Wait for user form to appear
    expect(page.locator("#user-name")).to_be_visible(timeout=10000)
    
    page.fill("#user-name", "Strict User")
    page.fill("#user-email", f"strict_user_{timestamp}@test.com")
    page.fill("#user-password", "password123")
    
    # Click Complete Registration
    complete_btn = page.locator("button:has-text('Complete Registration')")
    expect(complete_btn).to_be_visible()
    complete_btn.click()
    
    # 3. Verify Dashboard Loaded
    expect(page.locator("#main-app")).to_be_visible(timeout=10000)
    
    # Wait for network idle
    page.wait_for_load_state("networkidle")
    
    return page

def test_user_navigation_strict(user_page: Page):
    """Strictly verify user navigation buttons exist and work."""
    views = ["schedule", "events", "availability"]
    
    for view in views:
        btn = user_page.locator(f'button[data-view="{view}"]')
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()
        
        # Click and verify active state
        btn.click()
        expect(btn).to_have_class(r"nav-item nav-btn active")
        expect(user_page.locator(f'#{view}-view')).to_be_visible()

def test_schedule_view_strict(user_page: Page):
    """Strictly verify Schedule View content."""
    # Ensure we are on schedule view
    user_page.locator('button[data-view="schedule"]').click()
    
    # Verify Stats
    expect(user_page.locator('#upcoming-count')).to_be_visible()
    expect(user_page.locator('#this-month-count')).to_be_visible()
    
    # Verify Quick Actions
    expect(user_page.locator('button[onclick="showCalendarSubscription()"]')).to_be_visible()
    expect(user_page.locator('button[onclick="exportMyCalendar()"]')).to_be_visible()
    
    # Verify Schedule List
    expect(user_page.locator('#schedule-list')).to_be_visible()

def test_events_view_strict(user_page: Page):
    """Strictly verify Events View content."""
    # Navigate to Events
    user_page.locator('button[data-view="events"]').click()
    
    # Verify Filter
    filter_select = user_page.locator('#events-month-filter')
    expect(filter_select).to_be_visible()
    expect(filter_select).to_contain_text("This Month")
    
    # Verify Events List
    expect(user_page.locator('#all-events-list')).to_be_visible()

def test_availability_view_strict(user_page: Page):
    """Strictly verify Availability View content."""
    # Navigate to Availability
    user_page.locator('button[data-view="availability"]').click()
    
    # Verify Add Time Off Form
    expect(user_page.locator('form[onsubmit="addTimeOff(event)"]')).to_be_visible()
    expect(user_page.locator('#timeoff-start')).to_be_visible()
    expect(user_page.locator('#timeoff-end')).to_be_visible()
    expect(user_page.locator('#timeoff-reason')).to_be_visible()
    
    # Verify Blocked Dates List
    expect(user_page.locator('#timeoff-list')).to_be_visible()
