"""Marathon P1.4 — constraints DSL editor."""

from __future__ import annotations

from api.models import Constraint
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _cid(db, org):
    return db.query(Constraint).filter(Constraint.org_id == org).first().id


def test_constraints_page_admin_only(client, db):
    seed_person(db, person_id="c_vol", email="cvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "cvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/constraints", cookies={SESSION_COOKIE: vtok}).status_code == 303
    assert client.get("/a/constraints").status_code == 303

    atok = _admin(client, db, org="c_o1", email="c1@web.test")
    resp = client.get("/a/constraints", cookies={SESSION_COOKIE: atok})
    assert resp.status_code == 200
    assert 'id="constraints-list"' in resp.text
    assert "New constraint" in resp.text


def test_constraint_create_with_params(client, db):
    tok = _admin(client, db, org="c_o2", email="c2@web.test")
    r = client.post(
        "/a/constraints/create",
        data={
            "key": "min_gap",
            "type": "soft",
            "weight": "10",
            "predicate": "min_gap_hours_satisfied(person_id, 12)",
            "params": '{"min_hours": 12}',
        },
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert "min_gap" in r.text
    c = db.query(Constraint).filter(Constraint.org_id == "c_o2").first()
    assert c.type == "soft"
    assert c.weight == 10
    assert c.params == {"min_hours": 12}


def test_constraint_create_validation(client, db):
    tok = _admin(client, db, org="c_o3", email="c3@web.test")
    base = {"key": "k", "type": "hard", "weight": "", "predicate": "p", "params": ""}

    assert (
        client.post(
            "/a/constraints/create",
            data={**base, "key": "  "},
            cookies={SESSION_COOKIE: tok},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/a/constraints/create",
            data={**base, "predicate": ""},
            cookies={SESSION_COOKIE: tok},
        ).status_code
        == 400
    )
    bad_json = client.post(
        "/a/constraints/create",
        data={**base, "params": "{not json}"},
        cookies={SESSION_COOKIE: tok},
    )
    assert bad_json.status_code == 400
    assert "json" in bad_json.text.lower()
    bad_w = client.post(
        "/a/constraints/create",
        data={**base, "weight": "heavy"},
        cookies={SESSION_COOKIE: tok},
    )
    assert bad_w.status_code == 400


def test_constraint_update_and_delete(client, db):
    tok = _admin(client, db, org="c_o4", email="c4@web.test")
    client.post(
        "/a/constraints/create",
        data={"key": "k1", "type": "hard", "weight": "", "predicate": "p", "params": ""},
        cookies={SESSION_COOKIE: tok},
    )
    cid = _cid(db, "c_o4")

    r = client.post(
        f"/a/constraints/{cid}/update",
        data={
            "type": "soft",
            "weight": "5",
            "predicate": "has_role(usher)",
            "params": "",
        },
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    c = db.query(Constraint).filter(Constraint.id == cid).first()
    db.refresh(c)
    assert c.type == "soft" and c.weight == 5
    assert c.predicate == "has_role(usher)"

    d = client.post(f"/a/constraints/{cid}/delete", cookies={SESSION_COOKIE: tok})
    assert d.status_code == 200
    assert db.query(Constraint).filter(Constraint.id == cid).first() is None


def test_constraint_cross_org_isolated(client, db):
    tok = _admin(client, db, org="c_o5", email="c5@web.test")
    seed_person(db, person_id="oadm", org_id="c_other", email="o@c.test", roles=["admin"])
    other = Constraint(org_id="c_other", key="secret", type="hard", predicate="p", params=None)
    db.add(other)
    db.commit()

    page = client.get("/a/constraints", cookies={SESSION_COOKIE: tok})
    assert "secret" not in page.text

    resp = client.post(
        f"/a/constraints/{other.id}/update",
        data={"type": "hard", "weight": "", "predicate": "hacked", "params": ""},
        cookies={SESSION_COOKIE: tok},
    )
    assert resp.status_code == 400
    db.refresh(other)
    assert other.predicate == "p"
