"""Security utilities for token generation and password hashing."""

import secrets
import hashlib


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
    """Generate a session/authentication token."""
    return generate_token(32)


def generate_calendar_token() -> str:
    """Generate a calendar subscription token."""
    return generate_token(32)


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256.

    Note: In production, use bcrypt or argon2 instead.

    Args:
        password: Plain text password

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hash to compare against

    Returns:
        True if password matches hash
    """
    return hash_password(plain_password) == hashed_password
