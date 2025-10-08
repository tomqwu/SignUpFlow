"""Security tests for JWT authentication."""

import pytest
from httpx import AsyncClient
from datetime import timedelta

from api.main import app
from api.security import create_access_token, verify_token, hash_password, verify_password


def test_password_hashing():
    """Test bcrypt password hashing."""
    password = "test_password_123"
    hashed = hash_password(password)

    # Hash should be different from plain password
    assert hashed != password

    # Should start with bcrypt prefix
    assert hashed.startswith("$2b$")

    # Should verify correctly
    assert verify_password(password, hashed)

    # Wrong password should not verify
    assert not verify_password("wrong_password", hashed)


def test_jwt_token_creation():
    """Test JWT token creation and verification."""
    user_id = "test_user_123"
    token = create_access_token(data={"sub": user_id})

    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Should be able to verify and decode
    payload = verify_token(token)
    assert payload["sub"] == user_id


def test_jwt_token_expiration():
    """Test JWT token expiration."""
    user_id = "test_user_123"

    # Create token that expires in the past (invalid)
    expired_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=-1)
    )

    # Should raise HTTPException when verifying expired token
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        verify_token(expired_token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_request_to_protected_endpoint():
    """Test that requests without auth token are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Try to access protected endpoint without token
        response = await ac.get("/api/people/me")

        # Should return 403 Forbidden (no auth header provided)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    """Test that invalid tokens are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/people/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_returns_jwt_token():
    """Test that login endpoint returns a valid JWT token."""
    from api.database import get_db
    from api.models import Person, Organization
    from api.security import hash_password

    # Create test user
    db = next(get_db())

    # Check if test org exists
    org = db.query(Organization).filter_by(id="test_security_org").first()
    if not org:
        org = Organization(id="test_security_org", name="Test Security Org")
        db.add(org)
        db.commit()

    # Check if test person exists
    person = db.query(Person).filter_by(email="security_test@example.com").first()
    if person:
        db.delete(person)
        db.commit()

    # Create test person with bcrypt hash
    person = Person(
        id="security_test_person",
        org_id="test_security_org",
        name="Security Test",
        email="security_test@example.com",
        password_hash=hash_password("testpass123"),
        roles=["volunteer"]
    )
    db.add(person)
    db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/login",
            json={
                "email": "security_test@example.com",
                "password": "testpass123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should return token
        assert "token" in data
        assert len(data["token"]) > 0

        # Token should be valid JWT
        payload = verify_token(data["token"])
        assert payload["sub"] == "security_test_person"

    # Cleanup
    db.delete(person)
    db.delete(org)
    db.commit()


@pytest.mark.asyncio
async def test_authenticated_request_with_valid_token():
    """Test that authenticated requests with valid tokens succeed."""
    from api.database import get_db
    from api.models import Person, Organization
    from api.security import hash_password

    # Create test data
    db = next(get_db())

    org = db.query(Organization).filter_by(id="test_auth_org").first()
    if not org:
        org = Organization(id="test_auth_org", name="Test Auth Org")
        db.add(org)
        db.commit()

    person = db.query(Person).filter_by(email="auth_test@example.com").first()
    if person:
        db.delete(person)
        db.commit()

    person = Person(
        id="auth_test_person",
        org_id="test_auth_org",
        name="Auth Test",
        email="auth_test@example.com",
        password_hash=hash_password("testpass123"),
        roles=["volunteer"]
    )
    db.add(person)
    db.commit()

    # Create valid token for this user
    token = create_access_token(data={"sub": "auth_test_person"})

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/people/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "auth_test_person"
        assert data["email"] == "auth_test@example.com"

    # Cleanup
    db.delete(person)
    db.delete(org)
    db.commit()
