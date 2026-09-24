"""A recurring series must be schedulable like any other event.

Occurrences used to store the series' roles under ``role_requirements``, while
the solver, publication checks and event helpers read only ``role_counts``. So
a weekly series looked like it needed nobody: the solver left every
occurrence empty and nothing warned the coordinator. These tests hold the
series to the same path as a hand-made event: solved, fully staffed and
publishable, and still correct after its roles are edited.
"""

from collections import Counter
from datetime import date, timedelta

import pytest

from api.models import Assignment, Event, RecurringSeries
from api.timeutils import utcnow
from tests.api.conftest import (
    accept_invitation,
    auth_headers,
    seed_invitation,
    seed_org,
    seed_user,
)

ORG = "recurring-staffing-org"
ADMIN_EMAIL = "admin@recurring-staffing.org"
ADMIN_PW = "AdminPass123!"


def _org_with_ushers(client, count=3):
    seed_org(client, ORG)
    seed_user(client, ORG, ADMIN_EMAIL, "Admin", ADMIN_PW)
    headers = auth_headers(client, ADMIN_EMAIL, ADMIN_PW)
    for index in range(count):
        invitation = seed_invitation(
            client,
            headers,
            ORG,
            f"usher{index}@recurring-staffing.org",
            f"Usher {index}",
            roles=["usher"],
        )
        accept_invitation(client, invitation["token"])
    return headers


def _next_sunday() -> date:
    today = date.today()
    return today + timedelta(days=(6 - today.weekday()) % 7 or 7)


def _create_series(client, headers, roles, *, start=None, weeks=4):
    response = client.post(
        f"/api/v1/recurring-series?org_id={ORG}",
        json={
            "title": "Sunday service",
            "duration": 90,
            "location": "Sanctuary",
            "role_requirements": roles,
            "pattern_type": "weekly",
            "frequency_interval": 1,
            "selected_days": ["sunday"],
            "start_date": (start or _next_sunday()).isoformat(),
            "start_time": "10:00:00",
            "end_condition_type": "count",
            "occurrence_count": weeks,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def _occurrences(db, series_id):
    return (
        db.query(Event)
        .filter(Event.org_id == ORG, Event.series_id == series_id)
        .order_by(Event.start_time)
        .all()
    )


def _solve(client, headers, start, end):
    response = client.post(
        "/api/v1/solver/solve",
        json={"org_id": ORG, "from_date": start.isoformat(), "to_date": end.isoformat()},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.no_mock_auth
class TestRecurringSeriesIsSchedulable:
    def test_occurrences_carry_the_roles_the_solver_reads(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, {"usher": 2})
        for event in _occurrences(db, series_id):
            assert event.extra_data["role_counts"] == {"usher": 2}

    def test_solver_staffs_every_occurrence(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, {"usher": 2})
        sunday = _next_sunday()
        solution = _solve(client, headers, sunday, sunday + timedelta(weeks=4))

        assert solution["metrics"]["hard_violations"] == 0
        for event in _occurrences(db, series_id):
            rows = db.query(Assignment).filter(Assignment.event_id == event.id).all()
            assert Counter(a.role for a in rows) == {"usher": 2}, event.id

    def test_solved_series_can_be_published(self, client, db):
        headers = _org_with_ushers(client)
        _create_series(client, headers, {"usher": 2})
        sunday = _next_sunday()
        solution = _solve(client, headers, sunday, sunday + timedelta(weeks=4))
        published = client.post(
            f"/api/v1/solutions/{solution['solution_id']}/publish", headers=headers
        )
        assert published.status_code == 200, published.text

    def test_series_without_roles_asks_for_nobody(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, None)
        for event in _occurrences(db, series_id):
            assert not (event.extra_data or {}).get("role_counts")


@pytest.mark.no_mock_auth
class TestEditingSeriesRoles:
    def test_new_roles_reach_occurrences_that_have_not_happened(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, {"usher": 2})

        response = client.put(
            f"/api/v1/recurring-series/{series_id}", json={"usher": 3}, headers=headers
        )
        assert response.status_code == 200, response.text

        db.expire_all()
        for event in _occurrences(db, series_id):
            assert event.extra_data["role_counts"] == {"usher": 3}
        assert db.get(RecurringSeries, series_id).role_requirements == {"usher": 3}

    def test_an_individually_edited_occurrence_keeps_its_own_roles(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, {"usher": 2})
        edited = _occurrences(db, series_id)[1]
        edited.is_exception = True
        edited.extra_data = {**edited.extra_data, "role_counts": {"usher": 1}}
        db.commit()

        client.put(f"/api/v1/recurring-series/{series_id}", json={"usher": 3}, headers=headers)

        db.expire_all()
        assert db.get(Event, edited.id).extra_data["role_counts"] == {"usher": 1}

    def test_past_occurrences_keep_the_roles_they_were_served_with(self, client, db):
        headers = _org_with_ushers(client)
        series_id = _create_series(client, headers, {"usher": 2})
        past = _occurrences(db, series_id)[0]
        past.start_time = utcnow() - timedelta(days=7)
        past.end_time = past.start_time + timedelta(minutes=90)
        db.commit()

        client.put(f"/api/v1/recurring-series/{series_id}", json={"usher": 3}, headers=headers)

        db.expire_all()
        assert db.get(Event, past.id).extra_data["role_counts"] == {"usher": 2}
