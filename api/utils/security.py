"""Security utilities for token generation and password hashing.

DEPRECATED: hash_password and verify_password have been moved to api.security
with bcrypt implementation. This module is kept for backward compatibility.
"""

import secrets
from api.security import hash_password as _hash_password, verify_password as _verify_password


def generate_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Number of bytes to generate (default 32)

    Returns:
        URL-safe base64 encoded token string
    """
    return secrets.token_urlsafe(length)


def generate_invitation_token() -> str:
    """Generate a unique invitation token."""
    return generate_token(32)


def generate_auth_token() -> str:
    """Generate a session/authentication token (for calendar subscriptions)."""
    return generate_token(32)


def generate_calendar_token() -> str:
    """Generate a calendar subscription token."""
    return generate_token(32)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password

    Note: This now uses bcrypt from api.security instead of SHA-256
    """
    return _hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches hash
    """
    return _verify_password(plain_password, hashed_password)
