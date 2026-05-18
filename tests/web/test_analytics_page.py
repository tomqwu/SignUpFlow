"""Marathon P1.8 — analytics drill-down page."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_analytics_admin_only(client, db):
    seed_person(db, person_id="an_vol", email="anvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "anvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/analytics").status_code == 303
    assert client.get("/a/analytics", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="an_o1", email="an1@web.test")
    resp = client.get("/a/analytics", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Analytics" in resp.text
    assert "Participation" in resp.text
    assert "Schedule health" in resp.text
    assert "Burnout risk" in resp.text


def test_analytics_filters_applied_and_clamped(client, db):
    tok = _admin(client, db, org="an_o2", email="an2@web.test")
    ok = client.get("/a/analytics?days=7&threshold=2", cookies={SESSION_COOKIE: tok})
    assert ok.status_code == 200
    assert "last 7 days" in ok.text
    assert "≥ 2 in 30 days" in ok.text

    # Out-of-range values fall back to defaults (30 / 4).
    clamped = client.get("/a/analytics?days=9999&threshold=0", cookies={SESSION_COOKIE: tok})
    assert clamped.status_code == 200
    assert "last 30 days" in clamped.text
    assert "≥ 4 in 30 days" in clamped.text


def test_dashboard_links_to_analytics(client, db):
    tok = _admin(client, db, org="an_o3", email="an3@web.test")
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert dash.status_code == 200
    assert 'href="/a/analytics"' in dash.text
