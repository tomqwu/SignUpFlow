#!/usr/bin/env python3
"""Integration tests: availability router (Sprint 4 PR 4.6b).

Tests the /api/v1/availability endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /availability/                                     - Create root record
- GET    /availability/{person_id}/timeoff                  - List time-off
- POST   /availability/{person_id}/timeoff                  - Add time-off
- PATCH  /availability/{person_id}/timeoff/{id}             - Update time-off
- DELETE /availability/{person_id}/timeoff/{id}             - Delete time-off
- GET    /availability/{person_id}/exceptions               - List exceptions
- POST   /availability/{person_id}/exceptions               - Add exception
- DELETE /availability/{person_id}/exceptions/{id}          - Delete exception
- GET    /availability/{person_id}/rrule                    - Get rrule
- PUT    /availability/{person_id}/rrule                    - Set rrule
- DELETE /availability/{person_id}/rrule                    - Clear rrule
"""

import random
import time
from datetime import date, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def setup_person(api_server, api_base):
    """Create an org + admin (who is a Person we can query for). Return context."""
    client = httpx.Client()

    org_id = _unique("avail_org")
    org_response = client.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Availability Org {org_id}", "region": "US", "config": {}},
    )
    assert org_response.status_code == 201, org_response.text

    email = f"person_{org_id}@test.com"
    signup_response = client.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Availability User",
            "email": email,
            "password": "AvailPass123!",
        },
    )
    assert signup_response.status_code == 201, signup_response.text
    admin_data = signup_response.json()

    client.headers["Authorization"] = f"Bearer {admin_data['token']}"
    return {
        "client": client,
        "org_id": org_id,
        "person_id": admin_data["person_id"],
        "api_base": api_base,
    }


class TestCreateAvailability:
    """POST /availability/?person_id=…"""

    def test_create_first_time_returns_id(self, setup_person):
        setup = setup_person
        resp = setup["client"].post(
            f"{setup['api_base']}/availability/",
            params={"person_id": setup["person_id"]},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["person_id"] == setup["person_id"]
        assert isinstance(body["availability_id"], int)

    def test_create_missing_person_returns_404(self, setup_person):
        setup = setup_person
        resp = setup["client"].post(
            f"{setup['api_base']}/availability/",
            params={"person_id": f"ghost_{int(time.time())}"},
        )
        assert resp.status_code == 404


class TestTimeOff:
    """/availability/{person_id}/timeoff — add, list, patch, delete."""

    def test_list_empty_when_no_availability(self, setup_person):
        setup = setup_person
        resp = setup["client"].get(f"{setup['api_base']}/availability/{setup['person_id']}/timeoff")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["timeoff"] == []

    def test_add_timeoff_success(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=14)
        end = start + timedelta(days=2)

        resp = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
            json={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "reason": "Family trip",
            },
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["start_date"] == start.isoformat()
        assert body["end_date"] == end.isoformat()
        assert body["reason"] == "Family trip"

    def test_add_timeoff_invalid_range_rejected(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=20)
        end = date.today() + timedelta(days=10)  # before start

        resp = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
            json={"start_date": start.isoformat(), "end_date": end.isoformat()},
        )
        assert resp.status_code == 400

    def test_add_overlapping_timeoff_rejected(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=30)
        end = start + timedelta(days=3)

        # First block succeeds
        first = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
            json={"start_date": start.isoformat(), "end_date": end.isoformat()},
        )
        assert first.status_code == 201, first.text

        # Overlapping block is rejected with 409
        overlap = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
            json={
                "start_date": (start + timedelta(days=1)).isoformat(),
                "end_date": (end + timedelta(days=2)).isoformat(),
            },
        )
        assert overlap.status_code == 409

    def test_list_returns_added_timeoff(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=60)
        end = start + timedelta(days=1)
        add = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
            json={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "reason": "Vacation",
            },
        )
        assert add.status_code == 201

        resp = setup["client"].get(f"{setup['api_base']}/availability/{setup['person_id']}/timeoff")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert any(t["start_date"] == start.isoformat() for t in body["timeoff"])

    def test_patch_timeoff_updates_reason_and_dates(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=90)
        end = start + timedelta(days=1)
        added = (
            setup["client"]
            .post(
                f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
                json={
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "reason": "old",
                },
            )
            .json()
        )

        new_start = start + timedelta(days=1)
        new_end = end + timedelta(days=2)
        resp = setup["client"].patch(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff/{added['id']}",
            json={
                "start_date": new_start.isoformat(),
                "end_date": new_end.isoformat(),
                "reason": "new",
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["start_date"] == new_start.isoformat()
        assert body["reason"] == "new"

    def test_delete_timeoff_removes_it(self, setup_person):
        setup = setup_person
        start = date.today() + timedelta(days=120)
        end = start + timedelta(days=1)
        added = (
            setup["client"]
            .post(
                f"{setup['api_base']}/availability/{setup['person_id']}/timeoff",
                json={"start_date": start.isoformat(), "end_date": end.isoformat()},
            )
            .json()
        )

        resp = setup["client"].delete(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff/{added['id']}"
        )
        assert resp.status_code == 204

        follow = setup["client"].get(
            f"{setup['api_base']}/availability/{setup['person_id']}/timeoff"
        )
        assert added["id"] not in {t["id"] for t in follow.json()["timeoff"]}


class TestAvailabilityExceptions:
    """/availability/{person_id}/exceptions — single-date blocks."""

    def test_list_empty_when_no_availability(self, setup_person):
        setup = setup_person
        resp = setup["client"].get(
            f"{setup['api_base']}/availability/{setup['person_id']}/exceptions"
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_exception_creates_row(self, setup_person):
        setup = setup_person
        d = (date.today() + timedelta(days=45)).isoformat()

        resp = setup["client"].post(
            f"{setup['api_base']}/availability/{setup['person_id']}/exceptions",
            json={"exception_date": d},
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["exception_date"] == d

    def test_add_exception_is_idempotent(self, setup_person):
        setup = setup_person
        d = (date.today() + timedelta(days=50)).isoformat()

        first = (
            setup["client"]
            .post(
                f"{setup['api_base']}/availability/{setup['person_id']}/exceptions",
                json={"exception_date": d},
            )
            .json()
        )
        second = (
            setup["client"]
            .post(
                f"{setup['api_base']}/availability/{setup['person_id']}/exceptions",
                json={"exception_date": d},
            )
            .json()
        )
        assert first["id"] == second["id"]

    def test_delete_exception(self, setup_person):
        setup = setup_person
        d = (date.today() + timedelta(days=70)).isoformat()
        added = (
            setup["client"]
            .post(
                f"{setup['api_base']}/availability/{setup['person_id']}/exceptions",
                json={"exception_date": d},
            )
            .json()
        )

        resp = setup["client"].delete(
            f"{setup['api_base']}/availability/{setup['person_id']}/exceptions/{added['id']}"
        )
        assert resp.status_code == 204


class TestAvailabilityRrule:
    """/availability/{person_id}/rrule — get/set/clear the recurring rule."""

    def test_get_rrule_when_none_returns_null(self, setup_person):
        setup = setup_person
        resp = setup["client"].get(f"{setup['api_base']}/availability/{setup['person_id']}/rrule")
        assert resp.status_code == 200
        assert resp.json() == {"rrule": None}

    def test_set_and_get_rrule(self, setup_person):
        setup = setup_person
        rule = "FREQ=WEEKLY;BYDAY=SU"

        put = setup["client"].put(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule",
            json={"rrule": rule},
        )
        assert put.status_code == 200
        assert put.json()["rrule"] == rule

        get_resp = setup["client"].get(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule"
        )
        assert get_resp.json()["rrule"] == rule

    def test_clear_rrule_idempotent(self, setup_person):
        setup = setup_person
        # Clear when nothing set — still 204
        resp = setup["client"].delete(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule"
        )
        assert resp.status_code == 204

        # Set, then clear
        setup["client"].put(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule",
            json={"rrule": "FREQ=DAILY"},
        )
        resp2 = setup["client"].delete(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule"
        )
        assert resp2.status_code == 204

        get_resp = setup["client"].get(
            f"{setup['api_base']}/availability/{setup['person_id']}/rrule"
        )
        assert get_resp.json() == {"rrule": None}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
