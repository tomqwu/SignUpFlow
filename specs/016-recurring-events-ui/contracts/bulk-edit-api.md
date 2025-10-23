# API Contract: Bulk Edit Operations

**Feature**: Recurring Events UI | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

Enables administrators to bulk-edit multiple event occurrences atomically. Common use case: Update role requirements for all 52 occurrences in a recurring series without editing individually.

**Base Path**: `/api/events/bulk-edit`
**Authentication**: JWT Bearer token (admin access required)
**Content-Type**: `application/json`

---

## Use Cases

### Update Role Requirements for Entire Series
- **Example**: Change Worship Leader from 1 person to 2 people for all 52 Sundays
- **Benefit**: Single operation vs 52 individual edits (98% time savings)

### Update Duration for Selected Occurrences
- **Example**: Summer services (June-August) are 45 minutes instead of 60 minutes
- **Benefit**: Select specific date range, update duration in bulk

### Update Title for Multiple Occurrences
- **Example**: Rename "Sunday Service" to "Sunday Worship Service" for all future occurrences
- **Benefit**: Consistent naming across all events

---

## Endpoints

### 1. Bulk Edit Selected Occurrences

**POST** `/api/events/bulk-edit`

Updates multiple event occurrences atomically (all succeed or all fail).

#### Request

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "event_ids": [
    "event_abc123",
    "event_def456",
    "event_ghi789"
  ],
  "updates": {
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
}
```

**Field Descriptions**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `event_ids` | array of strings | Yes | 1-104 event IDs | List of event IDs to update |
| `updates` | object | Yes | See below | Field updates to apply to all events |

**Allowed Update Fields**:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `role_requirements` | array | Role requirements JSON | `[{"role": "Host", "count": 2}]` |
| `duration` | integer | Duration in minutes | `45` |
| `title` | string | Event title | `"Summer Service"` |

**NOT Allowed** (creates data inconsistency):
- `datetime`: Use exception API to modify individual occurrences
- `org_id`: Cannot change organization ownership
- `series_id`: Cannot reassign to different series
- `sequence_number`: Automatically managed

#### Response

**Success Response** (200 OK):
```json
{
  "status": "success",
  "updated_count": 52,
  "event_ids": [
    "event_abc123",
    "event_def456",
    "event_ghi789"
  ],
  "updates_applied": {
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

// 400 Bad Request - Too many events
{
  "detail": "Cannot bulk edit more than 104 events at once"
}

// 400 Bad Request - Invalid field
{
  "detail": "Cannot bulk edit field: datetime. Use exception API instead."
}

// 404 Not Found - Event doesn't exist
{
  "detail": "Event event_abc123 not found"
}

// 403 Forbidden - Events belong to different organizations
{
  "detail": "All events must belong to same organization"
}

// 500 Internal Server Error - Update failed
{
  "detail": "Bulk update failed: Database error"
}
```

#### Implementation Notes

1. **Atomic Transaction**:
   - All updates wrapped in database transaction
   - If any update fails, all rollback automatically
   - No partial state (all succeed or all fail)

2. **Validation**:
   - Verify all events exist
   - Verify all events belong to same organization
   - Verify user has admin access to organization
   - Verify update fields are allowed
   - Maximum 104 events per bulk operation

3. **Performance**:
   - Use single UPDATE statement with IN clause (not loop)
   - Complete in <5 seconds for 104 events (target <1s for 52)

**Example Implementation**:

```python
# api/services/bulk_edit_service.py
from sqlalchemy.orm import Session
from sqlalchemy import update
from api.models import Event
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BulkEditService:
    ALLOWED_FIELDS = ["role_requirements", "duration", "title"]
    MAX_EVENTS = 104

    def bulk_update_occurrences(
        self,
        db: Session,
        event_ids: List[str],
        updates: Dict[str, any],
        admin_org_id: str
    ) -> Dict:
        """
        Bulk update multiple event occurrences atomically.

        Args:
            db: Database session
            event_ids: List of event IDs to update
            updates: Dictionary of field updates
            admin_org_id: Admin's organization ID

        Returns:
            Dictionary with status and updated count

        Raises:
            HTTPException: If validation fails or update errors
        """
        # Validation
        if len(event_ids) > self.MAX_EVENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot bulk edit more than {self.MAX_EVENTS} events at once"
            )

        for field in updates.keys():
            if field not in self.ALLOWED_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot bulk edit field: {field}. Allowed: {', '.join(self.ALLOWED_FIELDS)}"
                )

        try:
            # Start transaction (implicit with SQLAlchemy session)

            # Verify all events exist and belong to same org
            events = db.query(Event).filter(Event.id.in_(event_ids)).all()

            if len(events) != len(event_ids):
                found_ids = {event.id for event in events}
                missing_ids = set(event_ids) - found_ids
                raise HTTPException(
                    status_code=404,
                    detail=f"Events not found: {', '.join(missing_ids)}"
                )

            # Verify all events belong to admin's organization
            org_ids = {event.org_id for event in events}
            if len(org_ids) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="All events must belong to same organization"
                )

            if list(org_ids)[0] != admin_org_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: wrong organization"
                )

            # Perform bulk update using single SQL statement
            stmt = update(Event).where(Event.id.in_(event_ids)).values(**updates)
            db.execute(stmt)

            # Commit transaction (all updates succeed)
            db.commit()

            logger.info(f"Bulk updated {len(event_ids)} events for org {admin_org_id}")

            return {
                "status": "success",
                "updated_count": len(event_ids),
                "event_ids": event_ids,
                "updates_applied": updates
            }

        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e

        except Exception as e:
            # Rollback transaction (all updates fail)
            db.rollback()
            logger.error(f"Bulk update failed: {str(e)}")

            raise HTTPException(
                status_code=500,
                detail=f"Bulk update failed: {str(e)}"
            )

# api/routers/events.py
@router.post("/events/bulk-edit")
def bulk_edit_occurrences(
    request: BulkEditRequest,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Bulk edit multiple event occurrences atomically."""
    bulk_edit_service = BulkEditService()

    result = bulk_edit_service.bulk_update_occurrences(
        db=db,
        event_ids=request.event_ids,
        updates=request.updates,
        admin_org_id=admin.org_id
    )

    return result
```

---

### 2. Bulk Edit Entire Series

**POST** `/api/recurring-series/{series_id}/bulk-edit`

Convenience endpoint to update all occurrences in a recurring series.

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
  "updates": {
    "role_requirements": [
      {
        "role": "Worship Leader",
        "count": 2
      }
    ]
  }
}
```

#### Response

**Success Response** (200 OK):
```json
{
  "status": "success",
  "series_id": "series_abc123",
  "updated_count": 52,
  "updates_applied": {
    "role_requirements": [
      {
        "role": "Worship Leader",
        "count": 2
      }
    ]
  }
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

This is a convenience wrapper around the main bulk-edit endpoint:

```python
@router.post("/recurring-series/{series_id}/bulk-edit")
def bulk_edit_series(
    series_id: str,
    request: BulkEditSeriesRequest,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Bulk edit all occurrences in recurring series."""
    # Verify series exists
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    verify_org_member(admin, series.org_id)

    # Get all event IDs for series
    events = db.query(Event).filter(Event.series_id == series_id).all()
    event_ids = [event.id for event in events]

    # Delegate to bulk edit service
    bulk_edit_service = BulkEditService()

    result = bulk_edit_service.bulk_update_occurrences(
        db=db,
        event_ids=event_ids,
        updates=request.updates,
        admin_org_id=admin.org_id
    )

    return {
        "status": "success",
        "series_id": series_id,
        "updated_count": result["updated_count"],
        "updates_applied": result["updates_applied"]
    }
```

---

### 3. Bulk Edit by Date Range

**POST** `/api/events/bulk-edit-range`

Updates all occurrences within a specific date range.

#### Request

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "series_id": "series_abc123",
  "start_date": "2025-06-01",
  "end_date": "2025-08-31",
  "updates": {
    "duration": 45,
    "title": "Summer Service"
  }
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `series_id` | string | No | Optional: Limit to specific series |
| `start_date` | string (ISO 8601) | Yes | Start of date range (inclusive) |
| `end_date` | string (ISO 8601) | Yes | End of date range (inclusive) |
| `updates` | object | Yes | Field updates to apply |

#### Response

**Success Response** (200 OK):
```json
{
  "status": "success",
  "updated_count": 13,
  "date_range": {
    "start_date": "2025-06-01",
    "end_date": "2025-08-31"
  },
  "updates_applied": {
    "duration": 45,
    "title": "Summer Service"
  }
}
```

#### Implementation Notes

```python
@router.post("/events/bulk-edit-range")
def bulk_edit_by_date_range(
    request: BulkEditRangeRequest,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Bulk edit occurrences within date range."""
    # Build query
    query = db.query(Event).filter(
        Event.org_id == admin.org_id,
        Event.datetime >= request.start_date,
        Event.datetime <= request.end_date
    )

    if request.series_id:
        query = query.filter(Event.series_id == request.series_id)

    events = query.all()
    event_ids = [event.id for event in events]

    # Delegate to bulk edit service
    bulk_edit_service = BulkEditService()

    result = bulk_edit_service.bulk_update_occurrences(
        db=db,
        event_ids=event_ids,
        updates=request.updates,
        admin_org_id=admin.org_id
    )

    return {
        "status": "success",
        "updated_count": result["updated_count"],
        "date_range": {
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat()
        },
        "updates_applied": result["updates_applied"]
    }
```

---

## Request Schemas

### BulkEditRequest

```python
# api/schemas/bulk_edit.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any

class BulkEditRequest(BaseModel):
    """Schema for bulk editing selected events."""
    event_ids: List[str] = Field(..., min_items=1, max_items=104)
    updates: Dict[str, Any] = Field(...)

    @validator("updates")
    def validate_updates(cls, v):
        allowed_fields = ["role_requirements", "duration", "title"]
        for field in v.keys():
            if field not in allowed_fields:
                raise ValueError(f"Cannot bulk edit field: {field}")
        return v

    @validator("event_ids")
    def validate_event_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate event IDs not allowed")
        return v
```

### BulkEditSeriesRequest

```python
class BulkEditSeriesRequest(BaseModel):
    """Schema for bulk editing entire series."""
    updates: Dict[str, Any] = Field(...)

    @validator("updates")
    def validate_updates(cls, v):
        allowed_fields = ["role_requirements", "duration", "title"]
        for field in v.keys():
            if field not in allowed_fields:
                raise ValueError(f"Cannot bulk edit field: {field}")
        return v
```

### BulkEditRangeRequest

```python
from datetime import datetime

class BulkEditRangeRequest(BaseModel):
    """Schema for bulk editing by date range."""
    series_id: Optional[str] = None
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    updates: Dict[str, Any] = Field(...)

    @validator("end_date")
    def validate_date_range(cls, v, values):
        start_date = values.get("start_date")
        if start_date and v < start_date:
            raise ValueError("end_date must be after start_date")
        if start_date and (v - start_date).days > 365:
            raise ValueError("Date range cannot exceed 1 year")
        return v

    @validator("updates")
    def validate_updates(cls, v):
        allowed_fields = ["role_requirements", "duration", "title"]
        for field in v.keys():
            if field not in allowed_fields:
                raise ValueError(f"Cannot bulk edit field: {field}")
        return v
```

---

## Bulk Edit Workflows

### Workflow 1: Update Role Requirements for Entire Series

```
User Action:
  1. Admin views recurring series list
  2. Selects series (Sunday Service, 52 occurrences)
  3. Clicks "Edit Series"
  4. Changes Worship Leader from 1 to 2
  5. Confirms bulk edit

Backend Processing:
  POST /api/recurring-series/{series_id}/bulk-edit
  {
    "updates": {
      "role_requirements": [
        {"role": "Worship Leader", "count": 2}
      ]
    }
  }

  → Get all 52 event IDs for series
  → Start database transaction
  → Update all 52 events with new role requirements
  → Commit transaction (atomic)
  → Return success

UI Update:
  - Show success toast: "Updated 52 occurrences"
  - Refresh calendar view
  - Display updated role requirements
```

### Workflow 2: Update Duration for Summer Services

```
User Action:
  1. Admin views calendar
  2. Selects date range (June 1 - Aug 31)
  3. Multi-selects 13 Sunday services
  4. Clicks "Edit Selected"
  5. Changes duration from 60 to 45 minutes
  6. Changes title to "Summer Service"
  7. Confirms

Backend Processing:
  POST /api/events/bulk-edit
  {
    "event_ids": ["event_1", "event_2", ..., "event_13"],
    "updates": {
      "duration": 45,
      "title": "Summer Service"
    }
  }

  → Verify all 13 events exist
  → Verify all belong to admin's org
  → Start database transaction
  → Update all 13 events
  → Commit transaction
  → Return success

UI Update:
  - Show success toast: "Updated 13 occurrences"
  - Refresh calendar
  - Display "Summer Service" title and 45-minute duration
```

---

## Performance Optimization

### Single SQL Statement

Use `UPDATE ... WHERE id IN (...)` instead of loop:

```python
# ✅ FAST - Single SQL statement
stmt = update(Event).where(Event.id.in_(event_ids)).values(**updates)
db.execute(stmt)

# ❌ SLOW - N queries for N events
for event_id in event_ids:
    event = db.query(Event).filter(Event.id == event_id).first()
    for field, value in updates.items():
        setattr(event, field, value)
```

**Performance Benchmark**:
- Loop approach: 50ms per event × 52 events = 2,600ms (2.6 seconds)
- Single statement: 50ms total (52x faster)

### Transaction Timeout

Set reasonable timeout to prevent long-running transactions:

```python
# Set transaction timeout
db.execute("SET LOCAL statement_timeout = '5s'")

# Perform bulk update
stmt = update(Event).where(Event.id.in_(event_ids)).values(**updates)
db.execute(stmt)
```

---

## Security & Authorization

### Authentication

All endpoints require JWT Bearer token with admin role.

### Authorization Rules

| Endpoint | Allowed Roles | Organization Check |
|----------|---------------|-------------------|
| POST /events/bulk-edit | Admin | Yes (verify all events belong to admin's org) |
| POST /recurring-series/{id}/bulk-edit | Admin | Yes (verify series belongs to admin's org) |
| POST /events/bulk-edit-range | Admin | Yes (implicit - filter by org_id) |

### Multi-Tenant Isolation

**Critical**: Verify ALL events belong to same organization:

```python
# Verify all events belong to admin's organization
org_ids = {event.org_id for event in events}
if len(org_ids) > 1:
    raise HTTPException(status_code=400, detail="All events must belong to same organization")

if list(org_ids)[0] != admin.org_id:
    raise HTTPException(status_code=403, detail="Access denied: wrong organization")
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /events/bulk-edit | 10 requests | 1 minute |
| POST /recurring-series/{id}/bulk-edit | 10 requests | 1 minute |
| POST /events/bulk-edit-range | 10 requests | 1 minute |

**Rationale**: Bulk operations are expensive, limit to prevent abuse.

---

## Testing Requirements

### Unit Tests
- Test validation (allowed fields, max events)
- Test atomic rollback on error
- Test duplicate event ID detection

### Integration Tests
- Test POST updates all selected events
- Test transaction rollback if any event fails
- Test multi-tenant isolation (can't edit other org's events)
- Test performance (<5s for 104 events)

### E2E Tests
- Test admin can bulk edit from calendar UI
- Test multi-select and bulk update workflow
- Test rollback if error occurs mid-update
- Test success toast and UI refresh

---

## Related Contracts

- [Recurring Series API](./recurring-series-api.md) - CRUD operations for series
- [Recurrence Exceptions API](./recurrence-exceptions-api.md) - Skip or modify individual occurrences
- [Calendar Preview API](./calendar-preview-api.md) - Preview occurrences before creation

---

**Document Status**: ✅ Complete
**Next Action**: Generate final API contract (calendar-preview-api.md)
