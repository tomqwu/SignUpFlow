"""Marathon P3.21 — public pricing page."""

from __future__ import annotations

import pytest

from api.core.config import settings


@pytest.fixture(autouse=True)
def _enable_billing(monkeypatch):
    """Exercise the deferred page only through explicit opt-in."""
    monkeypatch.setattr(settings, "BILLING_ENABLED", True)


def test_pricing_is_public_and_lists_tiers(client):
    # No auth required — mirrors /auth/login.
    r = client.get("/pricing")
    assert r.status_code == 200
    body = r.text
    assert "Pricing" in body
    # Tier names are lowercase in HTML (CSS upper-cases for display).
    for tier in ("free", "starter", "pro", "enterprise"):
        assert tier in body
    # Truthful limits from UsageService.PLAN_LIMITS.
    assert "Unlimited" in body  # enterprise
    assert "200" in body  # pro volunteers / starter events
    assert 'href="/auth/signup"' in body
    assert 'href="/auth/login"' in body


def test_login_links_to_pricing(client):
    assert 'href="/pricing"' in client.get("/auth/login").text
