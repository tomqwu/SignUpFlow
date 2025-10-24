# API Contract: Recurrence Exception Management

**Feature**: Recurring Events UI | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

Manages exceptions for individual occurrences in recurring series. Enables administrators to skip (cancel) or modify (reschedule) specific occurrences without affecting the entire series.

**Base Path**: `/api/recurring-series/{series_id}/exceptions`
**Authentication**: JWT Bearer token (admin access required)
**Content-Type**: `application/json`

---

## Use Cases

### Skip Occurrence (Cancel)
- **Example**: Skip Christmas Day service (Dec 25)
- **Behavior**: Delete event occurrence from database
- **Use Case**: Holiday closures, cancelled events

### Modify Occurrence (Reschedule)
- **Example**: Move New Year's Day service from 10 AM to 12 PM
- **Behavior**: Update event datetime, mark as exception
- **Use Case**: Time changes, venue conflicts

---

## Endpoints

### 1. Create Exception

**POST** `/api/recurring-series/{series_id}/exceptions`

Creates an exception to skip or modify a specific occurrence.

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
  "exception_type": "skip",
  "original_date": "2025-12-25T10:00:00",
  "modified_datetime": null,
  "reason": "Christmas Day - service cancelled"
}
```

**Field Descriptions**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `exception_type` | string | Yes | "skip" or "modify" | Exception type |
| `original_date` | string (ISO 8601) | Yes | Must match existing occurrence | Original occurrence datetime |
| `modified_datetime` | string (ISO 8601) | Conditional | Required if type="modify", null if type="skip" | New datetime for rescheduled occurrence |
| `reason` | string | No | max 500 chars | Human-readable reason for exception |

#### Response

**Success Response** (201 Created):

**Skip Exception**:
```json
{
  "id": "exception_christmas_2025",
  "series_id": "series_abc123",
  "exception_type": "skip",
  "original_date": "2025-12-25T10:00:00Z",
  "modified_datetime": null,
  "reason": "Christmas Day - service cancelled",
  "created_by": "admin_456",
  "created_at": "2025-12-01T09:00:00.000Z",
  "event_deleted": true
}
```

**Modify Exception**:
```json
{
  "id": "exception_newyear_2026",
  "series_id": "series_abc123",
  "exception_type": "modify",
  "original_date": "2026-01-01T10:00:00Z",
  "modified_datetime": "2026-01-01T12:00:00Z",
  "reason": "New Year's Day - moved to noon",
  "created_by": "admin_456",
  "created_at": "2025-12-15T10:30:00.000Z",
  "event_updated": true
}
```

**Error Responses**:

```json
// 401 Unauthorized
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden - Non-admin user
{
  "detail": "Admin access required"
}

// 404 Not Found - Series doesn't exist
{
  "detail": "Recurring series not found"
}

// 404 Not Found - Occurrence doesn't exist
{
  "detail": "No occurrence found for date 2025-12-25T10:00:00"
}

// 409 Conflict - Exception already exists
{
  "detail": "Exception already exists for date 2025-12-25T10:00:00"
}

// 422 Unprocessable Entity - Validation error
{
  "detail": [
    {
      "loc": ["body", "modified_datetime"],
      "msg": "modified_datetime required for 'modify' exception type",
      "type": "value_error"
    }
  ]
}
```

#### Implementation Notes

1. **Skip Exception Behavior**:
   - Create exception record in `recurrence_exceptions` table
   - Delete corresponding event from `events` table
   - Mark event as skipped in calendar preview

2. **Modify Exception Behavior**:
   - Create exception record in `recurrence_exceptions` table
   - Update event datetime in `events` table
   - Set `event.is_exception = true` flag
   - Preserve `event.series_id` and `event.sequence_number`

3. **Validation**:
   - Verify series exists and belongs to user's organization
   - Verify occurrence exists at `original_date`
   - Verify no duplicate exception for same date
   - Validate `modified_datetime` format and logic

**Example Implementation**:

```python
@router.post("/recurring-series/{series_id}/exceptions")
def create_exception(
    series_id: str,
    request: RecurrenceExceptionCreate,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Create exception to skip or modify occurrence."""
    # Verify series exists
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    verify_org_member(admin, series.org_id)

    # Verify occurrence exists
    event = db.query(Event).filter(
        Event.series_id == series_id,
        Event.datetime == request.original_date
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"No occurrence found for date {request.original_date}"
        )

    # Check for duplicate exception
    existing_exception = db.query(RecurrenceException).filter(
        RecurrenceException.series_id == series_id,
        RecurrenceException.original_date == request.original_date
    ).first()

    if existing_exception:
        raise HTTPException(
            status_code=409,
            detail=f"Exception already exists for date {request.original_date}"
        )

    # Create exception record
    exception = RecurrenceException(
        id=f"exception_{generate_id()}",
        series_id=series_id,
        exception_type=request.exception_type,
        original_date=request.original_date,
        modified_datetime=request.modified_datetime if request.exception_type == "modify" else None,
        reason=request.reason,
        created_by=admin.id
    )

    db.add(exception)

    # Apply exception to event
    if request.exception_type == "skip":
        # Delete event occurrence
        db.delete(event)
        event_deleted = True
        event_updated = False
    elif request.exception_type == "modify":
        # Update event datetime
        event.datetime = request.modified_datetime
        event.is_exception = True
        event_deleted = False
        event_updated = True

    db.commit()

    return {
        "id": exception.id,
        "series_id": exception.series_id,
        "exception_type": exception.exception_type,
        "original_date": exception.original_date.isoformat() + "Z",
        "modified_datetime": exception.modified_datetime.isoformat() + "Z" if exception.modified_datetime else None,
        "reason": exception.reason,
        "created_by": exception.created_by,
        "created_at": exception.created_at.isoformat() + "Z",
        "event_deleted": event_deleted,
        "event_updated": event_updated
    }
```

---

### 2. List Exceptions for Series

**GET** `/api/recurring-series/{series_id}/exceptions`

Retrieves all exceptions for a recurring series.

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
  "exceptions": [
    {
      "id": "exception_christmas_2025",
      "exception_type": "skip",
      "original_date": "2025-12-25T10:00:00Z",
      "modified_datetime": null,
      "reason": "Christmas Day - service cancelled",
      "created_by": "admin_456",
      "created_at": "2025-12-01T09:00:00.000Z"
    },
    {
      "id": "exception_newyear_2026",
      "exception_type": "modify",
      "original_date": "2026-01-01T10:00:00Z",
      "modified_datetime": "2026-01-01T12:00:00Z",
      "reason": "New Year's Day - moved to noon",
      "created_by": "admin_456",
      "created_at": "2025-12-15T10:30:00.000Z"
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

#### Implementation Notes

```python
@router.get("/recurring-series/{series_id}/exceptions")
def list_exceptions(
    series_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all exceptions for recurring series."""
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    verify_org_member(current_user, series.org_id)

    exceptions = db.query(RecurrenceException)\
        .filter(RecurrenceException.series_id == series_id)\
        .order_by(RecurrenceException.original_date)\
        .all()

    return {
        "exceptions": [
            {
                "id": exception.id,
                "exception_type": exception.exception_type,
                "original_date": exception.original_date.isoformat() + "Z",
                "modified_datetime": exception.modified_datetime.isoformat() + "Z" if exception.modified_datetime else None,
                "reason": exception.reason,
                "created_by": exception.created_by,
                "created_at": exception.created_at.isoformat() + "Z"
            }
            for exception in exceptions
        ]
    }
```

---

### 3. Get Exception Details

**GET** `/api/recurring-series/{series_id}/exceptions/{exception_id}`

Retrieves detailed information about a specific exception.

#### Request

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `series_id` | string | Yes | Recurring series ID |
| `exception_id` | string | Yes | Exception ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
```

#### Response

**Success Response** (200 OK):
```json
{
  "id": "exception_christmas_2025",
  "series_id": "series_abc123",
  "exception_type": "skip",
  "original_date": "2025-12-25T10:00:00Z",
  "modified_datetime": null,
  "reason": "Christmas Day - service cancelled",
  "created_by": "admin_456",
  "created_at": "2025-12-01T09:00:00.000Z",
  "series_title": "Sunday Service"
}
```

**Error Responses**:

```json
// 404 Not Found - Exception doesn't exist
{
  "detail": "Exception not found"
}

// 403 Forbidden - Wrong organization
{
  "detail": "Access denied: wrong organization"
}
```

---

### 4. Delete Exception (Restore Occurrence)

**DELETE** `/api/recurring-series/{series_id}/exceptions/{exception_id}`

Deletes an exception and restores the original occurrence.

#### Request

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `series_id` | string | Yes | Recurring series ID |
| `exception_id` | string | Yes | Exception ID |

**Headers**:
```
Authorization: Bearer <jwt_token>
```

#### Response

**Success Response** (200 OK):
```json
{
  "status": "deleted",
  "exception_id": "exception_christmas_2025",
  "occurrence_restored": true,
  "restored_datetime": "2025-12-25T10:00:00Z"
}
```

**Error Responses**:

```json
// 403 Forbidden - Admin access required
{
  "detail": "Admin access required"
}

// 404 Not Found - Exception doesn't exist
{
  "detail": "Exception not found"
}
```

#### Implementation Notes

1. **Skip Exception Deletion**:
   - Delete exception record
   - Re-create event occurrence with original datetime
   - Restore `series_id`, `sequence_number`, `is_exception=false`

2. **Modify Exception Deletion**:
   - Delete exception record
   - Restore event to original datetime
   - Set `event.is_exception = false`

**Example Implementation**:

```python
@router.delete("/recurring-series/{series_id}/exceptions/{exception_id}")
def delete_exception(
    series_id: str,
    exception_id: str,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Delete exception and restore original occurrence."""
    exception = db.query(RecurrenceException).filter(
        RecurrenceException.id == exception_id,
        RecurrenceException.series_id == series_id
    ).first()

    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")

    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()
    verify_org_member(admin, series.org_id)

    occurrence_restored = False
    restored_datetime = None

    if exception.exception_type == "skip":
        # Re-create deleted event occurrence
        # Calculate sequence number
        sequence_number = db.query(Event).filter(
            Event.series_id == series_id,
            Event.datetime < exception.original_date
        ).count() + 1

        event = Event(
            id=f"event_{generate_id()}",
            org_id=series.org_id,
            title=series.title,
            datetime=exception.original_date,
            duration=series.recurrence_rule.get("duration", 60),
            series_id=series_id,
            sequence_number=sequence_number,
            is_exception=False,
            role_requirements=[]  # Copy from series or first occurrence
        )

        db.add(event)
        occurrence_restored = True
        restored_datetime = exception.original_date

    elif exception.exception_type == "modify":
        # Restore event to original datetime
        event = db.query(Event).filter(
            Event.series_id == series_id,
            Event.is_exception == True
        ).filter(
            # Find event that was modified (has different datetime)
            Event.sequence_number == get_sequence_from_date(series, exception.original_date)
        ).first()

        if event:
            event.datetime = exception.original_date
            event.is_exception = False
            occurrence_restored = True
            restored_datetime = exception.original_date

    # Delete exception record
    db.delete(exception)
    db.commit()

    return {
        "status": "deleted",
        "exception_id": exception_id,
        "occurrence_restored": occurrence_restored,
        "restored_datetime": restored_datetime.isoformat() + "Z" if restored_datetime else None
    }
```

---

## Exception Workflows

### Workflow 1: Skip Occurrence (Cancel Event)

```
User Action:
  1. Admin views calendar preview
  2. Clicks occurrence (Dec 25, 10 AM)
  3. Selects "Skip this occurrence"
  4. Enters reason: "Christmas Day - service cancelled"
  5. Confirms

Backend Processing:
  POST /api/recurring-series/{series_id}/exceptions
  {
    "exception_type": "skip",
    "original_date": "2025-12-25T10:00:00",
    "reason": "Christmas Day - service cancelled"
  }

  → Create exception record
  → Delete event occurrence
  → Return success

UI Update:
  - Remove occurrence from calendar preview
  - Show red indicator: "Cancelled"
  - Display reason tooltip on hover
```

### Workflow 2: Modify Occurrence (Reschedule)

```
User Action:
  1. Admin views calendar preview
  2. Clicks occurrence (Jan 1, 10 AM)
  3. Selects "Modify this occurrence"
  4. Changes time to 12:00 PM
  5. Enters reason: "New Year's Day - moved to noon"
  6. Confirms

Backend Processing:
  POST /api/recurring-series/{series_id}/exceptions
  {
    "exception_type": "modify",
    "original_date": "2026-01-01T10:00:00",
    "modified_datetime": "2026-01-01T12:00:00",
    "reason": "New Year's Day - moved to noon"
  }

  → Create exception record
  → Update event datetime to 12:00 PM
  → Set event.is_exception = true
  → Return success

UI Update:
  - Move occurrence on calendar to 12:00 PM
  - Show orange indicator: "Modified"
  - Display reason tooltip on hover
```

### Workflow 3: Restore Occurrence

```
User Action:
  1. Admin views exceptions list
  2. Clicks exception (Dec 25 skip)
  3. Selects "Restore occurrence"
  4. Confirms

Backend Processing:
  DELETE /api/recurring-series/{series_id}/exceptions/{exception_id}

  → Delete exception record
  → Re-create event occurrence with original datetime
  → Return success

UI Update:
  - Restore occurrence on calendar
  - Remove "Cancelled" indicator
  - Show as regular occurrence
```

---

## Security & Authorization

### Authentication

All endpoints require JWT Bearer token with admin role.

### Authorization Rules

| Endpoint | Allowed Roles | Organization Check |
|----------|---------------|-------------------|
| POST /exceptions | Admin | Yes (verify admin belongs to series org) |
| GET /exceptions | Admin, Volunteer | Yes (verify user belongs to series org) |
| GET /exceptions/{id} | Admin, Volunteer | Yes (verify user belongs to series org) |
| DELETE /exceptions/{id} | Admin | Yes (verify admin belongs to series org) |

### Multi-Tenant Isolation

Always verify series belongs to user's organization:

```python
series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()
verify_org_member(current_user, series.org_id)
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /exceptions | 30 requests | 1 minute |
| GET /exceptions | 60 requests | 1 minute |
| DELETE /exceptions/{id} | 30 requests | 1 minute |

---

## Testing Requirements

### Unit Tests
- Test exception validation (skip requires null modified_datetime)
- Test duplicate exception prevention
- Test occurrence restoration logic

### Integration Tests
- Test POST skip deletes event occurrence
- Test POST modify updates event datetime
- Test DELETE restores original occurrence
- Test exception for non-existent occurrence returns 404

### E2E Tests
- Test admin can skip occurrence from calendar
- Test admin can modify occurrence time
- Test admin can restore skipped occurrence
- Test exception indicators appear on calendar

---

## Related Contracts

- [Recurring Series API](./recurring-series-api.md) - CRUD operations for series
- [Bulk Edit API](./bulk-edit-api.md) - Bulk update multiple occurrences
- [Calendar Preview API](./calendar-preview-api.md) - Preview occurrences with exceptions

---

**Document Status**: ✅ Complete
**Next Action**: Generate remaining 2 API contracts (bulk-edit, calendar-preview)
