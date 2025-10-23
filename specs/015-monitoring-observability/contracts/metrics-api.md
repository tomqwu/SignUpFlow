# Metrics API Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: REST API Endpoint Specification (Prometheus Format)
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Metrics endpoint exposes application performance metrics in Prometheus text-based exposition format. Prometheus server scrapes this endpoint at configured intervals (default 10 seconds) to collect time-series data for alerting, graphing, and analysis.

**Use Cases**:
- Prometheus server scraping for metrics collection
- Performance monitoring and alerting
- Capacity planning and trend analysis
- SLO/SLI tracking for SRE practices

---

## API Endpoint

### GET /metrics - Prometheus Metrics Exposition

**Purpose**: Expose application metrics in Prometheus text-based format for scraping.

**Authentication**: None (internal network only, firewall protected)

**Request**:
```http
GET /metrics HTTP/1.1
Host: api.signupflow.io
Accept: text/plain
```

**Query Parameters**: None

**Response (200 OK)**:
```
# HELP http_requests_total Total HTTP requests by method, endpoint, and status
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/people",status_code="200"} 145230
http_requests_total{method="POST",endpoint="/api/events",status_code="201"} 23401
http_requests_total{method="GET",endpoint="/api/events",status_code="200"} 89234
http_requests_total{method="PUT",endpoint="/api/people/me",status_code="200"} 12034
http_requests_total{method="POST",endpoint="/api/auth/login",status_code="401"} 234

# HELP http_request_duration_seconds HTTP request latency by method and endpoint
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="0.01"} 98234
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="0.05"} 143201
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="0.1"} 145100
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="0.5"} 145220
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="1.0"} 145228
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="5.0"} 145230
http_request_duration_seconds_bucket{method="GET",endpoint="/api/people",le="+Inf"} 145230
http_request_duration_seconds_sum{method="GET",endpoint="/api/people"} 1234.56
http_request_duration_seconds_count{method="GET",endpoint="/api/people"} 145230

# HELP http_requests_in_progress Current HTTP requests being processed
# TYPE http_requests_in_progress gauge
http_requests_in_progress 12

# HELP database_connections_active Active database connections in pool
# TYPE database_connections_active gauge
database_connections_active 8

# HELP database_query_duration_seconds Database query latency
# TYPE database_query_duration_seconds histogram
database_query_duration_seconds_bucket{query="select_person",le="0.01"} 12034
database_query_duration_seconds_bucket{query="select_person",le="0.05"} 23401
database_query_duration_seconds_bucket{query="select_person",le="0.1"} 24500
database_query_duration_seconds_bucket{query="select_person",le="+Inf"} 24534
database_query_duration_seconds_sum{query="select_person"} 456.78
database_query_duration_seconds_count{query="select_person"} 24534

# HELP solver_executions_total Total solver executions by organization
# TYPE solver_executions_total counter
solver_executions_total{org_id="org_123",status="success"} 45
solver_executions_total{org_id="org_123",status="failure"} 2
solver_executions_total{org_id="org_456",status="success"} 78

# HELP solver_execution_duration_seconds Solver execution time
# TYPE solver_execution_duration_seconds histogram
solver_execution_duration_seconds_bucket{le="1.0"} 23
solver_execution_duration_seconds_bucket{le="5.0"} 89
solver_execution_duration_seconds_bucket{le="10.0"} 120
solver_execution_duration_seconds_bucket{le="+Inf"} 125
solver_execution_duration_seconds_sum 890.12
solver_execution_duration_seconds_count 125

# HELP redis_operations_total Total Redis operations by operation type
# TYPE redis_operations_total counter
redis_operations_total{operation="get",status="success"} 234012
redis_operations_total{operation="set",status="success"} 123401
redis_operations_total{operation="get",status="error"} 12

# HELP authentication_attempts_total Total authentication attempts by status
# TYPE authentication_attempts_total counter
authentication_attempts_total{status="success"} 12034
authentication_attempts_total{status="failed"} 234
authentication_attempts_total{status="rate_limited"} 45

# HELP active_users_count Active users in last 5 minutes (Top-K aggregation)
# TYPE active_users_count gauge
active_users_count{user_id="user_admin_123"} 145
active_users_count{user_id="user_admin_456"} 89
active_users_count{user_id="other"} 234
```

**Content-Type**: `text/plain; version=0.0.4; charset=utf-8`

**Status Codes**:
- `200 OK`: Metrics successfully generated
- `500 Internal Server Error`: Metrics collection failure

---

## Metric Types

### 1. Counter

**Definition**: Monotonically increasing value (can only go up, resets on restart).

**Use Cases**: Total requests, total errors, total events processed.

**Naming Convention**: `*_total` suffix.

**Example**:
```python
from prometheus_client import Counter

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Increment counter
http_requests_total.labels(
    method="GET",
    endpoint="/api/people",
    status_code="200"
).inc()
```

**Prometheus Queries**:
```promql
# Requests per second (rate over 1 minute)
rate(http_requests_total[1m])

# Total requests in last hour
increase(http_requests_total[1h])

# Error rate (4xx + 5xx responses)
rate(http_requests_total{status_code=~"4..|5.."}[1m])
```

---

### 2. Gauge

**Definition**: Value that can go up or down (current state).

**Use Cases**: Active connections, memory usage, queue depth, current temperature.

**Naming Convention**: No specific suffix.

**Example**:
```python
from prometheus_client import Gauge

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Current HTTP requests being processed'
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections in pool'
)

# Set gauge value
http_requests_in_progress.set(12)

# Increment/decrement gauge
http_requests_in_progress.inc()
http_requests_in_progress.dec()
```

**Prometheus Queries**:
```promql
# Current active requests
http_requests_in_progress

# Average active requests over 5 minutes
avg_over_time(http_requests_in_progress[5m])

# Database connection pool utilization (%)
(database_connections_active / database_connections_max) * 100
```

---

### 3. Histogram

**Definition**: Samples observations and counts them in configurable buckets.

**Use Cases**: Request duration, response size, query latency.

**Naming Convention**: `*_seconds` or `*_bytes` suffix, generates `*_bucket`, `*_sum`, `*_count` metrics.

**Example**:
```python
from prometheus_client import Histogram

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]  # Buckets in seconds
)

# Observe value
start_time = time.time()
# ... process request
duration = time.time() - start_time
http_request_duration_seconds.labels(
    method="GET",
    endpoint="/api/people"
).observe(duration)
```

**Prometheus Queries**:
```promql
# p95 latency (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# p50 latency (median)
histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m]))

# Average latency
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

---

### 4. Summary (Not Used)

**Reason**: Histograms preferred over summaries for quantile calculation (more flexible, aggregatable across instances).

---

## Metric Naming Conventions

### SignUpFlow Metric Naming Standard

**Format**: `{namespace}_{subsystem}_{metric_name}_{unit}`

**Rules**:
1. **Namespace**: Always `signupflow_` prefix (or omit for standard metrics)
2. **Subsystem**: Component name (e.g., `http`, `database`, `solver`, `redis`)
3. **Metric Name**: Descriptive name (e.g., `requests`, `connections`, `executions`)
4. **Unit**: Append unit suffix (e.g., `_seconds`, `_bytes`, `_total`, `_ratio`)
5. **Snake Case**: Use underscores, not camelCase or kebab-case
6. **Plurals**: Use plural for countable nouns (e.g., `requests`, `connections`)

**Examples**:
```
✅ http_requests_total
✅ http_request_duration_seconds
✅ database_connections_active
✅ solver_execution_duration_seconds
✅ redis_operations_total

❌ HttpRequestsTotal (wrong case)
❌ http-requests-total (wrong separator)
❌ http_request (missing unit)
❌ request_count (inconsistent naming)
```

---

## Label Best Practices

### Good Labels (Low Cardinality)

**Definition**: Low cardinality labels have bounded, predictable values (e.g., HTTP method, status code).

**Examples**:
```python
# ✅ Good: Bounded values
http_requests_total.labels(
    method="GET",           # 7 values (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
    endpoint="/api/people", # ~50 endpoints
    status_code="200"       # ~15 status codes (200, 201, 400, 401, 403, 404, 500, etc.)
)
# Total cardinality: 7 × 50 × 15 = 5,250 time series (acceptable)
```

### Bad Labels (High Cardinality)

**Definition**: High cardinality labels have unbounded, unpredictable values (e.g., user ID, email, timestamp).

**Examples**:
```python
# ❌ Bad: Unbounded values (cardinality explosion)
http_requests_total.labels(
    user_id="user_123",        # 5,000+ values (unbounded)
    request_id="abc123",       # Infinite values (unique per request)
    timestamp="2025-10-23T..."  # Infinite values (unique per second)
)
# Total cardinality: MILLIONS of time series → Prometheus OOM, InfluxDB cost explosion
```

**Solution**: Use Top-K aggregation for high-cardinality labels:
```python
# ✅ Good: Top-K aggregation (bounded cardinality)
if top_k_tracker.should_track_user(user_id):
    metric_user_label = user_id  # Track top 100 users
else:
    metric_user_label = "other"  # Aggregate remaining users

http_requests_total.labels(user_id=metric_user_label).inc()
# Total cardinality: 101 user labels (100 tracked + 1 "other")
```

---

## SignUpFlow Metrics Reference

### HTTP Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `http_requests_total` | Counter | `method`, `endpoint`, `status_code` | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` | HTTP request latency |
| `http_requests_in_progress` | Gauge | - | Current requests being processed |
| `http_response_size_bytes` | Histogram | `method`, `endpoint` | HTTP response body size |

### Database Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `database_connections_active` | Gauge | - | Active database connections in pool |
| `database_connections_max` | Gauge | - | Maximum database connections configured |
| `database_query_duration_seconds` | Histogram | `query` | Database query latency |
| `database_queries_total` | Counter | `query`, `status` | Total database queries |

### Solver Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `solver_executions_total` | Counter | `org_id`, `status` | Total solver executions |
| `solver_execution_duration_seconds` | Histogram | - | Solver execution time |
| `solver_variables_count` | Histogram | - | Number of variables in constraint problem |
| `solver_constraints_count` | Histogram | - | Number of constraints in problem |

### Redis Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `redis_operations_total` | Counter | `operation`, `status` | Total Redis operations |
| `redis_operation_duration_seconds` | Histogram | `operation` | Redis operation latency |
| `redis_connections_active` | Gauge | - | Active Redis connections |

### Authentication Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `authentication_attempts_total` | Counter | `status` | Total authentication attempts |
| `authentication_duration_seconds` | Histogram | - | Authentication processing time |
| `rate_limit_hits_total` | Counter | `endpoint` | Total rate limit violations |

### Business Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `active_organizations_count` | Gauge | - | Active organizations (Top-K) |
| `active_users_count` | Gauge | `user_id` | Active users in last 5 minutes (Top-K) |
| `events_created_total` | Counter | `org_id` | Total events created (Top-K orgs) |
| `schedules_generated_total` | Counter | `org_id` | Total schedules generated (Top-K orgs) |

---

## Implementation

### Backend Implementation

**File**: `api/routers/metrics.py`

```python
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from starlette.responses import Response

router = APIRouter(tags=["metrics"])

@router.get("/metrics")
def prometheus_metrics():
    """
    Expose Prometheus metrics in text-based exposition format.

    This endpoint is scraped by Prometheus server every 10 seconds.
    Should be fast (<100ms) and lightweight to support frequent scraping.
    """
    # Generate Prometheus text format from default registry
    metrics_output = generate_latest(REGISTRY)

    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )
```

**File**: `api/core/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Current HTTP requests being processed'
)

# Database Metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections in pool'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query latency',
    ['query'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Solver Metrics
solver_executions_total = Counter(
    'solver_executions_total',
    'Total solver executions',
    ['org_id', 'status']
)

solver_execution_duration_seconds = Histogram(
    'solver_execution_duration_seconds',
    'Solver execution time',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)
```

**File**: `api/middleware/prometheus_middleware.py`

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware
from api.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collect HTTP request metrics for Prometheus."""

    async def dispatch(self, request, call_next):
        # Increment in-progress gauge
        http_requests_in_progress.inc()

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Track 500 errors
            status_code = 500
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Decrement in-progress gauge
            http_requests_in_progress.dec()

            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=str(status_code)
            ).inc()

            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

        return response
```

---

## Prometheus Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 10s       # Scrape metrics every 10 seconds
  evaluation_interval: 10s   # Evaluate alerting rules every 10 seconds
  external_labels:
    cluster: 'signupflow-prod'
    environment: 'production'

scrape_configs:
  # SignUpFlow API metrics
  - job_name: 'signupflow-api'
    static_configs:
      - targets:
          - 'api-1:8000'
          - 'api-2:8000'
          - 'api-3:8000'
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s

  # Node exporter (OS-level metrics)
  - job_name: 'node'
    static_configs:
      - targets:
          - 'api-1:9100'
          - 'api-2:9100'

# Remote write to InfluxDB
remote_write:
  - url: "http://influxdb:8086/api/v1/prom/write?db=signupflow"
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_metrics.py
from prometheus_client import REGISTRY

def test_http_requests_total_metric_exists():
    """Test that http_requests_total metric is registered."""
    metrics = [metric.name for metric in REGISTRY.collect()]
    assert 'http_requests_total' in metrics

def test_http_request_duration_buckets():
    """Test that histogram has correct buckets."""
    from api.core.metrics import http_request_duration_seconds
    assert http_request_duration_seconds._buckets == [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, float('inf')]
```

### Integration Tests

```python
# tests/integration/test_metrics_endpoint.py
def test_metrics_endpoint_returns_prometheus_format(client):
    """Test /metrics returns Prometheus text format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    content = response.text
    assert "http_requests_total" in content
    assert "# HELP" in content
    assert "# TYPE" in content
```

---

## Performance Requirements

| Metric | Target | Justification |
|--------|--------|---------------|
| **Response Time** | <100ms | Prometheus scrapes every 10s, must be fast |
| **Memory Overhead** | <50MB | Metrics stored in-memory |
| **CPU Overhead** | <1% | Metric collection lightweight (atomic increments) |
| **Cardinality Limit** | <10,000 time series | Prevent memory/cost explosion |

---

## References

- **Prometheus Docs**: [Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- **Prometheus Best Practices**: [Naming](https://prometheus.io/docs/practices/naming/)
- **Prometheus Python Client**: [prometheus_client](https://github.com/prometheus/client_python)
- **Prometheus Exposition Format**: [Text-based Format Specification](https://prometheus.io/docs/instrumenting/exposition_formats/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/routers/metrics.py` and `api/middleware/prometheus_middleware.py` during Feature 015 implementation phase
