"""
Complete Admin Workflow Demo - Shows admin user from login to export
Demonstrates: Login → Navigate to Admin → Run Solver → View Schedules → Export
"""
from playwright.sync_api import sync_playwright
import requests
import time

BASE_URL = "http://localhost:8000"

def demo_admin_workflow():
    print("\n" + "="*70)
    print("🎬 ROSTIO ADMIN COMPLETE WORKFLOW DEMONSTRATION")
    print("="*70)

    with sync_playwright() as p:
        # Launch browser in headed mode to show the user
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # STEP 1: Login as Admin
        print("\n📋 STEP 1: Admin Login")
        print("-" * 70)
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

        print("   👤 User: pastor@grace.church (Admin)")
        page.fill('#login-email', 'pastor@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

        page.screenshot(path='docs/screenshots/admin-01-logged-in.png')
        print("   ✅ Logged in successfully")
        print("   📸 Screenshot: docs/screenshots/admin-01-logged-in.png")

        # STEP 2: Navigate to Admin Dashboard
        print("\n📋 STEP 2: Navigate to Admin Dashboard")
        print("-" * 70)
        admin_tab = page.locator('button:has-text("Admin Dashboard")')
        admin_tab.click()
        page.wait_for_timeout(1500)

        page.screenshot(path='docs/screenshots/admin-02-dashboard.png')
        print("   ✅ Admin Dashboard opened")
        print("   📸 Screenshot: docs/screenshots/admin-02-dashboard.png")

        # STEP 3: Check existing solutions
        print("\n📋 STEP 3: Check Existing Solutions")
        print("-" * 70)
        response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
        initial_data = response.json()
        print(f"   📊 Current solutions: {initial_data['total']}")
        for sol in initial_data['solutions']:
            print(f"      - Solution {sol['id']}: {sol['assignment_count']} assignments")

        # STEP 4: Run Solver
        print("\n📋 STEP 4: Run Solver to Generate Schedule")
        print("-" * 70)
        print("   🔄 Clicking 'Generate Schedule' button...")

        generate_btn = page.locator('button:has-text("Generate")')
        generate_btn.click()
        print("   ⏳ Solver running...")
        page.wait_for_timeout(6000)  # Wait for solver to complete

        page.screenshot(path='docs/screenshots/admin-03-after-solve.png')
        print("   📸 Screenshot: docs/screenshots/admin-03-after-solve.png")

        # STEP 5: Verify new solution created
        print("\n📋 STEP 5: Verify New Solution Created")
        print("-" * 70)
        response = requests.get(f"{BASE_URL}/api/solutions/?org_id=grace-church")
        after_data = response.json()
        print(f"   📊 Solutions after solver: {after_data['total']}")

        new_solutions = []
        for sol in after_data['solutions']:
            print(f"      - Solution {sol['id']}: {sol['assignment_count']} assignments (Health: {sol['health_score']})")
            if sol['id'] not in [s['id'] for s in initial_data['solutions']]:
                new_solutions.append(sol)

        if new_solutions:
            print(f"\n   ✅ SUCCESS: {len(new_solutions)} new solution(s) created!")
            for sol in new_solutions:
                print(f"      🎯 Solution {sol['id']}: {sol['assignment_count']} assignments")

                # Get detailed assignments
                resp = requests.get(f"{BASE_URL}/api/solutions/{sol['id']}/assignments")
                assignments = resp.json()
                print(f"         Total assignment records: {assignments['total']}")
                print(f"         Sample assignments:")
                for i, asn in enumerate(assignments['assignments'][:3]):
                    print(f"           {i+1}. {asn['person_name']} → {asn['event_type']} on {asn['event_start'][:10]}")
        else:
            print("   ⚠️  No new solution created")

        # STEP 6: Test Export Functionality
        print("\n📋 STEP 6: Test Export Functionality")
        print("-" * 70)
        if after_data['solutions']:
            latest_solution = after_data['solutions'][0]
            solution_id = latest_solution['id']

            print(f"   📤 Exporting Solution {solution_id}...")

            # Test JSON export
            export_response = requests.post(
                f"{BASE_URL}/api/solutions/{solution_id}/export",
                json={"format": "json", "scope": "org"}
            )

            if export_response.status_code == 200:
                print(f"   ✅ Export successful!")
                print(f"      Format: JSON")
                print(f"      Size: {len(export_response.content)} bytes")

                # Save export to file
                with open('/tmp/schedule_export.json', 'wb') as f:
                    f.write(export_response.content)
                print(f"      💾 Saved to: /tmp/schedule_export.json")

                # Show preview
                import json
                try:
                    data = json.loads(export_response.content)
                    if 'assignments' in data:
                        print(f"      📋 Assignments in export: {len(data['assignments'])}")
                except:
                    pass
            else:
                print(f"   ❌ Export failed: {export_response.status_code}")
                print(f"      Error: {export_response.text[:200]}")

        # STEP 7: Final Screenshot
        print("\n📋 STEP 7: Final State")
        print("-" * 70)
        page.screenshot(path='docs/screenshots/admin-04-final.png', full_page=True)
        print("   📸 Final screenshot: docs/screenshots/admin-04-final.png")

        browser.close()

    print("\n" + "="*70)
    print("✅ ADMIN WORKFLOW DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n📁 Screenshots saved to docs/screenshots/:")
    print("   1. admin-01-logged-in.png - After admin login")
    print("   2. admin-02-dashboard.png - Admin dashboard view")
    print("   3. admin-03-after-solve.png - After running solver")
    print("   4. admin-04-final.png - Final state")
    print("\n💾 Export saved to:")
    print("   - /tmp/schedule_export.json")
    print("\n")

if __name__ == "__main__":
    demo_admin_workflow()
