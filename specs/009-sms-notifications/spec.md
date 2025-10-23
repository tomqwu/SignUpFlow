# Feature Specification: SMS Notifications

**Feature Branch**: `009-sms-notifications`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "SMS notification system as alternative to email for volunteer communications..."

## User Scenarios & Testing

### User Story 1 - Receive SMS Assignment Reminders (Priority: P1)

Volunteer users receive SMS text messages 24 hours before their scheduled assignments as reminders. Messages include event name, date, time, and location in concise format (under 160 characters). Volunteers can reply YES to confirm or NO to decline directly via SMS.

**Why this priority**: Core SMS value proposition. Text message reminders have 98% open rate vs 20% email open rate, dramatically improving volunteer show-up rates. This is the primary reason organizations adopt SMS notifications.

**Independent Test**: Can be fully tested by triggering assignment reminder SMS to test phone number, verifying message delivery, and testing reply functionality. Delivers standalone value of improving volunteer attendance.

**Acceptance Scenarios**:

1. **Given** volunteer has assignment tomorrow, **When** system sends 24h reminder, **Then** volunteer receives SMS "Reminder: Sunday Service - Greeter tomorrow 10am at Main Campus" within 5 minutes
2. **Given** volunteer receives reminder SMS, **When** they reply "YES", **Then** system confirms attendance and sends "Thanks! See you tomorrow at 10am"
3. **Given** volunteer receives reminder SMS, **When** they reply "NO", **Then** system marks unavailability and sends "Got it. We'll find a replacement. Reply HELP for support"
4. **Given** multiple volunteers assigned to same event, **When** reminder triggers, **Then** system sends personalized SMS to each volunteer with their specific role
5. **Given** volunteer phone number invalid, **When** reminder attempts delivery, **Then** system logs failed delivery and notifies admin via email

---

### User Story 2 - Opt-In to SMS Notifications (Priority: P1)

Volunteer users opt-in to receive SMS notifications by providing phone number and confirming via double opt-in process. System validates phone number format, verifies deliverability, and sends confirmation code. Volunteers choose notification preferences (SMS only, email only, or both) for different notification types.

**Why this priority**: Legal requirement. SMS regulations (TCPA in US) mandate explicit opt-in before sending marketing/informational texts. Without compliant opt-in, organizations face legal liability. Must be implemented before any SMS can be sent.

**Independent Test**: Can be tested by entering phone number in profile settings, receiving confirmation SMS with code, entering code to complete opt-in, and verifying preferences saved. Delivers compliance with SMS regulations.

**Acceptance Scenarios**:

1. **Given** volunteer in profile settings, **When** they enter phone number and click "Enable SMS", **Then** system validates format (US: +1XXXXXXXXXX) and sends confirmation code via SMS
2. **Given** volunteer receives confirmation code, **When** they enter code within 10 minutes, **Then** system activates SMS notifications and displays "SMS enabled successfully"
3. **Given** volunteer enters invalid phone format, **When** they attempt to save, **Then** system displays error "Please enter valid phone number: +1XXXXXXXXXX"
4. **Given** phone number is landline, **When** system validates, **Then** system displays error "SMS not supported for landlines. Please enter mobile number"
5. **Given** volunteer completes opt-in, **When** they view preferences, **Then** options display: Assignment Reminders (SMS/Email/Both), Schedule Changes (SMS/Email/Both), Urgent Alerts (SMS/Email/Both)

---

### User Story 3 - Admin Broadcast Messages (Priority: P2)

Admin users send broadcast SMS to teams or individual volunteers for urgent communications (event cancellation, last-minute changes, emergency alerts). System provides preview of message, shows character count, allows selection of recipients (all volunteers, specific team, individual), and displays delivery status.

**Why this priority**: Critical for time-sensitive communications where email delays are unacceptable (weather cancellation, venue change, emergency situations). SMS ensures immediate delivery and high read rates for urgent information.

**Independent Test**: Can be tested by admin composing broadcast message, selecting recipients, previewing message, sending, and verifying delivery status dashboard shows sent/delivered/failed counts. Delivers urgent communication capability.

**Acceptance Scenarios**:

1. **Given** admin in Messages section, **When** they compose "Sunday Service CANCELLED due to weather", **Then** system shows character count (42/160), recipient count, and estimated cost
2. **Given** admin selects "Sunday Service Greeters" team, **When** they click Send, **Then** system sends SMS to all team members with SMS enabled and displays progress bar
3. **Given** broadcast sent, **When** delivery completes, **Then** admin sees summary "12 delivered, 1 failed (invalid number), 1 pending" with failed recipient details
4. **Given** admin composes message >160 characters, **When** system displays preview, **Then** indicator shows "2 SMS segments (320 chars max)" and increased cost
5. **Given** admin attempts broadcast at 11pm, **When** they click Send, **Then** system warns "Quiet hours (10pm-8am). Schedule for 8am or send urgent override?"

---

### User Story 4 - Automatic Schedule Change Notifications (Priority: P2)

Volunteers automatically receive SMS when their assignments change (time, location, role, or cancellation). Notifications sent immediately when admin makes changes. Messages include what changed, old vs new details, and link to view full schedule.

**Why this priority**: Prevents volunteers from showing up at wrong time/location or preparing for wrong role. Automatic notifications reduce admin workload (no manual calling) and improve volunteer satisfaction by keeping them informed.

**Independent Test**: Can be tested by admin changing assignment details and verifying affected volunteers receive SMS within 1 minute describing changes. Delivers automatic change notification capability.

**Acceptance Scenarios**:

1. **Given** admin changes Sunday Service time from 10am to 11am, **When** change saved, **Then** assigned volunteers receive "SCHEDULE CHANGE: Sunday Service moved to 11am (was 10am). View: [link]"
2. **Given** admin cancels event, **When** cancellation saved, **Then** assigned volunteers receive "CANCELLED: Sunday Service on July 15. You're no longer scheduled. Questions? Reply HELP"
3. **Given** admin swaps volunteer role from Greeter to Usher, **When** change saved, **Then** volunteer receives "ROLE CHANGE: Sunday Service - now Usher (was Greeter). Same time/location"
4. **Given** volunteer opted for email-only, **When** admin changes assignment, **Then** volunteer receives email notification only, not SMS
5. **Given** multiple changes to same assignment within 5 minutes, **When** changes saved, **Then** system batches into single SMS summarizing all changes

---

### User Story 5 - SMS Cost Management (Priority: P2)

Organizations track SMS usage against monthly limits with cost alerts when approaching limit. Admin dashboard shows SMS sent this month, remaining balance, cost per message, and projected usage. System prevents sending when limit exceeded unless admin approves overage.

**Why this priority**: SMS costs add up quickly at scale ($0.01-0.02 per message). Without cost controls, organizations risk unexpected bills. Monthly limits and alerts ensure predictable budgeting and prevent runaway costs.

**Independent Test**: Can be tested by simulating SMS sends, verifying counter increments, triggering alert at 80% limit, and blocking sends at 100% limit. Delivers cost control capability.

**Acceptance Scenarios**:

1. **Given** organization on 500 SMS/month plan, **When** admin views dashboard, **Then** displays "287/500 used this month (57%), $5.74 spent, resets Dec 1"
2. **Given** organization reaches 400 SMS (80% limit), **When** next SMS triggers, **Then** admin receives email alert "SMS usage at 80% (400/500). Consider upgrading plan"
3. **Given** organization reaches 500 SMS (100% limit), **When** admin attempts broadcast, **Then** system blocks send with "Monthly limit reached. Approve $10 overage for 100 SMS?"
4. **Given** admin approves overage, **When** confirmed, **Then** system allows additional 100 SMS and sends invoice for $10 overage at month end
5. **Given** multiple admins in organization, **When** any admin sends SMS, **Then** shared usage counter increments and all admins see updated dashboard

---

### User Story 6 - Opt-Out and STOP Keyword (Priority: P1)

Volunteers opt-out of SMS notifications by replying STOP to any message or disabling in profile settings. System immediately stops all SMS, sends confirmation "You're unsubscribed. No more texts. Text START to re-enable", and logs opt-out for compliance audit trail.

**Why this priority**: Legal compliance requirement. SMS regulations mandate easy opt-out mechanism. STOP keyword must work universally on all messages. Failure to honor opt-out requests results in fines up to $1,500 per violation.

**Independent Test**: Can be tested by replying STOP to any SMS, verifying all future SMS blocked, and testing profile setting toggle. Delivers regulatory compliance.

**Acceptance Scenarios**:

1. **Given** volunteer receives any SMS, **When** they reply "STOP", **Then** system unsubscribes them immediately and sends confirmation "You're unsubscribed from SignUpFlow SMS. Text START to resume"
2. **Given** volunteer unsubscribed, **When** admin attempts to send them SMS, **Then** system skips them and logs "Skipped: volunteer opted out on 2025-10-15"
3. **Given** volunteer unsubscribed, **When** they reply "START", **Then** system re-subscribes them and sends "Welcome back! SMS notifications re-enabled"
4. **Given** volunteer in profile settings, **When** they toggle "Receive SMS" off, **Then** system immediately stops SMS and displays "SMS disabled. You'll still receive emails"
5. **Given** volunteer opted out, **When** system generates compliance report, **Then** report includes opt-out date, method (STOP keyword vs profile), and audit trail

---

### User Story 7 - Message Templates and Personalization (Priority: P3)

Admins create reusable SMS templates for common scenarios (reminders, changes, cancellations) with dynamic variables for personalization. Templates include {{volunteer_name}}, {{event_name}}, {{date}}, {{time}}, {{location}}. System automatically substitutes variables when sending.

**Why this priority**: Improves efficiency and consistency. Templates ensure professional messaging and save admin time. Personalization increases engagement (volunteers respond better to messages using their name). Can be implemented after core SMS functionality stable.

**Independent Test**: Can be tested by creating template with variables, sending test message, and verifying variables replaced with actual data. Delivers template management capability.

**Acceptance Scenarios**:

1. **Given** admin in Templates section, **When** they create "Hi {{volunteer_name}}, reminder for {{event_name}} tomorrow at {{time}}", **Then** system validates variables and saves template
2. **Given** template exists, **When** admin sends reminder using template, **Then** system replaces {{volunteer_name}} with "John", {{event_name}} with "Sunday Service", {{time}} with "10am"
3. **Given** admin composes new message, **When** they click "Insert Variable", **Then** dropdown shows: volunteer_name, event_name, date, time, location, role
4. **Given** template includes invalid variable {{phone_number}}, **When** admin attempts to save, **Then** system displays error "Invalid variable: phone_number. Allowed: volunteer_name, event_name, date, time, location, role"
5. **Given** organization with bilingual volunteers, **When** sending template to Spanish-speaking volunteer, **Then** system uses Spanish template version based on volunteer language preference

---

### Edge Cases

- **SMS Delivery Failures**: What happens when carrier rejects SMS (invalid number, blocked, carrier issue)? System must retry once after 5 minutes, log permanent failure after 2 attempts, and notify admin of undeliverable numbers for cleanup.

- **International Phone Numbers**: How does system handle non-US phone numbers (+44 UK, +52 Mexico, etc.)? System validates international formats, charges international rates (disclosed upfront), and warns admin if organization plan doesn't include international SMS.

- **Duplicate Phone Numbers**: What if multiple volunteers share same phone number (family members, spouses)? System detects duplicates, sends single SMS with combined information, and flags for admin review to confirm intentional sharing.

- **Message Truncation**: What happens if personalized message exceeds 160 character limit after variable substitution? System counts final length including variables, warns during template creation, and splits into multiple segments automatically if needed.

- **Rate Limit Exceeded**: What if organization sends 100 SMS in 1 minute exceeding carrier throughput limits? System queues messages, sends at carrier-allowed rate (10/second for Twilio), and displays "Sending 100 messages (ETA: 10 seconds)".

- **Timezone Confusion**: What if volunteer in different timezone receives "tomorrow 10am" reminder but timezone ambiguous? System always uses volunteer's timezone from profile, converts times appropriately, and includes timezone in message "tomorrow 10am PST".

- **Reply to Wrong Number**: What if volunteer replies to SMS from different phone than registered? System matches phone numbers, warns "Reply received from unregistered number. Call support to update", and logs for security audit.

- **Quiet Hours Override**: What if emergency requires sending SMS during quiet hours (10pm-8am)? Admin can mark message "Urgent" bypassing quiet hours restriction, system requires confirmation "Send to 50 volunteers despite quiet hours?", and logs override for review.

## Requirements

### SMS Delivery System

- **FR-001**: System MUST send SMS to volunteers with opt-in consent via SMS gateway service supporting message delivery, status tracking, and reply handling
- **FR-002**: SMS sending MUST complete within 5 minutes from trigger (reminder, schedule change, admin broadcast) with delivery confirmation
- **FR-003**: System MUST track message delivery status with states: queued, sent, delivered, failed, undelivered with timestamp for each state transition
- **FR-004**: System MUST retry failed SMS once after 5-minute delay, mark as permanently failed after 2 attempts, and log error details
- **FR-005**: System MUST support standard SMS (160 characters) and multi-part SMS (up to 1600 characters split into 10 segments) with automatic segmentation
- **FR-006**: System MUST include opt-out instruction in first message to new phone number: "Reply STOP to unsubscribe"

### Opt-In and Consent Management

- **FR-007**: System MUST require double opt-in process: volunteer provides phone number, receives confirmation code, enters code to activate
- **FR-008**: Confirmation codes MUST be 6-digit numbers, valid for 10 minutes, and expire after 3 failed attempts
- **FR-009**: System MUST validate phone number format (E.164 international format: +[country][number]) before sending confirmation
- **FR-010**: System MUST verify phone number deliverability by checking carrier type (mobile vs landline) and block landlines with error message
- **FR-011**: System MUST maintain opt-in consent record with timestamp, IP address, phone number, and confirmation method for compliance audit
- **FR-012**: System MUST display clear terms of service before opt-in explaining message frequency, standard rates may apply, and opt-out instructions

### Opt-Out and STOP Keyword

- **FR-013**: System MUST immediately stop all SMS to volunteer when they reply with STOP keyword (case-insensitive) to any message
- **FR-014**: System MUST send confirmation message after STOP received: "You're unsubscribed. No more texts. Text START to re-enable"
- **FR-015**: System MUST support START keyword for re-subscription sending confirmation "Welcome back! SMS notifications re-enabled"
- **FR-016**: System MUST support HELP keyword sending automated reply with support contact information
- **FR-017**: System MUST allow opt-out via profile settings with toggle switch for SMS notifications
- **FR-018**: Opt-out MUST take effect immediately (within 1 minute) preventing any queued or future SMS to that phone number

### Notification Preferences

- **FR-019**: Volunteers MUST choose notification method per notification type: Assignment Reminders (SMS/Email/Both), Schedule Changes (SMS/Email/Both), Urgent Alerts (SMS/Email/Both)
- **FR-020**: System MUST respect quiet hours (10pm-8am in volunteer's local timezone) by default, queuing SMS for 8am delivery
- **FR-021**: System MUST allow admin to mark broadcast as "Urgent" bypassing quiet hours with confirmation prompt before sending
- **FR-022**: System MUST support bilingual SMS content (English/Spanish) based on volunteer language preference in profile

### Rate Limiting and Spam Prevention

- **FR-023**: System MUST limit SMS to maximum 3 messages per volunteer per day (excludes urgent messages marked by admin)
- **FR-024**: System MUST batch multiple notifications within 5-minute window into single SMS summarizing all changes
- **FR-025**: System MUST throttle outbound SMS to comply with carrier rate limits (default: 10 messages per second)

### Cost Management

- **FR-026**: System MUST track SMS usage per organization with counters: sent this month, failed, delivered, cost accumulated
- **FR-027**: Organizations MUST have monthly SMS limit (default: 500 messages) with usage tracking displayed on admin dashboard
- **FR-028**: System MUST alert admins at 80% usage via email with message "SMS usage at 80% (400/500). Consider upgrading"
- **FR-029**: System MUST block new SMS when 100% limit reached unless admin approves overage with confirmation "Approve $X overage for Y additional messages?"
- **FR-030**: System MUST reset monthly counters on first day of billing cycle and send usage report email to admins

### Message Templates

- **FR-031**: System MUST provide message templates for common scenarios: assignment reminder, schedule change, event cancellation, urgent alert
- **FR-032**: Templates MUST support dynamic variable substitution: {{volunteer_name}}, {{event_name}}, {{date}}, {{time}}, {{location}}, {{role}}
- **FR-033**: System MUST validate template character count including variables with maximum expanded length warning
- **FR-034**: Admins MUST be able to create custom templates with variable insertion and preview of personalized output

### Reply Handling

- **FR-035**: System MUST accept replies to assignment reminders: YES (confirm), NO (decline), HELP (support info)
- **FR-036**: Reply YES MUST mark volunteer attendance as confirmed and send acknowledgment "Thanks! See you at [event]"
- **FR-037**: Reply NO MUST mark volunteer as unavailable for that assignment and send acknowledgment "Got it. We'll find replacement"
- **FR-038**: Unrecognized replies MUST trigger automated response "Reply YES to confirm, NO to decline, STOP to unsubscribe, HELP for support"

### Message History and Audit Trail

- **FR-039**: System MUST log all sent SMS with: timestamp, recipient phone, message content, delivery status, cost
- **FR-040**: Admins MUST be able to view message history filtered by: date range, recipient, status, message type
- **FR-041**: System MUST retain message history for 12 months for compliance audit purposes
- **FR-042**: Opt-out requests MUST be logged with: timestamp, phone number, method (STOP keyword, profile toggle, admin action), IP address

### Testing and Preview

- **FR-043**: Admins MUST be able to send test SMS to own phone number before broadcasting to volunteers
- **FR-044**: Test mode MUST show actual message content with personalization but not count toward usage limits or cost
- **FR-045**: Broadcast preview MUST display: recipient count, estimated cost, message content, character count, segment count

### Key Entities

- **SMSMessage**: Sent text message record with content, recipient phone, volunteer reference, delivery status, timestamps, cost, and reply received
- **SMSOptIn**: Consent record with phone number, volunteer reference, opt-in timestamp, confirmation method, IP address, and opt-out timestamp if applicable
- **SMSTemplate**: Reusable message template with name, content with variables, character count, language, and usage count
- **SMSUsageLimit**: Organization monthly SMS quota with limit count, used count, overage count, billing cycle start, and cost tracking
- **SMSDeliveryStatus**: Message delivery state tracking with status (queued, sent, delivered, failed), timestamp, error code if failed, and retry attempts

## Success Criteria

### Measurable Outcomes

- **SC-001**: Volunteers receive SMS reminders within 5 minutes of scheduled send time with 95% delivery rate
- **SC-002**: Volunteer attendance rate improves by 30% for events with SMS reminders compared to email-only
- **SC-003**: SMS open rate achieves 98% or higher (industry standard) compared to 20% for email
- **SC-004**: Opt-in process completion rate achieves 80% or higher from volunteers who start phone number entry
- **SC-005**: SMS costs remain predictable with 95% of organizations staying within monthly limits
- **SC-006**: Opt-out requests processed within 1 minute with 100% compliance (zero SMS sent after opt-out)
- **SC-007**: Reply handling (YES/NO) achieves 90% accuracy with appropriate system actions
- **SC-008**: Broadcast messages reach all intended recipients within 2 minutes for groups up to 100 volunteers
- **SC-009**: Admin time savings of 80% for urgent communications compared to individual phone calls
- **SC-010**: Zero regulatory violations (TCPA compliance) measured by zero opt-out related complaints or fines

## Assumptions

1. **SMS Gateway Provider**: Assumes integration with Twilio SMS API as primary gateway. Rationale: Industry-standard provider with 99.95% uptime, comprehensive API, and competitive pricing ($0.0079/SMS US).

2. **US-Centric Initially**: Assumes initial rollout targets US organizations with US phone numbers (+1 country code). International expansion as Phase 2. Rationale: Focus resources on single regulatory environment (TCPA) before adding international complexity.

3. **Mobile Phone Adoption**: Assumes 95% of volunteers have mobile phones capable of receiving SMS. Rationale: Mobile phone penetration in US exceeds 95% across all age groups.

4. **Carrier Support**: Assumes major carriers (Verizon, AT&T, T-Mobile, Sprint) support standard SMS features (reply, STOP keyword). Rationale: Carriers comply with CTIA Short Code Monitoring Handbook requirements.

5. **Opt-In Compliance**: Assumes volunteers provide explicit consent and understand terms before SMS enabled. Rationale: Required for TCPA compliance, reduces liability risk.

6. **Cost Acceptance**: Assumes organizations willing to pay SMS costs ($0.01/message) for improved volunteer engagement. Rationale: ROI positive if SMS reduces no-shows (volunteer replacement cost > SMS cost).

7. **Reply Rate**: Assumes 40-60% of volunteers will reply to interactive SMS (YES/NO prompts). Rationale: Industry average for two-way SMS engagement.

8. **Language Support**: Assumes English and Spanish cover 98% of US volunteer base. Additional languages added based on demand. Rationale: Spanish second most common language in US (13% population).

9. **Quiet Hours Standard**: Assumes 10pm-8am quiet hours appropriate across US timezones. Rationale: Aligns with TCPA safe harbor hours and industry best practices.

10. **Template Usage**: Assumes 80% of SMS sent via templates, 20% custom messages. Rationale: Common scenarios (reminders, changes) covered by templates, reducing admin effort.

## Dependencies

1. **SMS Gateway Service**: Requires active account with SMS gateway provider (Twilio) with API credentials, phone number provisioning, and billing setup
2. **Phone Number Validation Service**: Depends on carrier lookup API for validating phone numbers and detecting landlines vs mobile
3. **Existing Notification System**: Integrates with email notification infrastructure (feature 001) for unified preference management
4. **User Profile System**: Requires phone number field in Person model with validation, storage, and security (encryption at rest)
5. **Timezone Data**: Depends on volunteer timezone information for quiet hours enforcement and time-appropriate messaging

## Out of Scope

1. **MMS (Multimedia Messages)**: SMS text-only; image, video, or audio attachments not supported in initial version
2. **International SMS (Phase 1)**: Initial rollout US phone numbers only; international expansion (Canada, Mexico, UK) as Phase 2
3. **Voice Calls**: SMS notifications only; voice call reminders or interactive voice response (IVR) not included
4. **WhatsApp/RCS Integration**: SMS via cellular carrier networks only; messaging app integrations out of scope
5. **SMS Marketing Campaigns**: Transactional notifications only (reminders, changes); promotional/marketing SMS not supported
6. **Group Chat**: One-to-one SMS only; group messaging or volunteer-to-volunteer communication not included
7. **Rich Media Links**: URL shortening and link tracking not included; full URLs sent as-is
8. **A/B Testing**: Message content testing and optimization features not included; admins craft messages without testing variants
9. **Advanced Analytics**: Basic delivery tracking only; engagement analytics (click rates, conversion tracking) not included
10. **Custom Phone Numbers**: System-provided phone numbers only; branded short codes or vanity numbers not supported
