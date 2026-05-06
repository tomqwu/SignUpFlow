"""Unit tests: solver honors rrule-expanded blocks and AvailabilityException dates.

Sprint 3-E hooked up VacationPeriod ranges. Sprint 5-4 extends the solver to also
honor:
- Availability.rrule (e.g. FREQ=WEEKLY;BYDAY=MO blocks every Monday)
- AvailabilityException single-date rows

This is a unit test on the GreedyHeuristicSolver — no FastAPI / DB layer.
"""

from datetime import date, datetime, timedelta

from api.core.models import (
    Availability,
    Event,
    Org,
    OrgDefaults,
    Person,
    RequiredRole,
)
from api.core.solver.adapter import SolveContext
from api.core.solver.heuristics import GreedyHeuristicSolver


def _ctx_with(
    *,
    people: list[Person],
    events: list[Event],
    availability: list[Availability],
    from_date: date,
    to_date: date,
) -> SolveContext:
    return SolveContext(
        org=Org(org_id="t-org", region="US", defaults=OrgDefaults()),
        people=people,
        teams=[],
        resources=[],
        events=events,
        constraints=[],
        availability=availability,
        holidays=[],
        from_date=from_date,
        to_date=to_date,
        mode="strict",
        change_min=False,
    )


def _solve(ctx: SolveContext):
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    return solver.solve()


def _person(pid: str) -> Person:
    return Person(id=pid, name=pid, roles=["volunteer"], skills=[], teams=[])


def _event(eid: str, on: date, *, count: int = 1) -> Event:
    return Event(
        id=eid,
        type="service",
        start=datetime.combine(on, datetime.min.time().replace(hour=10)),
        end=datetime.combine(on, datetime.min.time().replace(hour=11)),
        required_roles=[RequiredRole(role="volunteer", count=count)],
    )


def test_weekly_rrule_blocks_matching_weekday():
    """A volunteer with FREQ=WEEKLY;BYDAY=MO is not assigned to Monday events."""
    monday = date(2026, 5, 4)  # Monday
    next_tue = monday + timedelta(days=1)
    tomorrow_dt = datetime.combine(next_tue, datetime.min.time())
    one_year = tomorrow_dt + timedelta(days=365)

    # Pre-expand the rrule the way solver.py does in production:
    # the unit test passes already-expanded `exceptions` since the solver heuristics
    # only consume `exceptions` (rrule expansion happens in the router layer).
    from dateutil.rrule import MO, WEEKLY, rrule

    expanded = [d.date() for d in rrule(WEEKLY, byweekday=MO, dtstart=tomorrow_dt, until=one_year)]

    p_blocked = _person("p_blocked")
    p_open = _person("p_open")
    avail = Availability(person_id="p_blocked", exceptions=expanded)

    ctx = _ctx_with(
        people=[p_blocked, p_open],
        events=[_event("evt-mon", monday + timedelta(days=7))],  # Next Monday
        availability=[avail],
        from_date=monday + timedelta(days=1),
        to_date=monday + timedelta(days=14),
    )
    result = _solve(ctx)

    assignments = [a for a in result.assignments if a.event_id == "evt-mon"]
    assert assignments, "should have one assignment row for the event"
    assignees = assignments[0].assignees
    assert "p_blocked" not in assignees
    assert "p_open" in assignees


def test_single_exception_date_blocks_assignment():
    """One-off AvailabilityException date blocks just that day."""
    target = date(2026, 9, 12)
    p_blocked = _person("p_blocked")
    p_open = _person("p_open")
    avail = Availability(person_id="p_blocked", exceptions=[target])

    ctx = _ctx_with(
        people=[p_blocked, p_open],
        events=[_event("evt-target", target)],
        availability=[avail],
        from_date=target - timedelta(days=2),
        to_date=target + timedelta(days=2),
    )
    result = _solve(ctx)

    assignees = next(a.assignees for a in result.assignments if a.event_id == "evt-target")
    assert "p_blocked" not in assignees
    assert "p_open" in assignees


def test_exception_does_not_affect_other_dates():
    """An exception on one date doesn't block events on other dates."""
    blocked_day = date(2026, 9, 12)
    other_day = date(2026, 9, 13)
    only_p = _person("p_only")
    avail = Availability(person_id="p_only", exceptions=[blocked_day])

    ctx = _ctx_with(
        people=[only_p],
        events=[_event("evt-other", other_day)],
        availability=[avail],
        from_date=blocked_day - timedelta(days=2),
        to_date=blocked_day + timedelta(days=10),
    )
    result = _solve(ctx)

    assignees = next(a.assignees for a in result.assignments if a.event_id == "evt-other")
    # The only volunteer is available on the other day
    assert "p_only" in assignees


def test_empty_availability_means_assignable():
    """No Availability row at all means no blocks."""
    p = _person("p_free")
    today = date(2026, 6, 1)

    ctx = _ctx_with(
        people=[p],
        events=[_event("evt-free", today)],
        availability=[],
        from_date=today - timedelta(days=2),
        to_date=today + timedelta(days=2),
    )
    result = _solve(ctx)

    assignees = next(a.assignees for a in result.assignments if a.event_id == "evt-free")
    assert "p_free" in assignees


def test_multiple_rules_stack():
    """Vacation + exception both apply; remaining open dates are still assignable."""
    from api.core.models import VacationPeriod

    busy_p = _person("p_busy")
    spare_p = _person("p_spare")
    vacation_start = date(2026, 7, 4)
    vacation_end = date(2026, 7, 8)
    one_off = date(2026, 7, 15)

    avail = Availability(
        person_id="p_busy",
        vacations=[VacationPeriod(start=vacation_start, end=vacation_end)],
        exceptions=[one_off],
    )

    # Three events: one in the vacation, one on the exception day, one free
    events = [
        _event("evt-vac", date(2026, 7, 5)),  # in vacation range
        _event("evt-exc", one_off),
        _event("evt-free", date(2026, 7, 20)),
    ]

    ctx = _ctx_with(
        people=[busy_p, spare_p],
        events=events,
        availability=[avail],
        from_date=date(2026, 7, 1),
        to_date=date(2026, 7, 31),
    )
    result = _solve(ctx)

    by_event = {a.event_id: a.assignees for a in result.assignments}
    assert "p_busy" not in by_event["evt-vac"]
    assert "p_busy" not in by_event["evt-exc"]
    # On the free day busy_p IS assignable (spare_p may also be picked first
    # by fairness; relax the assertion to "at least one of the two").
    assert by_event["evt-free"], "free-day event must have at least one assignee"
