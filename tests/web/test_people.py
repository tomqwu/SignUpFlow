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


def test_people_page_exposes_scheduling_qualification_controls(client, db):
    token = _admin(client, db, org="p_roles", email="roles-admin@web.test")
    seed_person(
        db,
        person_id="p_qualified",
        org_id="p_roles",
        email="qualified@web.test",
        roles=["volunteer", "usher"],
    )

    response = client.get("/a/people", cookies={SESSION_COOKIE: token})

    assert response.status_code == 200
    assert 'action="/a/people/p_qualified/qualifications"' in response.text
    assert 'value="usher"' in response.text


def test_admin_updates_qualifications_without_changing_access(client, db):
    token = _admin(client, db, org="p_update", email="update-admin@web.test")
    member = seed_person(
        db,
        person_id="p_update_member",
        org_id="p_update",
        email="update-member@web.test",
        roles=["volunteer", "usher"],
    )

    response = client.post(
        "/a/people/p_update_member/qualifications",
        data={"qualifications": "sound; children_leader"},
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    db.refresh(member)
    assert member.roles == ["volunteer", "sound", "children_leader"]
    assert "Qualifications saved" in response.text


def test_qualification_update_rejects_admin_alias_and_preserves_roles(client, db):
    token = _admin(client, db, org="p_reject", email="reject-admin@web.test")
    member = seed_person(
        db,
        person_id="p_reject_member",
        org_id="p_reject",
        email="reject-member@web.test",
        roles=["volunteer", "usher"],
    )

    response = client.post(
        "/a/people/p_reject_member/qualifications",
        data={"qualifications": "usher, ADMIN"},
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 400
    db.refresh(member)
    assert member.roles == ["volunteer", "usher"]
    assert "reserved" in response.text.lower()


def test_qualification_update_cannot_target_another_organization(client, db):
    token = _admin(client, db, org="p_owner", email="owner-admin@web.test")
    outsider = seed_person(
        db,
        person_id="p_outside_member",
        org_id="p_outside",
        email="outside-member@web.test",
        roles=["volunteer", "coach"],
    )

    response = client.post(
        "/a/people/p_outside_member/qualifications",
        data={"qualifications": "scorekeeper"},
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 404
    db.refresh(outsider)
    assert outsider.roles == ["volunteer", "coach"]


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
