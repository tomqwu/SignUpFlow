# Log Search API Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: REST API Endpoint Specification
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Log Search API provides structured query interface for searching, filtering, and analyzing application logs stored in CloudWatch Logs or Elasticsearch. Enables operations team to troubleshoot issues, trace requests, and analyze system behavior.

**Use Cases**:
- Troubleshoot production errors by searching logs
- Trace specific requests through multiple services
- Analyze user behavior patterns
- Debug performance issues with log correlation

---

## API Endpoint

### GET /api/logs - Search Logs

**Purpose**: Search application logs with filters, pagination, and ordering.

**Authentication**: Admin or operations user (JWT Bearer token)

**Request**:
```http
GET /api/logs?org_id=org_456&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z&level=ERROR&limit=100&order=desc HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Query Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `org_id` | string | Yes | Organization ID filter | `org_456` |
| `start_time` | ISO 8601 | Yes | Start of time range (UTC) | `2025-10-23T00:00:00Z` |
| `end_time` | ISO 8601 | Yes | End of time range (UTC) | `2025-10-23T23:59:59Z` |
| `level` | string | No | Log level filter | `ERROR`, `WARNING`, `INFO`, `DEBUG` |
| `user_id` | string | No | Filter by user ID | `user_admin_123` |
| `request_id` | string | No | Filter by request ID (trace) | `req_abc123` |
| `endpoint` | string | No | Filter by API endpoint | `/api/solver/solve` |
| `search` | string | No | Keyword search (full-text) | `database connection` |
| `limit` | integer | No | Max results (default 100, max 1000) | `100` |
| `offset` | integer | No | Pagination offset (default 0) | `0` |
| `order` | string | No | Sort order (asc/desc, default desc) | `desc` |

**Response (200 OK)**:
```json
{
  "logs": [
    {
      "timestamp": "2025-10-23T08:15:30.123Z",
      "level": "ERROR",
      "message": "Database connection timeout after 2000ms",
      "logger": "api.services.database",
      "request_id": "req_abc123",
      "user_id": "user_admin_456",
      "org_id": "org_456",
      "endpoint": "/api/events",
      "method": "POST",
      "status_code": 500,
      "duration_ms": 2150,
      "ip_address": "203.0.113.42",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
      "error": {
        "type": "DatabaseError",
        "message": "Connection timeout",
        "stack_trace": "Traceback (most recent call last):\n  File..."
      },
      "context": {
        "query": "SELECT * FROM events WHERE org_id = :org_id",
        "params": {"org_id": "org_456"}
      }
    },
    {
      "timestamp": "2025-10-23T08:14:25.456Z",
      "level": "WARNING",
      "message": "Slow query detected: 1250ms",
      "logger": "api.middleware.performance",
      "request_id": "req_def456",
      "user_id": "user_volunteer_789",
      "org_id": "org_456",
      "endpoint": "/api/people",
      "method": "GET",
      "status_code": 200,
      "duration_ms": 1250,
      "context": {
        "query_type": "select_people",
        "rows_returned": 250
      }
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0,
  "query_time_ms": 150,
  "next_offset": null
}
```

**Status Codes**:
- `200 OK`: Logs retrieved successfully
- `400 Bad Request`: Invalid query parameters (e.g., invalid date format, limit > 1000)
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not authorized or wrong organization
- `422 Unprocessable Entity`: Invalid time range (end_time before start_time, range > 7 days)
- `503 Service Unavailable`: Log search service (CloudWatch/Elasticsearch) unavailable

**Validation Rules**:
- `start_time` and `end_time`: Required, must be valid ISO 8601 format with timezone
- `end_time` must be after `start_time`
- Time range limit: Maximum 7 days (prevents expensive queries)
- `level`: Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `limit`: 1-1000 (default 100)
- `offset`: >= 0
- `order`: Must be "asc" or "desc"

---

## Log Entry Structure

### JSON Log Format

**Standard Fields** (present in all logs):
```json
{
  "timestamp": "2025-10-23T08:15:30.123Z",
  "level": "ERROR",
  "message": "Human-readable log message",
  "logger": "api.module.function",
  "hostname": "api-server-1",
  "process_id": 12345,
  "thread_id": 67890
}
```

**Request Context Fields** (present for HTTP requests):
```json
{
  "request_id": "req_abc123",
  "user_id": "user_admin_456",
  "org_id": "org_456",
  "endpoint": "/api/events",
  "method": "POST",
  "status_code": 500,
  "duration_ms": 2150,
  "ip_address": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "referer": "https://app.signupflow.io/schedule"
}
```

**Error Context Fields** (present for ERROR/CRITICAL logs):
```json
{
  "error": {
    "type": "DatabaseError",
    "message": "Connection timeout",
    "stack_trace": "Traceback...",
    "file": "api/database.py",
    "line": 123,
    "function": "execute_query"
  }
}
```

**Custom Context Fields** (application-specific):
```json
{
  "context": {
    "query": "SELECT ...",
    "params": {...},
    "solver_complexity": "high",
    "cache_hit": false
  }
}
```

---

## Log Levels

| Level | Severity | Use Case | Example |
|-------|----------|----------|---------|
| **DEBUG** | Lowest | Development debugging, variable dumps | `"User input: {data}"` |
| **INFO** | Normal | Normal operations, audit trail | `"User logged in: user_admin_123"` |
| **WARNING** | Attention | Potentially problematic situations | `"Slow query: 1250ms"` |
| **ERROR** | Failure | Application errors, exceptions | `"Database connection timeout"` |
| **CRITICAL** | Emergency | System failures requiring immediate action | `"Database unavailable"` |

---

## Search Capabilities

### 1. Time Range Search

**Query**: Get all logs in specific time range.

```
GET /api/logs?org_id=org_456&start_time=2025-10-23T08:00:00Z&end_time=2025-10-23T09:00:00Z
```

**Result**: All logs between 8:00 AM and 9:00 AM on Oct 23, 2025.

---

### 2. Log Level Filtering

**Query**: Get all ERROR logs.

```
GET /api/logs?org_id=org_456&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z&level=ERROR
```

**Result**: Only ERROR-level logs for the day.

---

### 3. Request Tracing

**Query**: Trace specific request through system.

```
GET /api/logs?org_id=org_456&request_id=req_abc123&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z
```

**Result**: All logs related to request `req_abc123` across multiple services/functions.

**Use Case**: Trace request flow through application:
```
[INFO] Received POST /api/solver/solve (req_abc123)
[DEBUG] Loading 50 people from database (req_abc123)
[DEBUG] Loading 20 events from database (req_abc123)
[INFO] Starting solver execution (req_abc123)
[WARNING] Solver taking longer than expected: 45s (req_abc123)
[INFO] Solver completed successfully (req_abc123)
[INFO] Saved 100 assignments to database (req_abc123)
[INFO] Returned 200 OK (req_abc123)
```

---

### 4. User Activity Tracking

**Query**: Track specific user's actions.

```
GET /api/logs?org_id=org_456&user_id=user_admin_123&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z
```

**Result**: All logs related to user `user_admin_123` (audit trail).

**Use Case**: Security investigation, user behavior analysis.

---

### 5. Endpoint Performance Analysis

**Query**: Analyze specific endpoint performance.

```
GET /api/logs?org_id=org_456&endpoint=/api/solver/solve&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z
```

**Result**: All logs related to `/api/solver/solve` endpoint.

**Use Case**: Identify slow requests, error patterns for specific endpoint.

---

### 6. Keyword Search (Full-Text)

**Query**: Search for specific error messages.

```
GET /api/logs?org_id=org_456&search=database+connection&start_time=2025-10-23T00:00:00Z&end_time=2025-10-23T23:59:59Z
```

**Result**: All logs containing "database connection" in message or context.

**Use Case**: Find all instances of specific error, search for specific user action.

---

## Implementation

### Backend Service

**File**: `api/services/log_service.py`

```python
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import boto3  # AWS CloudWatch Logs
from elasticsearch import Elasticsearch  # Elasticsearch alternative

class LogService:
    """Service for searching and analyzing application logs."""

    def __init__(self):
        # Initialize CloudWatch Logs client (or Elasticsearch)
        self.cloudwatch = boto3.client('logs', region_name='us-east-1')
        self.log_group_name = "/signupflow/api/production"

    def search_logs(
        self,
        org_id: str,
        start_time: datetime,
        end_time: datetime,
        level: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Search logs with filters and pagination.

        Returns:
            {
                "logs": [log entries],
                "total": total count,
                "limit": limit,
                "offset": offset,
                "query_time_ms": query execution time,
                "next_offset": next offset or None
            }
        """
        # Validate time range (max 7 days)
        if (end_time - start_time).days > 7:
            raise ValueError("Time range must be <= 7 days")

        # Build CloudWatch Logs Insights query
        query = self._build_cloudwatch_query(
            org_id=org_id,
            level=level,
            user_id=user_id,
            request_id=request_id,
            endpoint=endpoint,
            search=search
        )

        # Execute query
        start_query_time = time.time()

        response = self.cloudwatch.start_query(
            logGroupName=self.log_group_name,
            startTime=int(start_time.timestamp()),
            endTime=int(end_time.timestamp()),
            queryString=query,
            limit=limit
        )

        query_id = response['queryId']

        # Poll for query completion (up to 30 seconds)
        for _ in range(30):
            result = self.cloudwatch.get_query_results(queryId=query_id)
            status = result['status']

            if status == 'Complete':
                break

            time.sleep(1)

        query_time_ms = int((time.time() - start_query_time) * 1000)

        # Parse results
        logs = self._parse_cloudwatch_results(result['results'])

        # Apply offset and ordering
        if order == "desc":
            logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        else:
            logs = sorted(logs, key=lambda x: x['timestamp'])

        logs = logs[offset:offset + limit]

        return {
            "logs": logs,
            "total": len(result['results']),
            "limit": limit,
            "offset": offset,
            "query_time_ms": query_time_ms,
            "next_offset": offset + limit if len(result['results']) > offset + limit else None
        }

    def _build_cloudwatch_query(
        self,
        org_id: str,
        level: Optional[str],
        user_id: Optional[str],
        request_id: Optional[str],
        endpoint: Optional[str],
        search: Optional[str]
    ) -> str:
        """
        Build CloudWatch Logs Insights query.

        CloudWatch Logs Insights Query Language:
        - fields: Select fields to return
        - filter: Filter conditions
        - sort: Sort order
        - limit: Max results
        """
        query_parts = [
            "fields @timestamp, level, message, logger, request_id, user_id, org_id, endpoint, method, status_code, duration_ms, error, context"
        ]

        # Add filters
        filters = [f"org_id = '{org_id}'"]

        if level:
            filters.append(f"level = '{level}'")

        if user_id:
            filters.append(f"user_id = '{user_id}'")

        if request_id:
            filters.append(f"request_id = '{request_id}'")

        if endpoint:
            filters.append(f"endpoint = '{endpoint}'")

        if search:
            # Full-text search across message and context
            filters.append(f"(message like /{search}/ or context like /{search}/)")

        if filters:
            query_parts.append(f"| filter {' and '.join(filters)}")

        # Sort by timestamp descending
        query_parts.append("| sort @timestamp desc")

        return " ".join(query_parts)

    def _parse_cloudwatch_results(self, results: List[Dict]) -> List[Dict]:
        """Parse CloudWatch Logs Insights results into structured log entries."""
        logs = []

        for result in results:
            log_entry = {}
            for field in result:
                field_name = field['field']
                field_value = field['value']

                # Parse JSON fields
                if field_name in ['error', 'context']:
                    try:
                        log_entry[field_name] = json.loads(field_value)
                    except:
                        log_entry[field_name] = field_value
                else:
                    log_entry[field_name] = field_value

            logs.append(log_entry)

        return logs
```

**Alternative: Elasticsearch Implementation**

```python
class ElasticsearchLogService:
    """Service for searching logs using Elasticsearch."""

    def __init__(self):
        self.es = Elasticsearch(
            hosts=[os.getenv("ELASTICSEARCH_URL")],
            http_auth=(os.getenv("ELASTICSEARCH_USER"), os.getenv("ELASTICSEARCH_PASSWORD"))
        )
        self.index_name = "signupflow-logs-*"

    def search_logs(self, org_id: str, start_time: datetime, end_time: datetime, **filters) -> Dict:
        """Search logs using Elasticsearch Query DSL."""
        # Build Elasticsearch query
        query = {
            "bool": {
                "must": [
                    {"term": {"org_id": org_id}},
                    {"range": {
                        "timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }}
                ]
            }
        }

        # Add filters
        if filters.get("level"):
            query["bool"]["must"].append({"term": {"level": filters["level"]}})

        if filters.get("user_id"):
            query["bool"]["must"].append({"term": {"user_id": filters["user_id"]}})

        if filters.get("request_id"):
            query["bool"]["must"].append({"term": {"request_id": filters["request_id"]}})

        if filters.get("search"):
            query["bool"]["must"].append({
                "multi_match": {
                    "query": filters["search"],
                    "fields": ["message", "context.*"]
                }
            })

        # Execute search
        response = self.es.search(
            index=self.index_name,
            query=query,
            size=filters.get("limit", 100),
            from_=filters.get("offset", 0),
            sort=[{"timestamp": {"order": filters.get("order", "desc")}}]
        )

        # Parse results
        logs = [hit["_source"] for hit in response["hits"]["hits"]]

        return {
            "logs": logs,
            "total": response["hits"]["total"]["value"],
            "limit": filters.get("limit", 100),
            "offset": filters.get("offset", 0),
            "query_time_ms": response["took"]
        }
```

---

## Performance Optimization

### 1. Time Range Limitation

**Rule**: Max 7-day time range to prevent expensive queries.

**Reason**: Searching 30 days of logs at 1GB/day = 30GB scan = $15 cost + slow query.

**Enforcement**:
```python
if (end_time - start_time).days > 7:
    raise HTTPException(
        status_code=422,
        detail="Time range must be <= 7 days. For longer ranges, export logs to S3."
    )
```

---

### 2. Index Optimization

**CloudWatch Logs**: Automatic indexing on timestamp, no additional indexes needed.

**Elasticsearch**: Create indexes for common filters.

```json
{
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "org_id": {"type": "keyword"},
      "user_id": {"type": "keyword"},
      "request_id": {"type": "keyword"},
      "endpoint": {"type": "keyword"},
      "message": {"type": "text", "analyzer": "standard"},
      "context": {"type": "object"}
    }
  }
}
```

---

### 3. Query Caching

**Strategy**: Cache log search results for 1 minute (logs rarely change retroactively).

```python
@cache(ttl=60)
def search_logs(org_id, start_time, end_time, **filters):
    # ... search logic
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_log_service.py
def test_build_cloudwatch_query_with_filters():
    """Test CloudWatch query building with filters."""
    query = log_service._build_cloudwatch_query(
        org_id="org_456",
        level="ERROR",
        user_id="user_admin_123"
    )
    assert "org_id = 'org_456'" in query
    assert "level = 'ERROR'" in query
    assert "user_id = 'user_admin_123'" in query
```

### Integration Tests

```python
# tests/integration/test_log_search_api.py
def test_search_logs_by_time_range(client, admin_auth_headers):
    """Test GET /api/logs returns logs in time range."""
    response = client.get(
        "/api/logs",
        params={
            "org_id": "org_test",
            "start_time": "2025-10-23T00:00:00Z",
            "end_time": "2025-10-23T23:59:59Z",
            "limit": 100
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)
```

---

## Performance Requirements

| Metric | Target | Justification |
|--------|--------|---------------|
| **Query Response Time** | <2 seconds | Ops team needs fast troubleshooting |
| **Time Range Limit** | 7 days max | Prevent expensive 30-day scans |
| **Result Limit** | 1000 max | Prevent memory exhaustion |
| **Query Timeout** | 30 seconds | CloudWatch Logs Insights timeout |

---

## Cost Optimization

### CloudWatch Logs Costs

- **Ingestion**: $0.50/GB ingested
- **Storage**: $0.03/GB/month stored
- **Query**: $0.005 per GB scanned

**Example**: 1GB/day logs, 7-day queries = $0.035/query (acceptable)

**Optimization**: Limit to 7-day queries instead of 30-day to reduce cost 4x.

---

## References

- **CloudWatch Logs Insights**: [Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- **Elasticsearch Query DSL**: [Full Text Queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)
- **Structured Logging**: [JSON Logging Best Practices](https://www.loggly.com/ultimate-guide/json-logging-best-practices/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/routers/monitoring.py` and `api/services/log_service.py` during Feature 015 implementation phase
