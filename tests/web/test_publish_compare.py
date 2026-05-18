"""Sprint 11.20 — publish solution + compare."""

from __future__ import annotations

from api.models import Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="pc_org", email="pcadmin@web.test"):
    seed_person(db, person_id="pc_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _sol(db, org):
    s = Solution(
        org_id=org,
        hard_violations=0,
        soft_score=1.0,
        health_score=90.0,
        solve_ms=5.0,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_publish_marks_solution_and_unpublishes_prior(client, db):
    token = _admin(client, db, org="pc_o1", email="pc1@web.test")
    s1 = _sol(db, "pc_o1")
    s2 = _sol(db, "pc_o1")
    # Publish s1.
    r1 = client.post(f"/a/solution/{s1.id}/publish", cookies={SESSION_COOKIE: token})
    assert r1.status_code == 200
    assert "Published" in r1.text
    db.refresh(s1)
    assert s1.is_published is True
    # Publish s2 → s1 auto-unpublished.
    r2 = client.post(f"/a/solution/{s2.id}/publish", cookies={SESSION_COOKIE: token})
    assert r2.status_code == 200
    db.refresh(s1)
    db.refresh(s2)
    assert s2.is_published is True
    assert s1.is_published is False


def test_publish_404_other_org(client, db):
    token = _admin(client, db, org="pc_o2", email="pc2@web.test")
    other = _sol(db, "pc_other")
    resp = client.post(f"/a/solution/{other.id}/publish", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404


def test_review_page_shows_publish_control(client, db):
    token = _admin(client, db, org="pc_o3", email="pc3@web.test")
    s = _sol(db, "pc_o3")
    resp = client.get(f"/a/solution/{s.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="publish-state"' in resp.text
    assert "Publish this solution" in resp.text
    assert "Compare with another solution" in resp.text


def test_compare_page_needs_two(client, db):
    token = _admin(client, db, org="pc_o4", email="pc4@web.test")
    _sol(db, "pc_o4")  # only one
    resp = client.get("/a/compare", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Need at least two solutions" in resp.text


def test_compare_runs_diff(client, db):
    token = _admin(client, db, org="pc_o5", email="pc5@web.test")
    a = _sol(db, "pc_o5")
    b = _sol(db, "pc_o5")
    page = client.get("/a/compare", cookies={SESSION_COOKIE: token})
    assert "Solution A" in page.text and "Solution B" in page.text
    resp = client.post(
        "/a/compare",
        data={"solution_a": a.id, "solution_b": b.id},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="compare-result"' in resp.text
    assert "Moves" in resp.text  # diff KPI grid rendered


def test_compare_other_org_rejected(client, db):
    token = _admin(client, db, org="pc_o6", email="pc6@web.test")
    a = _sol(db, "pc_o6")
    other = _sol(db, "pc_other2")
    resp = client.post(
        "/a/compare",
        data={"solution_a": a.id, "solution_b": other.id},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 404


def test_publish_compare_require_admin(client, db):
    seed_person(db, person_id="pc_vol", email="pcvol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "pcvol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    assert client.post("/a/solution/1/publish", cookies={SESSION_COOKIE: token}).status_code == 303
    assert client.get("/a/compare", cookies={SESSION_COOKIE: token}).status_code == 303


def test_publish_compare_require_auth(client):
    assert client.post("/a/solution/1/publish").status_code == 303
    assert client.get("/a/compare").status_code == 303
