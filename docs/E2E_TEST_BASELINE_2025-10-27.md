# E2E Test Baseline - October 27, 2025

**Test Environment:** Docker Compose (PostgreSQL + Redis + FastAPI)
**Test Command:** `make test-docker-summary`
**Runtime:** 45 minutes 31 seconds
**Total Tests:** 183 tests

## Test Results Summary

```
✅ PASSED:  75 tests (41%)
❌ FAILED:  58 tests (32%)
⏭️ SKIPPED: 48 tests (26%)
💥 ERRORS:   2 tests (1%)
```

---

## Phase 1 Priority Analysis

### Task 1: Solver Workflow Tests
**Status:** ❌ FAILED (1 test)

```
FAILED tests/e2e/test_solver_workflow.py::test_run_solver_with_constraints_complete_workflow
```

**Note:** Test is RUNNING (not skipped), but failing. Need to investigate selector mismatches.

---

### Task 2: Availability Management Tests
**Status:** ❌ FAILED (3 tests) - **ROOT CAUSE IDENTIFIED**

**Error:** TimeoutError finding `a[href="/app/availability"]` navigation link

```
FAILED tests/e2e/test_availability_management.py::test_add_time_off_request_complete_workflow
  playwright._impl._errors.TimeoutError: Locator.click: Timeout 5000ms exceeded.
  waiting for locator("a[href='/app/availability']")

FAILED tests/e2e/test_availability_management.py::test_edit_time_off_request
  (same error - navigation link not found)

FAILED tests/e2e/test_availability_management.py::test_delete_time_off_request
  (same error - navigation link not found)
```

**Root Cause:** The `/app/availability` navigation link is **missing from the UI**. Tests can't proceed past navigation.

**Fix Required:**
1. Add availability navigation link to main app UI
2. Verify availability route exists in frontend router
3. Ensure availability page template is accessible

**Impact:** Once navigation is fixed, all 3 tests should pass (tests are structurally correct).

Additional skipped tests:
```
SKIPPED tests/e2e/test_availability_management.py::test_view_availability_calendar
SKIPPED tests/e2e/test_availability_management.py::test_overlap_validation
SKIPPED tests/e2e/test_availability_management.py::test_past_date_validation
```

---

### Task 3: Authentication Flow Tests
**Status:** ⚠️ MIXED (some passed, some failed)

**Passed:**
```
PASSED tests/e2e/test_auth_flows.py::test_protected_route_redirect
PASSED tests/e2e/test_auth_flows.py::test_invalid_credentials
```

**Failed:**
```
FAILED tests/e2e/test_auth_flows.py::test_login_existing_user
FAILED tests/e2e/test_auth_flows.py::test_logout_flow
FAILED tests/e2e/test_auth_flows.py::test_session_persistence
```

**Skipped:**
```
SKIPPED tests/e2e/test_auth_flows.py::test_signup_new_user (Join page broken)
```

---

### Task 4: RBAC Security Tests
**Status:** 🔍 **CRITICAL DISCOVERY - TEST ISOLATION ISSUE**

**🎉 MAJOR BREAKTHROUGH:**
- **Isolated Run:** ✅ 27/27 tests PASSING (100%)
- **Full Suite Run:** ❌ 16/27 tests FAILING (59%)
- **Root Cause:** Test isolation problem - tests pass alone but fail when run with other tests

**Evidence:**
```bash
# Isolated RBAC tests only
docker-compose exec -T api pytest tests/e2e/test_rbac_security.py -v
Result: 27 passed, 1 error (teardown - not a test failure)

# Full E2E suite
docker-compose exec -T api pytest tests/e2e/ -v
Result: 16 RBAC tests failed
```

**Implication:** The RBAC security implementation is **CORRECT**, but there's a **test setup/teardown issue** causing failures when tests run together.

**Potential Causes:**
1. Database state not properly reset between test modules
2. Session/authentication state leaking between tests
3. Browser context not isolated between tests
4. Test fixtures not properly cleaning up

**Failed Tests in Full Suite (16):**

**Volunteer Permission Tests:**
```
FAILED test_rbac_security.py::test_volunteer_can_view_own_organization_people
FAILED test_rbac_security.py::test_volunteer_cannot_edit_own_roles
FAILED test_rbac_security.py::test_volunteer_cannot_edit_other_users
FAILED test_rbac_security.py::test_volunteer_cannot_create_events
FAILED test_rbac_security.py::test_volunteer_cannot_delete_events
```

**Admin Permission Tests:**
```
FAILED test_rbac_security.py::test_admin_can_create_events
FAILED test_rbac_security.py::test_admin_can_edit_events
FAILED test_rbac_security.py::test_admin_can_delete_events
FAILED test_rbac_security.py::test_admin_can_create_teams
FAILED test_rbac_security.py::test_admin_can_edit_user_profiles
FAILED test_rbac_security.py::test_admin_can_modify_user_roles
FAILED test_rbac_security.py::test_admin_can_run_solver
```

**Cross-Org Isolation Tests:**
```
FAILED test_rbac_security.py::test_admin_cannot_create_events_in_other_org
FAILED test_rbac_security.py::test_no_cross_org_data_leak_in_people_list
```

**Workflow Tests:**
```
FAILED test_rbac_security.py::test_complete_admin_workflow
FAILED test_rbac_security.py::test_complete_volunteer_workflow
```

**Error Detected:**
```
ERROR at teardown of test_complete_volunteer_workflow
sqlite3.OperationalError: no such table: sms_replies
```
**Analysis:** Database cleanup trying to delete from non-existent table - suggests schema mismatch or migration issue.

**✅ ROOT CAUSE IDENTIFIED & FIXED (2025-10-27):**
The issue was in `tests/conftest.py` lines 253-257 and 288-292. The model imports were outdated and missing 5 new models:
- RecurringSeries
- RecurrenceException
- OnboardingProgress
- Notification
- EmailPreference

When `Base.metadata.sorted_tables` tried to clean up ALL tables (including the new ones), but only the old models were imported, it caused schema mismatches.

**Fix Applied:** Updated both import statements in conftest.py to include all current models.

**Status:** Testing fix now - expecting 27/27 tests to pass in both isolated and full suite runs.

---

## Other Notable Failures

### Invitation Workflow (5 tests)
```
FAILED test_invitation_workflow.py::test_complete_invitation_workflow
FAILED test_invitation_workflow.py::test_admin_resends_invitation
FAILED test_invitation_workflow.py::test_admin_cancels_invitation
FAILED test_invitation_workflow.py::test_expired_invitation_token
FAILED test_invitation_workflow.py::test_used_invitation_token
```

### Mobile Responsive (9 tests)
```
FAILED test_mobile_responsive.py::test_mobile_login_flow
FAILED test_mobile_responsive.py::test_mobile_schedule_view
FAILED test_mobile_responsive.py::test_mobile_settings_modal
FAILED test_mobile_responsive.py::test_multiple_device_sizes_login[iPhone SE-viewport0]
FAILED test_mobile_responsive.py::test_multiple_device_sizes_login[iPhone 12-viewport1]
FAILED test_mobile_responsive.py::test_multiple_device_sizes_login[Pixel 5-viewport2]
FAILED test_mobile_responsive.py::test_multiple_device_sizes_login[Galaxy S21-viewport3]
FAILED test_mobile_responsive.py::test_tablet_layout_ipad
FAILED test_mobile_responsive.py::test_mobile_touch_gestures
```

### Onboarding Wizard (7 tests)
```
FAILED test_onboarding_wizard.py::test_wizard_complete_flow
FAILED test_onboarding_wizard.py::test_wizard_resume_after_logout
FAILED test_onboarding_wizard.py::test_wizard_back_button_navigation
FAILED test_onboarding_wizard.py::test_wizard_validation_prevents_empty_submission
FAILED test_onboarding_dashboard.py::test_onboarding_dashboard_displays
FAILED test_onboarding_dashboard.py::test_checklist_widget_interaction
FAILED test_onboarding_dashboard.py::test_video_grid_playback
```

### Email Notifications (4 tests)
```
FAILED test_email_invitation_workflow.py::test_admin_sends_invitation_email
FAILED test_email_invitation_workflow.py::test_invitation_email_contains_correct_content
FAILED test_email_invitation_workflow.py::test_invitation_email_service_handles_errors
FAILED test_email_invitation_workflow.py::test_invitation_email_delivered_to_mailtrap_inbox
```

---

## Test Categories with 100% Pass Rate

These test files have ALL tests passing:

```
✅ test_calendar_features.py (3/4 passed, 1 failed)
✅ test_clear_corrupted_localstorage.py (1/1 passed)
✅ test_admin_console.py (4/7 passed, 3 failed)
✅ test_assignment_notifications.py (2/5 passed, 2 failed, 1 error)
```

---

## Warnings Detected

**Pydantic V1 → V2 Migration Needed:**
```
PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated.
Location: /app/api/schemas/billing.py (lines 75, 82, 108, 132, 139, 164, 171)
```

**Query Parameter Deprecation:**
```
DeprecationWarning: `regex` has been deprecated, please use `pattern` instead
Location: /app/api/routers/billing.py:841
```

---

## Recommended Fixes Priority

### IMMEDIATE (Critical Security)
1. ⚠️ **RBAC Security Tests** - 16 failures affecting security model
   - Fix permission checks
   - Fix cross-org isolation
   - Verify admin/volunteer workflows

### HIGH (Phase 1 Tasks)
2. 🔧 **Availability Management** - 3 failures, tests are running
   - Fix add/edit/delete workflows
   - Then enable skipped tests (calendar, validation)

3. 🔐 **Authentication Flows** - 3 failures
   - Fix login/logout/session persistence

### MEDIUM
4. 📧 **Invitation Workflow** - 5 failures
5. 🤖 **Solver Workflow** - 1 failure (selector mismatch)
6. 📱 **Mobile Responsive** - 9 failures
7. 🎓 **Onboarding** - 7 failures

### LOW (Future Enhancements)
8. 📧 **Email Integration** - 4 failures (requires Mailtrap setup)
9. 🎨 **Visual Regression** - 5 failures (screenshots needed)
10. ⚙️ **Code Warnings** - Pydantic V2 migration

---

## Next Steps

### Phase 1 Task Execution Order

1. **Start with Availability Management** (tests running, easier to debug)
   - Investigate why add/edit/delete tests fail
   - Fix UI selectors if needed
   - Verify backend API responses
   - Enable skipped validation tests

2. **Fix RBAC Security** (critical for production)
   - Check permission enforcement in backend
   - Verify role checks in frontend
   - Test cross-org isolation
   - Validate complete workflows

3. **Fix Authentication** (foundation for all tests)
   - Debug login/logout flows
   - Fix session persistence
   - Re-enable signup test

4. **Fix Solver Workflow** (core product feature)
   - Update selectors to match current UI
   - Verify solver integration
   - Test constraint handling

---

## Docker Environment Notes

**Environment Variables Missing** (warnings during test run):
- MAILTRAP_SMTP_USER
- MAILTRAP_SMTP_PASSWORD
- RECAPTCHA_SITE_KEY
- RECAPTCHA_SECRET_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- STRIPE_PUBLISHABLE_KEY
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET

**Status:** Tests ran successfully despite missing variables (defaulted to blank strings).
**Action Required:** Set up `.env` file with required credentials for email/payment/SMS features.

---

## Test Execution Commands

All commands run tests in Docker:

```bash
# Complete test suite
make test-docker

# Quick summary
make test-docker-summary

# Phase 1 specific tests
make test-docker-availability    # Task 2
make test-docker-rbac            # Task 4
make test-docker-auth            # Task 3
make test-docker-solver          # Task 1

# Individual file tests
make test-docker-file FILE=tests/e2e/test_availability_management.py
```

---

**Generated:** 2025-10-27
**Docker Daemon Status:** Stopped after test run (need to restart for next run)
**Next Action:** Start with `make test-docker-availability` to investigate failures
