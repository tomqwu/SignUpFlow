"""
Tests for conftest.py authentication mocking infrastructure.

These tests verify that the authentication mocking in conftest.py works correctly,
allowing unit tests to bypass JWT authentication and org membership verification.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.models import Person, Organization
from api.database import get_db


class TestAuthenticationMocking:
    """Test that authentication mocking allows unit tests to bypass JWT auth."""

    def test_mock_admin_user_has_correct_attributes(self):
        """Verify mock admin user has expected attributes."""
        from api.dependencies import get_current_admin_user

        # Get the overridden dependency
        mock_admin = app.dependency_overrides[get_current_admin_user]()

        assert mock_admin.id == "test_admin"
        assert mock_admin.org_id == "test_org"
        assert mock_admin.name == "Test Admin"
        assert mock_admin.email == "admin@test.com"
        assert "admin" in mock_admin.roles

    def test_mock_user_has_admin_role(self):
        """Verify mock user has admin role to allow test operations."""
        from api.dependencies import get_current_user

        # Get the overridden dependency
        mock_user = app.dependency_overrides[get_current_user]()

        assert "admin" in mock_user.roles, "Mock user should have admin role to allow unit tests to pass"

    def test_protected_endpoint_accessible_without_jwt(self):
        """Verify protected endpoints are accessible without JWT tokens in tests."""
        client = TestClient(app)

        # Use the overridden get_db to access test database
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test org
        org = Organization(id="test_org_endpoint", name="Test Org", region="Test")
        db.add(org)
        db.commit()

        # Create test person
        person = Person(
            id="test_person_endpoint",
            org_id="test_org_endpoint",
            name="Test Person",
            email="test@example.com",
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Call protected endpoint without Authorization header
        response = client.get("/api/people/test_person_endpoint")

        # Should succeed because auth is mocked
        assert response.status_code == 200
        assert response.json()["id"] == "test_person_endpoint"

        # Cleanup
        db.delete(person)
        db.delete(org)
        db.commit()
        db.close()

    def test_verify_org_member_bypassed_in_tests(self):
        """Verify org membership verification is bypassed in tests."""
        from api.dependencies import verify_org_member
        from api.models import Person

        # Create a person from one org
        person = Person(
            id="person_org_a",
            org_id="org_a",
            name="Person A",
            email="persona@example.com",
            roles=["volunteer"]
        )

        # Should not raise error even when checking different org
        # (In production, this would raise HTTPException)
        try:
            verify_org_member(person, "org_b")
            # If we get here, verification was bypassed (correct for tests)
            assert True
        except Exception as e:
            pytest.fail(f"verify_org_member should be mocked in tests but raised: {e}")


class TestDatabaseOverride:
    """Test that database dependency is overridden correctly."""

    def test_test_database_is_used(self):
        """Verify tests use test database, not production database."""
        from api.database import get_db

        # Get database session
        db = next(app.dependency_overrides[get_db]())

        # Check that it's a test database session
        # We can verify by checking the connection URL
        assert "test_roster.db" in str(db.bind.url)

    def test_database_session_can_be_created(self):
        """Verify database session can be created from override."""
        from api.database import get_db

        # Get database session
        db_generator = app.dependency_overrides[get_db]()
        db = next(db_generator)

        # Session should be active
        assert db.is_active

        # Session should use test database
        assert "test_roster.db" in str(db.bind.url)

        db.close()

    def test_test_database_has_all_tables(self):
        """Verify test database has all required tables."""
        from api.database import get_db
        from sqlalchemy import inspect

        db = next(app.dependency_overrides[get_db]())
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()

        # Verify critical tables exist
        required_tables = [
            "organizations",
            "people",
            "teams",
            "events",
            "assignments",
            "availability",
            "invitations"
        ]

        for table in required_tables:
            assert table in tables, f"Required table '{table}' missing from test database"


class TestDependencyOverrideCleanup:
    """Test that dependency overrides are cleaned up properly."""

    def test_overrides_are_applied(self):
        """Verify that dependency overrides are active during tests."""
        from api.dependencies import get_current_admin_user, get_current_user
        from api.database import get_db

        # All three dependencies should be overridden
        assert get_db in app.dependency_overrides
        assert get_current_admin_user in app.dependency_overrides
        assert get_current_user in app.dependency_overrides

    def test_monkey_patching_is_active(self):
        """Verify that verify_org_member is monkey-patched."""
        import api.dependencies
        import api.routers.people

        # Create test person
        person = Person(
            id="test_monkey_patch",
            org_id="org_a",
            name="Test",
            email="test@example.com",
            roles=["volunteer"]
        )

        # Should not raise (monkey-patched to do nothing)
        try:
            api.dependencies.verify_org_member(person, "org_b")
            api.routers.people.verify_org_member(person, "org_b")
            assert True
        except Exception as e:
            pytest.fail(f"Monkey-patched verify_org_member should not raise: {e}")


class TestMockingIntegration:
    """Test that mocking integrates correctly with FastAPI TestClient."""

    def test_create_resource_without_auth_header(self):
        """Verify we can create resources without Authorization header."""
        client = TestClient(app)
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create org first
        org = Organization(id="test_org_mock", name="Test Org", region="Test")
        db.add(org)
        db.commit()

        # Create person without auth header
        response = client.post("/api/people/", json={
            "id": "test_person_mock",
            "org_id": "test_org_mock",
            "name": "Test Person",
            "email": "testmock@example.com",
            "roles": ["volunteer"]
        })

        assert response.status_code == 201

        # Cleanup
        db.query(Person).filter(Person.id == "test_person_mock").delete()
        db.delete(org)
        db.commit()
        db.close()

    def test_update_resource_without_auth_header(self):
        """Verify we can update resources without Authorization header."""
        client = TestClient(app)
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test data
        org = Organization(id="test_org_update", name="Test Org", region="Test")
        db.add(org)
        db.commit()

        person = Person(
            id="test_person_update",
            org_id="test_org_update",
            name="Original Name",
            email="update@example.com",
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Update without auth header
        response = client.put("/api/people/test_person_update", json={
            "name": "Updated Name"
        })

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

        # Cleanup
        db.delete(person)
        db.delete(org)
        db.commit()
        db.close()

    def test_delete_resource_without_auth_header(self):
        """Verify we can delete resources without Authorization header."""
        client = TestClient(app)
        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)

        # Create test data
        org = Organization(id="test_org_delete", name="Test Org", region="Test")
        db.add(org)
        db.commit()

        person = Person(
            id="test_person_delete",
            org_id="test_org_delete",
            name="To Delete",
            email="delete@example.com",
            roles=["volunteer"]
        )
        db.add(person)
        db.commit()

        # Delete without auth header
        response = client.delete("/api/people/test_person_delete")

        # DELETE returns 204 No Content on success
        assert response.status_code == 204

        # Cleanup org
        db.delete(org)
        db.commit()
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
