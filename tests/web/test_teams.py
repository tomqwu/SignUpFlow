"""Marathon P1.3 — teams admin CRUD + membership."""

from __future__ import annotations

from api.models import Team, TeamMember
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="t_org", email="tadmin@web.test"):
    seed_person(db, person_id="t_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _team_id(db, org):
    return db.query(Team).filter(Team.org_id == org).first().id


def test_teams_page_admin_only(client, db):
    seed_person(db, person_id="t_vol", email="tvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "tvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/teams", cookies={SESSION_COOKIE: vtok}).status_code == 303
    assert client.get("/a/teams").status_code == 303

    atok = _admin(client, db, org="t_o1", email="t1@web.test")
    resp = client.get("/a/teams", cookies={SESSION_COOKIE: atok})
    assert resp.status_code == 200
    assert 'id="teams-list"' in resp.text
    assert "New team" in resp.text


def test_team_create_update_delete(client, db):
    tok = _admin(client, db, org="t_o2", email="t2@web.test")
    # Create
    r = client.post(
        "/a/teams/create",
        data={"name": "Worship", "description": "Sunday band"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert "Worship" in r.text
    tid = _team_id(db, "t_o2")

    # Name required
    bad = client.post("/a/teams/create", data={"name": "  "}, cookies={SESSION_COOKIE: tok})
    assert bad.status_code == 400
    assert "required" in bad.text.lower()

    # Update
    r2 = client.post(
        f"/a/teams/{tid}/update",
        data={"name": "Worship Team", "description": "Updated"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r2.status_code == 200
    assert "Worship Team" in r2.text
    t = db.query(Team).filter(Team.id == tid).first()
    db.refresh(t)
    assert t.name == "Worship Team"
    assert t.description == "Updated"

    # Delete
    r3 = client.post(f"/a/teams/{tid}/delete", cookies={SESSION_COOKIE: tok})
    assert r3.status_code == 200
    assert db.query(Team).filter(Team.id == tid).first() is None


def test_team_membership_add_remove(client, db):
    tok = _admin(client, db, org="t_o3", email="t3@web.test")
    seed_person(db, person_id="t_p1", org_id="t_o3", email="p1@t.test", roles=["volunteer"])
    seed_person(db, person_id="t_p2", org_id="t_o3", email="p2@t.test", roles=["volunteer"])
    client.post("/a/teams/create", data={"name": "Ushers"}, cookies={SESSION_COOKIE: tok})
    tid = _team_id(db, "t_o3")

    # Add a member
    r = client.post(
        f"/a/teams/{tid}/members/add",
        data={"person_id": "t_p1"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert (
        db.query(TeamMember)
        .filter(TeamMember.team_id == tid, TeamMember.person_id == "t_p1")
        .first()
        is not None
    )
    assert "t_p1" in r.text or "P1 T.test" in r.text or "p1@t.test" not in r.text

    # Remove the member
    r2 = client.post(
        f"/a/teams/{tid}/members/remove",
        data={"person_id": "t_p1"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r2.status_code == 200
    assert (
        db.query(TeamMember)
        .filter(TeamMember.team_id == tid, TeamMember.person_id == "t_p1")
        .first()
        is None
    )


def test_team_cross_org_isolated(client, db):
    tok = _admin(client, db, org="t_o4", email="t4@web.test")
    # A team in a different org.
    seed_person(db, person_id="other_admin", org_id="t_other", email="o@t.test", roles=["admin"])
    other = Team(id="other_team", org_id="t_other", name="Secret")
    db.add(other)
    db.commit()

    page = client.get("/a/teams", cookies={SESSION_COOKIE: tok})
    assert "Secret" not in page.text  # not in this admin's org

    # Mutating another org's team is rejected (verify_org_member).
    resp = client.post(
        "/a/teams/other_team/update",
        data={"name": "Hacked"},
        cookies={SESSION_COOKIE: tok},
    )
    assert resp.status_code == 400
    db.refresh(other)
    assert other.name == "Secret"
