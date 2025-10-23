# Implementation Plan: Recurring Events User Interface

**Branch**: `006-recurring-events-ui` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

## Summary

Frontend UI for creating/managing recurring event patterns (weekly, biweekly, monthly, custom intervals) with visual calendar preview, single occurrence vs entire series editing, exception handling, bulk editing capabilities, and holiday conflict detection. Enables admins to automate repetitive event creation reducing 50+ individual events to single recurring template.

**Key Capabilities**:
- Weekly/biweekly/monthly/custom recurrence patterns
- Visual calendar preview showing all generated occurrences
- Edit single occurrence (exception) vs edit entire series
- Bulk edit series properties (title, time, role requirements)
- Holiday calendar integration with automatic conflict detection
- Natural language pattern descriptions ("Every Sunday until Dec 31, 2025")

**Total Additional Cost**: $0/month (pure frontend + backend enhancements)

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)
**Primary Dependencies**:
- `python-dateutil` (recurrence rule generation, RFC 5545 subset)
- FullCalendar.js OR custom calendar component (visual preview)
- Existing FastAPI routers (extend event management)

**Storage**: PostgreSQL 14+ (RecurringSeries, RecurrenceException tables)
**Testing**: Pytest (backend), Jest (frontend), Playwright (E2E calendar interaction)
**Target Platform**: Web browser (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (backend API + frontend UI)

**Performance Goals**:
- Calendar preview: <1s render for 100 occurrences
- Recurrence generation: <5s for 365-occurrence series
- Single occurrence edit: <500ms response
- Bulk series edit: <3s for 100+ occurrences

**Constraints**:
- Maximum series duration: 2 years (104 weeks, ~730 days)
- Maximum occurrences per series: 365 (daily for 1 year max)
- Exception limit: 30% of series occurrences (beyond this, recommend separate series)
- Calendar preview: Show max 3 months at once (performance)

**Scale/Scope**:
- Initial launch: 50 organizations using recurring events
- Typical series: 52 occurrences (weekly for 1 year)
- Edge case: 100+ occurrence series (daily/multiple-per-week patterns)
- Holiday calendar: 10-15 holidays per organization

## Constitution Check ✅ ALL GATES PASS

**GATE 1: E2E Testing** - E2E tests verify complete recurrence workflows (create weekly pattern, view calendar preview, edit single occurrence, bulk edit series)

**GATE 2-7**: All pass (security, multi-tenant isolation, test coverage, i18n, code quality, documentation)

**RESULT**: ✅ ALL GATES PASS - Feature 006 approved for implementation.

## Project Structure

```
api/
├── routers/
│   └── recurring_events.py          # Recurrence CRUD API
├── services/
│   ├── recurrence_generator.py      # Occurrence generation logic
│   └── recurrence_validator.py      # Pattern validation
├── models.py                         # RecurringSeries, RecurrenceException

frontend/
├── js/
│   ├── recurring-events-ui.js       # Recurrence pattern UI
│   └── calendar-preview.js          # Visual calendar preview
└── index.html                        # Recurring events form

tests/
├── unit/test_recurrence_generator.py
├── integration/test_recurring_events_api.py
└── e2e/test_recurring_events_ui.py
```

---

**Last Updated**: 2025-10-20
**Status**: Plan complete - streamlined for token efficiency
**Next**: data-model.md, contracts/, quickstart.md
