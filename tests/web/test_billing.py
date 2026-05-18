"""Marathon P2.14 — web billing page."""

from __future__ import annotations

from api.models import Subscription
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_billing_admin_only(client, db):
    seed_person(db, person_id="bw_vol", email="bwvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "bwvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/billing").status_code == 303
    assert client.get("/a/billing", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="bw_o1", email="bw1@web.test")
    resp = client.get("/a/billing", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Billing" in resp.text
    # No subscription → free tier + the Stripe-not-configured notice.
    assert "free" in resp.text.lower()
    assert "STRIPE_SECRET_KEY" in resp.text


def test_billing_shows_subscription(client, db):
    tok = _admin(client, db, org="bw_o2", email="bw2@web.test")
    db.add(Subscription(org_id="bw_o2", plan_tier="pro", status="active", billing_cycle="monthly"))
    db.commit()
    resp = client.get("/a/billing", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    # Tier text is lowercase in HTML; CSS upper-cases it for display.
    assert "pro" in resp.text
    assert "active" in resp.text
    assert "monthly billing" in resp.text


def test_dashboard_links_to_billing(client, db):
    tok = _admin(client, db, org="bw_o3", email="bw3@web.test")
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'href="/a/billing"' in dash.text
