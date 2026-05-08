"""Tests for POST /auth/refresh (Sprint 9 PR 9.3).

Covers:
- Happy path: refresh token from /auth/login → /auth/refresh → new pair.
- Wrong type: passing an access token to /auth/refresh → 401.
- Expired refresh token → 401.
- pwd_iat mismatch (password changed after refresh issued) → 401.
- Refreshed access token is usable as a normal access token.
- Refreshed refresh token is itself a refresh token (recursively refreshable).
"""

import time
from datetime import timedelta

import pytest
from jose import jwt

from api.models import Organization, Person
from api.security import (
    ALGORITHM,
    SECRET_KEY,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    hash_password,
)
from api.timeutils import utcnow


def _seed_login_user(db, email: str = "refresh-test@example.com"):
    org_id = "refresh_org"
    if not db.query(Organization).filter(Organization.id == org_id).first():
        db.add(Organization(id=org_id, name="Refresh Org", region="Test"))
    pwd_hash = hash_password("RefreshPass1!")
    person = Person(
        id=f"refresh_person_{email.split('@')[0]}",
        org_id=org_id,
        name="Refresh Tester",
        email=email,
        password_hash=pwd_hash,
        roles=["volunteer"],
        password_changed_at=utcnow(),
    )
    db.add(person)
    db.commit()
    return person


@pytest.mark.no_mock_auth
class TestAuthRefreshHappyPath:
    def test_login_returns_refresh_token_and_refresh_works(self, client, db):
        person = _seed_login_user(db, email="refresh-happy@example.com")
        login = client.post(
            "/api/v1/auth/login",
            json={"email": person.email, "password": "RefreshPass1!"},
        )
        assert login.status_code == 200, login.text
        body = login.json()
        assert "token" in body and body["token"]
        assert "refresh_token" in body and body["refresh_token"]
        original_refresh = body["refresh_token"]
        original_access = body["token"]

        # Wait long enough that the new tokens have a different `iat`/`exp`
        # so they're observably different strings (or at least don't match
        # the old ones byte-for-byte).
        time.sleep(1)

        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": original_refresh},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["token"] and data["token"] != original_access
        assert data["refresh_token"] and data["refresh_token"] != original_refresh

    def test_refresh_response_is_a_real_access_token(self, client, db):
        person = _seed_login_user(db, email="refresh-usable@example.com")
        login = client.post(
            "/api/v1/auth/login",
            json={"email": person.email, "password": "RefreshPass1!"},
        )
        refresh_token = login.json()["refresh_token"]
        new_pair = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        new_access = new_pair.json()["token"]

        # The new access token decodes as type:"access".
        payload = jwt.decode(new_access, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("type") == "access"
        assert payload.get("sub") == person.id

    def test_refresh_token_is_recursively_refreshable(self, client, db):
        person = _seed_login_user(db, email="refresh-chain@example.com")
        login = client.post(
            "/api/v1/auth/login",
            json={"email": person.email, "password": "RefreshPass1!"},
        )
        first = login.json()["refresh_token"]
        time.sleep(1)
        second = client.post("/api/v1/auth/refresh", json={"refresh_token": first}).json()[
            "refresh_token"
        ]
        time.sleep(1)
        third_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": second})
        assert third_resp.status_code == 200, third_resp.text


@pytest.mark.no_mock_auth
class TestAuthRefreshRejection:
    def test_access_token_rejected_at_refresh_endpoint(self, client, db):
        person = _seed_login_user(db, email="refresh-wrongtype@example.com")
        # Forge an access token directly (skip login round-trip).
        access = create_access_token(data={"sub": person.id, "pwd_iat": utcnow().timestamp()})
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access})
        assert resp.status_code == 401
        assert (
            "wrong" in resp.json()["detail"].lower() or "invalid" in resp.json()["detail"].lower()
        )

    def test_expired_refresh_token_rejected(self, client, db):
        person = _seed_login_user(db, email="refresh-expired@example.com")
        # Mint a refresh token that's already expired.
        expired = create_refresh_token(
            data={"sub": person.id, "pwd_iat": utcnow().timestamp()},
            expires_delta=timedelta(seconds=-60),
        )
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": expired})
        assert resp.status_code == 401

    def test_pwd_iat_mismatch_rejected(self, client, db):
        person = _seed_login_user(db, email="refresh-pwdmismatch@example.com")
        # Mint a refresh token with a stale pwd_iat (representing a
        # refresh issued before the user changed their password).
        stale_pwd_iat = (utcnow() - timedelta(days=1)).timestamp()
        stale_refresh = create_refresh_token(data={"sub": person.id, "pwd_iat": stale_pwd_iat})
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": stale_refresh})
        assert resp.status_code == 401
        assert (
            "password change" in resp.json()["detail"].lower()
            or "invalid" in resp.json()["detail"].lower()
        )

    def test_garbage_refresh_token_rejected(self, client, db):
        _seed_login_user(db, email="refresh-garbage@example.com")
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not.a.real.jwt"})
        assert resp.status_code == 401

    def test_unknown_user_rejected(self, client, db):
        # Mint a refresh token for a user that doesn't exist.
        ghost_refresh = create_refresh_token(
            data={"sub": "ghost_person_id", "pwd_iat": utcnow().timestamp()}
        )
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": ghost_refresh})
        assert resp.status_code == 401


@pytest.mark.no_mock_auth
class TestSignupReturnsRefreshToken:
    def test_signup_returns_refresh_token(self, client, db):
        org_id = "refresh_signup_org"
        if not db.query(Organization).filter(Organization.id == org_id).first():
            db.add(Organization(id=org_id, name="Signup Org", region="Test"))
            db.commit()
        resp = client.post(
            "/api/v1/auth/signup",
            json={
                "org_id": org_id,
                "name": "New Admin",
                "email": "refresh-signup@example.com",
                "password": "SignupPass1!",
            },
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["refresh_token"]
        # And the refresh token has type:"refresh".
        payload = jwt.decode(body["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("type") == TOKEN_TYPE_REFRESH
