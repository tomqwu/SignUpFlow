"""Saved rules change API solve results and preserve selected role slots."""

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, Availability, Constraint
from tests.api.conftest import auth_headers, seed_event, seed_org, seed_user

pytestmark = pytest.mark.no_mock_auth


def _solve(client, headers: dict, org_id: str, start: datetime) -> dict:
    response = client.post(
        "/api/v1/solver/solve",
        json={
            "org_id": org_id,
            "from_date": start.date().isoformat(),
            "to_date": (start + timedelta(days=7)).date().isoformat(),
            "mode": "strict",
            "change_min": False,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_solve_delete_hard_cap_changes_assignments(client, db):
    org_id = "saved-cap"
    email = "admin@saved-cap.example"
    password = "AdminPass123!"
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", password)
    volunteer = seed_user(
        client,
        org_id,
        "volunteer@saved-cap.example",
        "Volunteer",
        roles=["volunteer", "usher"],
    )
    headers = auth_headers(client, email, password)
    start = datetime.now() + timedelta(days=21)
    for index in range(2):
        seed_event(
            client,
            headers,
            org_id,
            f"service-{index}",
            event_type="service",
            days_from_now=21 + index,
            duration_hours=1,
            role_counts={"usher": 1},
        )

    created = client.post(
        "/api/v1/constraints/",
        json={
            "org_id": org_id,
            "key": "one-per-week",
            "type": "hard",
            "predicate": "max_assignments",
            "params": {"period": "P7D", "max_count": 1, "applies_to": ["service"]},
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text

    constrained = _solve(client, headers, org_id, start)
    constrained_rows = (
        db.query(Assignment).filter(Assignment.solution_id == constrained["solution_id"]).all()
    )
    assert [(row.event_id, row.person_id, row.role) for row in constrained_rows] == [
        ("service-0", volunteer["person_id"], "usher")
    ]

    deleted = client.delete(f"/api/v1/constraints/{created.json()['id']}", headers=headers)
    assert deleted.status_code == 204
    unconstrained = _solve(client, headers, org_id, start)
    unconstrained_rows = (
        db.query(Assignment).filter(Assignment.solution_id == unconstrained["solution_id"]).all()
    )
    assert [(row.event_id, row.person_id, row.role) for row in unconstrained_rows] == [
        ("service-0", volunteer["person_id"], "usher"),
        ("service-1", volunteer["person_id"], "usher"),
    ]


def test_constraint_write_rejects_unsupported_rule_without_mutation(client, db):
    org_id = "saved-invalid"
    email = "admin@saved-invalid.example"
    password = "AdminPass123!"
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", password)
    headers = auth_headers(client, email, password)

    response = client.post(
        "/api/v1/constraints/",
        json={
            "org_id": org_id,
            "key": "arbitrary-code",
            "type": "hard",
            "predicate": "min_gap_hours_satisfied(person_id, 12)",
            "params": {"min_hours": 12},
        },
        headers=headers,
    )

    assert response.status_code == 422
    assert "unsupported predicate" in response.text
    assert db.query(Constraint).filter(Constraint.org_id == org_id).count() == 0


def test_solve_rejects_historical_malformed_rrule_with_record_identity(client, db):
    org_id = "saved-invalid-rrule"
    email = "admin@saved-invalid-rrule.example"
    password = "AdminPass123!"
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", password)
    volunteer = seed_user(
        client,
        org_id,
        "volunteer@saved-invalid-rrule.example",
        "Volunteer",
        roles=["volunteer", "usher"],
    )
    headers = auth_headers(client, email, password)
    start = datetime.now() + timedelta(days=21)
    seed_event(
        client,
        headers,
        org_id,
        "service",
        event_type="service",
        days_from_now=21,
        role_counts={"usher": 1},
    )
    availability = Availability(
        person_id=volunteer["person_id"],
        rrule="FREQ=NOT-A-FREQUENCY",
        extra_data={},
    )
    db.add(availability)
    db.commit()

    response = client.post(
        "/api/v1/solver/solve",
        json={
            "org_id": org_id,
            "from_date": start.date().isoformat(),
            "to_date": (start + timedelta(days=1)).date().isoformat(),
            "mode": "strict",
            "change_min": False,
        },
        headers=headers,
    )

    assert response.status_code == 422
    assert f"Availability {availability.id}" in response.text
    assert volunteer["person_id"] in response.text
    assert db.query(Assignment).count() == 0
