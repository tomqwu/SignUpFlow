"""
Quiet hours enforcement for SMS notifications.

Prevents SMS during sleep hours (10pm-8am local time) unless urgent.
Uses volunteer's timezone from sms_preferences table.
"""

from datetime import datetime, time, timedelta
from typing import Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class QuietHours:
    """Quiet hours checker for SMS notifications."""

    def __init__(self):
        """Initialize quiet hours configuration."""
        self.quiet_start = time(22, 0)  # 10:00 PM
        self.quiet_end = time(8, 0)  # 8:00 AM

    def is_quiet_hours(
        self, timezone: str, is_urgent: bool = False
    ) -> Tuple[bool, str]:
        """
        Check if current time is within quiet hours for timezone.

        Args:
            timezone: Timezone string (e.g., "America/Toronto", "UTC")
            is_urgent: If True, bypasses quiet hours

        Returns:
            Tuple of (is_quiet: bool, reason: str)
            - is_quiet: True if in quiet hours and should not send
            - reason: Explanation for quiet hours status
        """
        if is_urgent:
            return (False, "Urgent message bypasses quiet hours")

        try:
            tz = ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo("UTC")
            timezone = "UTC"

        # Get current time in volunteer's timezone
        now_local = datetime.now(tz).time()

        # Check if in quiet hours
        if self._is_between(now_local, self.quiet_start, self.quiet_end):
            return (
                True,
                f"Quiet hours (10pm-8am) in {timezone}. Current time: {now_local.strftime('%I:%M %p')}",
            )

        return (False, "Outside quiet hours")

    def get_next_send_time(self, timezone: str) -> datetime:
        """
        Calculate next time message can be sent (after quiet hours).

        Args:
            timezone: Timezone string

        Returns:
            datetime when message can be sent (8am in volunteer's timezone)
        """
        try:
            tz = ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo("UTC")

        now_local = datetime.now(tz)
        now_time = now_local.time()

        # If before 8am, send at 8am today
        if now_time < self.quiet_end:
            next_send = now_local.replace(
                hour=self.quiet_end.hour,
                minute=self.quiet_end.minute,
                second=0,
                microsecond=0,
            )
        # If after 10pm, send at 8am tomorrow
        elif now_time >= self.quiet_start:
            next_send = now_local.replace(
                hour=self.quiet_end.hour,
                minute=self.quiet_end.minute,
                second=0,
                microsecond=0,
            )
            next_send = next_send + timedelta(days=1)
        # Otherwise send now
        else:
            next_send = now_local

        return next_send

    def _is_between(
        self, current: time, start: time, end: time
    ) -> bool:
        """
        Check if current time is between start and end times.
        Handles overnight ranges (e.g., 10pm-8am).

        Args:
            current: Current time to check
            start: Start of quiet hours (e.g., 10pm)
            end: End of quiet hours (e.g., 8am)

        Returns:
            True if current time is in quiet hours range
        """
        if start < end:
            # Normal range (e.g., 8am-10pm)
            return start <= current < end
        else:
            # Overnight range (e.g., 10pm-8am)
            return current >= start or current < end
