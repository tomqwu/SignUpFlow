# Rostio Date/Time Architecture

## Principles

### 1. **Storage: Always UTC**
- Database stores all dates/times in UTC
- No timezone conversion on write
- Single source of truth

### 2. **Display: User's Timezone**
- Convert to user's timezone for display only
- User selects timezone in settings
- Default: Browser's timezone if not set

### 3. **API: ISO 8601 with UTC**
- API sends/receives ISO 8601 format
- Always include timezone marker (Z for UTC)
- Example: `2025-10-11T14:00:00Z`

### 4. **Dates Only (No Time)**
- For blocked dates, events without specific time
- Store as DATE type (not DATETIME)
- No timezone issues - "Oct 11" is "Oct 11" everywhere

## Implementation Plan

### Phase 1: Database Schema
```python
# Person model
class Person(Base):
    ...
    timezone = Column(String, default="UTC", nullable=False)
    # Examples: "America/New_York", "Europe/London", "Asia/Tokyo"
```

### Phase 2: Backend Utilities
```python
# api/utils/datetime_utils.py
from datetime import datetime, date
from zoneinfo import ZoneInfo

def to_user_timezone(utc_datetime: datetime, user_tz: str) -> datetime:
    """Convert UTC datetime to user's timezone"""
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=ZoneInfo("UTC"))
    return utc_datetime.astimezone(ZoneInfo(user_tz))

def from_user_timezone(user_datetime: datetime, user_tz: str) -> datetime:
    """Convert user's timezone datetime to UTC"""
    if user_datetime.tzinfo is None:
        user_datetime = user_datetime.replace(tzinfo=ZoneInfo(user_tz))
    return user_datetime.astimezone(ZoneInfo("UTC"))

def parse_date_safe(date_string: str) -> date:
    """Parse date string without timezone issues"""
    # "2025-10-11" -> date(2025, 10, 11)
    return date.fromisoformat(date_string.split('T')[0])
```

### Phase 3: API Response Formatting
```python
# Return timezone-aware ISO strings
class EventResponse(BaseModel):
    start_time: datetime
    timezone: str  # User's timezone for reference

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Always includes timezone
        }
```

### Phase 4: Frontend Utilities
```javascript
// frontend/js/datetime-utils.js

// User's timezone (from settings or browser default)
let userTimezone = null;

function getUserTimezone() {
    if (userTimezone) return userTimezone;
    // Fallback to browser timezone
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function setUserTimezone(tz) {
    userTimezone = tz;
    localStorage.setItem('userTimezone', tz);
}

// Format datetime for display
function formatDateTime(isoString, options = {}) {
    const date = new Date(isoString);
    const tz = options.timezone || getUserTimezone();

    return date.toLocaleString('en-US', {
        timeZone: tz,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        ...options
    });
}

// Format date only (no time, no timezone issues)
function formatDate(dateString) {
    // Input: "2025-10-11" or "2025-10-11T00:00:00Z"
    const [year, month, day] = dateString.split('T')[0].split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Parse date input (from <input type="date">)
function parseDateInput(inputValue) {
    // Input value is always YYYY-MM-DD (local date)
    // Return as-is for storage
    return inputValue;
}
```

### Phase 5: Settings UI
```html
<!-- In Settings Modal -->
<div class="form-group">
    <label>Timezone</label>
    <select id="settings-timezone">
        <option value="">Use browser timezone</option>
        <optgroup label="US & Canada">
            <option value="America/New_York">Eastern Time</option>
            <option value="America/Chicago">Central Time</option>
            <option value="America/Denver">Mountain Time</option>
            <option value="America/Los_Angeles">Pacific Time</option>
        </optgroup>
        <optgroup label="Europe">
            <option value="Europe/London">London</option>
            <option value="Europe/Paris">Paris</option>
            <option value="Europe/Berlin">Berlin</option>
        </optgroup>
        <optgroup label="Asia">
            <option value="Asia/Tokyo">Tokyo</option>
            <option value="Asia/Shanghai">Shanghai</option>
            <option value="Asia/Dubai">Dubai</option>
        </optgroup>
        <optgroup label="Australia">
            <option value="Australia/Sydney">Sydney</option>
            <option value="Australia/Melbourne">Melbourne</option>
        </optgroup>
    </select>
</div>
```

## Migration Strategy

### Step 1: Add Timezone Column
```python
# alembic migration
def upgrade():
    op.add_column('people',
        sa.Column('timezone', sa.String(), nullable=False, server_default='UTC')
    )
```

### Step 2: Update Existing Code (Priority Order)

1. **Date-only fields** (blocked dates, event dates without time)
   - Use `formatDate()` - no timezone conversion needed
   - Store as DATE type

2. **DateTime fields** (event start/end with specific times)
   - Use `formatDateTime()` with user timezone
   - Store as DATETIME in UTC

3. **API responses**
   - Include timezone info in responses
   - Frontend converts for display

### Step 3: Test Cases
```python
# Test timezone handling
def test_blocked_date_no_timezone_shift():
    """Oct 11 in database should show as Oct 11 everywhere"""
    blocked_date = date(2025, 10, 11)
    # Regardless of user timezone, date stays the same
    assert format_date(blocked_date) == "Oct 11, 2025"

def test_event_time_converts_to_user_timezone():
    """Event at 14:00 UTC shows correctly in user's timezone"""
    utc_time = datetime(2025, 10, 11, 14, 0, tzinfo=ZoneInfo("UTC"))

    # New York user (UTC-4 or UTC-5)
    ny_time = to_user_timezone(utc_time, "America/New_York")
    assert ny_time.hour in [9, 10]  # Depending on DST

    # Tokyo user (UTC+9)
    tokyo_time = to_user_timezone(utc_time, "Asia/Tokyo")
    assert tokyo_time.hour == 23
```

## Current Issues to Fix

### 1. Blocked Dates Display
**Problem**: "Oct 11" showing as "Oct 10"

**Current Hack**:
```javascript
const startStr = b.start_date.split('T')[0];
const [year, month, day] = startStr.split('-');
const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
```

**Proper Solution**:
```javascript
// Use formatDate() utility
const displayDate = formatDate(b.start_date);  // "Oct 11"
```

### 2. Event Times
**Problem**: Events showing in UTC instead of user's local time

**Current Code**:
```javascript
const eventDate = new Date(event.start_time);
// Shows UTC time
```

**Proper Solution**:
```javascript
const displayTime = formatDateTime(event.start_time, {
    timezone: currentUser.timezone || getUserTimezone()
});
// Shows "Oct 11, 2025, 10:00 AM EDT"
```

## Benefits of This Approach

1. ✅ **No more date shifting bugs**
2. ✅ **Proper timezone support for international users**
3. ✅ **Consistent date handling across app**
4. ✅ **Easy to test and maintain**
5. ✅ **Follows industry best practices**
6. ✅ **No hacks or workarounds**

## Implementation Timeline

- **Day 1**: Create utilities, add timezone column
- **Day 2**: Update backend API responses
- **Day 3**: Update frontend to use utilities
- **Day 4**: Add timezone selector to Settings
- **Day 5**: Test all date/time features
- **Day 6**: Fix any issues, documentation

## Files to Create/Update

### New Files
- `api/utils/datetime_utils.py` - Backend date utilities
- `frontend/js/datetime-utils.js` - Frontend date utilities
- `alembic/versions/xxx_add_timezone_to_person.py` - Migration

### Files to Update
- `roster_cli/db/models.py` - Add timezone column
- `api/schemas/person.py` - Add timezone field
- `frontend/js/app-user.js` - Use datetime utilities
- `frontend/index.html` - Add timezone selector
- All date/time display code throughout app

## Testing Strategy

1. Unit tests for datetime utilities
2. API tests with different timezones
3. GUI tests verifying correct display
4. Integration tests across timezones
5. Manual testing with different timezone settings

---

**Status**: Architecture defined, ready for implementation
**Next Step**: Create datetime utility modules
