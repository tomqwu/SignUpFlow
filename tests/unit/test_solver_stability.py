"""Unit tests: compute_stability_metrics against a published solution.

Sprint 6 PR 6.1 turns the dormant StabilityMetrics zero-stub into a real
signal: how many ``(event_id, person_id, role)`` tuples differ between a
fresh solve's assignments and the org's currently-published solution, and
how many distinct people are affected.
"""

from datetime import datetime, timedelta

import pytest

from api.core.models import Assignment as CoreAssignment
from api.models import Assignment as DBAssignment
from api.models import Event, Person, Solution
from api.timeutils import utcnow
from api.utils.solver_stability import compute_stability_metrics


@pytest.fixture
def org_id():
    return "test_org"  # auto-seeded by tests/conftest.py reset


def _seed_event(db, org_id: str, event_id: str) -> Event:
    start = datetime(2026, 6, 1, 10, 0, 0)
    e = Event(
        id=event_id,
        org_id=org_id,
        type="Service",
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    db.add(e)
    db.commit()
    return e


def _seed_person(db, org_id: str, person_id: str) -> Person:
    p = Person(id=person_id, org_id=org_id, name=person_id.title(), roles=[])
    db.add(p)
    db.commit()
    return p


def _seed_published_solution(
    db, org_id: str, *, assignments: list[tuple[str, str, str | None]]
) -> Solution:
    """Create a published Solution with the given (event_id, person_id, role) rows."""
    sol = Solution(
        org_id=org_id,
        solve_ms=10.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=1.0,
        metrics={},
        is_published=True,
        published_at=utcnow(),
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)

    for event_id, person_id, role in assignments:
        db.add(
            DBAssignment(
                solution_id=sol.id,
                event_id=event_id,
                person_id=person_id,
                role=role,
            )
        )
    db.commit()
    return sol


def test_no_prior_published_returns_zeros(db, org_id):
    """When no solution is published in the org, both metrics are 0."""
    new_assignments = [CoreAssignment(event_id="e1", assignees=["p1"])]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    assert metrics.moves_from_published == 0
    assert metrics.affected_persons == 0


def test_byte_equal_solve_returns_zeros(db, org_id):
    """When the new solve matches the published solution exactly, metrics are 0."""
    _seed_event(db, org_id, "e1")
    _seed_event(db, org_id, "e2")
    _seed_person(db, org_id, "p1")
    _seed_person(db, org_id, "p2")
    _seed_published_solution(db, org_id, assignments=[("e1", "p1", None), ("e2", "p2", None)])

    new_assignments = [
        CoreAssignment(event_id="e1", assignees=["p1"]),
        CoreAssignment(event_id="e2", assignees=["p2"]),
    ]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    assert metrics.moves_from_published == 0
    assert metrics.affected_persons == 0


def test_one_swap_counts_as_two_moves(db, org_id):
    """Replacing p1 with p3 on e1 = 2 moves (1 removed + 1 added), 2 affected."""
    for pid in ("p1", "p2", "p3"):
        _seed_person(db, org_id, pid)
    _seed_event(db, org_id, "e1")
    _seed_event(db, org_id, "e2")
    _seed_published_solution(db, org_id, assignments=[("e1", "p1", None), ("e2", "p2", None)])

    new_assignments = [
        CoreAssignment(event_id="e1", assignees=["p3"]),  # changed: p1 → p3
        CoreAssignment(event_id="e2", assignees=["p2"]),  # unchanged
    ]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    assert metrics.moves_from_published == 2
    assert metrics.affected_persons == 2  # p1 (removed) + p3 (added)


def test_completely_different_solve(db, org_id):
    """Disjoint assignment sets produce |a| + |b| moves."""
    for pid in ("p1", "p2", "p3", "p4"):
        _seed_person(db, org_id, pid)
    for eid in ("e1", "e2"):
        _seed_event(db, org_id, eid)
    _seed_published_solution(db, org_id, assignments=[("e1", "p1", None), ("e2", "p2", None)])

    new_assignments = [
        CoreAssignment(event_id="e1", assignees=["p3"]),
        CoreAssignment(event_id="e2", assignees=["p4"]),
    ]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    assert metrics.moves_from_published == 4
    assert metrics.affected_persons == 4


def test_role_differences_in_prior_count_as_moves(db, org_id):
    """Solver writes role=None; if prior used a role string, both rows differ."""
    _seed_person(db, org_id, "p1")
    _seed_event(db, org_id, "e1")
    _seed_published_solution(db, org_id, assignments=[("e1", "p1", "usher")])

    new_assignments = [CoreAssignment(event_id="e1", assignees=["p1"])]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    # Prior key = (e1, p1, "usher"); new key = (e1, p1, None) — different tuples.
    assert metrics.moves_from_published == 2
    assert metrics.affected_persons == 1


def test_multi_assignee_event_counted_per_person(db, org_id):
    """An Event with multiple assignees expands into one key per person."""
    for pid in ("p1", "p2"):
        _seed_person(db, org_id, pid)
    _seed_event(db, org_id, "e1")
    _seed_published_solution(db, org_id, assignments=[("e1", "p1", None), ("e1", "p2", None)])

    new_assignments = [CoreAssignment(event_id="e1", assignees=["p1", "p2"])]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    assert metrics.moves_from_published == 0
    assert metrics.affected_persons == 0


def test_other_org_published_solution_ignored(db, org_id):
    """Stability is scoped per-org; another org's published solution is irrelevant."""
    from api.models import Organization

    other = Organization(id="other_org", name="Other", region="US", config={})
    db.add(other)
    db.commit()

    _seed_person(db, "other_org", "px")
    _seed_event(db, "other_org", "ex")
    _seed_published_solution(db, "other_org", assignments=[("ex", "px", None)])

    new_assignments = [CoreAssignment(event_id="e1", assignees=["p1"])]

    metrics = compute_stability_metrics(db, org_id=org_id, new_assignments=new_assignments)

    # No published solution for org_id="test_org" — zero baseline.
    assert metrics.moves_from_published == 0
    assert metrics.affected_persons == 0
