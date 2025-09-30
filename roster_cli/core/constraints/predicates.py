"""Predicate functions for constraint evaluation."""

from datetime import date, datetime, timedelta

from roster_cli.core.constraints.dsl import EvalContext


def is_day_of_week(ctx: EvalContext, day: str) -> bool:
    """Check if event date is a specific day of week."""
    if not ctx.event or not ctx.date:
        return False
    day_name = ctx.date.strftime("%A")
    return day_name.upper() == day.upper()


def is_long_weekend(ctx: EvalContext) -> bool:
    """Check if event date is part of a long weekend."""
    if not ctx.date or not ctx.holidays:
        return False
    return ctx.holidays.get(ctx.date, False)


def is_friday_or_monday(ctx: EvalContext) -> bool:
    """Check if date is Friday or Monday."""
    if not ctx.date:
        return False
    day = ctx.date.strftime("%A")
    return day in ["Friday", "Monday"]


def overlaps_external(ctx: EvalContext, external_events: list[dict[str, datetime]]) -> bool:
    """Check if event overlaps with external calendar events."""
    if not ctx.event:
        return False

    for ext in external_events:
        if ctx.event.start < ext["end"] and ctx.event.end > ext["start"]:
            return True
    return False


def has_role(ctx: EvalContext, role: str) -> bool:
    """Check if person has specific role."""
    if not ctx.person:
        return False
    return role in ctx.person.roles


def count_assignments_in_period(
    ctx: EvalContext, person_id: str, start: date, end: date
) -> int:
    """Count assignments for person in date range."""
    if not ctx.person_assignments or person_id not in ctx.person_assignments:
        return 0

    count = 0
    for event in ctx.person_assignments[person_id]:
        event_date = event.start.date()
        if start <= event_date <= end:
            count += 1
    return count


def min_gap_hours_satisfied(ctx: EvalContext, person_id: str, min_hours: int) -> bool:
    """Check if minimum gap between assignments is satisfied."""
    if not ctx.person_assignments or person_id not in ctx.person_assignments:
        return True

    events = sorted(ctx.person_assignments[person_id], key=lambda e: e.start)
    for i in range(len(events) - 1):
        gap = (events[i + 1].start - events[i].end).total_seconds() / 3600
        if gap < min_hours:
            return False
    return True


def last_assignment_days_ago(ctx: EvalContext, person_id: str, current_date: date) -> int | None:
    """Get days since last assignment for person."""
    if not ctx.person_assignments or person_id not in ctx.person_assignments:
        return None

    events = ctx.person_assignments[person_id]
    if not events:
        return None

    last_event = max(events, key=lambda e: e.end)
    last_date = last_event.end.date()
    return (current_date - last_date).days
