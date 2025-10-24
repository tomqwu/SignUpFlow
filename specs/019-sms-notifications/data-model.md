# Data Model: SMS Notification System

**Feature**: 019 - SMS Notifications | **Phase**: 1 - Design | **Date**: 2025-10-23

This document defines database schemas for SMS notification functionality in SignUpFlow.

---

## Database Schema

### Table: `sms_preferences`

Stores volunteer SMS notification preferences and phone verification status.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | INTEGER | PRIMARY KEY, FOREIGN KEY → people.id | Volunteer owning preferences |
| `phone_number` | VARCHAR(20) | NOT NULL, UNIQUE | E.164 format: +12345678900 |
| `verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | Phone verified via SMS code |
| `notification_types` | JSON | NOT NULL, DEFAULT [] | Array: ['assignment', 'reminder', 'change', 'cancellation'] |
| `opt_in_date` | TIMESTAMP | NULL | When user completed opt-in |
| `opt_out_date` | TIMESTAMP | NULL | When user opted out (STOP reply) |
| `language` | VARCHAR(5) | NOT NULL, DEFAULT 'en' | Message language: 'en' or 'es' |
| `timezone` | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | Volunteer timezone for quiet hours |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update |

**Indexes**:
- PRIMARY KEY (`person_id`)
- UNIQUE (`phone_number`) WHERE `verified` = TRUE
- INDEX (`verified`, `opt_out_date`) for active users query

**Relationships**:
- `person_id` → `people.id` (ONE-TO-ONE) - Each person has one SMS preference

**Validation Rules**:
- `phone_number` must match E.164 format regex: `^\+[1-9]\d{1,14}$`
- `notification_types` array values restricted to: 'assignment', 'reminder', 'change', 'cancellation'
- `language` restricted to: 'en', 'es'
- `opt_out_date` must be NULL if `verified` = TRUE (cannot be opted-in and opted-out simultaneously)

**Example Record**:
```json
{
  "person_id": 123,
  "phone_number": "+14155551234",
  "verified": true,
  "notification_types": ["assignment", "reminder"],
  "opt_in_date": "2025-10-23T14:30:00Z",
  "opt_out_date": null,
  "language": "en",
  "timezone": "America/Los_Angeles",
  "created_at": "2025-10-23T14:25:00Z",
  "updated_at": "2025-10-23T14:30:00Z"
}
```

---

### Table: `sms_messages`

Log of all sent SMS messages for audit trail and delivery tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Message ID |
| `organization_id` | INTEGER | NOT NULL, FOREIGN KEY → organizations.id | Organization sending message |
| `recipient_id` | INTEGER | NOT NULL, FOREIGN KEY → people.id | Volunteer receiving message |
| `phone_number` | VARCHAR(20) | NOT NULL | Recipient phone (denormalized for audit) |
| `message_text` | TEXT | NOT NULL | Message content sent |
| `message_type` | VARCHAR(20) | NOT NULL | 'assignment', 'reminder', 'broadcast', 'system', 'verification' |
| `event_id` | INTEGER | NULL, FOREIGN KEY → events.id | Related event (if applicable) |
| `template_id` | INTEGER | NULL, FOREIGN KEY → sms_templates.id | Template used (if applicable) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'queued' | 'queued', 'sent', 'delivered', 'failed', 'undelivered' |
| `twilio_message_sid` | VARCHAR(34) | NULL, UNIQUE | Twilio message ID (SM...) |
| `cost_cents` | INTEGER | NOT NULL, DEFAULT 0 | Cost in cents (79 = $0.0079) |
| `error_message` | TEXT | NULL | Error details if failed |
| `is_urgent` | BOOLEAN | NOT NULL, DEFAULT FALSE | Bypasses rate limit and quiet hours |
| `sent_at` | TIMESTAMP | NULL | When message sent to Twilio |
| `delivered_at` | TIMESTAMP | NULL | When message delivered (Twilio webhook) |
| `failed_at` | TIMESTAMP | NULL | When delivery failed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation (queue time) |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX (`organization_id`, `created_at`) for organization message history
- INDEX (`recipient_id`, `created_at`) for volunteer message history
- INDEX (`status`, `created_at`) for retry queries (failed messages)
- INDEX (`twilio_message_sid`) for webhook lookups
- INDEX (`message_type`, `created_at`) for analytics queries

**Relationships**:
- `organization_id` → `organizations.id` (MANY-TO-ONE)
- `recipient_id` → `people.id` (MANY-TO-ONE)
- `event_id` → `events.id` (MANY-TO-ONE) - Optional
- `template_id` → `sms_templates.id` (MANY-TO-ONE) - Optional

**Validation Rules**:
- `message_type` restricted to: 'assignment', 'reminder', 'broadcast', 'system', 'verification'
- `status` restricted to: 'queued', 'sent', 'delivered', 'failed', 'undelivered'
- `message_text` max length: 1600 characters (10 SMS segments)
- `cost_cents` must be >= 0
- If `status` = 'delivered', `delivered_at` must not be NULL
- If `status` = 'failed', `error_message` should not be NULL

**Example Record**:
```json
{
  "id": 1001,
  "organization_id": 5,
  "recipient_id": 123,
  "phone_number": "+14155551234",
  "message_text": "Sunday Service - Nov 15 at 10:00 AM - Role: Greeter. Reply YES to confirm, NO to decline",
  "message_type": "assignment",
  "event_id": 789,
  "template_id": 1,
  "status": "delivered",
  "twilio_message_sid": "SM1234567890abcdef1234567890abcdef",
  "cost_cents": 79,
  "error_message": null,
  "is_urgent": false,
  "sent_at": "2025-10-23T14:35:00Z",
  "delivered_at": "2025-10-23T14:35:03Z",
  "failed_at": null,
  "created_at": "2025-10-23T14:35:00Z"
}
```

---

### Table: `sms_templates`

Reusable message templates with variable substitution.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Template ID |
| `organization_id` | INTEGER | NOT NULL, FOREIGN KEY → organizations.id | Organization owning template |
| `name` | VARCHAR(100) | NOT NULL | Template name (display) |
| `template_text` | TEXT | NOT NULL | Jinja2 template with variables |
| `message_type` | VARCHAR(20) | NOT NULL | 'assignment', 'reminder', 'cancellation', 'broadcast' |
| `character_count` | INTEGER | NOT NULL | Approximate length (before variable substitution) |
| `translations` | JSON | NOT NULL, DEFAULT {} | {'en': '...', 'es': '...'} |
| `is_system` | BOOLEAN | NOT NULL, DEFAULT FALSE | System template (cannot be deleted) |
| `usage_count` | INTEGER | NOT NULL, DEFAULT 0 | Times template used |
| `created_by` | INTEGER | NOT NULL, FOREIGN KEY → people.id | Admin who created template |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Template creation |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX (`organization_id`, `message_type`) for template selection
- INDEX (`is_system`) for system template queries

**Relationships**:
- `organization_id` → `organizations.id` (MANY-TO-ONE)
- `created_by` → `people.id` (MANY-TO-ONE)

**Validation Rules**:
- `message_type` restricted to: 'assignment', 'reminder', 'cancellation', 'broadcast'
- `template_text` must contain valid Jinja2 syntax
- `translations` must be valid JSON object with language codes as keys
- `character_count` should be <= 160 (recommended single SMS segment)
- System templates (`is_system` = TRUE) cannot be deleted

**Example Record**:
```json
{
  "id": 1,
  "organization_id": 5,
  "name": "Assignment Notification",
  "template_text": "{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline",
  "message_type": "assignment",
  "character_count": 85,
  "translations": {
    "en": "{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline",
    "es": "{{event_name}} - {{date}} a las {{time}} - Rol: {{role}}. Responde SÍ para confirmar, NO para declinar"
  },
  "is_system": true,
  "usage_count": 234,
  "created_by": 1,
  "created_at": "2025-10-01T00:00:00Z",
  "updated_at": "2025-10-23T14:00:00Z"
}
```

---

### Table: `sms_usage`

Monthly SMS usage tracking and budget management per organization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `organization_id` | INTEGER | PRIMARY KEY, FOREIGN KEY → organizations.id | Organization ID |
| `month_year` | VARCHAR(7) | PRIMARY KEY | Month: '2025-10' |
| `assignment_count` | INTEGER | NOT NULL, DEFAULT 0 | Assignment notifications sent |
| `reminder_count` | INTEGER | NOT NULL, DEFAULT 0 | Reminder notifications sent |
| `broadcast_count` | INTEGER | NOT NULL, DEFAULT 0 | Broadcast messages sent |
| `system_count` | INTEGER | NOT NULL, DEFAULT 0 | System messages (verification, opt-in) |
| `total_cost_cents` | INTEGER | NOT NULL, DEFAULT 0 | Total cost in cents |
| `budget_limit_cents` | INTEGER | NOT NULL, DEFAULT 10000 | Monthly budget: $100 default |
| `alert_threshold_percent` | INTEGER | NOT NULL, DEFAULT 80 | Alert when usage >= 80% |
| `alert_sent_at_80` | BOOLEAN | NOT NULL, DEFAULT FALSE | 80% alert sent this month |
| `alert_sent_at_100` | BOOLEAN | NOT NULL, DEFAULT FALSE | 100% alert sent this month |
| `auto_pause_enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Auto-pause non-critical at 100% |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update |

**Indexes**:
- PRIMARY KEY (`organization_id`, `month_year`)
- INDEX (`month_year`) for cross-organization analytics

**Relationships**:
- `organization_id` → `organizations.id` (MANY-TO-ONE)

**Validation Rules**:
- `month_year` format: YYYY-MM (e.g., '2025-10')
- All count fields must be >= 0
- `total_cost_cents` must be >= 0
- `budget_limit_cents` must be > 0
- `alert_threshold_percent` must be between 1 and 100

**Computed Fields** (application-level):
- `utilization_percent` = (`total_cost_cents` / `budget_limit_cents`) * 100
- `remaining_budget_cents` = `budget_limit_cents` - `total_cost_cents`
- `projected_overage_date` = Based on current usage rate

**Example Record**:
```json
{
  "organization_id": 5,
  "month_year": "2025-10",
  "assignment_count": 150,
  "reminder_count": 120,
  "broadcast_count": 10,
  "system_count": 25,
  "total_cost_cents": 2400,
  "budget_limit_cents": 10000,
  "alert_threshold_percent": 80,
  "alert_sent_at_80": false,
  "alert_sent_at_100": false,
  "auto_pause_enabled": true,
  "created_at": "2025-10-01T00:00:00Z",
  "updated_at": "2025-10-23T14:40:00Z"
}
```

---

### Table: `sms_verification_codes`

Temporary storage for phone verification codes (10-minute expiration).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | INTEGER | PRIMARY KEY, FOREIGN KEY → people.id | Volunteer verifying phone |
| `phone_number` | VARCHAR(20) | NOT NULL | Phone being verified |
| `verification_code` | INTEGER | NOT NULL | 6-digit code: 100000-999999 |
| `attempts` | INTEGER | NOT NULL, DEFAULT 0 | Verification attempts (max 3) |
| `expires_at` | TIMESTAMP | NOT NULL | Expiration time (10 minutes) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Code generation time |

**Indexes**:
- PRIMARY KEY (`person_id`)
- INDEX (`expires_at`) for cleanup of expired codes

**Relationships**:
- `person_id` → `people.id` (ONE-TO-ONE temporary)

**Validation Rules**:
- `verification_code` must be 6-digit integer: 100000-999999
- `attempts` must be 0-3
- `expires_at` must be > `created_at`
- Record automatically deleted after successful verification or after expiration

**Cleanup**: Expired codes deleted via scheduled job (every 1 hour: DELETE WHERE `expires_at` < NOW())

**Example Record**:
```json
{
  "person_id": 123,
  "phone_number": "+14155551234",
  "verification_code": 482951,
  "attempts": 1,
  "expires_at": "2025-10-23T14:45:00Z",
  "created_at": "2025-10-23T14:35:00Z"
}
```

---

### Table: `sms_replies`

Log of incoming SMS replies for audit trail and analytics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Reply ID |
| `person_id` | INTEGER | NOT NULL, FOREIGN KEY → people.id | Volunteer who replied |
| `phone_number` | VARCHAR(20) | NOT NULL | Phone that sent reply |
| `message_text` | TEXT | NOT NULL | Reply content received |
| `reply_type` | VARCHAR(20) | NOT NULL | 'yes', 'no', 'stop', 'start', 'help', 'unknown' |
| `original_message_id` | INTEGER | NULL, FOREIGN KEY → sms_messages.id | Message being replied to |
| `event_id` | INTEGER | NULL, FOREIGN KEY → events.id | Related event (if assignment reply) |
| `action_taken` | VARCHAR(50) | NOT NULL | 'confirmed', 'declined', 'opted_out', 'help_sent', etc. |
| `twilio_message_sid` | VARCHAR(34) | NULL, UNIQUE | Twilio incoming message ID |
| `processed_at` | TIMESTAMP | NULL | When reply was processed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When reply received |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX (`person_id`, `created_at`) for volunteer reply history
- INDEX (`reply_type`, `created_at`) for analytics queries
- INDEX (`twilio_message_sid`) for webhook lookups

**Relationships**:
- `person_id` → `people.id` (MANY-TO-ONE)
- `original_message_id` → `sms_messages.id` (MANY-TO-ONE) - Optional
- `event_id` → `events.id` (MANY-TO-ONE) - Optional

**Validation Rules**:
- `reply_type` restricted to: 'yes', 'no', 'stop', 'start', 'help', 'unknown'
- `action_taken` examples: 'confirmed', 'declined', 'opted_out', 'opted_in', 'help_sent', 'unrecognized'

**Example Record**:
```json
{
  "id": 501,
  "person_id": 123,
  "phone_number": "+14155551234",
  "message_text": "YES",
  "reply_type": "yes",
  "original_message_id": 1001,
  "event_id": 789,
  "action_taken": "confirmed",
  "twilio_message_sid": "SM9876543210fedcba9876543210fedcba",
  "processed_at": "2025-10-23T14:36:00Z",
  "created_at": "2025-10-23T14:36:00Z"
}
```

---

## Entity Relationships

```
┌──────────────┐
│ organizations│
└──────┬───────┘
       │
       │ 1:N
       │
┌──────▼───────┐       ┌─────────────────┐
│ people       │◄──────│ sms_preferences │ (1:1)
└──────┬───────┘       └─────────────────┘
       │
       │ 1:N
       │
┌──────▼───────┐       ┌─────────────────┐
│ events       │       │ sms_messages    │
└──────────────┘       └─────────────────┘
       │                      │
       │ 1:N                  │ N:1
       │                      │
       └──────────────────────┘

┌──────────────┐
│ organizations│
└──────┬───────┘
       │
       │ 1:N
       │
┌──────▼───────┐       ┌─────────────────┐
│sms_templates │       │ sms_usage       │ (1:1 per month)
└──────────────┘       └─────────────────┘

┌──────────────┐       ┌─────────────────┐
│ people       │◄──────│ sms_verification│ (1:1 temporary)
└──────────────┘       │ _codes          │
                       └─────────────────┘

┌──────────────┐       ┌─────────────────┐
│ people       │◄──────│ sms_replies     │ (1:N)
└──────────────┘       └─────────────────┘
       │                      │
       │                      │ N:1
       │                      │
       ▼                      ▼
┌──────────────┐       ┌─────────────────┐
│ events       │       │ sms_messages    │
└──────────────┘       └─────────────────┘
```

---

## Migration Strategy

### Initial Migration

```sql
-- Add sms_preferences table
CREATE TABLE sms_preferences (
    person_id INTEGER PRIMARY KEY REFERENCES people(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    notification_types JSON NOT NULL DEFAULT '[]',
    opt_in_date TIMESTAMP,
    opt_out_date TIMESTAMP,
    language VARCHAR(5) NOT NULL DEFAULT 'en',
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_verified_phone UNIQUE (phone_number) WHERE verified = TRUE,
    CONSTRAINT valid_phone_format CHECK (phone_number ~ '^\+[1-9]\d{1,14}$'),
    CONSTRAINT valid_language CHECK (language IN ('en', 'es'))
);

CREATE INDEX idx_sms_preferences_verified ON sms_preferences(verified, opt_out_date);

-- Add sms_messages table
CREATE TABLE sms_messages (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('assignment', 'reminder', 'broadcast', 'system', 'verification')),
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    template_id INTEGER REFERENCES sms_templates(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'delivered', 'failed', 'undelivered')),
    twilio_message_sid VARCHAR(34) UNIQUE,
    cost_cents INTEGER NOT NULL DEFAULT 0 CHECK (cost_cents >= 0),
    error_message TEXT,
    is_urgent BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sms_messages_org_created ON sms_messages(organization_id, created_at);
CREATE INDEX idx_sms_messages_recipient_created ON sms_messages(recipient_id, created_at);
CREATE INDEX idx_sms_messages_status_created ON sms_messages(status, created_at);
CREATE INDEX idx_sms_messages_twilio_sid ON sms_messages(twilio_message_sid);
CREATE INDEX idx_sms_messages_type_created ON sms_messages(message_type, created_at);

-- Add sms_templates table
CREATE TABLE sms_templates (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    template_text TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('assignment', 'reminder', 'cancellation', 'broadcast')),
    character_count INTEGER NOT NULL,
    translations JSON NOT NULL DEFAULT '{}',
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sms_templates_org_type ON sms_templates(organization_id, message_type);
CREATE INDEX idx_sms_templates_system ON sms_templates(is_system);

-- Add sms_usage table
CREATE TABLE sms_usage (
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    month_year VARCHAR(7) NOT NULL CHECK (month_year ~ '^\d{4}-\d{2}$'),
    assignment_count INTEGER NOT NULL DEFAULT 0 CHECK (assignment_count >= 0),
    reminder_count INTEGER NOT NULL DEFAULT 0 CHECK (reminder_count >= 0),
    broadcast_count INTEGER NOT NULL DEFAULT 0 CHECK (broadcast_count >= 0),
    system_count INTEGER NOT NULL DEFAULT 0 CHECK (system_count >= 0),
    total_cost_cents INTEGER NOT NULL DEFAULT 0 CHECK (total_cost_cents >= 0),
    budget_limit_cents INTEGER NOT NULL DEFAULT 10000 CHECK (budget_limit_cents > 0),
    alert_threshold_percent INTEGER NOT NULL DEFAULT 80 CHECK (alert_threshold_percent BETWEEN 1 AND 100),
    alert_sent_at_80 BOOLEAN NOT NULL DEFAULT FALSE,
    alert_sent_at_100 BOOLEAN NOT NULL DEFAULT FALSE,
    auto_pause_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (organization_id, month_year)
);

CREATE INDEX idx_sms_usage_month ON sms_usage(month_year);

-- Add sms_verification_codes table
CREATE TABLE sms_verification_codes (
    person_id INTEGER PRIMARY KEY REFERENCES people(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    verification_code INTEGER NOT NULL CHECK (verification_code BETWEEN 100000 AND 999999),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts BETWEEN 0 AND 3),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sms_verification_expires ON sms_verification_codes(expires_at);

-- Add sms_replies table
CREATE TABLE sms_replies (
    id SERIAL PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    message_text TEXT NOT NULL,
    reply_type VARCHAR(20) NOT NULL CHECK (reply_type IN ('yes', 'no', 'stop', 'start', 'help', 'unknown')),
    original_message_id INTEGER REFERENCES sms_messages(id) ON DELETE SET NULL,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    action_taken VARCHAR(50) NOT NULL,
    twilio_message_sid VARCHAR(34) UNIQUE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sms_replies_person_created ON sms_replies(person_id, created_at);
CREATE INDEX idx_sms_replies_type_created ON sms_replies(reply_type, created_at);
CREATE INDEX idx_sms_replies_twilio_sid ON sms_replies(twilio_message_sid);
```

### Seed Data: System Templates

```sql
INSERT INTO sms_templates (organization_id, name, template_text, message_type, character_count, translations, is_system, created_by) VALUES
(NULL, 'Assignment Notification', '{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline', 'assignment', 85, '{"en": "{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline", "es": "{{event_name}} - {{date}} a las {{time}} - Rol: {{role}}. Responde SÍ para confirmar, NO para declinar"}', TRUE, 1),
(NULL, '24-Hour Reminder', 'Reminder: {{event_name}} tomorrow at {{time}}. {% if location %}Location: {{location}}{% endif %} See you there!', 'reminder', 90, '{"en": "Reminder: {{event_name}} tomorrow at {{time}}. {% if location %}Location: {{location}}{% endif %} See you there!", "es": "Recordatorio: {{event_name}} mañana a las {{time}}. {% if location %}Ubicación: {{location}}{% endif %} ¡Nos vemos!"}', TRUE, 1),
(NULL, 'Event Cancellation', 'CANCELLED: {{event_name}} on {{date}} at {{time}} has been cancelled. Apologies for any inconvenience.', 'cancellation', 110, '{"en": "CANCELLED: {{event_name}} on {{date}} at {{time}} has been cancelled. Apologies for any inconvenience.", "es": "CANCELADO: {{event_name}} el {{date}} a las {{time}} ha sido cancelado. Disculpe las molestias."}', TRUE, 1);
```

---

## Storage Estimates

### Record Sizes

| Table | Columns | Avg Size | Notes |
|-------|---------|----------|-------|
| `sms_preferences` | 10 | 200 bytes | JSON notification_types ~50 bytes |
| `sms_messages` | 17 | 500 bytes | Message text ~150 bytes avg |
| `sms_templates` | 12 | 600 bytes | Template text + translations ~400 bytes |
| `sms_usage` | 14 | 150 bytes | Mostly integers |
| `sms_verification_codes` | 6 | 100 bytes | Temporary, auto-deleted |
| `sms_replies` | 11 | 300 bytes | Reply text ~50 bytes avg |

### Volume Projections (per organization, per month)

| Table | Records | Total Size | Growth Rate |
|-------|---------|------------|-------------|
| `sms_preferences` | 100 | 20 KB | Low (one-time setup) |
| `sms_messages` | 200 | 100 KB | 200/month |
| `sms_templates` | 10 | 6 KB | Low (occasional additions) |
| `sms_usage` | 1 | 150 bytes | 12/year |
| `sms_verification_codes` | 1-5 | 500 bytes | Temporary (auto-deleted) |
| `sms_replies` | 50 | 15 KB | 50/month |

**Total Storage**: ~150 KB/month/organization

**10 Organizations, 1 Year**: 18 MB (very manageable)

---

**Next**: Generate API contracts in `contracts/` directory (sms-api.md, preferences-api.md, webhooks-api.md, templates-api.md)
