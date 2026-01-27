#!/usr/bin/env python3
"""
Test GUI i18n implementation to prevent regression

Verifies that all BLOCKED/Confirmed badges and labels use i18n.t() instead of
hardcoded English strings.
"""

import re


class TestGUIBlockedBadgesI18n:
    """Test that BLOCKED badges use i18n translation keys"""

    def test_event_blocked_badge_uses_i18n(self):
        """Verify event-blocked-badge uses i18n.t('schedule.badges.blocked')"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find the event-blocked-badge div - it should use i18n.t()
        # Pattern matches: <div class="event-blocked-badge">...${i18n.t('schedule.badges.blocked')...
        badge_pattern = r'event-blocked-badge[^>]*>.*?\$\{.*?i18n\.t\([\'"]schedule\.badges\.blocked[\'"]\)'
        assert re.search(badge_pattern, content, re.DOTALL), \
            "event-blocked-badge should use i18n.t('schedule.badges.blocked')"

    def test_no_hardcoded_blocked_in_badges(self):
        """Verify no hardcoded 'BLOCKED' strings in badge HTML"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Should NOT have hardcoded "BLOCKED" in badge divs
        # This regex finds badge HTML with hardcoded text
        bad_pattern = r'event-blocked-badge[^}]*>[^$]*BLOCKED'
        assert not re.search(bad_pattern, content), \
            "event-blocked-badge should not contain hardcoded 'BLOCKED' text"

    def test_schedule_badge_blocked_uses_i18n(self):
        """Verify schedule-badge-blocked uses i18n.t('schedule.badges.blocked')"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find schedule-badge-blocked span
        pattern = r'schedule-badge-blocked[^}]+i18n\.t\([\'"]schedule\.badges\.blocked[\'"]\)'
        assert re.search(pattern, content, re.DOTALL), \
            "schedule-badge-blocked should use i18n.t('schedule.badges.blocked')"

    def test_schedule_badge_confirmed_uses_i18n(self):
        """Verify schedule-badge confirmed uses i18n.t('schedule.badges.confirmed')"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find confirmed badge
        pattern = r'schedule-badge[^}]+i18n\.t\([\'"]schedule\.badges\.confirmed[\'"]\)'
        assert re.search(pattern, content, re.DOTALL), \
            "schedule-badge should use i18n.t('schedule.badges.confirmed') for confirmed state"

    def test_blocked_dates_label_uses_i18n(self):
        """Verify 'Blocked Dates:' label uses i18n.t('schedule.blocked_dates')"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find blocked dates label
        pattern = r'i18n\.t\([\'"]schedule\.blocked_dates[\'"]\)'
        assert re.search(pattern, content), \
            "Blocked dates label should use i18n.t('schedule.blocked_dates')"


class TestGUIBlockedBadgesTranslationKeys:
    """Test that translation keys exist in locale JSON files"""

    def test_blocked_badge_key_exists_in_english(self):
        """Verify schedule.badges.blocked exists in English"""
        import json
        with open('locales/en/schedule.json', 'r') as f:
            translations = json.load(f)

        assert 'badges' in translations, "Missing 'badges' key in schedule.json"
        assert 'blocked' in translations['badges'], \
            "Missing 'badges.blocked' key in schedule.json"

    def test_confirmed_badge_key_exists_in_english(self):
        """Verify schedule.badges.confirmed exists in English"""
        import json
        with open('locales/en/schedule.json', 'r') as f:
            translations = json.load(f)

        assert 'confirmed' in translations['badges'], \
            "Missing 'badges.confirmed' key in schedule.json"

    def test_blocked_dates_key_exists_in_english(self):
        """Verify schedule.blocked_dates exists in English"""
        import json
        with open('locales/en/schedule.json', 'r') as f:
            translations = json.load(f)

        assert 'blocked_dates' in translations, \
            "Missing 'blocked_dates' key in schedule.json"

    def test_translation_keys_exist_in_all_languages(self):
        """Verify all badge translation keys exist in all supported languages"""
        import json
        import os

        languages = ['en', 'es', 'zh-CN', 'ko', 'tl', 'vi']
        required_keys = ['badges', 'blocked_dates']

        for lang in languages:
            locale_file = f'locales/{lang}/schedule.json'
            if not os.path.exists(locale_file):
                continue

            with open(locale_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            for key in required_keys:
                assert key in translations, \
                    f"Missing key '{key}' in {lang}/schedule.json"

            # Also check that badges has blocked and confirmed
            if 'badges' in translations:
                assert 'blocked' in translations['badges'], \
                    f"Missing 'badges.blocked' in {lang}/schedule.json"
                assert 'confirmed' in translations['badges'], \
                    f"Missing 'badges.confirmed' in {lang}/schedule.json"


class TestGUIBlockedBadgesRegression:
    """Regression tests to prevent returning to hardcoded strings"""

    def test_no_hardcoded_blocked_in_event_list(self):
        """Verify event list HTML generation doesn't use hardcoded 'BLOCKED'"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Find renderEventsList or similar functions
        # Should not have template strings with raw "BLOCKED"
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'event-blocked-badge' in line or 'schedule-badge-blocked' in line:
                # Check that this line or nearby lines use i18n.t()
                context = '\n'.join(lines[max(0, i-3):min(len(lines), i+3)])
                assert 'i18n.t(' in context, \
                    f"Line {i} contains badge HTML but no i18n.t() nearby:\n{line}"

    def test_uppercase_blocked_uses_translation(self):
        """Verify uppercase BLOCKED text comes from .toUpperCase() on translation"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # If BLOCKED appears uppercase, it should be from .toUpperCase()
        # Find all occurrences of uppercase transformations
        uppercase_pattern = r'i18n\.t\([\'"]schedule\.badges\.blocked[\'"]\)\.toUpperCase\(\)'

        # Count how many times we use toUpperCase on the translation
        uppercase_count = len(re.findall(uppercase_pattern, content))

        # Should have at least one (event-blocked-badge uses uppercase)
        assert uppercase_count >= 1, \
            "Should use i18n.t('schedule.badges.blocked').toUpperCase() for uppercase display"

    def test_no_english_only_badge_text(self):
        """Verify no badge-related text is hardcoded in English"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # These phrases should NEVER appear as hardcoded strings in badge contexts
        forbidden_phrases = [
            '"BLOCKED"',
            "'BLOCKED'",
            '"Blocked"',
            "'Blocked'",
            '"Confirmed"',
            "'Confirmed'",
            '"Blocked Dates:"',
            "'Blocked Dates:'"
        ]

        for phrase in forbidden_phrases:
            # Allow these in comments, but not in actual code
            lines = content.split('\n')
            for line in lines:
                # Skip comment lines
                if line.strip().startswith('//'):
                    continue

                if phrase in line and 'i18n' not in line:
                    # This is likely a hardcoded string (not a translation)
                    assert False, \
                        f"Found hardcoded phrase {phrase} in non-i18n context:\n{line}"


class TestGUIBlockedBadgesStyling:
    """Test that badge CSS classes are correctly applied"""

    def test_blocked_badge_has_correct_css_class(self):
        """Verify blocked badges use 'event-blocked-badge' or 'schedule-badge-blocked' class"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Should have both badge classes
        assert 'event-blocked-badge' in content, \
            "Missing 'event-blocked-badge' CSS class"
        assert 'schedule-badge-blocked' in content, \
            "Missing 'schedule-badge-blocked' CSS class"

    def test_confirmed_badge_has_correct_css_class(self):
        """Verify confirmed badges use 'schedule-badge' class"""
        with open('frontend/js/app-user.js', 'r') as f:
            content = f.read()

        # Should have schedule-badge class for confirmed state
        assert 'schedule-badge' in content, \
            "Missing 'schedule-badge' CSS class for confirmed state"

    def test_blocked_badge_css_exists(self):
        """Verify CSS styles exist for blocked badges"""
        import os

        # Check if CSS file exists
        css_files = [
            'frontend/css/styles.css',
            'frontend/css/styles-admin.css',
            'frontend/css/mobile.css'
        ]

        css_content = ""
        for css_file in css_files:
            if os.path.exists(css_file):
                with open(css_file, 'r') as f:
                    css_content += f.read()

        # Should have styles for blocked badges
        assert 'event-blocked-badge' in css_content or 'schedule-badge-blocked' in css_content, \
            "CSS styles for blocked badges not found"
