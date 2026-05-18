"""Sprint 11.19 — solution-review live SSE (cookie-authed mirror).

The SSE happy-path body is an infinite generator (event_bus.subscribe);
a sync TestClient would hang trying to read it, so we exercise the
guard paths (auth / ownership) that short-circuit BEFORE streaming
starts. The event_bus round-trip itself is covered by the Sprint 10.4
API tests (tests/api/test_solutions_stream.py) — this route is a thin
cookie-authed mirror over the same topic.
"""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="se_org", email="seadmin@web.test"):
    seed_person(db, person_id="se_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _seed_solution(db, org):
    vol = seed_person(db, person_id=f"{org}_v", org_id=org, email=f"{org}v@web.test")
    sol = Solution(
        org_id=org,
        hard_violations=0,
        soft_score=1.0,
        health_score=95.0,
        solve_ms=8.0,
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


def test_review_page_wires_sse(client, db):
    token = _admin(client, db, org="se_o1", email="se1@web.test")
    sol = _seed_solution(db, "se_o1")
    resp = client.get(f"/a/solution/{sol.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'hx-ext="sse"' in resp.text
    assert f'sse-connect="/a/solution/{sol.id}/stream"' in resp.text
    assert 'hx-trigger="sse:message"' in resp.text
    assert 'id="solution-assignments"' in resp.text


def test_assignments_fragment_renders(client, db):
    token = _admin(client, db, org="se_o2", email="se2@web.test")
    sol = _seed_solution(db, "se_o2")
    resp = client.get(
        f"/a/solution/{sol.id}/assignments",
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="solution-assignments"' in resp.text
    assert "Sunday Service" in resp.text
    assert "Web User" in resp.text


def test_assignments_fragment_404_other_org(client, db):
    token = _admin(client, db, org="se_o3", email="se3@web.test")
    other = _seed_solution(db, "se_other")
    resp = client.get(
        f"/a/solution/{other.id}/assignments",
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 404


def test_stream_404_for_unknown_solution(client, db):
    token = _admin(client, db, org="se_o4", email="se4@web.test")
    # Unknown id → HTTPException raised before the streaming body, so
    # the sync client doesn't hang.
    resp = client.get("/a/solution/999999/stream", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404


def test_stream_requires_admin(client, db):
    seed_person(db, person_id="se_vol", email="sevol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "sevol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/solution/1/stream", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303


def test_stream_requires_auth(client):
    assert client.get("/a/solution/1/stream").status_code == 303
    assert client.get("/a/solution/1/assignments").status_code == 303
