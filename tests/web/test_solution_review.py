"""Sprint 11.18 — admin solution review (assignments + stats)."""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="sr_org", email="sradmin@web.test"):
    seed_person(db, person_id="sr_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _seed_solution(db, org):
    vol = seed_person(db, person_id=f"{org}_v", org_id=org, email=f"{org}v@web.test")
    sol = Solution(
        org_id=org,
        hard_violations=0,
        soft_score=1.5,
        health_score=98.0,
        solve_ms=12.0,
    )
    db.add(sol)
    db.add(
        Event(
            id=f"{org}_ev",
            org_id=org,
            type="Sunday Service",
            start_time=datetime(2099, 6, 7, 10, 0),
            end_time=datetime(2099, 6, 7, 11, 30),
        )
    )
    db.commit()
    db.refresh(sol)
    db.add(
        Assignment(
            solution_id=sol.id,
            event_id=f"{org}_ev",
            person_id=vol.id,
            role="usher",
            status="confirmed",
        )
    )
    db.commit()
    return sol


def test_solution_review_renders(client, db):
    token = _admin(client, db, org="sr_o1", email="sr1@web.test")
    sol = _seed_solution(db, "sr_o1")
    resp = client.get(f"/a/solution/{sol.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert f"Solution #{sol.id}" in resp.text
    assert "Health" in resp.text
    assert "Sunday Service" in resp.text  # assignments segment
    assert "Fairness stdev" in resp.text  # stats segment
    assert "Web User" in resp.text  # assignee chip


def test_solution_review_404_unknown(client, db):
    token = _admin(client, db, org="sr_o2", email="sr2@web.test")
    resp = client.get("/a/solution/999999", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()


def test_solution_review_404_other_org(client, db):
    token = _admin(client, db, org="sr_o3", email="sr3@web.test")
    other_sol = _seed_solution(db, "sr_other")
    resp = client.get(f"/a/solution/{other_sol.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404


def test_solution_review_requires_admin(client, db):
    seed_person(db, person_id="sr_vol", email="srvol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "srvol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/solution/1", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303


def test_solution_review_requires_auth(client):
    assert client.get("/a/solution/1").status_code == 303
