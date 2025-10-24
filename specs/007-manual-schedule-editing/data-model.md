# Data Model: Manual Schedule Editing

**Feature**: Manual Schedule Editing | **Branch**: 007-manual-schedule-editing | **Date**: 2025-10-23

## Overview

This document defines the database schema and data structures for manual schedule editing functionality. The feature extends the existing SignUpFlow data model with minimal new tables, primarily adding a `is_locked` flag to preserve manual overrides across solver re-runs.

**Design Philosophy**: Minimal database changes. Most state (undo/redo history, constraint violations) stored client-side for performance. Only committed manual edits persisted to database.

---

## Database Schema Changes

### 1. Extend `event_assignments` Table

**Purpose**: Mark assignments as "locked" (manually set, don't modify on solver re-run)

```sql
ALTER TABLE event_assignments
ADD COLUMN is_locked BOOLEAN DEFAULT FALSE,
ADD COLUMN locked_at DATETIME NULL,
ADD COLUMN locked_by VARCHAR(255) NULL REFERENCES people(id);

CREATE INDEX idx_event_assignments_locked ON event_assignments(is_locked);
```

**SQLAlchemy Model Extension**:
```python
# api/models.py (extend existing EventAssignment)
class EventAssignment(Base):
    __tablename__ = "event_assignments"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # NEW: Manual editing fields
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(String, ForeignKey("people.id"), nullable=True)

    # Relationships
    event = relationship("Event", back_populates="assignments")
    person = relationship("Person")
    locked_by_user = relationship("Person", foreign_keys=[locked_by])
```

**Usage**:
- When admin manually drags volunteer to time slot → set `is_locked=True`, `locked_by=admin.id`, `locked_at=now()`
- When solver re-runs schedule → skip assignments where `is_locked=True`
- Admin can explicitly "unlock" assignment → set `is_locked=False`

**Storage Impact**: 3 new columns × 10,000 assignments = ~50KB additional storage

### 2. New `manual_edit_log` Table (Audit Trail)

**Purpose**: Audit log of all manual edits for compliance and debugging

```sql
CREATE TABLE manual_edit_log (
    id VARCHAR(255) PRIMARY KEY,
    org_id VARCHAR(255) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    admin_id VARCHAR(255) NOT NULL REFERENCES people(id),
    edit_type VARCHAR(50) NOT NULL,  -- 'reassign', 'swap', 'lock', 'unlock'
    edit_data JSON NOT NULL,          -- Command parameters
    reason TEXT NULL,                 -- Optional reason for edit
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_undone BOOLEAN DEFAULT FALSE,
    undone_at DATETIME NULL
);

CREATE INDEX idx_manual_edit_log_org_timestamp ON manual_edit_log(org_id, timestamp DESC);
CREATE INDEX idx_manual_edit_log_admin_timestamp ON manual_edit_log(admin_id, timestamp DESC);
CREATE INDEX idx_manual_edit_log_undone ON manual_edit_log(is_undone);
```

**SQLAlchemy Model**:
```python
# api/models.py
class ManualEditLog(Base):
    __tablename__ = "manual_edit_log"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(String, ForeignKey("people.id"), nullable=False)
    edit_type = Column(String(50), nullable=False)
    edit_data = Column(JSON, nullable=False)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_undone = Column(Boolean, default=False, nullable=False)
    undone_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization")
    admin = relationship("Person", foreign_keys=[admin_id])

    def to_dict(self):
        return {
            "id": self.id,
            "org_id": self.org_id,
            "admin_id": self.admin_id,
            "edit_type": self.edit_type,
            "edit_data": self.edit_data,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "is_undone": self.is_undone
        }
```

**Edit Types**:
- `reassign`: Move volunteer from one event to another
- `swap`: Swap two volunteers between events
- `lock`: Explicitly lock assignment (prevent solver from changing)
- `unlock`: Explicitly unlock assignment (allow solver to change)
- `bulk_reassign`: Bulk operation affecting multiple assignments

**Edit Data Examples**:
```json
// Reassign edit
{
    "person_id": "person_123",
    "source_event_id": "event_456",
    "target_event_id": "event_789",
    "role": "Worship Leader"
}

// Swap edit
{
    "person_a_id": "person_123",
    "person_b_id": "person_456",
    "event_id": "event_789",
    "role": "Worship Leader"
}

// Lock edit
{
    "assignment_id": "assignment_123",
    "reason": "Pastor specifically requested this volunteer"
}
```

**Usage**:
- Log every manual edit for audit trail (compliance requirement for some organizations)
- Support undo by marking `is_undone=True` (keeps audit trail intact)
- Query edit history for debugging ("When did this assignment change?")
- Generate reports ("How many manual overrides this month?")

**Retention**: Keep logs for 90 days, then archive (compliance requirement varies by organization)

---

## Client-Side Data Structures (Not in Database)

### 3. ConstraintViolation (Transient)

**Purpose**: Represent constraint violations detected during drag-and-drop validation

```typescript
interface ConstraintViolation {
    type: 'availability' | 'role' | 'fairness' | 'coverage';
    severity: 'error' | 'warning' | 'info';
    message: string;
    affectedEntities: {
        personId?: string;
        eventId?: string;
        assignmentId?: string;
    };
    suggestedFix?: Suggestion;
}
```

**Example**:
```javascript
{
    type: 'availability',
    severity: 'error',
    message: 'Jane Doe is unavailable on Sunday 10:00 AM (marked as unavailable)',
    affectedEntities: {
        personId: 'person_123',
        eventId: 'event_456'
    },
    suggestedFix: {
        action: 'reassign',
        targetEventId: 'event_789',
        reasoning: 'Jane is available for Sunday 2:00 PM service'
    }
}
```

**Lifecycle**: Created during validation, displayed in UI, discarded after resolution. Not persisted to database.

### 4. EditCommand (Command Pattern - Session Storage)

**Purpose**: Encapsulate manual edit operations for undo/redo

```typescript
interface EditCommand {
    id: string;  // Unique command ID
    type: 'reassign' | 'swap' | 'lock' | 'unlock';
    data: object;  // Command-specific data
    timestamp: number;  // Unix timestamp
    isTransient: boolean;  // Don't persist to database
    toJSON(): object;  // Serialize for sessionStorage
    execute(): Promise<void>;  // Apply edit
    undo(): Promise<void>;  // Revert edit
}
```

**Implementation** (JavaScript):
```javascript
class ReassignCommand {
    constructor({ personId, sourceEventId, targetEventId, role }) {
        this.id = generateId();
        this.type = 'reassign';
        this.data = { personId, sourceEventId, targetEventId, role };
        this.timestamp = Date.now();
        this.isTransient = false;  // Persist to database
    }

    async execute() {
        // Move volunteer in DOM
        const element = document.querySelector(`[data-person-id="${this.data.personId}"]`);
        const targetContainer = document.querySelector(`[data-event-id="${this.data.targetEventId}"] .assignments`);
        targetContainer.appendChild(element);

        // Update backend
        await api.post('/api/manual-edits', {
            type: 'reassign',
            data: this.data
        });
    }

    async undo() {
        // Move back to original event
        const element = document.querySelector(`[data-person-id="${this.data.personId}"]`);
        const sourceContainer = document.querySelector(`[data-event-id="${this.data.sourceEventId}"] .assignments`);
        sourceContainer.appendChild(element);

        // Revert backend
        await api.post(`/api/manual-edits/${this.id}/undo`);
    }

    toJSON() {
        return {
            id: this.id,
            type: this.type,
            data: this.data,
            timestamp: this.timestamp
        };
    }

    static fromJSON(json) {
        const cmd = new ReassignCommand(json.data);
        cmd.id = json.id;
        cmd.timestamp = json.timestamp;
        return cmd;
    }
}
```

**Storage**: Stored in browser sessionStorage (10-20 KB for 50 commands). Not in database.

---

## Database Migration

**Alembic Migration** (auto-generated with manual edits):

```python
# migrations/versions/xxx_add_manual_editing_support.py
"""Add manual editing support

Revision ID: xxx
Revises: yyy
Create Date: 2025-10-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to event_assignments table
    op.add_column('event_assignments', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('event_assignments', sa.Column('locked_at', sa.DateTime(), nullable=True))
    op.add_column('event_assignments', sa.Column('locked_by', sa.String(255), nullable=True))
    op.create_foreign_key('fk_event_assignments_locked_by', 'event_assignments', 'people', ['locked_by'], ['id'])
    op.create_index('idx_event_assignments_locked', 'event_assignments', ['is_locked'])

    # Create manual_edit_log table
    op.create_table('manual_edit_log',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('org_id', sa.String(255), nullable=False),
        sa.Column('admin_id', sa.String(255), nullable=False),
        sa.Column('edit_type', sa.String(50), nullable=False),
        sa.Column('edit_data', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_undone', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('undone_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['people.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_manual_edit_log_org_timestamp', 'manual_edit_log', ['org_id', sa.text('timestamp DESC')])
    op.create_index('idx_manual_edit_log_admin_timestamp', 'manual_edit_log', ['admin_id', sa.text('timestamp DESC')])
    op.create_index('idx_manual_edit_log_undone', 'manual_edit_log', ['is_undone'])


def downgrade():
    # Drop manual_edit_log table
    op.drop_index('idx_manual_edit_log_undone', table_name='manual_edit_log')
    op.drop_index('idx_manual_edit_log_admin_timestamp', table_name='manual_edit_log')
    op.drop_index('idx_manual_edit_log_org_timestamp', table_name='manual_edit_log')
    op.drop_table('manual_edit_log')

    # Remove columns from event_assignments table
    op.drop_index('idx_event_assignments_locked', table_name='event_assignments')
    op.drop_constraint('fk_event_assignments_locked_by', 'event_assignments', type_='foreignkey')
    op.drop_column('event_assignments', 'locked_by')
    op.drop_column('event_assignments', 'locked_at')
    op.drop_column('event_assignments', 'is_locked')
```

**Run Migration**:
```bash
# Generate migration
poetry run alembic revision --autogenerate -m "Add manual editing support"

# Apply migration
poetry run alembic upgrade head

# Verify
poetry run python -c "
from api.database import get_db
from sqlalchemy import inspect

db = next(get_db())
inspector = inspect(db.bind)

# Check event_assignments extensions
columns = [col['name'] for col in inspector.get_columns('event_assignments')]
print('✅ is_locked' if 'is_locked' in columns else '❌ is_locked missing')
print('✅ locked_at' if 'locked_at' in columns else '❌ locked_at missing')
print('✅ locked_by' if 'locked_by' in columns else '❌ locked_by missing')

# Check manual_edit_log table
tables = inspector.get_table_names()
print('✅ manual_edit_log' if 'manual_edit_log' in tables else '❌ manual_edit_log missing')
"
```

---

## Pydantic Schemas

### Request/Response Schemas for API

```python
# api/schemas/manual_edits.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Literal

class ReassignRequest(BaseModel):
    """Request to reassign volunteer to different event."""
    person_id: str = Field(..., description="ID of volunteer to reassign")
    source_event_id: str = Field(..., description="Current event ID")
    target_event_id: str = Field(..., description="Target event ID")
    role: str = Field(..., description="Role for assignment")
    reason: Optional[str] = Field(None, description="Optional reason for manual edit")

class SwapRequest(BaseModel):
    """Request to swap two volunteers."""
    person_a_id: str
    person_b_id: str
    event_id: str
    role: str
    reason: Optional[str] = None

class LockAssignmentRequest(BaseModel):
    """Request to lock assignment (prevent solver from changing)."""
    assignment_id: str
    reason: Optional[str] = None

class UnlockAssignmentRequest(BaseModel):
    """Request to unlock assignment (allow solver to change)."""
    assignment_id: str

class ConstraintViolationResponse(BaseModel):
    """Constraint violation detected during validation."""
    type: Literal['availability', 'role', 'fairness', 'coverage']
    severity: Literal['error', 'warning', 'info']
    message: str
    affected_entities: Dict[str, str]
    suggested_fix: Optional[Dict[str, Any]] = None

class ValidateEditRequest(BaseModel):
    """Request to validate proposed edit before committing."""
    edit_type: Literal['reassign', 'swap', 'lock', 'unlock']
    edit_data: Dict[str, Any]

class ValidateEditResponse(BaseModel):
    """Validation result with constraint violations."""
    is_valid: bool
    violations: list[ConstraintViolationResponse]
    warnings: list[ConstraintViolationResponse] = []

class ManualEditLogResponse(BaseModel):
    """Manual edit log entry."""
    id: str
    org_id: str
    admin_id: str
    admin_name: str  # Denormalized for display
    edit_type: str
    edit_data: Dict[str, Any]
    reason: Optional[str]
    timestamp: datetime
    is_undone: bool
    undone_at: Optional[datetime]

class EditHistoryResponse(BaseModel):
    """Paginated edit history."""
    edits: list[ManualEditLogResponse]
    total_count: int
    page: int
    page_size: int
```

---

## Storage Requirements

**Per Organization** (assuming 200 volunteers, 50 events):

| Data | Count | Size per Item | Total Size |
|------|-------|---------------|------------|
| EventAssignment (locked fields) | 500 | 50 bytes | 25 KB |
| ManualEditLog (3 months) | 500 edits | 300 bytes | 150 KB |
| **Total per org** | - | - | **~175 KB** |

**For 1000 Organizations**: 175 KB × 1000 = 175 MB (negligible)

**Growth Rate**: Assuming 50 manual edits per month per org:
- Per month: 50 edits × 300 bytes = 15 KB
- Per year: 15 KB × 12 = 180 KB per org

**Cleanup Policy**:
- Archive manual_edit_log older than 90 days
- Compress archived logs (JSON → gzip)
- Keep locked assignments indefinitely (small data)

---

## Query Patterns

### Common Queries

**Get Locked Assignments for Event**:
```sql
SELECT * FROM event_assignments
WHERE event_id = ? AND is_locked = true;
```

**Get Recent Manual Edits by Admin**:
```sql
SELECT * FROM manual_edit_log
WHERE admin_id = ?
ORDER BY timestamp DESC
LIMIT 50;
```

**Count Manual Overrides per Event**:
```sql
SELECT event_id, COUNT(*) as override_count
FROM event_assignments
WHERE is_locked = true
GROUP BY event_id;
```

**Get Undone Edits (for debugging)**:
```sql
SELECT * FROM manual_edit_log
WHERE is_undone = true
ORDER BY timestamp DESC;
```

### Performance Optimization

**Indexes Created**:
- `idx_event_assignments_locked` on `is_locked` (filter locked assignments quickly)
- `idx_manual_edit_log_org_timestamp` on `(org_id, timestamp DESC)` (org edit history)
- `idx_manual_edit_log_admin_timestamp` on `(admin_id, timestamp DESC)` (admin edit history)
- `idx_manual_edit_log_undone` on `is_undone` (filter undone edits)

**Query Performance**:
- Get locked assignments: <10ms (index scan)
- Get edit history: <20ms (index scan + sort)
- Insert manual edit log: <5ms (simple insert)

---

## Backward Compatibility

**No Breaking Changes**: All schema changes are additive (new columns, new table). Existing features continue to work without modification.

**Migration Safety**:
- `is_locked` defaults to `FALSE` (existing assignments remain unlocked)
- `locked_at`, `locked_by` are nullable (no data required for existing assignments)
- New table `manual_edit_log` doesn't affect existing tables

**Rollback Plan**: If Feature 017 needs to be disabled, simply:
1. Set all `is_locked=FALSE` (solver resumes normal operation)
2. Stop writing to `manual_edit_log` (historical logs preserved)
3. No data loss, no schema downgrade needed

---

## Next Steps

**Phase 1 Remaining**:
1. Generate API contracts (`contracts/manual-edit-api.md`, `contracts/constraint-validation-api.md`)
2. Generate quickstart guide (`quickstart.md`)
3. Update agent context (`update-agent-context.sh claude`)

**Phase 2** (Task Breakdown):
- Run `/speckit.tasks` to generate implementation task list
