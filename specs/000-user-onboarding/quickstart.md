# Quick Start: User Onboarding System (5 Minutes)

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

Get the onboarding wizard, sample data generator, and interactive tutorials working in 5 minutes.

---

## Prerequisites

- SignUpFlow backend running (`make run`)
- Admin account in SignUpFlow
- Browser with JavaScript enabled
- npm installed (for Shepherd.js library)

**Time Estimate**: 5 minutes

---

## Step 1: Install Shepherd.js for Tutorial Overlays (1 minute)

### Install via npm

```bash
cd /home/ubuntu/SignUpFlow

# Install Shepherd.js for interactive tutorials
npm install shepherd.js --save

# Or use CDN (alternative for quick testing)
# Add to frontend/index.html:
# <script src="https://cdn.jsdelivr.net/npm/shepherd.js@11.0.1/dist/js/shepherd.min.js"></script>
# <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/shepherd.js@11.0.1/dist/css/shepherd.css"/>
```

---

## Step 2: Create Onboarding Database Tables (1 minute)

### Run Database Migration

```bash
# Create onboarding tables using Alembic
poetry run alembic revision --autogenerate -m "Add onboarding tables"

# Apply migration
poetry run alembic upgrade head

# Seed checklist tasks
poetry run python -c "
from api.database import get_db
from api.models import OnboardingChecklistTask

db = get_db()

# Create 6 checklist tasks
tasks = [
    OnboardingChecklistTask(
        id='complete_profile',
        title_key='onboarding.checklist.complete_profile',
        description_key='onboarding.checklist.complete_profile_desc',
        completion_criteria={'type': 'state_check', 'field': 'wizard_completed', 'value': True},
        priority_order=1,
        icon='user-circle',
        quick_action_url='/app/settings/organization'
    ),
    OnboardingChecklistTask(
        id='create_first_event',
        title_key='onboarding.checklist.create_first_event',
        description_key='onboarding.checklist.create_first_event_desc',
        completion_criteria={'type': 'database_query', 'query': 'SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE', 'threshold': 1, 'operator': '>='},
        priority_order=2,
        icon='calendar',
        quick_action_url='/app/events/create'
    ),
    # Add remaining 4 tasks...
]

for task in tasks:
    db.add(task)

db.commit()
print('✅ Checklist tasks seeded successfully!')
"
```

**Or use SQL directly**:

```sql
-- Insert checklist tasks
INSERT INTO onboarding_checklist_task (id, title_key, description_key, completion_criteria, priority_order, icon, quick_action_url, is_active) VALUES
('complete_profile', 'onboarding.checklist.complete_profile', 'onboarding.checklist.complete_profile_desc',
 '{"type": "state_check", "field": "wizard_completed", "value": true}',
 1, 'user-circle', '/app/settings/organization', true),
('create_first_event', 'onboarding.checklist.create_first_event', 'onboarding.checklist.create_first_event_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE", "threshold": 1, "operator": ">="}',
 2, 'calendar', '/app/events/create', true),
('add_team', 'onboarding.checklist.add_team', 'onboarding.checklist.add_team_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM teams WHERE org_id = :org_id AND is_sample = FALSE", "threshold": 1, "operator": ">="}',
 3, 'users', '/app/teams/create', true),
('invite_volunteers', 'onboarding.checklist.invite_volunteers', 'onboarding.checklist.invite_volunteers_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM people WHERE org_id = :org_id AND is_sample = FALSE AND roles LIKE ''%volunteer%''", "threshold": 3, "operator": ">="}',
 4, 'user-plus', '/app/people/invite', true),
('run_first_schedule', 'onboarding.checklist.run_first_schedule', 'onboarding.checklist.run_first_schedule_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM event_assignments WHERE event_id IN (SELECT id FROM events WHERE org_id = :org_id AND is_sample = FALSE)", "threshold": 1, "operator": ">="}',
 5, 'check-circle', '/app/solver', true),
('view_reports', 'onboarding.checklist.view_reports', 'onboarding.checklist.view_reports_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM onboarding_metric WHERE organization_id = :org_id AND event_type = ''view_reports''", "threshold": 1, "operator": ">="}',
 6, 'bar-chart', '/app/reports', true);
```

---

## Step 3: Test Wizard State API (1 minute)

### Create Onboarding State for Test Organization

```bash
poetry run python

>>> from api.database import get_db
>>> from api.models import OnboardingState
>>>
>>> db = get_db()
>>>
>>> # Create onboarding state for test organization
>>> state = OnboardingState(organization_id='org_test_123')
>>> db.add(state)
>>> db.commit()
>>>
>>> print(f"✅ Onboarding state created with ID: {state.id}")
>>> print(f"   Current wizard step: {state.wizard_current_step}")
>>> print(f"   Wizard completed: {state.wizard_completed}")
```

### Test Wizard API Endpoint

```bash
# Get wizard state
curl -X GET "http://localhost:8000/api/onboarding/wizard?org_id=org_test_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected response:
# {
#   "wizard_state": {
#     "organization_id": "org_test_123",
#     "wizard_completed": false,
#     "wizard_current_step": 1,
#     "wizard_step_data": {},
#     ...
#   },
#   "available_steps": [...],
#   "can_advance": true,
#   "progress_percent": 0
# }
```

---

## Step 4: Test Sample Data Generation (1 minute)

### Generate Sample Data via API

```bash
# Generate sample data
curl -X POST "http://localhost:8000/api/onboarding/sample-data?org_id=org_test_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_size": "minimal",
    "include_schedule": false,
    "expiry_days": 30
  }'

# Expected response:
# {
#   "sample_data": {
#     "organization_id": "org_test_123",
#     "generated": true,
#     "summary": {
#       "events_created": 2,
#       "teams_created": 1,
#       "volunteers_created": 5
#     },
#     "generation_time_seconds": 0.8
#   }
# }
```

### Verify Sample Data Created

```bash
poetry run python -c "
from api.database import get_db
from api.models import Event, Team, Person

db = get_db()

# Count sample events
events = db.query(Event).filter(Event.org_id == 'org_test_123', Event.is_sample == True).count()
print(f'Sample Events: {events}')

# Count sample teams
teams = db.query(Team).filter(Team.org_id == 'org_test_123', Team.is_sample == True).count()
print(f'Sample Teams: {teams}')

# Count sample volunteers
volunteers = db.query(Person).filter(Person.org_id == 'org_test_123', Person.is_sample == True).count()
print(f'Sample Volunteers: {volunteers}')

# Expected output:
# Sample Events: 2
# Sample Teams: 1
# Sample Volunteers: 5
"
```

---

## Step 5: Test Shepherd.js Tutorial Integration (1 minute)

### Create Simple Tutorial Test Page

```html
<!-- frontend/test-tutorial.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tutorial Test</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/shepherd.js@11.0.1/dist/css/shepherd.css"/>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        #create-event-button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Test Tutorial System</h1>
    <button id="create-event-button">Create Event</button>

    <script src="https://cdn.jsdelivr.net/npm/shepherd.js@11.0.1/dist/js/shepherd.min.js"></script>
    <script>
        // Initialize Shepherd tour
        const tour = new Shepherd.Tour({
            useModalOverlay: true,
            defaultStepOptions: {
                classes: 'signupflow-tutorial',
                scrollTo: { behavior: 'smooth', block: 'center' },
                cancelIcon: {
                    enabled: true
                }
            }
        });

        // Add tutorial steps
        tour.addStep({
            id: 'welcome',
            text: '<h3>Welcome to SignUpFlow!</h3><p>Let\'s create your first event in just a few steps.</p>',
            buttons: [
                {
                    text: 'Skip Tutorial',
                    action: tour.cancel
                },
                {
                    text: 'Next',
                    action: tour.next
                }
            ]
        });

        tour.addStep({
            id: 'create-event',
            text: '<p>Click this button to create a new event. Events are activities that need volunteer assignments.</p>',
            attachTo: {
                element: '#create-event-button',
                on: 'bottom'
            },
            buttons: [
                {
                    text: 'Back',
                    action: tour.back
                },
                {
                    text: 'Got It!',
                    action: tour.next
                }
            ],
            advanceOn: {
                selector: '#create-event-button',
                event: 'click'
            }
        });

        tour.addStep({
            id: 'complete',
            text: '<h3>Tutorial Complete!</h3><p>You\'re ready to start creating events and managing volunteers.</p>',
            buttons: [
                {
                    text: 'Finish',
                    action: tour.complete
                }
            ]
        });

        // Start tour automatically
        tour.start();

        // Button handler
        document.getElementById('create-event-button').addEventListener('click', () => {
            alert('Create Event clicked!');
        });
    </script>
</body>
</html>
```

### Test Tutorial

```bash
# Open test page in browser
open frontend/test-tutorial.html
# Or on Linux:
xdg-open frontend/test-tutorial.html

# Expected behavior:
# 1. Page loads with tutorial overlay
# 2. Welcome step appears with "Skip" and "Next" buttons
# 3. Click "Next" → highlights "Create Event" button
# 4. Click "Create Event" → advances to completion step
# 5. Click "Finish" → tutorial closes
```

---

## Step 6: Test Checklist API (30 seconds)

### Get Checklist Progress

```bash
# Get checklist with completion status
curl -X GET "http://localhost:8000/api/onboarding/checklist?org_id=org_test_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected response:
# {
#   "checklist": {
#     "organization_id": "org_test_123",
#     "tasks": [
#       {
#         "id": "complete_profile",
#         "title": "Complete Organization Profile",
#         "completed": false,
#         "priority_order": 1,
#         "quick_action_url": "/app/settings/organization"
#       },
#       {
#         "id": "create_first_event",
#         "title": "Create Your First Event",
#         "completed": false,
#         "priority_order": 2,
#         "quick_action_url": "/app/events/create"
#       },
#       ...
#     ],
#     "progress": {
#       "completed_count": 0,
#       "total_count": 6,
#       "completion_percent": 0
#     }
#   }
# }
```

---

## Step 7: Test Analytics Tracking (30 seconds)

### Track Onboarding Event

```bash
# Track wizard step completion
curl -X POST "http://localhost:8000/api/analytics/onboarding-events" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "org_test_123",
    "event_type": "wizard_step_completed",
    "event_data": {
      "step_number": 1,
      "step_name": "organization_profile",
      "time_spent_seconds": 45
    },
    "wizard_step_reached": 1,
    "step_duration_seconds": 45,
    "session_id": "session_test_123"
  }'

# Expected response:
# {
#   "event": {
#     "id": "metric_1234567890",
#     "organization_id": "org_test_123",
#     "event_type": "wizard_step_completed",
#     "timestamp": "2025-10-23T15:30:00Z"
#   },
#   "message": "Event tracked successfully"
# }
```

### Verify Event Recorded

```bash
poetry run python -c "
from api.database import get_db
from api.models import OnboardingMetric

db = get_db()

# Count analytics events
events = db.query(OnboardingMetric).filter(
    OnboardingMetric.organization_id == 'org_test_123'
).count()

print(f'✅ Analytics Events Recorded: {events}')
"

# Expected output:
# ✅ Analytics Events Recorded: 1
```

---

## Verification Checklist

Before moving to full implementation, verify:

- [x] Shepherd.js installed and working
- [x] Database tables created successfully
- [x] Wizard state API returns correct structure
- [x] Sample data generation creates labeled records
- [x] Tutorial overlay displays and progresses correctly
- [x] Checklist API calculates completion dynamically
- [x] Analytics events recorded in database

**All checks passed?** → Ready for full implementation! 🎉

---

## Troubleshooting

### Issue: Shepherd.js not loading

**Symptom**: Tutorial overlay doesn't appear

**Fix**:
```bash
# Check if Shepherd.js installed
npm list shepherd.js

# If not installed, install it
npm install shepherd.js --save

# Or use CDN version in HTML
# <script src="https://cdn.jsdelivr.net/npm/shepherd.js@11.0.1/dist/js/shepherd.min.js"></script>
```

---

### Issue: Database tables don't exist

**Symptom**: `relation "onboarding_state" does not exist`

**Fix**:
```bash
# Run migration
poetry run alembic upgrade head

# If migration doesn't exist, create it
poetry run alembic revision --autogenerate -m "Add onboarding tables"
poetry run alembic upgrade head

# Or create tables manually in Python
poetry run python -c "
from api.database import Base, engine
from api.models import OnboardingState, OnboardingChecklistTask, OnboardingTutorialCompletion, OnboardingMetric

Base.metadata.create_all(engine)
print('✅ Tables created!')
"
```

---

### Issue: Sample data not labeled as "(Sample)"

**Symptom**: Sample events don't have "(Sample)" suffix in title

**Fix**: Check `api/services/sample_data_generator.py`:

```python
# Ensure sample data has "(Sample)" suffix
event = Event(
    title=f"{base_title} (Sample)",  # ← Must have (Sample)
    is_sample=True,                  # ← Must be True
    org_id=org_id
)
```

---

### Issue: Checklist shows all tasks incomplete

**Symptom**: All tasks show `completed: false` even after creating events

**Fix**: Verify completion criteria queries:

```bash
# Test query manually
poetry run python -c "
from api.database import get_db

db = get_db()

# Test event count query
result = db.execute(
    'SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE',
    {'org_id': 'org_test_123'}
).scalar()

print(f'Real Events (not sample): {result}')

# If 0, create a real event first:
from api.models import Event
from datetime import datetime, timedelta

event = Event(
    title='Test Event',
    datetime=datetime.utcnow() + timedelta(days=7),
    org_id='org_test_123',
    is_sample=False  # ← Must be False for real event
)
db.add(event)
db.commit()

print('✅ Real event created!')
"
```

---

### Issue: Tutorial overlay blocks UI

**Symptom**: Can't click buttons behind tutorial

**Fix**: Check Shepherd.js configuration:

```javascript
const tour = new Shepherd.Tour({
    useModalOverlay: true,  // Adds semi-transparent overlay
    defaultStepOptions: {
        scrollTo: { behavior: 'smooth', block: 'center' },
        cancelIcon: {
            enabled: true  // Shows X button to close
        }
    }
});

// Add arrow to point to element
tour.addStep({
    attachTo: {
        element: '#button',
        on: 'bottom'  // Arrow points up from button
    },
    // Allow clicking highlighted element
    advanceOn: {
        selector: '#button',
        event: 'click'  // Tutorial advances when button clicked
    }
});
```

---

## Next Steps

After completing this quickstart:

1. **Implement Onboarding Service**:
   - `api/services/onboarding_service.py` - Wizard state machine, checklist logic
   - `api/services/sample_data_generator.py` - Sample data templates

2. **Add API Routers**:
   - `api/routers/onboarding.py` - Wizard, checklist, sample data endpoints
   - `api/routers/analytics.py` - Analytics event tracking

3. **Build Frontend UI**:
   - `frontend/js/onboarding-wizard.js` - 5-step wizard UI
   - `frontend/js/tutorial-overlay.js` - Shepherd.js integration
   - `frontend/js/sample-data-manager.js` - Sample data controls
   - `frontend/js/onboarding-dashboard.js` - Checklist and videos

4. **Add i18n Translations**:
   - `locales/en/onboarding.json` - English translations
   - `locales/es/onboarding.json` - Spanish translations
   - `locales/pt/onboarding.json` - Portuguese translations
   - `locales/zh-CN/onboarding.json` - Simplified Chinese translations
   - `locales/zh-TW/onboarding.json` - Traditional Chinese translations

5. **Run Tests**:
   ```bash
   # Unit tests
   poetry run pytest tests/unit/test_onboarding_service.py -v

   # Integration tests
   poetry run pytest tests/integration/test_onboarding_api.py -v

   # E2E tests
   poetry run pytest tests/e2e/test_wizard_flow.py -v
   ```

---

## Reference Documentation

- **Plan**: `specs/020-user-onboarding/plan.md` - Implementation plan
- **Research**: `specs/020-user-onboarding/research.md` - Technology decisions
- **Data Model**: `specs/020-user-onboarding/data-model.md` - Database schemas
- **API Contracts**: `specs/020-user-onboarding/contracts/` - API specifications
- **Shepherd.js Docs**: https://shepherdjs.dev/docs/
- **Shepherd.js Examples**: https://shepherdjs.dev/docs/examples/

---

**Time to Complete**: 5 minutes
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
