# Implementation Plan: Manual Schedule Editing Interface

**Branch**: `007-manual-schedule-editing` | **Date**: 2025-10-23 | **Feature**: 017
**Input**: Feature specification from original requirements

## Summary

Implement a manual schedule editing interface that allows administrators to directly manipulate solver-generated schedules through drag-and-drop interactions. Admins can reassign volunteers between time slots, swap role assignments, add/remove assignments, and override automated scheduling decisions while the system provides real-time feedback on constraint violations (availability conflicts, fairness imbalance, coverage gaps). Manual overrides are preserved when the solver re-runs by marking them as "locked" assignments. The interface includes undo/redo functionality and provides intelligent suggestions for resolving constraint violations introduced by manual edits.

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, OR-Tools (backend); Vanilla JavaScript, drag-and-drop library (SortableJS or dragula) (frontend)
**Storage**: PostgreSQL (production) / SQLite (development) via SQLAlchemy ORM
**Testing**: pytest (unit/integration), Playwright (E2E), Jest (frontend unit tests)
**Target Platform**: Web application (responsive, desktop-optimized)
**Project Type**: Web (frontend + backend)
**Performance Goals**: <100ms drag-and-drop responsiveness, <500ms constraint validation, <2s for conflict resolution suggestions
**Constraints**: Real-time validation without blocking UI, preserve undo history (last 50 actions), maintain fairness metrics accuracy
**Scale/Scope**: Handle schedules with 50+ events, 200+ volunteers, 10+ concurrent editors (admin users)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: No constitution file defined for this project (template only). Proceeding with standard software engineering best practices:

✅ **Test-First Development**: E2E tests will be written for drag-and-drop workflows before implementation
✅ **Integration Testing**: Contract tests for manual edit API, constraint validation, and solver integration
✅ **Simplicity**: Start with core drag-and-drop, then add undo/redo, then conflict resolution
✅ **Performance**: Validate constraints client-side for immediate feedback, server-side for accuracy
✅ **Security**: Admin-only access (RBAC enforcement), validate all manual edits server-side

**No violations** - Feature aligns with existing SignUpFlow architecture patterns.

## Project Structure

### Documentation (this feature)

```
specs/007-manual-schedule-editing/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions (drag-drop libs, undo/redo patterns)
├── data-model.md        # Phase 1: ManualOverride, EditHistory, ConstraintViolation entities
├── quickstart.md        # Phase 1: 10-minute manual editing setup guide
└── contracts/           # Phase 1: Manual edit APIs, constraint validation APIs
```

### Source Code (repository root)

```
# SignUpFlow uses existing web application structure

backend → api/
├── routers/
│   ├── manual_edits.py          # NEW: Manual schedule editing endpoints
│   └── constraint_validation.py # NEW: Real-time constraint checks
├── services/
│   ├── manual_edit_service.py   # NEW: Manual override business logic
│   ├── edit_history_service.py  # NEW: Undo/redo management
│   └── conflict_resolver.py     # NEW: Constraint violation resolution
├── models.py                    # EXTEND: Add ManualOverride, EditHistory models
└── schemas/
    └── manual_edits.py          # NEW: Pydantic schemas for manual edit operations

frontend/
├── js/
│   ├── app-admin.js             # EXTEND: Add manual editing interface
│   ├── schedule-editor.js       # NEW: Drag-and-drop schedule editor
│   ├── constraint-validator.js  # NEW: Real-time constraint validation
│   └── edit-history.js          # NEW: Undo/redo management
└── css/
    └── schedule-editor.css      # NEW: Manual editing interface styles

tests/
├── e2e/
│   ├── test_manual_editing.py   # NEW: Drag-drop workflows, constraint warnings
│   └── test_undo_redo.py        # NEW: Undo/redo functionality
├── integration/
│   ├── test_manual_edit_api.py  # NEW: Manual edit endpoint tests
│   └── test_constraint_validation.py # NEW: Constraint validation tests
└── unit/
    ├── test_manual_edit_service.py  # NEW: Business logic unit tests
    └── test_edit_history.py         # NEW: Undo/redo logic unit tests
```

**Structure Decision**: Extends existing SignUpFlow web application structure. Manual editing functionality is implemented as a new admin console feature within the existing architecture. Frontend uses Vanilla JavaScript (no framework) to match existing codebase patterns. Backend follows FastAPI + SQLAlchemy patterns established in the project.

## Complexity Tracking

*No constitution violations requiring justification.*

**Complexity Notes**:
- **Drag-and-drop library**: Adding SortableJS (10KB) for drag-drop interactions - justified for UX quality and development velocity vs custom implementation (2+ weeks)
- **Undo/redo pattern**: Command pattern for edit history - standard software engineering pattern, minimal complexity
- **Real-time validation**: Client-side validation for immediate feedback, server-side for accuracy - necessary for good UX
- **Locked assignments**: Extending EventAssignment model with `is_locked` flag - minimal schema change, high value for preserving manual edits

## Next Steps

**Phase 0 (Research)**: Generate `research.md` with technology decisions:
1. Drag-and-drop library selection (SortableJS vs dragula vs custom)
2. Undo/redo implementation pattern (Command pattern vs event sourcing)
3. Real-time constraint validation approach (WebSocket vs polling vs client-side only)
4. Conflict resolution algorithm (greedy vs constraint satisfaction)
5. Edit history storage strategy (database vs in-memory vs session storage)

**Phase 1 (Design)**: Generate data model, API contracts, and quickstart guide:
1. `data-model.md`: ManualOverride, EditHistory, ConstraintViolation entities
2. `contracts/manual-edit-api.md`: Drag-drop assignment API
3. `contracts/constraint-validation-api.md`: Real-time validation API
4. `contracts/undo-redo-api.md`: Edit history management API
5. `quickstart.md`: 10-minute manual editing setup guide

**Phase 2 (Tasks)**: Generate `tasks.md` (executed by `/speckit.tasks` command, NOT by this command)
