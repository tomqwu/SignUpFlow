# Alert Configuration API Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: REST API Endpoint Specification
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Alert Configuration API enables admin users to create, manage, and configure monitoring alert rules. Alert rules define conditions that trigger notifications when metrics exceed thresholds, enabling proactive incident response.

**Use Cases**:
- Create alert rules for high error rates
- Configure Slack/email notifications
- Manage alert instances (acknowledge, resolve)
- View alert history and statistics

---

## API Endpoints

### 1. POST /api/alerts - Create Alert Rule

**Purpose**: Create new monitoring alert rule.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
POST /api/alerts?org_id=org_456 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "name": "High Error Rate",
  "metric_name": "http_requests_total",
  "metric_filter": {
    "status_code": "5.."
  },
  "aggregation": "rate",
  "condition": ">",
  "threshold": 10,
  "sustained_duration_seconds": 300,
  "severity": "critical",
  "notification_channels": ["slack", "email"],
  "slack_channel": "#alerts",
  "email_recipients": ["ops@signupflow.io"],
  "enabled": true,
  "suppression_threshold": 100,
  "suppression_window_seconds": 300
}
```

**Request Schema**:
```python
class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_filter: Optional[Dict[str, str]] = None
    aggregation: str = Field(..., regex="^(rate|avg|sum|count|p50|p95|p99)$")
    condition: str = Field(..., regex="^(>|<|==|>=|<=)$")
    threshold: float
    sustained_duration_seconds: int = Field(default=300, ge=0, le=3600)
    severity: str = Field(..., regex="^(critical|warning|info)$")
    notification_channels: List[str] = Field(..., min_items=1)
    slack_channel: Optional[str] = None
    email_recipients: Optional[List[str]] = None
    enabled: bool = True
    suppression_threshold: Optional[int] = None
    suppression_window_seconds: Optional[int] = None
```

**Response (201 Created)**:
```json
{
  "id": "alert_rule_abc123",
  "name": "High Error Rate",
  "metric_name": "http_requests_total",
  "metric_filter": {
    "status_code": "5.."
  },
  "aggregation": "rate",
  "condition": ">",
  "threshold": 10,
  "sustained_duration_seconds": 300,
  "severity": "critical",
  "notification_channels": ["slack", "email"],
  "slack_channel": "#alerts",
  "email_recipients": ["ops@signupflow.io"],
  "org_id": "org_456",
  "enabled": true,
  "suppression_threshold": 100,
  "suppression_window_seconds": 300,
  "created_at": "2025-10-23T10:30:45.123Z",
  "updated_at": "2025-10-23T10:30:45.123Z",
  "status": "active",
  "last_triggered_at": null,
  "trigger_count": 0
}
```

**Status Codes**:
- `201 Created`: Alert rule created successfully
- `400 Bad Request`: Invalid request data (validation error)
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin or wrong organization
- `422 Unprocessable Entity`: Invalid metric name or aggregation type

**Validation Rules**:
- `name`: Required, 1-200 characters, unique per organization
- `metric_name`: Must exist in Prometheus metrics registry
- `aggregation`: Must be one of: rate, avg, sum, count, p50, p95, p99
- `condition`: Must be one of: >, <, ==, >=, <=
- `threshold`: Must be positive number
- `sustained_duration_seconds`: 0-3600 seconds (0 = instant trigger, 3600 = 1 hour sustained)
- `severity`: Must be one of: critical, warning, info
- `notification_channels`: At least one channel required
- `slack_channel`: Required if "slack" in notification_channels
- `email_recipients`: Required if "email" in notification_channels, must be valid emails
- `suppression_threshold`: Optional, must be >= 1 (alerts in suppression window)
- `suppression_window_seconds`: Optional, must be >= 60 (1 minute minimum)

---

### 2. GET /api/alerts - List Alert Rules

**Purpose**: List all alert rules for organization.

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
GET /api/alerts?org_id=org_456&enabled=true&severity=critical HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Query Parameters**:
- `org_id` (required): Organization ID filter
- `enabled` (optional): Filter by enabled status (true/false)
- `severity` (optional): Filter by severity (critical/warning/info)
- `metric_name` (optional): Filter by metric name

**Response (200 OK)**:
```json
{
  "alert_rules": [
    {
      "id": "alert_rule_abc123",
      "name": "High Error Rate",
      "metric_name": "http_requests_total",
      "condition": ">",
      "threshold": 10,
      "severity": "critical",
      "enabled": true,
      "status": "active",
      "last_triggered_at": "2025-10-23T08:15:30.000Z",
      "trigger_count": 5,
      "created_at": "2025-10-20T10:30:45.123Z"
    },
    {
      "id": "alert_rule_def456",
      "name": "Slow API Response",
      "metric_name": "http_request_duration_seconds",
      "condition": ">",
      "threshold": 1.0,
      "severity": "warning",
      "enabled": true,
      "status": "active",
      "last_triggered_at": null,
      "trigger_count": 0,
      "created_at": "2025-10-21T14:20:00.000Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

**Status Codes**:
- `200 OK`: Alert rules retrieved successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or wrong organization

---

### 3. GET /api/alerts/{alert_rule_id} - Get Alert Rule Details

**Purpose**: Retrieve specific alert rule with detailed configuration and statistics.

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
GET /api/alerts/alert_rule_abc123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK)**:
```json
{
  "id": "alert_rule_abc123",
  "name": "High Error Rate",
  "metric_name": "http_requests_total",
  "metric_filter": {
    "status_code": "5.."
  },
  "aggregation": "rate",
  "condition": ">",
  "threshold": 10,
  "sustained_duration_seconds": 300,
  "severity": "critical",
  "notification_channels": ["slack", "email"],
  "slack_channel": "#alerts",
  "email_recipients": ["ops@signupflow.io"],
  "org_id": "org_456",
  "enabled": true,
  "suppression_threshold": 100,
  "suppression_window_seconds": 300,
  "created_at": "2025-10-20T10:30:45.123Z",
  "updated_at": "2025-10-23T10:30:45.123Z",
  "status": "active",
  "last_triggered_at": "2025-10-23T08:15:30.000Z",
  "trigger_count": 5,
  "active_instances": 0,
  "acknowledged_instances": 2,
  "resolved_instances": 3,
  "average_resolution_time_seconds": 1200
}
```

**Status Codes**:
- `200 OK`: Alert rule retrieved successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or alert belongs to different organization
- `404 Not Found`: Alert rule ID does not exist

---

### 4. PUT /api/alerts/{alert_rule_id} - Update Alert Rule

**Purpose**: Update existing alert rule configuration.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
PUT /api/alerts/alert_rule_abc123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "threshold": 15,
  "sustained_duration_seconds": 600,
  "enabled": true
}
```

**Request Schema**: Same as AlertRuleCreate, all fields optional (partial update).

**Response (200 OK)**:
```json
{
  "id": "alert_rule_abc123",
  "name": "High Error Rate",
  "threshold": 15,
  "sustained_duration_seconds": 600,
  "enabled": true,
  "updated_at": "2025-10-23T10:35:00.000Z"
}
```

**Status Codes**:
- `200 OK`: Alert rule updated successfully
- `400 Bad Request`: Invalid request data (validation error)
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin or alert belongs to different organization
- `404 Not Found`: Alert rule ID does not exist

**Validation Rules**: Same as POST /api/alerts (only provided fields validated).

---

### 5. DELETE /api/alerts/{alert_rule_id} - Delete Alert Rule

**Purpose**: Delete alert rule and all associated alert instances.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
DELETE /api/alerts/alert_rule_abc123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (204 No Content)**:
```
(empty body)
```

**Status Codes**:
- `204 No Content`: Alert rule deleted successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin or alert belongs to different organization
- `404 Not Found`: Alert rule ID does not exist

---

### 6. GET /api/alerts/{alert_rule_id}/instances - List Alert Instances

**Purpose**: List all triggered instances of specific alert rule.

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
GET /api/alerts/alert_rule_abc123/instances?status=active&limit=20 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Query Parameters**:
- `status` (optional): Filter by status (active/acknowledged/resolved)
- `limit` (optional): Max results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**Response (200 OK)**:
```json
{
  "alert_instances": [
    {
      "id": "alert_instance_xyz789",
      "alert_rule_id": "alert_rule_abc123",
      "triggered_at": "2025-10-23T08:15:30.000Z",
      "acknowledged_at": null,
      "acknowledged_by": null,
      "resolved_at": null,
      "status": "active",
      "metric_value": 45.6,
      "metric_threshold": 10.0,
      "notifications_sent": [
        {
          "channel": "slack",
          "sent_at": "2025-10-23T08:15:35.000Z",
          "status": "delivered"
        },
        {
          "channel": "email",
          "sent_at": "2025-10-23T08:15:36.000Z",
          "status": "delivered"
        }
      ],
      "duration_seconds": null
    },
    {
      "id": "alert_instance_uvw456",
      "alert_rule_id": "alert_rule_abc123",
      "triggered_at": "2025-10-23T06:10:20.000Z",
      "acknowledged_at": "2025-10-23T06:15:00.000Z",
      "acknowledged_by": "user_admin_123",
      "resolved_at": "2025-10-23T07:30:00.000Z",
      "status": "resolved",
      "metric_value": 23.4,
      "metric_threshold": 10.0,
      "notifications_sent": [
        {
          "channel": "slack",
          "sent_at": "2025-10-23T06:10:25.000Z",
          "status": "delivered"
        }
      ],
      "duration_seconds": 4800
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

**Status Codes**:
- `200 OK`: Alert instances retrieved successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or alert belongs to different organization
- `404 Not Found`: Alert rule ID does not exist

---

### 7. POST /api/alerts/instances/{alert_instance_id}/acknowledge - Acknowledge Alert

**Purpose**: Acknowledge active alert instance (stops repeated notifications).

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
POST /api/alerts/instances/alert_instance_xyz789/acknowledge HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "note": "Investigating high error rate, suspected database issue"
}
```

**Request Schema**:
```python
class AcknowledgeRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)
```

**Response (200 OK)**:
```json
{
  "id": "alert_instance_xyz789",
  "status": "acknowledged",
  "acknowledged_at": "2025-10-23T10:40:00.000Z",
  "acknowledged_by": "user_admin_123",
  "acknowledged_by_name": "Admin User",
  "note": "Investigating high error rate, suspected database issue"
}
```

**Status Codes**:
- `200 OK`: Alert acknowledged successfully
- `400 Bad Request`: Alert already acknowledged or resolved
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or alert belongs to different organization
- `404 Not Found`: Alert instance ID does not exist

---

### 8. POST /api/alerts/instances/{alert_instance_id}/resolve - Resolve Alert

**Purpose**: Mark alert instance as resolved (issue fixed).

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
POST /api/alerts/instances/alert_instance_xyz789/resolve HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "note": "Database connection pool increased, error rate back to normal"
}
```

**Request Schema**:
```python
class ResolveRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)
```

**Response (200 OK)**:
```json
{
  "id": "alert_instance_xyz789",
  "status": "resolved",
  "resolved_at": "2025-10-23T10:45:00.000Z",
  "resolved_by": "user_admin_123",
  "resolved_by_name": "Admin User",
  "note": "Database connection pool increased, error rate back to normal",
  "duration_seconds": 1800
}
```

**Status Codes**:
- `200 OK`: Alert resolved successfully
- `400 Bad Request`: Alert already resolved
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or alert belongs to different organization
- `404 Not Found`: Alert instance ID does not exist

---

## Alert Rule Evaluation Logic

### Backend Service

**File**: `api/services/alert_service.py`

```python
from datetime import datetime, timedelta
from api.models import AlertRule, AlertInstance
from api.services.prometheus_service import query_prometheus
from api.services.notification_service import send_slack_notification, send_email_notification

class AlertService:
    """Service for evaluating alert rules and triggering notifications."""

    def evaluate_all_rules(self, db: Session):
        """
        Evaluate all enabled alert rules (runs every 10 seconds).

        Called by background task scheduler (Celery or APScheduler).
        """
        # Get all enabled alert rules
        rules = db.query(AlertRule).filter(AlertRule.enabled == True).all()

        for rule in rules:
            self.evaluate_rule(rule, db)

    def evaluate_rule(self, rule: AlertRule, db: Session):
        """
        Evaluate single alert rule against current metrics.

        Steps:
        1. Query Prometheus for current metric value
        2. Apply metric filter (e.g., status_code=5xx)
        3. Apply aggregation (rate, avg, p95, etc.)
        4. Check condition (>, <, ==, etc.)
        5. Verify sustained duration (metric above threshold for N seconds)
        6. Trigger alert if condition met
        7. Check suppression (>100 alerts in 5 minutes → send summary)
        """
        # Query Prometheus
        metric_value = self._query_metric(rule)

        # Check condition
        condition_met = self._check_condition(
            metric_value,
            rule.condition,
            rule.threshold
        )

        if condition_met:
            # Check sustained duration
            if rule.sustained_duration_seconds > 0:
                sustained = self._check_sustained(rule, metric_value, db)
                if not sustained:
                    return  # Condition not sustained long enough

            # Check if alert already active
            existing_active = db.query(AlertInstance).filter(
                AlertInstance.alert_rule_id == rule.id,
                AlertInstance.status == "active"
            ).first()

            if existing_active:
                # Update existing alert (don't create duplicate)
                existing_active.metric_value = metric_value
                db.commit()
                return

            # Check suppression
            if self._check_suppression(rule, db):
                # Send summary notification instead of individual alerts
                self._send_suppression_summary(rule, db)
                return

            # Create new alert instance
            alert_instance = AlertInstance(
                id=f"alert_instance_{generate_id()}",
                alert_rule_id=rule.id,
                triggered_at=datetime.utcnow(),
                status="active",
                metric_value=metric_value,
                metric_threshold=rule.threshold
            )
            db.add(alert_instance)
            db.commit()

            # Send notifications
            self._send_notifications(rule, alert_instance, db)

            # Update rule statistics
            rule.last_triggered_at = datetime.utcnow()
            rule.trigger_count += 1
            db.commit()

    def _query_metric(self, rule: AlertRule) -> float:
        """Query Prometheus for current metric value."""
        # Build Prometheus query
        query = self._build_prometheus_query(rule)

        # Query Prometheus API
        result = query_prometheus(query)

        # Extract value
        if result and len(result) > 0:
            return float(result[0]["value"][1])

        return 0.0

    def _build_prometheus_query(self, rule: AlertRule) -> str:
        """Build Prometheus query from alert rule."""
        metric_name = rule.metric_name

        # Apply filters
        if rule.metric_filter:
            filters = ",".join([
                f'{key}=~"{value}"'
                for key, value in rule.metric_filter.items()
            ])
            metric_name = f'{metric_name}{{{filters}}}'

        # Apply aggregation
        if rule.aggregation == "rate":
            query = f'rate({metric_name}[1m])'
        elif rule.aggregation == "avg":
            query = f'avg_over_time({metric_name}[5m])'
        elif rule.aggregation == "sum":
            query = f'sum({metric_name})'
        elif rule.aggregation == "count":
            query = f'count({metric_name})'
        elif rule.aggregation == "p50":
            query = f'histogram_quantile(0.5, rate({metric_name}_bucket[5m]))'
        elif rule.aggregation == "p95":
            query = f'histogram_quantile(0.95, rate({metric_name}_bucket[5m]))'
        elif rule.aggregation == "p99":
            query = f'histogram_quantile(0.99, rate({metric_name}_bucket[5m]))'

        return query

    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if metric value meets alert condition."""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == "==":
            return abs(value - threshold) < 0.01
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold

        return False

    def _check_sustained(self, rule: AlertRule, current_value: float, db: Session) -> bool:
        """Check if condition sustained for required duration."""
        # Query historical metric values from InfluxDB
        # Verify metric above threshold for sustained_duration_seconds
        # Return True if sustained, False if transient spike
        pass  # Implementation details

    def _check_suppression(self, rule: AlertRule, db: Session) -> bool:
        """Check if alert suppression should trigger."""
        if not rule.suppression_threshold:
            return False

        # Count recent alert instances
        window_start = datetime.utcnow() - timedelta(seconds=rule.suppression_window_seconds)
        recent_count = db.query(AlertInstance).filter(
            AlertInstance.alert_rule_id == rule.id,
            AlertInstance.triggered_at >= window_start
        ).count()

        return recent_count >= rule.suppression_threshold

    def _send_notifications(self, rule: AlertRule, alert_instance: AlertInstance, db: Session):
        """Send alert notifications to configured channels."""
        notifications_sent = []

        for channel in rule.notification_channels:
            try:
                if channel == "slack":
                    send_slack_notification(
                        channel=rule.slack_channel,
                        alert_rule=rule,
                        alert_instance=alert_instance
                    )
                    notifications_sent.append({
                        "channel": "slack",
                        "sent_at": datetime.utcnow().isoformat(),
                        "status": "delivered"
                    })

                elif channel == "email":
                    for recipient in rule.email_recipients:
                        send_email_notification(
                            to=recipient,
                            alert_rule=rule,
                            alert_instance=alert_instance
                        )
                    notifications_sent.append({
                        "channel": "email",
                        "sent_at": datetime.utcnow().isoformat(),
                        "status": "delivered"
                    })

            except Exception as e:
                notifications_sent.append({
                    "channel": channel,
                    "sent_at": datetime.utcnow().isoformat(),
                    "status": "failed",
                    "error": str(e)
                })

        # Update alert instance with notification status
        alert_instance.notifications_sent = notifications_sent
        db.commit()
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_alert_service.py
def test_check_condition_greater_than():
    """Test alert condition evaluation (>)."""
    assert alert_service._check_condition(15.0, ">", 10.0) == True
    assert alert_service._check_condition(5.0, ">", 10.0) == False

def test_build_prometheus_query_with_filter():
    """Test Prometheus query building with metric filter."""
    rule = AlertRule(
        metric_name="http_requests_total",
        metric_filter={"status_code": "5.."},
        aggregation="rate"
    )
    query = alert_service._build_prometheus_query(rule)
    assert query == 'rate(http_requests_total{status_code=~"5.."}[1m])'
```

### Integration Tests

```python
# tests/integration/test_alert_configuration_api.py
def test_create_alert_rule(client, admin_auth_headers):
    """Test POST /api/alerts creates alert rule."""
    response = client.post(
        "/api/alerts?org_id=org_test",
        json={
            "name": "Test Alert",
            "metric_name": "http_requests_total",
            "condition": ">",
            "threshold": 10.0,
            "severity": "critical",
            "notification_channels": ["slack"],
            "slack_channel": "#test-alerts"
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Alert"
    assert data["threshold"] == 10.0
```

---

## References

- **Prometheus Alerting**: [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- **Alertmanager**: [Notification Routing](https://prometheus.io/docs/alerting/latest/configuration/)
- **SLO/SLI**: [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/routers/monitoring.py` and `api/services/alert_service.py` during Feature 015 implementation phase
