# Timezone Preference Implementation Plan

## Current State
- ✅ Architecture documented (DATETIME_ARCHITECTURE.md)
- ✅ Backend utilities created (api/utils/datetime_utils.py)
- ❌ Timezone field not added to Person model
- ❌ Settings UI not updated
- ❌ Frontend not using utilities

## Step-by-Step Implementation

### 1. Add Timezone Column to Database

```python
# roster_cli/db/models.py - Line 76 (after roles column)
timezone = Column(String, default="UTC", nullable=False)
```

### 2. Create Migration

```bash
# Run this command:
poetry run alembic revision --autogenerate -m "add timezone to person"

# Then run migration:
poetry run alembic upgrade head
```

### 3. Update Person Schema (API)

```python
# api/schemas/person.py
class PersonCreate(BaseModel):
    ...
    timezone: Optional[str] = "UTC"

class PersonResponse(BaseModel):
    ...
    timezone: str = "UTC"

class PersonUpdate(BaseModel):
    ...
    timezone: Optional[str] = None
```

### 4. Update Settings Modal (Frontend)

```html
<!-- frontend/index.html - In Settings Modal (around line 480) -->

<!-- Add after roles section, before modal footer -->
<div class="setting-item">
    <label>Timezone</label>
    <select id="settings-timezone">
        <option value="">Use browser timezone</option>
        <optgroup label="US & Canada">
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
        </optgroup>
        <optgroup label="Europe">
            <option value="Europe/London">London (GMT/BST)</option>
            <option value="Europe/Paris">Paris (CET/CEST)</option>
            <option value="Europe/Berlin">Berlin (CET/CEST)</option>
        </optgroup>
        <optgroup label="Asia">
            <option value="Asia/Tokyo">Tokyo (JST)</option>
            <option value="Asia/Shanghai">Shanghai (CST)</option>
            <option value="Asia/Dubai">Dubai (GST)</option>
        </optgroup>
        <optgroup label="Australia">
            <option value="Australia/Sydney">Sydney (AEDT/AEST)</option>
        </optgroup>
    </select>
    <p class="help-text">Choose your timezone for correct date/time display</p>
</div>
```

### 5. Update Settings JavaScript

```javascript
// frontend/js/app-user.js - In showSettings() function

// Add to loading settings (around line 800):
document.getElementById('settings-timezone').value = currentUser.timezone || '';

// Add to saveSettings() function (around line 820):
const timezone = document.getElementById('settings-timezone').value || 'UTC';

// Include in update payload:
const updates = {
    roles: selectedRoles,
    timezone: timezone
};
```

### 6. Create Frontend Date Utilities

```javascript
// frontend/js/datetime-utils.js (NEW FILE)

function getUserTimezone() {
    // Get from currentUser or fallback to browser
    return currentUser?.timezone ||
           Intl.DateTimeFormat().resolvedOptions().timeZone ||
           'UTC';
}

function formatDate(dateString) {
    // For date-only fields (no time)
    // Input: "2025-10-11" or "2025-10-11T00:00:00Z"
    const [year, month, day] = dateString.split('T')[0].split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(isoString) {
    // For datetime fields (with time)
    const date = new Date(isoString);
    const tz = getUserTimezone();

    return date.toLocaleString('en-US', {
        timeZone: tz,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}
```

### 7. Include Utilities in HTML

```html
<!-- frontend/index.html - Before app-user.js -->
<script src="js/datetime-utils.js"></script>
<script src="js/app-user.js"></script>
```

### 8. Replace Date Hacks with Utilities

Search and replace across `frontend/js/app-user.js`:

**BEFORE:**
```javascript
const startStr = b.start_date.split('T')[0];
const [year, month, day] = startStr.split('-');
const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
const start = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
```

**AFTER:**
```javascript
const start = formatDate(b.start_date);
```

### 9. Test the Implementation

```bash
# 1. Run migration
poetry run alembic upgrade head

# 2. Start server
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Test in browser:
# - Login
# - Go to Settings
# - Select timezone (e.g., "Pacific Time")
# - Save
# - Check that dates display correctly
# - Verify Oct 11 shows as Oct 11 (not Oct 10)
```

## Files to Create/Update

### New Files
- [x] `api/utils/datetime_utils.py` ✅ Already created
- [ ] `frontend/js/datetime-utils.js` - Frontend date utilities
- [ ] `alembic/versions/xxx_add_timezone.py` - Migration (auto-generated)

### Files to Update
- [ ] `roster_cli/db/models.py` - Add timezone column (line 76)
- [ ] `api/schemas/person.py` - Add timezone field
- [ ] `frontend/index.html` - Add timezone selector (line ~480)
- [ ] `frontend/js/app-user.js` - Use datetime utilities everywhere
  - Line 630-650: Blocked dates display
  - Line 992-1008: People & Availability
  - All other date displays

## Testing Checklist

- [ ] Timezone selector appears in Settings
- [ ] User can select and save timezone
- [ ] Blocked dates show correct date (Oct 11 not Oct 10)
- [ ] Event times convert to user's timezone
- [ ] People & Availability shows correct dates
- [ ] Calendar view shows correct dates
- [ ] PDF export works (uses UTC, no conversion needed)

## Known Issues to Fix

### Issue 1: Oct 10 instead of Oct 11
**Location**: People & Availability, Blocked Dates list
**Root Cause**: `new Date()` timezone conversion
**Fix**: Use `formatDate()` utility

### Issue 2: No timezone preference
**Location**: Settings modal
**Root Cause**: Field not implemented
**Fix**: Add select dropdown, update saveSettings()

### Issue 3: Inconsistent date handling
**Location**: Throughout app
**Root Cause**: Different date parsing methods
**Fix**: Use utilities consistently

## Estimated Time
- Database migration: 10 minutes
- Settings UI: 30 minutes
- Frontend utilities: 20 minutes
- Replace date hacks: 40 minutes
- Testing: 30 minutes
**Total: ~2 hours**

## After Implementation

1. Update `TEST_COVERAGE.md` with timezone tests
2. Add timezone test cases to `comprehensive_test_suite.py`
3. Document timezone feature in `QUICK_START.md`
4. Mark timezone support as ✅ in `FINAL_STATUS.md`

---

**Status**: Ready for implementation
**Blocked By**: 20+ zombie background processes need cleanup first
**Next Step**: Clean up processes, then follow steps 1-9 above
