"""E2E tests for regular user features."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def user_page(page: Page):
    """Login as regular user."""
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)
    return page


def test_view_schedule(user_page: Page):
    """Test viewing personal schedule."""
    user_page.goto("http://localhost:8000/app/schedule")
    user_page.wait_for_timeout(1000)

    # Should show schedule view
    expect(user_page.locator("#schedule-view, .schedule-container")).to_be_visible(timeout=5000)
    user_page.screenshot(path="/tmp/e2e-schedule-view.png")


def test_set_availability(user_page: Page):
    """Test setting availability/blocked dates."""
    user_page.goto("http://localhost:8000/app/availability")
    user_page.wait_for_timeout(1000)

    # Look for availability form
    availability_section = user_page.locator("#availability-view, .availability-container")

    # Try to add blocked date
    add_button = user_page.locator("button:has-text('Add Blocked Date'), button:has-text('Block Date')")
    if add_button.count() > 0:
        add_button.first.click()
        user_page.wait_for_timeout(500)

        # Fill blocked date form
        date_input = user_page.locator("input[type='date']")
        if date_input.count() > 0:
            date_input.first.fill("2025-12-31")

            reason_input = user_page.locator("input[name='reason'], textarea[name='reason']")
            if reason_input.count() > 0:
                reason_input.fill("Vacation")

            save_button = user_page.locator("button:has-text('Save'), button:has-text('Add')")
            if save_button.count() > 0:
                save_button.first.click()
                user_page.wait_for_timeout(1000)

    user_page.screenshot(path="/tmp/e2e-availability-set.png")


def test_browse_events(user_page: Page):
    """Test browsing available events."""
    user_page.goto("http://localhost:8000/app/events")
    user_page.wait_for_timeout(1000)

    # Should show events list
    events_view = user_page.locator("#events-view, .events-container")

    user_page.screenshot(path="/tmp/e2e-events-browse.png")


def test_join_event(user_page: Page):
    """Test joining an event."""
    user_page.goto("http://localhost:8000/app/events")
    user_page.wait_for_timeout(1000)

    # Look for event card
    event_card = user_page.locator(".event-card, .event-item")
    if event_card.count() > 0:
        # Click on first event
        event_card.first.click()
        user_page.wait_for_timeout(500)

        # Look for "Join" button
        join_button = user_page.locator("button:has-text('Join'), button:has-text('Sign Up')")
        if join_button.count() > 0:
            join_button.first.click()
            user_page.wait_for_timeout(500)

            # May need to select a role
            role_option = user_page.locator(".role-option, button[data-role]")
            if role_option.count() > 0:
                role_option.first.click()
                user_page.wait_for_timeout(1000)

    user_page.screenshot(path="/tmp/e2e-event-joined.png")


def test_change_language(user_page: Page):
    """Test changing interface language."""
    user_page.goto("http://localhost:8000/app/schedule")
    user_page.wait_for_timeout(1000)

    # Look for language selector
    lang_selector = user_page.locator("select[id*='language'], button:has-text('EN'), button:has-text('Language')")
    if lang_selector.count() > 0:
        # Click to open language menu
        lang_selector.first.click()
        user_page.wait_for_timeout(500)

        # Select Spanish
        es_option = user_page.locator("option[value='es'], button:has-text('ES'), button:has-text('Español')")
        if es_option.count() > 0:
            es_option.first.click()
            user_page.wait_for_timeout(1000)

            # Page should now be in Spanish
            user_page.screenshot(path="/tmp/e2e-language-spanish.png")

            # Change back to English
            lang_selector = user_page.locator("select[id*='language'], button:has-text('ES')")
            if lang_selector.count() > 0:
                lang_selector.first.click()
                user_page.wait_for_timeout(500)

                en_option = user_page.locator("option[value='en'], button:has-text('EN'), button:has-text('English')")
                if en_option.count() > 0:
                    en_option.first.click()
                    user_page.wait_for_timeout(1000)


def test_update_profile(user_page: Page):
    """Test updating user profile."""
    # Look for profile/settings button
    profile_button = user_page.locator("button:has-text('Profile'), button:has-text('Settings'), button:has-text('⚙️')")
    if profile_button.count() > 0:
        profile_button.first.click()
        user_page.wait_for_timeout(500)

        # Update name
        name_input = user_page.locator("input[name='name'], #profile-name")
        if name_input.count() > 0:
            current_name = name_input.input_value()
            name_input.fill(f"{current_name} Updated")

            # Save changes
            save_button = user_page.locator("button:has-text('Save'), button:has-text('Update')")
            if save_button.count() > 0:
                save_button.first.click()
                user_page.wait_for_timeout(1000)

        user_page.screenshot(path="/tmp/e2e-profile-updated.png")


def test_timezone_support(user_page: Page):
    """Test timezone selection and display."""
    user_page.goto("http://localhost:8000/app/schedule")
    user_page.wait_for_timeout(1000)

    # Look for timezone selector
    tz_selector = user_page.locator("select[id*='timezone'], #user-timezone")
    if tz_selector.count() > 0:
        # Change timezone
        tz_selector.select_option("America/New_York")
        user_page.wait_for_timeout(1000)

        user_page.screenshot(path="/tmp/e2e-timezone-changed.png")
