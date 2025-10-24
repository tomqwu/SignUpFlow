# Status Page API Contract

**Feature**: Monitoring and Observability Platform
**Contract Type**: REST API Endpoint Specification
**Version**: 1.0.0
**Status**: Phase 1 Design
**Date**: 2025-10-23

---

## Overview

Status Page API provides public visibility into SignUpFlow system health, component status, incident history, and uptime metrics. Enables users to check service availability and understand ongoing incidents without requiring authentication.

**Use Cases**:
- Public status page for customers (status.signupflow.io)
- Incident communication during outages
- Historical uptime tracking (99.9% SLA verification)
- Component-level status visibility

---

## API Endpoints

### 1. GET /status - Overall System Status

**Purpose**: Get overall system health status for public consumption.

**Authentication**: None (public endpoint)

**Request**:
```http
GET /status HTTP/1.1
Host: status.signupflow.io
Accept: application/json
```

**Response (200 OK - All Systems Operational)**:
```json
{
  "status": "operational",
  "last_updated": "2025-10-23T10:30:45.123Z",
  "components": [
    {
      "id": "api",
      "name": "API",
      "status": "operational",
      "description": "SignUpFlow REST API",
      "uptime_percentage_24h": 100.0,
      "uptime_percentage_7d": 99.98,
      "uptime_percentage_30d": 99.95
    },
    {
      "id": "web-app",
      "name": "Web Application",
      "status": "operational",
      "description": "SignUpFlow web interface",
      "uptime_percentage_24h": 100.0,
      "uptime_percentage_7d": 100.0,
      "uptime_percentage_30d": 99.99
    },
    {
      "id": "database",
      "name": "Database",
      "status": "operational",
      "description": "PostgreSQL database cluster",
      "uptime_percentage_24h": 100.0,
      "uptime_percentage_7d": 99.99,
      "uptime_percentage_30d": 99.97
    },
    {
      "id": "solver",
      "name": "Scheduling Solver",
      "status": "operational",
      "description": "OR-Tools constraint solver",
      "uptime_percentage_24h": 100.0,
      "uptime_percentage_7d": 100.0,
      "uptime_percentage_30d": 99.98
    }
  ],
  "active_incidents": [],
  "scheduled_maintenances": []
}
```

**Response (200 OK - Partial Outage)**:
```json
{
  "status": "partial_outage",
  "last_updated": "2025-10-23T08:15:30.000Z",
  "components": [
    {
      "id": "api",
      "name": "API",
      "status": "degraded",
      "description": "SignUpFlow REST API",
      "uptime_percentage_24h": 98.5,
      "uptime_percentage_7d": 99.95,
      "uptime_percentage_30d": 99.92,
      "latest_incident_id": "incident_abc123"
    },
    {
      "id": "database",
      "name": "Database",
      "status": "operational",
      "description": "PostgreSQL database cluster",
      "uptime_percentage_24h": 100.0,
      "uptime_percentage_7d": 99.99,
      "uptime_percentage_30d": 99.97
    }
  ],
  "active_incidents": [
    {
      "id": "incident_abc123",
      "title": "Elevated API Error Rates",
      "status": "investigating",
      "severity": "major",
      "affected_components": ["api"],
      "started_at": "2025-10-23T08:00:00.000Z",
      "last_update": "2025-10-23T08:15:30.000Z",
      "latest_message": "We are investigating elevated error rates on the API. The issue appears to be intermittent."
    }
  ],
  "scheduled_maintenances": []
}
```

**Status Codes**:
- `200 OK`: Status retrieved successfully

**Overall Status Values**:
- `operational`: All components operational
- `degraded_performance`: Some components degraded but functional
- `partial_outage`: Some components down
- `major_outage`: Core functionality unavailable
- `under_maintenance`: Scheduled maintenance in progress

**Component Status Values**:
- `operational`: Component fully functional
- `degraded`: Component functional but slow/degraded
- `partial_outage`: Component partially unavailable
- `major_outage`: Component completely unavailable
- `under_maintenance`: Component undergoing maintenance

---

### 2. GET /status/uptime - Historical Uptime Data

**Purpose**: Get historical uptime statistics for SLA verification.

**Authentication**: None (public endpoint)

**Request**:
```http
GET /status/uptime?component=api&period=30d HTTP/1.1
Host: status.signupflow.io
Accept: application/json
```

**Query Parameters**:
- `component` (optional): Component ID filter (api, web-app, database, solver)
- `period` (optional): Time period (24h, 7d, 30d, 90d, default: 30d)

**Response (200 OK)**:
```json
{
  "component": "api",
  "period": "30d",
  "uptime_percentage": 99.95,
  "downtime_minutes": 21.6,
  "total_minutes": 43200,
  "incidents": 2,
  "daily_uptime": [
    {"date": "2025-10-23", "uptime_percentage": 99.8, "downtime_minutes": 2.88},
    {"date": "2025-10-22", "uptime_percentage": 100.0, "downtime_minutes": 0},
    {"date": "2025-10-21", "uptime_percentage": 100.0, "downtime_minutes": 0},
    {"date": "2025-10-20", "uptime_percentage": 99.5, "downtime_minutes": 7.2}
    // ... 26 more days
  ],
  "calculated_at": "2025-10-23T10:30:45.123Z"
}
```

**Status Codes**:
- `200 OK`: Uptime data retrieved successfully
- `400 Bad Request`: Invalid period parameter

---

### 3. GET /status/incidents - Incident History

**Purpose**: List recent incidents and their resolution status.

**Authentication**: None (public endpoint)

**Request**:
```http
GET /status/incidents?status=resolved&limit=20 HTTP/1.1
Host: status.signupflow.io
Accept: application/json
```

**Query Parameters**:
- `status` (optional): Filter by status (investigating, identified, monitoring, resolved)
- `limit` (optional): Max results (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**Response (200 OK)**:
```json
{
  "incidents": [
    {
      "id": "incident_abc123",
      "title": "Database Connection Pool Exhaustion",
      "status": "resolved",
      "severity": "major",
      "affected_components": ["api", "database"],
      "started_at": "2025-10-20T14:30:00.000Z",
      "resolved_at": "2025-10-20T15:45:00.000Z",
      "duration_minutes": 75,
      "updates": [
        {
          "timestamp": "2025-10-20T14:30:00.000Z",
          "status": "investigating",
          "message": "We are investigating reports of API timeouts."
        },
        {
          "timestamp": "2025-10-20T14:45:00.000Z",
          "status": "identified",
          "message": "Issue identified: Database connection pool exhausted. Scaling up database connections."
        },
        {
          "timestamp": "2025-10-20T15:15:00.000Z",
          "status": "monitoring",
          "message": "Connection pool increased. Monitoring for stability."
        },
        {
          "timestamp": "2025-10-20T15:45:00.000Z",
          "status": "resolved",
          "message": "All systems operational. Connection pool has been permanently increased."
        }
      ]
    },
    {
      "id": "incident_def456",
      "title": "Elevated API Error Rates",
      "status": "resolved",
      "severity": "minor",
      "affected_components": ["api"],
      "started_at": "2025-10-18T10:00:00.000Z",
      "resolved_at": "2025-10-18T10:30:00.000Z",
      "duration_minutes": 30,
      "updates": [
        {
          "timestamp": "2025-10-18T10:00:00.000Z",
          "status": "investigating",
          "message": "Investigating intermittent 500 errors on API endpoints."
        },
        {
          "timestamp": "2025-10-18T10:30:00.000Z",
          "status": "resolved",
          "message": "Issue resolved. Transient Redis connection issue, now stable."
        }
      ]
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

**Status Codes**:
- `200 OK`: Incidents retrieved successfully
- `400 Bad Request`: Invalid parameters

**Incident Status Values**:
- `investigating`: Team is investigating the issue
- `identified`: Root cause identified, working on fix
- `monitoring`: Fix applied, monitoring for stability
- `resolved`: Issue completely resolved

**Incident Severity Values**:
- `minor`: Minimal impact, affects small subset of users
- `major`: Significant impact, affects many users
- `critical`: Complete service outage

---

### 4. POST /status/incidents - Create Incident (Admin)

**Purpose**: Create new status page incident during outage.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
POST /status/incidents HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "title": "Database Connection Issues",
  "description": "Investigating database connection timeouts affecting API requests.",
  "severity": "major",
  "affected_components": ["api", "database"],
  "status": "investigating",
  "public": true
}
```

**Request Schema**:
```python
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    severity: str = Field(..., regex="^(minor|major|critical)$")
    affected_components: List[str] = Field(..., min_items=1)
    status: str = Field(..., regex="^(investigating|identified|monitoring|resolved)$")
    public: bool = True
```

**Response (201 Created)**:
```json
{
  "id": "incident_ghi789",
  "title": "Database Connection Issues",
  "description": "Investigating database connection timeouts affecting API requests.",
  "severity": "major",
  "affected_components": ["api", "database"],
  "status": "investigating",
  "public": true,
  "started_at": "2025-10-23T10:30:45.123Z",
  "created_by": "user_admin_123",
  "updates": [
    {
      "timestamp": "2025-10-23T10:30:45.123Z",
      "status": "investigating",
      "message": "Investigating database connection timeouts affecting API requests."
    }
  ]
}
```

**Status Codes**:
- `201 Created`: Incident created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin

---

### 5. POST /status/incidents/{incident_id}/updates - Add Incident Update (Admin)

**Purpose**: Add status update to existing incident.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
POST /status/incidents/incident_ghi789/updates HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "status": "identified",
  "message": "Root cause identified: Database connection pool exhausted. Scaling up capacity."
}
```

**Request Schema**:
```python
class IncidentUpdate(BaseModel):
    status: str = Field(..., regex="^(investigating|identified|monitoring|resolved)$")
    message: str = Field(..., min_length=1, max_length=2000)
```

**Response (201 Created)**:
```json
{
  "id": "incident_ghi789",
  "title": "Database Connection Issues",
  "status": "identified",
  "updates": [
    {
      "timestamp": "2025-10-23T10:30:45.123Z",
      "status": "investigating",
      "message": "Investigating database connection timeouts affecting API requests."
    },
    {
      "timestamp": "2025-10-23T10:45:00.000Z",
      "status": "identified",
      "message": "Root cause identified: Database connection pool exhausted. Scaling up capacity.",
      "created_by": "user_admin_123"
    }
  ],
  "last_update": "2025-10-23T10:45:00.000Z"
}
```

**Status Codes**:
- `201 Created`: Update added successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin
- `404 Not Found`: Incident ID does not exist

---

### 6. POST /status/incidents/{incident_id}/resolve - Resolve Incident (Admin)

**Purpose**: Mark incident as resolved.

**Authentication**: Admin only (JWT Bearer token)

**Request**:
```http
POST /status/incidents/incident_ghi789/resolve HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "message": "All systems operational. Database connection pool permanently increased to handle peak load."
}
```

**Request Schema**:
```python
class ResolveIncident(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
```

**Response (200 OK)**:
```json
{
  "id": "incident_ghi789",
  "status": "resolved",
  "resolved_at": "2025-10-23T11:00:00.000Z",
  "duration_minutes": 30,
  "last_update": {
    "timestamp": "2025-10-23T11:00:00.000Z",
    "status": "resolved",
    "message": "All systems operational. Database connection pool permanently increased to handle peak load."
  }
}
```

**Status Codes**:
- `200 OK`: Incident resolved successfully
- `400 Bad Request`: Incident already resolved
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User not admin
- `404 Not Found`: Incident ID does not exist

---

## Implementation

### Backend Service

**File**: `api/services/status_page_service.py`

```python
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models import StatusIncident, HealthCheckResult
from typing import Dict, List

class StatusPageService:
    """Service for managing public status page data."""

    def get_overall_status(self, db: Session) -> Dict:
        """
        Get overall system status for status page.

        Aggregates:
        - Component health check results
        - Active incidents
        - Uptime statistics
        """
        # Get component statuses
        components = self._get_component_statuses(db)

        # Determine overall status
        component_statuses = [c["status"] for c in components]

        if all(s == "operational" for s in component_statuses):
            overall_status = "operational"
        elif any(s == "major_outage" for s in component_statuses):
            overall_status = "major_outage"
        elif any(s == "partial_outage" for s in component_statuses):
            overall_status = "partial_outage"
        else:
            overall_status = "degraded_performance"

        # Get active incidents
        active_incidents = db.query(StatusIncident).filter(
            StatusIncident.status.in_(["investigating", "identified", "monitoring"]),
            StatusIncident.public == True
        ).order_by(StatusIncident.started_at.desc()).all()

        return {
            "status": overall_status,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "components": components,
            "active_incidents": [
                self._serialize_incident(incident)
                for incident in active_incidents
            ],
            "scheduled_maintenances": []
        }

    def _get_component_statuses(self, db: Session) -> List[Dict]:
        """Get status and uptime for each system component."""
        components = [
            {
                "id": "api",
                "name": "API",
                "description": "SignUpFlow REST API"
            },
            {
                "id": "web-app",
                "name": "Web Application",
                "description": "SignUpFlow web interface"
            },
            {
                "id": "database",
                "name": "Database",
                "description": "PostgreSQL database cluster"
            },
            {
                "id": "solver",
                "name": "Scheduling Solver",
                "description": "OR-Tools constraint solver"
            }
        ]

        for component in components:
            # Get latest health check result
            latest_check = db.query(HealthCheckResult).filter(
                HealthCheckResult.component == component["id"]
            ).order_by(HealthCheckResult.checked_at.desc()).first()

            if latest_check:
                component["status"] = latest_check.status
            else:
                component["status"] = "operational"  # Default

            # Calculate uptime percentages
            component["uptime_percentage_24h"] = self._calculate_uptime(
                component["id"], timedelta(hours=24), db
            )
            component["uptime_percentage_7d"] = self._calculate_uptime(
                component["id"], timedelta(days=7), db
            )
            component["uptime_percentage_30d"] = self._calculate_uptime(
                component["id"], timedelta(days=30), db
            )

        return components

    def _calculate_uptime(self, component: str, period: timedelta, db: Session) -> float:
        """
        Calculate uptime percentage for component over time period.

        Uptime = (total_minutes - downtime_minutes) / total_minutes * 100
        """
        start_time = datetime.utcnow() - period
        end_time = datetime.utcnow()
        total_minutes = period.total_seconds() / 60

        # Query health check results
        checks = db.query(HealthCheckResult).filter(
            HealthCheckResult.component == component,
            HealthCheckResult.checked_at >= start_time
        ).order_by(HealthCheckResult.checked_at).all()

        # Calculate downtime minutes
        downtime_minutes = 0
        previous_check = None

        for check in checks:
            if previous_check and check.status in ["major_outage", "partial_outage"]:
                # Component was down between previous_check and current check
                downtime_delta = (check.checked_at - previous_check.checked_at).total_seconds() / 60
                downtime_minutes += downtime_delta

            previous_check = check

        # Calculate uptime percentage
        uptime_percentage = ((total_minutes - downtime_minutes) / total_minutes) * 100

        return round(uptime_percentage, 2)

    def _serialize_incident(self, incident: StatusIncident) -> Dict:
        """Serialize StatusIncident to public API format."""
        return {
            "id": incident.id,
            "title": incident.title,
            "status": incident.status,
            "severity": incident.severity,
            "affected_components": incident.affected_components,
            "started_at": incident.started_at.isoformat() + "Z",
            "resolved_at": incident.resolved_at.isoformat() + "Z" if incident.resolved_at else None,
            "last_update": incident.updates[-1]["timestamp"] if incident.updates else incident.started_at.isoformat() + "Z",
            "latest_message": incident.updates[-1]["message"] if incident.updates else incident.description
        }

    def create_incident(
        self,
        title: str,
        description: str,
        severity: str,
        affected_components: List[str],
        status: str,
        public: bool,
        created_by: str,
        db: Session
    ) -> StatusIncident:
        """Create new status page incident."""
        incident = StatusIncident(
            id=f"incident_{generate_id()}",
            title=title,
            description=description,
            severity=severity,
            affected_components=affected_components,
            status=status,
            public=public,
            started_at=datetime.utcnow(),
            updates=[
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "status": status,
                    "message": description,
                    "created_by": created_by
                }
            ]
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    def add_incident_update(
        self,
        incident_id: str,
        status: str,
        message: str,
        created_by: str,
        db: Session
    ) -> StatusIncident:
        """Add status update to existing incident."""
        incident = db.query(StatusIncident).filter(
            StatusIncident.id == incident_id
        ).first()

        if not incident:
            raise ValueError("Incident not found")

        # Add update
        incident.updates.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": status,
            "message": message,
            "created_by": created_by
        })

        # Update incident status
        incident.status = status

        db.commit()
        db.refresh(incident)

        return incident

    def resolve_incident(
        self,
        incident_id: str,
        message: str,
        created_by: str,
        db: Session
    ) -> StatusIncident:
        """Mark incident as resolved."""
        incident = db.query(StatusIncident).filter(
            StatusIncident.id == incident_id
        ).first()

        if not incident:
            raise ValueError("Incident not found")

        if incident.status == "resolved":
            raise ValueError("Incident already resolved")

        # Add resolution update
        incident.updates.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "resolved",
            "message": message,
            "created_by": created_by
        })

        # Update incident
        incident.status = "resolved"
        incident.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(incident)

        return incident
```

---

## Status Page Frontend

### HTML/CSS/JavaScript Implementation

**File**: `frontend/status/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignUpFlow Status</title>
    <link rel="stylesheet" href="status.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>SignUpFlow Status</h1>
            <p class="subtitle">Real-time service status and incident updates</p>
        </header>

        <section class="overall-status" id="overall-status">
            <div class="status-indicator operational">
                <span class="status-icon">✓</span>
                <span class="status-text">All Systems Operational</span>
            </div>
            <p class="last-updated">Last updated: <span id="last-updated-time">Loading...</span></p>
        </section>

        <section class="active-incidents" id="active-incidents" style="display: none;">
            <h2>Active Incidents</h2>
            <!-- Incident cards populated by JavaScript -->
        </section>

        <section class="components">
            <h2>System Components</h2>
            <div id="components-list">
                <!-- Component status cards populated by JavaScript -->
            </div>
        </section>

        <section class="incident-history">
            <h2>Recent Incidents</h2>
            <div id="incident-history-list">
                <!-- Incident history populated by JavaScript -->
            </div>
        </section>
    </div>

    <script src="status.js"></script>
</body>
</html>
```

**File**: `frontend/status/status.js`

```javascript
// Status page client-side logic
const API_URL = 'https://status.signupflow.io';

async function loadStatusPage() {
    try {
        // Fetch overall status
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();

        // Update overall status
        updateOverallStatus(data.status, data.last_updated);

        // Update components
        updateComponents(data.components);

        // Show active incidents if any
        if (data.active_incidents.length > 0) {
            updateActiveIncidents(data.active_incidents);
        }

        // Load incident history
        loadIncidentHistory();

    } catch (error) {
        console.error('Failed to load status:', error);
        showError('Unable to load status page. Please try again later.');
    }
}

function updateOverallStatus(status, lastUpdated) {
    const statusSection = document.getElementById('overall-status');
    const statusIndicator = statusSection.querySelector('.status-indicator');

    // Update status class
    statusIndicator.className = `status-indicator ${status}`;

    // Update status text
    const statusTexts = {
        'operational': 'All Systems Operational',
        'degraded_performance': 'Degraded Performance',
        'partial_outage': 'Partial System Outage',
        'major_outage': 'Major System Outage'
    };

    statusIndicator.querySelector('.status-text').textContent = statusTexts[status];

    // Update last updated time
    document.getElementById('last-updated-time').textContent = new Date(lastUpdated).toLocaleString();
}

// Auto-refresh every 60 seconds
setInterval(loadStatusPage, 60000);

// Initial load
loadStatusPage();
```

---

## Performance Requirements

| Metric | Target | Justification |
|--------|--------|---------------|
| **Response Time** | <500ms | Public page, must load fast |
| **Uptime** | 99.99% | Status page must be more reliable than main service |
| **Cache TTL** | 60 seconds | Balance freshness vs load |
| **CDN Distribution** | Global | Low latency worldwide |

---

## Testing

### Unit Tests

```python
# tests/unit/test_status_page_service.py
def test_calculate_uptime_all_operational():
    """Test uptime calculation when component always operational."""
    uptime = status_page_service._calculate_uptime(
        component="api",
        period=timedelta(hours=24),
        db=db_session
    )
    assert uptime == 100.0
```

### Integration Tests

```python
# tests/integration/test_status_page_api.py
def test_get_overall_status(client):
    """Test GET /status returns overall system status."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert data["status"] in ["operational", "degraded_performance", "partial_outage", "major_outage"]
```

---

## References

- **Atlassian Statuspage**: [Best Practices](https://www.atlassian.com/software/statuspage)
- **StatusPage Format**: [JSON Schema](https://www.statuspage.io/api)
- **SLA Calculations**: [Uptime Percentages](https://uptime.is/)

---

**Status**: ✅ Contract Complete
**Next**: Implement in `api/routers/status.py` and `api/services/status_page_service.py` during Feature 015 implementation phase
