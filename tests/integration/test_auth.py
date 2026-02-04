#!/usr/bin/env python3
"""
Unit Tests: Authentication

Tests all authentication endpoints:
- POST /auth/signup
- POST /auth/login
- POST /auth/check-email
"""

import pytest
import httpx
from datetime import datetime

API_BASE = "http://localhost:8001/api"


class TestAuthSignup:
    """Test signup endpoint."""

    def test_signup_success(self, api_server):
        """Test successful signup with valid data."""
        client = httpx.Client()

        # Create org first
        org_id = f"test_org_{int(datetime.now().timestamp())}"
        client.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Test Org",
            "region": "US",
            "config": {}
        })

        # Signup - first user in org becomes admin automatically
        email = f"test_{int(datetime.now().timestamp())}@test.com"
        response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Test User",
            "email": email,
            "password": "password123",
            "roles": ["volunteer"]  # Requested role will be ignored; first user gets admin
        })

        assert response.status_code == 201
        data = response.json()
        assert "person_id" in data
        assert "token" in data
        assert data["email"] == email
        # First user automatically becomes admin
        assert "admin" in data["roles"]

    def test_signup_duplicate_email(self, api_server):
        """Test signup rejects duplicate email."""
        client = httpx.Client()

        org_id = f"test_org_{int(datetime.now().timestamp())}"
        client.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Test Org",
            "region": "US",
            "config": {}
        })

        email = f"duplicate_{int(datetime.now().timestamp())}@test.com"

        # First signup
        client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "User 1",
            "email": email,
            "password": "pass123",
            "roles": []
        })

        # Second signup with same email
        response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "User 2",
            "email": email,
            "password": "pass456",
            "roles": []
        })

        assert response.status_code == 409

    def test_signup_invalid_org(self, api_server):
        """Test signup fails with nonexistent organization."""
        client = httpx.Client()

        response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": "nonexistent_org",
            "name": "Test User",
            "email": "test@test.com",
            "password": "pass123",
            "roles": []
        })

        assert response.status_code == 404


class TestAuthLogin:
    """Test login endpoint."""

    def test_login_success(self, api_server):
        """Test successful login with correct credentials."""
        client = httpx.Client()

        # Create org and user with highly unique IDs
        import random
        unique_id = f"{int(datetime.now().timestamp() * 1000)}_{random.randint(10000, 99999)}"
        org_id = f"login_test_org_{unique_id}"
        email = f"login_{unique_id}@test.com"
        password = "testpass123"

        org_response = client.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Login Test Org",
            "region": "US",
            "config": {}
        })
        assert org_response.status_code == 201, f"Org creation failed: {org_response.text}"

        # Sign up first user - they automatically become admin
        signup_response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Login User",
            "email": email,
            "password": password
        })
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        signup_data = signup_response.json()
        # Verify first user got admin role
        assert "admin" in signup_data["roles"], f"First user should get admin, got: {signup_data['roles']}"

        # Login
        response = client.post(f"{API_BASE}/auth/login", json={
            "email": email,
            "password": password
        })

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["email"] == email
        # First user in org automatically gets admin role
        assert "admin" in data["roles"]

    def test_login_wrong_password(self, api_server):
        """Test login fails with wrong password."""
        client = httpx.Client()

        org_id = f"test_org_{int(datetime.now().timestamp())}"
        email = f"wrongpass_{int(datetime.now().timestamp())}@test.com"

        client.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Test Org",
            "region": "US",
            "config": {}
        })

        client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Test User",
            "email": email,
            "password": "correctpass",
            "roles": []
        })

        # Login with wrong password
        response = client.post(f"{API_BASE}/auth/login", json={
            "email": email,
            "password": "wrongpass"
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_server):
        """Test login fails with nonexistent email."""
        client = httpx.Client()

        response = client.post(f"{API_BASE}/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "anypass"
        })

        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
