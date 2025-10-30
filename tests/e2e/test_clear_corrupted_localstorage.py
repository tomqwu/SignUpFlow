"""Test to demonstrate and fix corrupted localStorage org_id=xyz issue."""

from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"

def test_clear_corrupted_localstorage(page: Page):
    """
    Simulate corrupted localStorage with org_id=xyz and verify clearing fixes it.

    This demonstrates the issue the user is experiencing:
    - Browser has old localStorage with org_id="xyz"
    - API calls fail with 404 because org "xyz" doesn't exist
    - Solution: Clear localStorage
    """
    print("\n🔍 Test: Corrupted localStorage with org_id=xyz")

    # Step 1: Navigate to app
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')

    # Step 2: Inject corrupted localStorage (simulating user's state)
    print("\n⚠️  Injecting corrupted localStorage with org_id=xyz...")
    page.evaluate("""() => {
        localStorage.setItem('roster_user', JSON.stringify({
            id: 'person_test',
            name: 'Test User',
            email: 'test@test.com',
            org_id: 'xyz',  // ← CORRUPTED VALUE
            roles: ['volunteer'],
            timezone: 'UTC',
            language: 'en'
        }));
        localStorage.setItem('roster_org', JSON.stringify({
            id: 'xyz',  // ← CORRUPTED VALUE
            name: 'XYZ Organization'
        }));
        localStorage.setItem('authToken', 'fake-token-12345');
    }""")

    # Step 3: Reload page to trigger API calls with corrupted org_id
    print("\n🔄 Reloading page to trigger API calls with corrupted org_id...")
    page.reload()
    page.wait_for_timeout(2000)  # Wait for API calls

    # Step 4: Verify corrupted state in console
    local_storage = page.evaluate("""() => {
        return {
            roster_user: JSON.parse(localStorage.getItem('roster_user') || 'null'),
            roster_org: JSON.parse(localStorage.getItem('roster_org') || 'null')
        };
    }""")

    print(f"\n💾 localStorage state:")
    print(f"   roster_user.org_id: {local_storage['roster_user']['org_id']}")
    print(f"   roster_org.id: {local_storage['roster_org']['id']}")

    assert local_storage['roster_user']['org_id'] == 'xyz', "Should have corrupted org_id"
    assert local_storage['roster_org']['id'] == 'xyz', "Should have corrupted org_id"

    # Step 5: Clear localStorage (THE FIX)
    print("\n🧹 Clearing corrupted localStorage...")
    page.evaluate("() => localStorage.clear()")

    # Step 6: Verify localStorage is cleared
    local_storage_after = page.evaluate("""() => {
        return {
            roster_user: localStorage.getItem('roster_user'),
            roster_org: localStorage.getItem('roster_org'),
            authToken: localStorage.getItem('authToken')
        };
    }""")

    print(f"\n✅ localStorage after clearing:")
    print(f"   roster_user: {local_storage_after['roster_user']}")
    print(f"   roster_org: {local_storage_after['roster_org']}")
    print(f"   authToken: {local_storage_after['authToken']}")

    assert local_storage_after['roster_user'] is None, "Should be cleared"
    assert local_storage_after['roster_org'] is None, "Should be cleared"
    assert local_storage_after['authToken'] is None, "Should be cleared"

    # Step 7: Reload and verify redirect to login
    print("\n🔄 Reloading page - should redirect to login...")
    page.reload()
    page.wait_for_timeout(2000)

    # Should be on login page now
    current_url = page.url
    print(f"\n🌐 Current URL: {current_url}")

    # Verify on login page or home page (not app page)
    assert '/app/' not in current_url, "Should not be on app page without session"

    print("\n✅ TEST PASSED: localStorage cleared successfully")
    print("\n📝 USER ACTION REQUIRED:")
    print("   1. Open browser DevTools (F12)")
    print("   2. Go to Application/Storage tab")
    print("   3. Click 'Clear storage' or run: localStorage.clear()")
    print("   4. Reload the page")
    print("   5. Login again\n")


if __name__ == "__main__":
    test_clear_corrupted_localstorage()
