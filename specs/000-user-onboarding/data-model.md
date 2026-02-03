# Data Model: User Onboarding System

**Feature**: User Onboarding System | **Branch**: `020-user-onboarding` | **Date**: 2025-10-23

Database schemas for onboarding wizard state, checklist tracking, tutorial completions, and analytics.

---

## Overview

The onboarding system requires 4 new database tables:

1. **onboarding_state** - Wizard progress and sample data state per organization
2. **onboarding_checklist_task** - Task definitions for progress checklist
3. **onboarding_tutorial_completion** - Tutorial view/completion tracking
4. **onboarding_metric** - Analytics events for funnel analysis

---

## Table: `onboarding_state`

**Purpose**: Track wizard progress, sample data generation, feature unlocks, and completion status per organization.

**Cardinality**: One record per organization (1:1 with `organizations` table)

### Schema

```sql
CREATE TABLE onboarding_state (
    -- Primary Key
    id VARCHAR(50) PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL UNIQUE,

    -- Wizard Progress
    wizard_completed BOOLEAN DEFAULT FALSE,
    wizard_current_step INTEGER DEFAULT 1,
    wizard_step_data JSON DEFAULT '{}',

    -- Sample Data
    sample_data_generated BOOLEAN DEFAULT FALSE,
    sample_data_generated_at TIMESTAMP,
    sample_data_expiry TIMESTAMP,
    sample_data_cleared BOOLEAN DEFAULT FALSE,

    -- Checklist Progress
    checklist_progress JSON DEFAULT '{}',

    -- Progressive Feature Disclosure
    features_unlocked JSON DEFAULT '[]',
    show_all_features BOOLEAN DEFAULT FALSE,

    -- Onboarding Flow Control
    skipped BOOLEAN DEFAULT FALSE,
    skipped_at TIMESTAMP,

    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_org_wizard_state (organization_id, wizard_completed),
    INDEX idx_sample_data_expiry (sample_data_expiry)
);
```

### Column Definitions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | VARCHAR(50) | NO | auto | Primary key (e.g., `onboard_org_1234567890`) |
| **organization_id** | VARCHAR(50) | NO | - | Foreign key to `organizations.id` |
| **wizard_completed** | BOOLEAN | NO | FALSE | True when user completes all 5 wizard steps |
| **wizard_current_step** | INTEGER | NO | 1 | Current wizard step (1-5) |
| **wizard_step_data** | JSON | NO | {} | Form data for each wizard step |
| **sample_data_generated** | BOOLEAN | NO | FALSE | True if sample data has been generated |
| **sample_data_generated_at** | TIMESTAMP | YES | NULL | When sample data was created |
| **sample_data_expiry** | TIMESTAMP | YES | NULL | When sample data will be auto-deleted (30 days) |
| **sample_data_cleared** | BOOLEAN | NO | FALSE | True if user manually cleared sample data |
| **checklist_progress** | JSON | NO | {} | Map of checklist task IDs to completion status |
| **features_unlocked** | JSON | NO | [] | Array of feature IDs unlocked by milestones |
| **show_all_features** | BOOLEAN | NO | FALSE | True if user toggled "Show all features" |
| **skipped** | BOOLEAN | NO | FALSE | True if user skipped onboarding wizard |
| **skipped_at** | TIMESTAMP | YES | NULL | When user skipped onboarding |
| **started_at** | TIMESTAMP | NO | NOW() | When onboarding was initiated |
| **completed_at** | TIMESTAMP | YES | NULL | When wizard was completed |

### JSON Structure Examples

#### `wizard_step_data`
```json
{
  "step_1": {
    "organization_name": "Grace Community Church",
    "location": "123 Main St, Toronto, ON",
    "timezone": "America/Toronto",
    "completed": true
  },
  "step_2": {
    "event_title": "Sunday Morning Service",
    "event_datetime": "2025-11-01T10:00:00",
    "completed": true
  },
  "step_3": {
    "team_name": "Worship Team",
    "team_role": "Worship Leader",
    "completed": false
  }
}
```

#### `checklist_progress`
```json
{
  "complete_profile": {
    "completed": true,
    "completed_at": "2025-10-23T14:30:00Z"
  },
  "create_first_event": {
    "completed": true,
    "completed_at": "2025-10-23T14:45:00Z"
  },
  "add_team": {
    "completed": false
  },
  "invite_volunteers": {
    "completed": false
  },
  "run_first_schedule": {
    "completed": false
  },
  "view_reports": {
    "completed": false
  }
}
```

#### `features_unlocked`
```json
[
  "recurring_events",
  "manual_editing",
  "sms_notifications"
]
```

### Business Rules

1. **One State Per Organization**: `organization_id` is UNIQUE constraint
2. **Wizard Steps Sequential**: Cannot advance to step N+1 without completing step N
3. **Sample Data Expiry**: Auto-delete after 30 days (`sample_data_expiry`)
4. **Checklist Dynamic**: Progress calculated real-time via database queries
5. **Feature Unlocks**: Triggered by activity milestones (e.g., 5 events created)
6. **Skip Anytime**: User can skip wizard at any step (`skipped = TRUE`)

### Indexes

- `idx_org_wizard_state`: Fast lookup by organization and completion status
- `idx_sample_data_expiry`: Support cleanup job to delete expired sample data

---

## Table: `onboarding_checklist_task`

**Purpose**: Define checklist tasks with completion criteria and quick action URLs.

**Cardinality**: Fixed set of 6 tasks (seed data, not user-created)

### Schema

```sql
CREATE TABLE onboarding_checklist_task (
    -- Primary Key
    id VARCHAR(50) PRIMARY KEY,

    -- Task Details
    title_key VARCHAR(100) NOT NULL,
    description_key VARCHAR(100) NOT NULL,

    -- Completion Detection
    completion_criteria JSON NOT NULL,

    -- Display & Navigation
    priority_order INTEGER NOT NULL,
    icon VARCHAR(50),
    quick_action_url VARCHAR(200),

    -- Active Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_priority_order (priority_order, is_active)
);
```

### Column Definitions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | VARCHAR(50) | NO | - | Task ID (e.g., `complete_profile`, `create_first_event`) |
| **title_key** | VARCHAR(100) | NO | - | i18n key for task title (e.g., `onboarding.checklist.complete_profile`) |
| **description_key** | VARCHAR(100) | NO | - | i18n key for task description |
| **completion_criteria** | JSON | NO | - | SQL query or logic to determine completion |
| **priority_order** | INTEGER | NO | - | Display order (1-6) |
| **icon** | VARCHAR(50) | YES | NULL | Icon name for UI (e.g., `user-circle`, `calendar`) |
| **quick_action_url** | VARCHAR(200) | YES | NULL | URL to complete task (e.g., `/app/events/create`) |
| **is_active** | BOOLEAN | NO | TRUE | False to hide task (feature flag) |
| **created_at** | TIMESTAMP | NO | NOW() | When task was created |

### JSON Structure: `completion_criteria`

```json
{
  "type": "database_query",
  "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE",
  "threshold": 1,
  "operator": ">=",
  "description": "Organization has created at least 1 real event"
}
```

**Supported Types**:
- `database_query`: Execute SQL query, compare result to threshold
- `state_check`: Check `onboarding_state` field value
- `composite_and`: Multiple criteria (all must be true)
- `composite_or`: Multiple criteria (any must be true)

### Seed Data

```sql
INSERT INTO onboarding_checklist_task (id, title_key, description_key, completion_criteria, priority_order, icon, quick_action_url) VALUES
('complete_profile', 'onboarding.checklist.complete_profile', 'onboarding.checklist.complete_profile_desc',
 '{"type": "state_check", "field": "wizard_completed", "value": true}',
 1, 'user-circle', '/app/settings/organization'),

('create_first_event', 'onboarding.checklist.create_first_event', 'onboarding.checklist.create_first_event_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM events WHERE org_id = :org_id AND is_sample = FALSE", "threshold": 1, "operator": ">="}',
 2, 'calendar', '/app/events/create'),

('add_team', 'onboarding.checklist.add_team', 'onboarding.checklist.add_team_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM teams WHERE org_id = :org_id AND is_sample = FALSE", "threshold": 1, "operator": ">="}',
 3, 'users', '/app/teams/create'),

('invite_volunteers', 'onboarding.checklist.invite_volunteers', 'onboarding.checklist.invite_volunteers_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM people WHERE org_id = :org_id AND is_sample = FALSE AND roles LIKE \'%volunteer%\'", "threshold": 3, "operator": ">="}',
 4, 'user-plus', '/app/people/invite'),

('run_first_schedule', 'onboarding.checklist.run_first_schedule', 'onboarding.checklist.run_first_schedule_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM event_assignments WHERE event_id IN (SELECT id FROM events WHERE org_id = :org_id AND is_sample = FALSE)", "threshold": 1, "operator": ">="}',
 5, 'check-circle', '/app/solver'),

('view_reports', 'onboarding.checklist.view_reports', 'onboarding.checklist.view_reports_desc',
 '{"type": "database_query", "query": "SELECT COUNT(*) FROM onboarding_metric WHERE organization_id = :org_id AND event_type = \'view_reports\'", "threshold": 1, "operator": ">="}',
 6, 'bar-chart', '/app/reports');
```

### Business Rules

1. **Fixed Task Set**: 6 tasks defined at system level (not user-editable)
2. **Real-Time Completion**: Queries run on-demand when checklist viewed
3. **Quick Actions**: Each task links to relevant page to complete it
4. **Translatable**: All text via i18n keys supporting 6 languages
5. **Feature Flags**: `is_active` allows hiding tasks per deployment

---

## Table: `onboarding_tutorial_completion`

**Purpose**: Track which tutorials users have viewed, completed, or skipped.

**Cardinality**: One record per (organization, tutorial) pair

### Schema

```sql
CREATE TABLE onboarding_tutorial_completion (
    -- Primary Key
    id VARCHAR(50) PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    tutorial_id VARCHAR(50) NOT NULL,

    -- Completion Status
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    skipped BOOLEAN DEFAULT FALSE,
    skipped_at TIMESTAMP,

    -- Replay Tracking
    replay_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,

    -- Tutorial Progress
    steps_completed INTEGER DEFAULT 0,
    total_steps INTEGER NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,

    -- Constraints
    UNIQUE (organization_id, tutorial_id),

    -- Indexes
    INDEX idx_org_tutorial (organization_id, tutorial_id),
    INDEX idx_completion_status (organization_id, completed)
);
```

### Column Definitions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | VARCHAR(50) | NO | auto | Primary key (e.g., `tutorial_comp_1234567890`) |
| **organization_id** | VARCHAR(50) | NO | - | Foreign key to `organizations.id` |
| **tutorial_id** | VARCHAR(50) | NO | - | Tutorial identifier (e.g., `events_intro`, `solver_basics`) |
| **completed** | BOOLEAN | NO | FALSE | True when user completes all tutorial steps |
| **completed_at** | TIMESTAMP | YES | NULL | When tutorial was completed |
| **skipped** | BOOLEAN | NO | FALSE | True if user clicked "Skip Tutorial" |
| **skipped_at** | TIMESTAMP | YES | NULL | When tutorial was skipped |
| **replay_count** | INTEGER | NO | 0 | Number of times user replayed tutorial |
| **last_viewed_at** | TIMESTAMP | YES | NULL | Most recent tutorial view |
| **steps_completed** | INTEGER | NO | 0 | Number of tutorial steps completed (progress tracking) |
| **total_steps** | INTEGER | NO | - | Total steps in tutorial (varies by tutorial) |
| **created_at** | TIMESTAMP | NO | NOW() | When tutorial was first started |

### Tutorial IDs

**Predefined tutorials** (5 interactive tutorials):

| Tutorial ID | Total Steps | Description |
|-------------|-------------|-------------|
| `events_intro` | 4 | Creating events, setting date/time, roles |
| `teams_setup` | 3 | Creating teams, adding members, roles |
| `availability_management` | 5 | Marking unavailable dates, preferences |
| `solver_run` | 6 | Running solver, understanding constraints, reviewing results |
| `schedule_export` | 3 | Exporting to ICS, calendar integration |

### Business Rules

1. **Tutorial Progress**: Track partial completion via `steps_completed`
2. **Replay Allowed**: Users can replay tutorials anytime (increments `replay_count`)
3. **Skip vs Complete**: Mutually exclusive states
4. **Lazy Creation**: Records created when tutorial first viewed (not pre-seeded)
5. **Organization Scope**: Each org has independent tutorial progress

### Indexes

- `idx_org_tutorial`: Fast lookup for specific tutorial completion status
- `idx_completion_status`: Support queries like "which tutorials are incomplete?"

---

## Table: `onboarding_metric`

**Purpose**: Analytics events for onboarding funnel analysis, A/B testing, and performance monitoring.

**Cardinality**: Multiple events per organization (time-series data)

### Schema

```sql
CREATE TABLE onboarding_metric (
    -- Primary Key
    id VARCHAR(50) PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,

    -- Event Details
    event_type VARCHAR(50) NOT NULL,
    event_data JSON DEFAULT '{}',

    -- Timing
    completion_time_minutes INTEGER,
    step_duration_seconds INTEGER,

    -- Drop-off Tracking
    wizard_step_reached INTEGER,
    wizard_step_dropped INTEGER,

    -- User Context
    user_agent VARCHAR(500),
    session_id VARCHAR(50),

    -- Timestamps
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_org_events (organization_id, event_type),
    INDEX idx_event_timestamp (event_type, timestamp),
    INDEX idx_drop_off (wizard_step_dropped)
);
```

### Column Definitions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | VARCHAR(50) | NO | auto | Primary key (e.g., `metric_1234567890`) |
| **organization_id** | VARCHAR(50) | NO | - | Foreign key to `organizations.id` |
| **event_type** | VARCHAR(50) | NO | - | Event name (e.g., `wizard_started`, `step_completed`) |
| **event_data** | JSON | NO | {} | Custom event properties |
| **completion_time_minutes** | INTEGER | YES | NULL | Time to complete onboarding (for `wizard_completed` event) |
| **step_duration_seconds** | INTEGER | YES | NULL | Time spent on specific wizard step |
| **wizard_step_reached** | INTEGER | YES | NULL | Which wizard step was reached |
| **wizard_step_dropped** | INTEGER | YES | NULL | Which wizard step user abandoned |
| **user_agent** | VARCHAR(500) | YES | NULL | Browser user agent (for device analysis) |
| **session_id** | VARCHAR(50) | YES | NULL | Session ID to group events |
| **timestamp** | TIMESTAMP | NO | NOW() | When event occurred |

### Event Types

| Event Type | Description | Key Fields |
|------------|-------------|------------|
| `wizard_started` | User began onboarding wizard | `event_data.entry_point` |
| `wizard_step_completed` | User completed specific wizard step | `wizard_step_reached`, `step_duration_seconds` |
| `wizard_completed` | User finished entire wizard | `completion_time_minutes` |
| `wizard_skipped` | User clicked "Skip Onboarding" | `wizard_step_dropped` |
| `sample_data_generated` | User generated sample data | `event_data.generation_time_seconds` |
| `sample_data_cleared` | User cleared sample data | `event_data.data_age_days` |
| `tutorial_started` | User started interactive tutorial | `event_data.tutorial_id` |
| `tutorial_completed` | User completed tutorial | `event_data.tutorial_id`, `event_data.duration_seconds` |
| `tutorial_skipped` | User skipped tutorial | `event_data.tutorial_id`, `event_data.step_reached` |
| `feature_unlocked` | Feature unlocked via milestone | `event_data.feature_id`, `event_data.milestone_type` |
| `video_played` | User played quick start video | `event_data.video_id`, `event_data.video_title` |
| `video_completed` | User watched video to end | `event_data.video_id`, `event_data.watch_percentage` |
| `checklist_task_completed` | User completed checklist task | `event_data.task_id` |
| `view_reports` | User viewed reports page | - |

### JSON Structure: `event_data`

#### Example: `wizard_step_completed`
```json
{
  "step_number": 2,
  "step_name": "first_event",
  "entry_point": "signup_flow",
  "validation_errors": 0,
  "field_prefill_count": 3
}
```

#### Example: `sample_data_generated`
```json
{
  "events_created": 5,
  "teams_created": 3,
  "volunteers_created": 15,
  "schedule_generated": true,
  "generation_time_seconds": 2.3
}
```

#### Example: `feature_unlocked`
```json
{
  "feature_id": "recurring_events",
  "milestone_type": "events_created",
  "milestone_threshold": 5,
  "current_count": 7
}
```

### Business Rules

1. **Append-Only**: Metrics are never updated, only inserted (time-series)
2. **Retention**: Keep all metrics indefinitely for trend analysis
3. **Privacy**: No PII stored (org_id is anonymized for analytics)
4. **Session Tracking**: `session_id` groups events within same user session
5. **Funnel Analysis**: Use `wizard_step_dropped` to identify drop-off points

### Indexes

- `idx_org_events`: Fast aggregation of events per organization
- `idx_event_timestamp`: Time-range queries for analytics dashboards
- `idx_drop_off`: Identify common wizard abandonment points

---

## SQLAlchemy ORM Models

### Python Implementation

```python
# api/models.py
from sqlalchemy import Column, String, Boolean, Integer, JSON, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from api.database import Base

class OnboardingState(Base):
    __tablename__ = 'onboarding_state'

    # Primary Key
    id = Column(String(50), primary_key=True)
    organization_id = Column(String(50), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Wizard Progress
    wizard_completed = Column(Boolean, default=False, nullable=False)
    wizard_current_step = Column(Integer, default=1, nullable=False)
    wizard_step_data = Column(JSON, default={}, nullable=False)

    # Sample Data
    sample_data_generated = Column(Boolean, default=False, nullable=False)
    sample_data_generated_at = Column(TIMESTAMP, nullable=True)
    sample_data_expiry = Column(TIMESTAMP, nullable=True)
    sample_data_cleared = Column(Boolean, default=False, nullable=False)

    # Checklist Progress
    checklist_progress = Column(JSON, default={}, nullable=False)

    # Progressive Feature Disclosure
    features_unlocked = Column(JSON, default=[], nullable=False)
    show_all_features = Column(Boolean, default=False, nullable=False)

    # Onboarding Flow Control
    skipped = Column(Boolean, default=False, nullable=False)
    skipped_at = Column(TIMESTAMP, nullable=True)

    # Timestamps
    started_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="onboarding_state")

    # Indexes
    __table_args__ = (
        Index('idx_org_wizard_state', 'organization_id', 'wizard_completed'),
        Index('idx_sample_data_expiry', 'sample_data_expiry'),
    )

    def __init__(self, organization_id: str):
        """Initialize onboarding state for new organization."""
        self.id = f"onboard_{organization_id}_{int(datetime.utcnow().timestamp())}"
        self.organization_id = organization_id
        self.wizard_current_step = 1
        self.wizard_step_data = {}
        self.checklist_progress = {}
        self.features_unlocked = []
        self.started_at = datetime.utcnow()

        # Sample data expires 30 days after generation
        if self.sample_data_generated:
            self.sample_data_expiry = datetime.utcnow() + timedelta(days=30)


class OnboardingChecklistTask(Base):
    __tablename__ = 'onboarding_checklist_task'

    # Primary Key
    id = Column(String(50), primary_key=True)

    # Task Details
    title_key = Column(String(100), nullable=False)
    description_key = Column(String(100), nullable=False)

    # Completion Detection
    completion_criteria = Column(JSON, nullable=False)

    # Display & Navigation
    priority_order = Column(Integer, nullable=False)
    icon = Column(String(50), nullable=True)
    quick_action_url = Column(String(200), nullable=True)

    # Active Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_priority_order', 'priority_order', 'is_active'),
    )


class OnboardingTutorialCompletion(Base):
    __tablename__ = 'onboarding_tutorial_completion'

    # Primary Key
    id = Column(String(50), primary_key=True)
    organization_id = Column(String(50), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    tutorial_id = Column(String(50), nullable=False)

    # Completion Status
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    skipped = Column(Boolean, default=False, nullable=False)
    skipped_at = Column(TIMESTAMP, nullable=True)

    # Replay Tracking
    replay_count = Column(Integer, default=0, nullable=False)
    last_viewed_at = Column(TIMESTAMP, nullable=True)

    # Tutorial Progress
    steps_completed = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="tutorial_completions")

    # Indexes
    __table_args__ = (
        Index('idx_org_tutorial', 'organization_id', 'tutorial_id', unique=True),
        Index('idx_completion_status', 'organization_id', 'completed'),
    )

    def __init__(self, organization_id: str, tutorial_id: str, total_steps: int):
        """Initialize tutorial completion tracking."""
        self.id = f"tutorial_comp_{organization_id}_{tutorial_id}_{int(datetime.utcnow().timestamp())}"
        self.organization_id = organization_id
        self.tutorial_id = tutorial_id
        self.total_steps = total_steps
        self.created_at = datetime.utcnow()


class OnboardingMetric(Base):
    __tablename__ = 'onboarding_metric'

    # Primary Key
    id = Column(String(50), primary_key=True)
    organization_id = Column(String(50), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)

    # Event Details
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, default={}, nullable=False)

    # Timing
    completion_time_minutes = Column(Integer, nullable=True)
    step_duration_seconds = Column(Integer, nullable=True)

    # Drop-off Tracking
    wizard_step_reached = Column(Integer, nullable=True)
    wizard_step_dropped = Column(Integer, nullable=True)

    # User Context
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(50), nullable=True)

    # Timestamps
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="onboarding_metrics")

    # Indexes
    __table_args__ = (
        Index('idx_org_events', 'organization_id', 'event_type'),
        Index('idx_event_timestamp', 'event_type', 'timestamp'),
        Index('idx_drop_off', 'wizard_step_dropped'),
    )

    def __init__(self, organization_id: str, event_type: str, event_data: dict = None):
        """Initialize onboarding metric."""
        self.id = f"metric_{organization_id}_{int(datetime.utcnow().timestamp() * 1000)}"
        self.organization_id = organization_id
        self.event_type = event_type
        self.event_data = event_data or {}
        self.timestamp = datetime.utcnow()
```

---

## Alembic Migration

### Migration Script

```python
"""Add onboarding tables

Revision ID: add_onboarding_tables
Revises: previous_migration
Create Date: 2025-10-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = 'add_onboarding_tables'
down_revision = 'previous_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Create onboarding_state table
    op.create_table(
        'onboarding_state',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('organization_id', sa.String(50), nullable=False, unique=True),
        sa.Column('wizard_completed', sa.Boolean, default=False, nullable=False),
        sa.Column('wizard_current_step', sa.Integer, default=1, nullable=False),
        sa.Column('wizard_step_data', JSON, default={}, nullable=False),
        sa.Column('sample_data_generated', sa.Boolean, default=False, nullable=False),
        sa.Column('sample_data_generated_at', sa.TIMESTAMP, nullable=True),
        sa.Column('sample_data_expiry', sa.TIMESTAMP, nullable=True),
        sa.Column('sample_data_cleared', sa.Boolean, default=False, nullable=False),
        sa.Column('checklist_progress', JSON, default={}, nullable=False),
        sa.Column('features_unlocked', JSON, default=[], nullable=False),
        sa.Column('show_all_features', sa.Boolean, default=False, nullable=False),
        sa.Column('skipped', sa.Boolean, default=False, nullable=False),
        sa.Column('skipped_at', sa.TIMESTAMP, nullable=True),
        sa.Column('started_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP, nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE')
    )

    op.create_index('idx_org_wizard_state', 'onboarding_state', ['organization_id', 'wizard_completed'])
    op.create_index('idx_sample_data_expiry', 'onboarding_state', ['sample_data_expiry'])

    # Create onboarding_checklist_task table
    op.create_table(
        'onboarding_checklist_task',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('title_key', sa.String(100), nullable=False),
        sa.Column('description_key', sa.String(100), nullable=False),
        sa.Column('completion_criteria', JSON, nullable=False),
        sa.Column('priority_order', sa.Integer, nullable=False),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('quick_action_url', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    )

    op.create_index('idx_priority_order', 'onboarding_checklist_task', ['priority_order', 'is_active'])

    # Create onboarding_tutorial_completion table
    op.create_table(
        'onboarding_tutorial_completion',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('organization_id', sa.String(50), nullable=False),
        sa.Column('tutorial_id', sa.String(50), nullable=False),
        sa.Column('completed', sa.Boolean, default=False, nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('skipped', sa.Boolean, default=False, nullable=False),
        sa.Column('skipped_at', sa.TIMESTAMP, nullable=True),
        sa.Column('replay_count', sa.Integer, default=0, nullable=False),
        sa.Column('last_viewed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('steps_completed', sa.Integer, default=0, nullable=False),
        sa.Column('total_steps', sa.Integer, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('organization_id', 'tutorial_id', name='uq_org_tutorial')
    )

    op.create_index('idx_org_tutorial', 'onboarding_tutorial_completion', ['organization_id', 'tutorial_id'])
    op.create_index('idx_completion_status', 'onboarding_tutorial_completion', ['organization_id', 'completed'])

    # Create onboarding_metric table
    op.create_table(
        'onboarding_metric',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('organization_id', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', JSON, default={}, nullable=False),
        sa.Column('completion_time_minutes', sa.Integer, nullable=True),
        sa.Column('step_duration_seconds', sa.Integer, nullable=True),
        sa.Column('wizard_step_reached', sa.Integer, nullable=True),
        sa.Column('wizard_step_dropped', sa.Integer, nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('session_id', sa.String(50), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE')
    )

    op.create_index('idx_org_events', 'onboarding_metric', ['organization_id', 'event_type'])
    op.create_index('idx_event_timestamp', 'onboarding_metric', ['event_type', 'timestamp'])
    op.create_index('idx_drop_off', 'onboarding_metric', ['wizard_step_dropped'])

    # Seed checklist tasks
    op.execute("""
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
         6, 'bar-chart', '/app/reports', true)
    """)


def downgrade():
    op.drop_index('idx_drop_off', 'onboarding_metric')
    op.drop_index('idx_event_timestamp', 'onboarding_metric')
    op.drop_index('idx_org_events', 'onboarding_metric')
    op.drop_table('onboarding_metric')

    op.drop_index('idx_completion_status', 'onboarding_tutorial_completion')
    op.drop_index('idx_org_tutorial', 'onboarding_tutorial_completion')
    op.drop_table('onboarding_tutorial_completion')

    op.drop_index('idx_priority_order', 'onboarding_checklist_task')
    op.drop_table('onboarding_checklist_task')

    op.drop_index('idx_sample_data_expiry', 'onboarding_state')
    op.drop_index('idx_org_wizard_state', 'onboarding_state')
    op.drop_table('onboarding_state')
```

---

## Data Integrity Rules

### Cascade Deletes
- All tables have `ON DELETE CASCADE` for `organization_id`
- When organization deleted, all onboarding state automatically removed

### Unique Constraints
- `onboarding_state.organization_id` - One onboarding state per organization
- `(organization_id, tutorial_id)` - One tutorial completion record per tutorial per org

### Check Constraints (Future Enhancement)
```sql
ALTER TABLE onboarding_state ADD CONSTRAINT chk_wizard_step_range
    CHECK (wizard_current_step BETWEEN 1 AND 5);

ALTER TABLE onboarding_tutorial_completion ADD CONSTRAINT chk_steps_range
    CHECK (steps_completed >= 0 AND steps_completed <= total_steps);

ALTER TABLE onboarding_metric ADD CONSTRAINT chk_positive_duration
    CHECK (step_duration_seconds >= 0 AND completion_time_minutes >= 0);
```

---

## Sample Data Queries

### Get onboarding state with completion percentage
```sql
SELECT
    os.organization_id,
    os.wizard_completed,
    os.wizard_current_step,
    os.sample_data_generated,
    os.features_unlocked,
    (SELECT COUNT(*) FROM json_each(os.checklist_progress) WHERE value->>'completed' = 'true') AS tasks_completed,
    6 AS total_tasks,
    ROUND((SELECT COUNT(*) FROM json_each(os.checklist_progress) WHERE value->>'completed' = 'true') * 100.0 / 6, 1) AS completion_percent
FROM onboarding_state os
WHERE os.organization_id = 'org_123';
```

### Get organizations with incomplete onboarding
```sql
SELECT
    o.id,
    o.name,
    os.wizard_current_step,
    os.started_at,
    EXTRACT(EPOCH FROM (NOW() - os.started_at)) / 3600 AS hours_since_start
FROM organizations o
JOIN onboarding_state os ON os.organization_id = o.id
WHERE os.wizard_completed = FALSE
  AND os.skipped = FALSE
ORDER BY os.started_at DESC;
```

### Get wizard drop-off funnel
```sql
SELECT
    wizard_step_dropped AS step,
    COUNT(*) AS drop_off_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM onboarding_metric WHERE event_type = 'wizard_started'), 2) AS drop_off_percent
FROM onboarding_metric
WHERE wizard_step_dropped IS NOT NULL
GROUP BY wizard_step_dropped
ORDER BY wizard_step_dropped;
```

### Get average completion time
```sql
SELECT
    AVG(completion_time_minutes) AS avg_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_time_minutes) AS median_minutes,
    MIN(completion_time_minutes) AS fastest_minutes,
    MAX(completion_time_minutes) AS slowest_minutes
FROM onboarding_metric
WHERE event_type = 'wizard_completed';
```

---

## Testing Requirements

### Unit Tests
- [ ] Test `OnboardingState.__init__()` creates valid record
- [ ] Test wizard step validation logic
- [ ] Test sample data expiry calculation (30 days)
- [ ] Test checklist progress JSON serialization
- [ ] Test feature unlock array manipulation

### Integration Tests
- [ ] Test creating onboarding state on organization signup
- [ ] Test advancing wizard steps with validation
- [ ] Test generating and clearing sample data
- [ ] Test checklist completion detection queries
- [ ] Test tutorial replay tracking
- [ ] Test analytics event recording

### Database Tests
- [ ] Test `organization_id` UNIQUE constraint
- [ ] Test CASCADE delete when organization removed
- [ ] Test checklist task seed data inserted correctly
- [ ] Test indexes improve query performance (EXPLAIN ANALYZE)

---

## Performance Considerations

### Query Optimization
- Indexes on `organization_id` for fast org-scoped queries
- Composite index on `(organization_id, wizard_completed)` for dashboard queries
- `sample_data_expiry` index supports cleanup cron job

### JSON Column Best Practices
- Keep JSON columns small (<10KB) for indexing efficiency
- Use PostgreSQL JSONB type for faster queries
- Consider migrating frequently queried JSON fields to regular columns if performance issues

### Analytics Scaling
- `onboarding_metric` table will grow large (time-series data)
- Consider partitioning by `timestamp` (monthly) after 1M+ records
- Archive metrics older than 12 months to separate table

---

## Security & Privacy

### Data Access Rules
- Onboarding state visible only to organization admins
- Analytics aggregated across organizations (no cross-org data leaks)
- Tutorial completions private to organization

### PII Handling
- No personally identifiable information stored in `onboarding_metric`
- User agent strings truncated to avoid fingerprinting
- Session IDs randomized and not linked to user accounts

### GDPR Compliance
- All onboarding data deleted when organization account deleted (`ON DELETE CASCADE`)
- Analytics anonymized for reporting
- User can request data export via organization data export feature

---

**Time to Complete**: Data model design
**Last Updated**: 2025-10-23
**Feature**: 020 - User Onboarding System
