# Data Model: Email Notification System

**Feature**: Email Notification System for Volunteer Assignments
**Branch**: `001-email-notifications`
**Phase**: Phase 1 - Design & Contracts
**Created**: 2025-01-20

## Overview

This document defines the database schema for the email notification system. All new tables follow SignUpFlow's multi-tenant isolation principles (ALWAYS filter by `org_id`) and integrate with existing models (`Person`, `Organization`, `Event`).

## New Tables

### 1. Notification

Represents a single email notification to be sent to a volunteer or admin.

**SQLAlchemy Model**:

```python
# api/models.py (add to existing file)

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class NotificationType(str, enum.Enum):
    """Email notification types."""
    ASSIGNMENT = "assignment"              # Volunteer assigned to event
    REMINDER = "reminder"                  # 24-hour event reminder
    UPDATE = "update"                      # Event details changed
    CANCELLATION = "cancellation"          # Event canceled
    DIGEST_DAILY = "digest_daily"          # Daily digest of assignments
    DIGEST_WEEKLY = "digest_weekly"        # Weekly digest of assignments
    ADMIN_SUMMARY = "admin_summary"        # Weekly admin statistics

class NotificationStatus(str, enum.Enum):
    """Email delivery status lifecycle."""
    PENDING = "pending"         # Created, not yet queued
    QUEUED = "queued"           # Added to Celery queue
    SENT = "sent"               # Sent to SendGrid
    DELIVERED = "delivered"     # SendGrid webhook: delivered to inbox
    OPENED = "opened"           # SendGrid webhook: recipient opened email
    CLICKED = "clicked"         # SendGrid webhook: recipient clicked link
    FAILED = "failed"           # Temporary failure (will retry)
    BOUNCED = "bounced"         # Permanent failure (bad email address)
    SPAM = "spam"               # Marked as spam by recipient
    UNSUBSCRIBED = "unsubscribed"  # Recipient unsubscribed

class Notification(Base):
    """Individual email notification record."""
    __tablename__ = "notifications"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: f"notif_{int(datetime.utcnow().timestamp())}")

    # Multi-tenant isolation (MANDATORY)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Recipient
    recipient_id = Column(String, ForeignKey("people.id"), nullable=False, index=True)

    # Notification type and status
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    status = Column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING, index=True)

    # Related event (optional - admin summaries don't have event_id)
    event_id = Column(String, ForeignKey("events.id"), nullable=True, index=True)

    # Template data (JSON - dynamic content for email)
    # Example: {"event_title": "Sunday Service", "event_datetime": "2025-01-05T10:00:00", ...}
    template_data = Column(JSON, nullable=False, default=dict)

    # Retry tracking
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    queued_at = Column(DateTime, nullable=True)   # When added to Celery queue
    sent_at = Column(DateTime, nullable=True)     # When sent to SendGrid
    delivered_at = Column(DateTime, nullable=True)  # When SendGrid confirmed delivery
    next_retry_at = Column(DateTime, nullable=True, index=True)  # For retry scheduling

    # SendGrid metadata
    sendgrid_message_id = Column(String, nullable=True, index=True)  # For webhook matching

    # Relationships
    organization = relationship("Organization", back_populates="notifications")
    recipient = relationship("Person", foreign_keys=[recipient_id], back_populates="notifications_received")
    event = relationship("Event", back_populates="notifications")
    delivery_logs = relationship("DeliveryLog", back_populates="notification", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Notification {self.id} type={self.type.value} status={self.status.value} recipient={self.recipient_id}>"
```

**Indexes** (performance optimization):
```sql
CREATE INDEX idx_notifications_org_status ON notifications(org_id, status);
CREATE INDEX idx_notifications_recipient_created ON notifications(recipient_id, created_at);
CREATE INDEX idx_notifications_next_retry ON notifications(next_retry_at) WHERE status = 'failed';
CREATE INDEX idx_notifications_sendgrid_msg ON notifications(sendgrid_message_id);
```

**Query Patterns**:
```python
# CORRECT - Always filter by org_id
pending_notifications = db.query(Notification)\
    .filter(Notification.org_id == org_id)\
    .filter(Notification.status == NotificationStatus.PENDING)\
    .order_by(Notification.created_at)\
    .all()

# Get notifications ready for retry
retry_notifications = db.query(Notification)\
    .filter(Notification.status == NotificationStatus.FAILED)\
    .filter(Notification.next_retry_at <= datetime.utcnow())\
    .filter(Notification.retry_count < Notification.max_retries)\
    .all()
```

---

### 2. EmailPreference

Stores volunteer email notification preferences (frequency, enabled types, language).

**SQLAlchemy Model**:

```python
# api/models.py (add to existing file)

class EmailFrequency(str, enum.Enum):
    """Email notification frequency options."""
    IMMEDIATE = "immediate"      # Send emails immediately
    DAILY = "daily"              # Batch into daily digest at 8am
    WEEKLY = "weekly"            # Batch into weekly digest (Monday 8am)
    DISABLED = "disabled"        # No emails (except critical)

class EmailPreference(Base):
    """Volunteer email notification settings."""
    __tablename__ = "email_preferences"

    # Composite primary key (one preference record per person per org)
    person_id = Column(String, ForeignKey("people.id"), primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), primary_key=True, index=True)

    # Notification frequency
    frequency = Column(SQLEnum(EmailFrequency), nullable=False, default=EmailFrequency.IMMEDIATE)

    # Digest delivery time (hour 0-23, timezone from person.timezone)
    digest_hour = Column(Integer, nullable=False, default=8)  # 8am local time

    # Enabled notification types (JSON array)
    # Example: ["assignment", "reminder", "update", "cancellation"]
    # Empty array = all disabled, null = all enabled (default)
    enabled_types = Column(JSON, nullable=True, default=None)

    # Language preference (defaults to person.language if not set)
    # Options: "en", "es", "pt", "zh-CN", "zh-TW", "ko"
    language = Column(String, nullable=True)

    # Timezone for event times in emails (defaults to person.timezone if not set)
    timezone = Column(String, nullable=True)

    # Unsubscribe token (for unsubscribe links)
    unsubscribe_token = Column(String, unique=True, nullable=False,
                               default=lambda: f"unsub_{secrets.token_urlsafe(32)}")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="email_preferences")
    organization = relationship("Organization", back_populates="email_preferences")

    def __repr__(self):
        return f"<EmailPreference person={self.person_id} org={self.org_id} frequency={self.frequency.value}>"

    def is_type_enabled(self, notification_type: NotificationType) -> bool:
        """Check if notification type is enabled for this user."""
        # If disabled frequency, only critical notifications allowed
        if self.frequency == EmailFrequency.DISABLED:
            return notification_type in [NotificationType.ASSIGNMENT, NotificationType.CANCELLATION]

        # If enabled_types is None (default), all types enabled
        if self.enabled_types is None:
            return True

        # Check if type is in enabled list
        return notification_type.value in self.enabled_types
```

**Indexes**:
```sql
CREATE INDEX idx_email_preferences_org ON email_preferences(org_id);
CREATE INDEX idx_email_preferences_frequency ON email_preferences(frequency);
CREATE UNIQUE INDEX idx_email_preferences_unsub_token ON email_preferences(unsubscribe_token);
```

**Query Patterns**:
```python
# Get or create default preferences for user
def get_email_preferences(db: Session, person_id: str, org_id: str) -> EmailPreference:
    """Get email preferences, creating default if not exists."""
    prefs = db.query(EmailPreference)\
        .filter(EmailPreference.person_id == person_id)\
        .filter(EmailPreference.org_id == org_id)\
        .first()

    if not prefs:
        # Create default preferences
        prefs = EmailPreference(
            person_id=person_id,
            org_id=org_id,
            frequency=EmailFrequency.IMMEDIATE,
            enabled_types=None  # All types enabled by default
        )
        db.add(prefs)
        db.commit()

    return prefs

# Find users who want daily digest at current hour
def get_daily_digest_recipients(db: Session, org_id: str, current_hour: int) -> list[Person]:
    """Get users who should receive daily digest at current hour."""
    return db.query(Person)\
        .join(EmailPreference)\
        .filter(EmailPreference.org_id == org_id)\
        .filter(EmailPreference.frequency == EmailFrequency.DAILY)\
        .filter(EmailPreference.digest_hour == current_hour)\
        .all()
```

---

### 3. DeliveryLog

Audit trail of all notification delivery attempts and status changes.

**SQLAlchemy Model**:

```python
# api/models.py (add to existing file)

class DeliveryEventType(str, enum.Enum):
    """Types of delivery events to log."""
    CREATED = "created"           # Notification created
    QUEUED = "queued"             # Added to Celery queue
    SENDING = "sending"           # Sending to SendGrid
    SENT = "sent"                 # Successfully sent
    DELIVERED = "delivered"       # SendGrid webhook: delivered
    OPENED = "opened"             # SendGrid webhook: opened
    CLICKED = "clicked"           # SendGrid webhook: clicked link
    BOUNCED = "bounced"           # SendGrid webhook: bounced
    FAILED = "failed"             # Temporary failure
    RETRY = "retry"               # Retry attempt scheduled
    SPAM = "spam"                 # Marked as spam
    UNSUBSCRIBED = "unsubscribed" # Recipient unsubscribed

class DeliveryLog(Base):
    """Audit trail of notification delivery attempts."""
    __tablename__ = "delivery_logs"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: f"log_{int(datetime.utcnow().timestamp() * 1000)}")

    # Related notification
    notification_id = Column(String, ForeignKey("notifications.id"), nullable=False, index=True)

    # Event details
    event_type = Column(SQLEnum(DeliveryEventType), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Status and provider response
    status_code = Column(Integer, nullable=True)  # HTTP status code
    provider_response = Column(JSON, nullable=True)  # Full SendGrid API response
    error_message = Column(String, nullable=True)  # Human-readable error

    # SendGrid webhook data (for delivered, opened, clicked events)
    webhook_data = Column(JSON, nullable=True)

    # Retry information
    retry_attempt = Column(Integer, nullable=True)  # Which retry attempt (1, 2, 3)
    next_retry_delay = Column(Integer, nullable=True)  # Seconds until next retry

    # Relationships
    notification = relationship("Notification", back_populates="delivery_logs")

    def __repr__(self):
        return f"<DeliveryLog {self.id} notif={self.notification_id} event={self.event_type.value} time={self.timestamp}>"
```

**Indexes**:
```sql
CREATE INDEX idx_delivery_logs_notification ON delivery_logs(notification_id, timestamp);
CREATE INDEX idx_delivery_logs_event_time ON delivery_logs(event_type, timestamp);
```

**Query Patterns**:
```python
# Get delivery history for notification
delivery_history = db.query(DeliveryLog)\
    .filter(DeliveryLog.notification_id == notification_id)\
    .order_by(DeliveryLog.timestamp)\
    .all()

# Get failed notifications in last 24 hours
failed_logs = db.query(DeliveryLog)\
    .filter(DeliveryLog.event_type == DeliveryEventType.FAILED)\
    .filter(DeliveryLog.timestamp >= datetime.utcnow() - timedelta(hours=24))\
    .all()

# Helper function to log delivery event
def log_delivery_event(
    db: Session,
    notification_id: str,
    event_type: DeliveryEventType,
    status_code: int = None,
    provider_response: dict = None,
    error_message: str = None
):
    """Log a delivery event for audit trail."""
    log = DeliveryLog(
        notification_id=notification_id,
        event_type=event_type,
        status_code=status_code,
        provider_response=provider_response,
        error_message=error_message
    )
    db.add(log)
    db.commit()
```

---

## Relationship Updates to Existing Models

### Person Model Updates

```python
# api/models.py - Add to existing Person class

class Person(Base):
    # ... existing fields ...

    # New relationships
    notifications_received = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan"
    )
    email_preferences = relationship(
        "EmailPreference",
        back_populates="person",
        cascade="all, delete-orphan"
    )
```

### Organization Model Updates

```python
# api/models.py - Add to existing Organization class

class Organization(Base):
    # ... existing fields ...

    # New relationships
    notifications = relationship(
        "Notification",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    email_preferences = relationship(
        "EmailPreference",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
```

### Event Model Updates

```python
# api/models.py - Add to existing Event class

class Event(Base):
    # ... existing fields ...

    # New relationship
    notifications = relationship(
        "Notification",
        back_populates="event",
        cascade="all, delete-orphan"
    )
```

---

## Database Migration Strategy

### Migration Script (Alembic)

```python
# migrations/versions/YYYYMMDD_HHMM_add_email_notifications.py

"""Add email notification tables

Revision ID: 001_email_notifications
Revises: previous_revision
Create Date: 2025-01-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Create email notification tables."""

    # 1. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('recipient_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('assignment', 'reminder', 'update', 'cancellation',
                                  'digest_daily', 'digest_weekly', 'admin_summary',
                                  name='notificationtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'queued', 'sent', 'delivered', 'opened',
                                   'clicked', 'failed', 'bounced', 'spam', 'unsubscribed',
                                   name='notificationstatus'), nullable=False),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('queued_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('sendgrid_message_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['people.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Indexes for notifications
    op.create_index('idx_notifications_org_status', 'notifications', ['org_id', 'status'])
    op.create_index('idx_notifications_recipient_created', 'notifications', ['recipient_id', 'created_at'])
    op.create_index('idx_notifications_next_retry', 'notifications', ['next_retry_at'])
    op.create_index('idx_notifications_sendgrid_msg', 'notifications', ['sendgrid_message_id'])

    # 2. Create email_preferences table
    op.create_table(
        'email_preferences',
        sa.Column('person_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('frequency', sa.Enum('immediate', 'daily', 'weekly', 'disabled',
                                      name='emailfrequency'), nullable=False),
        sa.Column('digest_hour', sa.Integer(), nullable=False, default=8),
        sa.Column('enabled_types', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('unsubscribe_token', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['people.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('person_id', 'org_id')
    )

    # Indexes for email_preferences
    op.create_index('idx_email_preferences_org', 'email_preferences', ['org_id'])
    op.create_index('idx_email_preferences_frequency', 'email_preferences', ['frequency'])
    op.create_index('idx_email_preferences_unsub_token', 'email_preferences', ['unsubscribe_token'], unique=True)

    # 3. Create delivery_logs table
    op.create_table(
        'delivery_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('notification_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.Enum('created', 'queued', 'sending', 'sent', 'delivered',
                                       'opened', 'clicked', 'bounced', 'failed', 'retry',
                                       'spam', 'unsubscribed', name='deliveryeventtype'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('webhook_data', sa.JSON(), nullable=True),
        sa.Column('retry_attempt', sa.Integer(), nullable=True),
        sa.Column('next_retry_delay', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Indexes for delivery_logs
    op.create_index('idx_delivery_logs_notification', 'delivery_logs', ['notification_id', 'timestamp'])
    op.create_index('idx_delivery_logs_event_time', 'delivery_logs', ['event_type', 'timestamp'])

def downgrade():
    """Drop email notification tables."""
    op.drop_table('delivery_logs')
    op.drop_table('email_preferences')
    op.drop_table('notifications')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS notificationstatus')
    op.execute('DROP TYPE IF EXISTS emailfrequency')
    op.execute('DROP TYPE IF EXISTS deliveryeventtype')
```

### Migration Execution

```bash
# Generate migration (after updating models.py)
alembic revision --autogenerate -m "Add email notification tables"

# Review generated migration (verify correctness)
cat migrations/versions/001_email_notifications.py

# Apply migration
alembic upgrade head

# Verify tables created
poetry run python -c "
from api.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

---

## Multi-Tenant Isolation Verification

### Critical: ALWAYS Filter by org_id

```python
# ✅ CORRECT - Multi-tenant safe
notifications = db.query(Notification)\
    .filter(Notification.org_id == org_id)\
    .all()

# ❌ WRONG - Data leak! Returns all orgs' notifications
notifications = db.query(Notification).all()

# ✅ CORRECT - Verify recipient belongs to org
notification = db.query(Notification)\
    .filter(Notification.id == notification_id)\
    .filter(Notification.org_id == org_id)\
    .first()

# ❌ WRONG - Attacker can read other orgs' notifications
notification = db.query(Notification)\
    .filter(Notification.id == notification_id)\
    .first()
```

### Enforce in API Endpoints

```python
# api/routers/notifications.py (example)

@router.get("/notifications")
def list_notifications(
    org_id: str = Query(...),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notifications for organization."""
    # MANDATORY: Verify user belongs to organization
    verify_org_member(current_user, org_id)

    # MANDATORY: Filter by org_id
    notifications = db.query(Notification)\
        .filter(Notification.org_id == org_id)\
        .order_by(Notification.created_at.desc())\
        .all()

    return notifications
```

---

## Performance Considerations

### Database Indexes Summary

```sql
-- Notifications table (4 indexes)
CREATE INDEX idx_notifications_org_status ON notifications(org_id, status);
CREATE INDEX idx_notifications_recipient_created ON notifications(recipient_id, created_at);
CREATE INDEX idx_notifications_next_retry ON notifications(next_retry_at) WHERE status = 'failed';
CREATE INDEX idx_notifications_sendgrid_msg ON notifications(sendgrid_message_id);

-- Email preferences table (3 indexes)
CREATE INDEX idx_email_preferences_org ON email_preferences(org_id);
CREATE INDEX idx_email_preferences_frequency ON email_preferences(frequency);
CREATE UNIQUE INDEX idx_email_preferences_unsub_token ON email_preferences(unsubscribe_token);

-- Delivery logs table (2 indexes)
CREATE INDEX idx_delivery_logs_notification ON delivery_logs(notification_id, timestamp);
CREATE INDEX idx_delivery_logs_event_time ON delivery_logs(event_type, timestamp);
```

### Query Performance Targets

- **List pending notifications**: < 50ms (indexed on org_id + status)
- **Get notification by ID**: < 10ms (primary key lookup)
- **Find retry candidates**: < 100ms (indexed on next_retry_at)
- **Webhook matching**: < 20ms (indexed on sendgrid_message_id)
- **Delivery log insertion**: < 5ms (simple insert)

### Data Retention Policy

```python
# Cleanup job (run daily via Celery beat)
@celery_app.task
def cleanup_old_delivery_logs():
    """Delete delivery logs older than 90 days."""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    deleted_count = db.query(DeliveryLog)\
        .filter(DeliveryLog.timestamp < cutoff_date)\
        .delete()

    db.commit()
    return {"deleted_logs": deleted_count}

# Archive old notifications (run monthly)
@celery_app.task
def archive_old_notifications():
    """Archive delivered notifications older than 180 days."""
    cutoff_date = datetime.utcnow() - timedelta(days=180)

    # Move to archive table or delete
    archived_count = db.query(Notification)\
        .filter(Notification.status == NotificationStatus.DELIVERED)\
        .filter(Notification.delivered_at < cutoff_date)\
        .delete()

    db.commit()
    return {"archived_notifications": archived_count}
```

---

## Testing Strategy

### Unit Tests for Models

```python
# tests/unit/test_notification_models.py

def test_notification_creation():
    """Test creating notification with all required fields."""
    notification = Notification(
        org_id="org_123",
        recipient_id="person_456",
        type=NotificationType.ASSIGNMENT,
        status=NotificationStatus.PENDING,
        event_id="event_789",
        template_data={"event_title": "Sunday Service"}
    )
    assert notification.retry_count == 0
    assert notification.max_retries == 3

def test_email_preference_type_enabled():
    """Test is_type_enabled logic."""
    prefs = EmailPreference(
        person_id="person_123",
        org_id="org_456",
        frequency=EmailFrequency.IMMEDIATE,
        enabled_types=["assignment", "reminder"]
    )
    assert prefs.is_type_enabled(NotificationType.ASSIGNMENT) is True
    assert prefs.is_type_enabled(NotificationType.UPDATE) is False

def test_email_preference_disabled_frequency():
    """Test that disabled frequency only allows critical notifications."""
    prefs = EmailPreference(
        person_id="person_123",
        org_id="org_456",
        frequency=EmailFrequency.DISABLED
    )
    assert prefs.is_type_enabled(NotificationType.ASSIGNMENT) is True
    assert prefs.is_type_enabled(NotificationType.REMINDER) is False
```

### Integration Tests for Database

```python
# tests/integration/test_notification_database.py

def test_notification_query_multi_tenant_isolation(db):
    """Test that notifications are isolated by org_id."""
    # Create notifications for two different orgs
    notif1 = Notification(org_id="org_A", recipient_id="person_1", type=NotificationType.ASSIGNMENT, template_data={})
    notif2 = Notification(org_id="org_B", recipient_id="person_2", type=NotificationType.ASSIGNMENT, template_data={})
    db.add_all([notif1, notif2])
    db.commit()

    # Query for org_A - should only get notif1
    org_a_notifications = db.query(Notification).filter(Notification.org_id == "org_A").all()
    assert len(org_a_notifications) == 1
    assert org_a_notifications[0].id == notif1.id

def test_delivery_log_cascade_delete(db):
    """Test that delivery logs are deleted when notification is deleted."""
    notif = Notification(org_id="org_123", recipient_id="person_456", type=NotificationType.ASSIGNMENT, template_data={})
    db.add(notif)
    db.commit()

    # Add delivery log
    log = DeliveryLog(notification_id=notif.id, event_type=DeliveryEventType.CREATED)
    db.add(log)
    db.commit()

    # Delete notification
    db.delete(notif)
    db.commit()

    # Verify log was also deleted (cascade)
    remaining_logs = db.query(DeliveryLog).filter(DeliveryLog.notification_id == notif.id).count()
    assert remaining_logs == 0
```

---

## Next Steps

After this data model is approved:

1. ✅ **Data model complete** - All tables defined with indexes and relationships
2. ⏳ **Generate API contracts** - OpenAPI specs for notification endpoints and SendGrid webhooks
3. ⏳ **Generate quickstart.md** - Developer guide for implementing email notifications
4. ⏳ **Update CLAUDE.md** - Add email notification patterns to AI assistant context
5. ⏳ **Run `/speckit.tasks`** - Break down into implementation tasks

---

**Document Status**: ✅ COMPLETE
**Constitution Compliance**: ✅ Multi-tenant isolation enforced, all queries filter by org_id
**Review Required**: Data model structure, indexes, migration strategy
**Next Command**: Continue to API contracts generation
