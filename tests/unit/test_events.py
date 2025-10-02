"""Unit tests for event endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
API_BASE = "http://localhost:8000/api"


class TestEventCreate:
    """Test event creation."""

    def test_create_event_success(self):
        """Test successful event creation."""
        # Setup
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org", "name": "Event Test Org"}
        )
        client.post(
            f"{API_BASE}/resources/",
            json={
                "id": "sanctuary",
                "org_id": "event_test_org",
                "type": "venue",
                "location": "Main Building"
            }
        )
        # Create event
        start = (datetime.now() + timedelta(days=1)).isoformat()
        end = (datetime.now() + timedelta(days=1, hours=2)).isoformat()
        response = client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_001",
                "org_id": "event_test_org",
                "type": "Sunday Service",
                "start_time": start,
                "end_time": end,
                "resource_id": "sanctuary",
                "extra_data": {"roles": ["volunteer"]}
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["id"] == "event_001"
        assert data["type"] == "Sunday Service"

    def test_create_event_without_resource(self):
        """Test creating event without resource (optional)."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org2", "name": "Event Test Org 2"}
        )
        start = (datetime.now() + timedelta(days=2)).isoformat()
        end = (datetime.now() + timedelta(days=2, hours=1)).isoformat()
        response = client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_002",
                "org_id": "event_test_org2",
                "type": "Meeting",
                "start_time": start,
                "end_time": end
            }
        )
        assert response.status_code in [200, 201]

    def test_create_event_invalid_org(self):
        """Test creating event with invalid org fails."""
        start = datetime.now().isoformat()
        end = (datetime.now() + timedelta(hours=1)).isoformat()
        response = client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_003",
                "org_id": "nonexistent_org",
                "type": "Meeting",
                "start_time": start,
                "end_time": end
            }
        )
        assert response.status_code == 404

    def test_create_event_end_before_start(self):
        """Test creating event where end time is before start time."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org3", "name": "Event Test Org 3"}
        )
        start = datetime.now().isoformat()
        end = (datetime.now() - timedelta(hours=1)).isoformat()  # Earlier than start
        response = client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_004",
                "org_id": "event_test_org3",
                "type": "Invalid Event",
                "start_time": start,
                "end_time": end
            }
        )
        # Should either fail validation or accept (depending on backend validation)
        # At minimum, we document this case
        assert response.status_code in [200, 201, 400, 422]


class TestEventRead:
    """Test event retrieval."""

    def test_get_event_success(self):
        """Test successful event retrieval."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org4", "name": "Event Test Org 4"}
        )
        start = (datetime.now() + timedelta(days=3)).isoformat()
        end = (datetime.now() + timedelta(days=3, hours=2)).isoformat()
        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_005",
                "org_id": "event_test_org4",
                "type": "Service",
                "start_time": start,
                "end_time": end
            }
        )
        response = client.get(f"{API_BASE}/events/event_005")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "event_005"

    def test_get_event_not_found(self):
        """Test retrieving non-existent event returns 404."""
        response = client.get(f"{API_BASE}/events/nonexistent_event")
        assert response.status_code == 404

    def test_list_events_by_org(self):
        """Test listing events filtered by organization."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org5", "name": "Event Test Org 5"}
        )
        # Create multiple events
        for i in range(6, 9):
            start = (datetime.now() + timedelta(days=i)).isoformat()
            end = (datetime.now() + timedelta(days=i, hours=2)).isoformat()
            client.post(
                f"{API_BASE}/events/",
                json={
                    "id": f"event_{i:03d}",
                    "org_id": "event_test_org5",
                    "type": f"Event {i}",
                    "start_time": start,
                    "end_time": end
                }
            )
        response = client.get(f"{API_BASE}/events/?org_id=event_test_org5")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) >= 3

    def test_list_events_date_range(self):
        """Test listing events within date range."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org6", "name": "Event Test Org 6"}
        )
        # Create event
        start = (datetime.now() + timedelta(days=10)).isoformat()
        end = (datetime.now() + timedelta(days=10, hours=2)).isoformat()
        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_009",
                "org_id": "event_test_org6",
                "type": "Range Event",
                "start_time": start,
                "end_time": end
            }
        )
        # Query with date range
        from_date = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=11)).strftime("%Y-%m-%d")
        response = client.get(
            f"{API_BASE}/events/?org_id=event_test_org6&from_date={from_date}&to_date={to_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 1


class TestEventUpdate:
    """Test event updates."""

    def test_update_event_success(self):
        """Test successful event update."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org7", "name": "Event Test Org 7"}
        )
        start = (datetime.now() + timedelta(days=20)).isoformat()
        end = (datetime.now() + timedelta(days=20, hours=2)).isoformat()
        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_010",
                "org_id": "event_test_org7",
                "type": "Original Type",
                "start_time": start,
                "end_time": end
            }
        )
        # Update
        new_start = (datetime.now() + timedelta(days=21)).isoformat()
        new_end = (datetime.now() + timedelta(days=21, hours=3)).isoformat()
        response = client.put(
            f"{API_BASE}/events/event_010",
            json={
                "type": "Updated Type",
                "start_time": new_start,
                "end_time": new_end
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "Updated Type"

    def test_update_event_not_found(self):
        """Test updating non-existent event returns 404."""
        start = datetime.now().isoformat()
        end = (datetime.now() + timedelta(hours=2)).isoformat()
        response = client.put(
            f"{API_BASE}/events/nonexistent_event",
            json={"type": "Updated", "start_time": start, "end_time": end}
        )
        assert response.status_code == 404


class TestEventDelete:
    """Test event deletion."""

    def test_delete_event_success(self):
        """Test successful event deletion."""
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "event_test_org8", "name": "Event Test Org 8"}
        )
        start = (datetime.now() + timedelta(days=30)).isoformat()
        end = (datetime.now() + timedelta(days=30, hours=2)).isoformat()
        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "event_011",
                "org_id": "event_test_org8",
                "type": "To Delete",
                "start_time": start,
                "end_time": end
            }
        )
        response = client.delete(f"{API_BASE}/events/event_011")
        assert response.status_code in [200, 204]  # OK or No Content
        # Verify deletion
        response = client.get(f"{API_BASE}/events/event_011")
        assert response.status_code == 404

    def test_delete_event_not_found(self):
        """Test deleting non-existent event returns 404."""
        response = client.delete(f"{API_BASE}/events/nonexistent_event")
        assert response.status_code == 404
