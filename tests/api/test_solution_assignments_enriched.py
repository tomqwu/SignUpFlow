"""Tests for the typed, event-grouped /solutions/{id}/assignments response.

Sprint 8 PR 8.1 swaps the untyped flat list for a typed
``SolutionAssignmentsResponse`` that groups assignees per event so the mobile
Solution Review screen can render the per-event breakdown without client-side
regrouping.
"""

import pytest

from api.models import Assignment, Event, Person, Solution
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@o.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _seed_solution(db, org_id: str) -> Solution:
    sol = Solution(
        org_id=org_id,
        solve_ms=10.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=99.0,
        metrics={},
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


def _seed_event(db, org_id: str, event_id: str, event_type: str = "Sunday Service") -> Event:
    start = utcnow()
    evt = Event(
        id=event_id,
        org_id=org_id,
        type=event_type,
        start_time=start,
        end_time=start,
        extra_data={},
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return evt


def _seed_person(db, org_id: str, person_id: str, name: str) -> Person:
    p = Person(
        id=person_id,
        org_id=org_id,
        name=name,
        roles=["volunteer"],
        timezone="UTC",
        language="en",
        extra_data={},
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_assignment(db, solution_id: int, event_id: str, person_id: str) -> Assignment:
    a = Assignment(
        solution_id=solution_id,
        event_id=event_id,
        person_id=person_id,
        assigned_at=utcnow(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.mark.no_mock_auth
class TestSolutionAssignmentsEnriched:
    def test_groups_assignees_by_event(self, client, db):
        org_id = "sa-grouping"
        seed_org(client, org_id)
        _admin_for(client, org_id, "g")

        sol = _seed_solution(db, org_id)
        _seed_event(db, org_id, "evt-a", event_type="Sunday Service")
        _seed_person(db, org_id, "p1", "Alice")
        _seed_person(db, org_id, "p2", "Bob")
        _seed_assignment(db, sol.id, "evt-a", "p1")
        _seed_assignment(db, sol.id, "evt-a", "p2")

        resp = client.get(f"/api/v1/solutions/{sol.id}/assignments")
        assert resp.status_code == 200, resp.text
        body = resp.json()

        assert body["solution_id"] == sol.id
        assert body["total_assignments"] == 2
        assert len(body["events"]) == 1
        event = body["events"][0]
        assert event["event_id"] == "evt-a"
        assert event["event_type"] == "Sunday Service"
        names = {a["person_name"] for a in event["assignees"]}
        assert names == {"Alice", "Bob"}

    def test_empty_solution_returns_zero_events(self, client, db):
        org_id = "sa-empty"
        seed_org(client, org_id)
        _admin_for(client, org_id, "e")
        sol = _seed_solution(db, org_id)

        resp = client.get(f"/api/v1/solutions/{sol.id}/assignments")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["solution_id"] == sol.id
        assert body["total_assignments"] == 0
        assert body["events"] == []

    def test_unknown_solution_returns_404(self, client):
        org_id = "sa-404"
        seed_org(client, org_id)
        _admin_for(client, org_id, "x")
        resp = client.get("/api/v1/solutions/999999/assignments")
        assert resp.status_code == 404

    def test_two_events_in_one_solution(self, client, db):
        org_id = "sa-twoevt"
        seed_org(client, org_id)
        _admin_for(client, org_id, "t")

        sol = _seed_solution(db, org_id)
        _seed_event(db, org_id, "evt-1", event_type="Practice")
        _seed_event(db, org_id, "evt-2", event_type="Sunday Service")
        _seed_person(db, org_id, "p1", "Alice")
        _seed_assignment(db, sol.id, "evt-1", "p1")
        _seed_assignment(db, sol.id, "evt-2", "p1")

        resp = client.get(f"/api/v1/solutions/{sol.id}/assignments")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_assignments"] == 2
        assert len(body["events"]) == 2
        # Each event has exactly one assignee.
        for event in body["events"]:
            assert len(event["assignees"]) == 1
            assert event["assignees"][0]["person_id"] == "p1"
