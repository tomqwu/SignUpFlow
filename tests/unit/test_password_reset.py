"""Test password reset functionality uses bcrypt correctly."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from api.database import get_db
from api.models import Person, Organization
from api.security import verify_password


class TestPasswordResetSecurity:
    """Test that password reset uses bcrypt instead of SHA256."""

    def test_password_reset_uses_bcrypt(self, api_server):
        """Verify that password reset hashes passwords with bcrypt, not SHA256."""
        client = TestClient(app)

        # Get database session
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test organization
        org = Organization(id="test_reset_org", name="Test Reset Org", region="Test")
        db.add(org)
        db.commit()

        # Create test user with known password
        person = Person(
            id="test_reset_person",
            org_id="test_reset_org",
            name="Test Reset Person",
            email="reset@example.com",
            password_hash="$2b$12$dummy_hash_will_be_replaced",  # bcrypt format
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Request password reset
        response = client.post("/api/auth/forgot-password", json={
            "email": "reset@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert "reset_link" in data

        # Extract token from reset link
        reset_link = data["reset_link"]
        token = reset_link.split("token=")[1]

        # Reset password
        new_password = "NewSecurePassword123!"
        response = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": new_password
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset successfully"

        # Verify password was hashed with bcrypt
        db.refresh(person)

        # Check password hash format (bcrypt starts with $2b$)
        assert person.password_hash is not None, "password_hash should be set"
        assert person.password_hash.startswith("$2b$"), \
            f"Password should be bcrypt format (start with $2b$), got: {person.password_hash[:10]}"

        # Verify password can be verified with bcrypt
        assert verify_password(new_password, person.password_hash), \
            "Password should be verifiable with bcrypt"

        # Verify password_hash is NOT in extra_data (old vulnerable pattern)
        extra_data = person.extra_data or {}
        assert "password_hash" not in extra_data, \
            "password_hash should NOT be in extra_data (security vulnerability)"

        # Verify password hash length (bcrypt hashes are 60 characters)
        assert len(person.password_hash) == 60, \
            f"bcrypt hash should be 60 characters, got: {len(person.password_hash)}"

        # Clean up
        db.delete(person)
        db.delete(org)
        db.commit()

    def test_password_reset_different_from_sha256(self, api_server):
        """Verify that bcrypt hash is different from SHA256 hash."""
        client = TestClient(app)

        # Get database session
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test organization
        org = Organization(id="test_sha_org", name="Test SHA Org", region="Test")
        db.add(org)
        db.commit()

        # Create test user
        person = Person(
            id="test_sha_person",
            org_id="test_sha_org",
            name="Test SHA Person",
            email="sha@example.com",
            password_hash="$2b$12$dummy_hash",
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Request password reset
        response = client.post("/api/auth/forgot-password", json={
            "email": "sha@example.com"
        })
        token = response.json()["reset_link"].split("token=")[1]

        # Reset password
        new_password = "TestPassword123"
        response = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": new_password
        })
        assert response.status_code == 200

        # Get the bcrypt hash
        db.refresh(person)
        bcrypt_hash = person.password_hash

        # Calculate what SHA256 would produce (vulnerable approach)
        import hashlib
        sha256_hash = hashlib.sha256(new_password.encode()).hexdigest()

        # Verify they are different
        assert bcrypt_hash != sha256_hash, \
            "bcrypt hash should be completely different from SHA256 hash"

        # Verify SHA256 hash would NOT be recognized as valid format by passlib
        from passlib.exc import UnknownHashError
        with pytest.raises(UnknownHashError):
            verify_password(new_password, sha256_hash)

        # Clean up
        db.delete(person)
        db.delete(org)
        db.commit()

    def test_password_reset_with_login(self, api_server):
        """Verify that reset password can be used to log in."""
        client = TestClient(app)

        # Get database session
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test organization
        org = Organization(id="test_login_org", name="Test Login Org", region="Test")
        db.add(org)
        db.commit()

        # Create test user
        person = Person(
            id="test_login_person",
            org_id="test_login_org",
            name="Test Login Person",
            email="login@example.com",
            password_hash="$2b$12$dummy_hash",
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Request password reset
        response = client.post("/api/auth/forgot-password", json={
            "email": "login@example.com"
        })
        token = response.json()["reset_link"].split("token=")[1]

        # Reset password to known value
        new_password = "MyNewPassword456!"
        response = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": new_password
        })
        assert response.status_code == 200

        # Try to log in with new password
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": new_password
        })

        # Should succeed because password was properly hashed with bcrypt
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "login@example.com"
        assert "token" in data

        # Clean up
        db.delete(person)
        db.delete(org)
        db.commit()
