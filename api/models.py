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
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql import func

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

    # Cancellation and data retention fields
    cancelled_at = Column(DateTime, nullable=True)  # When subscription was cancelled
    data_retention_until = Column(DateTime, nullable=True)  # When data should be deleted (period_end + 30 days)
    deletion_scheduled_at = Column(DateTime, nullable=True)  # When organization was marked for deletion

    # Relationships
    people = relationship("Person", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="organization", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="organization", cascade="all, delete-orphan")
    recurring_series = relationship("RecurringSeries", back_populates="organization", cascade="all, delete-orphan")
    holidays = relationship("Holiday", back_populates="organization", cascade="all, delete-orphan")
    constraints = relationship("Constraint", back_populates="organization", cascade="all, delete-orphan")
    solutions = relationship("Solution", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")
    onboarding_progress = relationship("OnboardingProgress", back_populates="organization", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="organization", cascade="all, delete-orphan")
    email_preferences = relationship("EmailPreference", back_populates="organization", cascade="all, delete-orphan")

    # Billing relationships
    subscription = relationship("Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    usage_metrics = relationship("UsageMetrics", cascade="all, delete-orphan")
    subscription_events = relationship("SubscriptionEvent", cascade="all, delete-orphan")

    # Convenience properties for billing
    @property
    def subscription_tier(self):
        """Get current subscription tier."""
        return self.subscription.plan_tier if self.subscription else "free"

    @property
    def volunteer_limit(self):
        """Get volunteer limit based on subscription tier."""
        tier_limits = {
            "free": 10,
            "starter": 50,
            "pro": 200,
            "enterprise": None  # Unlimited
        }
        return tier_limits.get(self.subscription_tier, 10)

    @property
    def is_over_limit(self):
        """Check if organization is over volunteer limit."""
        if self.volunteer_limit is None:  # Unlimited
            return False
        current_volunteers = len([p for p in self.people if "volunteer" in (p.roles or [])])
        return current_volunteers > self.volunteer_limit


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
    language = Column(String, default="en", nullable=False)  # User's language preference (ISO 639-1 code)
    status = Column(String, default="active", nullable=False)  # active, inactive, invited
    invited_by = Column(String, ForeignKey("people.id"), nullable=True)  # Who invited this person
    last_login = Column(DateTime, nullable=True)  # Last login timestamp
    calendar_token = Column(String, unique=True, nullable=True)  # Unique token for calendar subscription
    is_sample = Column(Boolean, default=False, nullable=False)  # For sample/demo data
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
    onboarding_progress = relationship("OnboardingProgress", back_populates="person", uselist=False, cascade="all, delete-orphan")
    notifications_received = relationship("Notification", back_populates="recipient", foreign_keys="Notification.recipient_id", cascade="all, delete-orphan")
    email_preferences = relationship("EmailPreference", back_populates="person", uselist=False, cascade="all, delete-orphan")

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
    is_sample = Column(Boolean, default=False, nullable=False)  # For sample/demo data
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
    is_sample = Column(Boolean, default=False, nullable=False)  # For sample/demo data
    extra_data = Column(JSONType, nullable=True)

    # Recurring events support (added for spec 006-recurring-events-ui)
    series_id = Column(String, ForeignKey("recurring_series.id"), nullable=True)  # Link to recurring series
    occurrence_sequence = Column(Integer, nullable=True)  # Position in series (1, 2, 3...)
    is_exception = Column(Boolean, default=False, nullable=False)  # Single occurrence modified

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="events")
    resource = relationship("Resource", back_populates="events")
    event_teams = relationship("EventTeam", back_populates="event", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="event", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="event", cascade="all, delete-orphan")
    recurring_series = relationship("RecurringSeries", back_populates="occurrences")
    recurrence_exception = relationship("RecurrenceException", back_populates="occurrence", uselist=False, cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_events_org_id", "org_id"),
        Index("idx_events_start_time", "start_time"),
        Index("idx_events_series_id", "series_id"),
    )


class RecurringSeries(Base):
    """Recurring event series template and recurrence pattern definition."""

    __tablename__ = "recurring_series"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String, ForeignKey("people.id"), nullable=False)

    # Event template (inherited by occurrences)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    location = Column(String, nullable=True)
    role_requirements = Column(JSONType, nullable=True)  # {"usher": 2, "greeter": 1}

    # Recurrence pattern
    pattern_type = Column(String, nullable=False)  # 'weekly', 'biweekly', 'monthly', 'custom'
    frequency_interval = Column(Integer, nullable=True)  # For custom patterns (e.g., every 3 weeks)
    selected_days = Column(JSONType, nullable=True)  # For weekly: ["sunday", "wednesday"]
    weekday_position = Column(String, nullable=True)  # For monthly: "first", "second", "last"
    weekday_name = Column(String, nullable=True)  # For monthly: "sunday", "monday", "friday"

    # Series duration
    start_date = Column(Date, nullable=False)
    end_condition_type = Column(String, nullable=False)  # 'date', 'count', 'indefinite'
    end_date = Column(Date, nullable=True)
    occurrence_count = Column(Integer, nullable=True)

    # Status
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="recurring_series")
    creator = relationship("Person", foreign_keys=[created_by])
    occurrences = relationship("Event", back_populates="recurring_series", cascade="all, delete-orphan")
    exceptions = relationship("RecurrenceException", back_populates="series", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_recurring_series_org_id", "org_id"),
        Index("idx_recurring_series_created_by", "created_by"),
        Index("idx_recurring_series_start_date", "start_date"),
        Index("idx_recurring_series_active", "active"),
    )


class RecurrenceException(Base):
    """Single occurrence modification in a recurring series."""

    __tablename__ = "recurrence_exceptions"

    id = Column(String, primary_key=True)
    occurrence_id = Column(String, ForeignKey("events.id"), nullable=False, unique=True)
    series_id = Column(String, ForeignKey("recurring_series.id"), nullable=False)

    # Exception type
    exception_type = Column(String, nullable=False)  # 'time_change', 'cancellation', 'full_edit'

    # Original values (before modification)
    original_title = Column(String, nullable=True)
    original_start_time = Column(DateTime, nullable=True)
    original_end_time = Column(DateTime, nullable=True)
    original_location = Column(String, nullable=True)

    # Custom values (after modification)
    custom_title = Column(String, nullable=True)
    custom_start_time = Column(DateTime, nullable=True)
    custom_end_time = Column(DateTime, nullable=True)
    custom_location = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    occurrence = relationship("Event", back_populates="recurrence_exception")
    series = relationship("RecurringSeries", back_populates="exceptions")

    # Indexes
    __table_args__ = (
        Index("idx_recurrence_exceptions_occurrence_id", "occurrence_id"),
        Index("idx_recurrence_exceptions_series_id", "series_id"),
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


class OnboardingProgress(Base):
    """Onboarding progress tracking for users."""

    __tablename__ = "onboarding_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String, ForeignKey("people.id"), nullable=False, unique=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    wizard_step_completed = Column(Integer, default=0)  # 0-4 (0=not started, 4=completed)
    wizard_data = Column(JSONType, default=dict)  # {"org": {...}, "event": {...}, "team": {...}, "invitations": [...]}
    checklist_state = Column(JSONType, default=dict)  # {"complete_profile": True, "create_event": False, ...}
    tutorials_completed = Column(JSONType, default=list)  # ["event_creation", "team_management", ...]
    features_unlocked = Column(JSONType, default=list)  # ["recurring_events", "manual_editing", "sms"]
    videos_watched = Column(JSONType, default=list)  # ["getting_started", "creating_events", ...]
    onboarding_skipped = Column(Boolean, default=False)
    checklist_dismissed = Column(Boolean, default=False)
    tutorials_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="onboarding_progress")
    organization = relationship("Organization", back_populates="onboarding_progress")

    # Indexes
    __table_args__ = (
        Index("idx_onboarding_progress_person_id", "person_id"),
        Index("idx_onboarding_progress_org_id", "org_id"),
    )


class Assignment(Base):
    """Assignment of person to event with specific role."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(Integer, ForeignKey("solutions.id"), nullable=True)  # Nullable for manual assignments
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)
    role = Column(String, nullable=True)  # Event-specific role (e.g., "usher", "greeter", "sound_tech")
    status = Column(String, default="confirmed", nullable=False)  # confirmed, declined, swap_requested
    decline_reason = Column(String, nullable=True)
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


# ==============================================================================
# Email Notification Models
# ==============================================================================

class NotificationType:
    """Email notification types."""
    ASSIGNMENT = "assignment"  # Volunteer assigned to event
    REMINDER = "reminder"  # 24-hour reminder before event
    UPDATE = "update"  # Event details changed
    CANCELLATION = "cancellation"  # Event canceled
    DIGEST_DAILY = "digest_daily"  # Daily digest of notifications
    DIGEST_WEEKLY = "digest_weekly"  # Weekly digest of notifications
    ADMIN_SUMMARY = "admin_summary"  # Weekly admin statistics


class NotificationStatus:
    """Email notification delivery statuses."""
    PENDING = "pending"  # Queued for sending
    SENDING = "sending"  # Currently being sent
    SENT = "sent"  # Sent successfully
    DELIVERED = "delivered"  # Delivered to recipient's mailbox
    OPENED = "opened"  # Recipient opened email
    CLICKED = "clicked"  # Recipient clicked link in email
    BOUNCED = "bounced"  # Email bounced (invalid address)
    FAILED = "failed"  # Sending failed (will retry)
    RETRY = "retry"  # Retrying after failure


class EmailFrequency:
    """Email notification frequency preferences."""
    IMMEDIATE = "immediate"  # Send immediately
    DAILY = "daily"  # Batch into daily digest
    WEEKLY = "weekly"  # Batch into weekly digest
    DISABLED = "disabled"  # No emails


class DeliveryEventType:
    """SendGrid webhook event types."""
    PROCESSED = "processed"
    DROPPED = "dropped"
    DELIVERED = "delivered"
    DEFERRED = "deferred"
    BOUNCE = "bounce"
    OPEN = "open"
    CLICK = "click"
    SPAM_REPORT = "spamreport"
    UNSUBSCRIBE = "unsubscribe"


class Notification(Base):
    """Email notification tracking."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("people.id"), nullable=False)
    type = Column(String, nullable=False)  # NotificationType value
    status = Column(String, default=NotificationStatus.PENDING, nullable=False)
    event_id = Column(String, ForeignKey("events.id"), nullable=True)  # Related event (if applicable)
    template_data = Column(JSONType, nullable=True)  # Template rendering data
    retry_count = Column(Integer, default=0, nullable=False)
    sendgrid_message_id = Column(String, nullable=True, unique=True)  # SendGrid message ID
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="notifications")
    recipient = relationship("Person", back_populates="notifications_received", foreign_keys=[recipient_id])
    event = relationship("Event", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("idx_notifications_org_id", "org_id"),
        Index("idx_notifications_recipient_id", "recipient_id"),
        Index("idx_notifications_event_id", "event_id"),
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_created_at", "created_at"),
    )


class EmailPreference(Base):
    """User email notification preferences."""

    __tablename__ = "email_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String, ForeignKey("people.id"), nullable=False, unique=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    frequency = Column(String, default=EmailFrequency.IMMEDIATE, nullable=False)
    enabled_types = Column(JSONType, default=list, nullable=False)  # List of enabled NotificationType values
    language = Column(String, default="en", nullable=False)  # Email language preference
    timezone = Column(String, default="UTC", nullable=False)  # For digest scheduling
    digest_hour = Column(Integer, default=8, nullable=False)  # Hour to send digests (0-23)
    unsubscribe_token = Column(String, unique=True, nullable=False)  # Unique unsubscribe token
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="email_preferences", uselist=False)
    organization = relationship("Organization", back_populates="email_preferences")

    # Indexes
    __table_args__ = (
        Index("idx_email_preferences_person_id", "person_id"),
        Index("idx_email_preferences_org_id", "org_id"),
    )


class DeliveryLog(Base):
    """SendGrid webhook delivery event log."""

    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    event_type = Column(String, nullable=False)  # DeliveryEventType value
    sendgrid_message_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    reason = Column(Text, nullable=True)  # Bounce reason, error message, etc.
    raw_event = Column(JSONType, nullable=True)  # Full SendGrid webhook payload
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notification = relationship("Notification", backref="delivery_logs")

    # Indexes
    __table_args__ = (
        Index("idx_delivery_logs_notification_id", "notification_id"),
        Index("idx_delivery_logs_sendgrid_message_id", "sendgrid_message_id"),
        Index("idx_delivery_logs_timestamp", "timestamp"),
    )


class AuditLog(Base):
    """
    Audit log for security-sensitive operations.

    Stores immutable records of who did what, when, and from where.
    """

    __tablename__ = "audit_logs"

    # Primary key
    id = Column(String, primary_key=True)

    # Who
    user_id = Column(String, nullable=True, index=True)  # Nullable for system events
    user_email = Column(String, nullable=True)  # Denormalized for easy lookup
    organization_id = Column(String, nullable=True, index=True)

    # What
    action = Column(String, nullable=False, index=True)  # e.g., "user.created", "role.changed", "data.exported"
    resource_type = Column(String, nullable=True)  # e.g., "person", "event", "organization"
    resource_id = Column(String, nullable=True)  # ID of affected resource

    # Details
    details = Column(JSON, nullable=True)  # Additional context (before/after values, etc.)

    # When
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Where
    ip_address = Column(String, nullable=True)  # Client IP address
    user_agent = Column(String, nullable=True)  # Browser/client info

    # Outcome
    status = Column(String, nullable=False, default="success")  # "success", "failure", "denied"
    error_message = Column(String, nullable=True)  # If status = "failure"

    # Indexes for common queries
    __table_args__ = (
        Index("idx_audit_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_org_timestamp", "organization_id", "timestamp"),
        Index("idx_audit_action_timestamp", "action", "timestamp"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email} at {self.timestamp}>"


# Audit action constants
class AuditAction:
    """Standard audit action names."""

    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    PASSWORD_RESET_REQUESTED = "auth.password_reset.requested"
    PASSWORD_RESET_COMPLETED = "auth.password_reset.completed"

    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_INVITED = "user.invited"
    USER_INVITATION_ACCEPTED = "user.invitation.accepted"

    # Permissions
    ROLE_ASSIGNED = "permission.role.assigned"
    ROLE_REMOVED = "permission.role.removed"
    PERMISSION_DENIED = "permission.denied"

    # Data access
    DATA_EXPORTED = "data.exported"
    CALENDAR_EXPORTED = "data.calendar.exported"
    REPORT_GENERATED = "data.report.generated"

    # Organization
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_SETTINGS_CHANGED = "org.settings.changed"

    # Sensitive operations
    BULK_DELETE = "data.bulk_delete"
    DATABASE_BACKUP = "system.database.backup"
    CONFIG_CHANGED = "system.config.changed"


class SmsPreference(Base):
    """SMS notification preferences for volunteers."""

    __tablename__ = "sms_preferences"

    person_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    notification_types = Column(JSONType, nullable=False, default=list)  # ['assignment', 'reminder', 'change', 'cancellation']
    opt_in_date = Column(DateTime, nullable=True)
    opt_out_date = Column(DateTime, nullable=True)
    language = Column(String(5), nullable=False, default="en")
    timezone = Column(String(50), nullable=False, default="UTC")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_preferences_verified", "verified", "opt_out_date"),
    )


class SmsMessage(Base):
    """Log of all sent SMS messages for audit trail and delivery tracking."""

    __tablename__ = "sms_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'assignment', 'reminder', 'broadcast', 'system', 'verification'
    event_id = Column(String, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    template_id = Column(Integer, ForeignKey("sms_templates.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="queued")  # 'queued', 'sent', 'delivered', 'failed', 'undelivered'
    twilio_message_sid = Column(String(34), unique=True, nullable=True)
    cost_cents = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    is_urgent = Column(Boolean, nullable=False, default=False)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_messages_org_created", "organization_id", "created_at"),
        Index("idx_sms_messages_recipient_created", "recipient_id", "created_at"),
        Index("idx_sms_messages_status_created", "status", "created_at"),
        Index("idx_sms_messages_twilio_sid", "twilio_message_sid"),
        Index("idx_sms_messages_type_created", "message_type", "created_at"),
    )


class SmsTemplate(Base):
    """Reusable message templates with variable substitution."""

    __tablename__ = "sms_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    template_text = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'assignment', 'reminder', 'cancellation', 'broadcast'
    character_count = Column(Integer, nullable=False)
    translations = Column(JSONType, nullable=False, default=dict)  # {'en': '...', 'es': '...'}
    is_system = Column(Boolean, nullable=False, default=False)
    usage_count = Column(Integer, nullable=False, default=0)
    created_by = Column(String, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_templates_org_type", "organization_id", "message_type"),
        Index("idx_sms_templates_system", "is_system"),
    )


class SmsUsage(Base):
    """Monthly SMS usage tracking and budget management per organization."""

    __tablename__ = "sms_usage"

    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    month_year = Column(String(7), nullable=False, primary_key=True)  # '2025-10'
    assignment_count = Column(Integer, nullable=False, default=0)
    reminder_count = Column(Integer, nullable=False, default=0)
    broadcast_count = Column(Integer, nullable=False, default=0)
    system_count = Column(Integer, nullable=False, default=0)
    total_cost_cents = Column(Integer, nullable=False, default=0)
    budget_limit_cents = Column(Integer, nullable=False, default=10000)  # $100 default
    alert_threshold_percent = Column(Integer, nullable=False, default=80)
    alert_sent_at_80 = Column(Boolean, nullable=False, default=False)
    alert_sent_at_100 = Column(Boolean, nullable=False, default=False)
    auto_pause_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_usage_month", "month_year"),
    )


class SmsVerificationCode(Base):
    """Temporary storage for phone verification codes (10-minute expiration)."""

    __tablename__ = "sms_verification_codes"

    person_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20), nullable=False)
    verification_code = Column(Integer, nullable=False)  # 6-digit: 100000-999999
    attempts = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_verification_expires", "expires_at"),
    )


class SmsReply(Base):
    """Log of incoming SMS replies for audit trail and analytics."""

    __tablename__ = "sms_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_text = Column(Text, nullable=False)
    reply_type = Column(String(20), nullable=False)  # 'yes', 'no', 'stop', 'start', 'help', 'unknown'
    original_message_id = Column(Integer, ForeignKey("sms_messages.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(String, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    action_taken = Column(String(50), nullable=False)  # 'confirmed', 'declined', 'opted_out', 'help_sent', etc.
    twilio_message_sid = Column(String(34), unique=True, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_sms_replies_person_created", "person_id", "created_at"),
        Index("idx_sms_replies_type_created", "reply_type", "created_at"),
        Index("idx_sms_replies_twilio_sid", "twilio_message_sid"),
    )


# ==============================================================================
# Billing & Subscription Models
# ==============================================================================


class Subscription(Base):
    """Organization's current subscription tier and billing status."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)  # Stripe customer ID
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)  # Stripe subscription ID
    plan_tier = Column(String(20), nullable=False, default="free")  # free, starter, pro, enterprise
    billing_cycle = Column(String(10), nullable=True)  # monthly, annual (null for free)
    status = Column(String(20), nullable=False, default="active")  # active, trialing, past_due, cancelled, incomplete
    trial_end_date = Column(DateTime, nullable=True)  # Trial expiration date
    current_period_start = Column(DateTime, nullable=True)  # Current billing period start
    current_period_end = Column(DateTime, nullable=True)  # Current billing period end
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)  # Scheduled cancellation
    pending_downgrade = Column(JSONType, nullable=True)  # Scheduled downgrade: {"new_plan": "starter", "effective_date": "2025-11-01"}
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    billing_history = relationship("BillingHistory", back_populates="subscription", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_subscriptions_org_id", "org_id"),
        Index("idx_subscriptions_status", "status"),
        Index("idx_subscriptions_stripe_customer", "stripe_customer_id"),
        Index("idx_subscriptions_org_status", "org_id", "status"),  # Composite for common query pattern
    )


class BillingHistory(Base):
    """Historical record of all billing events."""

    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(50), nullable=False)  # charge, refund, subscription_change, trial_start, trial_end
    amount_cents = Column(Integer, nullable=False, default=0)  # Amount in cents (USD)
    currency = Column(String(3), nullable=False, default="usd")
    payment_status = Column(String(20), nullable=False)  # succeeded, failed, pending
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)
    invoice_pdf_url = Column(String(500), nullable=True)  # URL to invoice PDF
    description = Column(Text, nullable=True)
    extra_metadata = Column(JSONType, nullable=True)  # Additional event metadata
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="billing_history")

    # Indexes
    __table_args__ = (
        Index("idx_billing_history_org_timestamp", "org_id", "event_timestamp"),
        Index("idx_billing_history_stripe_invoice", "stripe_invoice_id"),
    )


class PaymentMethod(Base):
    """Organization's stored payment information (managed by Stripe)."""

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, amex, discover
    card_last4 = Column(String(4), nullable=True)  # Last 4 digits
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    billing_address = Column(JSONType, nullable=True)  # {street, city, state, zip, country}
    is_primary = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_payment_methods_org_id", "org_id"),
        Index("idx_payment_methods_stripe_pm", "stripe_payment_method_id"),
    )


class UsageMetrics(Base):
    """Tracks organization resource consumption for limit enforcement."""

    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # volunteers_count, events_count, storage_mb, api_calls
    current_value = Column(Integer, nullable=False, default=0)
    plan_limit = Column(Integer, nullable=True)  # null = unlimited
    percentage_used = Column(Float, nullable=False, default=0.0)  # Calculated field
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_usage_metrics_org_metric", "org_id", "metric_type"),
    )


class SubscriptionEvent(Base):
    """Audit log of all subscription changes for compliance and analytics."""

    __tablename__ = "subscription_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # created, upgraded, downgraded, trial_started, cancelled, reactivated
    previous_plan = Column(String(20), nullable=True)  # Previous plan tier
    new_plan = Column(String(20), nullable=False)  # New plan tier
    admin_id = Column(String, ForeignKey("people.id", ondelete="SET NULL"), nullable=True)  # Admin who initiated change
    reason = Column(Text, nullable=True)  # Reason for change (optional)
    notes = Column(Text, nullable=True)  # Additional notes
    extra_metadata = Column(JSONType, nullable=True)  # Additional metadata
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_subscription_events_org_timestamp", "org_id", "event_timestamp"),
        Index("idx_subscription_events_type", "event_type"),
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
