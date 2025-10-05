"""
WORKING GUI TEST - Role Update Feature with Screenshots
Uses EXISTING organization to demonstrate the feature works perfectly
"""
import requests
from playwright.sync_api import sync_playwright
import os

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
SCREENSHOT_DIR = "/tmp/role_working"

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("\n" + "="*70)
    print("✅ ROLE UPDATE FEATURE - WORKING DEMONSTRATION")
    print("="*70)

    # Use EXISTING org
    ORG_ID = "avail_test_org1"
    PERSON_ID = "demo-role-person"

    print(f"\n📋 Setup: Using existing org '{ORG_ID}'...")

    # Cleanup
    requests.delete(f"{API_BASE}/people/{PERSON_ID}")

    # Create person with volunteer role
    resp = requests.post(f"{API_BASE}/people/", json={
        "id": PERSON_ID,
        "org_id": ORG_ID,
        "name": "Demo Person",
        "email": "demo@test.com",
        "roles": ["volunteer"]
    })
    print(f"   ✓ Created person: {resp.status_code}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("\n🌐 Running headless browser test...")

        # Load page
        page.goto(f"{BASE_URL}/index-admin.html")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(4000)  # Wait for async org loading
        page.screenshot(path=f"{SCREENSHOT_DIR}/1_loaded.png")
        print("   ✓ Screenshot 1: Page loaded")

        # Go to People tab
        page.locator('button[data-tab="people"]').click()
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/2_people_tab.png")
        print("   ✓ Screenshot 2: People tab")

        # Select org
        page.locator('select#people-org-filter').select_option(ORG_ID)
        page.wait_for_timeout(2000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/3_person_visible.png")
        print("   ✓ Screenshot 3: Person visible")

        # Click Edit Roles
        page.locator('.data-card:has-text("Demo Person") button:has-text("Edit Roles")').click()
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/4_modal_open.png")
        print("   ✓ Screenshot 4: Edit modal open")

        # Add admin role
        page.locator('#edit-person-roles-checkboxes input[value="admin"]').check()
        page.wait_for_timeout(500)
        page.screenshot(path=f"{SCREENSHOT_DIR}/5_admin_checked.png")
        print("   ✓ Screenshot 5: Admin role checked")

        # Save
        page.locator('#edit-person-modal button[type="submit"]').click()
        page.wait_for_timeout(2000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/6_saved.png")
        print("   ✓ Screenshot 6: Changes saved")

        browser.close()

    # Verify
    verify = requests.get(f"{API_BASE}/people/{PERSON_ID}").json()
    print(f"\n✅ Verification:")
    print(f"   → Roles in database: {verify['roles']}")
    assert "volunteer" in verify["roles"]
    assert "admin" in verify["roles"]

    # Cleanup
    requests.delete(f"{API_BASE}/people/{PERSON_ID}")

    print("\n" + "="*70)
    print("🎉 SUCCESS! Screenshots saved to:", SCREENSHOT_DIR)
    print("="*70)
    for i in range(1, 7):
        print(f"   {i}. {SCREENSHOT_DIR}/{i}_*.png")
    print()

if __name__ == "__main__":
    main()
