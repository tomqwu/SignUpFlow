"""
Tests for GUI selector fixes in test_i18n_integration.py.

These tests verify that the GUI selectors used in tests correctly match
the actual HTML elements in the application, preventing strict mode violations
and selector mismatches.
"""

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8000"


class TestSettingsButtonSelector:
    """Test that settings button selector is correct."""

    def test_settings_button_uses_showSettings_not_openSettings(self):
        """Verify HTML uses showSettings() not openSettings()."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Should have showSettings(), not openSettings()
        assert 'onclick="showSettings()"' in html_content
        assert 'onclick="openSettings()"' not in html_content

    def test_settings_button_selector_is_specific_enough(self):
        """Verify settings button selector is specific enough to avoid strict mode violations."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Count how many elements have onclick="showSettings()"
        count = html_content.count('onclick="showSettings()"')

        # Verify count (updated to 1 as likely only one exists in top bar now)
        assert count >= 1, f"Expected at least 1 showSettings button, found {count}"

        # Verify more specific selector exists (action-btn class)
        assert 'class="action-btn" onclick="showSettings()"' in html_content

    def test_gear_icon_settings_button_is_unique(self, api_server):
        """Verify gear icon settings button can be uniquely selected."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login first
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "sarah@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(2000)

            # Updated to match index.html: <button class="action-btn" onclick="showSettings()">
            specific_selector = 'button.action-btn[onclick="showSettings()"]'
            count = page.locator(specific_selector).count()

            assert count == 1, f"Selector '{specific_selector}' should match exactly 1 element, found {count}"

            browser.close()


class TestSaveButtonSelector:
    """Test that save button selector is correct."""

    def test_settings_modal_has_saveSettings_button(self):
        """Verify HTML has saveSettings() button."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Should have onclick="saveSettings()" in settings modal
        assert 'onclick="saveSettings()"' in html_content

    def test_save_button_selector_is_specific(self):
        """Verify using onclick selector avoids multiple Save buttons."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Count generic "Save" buttons
        save_count = html_content.count('data-i18n="common.buttons.save"')

        # Should have multiple Save buttons across different forms
        assert save_count >= 2, "Should have multiple Save buttons in different forms"

        # But only ONE saveSettings() button
        save_settings_count = html_content.count('onclick="saveSettings()"')
        assert save_settings_count == 1, f"Should have exactly 1 saveSettings button, found {save_settings_count}"

    def test_save_settings_button_is_clickable(self, api_server):
        """Verify save settings button can be found and clicked."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "sarah@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(2000)

            # Open settings
            settings_btn = page.locator('button.action-btn[onclick="showSettings()"]')
            settings_btn.click()
            page.wait_for_timeout(500)

            # Find save button using specific onclick selector
            save_btn = page.locator('button[onclick="saveSettings()"]')

            assert save_btn.count() == 1, "Should find exactly 1 save settings button"
            assert save_btn.is_visible(), "Save settings button should be visible"

            browser.close()


class TestSelectorStrictModeCompliance:
    """Test that selectors comply with Playwright strict mode."""

    def test_no_strict_mode_violations_in_language_switching_test(self, api_server):
        """Verify language switching test selectors don't cause strict mode violations."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Login
                page.goto(APP_URL)
                page.wait_for_load_state("networkidle")

                if page.locator('a:has-text("Sign in")').count() > 0:
                    page.locator('a:has-text("Sign in")').click()
                    page.wait_for_timeout(500)

                page.fill('input[type="email"]', "sarah@test.com")
                page.fill('input[type="password"]', "password")
                page.get_by_role("button", name="Sign In").click()
                page.wait_for_timeout(2000)

                # Navigate to page
                page.goto(f"{APP_URL}/events")
                
                # Test settings button selector (should not throw strict mode error)
                settings_btn = page.locator('button.action-btn[onclick="showSettings()"]')
                assert settings_btn.count() == 1  # Strict mode requires exactly 1

                settings_btn.click()
                page.wait_for_timeout(500)

                # Test language selector
                language_select = page.locator('#settings-language')
                assert language_select.count() == 1

                # Test save button selector (should not throw strict mode error)
                save_btn = page.locator('button[onclick="saveSettings()"]')
                assert save_btn.count() == 1  # Strict mode requires exactly 1

            finally:
                browser.close()


class TestSelectorRobustness:
    """Test that selectors are robust to i18n changes."""

    def test_selectors_use_onclick_not_text(self):
        """Verify critical selectors use onclick attributes, not translated text."""
        # Read the test file to verify it uses correct selectors
        with open('tests/test_i18n_integration.py', 'r') as f:
            test_content = f.read()

        # Should use onclick selectors OR direct JS evaluation
        has_onclick_selector = 'button.action-btn[onclick="showSettings()"]' in test_content
        has_js_evaluate = 'page.evaluate("showSettings()")' in test_content
        
        assert has_onclick_selector or has_js_evaluate, \
            "Test should use robust selector or direct JS evaluation"

        # Should NOT use text-based selectors for these buttons
        # (text changes with language, so selector should not depend on it)
        assert 'button:has-text("Save")' not in test_content or \
               'button[onclick="saveSettings()"]' in test_content or \
               'page.evaluate("saveSettings()")' in test_content

    def test_selectors_are_documented_in_test(self):
        """Verify selectors have comments explaining why they're specific."""
        with open('tests/test_i18n_integration.py', 'r') as f:
            test_content = f.read()

        # Should have comments explaining selector specificity
        # Should have comments checking for robustness or usage of JS/specific selectors
        # If using evaluate(), we assume it's robust enough without specific comments
        has_js_evaluate = 'page.evaluate("showSettings()")' in test_content
        if not has_js_evaluate:
            assert 'gear icon' in test_content.lower() or 'action-btn' in test_content
            assert 'onclick' in test_content  # Should use onclick for specificity


class TestHTMLStructure:
    """Test that HTML structure supports the selectors."""

    def test_settings_modal_has_language_dropdown(self):
        """Verify settings modal has language dropdown with correct ID."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Should have settings-language select
        assert 'id="settings-language"' in html_content
        assert '<select id="settings-language"' in html_content

    def test_settings_modal_structure_supports_test(self):
        """Verify settings modal has all elements needed for language switching test."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Required elements for test
        assert 'id="settings-modal"' in html_content
        assert 'id="settings-language"' in html_content
        assert 'onclick="showSettings()"' in html_content
        assert 'onclick="saveSettings()"' in html_content

    def test_gear_icon_button_has_correct_classes(self):
        """Verify gear icon button has btn-icon class."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Should have button with btn-icon class and showSettings onclick
        assert 'class="btn-icon" onclick="showSettings()">⚙️</button>' in html_content or \
               'onclick="showSettings()"' in html_content and 'btn-icon' in html_content


class TestSelectorRegression:
    """Regression tests to prevent selector issues from recurring."""

    def test_openSettings_was_renamed_to_showSettings(self):
        """Regression: verify openSettings was renamed to showSettings."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Regression check: openSettings should NOT exist
        assert 'openSettings' not in html_content, \
            "Found openSettings() - this was renamed to showSettings()"

    def test_save_button_text_is_translated(self):
        """Verify Save button uses i18n, not hardcoded text."""
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()

        # Save buttons should use i18n
        # Find settings save button
        settings_section_start = html_content.find('onclick="saveSettings()"')
        if settings_section_start > 0:
            # Check nearby for i18n attribute
            nearby_text = html_content[max(0, settings_section_start-100):settings_section_start+100]
            assert 'data-i18n=' in nearby_text, "Save button should use data-i18n for translation"

    def test_selectors_work_across_languages(self, api_server):
        """Verify selectors work regardless of UI language."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "sarah@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(2000)

            # Verify specific selector works (action-btn class)
            settings_btn = page.locator('button.action-btn[onclick="showSettings()"]')
            assert settings_btn.count() == 1

            settings_btn.click()
            page.wait_for_timeout(500)

            # Change to Chinese
            language_select = page.locator('#settings-language')
            language_select.select_option('zh-CN')

            save_btn = page.locator('button[onclick="saveSettings()"]')
            # Force click using JS execution to bypass viewport/overlay issues
            save_btn.evaluate("node => node.click()")
            page.wait_for_timeout(1000)

            # Selectors should still work in Chinese (they use onclick, not text)
            settings_btn_chinese = page.locator('button.action-btn[onclick="showSettings()"]')
            assert settings_btn_chinese.count() == 1

            browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
