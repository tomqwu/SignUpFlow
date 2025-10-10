"""Test translation coverage across all languages.

This test ensures that every feature has complete i18n coverage.
Part of the "Definition of Done" for any UI feature.
"""

import json
import pytest
from pathlib import Path


class TestTranslationCoverage:
    """Ensure all languages have complete translation coverage."""

    LOCALES_DIR = Path("locales")
    NAMESPACES = ["admin", "auth", "common", "events", "messages", "schedule", "settings", "solver"]
    LANGUAGES = ["en", "es", "pt", "zh-CN", "zh-TW"]
    BASE_LANGUAGE = "en"

    def get_all_keys(self, obj, prefix=''):
        """Get all translation keys from a nested dict."""
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f'{prefix}.{k}' if prefix else k
                if isinstance(v, dict):
                    keys.extend(self.get_all_keys(v, new_key))
                else:
                    keys.append(new_key)
        return keys

    def load_namespace(self, lang: str, namespace: str):
        """Load a translation namespace for a language."""
        file_path = self.LOCALES_DIR / lang / f"{namespace}.json"
        if not file_path.exists():
            return None
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)

    def test_all_namespace_files_exist(self):
        """Test that all namespaces exist for all languages."""
        missing_files = []

        for namespace in self.NAMESPACES:
            # Check if English file exists
            en_file = self.LOCALES_DIR / self.BASE_LANGUAGE / f"{namespace}.json"
            if not en_file.exists():
                pytest.skip(f"English namespace {namespace} doesn't exist - skipping")

            # Check all other languages
            for lang in self.LANGUAGES:
                if lang == self.BASE_LANGUAGE:
                    continue

                lang_file = self.LOCALES_DIR / lang / f"{namespace}.json"
                if not lang_file.exists():
                    missing_files.append(f"{lang}/{namespace}.json")

        assert len(missing_files) == 0, \
            f"Missing translation files:\n  " + "\n  ".join(missing_files)

    def test_all_languages_have_same_keys(self):
        """Test that all languages have the same translation keys as English."""
        mismatches = []

        for namespace in self.NAMESPACES:
            # Load English (baseline)
            en_data = self.load_namespace(self.BASE_LANGUAGE, namespace)
            if en_data is None:
                continue

            en_keys = set(self.get_all_keys(en_data))

            # Check all other languages
            for lang in self.LANGUAGES:
                if lang == self.BASE_LANGUAGE:
                    continue

                lang_data = self.load_namespace(lang, namespace)
                if lang_data is None:
                    mismatches.append(f"{namespace}/{lang}: FILE MISSING")
                    continue

                lang_keys = set(self.get_all_keys(lang_data))

                # Check for missing keys
                missing = en_keys - lang_keys
                if missing:
                    mismatches.append(
                        f"{namespace}/{lang}: Missing {len(missing)} keys: " +
                        ", ".join(sorted(list(missing)[:5])) +
                        ("..." if len(missing) > 5 else "")
                    )

                # Check for extra keys (indicates structure mismatch)
                extra = lang_keys - en_keys
                if extra:
                    mismatches.append(
                        f"{namespace}/{lang}: Extra {len(extra)} keys: " +
                        ", ".join(sorted(list(extra)[:5])) +
                        ("..." if len(extra) > 5 else "")
                    )

        assert len(mismatches) == 0, \
            f"Translation coverage issues:\n  " + "\n  ".join(mismatches)

    def test_no_empty_translations(self):
        """Test that no translation values are empty strings."""
        empty_translations = []

        for namespace in self.NAMESPACES:
            for lang in self.LANGUAGES:
                lang_data = self.load_namespace(lang, namespace)
                if lang_data is None:
                    continue

                # Check all values
                all_keys = self.get_all_keys(lang_data)
                for key in all_keys:
                    # Navigate to the value
                    parts = key.split('.')
                    value = lang_data
                    for part in parts:
                        value = value[part]

                    if isinstance(value, str) and value.strip() == "":
                        empty_translations.append(f"{namespace}/{lang}: {key}")

        assert len(empty_translations) == 0, \
            f"Empty translation values found:\n  " + "\n  ".join(empty_translations)

    def test_chinese_translations_not_in_english(self):
        """Test that Chinese translations are actually in Chinese, not English fallbacks."""
        english_fallbacks = []

        for namespace in self.NAMESPACES:
            en_data = self.load_namespace(self.BASE_LANGUAGE, namespace)
            if en_data is None:
                continue

            for lang in ["zh-CN", "zh-TW"]:
                lang_data = self.load_namespace(lang, namespace)
                if lang_data is None:
                    continue

                # Sample some keys and check if they're identical to English
                all_keys = self.get_all_keys(en_data)
                sample_keys = all_keys[:10]  # Check first 10 keys

                for key in sample_keys:
                    parts = key.split('.')

                    en_value = en_data
                    lang_value = lang_data

                    try:
                        for part in parts:
                            en_value = en_value[part]
                            lang_value = lang_value[part]

                        # If values are identical and contain ASCII letters, it's likely an English fallback
                        if (isinstance(en_value, str) and isinstance(lang_value, str) and
                            en_value == lang_value and
                            any(c.isascii() and c.isalpha() for c in en_value)):
                            english_fallbacks.append(f"{namespace}/{lang}: {key} = '{en_value}'")
                    except (KeyError, TypeError):
                        pass

        # Allow some fallbacks but warn if too many
        if len(english_fallbacks) > 20:
            pytest.fail(
                f"Too many English fallbacks in Chinese translations ({len(english_fallbacks)}):\n  " +
                "\n  ".join(english_fallbacks[:10]) +
                "\n  ..."
            )

    def test_settings_namespace_fully_translated(self):
        """Test that the settings namespace is 100% translated for all languages.

        Settings is user-facing and critical, so it MUST be fully translated.
        """
        issues = []

        en_data = self.load_namespace(self.BASE_LANGUAGE, "settings")
        if en_data is None:
            pytest.skip("English settings namespace doesn't exist")

        en_keys = set(self.get_all_keys(en_data))

        for lang in self.LANGUAGES:
            if lang == self.BASE_LANGUAGE:
                continue

            lang_data = self.load_namespace(lang, "settings")
            if lang_data is None:
                issues.append(f"{lang}/settings.json: FILE MISSING")
                continue

            lang_keys = set(self.get_all_keys(lang_data))

            missing = en_keys - lang_keys
            if missing:
                issues.append(f"{lang}: Missing keys in settings: {', '.join(sorted(missing))}")

            extra = lang_keys - en_keys
            if extra:
                issues.append(f"{lang}: Extra keys in settings: {', '.join(sorted(extra))}")

        assert len(issues) == 0, \
            f"Settings namespace must be 100% translated:\n  " + "\n  ".join(issues)

    def test_generate_coverage_report(self):
        """Generate a coverage report for all namespaces and languages.

        This is informational - it shows what needs translation work.
        """
        report = []
        report.append("\n=== I18N COVERAGE REPORT ===\n")

        for namespace in self.NAMESPACES:
            en_data = self.load_namespace(self.BASE_LANGUAGE, namespace)
            if en_data is None:
                continue

            en_keys = set(self.get_all_keys(en_data))
            total_keys = len(en_keys)

            report.append(f"\n{namespace.upper()} ({total_keys} keys):")

            for lang in self.LANGUAGES:
                if lang == self.BASE_LANGUAGE:
                    continue

                lang_data = self.load_namespace(lang, namespace)
                if lang_data is None:
                    report.append(f"  {lang}: ❌ FILE MISSING")
                    continue

                lang_keys = set(self.get_all_keys(lang_data))
                missing = len(en_keys - lang_keys)
                coverage = ((total_keys - missing) / total_keys * 100) if total_keys > 0 else 0

                if missing == 0:
                    report.append(f"  {lang}: ✅ 100% ({len(lang_keys)} keys)")
                else:
                    report.append(f"  {lang}: ⚠️  {coverage:.1f}% ({len(lang_keys)}/{total_keys} keys, {missing} missing)")

        # Print report (will show in test output)
        print("".join(report))

        # This test always passes - it's just informational
        assert True, "Coverage report generated"
