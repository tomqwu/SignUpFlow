"""
Rate limiting utility to prevent spam and abuse.

Implements a simple token bucket algorithm with in-memory storage.
For production, consider using Redis for distributed rate limiting.
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.

    Thread-safe implementation for handling concurrent requests.
    """

    def __init__(self):
        # Store format: {key: (tokens, last_refill_time)}
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = Lock()

    def is_allowed(
        self,
        key: str,
        max_requests: int = 5,
        window_seconds: int = 60
    ) -> bool:
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

    def reset(self, key: str):
        """Reset rate limit for a specific key."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]

    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Remove old entries to prevent memory bloat.
        Call this periodically (e.g., every hour).
        """
        with self._lock:
            current_time = time.time()
            keys_to_remove = [
                key for key, (_, last_refill) in self._buckets.items()
                if current_time - last_refill > max_age_seconds
            ]
            for key in keys_to_remove:
                del self._buckets[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "signup": {"max_requests": 3, "window_seconds": 3600},  # 3 per hour
    "create_org": {"max_requests": 2, "window_seconds": 3600},  # 2 per hour
    "create_invitation": {"max_requests": 10, "window_seconds": 300},  # 10 per 5 min
    "login": {"max_requests": 5, "window_seconds": 300},  # 5 per 5 min
    "verify_invitation": {"max_requests": 10, "window_seconds": 60},  # 10 per min
}
