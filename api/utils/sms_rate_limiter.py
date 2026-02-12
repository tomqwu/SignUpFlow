"""
SMS-specific rate limiting using Redis.

Prevents SMS spam by enforcing:
- Max 3 SMS per volunteer per day (non-urgent)
- Urgent messages bypass rate limits
- Redis-backed counters with 24-hour expiration
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
import redis


class SmsRateLimiter:
    """Redis-based rate limiter for SMS messages."""

    def __init__(self):
        """Initialize Redis connection."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except (redis.ConnectionError, redis.RedisError) as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

        self.max_sms_per_day = 3  # Non-urgent messages limit

    def check_rate_limit(
        self, person_id: int, is_urgent: bool = False
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if person has exceeded daily SMS rate limit.

        Args:
            person_id: Person ID to check
            is_urgent: If True, bypasses rate limit

        Returns:
            Tuple of (allowed: bool, remaining_count: Optional[int])
            - allowed: True if message can be sent
            - remaining_count: How many messages remaining (None if urgent)
        """
        if is_urgent:
            return (True, None)  # Urgent messages bypass rate limit

        key = f"sms_rate_limit:person:{person_id}"
        current_count = self.redis_client.get(key)

        if current_count is None:
            # No messages sent yet today
            return (True, self.max_sms_per_day - 1)

        count = int(current_count)
        if count >= self.max_sms_per_day:
            return (False, 0)  # Rate limit exceeded

        return (True, self.max_sms_per_day - count - 1)

    def increment_count(self, person_id: int, is_urgent: bool = False) -> int:
        """
        Increment SMS count for person.

        Args:
            person_id: Person ID
            is_urgent: If True, doesn't increment counter

        Returns:
            New count (0 if urgent)
        """
        if is_urgent:
            return 0  # Don't track urgent messages

        key = f"sms_rate_limit:person:{person_id}"
        new_count = self.redis_client.incr(key)

        # Set expiration to midnight (24 hours from now)
        if new_count == 1:
            # First message today - set expiration
            seconds_until_midnight = self._seconds_until_midnight()
            self.redis_client.expire(key, seconds_until_midnight)

        return new_count

    def get_remaining_count(self, person_id: int) -> int:
        """
        Get remaining SMS count for person today.

        Args:
            person_id: Person ID

        Returns:
            Remaining messages (0-3)
        """
        key = f"sms_rate_limit:person:{person_id}"
        current_count = self.redis_client.get(key)

        if current_count is None:
            return self.max_sms_per_day

        count = int(current_count)
        remaining = max(0, self.max_sms_per_day - count)
        return remaining

    def reset_count(self, person_id: int) -> None:
        """
        Reset SMS count for person (admin override).

        Args:
            person_id: Person ID
        """
        key = f"sms_rate_limit:person:{person_id}"
        self.redis_client.delete(key)

    def _seconds_until_midnight(self) -> int:
        """Calculate seconds until midnight for expiration."""
        from api.timeutils import utcnow
        now = utcnow()
        midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        delta = midnight - now
        return int(delta.total_seconds())
