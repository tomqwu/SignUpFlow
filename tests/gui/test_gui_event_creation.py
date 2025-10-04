"""
Test GUI event creation flow end-to-end.
This test verifies that:
1. Events display correctly in the admin dashboard
2. Users can create new events via the GUI
3. Created events immediately appear in the event list
"""
import asyncio
import pytest
from playwright.async_api import async_playwright
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_event_display_and_creation():
    """Test that events display and can be created via GUI."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            bypass_csp=True,
            ignore_https_errors=True
        )
        page = await context.new_page()

        # Disable cache
        await context.route("**/*", lambda route: route.continue_(headers={**route.request.headers, "Cache-Control": "no-cache"}))

        # Enable console logging
        page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))

        # Enable page error logging
        page.on("pageerror", lambda exc: print(f"[BROWSER ERROR] {exc}"))

        try:
            # Navigate to app
            print("Navigating to http://localhost:8000")
            await page.goto('http://localhost:8000', wait_until='networkidle')

            # Click "Sign in" link
            print("Clicking Sign in")
            await page.click('a:has-text("Sign in")')

            # Login as admin
            print("Filling login form")
            await page.wait_for_selector('#login-email', state='visible', timeout=10000)
            await page.fill('#login-email', 'jane@test.com')
            await page.fill('#login-password', 'password')
            await page.click('button[type="submit"]:has-text("Sign In")')

            # Wait for main app to appear
            print("Waiting for main app")
            await page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

            # Switch to Admin Dashboard
            print("Switching to admin dashboard")
            await page.click('button:has-text("Admin Dashboard")')
            await page.wait_for_selector('#admin-view.active', timeout=5000)

            # Wait for events to load
            print("Waiting for events to load")
            await page.wait_for_timeout(2000)

            # Count initial events
            initial_events = await page.locator('#admin-events-list .admin-item').all()
            initial_count = len(initial_events)
            print(f"✅ Initial event count: {initial_count}")

            # Click Create Event button
            print("Clicking Create Event button")
            await page.click('button:has-text("Create Event")')

            # Wait for modal
            print("Waiting for create event modal")
            await page.wait_for_selector('#create-event-modal:not(.hidden)', timeout=5000)

            # Fill event form
            print("Filling event form")
            await page.select_option('#event-type', 'Sunday Service')

            # Set datetime to next Sunday at 10 AM
            next_sunday = datetime.now() + timedelta(days=((6 - datetime.now().weekday()) % 7) + 1)
            datetime_str = next_sunday.strftime("%Y-%m-%dT10:00")
            await page.fill('#event-start', datetime_str)

            await page.fill('#event-duration', '2')
            await page.fill('#event-location', 'Main Sanctuary')

            # Submit form
            print("Submitting event form")
            await page.click('button[type="submit"]:has-text("Create Event")')

            # Wait for modal to close or alert
            print("Waiting for response")
            await page.wait_for_timeout(3000)

            # Take screenshot
            await page.screenshot(path='/tmp/after_submit.png')
            print("Screenshot saved to /tmp/after_submit.png")

            # Check if modal closed (success) or is still open (error)
            modal_hidden = await page.is_hidden('#create-event-modal')
            if modal_hidden:
                print("✅ Modal closed successfully")
            else:
                print("❌ Modal still open - form submission may have failed")
                # Take another screenshot
                await page.screenshot(path='/tmp/modal_still_open.png')

            # Refresh events list
            print("Refreshing events list")
            await page.click('button:has-text("Refresh")')
            await page.wait_for_timeout(2000)

            # Count final events
            final_events = await page.locator('#admin-events-list .admin-item').all()
            final_count = len(final_events)
            print(f"✅ Final event count: {final_count}")

            # Verify event was created
            assert final_count > initial_count, f"Event count should increase from {initial_count}, got {final_count}"

            print(f"\n✅✅✅ TEST PASSED: Event created successfully! Count went from {initial_count} to {final_count}")

        except Exception as e:
            # Take screenshot on failure
            await page.screenshot(path='/tmp/test_failure.png')
            print(f"\n❌ Test failed: {e}")
            print("Screenshot saved to /tmp/test_failure.png")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_event_display_and_creation())
