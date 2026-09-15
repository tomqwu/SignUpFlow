"""
Rate limiting utility to prevent spam and abuse.

Development uses a process-local token bucket. Production uses an atomic Redis
counter so every application worker shares the same quota.

Configuration via environment variables:
- RATE_LIMIT_SIGNUP_MAX: Max signup requests (default: 3)
- RATE_LIMIT_SIGNUP_WINDOW: Signup window in seconds (default: 3600)
- RATE_LIMIT_LOGIN_MAX: Max login requests (default: 5)
- RATE_LIMIT_LOGIN_WINDOW: Login window in seconds (default: 300)
- RATE_LIMIT_CREATE_ORG_MAX: Max create org requests (default: 2)
- RATE_LIMIT_CREATE_ORG_WINDOW: Create org window in seconds (default: 3600)
- RATE_LIMIT_CREATE_INVITATION_MAX: Max create invitation requests (default: 10)
- RATE_LIMIT_CREATE_INVITATION_WINDOW: Create invitation window in seconds (default: 300)
- RATE_LIMIT_VERIFY_INVITATION_MAX: Max verify invitation requests (default: 10)
- RATE_LIMIT_VERIFY_INVITATION_WINDOW: Verify invitation window in seconds (default: 60)
"""

import hashlib
import math
import os
import time
from threading import Lock
from typing import Any

from redis import Redis
from redis.exceptions import RedisError


class RateLimitBackendUnavailableError(RuntimeError):
    """Raised when a required shared rate-limit backend cannot be used."""


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.

    Thread-safe implementation for handling concurrent requests.
    """

    def __init__(self) -> None:
        # Store format: {key: (tokens, last_refill_time)}
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
        """
        Check if a request is allowed based on rate limit.

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self._lock:
            current_time = time.time()

            if key not in self._buckets:
                # First request - initialize bucket
                self._buckets[key] = (max_requests - 1, current_time)
                return True

            tokens, last_refill = self._buckets[key]

            # Calculate token refill
            time_passed = current_time - last_refill
            refill_rate = max_requests / window_seconds
            tokens_to_add = time_passed * refill_rate

            # Update token count (cap at max_requests)
            new_tokens = min(max_requests, tokens + tokens_to_add)

            if new_tokens >= 1:
                # Request allowed - consume one token
                self._buckets[key] = (new_tokens - 1, current_time)
                return True
            else:
                # Rate limit exceeded
                self._buckets[key] = (new_tokens, current_time)
                return False

    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]

    def cleanup_old_entries(self, max_age_seconds: int = 3600) -> None:
        """
        Remove old entries to prevent memory bloat.
        Call this periodically (e.g., every hour).
        """
        with self._lock:
            current_time = time.time()
            keys_to_remove = [
                key
                for key, (_, last_refill) in self._buckets.items()
                if current_time - last_refill > max_age_seconds
            ]
            for key in keys_to_remove:
                del self._buckets[key]


class RedisRateLimiter:
    """Fixed-window limiter backed by one atomic Redis script."""

    _SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
if current <= tonumber(ARGV[2]) then
  return 1
end
return 0
"""

    def __init__(
        self,
        url: str | None = None,
        *,
        client: Any | None = None,
        namespace: str = "signupflow:rate-limit",
    ) -> None:
        if client is None and not url:
            raise ValueError("A Redis URL or client is required")
        self._client = client
        self._url = url
        self._namespace = namespace

    def _get_client(self) -> Any:
        if self._client is None:
            assert self._url is not None
            try:
                self._client = Redis.from_url(
                    self._url,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                )
            except (OSError, RedisError, ValueError) as exc:
                raise RateLimitBackendUnavailableError(
                    "Shared rate-limit storage is unavailable"
                ) from exc
        return self._client

    def _storage_key(self, key: str) -> str:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return f"{self._namespace}:{digest}"

    def is_allowed(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
        window = max(1, math.ceil(window_seconds))
        try:
            result = self._get_client().eval(
                self._SCRIPT,
                1,
                self._storage_key(key),
                window,
                max_requests,
            )
        except (OSError, RedisError) as exc:
            raise RateLimitBackendUnavailableError(
                "Shared rate-limit storage is unavailable"
            ) from exc
        return bool(result)

    def reset(self, key: str) -> None:
        try:
            self._get_client().delete(self._storage_key(key))
        except (OSError, RedisError) as exc:
            raise RateLimitBackendUnavailableError(
                "Shared rate-limit storage is unavailable"
            ) from exc


class ConfiguredRateLimiter:
    """Choose process-local or shared storage from the runtime environment."""

    def __init__(self) -> None:
        self._memory = RateLimiter()
        self._redis_limiters: dict[str, RedisRateLimiter] = {}
        self._lock = Lock()

    def _backend(self) -> RateLimiter | RedisRateLimiter:
        environment = os.getenv("ENVIRONMENT", "development").strip().lower()
        storage = os.getenv("RATE_LIMIT_STORAGE", "").strip().lower()
        use_redis = storage == "redis" or environment == "production"
        if not use_redis:
            return self._memory

        url = os.getenv("RATE_LIMIT_REDIS_URL") or os.getenv("REDIS_URL")
        if not url:
            raise RateLimitBackendUnavailableError(
                "Production rate limiting requires RATE_LIMIT_REDIS_URL or REDIS_URL"
            )
        with self._lock:
            limiter = self._redis_limiters.get(url)
            if limiter is None:
                limiter = RedisRateLimiter(url)
                self._redis_limiters[url] = limiter
        return limiter

    def is_allowed(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
        return self._backend().is_allowed(key, max_requests, window_seconds)

    def reset(self, key: str) -> None:
        self._memory.reset(key)
        for limiter in self._redis_limiters.values():
            limiter.reset(key)

    def cleanup_old_entries(self, max_age_seconds: int = 3600) -> None:
        self._memory.cleanup_old_entries(max_age_seconds)


# Global environment-aware limiter used by route dependencies.
rate_limiter = ConfiguredRateLimiter()


def get_env_int(key: str, default: int) -> int:
    """Get integer value from environment variable with default."""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


# Rate limit configurations for different endpoints
# Values can be overridden via environment variables
RATE_LIMITS = {
    "signup": {
        "max_requests": get_env_int("RATE_LIMIT_SIGNUP_MAX", 3),
        "window_seconds": get_env_int("RATE_LIMIT_SIGNUP_WINDOW", 3600),
    },
    "create_org": {
        "max_requests": get_env_int("RATE_LIMIT_CREATE_ORG_MAX", 2),
        "window_seconds": get_env_int("RATE_LIMIT_CREATE_ORG_WINDOW", 3600),
    },
    "create_invitation": {
        "max_requests": get_env_int("RATE_LIMIT_CREATE_INVITATION_MAX", 10),
        "window_seconds": get_env_int("RATE_LIMIT_CREATE_INVITATION_WINDOW", 300),
    },
    "login": {
        "max_requests": get_env_int("RATE_LIMIT_LOGIN_MAX", 5),
        "window_seconds": get_env_int("RATE_LIMIT_LOGIN_WINDOW", 300),
    },
    "verify_invitation": {
        "max_requests": get_env_int("RATE_LIMIT_VERIFY_INVITATION_MAX", 10),
        "window_seconds": get_env_int("RATE_LIMIT_VERIFY_INVITATION_WINDOW", 60),
    },
    "password_reset": {
        "max_requests": get_env_int("RATE_LIMIT_PASSWORD_RESET_MAX", 3),
        "window_seconds": get_env_int("RATE_LIMIT_PASSWORD_RESET_WINDOW", 3600),
    },
    "password_reset_confirm": {
        "max_requests": get_env_int("RATE_LIMIT_PASSWORD_RESET_CONFIRM_MAX", 5),
        "window_seconds": get_env_int("RATE_LIMIT_PASSWORD_RESET_CONFIRM_WINDOW", 300),
    },
    "refresh_token": {
        "max_requests": get_env_int("RATE_LIMIT_REFRESH_TOKEN_MAX", 60),
        "window_seconds": get_env_int("RATE_LIMIT_REFRESH_TOKEN_WINDOW", 3600),
    },
}
