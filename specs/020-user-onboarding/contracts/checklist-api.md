# API Contract: Checklist Progress Management

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

API endpoints for managing onboarding checklist progress, task completion detection, and quick actions.

---

## Base URL

```
/api/onboarding/checklist
```

**Authentication**: Required (JWT Bearer token)
**Rate Limit**: 200 requests per minute per organization
**RBAC**: Admin and Volunteer (checklist is visible to all users)

---

## Endpoints

### 1. Get Checklist Progress

**Endpoint**: `GET /api/onboarding/checklist`

**Description**: Retrieve checklist tasks with real-time completion status for organization.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |
| `include_inactive` | boolean | No | Include inactive tasks (default: false) |

**Request Example**:

```http
GET /api/onboarding/checklist?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):

```json
{
  "checklist": {
    "organization_id": "org_123",
    "tasks": [
      {
        "id": "complete_profile",
        "title": "Complete Organization Profile",
        "description": "Set up your organization name, location, and timezone",
        "completed": true,
        "completed_at": "2025-10-23T14:30:00Z",
        "priority_order": 1,
        "icon": "user-circle",
        "quick_action_url": "/app/settings/organization",
        "completion_criteria": {
          "type": "state_check",
          "field": "wizard_completed",
          "value": true
        }
      },
      {
        "id": "create_first_event",
        "title": "Create Your First Event",
        "description": "Add an event that needs volunteer assignments",
        "completed": false,
        "completed_at": null,
        "priority_order": 2,
        "icon": "calendar",
        "quick_action_url": "/app/events/create",
        "completion_criteria": {
          "type": "database_query",
          "threshold": 1,
          "current_count": 0
        }
      },
      {
        "id": "add_team",
        "title": "Create a Team",
        "description": "Organize volunteers into teams with specific roles",
        "completed": false,
        "completed_at": null,
        "priority_order": 3,
        "icon": "users",
        "quick_action_url": "/app/teams/create"
      },
      {
        "id": "invite_volunteers",
        "title": "Invite Volunteers",
        "description": "Add at least 3 volunteers to your organization",
        "completed": false,
        "completed_at": null,
        "priority_order": 4,
        "icon": "user-plus",
        "quick_action_url": "/app/people/invite",
        "completion_criteria": {
          "type": "database_query",
          "threshold": 3,
          "current_count": 0
        }
      },
      {
        "id": "run_first_schedule",
        "title": "Generate Your First Schedule",
        "description": "Use the AI solver to automatically create assignments",
        "completed": false,
        "completed_at": null,
        "priority_order": 5,
        "icon": "check-circle",
        "quick_action_url": "/app/solver"
      },
      {
        "id": "view_reports",
        "title": "View Reports",
        "description": "Check out volunteer utilization and fairness metrics",
        "completed": false,
        "completed_at": null,
        "priority_order": 6,
        "icon": "bar-chart",
        "quick_action_url": "/app/reports"
      }
    ],
    "progress": {
      "completed_count": 1,
      "total_count": 6,
      "completion_percent": 16.7
    },
    "next_recommended_task": {
      "id": "create_first_event",
      "title": "Create Your First Event",
      "quick_action_url": "/app/events/create"
    }
  },
  "timestamp": "2025-10-23T15:00:00Z"
}
```

**Response Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `checklist.organization_id` | string | Organization ID |
| `checklist.tasks` | array | Array of checklist tasks with completion status |
| `checklist.progress.completed_count` | integer | Number of completed tasks |
| `checklist.progress.total_count` | integer | Total number of tasks |
| `checklist.progress.completion_percent` | float | Completion percentage (0-100) |
| `checklist.next_recommended_task` | object | Next task user should complete |
| `timestamp` | string | When checklist was calculated (ISO 8601) |

**Task Object Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique task identifier |
| `title` | string | Task title (translated via i18n key) |
| `description` | string | Task description (translated via i18n key) |
| `completed` | boolean | Whether task is completed (real-time detection) |
| `completed_at` | string\|null | When task was completed (ISO 8601) |
| `priority_order` | integer | Display order (1-6) |
| `icon` | string | Icon name for UI |
| `quick_action_url` | string | URL to complete task |
| `completion_criteria` | object | Criteria used to determine completion |

---

### 2. Mark Task as Manually Completed

**Endpoint**: `PUT /api/onboarding/checklist/{task_id}`

**Description**: Manually mark specific task as completed (override automatic detection).

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes | Task ID (e.g., `view_reports`) |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "completed": true,
  "manual_override": true
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `completed` | boolean | Yes | Completion status |
| `manual_override` | boolean | No | Override automatic detection (default: false) |

**Request Example**:

```http
PUT /api/onboarding/checklist/view_reports?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "completed": true,
  "manual_override": true
}
```

**Success Response** (200 OK):

```json
{
  "task": {
    "id": "view_reports",
    "title": "View Reports",
    "completed": true,
    "completed_at": "2025-10-23T15:10:00Z",
    "manual_override": true
  },
  "checklist_progress": {
    "completed_count": 2,
    "total_count": 6,
    "completion_percent": 33.3
  },
  "message": "Task 'View Reports' marked as completed"
}
```

**Error Responses**:

```json
// 404 Not Found - Task doesn't exist
{
  "error": "Not Found",
  "message": "Checklist task 'invalid_task' not found"
}

// 400 Bad Request - Cannot manually complete auto-detected task
{
  "error": "Bad Request",
  "message": "Task 'create_first_event' completion is automatically detected. Set manual_override=true to force."
}
```

---

### 3. Reset Checklist Progress

**Endpoint**: `POST /api/onboarding/checklist/reset`

**Description**: Clear all manual overrides and re-calculate checklist from scratch.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**: None

**Success Response** (200 OK):

```json
{
  "checklist_progress": {
    "completed_count": 1,
    "total_count": 6,
    "completion_percent": 16.7,
    "manual_overrides_cleared": 3
  },
  "message": "Checklist reset. All tasks re-calculated from data."
}
```

---

### 4. Get Task Definition

**Endpoint**: `GET /api/onboarding/checklist/tasks/{task_id}`

**Description**: Get detailed information about specific checklist task.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes | Task ID |

**Request Example**:

```http
GET /api/onboarding/checklist/tasks/create_first_event HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):

```json
{
  "task": {
    "id": "create_first_event",
    "title_key": "onboarding.checklist.create_first_event",
    "description_key": "onboarding.checklist.create_first_event_desc",
    "title": "Create Your First Event",
    "description": "Add an event that needs volunteer assignments",
    "priority_order": 2,
    "icon": "calendar",
    "quick_action_url": "/app/events/create",
    "is_active": true,
    "completion_criteria": {
      "type": "database_query",
      "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE",
      "threshold": 1,
      "operator": ">=",
      "description": "Organization has created at least 1 real event"
    },
    "created_at": "2025-10-01T00:00:00Z"
  }
}
```

---

### 5. Get Task Completion History

**Endpoint**: `GET /api/onboarding/checklist/history`

**Description**: Get timeline of when tasks were completed.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Success Response** (200 OK):

```json
{
  "completion_history": [
    {
      "task_id": "complete_profile",
      "task_title": "Complete Organization Profile",
      "completed_at": "2025-10-23T14:30:00Z",
      "time_to_complete_minutes": 15,
      "manual_override": false
    },
    {
      "task_id": "create_first_event",
      "task_title": "Create Your First Event",
      "completed_at": "2025-10-23T14:45:00Z",
      "time_to_complete_minutes": 30,
      "manual_override": false
    }
  ],
  "total_completion_time_minutes": 45,
  "first_task_completed_at": "2025-10-23T14:30:00Z",
  "last_task_completed_at": "2025-10-23T14:45:00Z"
}
```

---

## Completion Criteria Types

### Type: `state_check`

Check if field in `onboarding_state` table matches expected value.

**Criteria Schema**:

```json
{
  "type": "state_check",
  "field": "wizard_completed",
  "value": true
}
```

**Evaluation Logic**:

```python
def evaluate_state_check(criteria, org_state):
    field_value = getattr(org_state, criteria['field'])
    return field_value == criteria['value']
```

**Example Tasks Using This**:
- `complete_profile`: Check if `wizard_completed = TRUE`

---

### Type: `database_query`

Execute SQL query and compare result to threshold.

**Criteria Schema**:

```json
{
  "type": "database_query",
  "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE",
  "threshold": 1,
  "operator": ">=",
  "description": "Organization has created at least 1 real event"
}
```

**Evaluation Logic**:

```python
def evaluate_database_query(criteria, org_id, db):
    result = db.execute(criteria['query'], {'org_id': org_id}).scalar()
    operator = criteria['operator']  # >=, >, <=, <, ==, !=
    threshold = criteria['threshold']

    if operator == '>=':
        return result >= threshold
    elif operator == '>':
        return result > threshold
    # ... other operators
```

**Example Tasks Using This**:
- `create_first_event`: Event count >= 1
- `add_team`: Team count >= 1
- `invite_volunteers`: Volunteer count >= 3
- `run_first_schedule`: Assignment count >= 1

---

### Type: `composite_and`

Multiple criteria, all must be true.

**Criteria Schema**:

```json
{
  "type": "composite_and",
  "criteria": [
    {
      "type": "database_query",
      "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id",
      "threshold": 5,
      "operator": ">="
    },
    {
      "type": "database_query",
      "query": "SELECT COUNT(*) FROM event_assignments WHERE event_id IN (SELECT id FROM events WHERE org_id = :org_id)",
      "threshold": 10,
      "operator": ">="
    }
  ]
}
```

**Evaluation Logic**:

```python
def evaluate_composite_and(criteria, org_id, db):
    for sub_criteria in criteria['criteria']:
        if not evaluate_criteria(sub_criteria, org_id, db):
            return False
    return True
```

---

### Type: `composite_or`

Multiple criteria, any one can be true.

**Criteria Schema**:

```json
{
  "type": "composite_or",
  "criteria": [
    {
      "type": "state_check",
      "field": "sample_data_generated",
      "value": true
    },
    {
      "type": "database_query",
      "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id",
      "threshold": 3,
      "operator": ">="
    }
  ]
}
```

---

## Business Logic Rules

### Completion Detection Rules

1. **Real-Time Calculation**: Task completion status calculated dynamically on every GET request
2. **No Caching**: Completion status not cached (always query database)
3. **Sample Data Excluded**: Queries exclude sample data via `is_sample = FALSE`
4. **Manual Override**: Admin can manually mark tasks complete (stored in `checklist_progress` JSON)
5. **Idempotent**: Marking completed task as complete again has no effect

### Progress Calculation Rules

```python
def calculate_progress(tasks):
    completed_count = sum(1 for task in tasks if task['completed'])
    total_count = len(tasks)
    completion_percent = (completed_count / total_count) * 100

    return {
        'completed_count': completed_count,
        'total_count': total_count,
        'completion_percent': round(completion_percent, 1)
    }
```

### Next Recommended Task

**Logic**: Return first incomplete task by `priority_order`.

```python
def get_next_recommended_task(tasks):
    incomplete_tasks = [t for t in tasks if not t['completed']]
    if incomplete_tasks:
        return min(incomplete_tasks, key=lambda t: t['priority_order'])
    return None
```

---

## Analytics Events Triggered

### Automatic Event Tracking

| API Action | Event Type | Event Data |
|------------|------------|------------|
| GET checklist | `checklist_viewed` | `{ completed_count: X, total_count: 6 }` |
| PUT task completed | `checklist_task_completed` | `{ task_id: X, manual_override: true/false }` |
| POST reset | `checklist_reset` | `{ manual_overrides_cleared: X }` |

**Event Payload Example**:

```json
{
  "event_type": "checklist_task_completed",
  "organization_id": "org_123",
  "event_data": {
    "task_id": "create_first_event",
    "task_title": "Create Your First Event",
    "manual_override": false,
    "time_to_complete_minutes": 30
  },
  "timestamp": "2025-10-23T14:45:00Z"
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User not authorized for organization |
| 404 | Not Found | Task ID not found |
| 422 | Validation Error | Manual override not allowed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Database query failed |

### Error Response Schema

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {
    "task_id": "invalid_task",
    "valid_task_ids": [
      "complete_profile",
      "create_first_event",
      "add_team",
      "invite_volunteers",
      "run_first_schedule",
      "view_reports"
    ]
  },
  "timestamp": "2025-10-23T15:00:00Z"
}
```

---

## Frontend Integration

### JavaScript Example: Fetch Checklist

```javascript
async function loadChecklistProgress(orgId) {
    const response = await authFetch(
        `/api/onboarding/checklist?org_id=${orgId}`
    );

    if (!response.ok) {
        throw new Error('Failed to load checklist');
    }

    const data = await response.json();

    // Update UI with progress
    updateProgressBar(data.checklist.progress.completion_percent);
    renderChecklistTasks(data.checklist.tasks);
    highlightNextTask(data.checklist.next_recommended_task);

    return data;
}

function updateProgressBar(percent) {
    const progressBar = document.getElementById('checklist-progress');
    progressBar.style.width = `${percent}%`;
    progressBar.setAttribute('aria-valuenow', percent);
    progressBar.textContent = `${Math.round(percent)}%`;
}

function renderChecklistTasks(tasks) {
    const container = document.getElementById('checklist-tasks');

    tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = `checklist-task ${task.completed ? 'completed' : ''}`;
        taskElement.innerHTML = `
            <div class="task-icon">
                <i class="icon-${task.icon}"></i>
            </div>
            <div class="task-content">
                <h4>${task.title}</h4>
                <p>${task.description}</p>
            </div>
            <div class="task-status">
                ${task.completed ?
                    '<i class="icon-check-circle completed"></i>' :
                    `<a href="${task.quick_action_url}" class="btn-quick-action">Do This</a>`
                }
            </div>
        `;

        container.appendChild(taskElement);
    });
}
```

### JavaScript Example: Quick Action Button

```javascript
function handleQuickAction(taskId, quickActionUrl) {
    // Track analytics
    trackChecklistAction(taskId, 'quick_action_clicked');

    // Navigate to action URL
    window.location.href = quickActionUrl;
}

async function trackChecklistAction(taskId, actionType) {
    await authFetch('/api/analytics/onboarding-events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event_type: 'checklist_action',
            event_data: {
                task_id: taskId,
                action_type: actionType
            }
        })
    });
}
```

---

## Testing Requirements

### Unit Tests
- [ ] Test state_check criteria evaluation logic
- [ ] Test database_query criteria with different operators
- [ ] Test composite_and criteria (all must pass)
- [ ] Test composite_or criteria (any can pass)
- [ ] Test progress calculation (0%, 50%, 100%)
- [ ] Test next recommended task selection

### Integration Tests
- [ ] Test GET checklist returns 6 tasks
- [ ] Test task completion detection (create event → task marked complete)
- [ ] Test manual override marks task complete
- [ ] Test reset clears manual overrides
- [ ] Test sample data excluded from completion queries
- [ ] Test analytics events triggered on task completion

### E2E Tests
- [ ] Test checklist appears in onboarding dashboard
- [ ] Test progress bar updates when task completed
- [ ] Test quick action button navigates to correct page
- [ ] Test checkmark appears when task auto-detected as complete
- [ ] Test "next recommended task" highlighted in UI

---

## Performance Considerations

### Query Optimization
- **Problem**: Running 6 SQL queries on every GET request (one per task)
- **Solution**: Batch queries into single SQL statement with JOINs and aggregates
- **Target**: <100ms total query time for all 6 tasks

**Optimized Query Example**:

```sql
WITH task_counts AS (
    SELECT
        (SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE) AS event_count,
        (SELECT COUNT(*) FROM teams WHERE org_id = :org_id AND is_sample = FALSE) AS team_count,
        (SELECT COUNT(*) FROM people WHERE org_id = :org_id AND is_sample = FALSE AND roles LIKE '%volunteer%') AS volunteer_count,
        (SELECT COUNT(*) FROM event_assignments ea
         JOIN events e ON ea.event_id = e.id
         WHERE e.org_id = :org_id AND e.is_sample = FALSE) AS assignment_count
)
SELECT * FROM task_counts;
```

### Caching Strategy
- **No caching**: Checklist must always reflect current state
- **Alternative**: Cache for 30 seconds with Redis (acceptable staleness)
- **Cache key**: `checklist:{org_id}`
- **Invalidate**: On any data change (event created, team created, etc.)

---

## Security Considerations

### SQL Injection Prevention
- All queries use parameterized queries (`:org_id` placeholder)
- No user input directly concatenated into SQL
- Queries stored in database, not user-editable

### Authorization
- User must be member of organization to view checklist
- Admin required to manually mark tasks complete
- Rate limiting prevents brute force detection of org data

---

**API Version**: v1
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
