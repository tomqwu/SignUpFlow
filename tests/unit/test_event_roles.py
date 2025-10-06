"""
Unit tests for event-specific roles functionality.

Tests the ability to assign people to events with specific roles
(e.g., "usher", "greeter", "sound_tech") rather than generic assignment.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from roster_cli.db.models import Organization, Person, Event, Assignment
from api.database import Base, engine
import time

client = TestClient(app)
API_BASE = "/api"


class TestEventRoleAssignment:
    """Test assigning people to events with specific roles."""

    def test_assign_person_with_role(self):
        """Test assigning a person to an event with a specific role."""
        timestamp = int(time.time() * 1000)
        org_id = f"role_org_{timestamp}"
        person_id = f"role_person_{timestamp}"
        event_id = f"role_event_{timestamp}"

        # Create org
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})

        # Create person
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "John Usher",
            "email": f"john_{timestamp}@test.com",
            "roles": ["volunteer"]
        })

        # Create event
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign person with role
        response = client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "usher"
        })

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "usher" in data["message"].lower()
        assert data["role"] == "usher"

    def test_assign_person_with_different_roles(self):
        """Test that the same person can have different roles in different events."""
        timestamp = int(time.time() * 1000)
        org_id = f"multi_role_org_{timestamp}"
        person_id = f"multi_role_person_{timestamp}"
        event1_id = f"event1_{timestamp}"
        event2_id = f"event2_{timestamp}"

        # Create org
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})

        # Create person
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "Jane Multirole",
            "email": f"jane_{timestamp}@test.com",
            "roles": ["volunteer"]
        })

        # Create two events
        client.post(f"{API_BASE}/events/", json={
            "id": event1_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event2_id,
            "org_id": org_id,
            "type": "wednesday_service",
            "start_time": "2025-12-27T19:00:00",
            "end_time": "2025-12-27T20:30:00"
        })

        # Assign to event 1 as usher
        response1 = client.post(f"{API_BASE}/events/{event1_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "usher"
        })
        assert response1.status_code == 200
        assert response1.json()["role"] == "usher"

        # Assign to event 2 as greeter
        response2 = client.post(f"{API_BASE}/events/{event2_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "greeter"
        })
        assert response2.status_code == 200
        assert response2.json()["role"] == "greeter"

        # Verify both assignments exist with different roles
        assignments_response = client.get(f"{API_BASE}/events/assignments/all", params={"org_id": org_id})
        assert assignments_response.status_code == 200
        assignments = assignments_response.json()["assignments"]

        # Find both assignments
        event1_assignment = next((a for a in assignments if a["event_id"] == event1_id), None)
        event2_assignment = next((a for a in assignments if a["event_id"] == event2_id), None)

        assert event1_assignment is not None
        assert event1_assignment["role"] == "usher"
        assert event2_assignment is not None
        assert event2_assignment["role"] == "greeter"

    def test_assign_without_role(self):
        """Test that assigning without a role still works (role is optional)."""
        timestamp = int(time.time() * 1000)
        org_id = f"no_role_org_{timestamp}"
        person_id = f"no_role_person_{timestamp}"
        event_id = f"no_role_event_{timestamp}"

        # Create org, person, and event
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "Bob Norole",
            "email": f"bob_{timestamp}@test.com",
            "roles": ["volunteer"]
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign without specifying role
        response = client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["role"] is None

    def test_get_assignments_includes_roles(self):
        """Test that fetching assignments returns role information."""
        timestamp = int(time.time() * 1000)
        org_id = f"get_role_org_{timestamp}"
        person_id = f"get_role_person_{timestamp}"
        event_id = f"get_role_event_{timestamp}"

        # Create org, person, and event
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "Alice Sound",
            "email": f"alice_{timestamp}@test.com",
            "roles": ["volunteer"]
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign with role
        client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "sound_tech"
        })

        # Get all assignments
        response = client.get(f"{API_BASE}/events/assignments/all", params={"org_id": org_id})
        assert response.status_code == 200

        assignments = response.json()["assignments"]
        assert len(assignments) > 0

        # Find our assignment
        our_assignment = next((a for a in assignments if a["person_id"] == person_id), None)
        assert our_assignment is not None
        assert our_assignment["role"] == "sound_tech"


class TestEventRoleValidation:
    """Test validation and edge cases for event roles."""

    def test_custom_role_name(self):
        """Test that custom role names can be used."""
        timestamp = int(time.time() * 1000)
        org_id = f"custom_role_org_{timestamp}"
        person_id = f"custom_role_person_{timestamp}"
        event_id = f"custom_role_event_{timestamp}"

        # Setup
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "Chris Custom",
            "email": f"chris_{timestamp}@test.com",
            "roles": ["volunteer"]
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "special_event",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign with custom role
        response = client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "Coffee Barista"  # Custom role
        })

        assert response.status_code == 200
        assert response.json()["role"] == "Coffee Barista"

    def test_role_persists_after_assignment(self):
        """Test that role information persists correctly in database."""
        timestamp = int(time.time() * 1000)
        org_id = f"persist_role_org_{timestamp}"
        person_id = f"persist_role_person_{timestamp}"
        event_id = f"persist_role_event_{timestamp}"

        # Setup
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "David Persist",
            "email": f"david_{timestamp}@test.com",
            "roles": ["volunteer"]
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign with role
        assign_response = client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": "worship_leader"
        })
        assert assign_response.status_code == 200

        # Fetch assignments again to verify persistence
        response = client.get(f"{API_BASE}/events/assignments/all", params={"org_id": org_id})
        assignments = response.json()["assignments"]

        our_assignment = next((a for a in assignments if a["person_id"] == person_id), None)
        assert our_assignment is not None
        assert our_assignment["role"] == "worship_leader"

    def test_empty_string_role(self):
        """Test that empty string role is handled correctly."""
        timestamp = int(time.time() * 1000)
        org_id = f"empty_role_org_{timestamp}"
        person_id = f"empty_role_person_{timestamp}"
        event_id = f"empty_role_event_{timestamp}"

        # Setup
        client.post(f"{API_BASE}/organizations/", json={"id": org_id, "name": "Test Org", "region": "Test"})
        client.post(f"{API_BASE}/people/", json={
            "id": person_id,
            "org_id": org_id,
            "name": "Emma Empty",
            "email": f"emma_{timestamp}@test.com",
            "roles": ["volunteer"]
        })
        client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": "sunday_service",
            "start_time": "2025-12-25T10:00:00",
            "end_time": "2025-12-25T12:00:00"
        })

        # Assign with empty string role
        response = client.post(f"{API_BASE}/events/{event_id}/assignments", json={
            "person_id": person_id,
            "action": "assign",
            "role": ""
        })

        # Should work - empty string is valid (will be stored as empty string, not null)
        assert response.status_code == 200
