"""Real-JWT tenant boundaries for the scheduling API surface."""

from datetime import date, datetime, timedelta
from io import BytesIO

import pytest

from api.models import (
    Assignment,
    Availability,
    Event,
    Resource,
    Solution,
    TeamMember,
    VacationPeriod,
)
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_event, seed_org, seed_team, seed_user


@pytest.fixture
def tenants(client, db):
    seed_org(client, "tenant-a", name="Tenant A")
    seed_org(client, "tenant-b", name="Tenant B")
    admin_a = seed_user(client, "tenant-a", "admin-a@test.org", "Admin A", "Pass123!")
    admin_b = seed_user(client, "tenant-b", "admin-b@test.org", "Admin B", "Pass123!")
    member_a = seed_user(client, "tenant-a", "member-a@test.org", "Member A", "Pass123!")
    peer_a = seed_user(client, "tenant-a", "peer-a@test.org", "Peer A", "Pass123!")
    member_b = seed_user(client, "tenant-b", "member-b@test.org", "Member B", "Pass123!")

    headers = {
        "admin_a": auth_headers(client, "admin-a@test.org", "Pass123!"),
        "admin_b": auth_headers(client, "admin-b@test.org", "Pass123!"),
        "member_a": auth_headers(client, "member-a@test.org", "Pass123!"),
        "peer_a": auth_headers(client, "peer-a@test.org", "Pass123!"),
        "member_b": auth_headers(client, "member-b@test.org", "Pass123!"),
        "invalid": {"Authorization": "Bearer not-a-jwt"},
    }
    event_a = seed_event(client, headers["admin_a"], "tenant-a", "tenant-a-event")
    event_b = seed_event(client, headers["admin_b"], "tenant-b", "tenant-b-event")

    return {
        "headers": headers,
        "admin_a": admin_a,
        "admin_b": admin_b,
        "member_a": member_a,
        "peer_a": peer_a,
        "member_b": member_b,
        "event_a": event_a,
        "event_b": event_b,
    }


@pytest.mark.no_mock_auth
def test_event_reads_are_member_scoped_and_private_views_are_admin_only(client, tenants):
    headers = tenants["headers"]

    assert client.get("/api/v1/events/?org_id=tenant-a").status_code == 401
    assert (
        client.get("/api/v1/events/?org_id=tenant-a", headers=headers["invalid"]).status_code == 401
    )
    own = client.get("/api/v1/events/?org_id=tenant-a", headers=headers["member_a"])
    assert own.status_code == 200
    assert {item["id"] for item in own.json()["items"]} == {"tenant-a-event"}
    hidden_search = client.get(
        "/api/v1/events/?org_id=tenant-a&q=tenant-b-event", headers=headers["member_a"]
    )
    assert hidden_search.status_code == 200
    assert hidden_search.json()["total"] == 0
    assert hidden_search.json()["items"] == []
    assert (
        client.get("/api/v1/events/?org_id=tenant-b", headers=headers["member_a"]).status_code
        == 403
    )
    assert (
        client.get("/api/v1/events/tenant-b-event", headers=headers["member_a"]).status_code == 404
    )

    for suffix in ("available-people", "validation"):
        path = f"/api/v1/events/tenant-a-event/{suffix}"
        assert client.get(path, headers=headers["member_a"]).status_code == 403
        assert client.get(path, headers=headers["admin_a"]).status_code == 200
        assert client.get(path, headers=headers["admin_b"]).status_code == 404

    assignments_path = "/api/v1/events/assignments/all?org_id=tenant-a"
    assert client.get(assignments_path, headers=headers["member_a"]).status_code == 403
    assert client.get(assignments_path, headers=headers["admin_a"]).status_code == 200
    assert client.get(assignments_path, headers=headers["admin_b"]).status_code == 403


@pytest.mark.no_mock_auth
def test_event_children_must_belong_to_the_event_tenant(client, db, tenants):
    headers = tenants["headers"]
    seed_team(client, headers["admin_b"], "tenant-b", "foreign-team", "Foreign Team")
    db.add(
        Resource(
            id="foreign-resource",
            org_id="tenant-b",
            type="court",
            location="Foreign Gym",
        )
    )
    db.commit()

    start = datetime.now() + timedelta(days=20)
    payload = {
        "id": "bad-child-event",
        "org_id": "tenant-a",
        "type": "Practice",
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=1)).isoformat(),
        "team_ids": ["foreign-team"],
    }
    response = client.post("/api/v1/events/", json=payload, headers=headers["admin_a"])
    assert response.status_code == 404
    assert db.query(Event).filter(Event.id == "bad-child-event").first() is None

    payload["team_ids"] = []
    payload["resource_id"] = "foreign-resource"
    response = client.post("/api/v1/events/", json=payload, headers=headers["admin_a"])
    assert response.status_code == 404
    assert db.query(Event).filter(Event.id == "bad-child-event").first() is None

    response = client.put(
        "/api/v1/events/tenant-a-event",
        json={"resource_id": "foreign-resource"},
        headers=headers["admin_a"],
    )
    assert response.status_code == 404
    assert db.query(Event).filter(Event.id == "tenant-a-event").one().resource_id is None

    response = client.post(
        "/api/v1/events/tenant-a-event/assignments",
        json={"person_id": tenants["member_b"]["person_id"], "action": "assign"},
        headers=headers["admin_a"],
    )
    assert response.status_code == 404
    assert db.query(Assignment).count() == 0

    foreign_availability = Availability(
        person_id=tenants["member_b"]["person_id"], rrule=None, extra_data={}
    )
    db.add(foreign_availability)
    db.flush()
    event_date = date.fromisoformat(tenants["event_a"]["start_time"][:10])
    db.add_all(
        [
            Assignment(
                event_id=tenants["event_a"]["id"],
                person_id=tenants["member_b"]["person_id"],
                role="foreign-role",
            ),
            VacationPeriod(
                availability_id=foreign_availability.id,
                start_date=event_date,
                end_date=event_date,
                reason="Foreign private reason",
            ),
        ]
    )
    db.commit()

    assignments = client.get(
        "/api/v1/events/assignments/all?org_id=tenant-a", headers=headers["admin_a"]
    )
    assert assignments.status_code == 200
    assert assignments.json() == {"assignments": [], "total": 0}

    validation = client.get("/api/v1/events/tenant-a-event/validation", headers=headers["admin_a"])
    assert validation.status_code == 200
    assert "Member B" not in validation.text
    assert "Foreign private reason" not in validation.text


@pytest.mark.no_mock_auth
def test_conflict_checks_are_admin_scoped_and_hide_foreign_children(client, tenants):
    path = "/api/v1/conflicts/check"
    own_body = {
        "person_id": tenants["member_a"]["person_id"],
        "event_id": tenants["event_a"]["id"],
    }
    foreign_person = {**own_body, "person_id": tenants["member_b"]["person_id"]}
    foreign_event = {**own_body, "event_id": tenants["event_b"]["id"]}
    headers = tenants["headers"]

    assert client.post(path, json=own_body).status_code == 401
    assert client.post(path, json=own_body, headers=headers["invalid"]).status_code == 401
    assert client.post(path, json=own_body, headers=headers["member_a"]).status_code == 403
    assert client.post(path, json=own_body, headers=headers["admin_a"]).status_code == 200
    assert client.post(path, json=foreign_person, headers=headers["admin_a"]).status_code == 404
    assert client.post(path, json=foreign_event, headers=headers["admin_a"]).status_code == 404
    assert client.post(path, json=own_body, headers=headers["admin_b"]).status_code == 404


@pytest.mark.no_mock_auth
def test_availability_is_self_service_with_same_tenant_admin_override(client, db, tenants):
    person_id = tenants["member_a"]["person_id"]
    path = f"/api/v1/availability/{person_id}/timeoff"
    payload = {
        "start_date": (date.today() + timedelta(days=10)).isoformat(),
        "end_date": (date.today() + timedelta(days=11)).isoformat(),
        "reason": "Travel",
    }
    headers = tenants["headers"]

    assert client.get(path).status_code == 401
    assert client.get(path, headers=headers["invalid"]).status_code == 401
    assert client.get(path, headers=headers["member_a"]).status_code == 200
    assert client.get(path, headers=headers["peer_a"]).status_code == 403
    assert client.get(path, headers=headers["admin_a"]).status_code == 200
    assert client.get(path, headers=headers["admin_b"]).status_code == 404

    assert client.post(path, json=payload, headers=headers["peer_a"]).status_code == 403
    assert client.post(path, json=payload, headers=headers["admin_b"]).status_code == 404
    assert db.query(Availability).filter(Availability.person_id == person_id).first() is None

    created = client.post(path, json=payload, headers=headers["member_a"])
    assert created.status_code == 201


def _seed_solution_export(db, tenants):
    solution = Solution(
        org_id="tenant-a",
        solve_ms=1.0,
        hard_violations=0,
        soft_score=0.0,
        health_score=1.0,
        metrics={
            "fairness": {
                "stdev": 99.0,
                "per_person_counts": {
                    tenants["member_a"]["person_id"]: 1,
                    tenants["peer_a"]["person_id"]: 1,
                    tenants["member_b"]["person_id"]: 99,
                },
            }
        },
        created_at=utcnow(),
    )
    db.add(solution)
    db.flush()
    db.add_all(
        [
            Assignment(
                solution_id=solution.id,
                event_id="tenant-a-event",
                person_id=tenants["member_a"]["person_id"],
                role="guard",
            ),
            Assignment(
                solution_id=solution.id,
                event_id="tenant-a-event",
                person_id=tenants["peer_a"]["person_id"],
                role="forward",
            ),
        ]
    )
    db.commit()
    return solution


@pytest.mark.no_mock_auth
def test_solution_surface_is_admin_only_and_foreign_ids_are_hidden(client, db, tenants):
    solution = _seed_solution_export(db, tenants)
    headers = tenants["headers"]
    collection = "/api/v1/solutions/?org_id=tenant-a"

    assert client.get(collection).status_code == 401
    assert client.get(collection, headers=headers["member_a"]).status_code == 403
    own_collection = client.get(collection, headers=headers["admin_a"])
    assert own_collection.status_code == 200
    assert tenants["member_b"]["person_id"] not in str(own_collection.json())
    assert client.get(collection, headers=headers["admin_b"]).status_code == 403

    detail_path = f"/api/v1/solutions/{solution.id}"
    detail = client.get(detail_path, headers=headers["admin_a"])
    assert detail.status_code == 200
    assert tenants["member_b"]["person_id"] not in str(detail.json()["metrics"])
    assert client.get(detail_path, headers=headers["admin_b"]).status_code == 404

    assignments_path = f"/api/v1/solutions/{solution.id}/assignments"
    assert client.get(assignments_path, headers=headers["admin_a"]).status_code == 200
    assert client.get(assignments_path, headers=headers["admin_b"]).status_code == 404

    stats_path = f"/api/v1/solutions/{solution.id}/stats"
    stats = client.get(stats_path, headers=headers["admin_a"])
    assert stats.status_code == 200
    assert tenants["member_b"]["person_id"] not in str(stats.json())

    stream_path = f"/api/v1/solutions/{solution.id}/assignments/stream"
    assert client.get(stream_path, headers=headers["member_a"]).status_code == 403
    assert client.get(stream_path, headers=headers["admin_b"]).status_code == 404
    assert (
        client.get(
            "/api/v1/solutions/999999/assignments/stream", headers=headers["admin_b"]
        ).status_code
        == 404
    )

    before = db.query(Solution).count()
    response = client.post(
        "/api/v1/solutions/",
        json={"org_id": "tenant-b"},
        headers=headers["admin_a"],
    )
    assert response.status_code == 403
    assert db.query(Solution).count() == before

    response = client.delete(f"/api/v1/solutions/{solution.id}", headers=headers["admin_b"])
    assert response.status_code == 404
    assert db.query(Solution).filter(Solution.id == solution.id).one()


@pytest.mark.no_mock_auth
def test_solution_exports_filter_person_and_team_before_serialization(
    client, db, tenants, monkeypatch
):
    solution = _seed_solution_export(db, tenants)
    headers = tenants["headers"]
    team = seed_team(
        client,
        headers["admin_a"],
        "tenant-a",
        "tenant-a-team",
        "Starting Five",
        member_ids=[tenants["member_a"]["person_id"]],
    )
    assert team["id"] == "tenant-a-team"
    assert db.query(TeamMember).filter(TeamMember.team_id == "tenant-a-team").count() == 1

    # A corrupt cross-tenant child attached to the solution must be excluded at the query boundary.
    db.add(
        Assignment(
            solution_id=solution.id,
            event_id=tenants["event_b"]["id"],
            person_id=tenants["member_b"]["person_id"],
            role="foreign-role",
        )
    )
    db.commit()

    endpoint = f"/api/v1/solutions/{solution.id}/export"
    person_response = client.post(
        endpoint,
        json={"format": "json", "scope": f"person:{tenants['member_a']['person_id']}"},
        headers=headers["admin_a"],
    )
    assert person_response.status_code == 200, person_response.text
    person_assignments = person_response.json()["assignments"]
    assert len(person_assignments) == 1
    assert person_assignments[0]["event_id"] == "tenant-a-event"
    assert person_assignments[0]["assignees"] == [tenants["member_a"]["person_id"]]
    assert person_response.json()["metrics"]["fairness"] == {
        "stdev": 0.0,
        "per_person_counts": {tenants["member_a"]["person_id"]: 1},
    }

    team_response = client.post(
        endpoint,
        json={"format": "json", "scope": "team:tenant-a-team"},
        headers=headers["admin_a"],
    )
    assert team_response.status_code == 200, team_response.text
    assert team_response.json()["assignments"] == person_assignments
    assert team_response.json()["metrics"] == person_response.json()["metrics"]

    org_response = client.post(
        endpoint,
        json={"format": "json", "scope": "org"},
        headers=headers["admin_a"],
    )
    assert org_response.status_code == 200
    assert tenants["member_b"]["person_id"] not in str(org_response.json())

    csv_response = client.post(
        endpoint,
        json={"format": "csv", "scope": "team:tenant-a-team"},
        headers=headers["admin_a"],
    )
    assert csv_response.status_code == 200
    assert "Member A" in csv_response.text
    assert "Peer A" not in csv_response.text
    assert "Member B" not in csv_response.text

    captured_pdf = {}

    def _capture_pdf(org_name, events, people, assignments, events_db_map, blocked_dates_map):
        captured_pdf.update(
            {
                "org_name": org_name,
                "events": events,
                "people": people,
                "assignments": assignments,
                "events_db_map": events_db_map,
                "blocked_dates_map": blocked_dates_map,
            }
        )
        return BytesIO(b"%PDF-filtered")

    monkeypatch.setattr("api.routers.solutions.generate_schedule_pdf", _capture_pdf)
    pdf_response = client.post(
        endpoint,
        json={"format": "pdf", "scope": "team:tenant-a-team"},
        headers=headers["admin_a"],
    )
    assert pdf_response.status_code == 200
    assert set(captured_pdf["people"]) == {tenants["member_a"]["person_id"]}
    assert captured_pdf["assignments"] == {"tenant-a-event": [tenants["member_a"]["person_id"]]}
    assert "Member B" not in str(captured_pdf)

    ics_response = client.post(
        endpoint,
        json={"format": "ics", "scope": "team:tenant-a-team"},
        headers=headers["admin_a"],
    )
    assert ics_response.status_code == 501
    assert "Member A" not in ics_response.text

    for scope, expected_status in (
        (f"person:{tenants['member_b']['person_id']}", 404),
        ("team:missing-team", 404),
        ("unexpected", 400),
    ):
        response = client.post(
            endpoint,
            json={"format": "json", "scope": scope},
            headers=headers["admin_a"],
        )
        assert response.status_code == expected_status
        assert "Member B" not in response.text

    assert (
        client.post(
            endpoint,
            json={"format": "json", "scope": "org"},
            headers=headers["admin_b"],
        ).status_code
        == 404
    )
