#!/usr/bin/env python3
"""Integration tests: solver router (Sprint 4 PR 4.6b).

Drives POST /api/v1/solver/solve over real HTTP against the session-
scoped uvicorn api_server. Locks in:
- Admin path produces assignments + persists a Solution row
- Volunteer 403 + cross-org admin 403
- 404 on missing org
- 400 when no events fall in the requested [from_date, to_date]
- Solver honors real availability (regression for the previously
  hard-coded `availability=[]` in the router)
"""

import random
import time
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


def _future(days: int, hours: int = 0) -> str:
    dt = datetime.now(UTC) + timedelta(days=days, hours=hours)
    return dt.isoformat()


def _date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


@pytest.fixture
def solver_org(api_server, api_base):
    """Provision two orgs; org1 has an admin, a volunteer, and one event
    14 days out. org2 has only an admin, so cross-org 403s are real.
    """
    marker = _unique("solver_org")
    org1_id = f"{marker}_a"
    org2_id = f"{marker}_b"

    bootstrap = httpx.Client()

    for oid in (org1_id, org2_id):
        r = bootstrap.post(
            f"{api_base}/organizations/",
            json={"id": oid, "name": f"Solver Setup {oid}", "region": "US", "config": {}},
        )
        assert r.status_code == 201, r.text

    def _signup(org_id: str, name: str, email: str, roles: list[str] | None = None) -> dict:
        body = {
            "org_id": org_id,
            "name": name,
            "email": email,
            "password": "TestPass123!",
        }
        if roles is not None:
            body["roles"] = roles
        r = bootstrap.post(f"{api_base}/auth/signup", json=body)
        assert r.status_code == 201, r.text
        return r.json()

    admin1 = _signup(org1_id, "Solver Admin", f"admin_{marker}@t.com")
    admin2 = _signup(org2_id, "Other Admin", f"admin2_{marker}@t.com")
    vol1 = _signup(org1_id, "Vol Solver", f"vol_{marker}@t.com", roles=["volunteer"])
    bootstrap.close()

    def _client(token: str) -> httpx.Client:
        c = httpx.Client()
        c.headers["Authorization"] = f"Bearer {token}"
        return c

    admin1_c = _client(admin1["token"])
    admin2_c = _client(admin2["token"])
    vol1_c = _client(vol1["token"])

    # Seed one event 14 days out with a single volunteer role slot.
    event_id = _unique("evt")
    event_start_days = 14
    r = admin1_c.post(
        f"{api_base}/events/",
        json={
            "id": event_id,
            "org_id": org1_id,
            "type": "meeting",
            "start_time": _future(event_start_days),
            "end_time": _future(event_start_days, hours=2),
            "extra_data": {"role_counts": {"volunteer": 1}},
        },
    )
    assert r.status_code == 201, r.text

    yield {
        "marker": marker,
        "org1_id": org1_id,
        "org2_id": org2_id,
        "admin1_client": admin1_c,
        "admin2_client": admin2_c,
        "vol1_client": vol1_c,
        "vol1_id": vol1["person_id"],
        "event_id": event_id,
        "event_start_days": event_start_days,
        "api_base": api_base,
    }

    admin1_c.close()
    admin2_c.close()
    vol1_c.close()


def _solve_window(days_before: int, days_after: int) -> dict:
    """Wide window bracketing the seeded event at day 14."""
    return {
        "from_date": _date(14 - days_before),
        "to_date": _date(14 + days_after),
        "mode": "relaxed",
        "change_min": False,
    }


class TestSolverAuth:
    """Auth gates on POST /solver/solve."""

    def test_admin_solves_and_persists_solution(self, solver_org):
        data = solver_org
        resp = data["admin1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": data["org1_id"], **_solve_window(2, 2)},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["solution_id"] is not None
        assert body["assignment_count"] >= 1
        assert "metrics" in body
        assert body["metrics"]["health_score"] >= 0
        # Solution should show up in the solutions list.
        list_resp = data["admin1_client"].get(
            f"{data['api_base']}/solutions/",
            params={"org_id": data["org1_id"]},
        )
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] >= 1

    def test_volunteer_forbidden(self, solver_org):
        data = solver_org
        resp = data["vol1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": data["org1_id"], **_solve_window(2, 2)},
        )
        assert resp.status_code == 403

    def test_cross_org_admin_forbidden(self, solver_org):
        data = solver_org
        resp = data["admin2_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": data["org1_id"], **_solve_window(2, 2)},
        )
        assert resp.status_code == 403

    def test_unauthenticated(self, solver_org):
        data = solver_org
        with httpx.Client() as anon:
            resp = anon.post(
                f"{data['api_base']}/solver/solve",
                json={"org_id": data["org1_id"], **_solve_window(2, 2)},
            )
        assert resp.status_code in (401, 403)


class TestSolverErrors:
    """Error paths on POST /solver/solve."""

    def test_missing_org_returns_404(self, solver_org):
        data = solver_org
        resp = data["admin1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": f"ghost_{data['marker']}", **_solve_window(2, 2)},
        )
        assert resp.status_code == 404

    def test_empty_date_range_returns_400(self, solver_org):
        data = solver_org
        # Window well before the seeded event (day 14).
        resp = data["admin1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={
                "org_id": data["org1_id"],
                "from_date": _date(-30),
                "to_date": _date(-10),
                "mode": "strict",
                "change_min": False,
            },
        )
        assert resp.status_code == 400

    def test_malformed_body_422(self, solver_org):
        data = solver_org
        resp = data["admin1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": data["org1_id"]},  # missing from_date/to_date
        )
        assert resp.status_code == 422


class TestSolverHonorsAvailability:
    """Regression: the solver must load real Availability + VacationPeriod
    rows for the org and skip volunteers whose time-off covers the event.

    This locks in Sprint 3-E: before that fix the router passed a hard-
    coded `availability=[]` to the solver and time-off was silently
    ignored.
    """

    def test_time_off_covering_event_prevents_assignment(self, solver_org):
        data = solver_org

        # Add a second volunteer who WILL be available so the event can
        # still be filled — the interesting assertion is that vol1 (with
        # time off) is not the one assigned.
        bootstrap = httpx.Client()
        r = bootstrap.post(
            f"{data['api_base']}/auth/signup",
            json={
                "org_id": data["org1_id"],
                "name": "Vol Present",
                "email": f"present_{data['marker']}@t.com",
                "password": "TestPass123!",
                "roles": ["volunteer"],
            },
        )
        assert r.status_code == 201, r.text
        present_id = r.json()["person_id"]

        # Block vol1 across the event day. This endpoint is currently
        # anon per its router, hence the bare httpx.Client.
        timeoff_start = _date(data["event_start_days"] - 1)
        timeoff_end = _date(data["event_start_days"] + 1)
        r = bootstrap.post(
            f"{data['api_base']}/availability/{data['vol1_id']}/timeoff",
            json={
                "start_date": timeoff_start,
                "end_date": timeoff_end,
                "reason": "Vacation",
            },
        )
        assert r.status_code in (200, 201), r.text
        bootstrap.close()

        # Solve.
        resp = data["admin1_client"].post(
            f"{data['api_base']}/solver/solve",
            json={"org_id": data["org1_id"], **_solve_window(2, 2)},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["assignment_count"] >= 1

        # Pull the fresh assignments for the org and confirm vol1 was NOT
        # picked for this event. (assignments/all is a debug-shaped list,
        # not ListResponse — that's a separate cleanup.)
        assignments = data["admin1_client"].get(
            f"{data['api_base']}/events/assignments/all",
            params={"org_id": data["org1_id"]},
        )
        assert assignments.status_code == 200
        rows = assignments.json()["assignments"]
        for row in rows:
            if row["event_id"] == data["event_id"]:
                assert row["person_id"] != data["vol1_id"], (
                    "Solver assigned vol1 despite covering time-off — " "availability was ignored."
                )
                assert row["person_id"] == present_id
