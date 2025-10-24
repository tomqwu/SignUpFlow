# API Contract: SMS Messaging Endpoints

**Feature**: SMS Notification System | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23

Core message sending endpoints for individual SMS delivery, broadcast messaging, message history, and usage analytics.

---

## Endpoints

### 1. Send Individual SMS Message

**Endpoint**: `POST /api/sms/send`

**Purpose**: Send SMS to single volunteer (assignment notification, reminder, or custom message)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID for multi-tenancy verification

**Request Body**:
```json
{
  "recipient_id": 123,
  "message_type": "assignment",
  "message_text": "Sunday Service - Jan 1 at 10:00AM - Role: Usher. Reply YES to confirm, NO to decline",
  "event_id": 456,
  "template_id": 789,
  "is_urgent": false
}
```

**Field Specifications**:
- `recipient_id` (required, integer): Person ID of SMS recipient (must belong to org_id)
- `message_type` (required, string): Message category (`assignment`, `reminder`, `broadcast`, `system`)
- `message_text` (required if template_id not provided, string): SMS message content (max 1600 chars)
- `event_id` (optional, integer): Associated event ID (for assignment/reminder messages)
- `template_id` (optional, integer): Template ID to render (alternative to message_text)
- `is_urgent` (optional, boolean, default: false): Bypass rate limits and quiet hours

**Validation Rules**:
1. Recipient must have verified SMS preferences (sms_preferences.verified = true)
2. Recipient must not be opted out (sms_preferences.opt_out_date IS NULL)
3. Message text must be 1-1600 characters (if provided)
4. If template_id provided, template must exist and belong to organization
5. Rate limit check: Max 3 SMS per recipient per day (unless is_urgent=true)
6. Quiet hours check: 10pm-8am local time (unless is_urgent=true)
7. Budget check: Organization must have remaining SMS budget (assignments bypass if at 100%)

**Response**:

**Success (201 Created)**:
```json
{
  "message_id": 12345,
  "status": "queued",
  "twilio_message_sid": "SM1234567890abcdef1234567890abcdef",
  "phone_number": "+15551234567",
  "character_count": 85,
  "cost_cents": 79,
  "queued_for_delivery": true,
  "send_time": "2025-01-01T10:00:00Z"
}
```

**Error Responses**:

**400 Bad Request** - Validation failure:
```json
{
  "detail": "Recipient does not have verified phone number"
}
```

**403 Forbidden** - Authorization failure:
```json
{
  "detail": "Admin access required"
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Rate limit exceeded: max 3 SMS per volunteer per day",
  "retry_after": "2025-01-02T00:00:00Z"
}
```

**503 Service Unavailable** - Quiet hours enforcement:
```json
{
  "detail": "Message queued for delivery at 8:00 AM (quiet hours: 10pm-8am)",
  "queued_until": "2025-01-02T08:00:00Z"
}
```

---

### 2. Send Broadcast SMS

**Endpoint**: `POST /api/sms/broadcast`

**Purpose**: Send same message to multiple volunteers (team notifications, urgent updates, cancellations)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "recipient_ids": [123, 456, 789],
  "message_type": "broadcast",
  "message_text": "URGENT: Sunday service cancelled due to weather. Stay safe!",
  "team_id": 10,
  "is_urgent": true,
  "bypass_quiet_hours": true
}
```

**Field Specifications**:
- `recipient_ids` (optional, array[integer]): Specific volunteer IDs (mutually exclusive with team_id)
- `team_id` (optional, integer): Team ID to broadcast to all members (mutually exclusive with recipient_ids)
- `message_type` (required, string): Must be `broadcast`
- `message_text` (required, string): Broadcast message (max 1600 chars)
- `is_urgent` (optional, boolean, default: false): Bypass rate limits
- `bypass_quiet_hours` (optional, boolean, default: false): Send immediately regardless of time

**Validation Rules**:
1. Must provide either recipient_ids OR team_id (not both)
2. Maximum 200 recipients per broadcast
3. All recipients must have verified SMS preferences
4. Message text 1-1600 characters
5. Budget check: Organization must have remaining budget (critical broadcasts bypass if urgent=true)
6. Rate limits still apply per volunteer (unless is_urgent=true)

**Response**:

**Success (202 Accepted)**:
```json
{
  "broadcast_id": "broadcast_1234567890",
  "total_recipients": 15,
  "queued_count": 12,
  "skipped_count": 3,
  "skipped_reasons": {
    "no_phone": 1,
    "opted_out": 1,
    "rate_limited": 1
  },
  "estimated_cost_cents": 948,
  "estimated_delivery_time": "2025-01-01T10:05:00Z",
  "status": "queued"
}
```

**Field Descriptions**:
- `broadcast_id`: Unique ID for tracking broadcast status
- `total_recipients`: Total volunteers targeted
- `queued_count`: Messages successfully queued for delivery
- `skipped_count`: Messages not sent (see skipped_reasons)
- `skipped_reasons`: Breakdown of why messages were skipped
- `estimated_cost_cents`: Total estimated cost ($0.0079 per SMS × queued_count)
- `estimated_delivery_time`: Expected completion time (batch rate: 10 msgs/minute)

**Error Responses**:

**400 Bad Request**:
```json
{
  "detail": "Must provide either recipient_ids or team_id, not both"
}
```

**403 Forbidden**:
```json
{
  "detail": "Organization has exceeded monthly SMS budget ($100.00)"
}
```

**422 Unprocessable Entity**:
```json
{
  "detail": "Maximum 200 recipients per broadcast"
}
```

---

### 3. Get Message History

**Endpoint**: `GET /api/sms/messages`

**Purpose**: Retrieve SMS message history and audit trail (admin analytics, volunteer personal history)

**Authentication**: Required (JWT Bearer token)

**Authorization**:
- Admins: Can view all organization messages
- Volunteers: Can view only their own messages

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID
- `recipient_id` (optional, integer): Filter by recipient (admins only; volunteers auto-filtered to self)
- `message_type` (optional, string): Filter by type (`assignment`, `reminder`, `broadcast`, `system`)
- `status` (optional, string): Filter by status (`queued`, `sent`, `delivered`, `failed`)
- `event_id` (optional, integer): Filter by associated event
- `start_date` (optional, ISO 8601 date): Filter messages after this date
- `end_date` (optional, ISO 8601 date): Filter messages before this date
- `limit` (optional, integer, default: 50, max: 200): Pagination limit
- `offset` (optional, integer, default: 0): Pagination offset

**Response**:

**Success (200 OK)**:
```json
{
  "messages": [
    {
      "id": 12345,
      "recipient_id": 123,
      "recipient_name": "John Smith",
      "phone_number": "+15551234567",
      "message_text": "Sunday Service - Jan 1 at 10:00AM - Role: Usher. Reply YES to confirm",
      "message_type": "assignment",
      "event_id": 456,
      "event_title": "Sunday Service",
      "status": "delivered",
      "cost_cents": 79,
      "is_urgent": false,
      "sent_at": "2025-01-01T09:00:00Z",
      "delivered_at": "2025-01-01T09:00:15Z",
      "created_at": "2025-01-01T08:59:50Z"
    },
    {
      "id": 12344,
      "recipient_id": 123,
      "recipient_name": "John Smith",
      "phone_number": "+15551234567",
      "message_text": "Reminder: Sunday Service tomorrow at 10:00 AM. Role: Usher",
      "message_type": "reminder",
      "event_id": 456,
      "event_title": "Sunday Service",
      "status": "delivered",
      "cost_cents": 79,
      "is_urgent": false,
      "sent_at": "2024-12-31T18:00:00Z",
      "delivered_at": "2024-12-31T18:00:22Z",
      "created_at": "2024-12-31T17:59:55Z"
    }
  ],
  "pagination": {
    "total_count": 127,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

**Error Responses**:

**403 Forbidden** - Volunteer trying to access other volunteers' messages:
```json
{
  "detail": "Access denied: can only view your own messages"
}
```

---

### 4. Get SMS Analytics

**Endpoint**: `GET /api/sms/analytics`

**Purpose**: Usage analytics, delivery statistics, and cost tracking (admin dashboard)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Admin only

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID
- `month` (optional, string, format: YYYY-MM): Month for analytics (default: current month)

**Response**:

**Success (200 OK)**:
```json
{
  "month_year": "2025-01",
  "message_counts": {
    "total_sent": 487,
    "assignment": 245,
    "reminder": 189,
    "broadcast": 43,
    "system": 10
  },
  "delivery_stats": {
    "delivered": 472,
    "failed": 15,
    "delivery_rate": 0.969
  },
  "cost_summary": {
    "total_cost_cents": 3847,
    "total_cost_dollars": 38.47,
    "budget_limit_cents": 10000,
    "budget_limit_dollars": 100.00,
    "budget_utilization": 0.3847,
    "remaining_budget_cents": 6153,
    "remaining_budget_dollars": 61.53
  },
  "alert_status": {
    "alert_threshold_percent": 80,
    "alert_sent_at_80": false,
    "alert_sent_at_100": false,
    "auto_pause_enabled": true
  },
  "performance_metrics": {
    "avg_delivery_time_seconds": 18.5,
    "p95_delivery_time_seconds": 27.3,
    "p99_delivery_time_seconds": 42.1
  },
  "top_recipients": [
    {
      "person_id": 123,
      "name": "John Smith",
      "message_count": 12,
      "cost_cents": 948
    },
    {
      "person_id": 456,
      "name": "Jane Doe",
      "message_count": 11,
      "cost_cents": 869
    }
  ],
  "daily_breakdown": [
    {
      "date": "2025-01-01",
      "message_count": 23,
      "cost_cents": 181,
      "delivery_rate": 0.957
    },
    {
      "date": "2025-01-02",
      "message_count": 19,
      "cost_cents": 150,
      "delivery_rate": 1.0
    }
  ]
}
```

**Field Descriptions**:
- `delivery_rate`: Percentage of messages successfully delivered (delivered / total_sent)
- `budget_utilization`: Percentage of monthly budget used (total_cost / budget_limit)
- `avg_delivery_time_seconds`: Average time from send to delivery
- `p95_delivery_time_seconds`: 95th percentile delivery time (performance target: <30s)
- `top_recipients`: Top 10 volunteers by message volume (identify frequent recipients)

**Error Responses**:

**403 Forbidden**:
```json
{
  "detail": "Admin access required"
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 Bad Request | Validation failure | Invalid phone format, missing required fields, message too long |
| 401 Unauthorized | Authentication failure | Missing/expired JWT token |
| 403 Forbidden | Authorization failure | Volunteer trying admin endpoint, wrong organization |
| 422 Unprocessable Entity | Business logic violation | Unverified phone, opted out user, invalid template |
| 429 Too Many Requests | Rate limit exceeded | 3+ SMS sent to volunteer today |
| 503 Service Unavailable | Temporary unavailability | Quiet hours enforcement, Twilio API downtime |

### Error Response Format

All error responses follow this structure:
```json
{
  "detail": "Human-readable error message",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2025-01-01T10:00:00Z",
  "retry_after": "2025-01-02T00:00:00Z"
}
```

---

## Rate Limiting

### Per-Volunteer Limits
- **Standard Messages**: 3 SMS per volunteer per day
- **Urgent Messages** (`is_urgent=true`): No rate limit
- **Rate Reset**: Daily at midnight UTC
- **Rate Limit Bypass**: Messages within 4 hours of event start time bypass limits

### API Rate Limits
- **Send Individual**: 100 requests/minute per organization
- **Broadcast**: 10 requests/minute per organization
- **Message History**: 60 requests/minute per user
- **Analytics**: 30 requests/minute per organization

---

## Cost Tracking

### Message Costs
- **US/Canada**: $0.0079 per SMS segment (160 chars)
- **International**: $0.04-0.50 per SMS (country-dependent)
- **Long Messages**: Charged per segment (306 chars = 2 segments = $0.0158)

### Budget Enforcement
1. **80% Budget**: Alert sent to admin, no action taken
2. **100% Budget**:
   - **Critical Messages** (assignment, urgent): Continue sending
   - **Non-Critical Messages** (reminder, broadcast): Auto-paused
3. **Budget Reset**: 1st of each month at midnight UTC

---

## Delivery Status Tracking

### Message Status Flow

```
queued → sent → delivered
   ↓       ↓
   ↓   → failed
   ↓
→ failed
```

### Status Definitions

| Status | Description | Twilio Equivalent |
|--------|-------------|-------------------|
| `queued` | Message queued for delivery (Celery task pending) | N/A (pre-Twilio) |
| `sent` | Accepted by Twilio, in transit to carrier | `sent`, `queued` |
| `delivered` | Confirmed delivery to recipient's device | `delivered` |
| `failed` | Permanent delivery failure | `failed` |
| `undelivered` | Temporary failure, retry in progress | `undelivered` |

### Webhook Status Updates

Message status automatically updated via Twilio webhooks (see `webhooks-api.md`). No polling required.

---

## Security

### Authentication
- **JWT Bearer Token**: Required in `Authorization` header
- **Token Format**: `Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...`
- **Token Expiration**: 24 hours

### Authorization
- **Admin Endpoints**: Send SMS, broadcast, analytics
- **Volunteer Endpoints**: Message history (own messages only)

### Multi-Tenancy
- All endpoints require `org_id` query parameter
- Backend verifies user belongs to requested organization
- Database queries filtered by `organization_id` to prevent data leaks

---

## Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| SMS Delivery Time (p95) | <30 seconds | Twilio webhooks |
| API Response Time (p95) | <200ms | Application logs |
| Message Queue Latency | <5 seconds | Celery metrics |
| Delivery Success Rate | >98% | Analytics dashboard |

---

## Implementation Notes

### Message Queue (Celery)
- All SMS sending happens asynchronously via Celery tasks
- API endpoints immediately return 201/202 (message queued)
- Celery workers process queue with retry logic
- Retry schedule: 1 minute, 5 minutes, 15 minutes, 1 hour (exponential backoff)

### Rate Limiting (Redis)
- Redis counters track daily SMS count per volunteer
- Counter key format: `sms_limit:{person_id}:{YYYY-MM-DD}`
- Counter expires after 24 hours (automatic cleanup)
- Check before queueing message (not before sending)

### Cost Calculation
- Twilio returns actual cost in webhook status update
- Initial cost estimate: $0.0079 × (message_length / 160 rounded up)
- Actual cost recorded when webhook received with `price` field

### Quiet Hours Enforcement
- Volunteer timezone stored in `sms_preferences.timezone`
- Quiet hours: 10pm-8am local time
- Non-urgent messages queued for 8am delivery (Celery ETA)
- Urgent messages bypass quiet hours

---

## Testing

### Unit Tests
```python
# tests/unit/test_sms_api.py
def test_send_sms_rate_limit_enforced():
    """Test that rate limiting prevents 4th SMS in same day."""
    # Send 3 SMS successfully
    # 4th SMS should return 429 Too Many Requests

def test_send_sms_quiet_hours_queued():
    """Test that non-urgent SMS queued during quiet hours."""
    # Send message at 11pm volunteer local time
    # Response should indicate queued for 8am
```

### Integration Tests
```python
# tests/integration/test_sms_api.py
def test_send_sms_via_template(client, auth_headers):
    """Test sending SMS using message template."""
    response = client.post(
        "/api/sms/send?org_id=test_org",
        json={
            "recipient_id": 123,
            "template_id": 1,
            "event_id": 456,
            "message_type": "assignment"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert "twilio_message_sid" in response.json()
```

### E2E Tests
```python
# tests/e2e/test_sms_workflows.py
def test_broadcast_message_to_team(page: Page):
    """Test admin sending broadcast to entire team."""
    page.goto("http://localhost:8000/app/admin")
    page.locator('[data-i18n="admin.tabs.sms"]').click()
    page.locator('#broadcast-team-select').select_option("Ushers")
    page.locator('#broadcast-message').fill("Team meeting today at 7pm")
    page.locator('[data-i18n="sms.send_broadcast"]').click()
    expect(page.locator('.success-message')).to_contain_text("Broadcast queued")
```

---

## Related Documentation

- **Data Model**: `../data-model.md` - Database schemas for sms_messages, sms_preferences
- **Preferences API**: `preferences-api.md` - Phone verification and notification settings
- **Webhooks API**: `webhooks-api.md` - Twilio delivery status and incoming replies
- **Templates API**: `templates-api.md` - Message template management
- **Quick Start**: `../quickstart.md` - 10-minute Twilio integration setup
- **Research**: `../research.md` - Technology decision analysis (SMS gateway, queue, rate limiting)

---

**Last Updated**: 2025-10-23
**API Version**: v1
**Feature**: 019 - SMS Notification System
