"""
GUI test for role update feature in Admin Console
"""
import requests
from playwright.sync_api import sync_playwright, expect
import pytest

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def test_role_update_gui():
    """Test updating person roles through GUI"""
    print("\n🧪 Testing Role Update GUI Feature...")

    # Setup: Create test organization and person
    org_data = {"id": "test-role-gui-org", "name": "Test Role GUI Org"}
    requests.post(f"{API_BASE}/organizations/", json=org_data)

    # Create admin user
    admin_data = {
        "id": "admin-role-test",
        "org_id": "test-role-gui-org",
        "name": "Admin User",
        "email": "admin@test.com",
        "password": "admin123",
        "roles": ["admin", "super_admin"]
    }
    requests.post(f"{API_BASE}/people/", json=admin_data)

    # Create test person with initial roles
    person_data = {
        "id": "test-person-role-update",
        "org_id": "test-role-gui-org",
        "name": "Test Person",
        "email": "testperson@test.com",
        "roles": ["volunteer"]
    }
    requests.post(f"{API_BASE}/people/", json=person_data)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 1. Load admin page
        print("  1. Loading admin page...")
        page.goto(f"{BASE_URL}/index-admin.html")
        page.wait_for_load_state('networkidle')
        print("     ✓ Page loaded")

        # 2. Navigate to People tab
        print("  2. Navigating to People tab...")
        people_tab = page.locator('button.tab-btn[data-tab="people"]')
        people_tab.click()
        page.wait_for_timeout(1000)
        print("     ✓ On People tab")

        # 3. Wait for organizations to load and select organization
        print("  3. Waiting for organizations to load...")
        # Wait for the option to be available
        page.wait_for_selector('select#people-org-filter option[value="test-role-gui-org"]', timeout=10000)

        print("  4. Selecting organization...")
        org_select = page.locator('select#people-org-filter')
        org_select.select_option("test-role-gui-org")
        page.wait_for_timeout(2000)
        print("     ✓ Organization selected")

        # 5. Verify person appears with initial role
        print("  5. Verifying person appears...")
        person_card = page.locator('.data-card:has-text("Test Person")')
        expect(person_card).to_be_visible()

        # Check initial role badge
        volunteer_badge = person_card.locator('.badge:has-text("volunteer")')
        expect(volunteer_badge).to_be_visible()
        print("     ✓ Person visible with 'volunteer' role")

        # 5. Click Edit Roles button
        print("  5. Clicking Edit Roles button...")
        edit_btn = person_card.locator('button:has-text("Edit Roles")')
        expect(edit_btn).to_be_visible()
        edit_btn.click()
        page.wait_for_timeout(1000)
        print("     ✓ Edit Roles button clicked")

        # 6. Verify modal opens
        print("  6. Verifying modal opens...")
        modal = page.locator('#edit-person-modal')
        expect(modal).not_to_have_class('hidden')

        modal_title = page.locator('#edit-person-name')
        expect(modal_title).to_have_text('Test Person')
        print("     ✓ Modal opened with correct person name")

        # 7. Verify volunteer checkbox is checked
        print("  7. Verifying initial role checkboxes...")
        volunteer_checkbox = page.locator('#edit-person-roles-checkboxes input[value="volunteer"]')
        expect(volunteer_checkbox).to_be_checked()
        print("     ✓ Volunteer checkbox is checked")

        # 8. Update roles: add 'admin' and 'leader', keep 'volunteer'
        print("  8. Updating roles...")
        admin_checkbox = page.locator('#edit-person-roles-checkboxes input[value="admin"]')
        leader_checkbox = page.locator('#edit-person-roles-checkboxes input[value="leader"]')

        admin_checkbox.check()
        leader_checkbox.check()
        page.wait_for_timeout(500)
        print("     ✓ Checked admin and leader roles")

        # 9. Save changes
        print("  9. Saving changes...")
        save_btn = page.locator('#edit-person-modal button[type="submit"]')
        save_btn.click()
        page.wait_for_timeout(2000)
        print("     ✓ Save button clicked")

        # 10. Verify modal closes
        print("  10. Verifying modal closes...")
        expect(modal).to_have_class('hidden')
        print("     ✓ Modal closed")

        # 11. Verify updated roles appear on person card
        print("  11. Verifying updated roles...")
        page.wait_for_timeout(1000)

        volunteer_badge_updated = person_card.locator('.badge:has-text("volunteer")')
        admin_badge = person_card.locator('.badge:has-text("admin")')
        leader_badge = person_card.locator('.badge:has-text("leader")')

        expect(volunteer_badge_updated).to_be_visible()
        expect(admin_badge).to_be_visible()
        expect(leader_badge).to_be_visible()
        print("     ✓ All three roles visible on card")

        # 12. Verify via API that roles persisted
        print("  12. Verifying roles persisted via API...")
        response = requests.get(f"{API_BASE}/people/test-person-role-update")
        data = response.json()
        assert "volunteer" in data["roles"]
        assert "admin" in data["roles"]
        assert "leader" in data["roles"]
        assert len(data["roles"]) == 3
        print("     ✓ Roles persisted in database")

        # 13. Test removing a role
        print("  13. Testing role removal...")
        edit_btn.click()
        page.wait_for_timeout(1000)

        # Uncheck volunteer
        volunteer_checkbox = page.locator('#edit-person-roles-checkboxes input[value="volunteer"]')
        volunteer_checkbox.uncheck()
        page.wait_for_timeout(500)

        save_btn = page.locator('#edit-person-modal button[type="submit"]')
        save_btn.click()
        page.wait_for_timeout(2000)
        print("     ✓ Removed volunteer role")

        # 14. Verify volunteer role is gone
        print("  14. Verifying role removed...")
        page.wait_for_timeout(1000)

        # Volunteer badge should not exist
        volunteer_count = person_card.locator('.badge:has-text("volunteer")').count()
        assert volunteer_count == 0, "Volunteer badge should be removed"

        # Admin and leader should still exist
        expect(admin_badge).to_be_visible()
        expect(leader_badge).to_be_visible()
        print("     ✓ Volunteer role removed, admin and leader remain")

        # 15. Verify via API
        print("  15. Final API verification...")
        response = requests.get(f"{API_BASE}/people/test-person-role-update")
        data = response.json()
        assert "volunteer" not in data["roles"]
        assert "admin" in data["roles"]
        assert "leader" in data["roles"]
        assert len(data["roles"]) == 2
        print("     ✓ Final state verified in database")

        browser.close()

    # Cleanup
    requests.delete(f"{API_BASE}/people/test-person-role-update")
    requests.delete(f"{API_BASE}/people/admin-role-test")
    requests.delete(f"{API_BASE}/organizations/test-role-gui-org")

    print("\n✅ Role Update GUI Test Passed!")


if __name__ == "__main__":
    test_role_update_gui()
