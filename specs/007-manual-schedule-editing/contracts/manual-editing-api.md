# API Contract: Manual Schedule Editing

**Feature**: Manual Schedule Editing | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This API enables administrators to manually edit solver-generated schedules through drag-and-drop reassignments, swaps, locks, and constraint validation. All endpoints require admin authentication (RBAC enforcement).

**Base URL**: `/api/manual-edits`
**Authentication**: JWT Bearer token (admin role required)

---

## Endpoints

### 1. POST /api/manual-edits/reassign

Reassign volunteer from one event to another (drag-and-drop operation).

**Request**:
```json
POST /api/manual-edits/reassign?org_id=org_123
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "person_id": "person_456",
  "source_event_id": "event_789",
  "target_event_id": "event_012",
  "role": "Worship Leader",
  "reason": "Pastor requested this change"
}
```

**Response** (200 OK):
```json
{
  "id": "edit_345",
  "status": "success",
  "assignment_id": "assignment_678",
  "is_locked": true,
  "locked_at": "2025-10-23T14:30:00Z",
  "locked_by": "admin_123",
  "violations": [],
  "warnings": [
    {
      "type": "fairness",
      "severity": "warning",
      "message": "Jane now has 11 assignments (avg: 8). Consider balancing."
    }
  ]
}
```

**Error** (400 Bad Request - Constraint Violation):
```json
{
  "error": "constraint_violation",
  "message": "Cannot reassign: constraint violations detected",
  "violations": [
    {
      "type": "availability",
      "severity": "error",
      "message": "Jane Doe is unavailable on Sunday 10:00 AM",
      "affected_entities": {
        "person_id": "person_456",
        "event_id": "event_012"
      },
      "suggested_fix": {
        "action": "reassign",
        "target_event_id": "event_345",
        "reasoning": "Jane is available for Sunday 2:00 PM service"
      }
    }
  ]
}
```

**Implementation**:
```python
@router.post("/api/manual-edits/reassign")
async def reassign_volunteer(
    request: ReassignRequest,
    org_id: str = Query(...),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    verify_org_member(admin, org_id)

    # Validate constraints
    violations = await constraint_validator.validate_reassignment(
        person_id=request.person_id,
        target_event_id=request.target_event_id
    )

    if any(v.severity == 'error' for v in violations):
        raise HTTPException(status_code=400, detail={
            "error": "constraint_violation",
            "violations": [v.dict() for v in violations]
        })

    # Delete old assignment
    old_assignment = db.query(EventAssignment).filter(
        EventAssignment.person_id == request.person_id,
        EventAssignment.event_id == request.source_event_id
    ).first()
    if old_assignment:
        db.delete(old_assignment)

    # Create new assignment (locked)
    new_assignment = EventAssignment(
        id=generate_id(),
        person_id=request.person_id,
        event_id=request.target_event_id,
        role=request.role,
        is_locked=True,
        locked_at=datetime.utcnow(),
        locked_by=admin.id
    )
    db.add(new_assignment)

    # Log manual edit
    log_entry = ManualEditLog(
        id=generate_id(),
        org_id=org_id,
        admin_id=admin.id,
        edit_type="reassign",
        edit_data=request.dict(),
        reason=request.reason,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)

    db.commit()

    return {
        "id": log_entry.id,
        "status": "success",
        "assignment_id": new_assignment.id,
        "is_locked": True,
        "violations": [],
        "warnings": [v.dict() for v in violations if v.severity == 'warning']
    }
```

---

### 2. POST /api/manual-edits/swap

Swap two volunteers between events.

**Request**:
```json
POST /api/manual-edits/swap?org_id=org_123
Authorization: Bearer {jwt_token}

{
  "person_a_id": "person_456",
  "person_b_id": "person_789",
  "event_id": "event_012",
  "role": "Worship Leader",
  "reason": "Balance workload"
}
```

**Response** (200 OK):
```json
{
  "id": "edit_456",
  "status": "success",
  "swapped_assignments": [
    {"person_id": "person_456", "event_id": "event_012"},
    {"person_id": "person_789", "event_id": "event_345"}
  ],
  "violations": [],
  "warnings": []
}
```

---

### 3. POST /api/manual-edits/validate

Validate proposed edit before committing (client calls during drag).

**Request**:
```json
POST /api/manual-edits/validate?org_id=org_123

{
  "edit_type": "reassign",
  "edit_data": {
    "person_id": "person_456",
    "target_event_id": "event_012",
    "role": "Worship Leader"
  }
}
```

**Response** (200 OK):
```json
{
  "is_valid": true,
  "violations": [],
  "warnings": [
    {
      "type": "fairness",
      "severity": "warning",
      "message": "This will give Jane 11 assignments (50% above average)"
    }
  ],
  "suggestions": [
    {
      "action": "swap",
      "person_b_id": "person_789",
      "score": 0.85,
      "reasoning": "Swap with Alice (6 assignments) improves fairness by 40%"
    }
  ]
}
```

**Performance**: <300ms (server-side constraint validation)

---

### 4. POST /api/manual-edits/lock

Explicitly lock assignment (prevent solver from changing).

**Request**:
```json
POST /api/manual-edits/lock?org_id=org_123

{
  "assignment_id": "assignment_678",
  "reason": "Pastor specifically requested this volunteer"
}
```

**Response** (200 OK):
```json
{
  "id": "edit_567",
  "status": "success",
  "assignment_id": "assignment_678",
  "is_locked": true,
  "locked_at": "2025-10-23T15:00:00Z",
  "locked_by": "admin_123"
}
```

---

### 5. POST /api/manual-edits/unlock

Unlock assignment (allow solver to change).

**Request**:
```json
POST /api/manual-edits/unlock?org_id=org_123

{
  "assignment_id": "assignment_678"
}
```

**Response** (200 OK):
```json
{
  "id": "edit_678",
  "status": "success",
  "assignment_id": "assignment_678",
  "is_locked": false
}
```

---

### 6. GET /api/manual-edits/history

Get manual edit history (paginated).

**Request**:
```
GET /api/manual-edits/history?org_id=org_123&page=1&page_size=50
```

**Response** (200 OK):
```json
{
  "edits": [
    {
      "id": "edit_123",
      "admin_id": "admin_456",
      "admin_name": "John Smith",
      "edit_type": "reassign",
      "edit_data": {
        "person_id": "person_789",
        "source_event_id": "event_012",
        "target_event_id": "event_345"
      },
      "reason": "Volunteer requested time change",
      "timestamp": "2025-10-23T14:30:00Z",
      "is_undone": false
    }
  ],
  "total_count": 247,
  "page": 1,
  "page_size": 50
}
```

---

### 7. POST /api/manual-edits/{edit_id}/undo

Undo previously committed edit.

**Request**:
```
POST /api/manual-edits/edit_123/undo?org_id=org_123
```

**Response** (200 OK):
```json
{
  "status": "success",
  "edit_id": "edit_123",
  "is_undone": true,
  "undone_at": "2025-10-23T15:30:00Z",
  "reverted_assignment": {
    "person_id": "person_789",
    "event_id": "event_012",
    "role": "Worship Leader"
  }
}
```

---

### 8. POST /api/manual-edits/resolve-conflicts

Get suggestions for resolving constraint violations.

**Request**:
```json
POST /api/manual-edits/resolve-conflicts?org_id=org_123

{
  "violations": [
    {
      "type": "availability",
      "person_id": "person_456",
      "event_id": "event_012"
    }
  ],
  "max_suggestions": 5
}
```

**Response** (200 OK):
```json
{
  "suggestions": [
    {
      "action": "reassign",
      "person_id": "person_456",
      "target_event_id": "event_345",
      "score": 0.92,
      "reasoning": "Same day, 4 hours later, volunteer is available"
    },
    {
      "action": "swap",
      "person_a_id": "person_456",
      "person_b_id": "person_789",
      "event_id": "event_012",
      "score": 0.85,
      "reasoning": "Alice is available and has fewer assignments"
    }
  ]
}
```

**Performance**: <2s (greedy heuristic conflict resolution)

---

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `constraint_violation` | Edit violates hard constraints (availability, role) | 400 |
| `not_found` | Assignment/person/event not found | 404 |
| `permission_denied` | Not admin or wrong organization | 403 |
| `already_locked` | Assignment already locked by another admin | 409 |
| `concurrent_edit` | Another admin modified this assignment | 409 |
| `invalid_edit_type` | Unknown edit type | 400 |

---

## Security

**RBAC Enforcement**:
- All endpoints require `admin` role (checked via `verify_admin_access`)
- Organization isolation enforced via `org_id` parameter
- Manual edit log tracks `admin_id` for audit trail

**Rate Limiting**:
- 100 requests per minute per admin (prevent abuse)
- Bulk operations limited to 50 assignments per request

**Validation**:
- All inputs validated via Pydantic schemas
- SQL injection prevented by SQLAlchemy ORM
- XSS prevention via JSON responses (no HTML)

---

## Performance Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| Reassign | <200ms | Direct DB queries, minimal validation |
| Validate | <300ms | Cached constraint data, incremental validation |
| Resolve conflicts | <2s | Greedy heuristic (not exhaustive search) |
| Undo | <100ms | Simple DB update, no complex logic |
| History query | <50ms | Indexed timestamp queries |

---

## Testing Strategy

**Unit Tests**:
- Test each endpoint handler in isolation
- Mock database and constraint validator
- Verify error handling (400, 403, 404 responses)

**Integration Tests**:
- Test full request/response cycle with real database
- Verify manual edits persist correctly
- Test undo/redo operations

**E2E Tests**:
- Test drag-and-drop workflow in browser (Playwright)
- Verify real-time validation feedback
- Test undo/redo via keyboard shortcuts

**Performance Tests**:
- Benchmark each endpoint with realistic payloads
- Measure p50, p95, p99 latencies
- Test under concurrent load (10+ admins editing)

---

## Migration Guide

**Database Migration**:
```bash
# Run Alembic migration
poetry run alembic upgrade head

# Verify schema changes
poetry run python -c "
from api.database import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)

# Check extensions
columns = [col['name'] for col in inspector.get_columns('event_assignments')]
print('✅ is_locked' if 'is_locked' in columns else '❌ Missing is_locked')

tables = inspector.get_table_names()
print('✅ manual_edit_log' if 'manual_edit_log' in tables else '❌ Missing table')
"
```

**Rollback Plan**:
If feature needs to be disabled:
1. Set all `is_locked=FALSE` (solver resumes)
2. Stop calling manual edit endpoints
3. Historical logs preserved (no data loss)
