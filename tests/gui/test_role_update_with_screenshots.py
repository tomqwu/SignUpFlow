"""
Headless GUI test for role update feature WITH SCREENSHOTS
This test proves the feature works by capturing visual evidence
"""
import requests
from playwright.sync_api import sync_playwright
import os

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
SCREENSHOT_DIR = "/tmp/role_update_screenshots"


def test_role_update_with_screenshots():
    """Test role update feature and capture screenshots as proof"""

    # Create screenshot directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("\n" + "="*70)
    print("🧪 ROLE UPDATE FEATURE - HEADLESS TEST WITH SCREENSHOTS")
    print("="*70)

    # STEP 1: Setup data BEFORE loading page
    print("\n📋 STEP 1: Setting up test data...")

    # Clean up any existing test data
    requests.delete(f"{API_BASE}/people/test-person-role")
    requests.delete(f"{API_BASE}/organizations/demo-org")

    # Create organization
    org_resp = requests.post(f"{API_BASE}/organizations/", json={
        "id": "demo-org",
        "name": "Demo Organization"
    })
    print(f"   ✓ Created organization: {org_resp.status_code}")

    # Create test person with initial roles
    person_resp = requests.post(f"{API_BASE}/people/", json={
        "id": "test-person-role",
        "org_id": "demo-org",
        "name": "Test Person",
        "email": "test@demo.com",
        "roles": ["volunteer"]
    })
    print(f"   ✓ Created person with 'volunteer' role: {person_resp.status_code}")

    # STEP 2: Run headless browser test
    print("\n🌐 STEP 2: Running headless browser test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Load admin page
        print("   → Loading admin page...")
        page.goto(f"{BASE_URL}/index-admin.html")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)  # Wait for async org loading

        # Screenshot 1: Initial page load
        screenshot1 = f"{SCREENSHOT_DIR}/01_page_loaded.png"
        page.screenshot(path=screenshot1)
        print(f"   ✓ Screenshot 1: {screenshot1}")

        # Navigate to People tab
        print("   → Navigating to People tab...")
        people_tab = page.locator('button.tab-btn[data-tab="people"]')
        people_tab.click()
        page.wait_for_timeout(1000)

        # Screenshot 2: People tab
        screenshot2 = f"{SCREENSHOT_DIR}/02_people_tab.png"
        page.screenshot(path=screenshot2)
        print(f"   ✓ Screenshot 2: {screenshot2}")

        # Select organization
        print("   → Selecting organization...")
        org_select = page.locator('select#people-org-filter')

        # Wait for org to be available
        page.wait_for_timeout(2000)
        options_html = org_select.inner_html()
        print(f"   → Dropdown options: {options_html[:200]}...")

        org_select.select_option("demo-org")
        page.wait_for_timeout(2000)

        # Screenshot 3: Organization selected, people visible
        screenshot3 = f"{SCREENSHOT_DIR}/03_org_selected.png"
        page.screenshot(path=screenshot3)
        print(f"   ✓ Screenshot 3: {screenshot3}")

        # Find and click Edit Roles button
        print("   → Clicking Edit Roles button...")
        person_card = page.locator('.data-card:has-text("Test Person")')
        edit_btn = person_card.locator('button:has-text("Edit Roles")')
        edit_btn.click()
        page.wait_for_timeout(1000)

        # Screenshot 4: Edit modal open
        screenshot4 = f"{SCREENSHOT_DIR}/04_edit_modal_open.png"
        page.screenshot(path=screenshot4)
        print(f"   ✓ Screenshot 4: {screenshot4}")

        # Check admin checkbox
        print("   → Adding 'admin' role...")
        admin_checkbox = page.locator('#edit-person-roles-checkboxes input[value="admin"]')
        admin_checkbox.check()
        page.wait_for_timeout(500)

        # Screenshot 5: Admin role checked
        screenshot5 = f"{SCREENSHOT_DIR}/05_admin_checked.png"
        page.screenshot(path=screenshot5)
        print(f"   ✓ Screenshot 5: {screenshot5}")

        # Save changes
        print("   → Saving changes...")
        save_btn = page.locator('#edit-person-modal button[type="submit"]')
        save_btn.click()
        page.wait_for_timeout(2000)

        # Screenshot 6: Modal closed, roles updated
        screenshot6 = f"{SCREENSHOT_DIR}/06_roles_updated.png"
        page.screenshot(path=screenshot6)
        print(f"   ✓ Screenshot 6: {screenshot6}")

        browser.close()

    # STEP 3: Verify via API
    print("\n✅ STEP 3: Verifying changes via API...")
    verify_resp = requests.get(f"{API_BASE}/people/test-person-role")
    data = verify_resp.json()

    print(f"   → Person roles: {data['roles']}")
    assert "volunteer" in data["roles"], "Volunteer role should still exist"
    assert "admin" in data["roles"], "Admin role should be added"
    print("   ✓ Roles verified in database!")

    # Cleanup
    requests.delete(f"{API_BASE}/people/test-person-role")
    requests.delete(f"{API_BASE}/organizations/demo-org")

    print("\n" + "="*70)
    print("🎉 TEST PASSED! Screenshots saved to:", SCREENSHOT_DIR)
    print("="*70)
    print("\nScreenshots captured:")
    for i, name in enumerate([
        "01_page_loaded.png",
        "02_people_tab.png",
        "03_org_selected.png",
        "04_edit_modal_open.png",
        "05_admin_checked.png",
        "06_roles_updated.png"
    ], 1):
        print(f"  {i}. {SCREENSHOT_DIR}/{name}")
    print()


if __name__ == "__main__":
    test_role_update_with_screenshots()
