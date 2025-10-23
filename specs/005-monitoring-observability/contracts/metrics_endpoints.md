# API Contract: Performance Metrics Endpoints

**Feature**: Monitoring & Observability Platform
**Purpose**: Performance metrics CRUD API for response times, database queries, memory usage, and error rates

---

## Endpoint Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/metrics` | POST | Admin | Record performance metric |
| `/api/metrics` | GET | Authenticated | Query metrics (filtered by org_id) |
| `/api/metrics/summary` | GET | Authenticated | Get aggregated metrics summary |

**Note**: Metrics are automatically captured by FastAPI middleware. Manual POST endpoint used for custom metrics or testing.

---

## 1. Record Performance Metric

### Request

**Method**: `POST`
**Path**: `/api/metrics?org_id={org_id}`
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
  "timestamp": "2025-10-20T14:30:52Z"
}
```

**Field Definitions**:
- `metric_type`: Type of metric (`response_time`, `db_query_count`, `memory_usage`, `error_rate`, `cpu_usage`)
- `value`: Numeric metric value (e.g., `152.34` ms)
- `unit`: Unit of measurement (`ms`, `count`, `MB`, `percentage`)
- `metadata`: Optional additional context (endpoint, status code, percentiles)
- `timestamp`: When metric was recorded (defaults to NOW() if omitted)

**Example Request**:
```bash
curl -X POST "https://signupflow.io/api/metrics?org_id=org_church_12345" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "metric_type": "response_time",
    "value": 152.34,
    "unit": "ms",
    "metadata": {"endpoint": "/api/events", "method": "GET", "status_code": 200},
    "timestamp": "2025-10-20T14:30:52Z"
  }'
```

### Response

**Success (201 Created)**:
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
    "status_code": 200
  },
  "timestamp": "2025-10-20T14:30:52Z",
  "created_at": "2025-10-20T14:30:52Z"
}
```

**Error (400 Bad Request)** - Invalid Metric Type:
```json
{
  "error": "invalid_metric_type",
  "message": "Invalid metric_type. Must be one of: response_time, db_query_count, memory_usage, error_rate, cpu_usage",
  "valid_types": ["response_time", "db_query_count", "memory_usage", "error_rate", "cpu_usage"]
}
```

**Error (403 Forbidden)** - Not Admin:
```json
{
  "error": "admin_access_required",
  "message": "Admin role required to record metrics manually."
}
```

**Error (422 Unprocessable Entity)** - Missing Required Field:
```json
{
  "error": "validation_error",
  "message": "Field 'metric_type' is required.",
  "field": "metric_type"
}
```

---

## 2. Query Performance Metrics

### Request

**Method**: `GET`
**Path**: `/api/metrics?org_id={org_id}&metric_type={type}&start_date={start}&end_date={end}&limit={limit}&offset={offset}`
**Authentication**: Authenticated user (JWT required)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `org_id` | String | Yes | Organization ID | `org_church_12345` |
| `metric_type` | String | No | Filter by metric type | `response_time` |
| `start_date` | ISO 8601 | No | Start date (inclusive) | `2025-10-01T00:00:00Z` |
| `end_date` | ISO 8601 | No | End date (inclusive) | `2025-10-20T23:59:59Z` |
| `limit` | Integer | No | Max results (default: 100, max: 1000) | `100` |
| `offset` | Integer | No | Pagination offset (default: 0) | `0` |

**Example Request**:
```bash
# Get last 100 response_time metrics
curl "https://signupflow.io/api/metrics?org_id=org_church_12345&metric_type=response_time&limit=100" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Get error_rate metrics for October 2025
curl "https://signupflow.io/api/metrics?org_id=org_church_12345&metric_type=error_rate&start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "metrics": [
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
    },
    {
      "id": "metric_20251020_143055_def456",
      "org_id": "org_church_12345",
      "metric_type": "response_time",
      "value": 165.21,
      "unit": "ms",
      "metadata": {
        "endpoint": "/api/people",
        "method": "GET",
        "status_code": 200
      },
      "timestamp": "2025-10-20T14:30:55Z",
      "created_at": "2025-10-20T14:30:55Z"
    }
  ],
  "pagination": {
    "total": 1234,
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

**Error (401 Unauthorized)** - No Authentication:
```json
{
  "error": "authentication_required",
  "message": "Authentication required."
}
```

**Error (403 Forbidden)** - Wrong Organization:
```json
{
  "error": "access_denied",
  "message": "You don't have permission to access this organization's metrics."
}
```

**Error (400 Bad Request)** - Invalid Date Format:
```json
{
  "error": "invalid_date_format",
  "message": "Invalid start_date format. Expected ISO 8601: YYYY-MM-DDTHH:MM:SSZ",
  "field": "start_date",
  "provided": "2025-10-01"
}
```

---

## 3. Get Metrics Summary (Aggregated)

### Request

**Method**: `GET`
**Path**: `/api/metrics/summary?org_id={org_id}&metric_type={type}&start_date={start}&end_date={end}&aggregation={agg}`
**Authentication**: Authenticated user (JWT required)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `org_id` | String | Yes | Organization ID | `org_church_12345` |
| `metric_type` | String | Yes | Metric type to aggregate | `response_time` |
| `start_date` | ISO 8601 | No | Start date (default: 7 days ago) | `2025-10-13T00:00:00Z` |
| `end_date` | ISO 8601 | No | End date (default: now) | `2025-10-20T23:59:59Z` |
| `aggregation` | String | No | Aggregation function (default: `avg`) | `avg`, `min`, `max`, `p50`, `p95`, `p99` |

**Example Request**:
```bash
# Get average response time for last 7 days
curl "https://signupflow.io/api/metrics/summary?org_id=org_church_12345&metric_type=response_time&aggregation=avg" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Get P95 response time for October 2025
curl "https://signupflow.io/api/metrics/summary?org_id=org_church_12345&metric_type=response_time&aggregation=p95&start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Get error rate summary
curl "https://signupflow.io/api/metrics/summary?org_id=org_church_12345&metric_type=error_rate&aggregation=max" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)** - Average Response Time:
```json
{
  "org_id": "org_church_12345",
  "metric_type": "response_time",
  "aggregation": "avg",
  "value": 162.45,
  "unit": "ms",
  "start_date": "2025-10-13T00:00:00Z",
  "end_date": "2025-10-20T23:59:59Z",
  "sample_count": 12543,
  "breakdown_by_endpoint": [
    {"endpoint": "/api/events", "avg": 145.2, "count": 5432},
    {"endpoint": "/api/people", "avg": 185.7, "count": 3210},
    {"endpoint": "/api/solver/solve", "avg": 350.1, "count": 234}
  ]
}
```

**Success (200 OK)** - P95 Response Time:
```json
{
  "org_id": "org_church_12345",
  "metric_type": "response_time",
  "aggregation": "p95",
  "value": 452.30,
  "unit": "ms",
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-31T23:59:59Z",
  "sample_count": 54321,
  "percentiles": {
    "p50": 165.2,
    "p75": 250.1,
    "p90": 380.5,
    "p95": 452.3,
    "p99": 1200.7
  }
}
```

**Success (200 OK)** - Error Rate Summary:
```json
{
  "org_id": "org_church_12345",
  "metric_type": "error_rate",
  "aggregation": "max",
  "value": 2.5,
  "unit": "percentage",
  "start_date": "2025-10-13T00:00:00Z",
  "end_date": "2025-10-20T23:59:59Z",
  "sample_count": 144,
  "timeline": [
    {"date": "2025-10-13", "error_rate": 0.5},
    {"date": "2025-10-14", "error_rate": 1.2},
    {"date": "2025-10-15", "error_rate": 0.8},
    {"date": "2025-10-16", "error_rate": 2.5},
    {"date": "2025-10-17", "error_rate": 1.1},
    {"date": "2025-10-18", "error_rate": 0.6},
    {"date": "2025-10-19", "error_rate": 0.9},
    {"date": "2025-10-20", "error_rate": 1.3}
  ]
}
```

**Field Definitions**:
- `value`: Aggregated metric value
- `sample_count`: Number of data points used in aggregation
- `breakdown_by_endpoint`: Response time breakdown by API endpoint (for `response_time` metrics)
- `percentiles`: Full percentile distribution (for `p95`, `p99` aggregations)
- `timeline`: Daily breakdown (for all metrics)

**Error (400 Bad Request)** - Invalid Aggregation Function:
```json
{
  "error": "invalid_aggregation",
  "message": "Invalid aggregation function. Must be one of: avg, min, max, p50, p95, p99",
  "valid_aggregations": ["avg", "min", "max", "p50", "p95", "p99"]
}
```

---

## Automatic Metric Collection (Middleware)

**Implementation**: FastAPI middleware automatically captures metrics for all API requests.

**Code Example** (`api/services/metrics_service.py`):
```python
import time
from fastapi import Request
from api.models import PerformanceMetric
from api.database import get_db

async def metrics_middleware(request: Request, call_next):
    """Capture request metrics automatically."""
    start_time = time.time()

    response = await call_next(request)

    response_time_ms = (time.time() - start_time) * 1000

    # Extract org_id from query params or JWT token
    org_id = request.query_params.get("org_id")

    if org_id:
        db = next(get_db())
        metric = PerformanceMetric(
            id=f"metric_{int(time.time())}_{secrets.token_hex(6)}",
            org_id=org_id,
            metric_type="response_time",
            value=round(response_time_ms, 2),
            unit="ms",
            metadata={
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code
            },
            timestamp=datetime.utcnow()
        )
        db.add(metric)
        db.commit()

    return response
```

**Registered in `api/main.py`**:
```python
from api.services.metrics_service import metrics_middleware

app = FastAPI()
app.middleware("http")(metrics_middleware)
```

---

## Frontend Integration

### Metrics Dashboard Component

**JavaScript Module** (`frontend/js/monitoring-dashboard.js`):
```javascript
// Fetch metrics summary for dashboard chart
async function loadMetricsSummary(metricType, days = 7) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const response = await authFetch(
        `/api/metrics/summary?org_id=${currentUser.org_id}&metric_type=${metricType}&start_date=${startDate.toISOString()}&aggregation=avg`
    );

    const data = await response.json();

    // Render Chart.js line chart
    renderMetricsChart(data.timeline, metricType);
}

// Render response time chart
function renderMetricsChart(timelineData, metricType) {
    const ctx = document.getElementById('metricsChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timelineData.map(d => d.date),
            datasets: [{
                label: metricType === 'response_time' ? 'Avg Response Time (ms)' : 'Error Rate (%)',
                data: timelineData.map(d => metricType === 'response_time' ? d.avg : d.error_rate),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load metrics on page load
document.addEventListener('DOMContentLoaded', () => {
    loadMetricsSummary('response_time', 7);
    loadMetricsSummary('error_rate', 7);
});
```

**HTML Template** (`frontend/index.html`):
```html
<div id="monitoring-dashboard" style="display:none;">
    <h2 data-i18n="monitoring.dashboard_title">Performance Metrics</h2>

    <div class="metrics-grid">
        <div class="metric-card">
            <h3 data-i18n="monitoring.response_time">Response Time</h3>
            <canvas id="responseTimeChart"></canvas>
        </div>

        <div class="metric-card">
            <h3 data-i18n="monitoring.error_rate">Error Rate</h3>
            <canvas id="errorRateChart"></canvas>
        </div>
    </div>
</div>
```

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_metrics_service.py
def test_create_performance_metric():
    """Test metric creation with valid data."""
    metric = PerformanceMetric(
        id="metric_test_123",
        org_id="org_test",
        metric_type="response_time",
        value=152.34,
        unit="ms",
        timestamp=datetime.utcnow()
    )
    assert metric.metric_type == "response_time"
    assert metric.value == 152.34
```

### Integration Tests

```python
# tests/integration/test_metrics_api.py
def test_post_metric_endpoint(client, auth_headers, test_org):
    """Test POST /api/metrics endpoint."""
    response = client.post(
        f"/api/metrics?org_id={test_org.id}",
        json={
            "metric_type": "response_time",
            "value": 152.34,
            "unit": "ms",
            "metadata": {"endpoint": "/api/events"}
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metric_type"] == "response_time"
    assert data["value"] == 152.34

def test_get_metrics_summary(client, auth_headers, test_org):
    """Test GET /api/metrics/summary endpoint."""
    response = client.get(
        f"/api/metrics/summary?org_id={test_org.id}&metric_type=response_time&aggregation=avg",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert "sample_count" in data
```

### E2E Tests

```python
# tests/e2e/test_metrics_dashboard.py
def test_metrics_dashboard_loads_charts(page: Page):
    """Test metrics dashboard displays charts correctly."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    page.fill('[data-i18n-placeholder="auth.email"]', "admin@test.com")
    page.fill('[data-i18n-placeholder="auth.password"]', "password123")
    page.click('[data-i18n="common.buttons.login"]')

    # Navigate to monitoring dashboard
    page.goto("http://localhost:8000/app/monitoring")

    # Verify charts rendered
    expect(page.locator('#responseTimeChart')).to_be_visible()
    expect(page.locator('#errorRateChart')).to_be_visible()

    # Verify chart data loaded
    expect(page.locator('.metric-card')).to_have_count(2)
```

---

## Internationalization (i18n)

**Translation Keys**:
```json
// locales/en/monitoring.json
{
  "dashboard_title": "Performance Metrics",
  "response_time": "Response Time",
  "error_rate": "Error Rate",
  "avg_label": "Average",
  "p95_label": "95th Percentile",
  "last_7_days": "Last 7 Days",
  "last_30_days": "Last 30 Days"
}
```

---

**Last Updated**: 2025-10-20
**Status**: Complete API specification for performance metrics
**Related**: data-model.md (PerformanceMetric entity), alert_rules_endpoints.md (uses metrics for alerts)
