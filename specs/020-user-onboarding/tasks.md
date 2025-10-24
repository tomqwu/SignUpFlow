# Tasks: User Onboarding System

**Input**: Design documents from `/specs/020-user-onboarding/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification - focusing on implementation tasks

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `api/services/`, `api/routers/`, `api/models.py`, `api/utils/`
- **Frontend**: `frontend/js/`, `frontend/css/`, `frontend/videos/`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Database**: `migrations/versions/`
- **Docs**: `docs/`, `locales/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and onboarding-specific dependencies

- [ ] T001 Install Shepherd.js library for tutorial overlays in package.json
- [ ] T002 [P] Create onboarding directory structure (api/services/, frontend/js/, tests/)
- [ ] T003 [P] Add i18n translation files for onboarding (locales/en/onboarding.json, es, pt, zh-CN, zh-TW)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database schema and base infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create database migration adding onboarding_state table in migrations/versions/add_onboarding_tables.py
- [ ] T005 Create database migration adding onboarding_checklist_task table in migrations/versions/add_onboarding_tables.py
- [ ] T006 Create database migration adding onboarding_tutorial_completion table in migrations/versions/add_onboarding_tables.py
- [ ] T007 Create database migration adding onboarding_metric table in migrations/versions/add_onboarding_tables.py
- [ ] T008 Run database migration with alembic upgrade head
- [ ] T009 [P] Add OnboardingState model class in api/models.py
- [ ] T010 [P] Add OnboardingChecklistTask model class in api/models.py
- [ ] T011 [P] Add OnboardingTutorialCompletion model class in api/models.py
- [ ] T012 [P] Add OnboardingMetric model class in api/models.py
- [ ] T013 Seed onboarding_checklist_task table with 6 task definitions per data-model.md
- [ ] T014 Create base OnboardingService class skeleton in api/services/onboarding_service.py
- [ ] T015 Create base onboarding router skeleton in api/routers/onboarding.py
- [ ] T016 Create base analytics router skeleton in api/routers/analytics.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Complete Guided Setup Wizard (Priority: P1) 🎯 MVP

**Goal**: New administrator completes 5-step setup wizard (organization profile, first event, first team, volunteer invitations, tutorial intro) with validation, resulting in fully configured organization within 15 minutes

**Independent Test**: Create new organization account. Complete all 5 wizard steps with validation. Verify organization profile saved, first event created, first team created, volunteer invitations sent, wizard completion state saved.

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement create_wizard_state method in api/services/onboarding_service.py
- [ ] T018 [P] [US1] Implement get_wizard_state method in api/services/onboarding_service.py
- [ ] T019 [P] [US1] Implement update_wizard_step_data method with validation in api/services/onboarding_service.py
- [ ] T020 [P] [US1] Implement advance_wizard_step method with step validation in api/services/onboarding_service.py
- [ ] T021 [P] [US1] Implement complete_wizard method in api/services/onboarding_service.py
- [ ] T022 [US1] Implement GET /api/onboarding/wizard endpoint per contracts/wizard-api.md in api/routers/onboarding.py
- [ ] T023 [US1] Implement PUT /api/onboarding/wizard endpoint with step validation in api/routers/onboarding.py
- [ ] T024 [US1] Implement POST /api/onboarding/wizard/complete endpoint in api/routers/onboarding.py
- [ ] T025 [US1] Create wizard step validation utility functions in api/utils/wizard_validator.py
- [ ] T026 [P] [US1] Create onboarding wizard UI component in frontend/js/onboarding-wizard.js
- [ ] T027 [P] [US1] Create wizard CSS styles with progress indicator in frontend/css/wizard.css
- [ ] T028 [US1] Implement step 1 (organization profile) form and validation in frontend/js/onboarding-wizard.js
- [ ] T029 [US1] Implement step 2 (first event) form and validation in frontend/js/onboarding-wizard.js
- [ ] T030 [US1] Implement step 3 (first team) form and validation in frontend/js/onboarding-wizard.js
- [ ] T031 [US1] Implement step 4 (volunteer invitations) form and validation in frontend/js/onboarding-wizard.js
- [ ] T032 [US1] Implement step 5 (tutorial introduction) with completion celebration in frontend/js/onboarding-wizard.js
- [ ] T033 [US1] Add wizard auto-launch on first login logic in frontend/js/app.js
- [ ] T034 [US1] Add i18n translations for wizard steps and validation messages in locales/*/onboarding.json

**Checkpoint**: At this point, User Story 1 should be fully functional - new administrators can complete wizard from start to finish

---

## Phase 4: User Story 2 - Explore Features with Sample Data (Priority: P1)

**Goal**: Administrator generates realistic sample dataset (5 events, 3 teams, 15 volunteers, 1 schedule) for hands-on learning, with clear labeling and ability to clear when ready for production

**Independent Test**: Complete setup wizard. Click "Generate Sample Data". Verify 5 sample events, 3 teams, 15 volunteers created with "(Sample)" labels. Explore schedule. Click "Clear Sample Data". Verify all sample data removed, configuration preserved.

### Implementation for User Story 2

- [ ] T035 [P] [US2] Create SampleDataGenerator class skeleton in api/services/sample_data_generator.py
- [ ] T036 [P] [US2] Implement generate_sample_events method (5 events) in api/services/sample_data_generator.py
- [ ] T037 [P] [US2] Implement generate_sample_teams method (3 teams) in api/services/sample_data_generator.py
- [ ] T038 [P] [US2] Implement generate_sample_volunteers method (15 volunteers) in api/services/sample_data_generator.py
- [ ] T039 [P] [US2] Implement generate_sample_availabilities method with realistic patterns in api/services/sample_data_generator.py
- [ ] T040 [US2] Implement generate_sample_schedule method calling solver in api/services/sample_data_generator.py
- [ ] T041 [US2] Implement generate_sample_data method orchestrating all generation in api/services/sample_data_generator.py
- [ ] T042 [US2] Implement clear_sample_data method with is_sample flag filtering in api/services/sample_data_generator.py
- [ ] T043 [US2] Implement POST /api/onboarding/sample-data endpoint per contracts/sample-data-api.md in api/routers/onboarding.py
- [ ] T044 [US2] Implement GET /api/onboarding/sample-data endpoint (status check) in api/routers/onboarding.py
- [ ] T045 [US2] Implement DELETE /api/onboarding/sample-data endpoint with confirmation in api/routers/onboarding.py
- [ ] T046 [US2] Implement PUT /api/onboarding/sample-data/regenerate endpoint in api/routers/onboarding.py
- [ ] T047 [US2] Implement PUT /api/onboarding/sample-data/extend endpoint (extend expiry) in api/routers/onboarding.py
- [ ] T048 [P] [US2] Create sample data manager UI component in frontend/js/sample-data-manager.js
- [ ] T049 [US2] Add "Generate Sample Data" button in wizard completion screen in frontend/js/onboarding-wizard.js
- [ ] T050 [US2] Add "Clear Sample Data" button in onboarding dashboard in frontend/js/onboarding-dashboard.js
- [ ] T051 [US2] Add sample data visual indicators (badges, background colors) in frontend/css/styles.css
- [ ] T052 [US2] Add sample data expiry reminder notification logic in frontend/js/app.js
- [ ] T053 [US2] Create cleanup cron script for expired sample data in scripts/cleanup_expired_sample_data.py
- [ ] T054 [US2] Add i18n translations for sample data UI and messages in locales/*/onboarding.json

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - wizard completes AND sample data generates/clears successfully

---

## Phase 5: User Story 3 - Track Onboarding Progress with Checklist (Priority: P2)

**Goal**: Administrator sees 6-task checklist with visual progress, quick action links, and real-time completion detection based on database queries, providing clear path to activation

**Independent Test**: View onboarding dashboard. See checklist with 6 tasks (complete profile, create event, add team, invite volunteers, run schedule, view reports). Complete tasks one by one. Verify checklist updates in real-time. Complete all 6. Verify celebration message.

### Implementation for User Story 3

- [ ] T055 [P] [US3] Implement get_checklist_state method with completion detection in api/services/onboarding_service.py
- [ ] T056 [P] [US3] Implement evaluate_completion_criteria method (state_check type) in api/services/onboarding_service.py
- [ ] T057 [P] [US3] Implement evaluate_completion_criteria method (database_query type) in api/services/onboarding_service.py
- [ ] T058 [P] [US3] Implement evaluate_completion_criteria method (composite_and type) in api/services/onboarding_service.py
- [ ] T059 [P] [US3] Implement mark_task_manually_complete method in api/services/onboarding_service.py
- [ ] T060 [P] [US3] Implement reset_checklist method in api/services/onboarding_service.py
- [ ] T061 [US3] Implement GET /api/onboarding/checklist endpoint per contracts/checklist-api.md in api/routers/onboarding.py
- [ ] T062 [US3] Implement PUT /api/onboarding/checklist/{task_id} endpoint (manual override) in api/routers/onboarding.py
- [ ] T063 [US3] Implement POST /api/onboarding/checklist/reset endpoint in api/routers/onboarding.py
- [ ] T064 [US3] Implement GET /api/onboarding/checklist/tasks/{task_id} endpoint in api/routers/onboarding.py
- [ ] T065 [US3] Implement GET /api/onboarding/checklist/history endpoint in api/routers/onboarding.py
- [ ] T066 [P] [US3] Create checklist UI component in frontend/js/onboarding-dashboard.js
- [ ] T067 [US3] Add checklist progress bar with percentage in frontend/js/onboarding-dashboard.js
- [ ] T068 [US3] Add quick action buttons linking to incomplete tasks in frontend/js/onboarding-dashboard.js
- [ ] T069 [US3] Add real-time checklist refresh logic on navigation in frontend/js/onboarding-dashboard.js
- [ ] T070 [US3] Add checklist completion celebration modal in frontend/js/onboarding-dashboard.js
- [ ] T071 [US3] Create checklist CSS styles with icons and progress animation in frontend/css/checklist.css
- [ ] T072 [US3] Add i18n translations for checklist tasks and messages in locales/*/onboarding.json

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - wizard, sample data, and checklist all functional

---

## Phase 6: User Story 4 - Learn Features with Interactive Tutorials (Priority: P2)

**Goal**: Administrator accesses interactive Shepherd.js tutorials with tooltips and overlays for key features (events, teams, solver) triggered automatically or via help menu, reducing learning curve

**Independent Test**: Navigate to events page for first time. Observe automatic tutorial overlay with tooltips. Click through tutorial steps. Verify completion tracked. Access help menu. Select "Replay Event Tutorial". Verify tutorial replays.

### Implementation for User Story 4

- [ ] T073 [P] [US4] Create TutorialService class for tutorial state management in api/services/tutorial_service.py
- [ ] T074 [P] [US4] Implement track_tutorial_start method in api/services/tutorial_service.py
- [ ] T075 [P] [US4] Implement track_tutorial_completion method in api/services/tutorial_service.py
- [ ] T076 [P] [US4] Implement track_tutorial_skip method in api/services/tutorial_service.py
- [ ] T077 [P] [US4] Implement get_tutorial_completions method in api/services/tutorial_service.py
- [ ] T078 [US4] Create tutorial state tracking endpoints in api/routers/onboarding.py
- [ ] T079 [P] [US4] Create Shepherd.js tutorial integration wrapper in frontend/js/tutorial-overlay.js
- [ ] T080 [P] [US4] Define events_intro tutorial with 4 steps in frontend/js/tutorial-overlay.js
- [ ] T081 [P] [US4] Define teams_setup tutorial with 3 steps in frontend/js/tutorial-overlay.js
- [ ] T082 [P] [US4] Define availability_management tutorial with 5 steps in frontend/js/tutorial-overlay.js
- [ ] T083 [P] [US4] Define solver_run tutorial with 6 steps in frontend/js/tutorial-overlay.js
- [ ] T084 [P] [US4] Define schedule_export tutorial with 3 steps in frontend/js/tutorial-overlay.js
- [ ] T085 [US4] Add auto-launch tutorial logic on first feature access in frontend/js/tutorial-overlay.js
- [ ] T086 [US4] Add tutorial replay functionality in help menu in frontend/js/app.js
- [ ] T087 [US4] Add tutorial completion status indicators in help menu in frontend/js/app.js
- [ ] T088 [US4] Create tutorial CSS styles and Shepherd.js theme customization in frontend/css/tutorial-overlay.css
- [ ] T089 [US4] Add i18n translations for tutorial steps and tooltips in locales/*/onboarding.json

**Checkpoint**: User Stories 1-4 complete - wizard, sample data, checklist, and tutorials all working

---

## Phase 7: User Story 5 - Access Quick Start Videos and Documentation (Priority: P2)

**Goal**: Administrator watches 2-3 minute quick start videos demonstrating key workflows with HTML5 video player controls and documentation links

**Independent Test**: Access onboarding dashboard. View "Quick Start Videos" section with 5 video cards. Click "How to Run the Solver". Verify video plays with controls. Close video. Click "View Full Documentation". Verify docs open in new tab.

### Implementation for User Story 5

- [ ] T090 [P] [US5] Create QuickStartVideos class for video management in frontend/js/onboarding-dashboard.js
- [ ] T091 [P] [US5] Add 5 YouTube video embeds (create_event, invite_volunteers, run_solver, manage_schedules, advanced_features) in frontend/videos/ (or links)
- [ ] T092 [P] [US5] Implement video player modal with HTML5 controls in frontend/js/onboarding-dashboard.js
- [ ] T093 [US5] Add video chapter outline with timestamps in frontend/js/onboarding-dashboard.js
- [ ] T094 [US5] Add "View Documentation" links in video descriptions in frontend/js/onboarding-dashboard.js
- [ ] T095 [US5] Track video play events via analytics in frontend/js/onboarding-dashboard.js
- [ ] T096 [US5] Track video completion events via analytics in frontend/js/onboarding-dashboard.js
- [ ] T097 [US5] Add video player CSS styles and responsive design in frontend/css/onboarding-dashboard.css
- [ ] T098 [US5] Add fallback to animated GIFs if video fails to load in frontend/js/onboarding-dashboard.js
- [ ] T099 [US5] Add i18n translations for video titles and descriptions in locales/*/onboarding.json

**Checkpoint**: User Stories 1-5 complete - wizard, sample data, checklist, tutorials, and videos all working

---

## Phase 8: User Story 6 - Progressive Feature Disclosure (Priority: P3)

**Goal**: Administrator experiences gradual revelation of advanced features (recurring events, manual editing, SMS) after reaching proficiency milestones, preventing overwhelming complexity

**Independent Test**: New admin completes basic onboarding. Verify advanced features hidden with lock icons. Create 5 events and run solver 3 times. Verify system detects proficiency. Verify in-app notification "You've unlocked Recurring Events!". Verify features now accessible.

### Implementation for User Story 6

- [ ] T100 [P] [US6] Define FEATURE_MILESTONES constant with unlock criteria in api/services/onboarding_service.py
- [ ] T101 [P] [US6] Implement check_proficiency_milestones method in api/services/onboarding_service.py
- [ ] T102 [P] [US6] Implement unlock_feature method in api/services/onboarding_service.py
- [ ] T103 [P] [US6] Implement get_unlocked_features method in api/services/onboarding_service.py
- [ ] T104 [US6] Create feature unlock detection endpoints in api/routers/onboarding.py
- [ ] T105 [P] [US6] Add feature lock/unlock UI logic in frontend/js/app.js
- [ ] T106 [US6] Add lock icons and tooltips to advanced features in navigation in frontend/js/app.js
- [ ] T107 [US6] Add feature unlock notification toasts in frontend/js/app.js
- [ ] T108 [US6] Add "Show All Features" toggle in settings in frontend/js/app.js
- [ ] T109 [US6] Track feature unlock analytics events in frontend/js/app.js
- [ ] T110 [US6] Add i18n translations for feature unlock messages in locales/*/onboarding.json

**Checkpoint**: User Stories 1-6 complete - progressive disclosure now working

---

## Phase 9: User Story 7 - Skip Onboarding for Experienced Users (Priority: P3)

**Goal**: Experienced administrator skips wizard via "Skip Onboarding" link, accesses full feature set immediately, with option to restart wizard later if needed

**Independent Test**: Create new organization. On wizard welcome screen, click "Skip Onboarding - I'm Experienced". Confirm skip in dialog. Verify navigation to full dashboard with all features unlocked. Access help menu. Verify "Restart Onboarding" option available.

### Implementation for User Story 7

- [ ] T111 [P] [US7] Implement skip_wizard method in api/services/onboarding_service.py
- [ ] T112 [P] [US7] Implement reset_wizard method in api/services/onboarding_service.py
- [ ] T113 [US7] Implement POST /api/onboarding/wizard/skip endpoint per contracts/wizard-api.md in api/routers/onboarding.py
- [ ] T114 [US7] Implement POST /api/onboarding/wizard/reset endpoint in api/routers/onboarding.py
- [ ] T115 [P] [US7] Add "Skip Onboarding" link to wizard welcome screen in frontend/js/onboarding-wizard.js
- [ ] T116 [US7] Add skip confirmation dialog with warning in frontend/js/onboarding-wizard.js
- [ ] T117 [US7] Add "Restart Onboarding" option in help menu in frontend/js/app.js
- [ ] T118 [US7] Add "Jump to Wizard Section" menu for selective restart in frontend/js/app.js
- [ ] T119 [US7] Track wizard skip analytics events in frontend/js/onboarding-wizard.js
- [ ] T120 [US7] Add i18n translations for skip/restart options in locales/*/onboarding.json

**Checkpoint**: User Stories 1-7 complete - skip/restart functionality working

---

## Phase 10: User Story 8 - Onboarding Analytics and Optimization (Priority: P3)

**Goal**: System tracks onboarding metrics (completion rate, drop-offs, time-to-first-value, feature adoption) enabling product team to optimize onboarding flow based on data

**Independent Test**: Administrators complete various onboarding paths. Access admin analytics dashboard. View funnel showing 65% completion rate, 18min avg time, 40% drop-off at "invite volunteers" step. Verify cohort analysis showing improvement trends.

### Implementation for User Story 8

- [ ] T121 [P] [US8] Implement track_analytics_event method in api/services/analytics_service.py
- [ ] T122 [P] [US8] Implement get_onboarding_funnel method calculating completion rates in api/services/analytics_service.py
- [ ] T123 [P] [US8] Implement get_completion_time_distribution method with percentiles in api/services/analytics_service.py
- [ ] T124 [P] [US8] Implement get_feature_usage_report method in api/services/analytics_service.py
- [ ] T125 [P] [US8] Implement get_cohort_analysis method grouping by signup date in api/services/analytics_service.py
- [ ] T126 [US8] Implement POST /api/analytics/onboarding-events endpoint per contracts/analytics-api.md in api/routers/analytics.py
- [ ] T127 [US8] Implement GET /api/analytics/onboarding-funnel endpoint in api/routers/analytics.py
- [ ] T128 [US8] Implement GET /api/analytics/onboarding-completion-time endpoint in api/routers/analytics.py
- [ ] T129 [US8] Implement GET /api/analytics/onboarding-features endpoint in api/routers/analytics.py
- [ ] T130 [US8] Implement GET /api/analytics/onboarding-cohorts endpoint in api/routers/analytics.py
- [ ] T131 [P] [US8] Create analytics tracking wrapper in frontend/js/analytics.js
- [ ] T132 [US8] Add auto-tracking for wizard step completions in frontend/js/onboarding-wizard.js
- [ ] T133 [US8] Add auto-tracking for sample data events in frontend/js/sample-data-manager.js
- [ ] T134 [US8] Add auto-tracking for tutorial events in frontend/js/tutorial-overlay.js
- [ ] T135 [US8] Add auto-tracking for video play events in frontend/js/onboarding-dashboard.js
- [ ] T136 [US8] Add auto-tracking for checklist task completions in frontend/js/onboarding-dashboard.js
- [ ] T137 [US8] Create admin analytics dashboard UI in frontend/js/admin-analytics.js
- [ ] T138 [US8] Add funnel visualization chart in frontend/js/admin-analytics.js
- [ ] T139 [US8] Add cohort analysis table in frontend/js/admin-analytics.js

**Checkpoint**: All user stories complete - full onboarding system with analytics operational

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T140 [P] Add comprehensive error handling across all onboarding endpoints in api/routers/onboarding.py
- [ ] T141 [P] Add request/response logging for debugging in api/routers/onboarding.py
- [ ] T142 [P] Add rate limiting to onboarding endpoints (100 req/min) in api/routers/onboarding.py
- [ ] T143 [P] Optimize database queries with indexes on organization_id in migrations/
- [ ] T144 [P] Add caching for wizard state (Redis, 1hr TTL) in api/services/onboarding_service.py
- [ ] T145 [P] Add caching for checklist state (Redis, 30s TTL) in api/services/onboarding_service.py
- [ ] T146 [P] Validate all i18n translations complete for 6 languages in locales/
- [ ] T147 [P] Add mobile responsive CSS for onboarding UI in frontend/css/
- [ ] T148 [P] Add accessibility attributes (ARIA labels, keyboard navigation) to wizard in frontend/js/onboarding-wizard.js
- [ ] T149 [P] Add error boundary components for graceful failure handling in frontend/js/
- [ ] T150 [P] Optimize Shepherd.js bundle size and lazy loading in frontend/js/
- [ ] T151 Code cleanup and refactoring across onboarding services
- [ ] T152 Security review of onboarding endpoints (RBAC enforcement)
- [ ] T153 Performance testing with 100 concurrent wizard sessions
- [ ] T154 Run quickstart.md validation (5-minute setup test)
- [ ] T155 Update API documentation with onboarding endpoints
- [ ] T156 Create onboarding feature demo video for internal testing
- [ ] T157 Final cross-browser testing (Chrome, Firefox, Safari, Edge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P2) → US6 (P3) → US7 (P3) → US8 (P3)
- **Polish (Phase 11)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1) - Setup Wizard**: Can start after Foundational - No dependencies on other stories
- **US2 (P1) - Sample Data**: Can start after Foundational - Integrates with US1 (generates data after wizard completes) but independently testable
- **US3 (P2) - Checklist**: Can start after Foundational - Integrates with US1 (wizard completion = checklist task) but independently testable
- **US4 (P2) - Tutorials**: Can start after Foundational - No dependencies on other stories, standalone feature
- **US5 (P2) - Videos**: Can start after Foundational - No dependencies on other stories, standalone feature
- **US6 (P3) - Progressive Disclosure**: Requires US1 complete (wizard provides initial proficiency data)
- **US7 (P3) - Skip Wizard**: Requires US1 complete (skip alternative to wizard flow)
- **US8 (P3) - Analytics**: Can start after Foundational - Tracks events from all stories but doesn't block them

### Within Each User Story

- Service layer methods before API endpoints
- API endpoints before frontend UI components
- Frontend components before integration/polish
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T001, T002, T003 can all run in parallel
- **Foundational (Phase 2)**: T009-T012 (model classes) can run in parallel
- **Within US1**: T017-T021 (service methods) can run in parallel, T026-T027 (frontend) can run in parallel
- **Within US2**: T035-T039 (generator methods) can run in parallel, T048 (UI) can run independently
- **Within US3**: T055-T060 (service methods) can run in parallel
- **Within US4**: T073-T077 (service methods) can run in parallel, T080-T084 (tutorial definitions) can run in parallel
- **Within US5**: T090-T091 (video setup) can run in parallel
- **Within US6**: T100-T103 (service methods) can run in parallel, T105-T106 (UI) can run in parallel
- **Within US7**: T111-T112 (service methods) can run in parallel, T115-T116 (UI) can run in parallel
- **Within US8**: T121-T125 (service methods) can run in parallel, T131-T136 (tracking) can run in parallel
- **Polish (Phase 11)**: T140-T150 can all run in parallel
- **Different user stories**: US3, US4, US5 can all be worked on in parallel after Foundational completes

---

## Parallel Example: User Story 1 (Setup Wizard)

```bash
# Launch all service methods for US1 together:
Task: "Implement create_wizard_state method in api/services/onboarding_service.py"
Task: "Implement get_wizard_state method in api/services/onboarding_service.py"
Task: "Implement update_wizard_step_data method in api/services/onboarding_service.py"
Task: "Implement advance_wizard_step method in api/services/onboarding_service.py"
Task: "Implement complete_wizard method in api/services/onboarding_service.py"

# Launch frontend components for US1 together:
Task: "Create onboarding wizard UI component in frontend/js/onboarding-wizard.js"
Task: "Create wizard CSS styles in frontend/css/wizard.css"
```

---

## Parallel Example: User Story 4 (Interactive Tutorials)

```bash
# Launch all tutorial definitions together:
Task: "Define events_intro tutorial with 4 steps in frontend/js/tutorial-overlay.js"
Task: "Define teams_setup tutorial with 3 steps in frontend/js/tutorial-overlay.js"
Task: "Define availability_management tutorial with 5 steps in frontend/js/tutorial-overlay.js"
Task: "Define solver_run tutorial with 6 steps in frontend/js/tutorial-overlay.js"
Task: "Define schedule_export tutorial with 3 steps in frontend/js/tutorial-overlay.js"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T016) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 - Setup Wizard (T017-T034)
4. Complete Phase 4: User Story 2 - Sample Data (T035-T054)
5. **STOP and VALIDATE**: Test wizard + sample data flow end-to-end
6. Deploy/demo if ready - New users can complete guided setup with examples!

**Why this MVP?**: US1 + US2 provide core onboarding value - guided setup with hands-on examples. Reduces time-to-first-value from 2 hours to 15 minutes. Other stories enhance experience but these two are essential.

### Incremental Delivery

1. MVP: Setup + Foundational + US1 + US2 → Deploy (Core onboarding working)
2. Add US3 (Checklist) → Deploy (Now with progress tracking)
3. Add US4 (Tutorials) → Deploy (Now with interactive learning)
4. Add US5 (Videos) → Deploy (Now with video content)
5. Add US6 (Progressive Disclosure) → Deploy (Now with smart feature unlocking)
6. Add US7 (Skip Option) → Deploy (Now with power user support)
7. Add US8 (Analytics) → Deploy (Now with data-driven optimization)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (Phase 1) + Foundational (Phase 2) together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Setup Wizard)
   - **Developer B**: User Story 2 (Sample Data)
   - **Developer C**: User Story 3 (Checklist)
   - **Developer D**: User Story 4 (Tutorials)
3. Stories complete independently, integrate naturally
4. Continue with US5-US8 in priority order

---

## Success Metrics

Track these metrics to measure onboarding success:

- **Activation Rate**: Target 65% (from 35%) completing first schedule within 7 days
- **Time-to-First-Value**: Target 15 minutes (from 2 hours) via guided wizard
- **Wizard Completion**: Target >75% completion with <20% drop-off per step
- **Sample Data Adoption**: Target 60% of new orgs generating sample data
- **Checklist Completion**: Target 85% completing all 6 tasks within 7 days
- **Tutorial Engagement**: Target 50% viewing at least one tutorial
- **Video Engagement**: Target 40% watching at least one complete video
- **Support Ticket Reduction**: Target 70% reduction in new user confusion tickets
- **Feature Discovery**: Target 3x faster (7 days vs 21 days) for advanced features
- **Skip Rate**: Target <15% (most users find onboarding valuable)
- **Satisfaction**: Target 8.0/10 rating with 80% "helpful" or "very helpful"
- **7-Day Retention**: Target 85% for completers vs 45% for skippers

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- Tests not explicitly requested in spec - focusing on implementation
- MVP = US1 + US2 provides core value for 65% activation goal
- All advanced stories (US6-US8) are enhancements, not blockers
- Avoid: vague tasks, same file conflicts, tight cross-story dependencies

---

**Total Tasks**: 157 tasks
**MVP Tasks**: 54 tasks (T001-T054 covering Setup, Foundational, US1, US2)
**Parallel Opportunities**: 60+ parallelizable tasks marked with [P]
**Estimated Implementation Time**: 8-12 weeks for full feature, 3-4 weeks for MVP

---

**Generated**: 2025-10-23
**Feature**: 020 - User Onboarding System
**Status**: Ready for Implementation
