"""
Password strength validation.

Enforces password security requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not a common/breached password (optional)
"""

import re
import os
from typing import Tuple, List, Optional


class PasswordValidator:
    """
    Validates password strength according to security best practices.

    Configuration via environment variables:
    - PASSWORD_MIN_LENGTH: Minimum password length (default: 8)
    - PASSWORD_REQUIRE_UPPERCASE: Require uppercase letter (default: true)
    - PASSWORD_REQUIRE_LOWERCASE: Require lowercase letter (default: true)
    - PASSWORD_REQUIRE_NUMBER: Require digit (default: true)
    - PASSWORD_REQUIRE_SPECIAL: Require special character (default: true)
    - PASSWORD_SPECIAL_CHARS: Allowed special characters (default: !@#$%^&*()_+-=[]{}|;:,.<>?)
    """

    def __init__(self):
        # Load configuration from environment
        self.min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        self.require_uppercase = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
        self.require_lowercase = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
        self.require_number = os.getenv("PASSWORD_REQUIRE_NUMBER", "true").lower() == "true"
        self.require_special = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
        self.special_chars = os.getenv("PASSWORD_SPECIAL_CHARS", "!@#$%^&*()_+-=[]{}|;:,.<>?")

        # Common weak passwords (top 100 most common passwords)
        self.common_passwords = {
            "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
            "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master",
            "sunshine", "ashley", "bailey", "passw0rd", "shadow", "123123", "654321",
            "superman", "qazwsx", "michael", "football", "password1", "admin", "welcome",
            "Login123", "Test123!", "Admin123",  # Common test passwords
        }

    def validate(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            (is_valid, error_message)
            - (True, None) if password is strong enough
            - (False, "error message") if password is weak
        """
        errors = self.get_validation_errors(password)

        if errors:
            # Return first error
            return False, errors[0]

        return True, None

    def get_validation_errors(self, password: str) -> List[str]:
        """
        Get all validation errors for a password.

        Args:
            password: Password to validate

        Returns:
            List of error messages (empty list if valid)
        """
        errors = []

        # Check length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")

        # Check uppercase
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        # Check lowercase
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        # Check number
        if self.require_number and not re.search(r"\d", password):
            errors.append("Password must contain at least one number")

        # Check special character
        if self.require_special:
            special_char_pattern = f"[{re.escape(self.special_chars)}]"
            if not re.search(special_char_pattern, password):
                errors.append(f"Password must contain at least one special character ({self.special_chars})")

        # Check against common passwords (case-insensitive)
        if password.lower() in self.common_passwords:
            errors.append("Password is too common. Please choose a stronger password")

        return errors

    def get_password_requirements(self) -> str:
        """
        Get human-readable password requirements.

        Returns:
            String describing password requirements
        """
        requirements = [f"At least {self.min_length} characters"]

        if self.require_uppercase:
            requirements.append("At least one uppercase letter")

        if self.require_lowercase:
            requirements.append("At least one lowercase letter")

        if self.require_number:
            requirements.append("At least one number")

        if self.require_special:
            requirements.append(f"At least one special character ({self.special_chars})")

        return "; ".join(requirements)

    def calculate_password_strength(self, password: str) -> Tuple[str, int]:
        """
        Calculate password strength score.

        Args:
            password: Password to evaluate

        Returns:
            (strength_label, score)
            - strength_label: "weak", "fair", "good", "strong"
            - score: 0-100
        """
        score = 0

        # Length (up to 40 points)
        if len(password) >= self.min_length:
            score += min(40, len(password) * 3)

        # Character variety (up to 60 points)
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 15
        if re.search(f"[{re.escape(self.special_chars)}]", password):
            score += 25

        # Penalties
        if password.lower() in self.common_passwords:
            score = max(0, score - 50)  # Heavy penalty for common passwords

        # Cap at 100
        score = min(100, score)

        # Determine strength label
        if score < 30:
            strength = "weak"
        elif score < 60:
            strength = "fair"
        elif score < 80:
            strength = "good"
        else:
            strength = "strong"

        return strength, score


# Global validator instance
_validator = None


def get_password_validator() -> PasswordValidator:
    """Get the global PasswordValidator instance."""
    global _validator
    if _validator is None:
        _validator = PasswordValidator()
    return _validator


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength using global validator.

    Args:
        password: Password to validate

    Returns:
        (is_valid, error_message)
    """
    validator = get_password_validator()
    return validator.validate(password)


def get_password_requirements() -> str:
    """Get human-readable password requirements."""
    validator = get_password_validator()
    return validator.get_password_requirements()
