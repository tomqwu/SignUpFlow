# Event-Specific Roles Feature

**Implemented:** 2025-10-06
**Status:** ✅ Complete - All tests passing (179/179)

---

## Overview

People can now join events with **specific roles** (e.g., "usher", "greeter", "sound_tech") rather than just generic assignment. This allows:

- **Better scheduling**: "Need 2 ushers + 1 greeter" vs "Need 3 people"
- **Clear accountability**: Everyone knows their specific responsibility
- **Flexibility**: Same person can be "usher" on Sunday, "greeter" on Wednesday
- **Custom roles**: Support for organization-specific roles

---

## Architecture

### Before (Generic Assignment)
```
Person → Event Assignment
  └─ No role information
  └─ Just assigned/not assigned
```

### After (Role-Based Assignment)
```
Person → Event Assignment
  ├─ Role: "usher"
  ├─ Role: "greeter"
  └─ Role: null (backward compatible)
```

### Key Design Decisions

1. **Event-level roles**, not person-level
   - Person has org-level roles: `["volunteer", "admin"]`
   - Assignment has event-specific role: `"usher"`

2. **Role is optional** (nullable field)
   - Backward compatible with existing assignments
   - Can assign without specifying role

3. **No role validation**
   - Roles are free-form strings
   - No predefined list enforced at API level
   - Frontend provides suggestions, but any role works

---

## Database Schema

### Assignment Table (Updated)

```sql
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solution_id INTEGER,
    event_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role TEXT,                 -- NEW: Event-specific role
    assigned_at DATETIME,
    FOREIGN KEY (solution_id) REFERENCES solutions(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (person_id) REFERENCES people(id)
);
```

### Migration

```bash
# Run migration
poetry run python scripts/migrate_add_role_to_assignments.py

# What it does:
1. Adds 'role' column to assignments table (TEXT, nullable)
2. Existing assignments get NULL role (backward compatible)
3. Verifies migration succeeded
```

---

## API Changes

### 1. Assign Person to Event

**Endpoint:** `POST /api/events/{event_id}/assignments`

**Request Body:**
```json
{
    "person_id": "john123",
    "action": "assign",
    "role": "usher"          // NEW: Optional role field
}
```

**Response:**
```json
{
    "message": "Assigned John Smith to event as usher",
    "assignment_id": 42,
    "role": "usher"          // NEW: Echoes role back
}
```

### 2. Get All Assignments

**Endpoint:** `GET /api/events/assignments/all?org_id={org_id}`

**Response:**
```json
{
    "assignments": [
        {
            "assignment_id": 1,
            "event_id": "sunday_service_001",
            "person_id": "john123",
            "person_name": "John Smith",
            "role": "usher",       // NEW: Role information
            "is_manual": true
        },
        {
            "assignment_id": 2,
            "event_id": "sunday_service_001",
            "person_id": "jane456",
            "person_name": "Jane Doe",
            "role": "greeter",     // NEW: Different role
            "is_manual": true
        }
    ],
    "total": 2
}
```

### 3. Backward Compatibility

Assigning without role still works:
```json
{
    "person_id": "bob789",
    "action": "assign"
    // No role specified - assignment.role will be NULL
}
```

---

## Frontend Changes

### 1. Role Selection Modal

When user clicks "Join Event", a modal appears:

```
┌─────────────────────────────────────┐
│ Select Your Role                  × │
├─────────────────────────────────────┤
│ What role will you fulfill?        │
│                                     │
│ Role: [▼ -- Select a role --    ]  │
│       │ Usher                    │  │
│       │ Greeter                  │  │
│       │ Sound Tech               │  │
│       │ Video Tech               │  │
│       │ Worship Leader           │  │
│       │ Speaker                  │  │
│       │ Nursery                  │  │
│       │ Parking                  │  │
│       │ Security                 │  │
│       │ Other                    │  │
│       └──────────────────────────┘  │
│                                     │
│       [Cancel]  [Join Event]        │
└─────────────────────────────────────┘
```

### 2. Custom Roles

When "Other" is selected:

```
┌─────────────────────────────────────┐
│ Select Your Role                  × │
├─────────────────────────────────────┤
│ Role: [Other ▼]                     │
│                                     │
│ Custom Role Name:                   │
│ [Coffee Barista________________]    │
│                                     │
│       [Cancel]  [Join Event]        │
└─────────────────────────────────────┘
```

### 3. Implementation

**HTML** (`frontend/index.html`):
- Added `#select-role-modal` with predefined role options
- Custom role input field (hidden by default)
- Form validation

**JavaScript** (`frontend/js/app-user.js`):
- `joinEvent(eventId)` - Shows role selection modal
- `closeSelectRoleModal()` - Hides modal
- `submitEventRole(event)` - Submits assignment with role
- Dynamic show/hide for custom role input

**CSS** (existing styles):
- Uses existing modal styles
- Consistent with other modals in the app

---

## Predefined Roles

The frontend suggests these common roles:

| Role | Description | Typical Use |
|------|-------------|-------------|
| **Usher** | Seating, offering | Sunday services |
| **Greeter** | Welcome at door | All services |
| **Sound Tech** | Audio equipment | Services with music |
| **Video Tech** | Video/streaming | Services with recording |
| **Worship Leader** | Lead singing | Worship services |
| **Speaker** | Give sermon/talk | Teaching events |
| **Nursery** | Childcare | Services with kids |
| **Parking** | Direct traffic | Large events |
| **Security** | Safety monitoring | Large gatherings |
| **Other** | Custom role | Organization-specific |

**Note:** These are suggestions only - any string can be a role.

---

## Use Cases

### Use Case 1: Multi-Role Person

**Scenario:** Sarah serves different roles on different days

```javascript
// Sunday morning - Usher
POST /events/sunday_service_001/assignments
{
    "person_id": "sarah123",
    "role": "usher"
}

// Wednesday night - Greeter
POST /events/wednesday_service_001/assignments
{
    "person_id": "sarah123",
    "role": "greeter"
}

// Same person, different roles!
```

### Use Case 2: Team Scheduling

**Scenario:** Organize complete team for an event

```
Event: Sunday Service (Dec 25)
Roles Needed:
  - 2 Ushers
  - 1 Greeter
  - 1 Sound Tech
  - 1 Video Tech

Assignments:
  ✓ John - usher
  ✓ Mike - usher
  ✓ Sarah - greeter
  ✓ Tom - sound_tech
  ✓ Lisa - video_tech
```

### Use Case 3: Custom Roles

**Scenario:** Church needs coffee servers

```javascript
POST /events/sunday_service_001/assignments
{
    "person_id": "bob456",
    "role": "Coffee Barista"  // Custom role
}
```

### Use Case 4: Backward Compatibility

**Scenario:** Quick assignment without role

```javascript
POST /events/meeting_001/assignments
{
    "person_id": "alice789",
    "action": "assign"
    // No role - works fine, role = NULL
}
```

---

## Testing

### Unit Tests (`tests/unit/test_event_roles.py`)

**7 comprehensive tests** covering:

1. ✅ **test_assign_person_with_role**
   Verify role is stored and returned correctly

2. ✅ **test_assign_person_with_different_roles**
   Same person can have different roles in different events

3. ✅ **test_assign_without_role**
   Backward compatibility - assigning without role works

4. ✅ **test_get_assignments_includes_roles**
   Role information returned when fetching assignments

5. ✅ **test_custom_role_name**
   Custom role names (e.g., "Coffee Barista") work

6. ✅ **test_role_persists_after_assignment**
   Role information persists in database correctly

7. ✅ **test_empty_string_role**
   Empty string role handled gracefully

### Test Results

```
Unit Tests:     154/154 passing (100%)
Integration:    25 passing, 2 skipped
Total:          179 passed, 2 skipped
New Tests:      +7 for event roles
```

### Running Tests

```bash
# Run only event role tests
make test-unit
pytest tests/unit/test_event_roles.py -v

# Run all tests
make test
```

---

## Future Enhancements

### Potential Improvements

1. **Role Requirements**
   Event specifies: "Need 2 ushers, 1 greeter"
   UI shows: "1/2 ushers filled"

2. **Role Permissions**
   Certain roles require certain person-level roles
   e.g., "speaker" role requires person has "admin" role

3. **Role History**
   Track: "John has served as usher 15 times"

4. **Role Preferences**
   Person profile: "Preferred roles: [usher, greeter]"

5. **Auto-Assignment by Role**
   Solver considers role preferences when assigning

6. **Role Badges/Icons**
   Visual indicators in UI: 👤 usher, 👋 greeter, 🔊 sound

---

## Migration Guide

### For Existing Deployments

```bash
# 1. Pull latest code
git pull origin main

# 2. Run database migration
poetry run python scripts/migrate_add_role_to_assignments.py

# 3. Restart server
make kill-servers
make server

# 4. Verify tests pass
make test
```

### For New Deployments

No action needed - role field included in schema from start.

---

## Code References

### Database Model
- [roster_cli/db/models.py:386](../roster_cli/db/models.py#L386) - Assignment model with role field

### API Endpoints
- [api/routers/events.py:26](../api/routers/events.py#L26) - AssignmentRequest schema
- [api/routers/events.py:335](../api/routers/events.py#L335) - Assign with role
- [api/routers/events.py:390](../api/routers/events.py#L390) - Return role in assignments

### Frontend
- [frontend/index.html:892](../frontend/index.html#L892) - Role selection modal
- [frontend/js/app-user.js:2202](../frontend/js/app-user.js#L2202) - joinEvent() function
- [frontend/js/app-user.js:2242](../frontend/js/app-user.js#L2242) - submitEventRole() function

### Tests
- [tests/unit/test_event_roles.py](../tests/unit/test_event_roles.py) - Comprehensive role tests

### Migration
- [scripts/migrate_add_role_to_assignments.py](../scripts/migrate_add_role_to_assignments.py) - Database migration

---

## Summary

Event-specific roles is a **major feature enhancement** that transforms generic event assignment into role-based scheduling. It provides:

✅ **Better UX** - Clear role selection during join
✅ **Better Scheduling** - Know exactly who's doing what
✅ **Flexibility** - Same person, different roles
✅ **Backward Compatible** - Existing code works unchanged
✅ **Well Tested** - 7 new tests, all passing
✅ **Production Ready** - Deployed and verified

**Status:** ✅ Complete and tested (179/179 tests passing)
