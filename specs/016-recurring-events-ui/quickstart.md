# Recurring Events: 10-Minute Quickstart Guide

**Feature**: Recurring Events UI | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This guide helps you set up and test the Recurring Events feature in 10 minutes. You'll create a weekly recurring series, preview occurrences, handle exceptions, and perform bulk edits.

**Prerequisites**:
- SignUpFlow development environment running
- Admin user account
- Basic familiarity with SignUpFlow UI

---

## Step 1: Install Dependencies (2 minutes)

### Backend Dependencies

```bash
# Add python-dateutil for recurrence calculation
poetry add python-dateutil

# Verify installation
poetry run python -c "from dateutil.rrule import rrule; print('✅ python-dateutil installed')"
```

### Frontend Dependencies

```bash
# Add FullCalendar for calendar preview
npm install @fullcalendar/core @fullcalendar/daygrid

# Verify installation
npm list @fullcalendar/core
```

**Expected Output**:
```
@fullcalendar/core@6.1.10
```

---

## Step 2: Run Database Migration (1 minute)

### Create Migration Script

```bash
# Generate Alembic migration
poetry run alembic revision --autogenerate -m "Add recurring events tables"

# Apply migration
poetry run alembic upgrade head
```

### Verify Tables Created

```bash
# Check database schema
poetry run python -c "
from api.database import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)

tables = inspector.get_table_names()
print('✅ recurring_series' if 'recurring_series' in tables else '❌ recurring_series missing')
print('✅ recurrence_exceptions' if 'recurrence_exceptions' in tables else '❌ recurrence_exceptions missing')

# Check events table extensions
columns = [col['name'] for col in inspector.get_columns('events')]
print('✅ series_id column' if 'series_id' in columns else '❌ series_id missing')
print('✅ sequence_number column' if 'sequence_number' in columns else '❌ sequence_number missing')
print('✅ is_exception column' if 'is_exception' in columns else '❌ is_exception missing')
"
```

**Expected Output**:
```
✅ recurring_series
✅ recurrence_exceptions
✅ series_id column
✅ sequence_number column
✅ is_exception column
```

---

## Step 3: Test Backend API (3 minutes)

### Test Recurrence Calculation

```python
# Test python-dateutil integration
poetry run python -c "
from dateutil.rrule import rrule, WEEKLY
from datetime import datetime

# Generate 52 weekly occurrences
rule = rrule(
    freq=WEEKLY,
    dtstart=datetime(2025, 1, 5, 10, 0, 0),
    count=52,
    byweekday=6  # Sunday
)

occurrences = list(rule)
print(f'✅ Generated {len(occurrences)} occurrences')
print(f'First: {occurrences[0].strftime(\"%Y-%m-%d %H:%M\")}')
print(f'Last: {occurrences[-1].strftime(\"%Y-%m-%d %H:%M\")}')
"
```

**Expected Output**:
```
✅ Generated 52 occurrences
First: 2025-01-05 10:00
Last: 2025-12-28 10:00
```

### Test Preview API

```bash
# Start development server
make run &

# Wait for server to start
sleep 3

# Test preview endpoint
curl -X POST http://localhost:8000/api/recurring-series/preview \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sunday Service",
    "recurrence_rule": {
      "frequency": "weekly",
      "interval": 1,
      "days_of_week": [6]
    },
    "start_datetime": "2025-01-05T10:00:00",
    "count": 52
  }'
```

**Expected Response** (truncated):
```json
{
  "occurrences": [
    {
      "datetime": "2025-01-05T10:00:00Z",
      "sequence_number": 1,
      "title": "Sunday Service"
    },
    {
      "datetime": "2025-01-12T10:00:00Z",
      "sequence_number": 2,
      "title": "Sunday Service"
    }
  ],
  "summary": {
    "total_count": 52,
    "first_occurrence": "2025-01-05T10:00:00Z",
    "last_occurrence": "2025-12-28T10:00:00Z",
    "natural_language": "Weekly on Sunday"
  }
}
```

### Test Create Series API

```bash
# Create recurring series
curl -X POST "http://localhost:8000/api/recurring-series?org_id=YOUR_ORG_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    ]
  }'
```

**Expected Response**:
```json
{
  "id": "series_abc123",
  "title": "Sunday Service",
  "occurrences_created": 52,
  "created_at": "2025-10-23T10:30:45.123Z"
}
```

---

## Step 4: Test Frontend UI (2 minutes)

### Open Admin Console

1. Navigate to `http://localhost:8000/app/admin`
2. Login with admin credentials
3. Click "Events" tab
4. Click "+ Create Recurring Series" button

### Create Weekly Series

1. **Title**: "Sunday Service"
2. **Frequency**: Select "Weekly"
3. **Days**: Check "Sunday"
4. **Start Date**: 2025-01-05
5. **Start Time**: 10:00 AM
6. **Occurrences**: 52
7. **Duration**: 60 minutes

### Verify Calendar Preview

- Calendar should display 52 blue dots (one per Sunday)
- Pattern summary: "Weekly on Sunday"
- Occurrence count: "52 occurrences"

### Create Series

1. Click "Create Series" button
2. Wait for confirmation toast: "Created 52 occurrences"
3. Calendar refreshes showing all events

### Verify Events Created

1. Navigate to "Events" tab
2. Filter by date range: Jan 2025 - Dec 2025
3. Verify 52 "Sunday Service" events appear
4. Click any event → shows "Part of series: series_abc123"

---

## Step 5: Test Exception Handling (1 minute)

### Skip Occurrence (Cancel Event)

1. In calendar view, click Christmas Day occurrence (Dec 25, 10 AM)
2. Click "Skip this occurrence"
3. Enter reason: "Christmas Day - service cancelled"
4. Confirm

**Verify**:
- Dec 25 occurrence removed from calendar
- Red "Cancelled" indicator appears
- Tooltip shows reason on hover

### Modify Occurrence (Reschedule)

1. Click New Year's Day occurrence (Jan 1, 10 AM)
2. Click "Modify this occurrence"
3. Change time to 12:00 PM
4. Enter reason: "New Year's Day - moved to noon"
5. Confirm

**Verify**:
- Jan 1 occurrence moved to 12:00 PM on calendar
- Orange "Modified" indicator appears
- Tooltip shows reason on hover

---

## Step 6: Test Bulk Edit (1 minute)

### Update Role Requirements for Entire Series

1. Navigate to "Recurring Series" tab
2. Click "Sunday Service" series
3. Click "Edit Series" button
4. Change "Worship Leader" count from 1 to 2
5. Confirm

**Verify**:
- Success toast: "Updated 52 occurrences"
- All 52 events now show "Worship Leader: 2"
- Calendar refreshes

### Update Duration for Summer Services

1. In calendar view, select date range: June 1 - Aug 31
2. Multi-select all Sunday services in range (13 occurrences)
3. Click "Edit Selected" button
4. Change duration from 60 to 45 minutes
5. Change title to "Summer Service"
6. Confirm

**Verify**:
- Success toast: "Updated 13 occurrences"
- Summer services show "Summer Service" title
- Duration: 45 minutes
- Rest of year: "Sunday Service", 60 minutes

---

## Common Issues & Solutions

### Issue 1: Migration Fails - Table Already Exists

**Error**:
```
sqlalchemy.exc.OperationalError: table recurring_series already exists
```

**Solution**:
```bash
# Drop and recreate tables
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

### Issue 2: Preview Shows Wrong Dates

**Symptom**: First Sunday should be Jan 5, but shows Jan 12

**Cause**: Wrong `days_of_week` value (0=Monday, 6=Sunday)

**Solution**:
```json
{
  "days_of_week": [6]  // ✅ Correct - Sunday
  // NOT [0] (Monday)
}
```

### Issue 3: Calendar Preview Not Updating

**Symptom**: Pattern changes, but calendar doesn't refresh

**Cause**: Debounce delay (300ms) or API error

**Solution**:
1. Check browser console for errors
2. Verify JWT token is valid
3. Wait 300ms after last change

### Issue 4: Bulk Edit Returns 403 Forbidden

**Symptom**: "Access denied: wrong organization"

**Cause**: Events belong to different organization than admin

**Solution**:
```bash
# Verify all events belong to same org
curl http://localhost:8000/api/events?org_id=YOUR_ORG_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Issue 5: Natural Language Summary Shows "Custom pattern"

**Symptom**: Expected "Weekly on Sunday", got "Custom pattern"

**Cause**: Unsupported pattern or missing translation

**Solution**:
- Verify pattern matches simplified subset (weekly, monthly)
- Check language setting: `current_user.language`
- Add translation key if missing

---

## Verification Checklist

After completing the quickstart, verify all features work:

- [ ] **Backend**:
  - [ ] python-dateutil installed and working
  - [ ] Database tables created (recurring_series, recurrence_exceptions)
  - [ ] Events table extended (series_id, sequence_number, is_exception)
  - [ ] Preview API returns correct occurrences
  - [ ] Create series API generates all events

- [ ] **Frontend**:
  - [ ] FullCalendar displays calendar preview
  - [ ] Pattern changes update preview immediately
  - [ ] Natural language summary displays correctly
  - [ ] Create series button works
  - [ ] Confirmation toast appears

- [ ] **Exceptions**:
  - [ ] Skip occurrence removes from calendar
  - [ ] Modify occurrence changes time on calendar
  - [ ] Exception indicators (red/orange) appear
  - [ ] Tooltips show reasons

- [ ] **Bulk Edit**:
  - [ ] Edit series updates all occurrences
  - [ ] Multi-select works on calendar
  - [ ] Bulk update completes atomically
  - [ ] Success toast shows updated count

---

## Next Steps

### Production Deployment

1. **Database Backup**:
   ```bash
   # Backup before migration
   pg_dump signupflow_db > backup_before_recurring_events.sql
   ```

2. **Run Migration**:
   ```bash
   # Production database
   DATABASE_URL=postgresql://... alembic upgrade head
   ```

3. **Verify Migration**:
   ```bash
   # Check tables exist
   psql signupflow_db -c "\dt recurring_series"
   psql signupflow_db -c "\dt recurrence_exceptions"
   ```

### Performance Monitoring

1. **Track Preview API Latency**:
   - Target: <100ms for 52 occurrences
   - Alert if: >500ms

2. **Track Create Series Time**:
   - Target: <3s for 104 occurrences
   - Alert if: >5s

3. **Track Bulk Edit Time**:
   - Target: <1s for 52 occurrences
   - Alert if: >5s

### User Training

1. **Create User Guide**: docs/USER_GUIDE_RECURRING_EVENTS.md
2. **Record Demo Video**: Show creating weekly series with exceptions
3. **Create FAQ**: Common questions (skip vs modify, bulk edit, etc.)

### Advanced Features (Future)

1. **Google Calendar Sync**: Import/export RFC 5545 rules
2. **Complex Patterns**: "Second Tuesday and Fourth Thursday of month"
3. **Recurring Exceptions**: Skip every Christmas Day automatically
4. **AI-Powered Suggestions**: "Detect holiday conflicts and suggest exceptions"

---

## Troubleshooting Commands

### Check Database State

```bash
# Count recurring series
poetry run python -c "
from api.database import get_db
from api.models import RecurringSeries

db = next(get_db())
count = db.query(RecurringSeries).count()
print(f'Recurring series: {count}')
"

# Count event occurrences
poetry run python -c "
from api.database import get_db
from api.models import Event

db = next(get_db())
count = db.query(Event).filter(Event.series_id != None).count()
print(f'Recurring occurrences: {count}')
"

# Count exceptions
poetry run python -c "
from api.database import get_db
from api.models import RecurrenceException

db = next(get_db())
count = db.query(RecurrenceException).count()
print(f'Exceptions: {count}')
"
```

### Delete Test Data

```bash
# Delete all recurring series (cascades to events and exceptions)
poetry run python -c "
from api.database import get_db
from api.models import RecurringSeries

db = next(get_db())
db.query(RecurringSeries).delete()
db.commit()
print('✅ Deleted all recurring series')
"
```

### Reset Database

```bash
# WARNING: Deletes ALL data
rm roster.db
poetry run python -c "from api.database import init_db; init_db()"
poetry run alembic upgrade head
```

---

## Support & Resources

### Documentation
- [Implementation Plan](./plan.md) - Technical overview
- [Research Document](./research.md) - Technology decisions
- [Data Model](./data-model.md) - Database schema
- [API Contracts](./contracts/) - Endpoint specifications

### Code Locations
- **Backend**: `api/services/recurrence_service.py`, `api/routers/recurring_events.py`
- **Frontend**: `frontend/js/recurring-events.js`, `frontend/js/calendar-preview.js`
- **Tests**: `tests/unit/test_recurrence_service.py`, `tests/e2e/test_recurring_events.py`

### Getting Help
- **GitHub Issues**: https://github.com/tomqwu/signupflow/issues
- **Documentation**: `docs/` directory
- **Email Support**: support@signupflow.io

---

**Quickstart Complete!** 🎉

You've successfully set up and tested the Recurring Events feature. You can now:
- Create weekly, biweekly, and monthly recurring series
- Preview occurrences before creation
- Handle exceptions (skip and modify)
- Perform bulk edits on multiple occurrences

**Total Time**: ~10 minutes ✅
