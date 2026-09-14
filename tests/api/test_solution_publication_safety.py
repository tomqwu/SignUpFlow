"""Safety contract for publishing and rolling back generated schedules."""

from __future__ import annotations

from datetime import timedelta

import pytest

from api.models import Assignment, Constraint, Event, Notification, Person, Solution
from api.services.assignment_response import record_assignment_response
from api.services.publication_service import capture_solution_scope
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_org, seed_user


def _setup_org(client, db, suffix: str) -> tuple[str, dict, Person]:
    org_id = f"publication-{suffix}"
    email = f"admin-{suffix}@example.org"
    seed_org(client, org_id)
    seed_user(client, org_id, email=email, name="Admin", password="AdminPass1!")
    headers = auth_headers(client, email=email, password="AdminPass1!")
    admin = db.query(Person).filter(Person.org_id == org_id, Person.email == email).one()
    return org_id, headers, admin


def _event(
    db,
    *,
    org_id: str,
    event_id: str,
    day: int,
    roles: dict[str, int],
) -> Event:
    start = utcnow() + timedelta(days=day)
    row = Event(
        id=event_id,
        org_id=org_id,
        type="Service",
        start_time=start,
        end_time=start + timedelta(hours=2),
        extra_data={"role_counts": roles},
    )
    db.add(row)
    db.commit()
    return row


def _member(db, *, org_id: str, person_id: str, roles: list[str]) -> Person:
    row = Person(
        id=person_id,
        org_id=org_id,
        name=person_id,
        email=f"{person_id}@example.org",
        roles=roles,
        status="active",
    )
    db.add(row)
    db.commit()
    return row


def _solution(
    db,
    *,
    org_id: str,
    events: list[Event],
    assignments: list[tuple[Event, Person, str]],
    published: bool = False,
) -> Solution:
    constraints = db.query(Constraint).filter(Constraint.org_id == org_id).all()
    scope = capture_solution_scope(
        events,
        range_start=min(event.start_time.date() for event in events),
        range_end=max(event.start_time.date() for event in events),
        constraints=constraints,
    )
    row = Solution(
        org_id=org_id,
        solve_ms=1.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=100.0,
        metrics={},
        scope_start=scope.range_start,
        scope_end=scope.range_end,
        scope_event_ids=scope.event_ids,
        scope_fingerprint=scope.fingerprint,
        is_published=published,
        published_at=utcnow() if published else None,
    )
    db.add(row)
    db.flush()
    for event, person, role in assignments:
        db.add(
            Assignment(
                solution_id=row.id,
                event_id=event.id,
                person_id=person.id,
                role=role,
            )
        )
    db.commit()
    db.refresh(row)
    return row


@pytest.mark.no_mock_auth
def test_legacy_solution_without_scope_requires_regeneration(client, db):
    org_id, headers, _ = _setup_org(client, db, "legacy")
    legacy = Solution(
        org_id=org_id,
        solve_ms=1.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=100.0,
        metrics={},
    )
    db.add(legacy)
    db.commit()

    response = client.post(f"/api/v1/solutions/{legacy.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "regenerate" in response.json()["detail"].lower()
    db.refresh(legacy)
    assert legacy.is_published is False


@pytest.mark.no_mock_auth
def test_incomplete_solution_keeps_prior_roster_active(client, db):
    org_id, headers, _ = _setup_org(client, db, "shortage")
    usher = _member(db, org_id=org_id, person_id="shortage-usher", roles=["usher"])
    second_usher = _member(
        db,
        org_id=org_id,
        person_id="shortage-second-usher",
        roles=["usher"],
    )
    event = _event(db, org_id=org_id, event_id="shortage-event", day=7, roles={"usher": 2})
    prior = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, usher, "usher"), (event, second_usher, "usher")],
        published=True,
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, usher, "usher")],
    )

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "shortage-event" in response.json()["detail"]
    db.refresh(prior)
    db.refresh(candidate)
    assert prior.is_published is True
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_narrow_solution_cannot_remove_future_published_horizon(client, db):
    org_id, headers, _ = _setup_org(client, db, "narrow")
    member = _member(db, org_id=org_id, person_id="narrow-member", roles=["usher"])
    week_one = _event(db, org_id=org_id, event_id="narrow-week-1", day=7, roles={"usher": 1})
    week_six = _event(db, org_id=org_id, event_id="narrow-week-6", day=42, roles={"usher": 1})
    prior = _solution(
        db,
        org_id=org_id,
        events=[week_one, week_six],
        assignments=[(week_one, member, "usher"), (week_six, member, "usher")],
        published=True,
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[week_one],
        assignments=[(week_one, member, "usher")],
    )

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "narrow-week-6" in response.json()["detail"]
    db.refresh(prior)
    assert prior.is_published is True


@pytest.mark.no_mock_auth
def test_changed_event_snapshot_requires_regeneration(client, db):
    org_id, headers, _ = _setup_org(client, db, "stale")
    member = _member(db, org_id=org_id, person_id="stale-member", roles=["usher", "greeter"])
    event = _event(db, org_id=org_id, event_id="stale-event", day=7, roles={"usher": 1})
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
    )
    event.extra_data = {"role_counts": {"greeter": 1}}
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "changed" in response.json()["detail"].lower()
    db.refresh(candidate)
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_changed_saved_constraint_requires_regeneration(client, db):
    org_id, headers, _ = _setup_org(client, db, "constraint")
    member = _member(db, org_id=org_id, person_id="constraint-member", roles=["usher"])
    event = _event(
        db,
        org_id=org_id,
        event_id="constraint-event",
        day=7,
        roles={"usher": 1},
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
    )
    db.add(
        Constraint(
            org_id=org_id,
            key="new-rest-rule",
            type="hard",
            predicate="min_gap_hours",
            params={"min_hours": 12, "applies_to": ["Service"]},
        )
    )
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "changed" in response.json()["detail"].lower()
    db.refresh(candidate)
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_current_hard_constraint_overrides_cached_healthy_score(client, db):
    org_id, headers, _ = _setup_org(client, db, "current-constraint")
    member = _member(db, org_id=org_id, person_id="capped-member", roles=["usher"])
    first = _event(
        db,
        org_id=org_id,
        event_id="capped-event-1",
        day=7,
        roles={"usher": 1},
    )
    second = _event(
        db,
        org_id=org_id,
        event_id="capped-event-2",
        day=8,
        roles={"usher": 1},
    )
    db.add(
        Constraint(
            org_id=org_id,
            key="one-service-per-week",
            type="hard",
            predicate="max_assignments",
            params={"period": "P7D", "max_count": 1, "applies_to": ["Service"]},
        )
    )
    db.commit()
    candidate = _solution(
        db,
        org_id=org_id,
        events=[first, second],
        assignments=[(first, member, "usher"), (second, member, "usher")],
    )
    candidate.hard_violations = 0
    candidate.health_score = 100.0
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "one-service-per-week" in response.json()["detail"]
    assert "maximum 1" in response.json()["detail"]
    db.refresh(candidate)
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_malformed_role_requirements_cannot_publish(client, db):
    org_id, headers, _ = _setup_org(client, db, "malformed-role")
    member = _member(db, org_id=org_id, person_id="malformed-member", roles=["usher"])
    event = _event(
        db,
        org_id=org_id,
        event_id="malformed-event",
        day=7,
        roles={"usher": "1"},
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
    )

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "invalid role requirements" in response.json()["detail"].lower()
    db.refresh(candidate)
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_unrequested_assignment_role_cannot_publish(client, db):
    org_id, headers, _ = _setup_org(client, db, "unexpected-role")
    usher = _member(db, org_id=org_id, person_id="expected-usher", roles=["usher"])
    greeter = _member(db, org_id=org_id, person_id="unexpected-greeter", roles=["greeter"])
    event = _event(
        db,
        org_id=org_id,
        event_id="unexpected-role-event",
        day=7,
        roles={"usher": 1},
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, usher, "usher"), (event, greeter, "greeter")],
    )

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "does not require assignment role greeter" in response.json()["detail"]
    db.refresh(candidate)
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_changed_qualification_keeps_prior_roster_active(client, db):
    org_id, headers, _ = _setup_org(client, db, "qualification")
    prior_member = _member(
        db,
        org_id=org_id,
        person_id="qualification-prior-member",
        roles=["usher"],
    )
    candidate_member = _member(
        db,
        org_id=org_id,
        person_id="qualification-candidate-member",
        roles=["usher"],
    )
    event = _event(
        db,
        org_id=org_id,
        event_id="qualification-event",
        day=7,
        roles={"usher": 1},
    )
    prior = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, prior_member, "usher")],
        published=True,
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, candidate_member, "usher")],
    )
    candidate_member.roles = ["greeter"]
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 409
    assert "no longer qualified" in response.json()["detail"].lower()
    db.refresh(prior)
    db.refresh(candidate)
    assert prior.is_published is True
    assert candidate.is_published is False


@pytest.mark.no_mock_auth
def test_explicit_cancellation_and_week_seven_rollover_can_publish(client, db):
    org_id, headers, _ = _setup_org(client, db, "rollover")
    member = _member(db, org_id=org_id, person_id="rollover-member", roles=["usher"])
    past = _event(db, org_id=org_id, event_id="rollover-past", day=-7, roles={"usher": 1})
    cancelled = _event(
        db,
        org_id=org_id,
        event_id="rollover-cancelled",
        day=14,
        roles={"usher": 1},
    )
    retained = _event(
        db,
        org_id=org_id,
        event_id="rollover-retained",
        day=35,
        roles={"usher": 1},
    )
    prior = _solution(
        db,
        org_id=org_id,
        events=[past, cancelled, retained],
        assignments=[
            (past, member, "usher"),
            (cancelled, member, "usher"),
            (retained, member, "usher"),
        ],
        published=True,
    )

    delete = client.delete(f"/api/v1/events/{cancelled.id}", headers=headers)
    assert delete.status_code == 204, delete.text
    week_seven = _event(
        db,
        org_id=org_id,
        event_id="rollover-week-7",
        day=49,
        roles={"usher": 1},
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[retained, week_seven],
        assignments=[(retained, member, "usher"), (week_seven, member, "usher")],
    )

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 200, response.text
    db.refresh(prior)
    db.refresh(candidate)
    assert prior.is_published is False
    assert candidate.is_published is True


@pytest.mark.no_mock_auth
def test_publish_preserves_only_current_equivalent_member_response(client, db):
    org_id, headers, admin = _setup_org(client, db, "response")
    member = _member(db, org_id=org_id, person_id="response-member", roles=["usher"])
    event = _event(db, org_id=org_id, event_id="response-event", day=7, roles={"usher": 1})
    prior = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
        published=True,
    )
    prior_assignment = db.query(Assignment).filter(Assignment.solution_id == prior.id).one()
    record_assignment_response(
        prior_assignment,
        actor_person_id=member.id,
        response_status="accepted",
        workflow_status="confirmed",
        expected_revision=1,
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
    )
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 200, response.text
    candidate_assignment = db.query(Assignment).filter(Assignment.solution_id == candidate.id).one()
    db.refresh(candidate_assignment)
    assert candidate_assignment.response_status == "accepted"
    assert candidate_assignment.responded_by_person_id == member.id
    assert db.query(Notification).filter(Notification.org_id == org_id).count() == 0
    assert admin.org_id == org_id


@pytest.mark.no_mock_auth
def test_publish_resets_responses_when_people_change_roles(client, db):
    org_id, headers, _ = _setup_org(client, db, "response-role-change")
    first = _member(
        db,
        org_id=org_id,
        person_id="response-role-first",
        roles=["usher", "greeter"],
    )
    second = _member(
        db,
        org_id=org_id,
        person_id="response-role-second",
        roles=["usher", "greeter"],
    )
    event = _event(
        db,
        org_id=org_id,
        event_id="response-role-event",
        day=7,
        roles={"usher": 1, "greeter": 1},
    )
    prior = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, first, "usher"), (event, second, "greeter")],
        published=True,
    )
    for assignment in db.query(Assignment).filter(Assignment.solution_id == prior.id).all():
        record_assignment_response(
            assignment,
            actor_person_id=assignment.person_id,
            response_status="accepted",
            workflow_status="confirmed",
            expected_revision=1,
        )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, first, "greeter"), (event, second, "usher")],
    )
    db.commit()

    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 200, response.text
    candidate_assignments = (
        db.query(Assignment).filter(Assignment.solution_id == candidate.id).all()
    )
    assert {assignment.response_status for assignment in candidate_assignments} == {"pending"}
    assert not any(assignment.response_current for assignment in candidate_assignments)
    notifications = db.query(Notification).filter(Notification.org_id == org_id).all()
    assert len(notifications) == 2
    assert len({notification.delivery_key for notification in notifications}) == 2
    assert all(
        notification.delivery_key.startswith(f"solution:{candidate.id}:assignment:")
        for notification in notifications
    )


@pytest.mark.no_mock_auth
def test_audit_failure_rolls_back_roster_and_notification_intent(client, db, monkeypatch):
    org_id, headers, _ = _setup_org(client, db, "audit-failure")
    member = _member(db, org_id=org_id, person_id="audit-member", roles=["usher"])
    event = _event(db, org_id=org_id, event_id="audit-event", day=7, roles={"usher": 1})
    prior = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
        published=True,
    )
    candidate = _solution(
        db,
        org_id=org_id,
        events=[event],
        assignments=[(event, member, "usher")],
    )

    def fail_audit(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("api.services.publication_service.log_audit_event", fail_audit)
    response = client.post(f"/api/v1/solutions/{candidate.id}/publish", headers=headers)

    assert response.status_code == 500
    db.expire_all()
    assert db.get(Solution, prior.id).is_published is True
    assert db.get(Solution, candidate.id).is_published is False
    assert db.query(Notification).filter(Notification.org_id == org_id).count() == 0
