"""
E2E tests for language switching functionality.

Tests the complete workflow:
1. User logs in (default English)
2. User switches to different language in settings
3. UI updates to show translations
4. Language preference persists on page reload
"""

import requests
import time
from playwright.sync_api import Page, expect


def test_language_switching_to_chinese(page: Page):
    """
    Test complete language switching workflow from English to Chinese.

    User Journey:
    1. Create test organization and user
    2. User logs in (default English)
    3. User opens settings
    4. User switches language to Chinese (Simplified)
    5. UI updates to show Chinese translations
    6. Verify specific translated elements
    """

    print("\n" + "="*80)
    print("TESTING LANGUAGE SWITCHING TO CHINESE")
    print("="*80)

    # Setup: Create test organization and user
    print("\nSetup: Creating test organization and user...")
    timestamp = int(time.time())
    test_org_id = f"org_lang_test_{timestamp}"
    user_email = f"user{timestamp}@test.com"
    test_password = "Password123"

    # Create organization
    org_response = requests.post(
        "http://localhost:8000/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Language Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201], f"Failed to create org: {org_response.text}"

    # Create user
    signup_response = requests.post(
        "http://localhost:8000/api/auth/signup",
        json={
            "email": user_email,
            "password": test_password,
            "name": f"Test User {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201
    print(f"✓ User created: {user_email}")

    # Step 1: User logs in (should be in English by default)
    print("\nStep 1: User logs in (default English)...")

    page.goto("http://localhost:8000/login")

    page.locator('#login-email').fill(user_email)
    page.locator('#login-password').fill(test_password)
    page.locator('#login-screen button[type="submit"]').click()

    # Verify logged in
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ User logged in successfully")

    # Verify English UI
    my_schedule_heading = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_heading).to_be_visible(timeout=3000)
    # In English, it should say "My Schedule"
    expect(my_schedule_heading).to_have_text("My Schedule")
    print("  ✓ UI is in English (verified 'My Schedule' heading)")

    # Step 2: Open settings
    print("\nStep 2: Opening settings...")

    # Click settings button (gear icon ⚙️)
    settings_btn = page.locator('button.btn-icon:has-text("⚙️")')
    expect(settings_btn).to_be_visible(timeout=3000)
    settings_btn.click()

    # Verify settings modal is visible
    settings_modal = page.locator('#settings-modal')
    expect(settings_modal).to_be_visible(timeout=3000)
    print("  ✓ Settings modal opened")

    # Step 3: Switch to Chinese (Simplified)
    print("\nStep 3: Switching language to Chinese (Simplified)...")

    # Find the language selector
    language_select = page.locator('#settings-language')
    expect(language_select).to_be_visible(timeout=3000)

    # Select Chinese (Simplified)
    language_select.select_option('zh-CN')
    print("  ✓ Selected Chinese (Simplified) from dropdown")

    # Wait for language to change
    page.wait_for_timeout(1000)

    # Close settings modal
    close_btn = page.locator('#settings-modal button.btn-close')
    close_btn.click()

    page.wait_for_timeout(1000)

    # Step 4: Verify UI updated to Chinese
    print("\nStep 4: Verifying UI is now in Chinese...")

    # Check that "My Schedule" is now in Chinese: "我的排班"
    my_schedule_heading_chinese = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_heading_chinese).to_be_visible(timeout=3000)
    expect(my_schedule_heading_chinese).to_have_text("我的排班")
    print("  ✓ 'My Schedule' heading is now '我的排班' (Chinese)")

    # Check another element - the "Upcoming" label should be "即将到来"
    upcoming_label = page.locator('.stat-label[data-i18n="schedule.upcoming"]')
    if upcoming_label.count() > 0:
        expect(upcoming_label.first).to_have_text("即将到来")
        print("  ✓ 'Upcoming' label is now '即将到来' (Chinese)")

    # Step 5: Verify language persists after page reload
    print("\nStep 5: Verifying language persists after reload...")

    page.reload()

    # Wait for page to reload
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)

    # Check that language is still Chinese
    my_schedule_heading_after_reload = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_heading_after_reload).to_be_visible(timeout=3000)
    expect(my_schedule_heading_after_reload).to_have_text("我的排班")
    print("  ✓ Language persisted after reload (still Chinese)")

    # Step 6: Verify via API that language preference is saved
    print("\nStep 6: Verifying language preference saved to user profile...")

    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"email": user_email, "password": test_password}
    )
    user_token = login_response.json()["token"]

    me_response = requests.get(
        "http://localhost:8000/api/people/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    user_data = me_response.json()

    assert user_data.get("language") == "zh-CN", f"Expected language 'zh-CN', got {user_data.get('language')}"
    print("  ✓ Language preference 'zh-CN' saved to user profile")

    print("\n" + "="*80)
    print("✅ LANGUAGE SWITCHING TEST PASSED")
    print("="*80)


def test_language_switching_to_spanish(page: Page):
    """
    Test language switching to Spanish.

    User Journey:
    1. Create user and log in
    2. Switch to Spanish
    3. Verify Spanish translations
    """

    print("\n" + "="*80)
    print("TESTING LANGUAGE SWITCHING TO SPANISH")
    print("="*80)

    # Setup
    print("\nSetup: Creating test organization and user...")
    timestamp = int(time.time())
    test_org_id = f"org_spanish_{timestamp}"
    user_email = f"user{timestamp}@test.com"
    test_password = "Password123"

    # Create organization
    org_response = requests.post(
        "http://localhost:8000/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"Spanish Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201]

    # Create user
    signup_response = requests.post(
        "http://localhost:8000/api/auth/signup",
        json={
            "email": user_email,
            "password": test_password,
            "name": f"Spanish User {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201
    print(f"✓ User created: {user_email}")

    # Login
    print("\nStep 1: User logs in...")
    page.goto("http://localhost:8000/login")

    page.locator('#login-email').fill(user_email)
    page.locator('#login-password').fill(test_password)
    page.locator('#login-screen button[type="submit"]').click()

    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ User logged in")

    # Open settings
    print("\nStep 2: Opening settings and switching to Spanish...")
    settings_btn = page.locator('button.btn-icon:has-text("⚙️")')
    expect(settings_btn).to_be_visible(timeout=3000)
    settings_btn.click()

    expect(page.locator('#settings-modal')).to_be_visible(timeout=3000)

    # Switch to Spanish
    language_select = page.locator('#settings-language')
    language_select.select_option('es')
    print("  ✓ Selected Spanish")

    page.wait_for_timeout(1000)

    # Close settings modal
    close_btn = page.locator('#settings-modal button.btn-close')
    close_btn.click()

    page.wait_for_timeout(1000)

    # Navigate to schedule
    print("\nStep 3: Verifying Spanish translations...")

    # Check Spanish translation - "My Schedule" should be "Mi horario"
    my_schedule_heading = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_heading).to_be_visible(timeout=3000)
    expect(my_schedule_heading).to_have_text("Mi horario")
    print("  ✓ 'My Schedule' is now 'Mi horario' (Spanish)")

    # Verify persistence
    print("\nStep 4: Verifying language persists...")
    page.reload()
    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)

    my_schedule_after_reload = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_after_reload).to_have_text("Mi horario")
    print("  ✓ Language persisted (still Spanish)")

    print("\n" + "="*80)
    print("✅ SPANISH LANGUAGE SWITCHING TEST PASSED")
    print("="*80)


def test_language_switching_back_to_english(page: Page):
    """
    Test switching language back to English after changing it.

    User Journey:
    1. Create user and log in
    2. Switch to Chinese
    3. Switch back to English
    4. Verify English translations restored
    """

    print("\n" + "="*80)
    print("TESTING LANGUAGE SWITCHING BACK TO ENGLISH")
    print("="*80)

    # Setup
    print("\nSetup: Creating test organization and user...")
    timestamp = int(time.time())
    test_org_id = f"org_eng_test_{timestamp}"
    user_email = f"user{timestamp}@test.com"
    test_password = "Password123"

    # Create organization
    org_response = requests.post(
        "http://localhost:8000/api/organizations/",
        json={
            "id": test_org_id,
            "name": f"English Test Org {timestamp}",
            "location": "Test City"
        }
    )
    assert org_response.status_code in [200, 201]

    # Create user
    signup_response = requests.post(
        "http://localhost:8000/api/auth/signup",
        json={
            "email": user_email,
            "password": test_password,
            "name": f"Test User {timestamp}",
            "org_id": test_org_id,
            "timezone": "America/Toronto"
        }
    )
    assert signup_response.status_code == 201
    print(f"✓ User created: {user_email}")

    # Login
    print("\nStep 1: User logs in...")
    page.goto("http://localhost:8000/login")
    page.locator('#login-email').fill(user_email)
    page.locator('#login-password').fill(test_password)
    page.locator('#login-screen button[type="submit"]').click()

    expect(page.locator('#main-app')).to_be_visible(timeout=5000)
    print("  ✓ User logged in")

    # Switch to Chinese first
    print("\nStep 2: Switching to Chinese...")
    settings_btn = page.locator('button.btn-icon:has-text("⚙️")')
    expect(settings_btn).to_be_visible(timeout=3000)
    settings_btn.click()
    expect(page.locator('#settings-modal')).to_be_visible(timeout=3000)

    language_select = page.locator('#settings-language')
    language_select.select_option('zh-CN')
    page.wait_for_timeout(1000)

    # Close settings modal
    close_btn = page.locator('#settings-modal button.btn-close')
    close_btn.click()
    page.wait_for_timeout(1000)
    print("  ✓ Switched to Chinese")

    my_schedule_chinese = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_chinese).to_have_text("我的排班")
    print("  ✓ Verified UI is in Chinese")

    # Switch back to English
    print("\nStep 3: Switching back to English...")
    settings_btn.click()
    expect(page.locator('#settings-modal')).to_be_visible(timeout=3000)

    language_select.select_option('en')
    page.wait_for_timeout(1000)

    # Close modal
    close_btn.click()
    page.wait_for_timeout(1000)
    print("  ✓ Switched back to English")

    # Verify English
    print("\nStep 4: Verifying English translations restored...")

    my_schedule_english = page.locator('h2[data-i18n="schedule.my_schedule"]')
    expect(my_schedule_english).to_have_text("My Schedule")
    print("  ✓ 'My Schedule' is back to English")

    print("\n" + "="*80)
    print("✅ ENGLISH RESTORATION TEST PASSED")
    print("="*80)
