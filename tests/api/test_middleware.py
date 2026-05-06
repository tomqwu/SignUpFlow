"""Middleware integration tests: request ID round-trip and CORS lockdown."""

import re

import pytest
from fastapi.testclient import TestClient

from api.main import app

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


@pytest.fixture
def client():
    return TestClient(app)


class TestRequestID:
    """X-Request-ID is generated when missing and echoed when supplied."""

    def test_request_id_generated_when_missing(self, client):
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert UUID_RE.match(response.headers["X-Request-ID"])

    def test_request_id_preserved_when_supplied(self, client):
        custom_id = "client-supplied-12345"
        response = client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers.get("X-Request-ID") == custom_id

    def test_request_id_unique_per_request(self, client):
        r1 = client.get("/health")
        r2 = client.get("/health")
        assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]


class TestApiPrefixRedirect:
    """Bare /api is a 308 redirect to /api/v1 for one release."""

    def test_bare_api_redirects_to_v1(self, client):
        response = client.get("/api", follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/api/v1"

    def test_v1_api_info_is_canonical(self, client):
        response = client.get("/api/v1")
        assert response.status_code == 200
        body = response.json()
        assert body["service"] == "SignUpFlow API"
        assert body["endpoints"]["organizations"] == "/api/v1/organizations"


class TestCORS:
    """CORS preflight allows configured origins and rejects others."""

    def test_allows_localhost_dev_origin(self, client):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:8000"

    def test_rejects_unconfigured_origin(self, client):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        header_keys = {k.lower() for k in response.headers.keys()}
        assert "access-control-allow-origin" not in header_keys
