"""
Unit tests for event helper functions.

Tests the refactored helper functions extracted from api/routers/events.py
to ensure DRY principles and single responsibility.

Note: Only testing pure functions without database dependencies.
Database-dependent functions are tested via integration tests in test_events.py.
"""

import pytest
from datetime import date, datetime

from api.utils.event_helpers import (
    person_has_matching_role,
    get_event_required_roles,
    count_people_with_role,
    validate_time_range
)
from api.models import Person, Event


class TestPersonHasMatchingRole:
    """Test person_has_matching_role helper function."""

    def test_no_roles_required_returns_true(self):
        """Test that empty required_roles returns True for any person."""
        result = person_has_matching_role(["admin"], [])

        assert result is True

    def test_matching_role_returns_true(self):
        """Test person with matching role returns True."""
        result = person_has_matching_role(["usher", "greeter"], ["usher"])

        assert result is True

    def test_no_matching_role_returns_false(self):
        """Test person without matching role returns False."""
        result = person_has_matching_role(["admin"], ["usher", "greeter"])

        assert result is False

    def test_multiple_matching_roles(self):
        """Test person with multiple matching roles returns True."""
        result = person_has_matching_role(
            ["usher", "greeter", "sound_tech"],
            ["greeter", "sound_tech"]
        )

        assert result is True

    def test_empty_person_roles_returns_false(self):
        """Test person with no roles and required roles returns False."""
        result = person_has_matching_role([], ["usher"])

        assert result is False


class TestGetEventRequiredRoles:
    """Test get_event_required_roles helper function."""

    def test_role_counts_returns_role_names(self):
        """Test extracts roles from role_counts in extra_data."""
        event = Event(
            id="test_event",
            org_id="test_org",
            type="Service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
            extra_data={
                "role_counts": {
                    "usher": 2,
                    "greeter": 1,
                    "sound_tech": 1
                }
            }
        )

        result = get_event_required_roles(event)

        assert set(result) == {"usher", "greeter", "sound_tech"}

    def test_roles_array_fallback(self):
        """Test falls back to roles array if no role_counts."""
        event = Event(
            id="test_event",
            org_id="test_org",
            type="Service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
            extra_data={"roles": ["usher", "greeter"]}
        )

        result = get_event_required_roles(event)

        assert result == ["usher", "greeter"]

    def test_no_roles_returns_empty_list(self):
        """Test returns empty list if no roles configured."""
        event = Event(
            id="test_event",
            org_id="test_org",
            type="Service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
            extra_data={}
        )

        result = get_event_required_roles(event)

        assert result == []

    def test_none_extra_data_returns_empty_list(self):
        """Test handles None extra_data gracefully."""
        event = Event(
            id="test_event",
            org_id="test_org",
            type="Service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
            extra_data=None
        )

        result = get_event_required_roles(event)

        assert result == []


class TestCountPeopleWithRole:
    """Test count_people_with_role helper function."""

    def test_no_people_returns_zero(self):
        """Test empty people list returns 0."""
        result = count_people_with_role([], "usher")

        assert result == 0

    def test_counts_people_with_role(self):
        """Test correctly counts people with specific role."""
        people = [
            Person(id="p1", name="Person 1", roles=["usher"]),
            Person(id="p2", name="Person 2", roles=["usher", "greeter"]),
            Person(id="p3", name="Person 3", roles=["admin"]),
        ]

        result = count_people_with_role(people, "usher")

        assert result == 2

    def test_counts_zero_for_role_not_found(self):
        """Test returns 0 when no people have the role."""
        people = [
            Person(id="p1", name="Person 1", roles=["admin"]),
            Person(id="p2", name="Person 2", roles=["greeter"]),
        ]

        result = count_people_with_role(people, "usher")

        assert result == 0

    def test_handles_people_without_roles(self):
        """Test handles people with None or empty roles."""
        people = [
            Person(id="p1", name="Person 1", roles=None),
            Person(id="p2", name="Person 2", roles=[]),
            Person(id="p3", name="Person 3", roles=["usher"]),
        ]

        result = count_people_with_role(people, "usher")

        assert result == 1


class TestValidateTimeRange:
    """Test validate_time_range helper function."""

    def test_valid_time_range_returns_true(self):
        """Test valid time range (end after start) returns True."""
        start = datetime(2025, 1, 1, 10, 0)
        end = datetime(2025, 1, 1, 12, 0)

        is_valid, error = validate_time_range(start, end)

        assert is_valid is True
        assert error is None

    def test_end_before_start_returns_false(self):
        """Test end time before start time returns False with error."""
        start = datetime(2025, 1, 1, 12, 0)
        end = datetime(2025, 1, 1, 10, 0)

        is_valid, error = validate_time_range(start, end)

        assert is_valid is False
        assert "End time must be after start time" in error

    def test_end_equals_start_returns_false(self):
        """Test end time equal to start time returns False."""
        start = datetime(2025, 1, 1, 10, 0)
        end = datetime(2025, 1, 1, 10, 0)

        is_valid, error = validate_time_range(start, end)

        assert is_valid is False
        assert error is not None


# Database-dependent functions (is_person_blocked_on_date, get_assigned_person_ids,
# get_blocked_assigned_people) are tested via integration tests in test_events.py
