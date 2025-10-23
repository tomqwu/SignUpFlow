# Quick Start: Monitoring and Observability (15 Minutes)

**Feature**: 015-monitoring-observability
**Time**: 15 minutes to production-ready monitoring
**Prerequisites**: SignUpFlow backend running, Python 3.11+, AWS account (for CloudWatch) or Docker (for InfluxDB)

This guide gets monitoring and observability infrastructure operational in 15 minutes.

---

## 🎯 What You'll Get

After completing this guide:
- ✅ Sentry error tracking capturing all exceptions with full context
- ✅ Prometheus metrics exposing performance data
- ✅ Health check endpoints for load balancers
- ✅ CloudWatch Logs aggregation (or ELK alternative)
- ✅ Slack alerts for critical errors
- ✅ Monitoring dashboard showing key metrics

---

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to SignUpFlow repository
cd /home/ubuntu/SignUpFlow

# Add monitoring dependencies
poetry add \
  sentry-sdk==1.40.0 \
  prometheus-client==0.19.0 \
  python-json-logger==2.0.7 \
  watchtower==3.0.1 \
  influxdb-client==1.39.0 \
  requests==2.31.0

# Verify installation
poetry show | grep -E "(sentry|prometheus|watchtower|influxdb)"
```

**Output**:
```
sentry-sdk                  1.40.0
prometheus-client           0.19.0
python-json-logger          2.0.7
watchtower                  3.0.1
influxdb-client             1.39.0
```

---

## Step 2: Configure Environment Variables (3 minutes)

```bash
# Create monitoring configuration section in .env
cat >> .env << 'EOF'

# Monitoring & Observability
SENTRY_DSN=https://your-sentry-dsn@o123456.ingest.sentry.io/7654321
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token-here
INFLUXDB_ORG=signupflow
INFLUXDB_BUCKET=metrics

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ALERT_CHANNEL=#oncall

LOG_LEVEL=INFO
CLOUDWATCH_LOG_GROUP=/signupflow/application
CLOUDWATCH_LOG_STREAM=api-{instance_id}

HEALTH_CHECK_TIMEOUT=3
ALERT_EVALUATION_INTERVAL=60
EOF

# Add .env to .gitignore (if not already present)
echo ".env" >> .gitignore
```

**Get Credentials**:
1. **Sentry DSN**: Sign up at https://sentry.io → Create project → Copy DSN
2. **Slack Webhook**: Go to https://api.slack.com/apps → Create New App → Incoming Webhooks → Add to Channel
3. **InfluxDB Token**: Run InfluxDB container (see Step 3) → Generate token in UI

---

## Step 3: Deploy InfluxDB (Optional - Self-Hosted) (3 minutes)

**Option A: InfluxDB Cloud** (Recommended for production)
```bash
# Sign up at https://cloud2.influxdata.com/signup
# Choose free tier (sufficient for 500 time series)
# Create bucket: "metrics"
# Generate API token
# Use credentials in .env
```

**Option B: InfluxDB Docker** (Development/testing)
```bash
# Run InfluxDB container
docker run -d --name influxdb \
  -p 8086:8086 \
  -v influxdb-data:/var/lib/influxdb2 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=signupflow123 \
  -e DOCKER_INFLUXDB_INIT_ORG=signupflow \
  -e DOCKER_INFLUXDB_INIT_BUCKET=metrics \
  influxdb:2.7-alpine

# Wait for initialization (30 seconds)
sleep 30

# Generate API token
docker exec influxdb influx auth create \
  --org signupflow \
  --description "SignUpFlow API Token" \
  --read-bucket metrics \
  --write-bucket metrics

# Copy token to .env
```

---

## Step 4: Initialize Monitoring Infrastructure (2 minutes)

Create monitoring initialization module:

```python
# api/core/monitoring.py
"""Monitoring and observability initialization."""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import Counter, Histogram, Gauge
import logging
from pythonjsonlogger import jsonlogger
import watchtower

def init_sentry():
    """Initialize Sentry error tracking."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logging.warning("SENTRY_DSN not set, skipping Sentry initialization")
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.1)),
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        release=os.getenv("GIT_COMMIT_SHA", "unknown")
    )
    logging.info("Sentry error tracking initialized")

def init_prometheus_metrics():
    """Initialize Prometheus metrics collectors."""
    global http_requests_total, http_request_duration_seconds, http_requests_in_progress

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
        'Number of HTTP requests currently being processed'
    )

    logging.info("Prometheus metrics initialized")

def init_logging():
    """Initialize structured JSON logging with CloudWatch."""
    logger = logging.getLogger()
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # JSON formatter for structured logs
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # CloudWatch Logs handler (if AWS credentials available)
    try:
        cloudwatch_handler = watchtower.CloudWatchLogHandler(
            log_group_name=os.getenv("CLOUDWATCH_LOG_GROUP", "/signupflow/application"),
            stream_name=os.getenv("CLOUDWATCH_LOG_STREAM", "api-{instance_id}"),
            send_interval=10,  # Buffer logs for 10 seconds
            create_log_group=True
        )
        cloudwatch_handler.setFormatter(formatter)
        logger.addHandler(cloudwatch_handler)
        logging.info("CloudWatch Logs handler initialized")
    except Exception as e:
        logging.warning(f"CloudWatch Logs initialization failed: {e}. Logs will only go to stdout.")

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def init_monitoring():
    """Initialize all monitoring infrastructure."""
    init_logging()
    init_sentry()
    init_prometheus_metrics()
    logging.info("Monitoring infrastructure initialized successfully")
```

Update FastAPI application:

```python
# api/main.py
from api.core.monitoring import init_monitoring

app = FastAPI(title="SignUpFlow API")

# Initialize monitoring BEFORE other middleware
init_monitoring()

# ... rest of FastAPI configuration
```

---

## Step 5: Add Health Check Endpoints (2 minutes)

```python
# api/routers/health.py
"""Health check endpoints for load balancers."""
from fastapi import APIRouter, Response
from api.database import get_db
from api.core.redis_client import redis_client
import time
import asyncio

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers.
    Returns 200 OK if healthy, 503 Service Unavailable if any component unhealthy.
    """
    components = {
        "database": await check_database(),
        "redis": await check_redis()
    }

    all_healthy = all(c["status"] == "healthy" for c in components.values())
    status_code = 200 if all_healthy else 503

    return Response(
        content=json.dumps({
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components
        }),
        status_code=status_code,
        media_type="application/json"
    )

@router.get("/ready")
async def readiness_check():
    """Readiness check for progressive rollout (Kubernetes, ECS)."""
    # Application is ready if initialized and all components healthy
    health_response = await health_check()
    return health_response

async def check_database(timeout: int = 2) -> dict:
    """Test database connectivity."""
    try:
        start_time = time.time()
        async with asyncio.timeout(timeout):
            db = next(get_db())
            await db.execute("SELECT 1")
        response_time = int((time.time() - start_time) * 1000)

        return {"status": "healthy", "response_time_ms": response_time}
    except asyncio.TimeoutError:
        return {"status": "unhealthy", "error": f"Timeout ({timeout}s)"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis(timeout: int = 1) -> dict:
    """Test Redis connectivity."""
    try:
        start_time = time.time()
        async with asyncio.timeout(timeout):
            redis_client.ping()
        response_time = int((time.time() - start_time) * 1000)

        return {"status": "healthy", "response_time_ms": response_time}
    except asyncio.TimeoutError:
        return {"status": "unhealthy", "error": f"Timeout ({timeout}s)"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

Register router:

```python
# api/main.py
from api.routers import health

app.include_router(health.router)
```

---

## Step 6: Add Prometheus Metrics Middleware (2 minutes)

```python
# api/middleware/prometheus_middleware.py
"""Prometheus metrics collection middleware."""
from fastapi import Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from api.core.monitoring import http_requests_total, http_request_duration_seconds, http_requests_in_progress
import time

async def prometheus_middleware(request: Request, call_next):
    """Collect HTTP request metrics for Prometheus."""
    # Skip metrics collection for /metrics endpoint (avoid recursion)
    if request.url.path == "/metrics":
        return await call_next(request)

    http_requests_in_progress.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
    finally:
        http_requests_in_progress.dec()

# Metrics exposition endpoint
@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics in text format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

Register middleware:

```python
# api/main.py
from api.middleware.prometheus_middleware import prometheus_middleware

app.middleware("http")(prometheus_middleware)
```

---

## Step 7: Verify Monitoring (1 minute)

```bash
# Start application
poetry run uvicorn api.main:app --reload

# Test health check (should return 200 OK)
curl http://localhost:8000/health

# Test metrics endpoint (should return Prometheus format)
curl http://localhost:8000/metrics | head -20

# Trigger test error (should appear in Sentry)
curl -X POST http://localhost:8000/api/trigger-test-error

# Check Sentry dashboard
open https://sentry.io/organizations/your-org/issues/
```

**Expected Output** (`/health`):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T10:30:00Z",
  "components": {
    "database": {"status": "healthy", "response_time_ms": 12},
    "redis": {"status": "healthy", "response_time_ms": 3}
  }
}
```

**Expected Output** (`/metrics`):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status_code="200"} 5.0
http_requests_total{method="GET",endpoint="/api/events",status_code="200"} 42.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/events",le="0.01"} 10.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/events",le="0.05"} 35.0
http_request_duration_seconds_count{method="GET",endpoint="/api/events"} 42.0
http_request_duration_seconds_sum{method="GET",endpoint="/api/events"} 1.245
```

---

## Step 8: Configure Slack Alerts (2 minutes - Optional)

Create alert service:

```python
# api/services/alert_service.py
"""Slack alert notification service."""
import requests
import os
import logging

class AlertService:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.channel = os.getenv("SLACK_ALERT_CHANNEL", "#oncall")

    def send_critical_alert(self, title: str, message: str, metric_value: float = None):
        """Send critical alert to Slack."""
        if not self.webhook_url:
            logging.warning("SLACK_WEBHOOK_URL not set, skipping alert")
            return

        payload = {
            "channel": self.channel,
            "username": "SignUpFlow Monitoring",
            "icon_emoji": ":rotating_light:",
            "attachments": [{
                "color": "danger",
                "title": f"🚨 CRITICAL: {title}",
                "text": message,
                "fields": [
                    {"title": "Current Value", "value": str(metric_value), "short": True},
                    {"title": "Severity", "value": "CRITICAL", "short": True}
                ] if metric_value else [],
                "footer": "SignUpFlow Monitoring",
                "footer_icon": "https://signupflow.io/favicon.ico",
                "ts": int(time.time())
            }]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logging.info(f"Slack alert sent: {title}")
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")
```

Test alert:

```bash
# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "channel": "#oncall",
    "text": "Test alert from SignUpFlow Monitoring"
  }'
```

---

## 🎉 Success! You're Monitoring Production

Your SignUpFlow application now has:
- ✅ **Error Tracking**: All exceptions sent to Sentry with full context
- ✅ **Performance Metrics**: HTTP request latency, throughput, error rates tracked
- ✅ **Health Checks**: `/health` and `/ready` endpoints for load balancers
- ✅ **Structured Logging**: JSON logs sent to CloudWatch (or stdout)
- ✅ **Slack Alerts**: Critical errors notify operations team immediately

---

## Next Steps

### 1. Create Grafana Dashboard (10 minutes)
```bash
# Install Grafana
docker run -d --name grafana \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana-oss:latest

# Add InfluxDB data source in Grafana UI
# Import dashboard template from specs/015-monitoring-observability/grafana-dashboard.json
```

### 2. Configure Alert Rules (5 minutes)
```sql
-- Example: High error rate alert rule
INSERT INTO alert_rules (id, name, metric_name, condition, threshold, severity, notification_channels)
VALUES (
  'alert_rule_high_error_rate',
  'High Error Rate',
  'error_rate',
  '>',
  10.0,
  'critical',
  '["slack", "email"]'
);
```

### 3. Set Up Monitoring Runbook (15 minutes)
Create `docs/MONITORING_RUNBOOK.md` with:
- How to respond to common alerts
- Dashboard URLs and access instructions
- Escalation procedures
- On-call rotation schedule

### 4. Enable Additional Metrics (10 minutes)
```python
# api/core/metrics.py
from prometheus_client import Gauge

# Database metrics
db_connections_active = Gauge('db_connections_active', 'Active database connections')
db_query_duration_seconds = Histogram('db_query_duration_seconds', 'Database query latency', ['query_type'])

# Background job metrics
background_jobs_pending = Gauge('background_jobs_pending', 'Pending background jobs')
background_jobs_duration_seconds = Histogram('background_jobs_duration_seconds', 'Job execution time', ['job_name'])
```

---

## Troubleshooting

### Sentry Not Capturing Errors
```bash
# Verify SENTRY_DSN is set
echo $SENTRY_DSN

# Test Sentry integration
python -c "import sentry_sdk; sentry_sdk.init('$SENTRY_DSN'); sentry_sdk.capture_message('Test message')"

# Check Sentry dashboard after 30 seconds
```

### CloudWatch Logs Not Appearing
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check CloudWatch log group exists
aws logs describe-log-groups --log-group-name-prefix /signupflow

# Test CloudWatch logging
python -c "import watchtower, logging; logger = logging.getLogger(); logger.addHandler(watchtower.CloudWatchLogHandler(log_group_name='/signupflow/test')); logger.error('Test log')"
```

### Metrics Not Exposed
```bash
# Verify Prometheus client installed
poetry show prometheus-client

# Check /metrics endpoint responds
curl -v http://localhost:8000/metrics

# Verify middleware registered
grep "prometheus_middleware" api/main.py
```

### Slack Alerts Not Sending
```bash
# Test webhook URL directly
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test alert"}'

# Check application logs for errors
grep "Slack alert" logs/application.log
```

---

## Cost Estimate

**Monthly monitoring costs** (1000 organizations, 100 req/s):

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| Sentry | Free → Pro | $0-29/month | 5K errors free, $29 for 50K errors |
| InfluxDB | OSS → Cloud | $0-25/month | Self-hosted free, Cloud $25/month |
| CloudWatch Logs | Pay-as-you-go | $16/month | 1GB/day logs = $0.50/GB + $0.03/GB storage |
| Slack | Free | $0/month | Webhook notifications free |
| Grafana | OSS | $0/month | Self-hosted free |

**Total**: **$16-70/month** (within $100 budget)

**Free Tier** (development): $0/month using Sentry free tier, self-hosted InfluxDB, and stdout logs

---

## Security Notes

1. **Never commit credentials**: Add `.env` to `.gitignore`
2. **Rotate API tokens**: Rotate Sentry DSN, InfluxDB tokens, Slack webhooks every 90 days
3. **Limit Slack webhook access**: Use private channels (#oncall) for sensitive alerts
4. **Scrub sensitive logs**: Enable log scrubbing middleware before CloudWatch upload
5. **Encrypt CloudWatch logs**: Enable KMS encryption for CloudWatch log groups

---

## Documentation

- **Sentry Docs**: https://docs.sentry.io/platforms/python/guides/fastapi/
- **Prometheus Client**: https://prometheus.github.io/client_python/
- **InfluxDB Docs**: https://docs.influxdata.com/influxdb/v2.7/
- **CloudWatch Logs**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/
- **Grafana Dashboards**: https://grafana.com/docs/grafana/latest/

**Complete API Contracts**: See `specs/015-monitoring-observability/contracts/` for detailed specifications of all monitoring APIs.
