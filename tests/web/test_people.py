"""Sprint 11.13 — admin people list + search."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="p_org", email="padmin@web.test"):
    seed_person(db, person_id="p_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_people_lists_org_members(client, db):
    token = _admin(client, db)
    seed_person(db, person_id="p_a", org_id="p_org", email="alice@web.test")
    seed_person(db, person_id="p_b", org_id="p_org", email="bob@web.test")
    resp = client.get("/a/people", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "People" in resp.text
    assert "alice@web.test" in resp.text
    assert "bob@web.test" in resp.text
    assert "padmin@web.test" in resp.text  # admin themselves listed


def test_people_search_filters(client, db):
    token = _admin(client, db, org="p_org2", email="padmin2@web.test")
    seed_person(
        db,
        person_id="p_zoe",
        org_id="p_org2",
        email="zoe@web.test",
    )
    # default seed name is "Web User"; override email distinct enough
    resp = client.get("/a/people/list?q=zoe", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="people-list"' in resp.text
    assert "zoe@web.test" in resp.text
    assert "padmin2@web.test" not in resp.text  # filtered out


def test_people_search_no_match(client, db):
    token = _admin(client, db, org="p_org3", email="padmin3@web.test")
    resp = client.get("/a/people/list?q=nobody-xyz", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "No people match" in resp.text


def test_people_scoped_to_org(client, db):
    token = _admin(client, db, org="p_org4", email="padmin4@web.test")
    seed_person(
        db,
        person_id="p_outsider",
        org_id="other_org",
        email="outsider@web.test",
    )
    resp = client.get("/a/people", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "outsider@web.test" not in resp.text


def test_people_requires_admin(client, db):
    seed_person(db, person_id="p_vol", email="pvol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "pvol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/people", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_people_requires_auth(client):
    assert client.get("/a/people").status_code == 303
    assert client.get("/a/people/list").status_code == 303
