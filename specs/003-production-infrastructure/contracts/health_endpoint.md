# API Contract: Health Check Endpoint

**Feature**: Production Infrastructure & Deployment
**Endpoint**: `GET /health`
**Purpose**: Application health status monitoring for load balancer, deployment validation, and operations dashboard

---

## Endpoint Specification

### Request

**Method**: `GET`
**Path**: `/health`
**Authentication**: None (public endpoint for load balancer health checks)
**Headers**: None required

**Query Parameters**: None

**Request Body**: None

**Example Request**:
```http
GET /health HTTP/1.1
Host: signupflow.io
```

```bash
curl https://signupflow.io/health
```

---

### Response

#### Success Response (200 OK - Healthy)

**Status Code**: `200 OK`
**Content-Type**: `application/json`

**Response Schema**:
```json
{
  "status": "healthy",
  "version": "string",
  "timestamp": "ISO 8601 datetime string",
  "uptime_seconds": "integer",
  "environment": "string",
  "checks": {
    "database": {
      "status": "connected" | "disconnected" | "slow",
      "response_time_ms": "integer | null"
    },
    "redis": {
      "status": "connected" | "disconnected" | "slow",
      "response_time_ms": "integer | null"
    }
  },
  "metrics": {
    "memory_usage_mb": "integer",
    "memory_usage_percent": "float",
    "cpu_usage_percent": "float",
    "active_connections": "integer",
    "total_requests": "integer",
    "error_rate_5min": "float"
  }
}
```

**Example Response**:
```json
{
  "status": "healthy",
  "version": "v1.2.3 (a1b2c3d)",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 86400,
  "environment": "production",
  "checks": {
    "database": {
      "status": "connected",
      "response_time_ms": 12
    },
    "redis": {
      "status": "connected",
      "response_time_ms": 3
    }
  },
  "metrics": {
    "memory_usage_mb": 450,
    "memory_usage_percent": 44.5,
    "cpu_usage_percent": 15.2,
    "active_connections": 8,
    "total_requests": 125340,
    "error_rate_5min": 0.002
  }
}
```

---

#### Degraded Response (200 OK - Degraded)

**Status Code**: `200 OK` (still accepting traffic, but with warnings)
**Content-Type**: `application/json`

**Example Response**:
```json
{
  "status": "degraded",
  "version": "v1.2.3 (a1b2c3d)",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 86400,
  "environment": "production",
  "checks": {
    "database": {
      "status": "slow",
      "response_time_ms": 150
    },
    "redis": {
      "status": "connected",
      "response_time_ms": 3
    }
  },
  "metrics": {
    "memory_usage_mb": 850,
    "memory_usage_percent": 84.5,
    "cpu_usage_percent": 78.2,
    "active_connections": 45,
    "total_requests": 1253400,
    "error_rate_5min": 0.035
  },
  "warnings": [
    "Database response time above threshold (150ms > 100ms)",
    "Memory usage high (84.5% > 80%)",
    "Error rate elevated (3.5% > 1%)"
  ]
}
```

---

#### Unhealthy Response (503 Service Unavailable)

**Status Code**: `503 Service Unavailable`
**Content-Type**: `application/json`

**Example Response**:
```json
{
  "status": "unhealthy",
  "version": "v1.2.3 (a1b2c3d)",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 86400,
  "environment": "production",
  "checks": {
    "database": {
      "status": "disconnected",
      "response_time_ms": null
    },
    "redis": {
      "status": "connected",
      "response_time_ms": 3
    }
  },
  "metrics": {
    "memory_usage_mb": 950,
    "memory_usage_percent": 94.5,
    "cpu_usage_percent": 95.2,
    "active_connections": 0,
    "total_requests": 1253400,
    "error_rate_5min": 0.98
  },
  "errors": [
    "Database connection failed: FATAL: password authentication failed for user 'signupflow'",
    "Critical error rate: 98% of requests failing in last 5 minutes"
  ]
}
```

---

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | Enum | Yes | Overall health status: `healthy`, `degraded`, `unhealthy` |
| `version` | String | Yes | Application version (Git tag + short commit SHA) |
| `timestamp` | DateTime | Yes | ISO 8601 timestamp in UTC (e.g., `2025-10-20T14:31:00Z`) |
| `uptime_seconds` | Integer | Yes | Application uptime in seconds since last restart |
| `environment` | String | Yes | Environment name: `development`, `staging`, `production` |
| `checks` | Object | Yes | Dependency health checks (database, redis) |
| `metrics` | Object | Yes | Application performance metrics |
| `warnings` | Array[String] | No | Warning messages (only present if status = `degraded`) |
| `errors` | Array[String] | No | Error messages (only present if status = `unhealthy`) |

### `checks` Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `database` | Object | Yes | PostgreSQL database health |
| `database.status` | Enum | Yes | Connection status: `connected`, `disconnected`, `slow` |
| `database.response_time_ms` | Integer | No | Ping response time in milliseconds (null if disconnected) |
| `redis` | Object | Yes | Redis cache health |
| `redis.status` | Enum | Yes | Connection status: `connected`, `disconnected`, `slow` |
| `redis.response_time_ms` | Integer | No | Ping response time in milliseconds (null if disconnected) |

### `metrics` Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `memory_usage_mb` | Integer | Yes | Process memory usage in megabytes |
| `memory_usage_percent` | Float | Yes | Memory usage as percentage of available memory (0-100) |
| `cpu_usage_percent` | Float | Yes | CPU usage percentage (0-100) |
| `active_connections` | Integer | Yes | Current active database connections |
| `total_requests` | Integer | Yes | Total HTTP requests handled since startup |
| `error_rate_5min` | Float | Yes | Error rate in last 5 minutes (0.0-1.0, e.g., 0.002 = 0.2%) |

---

## Status Determination Logic

### Healthy (`200 OK`)

**All conditions must be true**:
- Database status = `connected`
- Database response time < 100ms
- Redis status = `connected`
- Redis response time < 50ms
- Error rate < 0.01 (1%)
- Memory usage < 80%
- CPU usage < 85%

### Degraded (`200 OK` with warnings)

**Any condition is true**:
- Database response time 100-500ms (`slow`)
- Redis response time 50-200ms (`slow`)
- Error rate 0.01-0.05 (1%-5%)
- Memory usage 80%-90%
- CPU usage 85%-95%

**Response**: Return 200 OK (still serving traffic) with `warnings` array

### Unhealthy (`503 Service Unavailable`)

**Any condition is true**:
- Database status = `disconnected`
- Database response time > 500ms
- Redis status = `disconnected`
- Error rate > 0.05 (5%)
- Memory usage > 90%
- CPU usage > 95%

**Response**: Return 503 Service Unavailable with `errors` array

---

## Response Times

**Target Response Time**: < 200ms for 99% of requests

**Timeout**: 5 seconds (if health check takes >5s, return `unhealthy` with timeout error)

---

## Error Handling

### Database Connection Failed

```json
{
  "status": "unhealthy",
  "version": "v1.2.3 (a1b2c3d)",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 86400,
  "environment": "production",
  "checks": {
    "database": {
      "status": "disconnected",
      "response_time_ms": null
    },
    "redis": {
      "status": "connected",
      "response_time_ms": 3
    }
  },
  "errors": [
    "Database connection failed: could not connect to server"
  ]
}
```

### Redis Connection Failed

```json
{
  "status": "degraded",
  "version": "v1.2.3 (a1b2c3d)",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 86400,
  "environment": "production",
  "checks": {
    "database": {
      "status": "connected",
      "response_time_ms": 12
    },
    "redis": {
      "status": "disconnected",
      "response_time_ms": null
    }
  },
  "warnings": [
    "Redis connection failed: Connection refused - sessions may be unavailable"
  ]
}
```

**Note**: Redis failure results in `degraded` (not `unhealthy`) because application can continue serving traffic without sessions, albeit with degraded functionality.

---

## Use Cases

### 1. Load Balancer Health Checks

**Scenario**: DigitalOcean App Platform load balancer checks instance health every 10 seconds

**Success Criteria**:
- Health check responds in < 200ms
- Status code 200 = instance healthy (receives traffic)
- Status code 503 = instance unhealthy (removed from load balancer rotation within 30 seconds)

**Implementation**:
- Load balancer configured to call `GET /health` every 10 seconds
- 3 consecutive failures (30 seconds) → remove instance
- 2 consecutive successes (20 seconds) → re-add instance

---

### 2. Post-Deployment Validation

**Scenario**: GitHub Actions deployment workflow verifies new version healthy before marking deployment complete

**Success Criteria**:
- After deploying new version, call `GET /health`
- If status = `healthy` AND version matches deployed version → deployment successful
- If status = `unhealthy` OR version mismatch → rollback deployment

**Implementation**:
```yaml
# .github/workflows/deploy.yml
- name: Health Check
  run: |
    response=$(curl -s https://signupflow.io/health)
    status=$(echo $response | jq -r '.status')
    version=$(echo $response | jq -r '.version')

    if [ "$status" != "healthy" ]; then
      echo "Health check failed: status=$status"
      exit 1
    fi

    if [ "$version" != "$GITHUB_SHA" ]; then
      echo "Version mismatch: expected=$GITHUB_SHA, actual=$version"
      exit 1
    fi

    echo "Health check passed: status=$status, version=$version"
```

---

### 3. Operations Dashboard

**Scenario**: Operations team monitors production health in real-time dashboard

**Success Criteria**:
- Dashboard polls `/health` every 30 seconds
- Display color-coded status (green = healthy, yellow = degraded, red = unhealthy)
- Show metrics graphs (CPU, memory, error rate) over time
- Alert on status change to `unhealthy` (send PagerDuty/Slack notification)

**Implementation**:
- Frontend JavaScript polls `/health` endpoint
- Stores HealthCheck records in database for historical analysis
- Triggers alerts on status transitions

---

## Implementation Notes

### FastAPI Router

**File**: `api/routers/health.py`

**Implementation Skeleton**:
```python
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import psutil

router = APIRouter(tags=["health"])

class DependencyCheck(BaseModel):
    status: str  # "connected" | "disconnected" | "slow"
    response_time_ms: Optional[int]

class HealthMetrics(BaseModel):
    memory_usage_mb: int
    memory_usage_percent: float
    cpu_usage_percent: float
    active_connections: int
    total_requests: int
    error_rate_5min: float

class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str
    timestamp: datetime
    uptime_seconds: int
    environment: str
    checks: dict[str, DependencyCheck]
    metrics: HealthMetrics
    warnings: Optional[List[str]] = None
    errors: Optional[List[str]] = None

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for load balancer and monitoring.

    Returns:
    - 200 OK: status = "healthy" or "degraded"
    - 503 Service Unavailable: status = "unhealthy"
    """
    # Check database connection
    db_check = await check_database()

    # Check Redis connection
    redis_check = await check_redis()

    # Collect metrics
    metrics = collect_metrics()

    # Determine overall status
    overall_status, warnings, errors = determine_status(db_check, redis_check, metrics)

    # Build response
    response = HealthResponse(
        status=overall_status,
        version=get_version(),
        timestamp=datetime.utcnow(),
        uptime_seconds=get_uptime(),
        environment=get_environment(),
        checks={
            "database": db_check,
            "redis": redis_check
        },
        metrics=metrics,
        warnings=warnings if overall_status == "degraded" else None,
        errors=errors if overall_status == "unhealthy" else None
    )

    # Set HTTP status code
    if overall_status == "unhealthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.dict()
        )

    return response
```

---

## Testing Requirements

### Integration Tests

**File**: `tests/integration/test_health_checks.py`

**Test Cases**:
1. `test_health_check_returns_200_when_healthy`
2. `test_health_check_includes_version_and_uptime`
3. `test_health_check_returns_200_when_degraded`
4. `test_health_check_returns_503_when_database_disconnected`
5. `test_health_check_returns_503_when_unhealthy`
6. `test_health_check_response_time_under_200ms`

### E2E Tests

**File**: `tests/e2e/test_deployment.py`

**Test Cases**:
1. `test_post_deployment_health_check_passes`
2. `test_load_balancer_removes_unhealthy_instance`

---

## Security Considerations

**Public Endpoint**: No authentication required
- Health check must be publicly accessible for load balancer
- No sensitive information in response (no database passwords, no internal IPs)
- Version information safe to expose (Git commit SHA)

**Rate Limiting**: Not required
- Health checks expected to be high-frequency (every 10 seconds from load balancer)
- No abuse risk (no expensive operations, read-only)

**DDoS Protection**: Handled at load balancer layer
- DigitalOcean App Platform protects against DDoS attacks
- Health check endpoint lightweight (< 100ms response time)

---

## Monitoring & Alerting

### Alerts

**Critical Alerts** (PagerDuty / Phone):
- Health check status = `unhealthy` for > 5 minutes → Page on-call engineer

**Warning Alerts** (Slack / Email):
- Health check status = `degraded` for > 15 minutes → Notify operations team
- Health check response time > 200ms → Investigate performance

### Metrics Tracking

**HealthCheck Records**: Store in database for historical analysis
- Retention: 24 hours at 60-second intervals (1440 records per instance per day)
- Aggregation: Hourly averages for 90-day retention

**Dashboards**: Grafana / DigitalOcean Monitoring
- Health status timeline (healthy/degraded/unhealthy)
- Response time graph (target: < 200ms)
- Database connection time trend
- Error rate trend

---

## Next Steps

**Phase 1 Continuation**:
1. ✅ Data model defined (data-model.md)
2. ✅ Health check endpoint contract defined (this document)
3. ⏳ Create `quickstart.md` for developers (setup PostgreSQL locally)
4. ⏳ Update agent context file with infrastructure knowledge

**Ready for Quickstart Guide** - Proceed to developer setup documentation.
