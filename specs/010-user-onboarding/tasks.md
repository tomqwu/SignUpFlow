# Tasks: User Onboarding System

**Input**: Design documents from `/specs/010-user-onboarding/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: E2E tests requested in plan.md Constitution Check

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `api/` (backend), `frontend/` (frontend)
- Paths based on plan.md structure (SignUpFlow architecture)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and onboarding infrastructure

- [X] T001 Create OnboardingProgress model in api/models.py with fields: user_id, org_id, wizard_step_completed (int), checklist_state (JSON), tutorials_completed (JSON array), features_unlocked (JSON array), created_at, updated_at
- [X] T002 Create database migration for onboarding_progress table
- [X] T003 [P] Add Intro.js dependency to frontend/package.json for tutorial overlays
- [X] T004 [P] Create frontend/js/onboarding-wizard.js skeleton structure
- [X] T005 [P] Create frontend/js/onboarding-checklist.js skeleton structure
- [X] T006 [P] Create frontend/js/tutorial-overlays.js skeleton structure
- [X] T007 [P] Create frontend/js/feature-unlocks.js skeleton structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core onboarding infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create onboarding API router in api/routers/onboarding.py with base structure
- [X] T009 Implement GET /api/onboarding/progress endpoint returning OnboardingProgress for current user
- [X] T010 Implement PUT /api/onboarding/progress endpoint for updating wizard/checklist state
- [X] T011 [P] Create sample data generator service in api/services/sample_data_generator.py with generate_sample_data() function
- [X] T012 [P] Create onboarding dashboard HTML template in frontend/index.html (dashboard section)
- [X] T013 Initialize OnboardingProgress record on organization creation in api/routers/auth.py signup endpoint

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Guided Setup Wizard (Priority: P1) 🎯 MVP

**Goal**: 4-step wizard (Profile → Event → Team → Invitations) with progress saving and resume capability

**Independent Test**: Create new account, complete wizard steps, verify data saved. Log out mid-wizard, log back in, verify resume at correct step.

### Tests for User Story 1

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] E2E test for complete wizard flow in tests/e2e/test_onboarding_wizard.py::test_wizard_complete_flow
- [X] T015 [P] [US1] E2E test for wizard resume in tests/e2e/test_onboarding_wizard.py::test_wizard_resume_after_logout
- [X] T016 [P] [US1] Integration test for wizard progress saving in tests/integration/test_onboarding.py::test_save_wizard_progress

### Implementation for User Story 1

- [X] T017 [US1] Implement wizard Step 1 (Organization Profile) UI in frontend/js/onboarding-wizard.js::renderStep1()
- [X] T018 [US1] Implement wizard Step 2 (First Event) UI in frontend/js/onboarding-wizard.js::renderStep2()
- [X] T019 [US1] Implement wizard Step 3 (First Team) UI in frontend/js/onboarding-wizard.js::renderStep3()
- [X] T020 [US1] Implement wizard Step 4 (Invite Volunteers) UI in frontend/js/onboarding-wizard.js::renderStep4()
- [X] T021 [US1] Implement wizard progress bar component in frontend/js/onboarding-wizard.js::updateProgressBar()
- [X] T022 [US1] Implement wizard step validation in frontend/js/onboarding-wizard.js::validateStep()
- [X] T023 [US1] Implement wizard auto-save on step completion in frontend/js/onboarding-wizard.js::saveProgress()
- [X] T024 [US1] Implement wizard resume logic on login in frontend/js/onboarding-wizard.js::resumeWizard()
- [X] T025 [US1] Implement "Save and Continue Later" button in frontend/js/onboarding-wizard.js::saveLater()
- [X] T026 [US1] Implement wizard completion redirect to onboarding dashboard in frontend/js/onboarding-wizard.js::completeWizard()
- [X] T027 [US1] Add wizard completion success message display in frontend/js/onboarding-wizard.js::showSuccessMessage()

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Sample Data Exploration (Priority: P1)

**Goal**: Generate sample data (5 events, 3 teams, 10 volunteers, 1 schedule) with "SAMPLE" badges and one-click cleanup

**Independent Test**: Click "Generate Sample Data", verify sample records created with badges. Click "Clear Sample Data", verify only sample records deleted.

### Tests for User Story 2

- [ ] T028 [P] [US2] E2E test for sample data generation in tests/e2e/test_onboarding_wizard.py::test_generate_sample_data
- [ ] T029 [P] [US2] E2E test for sample data cleanup in tests/e2e/test_onboarding_wizard.py::test_clear_sample_data
- [ ] T030 [P] [US2] Integration test for sample data flagging in tests/integration/test_onboarding.py::test_sample_data_flag

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement generate_sample_events() in api/services/sample_data_generator.py creating 5 events with is_sample=True flag
- [ ] T032 [P] [US2] Implement generate_sample_teams() in api/services/sample_data_generator.py creating 3 teams with is_sample=True flag
- [ ] T033 [P] [US2] Implement generate_sample_volunteers() in api/services/sample_data_generator.py creating 10 volunteers with is_sample=True flag
- [ ] T034 [US2] Implement generate_sample_schedule() in api/services/sample_data_generator.py creating 1 complete schedule
- [ ] T035 [US2] Create POST /api/onboarding/sample-data endpoint in api/routers/onboarding.py calling sample generator
- [ ] T036 [US2] Create DELETE /api/onboarding/sample-data endpoint in api/routers/onboarding.py removing is_sample=True records
- [ ] T037 [US2] Add is_sample boolean field to Event, Team, Person models in api/models.py
- [ ] T038 [US2] Implement "SAMPLE" badge display in event list UI in frontend/js/app-admin.js::renderEventWithBadge()
- [ ] T039 [US2] Implement "SAMPLE" badge display in team list UI in frontend/js/app-admin.js::renderTeamWithBadge()
- [ ] T040 [US2] Implement "SAMPLE" badge display in volunteer list UI in frontend/js/app-admin.js::renderPersonWithBadge()
- [ ] T041 [US2] Implement "Generate Sample Data" button in onboarding dashboard in frontend/index.html
- [ ] T042 [US2] Implement "Clear Sample Data" button with confirmation dialog in frontend/js/onboarding-wizard.js::clearSampleData()
- [ ] T043 [US2] Display sample data deletion count in success message in frontend/js/onboarding-wizard.js::showDeletionCount()

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Getting Started Checklist (Priority: P1)

**Goal**: 6-task checklist (Complete Profile, Create Event, Add Team, Invite Volunteers, Run Solver, View Reports) with progress tracking

**Independent Test**: Complete each checklist item, verify checkmark appears and progress percentage updates. Click checklist item, verify navigation to relevant section.

### Tests for User Story 3

- [ ] T044 [P] [US3] E2E test for checklist display in tests/e2e/test_onboarding_wizard.py::test_checklist_display
- [ ] T045 [P] [US3] E2E test for checklist progress update in tests/e2e/test_onboarding_wizard.py::test_checklist_progress_update
- [ ] T046 [P] [US3] E2E test for checklist navigation in tests/e2e/test_onboarding_wizard.py::test_checklist_navigation

### Implementation for User Story 3

- [ ] T047 [US3] Implement checklist widget UI in frontend/js/onboarding-checklist.js::renderChecklist()
- [ ] T048 [US3] Implement checklist item component in frontend/js/onboarding-checklist.js::renderChecklistItem()
- [ ] T049 [US3] Implement checklist progress calculation in frontend/js/onboarding-checklist.js::calculateProgress()
- [ ] T050 [US3] Implement checklist state update on profile completion in frontend/js/app-admin.js::updateChecklistOnProfileComplete()
- [ ] T051 [US3] Implement checklist state update on event creation in frontend/js/app-admin.js::updateChecklistOnEventCreate()
- [ ] T052 [US3] Implement checklist state update on team creation in frontend/js/app-admin.js::updateChecklistOnTeamCreate()
- [ ] T053 [US3] Implement checklist state update on volunteer invitation in frontend/js/app-admin.js::updateChecklistOnInvite()
- [ ] T054 [US3] Implement checklist state update on solver run in frontend/js/app-admin.js::updateChecklistOnSolverRun()
- [ ] T055 [US3] Implement checklist state update on reports view in frontend/js/app-admin.js::updateChecklistOnReportsView()
- [ ] T056 [US3] Implement checklist item click navigation in frontend/js/onboarding-checklist.js::navigateToSection()
- [ ] T057 [US3] Implement checklist completion celebration (100%) in frontend/js/onboarding-checklist.js::showCompletionCelebration()
- [ ] T058 [US3] Implement "Hide Checklist" option on 100% completion in frontend/js/onboarding-checklist.js::hideChecklist()
- [ ] T059 [US3] Add checklist state persistence to OnboardingProgress in api/routers/onboarding.py

**Checkpoint**: All P1 user stories should now be independently functional

---

## Phase 6: User Story 4 - Interactive Tutorials (Priority: P2)

**Goal**: Contextual tutorials with spotlight overlays for Event Creation, Team Management, Solver, Invitations

**Independent Test**: Trigger tutorial on first feature use, complete tutorial steps, dismiss tutorial, replay from Help menu.

### Tests for User Story 4

- [ ] T060 [P] [US4] E2E test for tutorial trigger in tests/e2e/test_onboarding_wizard.py::test_tutorial_trigger
- [ ] T061 [P] [US4] E2E test for tutorial dismissal in tests/e2e/test_onboarding_wizard.py::test_tutorial_dismissal
- [ ] T062 [P] [US4] E2E test for tutorial replay in tests/e2e/test_onboarding_wizard.py::test_tutorial_replay

### Implementation for User Story 4

- [ ] T063 [US4] Initialize Intro.js library in frontend/js/tutorial-overlays.js
- [ ] T064 [US4] Create event creation tutorial steps in frontend/js/tutorial-overlays.js::eventCreationTutorial()
- [ ] T065 [US4] Create team management tutorial steps in frontend/js/tutorial-overlays.js::teamManagementTutorial()
- [ ] T066 [US4] Create solver tutorial steps in frontend/js/tutorial-overlays.js::solverTutorial()
- [ ] T067 [US4] Create invitations tutorial steps in frontend/js/tutorial-overlays.js::invitationsTutorial()
- [ ] T068 [US4] Implement tutorial trigger logic on first feature use in frontend/js/tutorial-overlays.js::triggerTutorialIfFirstUse()
- [ ] T069 [US4] Implement tutorial completion tracking in frontend/js/tutorial-overlays.js::markTutorialComplete()
- [ ] T070 [US4] Implement tutorial dismissal with "Don't show again" option in frontend/js/tutorial-overlays.js::dismissTutorial()
- [ ] T071 [US4] Create Help menu in frontend/index.html with Tutorials section
- [ ] T072 [US4] Implement tutorial list display in Help menu in frontend/js/tutorial-overlays.js::showTutorialList()
- [ ] T073 [US4] Implement tutorial replay functionality in frontend/js/tutorial-overlays.js::replayTutorial()
- [ ] T074 [US4] Add tutorials_completed JSON array tracking to OnboardingProgress in api/routers/onboarding.py

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Progressive Feature Disclosure (Priority: P2)

**Goal**: Hide advanced features (Recurring Events, Manual Editing, SMS) until unlock conditions met (3 events, 1 solver run, 5 volunteers)

**Independent Test**: Meet unlock condition (create 3rd event), verify unlock notification appears, verify feature now visible with "New!" badge.

### Tests for User Story 5

- [ ] T075 [P] [US5] E2E test for recurring events unlock in tests/e2e/test_onboarding_wizard.py::test_recurring_events_unlock
- [ ] T076 [P] [US5] E2E test for manual editing unlock in tests/e2e/test_onboarding_wizard.py::test_manual_editing_unlock
- [ ] T077 [P] [US5] E2E test for SMS unlock in tests/e2e/test_onboarding_wizard.py::test_sms_unlock

### Implementation for User Story 5

- [ ] T078 [US5] Implement feature unlock tracking in frontend/js/feature-unlocks.js::checkUnlockConditions()
- [ ] T079 [US5] Implement recurring events unlock condition (3 events) in frontend/js/feature-unlocks.js::checkRecurringEventsUnlock()
- [ ] T080 [US5] Implement manual editing unlock condition (1 solver run) in frontend/js/feature-unlocks.js::checkManualEditingUnlock()
- [ ] T081 [US5] Implement SMS unlock condition (5 volunteers) in frontend/js/feature-unlocks.js::checkSMSUnlock()
- [ ] T082 [US5] Implement unlock notification display in frontend/js/feature-unlocks.js::showUnlockNotification()
- [ ] T083 [US5] Hide recurring events option initially in frontend/js/app-admin.js::hideRecurringEventsOption()
- [ ] T084 [US5] Reveal recurring events option on unlock in frontend/js/feature-unlocks.js::revealRecurringEvents()
- [ ] T085 [US5] Hide manual editing option initially in frontend/js/app-admin.js::hideManualEditingOption()
- [ ] T086 [US5] Reveal manual editing option on unlock in frontend/js/feature-unlocks.js::revealManualEditing()
- [ ] T087 [US5] Hide SMS notifications option initially in frontend/js/app-admin.js::hideSMSOption()
- [ ] T088 [US5] Reveal SMS notifications option on unlock in frontend/js/feature-unlocks.js::revealSMS()
- [ ] T089 [US5] Implement "New!" badge display for 7 days after unlock in frontend/js/feature-unlocks.js::showNewBadge()
- [ ] T090 [US5] Add features_unlocked JSON array tracking to OnboardingProgress in api/routers/onboarding.py

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Onboarding Dashboard (Priority: P2)

**Goal**: Dedicated dashboard with Next Actions, tutorial videos (2-3 min), and documentation links

**Independent Test**: View onboarding dashboard, verify Next Actions panel shows incomplete tasks, play video tutorial, click documentation links.

### Tests for User Story 6

- [ ] T091 [P] [US6] E2E test for onboarding dashboard display in tests/e2e/test_onboarding_wizard.py::test_onboarding_dashboard_display
- [ ] T092 [P] [US6] E2E test for next actions panel in tests/e2e/test_onboarding_wizard.py::test_next_actions_panel
- [ ] T093 [P] [US6] E2E test for video tutorials in tests/e2e/test_onboarding_wizard.py::test_video_tutorials

### Implementation for User Story 6

- [ ] T094 [US6] Create onboarding dashboard route in frontend/js/router.js
- [ ] T095 [US6] Implement onboarding dashboard HTML template in frontend/index.html::onboardingDashboard
- [ ] T096 [US6] Implement Next Actions panel UI in frontend/js/onboarding-wizard.js::renderNextActionsPanel()
- [ ] T097 [US6] Implement Next Actions logic (show top 3 incomplete tasks) in frontend/js/onboarding-wizard.js::calculateNextActions()
- [ ] T098 [US6] Create video tutorials section HTML in frontend/index.html::videoTutorialsSection
- [ ] T099 [US6] Implement video tutorial cards with thumbnails in frontend/js/onboarding-wizard.js::renderVideoCards()
- [ ] T100 [US6] Embed YouTube/Vimeo videos using iframe in frontend/js/onboarding-wizard.js::embedVideo()
- [ ] T101 [US6] Implement video watch tracking in frontend/js/onboarding-wizard.js::trackVideoWatched()
- [ ] T102 [US6] Implement "Mark as Watched" button in frontend/js/onboarding-wizard.js::markVideoWatched()
- [ ] T103 [US6] Create Resources section HTML in frontend/index.html::resourcesSection
- [ ] T104 [US6] Add documentation links to Resources section (Documentation, FAQ, Schedule Call, Contact Support)
- [ ] T105 [US6] Implement dashboard adaptation based on progress in frontend/js/onboarding-wizard.js::adaptDashboard()
- [ ] T106 [US6] Add "Getting Started" menu item in frontend/index.html main navigation

**Checkpoint**: At this point, User Stories 1-6 should all work independently

---

## Phase 9: User Story 7 - Skip Onboarding Option (Priority: P3)

**Goal**: "Skip Setup" option on wizard first screen with confirmation dialog, re-enable capability in Settings

**Independent Test**: Click "Skip Setup", confirm action, verify full feature access. Re-enable onboarding in Settings, verify checklist shows based on existing data.

### Tests for User Story 7

- [ ] T107 [P] [US7] E2E test for skip onboarding in tests/e2e/test_onboarding_wizard.py::test_skip_onboarding
- [ ] T108 [P] [US7] E2E test for re-enable onboarding in tests/e2e/test_onboarding_wizard.py::test_reenable_onboarding

### Implementation for User Story 7

- [ ] T109 [US7] Add "Skip Setup" link to wizard Step 1 in frontend/js/onboarding-wizard.js::renderSkipSetupLink()
- [ ] T110 [US7] Implement skip confirmation dialog in frontend/js/onboarding-wizard.js::showSkipConfirmation()
- [ ] T111 [US7] Implement skip action (hide wizard, disable tutorials) in frontend/js/onboarding-wizard.js::skipOnboarding()
- [ ] T112 [US7] Add "Enable Onboarding" toggle in Settings page in frontend/index.html::settingsSection
- [ ] T113 [US7] Implement re-enable onboarding action in frontend/js/app-admin.js::reenableOnboarding()
- [ ] T114 [US7] Implement retroactive checklist update on re-enable in frontend/js/onboarding-checklist.js::retroactiveUpdate()
- [ ] T115 [US7] Add onboarding_skipped boolean field to OnboardingProgress in api/models.py
- [ ] T116 [US7] Update onboarding_skipped on skip action in api/routers/onboarding.py::skipOnboarding()
- [ ] T117 [US7] Update onboarding_skipped on re-enable in api/routers/onboarding.py::reenableOnboarding()

**Checkpoint**: All user stories should now be independently functional

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T118 [P] Add i18n translations for all onboarding text in locales/en/onboarding.json
- [ ] T119 [P] Add i18n translations for Spanish in locales/es/onboarding.json
- [ ] T120 [P] Implement celebration animations for milestones (first event, first volunteer, first schedule) in frontend/js/onboarding-wizard.js::celebrateMilestone()
- [ ] T121 [P] Add onboarding analytics tracking (completion rate, time to first value, drop-off points) in api/services/analytics_service.py
- [ ] T122 [P] Implement mid-flow browser close recovery (auto-save wizard progress) in frontend/js/onboarding-wizard.js::autoSaveProgress()
- [ ] T123 [P] Add validation for sample data conflicts (preserve real data on sample cleanup) in api/services/sample_data_generator.py::validateSampleCleanup()
- [ ] T124 [P] Implement language switch support mid-onboarding in frontend/js/i18n.js::switchLanguageMidOnboarding()
- [ ] T125 Code cleanup and refactoring for onboarding modules
- [ ] T126 Performance optimization: wizard step transitions <500ms, sample data generation <1s, checklist update <200ms
- [ ] T127 Security review: ensure onboarding progress scoped to user_id, validate org_id on all operations
- [ ] T128 Documentation: Add onboarding developer guide to docs/ONBOARDING_IMPLEMENTATION.md
- [ ] T129 Documentation: Add onboarding user guide to docs/ONBOARDING_USER_GUIDE.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 (sample data standalone)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 wizard completion but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent tutorials system
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Independent feature unlock system
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Independent dashboard (displays US3 checklist but works without it)
- **User Story 7 (P3)**: Can start after Foundational (Phase 2) - Independent skip/re-enable mechanism

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before API endpoints
- API endpoints before frontend integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T007)
- All Foundational tasks marked [P] can run in parallel (T011-T012)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Sample data generation tasks within US2 marked [P] can run in parallel (T031-T033)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "E2E test for sample data generation in tests/e2e/test_onboarding_wizard.py::test_generate_sample_data"
Task: "E2E test for sample data cleanup in tests/e2e/test_onboarding_wizard.py::test_clear_sample_data"
Task: "Integration test for sample data flagging in tests/integration/test_onboarding.py::test_sample_data_flag"

# Launch all sample generation functions together:
Task: "Implement generate_sample_events() in api/services/sample_data_generator.py"
Task: "Implement generate_sample_teams() in api/services/sample_data_generator.py"
Task: "Implement generate_sample_volunteers() in api/services/sample_data_generator.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only - All P1)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - Guided Setup Wizard (T014-T027)
4. **VALIDATE**: Test wizard independently, verify 4-step flow works
5. Complete Phase 4: User Story 2 - Sample Data Exploration (T028-T043)
6. **VALIDATE**: Test sample data generation and cleanup independently
7. Complete Phase 5: User Story 3 - Getting Started Checklist (T044-T059)
8. **VALIDATE**: Test checklist tracking and navigation independently
9. **STOP and VALIDATE**: Test all 3 P1 stories together (wizard → sample data → checklist integration)
10. Deploy/demo if ready

**MVP Scope**: User Stories 1-3 provide complete onboarding value:
- Guided setup wizard reduces time to first value
- Sample data enables hands-on learning
- Checklist provides clear progress tracking

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic wizard)
3. Add User Story 2 → Test independently → Deploy/Demo (Learning environment)
4. Add User Story 3 → Test independently → Deploy/Demo (Progress tracking - MVP!)
5. Add User Story 4 → Test independently → Deploy/Demo (Interactive tutorials)
6. Add User Story 5 → Test independently → Deploy/Demo (Progressive disclosure)
7. Add User Story 6 → Test independently → Deploy/Demo (Full dashboard)
8. Add User Story 7 → Test independently → Deploy/Demo (Skip option)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - Developer A: User Story 1 - Guided Wizard (T014-T027)
   - Developer B: User Story 2 - Sample Data (T028-T043)
   - Developer C: User Story 3 - Checklist (T044-T059)
3. Stories complete and integrate independently
4. Team continues with P2 stories in parallel:
   - Developer A: User Story 4 - Tutorials (T060-T074)
   - Developer B: User Story 5 - Feature Unlocks (T075-T090)
   - Developer C: User Story 6 - Dashboard (T091-T106)
5. Team completes P3 story together: User Story 7 - Skip Option (T107-T117)

---

## Summary

**Total Tasks**: 129 tasks
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1 - Guided Wizard): 14 tasks
- Phase 4 (US2 - Sample Data): 16 tasks
- Phase 5 (US3 - Checklist): 16 tasks
- Phase 6 (US4 - Tutorials): 15 tasks
- Phase 7 (US5 - Feature Unlocks): 16 tasks
- Phase 8 (US6 - Dashboard): 16 tasks
- Phase 9 (US7 - Skip Option): 11 tasks
- Phase 10 (Polish): 12 tasks

**Parallel Opportunities Identified**: 47 tasks marked [P] can run in parallel
- Setup phase: 5 parallel tasks
- Foundational phase: 2 parallel tasks
- User story tests: 21 parallel tasks (3 per story × 7 stories)
- User story implementations: 19 parallel tasks

**Independent Test Criteria**:
- US1: Complete 4-step wizard, verify data saved, test resume after logout
- US2: Generate sample data, verify badges, clear samples, verify only samples deleted
- US3: Complete checklist items, verify progress updates, test navigation
- US4: Trigger tutorial, complete steps, dismiss, replay from Help menu
- US5: Meet unlock condition, verify notification, verify feature revealed with badge
- US6: View dashboard, verify Next Actions, play video, click links
- US7: Skip onboarding, verify full access, re-enable, verify retroactive checklist

**Suggested MVP Scope**: User Stories 1-3 (Phases 3-5: 46 tasks)
- Provides complete guided onboarding experience
- Enables learning through sample data
- Tracks progress with checklist
- Delivers 80% of user value in 36% of total work

**Format Validation**: ✅ ALL tasks follow checklist format (checkbox, ID, [P] marker where applicable, [Story] label for user story phases, file paths included)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
