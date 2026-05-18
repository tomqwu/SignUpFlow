"""Marathon P3.19 — cross-origin isolation headers on every response."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.utils.security_headers_middleware import add_security_headers_middleware


def _client():
    app = FastAPI()

    @app.get("/x")
    def _x():
        return {"ok": True}

    add_security_headers_middleware(app)
    return TestClient(app)


def test_isolation_headers_present():
    r = _client().get("/x")
    assert r.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert r.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert r.headers["X-Permitted-Cross-Domain-Policies"] == "none"
    # Existing hardening still intact.
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
