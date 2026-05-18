"""Marathon P3.20 — readiness probe."""

from __future__ import annotations


def test_ready_returns_ready(client, db):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_health_still_healthy(client, db):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_ready_is_ops_only_not_in_contract(client):
    """Ops probe must stay out of the OpenAPI client contract."""
    paths = client.get("/openapi.json").json()["paths"]
    assert "/ready" not in paths
    assert "/health" in paths  # health remains documented (pre-existing)
