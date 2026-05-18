"""Marathon P1.12 — CSV people import."""

from __future__ import annotations

from api.models import Person
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _count(db, org):
    return db.query(Person).filter(Person.org_id == org).count()


def test_import_admin_only(client, db):
    seed_person(db, person_id="ci_vol", email="civol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "civol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert (
        client.post("/a/people/import", data={"csv_text": "A,a@x.io,volunteer"}).status_code == 303
    )
    assert (
        client.post(
            "/a/people/import",
            data={"csv_text": "A,a@x.io,volunteer"},
            cookies={SESSION_COOKIE: vtok},
        ).status_code
        == 303
    )


def test_import_creates_people(client, db):
    tok = _admin(client, db, org="ci_o1", email="ci1@web.test")
    before = _count(db, "ci_o1")
    csv = (
        "name,email,roles\n"
        "Jamie Park,jamie@hopechapel.org,volunteer;usher\n"
        "Sam Lee,sam@hopechapel.org,volunteer\n"
    )
    r = client.post("/a/people/import", data={"csv_text": csv}, cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert "Imported 2" in r.text
    assert _count(db, "ci_o1") == before + 2
    jamie = (
        db.query(Person)
        .filter(Person.org_id == "ci_o1", Person.email == "jamie@hopechapel.org")
        .first()
    )
    assert jamie is not None
    assert set(jamie.roles) == {"volunteer", "usher"}


def test_import_validation(client, db):
    tok = _admin(client, db, org="ci_o2", email="ci2@web.test")
    empty = client.post("/a/people/import", data={"csv_text": "   "}, cookies={SESSION_COOKIE: tok})
    assert empty.status_code == 400
    assert "at least one" in empty.text.lower()

    header_only = client.post(
        "/a/people/import",
        data={"csv_text": "name,email,roles"},
        cookies={SESSION_COOKIE: tok},
    )
    assert header_only.status_code == 400
    assert "no data rows" in header_only.text.lower()


def test_import_reports_row_errors(client, db):
    tok = _admin(client, db, org="ci_o3", email="ci3@web.test")
    csv = "Good Person,good@hopechapel.org,volunteer\nBad Person,not-an-email,volunteer\n"
    r = client.post("/a/people/import", data={"csv_text": csv}, cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert "Imported 1" in r.text
    assert "error" in r.text.lower()  # the bad-email row is reported


def test_people_page_has_import_button(client, db):
    tok = _admin(client, db, org="ci_o4", email="ci4@web.test")
    page = client.get("/a/people", cookies={SESSION_COOKIE: tok})
    assert "Import CSV" in page.text
