"""
Event CRUD + conflict detection + availability management.

Covers the full lifecycle of events and the guard rails around scheduling:
  create → read → update → delete
  conflict detection: double-booking, time-off overlap, duplicate assignment
  availability: add time-off, delete time-off
  event validation and available-people queries
"""

from datetime import datetime, timedelta

import pytest

from tests.api.conftest import (
    add_timeoff,
    auth_headers,
    seed_event,
    seed_org,
    seed_user,
)


@pytest.mark.no_mock_auth
class TestEventCRUD:
    """Full event lifecycle: create, read, update, delete."""

    ORG = "crud-org"
    ADMIN_EMAIL = "admin@crud.org"
    ADMIN_PW = "AdminPass123!"

    def _setup(self, client):
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        return auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

    def test_create_event(self, client):
        """Admin creates an event with role requirements."""
        hdrs = self._setup(client)
        event = seed_event(
            client,
            hdrs,
            self.ORG,
            "evt-1",
            event_type="Sunday Worship",
            role_counts={"musician": 2, "usher": 1},
        )
        assert event["id"] == "evt-1"
        assert event["org_id"] == self.ORG
        assert event["extra_data"]["role_counts"]["musician"] == 2

    def test_get_single_event(self, client):
        """Retrieve a single event by ID."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-get")

        resp = client.get("/api/events/evt-get")
        assert resp.status_code == 200
        assert resp.json()["id"] == "evt-get"

    def test_get_nonexistent_event_returns_404(self, client):
        """Getting a missing event returns 404."""
        self._setup(client)
        resp = client.get("/api/events/does-not-exist")
        assert resp.status_code == 404

    def test_list_events_filtered_by_org(self, client):
        """List events returns only events for the specified org."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-a", days_from_now=14)
        seed_event(client, hdrs, self.ORG, "evt-b", days_from_now=21)

        resp = client.get(f"/api/events/?org_id={self.ORG}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    def test_update_event_type(self, client):
        """Admin updates an event's type and role counts."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-update", event_type="Regular Service")

        resp = client.put(
            "/api/events/evt-update",
            json={
                "type": "Easter Service",
                "extra_data": {"role_counts": {"musician": 3, "usher": 2}},
            },
            headers=hdrs,
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["type"] == "Easter Service"
        assert updated["extra_data"]["role_counts"]["musician"] == 3

    def test_update_event_time(self, client):
        """Admin reschedules an event to a different time."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-reschedule")

        new_start = (datetime.now() + timedelta(days=30)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        new_end = new_start + timedelta(hours=3)

        resp = client.put(
            "/api/events/evt-reschedule",
            json={
                "start_time": new_start.isoformat(),
                "end_time": new_end.isoformat(),
            },
            headers=hdrs,
        )
        assert resp.status_code == 200
        assert "T10:00:00" in resp.json()["start_time"]

    def test_update_nonexistent_event_returns_404(self, client):
        """Updating a missing event returns 404."""
        hdrs = self._setup(client)
        resp = client.put("/api/events/ghost", json={"type": "X"}, headers=hdrs)
        assert resp.status_code == 404

    def test_delete_event(self, client):
        """Admin deletes an event; it disappears from list."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-delete")

        resp = client.delete("/api/events/evt-delete", headers=hdrs)
        assert resp.status_code == 204

        # Verify gone
        resp = client.get("/api/events/evt-delete")
        assert resp.status_code == 404

    def test_delete_nonexistent_event_returns_404(self, client):
        """Deleting a missing event returns 404."""
        hdrs = self._setup(client)
        resp = client.delete("/api/events/ghost", headers=hdrs)
        assert resp.status_code == 404

    def test_volunteer_cannot_update_event(self, client):
        """Volunteer gets 403 trying to update an event."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-protected")
        seed_user(client, self.ORG, "vol@crud.org", "Vol", "VolPass123!")
        vol_hdrs = auth_headers(client, "vol@crud.org", "VolPass123!")

        resp = client.put("/api/events/evt-protected", json={"type": "Hacked"}, headers=vol_hdrs)
        assert resp.status_code == 403

    def test_volunteer_cannot_delete_event(self, client):
        """Volunteer gets 403 trying to delete an event."""
        hdrs = self._setup(client)
        seed_event(client, hdrs, self.ORG, "evt-nodelete")
        seed_user(client, self.ORG, "vol@crud.org", "Vol", "VolPass123!")
        vol_hdrs = auth_headers(client, "vol@crud.org", "VolPass123!")

        resp = client.delete("/api/events/evt-nodelete", headers=vol_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestConflictDetection:
    """Detect scheduling conflicts before assigning volunteers."""

    ORG = "conflict-org"
    ADMIN_EMAIL = "admin@conflict.org"
    ADMIN_PW = "AdminPass123!"

    def _setup_with_volunteer(self, client):
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, "sarah@conflict.org", "Sarah", "VolPass123!")
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)
        return hdrs, vol

    def test_no_conflicts_for_clean_assignment(self, client):
        """No conflicts when person is free and not already assigned."""
        hdrs, vol = self._setup_with_volunteer(client)
        event = seed_event(client, hdrs, self.ORG, "evt-clean", days_from_now=14)

        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": vol["person_id"],
                "event_id": event["id"],
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["has_conflicts"] is False
        assert result["can_assign"] is True

    def test_detect_already_assigned(self, client):
        """Conflict detected when person is already assigned to the event."""
        hdrs, vol = self._setup_with_volunteer(client)
        event = seed_event(client, hdrs, self.ORG, "evt-dup", days_from_now=14)

        # Assign first
        client.post(
            f"/api/events/{event['id']}/assignments",
            json={
                "person_id": vol["person_id"],
                "action": "assign",
                "role": "volunteer",
            },
            headers=hdrs,
        )

        # Check conflicts — should detect already_assigned
        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": vol["person_id"],
                "event_id": event["id"],
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["has_conflicts"] is True
        assert result["can_assign"] is False
        assert any(c["type"] == "already_assigned" for c in result["conflicts"])

    def test_detect_time_off_conflict(self, client):
        """Conflict detected when person has time-off overlapping the event."""
        hdrs, vol = self._setup_with_volunteer(client)

        event_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        event = seed_event(client, hdrs, self.ORG, "evt-timeoff", days_from_now=14)

        # Sarah blocks that day
        add_timeoff(client, vol["person_id"], event_date, event_date, reason="Family vacation")

        # Check conflicts — should detect time_off
        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": vol["person_id"],
                "event_id": event["id"],
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["has_conflicts"] is True
        assert result["can_assign"] is False
        assert any(c["type"] == "time_off" for c in result["conflicts"])

    def test_detect_double_booking(self, client):
        """Conflict detected when person is assigned to another event at the same time."""
        hdrs, vol = self._setup_with_volunteer(client)

        # Two events at the same time
        evt_a = seed_event(client, hdrs, self.ORG, "evt-a", days_from_now=14)
        evt_b = seed_event(client, hdrs, self.ORG, "evt-b", days_from_now=14)

        # Assign to event A
        client.post(
            f"/api/events/{evt_a['id']}/assignments",
            json={
                "person_id": vol["person_id"],
                "action": "assign",
                "role": "volunteer",
            },
            headers=hdrs,
        )

        # Check conflicts for event B — should detect double_booked
        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": vol["person_id"],
                "event_id": evt_b["id"],
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["has_conflicts"] is True
        # Double-booking is a warning, not blocking
        assert result["can_assign"] is True
        assert any(c["type"] == "double_booked" for c in result["conflicts"])

    def test_conflict_check_nonexistent_person(self, client):
        """Conflict check with invalid person_id returns 404."""
        hdrs, _ = self._setup_with_volunteer(client)
        event = seed_event(client, hdrs, self.ORG, "evt-x", days_from_now=14)

        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": "ghost-person",
                "event_id": event["id"],
            },
        )
        assert resp.status_code == 404

    def test_conflict_check_nonexistent_event(self, client):
        """Conflict check with invalid event_id returns 404."""
        hdrs, vol = self._setup_with_volunteer(client)

        resp = client.post(
            "/api/conflicts/check",
            json={
                "person_id": vol["person_id"],
                "event_id": "ghost-event",
            },
        )
        assert resp.status_code == 404


@pytest.mark.no_mock_auth
class TestAvailabilityManagement:
    """Time-off CRUD: add, list, delete."""

    ORG = "avail-org"
    ADMIN_EMAIL = "admin@avail.org"
    ADMIN_PW = "AdminPass123!"

    def _setup_with_volunteer(self, client):
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, "vol@avail.org", "Sarah", "VolPass123!")
        return vol

    def test_add_and_list_timeoff(self, client):
        """Add time-off and verify it appears in the list."""
        vol = self._setup_with_volunteer(client)
        pid = vol["person_id"]

        add_timeoff(client, pid, "2026-06-01", "2026-06-07", reason="Vacation")

        resp = client.get(f"/api/availability/{pid}/timeoff")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["timeoff"][0]["reason"] == "Vacation"
        assert data["timeoff"][0]["start_date"] == "2026-06-01"

    def test_add_multiple_timeoff_periods(self, client):
        """Person can have multiple non-overlapping time-off periods."""
        vol = self._setup_with_volunteer(client)
        pid = vol["person_id"]

        add_timeoff(client, pid, "2026-06-01", "2026-06-07", reason="Vacation 1")
        add_timeoff(client, pid, "2026-07-01", "2026-07-07", reason="Vacation 2")

        resp = client.get(f"/api/availability/{pid}/timeoff")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    def test_delete_timeoff(self, client):
        """Delete a time-off period; it disappears from the list."""
        vol = self._setup_with_volunteer(client)
        pid = vol["person_id"]

        add_timeoff(client, pid, "2026-08-01", "2026-08-07", reason="To be deleted")

        # Get the timeoff ID
        resp = client.get(f"/api/availability/{pid}/timeoff")
        timeoff_id = resp.json()["timeoff"][0]["id"]

        # Delete it
        resp = client.delete(f"/api/availability/{pid}/timeoff/{timeoff_id}")
        assert resp.status_code == 204

        # Verify gone
        resp = client.get(f"/api/availability/{pid}/timeoff")
        assert resp.json()["total"] == 0

    def test_timeoff_for_unknown_person_returns_empty(self, client):
        """Querying time-off for a non-existent person returns empty list."""
        self._setup_with_volunteer(client)
        resp = client.get("/api/availability/ghost-person/timeoff")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


@pytest.mark.no_mock_auth
class TestProfileAndTeamMembers:
    """Profile update and team member management."""

    ORG = "profile-org"
    ADMIN_EMAIL = "admin@profile.org"
    ADMIN_PW = "AdminPass123!"

    def test_volunteer_updates_own_profile(self, client):
        """Volunteer can update their own name and timezone."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        seed_user(client, self.ORG, "vol@profile.org", "Old Name", "VolPass123!")
        vol_hdrs = auth_headers(client, "vol@profile.org", "VolPass123!")

        resp = client.put(
            "/api/people/me",
            json={
                "name": "New Name",
                "timezone": "US/Pacific",
            },
            headers=vol_hdrs,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["timezone"] == "US/Pacific"

    def test_add_and_remove_team_members(self, client):
        """Admin adds a member to a team, then removes them."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, "vol@profile.org", "Sarah", "VolPass123!")
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        # Create empty team
        resp = client.post(
            "/api/teams/",
            json={
                "id": "team-1",
                "org_id": self.ORG,
                "name": "Ushers",
            },
            headers=hdrs,
        )
        assert resp.status_code == 201

        # Add member
        resp = client.post(
            "/api/teams/team-1/members",
            json={
                "person_ids": [vol["person_id"]],
            },
            headers=hdrs,
        )
        assert resp.status_code == 204

        # Verify member count increased
        resp = client.get("/api/teams/team-1", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["member_count"] == 1

        # Remove member (DELETE with body requires request method)
        resp = client.request(
            "DELETE",
            "/api/teams/team-1/members",
            json={
                "person_ids": [vol["person_id"]],
            },
            headers=hdrs,
        )
        assert resp.status_code == 204

        # Verify member count back to 0
        resp = client.get("/api/teams/team-1", headers=hdrs)
        assert resp.json()["member_count"] == 0
