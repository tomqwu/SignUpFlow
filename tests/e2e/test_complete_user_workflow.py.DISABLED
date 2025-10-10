"""
End-to-End tests for complete user workflows.

Tests the full user journey from signup to viewing schedule.
Uses data-i18n selectors to be language-independent.
"""

import pytest
from playwright.sync_api import Page, expect


def test_complete_signup_and_login_workflow(page: Page):
    """Test complete user signup, login, and basic navigation."""
    page.goto("http://localhost:8000/")

    # Should see onboarding screen with i18n selector
    get_started = page.locator('[data-i18n="auth.get_started"]')
    expect(get_started).to_be_visible(timeout=5000)
    get_started.click()

    # Should see organization list
    expect(page.locator('[data-i18n="auth.join_org"]')).to_be_visible()

    # Create new organization
    create_org_btn = page.locator('[data-i18n="auth.create_new_organization"]')
    create_org_btn.click()

    # Fill organization form with unique timestamp
    timestamp = page.evaluate('Date.now()')
    page.fill('[data-i18n-placeholder="auth.placeholder_org_name"]', f"E2E Test Church {timestamp}")
    page.fill('[data-i18n-placeholder="auth.placeholder_location"]', "Test City")

    # Submit organization creation
    page.locator('[data-i18n="common.buttons.create"]').click()

    # Should navigate to profile screen
    expect(page.locator('[data-i18n="auth.about_you"]')).to_be_visible()

    # Fill user profile
    page.fill('[data-i18n-placeholder="common.placeholder_full_name"]', "E2E Test User")
    page.fill('[data-i18n-placeholder="common.placeholder_email"]', f"e2e-{page.evaluate('Date.now()')}@test.com")
    page.fill('[data-i18n-placeholder="auth.placeholder_create_password"]', "testpass123")

    # Select volunteer role (scope to profile screen role selector)
    page.locator('#role-selector input[value="volunteer"]').check()

    # Submit profile
    page.locator('[data-i18n="common.buttons.next"]').click()

    # Should navigate to main app
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Verify we can navigate between views
    page.locator('[data-i18n="schedule.availability"]').first.click()
    expect(page.locator('[data-i18n="schedule.add_time_off"]')).to_be_visible()

    # Navigate to events
    page.locator('[data-i18n="events.events"]').click()
    expect(page.locator('[data-i18n="events.title"]')).to_be_visible()


def test_page_reload_preserves_state(page: Page):
    """Test that reloading on different routes works correctly."""
    # First login
    page.goto("http://localhost:8000/")

    # Quick login (assuming we have test data)
    page.locator('[data-i18n="auth.sign_in_link"]').click()
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "admin@rostio.com")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "admin123")
    page.locator('[data-i18n="auth.sign_in"]').click()

    # Wait for main app
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Navigate to availability
    page.locator('[data-i18n="schedule.availability"]').first.click()
    expect(page.locator('[data-i18n="schedule.add_time_off"]')).to_be_visible()

    # Reload page
    page.reload()

    # Should still be on availability page and scripts should load
    expect(page.locator('[data-i18n="schedule.add_time_off"]')).to_be_visible(timeout=5000)

    # Check that JavaScript loaded (no console errors about '<')
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.reload()
    page.wait_for_timeout(2000)

    # Should not have "Unexpected token '<'" errors
    syntax_errors = [e for e in console_errors if "Unexpected token '<'" in e]
    assert len(syntax_errors) == 0, f"Found JavaScript syntax errors: {syntax_errors}"


def test_role_display_no_object_object(page: Page):
    """Test that roles are displayed correctly, not as [object Object]."""
    page.goto("http://localhost:8000/")

    # Login as admin
    page.locator('[data-i18n="auth.sign_in_link"]').click()
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "admin@rostio.com")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "admin123")
    page.locator('[data-i18n="auth.sign_in"]').click()

    # Wait for main app
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Open settings to check role display
    page.locator('button:has-text("⚙️")').click()
    expect(page.locator('[data-i18n="settings.title"]')).to_be_visible()

    # Check that permissions display doesn't contain [object Object]
    permissions_display = page.locator('#settings-permission-display').inner_text()
    assert "[object Object]" not in permissions_display, f"Found [object Object] in permissions: {permissions_display}"

    # Close settings
    page.locator('[data-i18n="common.buttons.cancel"]').last.click()

    # Check role badges in context panel
    role_badges = page.locator('.role-badge').all_inner_texts()
    for badge in role_badges:
        assert "[object Object]" not in badge, f"Found [object Object] in role badge: {badge}"


def test_admin_workflow_complete(page: Page):
    """Test complete admin workflow: create event, assign roles, generate schedule."""
    page.goto("http://localhost:8000/")

    # Login as admin
    page.locator('[data-i18n="auth.sign_in_link"]').click()
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "admin@rostio.com")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "admin123")
    page.locator('[data-i18n="auth.sign_in"]').click()

    # Wait for main app
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Navigate to admin dashboard
    page.locator('[data-i18n="admin.dashboard"]').click()
    expect(page.locator('[data-i18n="admin.admin_console"]')).to_be_visible()

    # Create new event
    page.locator('[data-i18n="admin.create_event_button"]').click()
    expect(page.locator('[data-i18n="events.create_event"]').first).to_be_visible()

    # Fill event form
    page.select_option('#event-type', 'Sunday Service')

    # Set date to tomorrow
    tomorrow = page.evaluate("""
        const d = new Date();
        d.setDate(d.getDate() + 1);
        return d.toISOString().slice(0, 16);
    """)
    page.fill('#event-start', tomorrow)

    # Submit event creation
    page.locator('[data-i18n="events.create_event"]').last.click()

    # Should see event in list
    expect(page.locator('text="Sunday Service"')).to_be_visible(timeout=5000)

    # Go to schedule tab
    page.locator('button[data-tab="schedule"]').click()

    # Generate schedule
    page.locator('text="Generate Schedule"').click()

    # Should see success message or schedule generated
    page.wait_for_timeout(2000)  # Wait for solver


def test_language_switching_works(page: Page):
    """Test that language switching works correctly."""
    page.goto("http://localhost:8000/")

    # Should see onboarding in English
    expect(page.locator('[data-i18n="auth.welcome_to_rostio"]')).to_be_visible()

    # Login
    page.get_by_role("link", name="Sign in").click()
    page.fill('#login-email', "admin@rostio.com")
    page.fill('#login-password', "admin123")
    page.get_by_role("button", name="Sign In").click()

    # Wait for main app
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)

    # Open settings
    page.locator('button:has-text("⚙️")').click()

    # Switch to Chinese (Simplified)
    page.select_option('#settings-language', 'zh-CN')

    # Wait for translation
    page.wait_for_timeout(1000)

    # Should see Chinese text
    expect(page.locator('text="我的日程"')).to_be_visible()

    # Switch back to English
    page.select_option('#settings-language', 'en')
    page.wait_for_timeout(1000)

    # Should see English again
    expect(page.locator('text="My Schedule"')).to_be_visible()


def test_availability_crud_complete(page: Page):
    """Test complete CRUD workflow for availability."""
    page.goto("http://localhost:8000/")

    # Login
    page.locator('[data-i18n="auth.sign_in_link"]').click()
    page.fill('[data-i18n-placeholder="auth.placeholder_email"]', "admin@rostio.com")
    page.fill('[data-i18n-placeholder="auth.placeholder_password"]', "admin123")
    page.locator('[data-i18n="auth.sign_in"]').click()

    # Navigate to availability
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(timeout=10000)
    page.locator('[data-i18n="schedule.availability"]').first.click()

    # Add time off
    start_date = page.evaluate("new Date(Date.now() + 86400000).toISOString().slice(0, 10)")
    end_date = page.evaluate("new Date(Date.now() + 172800000).toISOString().slice(0, 10)")

    page.fill('#timeoff-start', start_date)
    page.fill('#timeoff-end', end_date)
    page.fill('#timeoff-reason', 'E2E Test Vacation')

    page.locator('[data-i18n="schedule.add_time_off"]').click()

    # Should see time off in list
    expect(page.locator('text="E2E Test Vacation"')).to_be_visible(timeout=5000)

    # Edit time off
    page.locator('button:has-text("✏️")').first.click()
    expect(page.locator('[data-i18n="schedule.edit_timeoff"]')).to_be_visible()

    page.fill('#edit-timeoff-reason', 'Updated Vacation')
    page.locator('[data-i18n="common.buttons.save"]').click()

    # Should see updated reason
    expect(page.locator('text="Updated Vacation"')).to_be_visible(timeout=5000)

    # Delete time off
    page.locator('button:has-text("🗑️")').first.click()

    # Should be removed from list (or reduced count)
    page.wait_for_timeout(1000)


@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Setup test data before running E2E tests."""
    from api.database import get_db
    from api.models import Person, Organization
    from api.security import get_password_hash

    db = next(get_db())

    # Check if test org exists
    test_org = db.query(Organization).filter_by(name="Test Org").first()
    if not test_org:
        test_org = Organization(
            id="test_org",
            name="Test Org",
            config={"region": "Test Region", "roles": ["admin", "volunteer"]}
        )
        db.add(test_org)
        db.commit()

    # Check if admin exists
    admin = db.query(Person).filter_by(email="admin@rostio.com").first()
    if not admin:
        admin = Person(
            id="admin_user",
            name="Admin User",
            email="admin@rostio.com",
            password_hash=get_password_hash("admin123"),
            org_id=test_org.id,
            roles=["admin", "volunteer"]
        )
        db.add(admin)
        db.commit()

    db.commit()

    yield

    # Cleanup after tests
    # (Optional - keep test data for debugging)
