"""
Unit tests for password strength validation.

Tests the PasswordValidator class which enforces:
- Minimum length requirements
- Character variety (uppercase, lowercase, numbers, special)
- Common password blocking
- Password strength scoring
"""

import pytest
import os
from unittest.mock import patch
from api.utils.password_validator import (
    PasswordValidator,
    get_password_validator,
    validate_password_strength,
    get_password_requirements,
)


class TestPasswordValidator:
    """Test PasswordValidator class with default configuration."""

    def test_strong_password_passes(self):
        """Test that a strong password passes validation."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("MyStr0ng!Pass")

        assert is_valid is True
        assert error is None

    def test_weak_password_too_short(self):
        """Test that password shorter than minimum length fails."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("Sh0rt!")

        assert is_valid is False
        assert "at least 8 characters" in error

    def test_weak_password_no_uppercase(self):
        """Test that password without uppercase fails."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("mypassword123!")

        assert is_valid is False
        assert "uppercase letter" in error

    def test_weak_password_no_lowercase(self):
        """Test that password without lowercase fails."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("MYPASSWORD123!")

        assert is_valid is False
        assert "lowercase letter" in error

    def test_weak_password_no_number(self):
        """Test that password without number fails."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("MyPassword!")

        assert is_valid is False
        assert "number" in error

    def test_weak_password_no_special_char(self):
        """Test that password without special character fails."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("MyPassword123")

        assert is_valid is False
        assert "special character" in error

    def test_common_password_blocked(self):
        """Test that common passwords are blocked."""
        validator = PasswordValidator()

        # Test various common passwords
        common_passwords = [
            "password",
            "Password123!",  # Still common even with requirements
            "123456",
            "qwerty",
            "admin",
            "letmein",
        ]

        for pwd in common_passwords:
            is_valid, error = validator.validate(pwd)
            # Some may fail other checks, but should have common password error
            errors = validator.get_validation_errors(pwd)
            assert any("too common" in err for err in errors), f"{pwd} should be blocked as common"

    def test_get_validation_errors_returns_all_errors(self):
        """Test that get_validation_errors returns all validation failures."""
        validator = PasswordValidator()
        errors = validator.get_validation_errors("bad")

        # Should have multiple errors (too short, missing requirements)
        assert len(errors) >= 2
        assert any("at least 8 characters" in err for err in errors)

    def test_password_strength_calculation_weak(self):
        """Test password strength scoring for weak passwords."""
        validator = PasswordValidator()
        strength, score = validator.calculate_password_strength("password")

        assert strength == "weak"
        assert score < 30

    def test_password_strength_calculation_fair(self):
        """Test password strength scoring for fair passwords."""
        validator = PasswordValidator()
        strength, score = validator.calculate_password_strength("MyPass123")

        assert strength in ["fair", "good"]
        assert 30 <= score < 80

    def test_password_strength_calculation_good(self):
        """Test password strength scoring for good passwords."""
        validator = PasswordValidator()
        strength, score = validator.calculate_password_strength("MyGoodP@ss123")

        assert strength in ["good", "strong"]
        assert score >= 60

    def test_password_strength_calculation_strong(self):
        """Test password strength scoring for strong passwords."""
        validator = PasswordValidator()
        strength, score = validator.calculate_password_strength("MyVery$tr0ng!P@ssw0rd2024")

        assert strength == "strong"
        assert score >= 80

    def test_get_password_requirements(self):
        """Test that password requirements are returned as readable string."""
        validator = PasswordValidator()
        requirements = validator.get_password_requirements()

        assert "At least 8 characters" in requirements
        assert "uppercase letter" in requirements
        assert "lowercase letter" in requirements
        assert "number" in requirements
        assert "special character" in requirements


class TestPasswordValidatorConfiguration:
    """Test PasswordValidator with custom environment configuration."""

    @patch.dict(os.environ, {"PASSWORD_MIN_LENGTH": "12"})
    def test_custom_min_length(self):
        """Test that minimum length can be configured."""
        validator = PasswordValidator()

        # 10 characters should fail with min_length=12
        is_valid, error = validator.validate("MyP@ss1234")
        assert is_valid is False
        assert "at least 12 characters" in error

        # 12 characters should pass
        is_valid, error = validator.validate("MyP@ssword12")
        assert is_valid is True

    @patch.dict(os.environ, {"PASSWORD_REQUIRE_UPPERCASE": "false"})
    def test_uppercase_not_required(self):
        """Test that uppercase requirement can be disabled."""
        validator = PasswordValidator()

        # Should pass without uppercase
        is_valid, error = validator.validate("mypassword123!")
        assert is_valid is True

    @patch.dict(os.environ, {"PASSWORD_REQUIRE_LOWERCASE": "false"})
    def test_lowercase_not_required(self):
        """Test that lowercase requirement can be disabled."""
        validator = PasswordValidator()

        # Should pass without lowercase
        is_valid, error = validator.validate("MYPASSWORD123!")
        assert is_valid is True

    @patch.dict(os.environ, {"PASSWORD_REQUIRE_NUMBER": "false"})
    def test_number_not_required(self):
        """Test that number requirement can be disabled."""
        validator = PasswordValidator()

        # Should pass without number
        is_valid, error = validator.validate("MyPassword!")
        assert is_valid is True

    @patch.dict(os.environ, {"PASSWORD_REQUIRE_SPECIAL": "false"})
    def test_special_char_not_required(self):
        """Test that special character requirement can be disabled."""
        validator = PasswordValidator()

        # Should pass without special char
        is_valid, error = validator.validate("MyPassword123")
        assert is_valid is True

    @patch.dict(os.environ, {"PASSWORD_SPECIAL_CHARS": "!@#$"})
    def test_custom_special_chars(self):
        """Test that allowed special characters can be customized."""
        validator = PasswordValidator()

        # Should pass with allowed special char
        is_valid, error = validator.validate("MyPassword123!")
        assert is_valid is True

        # Should fail with non-allowed special char
        is_valid, error = validator.validate("MyPassword123%")
        assert is_valid is False
        assert "special character (!@#$)" in error


class TestGlobalValidatorFunctions:
    """Test global convenience functions."""

    def test_get_password_validator_returns_singleton(self):
        """Test that get_password_validator returns same instance."""
        validator1 = get_password_validator()
        validator2 = get_password_validator()

        assert validator1 is validator2

    def test_validate_password_strength_function(self):
        """Test global validate_password_strength function."""
        is_valid, error = validate_password_strength("MyStr0ng!Pass")

        assert is_valid is True
        assert error is None

    def test_validate_password_strength_function_fails(self):
        """Test global validate_password_strength function with weak password."""
        is_valid, error = validate_password_strength("weak")

        assert is_valid is False
        assert error is not None

    def test_get_password_requirements_function(self):
        """Test global get_password_requirements function."""
        requirements = get_password_requirements()

        assert isinstance(requirements, str)
        assert len(requirements) > 0
        assert "characters" in requirements


class TestPasswordValidatorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_password(self):
        """Test that empty password fails validation."""
        validator = PasswordValidator()
        is_valid, error = validator.validate("")

        assert is_valid is False
        assert "at least 8 characters" in error

    def test_very_long_password(self):
        """Test that very long passwords are accepted."""
        validator = PasswordValidator()
        long_password = "MyVeryLong!P@ssw0rd" * 10  # 190 characters

        is_valid, error = validator.validate(long_password)
        assert is_valid is True

    def test_unicode_characters(self):
        """Test that unicode characters are handled."""
        validator = PasswordValidator()
        # Unicode password with requirements
        is_valid, error = validator.validate("MyP@ss™123")

        # Should pass (™ counts as special char depending on regex)
        assert is_valid is True or "special character" in error

    def test_case_insensitive_common_password_check(self):
        """Test that common password check is case-insensitive."""
        validator = PasswordValidator()

        # Test various casings of "password"
        for pwd in ["password", "PASSWORD", "Password", "PaSsWoRd"]:
            errors = validator.get_validation_errors(pwd)
            assert any("too common" in err for err in errors), f"{pwd} should be blocked"

    def test_strength_calculation_capped_at_100(self):
        """Test that strength score is capped at 100."""
        validator = PasswordValidator()
        very_strong = "MyVeryStr0ng!P@ssw0rd2024WithLotsOfCharacters!@#$%"

        strength, score = validator.calculate_password_strength(very_strong)
        assert score <= 100

    def test_strength_calculation_floored_at_0(self):
        """Test that strength score doesn't go below 0."""
        validator = PasswordValidator()

        strength, score = validator.calculate_password_strength("password")
        assert score >= 0

    def test_common_password_with_variations(self):
        """Test that common password variations are blocked."""
        validator = PasswordValidator()

        # Common test passwords should be blocked
        test_passwords = [
            "Login123",
            "Test123!",
            "Admin123",
        ]

        for pwd in test_passwords:
            errors = validator.get_validation_errors(pwd)
            assert any("too common" in err for err in errors), f"{pwd} should be blocked as common test password"
