# API Contract: Recurring Series Management

**Feature**: Recurring Events UI | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

CRUD operations for managing recurring event series. Enables administrators to create repeating event patterns (weekly, biweekly, monthly) with automatic occurrence generation.

**Base Path**: `/api/recurring-series`
**Authentication**: JWT Bearer token (admin access required for write operations)
**Content-Type**: `application/json`

---

## Endpoints

### 1. Create Recurring Series

**POST** `/api/recurring-series?org_id={org_id}`

Creates a new recurring series and pre-generates all event occurrences.

#### Request

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Sunday Service",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "days_of_week": [6],
    "duration": 60
  },
  "start_datetime": "2025-01-05T10:00:00",
  "count": 52,
  "role_requirements": [
    {
      "role": "Worship Leader",
      "count": 1
    },
    {
      "role": "Sound Technician",
      "count": 1
    }
  ]
}
```

**Field Descriptions**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | 1-200 chars | Series title (applied to all occurrences) |
| `recurrence_rule` | object | Yes | See below | Recurrence pattern (RFC 5545 simplified) |
| `recurrence_rule.frequency` | string | Yes | "daily", "weekly", "monthly" | Recurrence frequency |
| `recurrence_rule.interval` | integer | Yes | 1-4 | Every N days/weeks/months |
| `recurrence_rule.days_of_week` | array | No | [0-6], 0=Mon, 6=Sun | Days for weekly pattern |
| `recurrence_rule.day_of_month` | integer | No | 1-31 | Day for monthly pattern |
| `recurrence_rule.week_of_month` | integer | No | 1-4 or -1 | Week position (1=first, -1=last) |
| `recurrence_rule.duration` | integer | No | 15-480 | Default duration (minutes) |
| `start_datetime` | string (ISO 8601) | Yes | Valid datetime | First occurrence date/time |
| `count` | integer | Yes | 1-104 | Number of occurrences to generate |
| `role_requirements` | array | Yes | min 1 role | Role requirements for all occurrences |

**Recurrence Rule Examples**:

```javascript
// Weekly on Sunday
{
  "frequency": "weekly",
  "interval": 1,
  "days_of_week": [6]
}

// Every 2 weeks on Wednesday
{
  "frequency": "weekly",
  "interval": 2,
  "days_of_week": [2]
}

// Monthly on 15th day
{
  "frequency": "monthly",
  "interval": 1,
  "day_of_month": 15
}

// First Sunday of every month
{
  "frequency": "monthly",
  "interval": 1,
  "days_of_week": [6],
  "week_of_month": 1
}

// Last Friday of every month
{
  "frequency": "monthly",
  "interval": 1,
  "days_of_week": [4],  // Friday
  "week_of_month": -1   // Last
}
```

#### Response

**Success Response** (201 Created):
```json
{
  "id": "series_abc123",
  "title": "Sunday Service",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "days_of_week": [6],
    "duration": 60
  },
  "start_datetime": "2025-01-05T10:00:00Z",
  "count": 52,
  "occurrences_created": 52,
  "org_id": "org_456",
  "created_by": "admin_456",
  "created_at": "2025-01-01T08:30:45.123Z",
  "updated_at": "2025-01-01T08:30:45.123Z"
}
```

**Error Responses**:

```json
// 401 Unauthorized - Invalid or missing JWT token
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden - Non-admin user
{
  "detail": "Admin access required"
}

// 403 Forbidden - Wrong organization
{
  "detail": "Access denied: wrong organization"
}

// 422 Unprocessable Entity - Validation error
{
  "detail": [
    {
      "loc": ["body", "count"],
      "msg": "ensure this value is less than or equal to 104",
      "type": "value_error.number.not_le"
    }
  ]
}

// 500 Internal Server Error - Creation failed
{
  "detail": "Failed to create recurring series: Database error"
}
```

#### Implementation Notes

1. **Occurrence Generation**:
   - Use python-dateutil.rrule to calculate all occurrences
   - Generate 52-104 occurrences in <3 seconds (target 1s)
   - Store all occurrences in `events` table with `series_id` foreign key

2. **Database Transaction**:
   - Create `recurring_series` record
   - Generate all `events` records
   - Commit atomically (all succeed or all fail)

3. **Validation**:
   - Verify user has admin role
   - Verify user belongs to organization
   - Validate recurrence rule (Pydantic schema)
   - Enforce max 104 occurrences (2 years)

4. **Performance**:
   - Use bulk insert for events (single SQL statement)
   - Return immediately after creation (no background processing)

**Example Implementation**:

```python
@router.post("/recurring-series")
def create_recurring_series(
    request: RecurringSeriesCreate,
    org_id: str = Query(...),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Create recurring series and pre-generate all occurrences."""
    verify_org_member(admin, org_id)

    # Create series
    series = RecurringSeries(
        id=f"series_{generate_id()}",
        org_id=org_id,
        title=request.title,
        recurrence_rule=request.recurrence_rule.dict(),
        start_datetime=request.start_datetime,
        count=request.count,
        created_by=admin.id
    )
    db.add(series)

    # Generate occurrences
    recurrence_service = RecurrenceService()
    occurrences = recurrence_service.generate_occurrences(
        pattern=request.recurrence_rule.dict(),
        start_datetime=request.start_datetime,
        count=request.count
    )

    # Create event records
    events = []
    for idx, occurrence_datetime in enumerate(occurrences, start=1):
        event = Event(
            id=f"event_{generate_id()}",
            org_id=org_id,
            title=request.title,
            datetime=occurrence_datetime,
            duration=request.recurrence_rule.duration or 60,
            series_id=series.id,
            sequence_number=idx,
            is_exception=False,
            role_requirements=request.role_requirements
        )
        events.append(event)

    db.bulk_save_objects(events)
    db.commit()

    return {
        "id": series.id,
        "title": series.title,
        "recurrence_rule": series.recurrence_rule,
        "start_datetime": series.start_datetime.isoformat() + "Z",
        "count": series.count,
        "occurrences_created": len(events),
        "org_id": series.org_id,
        "created_by": series.created_by,
        "created_at": series.created_at.isoformat() + "Z",
        "updated_at": series.updated_at.isoformat() + "Z"
    }
```

---

### 2. List Recurring Series

**GET** `/api/recurring-series?org_id={org_id}`

Retrieves all recurring series for an organization.

#### Request

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
```

#### Response

**Success Response** (200 OK):
```json
{
  "series": [
    {
      "id": "series_abc123",
      "title": "Sunday Service",
      "recurrence_rule": {
        "frequency": "weekly",
        "interval": 1,
        "days_of_week": [6]
      },
      "start_datetime": "2025-01-05T10:00:00Z",
      "count": 52,
      "occurrences_created": 52,
      "exceptions_count": 2,
      "next_occurrence": "2025-01-12T10:00:00Z",
      "created_by": "admin_456",
      "created_at": "2025-01-01T08:30:45.123Z"
    },
    {
      "id": "series_def456",
      "title": "Monthly Meeting",
      "recurrence_rule": {
        "frequency": "monthly",
        "interval": 1,
        "day_of_month": 15
      },
      "start_datetime": "2025-01-15T19:00:00Z",
      "count": 12,
      "occurrences_created": 12,
      "exceptions_count": 0,
      "next_occurrence": "2025-02-15T19:00:00Z",
      "created_by": "admin_789",
      "created_at": "2025-01-05T10:15:30.456Z"
    }
  ]
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `next_occurrence` | string (ISO 8601) | Next future occurrence datetime (null if all past) |
| `occurrences_created` | integer | Count of generated event occurrences |
| `exceptions_count` | integer | Count of exceptions (skip + modify) |

#### Implementation Notes

```python
@router.get("/recurring-series")
def list_recurring_series(
    org_id: str = Query(...),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all recurring series for organization."""
    verify_org_member(current_user, org_id)

    series_list = db.query(RecurringSeries)\
        .filter(RecurringSeries.org_id == org_id)\
        .order_by(RecurringSeries.created_at.desc())\
        .all()

    return {
        "series": [
            {
                "id": series.id,
                "title": series.title,
                "recurrence_rule": series.recurrence_rule,
                "start_datetime": series.start_datetime.isoformat() + "Z",
                "count": series.count,
                "occurrences_created": len(series.occurrences),
                "exceptions_count": len(series.exceptions),
                "next_occurrence": get_next_occurrence(series.occurrences),
                "created_by": series.created_by,
                "created_at": series.created_at.isoformat() + "Z"
            }
            for series in series_list
        ]
    }
```

---

### 3. Get Recurring Series Details

**GET** `/api/recurring-series/{series_id}`

Retrieves detailed information about a specific recurring series, including all occurrences and exceptions.

#### Request

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `series_id` | string | Yes | Recurring series ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
```

#### Response

**Success Response** (200 OK):
```json
{
  "id": "series_abc123",
  "title": "Sunday Service",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "days_of_week": [6],
    "duration": 60
  },
  "start_datetime": "2025-01-05T10:00:00Z",
  "count": 52,
  "org_id": "org_456",
  "created_by": "admin_456",
  "created_at": "2025-01-01T08:30:45.123Z",
  "updated_at": "2025-01-01T08:30:45.123Z",
  "occurrences": [
    {
      "id": "event_abc123",
      "datetime": "2025-01-05T10:00:00Z",
      "sequence_number": 1,
      "is_exception": false
    },
    {
      "id": "event_def456",
      "datetime": "2025-01-12T10:00:00Z",
      "sequence_number": 2,
      "is_exception": false
    },
    {
      "id": "event_ghi789",
      "datetime": "2025-12-25T12:00:00Z",
      "sequence_number": 52,
      "is_exception": true
    }
  ],
  "exceptions": [
    {
      "id": "exception_christmas_2025",
      "exception_type": "modify",
      "original_date": "2025-12-25T10:00:00Z",
      "modified_datetime": "2025-12-25T12:00:00Z",
      "reason": "Christmas Day - moved to noon",
      "created_by": "admin_456",
      "created_at": "2025-12-01T09:00:00.000Z"
    }
  ]
}
```

**Error Responses**:

```json
// 404 Not Found - Series doesn't exist
{
  "detail": "Recurring series not found"
}

// 403 Forbidden - Wrong organization
{
  "detail": "Access denied: wrong organization"
}
```

---

### 4. Update Recurring Series

**PUT** `/api/recurring-series/{series_id}`

Updates recurring series metadata (title, role requirements). Does NOT change recurrence pattern or occurrence dates.

#### Request

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `series_id` | string | Yes | Recurring series ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Sunday Worship Service",
  "role_requirements": [
    {
      "role": "Worship Leader",
      "count": 2
    },
    {
      "role": "Sound Technician",
      "count": 1
    }
  ]
}
```

**Allowed Updates**:
- `title`: Series title (applied to all future occurrences)
- `role_requirements`: Role requirements (applied to all future occurrences)

**NOT Allowed** (create new series instead):
- `recurrence_rule`: Changing pattern requires re-generation
- `start_datetime`: Changing start date requires re-generation
- `count`: Changing occurrence count requires re-generation

#### Response

**Success Response** (200 OK):
```json
{
  "id": "series_abc123",
  "title": "Sunday Worship Service",
  "updated_at": "2025-01-10T14:22:30.789Z"
}
```

**Error Responses**:

```json
// 403 Forbidden - Admin access required
{
  "detail": "Admin access required"
}

// 404 Not Found
{
  "detail": "Recurring series not found"
}
```

#### Implementation Notes

```python
@router.put("/recurring-series/{series_id}")
def update_recurring_series(
    series_id: str,
    request: RecurringSeriesUpdate,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Update recurring series metadata (title, role requirements)."""
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    verify_org_member(admin, series.org_id)

    # Update series metadata
    if request.title:
        series.title = request.title

    # Update all future occurrences
    future_occurrences = db.query(Event).filter(
        Event.series_id == series_id,
        Event.datetime >= datetime.utcnow()
    ).all()

    for event in future_occurrences:
        if request.title:
            event.title = request.title
        if request.role_requirements:
            event.role_requirements = request.role_requirements

    series.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": series.id,
        "title": series.title,
        "updated_at": series.updated_at.isoformat() + "Z"
    }
```

---

### 5. Delete Recurring Series

**DELETE** `/api/recurring-series/{series_id}`

Deletes recurring series and all associated occurrences (past and future).

#### Request

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `series_id` | string | Yes | Recurring series ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
```

#### Response

**Success Response** (200 OK):
```json
{
  "status": "deleted",
  "series_id": "series_abc123",
  "occurrences_deleted": 52,
  "exceptions_deleted": 2
}
```

**Error Responses**:

```json
// 403 Forbidden - Admin access required
{
  "detail": "Admin access required"
}

// 404 Not Found
{
  "detail": "Recurring series not found"
}
```

#### Implementation Notes

- Cascade delete automatically removes all `events` with `series_id`
- Cascade delete automatically removes all `recurrence_exceptions` with `series_id`
- Operation is atomic (all succeed or all fail)

```python
@router.delete("/recurring-series/{series_id}")
def delete_recurring_series(
    series_id: str,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Delete recurring series and all occurrences."""
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    verify_org_member(admin, series.org_id)

    # Count before delete
    occurrences_count = db.query(Event).filter(Event.series_id == series_id).count()
    exceptions_count = db.query(RecurrenceException).filter(RecurrenceException.series_id == series_id).count()

    # Delete series (cascades to events and exceptions)
    db.delete(series)
    db.commit()

    return {
        "status": "deleted",
        "series_id": series_id,
        "occurrences_deleted": occurrences_count,
        "exceptions_deleted": exceptions_count
    }
```

---

## Security & Authorization

### Authentication

All endpoints require JWT Bearer token:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Authorization Rules

| Endpoint | Allowed Roles | Organization Check |
|----------|---------------|-------------------|
| POST /recurring-series | Admin | Yes (verify admin belongs to org_id) |
| GET /recurring-series | Admin, Volunteer | Yes (verify user belongs to org_id) |
| GET /recurring-series/{id} | Admin, Volunteer | Yes (verify series belongs to user's org) |
| PUT /recurring-series/{id} | Admin | Yes (verify admin belongs to series org) |
| DELETE /recurring-series/{id} | Admin | Yes (verify admin belongs to series org) |

### Multi-Tenant Isolation

**Critical**: Every query must filter by organization to prevent data leaks:

```python
# ✅ CORRECT - Filters by org_id
series = db.query(RecurringSeries)\
    .filter(RecurringSeries.org_id == current_user.org_id)\
    .all()

# ❌ WRONG - Allows cross-organization access
series = db.query(RecurringSeries).all()
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /recurring-series | 10 requests | 1 minute |
| GET /recurring-series | 60 requests | 1 minute |
| GET /recurring-series/{id} | 60 requests | 1 minute |
| PUT /recurring-series/{id} | 30 requests | 1 minute |
| DELETE /recurring-series/{id} | 10 requests | 1 minute |

**Rationale**: Creating series is expensive (generates 52-104 events), limit to prevent abuse.

---

## Testing Requirements

### Unit Tests
- Test recurrence rule validation (valid/invalid patterns)
- Test occurrence generation logic (52 occurrences from weekly pattern)
- Test exception handling edge cases

### Integration Tests
- Test POST creates series + all occurrences in single transaction
- Test GET returns all series for organization
- Test DELETE removes series + all occurrences
- Test multi-tenant isolation (can't access other org's series)

### E2E Tests
- Test admin can create series from UI
- Test calendar preview shows all occurrences
- Test volunteer can view (but not edit) series
- Test series deletion removes all occurrences

---

## Related Contracts

- [Recurrence Exceptions API](./recurrence-exceptions-api.md) - Skip or modify individual occurrences
- [Bulk Edit API](./bulk-edit-api.md) - Bulk update multiple occurrences
- [Calendar Preview API](./calendar-preview-api.md) - Preview occurrences before creation

---

**Document Status**: ✅ Complete
**Next Action**: Generate remaining 3 API contracts
