# Data Model: Monitoring & Observability Platform

**Feature**: 005-monitoring-observability
**Purpose**: Define entities for performance metrics, alert rules, status page incidents, and monitoring integrations

---

## Entity Overview

| Entity | Storage | Purpose | Retention |
|--------|---------|---------|-----------|
| **PerformanceMetric** | PostgreSQL | Response times, DB query performance, memory usage | 90 days |
| **AlertRule** | PostgreSQL | Configurable thresholds for automated alerts | Permanent (until deleted) |
| **Incident** | PostgreSQL | Status page incidents and service disruptions | Permanent (until deleted) |
| **ErrorEvent** | Sentry Cloud | Exception tracking, stack traces, error context | 90 days (Sentry retention) |
| **LogEntry** | Papertrail Cloud | Application logs, request logs, system logs | 7 days (free tier) |

---

## 1. PerformanceMetric (PostgreSQL)

### Purpose
Store timeseries performance data (response times, database query counts, memory usage) for metrics dashboard and alert rule evaluation.

### Schema

```sql
CREATE TABLE performance_metrics (
    id VARCHAR(50) PRIMARY KEY,                      -- metric_20251020_143052_abc123
    org_id VARCHAR(50) NOT NULL,                     -- Multi-tenant isolation
    metric_type VARCHAR(50) NOT NULL,                -- response_time, db_query_count, memory_usage, error_rate
    value DECIMAL(10, 2) NOT NULL,                   -- Metric value (e.g., 152.34 ms)
    unit VARCHAR(20) NOT NULL,                       -- ms, count, MB, percentage
    metadata JSONB,                                  -- {endpoint: "/api/events", status_code: 200, p95: 200.5}
    timestamp TIMESTAMPTZ NOT NULL,                  -- When metric was recorded
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE INDEX idx_perf_metrics_org_type_ts ON performance_metrics(org_id, metric_type, timestamp DESC);
CREATE INDEX idx_perf_metrics_timestamp ON performance_metrics(timestamp DESC);
```

### Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | VARCHAR(50) | Yes | Unique identifier | `metric_20251020_143052_abc123` |
| `org_id` | VARCHAR(50) | Yes | Organization ID (multi-tenant isolation) | `org_church_12345` |
| `metric_type` | VARCHAR(50) | Yes | Metric type | `response_time`, `db_query_count`, `memory_usage`, `error_rate` |
| `value` | DECIMAL(10, 2) | Yes | Metric value | `152.34` (response time in ms) |
| `unit` | VARCHAR(20) | Yes | Unit of measurement | `ms`, `count`, `MB`, `percentage` |
| `metadata` | JSONB | No | Additional context | `{"endpoint": "/api/events", "status_code": 200, "p95": 200.5}` |
| `timestamp` | TIMESTAMPTZ | Yes | When metric recorded | `2025-10-20T14:30:52Z` |
| `created_at` | TIMESTAMPTZ | Yes | Record creation time | `2025-10-20T14:30:52Z` |

### Metric Types

| Type | Unit | Description | Threshold Example |
|------|------|-------------|-------------------|
| `response_time` | ms | API endpoint response time (P95) | Alert if P95 > 1000ms |
| `db_query_count` | count | Number of DB queries per request | Alert if count > 50 queries |
| `memory_usage` | MB | Server memory usage | Alert if > 1500MB (80% of 2GB) |
| `error_rate` | percentage | Percentage of requests returning 5xx errors | Alert if > 1% |
| `cpu_usage` | percentage | Server CPU usage | Alert if > 80% |

### Retention Policy
- **Duration**: 90 days
- **Cleanup**: Scheduled job deletes metrics older than 90 days (daily cron job)
- **Aggregation**: Optionally aggregate to hourly averages after 7 days to reduce storage

### Example Records

```json
{
  "id": "metric_20251020_143052_abc123",
  "org_id": "org_church_12345",
  "metric_type": "response_time",
  "value": 152.34,
  "unit": "ms",
  "metadata": {
    "endpoint": "/api/events",
    "method": "GET",
    "status_code": 200,
    "p50": 85.2,
    "p95": 152.34,
    "p99": 320.1
  },
  "timestamp": "2025-10-20T14:30:52Z",
  "created_at": "2025-10-20T14:30:52Z"
}
```

```json
{
  "id": "metric_20251020_143055_def456",
  "org_id": "org_church_12345",
  "metric_type": "error_rate",
  "value": 2.5,
  "unit": "percentage",
  "metadata": {
    "total_requests": 1000,
    "error_count": 25,
    "error_types": ["500", "503"]
  },
  "timestamp": "2025-10-20T14:30:55Z",
  "created_at": "2025-10-20T14:30:55Z"
}
```

---

## 2. AlertRule (PostgreSQL)

### Purpose
Store configurable alert rules with thresholds, notification channels, and evaluation intervals for automated alerting system.

### Schema

```sql
CREATE TABLE alert_rules (
    id VARCHAR(50) PRIMARY KEY,                      -- alert_rule_abc123
    org_id VARCHAR(50) NOT NULL,                     -- Multi-tenant isolation
    name VARCHAR(100) NOT NULL,                      -- "High Error Rate Alert"
    description TEXT,                                -- "Alert when error rate exceeds 1%"
    metric_type VARCHAR(50) NOT NULL,                -- response_time, error_rate, memory_usage
    threshold_value DECIMAL(10, 2) NOT NULL,         -- 1000 (ms), 1.0 (percentage), 1500 (MB)
    threshold_operator VARCHAR(10) NOT NULL,         -- gt (>), lt (<), gte (>=), lte (<=), eq (=)
    evaluation_interval_minutes INT NOT NULL,        -- 5 (evaluate every 5 minutes)
    notification_channels JSONB NOT NULL,            -- ["slack", "email"]
    notification_config JSONB NOT NULL,              -- {slack_webhook_url: "...", email_recipients: [...]}
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    snoozed_until TIMESTAMPTZ,                       -- If snoozed, don't evaluate until this time
    last_triggered_at TIMESTAMPTZ,                   -- Last time alert was sent
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE INDEX idx_alert_rules_org_enabled ON alert_rules(org_id, enabled);
CREATE INDEX idx_alert_rules_snoozed ON alert_rules(snoozed_until) WHERE snoozed_until IS NOT NULL;
```

### Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | VARCHAR(50) | Yes | Unique identifier | `alert_rule_abc123` |
| `org_id` | VARCHAR(50) | Yes | Organization ID | `org_church_12345` |
| `name` | VARCHAR(100) | Yes | Alert rule name | `"High Error Rate Alert"` |
| `description` | TEXT | No | Rule description | `"Alert when error rate exceeds 1%"` |
| `metric_type` | VARCHAR(50) | Yes | Metric to monitor | `response_time`, `error_rate`, `memory_usage` |
| `threshold_value` | DECIMAL(10, 2) | Yes | Threshold value | `1000` (ms), `1.0` (percentage) |
| `threshold_operator` | VARCHAR(10) | Yes | Comparison operator | `gt` (>), `lt` (<), `gte` (>=), `lte` (<=), `eq` (=) |
| `evaluation_interval_minutes` | INT | Yes | How often to evaluate | `5` (every 5 minutes) |
| `notification_channels` | JSONB | Yes | Where to send alerts | `["slack", "email"]` |
| `notification_config` | JSONB | Yes | Channel configuration | `{slack_webhook_url: "...", email_recipients: [...]}` |
| `enabled` | BOOLEAN | Yes | Is rule active | `true`, `false` |
| `snoozed_until` | TIMESTAMPTZ | No | Snooze until this time | `2025-10-20T15:30:00Z` |
| `last_triggered_at` | TIMESTAMPTZ | No | Last alert time | `2025-10-20T14:25:00Z` |

### Threshold Operators

| Operator | SQL | Description | Example Use Case |
|----------|-----|-------------|------------------|
| `gt` | `>` | Greater than | Alert if response time > 1000ms |
| `gte` | `>=` | Greater than or equal | Alert if error rate >= 1% |
| `lt` | `<` | Less than | Alert if uptime < 99% |
| `lte` | `<=` | Less than or equal | Alert if memory usage <= 100MB (too low) |
| `eq` | `=` | Equal to | Alert if exact value match |

### Notification Channels

| Channel | Configuration | Description |
|---------|---------------|-------------|
| `slack` | `{slack_webhook_url: "https://hooks.slack.com/..."}` | Slack Incoming Webhook |
| `email` | `{email_recipients: ["admin@example.com", "ops@example.com"]}` | Email via SMTP |

### Rate Limiting
- **Max Alerts per Hour**: 10 alerts per rule to prevent spam
- **Cooldown**: 15 minutes minimum between alerts for same rule
- **Snooze**: Admin can snooze rule for 1 hour via API

### Example Record

```json
{
  "id": "alert_rule_abc123",
  "org_id": "org_church_12345",
  "name": "High Error Rate Alert",
  "description": "Alert when error rate exceeds 1% over 5-minute window",
  "metric_type": "error_rate",
  "threshold_value": 1.0,
  "threshold_operator": "gt",
  "evaluation_interval_minutes": 5,
  "notification_channels": ["slack", "email"],
  "notification_config": {
    "slack_webhook_url": "https://hooks.slack.com/services/T00/B00/XXXX",
    "email_recipients": ["admin@church.com", "ops@church.com"]
  },
  "enabled": true,
  "snoozed_until": null,
  "last_triggered_at": "2025-10-20T14:25:00Z",
  "created_at": "2025-10-15T10:00:00Z",
  "updated_at": "2025-10-20T14:25:00Z"
}
```

---

## 3. Incident (PostgreSQL)

### Purpose
Store status page incidents for public/private status pages showing service disruptions, maintenance windows, and incident history.

### Schema

```sql
CREATE TABLE incidents (
    id VARCHAR(50) PRIMARY KEY,                      -- incident_20251020_143052_abc123
    org_id VARCHAR(50),                              -- Optional: NULL for global incidents, org_id for private incidents
    title VARCHAR(200) NOT NULL,                     -- "Database Performance Degradation"
    description TEXT NOT NULL,                       -- Detailed incident description
    status VARCHAR(20) NOT NULL,                     -- investigating, identified, monitoring, resolved
    severity VARCHAR(20) NOT NULL,                   -- critical, major, minor, maintenance
    affected_services JSONB NOT NULL,                -- ["api", "web_app", "email_notifications"]
    started_at TIMESTAMPTZ NOT NULL,                 -- When incident started
    resolved_at TIMESTAMPTZ,                         -- When incident resolved (NULL if ongoing)
    updates JSONB NOT NULL DEFAULT '[]',             -- [{timestamp: "...", message: "..."}]
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE INDEX idx_incidents_org_status ON incidents(org_id, status);
CREATE INDEX idx_incidents_started_at ON incidents(started_at DESC);
CREATE INDEX idx_incidents_severity ON incidents(severity);
```

### Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | VARCHAR(50) | Yes | Unique identifier | `incident_20251020_143052_abc123` |
| `org_id` | VARCHAR(50) | No | Organization ID (NULL for global incidents) | `org_church_12345` or `NULL` |
| `title` | VARCHAR(200) | Yes | Incident title | `"Database Performance Degradation"` |
| `description` | TEXT | Yes | Detailed description | `"Database queries running slower than normal..."` |
| `status` | VARCHAR(20) | Yes | Incident status | `investigating`, `identified`, `monitoring`, `resolved` |
| `severity` | VARCHAR(20) | Yes | Incident severity | `critical`, `major`, `minor`, `maintenance` |
| `affected_services` | JSONB | Yes | Affected services | `["api", "web_app", "email_notifications"]` |
| `started_at` | TIMESTAMPTZ | Yes | Incident start time | `2025-10-20T14:30:00Z` |
| `resolved_at` | TIMESTAMPTZ | No | Incident resolution time | `2025-10-20T15:45:00Z` or `NULL` |
| `updates` | JSONB | Yes | Timeline of updates | `[{timestamp: "...", message: "..."}]` |

### Incident Statuses

| Status | Description | Example |
|--------|-------------|---------|
| `investigating` | Incident reported, investigating cause | "Investigating database slowdown" |
| `identified` | Root cause identified, working on fix | "Identified slow query causing issue" |
| `monitoring` | Fix deployed, monitoring for stability | "Fix deployed, monitoring performance" |
| `resolved` | Incident fully resolved | "Database performance restored to normal" |

### Severity Levels

| Severity | Description | Example |
|----------|-------------|---------|
| `critical` | Complete service outage | "API completely down" |
| `major` | Significant degradation | "50% of API requests timing out" |
| `minor` | Limited impact | "Email notifications delayed by 5 minutes" |
| `maintenance` | Scheduled maintenance | "Database maintenance window" |

### Example Record

```json
{
  "id": "incident_20251020_143052_abc123",
  "org_id": null,
  "title": "Database Performance Degradation",
  "description": "Database queries are running 3x slower than normal, affecting API response times across all endpoints.",
  "status": "resolved",
  "severity": "major",
  "affected_services": ["api", "web_app"],
  "started_at": "2025-10-20T14:30:00Z",
  "resolved_at": "2025-10-20T15:45:00Z",
  "updates": [
    {
      "timestamp": "2025-10-20T14:30:00Z",
      "message": "Investigating reports of slow API response times."
    },
    {
      "timestamp": "2025-10-20T14:45:00Z",
      "message": "Identified slow query causing database contention. Deploying optimized index."
    },
    {
      "timestamp": "2025-10-20T15:00:00Z",
      "message": "Index deployed. Monitoring performance metrics."
    },
    {
      "timestamp": "2025-10-20T15:45:00Z",
      "message": "Database performance restored to normal. Incident resolved."
    }
  ],
  "created_at": "2025-10-20T14:30:00Z",
  "updated_at": "2025-10-20T15:45:00Z"
}
```

---

## 4. ErrorEvent (Sentry Cloud)

### Purpose
Track exceptions, stack traces, and error context captured by Sentry SDK for debugging and error rate monitoring.

**Note**: Stored in Sentry cloud (SaaS), not local PostgreSQL. Access via Sentry API or web UI.

### Structure (Sentry Event Format)

```json
{
  "event_id": "a3d1f2b5c6e7f8a9b0c1d2e3f4a5b6c7",
  "timestamp": "2025-10-20T14:30:52.123Z",
  "level": "error",
  "logger": "api.routers.events",
  "platform": "python",
  "message": "Database connection timeout",
  "exception": {
    "values": [
      {
        "type": "psycopg2.OperationalError",
        "value": "could not connect to server: Connection timed out",
        "stacktrace": {
          "frames": [
            {
              "filename": "api/database.py",
              "function": "get_db",
              "lineno": 45,
              "context_line": "    conn = psycopg2.connect(database_url)"
            }
          ]
        }
      }
    ]
  },
  "tags": {
    "org_id": "org_church_12345",
    "environment": "production",
    "server_name": "signupflow-web-01"
  },
  "user": {
    "id": "person_admin_67890",
    "email": "admin@example.com",
    "username": "admin"
  },
  "request": {
    "url": "https://signupflow.io/api/events?org_id=org_church_12345",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer eyJ...",
      "User-Agent": "Mozilla/5.0..."
    }
  },
  "breadcrumbs": [
    {"timestamp": "2025-10-20T14:30:50Z", "message": "Starting request"},
    {"timestamp": "2025-10-20T14:30:51Z", "message": "Authenticating user"},
    {"timestamp": "2025-10-20T14:30:52Z", "message": "Querying database"}
  ]
}
```

### Key Fields

| Field | Description | Example |
|-------|-------------|---------|
| `event_id` | Sentry unique error ID | `a3d1f2b5c6e7f8a9b0c1d2e3f4a5b6c7` |
| `timestamp` | When error occurred | `2025-10-20T14:30:52.123Z` |
| `level` | Error severity | `error`, `warning`, `fatal` |
| `exception` | Exception details with stack trace | See example above |
| `tags.org_id` | Organization context | `org_church_12345` |
| `user` | User who triggered error | `{id: "...", email: "..."}` |
| `request` | HTTP request details | URL, method, headers |
| `breadcrumbs` | Event timeline leading to error | See example above |

### Sentry Tags (for filtering)

| Tag | Purpose | Example |
|-----|---------|---------|
| `org_id` | Organization isolation | `org_church_12345` |
| `environment` | Deployment environment | `production`, `staging`, `development` |
| `server_name` | Server instance | `signupflow-web-01` |
| `user_role` | User role | `admin`, `volunteer` |
| `endpoint` | API endpoint | `/api/events` |

### Retention
- **Sentry Plan**: Developer plan ($26/month for 10K events)
- **Retention**: 90 days
- **Quota**: 10,000 events/month (additional events rejected after quota)

---

## 5. LogEntry (Papertrail Cloud)

### Purpose
Centralized log aggregation for application logs, request logs, and system logs for debugging and troubleshooting.

**Note**: Stored in Papertrail cloud (SaaS), not local PostgreSQL. Access via Papertrail web UI or API.

### Structure (JSON Structured Log Format)

```json
{
  "timestamp": "2025-10-20T14:30:52.123Z",
  "level": "INFO",
  "logger": "api.routers.events",
  "message": "Created new event successfully",
  "org_id": "org_church_12345",
  "user_id": "person_admin_67890",
  "request_id": "req_abc123def456",
  "endpoint": "/api/events",
  "method": "POST",
  "status_code": 201,
  "response_time_ms": 152.34,
  "context": {
    "event_id": "event_sunday_service_20251027",
    "event_title": "Sunday Service",
    "event_datetime": "2025-10-27T10:00:00Z"
  }
}
```

### Key Fields

| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | When log created | `2025-10-20T14:30:52.123Z` |
| `level` | Log level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `logger` | Logger name | `api.routers.events` |
| `message` | Log message | `"Created new event successfully"` |
| `org_id` | Organization context | `org_church_12345` |
| `user_id` | User context | `person_admin_67890` |
| `request_id` | Request correlation ID | `req_abc123def456` |
| `endpoint` | API endpoint | `/api/events` |
| `method` | HTTP method | `POST`, `GET`, `PUT`, `DELETE` |
| `status_code` | HTTP response code | `201`, `200`, `404`, `500` |
| `response_time_ms` | Request duration | `152.34` |
| `context` | Additional context | Event-specific data |

### Log Levels

| Level | Purpose | Example |
|-------|---------|---------|
| `DEBUG` | Detailed debugging info | "Query executed: SELECT * FROM events WHERE..." |
| `INFO` | Normal operations | "User logged in successfully" |
| `WARNING` | Warning conditions | "Database query took 800ms (slower than normal)" |
| `ERROR` | Error conditions | "Failed to send email notification" |
| `CRITICAL` | Critical failures | "Database connection lost" |

### Papertrail Configuration
- **Free Tier**: 50MB/day, 7-day retention
- **Log Format**: Syslog protocol with JSON payloads
- **Search**: Full-text search via Papertrail web UI
- **Alerts**: Optional Papertrail alerts for specific log patterns (future enhancement)

---

## Relationships

```
Organization
    ├── PerformanceMetric (1:N) - org_id foreign key
    ├── AlertRule (1:N) - org_id foreign key
    └── Incident (1:N) - org_id foreign key (optional, NULL for global incidents)

Person
    └── ErrorEvent (1:N) - Sentry user.id tag
    └── LogEntry (1:N) - Papertrail user_id field
```

---

## Data Flow

### Performance Metrics Collection
```
FastAPI Middleware
    → Capture request start/end time
    → Calculate response_time_ms
    → INSERT INTO performance_metrics
    → (Every request)
```

### Alert Rule Evaluation
```
Cron Job (every 5 minutes)
    → SELECT * FROM alert_rules WHERE enabled = TRUE AND (snoozed_until IS NULL OR snoozed_until < NOW())
    → For each rule:
        → Query performance_metrics for recent data
        → Evaluate threshold (value > threshold_value)
        → If triggered:
            → Send Slack webhook notification
            → Send email notification
            → UPDATE alert_rules SET last_triggered_at = NOW()
```

### Sentry Error Tracking
```
FastAPI Exception Handler
    → Sentry SDK captures exception
    → Add tags: org_id, user_id, environment
    → Send to Sentry cloud (async)
    → Return error response to client
```

### Papertrail Log Aggregation
```
Python Logger
    → Format log as JSON
    → Send to Papertrail syslog endpoint
    → Papertrail indexes and stores
    → Available for search in web UI
```

---

**Last Updated**: 2025-10-20
**Status**: Complete data model for monitoring & observability platform
**Related**: plan.md (technology stack), contracts/ (API specifications)
