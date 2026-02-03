# API Contract: Sample Data Management

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

API endpoints for generating, exploring, and clearing sample data for hands-on learning during onboarding.

---

## Base URL

```
/api/onboarding/sample-data
```

**Authentication**: Required (JWT Bearer token)
**Rate Limit**: 10 requests per minute per organization (generation is expensive)
**RBAC**: Admin only (sample data management)

---

## Endpoints

### 1. Generate Sample Data

**Endpoint**: `POST /api/onboarding/sample-data`

**Description**: Generate complete sample dataset (events, teams, volunteers, schedule) for organization.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "dataset_size": "standard",
  "include_schedule": true,
  "expiry_days": 30
}
```

**Request Body Schema**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_size` | string | No | `standard` | Enum: `minimal`, `standard`, `comprehensive` |
| `include_schedule` | boolean | No | `true` | Generate solver schedule |
| `expiry_days` | integer | No | `30` | Days until auto-deletion (1-90) |

**Dataset Sizes**:

| Size | Events | Teams | Volunteers | Assignments |
|------|--------|-------|------------|-------------|
| `minimal` | 2 | 1 | 5 | 10 |
| `standard` | 5 | 3 | 15 | 45 |
| `comprehensive` | 10 | 5 | 30 | 150 |

**Request Example**:

```http
POST /api/onboarding/sample-data?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "dataset_size": "standard",
  "include_schedule": true,
  "expiry_days": 30
}
```

**Success Response** (201 Created):

```json
{
  "sample_data": {
    "organization_id": "org_123",
    "generated": true,
    "generated_at": "2025-10-23T15:00:00Z",
    "expiry_date": "2025-11-22T15:00:00Z",
    "dataset_size": "standard",
    "summary": {
      "events_created": 5,
      "teams_created": 3,
      "volunteers_created": 15,
      "assignments_created": 45,
      "schedule_generated": true
    },
    "generation_time_seconds": 2.3,
    "sample_data_ids": {
      "events": [
        "event_sample_1",
        "event_sample_2",
        "event_sample_3",
        "event_sample_4",
        "event_sample_5"
      ],
      "teams": [
        "team_sample_1",
        "team_sample_2",
        "team_sample_3"
      ],
      "volunteers": [
        "person_sample_1",
        "person_sample_2",
        "person_sample_3",
        // ... 12 more
      ]
    }
  },
  "next_steps": [
    {
      "action": "explore_schedule",
      "url": "/app/schedule",
      "title": "View Generated Schedule"
    },
    {
      "action": "edit_assignment",
      "url": "/app/schedule/edit",
      "title": "Try Manual Editing"
    },
    {
      "action": "run_solver",
      "url": "/app/solver",
      "title": "Re-run Solver with Changes"
    }
  ],
  "message": "Sample data generated successfully. Explore the schedule to see how assignments work!"
}
```

**Sample Data Labeling**:

All sample data clearly labeled in UI:

```python
# Event title format
event.title = f"{base_title} (Sample)"
# Example: "Sunday Morning Service (Sample)"

# Person name format
person.name = f"{first_name} {last_name} (Sample)"
# Example: "John Smith (Sample)"

# Team name format
team.name = f"{base_name} (Sample)"
# Example: "Worship Team (Sample)"

# Database flag
model.is_sample = True  # All sample records marked
```

**Error Responses**:

```json
// 409 Conflict - Sample data already exists
{
  "error": "Conflict",
  "message": "Sample data already exists for organization org_123. Clear existing data first.",
  "details": {
    "existing_data": {
      "events": 5,
      "teams": 3,
      "volunteers": 15
    },
    "generated_at": "2025-10-23T14:00:00Z",
    "expiry_date": "2025-11-22T14:00:00Z"
  }
}

// 400 Bad Request - Invalid dataset size
{
  "error": "Bad Request",
  "message": "Invalid dataset_size. Must be one of: minimal, standard, comprehensive"
}

// 503 Service Unavailable - Solver timeout
{
  "error": "Service Unavailable",
  "message": "Sample schedule generation timed out. Sample data created without schedule.",
  "details": {
    "events_created": 5,
    "teams_created": 3,
    "volunteers_created": 15,
    "schedule_generated": false
  }
}
```

---

### 2. Get Sample Data Status

**Endpoint**: `GET /api/onboarding/sample-data`

**Description**: Check if sample data exists and view summary.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Example**:

```http
GET /api/onboarding/sample-data?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response** (200 OK) - Sample data exists:

```json
{
  "sample_data": {
    "exists": true,
    "organization_id": "org_123",
    "generated_at": "2025-10-23T15:00:00Z",
    "expiry_date": "2025-11-22T15:00:00Z",
    "days_until_expiry": 30,
    "dataset_size": "standard",
    "summary": {
      "events": 5,
      "teams": 3,
      "volunteers": 15,
      "assignments": 45
    },
    "can_clear": true
  }
}
```

**Success Response** (200 OK) - No sample data:

```json
{
  "sample_data": {
    "exists": false,
    "organization_id": "org_123",
    "can_generate": true
  }
}
```

---

### 3. Clear Sample Data

**Endpoint**: `DELETE /api/onboarding/sample-data`

**Description**: Delete all sample data for organization (events, teams, volunteers, assignments).

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body** (Optional):

```json
{
  "confirm": true,
  "keep_types": []
}
```

**Request Body Schema**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `confirm` | boolean | No | `false` | Confirmation flag (safety check) |
| `keep_types` | array | No | `[]` | Entity types to keep (e.g., `["events"]`) |

**Request Example**:

```http
DELETE /api/onboarding/sample-data?org_id=org_123 HTTP/1.1
Host: api.signupflow.io
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "confirm": true
}
```

**Success Response** (200 OK):

```json
{
  "sample_data": {
    "cleared": true,
    "organization_id": "org_123",
    "deleted_counts": {
      "events": 5,
      "teams": 3,
      "volunteers": 15,
      "assignments": 45
    },
    "cleared_at": "2025-10-23T16:00:00Z",
    "deletion_time_seconds": 0.8
  },
  "message": "Sample data cleared successfully. You can now add your real data."
}
```

**Error Responses**:

```json
// 404 Not Found - No sample data to clear
{
  "error": "Not Found",
  "message": "No sample data found for organization org_123"
}

// 400 Bad Request - Missing confirmation
{
  "error": "Bad Request",
  "message": "Confirmation required. Set confirm=true to delete sample data."
}
```

---

### 4. Regenerate Sample Data

**Endpoint**: `PUT /api/onboarding/sample-data/regenerate`

**Description**: Clear existing sample data and generate fresh dataset.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "dataset_size": "comprehensive",
  "include_schedule": true,
  "expiry_days": 30
}
```

**Success Response** (200 OK):

```json
{
  "sample_data": {
    "regenerated": true,
    "organization_id": "org_123",
    "previous_data_deleted": {
      "events": 5,
      "teams": 3,
      "volunteers": 15
    },
    "new_data_generated": {
      "events": 10,
      "teams": 5,
      "volunteers": 30,
      "assignments": 150
    },
    "generated_at": "2025-10-23T16:30:00Z",
    "expiry_date": "2025-11-22T16:30:00Z"
  },
  "message": "Sample data regenerated with comprehensive dataset"
}
```

---

### 5. Extend Sample Data Expiry

**Endpoint**: `PUT /api/onboarding/sample-data/extend`

**Description**: Extend expiry date for existing sample data.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | string | Yes | Organization ID |

**Request Body**:

```json
{
  "additional_days": 30
}
```

**Request Body Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `additional_days` | integer | Yes | Days to add to expiry (1-90) |

**Success Response** (200 OK):

```json
{
  "sample_data": {
    "organization_id": "org_123",
    "previous_expiry": "2025-11-22T15:00:00Z",
    "new_expiry": "2025-12-22T15:00:00Z",
    "days_until_expiry": 60,
    "extended_by_days": 30
  },
  "message": "Sample data expiry extended by 30 days"
}
```

---

## Sample Data Templates

### Events (Standard Dataset)

```python
SAMPLE_EVENTS = [
    {
        'title': 'Sunday Morning Service (Sample)',
        'datetime': next_sunday(10, 0),
        'duration': 120,
        'location': 'Main Sanctuary',
        'description': 'Weekly worship service with music, message, and communion',
        'role_requirements': {
            'Worship Leader': 2,
            'Greeter': 4,
            'Usher': 3,
            'Tech/Sound': 2
        }
    },
    {
        'title': 'Wednesday Night Prayer (Sample)',
        'datetime': next_wednesday(19, 0),
        'duration': 90,
        'location': 'Chapel',
        'description': 'Midweek prayer and Bible study',
        'role_requirements': {
            'Prayer Leader': 1,
            'Greeter': 2
        }
    },
    {
        'title': 'Youth Group Meeting (Sample)',
        'datetime': next_friday(19, 0),
        'duration': 120,
        'location': 'Youth Room',
        'description': 'Weekly youth fellowship and activities',
        'role_requirements': {
            'Youth Leader': 2,
            'Chaperone': 3,
            'Snack Coordinator': 1
        }
    },
    {
        'title': 'Community Outreach (Sample)',
        'datetime': next_saturday(10, 0),
        'duration': 180,
        'location': 'Community Center',
        'description': 'Monthly service project in the community',
        'role_requirements': {
            'Project Coordinator': 1,
            'Helper': 8
        }
    },
    {
        'title': 'Kids Ministry (Sample)',
        'datetime': next_sunday(10, 0),
        'duration': 90,
        'location': 'Kids Wing',
        'description': 'Children\'s Sunday school during main service',
        'role_requirements': {
            'Teacher': 3,
            'Assistant': 2,
            'Check-in': 2
        }
    }
]
```

### Teams (Standard Dataset)

```python
SAMPLE_TEAMS = [
    {
        'name': 'Worship Team (Sample)',
        'role': 'Worship Leader',
        'description': 'Leads Sunday morning worship services with music and vocals',
        'volunteer_count': 5
    },
    {
        'name': 'Hospitality Team (Sample)',
        'role': 'Greeter',
        'description': 'Welcomes guests and helps people feel at home',
        'volunteer_count': 6
    },
    {
        'name': 'Technical Team (Sample)',
        'role': 'Tech/Sound',
        'description': 'Manages audio, video, and live streaming',
        'volunteer_count': 4
    }
]
```

### Volunteers (Standard Dataset)

```python
SAMPLE_VOLUNTEERS = [
    # Worship Team members
    {'name': 'Emily Johnson (Sample)', 'email': 'emily.sample@example.com', 'team': 'Worship Team', 'role': 'Worship Leader'},
    {'name': 'Michael Chen (Sample)', 'email': 'michael.sample@example.com', 'team': 'Worship Team', 'role': 'Worship Leader'},
    {'name': 'Sarah Williams (Sample)', 'email': 'sarah.sample@example.com', 'team': 'Worship Team', 'role': 'Worship Leader'},
    {'name': 'David Martinez (Sample)', 'email': 'david.sample@example.com', 'team': 'Worship Team', 'role': 'Worship Leader'},
    {'name': 'Jessica Lee (Sample)', 'email': 'jessica.sample@example.com', 'team': 'Worship Team', 'role': 'Worship Leader'},

    # Hospitality Team members
    {'name': 'Robert Anderson (Sample)', 'email': 'robert.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},
    {'name': 'Jennifer Taylor (Sample)', 'email': 'jennifer.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},
    {'name': 'Christopher Brown (Sample)', 'email': 'chris.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},
    {'name': 'Amanda Garcia (Sample)', 'email': 'amanda.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},
    {'name': 'Matthew Wilson (Sample)', 'email': 'matthew.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},
    {'name': 'Lisa Rodriguez (Sample)', 'email': 'lisa.sample@example.com', 'team': 'Hospitality Team', 'role': 'Greeter'},

    # Technical Team members
    {'name': 'Daniel Thompson (Sample)', 'email': 'daniel.sample@example.com', 'team': 'Technical Team', 'role': 'Tech/Sound'},
    {'name': 'Ashley Davis (Sample)', 'email': 'ashley.sample@example.com', 'team': 'Technical Team', 'role': 'Tech/Sound'},
    {'name': 'Joshua Miller (Sample)', 'email': 'joshua.sample@example.com', 'team': 'Technical Team', 'role': 'Tech/Sound'},
    {'name': 'Nicole Martinez (Sample)', 'email': 'nicole.sample@example.com', 'team': 'Technical Team', 'role': 'Tech/Sound'}
]
```

### Availabilities (Random Pattern)

```python
# Generate realistic availability patterns
def generate_sample_availability(volunteer_id):
    """Generate 1-3 unavailable dates per volunteer."""
    unavailable_dates = []

    # Some volunteers unavailable for Thanksgiving
    if random.random() > 0.7:
        unavailable_dates.append({
            'start_date': '2025-11-27',
            'end_date': '2025-11-29',
            'reason': 'Thanksgiving vacation'
        })

    # Some volunteers unavailable for Christmas
    if random.random() > 0.6:
        unavailable_dates.append({
            'start_date': '2025-12-24',
            'end_date': '2025-12-26',
            'reason': 'Christmas holiday'
        })

    return unavailable_dates
```

---

## Sample Schedule Generation

### Solver Configuration for Sample Data

```python
def generate_sample_schedule(org_id, events, volunteers):
    """Run solver with sample data to create realistic assignments."""

    # Configure solver with balanced constraints
    solver_config = {
        'org_id': org_id,
        'events': events,
        'volunteers': volunteers,
        'constraints': {
            'respect_availability': True,
            'balance_workload': True,  # Fair distribution
            'avoid_consecutive': True,  # Prevent burnout
            'match_skills': True       # Role preferences
        },
        'timeout_seconds': 30,
        'optimization_level': 'balanced'
    }

    # Run solver
    result = solver_service.solve(solver_config)

    if result['status'] == 'optimal':
        return {
            'assignments_created': len(result['assignments']),
            'schedule_generated': True,
            'fairness_score': result['fairness_score'],
            'coverage_percent': result['coverage_percent']
        }
    else:
        # Partial solution acceptable for sample data
        return {
            'assignments_created': len(result['assignments']),
            'schedule_generated': True,
            'status': 'partial'
        }
```

---

## Business Logic Rules

### Generation Rules

1. **One-Time Generation**: Can only generate once (must clear first to regenerate)
2. **Clear Labeling**: All sample data labeled with "(Sample)" suffix and `is_sample = TRUE`
3. **Realistic Data**: Events use realistic dates (next Sunday, next Wednesday, etc.)
4. **Valid Emails**: Sample emails use `@example.com` domain (won't send real emails)
5. **Auto-Expiry**: Sample data auto-deleted after expiry date (default 30 days)

### Clearing Rules

1. **Confirmation Required**: Must set `confirm = true` to prevent accidental deletion
2. **Cascade Delete**: Deleting events/teams also deletes related assignments
3. **Preserve Real Data**: Only deletes records with `is_sample = TRUE`
4. **Atomic Operation**: All-or-nothing (transaction rollback on error)

### Expiry Rules

1. **Auto-Cleanup Job**: Cron job runs daily to delete expired sample data
2. **Grace Period**: 7-day grace period after expiry before deletion
3. **Email Notification**: Admin notified 3 days before expiry
4. **Extension Allowed**: Can extend expiry up to 90 days total

---

## Cleanup Cron Job

### Daily Cleanup Script

```python
# scripts/cleanup_expired_sample_data.py
from datetime import datetime, timedelta
from api.database import get_db
from api.models import OnboardingState, Event, Team, Person

def cleanup_expired_sample_data():
    """Delete sample data past expiry date + grace period."""
    db = get_db()

    # Find organizations with expired sample data
    grace_period_days = 7
    expiry_cutoff = datetime.utcnow() - timedelta(days=grace_period_days)

    expired_states = db.query(OnboardingState).filter(
        OnboardingState.sample_data_expiry < expiry_cutoff,
        OnboardingState.sample_data_generated == True,
        OnboardingState.sample_data_cleared == False
    ).all()

    for state in expired_states:
        org_id = state.organization_id

        # Delete sample events
        db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_sample == True
        ).delete()

        # Delete sample teams
        db.query(Team).filter(
            Team.org_id == org_id,
            Team.is_sample == True
        ).delete()

        # Delete sample volunteers
        db.query(Person).filter(
            Person.org_id == org_id,
            Person.is_sample == True
        ).delete()

        # Mark as cleared
        state.sample_data_cleared = True
        state.sample_data_expiry = None

        db.commit()

        print(f"Cleaned up expired sample data for org {org_id}")

if __name__ == "__main__":
    cleanup_expired_sample_data()
```

**Cron Schedule**: Daily at 3:00 AM UTC

```cron
0 3 * * * /usr/bin/python /path/to/scripts/cleanup_expired_sample_data.py
```

---

## Analytics Events Triggered

### Automatic Event Tracking

| API Action | Event Type | Event Data |
|------------|------------|------------|
| POST generate | `sample_data_generated` | `{ dataset_size, events_count, generation_time_seconds }` |
| DELETE clear | `sample_data_cleared` | `{ data_age_days, deleted_counts }` |
| PUT regenerate | `sample_data_regenerated` | `{ previous_size, new_size }` |
| PUT extend | `sample_data_extended` | `{ additional_days, new_expiry }` |

---

## Error Handling

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid dataset size or parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User not admin for organization |
| 409 | Conflict | Sample data already exists |
| 503 | Service Unavailable | Solver timeout during generation |
| 500 | Internal Server Error | Database or solver error |

---

## Testing Requirements

### Unit Tests
- [ ] Test event template generation (5 events with valid dates)
- [ ] Test team template generation (3 teams with members)
- [ ] Test volunteer template generation (15 volunteers with emails)
- [ ] Test sample data labeling (all have "(Sample)" suffix)
- [ ] Test `is_sample = TRUE` flag on all records

### Integration Tests
- [ ] Test POST generate creates all entities correctly
- [ ] Test POST generate runs solver successfully
- [ ] Test DELETE clear removes only sample data (not real data)
- [ ] Test PUT regenerate replaces old sample data
- [ ] Test GET status shows correct expiry date
- [ ] Test cleanup job deletes expired data

### E2E Tests
- [ ] Test generate sample data button in wizard
- [ ] Test sample events appear in calendar with "(Sample)" label
- [ ] Test clear sample data button removes data
- [ ] Test regenerate replaces dataset with different size
- [ ] Test expiry warning appears 3 days before expiry

---

## Performance Considerations

### Generation Time Targets

| Dataset Size | Target Time | Operations |
|--------------|-------------|------------|
| `minimal` | <1 second | Create 2 events, 1 team, 5 volunteers |
| `standard` | <3 seconds | Create 5 events, 3 teams, 15 volunteers + solver |
| `comprehensive` | <10 seconds | Create 10 events, 5 teams, 30 volunteers + solver |

### Optimization Strategies

1. **Batch Inserts**: Use SQLAlchemy bulk operations
2. **Solver Timeout**: Limit solver to 30 seconds max
3. **Async Generation**: Consider background job for large datasets
4. **Progress Feedback**: WebSocket updates during generation

---

## Security Considerations

### Data Isolation
- Sample data only visible to organization members
- Sample data cannot be shared across organizations
- Clearing sample data requires admin role

### Email Safety
- Sample volunteer emails use `@example.com` domain
- Email service should NOT send to `@example.com` addresses
- Invitation system skips sample volunteers

---

**API Version**: v1
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
