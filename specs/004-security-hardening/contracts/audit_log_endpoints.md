# API Contract: Audit Log Endpoints

**Feature**: Security Hardening & Compliance
**Purpose**: Immutable audit trail for admin actions (SOC 2, GDPR compliance)

---

## Endpoint Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/audit-logs` | GET | Admin | List audit logs with filtering |
| `/api/audit-logs/export` | GET | Admin | Export audit logs as CSV |
| `/api/audit-logs/stats` | GET | Admin | Audit log statistics dashboard |

**Note**: Audit log creation (`POST /api/internal/audit-logs`) is internal only, called automatically by middleware (not exposed to clients).

---

## 1. List Audit Logs

### Request

**Method**: `GET`
**Path**: `/api/audit-logs`
**Authentication**: Required (Admin only)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `org_id` | String | Yes | Organization ID (multi-tenant isolation) | `org_church_12345` |
| `limit` | Integer | No | Number of results per page (default: 50, max: 500) | `50` |
| `offset` | Integer | No | Pagination offset (default: 0) | `0` |
| `action_type` | String | No | Filter by action type | `user_role_changed` |
| `actor_person_id` | String | No | Filter by actor (who performed action) | `person_admin_67890` |
| `resource_type` | String | No | Filter by resource type | `person` |
| `resource_id` | String | No | Filter by specific resource | `person_volunteer_11111` |
| `start_date` | DateTime | No | Filter logs after this date (ISO 8601) | `2025-01-01T00:00:00Z` |
| `end_date` | DateTime | No | Filter logs before this date (ISO 8601) | `2025-12-31T23:59:59Z` |

**Example Request**:
```bash
# All logs for organization
curl "https://signupflow.io/api/audit-logs?org_id=org_church_12345&limit=50&offset=0" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Filter by action type
curl "https://signupflow.io/api/audit-logs?org_id=org_church_12345&action_type=user_role_changed" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Filter by date range
curl "https://signupflow.io/api/audit-logs?org_id=org_church_12345&start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "audit_logs": [
    {
      "id": "audit_20251020_143052_abc123",
      "timestamp": "2025-10-20T14:30:52Z",
      "actor": {
        "person_id": "person_admin_67890",
        "name": "Admin User",
        "email": "admin@example.com"
      },
      "action_type": "user_role_changed",
      "resource_type": "person",
      "resource": {
        "resource_id": "person_volunteer_11111",
        "name": "John Doe"
      },
      "changes": {
        "before": {
          "roles": ["volunteer"]
        },
        "after": {
          "roles": ["volunteer", "admin"]
        }
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    },
    {
      "id": "audit_20251020_140015_def456",
      "timestamp": "2025-10-20T14:00:15Z",
      "actor": {
        "person_id": "person_admin_67890",
        "name": "Admin User",
        "email": "admin@example.com"
      },
      "action_type": "event_created",
      "resource_type": "event",
      "resource": {
        "resource_id": "event_20251020_140015",
        "name": "Sunday Worship Service"
      },
      "changes": {
        "before": null,
        "after": {
          "title": "Sunday Worship Service",
          "datetime": "2025-10-27T10:00:00Z",
          "role_requirements": {...}
        }
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "pagination": {
    "total": 1234,
    "limit": 50,
    "offset": 0,
    "has_more": true,
    "next_offset": 50
  },
  "filters_applied": {
    "org_id": "org_church_12345",
    "action_type": null,
    "start_date": null,
    "end_date": null
  }
}
```

**Field Definitions**:
- `audit_logs`: Array of audit log entries (most recent first)
- `pagination.total`: Total number of logs matching filters
- `pagination.has_more`: Whether more results available
- `actor.person_id`: User who performed action (may be null if user deleted)
- `resource.name`: Human-readable name (denormalized for display)
- `changes.before`: Resource state before action (null for creation)
- `changes.after`: Resource state after action (null for deletion)

**Error (403 Forbidden)** - Not Admin:
```json
{
  "error": "admin_access_required",
  "message": "Admin access required to view audit logs."
}
```

**Error (422 Unprocessable Entity)** - Invalid Filters:
```json
{
  "error": "validation_error",
  "message": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ).",
  "field": "start_date"
}
```

---

## 2. Export Audit Logs (CSV)

### Request

**Method**: `GET`
**Path**: `/api/audit-logs/export`
**Authentication**: Required (Admin only)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | String | Yes | Organization ID |
| `format` | String | No | Export format: `csv`, `json` (default: csv) |
| `start_date` | DateTime | No | Filter logs after this date |
| `end_date` | DateTime | No | Filter logs before this date |
| `action_type` | String | No | Filter by action type |

**Example Request**:
```bash
# Export all logs as CSV
curl "https://signupflow.io/api/audit-logs/export?org_id=org_church_12345&format=csv" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -o audit_logs.csv

# Export date range as JSON
curl "https://signupflow.io/api/audit-logs/export?org_id=org_church_12345&format=json&start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -o audit_logs_2025.json
```

### Response

**Success (200 OK)** - CSV Format:
```http
Content-Type: text/csv
Content-Disposition: attachment; filename="audit_logs_org_church_12345_2025-10-20.csv"

id,timestamp,actor_email,actor_name,action_type,resource_type,resource_id,resource_name,changes_summary,ip_address
audit_20251020_143052_abc123,2025-10-20T14:30:52Z,admin@example.com,Admin User,user_role_changed,person,person_volunteer_11111,John Doe,"roles: [volunteer] → [volunteer, admin]",192.168.1.100
audit_20251020_140015_def456,2025-10-20T14:00:15Z,admin@example.com,Admin User,event_created,event,event_20251020_140015,Sunday Worship Service,"Created event",192.168.1.100
```

**Success (200 OK)** - JSON Format:
```http
Content-Type: application/json
Content-Disposition: attachment; filename="audit_logs_org_church_12345_2025-10-20.json"

[
  {
    "id": "audit_20251020_143052_abc123",
    "timestamp": "2025-10-20T14:30:52Z",
    "actor_email": "admin@example.com",
    "actor_name": "Admin User",
    "action_type": "user_role_changed",
    "resource_type": "person",
    "resource_id": "person_volunteer_11111",
    "resource_name": "John Doe",
    "changes": {
      "before": {"roles": ["volunteer"]},
      "after": {"roles": ["volunteer", "admin"]}
    },
    "ip_address": "192.168.1.100"
  }
]
```

**CSV Column Definitions**:
- `id`: Audit log unique identifier
- `timestamp`: ISO 8601 datetime (UTC)
- `actor_email`: Email of user who performed action
- `actor_name`: Name of user who performed action
- `action_type`: Type of action (user_role_changed, event_created, etc.)
- `resource_type`: Type of resource affected
- `resource_id`: ID of affected resource
- `resource_name`: Human-readable name of resource
- `changes_summary`: Human-readable summary of changes (for CSV)
- `ip_address`: IP address of client

**Error (403 Forbidden)** - Not Admin:
```json
{
  "error": "admin_access_required",
  "message": "Admin access required to export audit logs."
}
```

---

## 3. Audit Log Statistics

### Request

**Method**: `GET`
**Path**: `/api/audit-logs/stats`
**Authentication**: Required (Admin only)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | String | Yes | Organization ID |
| `period` | String | No | Time period: `24h`, `7d`, `30d`, `12m` (default: 30d) |

**Example Request**:
```bash
curl "https://signupflow.io/api/audit-logs/stats?org_id=org_church_12345&period=30d" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "period": "30d",
  "start_date": "2025-09-20T00:00:00Z",
  "end_date": "2025-10-20T23:59:59Z",
  "total_logs": 1234,
  "by_action_type": [
    {
      "action_type": "event_created",
      "count": 456,
      "percentage": 36.9
    },
    {
      "action_type": "user_role_changed",
      "count": 234,
      "percentage": 19.0
    },
    {
      "action_type": "team_member_added",
      "count": 189,
      "percentage": 15.3
    }
  ],
  "top_actors": [
    {
      "person_id": "person_admin_67890",
      "name": "Admin User",
      "email": "admin@example.com",
      "action_count": 567,
      "percentage": 46.0
    },
    {
      "person_id": "person_admin_11111",
      "name": "Secondary Admin",
      "email": "admin2@example.com",
      "action_count": 345,
      "percentage": 28.0
    }
  ],
  "daily_activity": [
    {
      "date": "2025-10-20",
      "count": 45
    },
    {
      "date": "2025-10-19",
      "count": 38
    },
    {
      "date": "2025-10-18",
      "count": 52
    }
  ]
}
```

**Field Definitions**:
- `by_action_type`: Breakdown of actions by type (most frequent first)
- `top_actors`: Most active administrators (by number of actions)
- `daily_activity`: Daily activity trend (last 30 days)

**Error (403 Forbidden)** - Not Admin:
```json
{
  "error": "admin_access_required",
  "message": "Admin access required to view audit log statistics."
}
```

---

## Action Types Reference

### User Management
| Action Type | Description | Changes Tracked |
|-------------|-------------|-----------------|
| `user_created` | New user account created | Email, name, roles |
| `user_updated` | User profile modified | Changed fields (name, email) |
| `user_deleted` | User account deleted | Previous user data |
| `user_role_changed` | User roles modified | Before/after roles array |
| `user_invited` | Invitation sent | Email, roles |

### Event Management
| Action Type | Description | Changes Tracked |
|-------------|-------------|-----------------|
| `event_created` | New event created | Title, datetime, role_requirements |
| `event_updated` | Event details modified | Changed fields |
| `event_deleted` | Event removed | Previous event data |
| `event_published` | Event published to volunteers | Publication status |
| `schedule_generated` | AI solver generated schedule | Assignments count |

### Team Management
| Action Type | Description | Changes Tracked |
|-------------|-------------|-----------------|
| `team_created` | New team created | Team name, role |
| `team_updated` | Team details modified | Changed fields |
| `team_deleted` | Team removed | Previous team data |
| `team_member_added` | Person added to team | Person ID, name |
| `team_member_removed` | Person removed from team | Person ID, name |

### Security Events
| Action Type | Description | Changes Tracked |
|-------------|-------------|-----------------|
| `password_changed` | User password updated | None (security) |
| `2fa_enabled` | Two-factor authentication enabled | Timestamp |
| `2fa_disabled` | Two-factor authentication disabled | Timestamp |
| `login_failed` | Failed login attempt | IP address, username |
| `session_invalidated` | Session terminated | Reason (password change) |

---

## Compliance Mapping

### SOC 2 Type II

**CC6.3 - Logical Access Controls**:
- ✅ Audit logs track all administrative access and changes
- ✅ Immutable logs (append-only, no updates/deletes)
- ✅ 12-month retention exceeds 90-day minimum

**Audit Log Query for Compliance**:
```bash
# Get all role changes in last 12 months
curl "https://signupflow.io/api/audit-logs/export?org_id=org_church_12345&action_type=user_role_changed&start_date=2024-10-20T00:00:00Z&format=csv" \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -o role_changes_audit_2024-2025.csv
```

### GDPR Article 30

**Records of Processing Activities**:
- ✅ Audit logs document who accessed/modified personal data
- ✅ IP address and timestamp tracked for all actions
- ✅ Changes field shows before/after values (data transparency)

**Data Subject Access Request (DSAR)**:
```bash
# Get all actions performed on specific user's data
curl "https://signupflow.io/api/audit-logs?org_id=org_church_12345&resource_type=person&resource_id=person_volunteer_11111" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

---

## Frontend Implementation Example

**Admin Dashboard - Audit Log Viewer** (`frontend/index.html`):
```html
<div id="audit-log-panel" class="admin-panel">
  <h2 data-i18n="admin.audit_logs.title">Audit Log</h2>

  <!-- Filters -->
  <div class="filters">
    <select id="action-type-filter">
      <option value="">All Actions</option>
      <option value="user_role_changed">Role Changes</option>
      <option value="event_created">Event Created</option>
      <option value="event_deleted">Event Deleted</option>
    </select>

    <input type="date" id="start-date-filter" placeholder="Start Date">
    <input type="date" id="end-date-filter" placeholder="End Date">

    <button id="apply-filters-btn" data-i18n="common.buttons.apply_filters">Apply</button>
    <button id="export-logs-btn" data-i18n="common.buttons.export">Export CSV</button>
  </div>

  <!-- Audit Log Table -->
  <table id="audit-log-table">
    <thead>
      <tr>
        <th data-i18n="admin.audit_logs.timestamp">Timestamp</th>
        <th data-i18n="admin.audit_logs.actor">User</th>
        <th data-i18n="admin.audit_logs.action">Action</th>
        <th data-i18n="admin.audit_logs.resource">Resource</th>
        <th data-i18n="admin.audit_logs.changes">Changes</th>
      </tr>
    </thead>
    <tbody id="audit-log-tbody">
      <!-- Populated via JavaScript -->
    </tbody>
  </table>

  <!-- Pagination -->
  <div class="pagination">
    <button id="prev-page-btn">Previous</button>
    <span id="page-info">Page 1 of 25</span>
    <button id="next-page-btn">Next</button>
  </div>
</div>
```

**JavaScript Handler** (`frontend/js/app-admin.js`):
```javascript
// Load audit logs
async function loadAuditLogs(filters = {}) {
    const params = new URLSearchParams({
        org_id: currentUser.org_id,
        limit: 50,
        offset: filters.offset || 0,
        ...(filters.action_type && { action_type: filters.action_type }),
        ...(filters.start_date && { start_date: filters.start_date }),
        ...(filters.end_date && { end_date: filters.end_date })
    });

    const response = await authFetch(`/api/audit-logs?${params}`);
    const data = await response.json();

    // Populate table
    const tbody = document.getElementById('audit-log-tbody');
    tbody.innerHTML = '';

    data.audit_logs.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(log.timestamp).toLocaleString()}</td>
            <td>${log.actor.name} (${log.actor.email})</td>
            <td>${formatActionType(log.action_type)}</td>
            <td>${log.resource.name || log.resource.resource_id}</td>
            <td><button onclick="showChanges('${log.id}')">View</button></td>
        `;
        tbody.appendChild(row);
    });

    // Update pagination
    updatePagination(data.pagination);
}

// Export audit logs
async function exportAuditLogs() {
    const filters = getAppliedFilters();
    const params = new URLSearchParams({
        org_id: currentUser.org_id,
        format: 'csv',
        ...filters
    });

    const response = await authFetch(`/api/audit-logs/export?${params}`);
    const blob = await response.blob();

    // Trigger download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// Show changes modal
function showChanges(logId) {
    const log = auditLogs.find(l => l.id === logId);
    if (!log) return;

    const modal = document.getElementById('changes-modal');
    const content = document.getElementById('changes-content');

    content.innerHTML = `
        <h3>Changes</h3>
        <pre>${JSON.stringify(log.changes, null, 2)}</pre>
    `;

    modal.style.display = 'block';
}
```

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_audit_service.py
def test_create_audit_log():
    """Test audit log creation with all fields."""

def test_audit_log_immutable():
    """Test audit logs cannot be updated or deleted."""

def test_filter_audit_logs_by_action_type():
    """Test filtering by action_type returns correct logs."""

def test_filter_audit_logs_by_date_range():
    """Test date range filtering works correctly."""
```

### Integration Tests

```python
# tests/integration/test_audit_log_endpoints.py
def test_list_audit_logs_admin_only():
    """Test GET /api/audit-logs requires admin role."""

def test_export_audit_logs_csv_format():
    """Test GET /api/audit-logs/export returns valid CSV."""

def test_audit_log_statistics():
    """Test GET /api/audit-logs/stats returns breakdown."""
```

### E2E Tests

```python
# tests/e2e/test_audit_logging.py
def test_user_role_change_creates_audit_log(page: Page):
    """
    Test complete audit log workflow:
    1. Admin changes user role
    2. Navigate to Audit Log tab
    3. Filter by action_type = user_role_changed
    4. Verify log entry appears with correct details
    5. Click "View Changes" → verify before/after values shown
    """

def test_export_audit_logs_downloads_csv(page: Page):
    """
    Test audit log export:
    1. Admin navigates to Audit Log tab
    2. Select date range filter
    3. Click Export CSV button
    4. Verify CSV file downloaded
    5. Verify CSV contains expected columns and data
    """
```

---

**Last Updated**: 2025-10-20
**Status**: Complete API specification for audit log endpoints
**Related**: data-model.md (AuditLog entity), research.md (SOC 2 compliance requirements)
