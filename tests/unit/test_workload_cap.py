"""Unit tests: enforce_cap with P{N}D rolling windows.

Sprint 6 PR 6.3 extends the existing ``enforce_cap`` constraint action to
support rolling N-day windows in addition to the prior ``P1M`` (monthly)
window. Period strings follow ISO-8601 abbreviated form: ``P7D`` = 7 days,
``P14D`` = 14 days, etc. Window is **centered** on the candidate event
date — for ``P7D`` and event on Jun 7, the window is [Jun 4, Jun 10].

This is a unit test on ``evaluate_constraint`` directly — no solver, no
router, no DB. The downstream wiring of DB constraints into solver context
is a separate follow-up.
"""

from datetime import date, datetime, timedelta

from api.core.constraints.dsl import EvalContext
from api.core.constraints.eval import evaluate_constraint
from api.core.models import (
    ConstraintAction,
    ConstraintBinding,
    Event,
    Person,
)


def _person(pid: str) -> Person:
    return Person(id=pid, name=pid, roles=["volunteer"], skills=[], teams=[])


def _event(eid: str, on: date) -> Event:
    return Event(
        id=eid,
        type="service",
        start=datetime.combine(on, datetime.min.time().replace(hour=10)),
        end=datetime.combine(on, datetime.min.time().replace(hour=11)),
    )


def _binding(period: str, max_count: int, severity: str = "hard") -> ConstraintBinding:
    return ConstraintBinding(
        key="weekly_cap",
        scope="person",
        applies_to=["service"],
        severity=severity,
        weight=10 if severity == "soft" else None,
        then=ConstraintAction(enforce_cap={"period": period, "max_count": max_count}),
    )


def _ctx(
    *,
    candidate_event: Event,
    person: Person,
    person_assignments: dict[str, list[Event]],
) -> EvalContext:
    return EvalContext(
        event=candidate_event,
        date=candidate_event.start.date(),
        person=person,
        person_assignments=person_assignments,
    )


def test_p7d_rejects_when_at_max_count():
    """Person with 2 prior events inside 7d window, hard cap=2 → rejected."""
    target_date = date(2026, 6, 7)
    p = _person("p1")
    candidate = _event("e_target", target_date)
    # 2 prior events in [Jun 4, Jun 10] window
    prior = [_event("e1", target_date - timedelta(days=2)), _event("e2", target_date)]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    binding = _binding("P7D", max_count=2)

    result = evaluate_constraint(binding, ctx)
    assert result.satisfied is False
    assert result.penalty == 1000.0
    assert "max" in result.reason.lower() or "cap" in result.reason.lower()


def test_p7d_allows_when_under_max():
    """Person with 1 prior event inside window, cap=2 → satisfied."""
    target_date = date(2026, 6, 7)
    p = _person("p1")
    candidate = _event("e_target", target_date)
    prior = [_event("e1", target_date - timedelta(days=1))]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    binding = _binding("P7D", max_count=2)

    result = evaluate_constraint(binding, ctx)
    assert result.satisfied is True


def test_p7d_excludes_events_outside_window():
    """Events more than half-window days away are not counted."""
    target_date = date(2026, 6, 15)
    p = _person("p1")
    candidate = _event("e_target", target_date)
    # P7D centered on Jun 15 = [Jun 12, Jun 18]
    # Jun 5 and Jun 25 are both outside.
    prior = [
        _event("e_far_back", date(2026, 6, 5)),
        _event("e_far_forward", date(2026, 6, 25)),
    ]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    binding = _binding("P7D", max_count=1)

    result = evaluate_constraint(binding, ctx)
    assert result.satisfied is True


def test_p14d_window_extends_further():
    """A 14-day window catches events a 7-day window misses."""
    target_date = date(2026, 6, 15)
    p = _person("p1")
    candidate = _event("e_target", target_date)
    # 6 days before: outside P7D ([Jun 12, Jun 18]) but inside P14D ([Jun 8, Jun 21])
    prior = [_event("e_back", date(2026, 6, 9))]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})

    # P7D with cap=1 → satisfied (event on Jun 9 is outside window)
    assert evaluate_constraint(_binding("P7D", max_count=1), ctx).satisfied is True
    # P14D with cap=1 → rejected (Jun 9 is inside window, count=1 already at cap)
    assert evaluate_constraint(_binding("P14D", max_count=1), ctx).satisfied is False


def test_p7d_soft_severity_returns_weight_penalty():
    """severity=soft hits the soft penalty branch with the binding's weight."""
    target_date = date(2026, 6, 7)
    p = _person("p1")
    candidate = _event("e_target", target_date)
    prior = [_event("e1", target_date), _event("e2", target_date)]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    binding = _binding("P7D", max_count=2, severity="soft")

    result = evaluate_constraint(binding, ctx)
    assert result.satisfied is False
    assert result.penalty == 10.0


def test_p1m_period_still_works():
    """Backwards compat: existing P1M monthly cap behavior is unchanged."""
    p = _person("p1")
    candidate = _event("e_target", date(2026, 6, 30))  # June
    # 5 events in June already
    prior = [_event(f"e{i}", date(2026, 6, i + 1)) for i in range(5)]

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    binding = _binding("P1M", max_count=5)

    result = evaluate_constraint(binding, ctx)
    assert result.satisfied is False


def test_no_prior_assignments_satisfies():
    """A person with no prior events is always under cap."""
    p = _person("p1")
    candidate = _event("e_target", date(2026, 6, 7))

    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={})
    binding = _binding("P7D", max_count=1)

    assert evaluate_constraint(binding, ctx).satisfied is True


def test_p7d_window_centering_math():
    """Verify the exact window bounds for P7D centered on a target date.

    For N=7, half=3, win=[date-3, date+3] inclusive, total 7 days.
    """
    target_date = date(2026, 6, 10)
    p = _person("p1")
    candidate = _event("e_target", target_date)

    # Boundary cases:
    # date-3 = Jun 7 (in window)
    # date-4 = Jun 6 (out)
    # date+3 = Jun 13 (in)
    # date+4 = Jun 14 (out)
    prior = [
        _event("e_in_back", date(2026, 6, 7)),
        _event("e_in_fwd", date(2026, 6, 13)),
    ]
    ctx = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior})
    # cap=2, 2 already in window → reject
    assert evaluate_constraint(_binding("P7D", max_count=2), ctx).satisfied is False

    # Boundary - just outside:
    prior_out = [
        _event("e_out_back", date(2026, 6, 6)),
        _event("e_out_fwd", date(2026, 6, 14)),
    ]
    ctx_out = _ctx(candidate_event=candidate, person=p, person_assignments={"p1": prior_out})
    assert evaluate_constraint(_binding("P7D", max_count=2), ctx_out).satisfied is True
