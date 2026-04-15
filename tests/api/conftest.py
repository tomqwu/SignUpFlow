"""
API workflow test fixtures and helpers.

Uses FastAPI TestClient (in-process, no HTTP server) with a fresh
in-memory SQLite database per test function. Real JWT auth, no mocking.

Helpers are plain functions (not fixtures) so they can be reused by
a future CLI module.
"""

import os
import pytest
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from api.models import Base
from api.main import app
from api.database import get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db():
    """Fresh in-memory SQLite database per test. All tables created/dropped."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    _SessionFactory = sessionmaker(bind=engine)
    session = _SessionFactory()

    # Override FastAPI's get_db to use this engine
    def _override_get_db():
        _s = _SessionFactory()
        try:
            yield _s
        finally:
            _s.close()

    app.dependency_overrides[get_db] = _override_get_db

    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db) -> TestClient:
    """FastAPI TestClient wired to the per-test in-memory DB."""
    os.environ["TESTING"] = "true"
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# Override root conftest autouse fixtures so they don't interfere
@pytest.fixture(autouse=True)
def mock_authentication():
    """Suppress root conftest auth mocking — API tests use real JWT."""
    yield


@pytest.fixture(autouse=True)
def reset_database_between_tests():
    """Suppress root conftest DB reset — API tests own their DB lifecycle."""
    yield


# ---------------------------------------------------------------------------
# Helper functions (reusable by CLI)
# ---------------------------------------------------------------------------

def seed_org(client: TestClient, org_id: str, name: str = "Test Org", region: str = "US") -> dict:
    """Create an organization. Returns response JSON."""
    resp = client.post("/api/organizations/", json={"id": org_id, "name": name, "region": region})
    assert resp.status_code == 201, f"seed_org failed: {resp.status_code} {resp.text}"
    return resp.json()


def seed_user(
    client: TestClient,
    org_id: str,
    email: str,
    name: str,
    password: str = "TestPass123!",
    roles: Optional[list] = None,
) -> dict:
    """Sign up a user. First user in org auto-becomes admin. Returns auth response with token."""
    resp = client.post("/api/auth/signup", json={
        "org_id": org_id, "name": name, "email": email,
        "password": password, "roles": roles or [],
    })
    assert resp.status_code == 201, f"seed_user failed: {resp.status_code} {resp.text}"
    return resp.json()


def login(client: TestClient, email: str, password: str) -> dict:
    """Log in and return full auth response (including token)."""
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"login failed: {resp.status_code} {resp.text}"
    return resp.json()


def auth_headers(client: TestClient, email: str, password: str) -> dict:
    """Log in and return Authorization headers dict."""
    data = login(client, email, password)
    return {"Authorization": f"Bearer {data['token']}"}


def seed_event(
    client: TestClient,
    headers: dict,
    org_id: str,
    event_id: str,
    event_type: str = "Sunday Service",
    days_from_now: int = 14,
    duration_hours: int = 2,
    role_counts: Optional[dict] = None,
) -> dict:
    """Create an event (admin only). Returns event response."""
    start = datetime.now() + timedelta(days=days_from_now)
    end = start + timedelta(hours=duration_hours)
    resp = client.post("/api/events/", json={
        "id": event_id, "org_id": org_id, "type": event_type,
        "start_time": start.isoformat(), "end_time": end.isoformat(),
        "extra_data": {"role_counts": role_counts or {}},
    }, headers=headers)
    assert resp.status_code == 201, f"seed_event failed: {resp.status_code} {resp.text}"
    return resp.json()


def seed_invitation(
    client: TestClient, headers: dict, org_id: str,
    email: str, name: str, roles: Optional[list] = None,
) -> dict:
    """Create an invitation (admin only). Returns invitation with token."""
    resp = client.post(f"/api/invitations?org_id={org_id}", json={
        "email": email, "name": name, "roles": roles or ["volunteer"],
    }, headers=headers)
    assert resp.status_code == 201, f"seed_invitation failed: {resp.status_code} {resp.text}"
    return resp.json()


def accept_invitation(client: TestClient, token: str, password: str = "VolPass123!") -> dict:
    """Accept invitation. NOTE: returned token is NOT a JWT — must call login() after."""
    resp = client.post(f"/api/invitations/{token}/accept", json={
        "password": password, "timezone": "UTC",
    })
    assert resp.status_code == 201, f"accept_invitation failed: {resp.status_code} {resp.text}"
    return resp.json()


def seed_team(
    client: TestClient, headers: dict, org_id: str,
    team_id: str, name: str, member_ids: Optional[list] = None,
) -> dict:
    """Create a team (admin only). Returns team response."""
    resp = client.post("/api/teams/", json={
        "id": team_id, "org_id": org_id, "name": name,
        "member_ids": member_ids or [],
    }, headers=headers)
    assert resp.status_code == 201, f"seed_team failed: {resp.status_code} {resp.text}"
    return resp.json()


def add_timeoff(
    client: TestClient, person_id: str,
    start_date: str, end_date: str, reason: str = "Unavailable",
) -> dict:
    """Add time-off for a person. Dates are ISO strings like '2026-05-01'."""
    resp = client.post(f"/api/availability/{person_id}/timeoff", json={
        "start_date": start_date, "end_date": end_date, "reason": reason,
    })
    assert resp.status_code == 201, f"add_timeoff failed: {resp.status_code} {resp.text}"
    return resp.json()
