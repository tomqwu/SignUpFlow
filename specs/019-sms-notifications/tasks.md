# Implementation Tasks: SMS Notification System

**Feature**: 019 - SMS Notifications | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23
**Source**: Generated from `/speckit.tasks` command using spec.md user stories

This document provides a comprehensive, immediately executable task breakdown organized by user story for independent implementation and parallel execution.

---

## Task Overview

| Phase | User Story | Tasks | Priority | Test Criteria |
|-------|------------|-------|----------|---------------|
| Phase 1 | Setup | 4 | P1 | Twilio credentials configured, dependencies installed |
| Phase 2 | Foundational | 18 | P1 | Database migrated, models testable, service skeleton functional |
| Phase 3 | US1 - Assignment Notifications | 26 | P1 | Volunteer receives SMS within 30s, YES/NO replies work |
| Phase 4 | US2 - Preference Configuration | 23 | P1 | Phone verification complete, preferences saved |
| Phase 5 | US3 - Broadcast Messaging | 18 | P2 | Broadcast sent to team, delivery tracking shows status |
| Phase 6 | US4 - Automatic Reminders | 16 | P2 | 24h reminder delivered, location included |
| Phase 7 | US5 - Opt-Out Compliance | 14 | P2 | STOP reply disables SMS, confirmation sent |
| Phase 8 | US6 - Cost Management | 15 | P3 | 80% alert sent, 100% pauses non-critical messages |
| Phase 9 | US7 - Message Templates | 13 | P3 | Template created, variables substituted, bilingual support |
| Phase 10 | US8 - Testing & Troubleshooting | 12 | P3 | Test SMS sent, delivery log shows status, retry works |
| Phase 11 | Polish | 15 | P3 | Error handling complete, monitoring added, docs updated |

**Total Tasks**: 174 tasks across 11 phases

**MVP Scope** (US1 + US2): 71 tasks (Phases 1-4)

**Estimated Timeline**:
- MVP (US1 + US2): 4-5 weeks (assignment notifications + preferences)
- Full Feature (US1-US8): 12-16 weeks

---

## Phase 1: Setup (4 tasks)

**Goal**: Install dependencies, configure Twilio credentials, set up project structure

**Independent Test**: `make test-setup` passes, Twilio test credentials work

### Setup Tasks

- [ ] T001 Install Twilio Python SDK: `poetry add twilio==8.0+` per plan.md
- [ ] T002 [P] Install Celery and Redis dependencies: `poetry add celery==5.0+ redis==7.0+` per plan.md
- [ ] T003 [P] Add i18n translations for SMS UI components in locales/en/sms.json and locales/es/sms.json
- [ ] T004 [P] Set up Twilio test credentials in .env file: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER per quickstart.md

---

## Phase 2: Foundational (18 tasks)

**Goal**: Database migrations, model classes, base SMS service, rate limiting infrastructure

**Why Priority P1**: These are blocking prerequisites for ALL user stories - no SMS functionality can work without database tables, Twilio service, and rate limiting.

**Independent Test**: Database migrated successfully, SMS service instantiates, rate limiter tracks counters

### Database Migration (5 tasks)

- [ ] T005 Create Alembic migration for 6 SMS tables per data-model.md in migrations/versions/add_sms_tables.py
- [ ] T006 [P] Add `SmsPreference` model class in api/models.py with phone_number, verified, notification_types, opt_in_date, opt_out_date, language, timezone fields
- [ ] T007 [P] Add `SmsMessage` model class in api/models.py with organization_id, recipient_id, phone_number, message_text, message_type, event_id, template_id, status, twilio_message_sid, cost_cents, error_message, is_urgent, sent_at, delivered_at, failed_at fields
- [ ] T008 [P] Add `SmsTemplate` model class in api/models.py with organization_id, name, template_text, message_type, character_count, translations, is_system, usage_count, created_by fields
- [ ] T009 [P] Add `SmsUsage` model class in api/models.py with organization_id, month_year, assignment_count, reminder_count, broadcast_count, system_count, total_cost_cents, budget_limit_cents, alert_threshold_percent fields

- [ ] T010 [P] Add `SmsVerificationCode` model class in api/models.py with person_id, phone_number, verification_code, attempts, expires_at fields
- [ ] T011 [P] Add `SmsReply` model class in api/models.py with person_id, phone_number, message_text, reply_type, original_message_id, event_id, action_taken, twilio_message_sid, processed_at fields
- [ ] T012 Run database migration: `poetry run alembic upgrade head`
- [ ] T013 Seed system templates per data-model.md (Assignment Notification, 24-Hour Reminder, Event Cancellation) in migrations seed script

### Core SMS Service (7 tasks)

- [ ] T014 Create `SMSService` class skeleton in api/services/sms_service.py with Twilio client initialization
- [ ] T015 [P] Implement `send_sms()` method in SMSService: sends via Twilio API, logs to sms_messages table, returns twilio_message_sid
- [ ] T016 [P] Implement `send_broadcast()` method in SMSService: batches messages (10/min), skips opted-out users, returns broadcast summary
- [ ] T017 [P] Implement `verify_phone_number()` method in SMSService: uses Twilio Lookup API, validates E.164 format, detects landlines
- [ ] T018 [P] Implement `generate_verification_code()` method in SMSService: creates 6-digit code, sends via SMS, stores in sms_verification_codes table
- [ ] T019 [P] Implement `verify_code()` method in SMSService: validates code against sms_verification_codes, checks expiration, marks phone verified
- [ ] T020 [P] Implement `process_incoming_reply()` method in SMSService: parses YES/NO/STOP/START/HELP replies, takes action, logs to sms_replies table

### Rate Limiting Infrastructure (4 tasks)

- [ ] T021 Create `RateLimiter` class in api/utils/rate_limiter.py using Redis counters per plan.md
- [ ] T022 [P] Implement `check_rate_limit()` method: checks Redis counter for person_id+date key, returns boolean and remaining count
- [ ] T023 [P] Implement `increment_rate_limit()` method: increments Redis counter with 24-hour expiry
- [ ] T024 [P] Implement `reset_rate_limit()` method: clears counter for person (admin override)

### Quiet Hours & Cost Tracking (2 tasks)

- [ ] T025 [P] Create `QuietHours` utility class in api/utils/quiet_hours.py: checks if current time 10pm-8am in volunteer timezone, calculates next send time
- [ ] T026 [P] Create `CostTracker` utility class in api/utils/cost_tracker.py: calculates message cost ($0.0079 per segment), checks budget, updates sms_usage table

---

## Phase 3: User Story 1 - Assignment Notifications (26 tasks)

**Priority**: P1 (MVP - Core notification delivery)

**User Story**: Volunteer receives SMS alert when assigned to upcoming event with concise message containing event details (date, time, role, location) and action options (reply YES to confirm, NO to decline), enabling immediate response without opening email or app.

**Why Priority P1**: This is the core SMS notification use case. 70% of volunteers prefer SMS for time-sensitive notifications. Without assignment SMS delivery, the feature provides no immediate value and volunteers miss critical assignments.

**Independent Test**: Create event with assignment. Configure volunteer for SMS notifications. Trigger assignment notification. Verify SMS delivered within 30 seconds containing event name, date, time, role. Verify volunteer can reply YES to confirm. Verify confirmation updates assignment status.

**Test Success Criteria**:
- ✅ SMS delivered within 30 seconds of assignment creation
- ✅ Message contains: event name, date, time, role, reply instructions
- ✅ Volunteer replies "YES" → assignment status = "confirmed"
- ✅ Volunteer replies "NO" → assignment removed, admin notified
- ✅ Invalid reply → help message sent with instructions

### API Endpoints (5 tasks)

- [ ] T027 [US1] Implement POST /api/sms/send endpoint per contracts/sms-api.md in api/routers/sms.py
- [ ] T028 [P] [US1] Implement GET /api/sms/messages endpoint (message history) per contracts/sms-api.md in api/routers/sms.py
- [ ] T029 [P] [US1] Implement POST /api/webhooks/twilio/status endpoint (delivery webhooks) per contracts/webhooks-api.md in api/routers/webhooks.py
- [ ] T030 [P] [US1] Implement POST /api/webhooks/twilio/incoming endpoint (reply webhooks) per contracts/webhooks-api.md in api/routers/webhooks.py
- [ ] T031 [P] [US1] Add SMS router registration in api/main.py: app.include_router(sms.router, prefix="/api/sms")

### Celery Async Tasks (4 tasks)

- [ ] T032 [US1] Create Celery task `send_assignment_notification` in api/tasks/sms_tasks.py: queues SMS when assignment created
- [ ] T033 [P] [US1] Implement retry logic in Celery task: exponential backoff (1min, 5min, 15min, 1hr) per plan.md
- [ ] T034 [P] [US1] Add error handling in Celery task: logs failures to sms_messages.error_message, updates status='failed'
- [ ] T035 [P] [US1] Add cost tracking in Celery task: calculates actual cost from Twilio webhook, updates sms_usage table

### Message Composition (4 tasks)

- [ ] T036 [US1] Implement `compose_assignment_message()` method in SMSService: formats event details, adds YES/NO reply options, uses assignment template
- [ ] T037 [P] [US1] Implement message length validation: warns if >160 chars (multi-segment), truncates if >1600 chars
- [ ] T038 [P] [US1] Add bilingual message support: selects template based on sms_preferences.language (en or es)
- [ ] T039 [P] [US1] Add variable substitution: replaces {{event_name}}, {{date}}, {{time}}, {{role}} with actual event data

### Reply Processing (6 tasks)

- [ ] T040 [US1] Implement `process_yes_reply()` method in SMSService: updates assignment status='confirmed', sends confirmation SMS
- [ ] T041 [P] [US1] Implement `process_no_reply()` method in SMSService: removes assignment, notifies admin, sends declination SMS
- [ ] T042 [P] [US1] Implement `process_help_reply()` method in SMSService: sends help message with valid commands and support contact
- [ ] T043 [P] [US1] Implement `process_unknown_reply()` method in SMSService: sends friendly error message explaining YES/NO/STOP options
- [ ] T044 [P] [US1] Add reply context tracking: associates incoming replies with original message via sms_replies.original_message_id
- [ ] T045 [P] [US1] Add duplicate reply detection: ignores multiple YES replies to same assignment within 5 minutes

### Validation & Rate Limiting (4 tasks)

- [ ] T046 [US1] Add recipient validation in send_sms endpoint: checks sms_preferences.verified=true, opt_out_date IS NULL
- [ ] T047 [P] [US1] Integrate rate limiter in send_sms endpoint: checks 3 SMS/day limit before queueing, bypasses if is_urgent=true
- [ ] T048 [P] [US1] Add quiet hours enforcement in Celery task: queues non-urgent messages for 8am if sent during 10pm-8am
- [ ] T049 [P] [US1] Add budget check in send_sms endpoint: verifies remaining budget, bypasses for critical assignments if at 100%

### Integration & Testing (3 tasks)

- [ ] T050 [US1] Connect assignment creation flow to SMS notification: triggers send_assignment_notification Celery task when new assignment created
- [ ] T051 [P] [US1] Add delivery tracking UI in frontend/js/app-admin.js: shows sent/delivered/failed status for each assignment notification
- [ ] T052 [P] [US1] Write E2E test for assignment notification workflow in tests/e2e/test_assignment_sms.py: creates event, assigns volunteer, verifies SMS delivery and reply processing

---

## Phase 4: User Story 2 - Preference Configuration (23 tasks)

**Priority**: P1 (MVP - Required for SMS delivery)

**User Story**: Volunteer configures notification preferences choosing SMS, email, or both for different notification types (assignment requests, schedule reminders, schedule changes, event cancellations) with phone number verification and opt-in confirmation required before SMS delivery begins.

**Why Priority P1**: Preference configuration is prerequisite for all SMS functionality. TCPA compliance mandates explicit opt-in. Without preference management, system cannot legally send SMS messages.

**Independent Test**: Navigate to notification settings. Enter phone number. Verify validation (format check, deliverability via Twilio lookup). Receive verification SMS with code. Enter code to confirm opt-in. Select notification types for SMS delivery. Save preferences. Verify SMS delivered only for selected types.

**Test Success Criteria**:
- ✅ Phone number validated (E.164 format, mobile not landline)
- ✅ Verification SMS delivered within 30 seconds
- ✅ Code entry succeeds (6-digit match, not expired)
- ✅ Preferences saved: notification types correctly stored
- ✅ Opt-in confirmation SMS sent after verification
- ✅ Notifications only sent for selected types

### API Endpoints (5 tasks)

- [ ] T053 [US2] Implement GET /api/sms/preferences endpoint per contracts/preferences-api.md in api/routers/sms.py
- [ ] T054 [P] [US2] Implement PUT /api/sms/preferences endpoint (save preferences) per contracts/preferences-api.md in api/routers/sms.py
- [ ] T055 [P] [US2] Implement POST /api/sms/verify/send endpoint (send verification code) per contracts/preferences-api.md in api/routers/sms.py
- [ ] T056 [P] [US2] Implement POST /api/sms/verify/confirm endpoint (verify code) per contracts/preferences-api.md in api/routers/sms.py
- [ ] T057 [P] [US2] Add authorization checks: volunteers can only access own preferences, admins can view all

### Phone Verification (5 tasks)

- [ ] T058 [US2] Implement `validate_phone_format()` method in SMSService: checks E.164 format regex ^\+[1-9]\d{1,14}$
- [ ] T059 [P] [US2] Implement Twilio Lookup API integration in verify_phone_number(): detects carrier type (mobile vs landline), returns deliverability status
- [ ] T060 [P] [US2] Implement verification code generation: creates random 6-digit code (100000-999999), stores in sms_verification_codes with 10-minute expiry
- [ ] T061 [P] [US2] Implement verification code SMS sending: uses system template, sends code to provided phone number
- [ ] T062 [P] [US2] Implement verification code validation: checks code match, expiration time, attempts (max 3), marks phone verified on success

### Frontend Preference UI (7 tasks)

- [ ] T063 [US2] Create SMS preferences UI component in frontend/js/sms-preferences.js: form with phone input, verification flow, notification type checkboxes
- [ ] T064 [P] [US2] Add phone number input field with E.164 format helper: placeholder "+1 555-123-4567", auto-formats as user types
- [ ] T065 [P] [US2] Add "Verify Phone" button: triggers POST /api/sms/verify/send, shows success message "Verification code sent"
- [ ] T066 [P] [US2] Add verification code input field: 6-digit input, auto-focuses when SMS sent
- [ ] T067 [P] [US2] Add "Confirm Code" button: triggers POST /api/sms/verify/confirm, shows success/error messages
- [ ] T068 [P] [US2] Add notification type checkboxes: assignment, reminder, change, cancellation with descriptions
- [ ] T069 [P] [US2] Add "Save Preferences" button: triggers PUT /api/sms/preferences, shows success toast

### Opt-In Compliance (3 tasks)

- [ ] T070 [US2] Implement double opt-in flow: phone verification required before enabling SMS notifications
- [ ] T071 [P] [US2] Add opt-in confirmation SMS: sent after successful verification with text "You have opted in to SMS notifications from SignUpFlow. Reply STOP to unsubscribe anytime"
- [ ] T072 [P] [US2] Add opt-in audit trail: logs opt_in_date timestamp in sms_preferences table for TCPA compliance

### Preference Management (3 tasks)

- [ ] T073 [US2] Implement `get_sms_preferences()` method in SMSService: retrieves sms_preferences for person, returns defaults if not exists
- [ ] T074 [P] [US2] Implement `update_sms_preferences()` method in SMSService: updates notification_types, language, timezone fields
- [ ] T075 [P] [US2] Add notification type filtering in send_assignment_notification task: checks if 'assignment' in recipient.notification_types before sending

---

## Phase 5: User Story 3 - Broadcast Messaging (18 tasks)

**Priority**: P2 (Enhancement - Urgent team communications)

**User Story**: Administrator sends urgent broadcast SMS to entire team or selected volunteers with concise message (max 160 chars recommended) for time-critical updates (event cancellation, schedule change, weather alert) with delivery tracking showing message status for each recipient.

**Why Priority P2**: Broadcast messaging enables rapid communication for urgent situations. Used infrequently (1-2x per month) but critical when needed. Lower priority than individual assignment notifications which occur daily.

**Independent Test**: As administrator, compose broadcast message (<160 chars). Select recipients (team or individual volunteers). Send message. Verify delivery tracking shows status for each recipient (queued, sent, delivered, failed). Verify rate limiting applied (batched to avoid carrier limits). Verify all recipients receive SMS within 5 minutes.

**Test Success Criteria**:
- ✅ Broadcast UI shows character count with 160-char warning
- ✅ Recipients selected via team dropdown or individual checkboxes
- ✅ Delivery tracking shows per-recipient status in real-time
- ✅ Messages batched at 10/minute to avoid carrier rate limits
- ✅ Opted-out volunteers automatically excluded with warning
- ✅ All delivered within 5 minutes for 50-recipient broadcast

### API Endpoint (2 tasks)

- [ ] T076 [US3] Implement POST /api/sms/broadcast endpoint per contracts/sms-api.md in api/routers/sms.py
- [ ] T077 [P] [US3] Add validation: max 200 recipients, message 1-1600 chars, mutually exclusive recipient_ids OR team_id

### Broadcast Logic (5 tasks)

- [ ] T078 [US3] Implement recipient expansion in send_broadcast(): resolves team_id to member list, filters opted-out users, validates phone verification
- [ ] T079 [P] [US3] Implement broadcast batching: queues messages at 10/minute rate (Celery ETA) to avoid carrier rate limits
- [ ] T080 [P] [US3] Implement broadcast tracking: generates unique broadcast_id, associates all messages with broadcast_id for status tracking
- [ ] T081 [P] [US3] Implement skipped recipient reporting: counts and categorizes skipped users (no_phone, opted_out, rate_limited), returns in response
- [ ] T082 [P] [US3] Implement broadcast summary notification: sends admin email when broadcast completes with delivery counts

### Frontend Admin UI (6 tasks)

- [ ] T083 [US3] Create broadcast message UI in frontend/js/sms-admin.js: textarea with character counter, recipient selector, send button
- [ ] T084 [P] [US3] Add character counter: shows current length, warns at 160 chars ("Will split into N segments"), red at 1600 chars limit
- [ ] T085 [P] [US3] Add recipient selector: dropdown for teams, multi-select for individual volunteers
- [ ] T086 [P] [US3] Add estimated cost display: calculates (recipients × segments × $0.0079), shows total before send
- [ ] T087 [P] [US3] Add "Send Broadcast" button with confirmation dialog: warns about cost and recipient count
- [ ] T088 [P] [US3] Add broadcast status tracking UI: shows queued/sent/delivered/failed counts, links to detailed delivery report

### Delivery Tracking (3 tasks)

- [ ] T089 [US3] Implement GET /api/sms/broadcasts/{broadcast_id}/status endpoint: returns per-recipient delivery status
- [ ] T090 [P] [US3] Add real-time status updates via webhook: updates sms_messages status as Twilio webhooks arrive
- [ ] T091 [P] [US3] Add broadcast retry functionality: allows admin to retry failed messages from delivery report UI

### Testing (2 tasks)

- [ ] T092 [US3] Write unit test for broadcast batching: verifies 50 recipients queued with 5-minute stagger
- [ ] T093 [P] [US3] Write E2E test for broadcast workflow in tests/e2e/test_broadcast_sms.py: admin sends to team, verifies delivery tracking

---

## Phase 6: User Story 4 - Automatic Reminders (16 tasks)

**Priority**: P2 (Enhancement - Reduces no-shows)

**User Story**: Volunteer receives automatic reminder SMS 24 hours before assigned event with event details and location, reducing missed assignments and providing advance notice to volunteers who may forget upcoming commitments.

**Why Priority P2**: Automatic reminders significantly reduce no-shows (40% reduction based on industry data) but are enhancement to core notification system. Can be added after assignment notifications working.

**Independent Test**: Create event scheduled 24 hours from now. Assign volunteer with SMS reminders enabled. Wait for scheduled reminder time (or trigger manually). Verify volunteer receives reminder SMS 24h before event with event name, date, time, location. Verify reminder not sent if volunteer already confirmed.

**Test Success Criteria**:
- ✅ Reminder scheduled for 24h before event start time
- ✅ Message contains: event name, date, time, location, directions link
- ✅ Already-confirmed assignments receive different message ("You're confirmed")
- ✅ Reminder respects quiet hours (queued for 8am if 24h mark is 11pm)
- ✅ Opted-out volunteers skipped automatically

### Scheduled Reminder Tasks (4 tasks)

- [ ] T094 [US4] Create Celery periodic task `schedule_event_reminders` in api/tasks/sms_tasks.py: runs hourly, finds events 24h away, queues reminders
- [ ] T095 [P] [US4] Implement reminder scheduling logic: calculates 24h before event start, creates Celery task with ETA
- [ ] T096 [P] [US4] Add duplicate reminder prevention: checks if reminder already sent for person+event combination
- [ ] T097 [P] [US4] Add confirmation status check: sends different message if assignment status='confirmed'

### Message Composition (4 tasks)

- [ ] T098 [US4] Implement `compose_reminder_message()` method in SMSService: formats event details, adds location if present, includes directions link
- [ ] T099 [P] [US4] Add Google Maps short link generation: creates maps.google.com/?q=lat,lng URL for event location
- [ ] T100 [P] [US4] Add conditional location handling: omits location line if event.location is empty (graceful degradation)
- [ ] T101 [P] [US4] Use reminder template from sms_templates: "Reminder: {{event_name}} tomorrow at {{time}}. Location: {{location}}. See you there!"

### Notification Type Filtering (3 tasks)

- [ ] T102 [US4] Add reminder preference check: only send if 'reminder' in sms_preferences.notification_types
- [ ] T103 [P] [US4] Add opt-in requirement: skip if sms_preferences.verified=false or opt_out_date NOT NULL
- [ ] T104 [P] [US4] Add budget check: reminders are non-critical, auto-paused if organization at 100% budget

### Integration & Testing (5 tasks)

- [ ] T105 [US4] Register Celery beat schedule for schedule_event_reminders: runs every hour at :00
- [ ] T106 [P] [US4] Add manual reminder trigger endpoint POST /api/sms/reminders/send for testing: allows admin to send immediate reminder
- [ ] T107 [P] [US4] Add reminder analytics tracking: counts reminder_count in sms_usage table
- [ ] T108 [P] [US4] Write unit test for reminder scheduling: verifies 24h calculation, duplicate prevention
- [ ] T109 [P] [US4] Write E2E test for reminder workflow in tests/e2e/test_reminder_sms.py: creates event, waits for scheduled time, verifies delivery

---

## Phase 7: User Story 5 - Opt-Out Compliance (14 tasks)

**Priority**: P2 (Legal requirement - TCPA compliance)

**User Story**: Volunteer opts out of SMS notifications by replying "STOP" to any message, immediately disabling future SMS delivery with confirmation message and compliance audit trail, meeting TCPA requirements for SMS marketing regulations.

**Why Priority P2**: TCPA compliance is legally required but opt-out scenarios are infrequent (1-5% of users). Must be implemented before production launch but lower priority than core messaging functionality.

**Independent Test**: Volunteer receives SMS notification. Reply "STOP" to message. Verify SMS notifications immediately disabled. Verify confirmation SMS sent: "You have unsubscribed from SignUpFlow SMS. You will no longer receive text messages." Verify opt-out logged in audit trail with timestamp. Verify future notifications sent via email only.

**Test Success Criteria**:
- ✅ STOP reply processed within 60 seconds
- ✅ sms_preferences.opt_out_date set to current timestamp
- ✅ Confirmation SMS sent: "You have unsubscribed..."
- ✅ Audit log entry created in sms_replies table
- ✅ Future SMS attempts skipped (send_sms returns error)
- ✅ Email notifications continue working

### STOP Reply Processing (5 tasks)

- [ ] T110 [US5] Implement `process_stop_reply()` method in SMSService: updates sms_preferences.opt_out_date=NOW(), sends confirmation SMS
- [ ] T111 [P] [US5] Add confirmation message for STOP: "You have unsubscribed from SignUpFlow SMS notifications. You will receive email notifications instead. Reply START to re-enable."
- [ ] T112 [P] [US5] Add audit logging for STOP: creates sms_replies record with reply_type='stop', action_taken='opted_out'
- [ ] T113 [P] [US5] Add opt-out enforcement in send_sms: checks opt_out_date NOT NULL before queuing, returns 422 error if opted out
- [ ] T114 [P] [US5] Add admin notification for STOP: emails admin when volunteer opts out (optional, configurable)

### START Reply Re-Enablement (4 tasks)

- [ ] T115 [US5] Implement `process_start_reply()` method in SMSService: clears opt_out_date, requires re-verification before re-enabling
- [ ] T116 [P] [US5] Add verification code requirement for START: generates new code, sends verification SMS before re-enabling
- [ ] T117 [P] [US5] Add welcome back message: "Welcome back! Reply with verification code {{code}} to resume SMS notifications"
- [ ] T118 [P] [US5] Add audit logging for START: creates sms_replies record with reply_type='start', action_taken='opted_in'

### Broadcast Exclusion (3 tasks)

- [ ] T119 [US5] Add opt-out filtering in send_broadcast(): automatically excludes recipients with opt_out_date NOT NULL
- [ ] T120 [P] [US5] Add admin warning in broadcast response: "{{N}} recipients excluded due to opt-out"
- [ ] T121 [P] [US5] Add opt-out list view endpoint GET /api/sms/opted-out: returns list of opted-out volunteers for admin review

### Testing (2 tasks)

- [ ] T122 [US5] Write unit test for STOP processing: verifies opt_out_date set, confirmation sent, future messages blocked
- [ ] T123 [P] [US5] Write E2E test for opt-out workflow in tests/e2e/test_opt_out_sms.py: receives SMS, replies STOP, verifies no future SMS

---

## Phase 8: User Story 6 - Cost Management (15 tasks)

**Priority**: P3 (Nice-to-have - Budget control)

**User Story**: Administrator monitors SMS usage and costs with monthly budget limits, receives alerts when approaching limit (80% usage), and can upgrade to higher tier or disable non-critical messages to stay within budget, preventing unexpected overage charges.

**Why Priority P3**: Cost management prevents budget overruns but is enhancement feature. Initial deployments have predictable costs ($50-200/month for typical organizations). Can be added after core SMS functionality stable.

**Independent Test**: Set organization monthly SMS budget ($100). Send messages approaching limit. Verify alert at 80% usage. Verify non-critical messages (reminders) automatically paused at 100% limit. Verify critical messages (assignment requests) still sent. Verify administrator can increase budget or disable SMS.

**Test Success Criteria**:
- ✅ Budget limit configurable per organization (default $100)
- ✅ Alert sent at 80% utilization
- ✅ Non-critical messages auto-paused at 100%
- ✅ Critical messages continue at 100%
- ✅ Dashboard shows: usage, cost breakdown, budget remaining
- ✅ Monthly reset on 1st at midnight UTC

### Budget Configuration (3 tasks)

- [ ] T124 [US6] Implement GET /api/sms/budget endpoint: returns sms_usage for current month with budget details
- [ ] T125 [P] [US6] Implement PUT /api/sms/budget endpoint: allows admin to update budget_limit_cents, alert_threshold_percent, auto_pause_enabled
- [ ] T126 [P] [US6] Add default budget initialization: creates sms_usage record with $100 default when organization first uses SMS

### Cost Tracking (4 tasks)

- [ ] T127 [US6] Implement real-time cost tracking in Celery task: increments message_count by type, adds cost_cents to total_cost_cents after Twilio webhook
- [ ] T128 [P] [US6] Add cost estimation in send_sms: calculates segments × $0.0079, displays estimated cost before sending
- [ ] T129 [P] [US6] Add actual cost update from Twilio webhook: uses price field from status callback, updates sms_messages.cost_cents and sms_usage.total_cost_cents
- [ ] T130 [P] [US6] Add monthly reset logic: Celery periodic task on 1st of month creates new sms_usage record, archives previous month

### Budget Alerts (4 tasks)

- [ ] T131 [US6] Implement 80% budget alert: checks utilization after each message, sends admin email/notification if >= 80% and alert_sent_at_80=false
- [ ] T132 [P] [US6] Implement 100% budget alert: sends admin email when budget reached, indicates non-critical messages paused
- [ ] T133 [P] [US6] Add projected overage calculation: estimates date when budget will be exceeded based on current usage rate
- [ ] T134 [P] [US6] Add alert email templates: "SMS usage at {{percent}}% ({{current}} of {{limit}}). Estimated to exceed budget by {{date}}."

### Auto-Pause Logic (2 tasks)

- [ ] T135 [US6] Implement budget enforcement in send_sms: checks if at 100% budget, pauses non-critical messages (reminder, broadcast), allows critical messages (assignment)
- [ ] T136 [P] [US6] Add queued message display in admin UI: shows "{{N}} reminders queued due to budget limit. Increase budget or wait until next billing cycle."

### Analytics Dashboard (2 tasks)

- [ ] T137 [US6] Implement GET /api/sms/analytics endpoint per contracts/sms-api.md: returns usage stats, cost breakdown, delivery metrics, budget utilization
- [ ] T138 [P] [US6] Create SMS analytics dashboard UI in frontend/js/sms-admin.js: charts for usage trend, cost by type, budget progress bar, top recipients

---

## Phase 9: User Story 7 - Message Templates (13 tasks)

**Priority**: P3 (Nice-to-have - Efficiency improvement)

**User Story**: Administrator creates reusable SMS message templates for common scenarios (assignment reminder, schedule change, event cancellation) with dynamic variable substitution (volunteer name, event details, date/time) and bilingual support (English, Spanish) based on volunteer language preference.

**Why Priority P3**: Templates improve efficiency and consistency but are enhancement. Administrators can manually compose messages initially. Templates add convenience after core functionality proven.

**Independent Test**: Create message template "Reminder: {{event_name}} on {{date}} at {{time}}. See you there, {{volunteer_name}}!". Send to volunteer. Verify variables replaced with actual values. Verify volunteer with Spanish preference receives Spanish version. Verify template reusable for future messages.

**Test Success Criteria**:
- ✅ Template CRUD endpoints functional
- ✅ Variables {{event_name}}, {{date}}, {{time}}, {{role}}, {{volunteer_name}} supported
- ✅ Jinja2 template rendering works correctly
- ✅ Bilingual templates (en/es) automatically selected
- ✅ Character count calculated (before variable substitution)
- ✅ System templates cannot be deleted

### Template API (4 tasks)

- [ ] T139 [US7] Implement GET /api/sms/templates endpoint per contracts/templates-api.md: returns template list filtered by organization
- [ ] T140 [P] [US7] Implement POST /api/sms/templates endpoint: creates new template with validation (Jinja2 syntax, character count)
- [ ] T141 [P] [US7] Implement PUT /api/sms/templates/{id} endpoint: updates template, increments usage_count when used
- [ ] T142 [P] [US7] Implement DELETE /api/sms/templates/{id} endpoint: soft-delete custom templates, prevent deletion of system templates

### Template Rendering (4 tasks)

- [ ] T143 [US7] Implement `render_template()` method in SMSService: uses Jinja2 to substitute variables from context dict
- [ ] T144 [P] [US7] Add variable context building: extracts event, person, organization data into context dict for template rendering
- [ ] T145 [P] [US7] Add graceful missing data handling: omits optional variables if null (e.g., {{location}} omitted if event.location IS NULL)
- [ ] T146 [P] [US7] Add character count estimation: calculates template length with sample data for admin UI display

### Bilingual Support (3 tasks)

- [ ] T147 [US7] Implement language selection in render_template(): checks sms_preferences.language, selects correct translation from template.translations JSON
- [ ] T148 [P] [US7] Add template translation management UI: allows admin to edit English and Spanish versions side-by-side
- [ ] T149 [P] [US7] Add bilingual system templates: update seed data with Spanish translations for Assignment, Reminder, Cancellation templates

### Frontend Template UI (2 tasks)

- [ ] T150 [US7] Create template management UI in frontend/js/sms-admin.js: list view, create/edit form, delete confirmation
- [ ] T151 [P] [US7] Add template preview feature: renders template with sample data, shows final message and character count

---

## Phase 10: User Story 8 - Testing & Troubleshooting (12 tasks)

**Priority**: P3 (Nice-to-have - Debugging tools)

**User Story**: Administrator tests SMS delivery by sending test message to their own phone number before broadcasting to volunteers, verifies message formatting and delivery time, and accesses delivery logs showing detailed status (queued, sent, delivered, failed) for troubleshooting failed messages.

**Why Priority P3**: Testing and troubleshooting are important for reliability but not needed for basic functionality. Most messages deliver successfully. Testing features add confidence and debugging capability for edge cases.

**Independent Test**: As administrator, use "Send Test SMS" feature. Enter own phone number. Send test message. Verify message received with correct formatting. View delivery log showing status transitions (queued → sent → delivered) with timestamps. Simulate failure scenario. Verify failure logged with error reason. Verify retry option available.

**Test Success Criteria**:
- ✅ Test mode UI available in admin console
- ✅ Test SMS delivered with [TEST] header
- ✅ Test messages don't count toward volunteer rate limits or budget
- ✅ Delivery log shows detailed timeline with timestamps
- ✅ Failed messages show error reason (invalid number, landline, carrier rejected)
- ✅ Manual retry option available for failed messages

### Test Mode (4 tasks)

- [ ] T152 [US8] Implement POST /api/sms/test endpoint: sends test SMS to admin phone, marks message with is_test=true flag
- [ ] T153 [P] [US8] Add test message formatting: prepends "[TEST]" header, appends "This is a test message from SignUpFlow" footer
- [ ] T154 [P] [US8] Exclude test messages from rate limits: skips rate_limiter.check_rate_limit() if is_test=true
- [ ] T155 [P] [US8] Exclude test messages from budget: doesn't increment sms_usage totals if is_test=true

### Delivery Log (4 tasks)

- [ ] T156 [US8] Enhance GET /api/sms/messages endpoint: adds detailed status timeline, error_message field, delivery timestamps
- [ ] T157 [P] [US8] Add delivery log UI in frontend/js/sms-admin.js: table with status badges, timestamps, error details, retry button
- [ ] T158 [P] [US8] Add real-time status updates: polls /api/sms/messages periodically or uses WebSocket for live delivery status
- [ ] T159 [P] [US8] Add export functionality: allows admin to export delivery log as CSV for analysis

### Error Troubleshooting (2 tasks)

- [ ] T160 [US8] Implement detailed error logging: captures Twilio error codes, carrier rejection reasons, network failures in sms_messages.error_message
- [ ] T161 [P] [US8] Add error categorization: groups errors by type (invalid_number, landline, carrier_rejected, rate_limit, network_error) for admin dashboard

### Manual Retry (2 tasks)

- [ ] T162 [US8] Implement POST /api/sms/messages/{id}/retry endpoint: requeues failed message, resets status to 'queued'
- [ ] T163 [P] [US8] Add batch retry UI: allows admin to select multiple failed messages and retry all at once

---

## Phase 11: Polish & Cross-Cutting Concerns (15 tasks)

**Goal**: Production readiness - error handling, monitoring, performance, documentation

**Why Priority P3**: Polish tasks don't add new features but improve reliability, maintainability, and developer experience. Essential for production deployment but can be done after MVP validated.

### Error Handling (4 tasks)

- [ ] T164 Add global exception handler in api/routers/sms.py: catches Twilio API errors, returns user-friendly messages
- [ ] T165 [P] Add validation error messages: clear explanations for common errors (unverified phone, opted out, rate limited, budget exceeded)
- [ ] T166 [P] Add retry exhaustion handling: after 4 retry attempts, marks message as permanently failed, notifies admin
- [ ] T167 [P] Add webhook signature verification: validates Twilio webhook requests using X-Twilio-Signature header per security best practices

### Performance Optimization (3 tasks)

- [ ] T168 Add database indexes per data-model.md: compound indexes on (organization_id, created_at), (status, created_at), (twilio_message_sid)
- [ ] T169 [P] Optimize message history query: add pagination cursor, limit joins, cache recent messages in Redis
- [ ] T170 [P] Add Celery task monitoring: integrate Flower dashboard for task queue visibility, retry tracking

### Monitoring & Alerting (3 tasks)

- [ ] T171 Add structured logging for all SMS operations: log message_id, recipient_id, status, cost, delivery_time with correlation IDs
- [ ] T172 [P] Add Sentry error tracking: captures Twilio API failures, webhook processing errors, template rendering errors
- [ ] T173 [P] Add performance metrics: track SMS delivery time (p95, p99), Celery queue depth, delivery success rate

### Documentation (3 tasks)

- [ ] T174 Write developer quickstart guide in docs/SMS_DEVELOPER_GUIDE.md: setup instructions, testing with Twilio sandbox, debugging tips
- [ ] T175 [P] Write admin user guide in docs/SMS_ADMIN_GUIDE.md: preference configuration, broadcast messaging, cost management, troubleshooting
- [ ] T176 [P] Update API documentation in docs/API.md: add SMS endpoints, webhook specifications, error codes

### Security (2 tasks)

- [ ] T177 Add rate limiting on SMS API endpoints: 100 req/min for send, 10 req/min for broadcast per contracts/sms-api.md
- [ ] T178 [P] Add CSRF protection for webhook endpoints: validate Twilio webhook origin, implement request signing

---

## Dependency Graph

### Story Completion Order

```
Setup (Phase 1)
  ↓
Foundational (Phase 2) ← BLOCKS ALL USER STORIES
  ↓
┌─────────────────────────────────┬─────────────────────────┐
↓                                 ↓                         ↓
US1: Assignment Notifications   US2: Preferences        (Independent)
  (Phase 3)                       (Phase 4)
  ↓                                 ↓
  └─────────────────────────────────┘
                  ↓
    ┌─────────────┴─────────────┬──────────────────┬──────────────────┐
    ↓                           ↓                  ↓                  ↓
US3: Broadcast            US4: Reminders      US5: Opt-Out       US6: Cost Mgmt
  (Phase 5)                 (Phase 6)           (Phase 7)          (Phase 8)
    ↓                           ↓                  ↓                  ↓
    └─────────────┬─────────────┴──────────────────┴──────────────────┘
                  ↓
    ┌─────────────┴─────────────┐
    ↓                           ↓
US7: Templates            US8: Testing
  (Phase 9)                 (Phase 10)
    ↓                           ↓
    └─────────────┬─────────────┘
                  ↓
            Polish (Phase 11)
```

### Critical Path

1. **Setup** (Phase 1: 4 tasks) - Twilio credentials, dependencies
2. **Foundational** (Phase 2: 18 tasks) - Database, models, SMSService, rate limiting **← BLOCKS EVERYTHING**
3. **MVP Track** (Phases 3-4: 49 tasks) - US1 + US2 together (assignment notifications require preferences)
4. **Enhancement Track** (Phases 5-10: 88 tasks) - US3-US8 can be done in any order after MVP
5. **Polish** (Phase 11: 15 tasks) - Final production readiness

**Blocker Note**: Phase 2 (Foundational) MUST complete before any user story implementation begins. All user stories depend on database tables, models, and SMSService skeleton.

---

## Parallel Execution Strategy

### Phase 2: Foundational (After migration complete)

**Launch in parallel** (different files, no dependencies):
- T006-T011: Model classes in api/models.py (can be written simultaneously by referring to data-model.md)
- T014-T020: SMSService methods in api/services/sms_service.py (each method independent)
- T021-T024: RateLimiter class in api/utils/rate_limiter.py
- T025: QuietHours class in api/utils/quiet_hours.py
- T026: CostTracker class in api/utils/cost_tracker.py

**Sequential constraint**: T005 (migration) → T012 (run migration) must complete before model classes testable

### Phase 3: US1 (After SMSService.send_sms() works)

**Launch in parallel**:
- T027-T031: API endpoints (5 separate endpoints in 2 routers)
- T032-T035: Celery tasks (each task independent)
- T036-T039: Message composition methods
- T040-T045: Reply processing methods
- T046-T049: Validation logic

**Sequential constraint**: T027 (send endpoint) must complete before T050 (integration)

### Phase 4: US2 (After sms_preferences table exists)

**Launch in parallel**:
- T053-T057: API endpoints (5 separate endpoints)
- T058-T062: Phone verification methods
- T063-T069: Frontend UI components
- T070-T072: Opt-in compliance logic
- T073-T075: Preference management methods

**Sequential constraint**: T053-T057 (API endpoints) must complete before T063-T069 (frontend UI that calls them)

### Phases 5-10: Enhancement User Stories

Each phase (US3-US8) can be implemented in parallel by different developers since they are independent user stories:

- **Developer A**: US3 (Broadcast) + US6 (Cost Management)
- **Developer B**: US4 (Reminders) + US7 (Templates)
- **Developer C**: US5 (Opt-Out) + US8 (Testing)

Within each phase, follow similar parallel pattern: API endpoints → Frontend UI → Integration, with most tasks parallelizable.

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**Week 1-2: Setup & Foundation**
- Complete Phase 1 (Setup: 4 tasks)
- Complete Phase 2 (Foundational: 18 tasks)
- **Milestone**: Database migrated, SMSService can send test SMS

**Week 3-4: User Story 1 (Assignment Notifications)**
- Complete Phase 3 (US1: 26 tasks)
- **Milestone**: Volunteers receive assignment SMS, can reply YES/NO

**Week 5-6: User Story 2 (Preference Configuration)**
- Complete Phase 4 (US2: 23 tasks)
- **Milestone**: Volunteers can verify phone, configure preferences

**Week 7: MVP Testing & Polish**
- E2E testing of complete MVP workflow
- Bug fixes and refinements
- Performance testing (delivery time, rate limiting)

**MVP COMPLETE** (71 tasks, ~7 weeks)

**Post-MVP: Incremental Delivery**

- **Sprint 1**: US3 (Broadcast) + US5 (Opt-Out) - Critical for production
- **Sprint 2**: US4 (Reminders) + US6 (Cost) - High-value enhancements
- **Sprint 3**: US7 (Templates) + US8 (Testing) - Nice-to-have features
- **Sprint 4**: Phase 11 (Polish) - Production hardening

### Testing Strategy

**Unit Tests** (write alongside implementation):
- SMSService methods: `test_send_sms()`, `test_verify_phone()`, `test_process_reply()`
- RateLimiter: `test_check_rate_limit()`, `test_increment_counter()`
- QuietHours: `test_is_quiet_hours()`, `test_calculate_next_send_time()`

**Integration Tests** (after API endpoints complete):
- SMS API: `test_send_sms_endpoint()`, `test_broadcast_endpoint()`
- Webhooks: `test_twilio_status_webhook()`, `test_incoming_reply_webhook()`
- Celery tasks: `test_send_assignment_notification_task()`

**E2E Tests** (after frontend UI complete):
- Assignment workflow: `test_assign_volunteer_sends_sms()`
- Preference workflow: `test_verify_phone_and_save_preferences()`
- Broadcast workflow: `test_admin_broadcast_to_team()`

---

## Success Metrics

### MVP Success (US1 + US2)

- ✅ 95% of assignment SMS delivered within 30 seconds
- ✅ 98% SMS open rate vs 20% email open rate
- ✅ 90% phone verification completion rate
- ✅ 100% TCPA compliance (double opt-in enforced)

### Full Feature Success (US1-US8)

- ✅ 60% reduction in last-minute schedule gaps
- ✅ 70% reduction in message composition time (templates)
- ✅ 98% delivery success rate
- ✅ 100% budget compliance (no overages)
- ✅ <30s SMS delivery time (p95)
- ✅ Zero TCPA violations

---

**Next Step**: Begin with Phase 1 (Setup) → Install Twilio SDK, configure credentials, add i18n translations

**Autonomous Execution**: Each task is specific enough for LLM to complete without additional context. File paths provided. Dependencies documented. MVP scope clear.
