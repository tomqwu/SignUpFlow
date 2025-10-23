# Manual Validation Guide - Email Notification System

**Purpose**: Step-by-step guide to manually validate the email notification system end-to-end with actual email delivery.

**Target**: MVP (US1 - Assignment Notifications)

**Last Updated**: 2025-10-21

---

## Prerequisites Checklist

Before starting validation, ensure ALL prerequisites are met:

### ✅ System Requirements

- [ ] **Python 3.11+** installed
  ```bash
  python3 --version
  ```

- [ ] **Poetry** installed and working
  ```bash
  poetry --version
  ```

- [ ] **Redis** installed and running (REQUIRED for Celery)
  ```bash
  # Install Redis
  sudo apt-get update
  sudo apt-get install redis-server -y

  # Start Redis
  sudo systemctl start redis-server
  sudo systemctl enable redis-server

  # Verify Redis is running
  redis-cli ping  # Should return: PONG
  ```

- [ ] **Dependencies** installed
  ```bash
  cd /home/ubuntu/SignUpFlow
  poetry install
  ```

### ✅ Email Service Configuration

You need EITHER Mailtrap (development) OR SendGrid (production):

#### Option A: Mailtrap (Recommended for Development)

1. **Create free Mailtrap account**: https://mailtrap.io/
2. **Get SMTP credentials**:
   - Login → Inbox → SMTP Settings
   - Copy: Host, Port, Username, Password
3. **Update `.env` file**:
   ```bash
   MAILTRAP_SMTP_HOST=sandbox.smtp.mailtrap.io
   MAILTRAP_SMTP_PORT=2525
   MAILTRAP_SMTP_USER=your_actual_username_here
   MAILTRAP_SMTP_PASSWORD=your_actual_password_here
   EMAIL_FROM=noreply@signupflow.io
   EMAIL_FROM_NAME=SignUpFlow
   ```

#### Option B: SendGrid (Production)

1. **Create SendGrid account**: https://sendgrid.com/
2. **Generate API Key**:
   - Settings → API Keys → Create API Key
   - Permissions: Full Access (Mail Send)
3. **Update `.env` file**:
   ```bash
   SENDGRID_API_KEY=SG.your_actual_api_key_here
   EMAIL_FROM=noreply@signupflow.io
   EMAIL_FROM_NAME=SignUpFlow
   ```

### ✅ Celery Configuration

Verify `.env` has Celery settings:

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_ENABLED=true
EMAIL_SEND_ASSIGNMENT_NOTIFICATIONS=true
```

---

## Validation Workflow

### Step 1: Start Services

Open **3 terminal windows**:

#### Terminal 1: FastAPI Server

```bash
cd /home/ubuntu/SignUpFlow
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
🚀 SignUpFlow API started
📖 API docs available at http://localhost:8000/docs
```

**Keep this terminal running**

#### Terminal 2: Celery Worker

```bash
cd /home/ubuntu/SignUpFlow
poetry run celery -A api.celery_app worker --loglevel=info
```

**Expected output**:
```
[tasks]
  . api.tasks.notifications.send_email_task
  . api.tasks.notifications.send_reminder_emails
  . api.tasks.notifications.send_daily_digests
  . api.tasks.notifications.send_weekly_digests
  . api.tasks.notifications.send_admin_summaries

[2025-10-21 12:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-21 12:00:00,000: INFO/MainProcess] celery@hostname ready.
```

**Keep this terminal running**

#### Terminal 3: Testing Commands

Keep this terminal available for running tests and monitoring.

### Step 2: Verify System Health

In **Terminal 3**, run:

```bash
# Test API is running
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"signupflow-api","version":"1.0.0"}

# Test Redis is accessible
redis-cli ping

# Expected: PONG

# Test database is initialized
poetry run python -c "from api.models import Notification; print('✅ Models imported successfully')"

# Expected: ✅ Models imported successfully
```

### Step 3: Test Email Sending (Direct API Test)

**Using Mailtrap**:

```bash
# Test direct email sending (bypasses Celery for debugging)
poetry run python << 'EOF'
from api.services.email_service import EmailService
from api.core.config import settings

email_service = EmailService()

# Send test email
email_service.send_email(
    to_email="test@example.com",
    subject="Test Email from SignUpFlow",
    template_name="assignment",
    template_data={
        "volunteer_name": "Test User",
        "event_title": "Sunday Service",
        "event_datetime": "2025-11-01 10:00 AM",
        "role": "Greeter",
        "event_location": "Main Building"
    },
    language="en"
)

print("✅ Email sent successfully!")
print(f"📧 Check your Mailtrap inbox: https://mailtrap.io/inboxes")
EOF
```

**Verification**:
1. Login to Mailtrap: https://mailtrap.io/inboxes
2. Check inbox - you should see the email
3. Verify email content:
   - Subject: "New Assignment: Sunday Service"
   - Body contains: "Test User", "Greeter", "Sunday Service"
   - HTML formatting is correct

**If email doesn't appear**:
- Check SMTP credentials in `.env`
- Check Terminal 1 (FastAPI) for errors
- Check Mailtrap SMTP Settings match your `.env`

### Step 4: Test Assignment Notification (Full Workflow)

Now test the complete workflow: Assignment → Notification → Email

#### 4.1: Login to SignUpFlow

Open browser: http://localhost:8000/

```
Email: pastor@grace.church
Password: password
```

*(If you don't have this test user, create one via signup)*

#### 4.2: Create Event

1. Navigate to **Admin Console**
2. Click **Events** tab
3. Click **+ Create Event**
4. Fill in:
   - Title: "Test Service"
   - Date/Time: (select future date)
   - Location: "Main Building"
5. Click **Create**

#### 4.3: Assign Volunteer to Event

1. Go to event details
2. Click **Assign Volunteer**
3. Select volunteer: (select any volunteer user)
4. Select role: "Greeter"
5. Click **Assign**

#### 4.4: Verify Notification Created

**In Terminal 3**:

```bash
# Check notification was created in database
poetry run python << 'EOF'
from api.database import get_db
from api.models import Notification
from sqlalchemy.orm import Session

db = next(get_db())
notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()

print(f"📊 Recent notifications ({len(notifications)} found):")
for n in notifications:
    print(f"  - ID: {n.id} | Type: {n.type} | Status: {n.status} | Recipient: {n.recipient_id}")
    print(f"    Created: {n.created_at} | Sent: {n.sent_at}")
EOF
```

**Expected output**:
```
📊 Recent notifications (1 found):
  - ID: 123 | Type: assignment | Status: sent | Recipient: person_volunteer_123
    Created: 2025-10-21 12:30:00 | Sent: 2025-10-21 12:30:05
```

#### 4.5: Verify Celery Task Executed

**In Terminal 2 (Celery Worker)**:

Look for output like:
```
[2025-10-21 12:30:05,000: INFO/MainProcess] Task api.tasks.notifications.send_email_task[abc-123] received
[2025-10-21 12:30:06,000: INFO/ForkPoolWorker-1] Sending assignment notification to test@example.com
[2025-10-21 12:30:07,000: INFO/ForkPoolWorker-1] Task api.tasks.notifications.send_email_task[abc-123] succeeded in 2.1s
```

If you see errors like:
- `Connection refused` → Redis not running (go back to Prerequisites)
- `SMTP authentication failed` → Check `.env` credentials
- `Task timeout` → Email service may be slow, check network

#### 4.6: Verify Email Received

**Check Mailtrap Inbox**:

1. Go to https://mailtrap.io/inboxes
2. Refresh inbox
3. You should see new email:
   - **Subject**: "New Assignment: Test Service"
   - **From**: SignUpFlow <noreply@signupflow.io>
   - **To**: (volunteer's email)
   - **Body**:
     - Greeting with volunteer name
     - Event title: "Test Service"
     - Role: "Greeter"
     - Date/time and location
     - Calendar integration link

**Verify HTML rendering**:
- Email should be responsive (mobile-friendly)
- Professional styling with SignUpFlow branding
- All links should be functional

### Step 5: Test Email Preferences (Optional)

Test that volunteers can manage their notification preferences:

#### 5.1: Get Current Preferences

```bash
curl -X GET "http://localhost:8000/api/notifications/preferences/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected**:
```json
{
  "person_id": "person_volunteer_123",
  "org_id": "org_church_456",
  "frequency": "immediate",
  "enabled_types": ["assignment", "reminder", "update", "cancellation"],
  "language": "en",
  "timezone": "America/New_York",
  "digest_hour": 8
}
```

#### 5.2: Update Preferences

```bash
curl -X PUT "http://localhost:8000/api/notifications/preferences/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "frequency": "daily",
    "enabled_types": ["assignment", "reminder"],
    "language": "es"
  }'
```

**Expected**:
```json
{
  "person_id": "person_volunteer_123",
  "frequency": "daily",
  "enabled_types": ["assignment", "reminder"],
  "language": "es"
}
```

#### 5.3: Verify Preferences Respected

Assign volunteer to another event - email should:
- Be in Spanish (language: "es")
- NOT be sent immediately (frequency: "daily")

### Step 6: Test Admin Statistics (Optional)

Verify admins can see org-wide notification stats:

```bash
curl -X GET "http://localhost:8000/api/notifications/stats/organization?org_id=org_church_456&days=7" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN_HERE"
```

**Expected**:
```json
{
  "org_id": "org_church_456",
  "days_analyzed": 7,
  "total_notifications": 15,
  "delivered_notifications": 14,
  "success_rate": 93.33,
  "status_breakdown": {
    "sent": 10,
    "delivered": 4,
    "pending": 1
  },
  "type_breakdown": {
    "assignment": 12,
    "reminder": 3
  },
  "recent_failures": []
}
```

---

## Success Criteria

Mark validation as ✅ PASSED if ALL of the following are true:

- [ ] **Redis is running** - `redis-cli ping` returns `PONG`
- [ ] **Celery worker is connected** - Terminal 2 shows "celery@hostname ready"
- [ ] **Direct email test passed** - Step 3 sent email to Mailtrap
- [ ] **Assignment creates notification** - Step 4.4 shows notification in database
- [ ] **Celery task executes** - Step 4.5 shows task success in worker logs
- [ ] **Email delivered to inbox** - Step 4.6 shows email in Mailtrap with correct content
- [ ] **Email is properly formatted** - HTML rendering is professional and responsive
- [ ] **No errors in logs** - All 3 terminals show no errors

---

## Troubleshooting

### Problem: Redis not running

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server -y

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return PONG
```

### Problem: Celery worker won't start

**Error**: `ModuleNotFoundError: No module named 'celery'`

**Solution**:
```bash
# Reinstall dependencies
cd /home/ubuntu/SignUpFlow
poetry install

# Verify celery is installed
poetry run celery --version
```

### Problem: Email not sending

**Error**: `SMTPAuthenticationError: (535, b'Authentication failed')`

**Solution**:
1. Check `.env` file has correct SMTP credentials
2. Verify credentials work in Mailtrap dashboard
3. Copy-paste exact values (no extra spaces)
4. Restart FastAPI server after changing `.env`

### Problem: Email sent but not received

**Checklist**:
1. ✅ Celery worker logs show task success?
2. ✅ Database shows notification status = "sent"?
3. ✅ Check Mailtrap spam/trash folders?
4. ✅ Correct Mailtrap inbox selected?
5. ✅ EMAIL_FROM in `.env` matches Mailtrap sender?

### Problem: Wrong email content

**Issue**: Email shows placeholder text like `{{ volunteer_name }}`

**Solution**: Jinja2 template rendering failed
```bash
# Verify template exists
ls -la /home/ubuntu/SignUpFlow/api/templates/email/assignment_en.html

# Check template syntax
poetry run python << 'EOF'
from jinja2 import Template
with open('api/templates/email/assignment_en.html') as f:
    template = Template(f.read())
    result = template.render(volunteer_name="Test", event_title="Event")
    print("✅ Template renders successfully")
EOF
```

### Problem: Celery tasks queued but not executing

**Symptoms**: Database shows status="pending" but never changes to "sent"

**Solution**:
1. Check Celery worker is running (Terminal 2)
2. Check Redis is running: `redis-cli ping`
3. Check Celery logs for errors
4. Restart Celery worker:
   ```bash
   # Ctrl+C in Terminal 2 to stop worker
   poetry run celery -A api.celery_app worker --loglevel=debug
   ```

### Problem: Performance issues

**Symptoms**: Email takes > 30 seconds to send

**Solution**:
1. Check Redis memory: `redis-cli info memory`
2. Check Celery worker concurrency: `poetry run celery -A api.celery_app worker --concurrency=4`
3. Check network latency to SMTP server
4. Consider using SendGrid instead of SMTP (faster)

---

## Next Steps After Validation

Once validation passes (all ✅), you can:

1. **Mark MVP complete** - US1 (Assignment Notifications) is production-ready
2. **Deploy to staging** - Test with real users before production
3. **Implement US2-US5** - Reminder emails, schedule updates, admin summaries
4. **Setup SendGrid webhooks** - Track email opens, clicks, bounces
5. **Production deployment** - Configure SendGrid API key, deploy to production server

---

## Test Data Cleanup

After validation, clean up test data:

```bash
# Remove test notifications
poetry run python << 'EOF'
from api.database import get_db
from api.models import Notification
db = next(get_db())

# Delete test notifications
test_notifications = db.query(Notification).filter(
    Notification.type == "assignment",
    Notification.created_at >= "2025-10-21"
).all()

for n in test_notifications:
    db.delete(n)

db.commit()
print(f"✅ Deleted {len(test_notifications)} test notifications")
EOF
```

---

## Validation Checklist Summary

Print this checklist and check off items as you complete them:

```
PREREQUISITES
□ Python 3.11+ installed
□ Poetry installed
□ Redis installed and running
□ Dependencies installed via poetry
□ Mailtrap OR SendGrid configured in .env
□ .env file has Celery configuration

SERVICES RUNNING
□ Terminal 1: FastAPI server running on port 8000
□ Terminal 2: Celery worker connected to Redis
□ Terminal 3: Available for testing commands

VALIDATION TESTS
□ Step 2: Health check passes
□ Step 3: Direct email test sends to Mailtrap
□ Step 4.2: Event created successfully
□ Step 4.3: Volunteer assigned to event
□ Step 4.4: Notification created in database
□ Step 4.5: Celery task executes successfully
□ Step 4.6: Email received in Mailtrap inbox
□ Step 4.6: Email content is correct (name, event, role)
□ Step 4.6: Email HTML formatting is professional

OPTIONAL TESTS
□ Step 5: Email preferences can be updated
□ Step 6: Admin can view notification statistics

SUCCESS CRITERIA
□ All validation tests passed
□ No errors in any terminal
□ Email received within 10 seconds of assignment

RESULT: [ ] ✅ VALIDATION PASSED  [ ] ❌ NEEDS DEBUGGING
```

---

**Manual Validation Guide Version**: 1.0
**Created**: 2025-10-21
**Next Review**: After first production deployment
