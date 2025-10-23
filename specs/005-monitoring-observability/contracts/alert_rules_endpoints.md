# API Contract: Alert Rules & Notifications Endpoints

**Feature**: Monitoring & Observability Platform
**Purpose**: Alert rule configuration, threshold management, and automated notification delivery

---

## Endpoint Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/alert-rules` | POST | Admin | Create alert rule |
| `/api/alert-rules` | GET | Authenticated | List alert rules (filtered by org_id) |
| `/api/alert-rules/{rule_id}` | GET | Authenticated | Get alert rule details |
| `/api/alert-rules/{rule_id}` | PUT | Admin | Update alert rule |
| `/api/alert-rules/{rule_id}` | DELETE | Admin | Delete alert rule |
| `/api/alert-rules/{rule_id}/snooze` | POST | Admin | Snooze alert rule for 1 hour |
| `/api/alert-rules/{rule_id}/test` | POST | Admin | Test alert rule (send notification immediately) |

**Note**: Alert rules are evaluated by background cron job every 5 minutes. Not evaluated on API calls.

---

## 1. Create Alert Rule

### Request

**Method**: `POST`
**Path**: `/api/alert-rules?org_id={org_id}`
**Authentication**: Admin required (`verify_admin_access()`)

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | String | Yes | Organization ID (multi-tenant isolation) |

**Body**:
```json
{
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
  "enabled": true
}
```

**Field Definitions**:
- `name`: Alert rule name (max 100 characters)
- `description`: Rule description (optional)
- `metric_type`: Metric to monitor (`response_time`, `error_rate`, `memory_usage`, `cpu_usage`, `db_query_count`)
- `threshold_value`: Threshold value (e.g., `1000` for 1000ms, `1.0` for 1%)
- `threshold_operator`: Comparison operator (`gt` > , `gte` >= , `lt` < , `lte` <= , `eq` =)
- `evaluation_interval_minutes`: How often to evaluate (5, 10, 15, 30, 60 minutes)
- `notification_channels`: Array of channels (`slack`, `email`)
- `notification_config`: Channel-specific configuration
- `enabled`: Is rule active (default: true)

**Example Requests**:
```bash
# High response time alert
curl -X POST "https://signupflow.io/api/alert-rules?org_id=org_church_12345" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Slow API Response Time",
    "description": "Alert when P95 response time exceeds 1000ms",
    "metric_type": "response_time",
    "threshold_value": 1000,
    "threshold_operator": "gt",
    "evaluation_interval_minutes": 5,
    "notification_channels": ["slack"],
    "notification_config": {
      "slack_webhook_url": "https://hooks.slack.com/services/T00/B00/XXXX"
    },
    "enabled": true
  }'

# High memory usage alert
curl -X POST "https://signupflow.io/api/alert-rules?org_id=org_church_12345" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Memory Usage",
    "metric_type": "memory_usage",
    "threshold_value": 1500,
    "threshold_operator": "gte",
    "evaluation_interval_minutes": 10,
    "notification_channels": ["email"],
    "notification_config": {
      "email_recipients": ["ops@church.com"]
    },
    "enabled": true
  }'
```

### Response

**Success (201 Created)**:
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
  "last_triggered_at": null,
  "created_at": "2025-10-20T14:30:00Z",
  "updated_at": "2025-10-20T14:30:00Z"
}
```

**Error (400 Bad Request)** - Invalid Threshold Operator:
```json
{
  "error": "invalid_threshold_operator",
  "message": "Invalid threshold_operator. Must be one of: gt, gte, lt, lte, eq",
  "valid_operators": ["gt", "gte", "lt", "lte", "eq"]
}
```

**Error (403 Forbidden)** - Not Admin:
```json
{
  "error": "admin_access_required",
  "message": "Admin role required to create alert rules."
}
```

**Error (422 Unprocessable Entity)** - Missing Required Field:
```json
{
  "error": "validation_error",
  "message": "Field 'notification_channels' is required.",
  "field": "notification_channels"
}
```

---

## 2. List Alert Rules

### Request

**Method**: `GET`
**Path**: `/api/alert-rules?org_id={org_id}&enabled={enabled}`
**Authentication**: Authenticated user (JWT required)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `org_id` | String | Yes | Organization ID | `org_church_12345` |
| `enabled` | Boolean | No | Filter by enabled status | `true`, `false` |

**Example Request**:
```bash
# Get all alert rules
curl "https://signupflow.io/api/alert-rules?org_id=org_church_12345" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Get only enabled rules
curl "https://signupflow.io/api/alert-rules?org_id=org_church_12345&enabled=true" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "alert_rules": [
    {
      "id": "alert_rule_abc123",
      "org_id": "org_church_12345",
      "name": "High Error Rate Alert",
      "description": "Alert when error rate exceeds 1%",
      "metric_type": "error_rate",
      "threshold_value": 1.0,
      "threshold_operator": "gt",
      "evaluation_interval_minutes": 5,
      "notification_channels": ["slack", "email"],
      "enabled": true,
      "snoozed_until": null,
      "last_triggered_at": "2025-10-20T14:25:00Z",
      "created_at": "2025-10-15T10:00:00Z",
      "updated_at": "2025-10-20T14:25:00Z"
    },
    {
      "id": "alert_rule_def456",
      "org_id": "org_church_12345",
      "name": "Slow API Response Time",
      "metric_type": "response_time",
      "threshold_value": 1000,
      "threshold_operator": "gt",
      "evaluation_interval_minutes": 5,
      "notification_channels": ["slack"],
      "enabled": true,
      "snoozed_until": null,
      "last_triggered_at": null,
      "created_at": "2025-10-15T10:05:00Z",
      "updated_at": "2025-10-15T10:05:00Z"
    }
  ],
  "total": 2
}
```

---

## 3. Update Alert Rule

### Request

**Method**: `PUT`
**Path**: `/api/alert-rules/{rule_id}`
**Authentication**: Admin required

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Body** (all fields optional):
```json
{
  "name": "High Error Rate Alert (Updated)",
  "threshold_value": 2.0,
  "enabled": false
}
```

**Example Request**:
```bash
# Disable alert rule
curl -X PUT "https://signupflow.io/api/alert-rules/alert_rule_abc123" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Update threshold
curl -X PUT "https://signupflow.io/api/alert-rules/alert_rule_abc123" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"threshold_value": 2.0}'
```

### Response

**Success (200 OK)**:
```json
{
  "id": "alert_rule_abc123",
  "org_id": "org_church_12345",
  "name": "High Error Rate Alert (Updated)",
  "threshold_value": 2.0,
  "enabled": false,
  "updated_at": "2025-10-20T15:00:00Z"
}
```

---

## 4. Snooze Alert Rule

### Request

**Method**: `POST`
**Path**: `/api/alert-rules/{rule_id}/snooze`
**Authentication**: Admin required

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Body**:
```json
{
  "duration_minutes": 60
}
```

**Field Definitions**:
- `duration_minutes`: Snooze duration (default: 60, max: 1440 = 24 hours)

**Example Request**:
```bash
# Snooze for 1 hour
curl -X POST "https://signupflow.io/api/alert-rules/alert_rule_abc123/snooze" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 60}'
```

### Response

**Success (200 OK)**:
```json
{
  "id": "alert_rule_abc123",
  "snoozed_until": "2025-10-20T16:00:00Z",
  "message": "Alert rule snoozed for 60 minutes. Will resume evaluation at 2025-10-20T16:00:00Z"
}
```

---

## 5. Test Alert Rule (Send Notification Immediately)

### Request

**Method**: `POST`
**Path**: `/api/alert-rules/{rule_id}/test`
**Authentication**: Admin required

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Example Request**:
```bash
curl -X POST "https://signupflow.io/api/alert-rules/alert_rule_abc123/test" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "id": "alert_rule_abc123",
  "test_notification_sent": true,
  "channels_notified": ["slack", "email"],
  "notification_results": {
    "slack": {
      "success": true,
      "response_code": 200,
      "message": "ok"
    },
    "email": {
      "success": true,
      "recipients": ["admin@church.com", "ops@church.com"],
      "message": "Email sent successfully"
    }
  },
  "message": "Test notification sent successfully to all channels"
}
```

**Error (500 Internal Server Error)** - Notification Failed:
```json
{
  "error": "notification_failed",
  "message": "Failed to send test notification",
  "details": {
    "slack": {
      "success": false,
      "error": "invalid_webhook_url",
      "message": "Webhook URL returned 404 Not Found"
    },
    "email": {
      "success": true
    }
  }
}
```

---

## Alert Rule Evaluation (Background Process)

**Implementation**: Cron job runs every 5 minutes to evaluate all active alert rules.

**Pseudo-code** (`api/services/alerting_service.py`):
```python
async def evaluate_alert_rules():
    """Evaluate all active alert rules and send notifications."""
    db = next(get_db())

    # Get all active rules (enabled, not snoozed)
    rules = db.query(AlertRule).filter(
        AlertRule.enabled == True,
        or_(
            AlertRule.snoozed_until == None,
            AlertRule.snoozed_until < datetime.utcnow()
        )
    ).all()

    for rule in rules:
        # Skip if last triggered within cooldown period (15 minutes)
        if rule.last_triggered_at:
            cooldown_minutes = 15
            if (datetime.utcnow() - rule.last_triggered_at).total_seconds() < cooldown_minutes * 60:
                continue

        # Query recent metrics
        recent_metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.org_id == rule.org_id,
            PerformanceMetric.metric_type == rule.metric_type,
            PerformanceMetric.timestamp >= datetime.utcnow() - timedelta(minutes=rule.evaluation_interval_minutes)
        ).all()

        if not recent_metrics:
            continue

        # Calculate aggregate value (avg, p95, max, etc.)
        metric_values = [m.value for m in recent_metrics]
        if rule.metric_type == "response_time":
            # Use P95 for response time
            aggregate_value = percentile(metric_values, 95)
        else:
            # Use average for other metrics
            aggregate_value = sum(metric_values) / len(metric_values)

        # Evaluate threshold
        threshold_met = False
        if rule.threshold_operator == "gt":
            threshold_met = aggregate_value > rule.threshold_value
        elif rule.threshold_operator == "gte":
            threshold_met = aggregate_value >= rule.threshold_value
        # ... other operators

        # Send notification if threshold met
        if threshold_met:
            await send_alert_notification(rule, aggregate_value)
            rule.last_triggered_at = datetime.utcnow()
            db.commit()
```

**Slack Notification Format**:
```json
{
  "text": "🚨 Alert: High Error Rate",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*🚨 Alert: High Error Rate*\n\n*Current Value:* 2.5%\n*Threshold:* > 1.0%\n*Organization:* Church Example\n*Time:* 2025-10-20 14:30:00 UTC"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "View Dashboard"},
          "url": "https://signupflow.io/app/monitoring"
        },
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "Snooze 1 Hour"},
          "url": "https://signupflow.io/api/alert-rules/alert_rule_abc123/snooze"
        }
      ]
    }
  ]
}
```

**Email Notification Template**:
```html
Subject: 🚨 Alert: High Error Rate - SignUpFlow

<h2>🚨 Alert: High Error Rate</h2>

<p><strong>Current Value:</strong> 2.5%</p>
<p><strong>Threshold:</strong> > 1.0%</p>
<p><strong>Organization:</strong> Church Example</p>
<p><strong>Time:</strong> 2025-10-20 14:30:00 UTC</p>

<p><a href="https://signupflow.io/app/monitoring">View Dashboard</a></p>
<p><a href="https://signupflow.io/api/alert-rules/alert_rule_abc123/snooze">Snooze for 1 Hour</a></p>

<hr>
<p><small>This is an automated alert from SignUpFlow. To manage alert rules, visit the <a href="https://signupflow.io/app/admin">Admin Console</a>.</small></p>
```

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_alerting_service.py
def test_evaluate_threshold_gt():
    """Test threshold evaluation with gt operator."""
    assert evaluate_threshold(value=150, operator="gt", threshold=100) == True
    assert evaluate_threshold(value=50, operator="gt", threshold=100) == False

def test_calculate_p95():
    """Test P95 calculation."""
    values = [100, 150, 200, 250, 300, 350, 400, 450, 500, 1000]
    p95 = percentile(values, 95)
    assert p95 == 950  # 95th percentile
```

### Integration Tests

```python
# tests/integration/test_alert_rules_api.py
def test_create_alert_rule(client, admin_auth_headers, test_org):
    """Test POST /api/alert-rules endpoint."""
    response = client.post(
        f"/api/alert-rules?org_id={test_org.id}",
        json={
            "name": "Test Alert",
            "metric_type": "error_rate",
            "threshold_value": 1.0,
            "threshold_operator": "gt",
            "evaluation_interval_minutes": 5,
            "notification_channels": ["slack"],
            "notification_config": {"slack_webhook_url": "https://test.com/webhook"}
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Alert"

def test_snooze_alert_rule(client, admin_auth_headers, test_alert_rule):
    """Test POST /api/alert-rules/{id}/snooze endpoint."""
    response = client.post(
        f"/api/alert-rules/{test_alert_rule.id}/snooze",
        json={"duration_minutes": 60},
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "snoozed_until" in data
```

### E2E Tests

```python
# tests/e2e/test_alerting_workflow.py
def test_alert_configuration_workflow(page: Page):
    """Test complete alert configuration and testing workflow."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    page.fill('[data-i18n-placeholder="auth.email"]', "admin@test.com")
    page.fill('[data-i18n-placeholder="auth.password"]', "password123")
    page.click('[data-i18n="common.buttons.login"]')

    # Navigate to alert rules
    page.goto("http://localhost:8000/app/monitoring/alerts")

    # Create new alert rule
    page.click('[data-i18n="monitoring.create_alert_rule"]')
    page.fill('#alert-name', 'High Error Rate Test')
    page.select_option('#metric-type', 'error_rate')
    page.fill('#threshold-value', '1.0')
    page.select_option('#threshold-operator', 'gt')
    page.check('#notification-slack')
    page.fill('#slack-webhook-url', 'https://hooks.slack.com/test')
    page.click('[data-i18n="common.buttons.create"]')

    # Verify alert rule created
    expect(page.locator('text=High Error Rate Test')).to_be_visible()

    # Test alert notification
    page.click('[data-i18n="monitoring.test_alert"]')
    expect(page.locator('[data-i18n="monitoring.test_notification_sent"]')).to_be_visible()
```

---

## Internationalization (i18n)

**Translation Keys**:
```json
// locales/en/monitoring.json
{
  "alert_rules": "Alert Rules",
  "create_alert_rule": "Create Alert Rule",
  "alert_name": "Alert Name",
  "metric_to_monitor": "Metric to Monitor",
  "threshold": "Threshold",
  "notification_channels": "Notification Channels",
  "test_alert": "Send Test Alert",
  "test_notification_sent": "Test notification sent successfully",
  "snooze_alert": "Snooze Alert",
  "alert_snoozed": "Alert snoozed for {duration} minutes"
}
```

---

**Last Updated**: 2025-10-20
**Status**: Complete API specification for alert rules and notifications
**Related**: data-model.md (AlertRule entity), metrics_endpoints.md (metrics for evaluation)
