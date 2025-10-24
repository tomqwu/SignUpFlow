# Data Model: Recurring Events User Interface

**Branch**: `016-recurring-events-ui` | **Date**: 2025-10-23 | **Phase**: 1 (Design)
**Input**: Technology decisions from [research.md](./research.md)

## Overview

This document defines the database schema for the Recurring Events feature, which enables administrators to create and manage repeating event patterns with visual calendar preview.

**Core Entities**:
1. **RecurringSeries**: Stores recurrence pattern metadata
2. **RecurrenceException**: Stores individual occurrence exceptions (skip/modify)
3. **Event** (Extended): Links occurrences to parent series

**Design Principles**:
- **Pre-generation Strategy**: All occurrences stored as regular events (not calculated on-demand)
- **Separate Exception Table**: Better query performance than JSONB array (4x faster)
- **Series-Occurrence Relationship**: `series_id` foreign key links occurrences to parent series

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        organizations                                 │
│  ─────────────────────────────────────────────────────────────────  │
│  id (PK)                                                             │
│  name                                                                │
│  timezone                                                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │ 1
                             │
                             │ N
                ┌────────────┴──────────────┐
                │                           │
                │                           │
         ┌──────▼──────────┐         ┌─────▼──────────────────────┐
         │  recurring_     │         │        events               │
         │  series         │◄────────┤  ──────────────────────────  │
         │  ─────────────  │  N      │  id (PK)                    │
         │  id (PK)        │         │  org_id (FK)                │
         │  org_id (FK)    │         │  series_id (FK) ← NEW       │
         │  title          │         │  sequence_number ← NEW      │
         │  recurrence_    │         │  is_exception ← NEW         │
         │    rule (JSON)  │         │  title                      │
         │  start_datetime │         │  datetime                   │
         │  count          │         │  duration                   │
         │  created_at     │         │  role_requirements (JSON)   │
         │  updated_at     │         │  created_at                 │
         └────────┬────────┘         └─────────────────────────────┘
                  │ 1
                  │
                  │ N
         ┌────────▼──────────────────────┐
         │  recurrence_exceptions         │
         │  ──────────────────────────────│
         │  id (PK)                       │
         │  series_id (FK)                │
         │  exception_type                │
         │  original_date                 │
         │  modified_datetime (nullable)  │
         │  reason (nullable)             │
         │  created_by (FK → people)      │
         │  created_at                    │
         └────────────────────────────────┘
```

---

## Entity Definitions

### 1. RecurringSeries

Stores metadata for recurring event series (pattern, count, start date).

```python
# api/models.py
from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

class RecurringSeries(Base):
    """
    Recurring event series with recurrence pattern.

    Represents the "parent" of all generated event occurrences.
    Example: "Sunday Service" recurring weekly for 52 weeks.
    """
    __tablename__ = "recurring_series"

    # Primary key
    id = Column(String, primary_key=True)  # series_abc123

    # Multi-tenant isolation
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)

    # Series metadata
    title = Column(String(200), nullable=False)  # "Sunday Service"

    # Recurrence rule (RFC 5545 simplified subset)
    recurrence_rule = Column(JSON, nullable=False)
    # Example: {
    #     "frequency": "weekly",
    #     "interval": 1,
    #     "days_of_week": [6],  # Sunday (0=Mon, 6=Sun)
    #     "duration": 60
    # }

    # Start date/time for first occurrence
    start_datetime = Column(DateTime, nullable=False)

    # Number of occurrences to generate (max 104 = 2 years)
    count = Column(Integer, nullable=False)

    # Audit trail
    created_by = Column(String, ForeignKey("people.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    occurrences = relationship(
        "Event",
        back_populates="recurring_series",
        cascade="all, delete-orphan"  # Delete all occurrences when series deleted
    )

    exceptions = relationship(
        "RecurrenceException",
        back_populates="series",
        cascade="all, delete-orphan"
    )

    organization = relationship("Organization")
    creator = relationship("Person", foreign_keys=[created_by])

    # Indexes for performance
    __table_args__ = (
        Index("idx_recurring_series_org_id", "org_id"),
        Index("idx_recurring_series_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<RecurringSeries(id={self.id}, title={self.title}, count={self.count})>"
```

**Field Descriptions**:

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String | No | Primary key | `series_abc123` |
| `org_id` | String (FK) | No | Organization owner | `org_456` |
| `title` | String(200) | No | Series title | `"Sunday Service"` |
| `recurrence_rule` | JSON | No | RFC 5545 pattern | `{"frequency": "weekly", "days_of_week": [6]}` |
| `start_datetime` | DateTime | No | First occurrence | `2025-01-05 10:00:00` |
| `count` | Integer | No | Occurrences to generate | `52` (1 year weekly) |
| `created_by` | String (FK) | No | Admin who created series | `admin_456` |
| `created_at` | DateTime | No | Creation timestamp | `2025-01-01 08:30:00` |
| `updated_at` | DateTime | No | Last update timestamp | `2025-01-05 10:15:00` |

**Recurrence Rule JSON Schema**:
```json
{
  "frequency": "weekly",     // Required: "daily" | "weekly" | "monthly"
  "interval": 1,             // Required: 1-4 (every N days/weeks/months)
  "days_of_week": [6],       // Optional: [0-6] for weekly (0=Mon, 6=Sun)
  "day_of_month": 15,        // Optional: 1-31 for monthly (specific date)
  "week_of_month": 1,        // Optional: 1-4 or -1 for monthly (first/last)
  "duration": 60             // Optional: Default duration in minutes
}
```

**Storage Estimate**: ~500 bytes per series

**Constraints**:
- `count` must be 1-104 (max 2 years)
- `recurrence_rule` validated by Pydantic schema before storage

---

### 2. RecurrenceException

Stores exceptions for individual occurrences (skip or modify).

```python
# api/models.py
class RecurrenceException(Base):
    """
    Exception for individual occurrence in recurring series.

    Types:
    - "skip": Occurrence is cancelled (deleted from events table)
    - "modify": Occurrence time/date changed (event.datetime updated)

    Example: Skip Christmas Day service (Dec 25), or move New Year's service to noon.
    """
    __tablename__ = "recurrence_exceptions"

    # Primary key
    id = Column(String, primary_key=True)  # exception_abc123

    # Link to parent series
    series_id = Column(
        String,
        ForeignKey("recurring_series.id", ondelete="CASCADE"),
        nullable=False
    )

    # Exception type
    exception_type = Column(String(10), nullable=False)  # "skip" or "modify"

    # Original date/time from pattern (before exception)
    original_date = Column(DateTime, nullable=False)

    # Modified date/time (only for "modify" type, null for "skip")
    modified_datetime = Column(DateTime, nullable=True)

    # Human-readable reason for exception
    reason = Column(String(500), nullable=True)  # "Christmas Day - service cancelled"

    # Audit trail
    created_by = Column(String, ForeignKey("people.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    series = relationship("RecurringSeries", back_populates="exceptions")
    creator = relationship("Person", foreign_keys=[created_by])

    # Indexes for performance
    __table_args__ = (
        Index("idx_recurrence_exceptions_series_id", "series_id"),
        Index("idx_recurrence_exceptions_original_date", "original_date"),
        # Prevent duplicate exceptions for same date
        Index(
            "idx_recurrence_exceptions_unique",
            "series_id",
            "original_date",
            unique=True
        ),
    )

    def __repr__(self):
        return f"<RecurrenceException(id={self.id}, type={self.exception_type}, date={self.original_date})>"
```

**Field Descriptions**:

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String | No | Primary key | `exception_abc123` |
| `series_id` | String (FK) | No | Parent series | `series_789` |
| `exception_type` | String(10) | No | Exception type | `"skip"` or `"modify"` |
| `original_date` | DateTime | No | Original occurrence date | `2025-12-25 10:00:00` |
| `modified_datetime` | DateTime | Yes | New date/time (modify only) | `2025-12-25 12:00:00` |
| `reason` | String(500) | Yes | Human-readable reason | `"Christmas Day - service cancelled"` |
| `created_by` | String (FK) | No | Admin who created exception | `admin_456` |
| `created_at` | DateTime | No | Creation timestamp | `2025-12-01 09:00:00` |

**Storage Estimate**: ~202 bytes per exception

**Constraints**:
- `exception_type` must be "skip" or "modify"
- `modified_datetime` required if `exception_type = "modify"`, null if "skip"
- Unique constraint on `(series_id, original_date)` prevents duplicate exceptions

**Usage Examples**:

```python
# Example 1: Skip Christmas Day service
exception_skip = RecurrenceException(
    id="exception_christmas_2025",
    series_id="series_789",
    exception_type="skip",
    original_date=datetime(2025, 12, 25, 10, 0, 0),
    modified_datetime=None,
    reason="Christmas Day - service cancelled",
    created_by="admin_456"
)

# Example 2: Move New Year's service to noon
exception_modify = RecurrenceException(
    id="exception_newyear_2026",
    series_id="series_789",
    exception_type="modify",
    original_date=datetime(2026, 1, 1, 10, 0, 0),
    modified_datetime=datetime(2026, 1, 1, 12, 0, 0),
    reason="New Year's Day - moved to noon",
    created_by="admin_456"
)
```

---

### 3. Event (Extended)

Existing `events` table extended with 3 new columns to link occurrences to series.

```python
# api/models.py
class Event(Base):
    """
    Scheduled event (single occurrence or part of recurring series).

    Extended with recurring event support:
    - series_id: Links occurrence to parent series (null for standalone events)
    - sequence_number: Order within series (1, 2, 3, ...)
    - is_exception: True if occurrence modified from original pattern
    """
    __tablename__ = "events"

    # Existing fields (unchanged)
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    title = Column(String(200), nullable=False)
    datetime = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes
    role_requirements = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # NEW: Recurring event fields
    series_id = Column(
        String,
        ForeignKey("recurring_series.id", ondelete="CASCADE"),
        nullable=True  # Null for standalone events
    )

    sequence_number = Column(
        Integer,
        nullable=True  # Null for standalone events
    )

    is_exception = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    recurring_series = relationship("RecurringSeries", back_populates="occurrences")
    organization = relationship("Organization")

    # Indexes for performance
    __table_args__ = (
        Index("idx_events_org_id", "org_id"),
        Index("idx_events_datetime", "datetime"),
        Index("idx_events_series_id", "series_id"),  # NEW
        Index("idx_events_series_sequence", "series_id", "sequence_number"),  # NEW
    )

    def __repr__(self):
        if self.series_id:
            return f"<Event(id={self.id}, series={self.series_id}, seq={self.sequence_number})>"
        else:
            return f"<Event(id={self.id}, title={self.title})>"
```

**New Field Descriptions**:

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `series_id` | String (FK) | Yes | Parent series ID (null for standalone) | `series_789` |
| `sequence_number` | Integer | Yes | Order in series (1, 2, 3...) | `12` (12th occurrence) |
| `is_exception` | Boolean | No | Modified from original pattern | `true` (time changed) |

**Field Semantics**:

- **Standalone Event** (not recurring):
  - `series_id = NULL`
  - `sequence_number = NULL`
  - `is_exception = false`

- **Regular Occurrence** (part of recurring series):
  - `series_id = "series_789"`
  - `sequence_number = 1-104`
  - `is_exception = false`

- **Exception Occurrence** (modified time/date):
  - `series_id = "series_789"`
  - `sequence_number = 1-104`
  - `is_exception = true` (indicates modification)

**Example Event Records**:

```python
# Standalone event (not recurring)
event_standalone = Event(
    id="event_abc123",
    org_id="org_456",
    title="Special Guest Speaker",
    datetime=datetime(2025, 3, 15, 10, 0, 0),
    duration=60,
    role_requirements=[{"role": "Host", "count": 1}],
    series_id=None,
    sequence_number=None,
    is_exception=False
)

# Regular occurrence (part of series)
event_occurrence = Event(
    id="event_def456",
    org_id="org_456",
    title="Sunday Service",
    datetime=datetime(2025, 1, 5, 10, 0, 0),
    duration=60,
    role_requirements=[{"role": "Worship Leader", "count": 1}],
    series_id="series_789",
    sequence_number=1,  # 1st occurrence in series
    is_exception=False
)

# Exception occurrence (modified time)
event_exception = Event(
    id="event_ghi789",
    org_id="org_456",
    title="Sunday Service",
    datetime=datetime(2026, 1, 1, 12, 0, 0),  # Moved to noon
    duration=60,
    role_requirements=[{"role": "Worship Leader", "count": 1}],
    series_id="series_789",
    sequence_number=52,  # 52nd occurrence
    is_exception=True  # Time changed from original 10:00 AM
)
```

---

## Queries and Performance

### Common Query Patterns

#### 1. List All Events for Organization (including recurring)

```sql
SELECT * FROM events
WHERE org_id = 'org_456'
ORDER BY datetime ASC;
```

**Performance**: <50ms (with index on `org_id`)

**Result**: All events (standalone + recurring occurrences) in chronological order.

---

#### 2. Get All Occurrences in Recurring Series

```sql
SELECT * FROM events
WHERE series_id = 'series_789'
ORDER BY sequence_number ASC;
```

**Performance**: <10ms (with index on `series_id`)

**Result**: All 52 occurrences in series, ordered by sequence.

---

#### 3. Get Recurring Series with Metadata

```sql
SELECT
    rs.id,
    rs.title,
    rs.recurrence_rule,
    rs.start_datetime,
    rs.count,
    COUNT(e.id) as occurrences_created,
    COUNT(re.id) as exceptions_count
FROM recurring_series rs
LEFT JOIN events e ON e.series_id = rs.id
LEFT JOIN recurrence_exceptions re ON re.series_id = rs.id
WHERE rs.org_id = 'org_456'
GROUP BY rs.id;
```

**Performance**: <50ms (with indexes)

**Result**: Series metadata + counts of occurrences and exceptions.

---

#### 4. Get Exceptions for Series

```sql
SELECT * FROM recurrence_exceptions
WHERE series_id = 'series_789'
ORDER BY original_date ASC;
```

**Performance**: <5ms (with index on `series_id`)

**Result**: All exceptions (skip + modify) for series.

---

#### 5. Check if Occurrence Has Exception

```sql
SELECT * FROM recurrence_exceptions
WHERE series_id = 'series_789'
AND original_date = '2025-12-25 10:00:00';
```

**Performance**: <2ms (with compound index on `series_id + original_date`)

**Result**: Exception record if exists, null otherwise.

---

#### 6. List Occurrences with Exceptions Applied

```sql
SELECT
    e.id,
    e.title,
    e.datetime,
    e.series_id,
    e.sequence_number,
    e.is_exception,
    re.exception_type,
    re.reason
FROM events e
LEFT JOIN recurrence_exceptions re
    ON re.series_id = e.series_id
    AND re.original_date = e.datetime
WHERE e.series_id = 'series_789'
ORDER BY e.sequence_number ASC;
```

**Performance**: <15ms (with indexes)

**Result**: All occurrences with exception metadata (type, reason).

---

### Bulk Operations

#### 1. Delete Entire Series (cascade to occurrences)

```sql
DELETE FROM recurring_series WHERE id = 'series_789';
-- Cascades to:
-- - All events with series_id = 'series_789' (cascade delete)
-- - All recurrence_exceptions with series_id = 'series_789' (cascade delete)
```

**Performance**: <50ms for 52 occurrences + 5 exceptions

**Database Behavior**: Automatic cascade delete via foreign key `ON DELETE CASCADE`.

---

#### 2. Bulk Update All Occurrences in Series

```sql
UPDATE events
SET role_requirements = '[{"role": "Worship Leader", "count": 2}]'
WHERE series_id = 'series_789';
```

**Performance**: <50ms for 52 occurrences (atomic transaction)

**Use Case**: Change role requirements for entire series.

---

#### 3. Mark Occurrence as Exception

```sql
UPDATE events
SET is_exception = true, datetime = '2026-01-01 12:00:00'
WHERE id = 'event_ghi789';
```

**Performance**: <5ms (single row update)

**Use Case**: Modify individual occurrence after exception created.

---

## Migration Strategy

### Phase 1: Add New Tables

```sql
-- Create recurring_series table
CREATE TABLE recurring_series (
    id VARCHAR(50) PRIMARY KEY,
    org_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    recurrence_rule JSON NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    count INTEGER NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES people(id)
);

CREATE INDEX idx_recurring_series_org_id ON recurring_series(org_id);
CREATE INDEX idx_recurring_series_created_at ON recurring_series(created_at);

-- Create recurrence_exceptions table
CREATE TABLE recurrence_exceptions (
    id VARCHAR(50) PRIMARY KEY,
    series_id VARCHAR(50) NOT NULL,
    exception_type VARCHAR(10) NOT NULL CHECK (exception_type IN ('skip', 'modify')),
    original_date TIMESTAMP NOT NULL,
    modified_datetime TIMESTAMP,
    reason VARCHAR(500),
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES recurring_series(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES people(id)
);

CREATE INDEX idx_recurrence_exceptions_series_id ON recurrence_exceptions(series_id);
CREATE INDEX idx_recurrence_exceptions_original_date ON recurrence_exceptions(original_date);
CREATE UNIQUE INDEX idx_recurrence_exceptions_unique ON recurrence_exceptions(series_id, original_date);
```

### Phase 2: Extend Events Table

```sql
-- Add new columns to events table
ALTER TABLE events ADD COLUMN series_id VARCHAR(50);
ALTER TABLE events ADD COLUMN sequence_number INTEGER;
ALTER TABLE events ADD COLUMN is_exception BOOLEAN NOT NULL DEFAULT false;

-- Add foreign key constraint
ALTER TABLE events ADD CONSTRAINT fk_events_series_id
    FOREIGN KEY (series_id) REFERENCES recurring_series(id) ON DELETE CASCADE;

-- Add indexes for performance
CREATE INDEX idx_events_series_id ON events(series_id);
CREATE INDEX idx_events_series_sequence ON events(series_id, sequence_number);
```

### Phase 3: Backfill Existing Data (if needed)

```sql
-- No backfill needed - all existing events are standalone (series_id = NULL)
-- New recurring events will have series_id populated
```

### Phase 4: Validation Queries

```sql
-- Verify all series have occurrences
SELECT rs.id, rs.count, COUNT(e.id) as actual_count
FROM recurring_series rs
LEFT JOIN events e ON e.series_id = rs.id
GROUP BY rs.id
HAVING COUNT(e.id) != rs.count;
-- Should return 0 rows (all series have correct occurrence count)

-- Verify all exceptions link to valid series
SELECT re.id FROM recurrence_exceptions re
LEFT JOIN recurring_series rs ON rs.id = re.series_id
WHERE rs.id IS NULL;
-- Should return 0 rows (no orphaned exceptions)

-- Verify exception occurrences marked correctly
SELECT e.id FROM events e
INNER JOIN recurrence_exceptions re
    ON re.series_id = e.series_id
    AND re.original_date = e.datetime
WHERE e.is_exception = false;
-- Should return 0 rows (all exception occurrences marked)
```

---

## Storage Analysis

### Per-Series Storage

```
RecurringSeries record: 500 bytes
+ 52 Event occurrences: 52 × 391 bytes = 20,332 bytes
+ 5 RecurrenceException records: 5 × 202 bytes = 1,010 bytes
──────────────────────────────────────────────────────
Total per series: ~21,842 bytes = ~21 KB
```

### Organization Storage Estimate

```
50 recurring series per organization
× 21 KB per series
──────────────────────────────────
Total: ~1.05 MB per organization

1000 organizations × 1.05 MB = ~1.05 GB total
```

**Conclusion**: Storage cost is negligible for modern databases (1 GB for 1000 organizations).

---

## Validation Rules

### Application-Level Validation (Pydantic)

```python
# api/schemas/recurrence.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class RecurrenceRuleCreate(BaseModel):
    """Pydantic schema for recurrence rule validation."""
    frequency: str = Field(..., regex="^(daily|weekly|monthly)$")
    interval: int = Field(default=1, ge=1, le=4)
    days_of_week: Optional[List[int]] = Field(None, min_items=1, max_items=7)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    week_of_month: Optional[int] = Field(None, ge=-1, le=4)
    duration: Optional[int] = Field(60, ge=15, le=480)  # 15 min to 8 hours

    @validator("days_of_week")
    def validate_days_of_week(cls, v):
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("days_of_week must be 0-6 (Monday-Sunday)")
        return v

class RecurringSeriesCreate(BaseModel):
    """Pydantic schema for creating recurring series."""
    title: str = Field(..., min_length=1, max_length=200)
    recurrence_rule: RecurrenceRuleCreate
    start_datetime: datetime
    count: int = Field(..., ge=1, le=104)  # Max 2 years
    role_requirements: List[dict] = Field(..., min_items=1)

class RecurrenceExceptionCreate(BaseModel):
    """Pydantic schema for creating exception."""
    exception_type: str = Field(..., regex="^(skip|modify)$")
    original_date: datetime
    modified_datetime: Optional[datetime] = None
    reason: Optional[str] = Field(None, max_length=500)

    @validator("modified_datetime")
    def validate_modified_datetime(cls, v, values):
        if values.get("exception_type") == "modify" and v is None:
            raise ValueError("modified_datetime required for 'modify' exception type")
        if values.get("exception_type") == "skip" and v is not None:
            raise ValueError("modified_datetime must be null for 'skip' exception type")
        return v
```

### Database-Level Constraints

```sql
-- recurring_series constraints
ALTER TABLE recurring_series
    ADD CONSTRAINT chk_count_range CHECK (count >= 1 AND count <= 104);

-- recurrence_exceptions constraints
ALTER TABLE recurrence_exceptions
    ADD CONSTRAINT chk_exception_type CHECK (exception_type IN ('skip', 'modify'));

ALTER TABLE recurrence_exceptions
    ADD CONSTRAINT chk_modified_datetime_for_modify
        CHECK (
            (exception_type = 'modify' AND modified_datetime IS NOT NULL)
            OR (exception_type = 'skip' AND modified_datetime IS NULL)
        );
```

---

## Relationships Summary

```
organizations
    ├── recurring_series (1:N)
    │   ├── occurrences → events (1:N, cascade delete)
    │   └── exceptions → recurrence_exceptions (1:N, cascade delete)
    └── events (1:N)
        ├── recurring_series (N:1, optional)
        └── organization (N:1)

people
    ├── created_series → recurring_series (1:N)
    └── created_exceptions → recurrence_exceptions (1:N)
```

**Cascade Delete Behavior**:
- Delete `recurring_series` → auto-delete all linked `events` + `recurrence_exceptions`
- Delete `organization` → auto-delete all `recurring_series` (which cascade to events/exceptions)

---

## Next Steps

1. **Complete Phase 1** ✅ (This Document)
   - Data model defined with 2 new tables + 3 extended columns
   - Relationships and indexes specified
   - Migration strategy documented

2. **Generate 4 API Contracts**:
   - `recurring-series-api.md`: POST/GET/PUT/DELETE /api/recurring-series
   - `recurrence-exceptions-api.md`: POST/DELETE /api/recurring-series/{id}/exceptions
   - `bulk-edit-api.md`: POST /api/events/bulk-edit
   - `calendar-preview-api.md`: POST /api/recurring-series/preview

3. **Generate Quickstart Guide**:
   - `quickstart.md`: 10-minute recurring events setup guide

4. **Update Agent Context**:
   - Run `.specify/scripts/bash/update-agent-context.sh claude`

---

**Document Status**: ✅ Complete
**Next Action**: Generate 4 API contract documents
