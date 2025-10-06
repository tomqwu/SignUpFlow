"""Unit tests for availability endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
API_BASE = "http://localhost:8000/api"


class TestAvailabilityCreate:
    """Test availability creation."""

    def test_add_availability_success(self):
        """Test successful availability/timeoff creation with start_date and end_date."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org1", "name": "Availability Test Org 1"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_001",
                "org_id": "avail_test_org1",
                "name": "Test Person 1"
            }
        )

        # Create availability record
        response = client.post(
            f"{API_BASE}/availability/?person_id=avail_person_001"
        )
        assert response.status_code == 201
        data = response.json()
        assert "availability_id" in data
        assert data["person_id"] == "avail_person_001"

        # Add timeoff period
        start = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        response = client.post(
            f"{API_BASE}/availability/avail_person_001/timeoff",
            json={
                "start_date": start,
                "end_date": end
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["start_date"] == start
        assert data["end_date"] == end

    def test_add_availability_invalid_person(self):
        """Test adding availability for non-existent person fails."""
        start = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        response = client.post(
            f"{API_BASE}/availability/nonexistent_person/timeoff",
            json={
                "start_date": start,
                "end_date": end
            }
        )
        assert response.status_code == 404

    def test_add_availability_overlapping(self):
        """Test adding overlapping availability periods returns conflict error."""
        import time
        timestamp = int(time.time() * 1000)
        org_id = f"avail_test_org_{timestamp}"
        person_id = f"avail_person_{timestamp}"

        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Availability Test Org"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": person_id,
                "org_id": org_id,
                "name": "Test Person",
                "email": f"{person_id}@test.com"
            }
        )

        # Add first timeoff period
        start1 = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        end1 = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        response1 = client.post(
            f"{API_BASE}/availability/{person_id}/timeoff",
            json={"start_date": start1, "end_date": end1}
        )
        assert response1.status_code == 201

        # Try to add overlapping period (overlaps days 18-20)
        start2 = (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d")
        end2 = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")
        response2 = client.post(
            f"{API_BASE}/availability/{person_id}/timeoff",
            json={"start_date": start2, "end_date": end2}
        )
        # Should fail with conflict error
        assert response2.status_code == 409
        assert "overlap" in response2.json()["detail"].lower()

    def test_add_availability_invalid_date_range(self):
        """Test adding availability with end_date before start_date fails."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org3", "name": "Availability Test Org 3"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_003",
                "org_id": "avail_test_org3",
                "name": "Test Person 3"
            }
        )

        # Try to add invalid timeoff period
        start = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")  # Before start
        response = client.post(
            f"{API_BASE}/availability/avail_person_003/timeoff",
            json={"start_date": start, "end_date": end}
        )
        assert response.status_code == 400


class TestAvailabilityRead:
    """Test availability retrieval."""

    def test_list_availability_by_person(self):
        """Test listing availability/timeoff for a specific person."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org4", "name": "Availability Test Org 4"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_004",
                "org_id": "avail_test_org4",
                "name": "Test Person 4"
            }
        )

        # Add multiple timeoff periods
        for i in range(3):
            start = (datetime.now() + timedelta(days=30 + i*10)).strftime("%Y-%m-%d")
            end = (datetime.now() + timedelta(days=35 + i*10)).strftime("%Y-%m-%d")
            client.post(
                f"{API_BASE}/availability/avail_person_004/timeoff",
                json={"start_date": start, "end_date": end}
            )

        # Retrieve timeoff list
        response = client.get(f"{API_BASE}/availability/avail_person_004/timeoff")
        assert response.status_code == 200
        data = response.json()
        assert "timeoff" in data
        assert "total" in data
        assert data["total"] >= 3
        assert len(data["timeoff"]) >= 3
        # Verify structure
        for item in data["timeoff"]:
            assert "id" in item
            assert "start_date" in item
            assert "end_date" in item

    def test_list_availability_empty(self):
        """Test listing availability for person with no timeoff."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org5", "name": "Availability Test Org 5"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_005",
                "org_id": "avail_test_org5",
                "name": "Test Person 5"
            }
        )

        # Retrieve timeoff list (should be empty)
        response = client.get(f"{API_BASE}/availability/avail_person_005/timeoff")
        assert response.status_code == 200
        data = response.json()
        assert data["timeoff"] == []
        assert data["total"] == 0

    def test_list_availability_nonexistent_person(self):
        """Test listing availability for non-existent person returns empty list."""
        response = client.get(f"{API_BASE}/availability/nonexistent_person/timeoff")
        assert response.status_code == 200
        data = response.json()
        # Should return empty list rather than 404
        assert data["timeoff"] == []
        assert data["total"] == 0


class TestAvailabilityDelete:
    """Test availability deletion."""

    def test_delete_availability_success(self):
        """Test successful deletion of availability/timeoff period."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org6", "name": "Availability Test Org 6"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_006",
                "org_id": "avail_test_org6",
                "name": "Test Person 6"
            }
        )

        # Add timeoff period
        start = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=65)).strftime("%Y-%m-%d")
        create_response = client.post(
            f"{API_BASE}/availability/avail_person_006/timeoff",
            json={"start_date": start, "end_date": end}
        )
        timeoff_id = create_response.json()["id"]

        # Delete timeoff period
        response = client.delete(
            f"{API_BASE}/availability/avail_person_006/timeoff/{timeoff_id}"
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"{API_BASE}/availability/avail_person_006/timeoff")
        data = response.json()
        assert data["total"] == 0

    def test_delete_availability_not_found(self):
        """Test deleting non-existent availability/timeoff returns 404."""
        # Setup: Create org and person
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org7", "name": "Availability Test Org 7"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_007",
                "org_id": "avail_test_org7",
                "name": "Test Person 7"
            }
        )

        # Try to delete non-existent timeoff
        response = client.delete(
            f"{API_BASE}/availability/avail_person_007/timeoff/99999"
        )
        assert response.status_code == 404

    def test_delete_availability_wrong_person(self):
        """Test deleting timeoff for wrong person returns 404."""
        # Setup: Create org and two persons
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "avail_test_org8", "name": "Availability Test Org 8"}
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_008",
                "org_id": "avail_test_org8",
                "name": "Test Person 8"
            }
        )
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "avail_person_009",
                "org_id": "avail_test_org8",
                "name": "Test Person 9"
            }
        )

        # Add timeoff for person 8
        start = (datetime.now() + timedelta(days=70)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=75)).strftime("%Y-%m-%d")
        create_response = client.post(
            f"{API_BASE}/availability/avail_person_008/timeoff",
            json={"start_date": start, "end_date": end}
        )
        timeoff_id = create_response.json()["id"]

        # Try to delete using person 9's endpoint
        response = client.delete(
            f"{API_BASE}/availability/avail_person_009/timeoff/{timeoff_id}"
        )
        assert response.status_code == 404
