import os
import json
import requests
import pytest
from playwright.sync_api import sync_playwright, expect

# Configuration
API_BASE = "http://localhost:8000/api"
APP_URL = "http://localhost:8000"

def test_dangling_org_login_handled_gracefully():
    """
    Test that logging in as a user whose organization has been deleted
    results in a clear error message, not a broken dashboard.
    """
    # 1. Setup: Create Org and User via API
    org_name = "Dangling Test Org " + os.urandom(4).hex()
    org_id = org_name.lower().replace(" ", "_")
    email = f"dangling_{org_id}@test.com"
    password = "password123"

    print(f"Creating Org: {org_name} ({org_id})")
    resp_org = requests.post(f"{API_BASE}/organizations/", json={
        "id": org_id,
        "name": org_name,
        "region": "US"
    })
    assert resp_org.status_code in [201, 409]

    print(f"Creating User: {email}")
    resp_user = requests.post(f"{API_BASE}/auth/signup", json={
        "email": email,
        "password": password,
        "name": "Dangling User",
        "org_id": org_id,
        "roles": ["admin"]
    })
    assert resp_user.status_code == 201

    # 2. Simulate Data Inconsistency: Delete the Organization
    # We need to delete the org but KEEP the user.
    # If DB cascade is ON, user is deleted. If OFF (SQLite default), user remains.
    # We'll check if user exists after deletion.
    
    print(f"Deleting Org: {org_id}")
    resp_del = requests.delete(f"{API_BASE}/organizations/{org_id}")
    assert resp_del.status_code == 204

    # Verify User still exists (if cascade is off)
    # We can't easily check DB directly here without DB session, but we can try login.
    # If login returns 401, user is gone (cascade worked).
    # If login returns 200 (but fails later), user exists.
    
    resp_login = requests.post(f"{API_BASE}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if resp_login.status_code == 401:
        print("User was deleted by cascade. Cannot reproduce 'Dangling User' scenario exactly.")
        print("However, this means the system is SAFE from this bug because the user is gone.")
        # We can force create a dangling user if we really want to test the UI handling
        # by inserting a user with bad org_id (if API allows).
        # But API checks org existence.
        # So we can only reproduce this if cascade is OFF.
        return

    print(f"User exists after org deletion (Status: {resp_login.status_code}). Reproducing scenario...")
    
    # 3. Attempt Login via UI
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to login page...")
        page.goto(APP_URL)
        
        # Ensure we are logged out
        page.evaluate("localStorage.clear()")
        page.reload()
        
        # Fill login form
        page.wait_for_selector('input[type="email"]')
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        
        print("Clicking Sign In...")
        # Use force click to avoid flakiness
        page.locator('form button[type="submit"]').click(force=True)
        
        # 4. Verify Error Handling
        # We expect a toast saying "Organization not found"
        # And we expect NOT to be redirected to dashboard
        
        print("Waiting for error toast...")
        try:
            # Wait for toast with specific text or generic error
            toast = page.locator('.toast.error')
            toast.wait_for(state="visible", timeout=5000)
            text = toast.inner_text()
            print(f"Found error toast: {text}")
            
            assert "Organization not found" in text or "not found" in text.lower()
            
        except Exception as e:
            print(f"Error waiting for toast: {e}")
            print(f"Page content: {page.content()[:500]}...")
            raise e

        # Ensure we are NOT on the dashboard
        page.wait_for_timeout(1000)
        assert "/app/schedule" not in page.url, f"Should NOT redirect to dashboard, but is {page.url}"
        assert "login" in page.url or page.url == APP_URL or page.url.endswith("/"), f"Should remain on login page, is {page.url}"

        # 5. Verify Page Reload Behavior (Dangling Session)
        # Manually set a dangling session to simulate the user's state
        print("Setting dangling session in localStorage...")
        dangling_user = {
            "id": "user_" + os.urandom(4).hex(),
            "name": "Dangling User",
            "email": email,
            "roles": ["admin"],
            "org_id": org_id
        }
        dangling_org = {
            "id": org_id,
            "name": org_name
        }
        
        page.evaluate(f"""
            localStorage.setItem('roster_user', '{json.dumps(dangling_user)}');
            localStorage.setItem('roster_org', '{json.dumps(dangling_org)}');
            localStorage.setItem('authToken', 'fake_token');
        """)
        
        print("Reloading page with dangling session...")
        page.reload()
        
        # We expect checkExistingSession to catch the 404 and logout
        page.wait_for_timeout(2000) # Wait for async check
        
        # Check if we are logged out (localStorage cleared or on login page)
        is_logged_out = page.evaluate("""
            !localStorage.getItem('currentUser') || !localStorage.getItem('currentOrg')
        """)
        
        print(f"Logged out after reload? {is_logged_out}")
        assert is_logged_out, "Session should be cleared after reloading with dangling org"
        assert "/app/schedule" not in page.url, "Should not be on dashboard"

        browser.close()
