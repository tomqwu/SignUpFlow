#!/usr/bin/env python3
"""Take screenshots of all Rostio pages for README."""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os

APP_URL = "http://localhost:8000"
SCREENSHOTS_DIR = "docs/screenshots"

def take_screenshot_safe(page, path, description):
    """Take a screenshot with error handling."""
    try:
        print(f"Taking screenshot: {description}...")
        page.screenshot(path=path, full_page=True)
        print(f"  ✓ Saved to {path}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def click_safe(page, selector, timeout=5000):
    """Click an element safely with timeout."""
    try:
        page.click(selector, timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        print(f"  ⚠ Element not found: {selector}")
        return False
    except Exception as e:
        print(f"  ⚠ Click failed: {e}")
        return False

def take_screenshots():
    """Take screenshots of all pages."""
    screenshots_taken = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        # Login as admin first
        print("Logging in as admin...")
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Click sign in if needed
        if page.locator('a:has-text("Sign in")').count() > 0:
            page.click('a:has-text("Sign in")')
            page.wait_for_timeout(500)

        # Fill login form
        page.fill('input[type="email"]', "pastor@grace.church")
        page.fill('input[type="password"]', "password123")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(3000)

        # 1. Dashboard/Home Page after login
        path = f"{SCREENSHOTS_DIR}/01-dashboard-home.png"
        if take_screenshot_safe(page, path, "Dashboard/Home Page"):
            screenshots_taken.append(path)

        # 2. My Schedule Page
        if click_safe(page, 'button:has-text("My Schedule")'):
            page.wait_for_timeout(1500)
            path = f"{SCREENSHOTS_DIR}/02-my-schedule.png"
            if take_screenshot_safe(page, path, "My Schedule Page"):
                screenshots_taken.append(path)

        # 3. Admin Dashboard - Navigate to Admin view first
        if click_safe(page, 'button:has-text("Admin Dashboard")'):
            page.wait_for_timeout(1500)

            # Events Tab (default/active)
            if click_safe(page, 'button.tab-btn:has-text("Events")'):
                page.wait_for_timeout(1000)
                path = f"{SCREENSHOTS_DIR}/03-admin-events.png"
                if take_screenshot_safe(page, path, "Admin Dashboard - Events Tab"):
                    screenshots_taken.append(path)

            # 4. Admin Dashboard - Roles Tab
            if click_safe(page, 'button.tab-btn:has-text("Roles")'):
                page.wait_for_timeout(1000)
                path = f"{SCREENSHOTS_DIR}/04-admin-roles.png"
                if take_screenshot_safe(page, path, "Admin Dashboard - Roles Tab"):
                    screenshots_taken.append(path)

            # 5. Admin Dashboard - Schedule Tab
            if click_safe(page, 'button.tab-btn:has-text("Schedule")'):
                page.wait_for_timeout(1000)
                path = f"{SCREENSHOTS_DIR}/05-admin-schedule.png"
                if take_screenshot_safe(page, path, "Admin Dashboard - Schedule Tab"):
                    screenshots_taken.append(path)

            # 6. Admin Dashboard - People Tab
            if click_safe(page, 'button.tab-btn:has-text("People")'):
                page.wait_for_timeout(1500)
                path = f"{SCREENSHOTS_DIR}/06-admin-people.png"
                if take_screenshot_safe(page, path, "Admin Dashboard - People Tab"):
                    screenshots_taken.append(path)

                # 9. Edit Roles Modal (if visible)
                try:
                    if page.locator('button:has-text("Edit Roles")').count() > 0:
                        page.locator('button:has-text("Edit Roles")').first.click(timeout=2000)
                        page.wait_for_timeout(1000)
                        path = f"{SCREENSHOTS_DIR}/09-edit-roles-modal.png"
                        if take_screenshot_safe(page, path, "Edit Roles Modal"):
                            screenshots_taken.append(path)

                        # Close modal
                        page.locator('#edit-person-modal .btn-close').click()
                        page.wait_for_timeout(500)
                except Exception as e:
                    print(f"  ⚠ Edit Roles modal error: {e}")

                # 10. Invite User Modal (if visible)
                try:
                    if page.locator('button:has-text("Invite User")').count() > 0:
                        page.click('button:has-text("Invite User")', timeout=2000)
                        page.wait_for_timeout(500)
                        path = f"{SCREENSHOTS_DIR}/10-invite-user-modal.png"
                        if take_screenshot_safe(page, path, "Invite User Modal"):
                            screenshots_taken.append(path)

                        # Close modal
                        page.evaluate("closeInviteUserModal()")
                        page.wait_for_timeout(500)
                except Exception as e:
                    print(f"  ⚠ Invite User modal error: {e}")

            # 7. Admin Dashboard - Reports Tab
            if click_safe(page, 'button.tab-btn:has-text("Reports")'):
                page.wait_for_timeout(1000)
                path = f"{SCREENSHOTS_DIR}/07-admin-reports.png"
                if take_screenshot_safe(page, path, "Admin Dashboard - Reports Tab"):
                    screenshots_taken.append(path)

        # 8. Settings Modal
        # Navigate to calendar view first to access the settings button
        if click_safe(page, 'button[data-view="calendar"]'):
            page.wait_for_timeout(500)

            try:
                # Settings button uses onclick="showSettings()" with gear icon
                if page.locator('button.btn-icon:has-text("⚙️")').count() > 0:
                    page.click('button.btn-icon:has-text("⚙️")', timeout=5000)
                    page.wait_for_timeout(500)
                    path = f"{SCREENSHOTS_DIR}/08-settings-modal.png"
                    if take_screenshot_safe(page, path, "Settings Modal"):
                        screenshots_taken.append(path)
                    # Close modal
                    if page.locator('button.btn-close').count() > 0:
                        page.click('button.btn-close', timeout=1000)
                    else:
                        page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                else:
                    print("  ⚠ Settings button not found, skipping")
            except Exception as e:
                print(f"  ⚠ Could not capture Settings modal: {e}")

        browser.close()

    return screenshots_taken

if __name__ == "__main__":
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print("=" * 60)
    print("Taking screenshots of Rostio application")
    print("=" * 60)
    print()

    screenshots = take_screenshots()

    print()
    print("=" * 60)
    print(f"✅ Completed! {len(screenshots)} screenshots saved:")
    print("=" * 60)
    for screenshot in screenshots:
        print(f"  • {screenshot}")
    print()
