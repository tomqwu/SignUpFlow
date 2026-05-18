"""Sprint 11.17 — admin run solver."""

from __future__ import annotations

from datetime import datetime

from api.models import Event, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="s_org", email="sadmin@web.test"):
    seed_person(db, person_id="s_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_solver_form_renders(client, db):
    token = _admin(client, db)
    resp = client.get("/a/solver", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Run Solver" in resp.text
    assert 'name="from_date"' in resp.text
    assert 'hx-post="/a/solver/run"' in resp.text
    assert "Strict" in resp.text and "Relaxed" in resp.text


def test_solver_run_creates_solution(client, db):
    token = _admin(client, db, org="s_org2", email="sadmin2@web.test")
    # Solver needs at least one event in range (it 400s on an empty
    # schedule — correct behaviour).
    seed_person(db, person_id="s_vol2", org_id="s_org2", email="svol2@web.test")
    db.add(
        Event(
            id="s_ev",
            org_id="s_org2",
            type="Sunday Service",
            start_time=datetime(2099, 6, 7, 10, 0),
            end_time=datetime(2099, 6, 7, 11, 30),
        )
    )
    db.commit()
    resp = client.post(
        "/a/solver/run",
        data={
            "from_date": "2099-06-01",
            "to_date": "2099-06-30",
            "mode": "strict",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="solver-result"' in resp.text
    assert "Solution #" in resp.text
    assert "Review solution" in resp.text
    sol = (
        db.query(Solution).filter(Solution.org_id == "s_org2").order_by(Solution.id.desc()).first()
    )
    assert sol is not None


def test_solver_run_invalid_range_rejected(client, db):
    token = _admin(client, db, org="s_org3", email="sadmin3@web.test")
    resp = client.post(
        "/a/solver/run",
        data={
            "from_date": "not-a-date",
            "to_date": "2099-06-30",
            "mode": "strict",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 400
    assert "form-error" in resp.text


def test_solver_requires_admin(client, db):
    seed_person(db, person_id="s_vol", email="svol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "svol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    assert client.get("/a/solver", cookies={SESSION_COOKIE: token}).status_code == 303
    assert (
        client.post(
            "/a/solver/run",
            data={
                "from_date": "2099-06-01",
                "to_date": "2099-06-30",
                "mode": "strict",
            },
            cookies={SESSION_COOKIE: token},
        ).status_code
        == 303
    )


def test_solver_requires_auth(client):
    assert client.get("/a/solver").status_code == 303
    assert (
        client.post(
            "/a/solver/run",
            data={
                "from_date": "2099-06-01",
                "to_date": "2099-06-30",
                "mode": "strict",
            },
        ).status_code
        == 303
    )
