"""Time and date utilities including RRULE parsing helpers."""

from datetime import date, datetime, timedelta
from typing import Iterator

from dateutil import rrule


def parse_rrule(rrule_str: str, dtstart: datetime, until: datetime) -> Iterator[datetime]:
    """Parse RRULE string and generate occurrences."""
    rule = rrule.rrulestr(rrule_str, dtstart=dtstart)
    return rule.between(dtstart, until, inc=True)


def date_range(start: date, end: date) -> Iterator[date]:
    """Generate all dates in range inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def is_date_in_range(check: date, start: date, end: date) -> bool:
    """Check if date falls within range inclusive."""
    return start <= check <= end


def get_day_of_week(d: date) -> str:
    """Get day of week as string (Monday, Tuesday, etc.)."""
    return d.strftime("%A")


def is_long_weekend_day(d: date, holidays: dict[date, bool]) -> bool:
    """Check if date is part of a long weekend."""
    return holidays.get(d, False)
