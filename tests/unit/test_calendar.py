"""Unit tests for calendar export and subscription endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from api.main import app
from api.utils.calendar_utils import (
    generate_calendar_token,
    generate_ics_from_assignments,
    generate_ics_from_events,
    generate_webcal_url,
    generate_https_feed_url,
)

API_BASE = "http://localhost:8000/api"


class TestCalendarUtils:
    """Test calendar utility functions."""

    def test_generate_calendar_token(self, client):
        """Test calendar token generation."""
        token1 = generate_calendar_token()
        token2 = generate_calendar_token()

        # URL-safe base64 encoding of 32 bytes = ~43 characters
        assert len(token1) >= 40
        assert len(token2) >= 40
        assert token1 != token2  # Tokens should be unique

    def test_generate_webcal_url(self, client):
        """Test webcal URL generation."""
        token = "test_token_123"

        # Test with https://
        url1 = generate_webcal_url("https://rostio.app", token)
        assert url1 == "webcal://rostio.app/api/calendar/feed/test_token_123"

        # Test with http://
        url2 = generate_webcal_url("http://localhost:8000", token)
        assert url2 == "webcal://localhost:8000/api/calendar/feed/test_token_123"

    def test_generate_https_feed_url(self, client):
        """Test HTTPS feed URL generation."""
        token = "test_token_123"

        url1 = generate_https_feed_url("https://rostio.app", token)
        assert url1 == "https://rostio.app/api/calendar/feed/test_token_123"

        url2 = generate_https_feed_url("rostio.app", token)
        assert url2 == "https://rostio.app/api/calendar/feed/test_token_123"

    def test_generate_ics_from_assignments(self, client):
        """Test ICS generation from assignments."""
        assignments = [
            {
                "id": 1,
                "person": {
                    "id": "person_1",
                    "name": "John Doe",
                },
                "event": {
                    "id": "event_1",
                    "type": "Sunday Service",
                    "start_time": datetime(2025, 10, 11, 10, 0),
                    "end_time": datetime(2025, 10, 11, 11, 30),
                    "extra_data": {"notes": "Main sanctuary"},
                    "resource": {
                        "location": "Main Church Building"
                    }
                },
                "role": "Greeter"
            }
        ]

        ics_content = generate_ics_from_assignments(assignments, "Test Calendar")

        # Verify ICS format
        assert "BEGIN:VCALENDAR" in ics_content
        assert "END:VCALENDAR" in ics_content
        assert "BEGIN:VEVENT" in ics_content
        assert "END:VEVENT" in ics_content

        # Verify calendar metadata
        assert "PRODID:-//Rostio//Calendar Export//EN" in ics_content
        assert "VERSION:2.0" in ics_content
        assert "X-WR-CALNAME:Test Calendar" in ics_content

        # Verify event data
        assert "SUMMARY:Sunday Service - Greeter" in ics_content
        assert "LOCATION:Main Church Building" in ics_content

    def test_generate_ics_from_events(self, client):
        """Test ICS generation from events (admin export)."""
        events = [
            {
                "id": "event_1",
                "type": "Sunday Service",
                "start_time": datetime(2025, 10, 11, 10, 0),
                "end_time": datetime(2025, 10, 11, 11, 30),
                "extra_data": {},
                "resource": {
                    "location": "Main Church"
                },
                "assignments": [
                    {
                        "person": {"name": "John Doe"},
                        "role": "Greeter"
                    }
                ]
            }
        ]

        ics_content = generate_ics_from_events(events, "Org Events", include_assignments=True)

        assert "BEGIN:VCALENDAR" in ics_content
        assert "SUMMARY:Sunday Service" in ics_content
        assert "LOCATION:Main Church" in ics_content
        # Assignments should be in description
        assert "John Doe" in ics_content


class TestCalendarExportAPI:
    """Test calendar export API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, client):
        """Create test organization, person, events, and assignments."""
        # Create organization
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "calendar_test_org", "name": "Calendar Test Org"}
        )

        # Create person
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "calendar_person_1",
                "org_id": "calendar_test_org",
                "name": "Test User",
                "email": "testuser@example.com",
                "roles": ["volunteer"],
                "timezone": "America/New_York"
            }
        )

        # Create resource
        client.post(
            f"{API_BASE}/organizations/calendar_test_org/resources",
            json={
                "id": "resource_1",
                "type": "venue",
                "location": "Test Church Building"
            }
        )

        # Create event
        start_time = (datetime.utcnow() + timedelta(days=7)).isoformat()
        end_time = (datetime.utcnow() + timedelta(days=7, hours=2)).isoformat()

        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "calendar_event_1",
                "org_id": "calendar_test_org",
                "type": "Sunday Service",
                "start_time": start_time,
                "end_time": end_time,
                "resource_id": "resource_1"
            }
        )

    def test_export_personal_schedule_no_assignments(self, client):
        """Test exporting personal schedule when no assignments exist."""
        response = client.get(f"{API_BASE}/calendar/export?person_id=calendar_person_1")

        # Should return 404 if no assignments
        assert response.status_code == 404
        assert "No assignments found" in response.json()["detail"]

    def test_get_subscription_url(self, client):
        """Test getting calendar subscription URL."""
        response = client.get(f"{API_BASE}/calendar/subscribe?person_id=calendar_person_1")

        assert response.status_code == 200
        data = response.json()

        assert "token" in data
        assert "webcal_url" in data
        assert "https_url" in data
        assert "message" in data

        # Verify URL format
        assert data["webcal_url"].startswith("webcal://")
        assert data["https_url"].startswith("http")
        assert data["token"] in data["webcal_url"]
        assert data["token"] in data["https_url"]

    def test_get_subscription_url_reuses_token(self, client):
        """Test that subscription URL reuses existing token."""
        # First request
        response1 = client.get(f"{API_BASE}/calendar/subscribe?person_id=calendar_person_1")
        token1 = response1.json()["token"]

        # Second request
        response2 = client.get(f"{API_BASE}/calendar/subscribe?person_id=calendar_person_1")
        token2 = response2.json()["token"]

        # Tokens should be the same
        assert token1 == token2

    def test_reset_calendar_token(self, client):
        """Test resetting calendar subscription token."""
        # Get initial token
        response1 = client.get(f"{API_BASE}/calendar/subscribe?person_id=calendar_person_1")
        token1 = response1.json()["token"]

        # Reset token
        response2 = client.post(f"{API_BASE}/calendar/reset-token?person_id=calendar_person_1")
        assert response2.status_code == 200
        token2 = response2.json()["token"]

        # Tokens should be different
        assert token1 != token2
        assert len(token2) >= 40  # URL-safe base64 encoding

    def test_calendar_feed_invalid_token(self, client):
        """Test calendar feed with invalid token."""
        response = client.get(f"{API_BASE}/calendar/feed/invalid_token_12345")

        assert response.status_code == 404
        assert "Invalid calendar token" in response.json()["detail"]

    def test_calendar_feed_valid_token_no_assignments(self, client):
        """Test calendar feed with valid token but no assignments."""
        # Get subscription URL to generate token
        sub_response = client.get(f"{API_BASE}/calendar/subscribe?person_id=calendar_person_1")
        token = sub_response.json()["token"]

        # Access feed
        response = client.get(f"{API_BASE}/calendar/feed/{token}")

        # Should succeed but return empty calendar
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")

        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content

    def test_export_nonexistent_person(self, client):
        """Test exporting calendar for non-existent person."""
        response = client.get(f"{API_BASE}/calendar/export?person_id=nonexistent_person")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_subscription_nonexistent_person(self, client):
        """Test getting subscription for non-existent person."""
        response = client.get(f"{API_BASE}/calendar/subscribe?person_id=nonexistent_person")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestOrganizationExport:
    """Test organization-wide event export."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, client):
        """Create test organization with admin and events."""
        # Create organization
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "org_export_test", "name": "Org Export Test"}
        )

        # Create admin
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "admin_person_1",
                "org_id": "org_export_test",
                "name": "Admin User",
                "email": "admin@example.com",
                "roles": ["admin"]
            }
        )

        # Create volunteer
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "volunteer_person_1",
                "org_id": "org_export_test",
                "name": "Volunteer User",
                "email": "volunteer@example.com",
                "roles": ["volunteer"]
            }
        )

        # Create event
        start_time = (datetime.utcnow() + timedelta(days=7)).isoformat()
        end_time = (datetime.utcnow() + timedelta(days=7, hours=2)).isoformat()

        client.post(
            f"{API_BASE}/events/",
            json={
                "id": "org_event_1",
                "org_id": "org_export_test",
                "type": "Team Meeting",
                "start_time": start_time,
                "end_time": end_time
            }
        )

    def test_org_export_as_admin(self, client):
        """Test organization export as admin."""
        response = client.get(
            f"{API_BASE}/calendar/org/export?org_id=org_export_test&person_id=admin_person_1"
        )

        assert response.status_code == 200
        assert "text/calendar" in response.headers["content-type"]

        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "Team Meeting" in content

    def test_org_export_as_volunteer_denied(self, client):
        """Test organization export as volunteer is denied."""
        response = client.get(
            f"{API_BASE}/calendar/org/export?org_id=org_export_test&person_id=volunteer_person_1"
        )

        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    def test_org_export_nonexistent_org(self, client):
        """Test organization export for non-existent org."""
        response = client.get(
            f"{API_BASE}/calendar/org/export?org_id=nonexistent_org&person_id=admin_person_1"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_org_export_no_events(self, client):
        """Test organization export when no events exist."""
        # Create new org with no events
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "empty_org", "name": "Empty Org"}
        )

        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "empty_org_admin",
                "org_id": "empty_org",
                "name": "Empty Admin",
                "roles": ["admin"]
            }
        )

        response = client.get(
            f"{API_BASE}/calendar/org/export?org_id=empty_org&person_id=empty_org_admin"
        )

        assert response.status_code == 404
        assert "No events found" in response.json()["detail"]


class TestCalendarIntegration:
    """Integration tests for complete calendar workflows."""

    def test_complete_subscription_workflow(self, client):
        """Test complete workflow: create person -> subscribe -> feed."""
        # 1. Create organization
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": "workflow_org", "name": "Workflow Test Org"}
        )

        # 2. Create person
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": "workflow_person",
                "org_id": "workflow_org",
                "name": "Workflow User",
                "email": "workflow@example.com",
                "roles": ["volunteer"]
            }
        )

        # 3. Get subscription URL
        sub_response = client.get(f"{API_BASE}/calendar/subscribe?person_id=workflow_person")
        assert sub_response.status_code == 200
        token = sub_response.json()["token"]

        # 4. Access calendar feed
        feed_response = client.get(f"{API_BASE}/calendar/feed/{token}")
        assert feed_response.status_code == 200
        assert "text/calendar" in feed_response.headers["content-type"]

        # 5. Verify ICS format
        content = feed_response.text
        assert "BEGIN:VCALENDAR" in content
        assert "PRODID:-//Rostio//Calendar Export//EN" in content
        assert "VERSION:2.0" in content
