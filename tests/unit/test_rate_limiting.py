"""Tests for rate limiting functionality."""

import pytest
import os
from fastapi import Request, HTTPException
from api.utils.rate_limiter import RateLimiter, rate_limiter
from api.utils.rate_limit_middleware import rate_limit, get_client_ip


class TestRateLimiter:
    """Test the core RateLimiter class."""

    def test_allows_requests_within_limit(self):
        """Test that requests within the limit are allowed."""
        limiter = RateLimiter()
        key = "test_user_1"

        # First 5 requests should be allowed
        for i in range(5):
            assert limiter.is_allowed(key, max_requests=5, window_seconds=60), f"Request {i+1} should be allowed"

    def test_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked."""
        limiter = RateLimiter()
        key = "test_user_2"

        # Allow 3 requests
        for i in range(3):
            assert limiter.is_allowed(key, max_requests=3, window_seconds=60)

        # 4th request should be blocked
        assert not limiter.is_allowed(key, max_requests=3, window_seconds=60), "4th request should be blocked"

    def test_resets_after_window(self):
        """Test that rate limit resets after window expires."""
        limiter = RateLimiter()
        key = "test_user_3"

        # Use a very short window for testing
        assert limiter.is_allowed(key, max_requests=2, window_seconds=0.1)
        assert limiter.is_allowed(key, max_requests=2, window_seconds=0.1)

        # Should be blocked immediately
        assert not limiter.is_allowed(key, max_requests=2, window_seconds=0.1)

        # Wait for window to expire
        import time
        time.sleep(0.15)

        # Should be allowed again
        assert limiter.is_allowed(key, max_requests=2, window_seconds=0.1), "Should be allowed after window expires"

    def test_different_keys_independent(self):
        """Test that different keys have independent rate limits."""
        limiter = RateLimiter()

        # Max out user1's limit
        for i in range(3):
            assert limiter.is_allowed("user1", max_requests=3, window_seconds=60)

        # user1 should be blocked
        assert not limiter.is_allowed("user1", max_requests=3, window_seconds=60)

        # But user2 should still be allowed
        assert limiter.is_allowed("user2", max_requests=3, window_seconds=60), "user2 should have independent limit"

    def test_reset_key(self):
        """Test that reset() clears the rate limit for a key."""
        limiter = RateLimiter()
        key = "test_user_4"

        # Max out the limit
        for i in range(3):
            assert limiter.is_allowed(key, max_requests=3, window_seconds=60)

        # Should be blocked
        assert not limiter.is_allowed(key, max_requests=3, window_seconds=60)

        # Reset the key
        limiter.reset(key)

        # Should be allowed again
        assert limiter.is_allowed(key, max_requests=3, window_seconds=60), "Should be allowed after reset"

    def test_cleanup_old_entries(self):
        """Test that cleanup removes old entries."""
        limiter = RateLimiter()

        # Create some entries
        limiter.is_allowed("old_user", max_requests=5, window_seconds=60)

        # Verify entry exists
        assert "old_user" in limiter._buckets

        # Cleanup with very short max_age (0.1 seconds)
        import time
        time.sleep(0.15)
        limiter.cleanup_old_entries(max_age_seconds=0.1)

        # Entry should be removed
        assert "old_user" not in limiter._buckets


class TestRateLimitMiddleware:
    """Test the FastAPI rate limit middleware."""

    def test_get_client_ip_from_direct_connection(self):
        """Test extracting IP from direct connection."""
        # Create a mock request
        class MockClient:
            host = "192.168.1.100"

        class MockRequest:
            client = MockClient()
            headers = {}

        request = MockRequest()
        ip = get_client_ip(request)
        assert ip == "192.168.1.100"

    def test_get_client_ip_from_forwarded_header(self):
        """Test extracting IP from X-Forwarded-For header."""
        class MockRequest:
            client = None
            headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}

        request = MockRequest()
        ip = get_client_ip(request)
        # Should get the first IP in the chain
        assert ip == "203.0.113.1"

    def test_rate_limit_disabled_during_tests(self):
        """Test that rate limiting is disabled when TESTING=true."""
        # TESTING should already be set by pytest_configure
        assert os.getenv("TESTING") == "true"

        # Create mock request
        class MockClient:
            host = "127.0.0.1"

        class MockRequest:
            client = MockClient()
            headers = {}

        # Rate limit function should return True during tests
        check_fn = rate_limit("signup")
        request = MockRequest()

        # Should not raise exception even after many calls
        for i in range(100):
            result = check_fn(request)
            assert result is True, "Rate limiting should be disabled during tests"


class TestRateLimitProduction:
    """Test rate limiting behavior in production mode."""

    def test_rate_limit_enforced_in_production(self):
        """Test that rate limits are enforced when TESTING is not set."""
        # Temporarily unset TESTING
        original_testing = os.getenv("TESTING")
        if "TESTING" in os.environ:
            del os.environ["TESTING"]

        try:
            class MockClient:
                host = "192.168.1.1"

            class MockRequest:
                client = MockClient()
                headers = {}

            # Clear any existing rate limit state for this IP
            rate_limiter.reset("signup:192.168.1.1")

            check_fn = rate_limit("signup")
            request = MockRequest()

            # First 3 requests should succeed (signup limit is 3 per hour)
            for i in range(3):
                result = check_fn(request)
                assert result is True, f"Request {i+1} should be allowed"

            # 4th request should raise 429
            with pytest.raises(HTTPException) as exc_info:
                check_fn(request)

            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in exc_info.value.detail

        finally:
            # Restore TESTING environment variable
            if original_testing:
                os.environ["TESTING"] = original_testing
            else:
                os.environ.pop("TESTING", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
