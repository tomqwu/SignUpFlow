# API Contract: Wizard State Management

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

API endpoints for managing onboarding wizard state, step progression, and validation.

---

## Base URL

```
/api/onboarding/wizard
```

**Authentication**: Required (JWT Bearer token)
**Rate Limit**: 100 requests per minute per organization
**RBAC**: Admin only (wizard state management)

---

## Endpoints

### 1. Get Wizard State

**Endpoint**: `GET /api/onboarding/wizard`

**Description**: Retrieve current onboarding wizard state for organization.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Example**:

```http
GET /api/onboarding/wizard?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK):

```json
{
  "wizard_state": {
    "organization_id": "org_123",
    "wizard_completed": false,
    "wizard_current_step": 2,
    "wizard_step_data": {
      "step_1": {
        "organization_name": "Grace Community Church",
        "location": "123 Main St, Toronto, ON",
        "timezone": "America/Toronto",
        "completed": true
      },
      "step_2": {
        "event_title": "Sunday Morning Service",
        "event_datetime": "2025-11-01T10:00:00",
        "completed": false
      }
    },
    "skipped": false,
    "started_at": "2025-10-23T14:00:00Z",
    "completed_at": null
  },
  "available_steps": [
    {
      "step_number": 1,
      "step_id": "organization_profile",
      "title": "Organization Profile",
      "completed": true
    },
    {
      "step_number": 2,
      "step_id": "first_event",
      "title": "Create First Event",
      "completed": false,
      "current": true
    },
    {
      "step_number": 3,
      "step_id": "first_team",
      "title": "Create First Team",
      "completed": false
    },
    {
      "step_number": 4,
      "step_id": "invite_volunteers",
      "title": "Invite Volunteers",
      "completed": false
    },
    {
      "step_number": 5,
      "step_id": "tutorial_intro",
      "title": "Tutorial Introduction",
      "completed": false
    }
  ],
  "can_advance": true,
  "can_skip": true,
  "progress_percent": 20
}
```

**Error Responses**:

```json
// 401 Unauthorized - Missing or invalid JWT token
{
  "error": "Unauthorized",
  "message": "Authentication required"
}

// 403 Forbidden - User not an admin
{
  "error": "Forbidden",
  "message": "Admin access required"
}

// 404 Not Found - No onboarding state exists
{
  "error": "Not Found",
  "message": "Onboarding state not found for organization org_123"
}
```

---

### 2. Update Wizard Step Data

**Endpoint**: `PUT /api/onboarding/wizard`

**Description**: Update wizard step data and optionally advance to next step.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "step_number": 2,
  "step_data": {
    "event_title": "Sunday Morning Service",
    "event_datetime": "2025-11-01T10:00:00",
    "event_duration": 120,
    "event_location": "Main Sanctuary",
    "role_requirements": {
      "Worship Leader": 2,
      "Greeter": 4,
      "Usher": 3
    }
  },
  "mark_completed": true,
  "advance_step": true
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `step_number` | integer | Yes | Current wizard step (1-5) |
| `step_data` | object | Yes | Step-specific form data |
| `mark_completed` | boolean | No | Mark step as completed (default: false) |
| `advance_step` | boolean | No | Advance to next step (default: false) |

**Success Response** (200 OK):

```json
{
  "wizard_state": {
    "organization_id": "org_123",
    "wizard_completed": false,
    "wizard_current_step": 3,
    "wizard_step_data": {
      "step_1": {
        "organization_name": "Grace Community Church",
        "completed": true
      },
      "step_2": {
        "event_title": "Sunday Morning Service",
        "event_datetime": "2025-11-01T10:00:00",
        "event_duration": 120,
        "completed": true
      },
      "step_3": {
        "completed": false
      }
    },
    "started_at": "2025-10-23T14:00:00Z",
    "completed_at": null
  },
  "next_step": {
    "step_number": 3,
    "step_id": "first_team",
    "title": "Create First Team"
  },
  "progress_percent": 40,
  "message": "Wizard step 2 completed successfully. Advanced to step 3."
}
```

**Validation Errors** (422 Unprocessable Entity):

```json
{
  "error": "Validation Error",
  "message": "Cannot advance to next step without completing current step",
  "details": {
    "step_number": 2,
    "validation_failures": [
      {
        "field": "event_datetime",
        "error": "Event date must be in the future"
      },
      {
        "field": "role_requirements",
        "error": "At least one role requirement is needed"
      }
    ]
  }
}
```

**Error Responses**:

```json
// 400 Bad Request - Invalid step number
{
  "error": "Bad Request",
  "message": "Invalid step number. Must be between 1 and 5."
}

// 409 Conflict - Wizard already completed
{
  "error": "Conflict",
  "message": "Wizard already completed. Cannot modify completed wizard."
}
```

---

### 3. Skip Wizard

**Endpoint**: `POST /api/onboarding/wizard/skip`

**Description**: Skip onboarding wizard entirely (for experienced users).

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "skip_reason": "experienced_user",
  "show_all_features": true
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skip_reason` | string | No | Reason for skipping (`experienced_user`, `return_later`, `other`) |
| `show_all_features` | boolean | No | Unlock all features immediately (default: true) |

**Success Response** (200 OK):

```json
{
  "wizard_state": {
    "organization_id": "org_123",
    "wizard_completed": false,
    "wizard_current_step": 1,
    "skipped": true,
    "skipped_at": "2025-10-23T14:30:00Z",
    "show_all_features": true
  },
  "message": "Onboarding wizard skipped. All features unlocked."
}
```

**Analytics Event Triggered**:

```json
{
  "event_type": "wizard_skipped",
  "wizard_step_dropped": 1,
  "event_data": {
    "skip_reason": "experienced_user",
    "time_spent_seconds": 45
  }
}
```

---

### 4. Reset Wizard

**Endpoint**: `POST /api/onboarding/wizard/reset`

**Description**: Reset wizard to beginning (clear all progress).

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "clear_sample_data": true,
  "reset_checklist": false
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `clear_sample_data` | boolean | No | Delete sample data if exists (default: false) |
| `reset_checklist` | boolean | No | Reset checklist progress (default: false) |

**Success Response** (200 OK):

```json
{
  "wizard_state": {
    "organization_id": "org_123",
    "wizard_completed": false,
    "wizard_current_step": 1,
    "wizard_step_data": {},
    "skipped": false,
    "started_at": "2025-10-23T15:00:00Z",
    "completed_at": null
  },
  "message": "Wizard reset to step 1. Sample data cleared.",
  "sample_data_cleared": true
}
```

---

### 5. Complete Wizard

**Endpoint**: `POST /api/onboarding/wizard/complete`

**Description**: Mark wizard as completed (all steps finished).

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "final_step_data": {
    "tutorials_shown": true,
    "dashboard_redirected": true
  }
}
```

**Success Response** (200 OK):

```json
{
  "wizard_state": {
    "organization_id": "org_123",
    "wizard_completed": true,
    "wizard_current_step": 5,
    "wizard_step_data": {
      "step_1": { "completed": true },
      "step_2": { "completed": true },
      "step_3": { "completed": true },
      "step_4": { "completed": true },
      "step_5": { "completed": true }
    },
    "skipped": false,
    "started_at": "2025-10-23T14:00:00Z",
    "completed_at": "2025-10-23T14:45:00Z"
  },
  "completion_time_minutes": 45,
  "message": "Congratulations! Onboarding completed successfully.",
  "next_steps": [
    {
      "action": "create_event",
      "url": "/app/events/create",
      "title": "Create Your First Event"
    },
    {
      "action": "invite_volunteers",
      "url": "/app/people/invite",
      "title": "Invite Volunteers"
    }
  ]
}
```

**Analytics Event Triggered**:

```json
{
  "event_type": "wizard_completed",
  "completion_time_minutes": 45,
  "event_data": {
    "steps_completed": 5,
    "sample_data_used": true,
    "tutorials_viewed": 2
  }
}
```

**Error Responses**:

```json
// 400 Bad Request - Not all steps completed
{
  "error": "Bad Request",
  "message": "Cannot complete wizard. Not all steps are marked complete.",
  "details": {
    "incomplete_steps": [3, 4]
  }
}

// 409 Conflict - Already completed
{
  "error": "Conflict",
  "message": "Wizard already completed at 2025-10-23T14:45:00Z"
}
```

---

## Step-Specific Data Schemas

### Step 1: Organization Profile

```json
{
  "organization_name": "Grace Community Church",
  "location": "123 Main St, Toronto, ON M5V 1A1, Canada",
  "timezone": "America/Toronto",
  "organization_type": "church",
  "volunteer_count_estimate": "20-50"
}
```

**Validation Rules**:
- `organization_name`: 3-100 characters, required
- `location`: 10-500 characters, required
- `timezone`: Valid IANA timezone, required
- `organization_type`: Enum (`church`, `non_profit`, `sports_league`, `other`), optional
- `volunteer_count_estimate`: Enum (`1-10`, `10-20`, `20-50`, `50-100`, `100+`), optional

### Step 2: First Event

```json
{
  "event_title": "Sunday Morning Service",
  "event_datetime": "2025-11-01T10:00:00",
  "event_duration": 120,
  "event_location": "Main Sanctuary",
  "event_description": "Weekly worship service",
  "role_requirements": {
    "Worship Leader": 2,
    "Greeter": 4,
    "Usher": 3
  }
}
```

**Validation Rules**:
- `event_title`: 3-200 characters, required
- `event_datetime`: ISO 8601 datetime, must be future date, required
- `event_duration`: Integer 15-480 minutes, required
- `event_location`: 3-200 characters, optional
- `role_requirements`: Object with string keys and integer values >0, required (at least 1 role)

### Step 3: First Team

```json
{
  "team_name": "Worship Team",
  "team_role": "Worship Leader",
  "team_description": "Leads Sunday morning worship services",
  "team_size_estimate": "5-10"
}
```

**Validation Rules**:
- `team_name`: 3-100 characters, required
- `team_role`: 3-100 characters, required
- `team_description`: 0-500 characters, optional
- `team_size_estimate`: Enum (`1-5`, `5-10`, `10-20`, `20+`), optional

### Step 4: Invite Volunteers

```json
{
  "invitation_emails": [
    "volunteer1@example.com",
    "volunteer2@example.com",
    "volunteer3@example.com"
  ],
  "invitation_message": "Join our volunteer team!",
  "assign_to_team": "team_worship_123",
  "send_immediately": true
}
```

**Validation Rules**:
- `invitation_emails`: Array of valid email addresses, 1-50 emails, required
- `invitation_message`: 0-500 characters, optional
- `assign_to_team`: Valid team ID, optional
- `send_immediately`: Boolean, default true

### Step 5: Tutorial Introduction

```json
{
  "tutorials_shown": true,
  "tutorials_to_show": ["events_intro", "solver_run"],
  "skip_tutorials": false,
  "dashboard_redirected": true
}
```

**Validation Rules**:
- `tutorials_shown`: Boolean, required
- `tutorials_to_show`: Array of valid tutorial IDs, optional
- `skip_tutorials`: Boolean, default false

---

## Business Logic Rules

### Wizard Progression Rules

1. **Sequential Steps**: Cannot advance to step N+1 without completing step N
2. **Step Validation**: Each step has validation rules that must pass before marking complete
3. **Skip Anytime**: User can skip wizard at any step (doesn't prevent access to app)
4. **One-Time Completion**: Once wizard completed, cannot be reopened (must reset)
5. **Resume Support**: If user leaves wizard, they can resume from last completed step

### State Persistence Rules

1. **Auto-Save**: Step data auto-saved on every PUT request (no manual save required)
2. **Partial Progress**: User can save incomplete step data (draft state)
3. **Validation on Advance**: Strict validation only when `advance_step = true`
4. **No Rollback**: Cannot go backwards to previous steps (edit via reset only)

### Skip vs Complete

| Action | wizard_completed | skipped | Behavior |
|--------|------------------|---------|----------|
| Skip wizard | FALSE | TRUE | Bypass wizard, unlock all features |
| Complete wizard | TRUE | FALSE | Normal completion flow |
| Reset wizard | FALSE | FALSE | Start over from step 1 |

---

## Analytics Events Triggered

### Automatic Event Tracking

| API Action | Event Type | Event Data |
|------------|------------|------------|
| GET wizard state | `wizard_viewed` | `{ step: current_step }` |
| PUT step data | `wizard_step_completed` | `{ step: N, duration_seconds: X }` |
| POST skip | `wizard_skipped` | `{ step_dropped: N, skip_reason: X }` |
| POST complete | `wizard_completed` | `{ completion_time_minutes: X, steps_completed: 5 }` |
| POST reset | `wizard_reset` | `{ previous_step: N, reason: X }` |

---

## Error Handling

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request parameters or body |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User not admin for organization |
| 404 | Not Found | Onboarding state not found |
| 409 | Conflict | State conflict (e.g., wizard already completed) |
| 422 | Validation Error | Step validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Schema

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {
    "field": "specific field that failed",
    "validation_failures": [
      {
        "field": "event_datetime",
        "error": "Must be a future date"
      }
    ]
  },
  "timestamp": "2025-10-23T14:30:00Z"
}
```

---

## Testing Requirements

### Unit Tests
- [ ] Test GET wizard state returns correct data structure
- [ ] Test PUT step data validates step number range (1-5)
- [ ] Test PUT with invalid step data returns 422 validation error
- [ ] Test POST skip sets `skipped = true` and unlocks features
- [ ] Test POST complete validates all steps completed
- [ ] Test POST reset clears wizard state correctly

### Integration Tests
- [ ] Test wizard state created on organization signup
- [ ] Test step progression from 1→2→3→4→5
- [ ] Test validation prevents skipping steps
- [ ] Test skip wizard bypasses validation
- [ ] Test reset wizard clears sample data if requested
- [ ] Test completion triggers analytics events

### E2E Tests
- [ ] Test complete wizard flow in browser (5 steps)
- [ ] Test skip wizard from step 2
- [ ] Test reset wizard and restart from step 1
- [ ] Test validation error messages appear in UI
- [ ] Test auto-save on blur events in form fields

---

## Performance Considerations

### Caching Strategy
- Wizard state cached in Redis for 1 hour (reduce DB queries)
- Cache invalidated on PUT/POST operations
- Cache key format: `onboarding:wizard:{org_id}`

### Query Optimization
- Index on `organization_id` for fast lookups
- JSON column queries use PostgreSQL JSONB operators
- Limit JSON field sizes (<10KB per step)

---

## Security Considerations

### Input Validation
- Sanitize all user input (SQL injection prevention)
- Validate timezone against IANA timezone database
- Limit array sizes (max 50 invitation emails)
- Check URL formats for XSS prevention

### Authorization
- Verify user is admin for organization before any write operation
- Check `organization_id` matches current user's organization
- Validate JWT token signature and expiration

---

**API Version**: v1
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
