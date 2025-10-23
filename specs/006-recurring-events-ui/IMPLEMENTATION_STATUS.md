# Recurring Events UI - Implementation Status

**Feature**: 006-recurring-events-ui
**Started**: 2025-10-22
**Status**: 🚧 IN PROGRESS
**Priority**: P0 CRITICAL (TOP PRIORITY - blocking MVP adoption)

---

## 📋 Quick Status

| Component | Status | Progress | Notes |
|-----------|--------|----------|-------|
| **Specification** | ✅ Complete | 100% | spec.md reviewed |
| **Technical Plan** | ✅ Complete | 100% | plan.md reviewed |
| **Data Model** | ⏳ Not Started | 0% | Need to define DB tables |
| **Backend API** | ⏳ Not Started | 0% | Need recurring_events.py router |
| **Recurrence Generator** | ⏳ Not Started | 0% | Need recurrence_generator.py service |
| **Frontend UI** | ⏳ Not Started | 0% | Need recurring-events-ui.js |
| **Calendar Preview** | ⏳ Not Started | 0% | Need calendar-preview.js |
| **E2E Tests** | 🚧 In Progress | 40% | 5 tests written for US1-US2 |
| **Integration Tests** | ⏳ Not Started | 0% | API endpoint tests |
| **Unit Tests** | ⏳ Not Started | 0% | Recurrence logic tests |

**Overall Progress**: 30% (spec + plan + E2E tests for US1-US2 complete)

---

## 🎯 Implementation Phases

### Phase 1: Foundation (Current Phase)
**Goal**: Understand requirements, create data model, set up tests

- [x] Read and analyze spec.md
- [x] Read and analyze plan.md
- [ ] Design database schema (RecurringSeries, RecurrencePattern, EventOccurrence, RecurrenceException)
- [ ] Write E2E test for User Story 1 (Create Weekly Recurring Events) - **MANDATORY FIRST**
- [ ] Create implementation checklist

**Status**: 🚧 IN PROGRESS
**Started**: 2025-10-22
**Estimated Completion**: 2025-10-22

### Phase 2: Core Backend (Next)
**Goal**: Implement recurrence pattern generation and API endpoints

- [ ] Implement RecurringSeries and related models in api/models.py
- [ ] Create database migration for new tables
- [ ] Implement recurrence_generator.py service (weekly, biweekly, monthly patterns)
- [ ] Implement recurring_events.py API router (CRUD operations)
- [ ] Write unit tests for recurrence generation logic
- [ ] Write integration tests for API endpoints

**Status**: ⏳ Not Started
**Estimated Duration**: 2-3 days

### Phase 3: Frontend UI (After Backend)
**Goal**: Build user interface for creating/managing recurring events

- [ ] Implement recurring-events-ui.js (pattern selection, form handling)
- [ ] Implement calendar-preview.js (visual date highlighting)
- [ ] Add recurring event UI to frontend/index.html
- [ ] Integrate with existing event management interface
- [ ] Add i18n translations for all UI text

**Status**: ⏳ Not Started
**Estimated Duration**: 2-3 days

### Phase 4: Advanced Features (After Core)
**Goal**: Single occurrence editing, bulk editing, holiday handling

- [ ] Implement RecurrenceException model and API
- [ ] Implement "Edit this occurrence" vs "Edit entire series" logic
- [ ] Implement bulk series editing
- [ ] Implement HolidayCalendar model and API
- [ ] Add holiday conflict detection
- [ ] Add natural language pattern descriptions

**Status**: ⏳ Not Started
**Estimated Duration**: 2-3 days

### Phase 5: Testing & Polish (Final)
**Goal**: Comprehensive testing, manual verification, documentation

- [ ] Run full E2E test suite
- [ ] Manual testing of all user stories
- [ ] Performance testing (100+ occurrence series)
- [ ] Edge case testing (DST, leap years, month boundaries)
- [ ] Update documentation
- [ ] Create user guide

**Status**: ⏳ Not Started
**Estimated Duration**: 1-2 days

---

## 📊 User Story Implementation Status

### User Story 1: Create Weekly Recurring Events (P1)
**Status**: 🧪 Tests Written (implementation pending)
**Test Status**: ✅ E2E tests written (tests/e2e/test_recurring_events_ui.py)

**Acceptance Criteria Checklist**:
- [ ] AC1: Generate 12-13 Sunday events for 3-month range
- [ ] AC2: Regenerate series when end date changes
- [ ] AC3: Calendar displays all occurrences with series indicator
- [ ] AC4: Series title updates affect all future occurrences
- [ ] AC5: Scheduling solver assigns volunteers to all occurrences

**Implementation Notes**: Start here - this is the MVP feature.

### User Story 2: Edit Single Occurrence vs Entire Series (P1)
**Status**: 🧪 Tests Written (implementation pending)
**Test Status**: ✅ E2E tests written (tests/e2e/test_recurring_events_ui.py)

**Acceptance Criteria Checklist**:
- [ ] AC1: Display "Edit this occurrence only" or "Edit entire series" dialog
- [ ] AC2: Single occurrence edit creates exception
- [ ] AC3: Series edit updates all future occurrences
- [ ] AC4: Exception occurrences show indicator
- [ ] AC5: Solver skips canceled occurrences

**Implementation Notes**: Requires RecurrenceException model.

### User Story 3: Visual Calendar Preview (P1)
**Status**: ⏳ Not Started
**Test Status**: ⏳ E2E test not written yet

**Acceptance Criteria Checklist**:
- [ ] AC1: Calendar preview highlights occurrence dates
- [ ] AC2: Preview allows scrolling through months
- [ ] AC3: Preview displays warning for 50+ occurrences
- [ ] AC4: Preview updates in real-time (<1s refresh)
- [ ] AC5: Hover tooltip shows occurrence details

**Implementation Notes**: May need FullCalendar.js or custom component.

### User Story 4: Monthly Recurrence Patterns (P2)
**Status**: ⏳ Not Started
**Test Status**: ⏳ E2E test not written yet

**Acceptance Criteria Checklist**:
- [ ] AC1: "2nd Sunday of every month" generates correctly
- [ ] AC2: "15th of every month" handles February correctly
- [ ] AC3: "Last Friday of every month" handles variable month lengths
- [ ] AC4: Year calendar displays 12 monthly occurrences
- [ ] AC5: Monthly pattern supports exception handling

**Implementation Notes**: Complex date logic - use python-dateutil.

### User Story 5: Biweekly and Custom Intervals (P2)
**Status**: ⏳ Not Started
**Test Status**: ⏳ E2E test not written yet

**Acceptance Criteria Checklist**:
- [ ] AC1: Biweekly generates occurrences exactly 14 days apart
- [ ] AC2: Custom interval (every N weeks) validates and generates
- [ ] AC3: Exceptions don't shift subsequent interval timing
- [ ] AC4: Calendar preview shows interval spacing
- [ ] AC5: Pattern description shows interval clearly

**Implementation Notes**: Interval tracking must be precise.

### User Story 6: Bulk Editing Recurring Series (P2)
**Status**: ⏳ Not Started
**Test Status**: ⏳ E2E test not written yet

**Acceptance Criteria Checklist**:
- [ ] AC1: Bulk edit updates all future non-exception occurrences
- [ ] AC2: Role requirement changes apply to all future occurrences
- [ ] AC3: Exceptions retain custom properties during bulk edit
- [ ] AC4: Confirmation shows count of updated occurrences
- [ ] AC5: Warning displayed when assignments exist

**Implementation Notes**: Backend-heavy - batch update logic.

### User Story 7: Holiday Exception Handling (P3)
**Status**: ⏳ Not Started
**Test Status**: ⏳ E2E test not written yet

**Acceptance Criteria Checklist**:
- [ ] AC1: Holiday calendar configuration working
- [ ] AC2: Series generation detects holiday conflicts
- [ ] AC3: Holiday occurrences show warning indicator
- [ ] AC4: Calendar preview highlights holiday conflicts
- [ ] AC5: Bulk holiday conflict resolution available

**Implementation Notes**: Lowest priority - can defer if needed.

---

## 🗄️ Database Schema Design

### Tables to Create

#### `recurring_series` (new table)
```sql
CREATE TABLE recurring_series (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR NOT NULL REFERENCES organizations(id),
    created_by VARCHAR NOT NULL REFERENCES people(id),

    -- Event template (inherited by occurrences)
    title VARCHAR NOT NULL,
    duration INTEGER NOT NULL,  -- minutes
    location VARCHAR,
    role_requirements JSON,  -- {"greeter": 2, "usher": 3}

    -- Recurrence pattern
    pattern_type VARCHAR NOT NULL,  -- 'weekly', 'biweekly', 'monthly', 'custom'
    frequency_interval INTEGER,  -- for custom patterns (every N days/weeks)
    selected_days JSON,  -- for weekly patterns: ["sunday", "wednesday"]
    weekday_position VARCHAR,  -- for monthly: "2nd", "last"
    weekday_name VARCHAR,  -- for monthly: "sunday", "friday"

    -- Series duration
    start_date DATE NOT NULL,
    end_condition_type VARCHAR NOT NULL,  -- 'date', 'count', 'indefinite'
    end_date DATE,
    occurrence_count INTEGER,

    -- Status
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES people(id) ON DELETE SET NULL
);
```

#### `event_occurrences` (modify existing `events` table)
```sql
-- Add columns to existing events table:
ALTER TABLE events ADD COLUMN series_id VARCHAR REFERENCES recurring_series(id) ON DELETE SET NULL;
ALTER TABLE events ADD COLUMN occurrence_sequence INTEGER;  -- 1st, 2nd, 3rd in series
ALTER TABLE events ADD COLUMN is_exception BOOLEAN DEFAULT FALSE;
```

#### `recurrence_exceptions` (new table)
```sql
CREATE TABLE recurrence_exceptions (
    id VARCHAR PRIMARY KEY,
    occurrence_id VARCHAR NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    series_id VARCHAR NOT NULL REFERENCES recurring_series(id) ON DELETE CASCADE,

    exception_type VARCHAR NOT NULL,  -- 'edited', 'canceled', 'holiday_conflict'

    -- Original values (from template)
    original_title VARCHAR,
    original_datetime TIMESTAMP,
    original_duration INTEGER,
    original_role_requirements JSON,

    -- Custom values (user changes)
    custom_title VARCHAR,
    custom_datetime TIMESTAMP,
    custom_duration INTEGER,
    custom_role_requirements JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR REFERENCES people(id) ON DELETE SET NULL,

    UNIQUE (occurrence_id)  -- One exception per occurrence
);
```

#### `holiday_calendar` (new table)
```sql
CREATE TABLE holiday_calendar (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    holiday_name VARCHAR NOT NULL,
    holiday_date DATE NOT NULL,
    recurring_annually BOOLEAN DEFAULT TRUE,

    -- Conflict handling policy
    conflict_policy VARCHAR DEFAULT 'flag',  -- 'skip', 'flag', 'auto_reschedule'

    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);
```

**Status**: ⏳ Schema designed, not implemented yet

---

## 🔧 Technical Decisions

### Decision 1: Use python-dateutil for Recurrence Rules
**Date**: 2025-10-22
**Context**: Need robust recurrence pattern generation (weekly, monthly, custom)
**Decision**: Use python-dateutil library (RFC 5545 subset support)
**Rationale**:
- Mature library, well-tested
- Handles DST, leap years, month boundaries automatically
- Supports complex patterns (2nd Sunday, last Friday)
**Alternatives Considered**: Custom implementation (too error-prone), croniter (cron-focused)

### Decision 2: Store Occurrences as Individual Events
**Date**: 2025-10-22
**Context**: How to store recurring event occurrences
**Decision**: Generate actual Event rows for each occurrence, link via series_id
**Rationale**:
- Existing scheduling solver treats events independently
- Volunteer assignments already per-event
- Calendar views work without changes
- Exceptions become event-level modifications
**Alternatives Considered**: Virtual occurrences (complex queries), hybrid approach

### Decision 3: Calendar Preview Component
**Date**: 2025-10-22
**Context**: Need visual calendar preview for recurrence patterns
**Decision**: DEFER - evaluate FullCalendar.js vs custom component during implementation
**Rationale**: Need to test integration with existing UI first
**Options**:
- FullCalendar.js (feature-rich, 50KB)
- Custom component (lightweight, tailored)
- HTML date inputs with highlighting (simplest)

### Decision 4: Past Occurrence Editing
**Date**: 2025-10-22
**Context**: Allow editing past occurrences?
**Decision**: NO - past occurrences read-only (historical data preservation)
**Rationale**:
- Preserves volunteer assignment history
- Prevents retroactive schedule changes
- Matches organizational compliance needs
**Implementation**: Edit dialog checks if occurrence_date < today, shows read-only message

### Decision 5: Maximum Series Duration
**Date**: 2025-10-22
**Context**: Limit on recurring series length
**Decision**: 2 years maximum (730 days, ~104 weeks, ~24 months)
**Rationale**:
- Organizations review schedules annually
- Prevents runaway generation (user error)
- Can extend series as end date approaches
**Implementation**: Backend validation + frontend warning

---

## 🧪 Testing Strategy

### E2E Tests (MANDATORY - Write First)
**File**: `tests/e2e/test_recurring_events_ui.py`

**Test Plan**:
1. ✅ `test_create_weekly_recurring_event_complete_workflow` - US1 complete flow (WRITTEN)
2. ✅ `test_calendar_preview_updates_realtime` - US3 real-time preview updates (WRITTEN)
3. ✅ `test_preview_warns_on_large_series` - US3 warning for 50+ occurrences (WRITTEN)
4. ✅ `test_edit_single_occurrence_creates_exception` - US2 exception handling (WRITTEN)
5. ✅ `test_edit_entire_series_updates_all_future` - US2 bulk series edit (WRITTEN)
6. ⏳ `test_monthly_pattern_generates_correctly` - US4 monthly recurrence (TODO)
7. ⏳ `test_biweekly_pattern_maintains_interval` - US5 biweekly interval (TODO)

**Current Status**: ✅ 5/7 tests written - Tests will FAIL until implementation complete (expected per TDD)

### Integration Tests
**File**: `tests/integration/test_recurring_events_api.py`

**Test Plan**:
- API: POST /api/recurring-series (create series)
- API: GET /api/recurring-series/{id} (get series details)
- API: PUT /api/recurring-series/{id} (update series template)
- API: DELETE /api/recurring-series/{id} (delete series)
- API: GET /api/recurring-series/{id}/occurrences (list occurrences)
- API: PUT /api/events/{id}?edit_mode=occurrence (edit single)
- API: PUT /api/events/{id}?edit_mode=series (edit series)

**Current Status**: ⏳ Not written yet

### Unit Tests
**File**: `tests/unit/test_recurrence_generator.py`

**Test Plan**:
- Weekly pattern generation (all days)
- Biweekly pattern (exact 14-day interval)
- Monthly pattern (2nd Sunday, last Friday, 15th)
- Custom interval pattern
- DST handling (time consistency)
- Leap year handling (Feb 29)
- Edge cases (5th Sunday when no 5th Sunday)

**Current Status**: ⏳ Not written yet

---

## 📝 Implementation Checklist

### PHASE 1: Foundation ✅ Current Phase
- [x] Read spec.md (299 lines - comprehensive)
- [x] Read plan.md (86 lines - technical approach)
- [x] Create IMPLEMENTATION_STATUS.md (this file)
- [ ] Design database schema (4 tables defined above)
- [ ] Write E2E test for US1 - **NEXT STEP**
- [ ] Create database migration script
- [ ] Add python-dateutil to pyproject.toml

### PHASE 2: Backend Core
- [ ] Implement RecurringSeries model in api/models.py
- [ ] Implement RecurrenceException model in api/models.py
- [ ] Implement HolidayCalendar model in api/models.py
- [ ] Modify Event model (add series_id, is_exception columns)
- [ ] Create api/services/recurrence_generator.py
  - [ ] generate_weekly_occurrences()
  - [ ] generate_biweekly_occurrences()
  - [ ] generate_monthly_occurrences()
  - [ ] generate_custom_interval_occurrences()
  - [ ] detect_holiday_conflicts()
- [ ] Create api/services/recurrence_validator.py
  - [ ] validate_pattern()
  - [ ] validate_end_condition()
  - [ ] validate_series_duration()
- [ ] Create api/routers/recurring_events.py
  - [ ] POST /api/recurring-series (create)
  - [ ] GET /api/recurring-series (list)
  - [ ] GET /api/recurring-series/{id} (get)
  - [ ] PUT /api/recurring-series/{id} (update template)
  - [ ] DELETE /api/recurring-series/{id} (delete)
  - [ ] GET /api/recurring-series/{id}/occurrences (list occurrences)
  - [ ] GET /api/recurring-series/preview (preview without saving)
- [ ] Modify api/routers/events.py
  - [ ] Add edit_mode parameter (occurrence vs series)
  - [ ] Implement exception creation logic
- [ ] Write 20+ unit tests for recurrence_generator.py
- [ ] Write 15+ integration tests for recurring_events API

### PHASE 3: Frontend UI
- [ ] Create frontend/js/recurring-events-ui.js
  - [ ] Pattern selection interface (weekly, biweekly, monthly, custom)
  - [ ] Day selection checkboxes (for weekly)
  - [ ] Interval input (for custom)
  - [ ] End condition selection (date, count, indefinite)
  - [ ] Form validation
  - [ ] API integration (create/update series)
- [ ] Create frontend/js/calendar-preview.js
  - [ ] Calendar grid component (month view)
  - [ ] Date highlighting for occurrences
  - [ ] Navigation controls (prev/next month)
  - [ ] Hover tooltips
  - [ ] Real-time preview update (<1s)
- [ ] Update frontend/index.html
  - [ ] Add recurring event form section
  - [ ] Add calendar preview container
  - [ ] Add "Edit this occurrence" vs "Edit series" dialog
- [ ] Update frontend/js/app-admin.js
  - [ ] Integrate recurring event creation
  - [ ] Handle series vs occurrence editing
  - [ ] Display series indicator in event lists
- [ ] Add i18n translations
  - [ ] locales/en/recurring.json (new file)
  - [ ] locales/es/recurring.json
  - [ ] locales/pt/recurring.json
  - [ ] locales/zh-CN/recurring.json
  - [ ] locales/zh-TW/recurring.json

### PHASE 4: Advanced Features
- [ ] Implement single occurrence editing
  - [ ] Backend: Create RecurrenceException on single edit
  - [ ] Frontend: "Edit this occurrence only" dialog
  - [ ] Display exception indicator in UI
- [ ] Implement bulk series editing
  - [ ] Backend: Update series template + all non-exception occurrences
  - [ ] Frontend: "Edit entire series" dialog
  - [ ] Display confirmation with occurrence count
- [ ] Implement holiday conflict detection
  - [ ] Backend: detect_holiday_conflicts() in generator
  - [ ] Frontend: Holiday calendar configuration UI
  - [ ] Display holiday warnings in preview
- [ ] Add natural language pattern descriptions
  - [ ] Backend: generate_pattern_description()
  - [ ] Frontend: Display "Every Sunday until Dec 31, 2025"

### PHASE 5: Testing & Polish
- [ ] Run full E2E test suite (6+ tests)
- [ ] Run integration test suite (15+ tests)
- [ ] Run unit test suite (20+ tests)
- [ ] Manual testing checklist:
  - [ ] Create weekly recurring event (Sunday service)
  - [ ] View calendar preview (verify dates)
  - [ ] Edit single occurrence (create exception)
  - [ ] Edit entire series (bulk update)
  - [ ] Delete occurrence (verify exception)
  - [ ] Create monthly pattern (2nd Sunday)
  - [ ] Create biweekly pattern (every 2 weeks)
  - [ ] Test with 100+ occurrences (performance)
  - [ ] Test DST boundary (March/November)
  - [ ] Test leap year (Feb 29)
- [ ] Performance testing
  - [ ] Calendar preview <1s for 100 occurrences
  - [ ] Series generation <5s for 365 occurrences
  - [ ] Bulk edit <3s for 100+ occurrences
- [ ] Update documentation
  - [ ] docs/RECURRING_EVENTS_GUIDE.md (user guide)
  - [ ] Update docs/API.md (new endpoints)
  - [ ] Update CLAUDE.md (mention recurring events)

---

## 🚀 Next Steps

### Immediate (Today 2025-10-22)
1. ✅ Read spec.md and plan.md
2. ✅ Create IMPLEMENTATION_STATUS.md
3. **NEXT**: Write E2E test for User Story 1 (Create Weekly Recurring Events)
   - File: `tests/e2e/test_recurring_events_ui.py`
   - Test: `test_create_weekly_recurring_event_workflow()`
   - Scenario: Admin creates "Every Sunday" pattern, views calendar preview, saves series
   - Expected: Calendar shows 12-13 Sunday occurrences

### This Week
4. Implement database schema + migration
5. Implement recurrence_generator.py service
6. Implement recurring_events.py API router
7. Run E2E test (should pass after backend complete)

### Next Week
8. Implement frontend UI (recurring-events-ui.js)
9. Implement calendar preview (calendar-preview.js)
10. Manual testing and refinement

---

## 📚 Key References

- **Specification**: [spec.md](./spec.md) - 299 lines, 7 user stories
- **Technical Plan**: [plan.md](./plan.md) - 86 lines, architecture
- **CLAUDE.md**: `/home/ubuntu/SignUpFlow/CLAUDE.md` - Mandatory E2E testing workflow
- **Constitution**: `/home/ubuntu/SignUpFlow/.specify/memory/constitution.md` - Development principles
- **Existing Event Model**: `api/models.py` line ~150 - Event class
- **Existing Event Router**: `api/routers/events.py` - Event CRUD operations

---

## 🔄 Session Resumption Guide

**To resume work on this feature:**

1. Read this file (`IMPLEMENTATION_STATUS.md`) - current progress
2. Check "Next Steps" section above
3. Review todo list for current phase
4. Follow CLAUDE.md mandatory workflow (E2E test first!)
5. Update this file after each phase completion

**Current Phase**: PHASE 1 - Foundation
**Next Task**: Write E2E test for User Story 1
**Blockers**: None
**Estimated Time to MVP**: 5-7 days (US1-US3 only)

---

**Last Updated**: 2025-10-22 (Initial creation)
**Updated By**: Claude Code
**Next Update**: After E2E test written
