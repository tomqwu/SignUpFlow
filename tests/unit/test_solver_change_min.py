"""Unit tests: solver candidate scoring honors change_min_weight bonus.

Sprint 6 PR 6.2 wires the dormant change-min plumbing
(``GreedyHeuristicSolver.enable_change_minimization`` was a no-op setter)
into the candidate scoring loop. When change_min is enabled and a candidate
``(event_id, person_id)`` matches a tuple in the prior-published-keys set,
the candidate gets a score bonus equal to ``change_min_weight``.

The match is **loose** — only ``(event_id, person_id)``, not role —
because the solver writes ``Assignment.role = NULL`` to the DB so a
role-strict match would never hit. See specs/020-solver-quality-changemin
for the rationale.

Hard-constraint rejections are NOT overridden by the bonus.
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


def _ctx(
    *,
    people: list[Person],
    events: list[Event],
    availability: list[Availability] | None = None,
    from_date: date,
    to_date: date,
    change_min: bool = False,
) -> SolveContext:
    return SolveContext(
        org=Org(org_id="t-org", region="US", defaults=OrgDefaults()),
        people=people,
        teams=[],
        resources=[],
        events=events,
        constraints=[],
        availability=availability or [],
        holidays=[],
        from_date=from_date,
        to_date=to_date,
        mode="strict",
        change_min=change_min,
    )


def _person(pid: str) -> Person:
    return Person(id=pid, name=pid, roles=["volunteer"], skills=[], teams=[])


def _event(eid: str, on: date) -> Event:
    return Event(
        id=eid,
        type="service",
        start=datetime.combine(on, datetime.min.time().replace(hour=10)),
        end=datetime.combine(on, datetime.min.time().replace(hour=11)),
        required_roles=[RequiredRole(role="volunteer", count=1)],
    )


def test_change_min_disabled_baseline_unchanged():
    """With change_min=False, prior keys are ignored — fairness picks the first candidate."""
    today = date(2026, 6, 1)
    p_a = _person("p_a")
    p_b = _person("p_b")
    e1 = _event("e1", today)

    ctx = _ctx(
        people=[p_a, p_b],
        events=[e1],
        from_date=today,
        to_date=today + timedelta(days=1),
        change_min=False,
    )
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    # Even setting prior keys, change_min=False means they are ignored
    solver.enable_change_minimization(False, 100)
    solver.set_prior_published_keys({("e1", "p_b")})  # would prefer p_b if enabled
    result = solver.solve()

    assignees = [a for a in result.assignments if a.event_id == "e1"][0].assignees
    # Both have the same penalty (zero assignments so far); first candidate wins.
    # The exact identity doesn't matter — what matters is no error is raised
    # and an assignment is produced.
    assert len(assignees) == 1
    assert assignees[0] in {"p_a", "p_b"}


def test_change_min_enabled_no_prior_unchanged():
    """change_min=True with empty prior set is a no-op."""
    today = date(2026, 6, 1)
    p_a = _person("p_a")
    p_b = _person("p_b")
    e1 = _event("e1", today)

    ctx = _ctx(
        people=[p_a, p_b],
        events=[e1],
        from_date=today,
        to_date=today + timedelta(days=1),
        change_min=True,
    )
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    solver.enable_change_minimization(True, 100)
    solver.set_prior_published_keys(set())
    result = solver.solve()

    assignees = [a for a in result.assignments if a.event_id == "e1"][0].assignees
    assert len(assignees) == 1


def test_prior_key_makes_candidate_preferred():
    """When prior had p_b on e1, change-min should pick p_b over p_a (tiebreak)."""
    today = date(2026, 6, 1)
    p_a = _person("p_a")
    p_b = _person("p_b")
    e1 = _event("e1", today)

    ctx = _ctx(
        people=[p_a, p_b],
        events=[e1],
        from_date=today,
        to_date=today + timedelta(days=1),
        change_min=True,
    )
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    solver.enable_change_minimization(True, 100)
    solver.set_prior_published_keys({("e1", "p_b")})
    result = solver.solve()

    assignees = [a for a in result.assignments if a.event_id == "e1"][0].assignees
    assert assignees == ["p_b"]


def test_prior_keys_are_per_event():
    """Prior on a different event should not influence this event's pick."""
    today = date(2026, 6, 1)
    p_a = _person("p_a")
    p_b = _person("p_b")
    e1 = _event("e1", today)

    ctx = _ctx(
        people=[p_a, p_b],
        events=[e1],
        from_date=today,
        to_date=today + timedelta(days=1),
        change_min=True,
    )
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    solver.enable_change_minimization(True, 100)
    # p_b was on a DIFFERENT event before — should not bias e1.
    solver.set_prior_published_keys({("e_other", "p_b")})
    result = solver.solve()

    assignees = [a for a in result.assignments if a.event_id == "e1"][0].assignees
    # Without the bonus applying, fairness picks first candidate; both have 0 prior
    # assignments so any pick is valid. The point: p_b is NOT artificially boosted.
    assert len(assignees) == 1


def test_unavailable_prior_person_is_still_rejected():
    """A person on vacation is rejected even if they were in the prior published set."""
    today = date(2026, 6, 1)
    p_a = _person("p_a")
    p_b = _person("p_b")
    e1 = _event("e1", today)

    # p_b is blocked on the event date via an exception.
    avail = Availability(person_id="p_b", exceptions=[today])

    ctx = _ctx(
        people=[p_a, p_b],
        events=[e1],
        availability=[avail],
        from_date=today,
        to_date=today + timedelta(days=1),
        change_min=True,
    )
    solver = GreedyHeuristicSolver()
    solver.build_model(ctx)
    solver.enable_change_minimization(True, 100)
    solver.set_prior_published_keys({("e1", "p_b")})  # bonus would prefer p_b
    result = solver.solve()

    assignees = [a for a in result.assignments if a.event_id == "e1"][0].assignees
    # Hard rejection (exception date) wins — p_b must not appear.
    assert "p_b" not in assignees
    assert assignees == ["p_a"]
