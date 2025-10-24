# Feature Specification: SMS Notification System

**Feature Branch**: `019-sms-notifications`
**Created**: 2025-10-22
**Status**: Draft
**Type**: Communication Enhancement (Medium Value)

---

## Overview

**Purpose**: Provide SMS-based notification delivery as an alternative to email, enabling volunteers to receive time-sensitive alerts (assignment requests, schedule changes, reminders) via text messages with immediate visibility and high engagement rates, particularly for volunteers who don't regularly check email.

**Business Value**: Increases volunteer response rates by 250% (SMS open rates 98% vs email 20%), reduces last-minute schedule gaps by 60% through immediate notification delivery, and enables real-time two-way communication where volunteers can confirm or decline assignments via simple text replies.

**Target Users**: Volunteer users receiving SMS notifications on mobile phones, Administrator users sending broadcast messages and managing SMS preferences.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Assignment Notification via SMS (Priority: P1)

Volunteer receives SMS alert when assigned to upcoming event with concise message containing event details (date, time, role, location) and action options (reply YES to confirm, NO to decline), enabling immediate response without opening email or app.

**Why this priority**: P1 - This is the core SMS notification use case. 70% of volunteers prefer SMS for time-sensitive notifications. Without assignment SMS delivery, the feature provides no immediate value and volunteers miss critical assignments.

**Independent Test**: Create event with assignment. Configure volunteer for SMS notifications. Trigger assignment notification. Verify SMS delivered within 30 seconds containing event name, date, time, role. Verify volunteer can reply YES to confirm. Verify confirmation updates assignment status.

**Acceptance Scenarios**:

1. **Given** volunteer has SMS notifications enabled with valid phone number, **When** administrator assigns them to event, **Then** SMS delivered within 30 seconds with message: "[Event Name] - [Date] [Time] - Role: [Role] - Reply YES to confirm, NO to decline"
2. **Given** volunteer receives assignment SMS, **When** they reply "YES" to confirmation number, **Then** assignment status updates to "confirmed" within 60 seconds and volunteer receives confirmation SMS "Assignment confirmed for [Event Name]"
3. **Given** volunteer receives assignment SMS, **When** they reply "NO" to decline, **Then** assignment is removed, administrator receives notification, and volunteer receives SMS "You have declined [Event Name]. Administrator has been notified."

---

### User Story 2 - Configure SMS Notification Preferences (Priority: P1)

Volunteer configures notification preferences choosing SMS, email, or both for different notification types (assignment requests, schedule reminders, schedule changes, event cancellations) with phone number verification and opt-in confirmation required before SMS delivery begins.

**Why this priority**: P1 - Preference configuration is prerequisite for all SMS functionality. TCPA compliance mandates explicit opt-in. Without preference management, system cannot legally send SMS messages.

**Independent Test**: Navigate to notification settings. Enter phone number. Verify validation (format check, deliverability via Twilio lookup). Receive verification SMS with code. Enter code to confirm opt-in. Select notification types for SMS delivery. Save preferences. Verify SMS delivered only for selected types.

**Acceptance Scenarios**:

1. **Given** volunteer accesses notification preferences, **When** they enter phone number, **Then** system validates format (E.164 standard), verifies deliverability via Twilio Lookup API, and detects landlines (cannot receive SMS) with error message "This phone number cannot receive SMS messages"
2. **Given** volunteer submits valid mobile number, **When** they click "Verify Number", **Then** SMS verification code sent within 30 seconds with message "SignUpFlow verification code: [6-digit code]. Reply with this code to enable SMS notifications"
3. **Given** volunteer enters correct verification code, **When** they select notification types (assignment requests, reminders, changes), **Then** preferences save and volunteer receives confirmation SMS "SMS notifications enabled for SignUpFlow. Reply STOP to unsubscribe anytime"

---

### User Story 3 - Send Broadcast Message to Team (Priority: P2)

Administrator sends urgent broadcast SMS to entire team or selected volunteers with concise message (max 160 chars recommended) for time-critical updates (event cancellation, schedule change, weather alert) with delivery tracking showing message status for each recipient.

**Why this priority**: P2 - Broadcast messaging enables rapid communication for urgent situations. Used infrequently (1-2x per month) but critical when needed. Lower priority than individual assignment notifications which occur daily.

**Independent Test**: As administrator, compose broadcast message (<160 chars). Select recipients (team or individual volunteers). Send message. Verify delivery tracking shows status for each recipient (queued, sent, delivered, failed). Verify rate limiting applied (batched to avoid carrier limits). Verify all recipients receive SMS within 5 minutes.

**Acceptance Scenarios**:

1. **Given** administrator composes broadcast message, **When** message exceeds 160 characters, **Then** character count displays with warning "Message will be split into [N] parts. Recommended: keep under 160 characters" and estimated cost shown
2. **Given** administrator selects 50 team members as recipients, **When** they send broadcast, **Then** messages batched (10 per minute to avoid carrier rate limits) and delivery tracking shows real-time status for each recipient with timestamps
3. **Given** broadcast message sent to team, **When** delivery completes, **Then** administrator receives summary notification: "[X] delivered, [Y] failed" with option to view detailed delivery report and retry failed messages

---

### User Story 4 - Automatic Schedule Reminder SMS (Priority: P2)

Volunteer receives automatic reminder SMS 24 hours before assigned event with event details and location, reducing missed assignments and providing advance notice to volunteers who may forget upcoming commitments.

**Why this priority**: P2 - Automatic reminders significantly reduce no-shows (40% reduction based on industry data) but are enhancement to core notification system. Can be added after assignment notifications working.

**Independent Test**: Create event scheduled 24 hours from now. Assign volunteer with SMS reminders enabled. Wait for scheduled reminder time (or trigger manually). Verify volunteer receives reminder SMS 24h before event with event name, date, time, location. Verify reminder not sent if volunteer already confirmed.

**Acceptance Scenarios**:

1. **Given** volunteer assigned to event 24 hours from now, **When** reminder scheduled job runs, **Then** volunteer receives SMS: "Reminder: [Event Name] tomorrow at [Time]. Location: [Address]. See you there!"
2. **Given** event includes location address, **When** reminder SMS sent, **Then** message includes "Get directions: [Google Maps short link]" for one-tap navigation to event location
3. **Given** volunteer already confirmed assignment, **When** 24h reminder time arrives, **Then** reminder SMS not sent (avoid duplicate messages) but volunteer receives SMS "You're confirmed for [Event Name] tomorrow at [Time]" instead

---

### User Story 5 - SMS Opt-Out and Compliance (Priority: P2)

Volunteer opts out of SMS notifications by replying "STOP" to any message, immediately disabling future SMS delivery with confirmation message and compliance audit trail, meeting TCPA requirements for SMS marketing regulations.

**Why this priority**: P2 - TCPA compliance is legally required but opt-out scenarios are infrequent (1-5% of users). Must be implemented before production launch but lower priority than core messaging functionality.

**Independent Test**: Volunteer receives SMS notification. Reply "STOP" to message. Verify SMS notifications immediately disabled. Verify confirmation SMS sent: "You have unsubscribed from SignUpFlow SMS. You will no longer receive text messages." Verify opt-out logged in audit trail with timestamp. Verify future notifications sent via email only.

**Acceptance Scenarios**:

1. **Given** volunteer receives any SMS from system, **When** they reply "STOP", **Then** SMS notifications immediately disabled (within 60 seconds), volunteer receives confirmation "You have unsubscribed from SignUpFlow SMS notifications. You will receive email notifications instead. Reply START to re-enable", and opt-out logged with timestamp for compliance
2. **Given** volunteer has opted out via STOP, **When** administrator attempts to send broadcast SMS, **Then** opted-out volunteer excluded from recipient list automatically with admin warning "[N] recipients excluded due to opt-out"
3. **Given** volunteer wants to re-enable SMS after opting out, **When** they reply "START" to any previous message, **Then** SMS re-enabled, verification code sent for confirmation, and volunteer receives "Welcome back! Reply with verification code [6-digit code] to resume SMS notifications"

---

### User Story 6 - SMS Cost Management and Budgeting (Priority: P3)

Administrator monitors SMS usage and costs with monthly budget limits, receives alerts when approaching limit (80% usage), and can upgrade to higher tier or disable non-critical messages to stay within budget, preventing unexpected overage charges.

**Why this priority**: P3 - Cost management prevents budget overruns but is enhancement feature. Initial deployments have predictable costs ($50-200/month for typical organizations). Can be added after core SMS functionality stable.

**Independent Test**: Set organization monthly SMS budget ($100). Send messages approaching limit. Verify alert at 80% usage. Verify non-critical messages (reminders) automatically paused at 100% limit. Verify critical messages (assignment requests) still sent. Verify administrator can increase budget or disable SMS.

**Acceptance Scenarios**:

1. **Given** organization set monthly SMS budget $100, **When** usage reaches $80 (80% of limit), **Then** administrator receives email and in-app alert: "SMS usage at 80% ($80 of $100). Estimated to exceed budget by [Date] based on current usage. Consider upgrading or reducing non-critical messages"
2. **Given** SMS usage reaches 100% of monthly budget, **When** non-critical message (reminder) triggered, **Then** message queued but not sent, administrator receives notification "[N] reminders queued due to budget limit. Critical assignment notifications will continue. Increase budget or wait until next billing cycle to send queued messages"
3. **Given** organization approaching SMS budget limit, **When** administrator reviews SMS analytics dashboard, **Then** dashboard shows: total messages sent, cost breakdown by type (assignments, reminders, broadcasts), top recipients, and monthly trend chart with budget utilization forecast

---

### User Story 7 - Message Templates and Personalization (Priority: P3)

Administrator creates reusable SMS message templates for common scenarios (assignment reminder, schedule change, event cancellation) with dynamic variable substitution (volunteer name, event details, date/time) and bilingual support (English, Spanish) based on volunteer language preference.

**Why this priority**: P3 - Templates improve efficiency and consistency but are enhancement. Administrators can manually compose messages initially. Templates add convenience after core functionality proven.

**Independent Test**: Create message template "Reminder: [event_name] on [date] at [time]. See you there, [volunteer_name]!". Send to volunteer. Verify variables replaced with actual values. Verify volunteer with Spanish preference receives Spanish version. Verify template reusable for future messages.

**Acceptance Scenarios**:

1. **Given** administrator creates template "Assignment for [event_name] on [date] at [time]. Reply YES to confirm", **When** template sent to volunteer, **Then** variables replaced with actual event data: "Assignment for Sunday Service on Nov 15 at 10:00 AM. Reply YES to confirm"
2. **Given** volunteer has language preference set to Spanish, **When** template message sent, **Then** volunteer receives Spanish translation: "Asignación para [event_name] el [date] a las [time]. Responde SÍ para confirmar" with date/time localized to Spanish format
3. **Given** administrator views template library, **When** they select pre-built template categories (assignment, reminder, cancellation, schedule change), **Then** templates include recommended character counts, response options, and variable placeholders with examples

---

### User Story 8 - SMS Delivery Troubleshooting and Testing (Priority: P3)

Administrator tests SMS delivery by sending test message to their own phone number before broadcasting to volunteers, verifies message formatting and delivery time, and accesses delivery logs showing detailed status (queued, sent, delivered, failed) for troubleshooting failed messages.

**Why this priority**: P3 - Testing and troubleshooting are important for reliability but not needed for basic functionality. Most messages deliver successfully. Testing features add confidence and debugging capability for edge cases.

**Independent Test**: As administrator, use "Send Test SMS" feature. Enter own phone number. Send test message. Verify message received with correct formatting. View delivery log showing status transitions (queued → sent → delivered) with timestamps. Simulate failure scenario. Verify failure logged with error reason. Verify retry option available.

**Acceptance Scenarios**:

1. **Given** administrator preparing broadcast message, **When** they click "Send Test", **Then** test mode UI appears with field for admin phone number, option to preview message with sample data, and "Send Test SMS" button that delivers only to admin number without affecting volunteer recipients
2. **Given** test SMS sent to administrator, **When** they receive message, **Then** message includes header "[TEST]" and footer "This is a test message from SignUpFlow" to distinguish from live messages, and admin sees delivery confirmation within 30 seconds
3. **Given** SMS message failed to deliver, **When** administrator views delivery log, **Then** log shows detailed error: "Failed: Invalid phone number", "Failed: Carrier rejected - landline cannot receive SMS", "Failed: Carrier rate limit - retry in 5 minutes" with option to manually retry failed messages

---

### Edge Cases

- **What happens when volunteer phone number becomes invalid (disconnected, carrier change)?** - System detects undeliverable status from Twilio webhook, marks phone number invalid, sends notification to administrator, and automatically falls back to email notifications for that volunteer.
- **How does system handle SMS delivery during carrier outages?** - Messages queue locally with retry logic (exponential backoff: retry after 1min, 5min, 15min, 1hr), delivery status tracked, and administrator notified if messages delayed > 1 hour.
- **What happens when volunteer replies with unexpected text (not YES/NO)?** - System sends auto-reply "Reply YES to confirm or NO to decline assignment for [Event Name]. Reply HELP for assistance, STOP to unsubscribe" with friendly tone and clear instructions.
- **How does system handle international phone numbers and SMS costs?** - International numbers supported via Twilio international SMS pricing ($0.10-0.50 per message), administrator warned of higher costs during configuration, and international messages excluded from default budget calculations.
- **What happens during quiet hours (10pm-8am volunteer local time)?** - Non-urgent messages (reminders, broadcasts) queued and sent at 8am local time the next day. Urgent messages (last-minute assignment requests <4 hours before event) bypass quiet hours with special handling.
- **How does system prevent SMS spam and abuse?** - Rate limiting enforces maximum 3 SMS per volunteer per day (excludes critical assignments), administrator sending patterns monitored for abuse (>1000 messages/day triggers review), and Twilio's built-in spam protection applied.
- **What happens when volunteer changes phone number?** - Old number marked inactive after verification SMS fails, volunteer prompted to update number in preferences, new number requires re-verification (TCPA compliance), and preference settings transfer to new number automatically.
- **How does system handle long messages exceeding 160 characters?** - Messages auto-split into segments (160 chars standard SMS, up to 10 segments = 1600 chars total), administrator warned of segment count and cost multiplier (3 segments = 3x cost), and long messages encouraged to include link to full details in app.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Twilio Integration and Message Delivery

- **FR-001**: System MUST integrate with Twilio SMS API for message sending, delivery tracking, and status webhooks
- **FR-002**: System MUST support Twilio Lookup API for phone number validation (format, type, carrier) before sending first SMS
- **FR-003**: SMS messages MUST deliver within 30 seconds of trigger event (95th percentile) for assignment notifications
- **FR-004**: System MUST track message delivery status (queued, sent, delivered, failed, undelivered) via Twilio status webhooks
- **FR-005**: Failed messages MUST implement retry logic with exponential backoff (retry after 1min, 5min, 15min, 1hr) up to 4 retry attempts

#### Notification Preference Management

- **FR-006**: Volunteers MUST configure notification preferences selecting SMS, email, or both for each notification type (assignment requests, reminders, schedule changes, cancellations)
- **FR-007**: Phone number entry MUST validate format (E.164 international standard: +1234567890) and detect landlines (cannot receive SMS) with clear error messages
- **FR-008**: New phone numbers MUST require SMS verification via 6-digit code sent to number before enabling SMS notifications
- **FR-009**: Verification codes MUST expire after 10 minutes and allow maximum 3 attempts before requiring new code generation
- **FR-010**: Preference changes MUST take effect immediately (within 60 seconds) for future notifications

#### Message Content and Formatting

- **FR-011**: SMS messages MUST be concise with recommended maximum 160 characters to fit single SMS segment
- **FR-012**: Messages exceeding 160 characters MUST auto-split into segments with administrator warning showing segment count and cost multiplier
- **FR-013**: Assignment notification SMS MUST include event name, date, time, role, and response options (reply YES/NO)
- **FR-014**: Reminder SMS MUST include event name, date, time, location, and optional directions link
- **FR-015**: Broadcast messages MUST include sender identifier "SignUpFlow: [message]" to indicate organizational source

#### Two-Way SMS Communication

- **FR-016**: System MUST process incoming SMS replies (YES, NO, STOP, START, HELP) and take appropriate action within 60 seconds
- **FR-017**: "YES" replies to assignment notifications MUST update assignment status to "confirmed" and send confirmation SMS
- **FR-018**: "NO" replies to assignment notifications MUST remove assignment, notify administrator, and send declination confirmation SMS
- **FR-019**: "HELP" replies MUST send auto-response with instructions and support contact information
- **FR-020**: Unrecognized replies MUST send auto-response explaining valid options (YES/NO/STOP/HELP)

#### TCPA Compliance and Opt-In/Opt-Out

- **FR-021**: System MUST require explicit opt-in via SMS verification before sending any messages (TCPA compliance)
- **FR-022**: Opt-in confirmation SMS MUST include clear statement: "You have opted in to SMS notifications from SignUpFlow. Reply STOP to unsubscribe anytime"
- **FR-023**: "STOP" replies MUST immediately disable SMS notifications (within 60 seconds), send confirmation SMS, and log opt-out for audit trail
- **FR-024**: "START" replies from opted-out users MUST re-enable SMS after verification code confirmation
- **FR-025**: Opted-out volunteers MUST be automatically excluded from all future SMS broadcasts with administrator notification showing excluded count

#### Rate Limiting and Quiet Hours

- **FR-026**: System MUST enforce rate limit of maximum 3 SMS per volunteer per day (excludes critical assignment requests within 4 hours of event)
- **FR-027**: Non-urgent messages (reminders, broadcasts) MUST respect quiet hours (10pm-8am volunteer local time) and queue for 8am delivery
- **FR-028**: Urgent messages (assignment requests <4 hours before event) MUST bypass quiet hours with special handling flag
- **FR-029**: Broadcast messages MUST batch at rate of 10 messages per minute to avoid carrier rate limits and prevent spam flags
- **FR-030**: System MUST track sending patterns and alert administrators if unusual volume detected (>1000 messages/day for organization)

#### Cost Management and Budgeting

- **FR-031**: Organizations MUST set monthly SMS budget limit ($50, $100, $200, custom) with default $100 for new organizations
- **FR-032**: System MUST track SMS usage costs by message type (assignment, reminder, broadcast) and calculate monthly totals
- **FR-033**: Administrators MUST receive alert when SMS usage reaches 80% of monthly budget with projected overage date
- **FR-034**: Non-critical messages (reminders) MUST pause automatically when budget reaches 100% while critical messages (assignments) continue
- **FR-035**: SMS analytics dashboard MUST display: messages sent, cost by type, top recipients, monthly trend, and budget utilization forecast

#### Message Templates and Variables

- **FR-036**: Administrators MUST create reusable message templates with dynamic variable placeholders ([event_name], [date], [time], [volunteer_name])
- **FR-037**: Templates MUST support variable substitution replacing placeholders with actual event/volunteer data before sending
- **FR-038**: System MUST provide pre-built template library for common scenarios (assignment, reminder, cancellation, schedule change)
- **FR-039**: Templates MUST support bilingual content (English, Spanish) with automatic language selection based on volunteer preference
- **FR-040**: Variable substitution MUST handle missing data gracefully (e.g., if no location, omit location line rather than showing "[location]")

#### Delivery Tracking and Audit Trail

- **FR-041**: System MUST log all sent SMS messages with timestamp, recipient, content, delivery status, and cost for audit purposes
- **FR-042**: Message history MUST be searchable and filterable by date range, recipient, message type, and delivery status
- **FR-043**: Delivery tracking MUST update in real-time based on Twilio status webhooks (delivered, failed, undelivered)
- **FR-044**: Failed messages MUST log detailed error reason (invalid number, landline, carrier rejected, rate limit) for troubleshooting
- **FR-045**: Delivery logs MUST be retained for minimum 90 days for compliance and support purposes

#### Testing and Troubleshooting

- **FR-046**: Administrators MUST send test SMS to own phone number before broadcasting to volunteers
- **FR-047**: Test mode MUST deliver message only to administrator number with [TEST] header and test footer indicating test message
- **FR-048**: Test messages MUST not count toward volunteer rate limits or organization budget
- **FR-049**: Delivery logs MUST provide detailed status timeline showing message progression through queued → sent → delivered states with timestamps
- **FR-050**: Administrators MUST manually retry failed messages individually or in batch from delivery log interface

### Key Entities

- **SmsPreference**: Volunteer SMS notification preferences with fields: phone_number (E.164 format), verified (boolean), notification_types (array: assignment, reminder, change, cancellation), opt_in_date (timestamp), opt_out_date (timestamp if unsubscribed), language (en or es)

- **SmsMessage**: Sent SMS message record with fields: recipient (volunteer_id), phone_number, message_text, message_type (assignment/reminder/broadcast/system), event_id (if applicable), status (queued/sent/delivered/failed), twilio_message_sid, cost_cents, sent_at (timestamp), delivered_at (timestamp), error_message (if failed)

- **SmsTemplate**: Reusable message template with fields: name, template_text (with variable placeholders), message_type, character_count, translations (en/es versions), usage_count, created_by (admin_id)

- **SmsUsage**: Monthly SMS usage tracking with fields: organization_id, month_year, messages_sent (count by type), total_cost_cents, budget_limit_cents, budget_alerts_sent (count), current_utilization_percent

- **SmsBudget**: Organization SMS budget configuration with fields: organization_id, monthly_limit_cents, current_period_spend_cents, alert_threshold_percent (default 80%), auto_pause_enabled (boolean), upgrade_tier_available

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: SMS assignment notifications deliver within 30 seconds of trigger event in 95% of cases with delivery confirmation within 2 minutes
- **SC-002**: Volunteer response rate to assignment requests increases by 250% for SMS vs email (98% SMS open rate vs 20% email open rate)
- **SC-003**: Last-minute schedule gaps (assignments <24 hours before event) reduce by 60% due to immediate SMS delivery and response capability
- **SC-004**: Phone number verification completes successfully for 95% of mobile numbers with clear error messaging for landlines and invalid numbers
- **SC-005**: TCPA compliance maintained at 100% with explicit opt-in required, opt-out processed within 60 seconds, and complete audit trail of all opt-in/opt-out actions
- **SC-006**: Rate limiting prevents SMS spam with maximum 3 messages per volunteer per day enforced (excludes urgent assignments) and carrier rate limits respected (10 messages/minute batching)
- **SC-007**: SMS cost management prevents budget overruns with 80% budget alerts sent proactively and non-critical messages auto-paused at 100% budget utilization
- **SC-008**: Message templates reduce administrator composition time by 70% compared to manual message writing for routine communications
- **SC-009**: Two-way SMS communication processes 95% of YES/NO replies within 60 seconds updating assignment status and sending confirmation messages automatically
- **SC-010**: Quiet hours compliance honors volunteer local time zones with 100% of non-urgent messages queued during 10pm-8am period and delivered at 8am next day
- **SC-011**: SMS delivery reliability achieves 98% successful delivery rate with failed messages automatically retried and administrators alerted to persistent failures
- **SC-012**: Testing mode enables administrators to verify message formatting and delivery with test messages sent successfully before broadcasting to 100+ volunteers

---

**Validation Date**: 2025-10-22
**Next Phase**: Planning (Design Twilio integration architecture, message queue system, compliance framework, cost tracking implementation)
