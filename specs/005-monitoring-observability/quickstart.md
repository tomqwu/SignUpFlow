# Quick Start: Monitoring & Observability Platform

**Feature**: 005-monitoring-observability
**Purpose**: Local testing guide for Sentry error tracking, metrics collection, alert rules, and status page

**Estimated Setup Time**: 15 minutes

---

## Prerequisites

- SignUpFlow development environment running (see `docs/QUICK_START.md`)
- Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)
- npm installed (`sudo apt install npm`)
- PostgreSQL database initialized (`roster.db` for dev, PostgreSQL for production)
- Admin account created

---

## 1. Sentry Error Tracking Setup

### Step 1.1: Create Free Sentry Account

```bash
# Go to https://sentry.io/signup/
# Create free account (5K events/month free tier)
# Create new project: "SignUpFlow"
# Copy DSN (Data Source Name) - looks like:
# https://abc123@o123456.ingest.sentry.io/789012
```

### Step 1.2: Configure Sentry DSN

```bash
# Add Sentry DSN to .env file
cat >> .env << 'EOF'
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/789012
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1
EOF

# Add to .env.example (for team)
cat >> .env.example << 'EOF'
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1
EOF
```

### Step 1.3: Install Sentry SDK

```bash
# Add Sentry SDK to Python dependencies
poetry add sentry-sdk[fastapi]

# Verify installation
poetry run python -c "import sentry_sdk; print(sentry_sdk.__version__)"
```

### Step 1.4: Initialize Sentry in FastAPI App

**File**: `api/main.py`

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os

# Initialize Sentry
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration()
        ],
        # Set custom tags
        before_send=add_org_context
    )

def add_org_context(event, hint):
    """Add org_id context to Sentry events."""
    # Extract org_id from request context (if available)
    # This is called automatically by Sentry SDK
    return event

app = FastAPI(title="SignUpFlow API")
# ... rest of app setup
```

### Step 1.5: Test Sentry Error Capture

```bash
# Start development server
make run

# Trigger test error
curl http://localhost:8000/api/test-sentry-error

# Check Sentry web UI (https://sentry.io/organizations/your-org/issues/)
# Should see new error: "Test Sentry Error Capture"
```

**Expected Output**:
```
INFO:     Sentry is enabled. DSN: https://***@o123456.ingest.sentry.io/789012
INFO:     Test error sent to Sentry: Test Sentry Error Capture
```

---

## 2. Performance Metrics Collection

### Step 2.1: Create Metrics Middleware

**File**: `api/services/metrics_service.py`

```python
import time
import secrets
from datetime import datetime
from fastapi import Request
from api.models import PerformanceMetric
from api.database import get_db

async def metrics_middleware(request: Request, call_next):
    """Capture request metrics automatically."""
    start_time = time.time()

    response = await call_next(request)

    response_time_ms = (time.time() - start_time) * 1000

    # Extract org_id from query params
    org_id = request.query_params.get("org_id")

    if org_id and org_id.startswith("org_"):  # Valid org_id format
        db = next(get_db())
        try:
            metric = PerformanceMetric(
                id=f"metric_{int(time.time())}_{secrets.token_hex(6)}",
                org_id=org_id,
                metric_type="response_time",
                value=round(response_time_ms, 2),
                unit="ms",
                metadata={
                    "endpoint": str(request.url.path),
                    "method": request.method,
                    "status_code": response.status_code
                },
                timestamp=datetime.utcnow()
            )
            db.add(metric)
            db.commit()
        except Exception as e:
            # Don't fail request if metrics collection fails
            print(f"Metrics collection error: {e}")
        finally:
            db.close()

    return response
```

**File**: `api/main.py`

```python
from api.services.metrics_service import metrics_middleware

app = FastAPI()

# Register metrics middleware
app.middleware("http")(metrics_middleware)
```

### Step 2.2: Test Metrics Collection

```bash
# Make API request with org_id
curl "http://localhost:8000/api/events?org_id=org_test_123" \
  -H "Authorization: Bearer your_jwt_token"

# Query metrics via SQL
poetry run python -c "
from api.database import get_db
from api.models import PerformanceMetric

db = next(get_db())
metrics = db.query(PerformanceMetric).filter(
    PerformanceMetric.org_id == 'org_test_123'
).all()

for m in metrics:
    print(f'{m.timestamp} | {m.metric_type} | {m.value}{m.unit} | {m.metadata}')
"
```

**Expected Output**:
```
2025-10-20 14:30:52 | response_time | 152.34ms | {'endpoint': '/api/events', 'method': 'GET', 'status_code': 200}
2025-10-20 14:30:55 | response_time | 165.21ms | {'endpoint': '/api/people', 'method': 'GET', 'status_code': 200}
```

---

## 3. Alert Rules Configuration

### Step 3.1: Create Alert Rule via API

```bash
# Create high error rate alert
curl -X POST "http://localhost:8000/api/alert-rules?org_id=org_test_123" \
  -H "Authorization: Bearer your_admin_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Error Rate Alert",
    "description": "Alert when error rate exceeds 1%",
    "metric_type": "error_rate",
    "threshold_value": 1.0,
    "threshold_operator": "gt",
    "evaluation_interval_minutes": 5,
    "notification_channels": ["slack"],
    "notification_config": {
      "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    },
    "enabled": true
  }'
```

### Step 3.2: Test Alert Notification

```bash
# Test alert (sends notification immediately)
RULE_ID="alert_rule_abc123"
curl -X POST "http://localhost:8000/api/alert-rules/${RULE_ID}/test" \
  -H "Authorization: Bearer your_admin_jwt_token"
```

**Expected Slack Notification**:
```
🚨 Alert: High Error Rate (TEST)

Current Value: 0.0%
Threshold: > 1.0%
Organization: Test Organization
Time: 2025-10-20 14:30:00 UTC

[View Dashboard] [Snooze 1 Hour]

This is a test notification from SignUpFlow.
```

### Step 3.3: Snooze Alert Rule

```bash
# Snooze alert for 1 hour
curl -X POST "http://localhost:8000/api/alert-rules/${RULE_ID}/snooze" \
  -H "Authorization: Bearer your_admin_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 60}'
```

---

## 4. Papertrail Log Aggregation (Optional)

### Step 4.1: Create Free Papertrail Account

```bash
# Go to https://papertrailapp.com/signup
# Create free account (50MB/day, 7-day retention)
# Get syslog endpoint (e.g., logs.papertrailapp.com:12345)
```

### Step 4.2: Configure Python Logging to Papertrail

**File**: `api/services/logging_service.py`

```python
import logging
from logging.handlers import SysLogHandler
import os

def configure_papertrail_logging():
    """Configure Python logging to send to Papertrail."""
    papertrail_host = os.getenv("PAPERTRAIL_HOST", "logs.papertrailapp.com")
    papertrail_port = int(os.getenv("PAPERTRAIL_PORT", "12345"))

    # Create syslog handler
    syslog = SysLogHandler(address=(papertrail_host, papertrail_port))

    # JSON log format
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    syslog.setFormatter(formatter)

    # Add to root logger
    logging.getLogger().addHandler(syslog)
    logging.getLogger().setLevel(logging.INFO)

# Initialize in api/main.py
configure_papertrail_logging()
```

**File**: `.env`

```bash
PAPERTRAIL_HOST=logs.papertrailapp.com
PAPERTRAIL_PORT=12345
```

### Step 4.3: Test Papertrail Logging

```bash
# Trigger log message
poetry run python -c "
import logging
from api.services.logging_service import configure_papertrail_logging

configure_papertrail_logging()
logging.info('Test log message from SignUpFlow')
"

# Check Papertrail web UI (https://papertrailapp.com/events)
# Should see: "Test log message from SignUpFlow"
```

---

## 5. Monitoring Dashboard (Frontend)

### Step 5.1: Create Metrics Dashboard Component

**File**: `frontend/js/monitoring-dashboard.js`

```javascript
// Metrics Dashboard Module
import { authFetch } from './auth.js';
import i18n from './i18n.js';

async function loadMetricsSummary(metricType, days = 7) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    try {
        const response = await authFetch(
            `/api/metrics/summary?org_id=${currentUser.org_id}&metric_type=${metricType}&start_date=${startDate.toISOString()}&aggregation=avg`
        );

        const data = await response.json();

        // Render Chart.js line chart
        renderMetricsChart(data.timeline || [], metricType);
    } catch (error) {
        console.error('Failed to load metrics:', error);
        showToast(i18n.t('monitoring.metrics_load_error'), 'error');
    }
}

function renderMetricsChart(timelineData, metricType) {
    const canvasId = metricType === 'response_time' ? 'responseTimeChart' : 'errorRateChart';
    const ctx = document.getElementById(canvasId)?.getContext('2d');

    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timelineData.map(d => d.date),
            datasets: [{
                label: metricType === 'response_time' ? 'Avg Response Time (ms)' : 'Error Rate (%)',
                data: timelineData.map(d => metricType === 'response_time' ? d.avg : d.error_rate),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Auto-load on page navigation
window.addEventListener('navigated', () => {
    if (window.location.pathname === '/app/monitoring') {
        loadMetricsSummary('response_time', 7);
        loadMetricsSummary('error_rate', 7);
    }
});

export { loadMetricsSummary, renderMetricsChart };
```

### Step 5.2: Add Monitoring Dashboard to Router

**File**: `frontend/js/router.js`

```javascript
const routes = {
    // ... existing routes
    '/app/monitoring': async () => {
        document.getElementById('main-app').style.display = 'none';
        document.getElementById('monitoring-dashboard').style.display = 'block';

        // Load metrics
        const { loadMetricsSummary } = await import('./monitoring-dashboard.js');
        loadMetricsSummary('response_time', 7);
        loadMetricsSummary('error_rate', 7);
    }
};
```

### Step 5.3: Add Monitoring Dashboard HTML

**File**: `frontend/index.html`

```html
<!-- Monitoring Dashboard -->
<div id="monitoring-dashboard" style="display:none;">
    <h2 data-i18n="monitoring.dashboard_title">Performance Metrics</h2>

    <div class="metrics-grid">
        <div class="metric-card">
            <h3 data-i18n="monitoring.response_time">Response Time</h3>
            <div style="height: 300px;">
                <canvas id="responseTimeChart"></canvas>
            </div>
        </div>

        <div class="metric-card">
            <h3 data-i18n="monitoring.error_rate">Error Rate</h3>
            <div style="height: 300px;">
                <canvas id="errorRateChart"></canvas>
            </div>
        </div>
    </div>

    <div class="alert-rules-section">
        <h3 data-i18n="monitoring.alert_rules">Alert Rules</h3>
        <button data-i18n="monitoring.create_alert_rule" onclick="createAlertRule()">
            Create Alert Rule
        </button>
        <div id="alert-rules-list"></div>
    </div>
</div>
```

### Step 5.4: Install Chart.js

```bash
# Install Chart.js via npm
npm install chart.js

# Or include via CDN in frontend/index.html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### Step 5.5: Test Monitoring Dashboard

```bash
# Start development server
make run

# Navigate to monitoring dashboard
open http://localhost:8000/app/monitoring

# Should see:
# - Response Time chart (last 7 days)
# - Error Rate chart (last 7 days)
# - Alert Rules section
```

---

## 6. Status Page (Public)

### Step 6.1: Create Status Page HTML

**File**: `frontend/status.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignUpFlow Status</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .status-operational { color: green; }
        .status-degraded { color: orange; }
        .status-down { color: red; }
        .incident { border-left: 4px solid #ccc; padding: 10px; margin: 10px 0; }
        .incident.critical { border-left-color: red; }
    </style>
</head>
<body>
    <h1>SignUpFlow Status</h1>

    <div id="current-status">
        <h2>Current Status: <span id="status-indicator" class="status-operational">All Systems Operational</span></h2>
    </div>

    <div id="incidents">
        <h2>Recent Incidents</h2>
        <div id="incidents-list"></div>
    </div>

    <script>
        async function loadStatusPage() {
            // Fetch status from API (no authentication required)
            const response = await fetch('/api/status-page/current');
            const data = await response.json();

            // Update status indicator
            document.getElementById('status-indicator').textContent = data.status;
            document.getElementById('status-indicator').className = `status-${data.status.toLowerCase().replace(' ', '-')}`;

            // Load recent incidents
            const incidentsResponse = await fetch('/api/status-page/incidents?limit=10');
            const incidents = await incidentsResponse.json();

            const incidentsList = document.getElementById('incidents-list');
            incidents.incidents.forEach(incident => {
                const div = document.createElement('div');
                div.className = `incident ${incident.severity}`;
                div.innerHTML = `
                    <h3>${incident.title}</h3>
                    <p><strong>Status:</strong> ${incident.status} | <strong>Started:</strong> ${new Date(incident.started_at).toLocaleString()}</p>
                    <p>${incident.description}</p>
                `;
                incidentsList.appendChild(div);
            });
        }

        loadStatusPage();
        // Refresh every 60 seconds
        setInterval(loadStatusPage, 60000);
    </script>
</body>
</html>
```

### Step 6.2: Test Status Page

```bash
# Start development server
make run

# Navigate to status page
open http://localhost:8000/status.html

# Should see:
# - Current Status: All Systems Operational
# - Recent Incidents (empty if no incidents)
```

---

## 7. Full Stack Testing

### Step 7.1: Trigger Error and Verify Sentry Capture

```bash
# Trigger deliberate error
curl "http://localhost:8000/api/events/nonexistent_id?org_id=org_test_123" \
  -H "Authorization: Bearer your_jwt_token"

# Check Sentry dashboard
# Should see error: "Event not found: nonexistent_id"
```

### Step 7.2: Generate Metrics and Verify Dashboard

```bash
# Make 100 API requests to generate metrics
for i in {1..100}; do
  curl -s "http://localhost:8000/api/events?org_id=org_test_123" \
    -H "Authorization: Bearer your_jwt_token" > /dev/null
  echo "Request $i completed"
done

# Navigate to monitoring dashboard
open http://localhost:8000/app/monitoring

# Should see response time chart populated with data
```

### Step 7.3: Test Alert Rule Evaluation

```bash
# Create error rate alert with low threshold (for testing)
curl -X POST "http://localhost:8000/api/alert-rules?org_id=org_test_123" \
  -H "Authorization: Bearer your_admin_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Error Alert",
    "metric_type": "error_rate",
    "threshold_value": 0.5,
    "threshold_operator": "gt",
    "evaluation_interval_minutes": 5,
    "notification_channels": ["slack"],
    "notification_config": {"slack_webhook_url": "YOUR_WEBHOOK_URL"},
    "enabled": true
  }'

# Trigger 10 errors (10% error rate)
for i in {1..10}; do
  curl "http://localhost:8000/api/events/error_test" \
    -H "Authorization: Bearer your_jwt_token"
done

# Wait 5 minutes for alert evaluation (or run manually)
poetry run python -c "
from api.services.alerting_service import evaluate_alert_rules
import asyncio
asyncio.run(evaluate_alert_rules())
"

# Check Slack for alert notification
```

---

## 8. Production Deployment Notes

### Sentry Configuration

```bash
# Production .env
SENTRY_DSN=https://your_production_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=1.0  # 100% sampling for production

# Enable Sentry Performance Monitoring (optional, $26/month)
SENTRY_ENABLE_PERFORMANCE=true
```

### Metrics Retention

```bash
# Schedule daily cleanup job (delete metrics >90 days)
crontab -e

# Add:
0 2 * * * cd /path/to/signupflow && poetry run python -c "from api.services.metrics_service import cleanup_old_metrics; cleanup_old_metrics()"
```

### Alert Rule Evaluation Cron Job

```bash
# Schedule alert evaluation every 5 minutes
crontab -e

# Add:
*/5 * * * * cd /path/to/signupflow && poetry run python -c "from api.services.alerting_service import evaluate_alert_rules; import asyncio; asyncio.run(evaluate_alert_rules())"
```

### Papertrail Log Forwarding

```bash
# Configure rsyslog to forward all logs
sudo nano /etc/rsyslog.d/90-papertrail.conf

# Add:
*.* @logs.papertrailapp.com:12345

# Restart rsyslog
sudo systemctl restart rsyslog
```

---

## Troubleshooting

### Issue: Sentry not capturing errors

**Solution**:
```bash
# Verify SENTRY_DSN is set
echo $SENTRY_DSN

# Test Sentry initialization
poetry run python -c "
import sentry_sdk
import os
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
sentry_sdk.capture_message('Test message')
print('Test message sent to Sentry')
"
```

### Issue: Metrics not appearing in dashboard

**Solution**:
```bash
# Check metrics middleware is registered
grep "metrics_middleware" api/main.py

# Query database directly
poetry run python -c "
from api.database import get_db
from api.models import PerformanceMetric
db = next(get_db())
count = db.query(PerformanceMetric).count()
print(f'Total metrics in database: {count}')
"
```

### Issue: Slack notifications not sending

**Solution**:
```bash
# Test webhook URL manually
curl -X POST YOUR_SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message from SignUpFlow"}'

# Expected response: "ok"
```

### Issue: Chart.js not loading

**Solution**:
```bash
# Install Chart.js if missing
npm install chart.js

# Verify Chart.js loaded
curl http://localhost:8000/ | grep "chart.js"
```

---

**Last Updated**: 2025-10-20
**Status**: Complete local testing guide for monitoring & observability platform
**Related**: plan.md (technology stack), data-model.md (entities), contracts/ (API specifications)
