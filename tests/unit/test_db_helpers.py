"""Tests for api/utils/db_helpers.py"""

import pytest
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.utils.db_helpers import (
    get_person_with_org_check,
    check_email_exists,
    get_team_members,
    get_person_assignments,
    is_person_blocked_on_date,
    get_event_assignments,
    get_organization_events,
    get_available_people_for_event,
)
from roster_cli.db.models import (
    Person,
    Organization,
    Team,
    Event,
    Assignment,
    VacationPeriod,
    Availability,
    TeamMember,
)


def _unique_id(prefix="test"):
    """Generate unique ID with timestamp."""
    return f"{prefix}_{int(time.time() * 1000000)}"


@pytest.fixture
def db_session():
    """Create a test database session."""
    from api.database import get_db, init_db
    import tempfile
    import os

    # Create temporary database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"

    # Initialize database
    init_db()

    # Get session
    db = next(get_db())

    yield db

    # Cleanup
    db.close()
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def test_org(db_session: Session):
    """Create a test organization with unique ID."""
    org_id = _unique_id("test_org")
    org = Organization(id=org_id, name="Test Organization")
    db_session.add(org)
    db_session.commit()
    return org


class TestGetPersonWithOrgCheck:
    """Test get_person_with_org_check function."""

    def test_person_in_org_returns_person(self, db_session: Session, test_org: Organization):
        """Test that person in correct org is returned."""
        pid = _unique_id("p")
        person = Person(
            id=pid,
            org_id=test_org.id,
            name="John",
            email=f"{pid}@test.com",
            roles=["volunteer"]
        )
        db_session.add(person)
        db_session.commit()

        result = get_person_with_org_check(db_session, pid, test_org.id)
        assert result is not None
        assert result.id == pid

    def test_person_in_different_org_returns_none(self, db_session: Session):
        """Test that person in different org returns None."""
        org1_id = _unique_id("org1")
        org2_id = _unique_id("org2")
        pid = _unique_id("p")

        org1 = Organization(id=org1_id, name="Org 1")
        org2 = Organization(id=org2_id, name="Org 2")
        person = Person(
            id=pid,
            org_id=org1_id,
            name="John",
            email=f"{pid}@test.com",
            roles=[]
        )
        db_session.add_all([org1, org2, person])
        db_session.commit()

        result = get_person_with_org_check(db_session, pid, org2_id)
        assert result is None

    def test_nonexistent_person_returns_none(self, db_session: Session, test_org: Organization):
        """Test that nonexistent person returns None."""
        result = get_person_with_org_check(db_session, "nonexistent", test_org.id)
        assert result is None


class TestCheckEmailExists:
    """Test check_email_exists function."""

    def test_existing_email_returns_true(self, db_session: Session, test_org: Organization):
        """Test that existing email returns True."""
        pid = _unique_id("p")
        email = f"{pid}@test.com"
        person = Person(
            id=pid,
            org_id=test_org.id,
            name="John",
            email=email,
            roles=[]
        )
        db_session.add(person)
        db_session.commit()

        assert check_email_exists(db_session, email, test_org.id) is True

    def test_nonexistent_email_returns_false(self, db_session: Session, test_org: Organization):
        """Test that nonexistent email returns False."""
        assert check_email_exists(db_session, "nonexistent@test.com", test_org.id) is False

    def test_email_in_different_org_returns_false(self, db_session: Session):
        """Test that email in different org returns False."""
        org1_id = _unique_id("org1")
        org2_id = _unique_id("org2")
        pid = _unique_id("p")
        email = f"{pid}@test.com"

        org1 = Organization(id=org1_id, name="Org 1")
        org2 = Organization(id=org2_id, name="Org 2")
        person = Person(
            id=pid,
            org_id=org1_id,
            name="John",
            email=email,
            roles=[]
        )
        db_session.add_all([org1, org2, person])
        db_session.commit()

        assert check_email_exists(db_session, email, org2_id) is False


class TestGetTeamMembers:
    """Test get_team_members function."""

    def test_team_with_members_returns_list(self, db_session: Session, test_org: Organization):
        """Test that team with members returns list of people."""
        tid = _unique_id("team")
        p1_id = _unique_id("p1")
        p2_id = _unique_id("p2")

        team = Team(id=tid, org_id=test_org.id, name="Team 1")
        person1 = Person(id=p1_id, org_id=test_org.id, name="Alice", email=f"{p1_id}@test.com", roles=[])
        person2 = Person(id=p2_id, org_id=test_org.id, name="Bob", email=f"{p2_id}@test.com", roles=[])

        db_session.add_all([team, person1, person2])
        db_session.commit()

        # Add team members through the association table
        tm1 = TeamMember(team_id=tid, person_id=p1_id)
        tm2 = TeamMember(team_id=tid, person_id=p2_id)
        db_session.add_all([tm1, tm2])
        db_session.commit()

        members = get_team_members(db_session, tid)
        assert len(members) == 2
        member_ids = [m.id for m in members]
        assert p1_id in member_ids
        assert p2_id in member_ids

    def test_team_without_members_returns_empty_list(self, db_session: Session, test_org: Organization):
        """Test that team without members returns empty list."""
        tid = _unique_id("team")
        team = Team(id=tid, org_id=test_org.id, name="Team 1")
        db_session.add(team)
        db_session.commit()

        members = get_team_members(db_session, tid)
        assert members == []

    def test_nonexistent_team_returns_empty_list(self, db_session: Session):
        """Test that nonexistent team returns empty list."""
        members = get_team_members(db_session, "nonexistent")
        assert members == []


class TestGetPersonAssignments:
    """Test get_person_assignments function."""

    def test_get_all_assignments(self, db_session: Session, test_org: Organization):
        """Test getting all assignments for a person."""
        pid = _unique_id("p")
        e1_id = _unique_id("e1")
        e2_id = _unique_id("e2")

        person = Person(id=pid, org_id=test_org.id, name="John", email=f"{pid}@test.com", roles=[])
        event1 = Event(
            id=e1_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0)
        )
        event2 = Event(
            id=e2_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 8, 10, 0),
            end_time=datetime(2025, 1, 8, 11, 0)
        )
        assignment1 = Assignment(person_id=pid, event_id=e1_id)
        assignment2 = Assignment(person_id=pid, event_id=e2_id)

        db_session.add_all([person, event1, event2, assignment1, assignment2])
        db_session.commit()

        assignments = get_person_assignments(db_session, pid)
        assert len(assignments) == 2

    def test_filter_by_date_range(self, db_session: Session, test_org: Organization):
        """Test filtering assignments by date range."""
        pid = _unique_id("p")
        e1_id = _unique_id("e1")
        e2_id = _unique_id("e2")

        person = Person(id=pid, org_id=test_org.id, name="John", email=f"{pid}@test.com", roles=[])
        event1 = Event(
            id=e1_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0)
        )
        event2 = Event(
            id=e2_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 2, 1, 10, 0),
            end_time=datetime(2025, 2, 1, 11, 0)
        )
        assignment1 = Assignment(person_id=pid, event_id=e1_id)
        assignment2 = Assignment(person_id=pid, event_id=e2_id)

        db_session.add_all([person, event1, event2, assignment1, assignment2])
        db_session.commit()

        # Filter to only get January assignments
        assignments = get_person_assignments(
            db_session,
            pid,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31)
        )
        assert len(assignments) == 1
        assert assignments[0].event_id == e1_id


class TestIsPersonBlockedOnDate:
    """Test is_person_blocked_on_date function."""

    @pytest.mark.skip("VacationPeriod model uses availability_id not person_id")
    def test_person_on_vacation_returns_blocked(self, db_session: Session, test_org: Organization):
        """Test that person on vacation is blocked."""
        pass

    @pytest.mark.skip("Availability model uses rrule not start_date/end_date")
    def test_person_with_availability_unavailable(self, db_session: Session, test_org: Organization):
        """Test that person with unavailable availability is blocked."""
        pass

    def test_person_not_blocked_returns_false(self, db_session: Session, test_org: Organization):
        """Test that person not blocked returns False."""
        pid = _unique_id("p")
        person = Person(id=pid, org_id=test_org.id, name="John", email=f"{pid}@test.com", roles=[])
        db_session.add(person)
        db_session.commit()

        is_blocked, reason = is_person_blocked_on_date(db_session, pid, datetime(2025, 1, 3))
        assert is_blocked is False
        assert reason is None


class TestGetEventAssignments:
    """Test get_event_assignments function."""

    def test_get_assignments_for_event(self, db_session: Session, test_org: Organization):
        """Test getting all assignments for an event."""
        eid = _unique_id("e")
        p1_id = _unique_id("p1")
        p2_id = _unique_id("p2")

        event = Event(
            id=eid,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0)
        )
        person1 = Person(id=p1_id, org_id=test_org.id, name="Alice", email=f"{p1_id}@test.com", roles=[])
        person2 = Person(id=p2_id, org_id=test_org.id, name="Bob", email=f"{p2_id}@test.com", roles=[])

        assignment1 = Assignment(person_id=p1_id, event_id=eid)
        assignment2 = Assignment(person_id=p2_id, event_id=eid)

        db_session.add_all([event, person1, person2, assignment1, assignment2])
        db_session.commit()

        assignments = get_event_assignments(db_session, eid)
        assert len(assignments) == 2


class TestGetOrganizationEvents:
    """Test get_organization_events function."""

    def test_get_all_events(self, db_session: Session, test_org: Organization):
        """Test getting all events for an organization."""
        e1_id = _unique_id("e1")
        e2_id = _unique_id("e2")

        event1 = Event(
            id=e1_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0)
        )
        event2 = Event(
            id=e2_id,
            org_id=test_org.id,
            type="meeting",
            start_time=datetime(2025, 1, 8, 10, 0),
            end_time=datetime(2025, 1, 8, 11, 0)
        )

        db_session.add_all([event1, event2])
        db_session.commit()

        events = get_organization_events(db_session, test_org.id)
        assert len(events) >= 2

    def test_filter_by_event_type(self, db_session: Session, test_org: Organization):
        """Test filtering events by type."""
        e1_id = _unique_id("e1")
        e2_id = _unique_id("e2")

        event1 = Event(
            id=e1_id,
            org_id=test_org.id,
            type="service",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0)
        )
        event2 = Event(
            id=e2_id,
            org_id=test_org.id,
            type="meeting",
            start_time=datetime(2025, 1, 8, 10, 0),
            end_time=datetime(2025, 1, 8, 11, 0)
        )

        db_session.add_all([event1, event2])
        db_session.commit()

        events = get_organization_events(db_session, test_org.id, event_type="service")
        # Should get at least our service event
        service_events = [e for e in events if e.type == "service" and e.id == e1_id]
        assert len(service_events) >= 1
