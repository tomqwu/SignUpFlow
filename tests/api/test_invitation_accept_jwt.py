"""Tests that POST /invitations/{token}/accept now returns real JWT
access + refresh tokens (Sprint 9 PR 9.4b).

The legacy implementation returned an opaque random token from
``generate_auth_token()``, which couldn't be used as a Bearer for
authenticated API calls. The new implementation mints the same
access+refresh JWT pair as /auth/login and /auth/signup, so the
mobile app can sign the user in directly after accepting.
"""

import time

import pytest
from jose import jwt

from api.models import Invitation, Organization
from api.security import (
    ALGORITHM,
    SECRET_KEY,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
)
from api.timeutils import utcnow


def _seed_pending_invitation(
    db,
    *,
    org_id: str,
    email: str,
    name: str = "Invited Volunteer",
    roles: list[str] | None = None,
) -> Invitation:
    if not db.query(Organization).filter(Organization.id == org_id).first():
        db.add(Organization(id=org_id, name=f"Org {org_id}", region="Test"))
    inv = Invitation(
        id=f"inv_{int(time.time())}_{email.replace('@', '_').replace('.', '_')}",
        org_id=org_id,
        email=email,
        name=name,
        roles=roles or ["volunteer"],
        invited_by="test_admin_id",
        token=f"token_{int(time.time())}_{email.split('@')[0]}",
        status="pending",
        expires_at=utcnow().replace(year=utcnow().year + 1),
    )
    db.add(inv)
    db.commit()
    return inv


@pytest.mark.no_mock_auth
class TestInvitationAcceptReturnsJwts:
    def test_accept_returns_access_token_jwt(self, client, db):
        inv = _seed_pending_invitation(db, org_id="inv_jwt_org_1", email="invitee1@example.com")
        resp = client.post(
            f"/api/v1/invitations/{inv.token}/accept",
            json={"password": "InviteePass1!", "timezone": "UTC"},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()

        # Token is a real JWT with type:"access".
        assert body["token"]
        payload = jwt.decode(body["token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["type"] == TOKEN_TYPE_ACCESS
        assert payload["sub"].startswith("person_invitee1_")
        assert "pwd_iat" in payload
        assert "exp" in payload

    def test_accept_returns_refresh_token_with_org_and_rtv(self, client, db):
        inv = _seed_pending_invitation(db, org_id="inv_jwt_org_2", email="invitee2@example.com")
        resp = client.post(
            f"/api/v1/invitations/{inv.token}/accept",
            json={"password": "InviteePass1!", "timezone": "UTC"},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()

        # refresh_token is present, non-empty, and decodes as a refresh JWT
        # carrying the same org_id + rtv claims as login/signup tokens.
        assert body["refresh_token"]
        payload = jwt.decode(body["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["type"] == TOKEN_TYPE_REFRESH
        assert payload["org_id"] == "inv_jwt_org_2"
        assert payload["rtv"] == 0
        assert "pwd_iat" in payload

    def test_returned_access_token_authenticates_against_a_real_endpoint(self, client, db):
        """The token is actually usable as a Bearer (regression for the
        legacy opaque-token bug)."""
        inv = _seed_pending_invitation(db, org_id="inv_jwt_org_3", email="invitee3@example.com")
        resp = client.post(
            f"/api/v1/invitations/{inv.token}/accept",
            json={"password": "InviteePass1!", "timezone": "UTC"},
        )
        assert resp.status_code == 201
        access = resp.json()["token"]

        # Use the token to hit /people/me — an authenticated endpoint.
        me = client.get(
            "/api/v1/people/me",
            headers={"Authorization": f"Bearer {access}"},
        )
        assert me.status_code == 200, me.text
        assert me.json()["email"] == "invitee3@example.com"

    def test_returned_refresh_token_works_against_auth_refresh(self, client, db):
        """Round-trip: accept invitation → use refresh_token at
        /auth/refresh → get a new access+refresh pair."""
        inv = _seed_pending_invitation(db, org_id="inv_jwt_org_4", email="invitee4@example.com")
        accept = client.post(
            f"/api/v1/invitations/{inv.token}/accept",
            json={"password": "InviteePass1!", "timezone": "UTC"},
        )
        assert accept.status_code == 201
        refresh_token = accept.json()["refresh_token"]

        time.sleep(1)  # so the new tokens have a different iat/exp
        rotate = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert rotate.status_code == 200, rotate.text
        new = rotate.json()
        assert new["token"] and new["token"] != accept.json()["token"]
        assert new["refresh_token"] and new["refresh_token"] != refresh_token
