"""
Integration tests for reCAPTCHA verification.

These tests verify the reCAPTCHA module works correctly but DO NOT
make real calls to Google (to avoid flakiness and API quotas).

Tests use mocked responses to verify:
- Token verification logic
- Score threshold enforcement
- Action name verification
- Error handling
- Testing mode bypass
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from api.utils.recaptcha import verify_recaptcha, get_recaptcha_site_key


class TestRecaptchaTestingMode:
    """Test reCAPTCHA behavior in testing mode."""

    @pytest.mark.asyncio
    async def test_recaptcha_disabled_in_test_mode(self, monkeypatch):
        """Test that reCAPTCHA is disabled when TESTING=true."""
        monkeypatch.setenv("TESTING", "true")

        # Should return True (bypass) when in test mode
        is_valid, score = await verify_recaptcha("any_token", "127.0.0.1", "test_action")

        assert is_valid is True
        assert score == 1.0  # Max score in test mode

    @pytest.mark.asyncio
    async def test_recaptcha_disabled_with_empty_token_in_test_mode(self, monkeypatch):
        """Test that even empty tokens pass in test mode."""
        monkeypatch.setenv("TESTING", "true")

        is_valid, score = await verify_recaptcha("", "127.0.0.1", "test_action")

        assert is_valid is True
        assert score == 1.0


class TestRecaptchaValidTokens:
    """Test reCAPTCHA with valid tokens."""

    @pytest.mark.asyncio
    async def test_recaptcha_valid_token_high_score(self, monkeypatch):
        """Test verification with valid reCAPTCHA token and high score."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        # Mock httpx AsyncClient response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.9,
            "action": "test_action",
            "challenge_ts": "2025-10-17T00:00:00Z",
            "hostname": "localhost"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("valid_token_abc123", "127.0.0.1", "test_action")

        assert is_valid is True
        assert score == 0.9

    @pytest.mark.asyncio
    async def test_recaptcha_valid_token_exact_threshold(self, monkeypatch):
        """Test verification with score exactly at threshold."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.5,  # Exactly at default threshold
            "action": "test_action"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("valid_token", "127.0.0.1", "test_action", min_score=0.5)

        assert is_valid is True
        assert score == 0.5

    @pytest.mark.asyncio
    async def test_recaptcha_valid_token_perfect_score(self, monkeypatch):
        """Test verification with perfect 1.0 score."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 1.0,
            "action": "test_action"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("perfect_token", "127.0.0.1", "test_action")

        assert is_valid is True
        assert score == 1.0


class TestRecaptchaLowScores:
    """Test reCAPTCHA rejection of low scores (likely bots)."""

    @pytest.mark.asyncio
    async def test_recaptcha_low_score_default_threshold(self, monkeypatch):
        """Test verification rejects low scores with default threshold."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.3,  # Below default 0.5 threshold
            "action": "test_action"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("bot_token", "127.0.0.1", "test_action")

        assert is_valid is False
        assert score == 0.3

    @pytest.mark.asyncio
    async def test_recaptcha_low_score_custom_threshold(self, monkeypatch):
        """Test verification with custom threshold."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.6,  # Would pass default, but we set higher threshold
            "action": "test_action"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "test_action", min_score=0.7)

        assert is_valid is False
        assert score == 0.6

    @pytest.mark.asyncio
    async def test_recaptcha_zero_score(self, monkeypatch):
        """Test verification rejects zero score (definitely bot)."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.0,
            "action": "test_action"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("bot_token", "127.0.0.1", "test_action")

        assert is_valid is False
        assert score == 0.0


class TestRecaptchaInvalidTokens:
    """Test reCAPTCHA handling of invalid tokens."""

    @pytest.mark.asyncio
    async def test_recaptcha_invalid_token(self, monkeypatch):
        """Test verification rejects invalid tokens."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error-codes": ["invalid-input-response"]
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("invalid_token", "127.0.0.1", "test_action")

        assert is_valid is False
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_recaptcha_expired_token(self, monkeypatch):
        """Test verification rejects expired tokens."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error-codes": ["timeout-or-duplicate"]
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("expired_token", "127.0.0.1", "test_action")

        assert is_valid is False
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_recaptcha_missing_secret_key(self, monkeypatch):
        """Test verification fails when secret key is missing."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.delenv("RECAPTCHA_SECRET_KEY", raising=False)

        is_valid, score = await verify_recaptcha("token", "127.0.0.1", "test_action")

        assert is_valid is False
        assert score == 0.0


class TestRecaptchaActionVerification:
    """Test reCAPTCHA action name verification."""

    @pytest.mark.asyncio
    async def test_recaptcha_action_mismatch(self, monkeypatch):
        """Test that action name mismatch is detected."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.9,
            "action": "wrong_action"  # Different from expected
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            # When expected action is provided, mismatch should fail
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "expected_action")

        assert is_valid is False
        assert score == 0.9  # Score is still returned

    @pytest.mark.asyncio
    async def test_recaptcha_action_match(self, monkeypatch):
        """Test that matching action names pass."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "score": 0.9,
            "action": "password_reset"
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "password_reset")

        assert is_valid is True
        assert score == 0.9


class TestRecaptchaErrorHandling:
    """Test reCAPTCHA error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_recaptcha_timeout(self, monkeypatch):
        """Test verification handles timeout gracefully (fail open)."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        # Simulate timeout
        import httpx

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch('httpx.AsyncClient', return_value=mock_client):
            # Should fail open (allow request) on timeout
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "test_action")

        # Based on RECAPTCHA.md: "fail open" on timeout
        assert is_valid is True
        assert score == 0.5

    @pytest.mark.asyncio
    async def test_recaptcha_network_error(self, monkeypatch):
        """Test verification handles network errors gracefully."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        # Simulate network error
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(side_effect=Exception("Network error"))

        with patch('httpx.AsyncClient', return_value=mock_client):
            # Should fail open on connection error
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "test_action")

        assert is_valid is True
        assert score == 0.5

    @pytest.mark.asyncio
    async def test_recaptcha_malformed_response(self, monkeypatch):
        """Test verification handles malformed JSON response."""
        monkeypatch.delenv("TESTING", raising=False)
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient', return_value=mock_client):
            is_valid, score = await verify_recaptcha("token", "127.0.0.1", "test_action")

        # Should fail open on malformed response
        assert is_valid is True
        assert score == 0.5


class TestRecaptchaSiteKey:
    """Test reCAPTCHA site key retrieval."""

    def test_get_site_key_returns_key(self, monkeypatch):
        """Test that site key is returned when configured."""
        monkeypatch.setenv("RECAPTCHA_SITE_KEY", "test_site_key_123456789")

        site_key = get_recaptcha_site_key()

        assert site_key == "test_site_key_123456789"

    def test_get_site_key_none_when_not_configured(self, monkeypatch):
        """Test that None is returned when not configured."""
        monkeypatch.delenv("RECAPTCHA_SITE_KEY", raising=False)

        site_key = get_recaptcha_site_key()

        assert site_key is None  # Returns None, not empty string

    def test_get_site_key_in_testing_mode(self, monkeypatch):
        """Test site key still returned in testing mode (for frontend)."""
        monkeypatch.setenv("TESTING", "true")
        monkeypatch.setenv("RECAPTCHA_SITE_KEY", "test_key")

        site_key = get_recaptcha_site_key()

        # Should still return key (frontend needs it)
        assert site_key == "test_key"


class TestRecaptchaMiddleware:
    """Test reCAPTCHA middleware integration."""

    @pytest.mark.asyncio
    async def test_middleware_bypasses_localhost(self):
        """Test that middleware bypasses reCAPTCHA for localhost."""
        from api.utils.recaptcha_middleware import require_recaptcha

        # Create mock request from localhost
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"

        # Should return True (bypass) for localhost
        result = await require_recaptcha(mock_request, x_recaptcha_token=None)
        assert result is True

    @pytest.mark.asyncio
    async def test_middleware_bypasses_non_production(self, monkeypatch):
        """Test that middleware bypasses reCAPTCHA in non-production environments."""
        from api.utils.recaptcha_middleware import require_recaptcha

        # Set non-production environment
        monkeypatch.setenv("ENVIRONMENT", "development")

        # Create mock request
        mock_request = MagicMock()
        mock_request.client.host = "192.168.1.1"

        # Should return True (bypass) in development
        result = await require_recaptcha(mock_request, x_recaptcha_token=None)
        assert result is True

    @pytest.mark.asyncio
    async def test_middleware_rejects_invalid_token_in_production(self, monkeypatch):
        """Test that middleware rejects invalid tokens in production."""
        from fastapi import HTTPException
        from api.utils.recaptcha_middleware import require_recaptcha

        # Disable testing mode (might be set by conftest.py)
        monkeypatch.delenv("TESTING", raising=False)

        # Set production environment
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("RECAPTCHA_SECRET_KEY", "test_secret")

        # Mock httpx to return invalid response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error-codes": ["invalid-input-response"]
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        # Create mock request with invalid token from non-localhost
        mock_request = MagicMock()
        mock_request.client.host = "203.0.113.0"  # Non-localhost IP

        # Should raise HTTPException
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await require_recaptcha(mock_request, x_recaptcha_token="invalid_token")

        assert exc_info.value.status_code == 400
        assert "reCAPTCHA" in exc_info.value.detail
