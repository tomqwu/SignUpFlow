"""
Integration tests for i18n (internationalization) functionality.

These tests verify the complete i18n workflow including:
- Language persistence across sessions
- Translation coverage
- URL routing with i18n
- Language switching workflow
"""

import pytest
import os
import requests
from playwright.sync_api import sync_playwright, expect
from datetime import datetime

from tests.e2e.helpers import AppConfig

# Globals removed in favor of app_config fixture


class TestI18nAPI:
    """Test i18n backend functionality using running server (avoids SQLite locking)"""

    def test_person_has_language_field(self, client, test_org_setup, app_config):
        """Verify Person model has language field"""
        # Login to get auth token
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "password"}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get people
        resp = client.get("/api/people/?org_id=test_org", headers=headers)
        assert resp.status_code == 200

        people = resp.json()["people"]
        if people:
            person = people[0]
            # Language field must exist
            assert "language" in person
            # Default should be 'en' or a valid locale
            assert person["language"] in ["en", "es", "pt", "fr", "zh-CN", "zh-TW", None]

    def test_update_person_language(self, client, test_org_setup, app_config):
        """Verify language can be updated via PUT /people/{id}"""
        # Login to get auth token
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "password"}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["token"]
        person_id = login_resp.json()["person_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update language to Chinese
        update_resp = client.put(
            f"/api/people/{person_id}",
            json={"language": "zh-CN"},
            headers=headers
        )
        assert update_resp.status_code == 200

        # Verify it was saved
        get_resp = client.get(f"/api/people/{person_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["language"] == "zh-CN"

        # Cleanup - set back to English
        client.put(
            f"/api/people/{person_id}",
            json={"language": "en"},
            headers=headers
        )

    def test_auth_login_returns_language(self, client, test_org_setup, app_config):
        """Verify login response includes language field"""
        # Use test admin user
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "password"}
        )

        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}: {login_resp.text}"

        data = login_resp.json()
        # Language must be in response
        assert "language" in data
        assert isinstance(data["language"], str)


class TestI18nTranslationFiles:
    """Test translation file integrity"""

    def test_all_translation_files_exist(self):
        """Verify all required translation files exist"""
        import os

        locales = ["en", "zh-CN", "zh-TW"]
        namespaces = ["common", "auth", "events", "schedule", "settings", "admin", "solver", "messages"]

        for locale in locales:
            for namespace in namespaces:
                file_path = f"locales/{locale}/{namespace}.json"
                assert os.path.exists(file_path), f"Missing translation file: {file_path}"

    def test_translation_files_valid_json(self):
        """Verify all translation files are valid JSON"""
        import os
        import json

        locales = ["en", "zh-CN", "zh-TW"]
        namespaces = ["common", "auth", "events", "schedule", "settings", "admin", "solver", "messages"]

        for locale in locales:
            for namespace in namespaces:
                file_path = f"locales/{locale}/{namespace}.json"
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        assert isinstance(data, dict), f"{file_path} should contain a JSON object"
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Invalid JSON in {file_path}: {e}")

    def test_translation_key_consistency(self):
        """Verify all locales have the same keys as English (baseline)"""
        import os
        import json

        def get_keys(obj, prefix=""):
            """Recursively get all keys from nested dict"""
            keys = set()
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.update(get_keys(value, full_key))
                else:
                    keys.add(full_key)
            return keys

        namespaces = ["common", "auth", "events", "schedule", "settings", "admin", "solver", "messages"]

        for namespace in namespaces:
            # Load English (baseline)
            en_path = f"locales/en/{namespace}.json"
            with open(en_path, 'r', encoding='utf-8') as f:
                en_data = json.load(f)
                en_keys = get_keys(en_data)

            # Check other locales have same keys
            for locale in ["zh-CN", "zh-TW"]:
                locale_path = f"locales/{locale}/{namespace}.json"
                with open(locale_path, 'r', encoding='utf-8') as f:
                    locale_data = json.load(f)
                    locale_keys = get_keys(locale_data)

                # Find missing keys
                missing_keys = en_keys - locale_keys
                extra_keys = locale_keys - en_keys

                assert len(missing_keys) == 0, \
                    f"{locale}/{namespace}.json missing keys: {missing_keys}"
                assert len(extra_keys) == 0, \
                    f"{locale}/{namespace}.json has extra keys: {extra_keys}"


class TestI18nGUI:
    """Test i18n GUI functionality"""

    def test_language_switching_workflow(self, api_server, test_org_setup, app_config):
        """Test complete language switching workflow via GUI"""
        # Create a fresh user via API to ensure they exist in the server's DB
        # This bypasses DB sync issues between test runner and api_server process
        import time
        import random
        
        timestamp = int(time.time())
        rand = random.randint(1000, 9999)
        email = f"gui_test_{timestamp}_{rand}@test.com"
        password = "password123"
        org_id = f"gui_org_{timestamp}_{rand}"
        
        # Create organization first
        org_resp = requests.post(
            f"{app_config.api_base}/organizations/",
            json={
                "id": org_id,
                "name": "GUI Test Org",
                "region": "US"
            }
        )
        assert org_resp.status_code == 201, f"Create org failed: {org_resp.text}"

        signup_resp = requests.post(
            f"{app_config.api_base}/auth/signup",
            json={
                "org_id": org_id,
                "name": "GUI Test User",
                "email": email,
                "password": password,
                "roles": ["admin"]
            }
        )
        assert signup_resp.status_code == 201, f"Signup failed: {signup_resp.text}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # 1. Login
                page.goto(f"{app_config.app_url}/login")
                page.wait_for_load_state("networkidle")

                # Login with new user
                page.fill('input[type="email"]', email)
                page.fill('input[type="password"]', password)
                page.get_by_role("button", name="Sign In").click()

                # Wait for login to complete (SPA may land on /wizard first)
                page.wait_for_timeout(2000)

                # Force navigation to main app screen
                page.goto(f"{app_config.app_url}/app")
                page.wait_for_load_state("networkidle")
                page.wait_for_selector('#main-app', state='visible', timeout=15_000)

                # 2. Open settings (use gear icon button)
                # 2. Open settings (use JS directly to avoid click issues)
                page.evaluate("showSettings()")
                page.locator('#settings-modal').wait_for(state="visible")
                page.wait_for_timeout(1000)

                # 3. Change language to Chinese
                language_select = page.locator('#settings-language')
                assert language_select.count() > 0, "Language selector not found - check if settings modal has language dropdown"

                language_select.select_option('zh-CN')

                # 4. Save settings (use JS directly to avoid click issues)
                page.evaluate("saveSettings()")
                page.wait_for_timeout(1000)

                # 5. Verify UI changed to Chinese
                # Check for Chinese text in navigation or headers
                body_text = page.locator('body').text_content()
                # Should contain some Chinese characters
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in body_text)
                assert has_chinese, "UI should contain Chinese text after language change"

                # 6. Refresh page
                page.reload()
                page.wait_for_timeout(2000)

                # 7. Verify language persisted
                body_text_after = page.locator('body').text_content()
                has_chinese_after = any('\u4e00' <= char <= '\u9fff' for char in body_text_after)
                assert has_chinese_after, "Language should persist after refresh"

            finally:
                browser.close()

    def test_no_object_object_in_ui(self, api_server, test_org_setup, app_config):
        """Test that no [object Object] appears in the UI"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Navigate to login
                page.goto(f"{app_config.app_url}/login")
                page.wait_for_load_state("networkidle")

                # Check for [object Object]
                body_text = page.locator('body').text_content()
                assert '[object Object]' not in body_text, \
                    "UI contains [object Object] - likely trying to display nested translation object"

                # Login
                page.fill('input[type="email"]', "admin@test.com")
                page.fill('input[type="password"]', "password")
                page.get_by_role("button", name="Sign In").click()
                page.wait_for_timeout(2000)

                # Check main app for [object Object]
                if page.locator('#main-app').is_visible():
                    body_text = page.locator('body').text_content()
                    assert '[object Object]' not in body_text, \
                        "Main app contains [object Object]"

            finally:
                browser.close()

    def test_html_has_data_i18n_attributes(self):
        """Test that HTML has data-i18n attributes on translatable elements"""
        import re

        with open('frontend/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Find translatable text patterns (text inside tags that's not HTML/JS)
        # This is a simplified check - just verify some key elements have data-i18n

        required_i18n_elements = [
            'data-i18n="common.buttons.save"',
            'data-i18n="common.buttons.cancel"',
            'data-i18n="auth.sign_in_title"',
            'data-i18n="schedule.title"',
        ]

        for element in required_i18n_elements:
            assert element in html_content or element.replace('"', "'") in html_content, \
                f"Missing i18n attribute: {element}"

    def test_url_routing_works(self, api_server, app_config):
        """Test that URL-based routing works correctly"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Test direct navigation to /login
                page.goto(f"{app_config.app_url}/login")
                page.wait_for_load_state("networkidle")
                assert '/login' in page.url

                # Test navigation to root
                page.goto(app_config.app_url)
                page.wait_for_load_state("networkidle")
                # Should show onboarding or redirect
                assert page.locator('body').is_visible()

            finally:
                browser.close()


class TestI18nRegression:
    """Regression tests for specific i18n bugs"""

    def test_modal_titles_translated(self):
        """Test that modal titles are properly translated (not hardcoded)"""
        # This is a code inspection test
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Should NOT contain hardcoded modal titles
        hardcoded_titles = [
            'textContent = "Create New Event"',
            'textContent = "Edit Event"',
            'textContent = "Create Event"',
            'textContent = "Update Event"',
        ]

        for hardcoded in hardcoded_titles:
            assert hardcoded not in content, \
                f"Found hardcoded modal title: {hardcoded}. Should use i18n.t()"

    def test_confirm_dialogs_use_i18n(self):
        """Test that confirm dialogs use i18n.t() not hardcoded strings"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find confirm() calls
        import re
        confirm_calls = re.findall(r'confirm\s*\([^)]+\)', content)

        for call in confirm_calls:
            # Should use i18n.t() not hardcoded strings
            if 'i18n.t(' not in call and '"' in call:
                # This might be a hardcoded string
                pytest.fail(f"Confirm dialog may use hardcoded string: {call}")

    def test_search_filter_all_uses_i18n(self):
        """Test that search filter 'All' option uses i18n"""
        with open('frontend/js/search-filter.js', 'r') as f:
            content = f.read()

        # Should use i18n.t() for 'All' option
        assert 'i18n.t(' in content or "i18n ? i18n.t('common.labels.all')" in content, \
            "search-filter.js should use i18n for 'All' option"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
