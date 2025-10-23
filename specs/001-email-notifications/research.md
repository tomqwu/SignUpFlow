# Technology Research & Decisions: Email Notification System

**Feature**: Email Notification System for Volunteer Assignments
**Date**: 2025-01-20
**Status**: Complete

## Executive Summary

This document records all technology decisions, alternatives evaluated, and rationale for the email notification system implementation. All decisions prioritize simplicity, leverage existing project infrastructure, and maintain constitution compliance.

---

## Decision 1: Email Service Provider

### Question
Which email service provider should we use for sending transactional notification emails?

### Options Evaluated

| Provider | Pros | Cons | Cost |
|----------|------|------|------|
| **Mailtrap** | - **Sandbox API** for dev/CI/test (captures emails safely)<br>- **Email API** for production delivery<br>- Unified platform for testing & production<br>- Excellent Python SDK<br>- Inbox UI for email preview<br>- No accidental email sends in testing | - Smaller market share than SendGrid<br>- Less mature than incumbents | Sandbox: Free<br>Email API: Pay-as-you-go |
| **SendGrid** | - Industry-leading deliverability (99%+)<br>- Excellent Python SDK<br>- Robust webhook support<br>- 100 emails/day free tier<br>- Detailed analytics dashboard | - Pricing jumps after free tier<br>- Separate testing infrastructure needed<br>- Risk of accidental sends in dev | Free: 100/day<br>Paid: $15/mo for 50k |
| **Mailgun** | - Developer-friendly API<br>- Good documentation<br>- 100 emails/day free | - Lower deliverability than SendGrid<br>- Webhook setup more complex<br>- Less comprehensive analytics | Free: 100/day<br>Paid: $35/mo for 50k |
| **AWS SES** | - Lowest cost ($0.10 per 1000)<br>- Reliable infrastructure<br>- Easy if already on AWS | - More complex setup (IAM, SMTP)<br>- No built-in analytics<br>- Requires separate bounce handling<br>- No free tier for non-AWS | $0.10 per 1000 emails |

### Decision: **Mailtrap** (Updated 2025-10-21)

**Rationale**:
1. **Unified Testing & Production**: Single platform with Sandbox API (dev/CI/staging) and Email API (production)
2. **Safety**: Sandbox API captures all emails in dev/test without risk of accidental sends to real users
3. **Already Configured**: API token already available (`f20c08c0e6c5a8c6a4fd123fa35ae173`)
4. **E2E Testing**: Can verify actual email delivery in integration tests using Sandbox API
5. **Cost-Effective**: Free Sandbox API for testing, pay-as-you-go Email API for production
6. **Seamless Promotion**: Same codebase works across environments (just change `MAILTRAP_MODE` env var)
7. **Developer Experience**: Inbox UI provides visual verification of email formatting
8. **Constitution Compliance**: Supports E2E testing principle (can test real email delivery)

**Implementation Plan**:
- **Sandbox API** (dev/CI/staging):
  - Base URL: `https://sandbox.api.mailtrap.io/api/send/4115456`
  - API Token: `f20c08c0e6c5a8c6a4fd123fa35ae173`
  - Use for: Local development, CI/CD tests, integration tests
- **Email API** (production):
  - Base URL: `https://send.api.mailtrap.io/api/send`
  - API Token: Same token (or separate production token)
  - Use for: Real email delivery in production
- **Environment Configuration**:
  ```python
  MAILTRAP_MODE=sandbox  # dev/test/staging
  MAILTRAP_MODE=production  # production
  MAILTRAP_API_TOKEN=f20c08c0e6c5a8c6a4fd123fa35ae173
  ```
- **Adapter Pattern**: `MailtrapAdapter` implements `EmailServiceInterface` for both modes

**Alternatives Rejected**:
- SendGrid: Requires separate testing infrastructure (Mailtrap or similar), risk of accidental sends
- AWS SES: Too complex for MVP, no built-in testing sandbox
- Mailgun: Lower deliverability, no integrated testing solution

---

## Decision 2: Async Job Queue

### Question
How should we handle asynchronous email sending to avoid blocking API requests?

### Options Evaluated

| Solution | Pros | Cons | Complexity |
|----------|------|------|------------|
| **Celery + Redis** | - Battle-tested (10+ years)<br>- Supports scheduled tasks (reminders)<br>- Robust retry logic<br>- Excellent monitoring tools<br>- Large community | - Requires Redis (additional dependency)<br>- More heavyweight than alternatives<br>- Learning curve for configuration | Medium |
| **RQ (Redis Queue)** | - Simpler than Celery<br>- Python-native<br>- Good for simple queues<br>- Requires Redis | - No built-in scheduled tasks<br>- Less mature retry logic<br>- Smaller community<br>- Would need separate cron for reminders | Low |
| **Dramatiq** | - Modern design<br>- Lighter than Celery<br>- Good retry logic<br>- Can use Redis or RabbitMQ | - Scheduled tasks require separate package<br>- Smaller community<br>- Less proven at scale | Low-Medium |
| **FastAPI Background Tasks** | - Built into FastAPI<br>- No external dependencies<br>- Simple for basic tasks | - Not persistent (lost on restart)<br>- No retry logic<br>- No scheduled tasks<br>- Not suitable for critical jobs | Very Low |

### Decision: **Celery + Redis**

**Rationale**:
1. **Scheduled Tasks**: Native support for cron-style scheduled jobs (24-hour reminders, weekly summaries)
2. **Retry Logic**: Built-in exponential backoff retry (critical for email delivery reliability)
3. **Monitoring**: Flower dashboard for real-time worker monitoring and debugging
4. **Proven at Scale**: Battle-tested by thousands of production applications
5. **Priority Queues**: Can prioritize urgent notifications (assignment/cancellation) over reminders
6. **Dead Letter Queue**: Failed tasks moved to separate queue for manual review
7. **Project Fit**: SignUpFlow likely already uses Redis for session storage or caching

**Implementation Plan**:
- Install: `celery[redis]==5.3+`, `redis==5.0+`
- Configuration: `CELERY_BROKER_URL=redis://localhost:6379/0`
- Task Structure:
  - `api/tasks/notifications.py` - Async email sending tasks
  - `api/tasks/reminders.py` - Scheduled reminder cron job
- Worker Command: `celery -A api.tasks worker --loglevel=info`
- Monitoring: Deploy Flower for production monitoring

**Alternatives Rejected**:
- RQ: No native scheduled task support (would need separate cron)
- Dramatiq: Less mature scheduled task story
- FastAPI Background Tasks: Not persistent, no retry logic (unacceptable for critical notifications)

---

## Decision 3: Email Template Engine

### Question
What template engine should we use for generating HTML emails with i18n support?

### Options Evaluated

| Engine | Pros | Cons | i18n Support |
|--------|------|------|--------------|
| **Jinja2** | - Already in project (FastAPI uses it)<br>- Excellent i18n integration<br>- Auto-escaping prevents XSS<br>- Large ecosystem<br>- Template inheritance | - Slightly verbose syntax | Excellent (babel integration) |
| **Mako** | - Faster than Jinja2<br>- Python-like syntax | - Less popular<br>- Manual XSS prevention<br>- Weaker i18n story | Fair (manual setup) |
| **Python f-strings** | - Native Python<br>- Very simple<br>- Fast | - No XSS protection<br>- No template reuse<br>- Poor i18n support<br>- HTML in Python code (bad separation) | Poor (manual) |
| **Mjml** | - Responsive email framework<br>- Great email client compatibility | - Requires Node.js toolchain<br>- Additional build step<br>- Overkill for simple templates | Good (with Jinja2) |

### Decision: **Jinja2**

**Rationale**:
1. **Already in Project**: FastAPI already uses Jinja2 for any server-side rendering needs
2. **i18n Integration**: Seamless integration with Python Babel for translations
3. **Auto-Escaping**: Prevents XSS vulnerabilities by default (security-first principle)
4. **Template Inheritance**: Base email template with blocks for customization
5. **Proven for Email**: Widely used for email template rendering in production
6. **No Additional Dependencies**: Zero new infrastructure required

**Implementation Plan**:
- Create base template: `api/templates/email/base.html`
- Child templates: `assignment.html`, `reminder.html`, `change.html`, `cancellation.html`
- i18n Pattern:
  ```python
  from jinja2 import Environment, FileSystemLoader
  from babel.support import Translations

  env = Environment(loader=FileSystemLoader('api/templates/email'))
  env.install_gettext_translations(Translations.load('locales', [lang]))
  template = env.get_template('assignment.html')
  html = template.render(event=event, person=person)
  ```
- Translation Keys: `locales/{lang}/email.json`

**Alternatives Rejected**:
- Mako: Not already in project, weaker i18n
- F-strings: No XSS protection, poor separation of concerns
- Mjml: Overkill for simple templates, requires Node.js toolchain

---

## Decision 4: Email Delivery Tracking

### Question
How should we track email delivery status (sent, delivered, opened, clicked, bounced)?

### Options Evaluated

| Approach | Pros | Cons | Reliability |
|----------|------|------|-------------|
| **SendGrid Event Webhook** | - Real-time delivery events<br>- Automatic retries<br>- Detailed event data<br>- No polling required | - Requires public webhook endpoint<br>- Need to handle duplicate events | Excellent |
| **SendGrid API Polling** | - Simple to implement<br>- No webhook setup | - Delayed status updates<br>- Rate limits on polling<br>- Less efficient | Good |
| **SMTP Read Receipts** | - Standard email protocol | - User must enable read receipts<br>- Often disabled by clients<br>- Unreliable | Poor |
| **Tracking Pixels** | - Simple implementation<br>- Works without webhooks | - Often blocked by email clients<br>- Privacy concerns<br>- Only tracks opens, not delivery | Fair |

### Decision: **SendGrid Event Webhook**

**Rationale**:
1. **Real-Time**: Immediate notification of delivery events (critical for debugging failures)
2. **Comprehensive**: Tracks all events - delivered, bounced, opened, clicked, spam reports
3. **Reliable**: SendGrid automatically retries failed webhook deliveries
4. **Standard Practice**: Industry-standard approach for transactional email tracking
5. **Success Criteria Alignment**: Enables measurement of SC-003 (90% delivery), SC-004 (60% open rate), SC-005 (70% CTR)

**Implementation Plan**:
- Webhook Endpoint: `POST /api/webhooks/sendgrid`
- Event Handling:
  ```python
  @router.post("/webhooks/sendgrid")
  async def handle_sendgrid_webhook(events: List[dict], db: Session):
      for event in events:
          notification_id = event.get("notification_id")  # Custom arg
          status = event.get("event")  # delivered, bounce, open, click

          # Log to DeliveryLog table
          log = DeliveryLog(
              notification_id=notification_id,
              status=status,
              provider_response=event,
              timestamp=datetime.utcnow()
          )
          db.add(log)
      db.commit()
  ```
- SendGrid Configuration:
  - Add webhook URL in SendGrid dashboard
  - Enable events: delivered, bounce, open, click, dropped, spam_report
  - Include custom args: `notification_id` for correlation
- Security: Verify SendGrid webhook signature to prevent spoofing

**Alternatives Rejected**:
- API Polling: Inefficient, delayed updates
- Read Receipts: Unreliable (user-controlled)
- Tracking Pixels: Often blocked, privacy concerns

---

## Decision 5: Development & Testing Strategy

### Question
How should we test email functionality in development and CI/CD environments?

### Options Evaluated

| Approach | Pros | Cons | Cost |
|----------|------|------|------|
| **Mailtrap (dev)** | - Free tier (500 emails/mo)<br>- Full email testing (HTML preview)<br>- No real emails sent<br>- Great for development | - Requires account signup<br>- Not for CI automation | Free: 500/mo |
| **SendGrid Sandbox Mode** | - No external service<br>- Built into SendGrid<br>- Perfect for CI/CD<br>- Free | - No HTML preview<br>- Returns fake success (no validation) | Free |
| **MailHog (self-hosted)** | - Completely free<br>- Self-hosted<br>- SMTP server + web UI | - Requires Docker/deployment<br>- Another service to manage | Free |
| **Real SendGrid (test mode)** | - Tests real integration<br>- Validates everything works | - Uses SendGrid quota<br>- Requires email cleanup | Uses quota |

### Decision: **Hybrid Approach**

**Mailtrap for Local Development** + **SendGrid Sandbox for CI/CD**

**Rationale**:
1. **Local Dev**: Mailtrap provides full email preview without consuming SendGrid quota
2. **CI/CD**: SendGrid sandbox mode perfect for automated testing (no external dependencies)
3. **E2E Testing**: Mock SendGrid API calls for E2E tests (don't actually send emails)
4. **Cost**: Both completely free within usage limits
5. **Constitution Compliance**: Supports E2E testing principle (Principle 1)

**Implementation Plan**:

**Local Development (Mailtrap)**:
```python
# .env.development
EMAIL_BACKEND=mailtrap
MAILTRAP_HOST=sandbox.smtp.mailtrap.io
MAILTRAP_PORT=2525
MAILTRAP_USER=<from_mailtrap_dashboard>
MAILTRAP_PASSWORD=<from_mailtrap_dashboard>
```

**CI/CD (SendGrid Sandbox)**:
```python
# .env.ci
EMAIL_BACKEND=sendgrid
SENDGRID_API_KEY=<test_api_key>
SENDGRID_SANDBOX_MODE=true  # Validates but doesn't send
```

**E2E Tests (Mocked)**:
```python
# tests/e2e/test_email_notifications.py
from unittest.mock import patch

@patch('api.services.email_service.send_email')
def test_assignment_notification_sent(mock_send, page: Page):
    """Test that assigning volunteer triggers email notification."""
    # Arrange: Navigate to admin panel
    page.goto("http://localhost:8000/app/admin")

    # Act: Assign volunteer to event
    assign_volunteer_to_event(page, "Jane Doe", "Sunday Service")

    # Assert: Email service called with correct params
    mock_send.assert_called_once()
    call_args = mock_send.call_args[0]
    assert call_args['to'] == 'jane@test.com'
    assert 'Sunday Service' in call_args['subject']
    assert call_args['template'] == 'assignment'
```

**Alternatives Rejected**:
- MailHog: Another service to deploy and manage (unnecessary complexity)
- Real SendGrid in tests: Consumes quota, requires cleanup, flaky (network issues)

---

## Decision 6: Database Schema Design

### Question
What database tables and relationships are needed for notifications?

### Schema Decision

**Three New Tables**:

1. **notifications** - Core notification records
2. **email_preferences** - Volunteer notification settings
3. **delivery_logs** - Audit trail of delivery attempts

**Relationships**:
- `notifications.recipient_id` → `people.id` (who receives notification)
- `notifications.event_id` → `events.id` (related event, nullable)
- `notifications.org_id` → `organizations.id` (multi-tenant isolation)
- `email_preferences.person_id` → `people.id` (one-to-one)
- `delivery_logs.notification_id` → `notifications.id` (one-to-many)

**Rationale**:
1. **Separation of Concerns**: Notifications separate from delivery tracking
2. **Audit Trail**: DeliveryLog provides compliance-required audit history
3. **Performance**: Indexes on `org_id`, `recipient_id`, `status` for fast queries
4. **Multi-tenant**: Every table includes `org_id` for isolation (Constitution Principle 3)
5. **Extensibility**: Can add `notification_templates` table in future without migration

See [`data-model.md`](./data-model.md) for complete schema specifications.

---

## Decision 7: Rate Limiting Strategy

### Question
How should we handle SendGrid rate limits and avoid overwhelming the email service?

### Strategy Decision

**Celery Rate Limiting + Priority Queues**

**Implementation**:
```python
# api/tasks/notifications.py
from celery import Task

class RateLimitedEmailTask(Task):
    rate_limit = '100/m'  # 100 emails per minute (SendGrid limit)

@app.task(base=RateLimitedEmailTask, priority=9)  # High priority
def send_assignment_notification(notification_id):
    """Send immediate assignment/cancellation notification."""
    pass

@app.task(base=RateLimitedEmailTask, priority=5)  # Medium priority
def send_reminder_notification(notification_id):
    """Send 24-hour reminder (can be delayed if queue busy)."""
    pass

@app.task(base=RateLimitedEmailTask, priority=1)  # Low priority
def send_digest_notification(person_id):
    """Send daily/weekly digest (lowest priority)."""
    pass
```

**Rationale**:
1. **SendGrid Limits**: Free tier limits to 100 emails/day, paid tier 100/min
2. **Priority**: Urgent notifications (assignment/cancellation) sent first
3. **Graceful Degradation**: Reminders delayed if queue backed up (acceptable)
4. **Burst Handling**: Can queue 200 assignments, send over 2 minutes (rate-limited)
5. **Constitution Compliance**: Meets 2-minute delivery SLA for high-priority notifications

---

## Decision 8: Retry Logic

### Question
How should failed email deliveries be retried?

### Retry Strategy Decision

**Exponential Backoff: 1 hour → 4 hours → 24 hours**

**Implementation**:
```python
@app.task(bind=True, max_retries=3)
def send_email_task(self, notification_id):
    try:
        send_email_via_sendgrid(notification_id)
    except EmailDeliveryException as exc:
        # Exponential backoff: 1h, 4h, 24h
        retry_delays = [3600, 14400, 86400]  # seconds
        retry_count = self.request.retries

        if retry_count < len(retry_delays):
            raise self.retry(exc=exc, countdown=retry_delays[retry_count])
        else:
            # Max retries exceeded - log failure
            log_permanent_failure(notification_id, str(exc))
```

**Rationale**:
1. **Temporary Outages**: 1-hour retry catches brief SendGrid outages
2. **Extended Outages**: 4-hour retry for longer outages (maintenance windows)
3. **Permanent Failures**: 24-hour final attempt before marking as failed
4. **Admin Visibility**: Failed notifications appear in admin dashboard for manual review
5. **Spec Alignment**: Matches FR-009 requirement (3 retries with exponential backoff)

---

## Technology Stack Summary

### Core Technologies

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Email Provider** | SendGrid | Python SDK 6.11+ | Industry-leading deliverability, robust webhooks |
| **Async Queue** | Celery + Redis | Celery 5.3+, Redis 5.0+ | Scheduled tasks, retry logic, priority queues |
| **Template Engine** | Jinja2 | 3.1+ | Already in project, excellent i18n support |
| **Delivery Tracking** | SendGrid Webhooks | Event API v3 | Real-time, comprehensive, reliable |
| **Dev Testing** | Mailtrap | Web service | Free, no SendGrid quota usage |
| **CI Testing** | SendGrid Sandbox | Built-in | No external dependencies |
| **E2E Testing** | Mocked SendGrid | unittest.mock | Fast, deterministic, no network calls |

### New Dependencies

```python
# pyproject.toml additions
[tool.poetry.dependencies]
celery = {extras = ["redis"], version = "^5.3"}
redis = "^5.0"
sendgrid = "^6.11"
jinja2 = "^3.1"  # Already in project (FastAPI dependency)

[tool.poetry.dev-dependencies]
# No new dev dependencies (use existing pytest, playwright)
```

---

## Open Questions & Future Research

### Resolved ✅
1. ✅ Email service provider → SendGrid
2. ✅ Async job queue → Celery + Redis
3. ✅ Template engine → Jinja2
4. ✅ Delivery tracking → SendGrid webhooks
5. ✅ Testing strategy → Mailtrap (dev) + SendGrid sandbox (CI)
6. ✅ Rate limiting → Celery rate limits + priority queues
7. ✅ Retry logic → Exponential backoff (1h, 4h, 24h)

### Future Iterations (Out of Scope for MVP)
1. Multi-provider fallback (SendGrid → Mailgun for redundancy)
2. A/B testing for email templates (which subject lines perform better?)
3. Email template versioning (gradual rollout of template changes)
4. Advanced segmentation (target specific volunteer groups)
5. Email deliverability score dashboard (track sender reputation)

---

## References

### Documentation Links
- SendGrid Python SDK: https://github.com/sendgrid/sendgrid-python
- SendGrid Event Webhook: https://docs.sendgrid.com/for-developers/tracking-events/event
- Celery Documentation: https://docs.celeryproject.org/en/stable/
- Jinja2 i18n: https://jinja.palletsprojects.com/en/3.1.x/extensions/#i18n-extension
- Mailtrap: https://mailtrap.io/

### Best Practices
- Transactional Email Best Practices: https://sendgrid.com/blog/transactional-email-best-practices/
- Email Deliverability Guide: https://sendgrid.com/resource/the-ultimate-guide-to-email-deliverability/
- CAN-SPAM Compliance: https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business

---

**Research Complete**: 2025-01-20
**Status**: All technology decisions finalized and documented
**Next Phase**: Data Model Design (`data-model.md`)
