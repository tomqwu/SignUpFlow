# Tasks: Email Notification System

**Input**: Design documents from `/specs/001-email-notifications/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Per spec.md Testing Requirements, this feature implements the comprehensive test pyramid with 90%+ coverage requirement. All test tasks are MANDATORY and marked below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `api/` (FastAPI application)
- **Frontend**: `frontend/` (Vanilla JS SPA)
- **Tests**: `tests/` (unit, integration, e2e subdirectories)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Add Celery dependency to pyproject.toml (celery==5.3.4)
- [X] T002 [P] Add Redis dependency to pyproject.toml (redis==5.0.1)
- [X] T003 [P] Add Jinja2 dependency to pyproject.toml (jinja2==3.1.2)
- [X] T004 [P] Add pytest-asyncio for async testing to pyproject.toml
- [X] T005 Run poetry install to install all new dependencies
- [X] T006 [P] Create api/templates/email/ directory for email templates
- [X] T007 [P] Create api/tasks/ directory for Celery background jobs
- [X] T008 [P] Create locales/en/emails.json for email notification translations
- [X] T009 [P] Create locales/es/emails.json for Spanish email translations
- [X] T010 [P] Create locales/pt/emails.json for Portuguese email translations
- [X] T011 [P] Create locales/zh-CN/emails.json for Simplified Chinese email translations
- [X] T012 [P] Create locales/zh-TW/emails.json for Traditional Chinese email translations
- [X] T013 [P] Create locales/fr/emails.json for French email translations (project uses FR not KO)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T014 Create api/celery_app.py with Celery application configuration and Beat schedule
- [X] T015 Add environment variables to api/core/config.py (MAILTRAP_API_TOKEN, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, FRONTEND_BASE_URL)
- [X] T016 Add Notification model to api/models.py with NotificationType and NotificationStatus enums
- [X] T017 [P] Add EmailPreference model to api/models.py with EmailFrequency enum
- [X] T018 [P] Add DeliveryLog model to api/models.py with DeliveryEventType enum
- [X] T019 Add notification relationships to Organization model in api/models.py (back_populates="notifications")
- [X] T020 [P] Add notification relationships to Person model in api/models.py (back_populates="notifications_received")
- [X] T021 [P] Add notification relationships to Event model in api/models.py (back_populates="notifications")
- [X] T022 Create Alembic migration for new notification tables (notifications, email_preferences, delivery_logs)
- [X] T023 Run Alembic migration to create database tables (alembic upgrade head)
- [X] T024 Create api/schemas/notifications.py with Pydantic schemas (NotificationResponse, NotificationCreate, EmailPreferenceResponse, EmailPreferenceUpdate)
- [X] T025 Create api/services/email_service.py with EmailService class and Mailtrap integration (sandbox + production modes)
- [X] T026 Create api/services/notification_service.py with NotificationService class for business logic
- [X] T027 Create api/tasks/__init__.py (empty package file)
- [X] T028 Create api/routers/notifications.py with router initialization and RBAC imports

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Assignment Notification (Priority: P1) 🎯 MVP

**Goal**: When admin assigns volunteer to event, volunteer receives immediate email with event details and schedule link within 2 minutes

**Independent Test**: Assign volunteer to event → verify email received within 2 minutes with correct event details and working schedule link

### Tests for User Story 1 (MANDATORY per Testing Requirements)

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T029 [P] [US1] Unit test for NotificationService.create_assignment_notification() in tests/unit/test_notification_service.py
- [X] T030 [P] [US1] Unit test for EmailService.send_assignment_email() with mocked Mailtrap in tests/unit/test_email_service.py
- [ ] T031 [P] [US1] Unit test for email template rendering (assignment_en.html) in tests/unit/test_email_templates.py
- [X] T032 [P] [US1] Integration test for POST /api/notifications endpoint in tests/integration/test_notification_api.py
- [X] T033 [P] [US1] Integration test for Mailtrap sandbox email delivery in tests/integration/test_email_integration.py
- [X] T034 [US1] E2E test for complete assignment notification workflow using Playwright in tests/e2e/test_assignment_notification.py

### Implementation for User Story 1

- [X] T035 [P] [US1] Create assignment_en.html email template in api/templates/email/ with event details and schedule link
- [X] T036 [P] [US1] Create assignment_es.html Spanish email template in api/templates/email/
- [X] T037 [P] [US1] Create assignment_pt.html Portuguese email template in api/templates/email/
- [X] T038 [P] [US1] Create assignment_zh-CN.html Simplified Chinese email template in api/templates/email/
- [X] T039 [P] [US1] Create assignment_zh-TW.html Traditional Chinese email template in api/templates/email/
- [X] T040 [P] [US1] Create assignment_fr.html French email template in api/templates/email/ (project uses FR not KO)
- [X] T041 [US1] Implement EmailService.send_assignment_email() in api/services/email_service.py with Jinja2 rendering and Mailtrap API integration
- [X] T042 [US1] Implement NotificationService.create_assignment_notification() in api/services/notification_service.py with email preference checking
- [X] T043 [US1] Implement send_email_task() Celery task in api/tasks/notifications.py with retry logic (3 attempts, exponential backoff)
- [X] T044 [US1] Implement GET /api/notifications endpoint in api/routers/notifications.py with RBAC (admins see all, volunteers see own)
- [X] T045 [US1] Implement GET /api/notifications/{id} endpoint in api/routers/notifications.py
- [X] T046 [US1] Implement POST /api/notifications endpoint in api/routers/notifications.py (admin-only, for testing)
- [X] T047 [US1] Integrate notification trigger in api/routers/events.py POST assignment endpoint (lines 381-389 per plan)
- [X] T048 [US1] Add error handling and logging for notification failures in notification trigger
- [ ] T049 [US1] Verify all US1 tests pass and achieve >90% coverage for US1 code

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Assignment Reminder (Priority: P2)

**Goal**: Volunteers receive automatic reminder emails 24 hours before scheduled event

**Independent Test**: Create event 25 hours in future, assign volunteer, wait for reminder job to run, verify reminder received at 24-hour mark

### Tests for User Story 2 (MANDATORY per Testing Requirements)

- [ ] T050 [P] [US2] Unit test for NotificationService.create_reminder_notification() in tests/unit/test_notification_service.py
- [ ] T051 [P] [US2] Unit test for EmailService.send_reminder_email() in tests/unit/test_email_service.py
- [ ] T052 [P] [US2] Unit test for send_reminder_emails() periodic task in tests/unit/test_notification_tasks.py
- [ ] T053 [P] [US2] Integration test for reminder email delivery via Mailtrap in tests/integration/test_email_integration.py
- [ ] T054 [US2] E2E test for 24-hour reminder workflow in tests/e2e/test_reminder_notification.py

### Implementation for User Story 2

- [ ] T055 [P] [US2] Create reminder_en.html email template in api/templates/email/ with event reminder and "add to calendar" option
- [ ] T056 [P] [US2] Create reminder_es.html Spanish reminder template in api/templates/email/
- [ ] T057 [P] [US2] Create reminder_pt.html Portuguese reminder template in api/templates/email/
- [ ] T058 [P] [US2] Create reminder_zh-CN.html Simplified Chinese reminder template in api/templates/email/
- [ ] T059 [P] [US2] Create reminder_zh-TW.html Traditional Chinese reminder template in api/templates/email/
- [ ] T060 [P] [US2] Create reminder_ko.html Korean reminder template in api/templates/email/
- [ ] T061 [US2] Implement EmailService.send_reminder_email() in api/services/email_service.py
- [ ] T062 [US2] Implement NotificationService.create_reminder_notification() in api/services/notification_service.py with 24-hour check
- [ ] T063 [US2] Implement send_reminder_emails() Celery Beat periodic task in api/tasks/notifications.py (runs every hour)
- [ ] T064 [US2] Implement reminder digest batching for volunteers with 3+ events within 48 hours in api/tasks/notifications.py
- [ ] T065 [US2] Verify all US2 tests pass and achieve >90% coverage for US2 code

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Schedule Change Notification (Priority: P2)

**Goal**: When event details change (time, location, cancellation), all assigned volunteers receive immediate update notifications

**Independent Test**: Modify event time or location → verify all assigned volunteers receive update email within 2 minutes highlighting changes

### Tests for User Story 3 (MANDATORY per Testing Requirements)

- [ ] T066 [P] [US3] Unit test for NotificationService.create_update_notification() in tests/unit/test_notification_service.py
- [ ] T067 [P] [US3] Unit test for EmailService.send_update_email() in tests/unit/test_email_service.py
- [ ] T068 [P] [US3] Unit test for change detection logic (old vs new event data) in tests/unit/test_notification_service.py
- [ ] T069 [P] [US3] Integration test for update notification delivery via Mailtrap in tests/integration/test_email_integration.py
- [ ] T070 [US3] E2E test for schedule change workflow in tests/e2e/test_schedule_change.py

### Implementation for User Story 3

- [ ] T071 [P] [US3] Create update_en.html email template in api/templates/email/ with "SCHEDULE CHANGE" subject and old vs new comparison
- [ ] T072 [P] [US3] Create update_es.html Spanish update template in api/templates/email/
- [ ] T073 [P] [US3] Create update_pt.html Portuguese update template in api/templates/email/
- [ ] T074 [P] [US3] Create update_zh-CN.html Simplified Chinese update template in api/templates/email/
- [ ] T075 [P] [US3] Create update_zh-TW.html Traditional Chinese update template in api/templates/email/
- [ ] T076 [P] [US3] Create update_ko.html Korean update template in api/templates/email/
- [ ] T077 [US3] Implement EmailService.send_update_email() in api/services/email_service.py with change highlighting
- [ ] T078 [US3] Implement NotificationService.create_update_notification() in api/services/notification_service.py with old/new data comparison
- [ ] T079 [US3] Implement NotificationService.create_cancellation_notification() in api/services/notification_service.py
- [ ] T080 [US3] Integrate update notification trigger in api/routers/events.py PUT event endpoint (detect changes)
- [ ] T081 [US3] Integrate cancellation notification trigger in api/routers/events.py DELETE event endpoint
- [ ] T082 [US3] Implement notification batching for multiple changes within 5 minutes (prevent email spam)
- [ ] T083 [US3] Verify all US3 tests pass and achieve >90% coverage for US3 code

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Email Preferences Management (Priority: P3)

**Goal**: Volunteers can control notification types and frequency (immediate, daily digest, weekly digest)

**Independent Test**: Volunteer changes preferences to "daily digest" → verify they receive single daily email at specified time instead of immediate notifications

### Tests for User Story 4 (MANDATORY per Testing Requirements)

- [ ] T084 [P] [US4] Unit test for EmailPreference.is_type_enabled() logic in tests/unit/test_email_preferences.py
- [ ] T085 [P] [US4] Unit test for daily digest batching in tests/unit/test_notification_tasks.py
- [ ] T086 [P] [US4] Unit test for weekly digest batching in tests/unit/test_notification_tasks.py
- [ ] T087 [P] [US4] Integration test for GET /api/notifications/preferences/me endpoint in tests/integration/test_notification_api.py
- [ ] T088 [P] [US4] Integration test for PUT /api/notifications/preferences/me endpoint in tests/integration/test_notification_api.py
- [ ] T089 [US4] E2E test for email preferences workflow in tests/e2e/test_email_preferences.py

### Implementation for User Story 4

- [ ] T090 [P] [US4] Create digest_daily_en.html email template in api/templates/email/ with consolidated assignments
- [ ] T091 [P] [US4] Create digest_weekly_en.html email template in api/templates/email/ with weekly summary
- [ ] T092 [P] [US4] Create digest templates for all 5 other languages (es, pt, zh-CN, zh-TW, ko) in api/templates/email/
- [ ] T093 [US4] Implement EmailService.send_digest_email() in api/services/email_service.py
- [ ] T094 [US4] Implement NotificationService.get_or_create_preferences() in api/services/notification_service.py
- [ ] T095 [US4] Implement NotificationService.should_send_immediate() checking preferences in api/services/notification_service.py
- [ ] T096 [US4] Implement send_daily_digests() Celery Beat periodic task in api/tasks/notifications.py (runs daily at 8am UTC)
- [ ] T097 [US4] Implement send_weekly_digests() Celery Beat periodic task in api/tasks/notifications.py (runs Monday 8am UTC)
- [ ] T098 [US4] Implement GET /api/notifications/preferences/me endpoint in api/routers/notifications.py
- [ ] T099 [US4] Implement PUT /api/notifications/preferences/me endpoint in api/routers/notifications.py with validation
- [ ] T100 [US4] Implement unsubscribe token generation and validation in api/services/notification_service.py
- [ ] T101 [US4] Update all notification creation logic to check email preferences before sending
- [ ] T102 [US4] Verify all US4 tests pass and achieve >90% coverage for US4 code

**Checkpoint**: All core user stories should now be independently functional

---

## Phase 7: User Story 5 - Admin Notification Summary (Priority: P3)

**Goal**: Admins receive weekly summary emails showing delivery statistics and volunteer engagement metrics

**Independent Test**: Run weekly summary job → verify admin receives email with notification counts (sent, delivered, failed, opened, clicked)

### Tests for User Story 5 (MANDATORY per Testing Requirements)

- [ ] T103 [P] [US5] Unit test for NotificationService.generate_weekly_stats() in tests/unit/test_notification_service.py
- [ ] T104 [P] [US5] Unit test for send_admin_summaries() periodic task in tests/unit/test_notification_tasks.py
- [ ] T105 [P] [US5] Integration test for admin summary email delivery in tests/integration/test_email_integration.py
- [ ] T106 [P] [US5] Integration test for GET /api/notifications/stats/organization endpoint in tests/integration/test_notification_api.py
- [ ] T107 [US5] E2E test for admin summary workflow in tests/e2e/test_admin_summary.py

### Implementation for User Story 5

- [ ] T108 [P] [US5] Create admin_summary_en.html email template in api/templates/email/ with statistics dashboard
- [ ] T109 [P] [US5] Create admin summary templates for all 5 other languages (es, pt, zh-CN, zh-TW, ko) in api/templates/email/
- [ ] T110 [US5] Implement EmailService.send_admin_summary_email() in api/services/email_service.py
- [ ] T111 [US5] Implement NotificationService.generate_weekly_stats() in api/services/notification_service.py with aggregation queries
- [ ] T112 [US5] Implement send_admin_summaries() Celery Beat periodic task in api/tasks/notifications.py (runs Monday 8am UTC)
- [ ] T113 [US5] Implement GET /api/notifications/stats/organization endpoint in api/routers/notifications.py (admin-only)
- [ ] T114 [US5] Implement failed delivery detection and highlighting in admin summary
- [ ] T115 [US5] Verify all US5 tests pass and achieve >90% coverage for US5 code

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Mailtrap Webhooks (Delivery Tracking)

**Purpose**: Receive delivery status updates from Mailtrap to update notification status (delivered, opened, clicked, bounced)

- [ ] T116 Create api/routers/webhooks.py with router initialization
- [ ] T117 [P] Implement POST /api/webhooks/mailtrap endpoint in api/routers/webhooks.py with signature verification
- [ ] T118 [P] Implement webhook signature validation using Mailtrap webhook secret
- [ ] T119 Implement handle_delivery_event() in api/services/notification_service.py to update notification status
- [ ] T120 [P] Create unit test for webhook signature validation in tests/unit/test_webhook_security.py
- [ ] T121 [P] Create integration test for webhook processing in tests/integration/test_mailtrap_webhooks.py
- [ ] T122 Register webhooks router in api/main.py
- [ ] T123 [P] Update docs/LOCAL_EMAIL_SETUP.md with Mailtrap webhook configuration instructions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T124 [P] Create comprehensive error handling for all API endpoints with translated error messages
- [ ] T125 [P] Add request/response logging for all notification API endpoints
- [ ] T126 [P] Implement rate limiting for notification creation (max 100/minute per org)
- [ ] T127 [P] Add database indexes for performance optimization (see data-model.md indexes section)
- [ ] T128 [P] Create cleanup_old_delivery_logs() Celery Beat task in api/tasks/cleanup.py (runs daily at 2am)
- [ ] T129 [P] Implement CAN-SPAM compliance checks (unsubscribe link, physical address) in all email templates
- [ ] T130 [P] Add monitoring/alerting for notification delivery failures (log to application logs)
- [ ] T131 [P] Create docs/NOTIFICATION_SYSTEM.md with architecture documentation and usage guide
- [ ] T132 [P] Update CLAUDE.md with notification system patterns and common tasks
- [ ] T133 Run full test suite and verify 90%+ coverage requirement (make test-all)
- [ ] T134 Run quickstart.md validation (follow quickstart guide to verify all steps work)
- [ ] T135 Code cleanup and refactoring (remove any TODO comments, optimize imports)
- [ ] T136 Security hardening (verify multi-tenant isolation, RBAC enforcement, JWT validation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3 → P3)
- **Webhooks (Phase 8)**: Can start after Foundational, parallel with user stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent (uses US1 email service but doesn't modify it)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent (uses US1 email service but doesn't modify it)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1/US2/US3 but should be independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent (reads notification data, doesn't modify flows)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach per Testing Requirements)
- Email templates before email service methods
- Email service methods before notification service methods
- Notification service before API endpoints
- API endpoints before event integration
- All tests pass before moving to next story

### Parallel Opportunities

- All Setup tasks (T001-T013) marked [P] can run in parallel
- All Foundational model tasks (T017-T018, T020-T021) marked [P] can run in parallel
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- All test tasks within a story marked [P] can run in parallel
- Email template creation within a story marked [P] can run in parallel (T035-T040, T055-T060, etc.)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all test tasks for User Story 1 together (MANDATORY TDD):
Task T029: "Unit test for NotificationService.create_assignment_notification() in tests/unit/test_notification_service.py"
Task T030: "Unit test for EmailService.send_assignment_email() with mocked Mailtrap in tests/unit/test_email_service.py"
Task T031: "Unit test for email template rendering (assignment_en.html) in tests/unit/test_email_templates.py"
Task T032: "Integration test for POST /api/notifications endpoint in tests/integration/test_notification_api.py"
Task T033: "Integration test for Mailtrap sandbox email delivery in tests/integration/test_email_integration.py"

# Launch all email template tasks for User Story 1 together:
Task T035: "Create assignment_en.html email template in api/templates/email/"
Task T036: "Create assignment_es.html Spanish email template in api/templates/email/"
Task T037: "Create assignment_pt.html Portuguese email template in api/templates/email/"
Task T038: "Create assignment_zh-CN.html Simplified Chinese email template in api/templates/email/"
Task T039: "Create assignment_zh-TW.html Traditional Chinese email template in api/templates/email/"
Task T040: "Create assignment_ko.html Korean email template in api/templates/email/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T013)
2. Complete Phase 2: Foundational (T014-T028) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T029-T049)
4. **STOP and VALIDATE**: Test User Story 1 independently, verify 90%+ coverage
5. Deploy/demo if ready

**MVP Delivery**: Assignment notifications working end-to-end with comprehensive test coverage

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! 🎯)
3. Add User Story 2 → Test independently → Deploy/Demo (Reminders working)
4. Add User Story 3 → Test independently → Deploy/Demo (Schedule changes working)
5. Add User Story 4 → Test independently → Deploy/Demo (Preferences working)
6. Add User Story 5 → Test independently → Deploy/Demo (Admin summaries working)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T028)
2. Once Foundational is done:
   - Developer A: User Story 1 (T029-T049) - MVP
   - Developer B: User Story 2 (T050-T065) - Reminders
   - Developer C: User Story 3 (T066-T083) - Updates
   - Developer D: Webhooks (T116-T123)
3. Stories complete and integrate independently
4. Continue with US4, US5, and Polish in priority order

---

## Testing Coverage Summary

Per spec.md Testing Requirements (90%+ coverage):

### Unit Tests (>90% code coverage)
- **US1**: T029-T031 (NotificationService, EmailService, templates)
- **US2**: T050-T052 (reminder logic, periodic tasks)
- **US3**: T066-T068 (update logic, change detection)
- **US4**: T084-T086 (preferences, digest batching)
- **US5**: T103-T104 (statistics, admin summaries)
- **Webhooks**: T120 (signature validation)

### Integration Tests (100% service integration coverage)
- **US1**: T032-T033 (API endpoints, Mailtrap delivery)
- **US2**: T053 (reminder delivery)
- **US3**: T069 (update delivery)
- **US4**: T087-T088 (preferences endpoints)
- **US5**: T105-T106 (admin stats)
- **Webhooks**: T121 (webhook processing)

### E2E Tests (100% critical user path coverage)
- **US1**: T034 (complete assignment notification workflow)
- **US2**: T054 (24-hour reminder workflow)
- **US3**: T070 (schedule change workflow)
- **US4**: T089 (preferences workflow)
- **US5**: T107 (admin summary workflow)

**Total Tests**: 36 mandatory test tasks ensuring comprehensive coverage

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tests MUST pass before marking story complete
- 90%+ coverage requirement enforced by CI/CD (gates will fail if not met)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Phase 1 (Setup)**: 13 tasks
- **Phase 2 (Foundational)**: 15 tasks
- **Phase 3 (US1 - Assignment Notification)**: 21 tasks (6 tests + 15 implementation)
- **Phase 4 (US2 - Reminders)**: 16 tasks (5 tests + 11 implementation)
- **Phase 5 (US3 - Schedule Changes)**: 18 tasks (5 tests + 13 implementation)
- **Phase 6 (US4 - Preferences)**: 19 tasks (6 tests + 13 implementation)
- **Phase 7 (US5 - Admin Summaries)**: 13 tasks (5 tests + 8 implementation)
- **Phase 8 (Webhooks)**: 8 tasks
- **Phase 9 (Polish)**: 13 tasks

**Total**: 136 tasks

**Parallel Opportunities**: 57 tasks marked [P] can run in parallel within their respective phases

**Suggested MVP Scope**: Phases 1-3 (T001-T049) = Assignment notifications with full test coverage
