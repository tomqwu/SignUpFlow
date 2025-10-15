#!/usr/bin/env python3
"""Quick check of what the GUI shows."""

from playwright.sync_api import sync_playwright
import sys

APP_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    # Login
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    if page.locator('a:has-text("Sign in")').count() > 0:
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

    page.fill('input[type="email"]', "jane@test.com")
    page.fill('input[type="password"]', "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(3000)

    # Go to Admin
    admin_btn = page.locator('button[data-view="admin"]')
    if admin_btn.count() > 0:
        admin_btn.click()
        page.wait_for_timeout(3000)

    # Take screenshot
    page.screenshot(path="/tmp/current_gui_state.png")
    print("Screenshot saved to /tmp/current_gui_state.png")

    # Find Sunday Service event
    events = page.locator('.admin-item').all()
    print(f"\nFound {len(events)} events")

    for i, event in enumerate(events):
        text = event.inner_text()
        if "Sunday Service" in text:
            print(f"\n=== Event {i+1}: Sunday Service ===")
            print(text[:300])

            # Click "View Assignments" if available
            view_btn = event.locator('button:has-text("View Assignments"), button:has-text("Assign People")')
            if view_btn.count() > 0:
                print("\nClicking 'View Assignments'...")
                view_btn.first.click()
                page.wait_for_timeout(1500)

                # Check modal content
                modal = page.locator('#assignment-modal')
                if modal.is_visible():
                    modal_text = modal.inner_text()
                    print("\n=== ASSIGNMENT MODAL ===")
                    print(modal_text)

                    # Take screenshot of modal
                    page.screenshot(path="/tmp/assignment_modal.png")
                    print("\nModal screenshot saved to /tmp/assignment_modal.png")

                    # Check for BLOCKED text
                    if "BLOCKED" in modal_text:
                        print("\n✅ SUCCESS: Found 'BLOCKED' in modal!")
                    else:
                        print("\n❌ FAIL: No 'BLOCKED' found in modal")
                        print("\nSearching for Jane Smith...")
                        if "Jane Smith" in modal_text:
                            print("Jane Smith is in the list")
                            # Check HTML for is_blocked
                            modal_html = modal.inner_html()
                            if "is_blocked" in modal_html or "person-blocked" in modal_html or "schedule-badge-blocked" in modal_html:
                                print("Found blocked-related classes in HTML")
                            else:
                                print("No blocked-related classes in HTML")
                else:
                    print("Modal not visible")

                break

    browser.close()
