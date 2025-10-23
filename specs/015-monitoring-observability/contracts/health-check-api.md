# Health Check API Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: REST API Endpoint Specification
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Health check endpoints provide component-level system status for load balancers, orchestrators (Kubernetes, Docker Swarm), and monitoring systems. These endpoints enable automated health detection, graceful degradation, and operational visibility.

**Use Cases**:
- Load balancer health probes (every 10 seconds)
- Kubernetes liveness/readiness probes
- Uptime monitoring (UptimeRobot, Pingdom)
- Operations team manual checks

---

## API Endpoints

### 1. GET /health - Overall System Health

**Purpose**: Report overall system health status for load balancer decisions.

**Authentication**: None (public endpoint)

**Request**:
```http
GET /health HTTP/1.1
Host: api.signupflow.io
Accept: application/json
```

**Query Parameters**: None

**Response (200 OK - Healthy)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T10:30:45.123Z",
  "version": "1.2.0",
  "uptime_seconds": 86400,
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15,
      "last_check": "2025-10-23T10:30:45.100Z"
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 5,
      "last_check": "2025-10-23T10:30:45.105Z"
    },
    "influxdb": {
      "status": "healthy",
      "response_time_ms": 25,
      "last_check": "2025-10-23T10:30:45.110Z"
    },
    "sentry": {
      "status": "healthy",
      "response_time_ms": 120,
      "last_check": "2025-10-23T10:30:45.115Z"
    }
  }
}
```

**Response (503 Service Unavailable - Unhealthy)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-23T10:30:45.123Z",
  "version": "1.2.0",
  "uptime_seconds": 86400,
  "components": {
    "database": {
      "status": "unhealthy",
      "error": "Connection timeout (2000ms exceeded)",
      "last_check": "2025-10-23T10:30:43.100Z"
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 5,
      "last_check": "2025-10-23T10:30:45.105Z"
    },
    "influxdb": {
      "status": "degraded",
      "response_time_ms": 2500,
      "warning": "Response time above threshold (2000ms)",
      "last_check": "2025-10-23T10:30:45.110Z"
    },
    "sentry": {
      "status": "healthy",
      "response_time_ms": 120,
      "last_check": "2025-10-23T10:30:45.115Z"
    }
  }
}
```

**Status Codes**:
- `200 OK`: All critical components healthy
- `503 Service Unavailable`: One or more critical components unhealthy
- `500 Internal Server Error`: Health check system failure

**Component Status Values**:
- `healthy`: Component responding within acceptable time (<1s)
- `degraded`: Component responding but slow (1-3s) or partial functionality
- `unhealthy`: Component timeout (>3s), connection refused, or error

---

### 2. GET /ready - Readiness Check

**Purpose**: Report if application is ready to accept traffic (all dependencies initialized).

**Authentication**: None (public endpoint)

**Request**:
```http
GET /ready HTTP/1.1
Host: api.signupflow.io
Accept: application/json
```

**Query Parameters**: None

**Response (200 OK - Ready)**:
```json
{
  "ready": true,
  "timestamp": "2025-10-23T10:30:45.123Z",
  "initialization": {
    "database_migrations": "complete",
    "redis_connection_pool": "initialized",
    "sentry_sdk": "initialized",
    "prometheus_metrics": "registered",
    "influxdb_client": "connected"
  }
}
```

**Response (503 Service Unavailable - Not Ready)**:
```json
{
  "ready": false,
  "timestamp": "2025-10-23T10:30:45.123Z",
  "initialization": {
    "database_migrations": "in_progress",
    "redis_connection_pool": "initialized",
    "sentry_sdk": "initialized",
    "prometheus_metrics": "registered",
    "influxdb_client": "connecting"
  },
  "blocking_issues": [
    "Database migrations in progress (2/5 complete)",
    "InfluxDB connection not established"
  ]
}
```

**Status Codes**:
- `200 OK`: Application ready to accept traffic
- `503 Service Unavailable`: Application not yet ready (initializing)
- `500 Internal Server Error`: Readiness check system failure

**Difference from /health**:
- `/health`: "Can I serve requests right now?" (operational health)
- `/ready`: "Have I finished starting up?" (initialization completeness)

---

## Implementation Patterns

### Backend Implementation

**File**: `api/routers/health.py`

```python
from fastapi import APIRouter, Response
from datetime import datetime
import asyncio
import time
from api.database import get_db
from api.core.redis_client import redis_client
from api.services.influxdb_service import influxdb_client
import sentry_sdk

router = APIRouter(tags=["health"])

# Application start time for uptime calculation
app_start_time = time.time()

@router.get("/health")
async def health_check() -> Response:
    """
    Overall system health check for load balancers.

    Returns 200 if all critical components healthy, 503 otherwise.
    Checks: database, Redis, InfluxDB, Sentry connectivity.
    """
    components = {}

    # Check database (critical)
    components["database"] = await check_database()

    # Check Redis (critical for rate limiting, sessions)
    components["redis"] = await check_redis()

    # Check InfluxDB (non-critical, metrics only)
    components["influxdb"] = await check_influxdb()

    # Check Sentry (non-critical, error tracking only)
    components["sentry"] = await check_sentry()

    # Determine overall status (fail if any critical component unhealthy)
    critical_components = ["database", "redis"]
    all_critical_healthy = all(
        components[name]["status"] == "healthy"
        for name in critical_components
    )

    overall_status = "healthy" if all_critical_healthy else "unhealthy"
    status_code = 200 if all_critical_healthy else 503

    response_body = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": os.getenv("APP_VERSION", "unknown"),
        "uptime_seconds": int(time.time() - app_start_time),
        "components": components
    }

    return Response(
        content=json.dumps(response_body),
        status_code=status_code,
        media_type="application/json"
    )

@router.get("/ready")
async def readiness_check() -> Response:
    """
    Readiness check for Kubernetes/orchestrators.

    Returns 200 if application fully initialized, 503 otherwise.
    Checks: database migrations, connection pools, SDK initialization.
    """
    initialization_status = {
        "database_migrations": "complete",  # Check alembic current revision
        "redis_connection_pool": "initialized" if redis_client.ping() else "failed",
        "sentry_sdk": "initialized" if sentry_sdk.Hub.current.client else "not_initialized",
        "prometheus_metrics": "registered",
        "influxdb_client": "connected" if influxdb_client.ping() else "disconnected"
    }

    # Determine readiness (all must be complete/initialized)
    ready = all(
        status in ["complete", "initialized", "registered", "connected"]
        for status in initialization_status.values()
    )

    blocking_issues = []
    if not ready:
        for component, status in initialization_status.items():
            if status not in ["complete", "initialized", "registered", "connected"]:
                blocking_issues.append(f"{component}: {status}")

    status_code = 200 if ready else 503

    response_body = {
        "ready": ready,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "initialization": initialization_status
    }

    if blocking_issues:
        response_body["blocking_issues"] = blocking_issues

    return Response(
        content=json.dumps(response_body),
        status_code=status_code,
        media_type="application/json"
    )

async def check_database(timeout: int = 2) -> dict:
    """Test database connectivity with timeout."""
    start_time = time.time()
    try:
        async with asyncio.timeout(timeout):
            db = next(get_db())
            result = db.execute(text("SELECT 1"))
            result.fetchone()

        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "healthy",
            "response_time_ms": response_time_ms,
            "last_check": datetime.utcnow().isoformat() + "Z"
        }
    except asyncio.TimeoutError:
        return {
            "status": "unhealthy",
            "error": f"Connection timeout ({timeout}s exceeded)",
            "last_check": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat() + "Z"
        }

async def check_redis(timeout: int = 2) -> dict:
    """Test Redis connectivity with timeout."""
    start_time = time.time()
    try:
        async with asyncio.timeout(timeout):
            redis_client.ping()

        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "healthy",
            "response_time_ms": response_time_ms,
            "last_check": datetime.utcnow().isoformat() + "Z"
        }
    except asyncio.TimeoutError:
        return {
            "status": "unhealthy",
            "error": f"Connection timeout ({timeout}s exceeded)",
            "last_check": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat() + "Z"
        }

async def check_influxdb(timeout: int = 2) -> dict:
    """Test InfluxDB connectivity with timeout (non-critical)."""
    start_time = time.time()
    try:
        async with asyncio.timeout(timeout):
            influxdb_client.ping()

        response_time_ms = int((time.time() - start_time) * 1000)

        # Warn if response time high but don't mark unhealthy
        status = "healthy"
        result = {
            "status": status,
            "response_time_ms": response_time_ms,
            "last_check": datetime.utcnow().isoformat() + "Z"
        }

        if response_time_ms > 2000:
            result["status"] = "degraded"
            result["warning"] = f"Response time above threshold (2000ms)"

        return result
    except Exception as e:
        # InfluxDB failure doesn't cause overall unhealthy (metrics only)
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat() + "Z"
        }

async def check_sentry(timeout: int = 2) -> dict:
    """Test Sentry SDK initialization (non-critical)."""
    try:
        # Check if Sentry client is initialized
        client = sentry_sdk.Hub.current.client
        if client:
            return {
                "status": "healthy",
                "last_check": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Sentry SDK not initialized",
                "last_check": datetime.utcnow().isoformat() + "Z"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat() + "Z"
        }
```

---

## Load Balancer Integration

### AWS Application Load Balancer (ALB)

```yaml
# ALB Target Group Health Check Configuration
HealthCheckProtocol: HTTP
HealthCheckPath: /health
HealthCheckPort: 8000
HealthCheckIntervalSeconds: 10
HealthCheckTimeoutSeconds: 5
HealthyThresholdCount: 2
UnhealthyThresholdCount: 2
Matcher:
  HttpCode: 200
```

### Kubernetes Liveness/Readiness Probes

```yaml
# Kubernetes Deployment Configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: signupflow-api
spec:
  template:
    spec:
      containers:
      - name: api
        image: signupflow/api:latest
        ports:
        - containerPort: 8000

        # Liveness probe - restart if unhealthy
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # Readiness probe - remove from service if not ready
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

### Docker Swarm Healthcheck

```dockerfile
# Dockerfile HEALTHCHECK instruction
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Traefik Health Check

```yaml
# Traefik Dynamic Configuration
http:
  services:
    signupflow-api:
      loadBalancer:
        servers:
          - url: "http://api-1:8000"
          - url: "http://api-2:8000"
        healthCheck:
          path: /health
          interval: 10s
          timeout: 5s
```

---

## Performance Requirements

| Metric | Target | Justification |
|--------|--------|---------------|
| **Response Time** | <100ms (healthy) | Load balancers probe every 10s, must be fast |
| **Timeout** | 2 seconds per component | Prevent cascade failures from slow dependencies |
| **Overhead** | <1% CPU | Health checks run continuously, must be lightweight |
| **Concurrent Requests** | 100 req/s | Multiple load balancers probing simultaneously |

---

## Error Scenarios

### Scenario 1: Database Connection Lost

**Trigger**: PostgreSQL server unreachable

**Response**:
```json
{
  "status": "unhealthy",
  "components": {
    "database": {
      "status": "unhealthy",
      "error": "Connection timeout (2000ms exceeded)"
    }
  }
}
```

**Status Code**: `503 Service Unavailable`

**Load Balancer Action**: Remove instance from rotation

---

### Scenario 2: Redis Degraded (Slow Response)

**Trigger**: Redis responding in 2500ms (above 2000ms threshold)

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "redis": {
      "status": "degraded",
      "response_time_ms": 2500,
      "warning": "Response time above threshold (2000ms)"
    }
  }
}
```

**Status Code**: `200 OK` (still serving traffic, but degraded)

**Load Balancer Action**: Keep in rotation (not critical enough to remove)

---

### Scenario 3: Application Starting Up

**Trigger**: Application initializing after deploy

**Response** (GET /ready):
```json
{
  "ready": false,
  "initialization": {
    "database_migrations": "in_progress"
  },
  "blocking_issues": [
    "Database migrations in progress (2/5 complete)"
  ]
}
```

**Status Code**: `503 Service Unavailable`

**Load Balancer Action**: Wait for readiness before routing traffic

---

## Testing

### Unit Tests

```python
# tests/unit/test_health_checks.py
def test_check_database_healthy(monkeypatch):
    """Test database health check returns healthy status."""
    # Mock database connection
    async def mock_execute(query):
        return MagicMock()

    result = await check_database(timeout=2)
    assert result["status"] == "healthy"
    assert result["response_time_ms"] < 1000

def test_check_database_timeout(monkeypatch):
    """Test database health check handles timeout."""
    # Mock slow database
    async def mock_execute_slow(query):
        await asyncio.sleep(5)  # Exceed 2s timeout

    result = await check_database(timeout=2)
    assert result["status"] == "unhealthy"
    assert "timeout" in result["error"].lower()
```

### Integration Tests

```python
# tests/integration/test_health_endpoints.py
def test_health_endpoint_healthy(client):
    """Test /health returns 200 when all components healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data["components"]
    assert data["components"]["database"]["status"] == "healthy"

def test_ready_endpoint_ready(client):
    """Test /ready returns 200 when application initialized."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["initialization"]["database_migrations"] == "complete"
```

### E2E Tests

```python
# tests/e2e/test_health_check_workflows.py
def test_load_balancer_health_probe_workflow(page: Page):
    """Test load balancer can probe health endpoint."""
    # Simulate load balancer health check
    response = requests.get("http://localhost:8000/health", timeout=5)

    assert response.status_code in [200, 503]  # Valid status codes
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert data["status"] in ["healthy", "unhealthy"]
```

---

## Monitoring Integration

### Prometheus Metrics

```python
# Metrics exposed by health check system
health_check_duration_seconds = Histogram(
    'health_check_duration_seconds',
    'Time taken for health check',
    ['component']
)

health_check_status = Gauge(
    'health_check_status',
    'Health check status (1=healthy, 0=unhealthy)',
    ['component']
)
```

### Sentry Error Tracking

```python
# Capture health check failures in Sentry
try:
    result = await check_database()
    if result["status"] == "unhealthy":
        sentry_sdk.capture_message(
            f"Database health check failed: {result['error']}",
            level="error",
            extra={"component": "database", "result": result}
        )
except Exception as e:
    sentry_sdk.capture_exception(e)
```

---

## References

- **RFC**: [Health Check Response Format for HTTP APIs (Draft)](https://tools.ietf.org/id/draft-inadarei-api-health-check-06.html)
- **Kubernetes**: [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- **AWS**: [Target Health Status](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- **Prometheus**: [Best Practices - Health Check](https://prometheus.io/docs/practices/pushing/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/routers/health.py` during Feature 015 implementation phase
