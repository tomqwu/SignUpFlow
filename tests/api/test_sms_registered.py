"""Marathon P2.16 — sms router is mounted (self-prefixed /api/sms)."""

from __future__ import annotations


def test_sms_endpoints_mounted(client, db):
    # Mounted but auth-protected → 401/403, NOT a 404 missing-route.
    r1 = client.get("/api/sms/organizations/x/sms-usage")
    assert r1.status_code in (401, 403)
    r2 = client.post("/api/sms/verify-phone", json={})
    assert r2.status_code in (401, 403, 422)  # auth/validation, not 404


def test_sms_path_in_openapi(client):
    schema = client.get("/openapi.json").json()
    assert any(p.startswith("/api/sms/") for p in schema["paths"]), schema["paths"].keys()
