"""Tests for api/utils/security.py"""

import pytest
import re

from api.utils.security import (
    generate_token,
    generate_invitation_token,
    generate_auth_token,
    generate_calendar_token,
    hash_password,
    verify_password,
)


class TestTokenGeneration:
    """Test token generation functions."""

    def test_generate_token_returns_string(self):
        """Test that generate_token returns a string."""
        token = generate_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_default_length(self):
        """Test that generate_token creates token with default length."""
        token = generate_token()
        # URL-safe base64 encoding of 32 bytes typically creates ~43 chars
        assert len(token) >= 40

    def test_generate_token_custom_length(self):
        """Test that generate_token respects custom length."""
        token = generate_token(length=16)
        # URL-safe base64 encoding of 16 bytes typically creates ~22 chars
        assert len(token) >= 20
        assert len(token) <= 30

    def test_generate_token_uniqueness(self):
        """Test that generate_token creates unique tokens."""
        tokens = {generate_token() for _ in range(100)}
        # All 100 tokens should be unique
        assert len(tokens) == 100

    def test_generate_token_url_safe(self):
        """Test that generated tokens are URL-safe."""
        token = generate_token()
        # URL-safe base64 uses only alphanumeric, hyphen, and underscore
        assert re.match(r'^[A-Za-z0-9_-]+$', token)

    def test_generate_invitation_token(self):
        """Test invitation token generation."""
        token = generate_invitation_token()
        assert isinstance(token, str)
        assert len(token) >= 40

    def test_generate_auth_token(self):
        """Test auth token generation."""
        token = generate_auth_token()
        assert isinstance(token, str)
        assert len(token) >= 40

    def test_generate_calendar_token(self):
        """Test calendar token generation."""
        token = generate_calendar_token()
        assert isinstance(token, str)
        assert len(token) >= 40

    def test_different_token_types_are_unique(self):
        """Test that different token type functions generate different tokens."""
        inv_token = generate_invitation_token()
        auth_token = generate_auth_token()
        cal_token = generate_calendar_token()

        # All should be different
        assert inv_token != auth_token
        assert auth_token != cal_token
        assert inv_token != cal_token


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        hashed = hash_password("test123")
        assert isinstance(hashed, str)

    def test_hash_password_produces_bcrypt_hash(self):
        """Test that hashing produces bcrypt format hash."""
        password = "test_password_123"
        hashed = hash_password(password)
        # Bcrypt hashes start with $2b$ and are ~60 characters
        assert hashed.startswith("$2b$")
        assert len(hashed) >= 59

    def test_hash_password_different_for_different_passwords(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2

    def test_hash_password_uses_salt(self):
        """Test that bcrypt generates different hashes for same password (salted)."""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Bcrypt uses random salt, so same password = different hash
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_hash_password_empty_string(self):
        """Test hashing empty string."""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert hashed.startswith("$2b$")

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters."""
        password = "пароль密码🔒"
        hashed = hash_password(password)
        assert hashed.startswith("$2b$")


class TestPasswordVerification:
    """Test password verification function."""

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test verification with empty password."""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("not_empty", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "Password123"
        hashed = hash_password(password)
        assert verify_password("Password123", hashed) is True
        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False

    def test_verify_password_special_characters(self):
        """Test verification with special characters."""
        password = "p@ssw0rd!#$%"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("p@ssw0rd!#$", hashed) is False

    def test_verify_password_unicode(self):
        """Test verification with unicode passwords."""
        password = "пароль密码🔒"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_whitespace_sensitive(self):
        """Test that verification is whitespace-sensitive."""
        password = "pass word"
        hashed = hash_password(password)
        assert verify_password("pass word", hashed) is True
        assert verify_password("password", hashed) is False
        assert verify_password(" pass word", hashed) is False
        assert verify_password("pass word ", hashed) is False


class TestSecurityProperties:
    """Test security properties of the utilities."""

    def test_tokens_are_cryptographically_random(self):
        """Test that tokens don't follow predictable patterns."""
        # Generate many tokens
        tokens = [generate_token() for _ in range(1000)]

        # Check for no sequential patterns (very basic check)
        for i in range(len(tokens) - 1):
            assert tokens[i] != tokens[i + 1]

        # All should be unique
        assert len(set(tokens)) == len(tokens)

    def test_hash_avalanche_effect(self):
        """Test that small password changes produce very different hashes."""
        password1 = "password123"
        password2 = "password124"  # Only last character changed

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Hashes should be completely different
        assert hash1 != hash2

        # Verify that wrong password doesn't work
        assert not verify_password(password1, hash2)
        assert not verify_password(password2, hash1)

    def test_password_length_affects_hash(self):
        """Test that password length affects the hash."""
        short = hash_password("abc")
        long = hash_password("abc" * 100)

        assert short != long
        # Verify each works with correct password
        assert verify_password("abc", short)
        assert verify_password("abc" * 100, long)
