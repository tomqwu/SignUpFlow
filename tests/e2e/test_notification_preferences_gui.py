"""
E2E tests for Notification Preferences GUI.

Tests:
- Change notification preferences in GUI
- Enable/disable email notifications
- Enable/disable SMS notifications
- Notification frequency settings
- Send test notification

Priority: MEDIUM - User preferences and notification management

STATUS: Tests implemented but SKIPPED - Notification Preferences GUI not yet implemented
Backend API partial (api/routers/notifications.py), SMS support and frontend pending

Backend API Endpoints:
- GET /api/notifications/preferences/me - Get current user's email notification preferences
- PUT /api/notifications/preferences/me - Update current user's email notification preferences
- POST /api/notifications/test/send - Send test notification (admin only, query params)

Email Preference Fields:
- frequency (str): immediate, daily, weekly, disabled
- enabled_types (list): List of notification types (assignment, reminder, update, cancellation)
- language (str): Email language preference (ISO 639-1 code, e.g., en, es, zh-CN)
- timezone (str): Timezone for digest scheduling (e.g., America/Toronto, UTC)
- digest_hour (int): Hour to send digests (0-23)

Default Preferences (if not set):
- frequency: immediate
- enabled_types: [assignment, reminder, update, cancellation]
- language: en
- timezone: UTC
- digest_hour: 8

UI Gaps Identified:
- No Notification Preferences section in Settings (#settings-notifications, .notification-preferences)
- No email notification toggle (#email-notifications-toggle)
- No SMS notification toggle (#sms-notifications-toggle) - BACKEND ALSO MISSING
- No frequency selector dropdown (#notification-frequency)
- No notification types checkboxes (#notification-types)
- No language preference selector (#notification-language)
- No timezone selector (#notification-timezone)
- No digest hour selector (#digest-hour)
- No "Send Test Notification" button (admin feature) (#send-test-notification)
- No test notification recipient email input
- No save preferences button (#save-notification-preferences)
- No success confirmation after saving
- Settings page doesn't have notification preferences tab/section
- SMS notifications backend support not implemented (EmailPreference table only)
- Backend has no SMS-related fields or endpoints

Once Notification Preferences GUI is implemented in Settings page (frontend/index.html, frontend/js/settings.js)
and SMS backend support added (api/models.py, api/schemas/notifications.py), unskip these tests.
"""

import pytest
from playwright.sync_api import Page, expect
import time

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


@pytest.fixture(scope="function")
def user_login(page: Page, app_config: AppConfig):
    """Login as regular user for notification preferences tests."""
    # Navigate directly to login page
    page.goto(f"{app_config.app_url}/login")
    page.wait_for_load_state("networkidle")

    # Verify login screen is visible
    expect(page.locator("#login-screen")).to_be_visible(timeout=5000)

    # Fill login form (regular volunteer user)
    page.fill("#login-email", "john@grace.church")
    page.fill("#login-password", "password")

    # Submit login
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Verify logged in
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    return page


@pytest.fixture(scope="function")
def admin_login(page: Page, app_config: AppConfig):
    """Login as admin for test notification feature."""
    # Navigate directly to login page
    page.goto(f"{app_config.app_url}/login")
    page.wait_for_load_state("networkidle")

    # Verify login screen is visible
    expect(page.locator("#login-screen")).to_be_visible(timeout=5000)

    # Fill login form (admin user)
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")

    # Submit login
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Verify logged in
    expect(page).to_have_url(f"{app_config.app_url}/app/schedule")
    expect(page.locator("#main-app")).to_be_visible()

    return page


@pytest.mark.skip(reason="Notification Preferences GUI not implemented - backend API exists but frontend pending")
def test_change_notification_preferences_in_gui(user_login: Page):
    """
    Test changing notification preferences in Settings GUI.

    User Journey:
    1. User clicks Settings/Profile
    2. User navigates to Notification Preferences section
    3. User sees current preferences loaded
    4. User changes frequency to "daily"
    5. User enables only "assignment" and "reminder" notification types
    6. User changes digest hour to 18:00
    7. User clicks Save
    8. User sees success confirmation
    9. User verifies preferences persisted (reload and check)
    """
    page = user_login

    # Step 1: Navigate to Settings
    settings_button = page.locator('button:has-text("Settings"), [data-i18n="settings.title"], #settings-button')

    # If no Settings button in main menu, try user menu dropdown
    if settings_button.count() == 0:
        user_menu = page.locator('#user-menu, .user-dropdown, button:has-text("John")')
        if user_menu.count() > 0:
            user_menu.first.click()
            page.wait_for_timeout(300)
            settings_button = page.locator('a:has-text("Settings"), [data-i18n="settings.title"]')

    expect(settings_button.first).to_be_visible(timeout=5000)
    settings_button.first.click()
    page.wait_for_timeout(1000)

    # Step 2: Navigate to Notification Preferences section
    # Look for Notifications tab or section
    notifications_tab = page.locator(
        'button:has-text("Notifications"), '
        '[data-i18n="settings.notifications"], '
        '#notifications-tab, '
        '.notifications-section'
    )

    if notifications_tab.count() > 0:
        notifications_tab.first.click()
        page.wait_for_timeout(500)

    # Verify notification preferences section is visible
    notification_prefs = page.locator('#settings-notifications, .notification-preferences, #notification-settings')
    expect(notification_prefs.first).to_be_visible(timeout=5000)

    # Step 3: Verify current preferences loaded
    # Check that frequency dropdown has a value
    frequency_selector = page.locator('#notification-frequency, select[name="frequency"]')
    expect(frequency_selector).to_be_visible()

    # Check that notification types checkboxes are present
    types_section = page.locator('#notification-types, .notification-types-section')
    expect(types_section).to_be_visible()

    # Step 4: Change frequency to "daily"
    frequency_selector.select_option(value="daily")
    page.wait_for_timeout(300)

    # Step 5: Enable only "assignment" and "reminder" notification types
    # Uncheck all first
    all_type_checkboxes = page.locator('input[type="checkbox"][name*="notification-type"]')
    for i in range(all_type_checkboxes.count()):
        checkbox = all_type_checkboxes.nth(i)
        if checkbox.is_checked():
            checkbox.uncheck()

    # Check only assignment and reminder
    assignment_checkbox = page.locator(
        'input[value="assignment"], '
        '#notification-type-assignment'
    )
    assignment_checkbox.check()

    reminder_checkbox = page.locator(
        'input[value="reminder"], '
        '#notification-type-reminder'
    )
    reminder_checkbox.check()

    # Step 6: Change digest hour to 18:00
    digest_hour_selector = page.locator('#digest-hour, select[name="digest-hour"], input[name="digest-hour"]')
    if digest_hour_selector.count() > 0:
        # Try as select first
        try:
            digest_hour_selector.select_option(value="18")
        except:
            # If not select, try as number input
            digest_hour_selector.fill("18")

    # Step 7: Click Save
    save_button = page.locator(
        'button:has-text("Save"), '
        'button:has-text("Save Preferences"), '
        '#save-notification-preferences, '
        'button[type="submit"]'
    )
    expect(save_button.first).to_be_visible()
    save_button.first.click()

    page.wait_for_timeout(2000)

    # Step 8: Verify success confirmation
    success_message = page.locator(
        'text="Preferences saved", '
        'text="Settings updated", '
        '.success-message, '
        '.toast-success'
    )
    expect(success_message.first).to_be_visible(timeout=5000)

    # Step 9: Verify preferences persisted
    # Reload page and check values
    page.reload()
    page.wait_for_timeout(2000)

    # Navigate back to notification settings
    notifications_tab = page.locator(
        'button:has-text("Notifications"), '
        '[data-i18n="settings.notifications"]'
    )
    if notifications_tab.count() > 0:
        notifications_tab.first.click()
        page.wait_for_timeout(500)

    # Verify frequency is "daily"
    frequency_value = page.locator('#notification-frequency, select[name="frequency"]').input_value()
    assert frequency_value == "daily", f"Expected frequency 'daily', got '{frequency_value}'"

    # Verify only assignment and reminder are checked
    assignment_checked = page.locator('#notification-type-assignment').is_checked()
    reminder_checked = page.locator('#notification-type-reminder').is_checked()
    assert assignment_checked, "Assignment checkbox should be checked"
    assert reminder_checked, "Reminder checkbox should be checked"


@pytest.mark.skip(reason="Notification Preferences GUI not implemented - backend API exists but frontend pending")
def test_enable_disable_email_notifications(user_login: Page):
    """
    Test enabling and disabling email notifications.

    User Journey:
    1. User navigates to Settings → Notifications
    2. User sees email notifications toggle (currently enabled)
    3. User clicks toggle to disable
    4. User saves preferences
    5. User verifies toggle state changed to disabled
    6. User re-enables email notifications
    7. User saves again
    8. User verifies toggle state is enabled
    """
    page = user_login

    # Navigate to Settings → Notifications
    settings_button = page.locator('button:has-text("Settings"), #settings-button')
    if settings_button.count() == 0:
        user_menu = page.locator('#user-menu, button:has-text("John")')
        user_menu.first.click()
        page.wait_for_timeout(300)
        settings_button = page.locator('a:has-text("Settings")')

    settings_button.first.click()
    page.wait_for_timeout(1000)

    notifications_tab = page.locator('button:has-text("Notifications"), #notifications-tab')
    if notifications_tab.count() > 0:
        notifications_tab.first.click()
        page.wait_for_timeout(500)

    # Step 2: Find email notifications toggle
    email_toggle = page.locator(
        '#email-notifications-toggle, '
        'input[type="checkbox"][name="email-enabled"], '
        '.email-notifications-toggle'
    )
    expect(email_toggle.first).to_be_visible(timeout=5000)

    # Verify currently enabled (default state)
    is_enabled = email_toggle.first.is_checked()
    if not is_enabled:
        # If disabled, enable it first to test disable flow
        email_toggle.first.check()
        page.locator('button:has-text("Save")').first.click()
        page.wait_for_timeout(2000)

    # Step 3: Disable email notifications
    email_toggle.first.uncheck()
    page.wait_for_timeout(300)

    # Step 4: Save preferences
    save_button = page.locator('button:has-text("Save"), #save-notification-preferences')
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 5: Verify success and toggle is unchecked
    success_message = page.locator('.success-message, .toast-success')
    expect(success_message.first).to_be_visible(timeout=5000)

    # Verify frequency changed to "disabled" (email notifications off)
    frequency_selector = page.locator('#notification-frequency, select[name="frequency"]')
    frequency_value = frequency_selector.input_value()
    assert frequency_value == "disabled", f"Expected frequency 'disabled', got '{frequency_value}'"

    # Step 6: Re-enable email notifications
    email_toggle.first.check()
    page.wait_for_timeout(300)

    # Optional: Change frequency back to immediate
    frequency_selector.select_option(value="immediate")

    # Step 7: Save again
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 8: Verify toggle is checked
    is_enabled_now = email_toggle.first.is_checked()
    assert is_enabled_now, "Email notifications should be enabled"

    frequency_value = frequency_selector.input_value()
    assert frequency_value == "immediate", f"Expected frequency 'immediate', got '{frequency_value}'"


@pytest.mark.skip(reason="SMS Notifications not implemented - backend has no SMS support, only email preferences")
def test_enable_disable_sms_notifications(user_login: Page):
    """
    Test enabling and disabling SMS notifications.

    **NOTE**: Backend currently only supports email preferences (EmailPreference table).
    SMS notifications require:
    - New SmsPreference model in api/models.py
    - SMS preference endpoints in api/routers/notifications.py
    - SMS provider integration (Twilio, etc.)
    - Phone number field in Person model

    User Journey (when implemented):
    1. User navigates to Settings → Notifications
    2. User sees SMS notifications toggle (currently disabled)
    3. User enters phone number
    4. User clicks SMS toggle to enable
    5. User saves preferences
    6. User verifies SMS toggle is enabled
    7. User disables SMS notifications
    8. User saves again
    9. User verifies toggle is disabled
    """
    page = user_login

    # Navigate to Settings → Notifications
    settings_button = page.locator('button:has-text("Settings"), #settings-button')
    if settings_button.count() == 0:
        user_menu = page.locator('#user-menu')
        user_menu.first.click()
        page.wait_for_timeout(300)
        settings_button = page.locator('a:has-text("Settings")')

    settings_button.first.click()
    page.wait_for_timeout(1000)

    notifications_tab = page.locator('button:has-text("Notifications"), #notifications-tab')
    if notifications_tab.count() > 0:
        notifications_tab.first.click()
        page.wait_for_timeout(500)

    # Look for SMS section
    sms_section = page.locator('#sms-notifications, .sms-preferences-section')
    expect(sms_section.first).to_be_visible(timeout=5000)

    # Step 3: Enter phone number
    phone_input = page.locator('#phone-number, input[name="phone"]')
    expect(phone_input).to_be_visible()
    phone_input.fill("+1 416-555-0123")

    # Step 4: Enable SMS notifications
    sms_toggle = page.locator(
        '#sms-notifications-toggle, '
        'input[type="checkbox"][name="sms-enabled"]'
    )
    expect(sms_toggle.first).to_be_visible()
    sms_toggle.first.check()
    page.wait_for_timeout(300)

    # Step 5: Save preferences
    save_button = page.locator('button:has-text("Save")')
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 6: Verify success and SMS is enabled
    success_message = page.locator('.success-message, .toast-success')
    expect(success_message.first).to_be_visible(timeout=5000)

    is_enabled = sms_toggle.first.is_checked()
    assert is_enabled, "SMS notifications should be enabled"

    # Step 7: Disable SMS notifications
    sms_toggle.first.uncheck()
    page.wait_for_timeout(300)

    # Step 8: Save again
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 9: Verify toggle is unchecked
    is_disabled = not sms_toggle.first.is_checked()
    assert is_disabled, "SMS notifications should be disabled"


@pytest.mark.skip(reason="Notification Preferences GUI not implemented - backend API exists but frontend pending")
def test_notification_frequency_settings(user_login: Page):
    """
    Test changing notification frequency settings.

    User Journey:
    1. User navigates to Settings → Notifications
    2. User sees frequency dropdown (current: immediate)
    3. User changes frequency to "daily"
    4. User sets digest hour to 9:00 AM
    5. User saves preferences
    6. User verifies frequency changed successfully
    7. User changes frequency to "weekly"
    8. User saves again
    9. User verifies frequency is weekly
    10. User changes back to "immediate"
    11. User verifies digest hour is hidden (only for daily/weekly)
    """
    page = user_login

    # Navigate to Settings → Notifications
    settings_button = page.locator('button:has-text("Settings"), #settings-button')
    if settings_button.count() == 0:
        user_menu = page.locator('#user-menu')
        user_menu.first.click()
        page.wait_for_timeout(300)
        settings_button = page.locator('a:has-text("Settings")')

    settings_button.first.click()
    page.wait_for_timeout(1000)

    notifications_tab = page.locator('button:has-text("Notifications")')
    if notifications_tab.count() > 0:
        notifications_tab.first.click()
        page.wait_for_timeout(500)

    # Step 2: Find frequency dropdown
    frequency_selector = page.locator('#notification-frequency, select[name="frequency"]')
    expect(frequency_selector).to_be_visible(timeout=5000)

    # Verify current value is "immediate" (default)
    current_frequency = frequency_selector.input_value()
    # Note: might be immediate or other value from previous tests

    # Step 3: Change to "daily"
    frequency_selector.select_option(value="daily")
    page.wait_for_timeout(500)

    # Step 4: Digest hour selector should now be visible
    digest_hour_selector = page.locator('#digest-hour, select[name="digest-hour"]')
    expect(digest_hour_selector).to_be_visible(timeout=3000)

    # Set digest hour to 9 AM
    digest_hour_selector.select_option(value="9")

    # Step 5: Save preferences
    save_button = page.locator('button:has-text("Save")')
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 6: Verify success
    success_message = page.locator('.success-message, .toast-success')
    expect(success_message.first).to_be_visible(timeout=5000)

    # Verify frequency is "daily"
    frequency_value = frequency_selector.input_value()
    assert frequency_value == "daily", f"Expected frequency 'daily', got '{frequency_value}'"

    # Verify digest hour is 9
    digest_hour_value = digest_hour_selector.input_value()
    assert digest_hour_value == "9", f"Expected digest hour '9', got '{digest_hour_value}'"

    # Step 7: Change to "weekly"
    frequency_selector.select_option(value="weekly")
    page.wait_for_timeout(500)

    # Digest hour should still be visible for weekly
    expect(digest_hour_selector).to_be_visible()

    # Step 8: Save again
    save_button.first.click()
    page.wait_for_timeout(2000)

    # Step 9: Verify frequency is weekly
    frequency_value = frequency_selector.input_value()
    assert frequency_value == "weekly", f"Expected frequency 'weekly', got '{frequency_value}'"

    # Step 10: Change back to "immediate"
    frequency_selector.select_option(value="immediate")
    page.wait_for_timeout(500)

    # Step 11: Digest hour should be hidden for immediate
    # Check if digest hour field is hidden or disabled
    digest_hour_visible = digest_hour_selector.is_visible()
    # For immediate notifications, digest hour is not relevant
    # UI may hide it or disable it

    save_button.first.click()
    page.wait_for_timeout(2000)

    # Verify frequency is immediate
    frequency_value = frequency_selector.input_value()
    assert frequency_value == "immediate", f"Expected frequency 'immediate', got '{frequency_value}'"


@pytest.mark.skip(reason="Notification Preferences GUI not implemented - backend API exists but frontend pending")
def test_send_test_notification(admin_login: Page):
    """
    Test sending a test notification (admin feature).

    User Journey:
    1. Admin navigates to Settings → Notifications (or Admin Console)
    2. Admin sees "Send Test Notification" button
    3. Admin enters recipient email address
    4. Admin clicks "Send Test Notification"
    5. Admin sees confirmation that test email was sent
    6. Admin verifies notification ID returned
    7. Admin checks notification appears in recipient's notifications list
    """
    page = admin_login

    # Navigate to Settings or Admin Console
    # Admins may have this feature in Admin Console or Settings
    admin_console_button = page.locator('button:has-text("Admin"), #admin-console-button')
    if admin_console_button.count() > 0:
        # Admin Console route
        admin_console_button.first.click()
        page.wait_for_timeout(1000)

        # Look for Notifications tab in admin console
        notifications_tab = page.locator('button:has-text("Notifications"), #notifications-admin-tab')
        if notifications_tab.count() > 0:
            notifications_tab.first.click()
            page.wait_for_timeout(500)
    else:
        # Settings route
        settings_button = page.locator('button:has-text("Settings")')
        if settings_button.count() == 0:
            user_menu = page.locator('#user-menu')
            user_menu.first.click()
            page.wait_for_timeout(300)
            settings_button = page.locator('a:has-text("Settings")')

        settings_button.first.click()
        page.wait_for_timeout(1000)

        notifications_tab = page.locator('button:has-text("Notifications")')
        if notifications_tab.count() > 0:
            notifications_tab.first.click()
            page.wait_for_timeout(500)

    # Step 2: Find "Send Test Notification" section
    test_notification_section = page.locator(
        '#send-test-notification, '
        '.test-notification-section, '
        '#test-notification-form'
    )
    expect(test_notification_section.first).to_be_visible(timeout=5000)

    # Step 3: Enter recipient email
    recipient_email_input = page.locator(
        '#test-notification-email, '
        'input[name="test-email"], '
        'input[placeholder*="email"]'
    )
    expect(recipient_email_input.first).to_be_visible()
    recipient_email_input.first.fill("john@grace.church")

    # Step 4: Click "Send Test Notification"
    send_test_button = page.locator(
        'button:has-text("Send Test"), '
        'button:has-text("Send Test Notification"), '
        '#send-test-notification-button'
    )
    expect(send_test_button.first).to_be_visible()
    send_test_button.first.click()

    page.wait_for_timeout(3000)  # Email sending may take time

    # Step 5: Verify success confirmation
    success_message = page.locator(
        'text="Test notification sent", '
        'text="Email sent successfully", '
        '.success-message, '
        '.toast-success'
    )
    expect(success_message.first).to_be_visible(timeout=5000)

    # Step 6: Verify notification ID or details shown
    notification_details = page.locator(
        '.notification-id, '
        '#test-notification-result, '
        'text=/Notification ID: \\d+/'
    )
    # Notification ID may be displayed in success message or separate field

    # Step 7: Verify notification in recipient's list (optional check)
    # This would require switching to recipient's account or checking database
    # For E2E test, we verify the UI confirms successful send
