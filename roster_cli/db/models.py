"""Database models for roster system using SQLAlchemy."""

from datetime import datetime, date
from typing import Optional
import json

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import TypeDecorator

Base = declarative_base()


class JSONType(TypeDecorator):
    """JSON column type that serializes/deserializes automatically."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class Organization(Base):
    """Organization/league/church entity."""

    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=True)
    config = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    people = relationship("Person", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="organization", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="organization", cascade="all, delete-orphan")
    holidays = relationship("Holiday", back_populates="organization", cascade="all, delete-orphan")
    constraints = relationship("Constraint", back_populates="organization", cascade="all, delete-orphan")
    solutions = relationship("Solution", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")


class Person(Base):
    """Person/player/volunteer entity."""

    __tablename__ = "people"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # Hashed password for login
    roles = Column(JSONType, nullable=True)  # Array of role strings
    timezone = Column(String, default="UTC", nullable=False)  # User's timezone preference
    status = Column(String, default="active", nullable=False)  # active, inactive, invited
    invited_by = Column(String, ForeignKey("people.id"), nullable=True)  # Who invited this person
    last_login = Column(DateTime, nullable=True)  # Last login timestamp
    calendar_token = Column(String, unique=True, nullable=True)  # Unique token for calendar subscription
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="people")
    team_memberships = relationship("TeamMember", back_populates="person", cascade="all, delete-orphan")
    availability = relationship("Availability", back_populates="person", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="person", cascade="all, delete-orphan")
    invitations_sent = relationship("Invitation", foreign_keys="Invitation.invited_by", back_populates="inviter", cascade="all, delete-orphan")
    invited_by_person = relationship("Person", remote_side="Person.id", foreign_keys=[invited_by])

    # Indexes
    __table_args__ = (
        Index("idx_people_org_id", "org_id"),
        Index("idx_people_email", "email"),
        Index("idx_people_status", "status"),
        Index("idx_people_calendar_token", "calendar_token"),
    )


class Team(Base):
    """Team entity."""

    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    event_teams = relationship("EventTeam", back_populates="team", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_teams_org_id", "org_id"),
    )


class TeamMember(Base):
    """Team membership junction table."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    person = relationship("Person", back_populates="team_memberships")

    # Indexes
    __table_args__ = (
        Index("idx_team_members_team_id", "team_id"),
        Index("idx_team_members_person_id", "person_id"),
    )


class Resource(Base):
    """Resource/venue/room entity."""

    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=True)
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="resources")
    events = relationship("Event", back_populates="resource")

    # Indexes
    __table_args__ = (
        Index("idx_resources_org_id", "org_id"),
    )


class Event(Base):
    """Event/match/shift entity."""

    __tablename__ = "events"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    type = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=True)
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="events")
    resource = relationship("Resource", back_populates="events")
    event_teams = relationship("EventTeam", back_populates="event", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="event", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_events_org_id", "org_id"),
        Index("idx_events_start_time", "start_time"),
    )


class EventTeam(Base):
    """Event-team junction table."""

    __tablename__ = "event_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="event_teams")
    team = relationship("Team", back_populates="event_teams")

    # Indexes
    __table_args__ = (
        Index("idx_event_teams_event_id", "event_id"),
        Index("idx_event_teams_team_id", "team_id"),
    )


class Availability(Base):
    """Availability rules for a person."""

    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)
    rrule = Column(String, nullable=True)
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="availability")
    vacations = relationship("VacationPeriod", back_populates="availability", cascade="all, delete-orphan")
    exceptions = relationship("AvailabilityException", back_populates="availability", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_availability_person_id", "person_id"),
    )


class VacationPeriod(Base):
    """Vacation period for availability."""

    __tablename__ = "vacation_periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    availability_id = Column(Integer, ForeignKey("availability.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)

    # Relationships
    availability = relationship("Availability", back_populates="vacations")

    # Indexes
    __table_args__ = (
        Index("idx_vacation_periods_availability_id", "availability_id"),
        Index("idx_vacation_periods_dates", "start_date", "end_date"),
    )


class AvailabilityException(Base):
    """Single date exception for availability."""

    __tablename__ = "availability_exceptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    availability_id = Column(Integer, ForeignKey("availability.id"), nullable=False)
    exception_date = Column(Date, nullable=False)

    # Relationships
    availability = relationship("Availability", back_populates="exceptions")

    # Indexes
    __table_args__ = (
        Index("idx_availability_exceptions_availability_id", "availability_id"),
        Index("idx_availability_exceptions_date", "exception_date"),
    )


class Holiday(Base):
    """Holiday entity."""

    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    date = Column(Date, nullable=False)
    label = Column(String, nullable=False)
    is_long_weekend = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="holidays")

    # Indexes
    __table_args__ = (
        Index("idx_holidays_org_id", "org_id"),
        Index("idx_holidays_date", "date"),
    )


class Constraint(Base):
    """Constraint/rule entity."""

    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    key = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'hard' or 'soft'
    weight = Column(Integer, nullable=True)
    predicate = Column(String, nullable=False)
    params = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="constraints")

    # Indexes
    __table_args__ = (
        Index("idx_constraints_org_id", "org_id"),
        Index("idx_constraints_key", "key"),
    )


class Solution(Base):
    """Generated solution entity."""

    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    solve_ms = Column(Float, nullable=True)
    hard_violations = Column(Integer, nullable=False)
    soft_score = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    metrics = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="solutions")
    assignments = relationship("Assignment", back_populates="solution", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_solutions_org_id", "org_id"),
        Index("idx_solutions_created_at", "created_at"),
    )


class Invitation(Base):
    """Invitation for new users to join an organization."""

    __tablename__ = "invitations"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    roles = Column(JSONType, nullable=False)  # Array of role strings
    invited_by = Column(String, ForeignKey("people.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, accepted, expired, cancelled
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    inviter = relationship("Person", foreign_keys=[invited_by], back_populates="invitations_sent")

    # Indexes
    __table_args__ = (
        Index("idx_invitations_org_id", "org_id"),
        Index("idx_invitations_email", "email"),
        Index("idx_invitations_token", "token"),
        Index("idx_invitations_status", "status"),
    )


class Assignment(Base):
    """Assignment of person to event."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(Integer, ForeignKey("solutions.id"), nullable=True)  # Nullable for manual assignments
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    solution = relationship("Solution", back_populates="assignments")
    event = relationship("Event", back_populates="assignments")
    person = relationship("Person", back_populates="assignments")

    # Indexes
    __table_args__ = (
        Index("idx_assignments_solution_id", "solution_id"),
        Index("idx_assignments_event_id", "event_id"),
        Index("idx_assignments_person_id", "person_id"),
    )


def create_database(db_url: str = "sqlite:///roster.db"):
    """Create database and all tables."""
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get database session."""
    Session = sessionmaker(bind=engine)
    return Session()
