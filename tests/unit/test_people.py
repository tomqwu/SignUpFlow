"""Unit tests for people endpoints."""

from tests.unit._identity import bootstrap_organization

API_BASE = "http://localhost:8000/api/v1"


class TestPersonCreate:
    """Test person creation (non-auth endpoint)."""

    def test_create_person_success(self, client):
        """Test successful person creation."""
        # Create org first
        bootstrap_organization(client, json={"id": "people_test_org", "name": "People Test Org"})
        # Create person
        response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_001",
                "org_id": "people_test_org",
                "name": "Test Person",
                "email": "test@example.com",
                "roles": ["volunteer"],
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["id"] == "person_001"
        assert data["name"] == "Test Person"
        assert data["email"] == "test@example.com"

    def test_create_person_duplicate_id(self, client):
        """Test creating person with duplicate ID fails."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org2", "name": "People Test Org 2"},
        )
        # Create first person
        client.post(
            f"{API_BASE}/people/",
            json={"id": "person_002", "org_id": "people_test_org2", "name": "First Person"},
        )
        # Try duplicate
        response = client.post(
            f"{API_BASE}/people/",
            json={"id": "person_002", "org_id": "people_test_org2", "name": "Duplicate Person"},
        )
        assert response.status_code == 409  # Conflict

    def test_create_person_invalid_org(self, client):
        """Test creating person with invalid org fails."""
        response = client.post(
            f"{API_BASE}/people/",
            json={"id": "person_003", "org_id": "nonexistent_org", "name": "Test Person"},
        )
        assert response.status_code == 404

    def test_create_person_with_access_role_and_qualifications(self, client):
        """Test creating a person with one access role and qualifications."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org3", "name": "People Test Org 3"},
        )
        response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_004",
                "org_id": "people_test_org3",
                "name": "Multi Role Person",
                "roles": ["admin", "leader"],
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["roles"] == ["admin", "leader"]


class TestPersonRead:
    """Test person retrieval."""

    def test_get_person_success(self, client):
        """Test successful person retrieval."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org4", "name": "People Test Org 4"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={"id": "person_005", "org_id": "people_test_org4", "name": "Get Test Person"},
        )
        response = client.get(f"{API_BASE}/people/person_005")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "person_005"
        assert data["name"] == "Get Test Person"

    def test_get_person_not_found(self, client):
        """Test retrieving non-existent person returns 404."""
        response = client.get(f"{API_BASE}/people/nonexistent_person")
        assert response.status_code == 404

    def test_list_people_by_org(self, client):
        """Test listing people filtered by organization."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org5", "name": "People Test Org 5"},
        )
        # Create multiple people
        for i in range(6, 9):
            client.post(
                f"{API_BASE}/people/",
                json={
                    "id": f"person_{i:03d}",
                    "org_id": "people_test_org5",
                    "name": f"List Person {i}",
                },
            )
        response = client.get(f"{API_BASE}/people/?org_id=people_test_org5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3


class TestPersonUpdate:
    """Test person updates."""

    def test_update_person_success(self, client):
        """Test successful person update."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org6", "name": "People Test Org 6"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={"id": "person_009", "org_id": "people_test_org6", "name": "Original Name"},
        )
        response = client.put(
            f"{API_BASE}/people/person_009",
            json={"name": "Updated Name", "email": "updated@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"

    def test_update_person_roles(self, client):
        """Test updating person roles."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org7", "name": "People Test Org 7"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_010",
                "org_id": "people_test_org7",
                "name": "Role Update Person",
                "roles": ["volunteer"],
            },
        )
        response = client.put(f"{API_BASE}/people/person_010", json={"roles": ["admin", "leader"]})
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 2
        assert "admin" in data["roles"]

    def test_update_person_not_found(self, client):
        """Test updating non-existent person returns 404."""
        response = client.put(
            f"{API_BASE}/people/nonexistent_person", json={"name": "Updated Name"}
        )
        assert response.status_code == 404

    def test_update_person_remove_role(self, client):
        """Test removing a role from person."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org_remove", "name": "People Test Org Remove"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_012",
                "org_id": "people_test_org_remove",
                "name": "Role Remove Person",
                "roles": ["admin", "leader"],
            },
        )
        # Remove one role
        response = client.put(
            f"{API_BASE}/people/person_012", json={"roles": ["volunteer", "leader"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 2
        assert "admin" not in data["roles"]
        assert "volunteer" in data["roles"]
        assert "leader" in data["roles"]

    def test_update_person_empty_roles_defaults_to_volunteer(self, client):
        """Test preserving account access when all explicit roles are cleared."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org_clear", "name": "People Test Org Clear"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_013",
                "org_id": "people_test_org_clear",
                "name": "Clear Roles Person",
                "roles": ["admin"],
            },
        )
        # Clear all roles
        response = client.put(f"{API_BASE}/people/person_013", json={"roles": []})
        assert response.status_code == 200
        data = response.json()
        assert data["roles"] == ["volunteer"]

    def test_update_person_add_multiple_roles(self, client):
        """Test adding multiple roles at once."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org_multi", "name": "People Test Org Multi"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_014",
                "org_id": "people_test_org_multi",
                "name": "Multi Role Add Person",
                "roles": [],
            },
        )
        # Add multiple roles
        response = client.put(
            f"{API_BASE}/people/person_014",
            json={"roles": ["admin", "leader", "super_admin"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 3
        assert "super_admin" in data["roles"]
        assert "admin" in data["roles"]

    def test_update_person_roles_persisted(self, client):
        """Test that role updates persist across GET requests."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org_persist", "name": "People Test Org Persist"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "person_015",
                "org_id": "people_test_org_persist",
                "name": "Persist Role Person",
                "roles": ["volunteer"],
            },
        )
        # Update roles
        client.put(f"{API_BASE}/people/person_015", json={"roles": ["admin", "leader"]})
        # Verify roles persisted by getting the person
        response = client.get(f"{API_BASE}/people/person_015")
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 2
        assert "admin" in data["roles"]
        assert "leader" in data["roles"]
        assert "volunteer" not in data["roles"]


class TestPersonDelete:
    """Test person deletion."""

    def test_delete_person_success(self, client):
        """Test successful person deletion."""
        bootstrap_organization(
            client,
            json={"id": "people_test_org8", "name": "People Test Org 8"},
        )
        client.post(
            f"{API_BASE}/people/",
            json={"id": "person_011", "org_id": "people_test_org8", "name": "To Be Deleted"},
        )
        response = client.delete(f"{API_BASE}/people/person_011")
        assert response.status_code in [200, 204]  # OK or No Content
        # Verify deletion
        response = client.get(f"{API_BASE}/people/person_011")
        assert response.status_code == 404

    def test_delete_person_not_found(self, client):
        """Test deleting non-existent person returns 404."""
        response = client.delete(f"{API_BASE}/people/nonexistent_person")
        assert response.status_code == 404
