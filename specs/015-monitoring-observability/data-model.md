# Data Model: Monitoring and Observability

**Feature**: 015-monitoring-observability
**Date**: 2025-10-23
**Status**: Design Phase

This document defines the data entities for monitoring and observability infrastructure. Note that most monitoring data (errors, metrics, logs) is stored in external services (Sentry, InfluxDB, CloudWatch) rather than SignUpFlow's PostgreSQL database. This document focuses on entities that MUST be persisted in the application database for configuration and status tracking.

---

## Entity Overview

| Entity | Storage | Purpose | Cardinality |
|--------|---------|---------|-------------|
| **AlertRule** | PostgreSQL | Alert configuration (thresholds, channels) | ~20 rules |
| **AlertInstance** | PostgreSQL | Alert trigger history (for UI/dashboard) | ~1K/month |
| **StatusIncident** | PostgreSQL | Status page incident tracking | ~10/month |
| **ErrorEvent** | Sentry Cloud | Application errors (external service) | ~15K/month |
| **PerformanceMetric** | InfluxDB | Time-series metrics (external service) | ~500 series |
| **LogEntry** | CloudWatch/ELK | Application logs (external service) | ~1M/day |
| **HealthCheckResult** | In-Memory | Component health status (ephemeral) | N/A |

**Design Rationale**: Store only configuration and incident tracking in PostgreSQL. Bulk operational data (errors, metrics, logs) stored in specialized external services optimized for those workloads.

---

## Entities Stored in PostgreSQL

### 1. AlertRule

Alert configuration defining conditions, thresholds, and notification channels.

**Purpose**: Allow operations team to configure automated alerting rules without code changes.

**Schema**:
```python
class AlertRule(Base):
    """Alert rule configuration for automated monitoring alerts."""
    __tablename__ = "alert_rules"

    id = Column(String, primary_key=True)               # Format: "alert_rule_{uuid}"
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # Rule Definition
    name = Column(String(200), nullable=False)          # "High Error Rate", "Slow API Response"
    description = Column(Text, nullable=True)           # Human-readable explanation
    metric_name = Column(String(100), nullable=False)   # "error_rate", "http_request_duration_p95"
    condition = Column(String(10), nullable=False)      # ">", "<", "==", ">=", "<="
    threshold = Column(Float, nullable=False)           # 10 (errors/min), 500 (milliseconds)
    sustained_duration_seconds = Column(Integer, nullable=False, default=300)  # 5 minutes

    # Severity & Notifications
    severity = Column(String(20), nullable=False)       # "critical", "warning", "info"
    notification_channels = Column(JSON, nullable=False) # ["slack", "email", "dashboard"]
    slack_channel = Column(String(100), nullable=True)  # "#oncall", "#ops-warnings"
    email_addresses = Column(JSON, nullable=True)       # ["ops@signupflow.io"]

    # Organization Scoping (multi-tenant)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)  # null = global rule
    enabled = Column(Boolean, nullable=False, default=True)

    # Alert Suppression
    suppression_threshold = Column(Integer, nullable=True)  # Max alerts per window (100)
    suppression_window_seconds = Column(Integer, nullable=True)  # 300 (5 minutes)

    # Metadata
    created_by_user_id = Column(String, ForeignKey("people.id"), nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)

    # Relationships
    alert_instances = relationship("AlertInstance", back_populates="alert_rule")
```

**Validation Rules**:
- `name`: 1-200 characters, unique per organization
- `metric_name`: Must be valid metric from Prometheus/InfluxDB
- `condition`: Must be one of: ">", "<", "==", ">=", "<="
- `threshold`: Must be positive number
- `sustained_duration_seconds`: 0-3600 (0 = instant, max 1 hour)
- `severity`: Must be one of: "critical", "warning", "info"
- `notification_channels`: Must contain at least one of: "slack", "email", "dashboard"

**Indexes**:
```sql
CREATE INDEX idx_alert_rules_org ON alert_rules(org_id);
CREATE INDEX idx_alert_rules_enabled ON alert_rules(enabled) WHERE enabled = true;
CREATE INDEX idx_alert_rules_metric ON alert_rules(metric_name);
```

**Business Logic**:
- Alert rules evaluated every 60 seconds (cron job or background worker)
- Sustained duration check: metric must exceed threshold for entire duration before triggering
- Suppression: After `suppression_threshold` alerts in `suppression_window_seconds`, send summary alert instead of individual notifications

**Example Records**:
```json
{
  "id": "alert_rule_high_error_rate",
  "name": "High Error Rate",
  "description": "Trigger critical alert when error rate exceeds 10 errors/minute for 5 minutes",
  "metric_name": "error_rate",
  "condition": ">",
  "threshold": 10.0,
  "sustained_duration_seconds": 300,
  "severity": "critical",
  "notification_channels": ["slack", "email"],
  "slack_channel": "#oncall",
  "email_addresses": ["ops@signupflow.io"],
  "org_id": null,
  "enabled": true,
  "suppression_threshold": 100,
  "suppression_window_seconds": 300,
  "created_by_user_id": "person_admin_123"
}
```

---

### 2. AlertInstance

Triggered alert occurrence with status tracking (active, acknowledged, resolved).

**Purpose**: Track alert history for dashboard display, acknowledgment workflow, and auto-resolution.

**Schema**:
```python
class AlertInstance(Base):
    """Triggered alert instance with lifecycle tracking."""
    __tablename__ = "alert_instances"

    id = Column(String, primary_key=True)               # Format: "alert_instance_{timestamp}_{uuid}"
    alert_rule_id = Column(String, ForeignKey("alert_rules.id"), nullable=False)

    # Lifecycle Timestamps
    triggered_at = Column(DateTime, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="active")  # "active", "acknowledged", "resolved"
    acknowledged_by_user_id = Column(String, ForeignKey("people.id"), nullable=True)
    resolution_reason = Column(String(50), nullable=True)  # "auto_resolved", "manual", "suppressed"

    # Metric Values at Trigger
    metric_value = Column(Float, nullable=False)        # Actual value that triggered alert
    metric_threshold = Column(Float, nullable=False)    # Threshold from alert rule (snapshot)

    # Notification Tracking
    notifications_sent = Column(JSON, nullable=False, default=list)  # ["slack", "email"]
    notification_timestamps = Column(JSON, nullable=False, default=dict)  # {"slack": "2025-10-23T10:30:00Z"}

    # Relationships
    alert_rule = relationship("AlertRule", back_populates="alert_instances")
```

**Validation Rules**:
- `status`: Must be one of: "active", "acknowledged", "resolved"
- `metric_value`: Must be float (can be negative for certain metrics)
- State transitions: active → acknowledged → resolved (no backward transitions)

**Indexes**:
```sql
CREATE INDEX idx_alert_instances_triggered ON alert_instances(triggered_at DESC);
CREATE INDEX idx_alert_instances_status ON alert_instances(status) WHERE status = 'active';
CREATE INDEX idx_alert_instances_rule ON alert_instances(alert_rule_id);
```

**Business Logic**:
- **Auto-Resolution**: When metric returns to normal for 10 minutes, status changes to "resolved" with resolution_reason="auto_resolved"
- **Acknowledgment**: Operations user can acknowledge alert (marks as "seen", stops repeat notifications)
- **Suppression**: If >100 instances of same alert in 5 minutes, new instances created with status="suppressed", single summary notification sent

**Example Records**:
```json
{
  "id": "alert_instance_20251023103000_abc123",
  "alert_rule_id": "alert_rule_high_error_rate",
  "triggered_at": "2025-10-23T10:30:00Z",
  "acknowledged_at": "2025-10-23T10:32:15Z",
  "resolved_at": "2025-10-23T10:45:00Z",
  "status": "resolved",
  "acknowledged_by_user_id": "person_ops_456",
  "resolution_reason": "auto_resolved",
  "metric_value": 15.3,
  "metric_threshold": 10.0,
  "notifications_sent": ["slack", "email"],
  "notification_timestamps": {
    "slack": "2025-10-23T10:30:05Z",
    "email": "2025-10-23T10:30:07Z"
  }
}
```

---

### 3. StatusIncident

Status page incident for public transparency during outages.

**Purpose**: Allow operations team to create public status page incidents with updates during outages.

**Schema**:
```python
class StatusIncident(Base):
    """Status page incident for public transparency."""
    __tablename__ = "status_incidents"

    id = Column(String, primary_key=True)               # Format: "incident_{timestamp}_{uuid}"
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False)

    # Incident Details
    title = Column(String(200), nullable=False)         # "Database Performance Degradation"
    description = Column(Text, nullable=False)          # Initial incident description
    severity = Column(String(20), nullable=False)       # "investigating", "identified", "monitoring", "resolved"

    # Affected Components
    affected_components = Column(JSON, nullable=False)  # ["database", "api"]
    component_status = Column(JSON, nullable=False)     # {"database": "degraded", "api": "operational"}

    # Timeline
    started_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Status Updates (array of timestamped messages)
    updates = Column(JSON, nullable=False, default=list)
    # [{"timestamp": "2025-10-23T10:30:00Z", "message": "Engineers investigating...", "status": "investigating"}]

    # Metadata
    created_by_user_id = Column(String, ForeignKey("people.id"), nullable=False)
    public = Column(Boolean, nullable=False, default=True)  # Show on public status page
    post_mortem_url = Column(String(500), nullable=True)    # Link to detailed post-mortem
```

**Validation Rules**:
- `title`: 1-200 characters
- `severity`: Must be one of: "investigating", "identified", "monitoring", "resolved"
- `affected_components`: Must contain at least one component from: "api", "database", "background_workers", "external_services"
- State progression: investigating → identified → monitoring → resolved (can skip steps)

**Indexes**:
```sql
CREATE INDEX idx_status_incidents_public ON status_incidents(public) WHERE public = true;
CREATE INDEX idx_status_incidents_created ON status_incidents(created_at DESC);
CREATE INDEX idx_status_incidents_severity ON status_incidents(severity);
```

**Business Logic**:
- **Public Visibility**: Only incidents with `public=true` shown on status page
- **Component Status**: Maps to health check results (auto-updates when health checks change)
- **Status Updates**: Append-only array (cannot edit/delete previous updates for transparency)
- **Historical Uptime**: Calculate 7-day, 30-day, 90-day uptime percentages based on incident duration

**Example Records**:
```json
{
  "id": "incident_20251023103000_abc123",
  "created_at": "2025-10-23T10:30:00Z",
  "updated_at": "2025-10-23T11:15:00Z",
  "title": "Database Performance Degradation",
  "description": "We are experiencing slow database queries affecting API response times.",
  "severity": "resolved",
  "affected_components": ["database", "api"],
  "component_status": {
    "database": "operational",
    "api": "operational"
  },
  "started_at": "2025-10-23T10:25:00Z",
  "resolved_at": "2025-10-23T11:15:00Z",
  "updates": [
    {
      "timestamp": "2025-10-23T10:30:00Z",
      "message": "Engineers investigating database slow queries",
      "status": "investigating"
    },
    {
      "timestamp": "2025-10-23T10:45:00Z",
      "message": "Root cause identified: missing database index. Applying fix.",
      "status": "identified"
    },
    {
      "timestamp": "2025-10-23T11:00:00Z",
      "message": "Database index created. Monitoring performance recovery.",
      "status": "monitoring"
    },
    {
      "timestamp": "2025-10-23T11:15:00Z",
      "message": "Performance fully restored. Incident resolved.",
      "status": "resolved"
    }
  ],
  "created_by_user_id": "person_ops_456",
  "public": true,
  "post_mortem_url": "https://blog.signupflow.io/incidents/2025-10-23-db-performance"
}
```

---

## Entities Stored Externally

### 4. ErrorEvent (Sentry Cloud)

Application errors captured by Sentry SDK (not stored in PostgreSQL).

**Schema (Sentry)**:
- **error_id**: Unique error identifier (Sentry issue ID)
- **timestamp**: When error occurred (ISO 8601 UTC)
- **error_type**: Exception class name (e.g., `ValueError`, `DatabaseConnectionError`)
- **error_message**: Exception message
- **stack_trace**: Full Python stack trace
- **user_id**: Authenticated user ID (from JWT token)
- **org_id**: Organization ID (from session context)
- **request_id**: Request correlation ID (UUID)
- **endpoint**: API endpoint (e.g., `/api/events`)
- **http_method**: HTTP method (GET, POST, PUT, DELETE)
- **environment**: "production", "staging", "development"
- **version**: Application version (git commit SHA)
- **occurrence_count**: Number of times this error occurred

**Access**: Via Sentry API or Sentry UI dashboard

---

### 5. PerformanceMetric (InfluxDB)

Time-series performance metrics collected via Prometheus (not stored in PostgreSQL).

**Schema (InfluxDB)**:
- **Measurement Name**: `http_requests_total`, `http_request_duration_seconds`, `db_query_duration_seconds`
- **Tags**: `endpoint`, `method`, `status_code`, `org_id` (dimensions for grouping)
- **Fields**: `value` (counter), `sum`, `count`, `p50`, `p95`, `p99` (percentiles)
- **Timestamp**: Nanosecond precision UTC

**Retention Policies**:
- Real-time (1-minute granularity): 7 days
- Hourly aggregates: 30 days
- Daily aggregates: 1 year

**Access**: Via InfluxDB HTTP API or Grafana dashboards

---

### 6. LogEntry (CloudWatch Logs or Elasticsearch)

Application logs aggregated in centralized logging service (not stored in PostgreSQL).

**Schema (CloudWatch/Elasticsearch)**:
- **timestamp**: ISO 8601 UTC
- **log_level**: ERROR, WARN, INFO, DEBUG
- **logger_name**: Python logger name (e.g., `api.routers.events`)
- **message**: Log message text
- **context**:
  - `user_id`: Authenticated user ID
  - `org_id`: Organization ID
  - `request_id`: Request correlation ID
  - `endpoint`: API endpoint
- **stack_trace**: Python stack trace (if exception logged)

**Retention**: 7 days (configurable up to 30 days for compliance)

**Access**: Via CloudWatch Logs Insights or Elasticsearch API

---

### 7. HealthCheckResult (In-Memory)

Component health status (ephemeral, not persisted).

**Schema (Python dict)**:
```python
{
    "timestamp": "2025-10-23T10:30:00Z",
    "components": {
        "database": {
            "status": "healthy",
            "response_time_ms": 12
        },
        "redis": {
            "status": "healthy",
            "response_time_ms": 3
        },
        "external_api": {
            "status": "degraded",
            "response_time_ms": 2500,
            "error": "Timeout after 3 seconds"
        }
    },
    "overall_status": "degraded"
}
```

**Lifetime**: Generated on-demand for each `/health` request (not cached)

**Access**: GET /health endpoint

---

## Entity Relationships

```
                    ┌──────────────┐
                    │ AlertRule    │
                    │ (PostgreSQL) │
                    └──────┬───────┘
                           │
                           │ 1:N
                           │
                    ┌──────▼───────┐
                    │AlertInstance │
                    │ (PostgreSQL) │
                    └──────────────┘

    ┌────────────────┐
    │StatusIncident  │
    │  (PostgreSQL)  │
    └────────────────┘

    ┌────────────────┐          ┌──────────────────┐
    │  ErrorEvent    │          │PerformanceMetric │
    │ (Sentry Cloud) │          │   (InfluxDB)     │
    └────────────────┘          └──────────────────┘

    ┌────────────────┐          ┌──────────────────┐
    │   LogEntry     │          │HealthCheckResult │
    │(CloudWatch/ELK)│          │   (In-Memory)    │
    └────────────────┘          └──────────────────┘
```

**Design Principle**: Store only configuration (AlertRule) and incident tracking (AlertInstance, StatusIncident) in PostgreSQL. Bulk operational data (errors, metrics, logs) belongs in specialized external services optimized for those workloads.

---

## Database Migration Script

```python
# alembic/versions/xxx_add_monitoring_tables.py
"""Add monitoring tables for alert rules, alert instances, and status incidents."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # AlertRule table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('condition', sa.String(10), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('sustained_duration_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('notification_channels', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('slack_channel', sa.String(100), nullable=True),
        sa.Column('email_addresses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('suppression_threshold', sa.Integer(), nullable=True),
        sa.Column('suppression_window_seconds', sa.Integer(), nullable=True),
        sa.Column('created_by_user_id', sa.String(), nullable=False),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_rules_org', 'alert_rules', ['org_id'])
    op.create_index('idx_alert_rules_enabled', 'alert_rules', ['enabled'], postgresql_where=sa.text('enabled = true'))
    op.create_index('idx_alert_rules_metric', 'alert_rules', ['metric_name'])

    # AlertInstance table
    op.create_table(
        'alert_instances',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('alert_rule_id', sa.String(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('acknowledged_by_user_id', sa.String(), nullable=True),
        sa.Column('resolution_reason', sa.String(50), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_threshold', sa.Float(), nullable=False),
        sa.Column('notifications_sent', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('notification_timestamps', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['alert_rule_id'], ['alert_rules.id'], ),
        sa.ForeignKeyConstraint(['acknowledged_by_user_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_instances_triggered', 'alert_instances', [sa.text('triggered_at DESC')])
    op.create_index('idx_alert_instances_status', 'alert_instances', ['status'], postgresql_where=sa.text("status = 'active'"))
    op.create_index('idx_alert_instances_rule', 'alert_instances', ['alert_rule_id'])

    # StatusIncident table
    op.create_table(
        'status_incidents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('affected_components', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('component_status', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('updates', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_by_user_id', sa.String(), nullable=False),
        sa.Column('public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('post_mortem_url', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_status_incidents_public', 'status_incidents', ['public'], postgresql_where=sa.text('public = true'))
    op.create_index('idx_status_incidents_created', 'status_incidents', [sa.text('created_at DESC')])
    op.create_index('idx_status_incidents_severity', 'status_incidents', ['severity'])

def downgrade():
    op.drop_index('idx_status_incidents_severity', table_name='status_incidents')
    op.drop_index('idx_status_incidents_created', table_name='status_incidents')
    op.drop_index('idx_status_incidents_public', table_name='status_incidents')
    op.drop_table('status_incidents')

    op.drop_index('idx_alert_instances_rule', table_name='alert_instances')
    op.drop_index('idx_alert_instances_status', table_name='alert_instances')
    op.drop_index('idx_alert_instances_triggered', table_name='alert_instances')
    op.drop_table('alert_instances')

    op.drop_index('idx_alert_rules_metric', table_name='alert_rules')
    op.drop_index('idx_alert_rules_enabled', table_name='alert_rules')
    op.drop_index('idx_alert_rules_org', table_name='alert_rules')
    op.drop_table('alert_rules')
```

---

## Summary

**PostgreSQL Tables** (3 tables, ~1000 records total):
1. `alert_rules` - Alert configuration (~20 records)
2. `alert_instances` - Alert trigger history (~1000 records/month, retention policy needed)
3. `status_incidents` - Status page incidents (~10 records/month)

**External Storage** (managed by specialized services):
4. ErrorEvent → Sentry Cloud (15K errors/month)
5. PerformanceMetric → InfluxDB (500 time series × 1 point/minute)
6. LogEntry → CloudWatch Logs or ELK (1M logs/day)
7. HealthCheckResult → In-memory (generated on-demand)

**Storage Efficiency**: By storing only configuration in PostgreSQL and bulk operational data in specialized services, we achieve:
- 99% reduction in PostgreSQL storage (no time-series or log data)
- Optimal query performance (each service optimized for its data type)
- Cost control (leverage free tiers of Sentry, InfluxDB, CloudWatch)
