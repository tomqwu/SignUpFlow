"""A person fills one slot, and cannot attend overlapping events."""

from datetime import datetime, timedelta

import pytest

from api.core.models import Event, Person, RequiredRole
from tests.unit.test_solver_rrule_honoring import _ctx_with, _solve

pytestmark = pytest.mark.unit


def test_multi_skilled_person_cannot_hide_a_missing_role():
    start = datetime(2030, 1, 6, 10)
    event = Event(
        id="service",
        type="service",
        start=start,
        end=start + timedelta(hours=1),
        required_roles=[RequiredRole(role="music", count=1), RequiredRole(role="sound", count=1)],
    )
    person = Person(id="alex", name="Alex", roles=["music", "sound"], skills=[], teams=[])
    result = _solve(
        _ctx_with(
            people=[person],
            events=[event],
            availability=[],
            from_date=start.date(),
            to_date=start.date(),
        )
    )
    assert len(result.violations.hard) == 1
    assert "sound needs 1, got 0" in result.violations.hard[0].message


@pytest.mark.parametrize("offset,expected", [(30, 1), (60, 2)])
def test_overlap_rejected_but_adjacent_events_allowed(offset, expected):
    start = datetime(2030, 1, 6, 10)
    events = [
        Event(
            id=str(i),
            type="game",
            start=start + timedelta(minutes=i * offset),
            end=start + timedelta(minutes=i * offset + 60),
            required_roles=[RequiredRole(role="coach", count=1)],
        )
        for i in range(2)
    ]
    person = Person(id="coach", name="Coach", roles=["coach"], skills=[], teams=[])
    result = _solve(
        _ctx_with(
            people=[person],
            events=events,
            availability=[],
            from_date=start.date(),
            to_date=start.date(),
        )
    )
    assert sum(len(a.assignees) for a in result.assignments) == expected
    assert len(result.violations.hard) == 2 - expected
