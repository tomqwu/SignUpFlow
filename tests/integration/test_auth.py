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

API_BASE = "http://localhost:8000/api"


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

        # Signup
        email = f"test_{int(datetime.now().timestamp())}@test.com"
        response = client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Test User",
            "email": email,
            "password": "password123",
            "roles": ["volunteer"]
        })

        assert response.status_code == 201
        data = response.json()
        assert "person_id" in data
        assert "token" in data
        assert data["email"] == email
        assert "volunteer" in data["roles"]

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

        # Create org and user
        org_id = f"test_org_{int(datetime.now().timestamp())}"
        email = f"login_{int(datetime.now().timestamp())}@test.com"
        password = "testpass123"

        client.post(f"{API_BASE}/organizations/", json={
            "id": org_id,
            "name": "Test Org",
            "region": "US",
            "config": {}
        })

        client.post(f"{API_BASE}/auth/signup", json={
            "org_id": org_id,
            "name": "Login User",
            "email": email,
            "password": password,
            "roles": ["admin"]
        })

        # Login
        response = client.post(f"{API_BASE}/auth/login", json={
            "email": email,
            "password": password
        })

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["email"] == email
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
