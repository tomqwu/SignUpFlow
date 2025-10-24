# Implementation Plan: Recurring Events User Interface

**Branch**: `016-recurring-events-ui` | **Date**: 2025-10-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-recurring-events-ui/spec.md`

## Summary

Enable administrators to create and manage repeating event patterns through intuitive UI with visual calendar preview, eliminating manual creation of 52+ individual events (reduces 45 minutes to 5 minutes, 90% time savings). Supports weekly/biweekly/monthly patterns, exception handling for holidays, single vs series editing, and bulk operations.

**Technical Approach**:
- **Frontend**: Vanilla JavaScript calendar widget with RFC 5545 recurrence rule generation
- **Backend**: Python dateutil.rrule for recurrence calculation, PostgreSQL JSONB for pattern storage
- **UI Pattern**: Progressive disclosure (simple patterns first, advanced options expandable)
- **Performance**: Pre-generate occurrences (not calculated on-demand) for sub-3s creation time

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript ES6+ (frontend)

**Primary Dependencies**:
- **python-dateutil 2.8+**: RFC 5545 recurrence rule calculation (rrule, rruleset)
- **FullCalendar 6.1+** OR **DayPilot Lite**: Visual calendar preview widget (lightweight, no jQuery)
- **date-fns 2.30+**: Frontend date manipulation (ISO parsing, formatting)
- **FastAPI Pydantic**: Request validation for recurrence patterns

**Database**:
- **PostgreSQL**: Existing SignUpFlow database
  - New table: `recurring_series` (series metadata, recurrence rule as JSONB)
  - New table: `recurrence_exceptions` (skipped/modified dates)
  - Extend `events` table: Add `series_id`, `sequence_number`, `is_exception` columns
- **Storage estimate**: ~10KB per series (pattern + 104 occurrences metadata)

**Testing**:
- **pytest 7.4+**: Backend unit tests for recurrence calculation
- **Playwright 1.40+**: E2E tests for calendar UI interactions
- **Hypothesis 6.92+**: Property-based testing for edge cases (month-end, DST, leap years)

**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+)
**Project Type**: Web (FastAPI backend + Vanilla JS frontend SPA)

**Performance Goals**:
- Generate 104 occurrences: <3 seconds (target 1s)
- Calendar preview render: <1 second after pattern change
- Bulk edit 50 occurrences: <5 seconds
- Database query for series + occurrences: <500ms

**Constraints**:
- **Maximum occurrences**: 104 (2 years) to prevent abuse and performance issues
- **No external calendar sync**: Manual creation only (Google Calendar import is future feature)
- **Single timezone**: All occurrences use organization timezone (no per-occurrence timezone)
- **Vanilla JavaScript**: No React/Vue/Angular - maintain existing architecture

**Scale/Scope**:
- Expected recurring series: ~50 per organization (weekly services, monthly meetings)
- Occurrences per series: Average 52 (1 year), maximum 104 (2 years)
- Concurrent administrators: 5-10 creating series simultaneously

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle 1: User-First Testing (E2E MANDATORY)

**Compliance Status**: ✅ **PASS**

**Justification**:
- E2E tests required for all 7 user stories (create pattern, preview calendar, edit series/occurrence, exceptions, bulk edit)
- E2E test scenario: Create weekly Sunday service series → verify calendar preview shows 52 Sundays → verify all events created
- E2E test scenario: Edit single occurrence time → verify only that occurrence changed, rest unchanged
- E2E test scenario: Add Christmas Day exception → verify that date skipped in calendar

**Verification**:
- User Story 1: Create recurring pattern → E2E test with Playwright calendar interaction
- User Story 2: Visual preview → E2E test verifies preview updates within 1s after pattern change
- User Story 3: Edit single vs series → E2E test ensures correct scope isolation

### Principle 2: Security-First Development

**Compliance Status**: ✅ **PASS**

**Justification**:
- All recurring event endpoints require JWT authentication (`Depends(verify_admin_access)`)
- RBAC enforcement: Only admins can create/edit recurring series (volunteers read-only)
- Multi-tenant isolation: All series filtered by `org_id` in database queries
- No cross-organization access: `verify_org_member()` check in all endpoints
- Audit logging: Track who created/modified recurring series

**Verification**:
- POST /api/recurring-series requires admin role (403 for volunteers)
- GET /api/events/?series_id=X filters by current user's org_id
- E2E security test: Verify volunteer cannot create recurring series

### Principle 3: Multi-tenant Isolation

**Compliance Status**: ✅ **PASS**

**Justification**:
- Recurring series table includes `org_id` column with foreign key to organizations
- All queries filter by `org_id`: `db.query(RecurringSeries).filter(RecurringSeries.org_id == org_id)`
- Generated event occurrences inherit `org_id` from parent series
- Calendar preview only shows occurrences for current organization

**Verification**:
- RecurringSeries entity has `org_id` field (spec line 238)
- Event occurrence inherits `org_id` from series
- API endpoints require `org_id` query parameter

### Principle 4: Test Coverage Excellence

**Compliance Status**: ✅ **PASS**

**Justification**:
- Unit tests: Recurrence calculation (weekly, biweekly, monthly, edge cases)
- Integration tests: API endpoints (create series, generate occurrences, bulk edit)
- E2E tests: Full user workflows (create pattern, preview, edit, exceptions)
- Property-based tests: Edge cases (month-end, DST transitions, leap years)

**Test Types Required**:
1. **Unit Tests** (~30 tests):
   - Recurrence rule calculation (52 weekly occurrences from pattern)
   - Month-end handling (31st → last day of month)
   - Exception application (skip dates, modify dates)
   - Natural language summary generation

2. **Integration Tests** (~20 tests):
   - POST /api/recurring-series creates series + generates occurrences
   - PUT /api/events/{id}?scope=series updates all occurrences
   - POST /api/recurring-series/{id}/exceptions skips occurrence
   - DELETE /api/recurring-series/{id} removes series + all occurrences

3. **E2E Tests** (~15 tests):
   - Create weekly pattern, verify calendar preview, submit, verify events created
   - Edit single occurrence time, verify isolation from series
   - Add holiday exception, verify occurrence skipped
   - Bulk select 10 occurrences, edit role requirements, verify changes
   - Complex pattern (first Sunday of month), verify correct dates

**Target Coverage**: 90% code coverage for recurrence logic

### Principle 5: Internationalization by Default

**Compliance Status**: ✅ **PASS**

**Justification**:
- Recurrence UI text uses i18n keys (en, es, pt, zh-CN, zh-TW, fr)
- Natural language summaries translated: "Weekly on Sunday" → "Semanal los domingos" (es)
- Calendar preview labels translated: "Occurrence", "Exception", "Modified"
- Date formatting respects locale: Sunday → Domingo (es), 星期日 (zh)

**i18n Scope**:
- ✅ Recurrence pattern labels: "Weekly", "Biweekly", "Monthly"
- ✅ Calendar preview UI: Day names, month names
- ✅ Natural language summaries: "Every 2 weeks on Wednesday"
- ✅ Error messages: "Maximum 104 occurrences exceeded"

### Principle 6: Code Quality Standards

**Compliance Status**: ✅ **PASS**

**Justification**:
- Type hints for recurrence functions: `def generate_occurrences(rule: RecurrenceRule) -> List[datetime]`
- Docstrings for public APIs: recurrence calculation, exception handling
- Error handling: RecurrenceRuleError, InvalidPatternError with user-friendly messages
- Validation: Pydantic schemas for recurrence patterns (frequency, interval, days_of_week)
- Configuration: Environment variables for max occurrences limit

### Principle 7: Clear Documentation

**Compliance Status**: ✅ **PASS**

**Justification**:
- User documentation: Recurring Events Guide, pattern examples, exception handling
- Technical documentation: RFC 5545 recurrence rule mapping, database schema
- Inline comments: Complex recurrence calculation logic, edge case handling
- API documentation: OpenAPI spec for recurring series endpoints

**Required Documentation**:
- Recurring Events User Guide (how to create patterns, handle exceptions)
- Recurrence Rule Technical Reference (RFC 5545 mapping)
- Calendar Widget Integration Guide (FullCalendar setup)

**Constitution Compliance**: ✅ **ALL GATES PASS** - No violations, proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```
specs/016-recurring-events-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── recurring-series-api.md      # POST/GET/PUT/DELETE /api/recurring-series
│   ├── recurrence-exceptions-api.md # POST/DELETE /api/recurring-series/{id}/exceptions
│   ├── bulk-edit-api.md             # POST /api/events/bulk-edit
│   └── calendar-preview-api.md      # GET /api/recurring-series/preview
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```
api/
├── models.py                        # Add: RecurringSeries, RecurrenceException entities
├── schemas/
│   └── recurrence.py                # Pydantic: RecurrenceRuleCreate, ExceptionCreate
├── routers/
│   └── recurring_events.py          # API endpoints for recurring series
├── services/
│   ├── recurrence_service.py        # Recurrence calculation (dateutil.rrule)
│   └── bulk_edit_service.py         # Bulk operations on occurrences
└── utils/
    └── recurrence_utils.py          # Natural language summary, RFC 5545 parsing

frontend/
├── js/
│   ├── recurring-events.js          # Recurrence pattern UI controller
│   ├── calendar-preview.js          # FullCalendar integration
│   └── bulk-edit.js                 # Multi-select and bulk edit UI
└── css/
    └── recurring-events.css         # Recurrence UI styling

tests/
├── unit/
│   ├── test_recurrence_service.py   # Recurrence calculation tests
│   └── test_recurrence_utils.py     # Natural language summary tests
├── integration/
│   ├── test_recurring_series_api.py # API endpoint tests
│   └── test_bulk_edit.py            # Bulk operations tests
└── e2e/
    ├── test_create_recurring_pattern.py    # Full pattern creation workflow
    ├── test_edit_series_vs_occurrence.py   # Edit scope isolation
    ├── test_exception_handling.py          # Holiday skip/modify
    └── test_calendar_preview.py            # Preview update responsiveness
```

## Complexity Tracking

*No constitution violations - this section intentionally left empty.*

## Next Steps

**Phase 0: Research & Technology Decisions** (generate `research.md`):
1. Decision 1: FullCalendar vs DayPilot vs Custom calendar widget
2. Decision 2: python-dateutil.rrule vs manual calculation vs croniter
3. Decision 3: Pre-generate occurrences vs calculate on-demand
4. Decision 4: RFC 5545 full compliance vs simplified subset
5. Decision 5: Natural language generation (manual vs library like humanize)
6. Decision 6: Exception storage (separate table vs JSONB array)
7. Decision 7: Bulk edit atomicity (transaction vs async with rollback)
8. Decision 8: Calendar preview performance (server-side vs client-side calculation)

**Phase 1: Design & Contracts** (generate `contracts/`, `quickstart.md`, update agent context):
1. Generate `data-model.md` with entities: RecurringSeries, RecurrenceException, Event extensions (series_id, sequence_number, is_exception)
2. Generate API contracts in `contracts/`:
   - `recurring-series-api.md`: CRUD operations for recurring series
   - `recurrence-exceptions-api.md`: Exception management (skip, modify)
   - `bulk-edit-api.md`: Bulk operations on selected occurrences
   - `calendar-preview-api.md`: Preview generation endpoint
3. Generate `quickstart.md`: 10-minute recurring events setup guide
4. Run `.specify/scripts/bash/update-agent-context.sh claude` to update agent-specific context

**Phase 2: Task Breakdown** (run `/speckit.tasks` after Phase 1 complete):
- Generate `tasks.md` with implementation tasks organized by user story
- Mark tasks as parallelizable where possible
- Identify MVP scope (P1 user stories: create pattern, preview, generate occurrences)

**Constitutional Compliance**: ✅ ALL GATES PASS
**Ready for Phase 0**: ✅ YES
**Estimated Complexity**: Medium (3-4 weeks implementation for P1 features)
