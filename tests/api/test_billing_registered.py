"""Marathon P2.14 — billing router is mounted and reachable."""

from __future__ import annotations

from api.models import Subscription
from tests.api.conftest import auth_headers, seed_org, seed_user


def test_billing_subscription_endpoint_mounted(client, db):
    seed_org(client, "bl_org")
    seed_user(client, "bl_org", email="a@bl.org", name="Admin", password="AdminPass1!")
    h = auth_headers(client, "a@bl.org", "AdminPass1!")

    # No subscription yet → the registered handler answers 404 (not a
    # missing-route 404: the detail is handler-specific).
    miss = client.get("/api/v1/billing/subscription?org_id=bl_org", headers=h)
    assert miss.status_code == 404
    assert "subscription" in miss.json()["detail"].lower()

    db.add(Subscription(org_id="bl_org", plan_tier="pro", status="active"))
    db.commit()
    ok = client.get("/api/v1/billing/subscription?org_id=bl_org", headers=h)
    assert ok.status_code == 200
    assert ok.json()["subscription"]["plan_tier"] == "pro"


def test_billing_requires_auth(client, db):
    seed_org(client, "bl_o2")
    r = client.get("/api/v1/billing/subscription?org_id=bl_o2")
    assert r.status_code in (401, 403)
