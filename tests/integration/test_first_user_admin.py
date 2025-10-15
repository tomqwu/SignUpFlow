"""Test that first user of organization gets admin role automatically."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_first_user_gets_admin_role():
    """Test that the first user to sign up for an organization automatically gets admin role."""
    
    # Create organization first
    org_response = client.post(
        "/api/organizations/",
        json={
            "id": "test_org_first_user_v2",
            "name": "Test Organization",
            "region": "US"
        }
    )
    assert org_response.status_code == 201
    
    # First user signs up (no roles specified)
    first_user_response = client.post(
        "/api/auth/signup",
        json={
            "org_id": "test_org_first_user_v2",
            "name": "First User",
            "email": "first_v2@example.com",
            "password": "password123"
        }
    )
    assert first_user_response.status_code == 201
    first_user_data = first_user_response.json()
    
    # Verify first user has admin role
    assert "admin" in first_user_data["roles"]
    assert len(first_user_data["roles"]) == 1
    print(f"✅ First user automatically got admin role: {first_user_data['roles']}")


def test_second_user_cannot_self_assign_admin():
    """Test that non-first users CANNOT self-assign admin role (security fix)."""
    
    # Create organization
    org_response = client.post(
        "/api/organizations/",
        json={
            "id": "test_org_security",
            "name": "Security Test Org",
            "region": "US"
        }
    )
    assert org_response.status_code == 201
    
    # First user (admin)
    first_user_response = client.post(
        "/api/auth/signup",
        json={
            "org_id": "test_org_security",
            "name": "Admin User",
            "email": "admin_security@example.com",
            "password": "password123"
        }
    )
    assert first_user_response.status_code == 201
    assert "admin" in first_user_response.json()["roles"]
    
    # Second user tries to self-assign admin role (should be blocked)
    malicious_user_response = client.post(
        "/api/auth/signup",
        json={
            "org_id": "test_org_security",
            "name": "Malicious User",
            "email": "malicious@example.com",
            "password": "password123",
            "roles": ["admin"]  # Trying to make themselves admin
        }
    )
    assert malicious_user_response.status_code == 201
    malicious_user_data = malicious_user_response.json()
    
    # Verify admin role was filtered out
    assert "admin" not in malicious_user_data["roles"]
    assert "volunteer" in malicious_user_data["roles"]  # Should default to volunteer
    print(f"✅ Security: Malicious user blocked from self-assigning admin: {malicious_user_data['roles']}")


def test_second_user_can_have_volunteer_role():
    """Test that second user defaults to volunteer role."""
    
    # Create organization
    org_response = client.post(
        "/api/organizations/",
        json={
            "id": "test_org_volunteer",
            "name": "Volunteer Test Org",
            "region": "US"
        }
    )
    assert org_response.status_code == 201
    
    # First user (admin)
    client.post(
        "/api/auth/signup",
        json={
            "org_id": "test_org_volunteer",
            "name": "Admin",
            "email": "admin_vol@example.com",
            "password": "password123"
        }
    )
    
    # Second user (should get volunteer by default)
    volunteer_response = client.post(
        "/api/auth/signup",
        json={
            "org_id": "test_org_volunteer",
            "name": "Volunteer User",
            "email": "volunteer@example.com",
            "password": "password123"
        }
    )
    assert volunteer_response.status_code == 201
    volunteer_data = volunteer_response.json()
    
    assert "volunteer" in volunteer_data["roles"]
    assert "admin" not in volunteer_data["roles"]
    print(f"✅ Second user got volunteer role by default: {volunteer_data['roles']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
