# Implementation Plan: Email Notification System

**Branch**: `001-email-notifications` | **Date**: 2025-10-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-email-notifications/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement automated email notification system for volunteer assignments with immediate notifications when volunteers are assigned, 24-hour reminders before events, schedule change notifications, and customizable email preferences. System uses async job queue for reliable delivery, comprehensive test pyramid (90%+ coverage), and Mailtrap for email testing across all environments. Primary goal: Reduce volunteer no-shows by 30% and save administrators 5+ hours per week on manual communication.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0+, Celery/RQ (job queue - NEEDS CLARIFICATION: which one?), Mailtrap (sandbox + production APIs), Jinja2 (email templates), pytest-xdist (parallel testing)
**Storage**: SQLite (development), PostgreSQL (production - migration path needed)
**Testing**: pytest (backend unit/integration), Playwright (E2E browser automation), Jest (frontend unit tests)
**Target Platform**: Linux server (Ubuntu/Debian), ASGI server (Uvicorn)
**Project Type**: Web application (FastAPI backend API + Vanilla JS frontend SPA)
**Performance Goals**: Email delivery within 2 minutes (95th percentile), support 1000+ emails per organization per day, notification processing rate of 1000/hour without degradation
**Constraints**: <2 minute delivery SLA for assignment notifications, 90%+ test coverage enforced by CI/CD, CAN-SPAM compliance required, multi-tenant isolation (no cross-org data leaks), JWT authentication for schedule links
**Scale/Scope**: 200+ volunteers per organization, 1000+ organizations (multi-tenant), 50+ concurrent events per org, 10,000 emails/month initial budget

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle 1: User-First Testing (E2E MANDATORY)
✅ **PASS** - Feature spec includes 5 user stories with comprehensive acceptance scenarios. Testing requirements mandate E2E tests with Playwright for all user stories (100% coverage of critical user paths). Each user story has independent test scenarios defined.

### Principle 2: Security-First Development
✅ **PASS** - Feature includes JWT authentication for secure schedule links (FR-003), RBAC enforcement for admin notification settings, multi-tenant isolation enforced in constraints. Email preferences respect existing authentication system.

### Principle 3: Multi-tenant Isolation
✅ **PASS** - Explicitly required in constraints: "multi-tenant isolation (no cross-org data leaks)". FR-010 specifies organization admins can only view notification logs for their org. All notification entities will filter by org_id.

### Principle 4: Test Coverage Excellence
✅ **PASS** - Testing Requirements section mandates 90%+ unit test coverage, 100% integration test coverage for all service integration points, 100% E2E coverage for all critical user paths. Multi-gate CI/CD approach with parallel execution. pytest-xdist and Playwright workers for speed optimization.

### Principle 5: Internationalization by Default
✅ **PASS** - FR-012 requires notification text translations in 6 languages (EN, ES, PT, ZH-CN, ZH-TW, KO). Email templates will use same i18n pattern as existing UI. Volunteer language preference used for email content.

### Principle 6: Code Quality Standards
✅ **PASS** - Implementation will follow existing FastAPI/SQLAlchemy/Pydantic patterns. Backend in `api/routers/notifications.py`, `api/services/notification_service.py`. Email service will use Jinja2 templates. No TODO comments for core functionality (per constitution). Frontend will use `authFetch()` for API calls.

### Principle 7: Clear Documentation
✅ **PASS** - This plan.md documents implementation approach. research.md will document technology decisions. data-model.md will document entities. quickstart.md will provide developer guide. API docs auto-generated via FastAPI Swagger. Will update CLAUDE.md with notification system architecture.

**Overall Status**: ✅ **ALL GATES PASS** - No violations requiring justification. Feature fully compliant with SignUpFlow constitution.

## Project Structure

### Documentation (this feature)

```
specs/001-email-notifications/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entities and relationships)
├── quickstart.md        # Phase 1 output (developer setup guide)
├── contracts/           # Phase 1 output (API specifications)
│   ├── notifications-api.yaml      # OpenAPI spec for notification endpoints
│   └── email-service-interface.py  # Email service adapter interface
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Type**: Web Application (FastAPI backend + Vanilla JS frontend SPA)

```
api/                                    # Backend (Python/FastAPI)
├── routers/
│   └── notifications.py                # NEW: Notification API endpoints
├── services/
│   ├── email_service.py                # NEW: Email sending abstraction (Mailtrap adapter)
│   └── notification_service.py         # NEW: Business logic for notifications
├── tasks/
│   └── notifications.py                # NEW: Celery/RQ background jobs
├── models.py                           # MODIFY: Add Notification, EmailPreference, DeliveryLog entities
├── schemas/
│   └── notifications.py                # NEW: Pydantic request/response models
└── templates/
    └── email/                          # NEW: Jinja2 email templates
        ├── assignment_en.html          # Assignment notification (6 languages)
        ├── reminder_en.html            # Reminder notification (6 languages)
        ├── update_en.html              # Schedule change notification (6 languages)
        └── ...                         # (ES, PT, ZH-CN, ZH-TW, KO variants)

frontend/                               # Frontend (Vanilla JS SPA)
├── js/
│   ├── notification-preferences.js     # NEW: Email preference management UI
│   └── app-admin.js                    # MODIFY: Add notification stats dashboard
└── index.html                          # MODIFY: Add notification preferences page

tests/                                  # Test suites
├── unit/
│   ├── test_notification_service.py    # NEW: Business logic tests (>90% coverage)
│   └── test_email_service.py           # NEW: Email service tests (mocked)
├── integration/
│   ├── test_notification_api.py        # NEW: API endpoint tests (real DB)
│   └── test_email_integration.py       # NEW: Email service integration (Mailtrap sandbox)
└── e2e/
    ├── test_assignment_notification.py # NEW: US1 acceptance scenarios (Playwright)
    ├── test_reminder_notification.py   # NEW: US2 acceptance scenarios
    ├── test_schedule_change.py         # NEW: US3 acceptance scenarios
    ├── test_email_preferences.py       # NEW: US4 acceptance scenarios
    └── test_admin_summary.py           # NEW: US5 acceptance scenarios

locales/                                # i18n translations
├── en/
│   └── emails.json                     # NEW: Email notification text
├── es/
│   └── emails.json                     # NEW: Spanish translations
└── ... (pt, zh-CN, zh-TW, ko)          # NEW: Other language translations

docs/
└── NOTIFICATION_SYSTEM.md              # NEW: Architecture and usage guide
```

**Structure Decision**: SignUpFlow uses a **web application structure** with separate `api/` (backend) and `frontend/` directories. This feature adds notification-specific modules to existing directories following established patterns. Email templates are co-located with backend code for easier deployment. Tests organized by type (unit/integration/e2e) with comprehensive coverage across all layers.

## Complexity Tracking

*No violations to justify - all constitution gates pass.*

