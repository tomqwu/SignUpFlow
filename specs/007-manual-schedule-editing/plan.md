# Implementation Plan: Manual Schedule Editing Interface

**Branch**: `007-manual-schedule-editing` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

## Summary

Interactive UI for manual schedule editing with drag-and-drop assignments, real-time constraint validation, locked assignment preservation, undo/redo, volunteer swapping, and conflict resolution suggestions. Enables admins to fine-tune solver-generated schedules while maintaining data integrity and fairness metrics.

**Key Capabilities**:
- Drag-and-drop volunteer assignments between slots
- Real-time constraint warnings (availability, fairness, coverage)
- Locked assignments preserved on solver re-run
- Undo/redo for manual edits (10-step history)
- Volunteer swap operations with validation
- Conflict resolution suggestions

**Cost**: $0/month (pure feature enhancement)

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vanilla JavaScript (frontend)
**Primary Dependencies**:
- Interact.js OR native HTML5 drag-and-drop (frontend dragging)
- Constraint validation service (reuse solver logic)

**Storage**: PostgreSQL 14+ (AssignmentLock table, EditHistory table)
**Testing**: Pytest, Jest, Playwright (E2E drag-drop interactions)
**Performance Goals**: <100ms drag validation, <500ms swap operation, <200ms undo/redo
**Constraints**: Max 10-step undo history, locked assignments <50% of total

## Constitution Check ✅ ALL GATES PASS

E2E tests verify drag-drop workflows, constraint validation, locked assignment preservation. All other gates pass.

## Project Structure

```
api/
├── routers/manual_editing.py      # Manual edit API
├── services/constraint_validator.py # Real-time validation
├── models.py                        # AssignmentLock, EditHistory

frontend/
├── js/schedule-editor.js          # Drag-drop UI
└── js/undo-redo.js                # Undo/redo manager

tests/
└── e2e/test_manual_editing.py     # Drag-drop E2E tests
```

---

**Status**: Streamlined plan complete
