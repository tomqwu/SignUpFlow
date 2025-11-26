
import pytest
from playwright.sync_api import sync_playwright, expect
import requests
import os

# Use environment variable for test server port (default 8000)
TEST_SERVER_PORT = os.getenv("TEST_SERVER_PORT", "8000")
APP_URL = f"http://localhost:{TEST_SERVER_PORT}"
API_BASE = f"{APP_URL}/api"

class TestOrgDropdown:
    def test_org_dropdown_exists(self):
        """
        Test that the organization dropdown exists and is visible for a user.
        """
        # 1. Create a user and organization via API
        org_id = "dropdown_test_org"
        email = "dropdown_test@example.com"
        password = "password123"

        # Ensure org exists
        requests.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Dropdown Test Org",
            "region": "US"
        })

        # Signup user
        requests.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Dropdown Test User",
            "email": email,
            "password": password,
            "roles": ["admin"]
        })

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 2. Login
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', email)
            page.fill('input[type="password"]', password)
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            # 3. Check for org dropdown
            # The dropdown might be hidden or replaced by a display, but the user expects a dropdown.
            # Based on index.html, there is #org-dropdown and #org-dropdown-visible
            
            # We expect at least one of them to be visible and contain options
            dropdown = page.locator('#org-dropdown')
            visible_dropdown = page.locator('#org-dropdown-visible')
            
            # Check if either is visible
            is_visible = False
            if dropdown.is_visible():
                is_visible = True
            elif visible_dropdown.is_visible():
                is_visible = True
            
            # This assertion is expected to fail currently because loadUserOrganizations hides it
            assert is_visible, "Organization dropdown should be visible"
            
            browser.close()
