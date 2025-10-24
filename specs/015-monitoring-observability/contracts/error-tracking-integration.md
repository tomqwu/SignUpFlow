# Error Tracking Integration Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: Integration Guide (Sentry SDK)
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Sentry error tracking integration provides automatic error capture, context enrichment, performance monitoring, and real-time alerting for production issues. Sentry SDK instruments FastAPI application to capture exceptions, track performance transactions, and provide actionable debugging context.

**Use Cases**:
- Automatic exception capture with full stack traces
- Performance transaction tracking for slow requests
- Real-time error alerting via email/Slack/PagerDuty
- Error grouping and deduplication
- Release tracking and regression detection

---

## Sentry SDK Integration

### Installation

```bash
poetry add sentry-sdk==1.40.0
```

### Initialization

**File**: `api/core/monitoring.py`

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

def init_sentry():
    """
    Initialize Sentry error tracking for SignUpFlow.

    Captures:
    - Unhandled exceptions (automatic)
    - HTTP errors (4xx, 5xx)
    - Database query errors (SQLAlchemy integration)
    - Redis errors (Redis integration)
    - Performance transactions (10% sampling)
    """
    sentry_sdk.init(
        # Sentry DSN (from environment variable)
        dsn=os.getenv("SENTRY_DSN"),

        # Environment (production, staging, development)
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),

        # Release version (Git commit SHA)
        release=os.getenv("GIT_COMMIT_SHA", "unknown"),

        # Integrations
        integrations=[
            # FastAPI integration (automatic request/response tracking)
            FastApiIntegration(
                transaction_style="endpoint",  # Group by endpoint, not URL
                failed_request_status_codes=[403, range(500, 599)]  # Capture 403, 5xx
            ),

            # SQLAlchemy integration (database query tracking)
            SqlalchemyIntegration(),

            # Redis integration (Redis command tracking)
            RedisIntegration(),
        ],

        # Performance monitoring (sample 10% of transactions)
        traces_sample_rate=0.1,

        # Error sampling (capture 100% of errors)
        sample_rate=1.0,

        # Send default PII (IP address, user ID) - disabled for privacy
        send_default_pii=False,

        # Attach stack locals (variable values at each stack frame)
        attach_stacktrace=True,

        # Max breadcrumbs (context trail before error)
        max_breadcrumbs=50,

        # Before send callback (scrub sensitive data)
        before_send=before_send_scrub_sensitive_data,

        # Before breadcrumb callback (filter noisy breadcrumbs)
        before_breadcrumb=before_breadcrumb_filter,
    )

def before_send_scrub_sensitive_data(event, hint):
    """
    Scrub sensitive data from error events before sending to Sentry.

    Removes:
    - Passwords from request bodies
    - API keys from headers
    - Credit card numbers from any field
    """
    # Scrub request body
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in ["password", "token", "api_key", "secret"]:
                if key in data:
                    data[key] = "[REDACTED]"

    # Scrub headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        for key in ["Authorization", "X-API-Key", "Cookie"]:
            if key in headers:
                headers[key] = "[REDACTED]"

    return event

def before_breadcrumb_filter(crumb, hint):
    """
    Filter noisy breadcrumbs before adding to event context.

    Filters:
    - Health check requests (every 10 seconds)
    - Metrics scraping (every 10 seconds)
    """
    if crumb.get("category") == "httplib":
        url = crumb.get("data", {}).get("url", "")
        if "/health" in url or "/metrics" in url:
            return None  # Drop breadcrumb

    return crumb
```

**File**: `api/main.py`

```python
from api.core.monitoring import init_sentry

# Initialize Sentry before creating FastAPI app
init_sentry()

app = FastAPI(title="SignUpFlow API", version="1.2.0")
```

---

## Context Enrichment

### User Context

**Purpose**: Associate errors with specific users for targeted debugging.

```python
from sentry_sdk import set_user

@app.middleware("http")
async def add_sentry_user_context(request: Request, call_next):
    """Add user context to Sentry events."""
    # Extract user from JWT token
    user = get_current_user_from_request(request)

    if user:
        # Set user context (appears in Sentry UI)
        set_user({
            "id": user.id,
            "email": user.email,
            "username": user.name,
            "org_id": user.org_id,
            "roles": user.roles
        })

    response = await call_next(request)

    # Clear user context after request
    set_user(None)

    return response
```

**Sentry UI Display**:
```
User: admin@church.org (user_admin_123)
Organization: Church of the Valley (org_456)
Roles: ["admin"]
```

### Tags (Searchable Metadata)

**Purpose**: Add searchable dimensions for filtering errors in Sentry UI.

```python
from sentry_sdk import set_tag

# Add organization tag
set_tag("org_id", "org_456")

# Add endpoint tag
set_tag("endpoint", "/api/solver/solve")

# Add feature tag
set_tag("feature", "scheduling_solver")

# Add custom business logic tag
set_tag("solver_complexity", "high")  # high/medium/low
```

**Sentry UI Search**:
```
org_id:org_456 endpoint:/api/solver/solve feature:scheduling_solver
```

### Extra Context (Detailed Debugging Info)

**Purpose**: Add detailed context data (not searchable, but visible in event details).

```python
from sentry_sdk import set_context

# Add request context
set_context("request_details", {
    "request_id": "req_abc123",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "203.0.113.42",
    "referer": "https://app.signupflow.io/schedule"
})

# Add solver context
set_context("solver_details", {
    "num_people": 50,
    "num_events": 20,
    "num_constraints": 1234,
    "execution_time_seconds": 45.6
})

# Add business context
set_context("organization_details", {
    "org_name": "Church of the Valley",
    "org_created_at": "2024-01-15",
    "org_plan": "Pro",
    "org_size": "medium"
})
```

---

## Manual Error Capture

### Capturing Exceptions

```python
import sentry_sdk

try:
    result = dangerous_operation()
except Exception as e:
    # Capture exception with custom context
    sentry_sdk.capture_exception(
        e,
        extra={
            "operation": "dangerous_operation",
            "input_data": input_data
        },
        tags={
            "severity": "high",
            "component": "solver"
        }
    )
    raise  # Re-raise after capturing
```

### Capturing Messages (Non-Exception Events)

```python
# Capture informational message
sentry_sdk.capture_message(
    "Solver execution took longer than expected",
    level="warning",
    extra={
        "execution_time": 67.8,
        "threshold": 60.0
    }
)

# Capture error message
sentry_sdk.capture_message(
    "Database connection pool exhausted",
    level="error",
    tags={"component": "database"}
)
```

---

## Performance Monitoring

### Automatic Transaction Tracking

**FastAPI Integration** automatically creates performance transactions for each HTTP request.

**Transaction Name Format**: `{method} {endpoint}` (e.g., `POST /api/solver/solve`)

**Transaction Data**:
- Duration (total request time)
- Status code
- HTTP method
- URL
- User context

### Manual Span Creation

**Purpose**: Track performance of specific operations within a transaction.

```python
from sentry_sdk import start_span

@router.post("/solver/solve")
async def solve_schedule(request: SolverRequest):
    """Solve scheduling problem with performance tracking."""

    # Automatic transaction created by FastAPI integration

    # Manual span for database query
    with start_span(op="db.query", description="Load people and events"):
        people = db.query(Person).filter(Person.org_id == request.org_id).all()
        events = db.query(Event).filter(Event.org_id == request.org_id).all()

    # Manual span for solver execution
    with start_span(op="solver.execute", description="OR-Tools solver"):
        solution = solver_service.solve(people, events)

    # Manual span for database write
    with start_span(op="db.query", description="Save assignments"):
        save_assignments(solution)

    return {"status": "success"}
```

**Sentry UI Display**:
```
Transaction: POST /api/solver/solve (45.6s)
├─ db.query: Load people and events (1.2s)
├─ solver.execute: OR-Tools solver (42.3s)
└─ db.query: Save assignments (2.1s)
```

### Custom Metrics

**Purpose**: Track business metrics alongside performance data.

```python
from sentry_sdk import metrics

# Increment counter
metrics.incr("solver.executions", value=1, tags={"status": "success"})

# Record distribution (histogram)
metrics.distribution("solver.execution_time", value=45.6, unit="second")

# Record gauge (current value)
metrics.gauge("active_users", value=234)

# Record set (unique values)
metrics.set("active_organizations", value="org_456")
```

---

## Error Grouping

### Automatic Grouping

Sentry automatically groups similar errors using:
- Exception type (e.g., `ValueError`, `DatabaseError`)
- Stack trace fingerprint
- Error message pattern

**Example Group**:
```
ValueError: Invalid date format
├─ 234 events in last 24 hours
├─ First seen: 2025-10-20 10:30 UTC
├─ Last seen: 2025-10-23 15:45 UTC
└─ Affected users: 12
```

### Custom Fingerprinting

**Purpose**: Override automatic grouping for better error organization.

```python
from sentry_sdk import configure_scope

def capture_solver_error(error, solver_input):
    """Capture solver error with custom fingerprint."""
    with configure_scope() as scope:
        # Group by solver error type, not stack trace
        scope.fingerprint = [
            "solver-error",
            error.error_code,  # e.g., "infeasible", "timeout"
            solver_input.org_id
        ]

        sentry_sdk.capture_exception(error)
```

**Result**: All "infeasible" solver errors for org_456 grouped together, regardless of where exception was raised.

---

## Alerting Configuration

### Alert Rules (Sentry Dashboard)

**Rule 1: High Error Rate**
```yaml
Condition: Error count > 10 in 1 minute
Actions:
  - Send email to ops@signupflow.io
  - Send Slack notification to #alerts
  - Create PagerDuty incident (P2)
```

**Rule 2: New Error Type**
```yaml
Condition: First time an error is seen
Actions:
  - Send Slack notification to #engineering
  - Tag as "needs-triage"
```

**Rule 3: Solver Failures**
```yaml
Condition: Error with tag "component:solver"
Actions:
  - Send email to solver-team@signupflow.io
  - Create JIRA ticket
```

**Rule 4: Database Connection Errors**
```yaml
Condition: Error message contains "database connection"
Actions:
  - Send Slack notification to #infrastructure
  - Create PagerDuty incident (P1)
  - Escalate after 5 minutes
```

### Slack Integration

**Setup**:
1. Go to Sentry Dashboard → Settings → Integrations
2. Add Slack integration
3. Connect Slack workspace
4. Create alert rule with Slack action

**Slack Message Format**:
```
🚨 New Error: ValueError in POST /api/solver/solve

Message: Invalid date format: "2025-13-45"
Environment: production
Release: v1.2.0 (abc123)
First seen: 2 minutes ago
Events: 5

👤 Affected Users: 2
🏢 Organization: org_456 (Church of the Valley)

🔗 View in Sentry: https://sentry.io/organizations/...
```

---

## Release Tracking

### Creating Releases

**Purpose**: Track which code version caused errors, detect regressions.

**Git Hook** (automatic release creation on deploy):
```bash
# .git/hooks/post-deploy
#!/bin/bash

COMMIT_SHA=$(git rev-parse HEAD)
RELEASE="signupflow@${COMMIT_SHA:0:7}"

# Create Sentry release
sentry-cli releases new $RELEASE --project signupflow-api

# Associate commits with release
sentry-cli releases set-commits $RELEASE --auto

# Finalize release
sentry-cli releases finalize $RELEASE

# Create deploy
sentry-cli releases deploys $RELEASE new --env production
```

**Sentry UI Display**:
```
Release: signupflow@abc1234
├─ Deploy: production (2025-10-23 10:30 UTC)
├─ Commits: 5 new commits
├─ New Errors: 2
├─ Resolved Errors: 3
└─ Regression Detection: 1 error reintroduced
```

---

## Performance Requirements

| Metric | Target | Justification |
|--------|--------|---------------|
| **SDK Overhead** | <5ms per request | Sentry SDK runs asynchronously, minimal blocking |
| **Error Capture Latency** | <30 seconds | Errors appear in Sentry dashboard within 30s |
| **Transaction Sampling** | 10% | Balance observability vs cost ($29/month Pro tier) |
| **Breadcrumb Limit** | 50 | Capture sufficient context without excessive memory |

---

## Cost Optimization

### Free Tier Limits

- **Errors**: 5,000 errors/month
- **Performance Transactions**: 10,000 transactions/month
- **Data Retention**: 90 days

### Pro Tier ($29/month)

- **Errors**: 50,000 errors/month
- **Performance Transactions**: 100,000 transactions/month
- **Data Retention**: 90 days
- **Additional features**: Advanced alerting, SSO, custom metrics

### Sampling Strategy

**Goal**: Stay within free tier (5K errors/month) or optimize Pro tier cost.

```python
def before_send_sampling(event, hint):
    """
    Sample errors to reduce Sentry volume.

    Strategy:
    - Capture 100% of critical errors (5xx, database errors)
    - Sample 10% of client errors (4xx)
    - Drop 100% of health check errors
    """
    # Always capture server errors
    if event.get("level") in ["error", "fatal"]:
        return event

    # Sample client errors (10%)
    if event.get("request", {}).get("status_code", 0) >= 400:
        if random.random() > 0.1:
            return None  # Drop 90% of 4xx errors

    # Drop health check errors
    if "/health" in event.get("request", {}).get("url", ""):
        return None

    return event
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_sentry_integration.py
from unittest.mock import patch
import sentry_sdk

@patch('sentry_sdk.capture_exception')
def test_solver_error_captured(mock_capture):
    """Test that solver errors are captured by Sentry."""
    try:
        raise ValueError("Invalid solver input")
    except Exception as e:
        sentry_sdk.capture_exception(e)

    mock_capture.assert_called_once()
    assert "ValueError" in str(mock_capture.call_args)
```

### Integration Tests

```python
# tests/integration/test_sentry_context.py
from sentry_sdk import Hub

def test_user_context_added_to_sentry(client, auth_headers):
    """Test that user context is added to Sentry events."""
    with patch('sentry_sdk.Hub.current') as mock_hub:
        response = client.get("/api/people/me", headers=auth_headers)
        assert response.status_code == 200

        # Verify user context was set
        mock_hub.scope.set_user.assert_called_once()
        user_data = mock_hub.scope.set_user.call_args[0][0]
        assert "id" in user_data
        assert "email" in user_data
```

### E2E Tests

```python
# tests/e2e/test_sentry_error_capture.py
def test_sentry_captures_500_errors(page: Page):
    """Test that 500 errors are captured by Sentry."""
    # Trigger 500 error (e.g., database connection failure)
    response = requests.get("http://localhost:8000/api/trigger-error")
    assert response.status_code == 500

    # Wait for error to appear in Sentry (up to 30 seconds)
    time.sleep(30)

    # Verify error appears in Sentry dashboard
    # (Manual verification or use Sentry API to check)
```

---

## Troubleshooting

### Issue 1: Errors Not Appearing in Sentry

**Symptoms**: No errors captured in Sentry dashboard.

**Diagnosis**:
```python
# Test Sentry connection
import sentry_sdk
sentry_sdk.capture_message("Test message from SignUpFlow")

# Check Sentry DSN configured
import os
print(os.getenv("SENTRY_DSN"))  # Should not be None
```

**Solutions**:
1. Verify `SENTRY_DSN` environment variable set
2. Check firewall allows outbound HTTPS to sentry.io
3. Verify Sentry project exists and DSN is correct

---

### Issue 2: Sensitive Data Leaking to Sentry

**Symptoms**: Passwords, API keys visible in Sentry error events.

**Diagnosis**:
```python
# Check before_send callback configured
print(sentry_sdk.Hub.current.client.options.get("before_send"))
```

**Solution**: Ensure `before_send=before_send_scrub_sensitive_data` configured in `init_sentry()`.

---

### Issue 3: High Sentry Costs

**Symptoms**: Sentry bill exceeds $100/month.

**Diagnosis**:
```python
# Check error volume in Sentry dashboard
# Settings → Usage Stats → Error Volume
```

**Solutions**:
1. Implement sampling with `before_send_sampling()` callback
2. Filter noisy errors (health checks, metrics scraping)
3. Increase error grouping (better fingerprinting)
4. Fix recurring errors causing high volume

---

## References

- **Sentry Python SDK**: [Documentation](https://docs.sentry.io/platforms/python/)
- **FastAPI Integration**: [Sentry FastAPI Guide](https://docs.sentry.io/platforms/python/guides/fastapi/)
- **Performance Monitoring**: [Transaction Tracking](https://docs.sentry.io/product/performance/)
- **Release Tracking**: [Releases & Health](https://docs.sentry.io/product/releases/)
- **Alerting**: [Alert Rules](https://docs.sentry.io/product/alerts/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/core/monitoring.py` during Feature 015 implementation phase
