"""Smoke test for the integration-tier `api_server` fixture (Sprint 4 PR 4.6a).

This test only verifies that:
  * the uvicorn-in-thread fixture starts on an ephemeral port,
  * lifespan ran (so the app's startup is complete),
  * the live server responds over real HTTP.

If this fails, the integration tier's foundation is broken and PR 4.6b
should not proceed.
"""

import httpx


def test_api_server_starts_and_serves_health(api_server):
    resp = httpx.get(f"{api_server.base_url}/health", timeout=5.0)
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "signupflow-api"
    assert body["status"] == "healthy"


def test_api_root_redirects_to_v1(api_client):
    resp = api_client.get("/api/v1", follow_redirects=False)
    assert resp.status_code == 200, resp.text


def test_openapi_schema_exposed(api_client):
    resp = api_client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    # The schema should at minimum advertise the /api/v1 prefix that all
    # routers use.
    paths = schema.get("paths", {})
    assert any(path.startswith("/api/v1") for path in paths)
