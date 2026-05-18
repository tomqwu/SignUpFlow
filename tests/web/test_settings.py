"""Marathon P1.1 — org/account settings page."""

from __future__ import annotations

from api.models import Organization
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="s_org", email="sadmin@web.test"):
    seed_person(db, person_id="s_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_settings_page_renders_for_admin(client, db):
    token = _admin(client, db, org="s_o1", email="s1@web.test")
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="settings-form"' in resp.text
    assert "Web Org" in resp.text  # current org name pre-filled
    assert "Save settings" in resp.text


def test_settings_requires_admin(client, db):
    seed_person(db, person_id="s_vol", email="svol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "svol@web.test", "password": "WebPass123!"})
    token = login.cookies[SESSION_COOKIE]
    assert client.get("/a/settings", cookies={SESSION_COOKIE: token}).status_code == 303
    assert (
        client.post(
            "/a/settings",
            data={"name": "X"},
            cookies={SESSION_COOKIE: token},
        ).status_code
        == 303
    )


def test_settings_requires_auth(client):
    assert client.get("/a/settings").status_code == 303
    assert client.post("/a/settings", data={"name": "X"}).status_code == 303


def test_settings_save_updates_org(client, db):
    token = _admin(client, db, org="s_o2", email="s2@web.test")
    resp = client.post(
        "/a/settings",
        data={
            "name": "Grace Community Church",
            "region": "US-CA",
            "timezone": "America/Los_Angeles",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "Settings saved" in resp.text
    assert "Grace Community Church" in resp.text

    org = db.query(Organization).filter(Organization.id == "s_o2").first()
    db.refresh(org)
    assert org.name == "Grace Community Church"
    assert org.region == "US-CA"
    assert (org.config or {}).get("timezone") == "America/Los_Angeles"


def test_settings_name_required(client, db):
    token = _admin(client, db, org="s_o3", email="s3@web.test")
    resp = client.post(
        "/a/settings",
        data={"name": "   ", "region": "", "timezone": ""},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 400
    assert "required" in resp.text.lower()


def test_settings_preserves_other_config_and_clears_timezone(client, db):
    token = _admin(client, db, org="s_o4", email="s4@web.test")
    org = db.query(Organization).filter(Organization.id == "s_o4").first()
    org.config = {"foo": "bar"}
    db.commit()

    # Set a timezone — keeps foo, adds timezone.
    client.post(
        "/a/settings",
        data={"name": "Web Org", "region": "", "timezone": "UTC"},
        cookies={SESSION_COOKIE: token},
    )
    db.refresh(org)
    assert org.config.get("foo") == "bar"
    assert org.config.get("timezone") == "UTC"

    # Clear timezone — foo stays, timezone removed.
    client.post(
        "/a/settings",
        data={"name": "Web Org", "region": "", "timezone": ""},
        cookies={SESSION_COOKIE: token},
    )
    db.refresh(org)
    assert org.config.get("foo") == "bar"
    assert "timezone" not in org.config
