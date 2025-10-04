"""
DateTime utilities for proper timezone handling.

Principles:
- Store in UTC (database)
- Display in user's timezone (frontend)
- Use timezone-aware datetimes
- Handle dates separately from datetimes
"""

from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from typing import Optional


def to_user_timezone(utc_datetime: datetime, user_tz: str = "UTC") -> datetime:
    """
    Convert UTC datetime to user's timezone.

    Args:
        utc_datetime: datetime in UTC
        user_tz: Target timezone (e.g., "America/New_York")

    Returns:
        datetime in user's timezone
    """
    if utc_datetime is None:
        return None

    # Ensure datetime is timezone-aware (UTC)
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=ZoneInfo("UTC"))

    # Convert to user's timezone
    return utc_datetime.astimezone(ZoneInfo(user_tz))


def from_user_timezone(user_datetime: datetime, user_tz: str = "UTC") -> datetime:
    """
    Convert user's timezone datetime to UTC for storage.

    Args:
        user_datetime: datetime in user's timezone
        user_tz: Source timezone

    Returns:
        datetime in UTC
    """
    if user_datetime is None:
        return None

    # Ensure datetime is timezone-aware
    if user_datetime.tzinfo is None:
        user_datetime = user_datetime.replace(tzinfo=ZoneInfo(user_tz))

    # Convert to UTC
    return user_datetime.astimezone(ZoneInfo("UTC"))


def parse_date_safe(date_string: str) -> date:
    """
    Parse date string without timezone issues.

    Args:
        date_string: Date string in format "YYYY-MM-DD" or ISO 8601

    Returns:
        date object
    """
    if not date_string:
        return None

    # Handle ISO 8601 format (with T and time component)
    if 'T' in date_string:
        date_string = date_string.split('T')[0]

    # Parse YYYY-MM-DD
    return date.fromisoformat(date_string)


def format_date_for_api(d: date) -> str:
    """
    Format date for API response (ISO 8601 date only).

    Args:
        d: date object

    Returns:
        "YYYY-MM-DD" string
    """
    if d is None:
        return None

    return d.isoformat()


def format_datetime_for_api(dt: datetime) -> str:
    """
    Format datetime for API response (ISO 8601 with timezone).

    Args:
        dt: datetime object

    Returns:
        ISO 8601 string with timezone (e.g., "2025-10-11T14:00:00Z")
    """
    if dt is None:
        return None

    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.isoformat()


def parse_datetime_safe(datetime_string: str) -> datetime:
    """
    Parse datetime string to timezone-aware datetime.

    Args:
        datetime_string: ISO 8601 datetime string

    Returns:
        timezone-aware datetime in UTC
    """
    if not datetime_string:
        return None

    # Parse ISO format
    dt = datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))

    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    else:
        dt = dt.astimezone(ZoneInfo("UTC"))

    return dt


def is_date_in_range(check_date: date, start_date: date, end_date: date) -> bool:
    """
    Check if a date falls within a range (inclusive).

    Args:
        check_date: Date to check
        start_date: Range start
        end_date: Range end

    Returns:
        True if date is in range
    """
    return start_date <= check_date <= end_date


def get_common_timezones() -> list[dict]:
    """
    Get list of common timezones for selector UI.

    Returns:
        List of {value, label, offset} dicts
    """
    return [
        # US & Canada
        {"value": "America/New_York", "label": "Eastern Time (ET)", "region": "US & Canada"},
        {"value": "America/Chicago", "label": "Central Time (CT)", "region": "US & Canada"},
        {"value": "America/Denver", "label": "Mountain Time (MT)", "region": "US & Canada"},
        {"value": "America/Los_Angeles", "label": "Pacific Time (PT)", "region": "US & Canada"},
        {"value": "America/Anchorage", "label": "Alaska Time (AKT)", "region": "US & Canada"},
        {"value": "Pacific/Honolulu", "label": "Hawaii Time (HT)", "region": "US & Canada"},

        # Europe
        {"value": "Europe/London", "label": "London (GMT/BST)", "region": "Europe"},
        {"value": "Europe/Paris", "label": "Paris (CET/CEST)", "region": "Europe"},
        {"value": "Europe/Berlin", "label": "Berlin (CET/CEST)", "region": "Europe"},
        {"value": "Europe/Moscow", "label": "Moscow (MSK)", "region": "Europe"},

        # Asia
        {"value": "Asia/Dubai", "label": "Dubai (GST)", "region": "Asia"},
        {"value": "Asia/Kolkata", "label": "India (IST)", "region": "Asia"},
        {"value": "Asia/Shanghai", "label": "China (CST)", "region": "Asia"},
        {"value": "Asia/Tokyo", "label": "Japan (JST)", "region": "Asia"},
        {"value": "Asia/Seoul", "label": "South Korea (KST)", "region": "Asia"},
        {"value": "Asia/Singapore", "label": "Singapore (SGT)", "region": "Asia"},

        # Australia
        {"value": "Australia/Sydney", "label": "Sydney (AEDT/AEST)", "region": "Australia"},
        {"value": "Australia/Melbourne", "label": "Melbourne (AEDT/AEST)", "region": "Australia"},
        {"value": "Australia/Brisbane", "label": "Brisbane (AEST)", "region": "Australia"},
        {"value": "Australia/Perth", "label": "Perth (AWST)", "region": "Australia"},

        # Other
        {"value": "UTC", "label": "UTC (Coordinated Universal Time)", "region": "Other"},
    ]


# Example usage and tests
if __name__ == "__main__":
    # Test date parsing (no timezone issues)
    print("=== Date Parsing Tests ===")
    test_date = parse_date_safe("2025-10-11")
    print(f"Parsed date: {test_date}")  # 2025-10-11
    print(f"Formatted: {format_date_for_api(test_date)}")  # 2025-10-11

    # Test datetime timezone conversion
    print("\n=== DateTime Timezone Tests ===")
    utc_time = datetime(2025, 10, 11, 14, 0, tzinfo=ZoneInfo("UTC"))
    print(f"UTC time: {utc_time}")

    ny_time = to_user_timezone(utc_time, "America/New_York")
    print(f"New York time: {ny_time}")  # Should be 9-10 AM depending on DST

    tokyo_time = to_user_timezone(utc_time, "Asia/Tokyo")
    print(f"Tokyo time: {tokyo_time}")  # Should be 11 PM

    # Test date range check
    print("\n=== Date Range Test ===")
    check_date = date(2025, 10, 11)
    start = date(2025, 10, 10)
    end = date(2025, 10, 12)
    in_range = is_date_in_range(check_date, start, end)
    print(f"Is {check_date} in range {start} to {end}? {in_range}")  # True
