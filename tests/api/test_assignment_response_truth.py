"""Member response state is distinct from assignment allocation state."""

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, AuditAction, AuditLog, Event, Solution
from api.services.publication_service import capture_solution_scope
from tests.api.conftest import auth_headers, seed_event, seed_org, seed_user

pytestmark = pytest.mark.no_mock_auth


def _setup_assignment(client, db, suffix: str):
    org_id = f"response-{suffix}"
    admin_email = f"admin-{suffix}@response.example"
    member_email = f"member-{suffix}@response.example"
    seed_org(client, org_id)
    seed_user(client, org_id, admin_email, "Admin", "AdminPass123!")
    member = seed_user(
        client,
        org_id,
        member_email,
        "Member",
        "MemberPass123!",
        roles=["volunteer", "usher"],
    )
    admin_headers = auth_headers(client, admin_email, "AdminPass123!")
    member_headers = auth_headers(client, member_email, "MemberPass123!")
    event = seed_event(
        client,
        admin_headers,
        org_id,
        f"event-{suffix}",
        days_from_now=21,
        role_counts={"usher": 1},
    )
    assigned = client.post(
        f"/api/v1/events/{event['id']}/assignments",
        json={"person_id": member["person_id"], "action": "assign", "role": "usher"},
        headers=admin_headers,
    )
    assert assigned.status_code == 200, assigned.text
    assignment = db.get(Assignment, assigned.json()["assignment_id"])
    assert assignment is not None
    return {
        "org_id": org_id,
        "admin_headers": admin_headers,
        "member": member,
        "member_headers": member_headers,
        "event": event,
        "assignment": assignment,
    }


def _solution(db, org_id: str, events: list[Event]) -> Solution:
    scope = capture_solution_scope(
        events,
        range_start=min(event.start_time.date() for event in events),
        range_end=max(event.start_time.date() for event in events),
    )
    solution = Solution(
        org_id=org_id,
        solve_ms=1,
        hard_violations=0,
        soft_score=0,
        health_score=100,
        metrics={},
        scope_start=scope.range_start,
        scope_end=scope.range_end,
        scope_event_ids=scope.event_ids,
        scope_fingerprint=scope.fingerprint,
    )
    db.add(solution)
    db.flush()
    return solution


def test_new_assignment_is_unanswered_until_member_accepts(client, db):
    context = _setup_assignment(client, db, "accept")
    assignment = context["assignment"]

    assert assignment.status == "pending"
    assert assignment.response_status == "pending"
    assert assignment.response_revision is None
    assert assignment.responded_at is None
    assert assignment.responded_by_person_id is None

    response = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        params={"expected_revision": assignment.commitment_revision},
        headers=context["member_headers"],
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "confirmed"
    assert body["response_status"] == "accepted"
    assert body["response_current"] is True
    assert body["response_revision"] == body["commitment_revision"]
    assert body["responded_by_person_id"] == context["member"]["person_id"]
    assert body["responded_at"] is not None

    coordinator = client.get(
        f"/api/v1/events/assignments/all?org_id={context['org_id']}",
        headers=context["admin_headers"],
    )
    assert coordinator.status_code == 200, coordinator.text
    coordinator_row = next(
        row for row in coordinator.json()["assignments"] if row["assignment_id"] == assignment.id
    )
    assert coordinator_row["response_status"] == "accepted"
    assert coordinator_row["responded_by_person_id"] == context["member"]["person_id"]
    assert coordinator_row["response_revision"] == coordinator_row["commitment_revision"]
    assert coordinator_row["response_current"] is True


def test_same_response_replay_is_idempotent_and_stale_revision_is_rejected(client, db):
    context = _setup_assignment(client, db, "replay")
    assignment = context["assignment"]
    url = f"/api/v1/assignments/{assignment.id}/accept"
    params = {"expected_revision": assignment.commitment_revision}

    first = client.post(url, params=params, headers=context["member_headers"])
    assert first.status_code == 200
    audit_count = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == AuditAction.ASSIGNMENT_ACCEPTED,
            AuditLog.resource_id == str(assignment.id),
        )
        .count()
    )

    replay = client.post(url, params=params, headers=context["member_headers"])
    assert replay.status_code == 200
    assert (
        db.query(AuditLog)
        .filter(
            AuditLog.action == AuditAction.ASSIGNMENT_ACCEPTED,
            AuditLog.resource_id == str(assignment.id),
        )
        .count()
        == audit_count
    )

    event = context["event"]
    moved_start = datetime.fromisoformat(event["start_time"]) + timedelta(hours=1)
    moved_end = datetime.fromisoformat(event["end_time"]) + timedelta(hours=1)
    changed = client.put(
        f"/api/v1/events/{event['id']}",
        json={"start_time": moved_start.isoformat(), "end_time": moved_end.isoformat()},
        headers=context["admin_headers"],
    )
    assert changed.status_code == 200, changed.text
    stale = client.post(url, params=params, headers=context["member_headers"])
    assert stale.status_code == 409
    db.refresh(assignment)
    assert assignment.response_status == "pending"
    assert assignment.response_revision is None


def test_audit_failure_rolls_back_response_mutation(client, db, monkeypatch):
    context = _setup_assignment(client, db, "rollback")
    assignment = context["assignment"]

    def fail_audit(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("api.routers.assignments.log_audit_event", fail_audit)
    response = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        params={"expected_revision": assignment.commitment_revision},
        headers=context["member_headers"],
    )
    assert response.status_code == 500

    db.expire_all()
    unchanged = db.get(Assignment, assignment.id)
    assert unchanged is not None
    assert unchanged.status == "pending"
    assert unchanged.response_status == "pending"
    assert unchanged.response_revision is None


def test_publish_carries_only_current_unchanged_response(client, db):
    context = _setup_assignment(client, db, "publish")
    manual = context["assignment"]
    event = db.get(Event, context["event"]["id"])
    assert event is not None

    first_solution = _solution(db, context["org_id"], [event])
    manual.solution_id = first_solution.id
    db.commit()
    assert (
        client.post(
            f"/api/v1/solutions/{first_solution.id}/publish",
            headers=context["admin_headers"],
        ).status_code
        == 200
    )
    accepted = client.post(
        f"/api/v1/assignments/{manual.id}/accept",
        params={"expected_revision": manual.commitment_revision},
        headers=context["member_headers"],
    )
    assert accepted.status_code == 200
    unchanged_solution = _solution(db, context["org_id"], [event])
    unchanged = Assignment(
        solution_id=unchanged_solution.id,
        event_id=event.id,
        person_id=context["member"]["person_id"],
        role="usher",
    )
    db.add(unchanged)
    db.commit()
    published = client.post(
        f"/api/v1/solutions/{unchanged_solution.id}/publish",
        headers=context["admin_headers"],
    )
    assert published.status_code == 200
    db.refresh(unchanged)
    assert unchanged.response_status == "accepted"
    assert unchanged.response_current is True
    moved_start = datetime.fromisoformat(context["event"]["start_time"]) + timedelta(hours=2)
    moved_end = datetime.fromisoformat(context["event"]["end_time"]) + timedelta(hours=2)
    moved = client.put(
        f"/api/v1/events/{event.id}",
        json={"start_time": moved_start.isoformat(), "end_time": moved_end.isoformat()},
        headers=context["admin_headers"],
    )
    assert moved.status_code == 200, moved.text
    db.refresh(unchanged)
    assert unchanged.status == "pending"
    assert unchanged.response_status == "pending"
    assert unchanged.response_revision is None
