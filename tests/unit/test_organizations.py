"""Unit tests for organization endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
API_BASE = "http://localhost:8000/api"


class TestOrganizationCreate:
    """Test organization creation."""

    def test_create_org_success(self):
        """Test successful organization creation."""
        response = client.post(
            f"{API_BASE}/organizations/",
            json={
                "id": "test_org_001_v2",
                "name": "Test Organization",
                "region": "Test Region",
                "config": {"location": "Test City"}
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["id"] == "test_org_001_v2"
        assert data["name"] == "Test Organization"

    def test_create_org_duplicate_id(self):
        """Test creating org with duplicate ID fails."""
        # Create first org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_002", "name": "First Org"}
        )
        # Try to create duplicate
        response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_002", "name": "Duplicate Org"}
        )
        assert response.status_code == 409  # Conflict

    def test_create_org_missing_name(self):
        """Test creating org without name fails."""
        response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_003"}
        )
        assert response.status_code == 422  # Validation error

    def test_create_org_empty_id(self):
        """Test creating org with empty ID fails."""
        response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "", "name": "Empty ID Org"}
        )
        assert response.status_code == 422


class TestOrganizationRead:
    """Test organization retrieval."""

    def test_get_org_success(self):
        """Test successful organization retrieval."""
        # Create org first
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_004", "name": "Get Test Org"}
        )
        # Retrieve it
        response = client.get(f"{API_BASE}/organizations/test_org_004")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_org_004"
        assert data["name"] == "Get Test Org"

    def test_get_org_not_found(self):
        """Test retrieving non-existent org returns 404."""
        response = client.get(f"{API_BASE}/organizations/nonexistent_org")
        assert response.status_code == 404

    def test_list_orgs(self):
        """Test listing all organizations."""
        # Create a few orgs
        for i in range(5, 8):
            client.post(
                f"{API_BASE}/organizations/",
                json={"id": f"test_org_{i:03d}", "name": f"List Test Org {i}"}
            )
        # List them
        response = client.get(f"{API_BASE}/organizations/")
        assert response.status_code == 200
        data = response.json()
        assert "organizations" in data
        assert len(data["organizations"]) >= 3


class TestOrganizationUpdate:
    """Test organization updates."""

    def test_update_org_success(self):
        """Test successful organization update."""
        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_008_v2", "name": "Original Name"}
        )
        # Update it
        response = client.put(
            f"{API_BASE}/organizations/test_org_008_v2",
            json={"name": "Updated Name", "region": "New Region"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data.get("region") == "New Region"

    def test_update_org_not_found(self):
        """Test updating non-existent org returns 404."""
        response = client.put(
            f"{API_BASE}/organizations/nonexistent_org",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 404

    def test_update_org_partial(self):
        """Test partial update of organization."""
        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_009_v2", "name": "Original", "region": "Original Region"}
        )
        # Update only name
        response = client.put(
            f"{API_BASE}/organizations/test_org_009_v2",
            json={"name": "New Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data.get("region") == "Original Region"


class TestOrganizationDelete:
    """Test organization deletion."""

    def test_delete_org_success(self):
        """Test successful organization deletion."""
        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_010", "name": "To Be Deleted"}
        )
        # Delete it
        response = client.delete(f"{API_BASE}/organizations/test_org_010")
        assert response.status_code in [200, 204]  # OK or No Content
        # Verify it's gone
        response = client.get(f"{API_BASE}/organizations/test_org_010")
        assert response.status_code == 404

    def test_delete_org_not_found(self):
        """Test deleting non-existent org returns 404."""
        response = client.delete(f"{API_BASE}/organizations/nonexistent_org")
        assert response.status_code == 404
