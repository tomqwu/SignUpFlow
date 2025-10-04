#!/usr/bin/env python3
"""
Integration Tests: Invitations

Tests all invitation endpoints:
- POST /api/invitations - Create invitation
- GET /api/invitations - List invitations
- GET /api/invitations/{token} - Verify invitation
- POST /api/invitations/{token}/accept - Accept invitation
- DELETE /api/invitations/{id} - Cancel invitation
- POST /api/invitations/{id}/resend - Resend invitation
"""

import pytest
import httpx
from datetime import datetime
import time

API_BASE = "http://localhost:8000/api"


@pytest.fixture
def setup_test_org():
    """Create a test organization with an admin user."""
    client = httpx.Client()
    timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness

    org_id = f"test_org_{timestamp}"
    admin_email = f"admin_{timestamp}@test.com"

    # Create organization
    org_response = client.post(f"{API_BASE}/organizations/", json={
        "id": org_id,
        "name": "Test Organization",
        "region": "US",
        "config": {}
    })

    if org_response.status_code not in [200, 201]:
        raise Exception(f"Failed to create org (status {org_response.status_code}): {org_response.text}")

    # Create admin user
    signup_response = client.post(f"{API_BASE}/auth/signup", json={
        "org_id": org_id,
        "name": "Admin User",
        "email": admin_email,
        "password": "admin123",
        "roles": ["admin"]
    })

    if signup_response.status_code != 201:
        raise Exception(f"Failed to signup: {signup_response.text}")

    admin_data = signup_response.json()

    return {
        "client": client,
        "org_id": org_id,
        "admin_id": admin_data["person_id"],
        "admin_email": admin_email,
    }


class TestCreateInvitation:
    """Test invitation creation."""

    def test_create_invitation_success(self, setup_test_org):
        """Test successful invitation creation by admin."""
        data = setup_test_org
        client = data["client"]

        invitee_email = f"invitee_{int(time.time())}@test.com"

        response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": invitee_email,
                "name": "New Volunteer",
                "roles": ["volunteer"]
            }
        )

        assert response.status_code == 201
        invitation = response.json()
        assert invitation["email"] == invitee_email
        assert invitation["name"] == "New Volunteer"
        assert "volunteer" in invitation["roles"]
        assert invitation["status"] == "pending"
        assert "token" in invitation
        assert invitation["invited_by"] == data["admin_id"]

    def test_create_invitation_duplicate_email(self, setup_test_org):
        """Test cannot create invitation for existing user."""
        data = setup_test_org
        client = data["client"]

        # Try to invite the admin (who already exists)
        response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": data["admin_email"],
                "name": "Duplicate User",
                "roles": ["volunteer"]
            }
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_invitation_non_admin(self, setup_test_org):
        """Test non-admin cannot create invitations."""
        data = setup_test_org
        client = data["client"]

        # Create a volunteer (non-admin) user
        volunteer_email = f"volunteer_{int(time.time())}@test.com"
        volunteer_response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": data["org_id"],
            "name": "Volunteer User",
            "email": volunteer_email,
            "password": "vol123",
            "roles": ["volunteer"]
        })
        volunteer_id = volunteer_response.json()["person_id"]

        # Try to create invitation as volunteer
        response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": volunteer_id
            },
            json={
                "email": f"new_{int(time.time())}@test.com",
                "name": "New User",
                "roles": ["volunteer"]
            }
        )

        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_create_invitation_duplicate_pending(self, setup_test_org):
        """Test cannot create duplicate pending invitation."""
        data = setup_test_org
        client = data["client"]

        invitee_email = f"duplicate_inv_{int(time.time())}@test.com"

        # Create first invitation
        client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": invitee_email,
                "name": "User",
                "roles": ["volunteer"]
            }
        )

        # Try to create second invitation with same email
        response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": invitee_email,
                "name": "User Again",
                "roles": ["volunteer"]
            }
        )

        assert response.status_code == 409
        assert "pending invitation" in response.json()["detail"]


class TestListInvitations:
    """Test listing invitations."""

    def test_list_invitations_admin(self, setup_test_org):
        """Test admin can list invitations."""
        data = setup_test_org
        client = data["client"]

        # Create a few invitations
        for i in range(3):
            client.post(
                f"{API_BASE}/invitations",
                params={
                    "org_id": data["org_id"],
                    "invited_by_id": data["admin_id"]
                },
                json={
                    "email": f"user{i}_{int(time.time())}@test.com",
                    "name": f"User {i}",
                    "roles": ["volunteer"]
                }
            )

        # List invitations
        response = client.get(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "person_id": data["admin_id"]
            }
        )

        assert response.status_code == 200
        result = response.json()
        assert "invitations" in result
        assert result["total"] >= 3

    def test_list_invitations_filter_status(self, setup_test_org):
        """Test filtering invitations by status."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"filter_{int(time.time())}@test.com",
                "name": "Filter User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()

        # Cancel it
        client.delete(
            f"{API_BASE}/invitations/{invitation['id']}",
            params={"person_id": data["admin_id"]}
        )

        # List cancelled invitations
        response = client.get(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "person_id": data["admin_id"],
                "status_filter": "cancelled"
            }
        )

        assert response.status_code == 200
        result = response.json()
        assert all(inv["status"] == "cancelled" for inv in result["invitations"])


class TestVerifyInvitation:
    """Test invitation verification."""

    def test_verify_valid_invitation(self, setup_test_org):
        """Test verifying a valid invitation token."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"verify_{int(time.time())}@test.com",
                "name": "Verify User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()
        token = invitation["token"]

        # Verify token
        response = client.get(f"{API_BASE}/invitations/{token}")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is True
        assert result["invitation"]["email"] == invitation["email"]

    def test_verify_invalid_token(self, setup_test_org):
        """Test verifying an invalid token."""
        data = setup_test_org
        client = data["client"]

        response = client.get(f"{API_BASE}/invitations/invalid_token_12345")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "invalid" in result["message"].lower()

    def test_verify_cancelled_invitation(self, setup_test_org):
        """Test verifying a cancelled invitation."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"cancelled_{int(time.time())}@test.com",
                "name": "Cancelled User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()

        # Cancel it
        client.delete(
            f"{API_BASE}/invitations/{invitation['id']}",
            params={"person_id": data["admin_id"]}
        )

        # Verify token
        response = client.get(f"{API_BASE}/invitations/{invitation['token']}")

        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert result["invitation"]["status"] == "cancelled"


class TestAcceptInvitation:
    """Test invitation acceptance."""

    def test_accept_invitation_success(self, setup_test_org):
        """Test successful invitation acceptance."""
        data = setup_test_org
        client = data["client"]

        invitee_email = f"accept_{int(time.time())}@test.com"

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": invitee_email,
                "name": "Accept User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()
        token = invitation["token"]

        # Accept invitation
        response = client.post(
            f"{API_BASE}/invitations/{token}/accept",
            json={
                "password": "newpassword123",
                "timezone": "America/New_York"
            }
        )

        assert response.status_code == 201
        result = response.json()
        assert result["email"] == invitee_email
        assert result["name"] == "Accept User"
        assert "volunteer" in result["roles"]
        assert result["timezone"] == "America/New_York"
        assert "token" in result  # Auth token for immediate login

        # Verify user can login
        login_response = client.post(f"{API_BASE}/auth/login", json={
            "email": invitee_email,
            "password": "newpassword123"
        })
        assert login_response.status_code == 200

    def test_accept_invitation_invalid_token(self, setup_test_org):
        """Test accepting with invalid token."""
        data = setup_test_org
        client = data["client"]

        response = client.post(
            f"{API_BASE}/invitations/invalid_token/accept",
            json={
                "password": "password123",
                "timezone": "UTC"
            }
        )

        assert response.status_code == 404

    def test_accept_invitation_twice(self, setup_test_org):
        """Test cannot accept same invitation twice."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"twice_{int(time.time())}@test.com",
                "name": "Twice User",
                "roles": ["volunteer"]
            }
        )
        token = inv_response.json()["token"]

        # Accept first time
        client.post(
            f"{API_BASE}/invitations/{token}/accept",
            json={"password": "pass123", "timezone": "UTC"}
        )

        # Try to accept again
        response = client.post(
            f"{API_BASE}/invitations/{token}/accept",
            json={"password": "pass456", "timezone": "UTC"}
        )

        assert response.status_code == 400
        assert "accepted" in response.json()["detail"]


class TestCancelInvitation:
    """Test invitation cancellation."""

    def test_cancel_invitation_success(self, setup_test_org):
        """Test admin can cancel invitation."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"cancel_{int(time.time())}@test.com",
                "name": "Cancel User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()

        # Cancel invitation
        response = client.delete(
            f"{API_BASE}/invitations/{invitation['id']}",
            params={"person_id": data["admin_id"]}
        )

        assert response.status_code == 204

        # Verify it's cancelled
        verify_response = client.get(f"{API_BASE}/invitations/{invitation['token']}")
        assert verify_response.json()["invitation"]["status"] == "cancelled"


class TestResendInvitation:
    """Test invitation resending."""

    def test_resend_invitation_success(self, setup_test_org):
        """Test admin can resend invitation."""
        data = setup_test_org
        client = data["client"]

        # Create invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"resend_{int(time.time())}@test.com",
                "name": "Resend User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()
        old_token = invitation["token"]

        # Resend invitation
        response = client.post(
            f"{API_BASE}/invitations/{invitation['id']}/resend",
            params={"person_id": data["admin_id"]}
        )

        assert response.status_code == 200
        new_invitation = response.json()
        new_token = new_invitation["token"]

        # Verify new token is different
        assert new_token != old_token

        # Verify new token works
        verify_response = client.get(f"{API_BASE}/invitations/{new_token}")
        assert verify_response.json()["valid"] is True

    def test_resend_accepted_invitation_fails(self, setup_test_org):
        """Test cannot resend accepted invitation."""
        data = setup_test_org
        client = data["client"]

        # Create and accept invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": f"resend_accepted_{int(time.time())}@test.com",
                "name": "Resend Accepted User",
                "roles": ["volunteer"]
            }
        )
        invitation = inv_response.json()

        client.post(
            f"{API_BASE}/invitations/{invitation['token']}/accept",
            json={"password": "pass123", "timezone": "UTC"}
        )

        # Try to resend
        response = client.post(
            f"{API_BASE}/invitations/{invitation['id']}/resend",
            params={"person_id": data["admin_id"]}
        )

        assert response.status_code == 400
        assert "cannot resend" in response.json()["detail"].lower()


class TestInvitationWorkflow:
    """Test complete invitation workflow."""

    def test_complete_invitation_workflow(self, setup_test_org):
        """Test end-to-end invitation workflow."""
        data = setup_test_org
        client = data["client"]

        invitee_email = f"workflow_{int(time.time())}@test.com"

        # Step 1: Admin creates invitation
        inv_response = client.post(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "invited_by_id": data["admin_id"]
            },
            json={
                "email": invitee_email,
                "name": "Workflow User",
                "roles": ["volunteer"]
            }
        )
        assert inv_response.status_code == 201
        invitation = inv_response.json()
        token = invitation["token"]

        # Step 2: Invitee verifies token
        verify_response = client.get(f"{API_BASE}/invitations/{token}")
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] is True

        # Step 3: Invitee accepts invitation
        accept_response = client.post(
            f"{API_BASE}/invitations/{token}/accept",
            json={
                "password": "workflow123",
                "timezone": "America/Los_Angeles"
            }
        )
        assert accept_response.status_code == 201
        user_data = accept_response.json()

        # Step 4: User can login
        login_response = client.post(f"{API_BASE}/auth/login", json={
            "email": invitee_email,
            "password": "workflow123"
        })
        assert login_response.status_code == 200

        # Step 5: Admin can see accepted invitation
        list_response = client.get(
            f"{API_BASE}/invitations",
            params={
                "org_id": data["org_id"],
                "person_id": data["admin_id"],
                "status_filter": "accepted"
            }
        )
        accepted_invitations = list_response.json()["invitations"]
        assert any(inv["email"] == invitee_email for inv in accepted_invitations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
