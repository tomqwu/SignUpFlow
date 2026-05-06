#!/usr/bin/env python3
"""Integration tests: authentication.

Tests all authentication endpoints over real HTTP against the
session-scoped uvicorn api_server (Sprint 4 PR 4.6a):
- POST /auth/signup
- POST /auth/login
"""

import random
from datetime import datetime

import httpx
import pytest


def _unique(prefix: str) -> str:
    """Return a stable-but-unique suffix to avoid collisions across tests."""
    return f"{prefix}_{int(datetime.now().timestamp() * 1000)}_{random.randint(10000, 99999)}"


class TestAuthSignup:
    """Test signup endpoint."""

    def test_signup_success(self, api_server, api_base):
        """Test successful signup with valid data."""
        client = httpx.Client()

        org_id = _unique("test_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Test Org", "region": "US", "config": {}},
        )

        # Signup - first user in org becomes admin automatically
        email = f"{_unique('signup')}@test.com"
        response = client.post(
            f"{api_base}/auth/signup",
            json={
                "org_id": org_id,
                "name": "Test User",
                "email": email,
                "password": "Password123!",
                "roles": ["volunteer"],  # First user gets admin regardless
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert "person_id" in data
        assert "token" in data
        assert data["email"] == email
        # First user automatically becomes admin
        assert "admin" in data["roles"]

    def test_signup_duplicate_email(self, api_server, api_base):
        """Test signup rejects duplicate email."""
        client = httpx.Client()

        org_id = _unique("dup_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Test Org", "region": "US", "config": {}},
        )

        email = f"{_unique('duplicate')}@test.com"

        first = client.post(
            f"{api_base}/auth/signup",
            json={
                "org_id": org_id,
                "name": "User 1",
                "email": email,
                "password": "Password123!",
                "roles": [],
            },
        )
        assert first.status_code == 201, first.text

        # Second signup with same email
        response = client.post(
            f"{api_base}/auth/signup",
            json={
                "org_id": org_id,
                "name": "User 2",
                "email": email,
                "password": "Password123!",
                "roles": [],
            },
        )

        assert response.status_code == 409

    def test_signup_invalid_org(self, api_server, api_base):
        """Test signup fails with nonexistent organization."""
        client = httpx.Client()

        response = client.post(
            f"{api_base}/auth/signup",
            json={
                "org_id": "nonexistent_org",
                "name": "Test User",
                "email": f"{_unique('noorg')}@test.com",
                "password": "Password123!",
                "roles": [],
            },
        )

        assert response.status_code == 404


class TestAuthLogin:
    """Test login endpoint."""

    def test_login_success(self, api_server, api_base):
        """Test successful login with correct credentials."""
        client = httpx.Client()

        unique = _unique("login")
        org_id = f"login_org_{unique}"
        email = f"{unique}@test.com"
        password = "TestPass123!"

        org_response = client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Login Test Org", "region": "US", "config": {}},
        )
        assert org_response.status_code == 201, f"Org creation failed: {org_response.text}"

        signup_response = client.post(
            f"{api_base}/auth/signup",
            json={"org_id": org_id, "name": "Login User", "email": email, "password": password},
        )
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        signup_data = signup_response.json()
        assert (
            "admin" in signup_data["roles"]
        ), f"First user should get admin, got: {signup_data['roles']}"

        response = client.post(
            f"{api_base}/auth/login", json={"email": email, "password": password}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "token" in data
        assert data["email"] == email
        assert "admin" in data["roles"]

    def test_login_wrong_password(self, api_server, api_base):
        """Test login fails with wrong password."""
        client = httpx.Client()

        unique = _unique("wrongpass")
        org_id = f"wrong_org_{unique}"
        email = f"{unique}@test.com"

        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Test Org", "region": "US", "config": {}},
        )

        client.post(
            f"{api_base}/auth/signup",
            json={
                "org_id": org_id,
                "name": "Test User",
                "email": email,
                "password": "CorrectPass123!",
                "roles": [],
            },
        )

        response = client.post(
            f"{api_base}/auth/login", json={"email": email, "password": "WrongPass456!"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_server, api_base):
        """Test login fails with nonexistent email."""
        client = httpx.Client()

        response = client.post(
            f"{api_base}/auth/login",
            json={"email": f"{_unique('nope')}@test.com", "password": "AnyPass123!"},
        )

        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
