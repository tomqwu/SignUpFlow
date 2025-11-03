"""Unit tests for team endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

API_BASE = "http://localhost:8000/api"


class TestTeamCreate:
    """Test team creation."""

    def test_create_team_success(self, client):
        """Test successful team creation."""
        # Create org first
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_001", "name": "Team Test Org 001"}
        )
        # Create team
        response = client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_001",
                "org_id": "team_test_org_001",
                "name": "Test Team",
                "description": "A test team"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["id"] == "team_001"
        assert data["name"] == "Test Team"
        assert data["description"] == "A test team"
        assert data["org_id"] == "team_test_org_001"
        assert "member_count" in data

    def test_create_team_duplicate_id(self, client):
        """Test creating team with duplicate ID fails."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_002", "name": "Team Test Org 002"}
        )
        # Create first team
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_002",
                "org_id": "team_test_org_002",
                "name": "First Team"
            }
        )
        # Try to create duplicate
        response = client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_002",
                "org_id": "team_test_org_002",
                "name": "Duplicate Team"
            }
        )
        assert response.status_code == 409  # Conflict

    def test_create_team_invalid_org(self, client):
        """Test creating team with invalid org fails."""
        response = client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_003",
                "org_id": "nonexistent_org",
                "name": "Test Team"
            }
        )
        assert response.status_code == 404

    def test_create_team_with_description(self, client):
        """Test creating team with description."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_003", "name": "Team Test Org 003"}
        )
        response = client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_004",
                "org_id": "team_test_org_003",
                "name": "Descriptive Team",
                "description": "This team has a detailed description"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["description"] == "This team has a detailed description"


class TestTeamRead:
    """Test team retrieval."""

    def test_get_team_success(self, client):
        """Test successful team retrieval."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_004", "name": "Team Test Org 004"}
        )
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_005",
                "org_id": "team_test_org_004",
                "name": "Get Test Team"
            }
        )
        response = client.get(f"{API_BASE}/teams/team_005")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "team_005"
        assert data["name"] == "Get Test Team"
        assert "member_count" in data

    def test_get_team_not_found(self, client):
        """Test retrieving non-existent team returns 404."""
        response = client.get(f"{API_BASE}/teams/nonexistent_team")
        assert response.status_code == 404

    def test_list_teams_by_org(self, client):
        """Test listing teams filtered by organization."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_005", "name": "Team Test Org 005"}
        )
        # Create multiple teams
        for i in range(6, 9):
            client.post(
                f"{API_BASE}/teams/",
                json={
                    "id": f"team_{i:03d}",
                    "org_id": "team_test_org_005",
                    "name": f"List Team {i}"
                }
            )
        response = client.get(f"{API_BASE}/teams/?org_id=team_test_org_005")
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert len(data["teams"]) >= 3


class TestTeamUpdate:
    """Test team updates."""

    def test_update_team_success(self, client):
        """Test successful team update."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_006", "name": "Team Test Org 006"}
        )
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_009",
                "org_id": "team_test_org_006",
                "name": "Original Name",
                "description": "Original Description"
            }
        )
        response = client.put(
            f"{API_BASE}/teams/team_009",
            json={
                "name": "Updated Name",
                "description": "Updated Description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated Description"

    def test_update_team_not_found(self, client):
        """Test updating non-existent team returns 404."""
        response = client.put(
            f"{API_BASE}/teams/nonexistent_team",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 404


class TestTeamDelete:
    """Test team deletion."""

    def test_delete_team_success(self, client):
        """Test successful team deletion."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_007", "name": "Team Test Org 007"}
        )
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_010",
                "org_id": "team_test_org_007",
                "name": "To Be Deleted"
            }
        )
        response = client.delete(f"{API_BASE}/teams/team_010")
        assert response.status_code in [200, 204]  # OK or No Content
        # Verify deletion
        response = client.get(f"{API_BASE}/teams/team_010")
        assert response.status_code == 404

    def test_delete_team_not_found(self, client):
        """Test deleting non-existent team returns 404."""
        response = client.delete(f"{API_BASE}/teams/nonexistent_team")
        assert response.status_code == 404


class TestTeamMembers:
    """Test team member operations."""

    def test_add_team_member_success(self, client):
        """Test successfully adding a member to a team."""
        # Setup: create org, person, and team
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_008", "name": "Team Test Org 008"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "team_member_001",
                "org_id": "team_test_org_008",
                "name": "Team Member 001"
            }
        )
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_011",
                "org_id": "team_test_org_008",
                "name": "Member Test Team"
            }
        )
        # Add member to team
        response = client.post(
            f"{API_BASE}/teams/team_011/members",
            json={"person_ids": ["team_member_001"]}
        )
        assert response.status_code == 204
        # Verify member was added by checking member count
        team_response = client.get(f"{API_BASE}/teams/team_011")
        assert team_response.status_code == 200
        team_data = team_response.json()
        assert team_data["member_count"] == 1

    def test_add_team_member_duplicate(self, client):
        """Test adding the same member twice (should be idempotent)."""
        # Setup: create org, person, and team
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "team_test_org_009", "name": "Team Test Org 009"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "team_member_002",
                "org_id": "team_test_org_009",
                "name": "Team Member 002"
            }
        )
        client.post(
            f"{API_BASE}/teams/",
            json={
                "id": "team_012",
                "org_id": "team_test_org_009",
                "name": "Duplicate Member Test Team"
            }
        )
        # Add member first time
        response1 = client.post(
            f"{API_BASE}/teams/team_012/members",
            json={"person_ids": ["team_member_002"]}
        )
        assert response1.status_code == 204
        # Add same member again (should succeed - idempotent)
        response2 = client.post(
            f"{API_BASE}/teams/team_012/members",
            json={"person_ids": ["team_member_002"]}
        )
        assert response2.status_code == 204
        # Verify member count is still 1
        team_response = client.get(f"{API_BASE}/teams/team_012")
        assert team_response.status_code == 200
        team_data = team_response.json()
        assert team_data["member_count"] == 1
