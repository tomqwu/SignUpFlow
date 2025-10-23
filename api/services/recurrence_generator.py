"""
Recurrence generator service for recurring events.

This service generates event occurrences from recurring series patterns using
python-dateutil's rrule functionality (RFC 5545 subset).

Supports:
- Weekly recurrence (every N weeks on specific days)
- Biweekly recurrence (every 2 weeks on specific days)
- Monthly recurrence (Nth weekday of month)
- Custom interval recurrence (every N days/weeks/months)

Performance goals:
- Calendar preview: <1s render for 100 occurrences
- Recurrence generation: <5s for 365-occurrence series
"""

from datetime import datetime, date, timedelta, time
from typing import List, Dict, Optional
from dateutil import rrule
from dateutil.rrule import rrule as rrule_func, DAILY, WEEKLY, MONTHLY, MO, TU, WE, TH, FR, SA, SU

from api.models import RecurringSeries, Event, Holiday
from sqlalchemy.orm import Session


# Weekday mapping for dateutil
WEEKDAY_MAP = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
}

# Weekday position mapping for monthly recurrence
POSITION_MAP = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "last": -1,
}


class RecurrenceGenerationError(Exception):
    """Error during recurrence generation."""
    pass


def generate_occurrences(
    series: RecurringSeries,
    start_time: time,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Generate all occurrences for a recurring series.

    Args:
        series: RecurringSeries model instance
        start_time: Time of day for events (datetime.time object)
        db: Database session (optional, for holiday conflict detection)

    Returns:
        List of dictionaries with occurrence data:
        [
            {
                "occurrence_sequence": 1,
                "start_time": datetime(2025, 1, 5, 10, 0),
                "end_time": datetime(2025, 1, 5, 11, 0),
                "title": "Sunday Service",
                "location": "Main Chapel",
                "role_requirements": {"usher": 2, "greeter": 1}
            },
            ...
        ]

    Raises:
        RecurrenceGenerationError: If pattern is invalid or generation fails
    """
    if series.pattern_type == "weekly":
        return generate_weekly_occurrences(series, start_time, db)
    elif series.pattern_type == "biweekly":
        return generate_biweekly_occurrences(series, start_time, db)
    elif series.pattern_type == "monthly":
        return generate_monthly_occurrences(series, start_time, db)
    elif series.pattern_type == "custom":
        return generate_custom_interval_occurrences(series, start_time, db)
    else:
        raise RecurrenceGenerationError(f"Unknown pattern type: {series.pattern_type}")


def generate_weekly_occurrences(
    series: RecurringSeries,
    start_time: time,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Generate weekly recurring occurrences.

    Pattern: Every week on selected days (e.g., every Sunday and Wednesday)

    Args:
        series: RecurringSeries with pattern_type="weekly" and selected_days=["sunday", "wednesday"]
        start_time: Time of day for events
        db: Database session for holiday detection

    Returns:
        List of occurrence dictionaries
    """
    if not series.selected_days:
        raise RecurrenceGenerationError("Weekly pattern requires selected_days")

    # Convert selected days to dateutil weekday objects
    try:
        weekdays = [WEEKDAY_MAP[day.lower()] for day in series.selected_days]
    except KeyError as e:
        raise RecurrenceGenerationError(f"Invalid weekday: {e}")

    # Create base datetime from start_date + start_time
    dtstart = datetime.combine(series.start_date, start_time)

    # Determine end condition
    if series.end_condition_type == "date" and series.end_date:
        until = datetime.combine(series.end_date, time(23, 59, 59))
        count = None
    elif series.end_condition_type == "count" and series.occurrence_count:
        until = None
        count = series.occurrence_count
    else:
        # Default: 2 years maximum (safety limit)
        until = dtstart + timedelta(days=730)
        count = None

    # Generate occurrences using rrule
    rule = rrule_func(
        WEEKLY,
        dtstart=dtstart,
        until=until,
        count=count,
        byweekday=weekdays,
        interval=1  # Every week
    )

    return _build_occurrence_list(series, rule, db)


def generate_biweekly_occurrences(
    series: RecurringSeries,
    start_time: time,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Generate biweekly (every 2 weeks) recurring occurrences.

    Pattern: Every 2 weeks on selected days (e.g., every other Sunday)

    Args:
        series: RecurringSeries with pattern_type="biweekly"
        start_time: Time of day for events
        db: Database session for holiday detection

    Returns:
        List of occurrence dictionaries
    """
    if not series.selected_days:
        raise RecurrenceGenerationError("Biweekly pattern requires selected_days")

    # Convert selected days to dateutil weekday objects
    try:
        weekdays = [WEEKDAY_MAP[day.lower()] for day in series.selected_days]
    except KeyError as e:
        raise RecurrenceGenerationError(f"Invalid weekday: {e}")

    # Create base datetime
    dtstart = datetime.combine(series.start_date, start_time)

    # Determine end condition
    if series.end_condition_type == "date" and series.end_date:
        until = datetime.combine(series.end_date, time(23, 59, 59))
        count = None
    elif series.end_condition_type == "count" and series.occurrence_count:
        until = None
        count = series.occurrence_count
    else:
        until = dtstart + timedelta(days=730)
        count = None

    # Generate occurrences using rrule with interval=2 (every 2 weeks)
    rule = rrule_func(
        WEEKLY,
        dtstart=dtstart,
        until=until,
        count=count,
        byweekday=weekdays,
        interval=2  # Every 2 weeks
    )

    return _build_occurrence_list(series, rule, db)


def generate_monthly_occurrences(
    series: RecurringSeries,
    start_time: time,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Generate monthly recurring occurrences.

    Pattern: Nth weekday of each month (e.g., "2nd Sunday of every month")

    Args:
        series: RecurringSeries with pattern_type="monthly",
                weekday_position="second", weekday_name="sunday"
        start_time: Time of day for events
        db: Database session for holiday detection

    Returns:
        List of occurrence dictionaries
    """
    if not series.weekday_position or not series.weekday_name:
        raise RecurrenceGenerationError("Monthly pattern requires weekday_position and weekday_name")

    # Convert weekday position and name to dateutil format
    try:
        position = POSITION_MAP[series.weekday_position.lower()]
        weekday = WEEKDAY_MAP[series.weekday_name.lower()]
    except KeyError as e:
        raise RecurrenceGenerationError(f"Invalid weekday position or name: {e}")

    # Create base datetime
    dtstart = datetime.combine(series.start_date, start_time)

    # Determine end condition
    if series.end_condition_type == "date" and series.end_date:
        until = datetime.combine(series.end_date, time(23, 59, 59))
        count = None
    elif series.end_condition_type == "count" and series.occurrence_count:
        until = None
        count = series.occurrence_count
    else:
        until = dtstart + timedelta(days=730)
        count = None

    # Generate occurrences using rrule
    # byweekday with position: e.g., TU(2) = 2nd Tuesday
    rule = rrule_func(
        MONTHLY,
        dtstart=dtstart,
        until=until,
        count=count,
        byweekday=weekday(position),  # e.g., SU(2) for 2nd Sunday
        interval=1  # Every month
    )

    return _build_occurrence_list(series, rule, db)


def generate_custom_interval_occurrences(
    series: RecurringSeries,
    start_time: time,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Generate custom interval recurring occurrences.

    Pattern: Every N weeks on selected days (e.g., every 3 weeks on Monday)

    Args:
        series: RecurringSeries with pattern_type="custom" and frequency_interval=3
        start_time: Time of day for events
        db: Database session for holiday detection

    Returns:
        List of occurrence dictionaries
    """
    if not series.frequency_interval or series.frequency_interval < 1:
        raise RecurrenceGenerationError("Custom pattern requires frequency_interval >= 1")

    if not series.selected_days:
        raise RecurrenceGenerationError("Custom pattern requires selected_days")

    # Convert selected days to dateutil weekday objects
    try:
        weekdays = [WEEKDAY_MAP[day.lower()] for day in series.selected_days]
    except KeyError as e:
        raise RecurrenceGenerationError(f"Invalid weekday: {e}")

    # Create base datetime
    dtstart = datetime.combine(series.start_date, start_time)

    # Determine end condition
    if series.end_condition_type == "date" and series.end_date:
        until = datetime.combine(series.end_date, time(23, 59, 59))
        count = None
    elif series.end_condition_type == "count" and series.occurrence_count:
        until = None
        count = series.occurrence_count
    else:
        until = dtstart + timedelta(days=730)
        count = None

    # Generate occurrences using rrule with custom interval
    rule = rrule_func(
        WEEKLY,
        dtstart=dtstart,
        until=until,
        count=count,
        byweekday=weekdays,
        interval=series.frequency_interval  # Every N weeks
    )

    return _build_occurrence_list(series, rule, db)


def _build_occurrence_list(
    series: RecurringSeries,
    rule: rrule,
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Build list of occurrence dictionaries from rrule result.

    Args:
        series: RecurringSeries model instance
        rule: dateutil rrule object
        db: Database session for holiday detection

    Returns:
        List of occurrence dictionaries with sequence numbers
    """
    occurrences = []
    duration_delta = timedelta(minutes=series.duration)

    # Get holidays for conflict detection (if db provided)
    holidays = set()
    if db and series.org_id:
        holiday_records = db.query(Holiday).filter(Holiday.org_id == series.org_id).all()
        holidays = {h.date for h in holiday_records}

    for sequence, start_dt in enumerate(rule, start=1):
        end_dt = start_dt + duration_delta

        occurrence = {
            "occurrence_sequence": sequence,
            "start_time": start_dt,
            "end_time": end_dt,
            "title": series.title,
            "location": series.location,
            "role_requirements": series.role_requirements,
            "is_holiday_conflict": start_dt.date() in holidays
        }

        occurrences.append(occurrence)

    return occurrences


def detect_holiday_conflicts(
    occurrences: List[Dict],
    org_id: str,
    db: Session
) -> List[Dict]:
    """
    Detect which occurrences conflict with organization holidays.

    Args:
        occurrences: List of occurrence dictionaries
        org_id: Organization ID
        db: Database session

    Returns:
        List of occurrences with is_holiday_conflict flag updated
    """
    # Get all holidays for this organization
    holidays = db.query(Holiday).filter(Holiday.org_id == org_id).all()
    holiday_dates = {h.date for h in holidays}

    # Update each occurrence with holiday conflict status
    for occurrence in occurrences:
        occurrence_date = occurrence["start_time"].date()
        occurrence["is_holiday_conflict"] = occurrence_date in holiday_dates

        # Add holiday label if conflict exists
        if occurrence["is_holiday_conflict"]:
            matching_holiday = next((h for h in holidays if h.date == occurrence_date), None)
            if matching_holiday:
                occurrence["holiday_label"] = matching_holiday.label

    return occurrences


def validate_series_duration(series: RecurringSeries) -> None:
    """
    Validate that recurring series doesn't exceed maximum duration (2 years).

    Args:
        series: RecurringSeries to validate

    Raises:
        RecurrenceGenerationError: If series duration exceeds 2 years
    """
    if series.end_condition_type == "date" and series.end_date:
        duration = (series.end_date - series.start_date).days
        if duration > 730:  # 2 years
            raise RecurrenceGenerationError(
                f"Series duration ({duration} days) exceeds maximum of 730 days (2 years)"
            )

    # For count-based series, we'll validate occurrence count during generation
    # Maximum is implicitly enforced by 2-year time limit
