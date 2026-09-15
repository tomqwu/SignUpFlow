"""Marathon P3.20 — readiness probe."""

from __future__ import annotations

import logging

from api import main


def test_ready_returns_ready(client, db):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_health_still_healthy(client, db):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_health_is_process_liveness_and_does_not_open_database(client, monkeypatch):
    calls = 0

    def fail_if_called():
        nonlocal calls
        calls += 1
        raise AssertionError("liveness must not open a database session")

    monkeypatch.setattr(main, "SessionLocal", fail_if_called)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "signupflow-api",
        "version": "1.0.0",
    }
    assert calls == 0


def test_ready_failure_is_generic_closes_session_and_recovers(client, monkeypatch, caplog):
    sessions = []
    secret = "postgresql://admin:do-not-leak@database.internal/signupflow"

    class FailingSession:
        def __init__(self):
            self.exited = False
            sessions.append(self)

        def __enter__(self):
            return self

        def execute(self, _statement):
            raise RuntimeError(secret)

        def __exit__(self, _exc_type, _exc, _traceback):
            self.exited = True

    monkeypatch.setattr(main, "SessionLocal", FailingSession)

    with caplog.at_level(logging.WARNING, logger="rostio"):
        failed = [client.get("/ready") for _ in range(4)]

    assert all(response.status_code == 503 for response in failed)
    assert all(
        response.json() == {"status": "not_ready", "reason": "dependency_unavailable"}
        for response in failed
    )
    assert all(session.exited for session in sessions)
    assert secret not in caplog.text
    assert secret not in "".join(response.text for response in failed)

    class HealthySession(FailingSession):
        def execute(self, _statement):
            return 1

    monkeypatch.setattr(main, "SessionLocal", HealthySession)
    recovered = client.get("/ready")
    assert recovered.status_code == 200
    assert recovered.json() == {"status": "ready"}
    assert sessions[-1].exited is True


def test_ready_is_ops_only_not_in_contract(client):
    """Ops probe must stay out of the OpenAPI client contract."""
    paths = client.get("/openapi.json").json()["paths"]
    assert "/ready" not in paths
    assert "/health" in paths  # health remains documented (pre-existing)
