# Email Notifications Developer Quickstart

**Feature**: Email Notification System for Volunteer Assignments
**Branch**: `001-email-notifications`
**Target Audience**: Developers implementing the email notification system

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Migration](#database-migration)
4. [SendGrid Setup](#sendgrid-setup)
5. [Celery Setup](#celery-setup)
6. [Implementation Phases](#implementation-phases)
7. [Testing Strategy](#testing-strategy)
8. [Common Pitfalls](#common-pitfalls)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting implementation, ensure you have:

- ✅ SignUpFlow development environment running (`make run`)
- ✅ Poetry installed with all Python dependencies
- ✅ Redis installed and running (for Celery)
- ✅ SendGrid account (free tier sufficient for development)
- ✅ Mailtrap account (for email testing without spamming real inboxes)
- ✅ Pytest and Playwright installed for testing
- ✅ Familiarity with SignUpFlow codebase (read `CLAUDE.md`)

### System Requirements

```bash
# Verify Python version (3.11+ required)
python --version  # Should be 3.11 or higher

# Verify Poetry installed
poetry --version

# Verify Redis installed
redis-cli ping  # Should return "PONG"

# Install Redis if not present (macOS)
brew install redis
brew services start redis

# Install Redis if not present (Ubuntu)
sudo apt-get install redis-server
sudo systemctl start redis
```

---

## Environment Setup

### 1. Install New Dependencies

```bash
# Add to pyproject.toml
poetry add celery==5.3.4
poetry add redis==5.0.1
poetry add sendgrid==6.11.0
poetry add jinja2==3.1.2

# Install
poetry install
```

### 2. Configure Environment Variables

Create or update `.env` file in project root:

```bash
# .env (add these new variables)

# SendGrid Configuration
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@signupflow.io
SENDGRID_FROM_NAME=SignUpFlow

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Testing (Mailtrap for development)
MAILTRAP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_PORT=2525
MAILTRAP_USER=xxxxxxxxxxxxxxxx
MAILTRAP_PASSWORD=xxxxxxxxxxxxxxxx
USE_MAILTRAP=true  # Set to false in production

# Application URLs
FRONTEND_BASE_URL=http://localhost:8000
```

### 3. Add Configuration to Settings

```python
# api/core/config.py (add to existing config)

from pydantic import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # SendGrid
    SENDGRID_API_KEY: str
    SENDGRID_WEBHOOK_SECRET: str
    SENDGRID_FROM_EMAIL: str = "noreply@signupflow.io"
    SENDGRID_FROM_NAME: str = "SignUpFlow"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Email Testing
    MAILTRAP_HOST: str = "sandbox.smtp.mailtrap.io"
    MAILTRAP_PORT: int = 2525
    MAILTRAP_USER: str = ""
    MAILTRAP_PASSWORD: str = ""
    USE_MAILTRAP: bool = True

    # Frontend URL
    FRONTEND_BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Database Migration

### 1. Create Migration Script

```bash
# Generate migration with Alembic
alembic revision --autogenerate -m "Add email notification tables"

# This creates: migrations/versions/YYYYMMDD_HHMM_add_email_notifications.py
```

### 2. Review Generated Migration

Open the generated migration file and verify it includes:
- `notifications` table
- `email_preferences` table
- `delivery_logs` table
- All required indexes
- Enum types (NotificationType, NotificationStatus, etc.)

**Reference**: See `specs/001-email-notifications/data-model.md` for complete schema.

### 3. Run Migration

```bash
# Apply migration
alembic upgrade head

# Verify tables created
poetry run python -c "
from api.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Created tables:', [t for t in tables if t in ['notifications', 'email_preferences', 'delivery_logs']])
"

# Expected output:
# Created tables: ['notifications', 'email_preferences', 'delivery_logs']
```

---

## SendGrid Setup

### 1. Create SendGrid Account

1. Go to https://signup.sendgrid.com/
2. Sign up (free tier: 100 emails/day)
3. Verify your email address

### 2. Generate API Key

1. Navigate to **Settings** → **API Keys**
2. Click **Create API Key**
3. Name: "SignUpFlow Development"
4. Permissions: **Full Access** (for development)
5. Copy API key → Save to `.env` as `SENDGRID_API_KEY`

### 3. Verify Sender Identity

**Option A: Single Sender Verification (Development)**

1. Navigate to **Settings** → **Sender Authentication**
2. Click **Single Sender Verification**
3. Add your email (e.g., `yourname@gmail.com`)
4. Verify email via link sent to your inbox
5. Use this email as `SENDGRID_FROM_EMAIL` in `.env`

**Option B: Domain Authentication (Production)**

1. Navigate to **Settings** → **Sender Authentication**
2. Click **Domain Authentication**
3. Follow instructions to add DNS records for your domain
4. Verify domain ownership
5. Use `noreply@yourdomain.com` as `SENDGRID_FROM_EMAIL`

### 4. Configure Event Webhook (for delivery tracking)

1. Navigate to **Settings** → **Mail Settings** → **Event Webhook**
2. HTTP POST URL: `https://your-ngrok-url.ngrok.io/api/webhooks/sendgrid` (for local dev)
3. Select all events: Delivered, Opened, Clicked, Bounced, etc.
4. Enable **Signature Verification**
5. Copy **Verification Key** → Save to `.env` as `SENDGRID_WEBHOOK_SECRET`
6. Status: **Enabled**

**Note**: Use ngrok for local webhook testing (see Testing section).

---

## Celery Setup

### 1. Create Celery App

```python
# api/celery_app.py (NEW FILE)

from celery import Celery
from celery.schedules import crontab
from api.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "signupflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # 9 minutes soft limit
)

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    # Send reminder emails every hour (check for events 24h away)
    'send-reminder-emails': {
        'task': 'api.tasks.notifications.send_reminder_emails',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
    # Process daily digests at 8am UTC
    'send-daily-digests': {
        'task': 'api.tasks.notifications.send_daily_digests',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM UTC daily
    },
    # Process weekly digests on Monday 8am UTC
    'send-weekly-digests': {
        'task': 'api.tasks.notifications.send_weekly_digests',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
    },
    # Clean up old delivery logs (run daily at 2am)
    'cleanup-old-logs': {
        'task': 'api.tasks.cleanup.cleanup_old_delivery_logs',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
}

# Auto-discover tasks in tasks module
celery_app.autodiscover_tasks(['api.tasks'])
```

### 2. Create Task Modules

```python
# api/tasks/__init__.py (NEW FILE)
# Empty file for package

# api/tasks/notifications.py (NEW FILE - stub for now)
from api.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, notification_id: str):
    """Send email notification via SendGrid."""
    # Implementation in Phase 2
    pass

@celery_app.task
def send_reminder_emails():
    """Send reminder emails for events 24 hours away."""
    # Implementation in Phase 2
    pass

@celery_app.task
def send_daily_digests():
    """Send daily digest emails."""
    # Implementation in Phase 2
    pass

@celery_app.task
def send_weekly_digests():
    """Send weekly digest emails."""
    # Implementation in Phase 2
    pass
```

### 3. Start Celery Workers

```bash
# Terminal 1: Start FastAPI server
make run

# Terminal 2: Start Celery worker
celery -A api.celery_app worker --loglevel=info

# Terminal 3: Start Celery Beat (scheduler)
celery -A api.celery_app beat --loglevel=info
```

### 4. Verify Celery Working

```python
# Test task execution
from api.tasks.notifications import send_email_task

# Queue a test task
result = send_email_task.delay("test_notification_123")

# Check result
print(result.id)  # Task ID
print(result.status)  # 'PENDING', 'SUCCESS', 'FAILURE'
```

---

## Implementation Phases

### Phase 1: Core Models & Database ✅

**Files to Create/Modify**:
- ✅ `api/models.py` - Add Notification, EmailPreference, DeliveryLog models
- ✅ Run Alembic migration

**Validation**:
```python
# Test model creation
from api.models import Notification, NotificationType, NotificationStatus
from api.database import SessionLocal

db = SessionLocal()
notif = Notification(
    org_id="org_test",
    recipient_id="person_test",
    type=NotificationType.ASSIGNMENT,
    status=NotificationStatus.PENDING,
    template_data={"event_title": "Test Event"}
)
db.add(notif)
db.commit()
print(f"Created notification: {notif.id}")
db.close()
```

### Phase 2: Email Service (SendGrid Integration)

**Files to Create**:
```python
# api/services/email_service.py (NEW FILE)

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader
from api.core.config import settings

class EmailService:
    """Service for sending emails via SendGrid."""

    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.template_env = Environment(
            loader=FileSystemLoader("api/templates/email")
        )

    def send_assignment_email(
        self,
        to_email: str,
        volunteer_name: str,
        event_data: dict,
        language: str = "en"
    ) -> str:
        """Send assignment notification email."""
        # Render template
        template = self.template_env.get_template(f"assignment_{language}.html")
        html_content = template.render(
            volunteer_name=volunteer_name,
            **event_data
        )

        # Create email
        message = Mail(
            from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
            to_emails=to_email,
            subject=f"New Assignment: {event_data['title']}",
            html_content=html_content
        )

        # Add tracking category
        message.add_category("assignment")

        # Send via SendGrid
        response = self.client.send(message)

        # Return SendGrid message ID
        return response.headers.get("X-Message-Id")
```

**Email Templates** (create directory):
```bash
mkdir -p api/templates/email
```

**Example Template**:
```html
<!-- api/templates/email/assignment_en.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>New Assignment</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1>New Assignment: {{ event_title }}</h1>
    <p>Hi {{ volunteer_name }},</p>
    <p>You have been assigned to:</p>
    <ul>
        <li><strong>Event:</strong> {{ event_title }}</li>
        <li><strong>Date:</strong> {{ event_date }}</li>
        <li><strong>Time:</strong> {{ event_time }}</li>
        <li><strong>Location:</strong> {{ event_location }}</li>
        <li><strong>Your Role:</strong> {{ role }}</li>
    </ul>
    <p>
        <a href="{{ schedule_link }}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            View My Schedule
        </a>
    </p>
    <p style="color: #888; font-size: 12px;">
        <a href="{{ unsubscribe_link }}">Unsubscribe</a> from assignment notifications
    </p>
</body>
</html>
```

**Validation**:
```python
# Test email sending
from api.services.email_service import EmailService

service = EmailService()
message_id = service.send_assignment_email(
    to_email="test@example.com",
    volunteer_name="John Doe",
    event_data={
        "event_title": "Sunday Service",
        "event_date": "January 5, 2025",
        "event_time": "10:00 AM",
        "event_location": "Main Sanctuary",
        "role": "Usher",
        "schedule_link": "http://localhost:8000/app/schedule",
        "unsubscribe_link": "http://localhost:8000/api/email-preferences/unsubscribe/token123"
    },
    language="en"
)
print(f"Email sent! Message ID: {message_id}")
```

### Phase 3: Notification API Endpoints

**Files to Create**:
```python
# api/routers/notifications.py (NEW FILE)

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.core.security import get_current_user, verify_admin_access, verify_org_member
from api.models import Person, Notification, NotificationStatus
from api.schemas.notifications import NotificationResponse, NotificationCreate

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
def list_notifications(
    org_id: str = Query(...),
    recipient_id: str = Query(None),
    status: NotificationStatus = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notifications (volunteers see only their own, admins see all)."""
    verify_org_member(current_user, org_id)

    query = db.query(Notification).filter(Notification.org_id == org_id)

    # Volunteers can only see their own notifications
    if "admin" not in current_user.roles:
        query = query.filter(Notification.recipient_id == current_user.id)
    elif recipient_id:
        query = query.filter(Notification.recipient_id == recipient_id)

    if status:
        query = query.filter(Notification.status == status)

    total = query.count()
    notifications = query.order_by(Notification.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    return {
        "notifications": notifications,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.post("", status_code=201)
def create_notification(
    request: NotificationCreate,
    org_id: str = Query(...),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Create notification manually (admin only, for testing)."""
    verify_org_member(admin, org_id)

    # Create notification
    notification = Notification(
        org_id=org_id,
        recipient_id=request.recipient_id,
        type=request.type,
        event_id=request.event_id,
        template_data=request.template_data
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Queue for sending
    from api.tasks.notifications import send_email_task
    send_email_task.delay(notification.id)

    return notification
```

**Register Router**:
```python
# api/main.py (MODIFY)

from api.routers import notifications

app.include_router(notifications.router, prefix="/api")
```

**Validation**:
```bash
# Test creating notification via API
curl -X POST "http://localhost:8000/api/notifications?org_id=org_test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": "person_123",
    "type": "assignment",
    "event_id": "event_456",
    "template_data": {
      "event_title": "Sunday Service",
      "event_date": "2025-01-05",
      "role": "Usher"
    }
  }'
```

### Phase 4: Celery Tasks (Email Sending)

**Files to Modify**:
```python
# api/tasks/notifications.py (IMPLEMENT)

from api.celery_app import celery_app
from api.database import SessionLocal
from api.models import Notification, NotificationStatus, DeliveryLog, DeliveryEventType
from api.services.email_service import EmailService
from datetime import datetime

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, notification_id: str):
    """Send email notification via SendGrid with retry."""
    db = SessionLocal()
    try:
        # Get notification
        notification = db.query(Notification)\
            .filter(Notification.id == notification_id)\
            .first()

        if not notification:
            return {"error": "Notification not found"}

        # Update status to queued
        notification.status = NotificationStatus.QUEUED
        notification.queued_at = datetime.utcnow()
        db.commit()

        # Log delivery event
        log_delivery_event(db, notification_id, DeliveryEventType.QUEUED)

        # Get recipient email
        recipient = notification.recipient

        # Send email via SendGrid
        email_service = EmailService()
        sendgrid_message_id = email_service.send_assignment_email(
            to_email=recipient.email,
            volunteer_name=recipient.name,
            event_data=notification.template_data,
            language=recipient.language or "en"
        )

        # Update notification
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        notification.sendgrid_message_id = sendgrid_message_id
        db.commit()

        # Log delivery event
        log_delivery_event(
            db,
            notification_id,
            DeliveryEventType.SENT,
            status_code=202,
            provider_response={"sendgrid_message_id": sendgrid_message_id}
        )

        return {"status": "sent", "message_id": sendgrid_message_id}

    except Exception as exc:
        # Log failure
        log_delivery_event(
            db,
            notification_id,
            DeliveryEventType.FAILED,
            error_message=str(exc)
        )

        # Retry with exponential backoff
        retry_delays = [3600, 14400, 86400]  # 1h, 4h, 24h
        retry_count = self.request.retries

        if retry_count < len(retry_delays):
            # Update notification
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            notification.next_retry_at = datetime.utcnow() + timedelta(seconds=retry_delays[retry_count])
            db.commit()

            raise self.retry(exc=exc, countdown=retry_delays[retry_count])
        else:
            # Max retries exceeded
            notification.status = NotificationStatus.FAILED
            notification.retry_count = notification.max_retries
            db.commit()
            return {"error": "Max retries exceeded", "exception": str(exc)}

    finally:
        db.close()

def log_delivery_event(
    db: Session,
    notification_id: str,
    event_type: DeliveryEventType,
    status_code: int = None,
    provider_response: dict = None,
    error_message: str = None
):
    """Helper to log delivery event."""
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

**Validation**:
```python
# Test task execution
from api.tasks.notifications import send_email_task

# Create test notification in database first
# ...

# Queue task
result = send_email_task.delay("notif_1234567890")
print(f"Task ID: {result.id}")

# Check result after a few seconds
print(result.status)  # 'SUCCESS'
print(result.result)  # {'status': 'sent', 'message_id': '...'}
```

### Phase 5: Event-Triggered Notifications

**Trigger notifications when**:
- Volunteer assigned to event
- Event details changed
- Event canceled
- 24 hours before event (reminder)

**Implementation** (example for assignment):
```python
# api/routers/events.py (MODIFY existing file)

from api.tasks.notifications import send_email_task

@router.post("/events/{event_id}/assignments")
def assign_volunteer(
    event_id: str,
    person_id: str,
    role: str,
    db: Session = Depends(get_db)
):
    """Assign volunteer to event."""
    # Create assignment (existing logic)
    assignment = EventAssignment(
        event_id=event_id,
        person_id=person_id,
        role=role
    )
    db.add(assignment)
    db.commit()

    # NEW: Create notification
    event = db.query(Event).filter(Event.id == event_id).first()
    notification = Notification(
        org_id=event.org_id,
        recipient_id=person_id,
        type=NotificationType.ASSIGNMENT,
        event_id=event_id,
        template_data={
            "event_title": event.title,
            "event_date": event.datetime.strftime("%B %d, %Y"),
            "event_time": event.datetime.strftime("%I:%M %p"),
            "event_location": event.location,
            "role": role,
            "schedule_link": f"{settings.FRONTEND_BASE_URL}/app/schedule",
            "unsubscribe_link": f"{settings.FRONTEND_BASE_URL}/api/email-preferences/unsubscribe/..."
        }
    )
    db.add(notification)
    db.commit()

    # Queue email task
    send_email_task.delay(notification.id)

    return assignment
```

---

## Testing Strategy

### 1. Unit Tests (Models & Services)

```python
# tests/unit/test_email_service.py

def test_email_service_renders_template():
    """Test that email templates render correctly."""
    service = EmailService()
    html = service.render_template("assignment_en.html", {
        "volunteer_name": "John Doe",
        "event_title": "Test Event"
    })
    assert "John Doe" in html
    assert "Test Event" in html
```

### 2. Integration Tests (API Endpoints)

```python
# tests/integration/test_notifications_api.py

def test_create_notification_admin_only(client, admin_headers):
    """Test that only admins can create notifications."""
    response = client.post(
        "/api/notifications?org_id=org_test",
        json={
            "recipient_id": "person_123",
            "type": "assignment",
            "template_data": {"event_title": "Test"}
        },
        headers=admin_headers
    )
    assert response.status_code == 201
```

### 3. E2E Tests (User Workflows)

```python
# tests/e2e/test_email_notification_flow.py

def test_volunteer_receives_assignment_email(page: Page, db: Session):
    """Test complete flow: assign volunteer → receives email."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    # ... login steps

    # Assign volunteer to event
    page.goto("http://localhost:8000/app/admin#events")
    page.locator('[data-event-id="event_123"]').click()
    page.locator('button:has-text("Assign Volunteer")').click()
    page.select_option('#volunteer-select', 'person_456')
    page.click('button:has-text("Save")')

    # Verify notification created
    notification = db.query(Notification)\
        .filter(Notification.recipient_id == "person_456")\
        .filter(Notification.type == NotificationType.ASSIGNMENT)\
        .order_by(Notification.created_at.desc())\
        .first()

    assert notification is not None
    assert notification.status in [NotificationStatus.QUEUED, NotificationStatus.SENT]

    # Verify email sent (check Mailtrap inbox via API)
    # ...
```

### 4. Webhook Testing (SendGrid Events)

Use **ngrok** to expose local server for webhook testing:

```bash
# Terminal 1: Start server
make run

# Terminal 2: Start ngrok
ngrok http 8000

# Output: Forwarding https://abc123.ngrok.io -> http://localhost:8000

# Update SendGrid webhook URL to: https://abc123.ngrok.io/api/webhooks/sendgrid

# Trigger test event
# Send test email via SendGrid
# Watch webhook events arrive at your local server

# Check logs
tail -f logs/webhook.log
```

---

## Common Pitfalls

### 1. ❌ Forgetting Multi-Tenant Isolation

```python
# WRONG - Data leak!
notifications = db.query(Notification).all()

# CORRECT - Filter by org_id
notifications = db.query(Notification)\
    .filter(Notification.org_id == org_id)\
    .all()
```

### 2. ❌ Not Checking Email Preferences

```python
# WRONG - Sends email even if user disabled notifications
send_email_task.delay(notification_id)

# CORRECT - Check preferences first
prefs = get_email_preferences(db, person_id, org_id)
if prefs.is_type_enabled(NotificationType.ASSIGNMENT):
    send_email_task.delay(notification_id)
```

### 3. ❌ Hardcoding English Text

```python
# WRONG - Only English
subject = "New Assignment"

# CORRECT - Use i18n
from api.core.i18n import get_message
subject = get_message("email.assignment.subject", language)
```

### 4. ❌ Not Handling SendGrid Errors

```python
# WRONG - No error handling
response = client.send(message)

# CORRECT - Handle errors and retry
try:
    response = client.send(message)
    if response.status_code >= 400:
        raise EmailDeliveryException(response.body)
except Exception as e:
    # Log error and queue for retry
    logger.error(f"SendGrid error: {e}")
    raise
```

### 5. ❌ Missing E2E Tests

```python
# WRONG - Only API tests
def test_notification_created():
    response = client.post("/api/notifications", ...)
    assert response.status_code == 201

# CORRECT - E2E test covering user workflow
def test_volunteer_receives_notification_email(page: Page):
    # Login as admin
    # Assign volunteer
    # Verify email received
    # Verify notification status updated
```

---

## Troubleshooting

### Issue 1: Celery Worker Not Starting

**Symptom**: `celery -A api.celery_app worker` fails

**Solutions**:
```bash
# Check Redis running
redis-cli ping  # Should return "PONG"

# Check Celery app imports correctly
poetry run python -c "from api.celery_app import celery_app; print(celery_app)"

# Check for circular imports
poetry run python -c "import api.tasks.notifications"
```

### Issue 2: Emails Not Sending

**Symptom**: Notifications stuck in `QUEUED` status

**Solutions**:
```bash
# Check Celery worker is running and processing tasks
# Check Celery logs for errors

# Test SendGrid API key
poetry run python -c "
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
client = SendGridAPIClient('YOUR_API_KEY')
message = Mail(from_email='test@example.com', to_emails='test@example.com', subject='Test', html_content='Test')
response = client.send(message)
print(response.status_code)  # Should be 202
"

# Check SendGrid dashboard for errors
# https://app.sendgrid.com/email_activity
```

### Issue 3: Webhook Events Not Received

**Symptom**: SendGrid webhooks not updating notification status

**Solutions**:
```bash
# Verify webhook URL is correct in SendGrid dashboard
# Verify ngrok tunnel is running (for local dev)
# Check signature verification isn't failing

# Test webhook endpoint manually
curl -X POST http://localhost:8000/api/webhooks/sendgrid \
  -H "Content-Type: application/json" \
  -d '[{"event":"delivered","sg_message_id":"test_123"}]'
```

### Issue 4: Template Rendering Errors

**Symptom**: Jinja2 template errors

**Solutions**:
```bash
# Verify template directory exists
ls -la api/templates/email/

# Verify template file exists
cat api/templates/email/assignment_en.html

# Test template rendering
poetry run python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('api/templates/email'))
template = env.get_template('assignment_en.html')
print(template.render(volunteer_name='Test', event_title='Test Event'))
"
```

---

## Next Steps

After completing implementation:

1. ✅ All Phase 1-5 implementations complete
2. ✅ All unit tests passing (`make test`)
3. ✅ All integration tests passing
4. ✅ All E2E tests passing (`poetry run pytest tests/e2e/`)
5. ✅ Manual testing in browser complete
6. ✅ Code review and constitution compliance check
7. ✅ Update `CLAUDE.md` with email notification patterns
8. ✅ Run `/speckit.tasks` to break down into implementation tasks

---

**Document Status**: ✅ COMPLETE
**Target Audience**: Developers implementing email notifications
**Estimated Implementation Time**: 3-5 days (full-time developer)
**Complexity**: Medium (requires Celery, SendGrid, Jinja2 integration)
