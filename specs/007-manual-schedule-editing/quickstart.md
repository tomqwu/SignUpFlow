# Quick Start: Manual Schedule Editing (10 Minutes)

**Feature**: Manual Schedule Editing | **Branch**: `007-manual-schedule-editing` | **Date**: 2025-10-23

Get manual schedule editing running in 10 minutes. This guide covers installation, database migration, testing, and integration.

---

## Prerequisites

- SignUpFlow backend running (`make run`)
- Admin account created (for testing admin-only features)
- Browser with DevTools (for frontend testing)
- Python 3.11+ and Poetry installed

**Time Estimate**: 10 minutes

---

## Step 1: Install Frontend Dependencies (2 minutes)

### Install SortableJS

```bash
cd /home/ubuntu/SignUpFlow/frontend
npm install sortablejs@1.15.2 --save
```

**Verify Installation**:
```bash
npm list sortablejs
# Expected: sortablejs@1.15.2
```

**Bundle Size Check**:
```bash
du -h node_modules/sortablejs/Sortable.min.js
# Expected: ~11KB
```

---

## Step 2: Database Migration (2 minutes)

### Generate Migration

```bash
cd /home/ubuntu/SignUpFlow

# Generate Alembic migration
poetry run alembic revision --autogenerate -m "Add manual editing support to event_assignments"
```

**Expected Migration** (verify in `alembic/versions/xxx_add_manual_editing.py`):
```python
def upgrade():
    # Add manual editing columns to event_assignments
    op.add_column('event_assignments', sa.Column('is_locked', sa.Boolean(),
                                                  nullable=False, server_default='false'))
    op.add_column('event_assignments', sa.Column('locked_at', sa.DateTime(), nullable=True))
    op.add_column('event_assignments', sa.Column('locked_by', sa.String(255), nullable=True))

    # Create index for performance
    op.create_index('idx_event_assignments_locked', 'event_assignments', ['is_locked'])

    # Create manual_edit_log table
    op.create_table('manual_edit_log',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('org_id', sa.String(255), nullable=False),
        sa.Column('admin_id', sa.String(255), nullable=False),
        sa.Column('edit_type', sa.String(50), nullable=False),
        sa.Column('edit_data', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('is_undone', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('undone_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['admin_id'], ['people.id'])
    )

    # Create indexes for query performance
    op.create_index('idx_manual_edit_log_org_timestamp', 'manual_edit_log',
                    ['org_id', 'timestamp'])
```

### Run Migration

```bash
poetry run alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, Add manual editing support
```

### Verify Schema Changes

```bash
poetry run python -c "
from api.database import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)

# Check event_assignments columns
columns = [col['name'] for col in inspector.get_columns('event_assignments')]
print('✅ is_locked' if 'is_locked' in columns else '❌ Missing is_locked')
print('✅ locked_at' if 'locked_at' in columns else '❌ Missing locked_at')
print('✅ locked_by' if 'locked_by' in columns else '❌ Missing locked_by')

# Check manual_edit_log table
tables = inspector.get_table_names()
print('✅ manual_edit_log' if 'manual_edit_log' in tables else '❌ Missing table')
"
```

**Expected Output**:
```
✅ is_locked
✅ locked_at
✅ locked_by
✅ manual_edit_log
```

---

## Step 3: Test Backend API (3 minutes)

### Start Backend Server

```bash
make run
# OR
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test Validation Endpoint

**Open new terminal window**:
```bash
# Login as admin to get JWT token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.token')

# Test validation endpoint (should return 200 OK)
curl -X POST "http://localhost:8000/api/manual-edits/validate?org_id=org_123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "edit_type": "reassign",
    "edit_data": {
      "person_id": "person_456",
      "target_event_id": "event_012",
      "role": "Worship Leader"
    }
  }'
```

**Expected Response** (200 OK):
```json
{
  "is_valid": true,
  "violations": [],
  "warnings": [],
  "suggestions": []
}
```

### Test Reassignment Endpoint

```bash
# Test reassignment (should return 201 Created)
curl -X POST "http://localhost:8000/api/manual-edits/reassign?org_id=org_123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "person_456",
    "source_event_id": "event_789",
    "target_event_id": "event_012",
    "role": "Worship Leader",
    "reason": "Testing manual edit"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": "edit_345",
  "status": "success",
  "assignment_id": "assignment_678",
  "is_locked": true,
  "locked_at": "2025-10-23T14:30:00Z",
  "locked_by": "admin_123",
  "violations": [],
  "warnings": []
}
```

### Verify Database Persistence

```bash
poetry run python -c "
from api.database import get_db
from api.models import EventAssignment, ManualEditLog

db = next(get_db())

# Check locked assignment
assignment = db.query(EventAssignment).filter(
    EventAssignment.is_locked == True
).first()

if assignment:
    print(f'✅ Locked assignment: {assignment.id}')
    print(f'   Person: {assignment.person_id}')
    print(f'   Event: {assignment.event_id}')
    print(f'   Locked by: {assignment.locked_by}')
else:
    print('❌ No locked assignments found')

# Check edit log
log_entry = db.query(ManualEditLog).first()
if log_entry:
    print(f'✅ Edit log entry: {log_entry.id}')
    print(f'   Type: {log_entry.edit_type}')
    print(f'   Admin: {log_entry.admin_id}')
else:
    print('❌ No edit log entries found')
"
```

---

## Step 4: Test Frontend Integration (2 minutes)

### Add Drag-and-Drop to Admin Console

**File**: `frontend/js/schedule-editor.js` (create new file)

```javascript
import Sortable from 'sortablejs';
import { authFetch } from './auth.js';

class ScheduleEditor {
    constructor() {
        this.sortables = [];
        this.editHistory = new EditHistory();
    }

    initializeDragDrop() {
        const eventContainers = document.querySelectorAll('.event-assignments');

        eventContainers.forEach(container => {
            const sortable = Sortable.create(container, {
                group: 'schedule',
                animation: 150,
                handle: '.drag-handle',

                // Validate move before completing
                onMove: (evt) => {
                    return this.validateMove(evt);
                },

                // Commit on drop
                onEnd: (evt) => {
                    this.handleDrop(evt);
                }
            });

            this.sortables.push(sortable);
        });
    }

    async validateMove(evt) {
        const personId = evt.dragged.dataset.personId;
        const targetEventId = evt.to.dataset.eventId;
        const role = evt.dragged.dataset.role;

        try {
            const response = await authFetch('/api/manual-edits/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    edit_type: 'reassign',
                    edit_data: { person_id: personId, target_event_id: targetEventId, role }
                })
            });

            const result = await response.json();

            // Show visual feedback
            if (result.violations.some(v => v.severity === 'error')) {
                evt.to.classList.add('drop-invalid');
                this.showConstraintWarning(result.violations);
                return false; // Cancel drop
            } else if (result.warnings.length > 0) {
                evt.to.classList.add('drop-warning');
                this.showConstraintWarning(result.warnings);
            } else {
                evt.to.classList.add('drop-valid');
            }

            return true; // Allow drop
        } catch (error) {
            console.error('Validation failed:', error);
            return false;
        }
    }

    async handleDrop(evt) {
        const personId = evt.item.dataset.personId;
        const sourceEventId = evt.from.dataset.eventId;
        const targetEventId = evt.to.dataset.eventId;
        const role = evt.item.dataset.role;

        try {
            const response = await authFetch('/api/manual-edits/reassign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    person_id: personId,
                    source_event_id: sourceEventId,
                    target_event_id: targetEventId,
                    role: role
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                // Add to undo history
                this.editHistory.push({
                    type: 'reassign',
                    data: { personId, sourceEventId, targetEventId, role },
                    undo: () => this.undoReassignment(result.assignment_id)
                });

                this.showToast('Assignment updated', 'success');
            }
        } catch (error) {
            console.error('Reassignment failed:', error);
            // Revert UI change
            evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
            this.showToast('Failed to update assignment', 'error');
        }
    }
}

class EditHistory {
    constructor(maxSize = 50) {
        this.undoStack = [];
        this.redoStack = [];
        this.maxSize = maxSize;
        this.loadFromSession();
    }

    push(command) {
        this.undoStack.push(command);
        this.redoStack = []; // Clear redo on new command

        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift();
        }

        this.saveToSession();
    }

    async undo() {
        if (this.undoStack.length === 0) return;

        const command = this.undoStack.pop();
        await command.undo();
        this.redoStack.push(command);

        this.saveToSession();
    }

    async redo() {
        if (this.redoStack.length === 0) return;

        const command = this.redoStack.pop();
        await command.redo();
        this.undoStack.push(command);

        this.saveToSession();
    }

    saveToSession() {
        sessionStorage.setItem('editHistory', JSON.stringify({
            undoStack: this.undoStack,
            redoStack: this.redoStack
        }));
    }

    loadFromSession() {
        const data = sessionStorage.getItem('editHistory');
        if (data) {
            const parsed = JSON.parse(data);
            this.undoStack = parsed.undoStack || [];
            this.redoStack = parsed.redoStack || [];
        }
    }
}

export default ScheduleEditor;
```

### Test in Browser

1. Open `http://localhost:8000/app/admin`
2. Navigate to schedule view
3. **Test drag-and-drop**:
   - Drag a volunteer assignment to different event
   - Should see validation feedback (green/yellow/red border)
   - Should see success toast on drop
4. **Test undo**:
   - Press `Ctrl+Z` (or `Cmd+Z` on Mac)
   - Should revert assignment
5. **Test redo**:
   - Press `Ctrl+Shift+Z` (or `Cmd+Shift+Z` on Mac)
   - Should re-apply assignment

**Open DevTools Console**:
```javascript
// Check edit history
const history = JSON.parse(sessionStorage.getItem('editHistory'));
console.log('Undo stack:', history.undoStack.length);
console.log('Redo stack:', history.redoStack.length);
```

---

## Step 5: Test Undo/Redo (1 minute)

### Test Keyboard Shortcuts

**Add keyboard listener** to `frontend/js/app-admin.js`:

```javascript
import ScheduleEditor from './schedule-editor.js';

const scheduleEditor = new ScheduleEditor();
scheduleEditor.initializeDragDrop();

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Z or Cmd+Z - Undo
    if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        scheduleEditor.editHistory.undo();
    }

    // Ctrl+Shift+Z or Cmd+Shift+Z - Redo
    if ((e.ctrlKey || e.metaKey) && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        scheduleEditor.editHistory.redo();
    }
});
```

### Manual Test

1. Make 3 manual edits (drag-drop assignments)
2. Press `Ctrl+Z` 3 times → All 3 edits should be undone
3. Press `Ctrl+Shift+Z` 3 times → All 3 edits should be redone
4. Refresh page → Undo stack should be cleared (sessionStorage cleared)

**Expected Behavior**:
- Undo/redo should be instant (<5ms)
- Each undo should make API call to revert backend state
- Visual feedback should be immediate (before API response)

---

## Troubleshooting

### Issue: "Module not found: sortablejs"

**Symptom**: `Error: Cannot find module 'sortablejs'`

**Fix**:
```bash
cd frontend
npm install sortablejs --save
npm list sortablejs  # Verify installation
```

### Issue: Migration Fails - Column Already Exists

**Symptom**: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) duplicate column name: is_locked`

**Fix**:
```bash
# Check if columns already exist
poetry run python -c "
from api.database import get_db
from sqlalchemy import inspect
db = next(get_db())
inspector = inspect(db.bind)
columns = [col['name'] for col in inspector.get_columns('event_assignments')]
print('Existing columns:', columns)
"

# If columns exist, skip migration or create manual migration
poetry run alembic stamp head
```

### Issue: 403 Forbidden on Manual Edit Endpoints

**Symptom**: `{"detail": "Admin access required"}`

**Fix**:
```bash
# Verify JWT token has admin role
curl -X GET "http://localhost:8000/api/people/me" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.roles'

# Expected: ["admin"] or ["volunteer", "admin"]

# If missing admin role, add via database
poetry run python -c "
from api.database import get_db
from api.models import Person
import json

db = next(get_db())
person = db.query(Person).filter(Person.email == 'admin@example.com').first()
person.roles = json.dumps(['admin'])
db.commit()
print('✅ Added admin role')
"
```

### Issue: Drag-and-Drop Not Working

**Symptom**: Can't drag volunteer assignments

**Fix**:
1. Check console for JavaScript errors
2. Verify SortableJS import:
   ```javascript
   import Sortable from 'sortablejs';
   console.log(Sortable); // Should show function
   ```
3. Check HTML structure:
   ```html
   <!-- Event containers need data-event-id -->
   <div class="event-assignments" data-event-id="event_123">
       <!-- Assignments need data-person-id and drag handles -->
       <div class="assignment" data-person-id="person_456" data-role="Worship Leader">
           <span class="drag-handle">⋮⋮</span>
           <span>Jane Doe</span>
       </div>
   </div>
   ```

### Issue: Undo Stack Lost on Page Refresh

**Symptom**: Undo history cleared after refresh

**Expected Behavior**: This is correct! sessionStorage is cleared on refresh for security.

**Workaround**: Save edits to database periodically:
```javascript
// Auto-save every 30 seconds
setInterval(() => {
    scheduleEditor.editHistory.saveToDatabase();
}, 30000);
```

---

## Verification Checklist

Before moving to implementation phase, verify:

- [ ] SortableJS installed (`npm list sortablejs` shows 1.15.2)
- [ ] Database migration complete (`is_locked` column exists)
- [ ] `manual_edit_log` table created
- [ ] Validation endpoint returns 200 OK
- [ ] Reassignment endpoint returns 200 OK
- [ ] Locked assignment in database (`is_locked=true`)
- [ ] Edit log entry in database
- [ ] Drag-and-drop works in browser
- [ ] Constraint validation shows visual feedback (red/yellow/green)
- [ ] Undo/redo keyboard shortcuts work
- [ ] Edit history persists in sessionStorage

---

## Next Steps

After completing this quickstart:

1. **Run Integration Tests**:
   ```bash
   poetry run pytest tests/integration/test_manual_edits.py -v
   ```

2. **Run E2E Tests**:
   ```bash
   poetry run pytest tests/e2e/test_manual_editing.py -v
   ```

3. **Implement Full Feature** (use `/speckit.tasks` to generate task breakdown):
   - Complete UI styling (drag handles, drop zones, constraint badges)
   - Add conflict resolution dialog
   - Add manual edit history panel
   - Implement bulk operations (swap multiple, lock multiple)
   - Add fairness metrics overlay

4. **Performance Testing**:
   ```bash
   # Benchmark drag-drop responsiveness
   poetry run python scripts/benchmark_manual_edits.py
   ```

---

## Reference Documentation

- **Plan**: `specs/007-manual-schedule-editing/plan.md`
- **Research**: `specs/007-manual-schedule-editing/research.md`
- **Data Model**: `specs/007-manual-schedule-editing/data-model.md`
- **API Contract**: `specs/007-manual-schedule-editing/contracts/manual-editing-api.md`
- **SortableJS Docs**: https://github.com/SortableJS/Sortable
- **Command Pattern**: https://refactoring.guru/design-patterns/command

---

## Support

- **Issues**: https://github.com/tomqwu/signupflow/issues
- **Docs**: `docs/` directory
- **Slack**: #manual-editing-dev (internal)

---

**Time to Complete**: 10 minutes
**Last Updated**: 2025-10-23
**Feature**: 017 - Manual Schedule Editing
