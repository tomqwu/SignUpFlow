#!/usr/bin/env python3
"""Integration tests: invitations.

Tests all invitation endpoints over real HTTP against the session-scoped
uvicorn api_server (Sprint 4 PR 4.6a):
- POST /api/v1/invitations              - Create invitation
- GET  /api/v1/invitations              - List invitations
- GET  /api/v1/invitations/{token}      - Verify invitation
- POST /api/v1/invitations/{token}/accept
- DELETE /api/v1/invitations/{id}       - Cancel invitation
- POST /api/v1/invitations/{id}/resend  - Resend invitation
"""

import time

import httpx
import pytest


@pytest.fixture
def setup_test_org(api_server, api_base):
    """Create a test organization with an admin user."""
    client = httpx.Client()
    timestamp = int(time.time() * 1000)  # milliseconds for uniqueness

    org_id = f"inv_org_{timestamp}"
    admin_email = f"admin_{timestamp}@test.com"
    admin_password = "AdminPass123!"

    # Create organization
    org_response = client.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": "Test Organization", "region": "US", "config": {}},
    )

    if org_response.status_code not in [200, 201]:
        raise AssertionError(
            f"Failed to create org (status {org_response.status_code}): {org_response.text}"
        )

    # Create admin user (first user becomes admin automatically)
    signup_response = client.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Admin User",
            "email": admin_email,
            "password": admin_password,
            "roles": ["admin"],
        },
    )

    if signup_response.status_code != 201:
        raise AssertionError(f"Failed to signup: {signup_response.text}")

    admin_data = signup_response.json()

    # JWT-authed client for admin requests
    jwt_token = admin_data["token"]
    client.headers["Authorization"] = f"Bearer {jwt_token}"

    return {
        "client": client,
        "org_id": org_id,
        "admin_id": admin_data["person_id"],
        "admin_email": admin_email,
        "api_base": api_base,
    }


class TestCreateInvitation:
    """Test invitation creation."""

    def test_create_invitation_success(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        invitee_email = f"invitee_{int(time.time() * 1000)}@test.com"

        response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": invitee_email, "name": "New Volunteer", "roles": ["volunteer"]},
        )

        assert response.status_code == 201, response.text
        invitation = response.json()
        assert invitation["email"] == invitee_email
        assert invitation["name"] == "New Volunteer"
        assert "volunteer" in invitation["roles"]
        assert invitation["status"] == "pending"
        assert "token" in invitation
        assert invitation["invited_by"] == data["admin_id"]

    def test_create_invitation_duplicate_email(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        # Try to invite the admin (who already exists)
        response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": data["admin_email"], "name": "Duplicate User", "roles": ["volunteer"]},
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_invitation_non_admin(self, setup_test_org):
        data = setup_test_org
        api_base = data["api_base"]

        # Create a volunteer (non-admin) user
        volunteer_email = f"volunteer_{int(time.time() * 1000)}@test.com"
        volunteer_password = "VolPass123!"
        volunteer_response = httpx.Client().post(
            f"{api_base}/auth/signup",
            json={
                "org_id": data["org_id"],
                "name": "Volunteer User",
                "email": volunteer_email,
                "password": volunteer_password,
                "roles": ["volunteer"],
            },
        )
        assert volunteer_response.status_code == 201, volunteer_response.text
        volunteer_data = volunteer_response.json()
        # Org's first user is admin; this second user is volunteer-only.
        assert "admin" not in volunteer_data["roles"]

        # New client with volunteer's JWT
        volunteer_client = httpx.Client()
        volunteer_client.headers["Authorization"] = f"Bearer {volunteer_data['token']}"

        try:
            response = volunteer_client.post(
                f"{api_base}/invitations",
                params={"org_id": data["org_id"]},
                json={
                    "email": f"new_{int(time.time() * 1000)}@test.com",
                    "name": "New User",
                    "roles": ["volunteer"],
                },
            )

            assert response.status_code == 403
        finally:
            volunteer_client.close()

    def test_create_invitation_duplicate_pending(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        invitee_email = f"duplicate_inv_{int(time.time() * 1000)}@test.com"

        # First invitation
        first = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": invitee_email, "name": "User", "roles": ["volunteer"]},
        )
        assert first.status_code == 201, first.text

        # Second with same email
        response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": invitee_email, "name": "User Again", "roles": ["volunteer"]},
        )

        assert response.status_code == 409
        assert "pending invitation" in response.json()["detail"]


class TestListInvitations:
    """Test listing invitations."""

    def test_list_invitations_admin(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        for i in range(3):
            r = client.post(
                f"{api_base}/invitations",
                params={"org_id": data["org_id"]},
                json={
                    "email": f"user{i}_{int(time.time() * 1000)}@test.com",
                    "name": f"User {i}",
                    "roles": ["volunteer"],
                },
            )
            assert r.status_code == 201, r.text

        response = client.get(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
        )

        assert response.status_code == 200
        result = response.json()
        assert "items" in result
        assert result["total"] >= 3

    def test_list_invitations_filter_status(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"filter_{int(time.time() * 1000)}@test.com",
                "name": "Filter User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()

        # Cancel it
        cancel_response = client.delete(f"{api_base}/invitations/{invitation['id']}")
        assert cancel_response.status_code == 204, cancel_response.text

        # List cancelled
        response = client.get(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"], "status": "cancelled"},
        )

        assert response.status_code == 200
        result = response.json()
        assert all(inv["status"] == "cancelled" for inv in result["items"])


class TestVerifyInvitation:
    """Test invitation verification."""

    def test_verify_valid_invitation(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"verify_{int(time.time() * 1000)}@test.com",
                "name": "Verify User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()
        token = invitation["token"]

        response = client.get(f"{api_base}/invitations/{token}")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is True
        assert result["invitation"]["email"] == invitation["email"]

    def test_verify_invalid_token(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        response = client.get(f"{api_base}/invitations/invalid_token_12345")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False

    def test_verify_cancelled_invitation(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"cancelled_{int(time.time() * 1000)}@test.com",
                "name": "Cancelled User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()

        cancel_response = client.delete(f"{api_base}/invitations/{invitation['id']}")
        assert cancel_response.status_code == 204, cancel_response.text

        response = client.get(f"{api_base}/invitations/{invitation['token']}")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert result["invitation"]["status"] == "cancelled"


class TestAcceptInvitation:
    """Test invitation acceptance."""

    def test_accept_invitation_success(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        invitee_email = f"accept_{int(time.time() * 1000)}@test.com"

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": invitee_email, "name": "Accept User", "roles": ["volunteer"]},
        )
        assert inv_response.status_code == 201, inv_response.text
        token = inv_response.json()["token"]

        # accept does not need auth (public flow)
        public_client = httpx.Client()
        try:
            response = public_client.post(
                f"{api_base}/invitations/{token}/accept",
                json={"password": "NewPassword123!", "timezone": "America/New_York"},
            )

            assert response.status_code == 201, response.text
            result = response.json()
            assert result["email"] == invitee_email
            assert result["name"] == "Accept User"
            assert "volunteer" in result["roles"]
            assert result["timezone"] == "America/New_York"
            assert "token" in result

            login_response = public_client.post(
                f"{api_base}/auth/login",
                json={"email": invitee_email, "password": "NewPassword123!"},
            )
            assert login_response.status_code == 200
        finally:
            public_client.close()

    def test_accept_invitation_invalid_token(self, setup_test_org):
        data = setup_test_org
        api_base = data["api_base"]

        public_client = httpx.Client()
        try:
            response = public_client.post(
                f"{api_base}/invitations/invalid_token/accept",
                json={"password": "Password123!", "timezone": "UTC"},
            )

            assert response.status_code == 404
        finally:
            public_client.close()

    def test_accept_invitation_twice(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"twice_{int(time.time() * 1000)}@test.com",
                "name": "Twice User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        token = inv_response.json()["token"]

        public_client = httpx.Client()
        try:
            first = public_client.post(
                f"{api_base}/invitations/{token}/accept",
                json={"password": "Password123!", "timezone": "UTC"},
            )
            assert first.status_code == 201, first.text

            response = public_client.post(
                f"{api_base}/invitations/{token}/accept",
                json={"password": "Password456!", "timezone": "UTC"},
            )

            assert response.status_code == 400
            assert "accepted" in response.json()["detail"]
        finally:
            public_client.close()


class TestCancelInvitation:
    """Test invitation cancellation."""

    def test_cancel_invitation_success(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"cancel_{int(time.time() * 1000)}@test.com",
                "name": "Cancel User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()

        response = client.delete(f"{api_base}/invitations/{invitation['id']}")
        assert response.status_code == 204, response.text

        verify_response = client.get(f"{api_base}/invitations/{invitation['token']}")
        assert verify_response.json()["invitation"]["status"] == "cancelled"


class TestResendInvitation:
    """Test invitation resending."""

    def test_resend_invitation_success(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"resend_{int(time.time() * 1000)}@test.com",
                "name": "Resend User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()
        old_token = invitation["token"]

        response = client.post(f"{api_base}/invitations/{invitation['id']}/resend")

        assert response.status_code == 200, response.text
        new_invitation = response.json()
        new_token = new_invitation["token"]

        assert new_token != old_token

        verify_response = client.get(f"{api_base}/invitations/{new_token}")
        assert verify_response.json()["valid"] is True

    def test_resend_accepted_invitation_fails(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={
                "email": f"resend_accepted_{int(time.time() * 1000)}@test.com",
                "name": "Resend Accepted User",
                "roles": ["volunteer"],
            },
        )
        assert inv_response.status_code == 201, inv_response.text
        invitation = inv_response.json()

        public_client = httpx.Client()
        try:
            accept = public_client.post(
                f"{api_base}/invitations/{invitation['token']}/accept",
                json={"password": "Password123!", "timezone": "UTC"},
            )
            assert accept.status_code == 201, accept.text
        finally:
            public_client.close()

        response = client.post(f"{api_base}/invitations/{invitation['id']}/resend")

        assert response.status_code == 400
        assert "cannot resend" in response.json()["detail"].lower()


class TestInvitationWorkflow:
    """End-to-end workflow."""

    def test_complete_invitation_workflow(self, setup_test_org):
        data = setup_test_org
        client = data["client"]
        api_base = data["api_base"]

        invitee_email = f"workflow_{int(time.time() * 1000)}@test.com"

        # Step 1: Admin creates invitation
        inv_response = client.post(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"]},
            json={"email": invitee_email, "name": "Workflow User", "roles": ["volunteer"]},
        )
        assert inv_response.status_code == 201, inv_response.text
        token = inv_response.json()["token"]

        # Step 2: Invitee verifies token
        verify_response = client.get(f"{api_base}/invitations/{token}")
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] is True

        # Step 3: Invitee accepts
        public_client = httpx.Client()
        try:
            accept_response = public_client.post(
                f"{api_base}/invitations/{token}/accept",
                json={"password": "Workflow123!", "timezone": "America/Los_Angeles"},
            )
            assert accept_response.status_code == 201, accept_response.text

            # Step 4: User logs in
            login_response = public_client.post(
                f"{api_base}/auth/login",
                json={"email": invitee_email, "password": "Workflow123!"},
            )
            assert login_response.status_code == 200
        finally:
            public_client.close()

        # Step 5: Admin lists accepted
        list_response = client.get(
            f"{api_base}/invitations",
            params={"org_id": data["org_id"], "status": "accepted"},
        )
        accepted = list_response.json()["items"]
        assert any(inv["email"] == invitee_email for inv in accepted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
