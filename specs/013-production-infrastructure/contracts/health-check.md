# Contract: Health Check Endpoint

**Feature**: Production Infrastructure Deployment (013)
**Contract Type**: API Endpoint Specification
**Version**: 1.0
**Status**: Draft

---

## Overview

The health check endpoint provides a standardized interface for monitoring systems, load balancers, and orchestration platforms to verify application health status. This contract defines the health check API specification that all monitoring and deployment systems depend on.

**Purpose**: Enable automated monitoring, load balancing, and deployment orchestration through standardized health status reporting.

---

## HTTP Endpoint

### GET /health

**Description**: Returns current health status of the application and its dependencies.

**Authentication**: None required (public endpoint for monitoring systems)

**Request Headers**: None required

**Response Format**: JSON

**Success Response**: HTTP 200 OK

**Degraded Response**: HTTP 503 Service Unavailable

---

## Response Schema

### Healthy Status (HTTP 200)

```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T14:32:15Z",
  "version": "1.2.0",
  "components": {
    "api": {
      "status": "healthy",
      "responseTime": "5ms"
    },
    "database": {
      "status": "healthy",
      "connectionPool": {
        "active": 3,
        "idle": 17,
        "max": 20
      },
      "responseTime": "12ms"
    },
    "storage": {
      "status": "healthy",
      "diskUsage": "45%"
    }
  },
  "uptime": 3600,
  "checks": {
    "database": "passed",
    "diskSpace": "passed",
    "memory": "passed"
  }
}
```

### Degraded Status (HTTP 503)

```json
{
  "status": "degraded",
  "timestamp": "2025-10-23T14:35:20Z",
  "version": "1.2.0",
  "components": {
    "api": {
      "status": "healthy",
      "responseTime": "8ms"
    },
    "database": {
      "status": "unhealthy",
      "error": "Connection timeout after 5000ms",
      "lastSuccessfulConnection": "2025-10-23T14:30:00Z"
    },
    "storage": {
      "status": "healthy",
      "diskUsage": "45%"
    }
  },
  "uptime": 3780,
  "checks": {
    "database": "failed",
    "diskSpace": "passed",
    "memory": "passed"
  }
}
```

---

## Field Definitions

### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | Overall health status: `"healthy"` or `"degraded"` |
| `timestamp` | string (ISO 8601) | Yes | UTC timestamp when health check was executed |
| `version` | string | Yes | Application version (semantic versioning) |
| `components` | object | Yes | Health status of individual components |
| `uptime` | integer | Yes | Application uptime in seconds since last restart |
| `checks` | object | Yes | Individual health check results |

### Components Object

Each component has:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | Component status: `"healthy"` or `"unhealthy"` |
| `responseTime` | string | No | Component response time (e.g., `"12ms"`) |
| `error` | string | No | Error message if status is `"unhealthy"` |
| Additional fields | varies | No | Component-specific metadata |

### Checks Object

| Field | Type | Description |
|-------|------|-------------|
| `database` | string | `"passed"` if database connection succeeds, `"failed"` otherwise |
| `diskSpace` | string | `"passed"` if disk usage <90%, `"failed"` if ≥90% |
| `memory` | string | `"passed"` if memory usage <85%, `"failed"` if ≥85% |

---

## Health Status Logic

### Status: "healthy" (HTTP 200)

Return HTTP 200 when **ALL** of the following conditions are true:

1. ✅ Database connection succeeds (query executes within 5 seconds)
2. ✅ Disk space usage <90%
3. ✅ Memory usage <85%
4. ✅ All critical components report "healthy" status

### Status: "degraded" (HTTP 503)

Return HTTP 503 when **ANY** of the following conditions are true:

1. ❌ Database connection fails or times out (>5 seconds)
2. ❌ Disk space usage ≥90%
3. ❌ Memory usage ≥85%
4. ❌ Any critical component reports "unhealthy" status

---

## Component Health Checks

### Database Component

**Check**: Execute `SELECT 1` query against PostgreSQL database

**Timeout**: 5 seconds

**Success Criteria**:
- Query completes successfully
- Response time <5 seconds
- Connection pool has available connections

**Failure Conditions**:
- Connection timeout (>5 seconds)
- Authentication failure
- Database unavailable
- Connection pool exhausted

**Response Fields**:
```json
{
  "status": "healthy",
  "connectionPool": {
    "active": 3,     // Currently executing queries
    "idle": 17,      // Available connections
    "max": 20        // Maximum pool size
  },
  "responseTime": "12ms"
}
```

### API Component

**Check**: Self-health verification (application is running)

**Success Criteria**: Application process is running and responding

**Response Fields**:
```json
{
  "status": "healthy",
  "responseTime": "5ms"
}
```

### Storage Component

**Check**: Disk space availability on mounted volumes

**Success Criteria**:
- Disk usage <90%
- Write permissions verified

**Failure Conditions**:
- Disk usage ≥90%
- Volume unmounted
- Permission denied

**Response Fields**:
```json
{
  "status": "healthy",
  "diskUsage": "45%"
}
```

---

## Usage Examples

### Load Balancer Health Check (Traefik)

```yaml
# docker-compose.prod.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Behavior**:
- Traefik checks `/health` every 30 seconds
- If endpoint returns non-200 status 3 times consecutively, instance marked unhealthy
- Traffic stops routing to unhealthy instance
- Traefik continues checking; re-enables instance when health returns

### CI/CD Deployment Verification

```bash
#!/bin/bash
# scripts/verify-deployment.sh

echo "Verifying deployment health..."
response=$(curl -s -o /dev/null -w "%{http_code}" https://api.signupflow.io/health)

if [ "$response" -eq 200 ]; then
  echo "✅ Deployment healthy (HTTP 200)"
  exit 0
else
  echo "❌ Deployment degraded (HTTP $response)"
  echo "Rolling back deployment..."
  exit 1
fi
```

### Monitoring Alert (Prometheus/Grafana)

```yaml
# prometheus-rules.yml
groups:
  - name: signupflow_health
    interval: 30s
    rules:
      - alert: ApplicationDegraded
        expr: up{job="signupflow-api"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "SignUpFlow API is degraded"
          description: "Health check returning HTTP 503 for >2 minutes"
```

### Python Client Example

```python
import requests

def check_application_health(base_url: str) -> dict:
    """
    Check application health and return status details.

    Returns:
        dict: Health status with components and checks

    Raises:
        requests.HTTPError: If health check fails
    """
    response = requests.get(f"{base_url}/health", timeout=10)

    if response.status_code == 200:
        print("✅ Application is healthy")
    elif response.status_code == 503:
        print("⚠️ Application is degraded")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

    return response.json()

# Usage
health = check_application_health("https://api.signupflow.io")
print(f"Database status: {health['components']['database']['status']}")
```

---

## Performance Requirements

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| **Response Time** | <100ms | Health checks should not impact application performance |
| **Timeout** | 10 seconds | Load balancers need quick response for routing decisions |
| **Frequency** | 30-60 seconds | Balance between quick failure detection and system load |
| **Retries** | 3 failures required | Avoid false positives from transient network issues |

---

## Error Handling

### Timeout Handling

If health check exceeds 10-second timeout:
- Load balancer marks instance as unhealthy
- Stops routing traffic to instance
- Continues checking every 30 seconds
- Re-enables instance when health returns

### Partial Degradation

If non-critical component fails:
- Return HTTP 200 (healthy overall status)
- Include component-specific error in response
- Log warning for monitoring
- Continue serving traffic

**Example**: Cache service down but database healthy
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy"},
    "cache": {"status": "unhealthy", "error": "Redis connection refused"}
  }
}
```

### Complete Failure

If critical component fails:
- Return HTTP 503 (degraded status)
- Include detailed error information
- Trigger automatic alerts
- Initiate auto-recovery if configured

---

## Integration Points

### Traefik Load Balancer

**Configuration**:
```yaml
services:
  api:
    labels:
      - "traefik.http.services.api.loadbalancer.healthcheck.path=/health"
      - "traefik.http.services.api.loadbalancer.healthcheck.interval=30s"
      - "traefik.http.services.api.loadbalancer.healthcheck.timeout=10s"
```

**Behavior**: Traefik automatically removes unhealthy instances from load balancer rotation.

### Docker Compose

**Configuration**:
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Behavior**: Docker restarts container if health check fails (based on `restart` policy).

### GitHub Actions CI/CD

**Post-Deployment Verification**:
```yaml
- name: Verify Deployment Health
  run: |
    curl --fail https://api.signupflow.io/health || exit 1
```

**Behavior**: Deployment marked as failed if health check returns non-200 status.

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_health.py
def test_health_endpoint_healthy(client):
    """Test health endpoint returns 200 when all components healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data["components"]

def test_health_endpoint_degraded_database(client, mock_database_failure):
    """Test health endpoint returns 503 when database unhealthy."""
    response = client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["database"]["status"] == "unhealthy"
```

### Integration Tests

```python
# tests/integration/test_health_check.py
def test_health_check_database_connectivity(client, db):
    """Test health check verifies actual database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["checks"]["database"] == "passed"

def test_health_check_timeout(client, mock_slow_database):
    """Test health check fails if database query times out."""
    response = client.get("/health")
    assert response.status_code == 503
    assert "timeout" in response.json()["components"]["database"]["error"].lower()
```

### E2E Tests

```python
# tests/e2e/test_production_deployment.py
def test_load_balancer_health_check():
    """Test load balancer uses health endpoint for routing decisions."""
    # Simulate database failure
    simulate_database_failure()

    # Wait for health check to fail
    time.sleep(90)  # 3 checks at 30s interval

    # Verify instance removed from load balancer
    response = requests.get("https://api.signupflow.io/health")
    assert response.status_code == 503

    # Restore database
    restore_database()

    # Verify instance re-added to load balancer
    time.sleep(60)
    response = requests.get("https://api.signupflow.io/health")
    assert response.status_code == 200
```

---

## Security Considerations

### No Authentication Required

Health check endpoint is **intentionally unauthenticated** to enable monitoring systems to verify application status without credentials.

**Rationale**:
- Load balancers need fast, unauthenticated access
- Monitoring systems should not store application credentials
- Health status is non-sensitive information (no PII, business data)

### Information Disclosure

Health check response includes:
- ✅ Safe: Component status, response times, uptime
- ❌ Excluded: Database passwords, API keys, user data, internal IPs

### Rate Limiting Exception

Health check endpoint is **exempt from rate limiting** to prevent false negatives from monitoring systems.

**Implementation**:
```python
# api/routers/health.py
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(request: Request):
    # No rate limiting applied to health checks
    pass
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-23 | Initial health check endpoint specification |

---

**Contract Status**: Draft - Ready for Implementation
**Dependencies**: None (foundational contract)
**Dependent Systems**: Traefik load balancer, Docker Compose, GitHub Actions, monitoring systems
