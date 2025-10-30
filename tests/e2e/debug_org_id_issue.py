"""Debug test to investigate org_id=xyz errors in browser."""

from playwright.sync_api import sync_playwright, expect
import time

BASE_URL = "http://localhost:8000"

def test_debug_org_id_issue():
    """Debug test to see what org_id is being used."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Track all network requests
        requests = []
        page.on("request", lambda request: requests.append({
            "url": request.url,
            "method": request.method
        }))

        # Track console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # Track errors
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("\n🔍 Debug: Loading fresh page without login")
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        print("\n🔍 Debug: Check localStorage")
        local_storage = page.evaluate("""() => {
            return {
                roster_user: localStorage.getItem('roster_user'),
                roster_org: localStorage.getItem('roster_org')
            };
        }""")
        print(f"localStorage: {local_storage}")

        print("\n🔍 Debug: Check global variables")
        globals_check = page.evaluate("""() => {
            return {
                currentUser: window.currentUser,
                currentOrg: window.currentOrg
            };
        }""")
        print(f"Global variables: {globals_check}")

        print("\n🔍 Debug: Filter requests with org_id parameter")
        org_id_requests = [r for r in requests if 'org_id=' in r['url']]
        for req in org_id_requests:
            print(f"  {req['method']} {req['url']}")

        if org_id_requests:
            print(f"\n⚠️  Found {len(org_id_requests)} requests with org_id parameter before login!")
            print("This might be the source of the xyz error")

        print("\n🔍 Debug: Now login as pastor@grace.church")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_timeout(500)
        page.locator('#login-email').fill('pastor@grace.church')
        page.locator('#login-password').fill('password')
        page.locator('button[type="submit"]:has-text("Sign In")').click()

        # Wait for main app
        expect(page.locator('#main-app:not(.hidden)')).to_be_visible(timeout=10000)
        print("✓ Logged in successfully")

        print("\n🔍 Debug: Check localStorage AFTER login")
        local_storage_after = page.evaluate("""() => {
            return {
                roster_user: JSON.parse(localStorage.getItem('roster_user') || 'null'),
                roster_org: JSON.parse(localStorage.getItem('roster_org') || 'null')
            };
        }""")
        print(f"localStorage after login:")
        print(f"  User: {local_storage_after['roster_user']}")
        print(f"  Org: {local_storage_after['roster_org']}")

        if local_storage_after['roster_org']:
            org_id = local_storage_after['roster_org'].get('id')
            print(f"\n✓ Org ID from localStorage: {org_id}")

            # Check if any requests are using 'xyz'
            xyz_requests = [r for r in requests if 'xyz' in r['url']]
            if xyz_requests:
                print(f"\n⚠️  FOUND {len(xyz_requests)} REQUESTS WITH 'xyz':")
                for req in xyz_requests:
                    print(f"  {req['method']} {req['url']}")
            else:
                print("\n✓ No requests with 'xyz' found")

        # Print any console errors
        if errors:
            print("\n❌ JavaScript errors detected:")
            for err in errors[-10:]:
                print(f"  {err}")
        else:
            print("\n✓ No JavaScript errors")

        # Print recent console messages
        print("\n📋 Recent console messages:")
        for msg in console_messages[-10:]:
            print(f"  {msg}")

        browser.close()

if __name__ == "__main__":
    test_debug_org_id_issue()
