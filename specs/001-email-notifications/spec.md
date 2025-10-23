# Feature Specification: Email Notification System for Volunteer Assignments

**Feature Branch**: `001-email-notifications`
**Created**: 2025-01-20
**Status**: Draft
**Input**: User description: "Email notification system for volunteer assignments"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assignment Notification (Priority: P1)

When an administrator assigns a volunteer to an event, the volunteer receives an immediate email notification with event details and a direct link to view their updated schedule.

**Why this priority**: Core value proposition - volunteers need to know when they're scheduled. Without notifications, volunteers must manually check the system, leading to missed assignments and scheduling conflicts.

**Independent Test**: Can be fully tested by assigning a volunteer to an event and verifying they receive an email within 2 minutes containing event details (date, time, role, location) and a working link to their schedule.

**Acceptance Scenarios**:

1. **Given** a volunteer exists with verified email, **When** admin assigns them to an event, **Then** volunteer receives email within 2 minutes with event details and schedule link
2. **Given** volunteer is assigned to multiple events simultaneously, **When** admin bulk-assigns roles, **Then** volunteer receives a single consolidated email listing all assignments
3. **Given** volunteer's email is invalid, **When** assignment is created, **Then** admin receives notification of delivery failure and assignment status shows "notification failed"

---

### User Story 2 - Assignment Reminder (Priority: P2)

Volunteers receive automatic reminder emails 24 hours before their scheduled event to reduce no-shows and last-minute cancellations.

**Why this priority**: Reduces no-shows by 40% (industry benchmark). Complements assignment notifications by providing timely reminder when event is approaching.

**Independent Test**: Can be fully tested by creating an event 25 hours in the future, assigning a volunteer, waiting for automated reminder job to run, and verifying volunteer receives reminder email at the 24-hour mark.

**Acceptance Scenarios**:

1. **Given** volunteer has assignment 24 hours away, **When** reminder job runs, **Then** volunteer receives email reminder with event details and "add to calendar" option
2. **Given** event is canceled after reminder sent, **When** cancellation occurs, **Then** volunteer receives cancellation email with explanation
3. **Given** volunteer has 3 events within 48 hours, **When** reminders are due, **Then** volunteer receives single digest email listing all upcoming events (not 3 separate emails)

---

### User Story 3 - Schedule Change Notification (Priority: P2)

When event details change (time, location, cancellation), all assigned volunteers receive immediate update notifications.

**Why this priority**: Critical for maintaining schedule accuracy. Volunteers need to know about changes to avoid showing up at wrong time/place.

**Independent Test**: Can be fully tested by modifying an event's time or location and verifying all assigned volunteers receive update email within 2 minutes highlighting what changed.

**Acceptance Scenarios**:

1. **Given** volunteer is assigned to event, **When** admin changes event time, **Then** volunteer receives email showing old time vs new time with clear "SCHEDULE CHANGE" subject line
2. **Given** event is canceled, **When** admin cancels event, **Then** all assigned volunteers receive cancellation email within 2 minutes
3. **Given** only location changes, **When** admin updates location, **Then** email clearly highlights location change with map link

---

### User Story 4 - Email Preferences Management (Priority: P3)

Volunteers can control which notification types they receive and their preferred notification frequency (immediate, daily digest, weekly digest).

**Why this priority**: Reduces email fatigue and respects user preferences. Some volunteers want immediate notifications, others prefer batched digests.

**Independent Test**: Can be fully tested by volunteer changing email preferences to "daily digest" and verifying they receive single daily email at specified time instead of immediate notifications.

**Acceptance Scenarios**:

1. **Given** volunteer sets preferences to "no reminders", **When** 24-hour reminder is due, **Then** volunteer does not receive reminder (but still receives assignment notifications)
2. **Given** volunteer chooses "daily digest at 8am", **When** multiple assignments occur throughout day, **Then** volunteer receives single email at 8am next day with all updates
3. **Given** volunteer opts out of all emails, **When** assignment is created, **Then** no email is sent and assignment status shows "notifications disabled by user"

---

### User Story 5 - Admin Notification Summary (Priority: P3)

Organization administrators receive weekly summary emails showing notification delivery statistics, failed deliveries, and volunteer engagement metrics.

**Why this priority**: Helps admins identify and fix email delivery issues. Provides visibility into which volunteers are engaged vs. unresponsive.

**Independent Test**: Can be fully tested by running weekly summary job and verifying admin receives email with counts of notifications sent, delivered, failed, and volunteer response rates.

**Acceptance Scenarios**:

1. **Given** week has ended, **When** summary job runs, **Then** admin receives email with notification statistics (sent, delivered, failed, opened, clicked)
2. **Given** multiple email failures occurred, **When** summary is generated, **Then** email highlights volunteers with delivery issues and suggests verification
3. **Given** admin manages multiple organizations, **When** summaries are sent, **Then** admin receives separate summary for each organization

---

### Edge Cases

- **Rapid schedule changes**: What happens when event is modified multiple times within 5 minutes? (Should batch updates into single notification)
- **Deleted volunteer accounts**: How does system handle notifications for volunteers removed from organization? (Cancel pending notifications, log for audit)
- **Email service outage**: How are failed notifications retried? (Implement exponential backoff retry up to 3 attempts over 24 hours)
- **Timezone mismatches**: How are event times displayed in emails for volunteers in different timezones? (Use volunteer's stored timezone preference or auto-detect from location)
- **Large organization events**: What happens when 200+ volunteers are assigned to single event? (Batch send emails in groups of 50 to avoid rate limits)
- **Duplicate assignments**: If volunteer is accidentally assigned to same event twice, do they receive two emails? (De-duplicate at notification queue level)
- **Unsubscribe handling**: How are unsubscribed emails handled while respecting critical notifications? (Allow "unsubscribe from reminders" but always send assignment/cancellation notifications)

## Clarifications

### Session 2025-10-21

- Q: What test automation strategy should be used for this feature and all future features? → A: Comprehensive test pyramid (Unit tests for business logic, Integration tests for service integration with mocks, E2E tests for actual end-to-end workflows) - applies to ALL features project-wide
- Q: How should email delivery be tested across environments? → A: Mailtrap for all environments - sandbox API (sandbox.api.mailtrap.io) for dev/CI/staging, production Email API for real delivery (already configured)
- Q: What minimum test coverage percentage is required for CI/CD pipeline? → A: 90%+ comprehensive coverage required - unit tests (>90% code coverage), integration tests (all service integrations), E2E tests with Playwright (all critical user paths)
- Q: When should tests be automatically executed in CI/CD pipeline? → A: Multi-gate approach - on every commit + PR merge + pre-deployment, with parallel execution for speed optimization

## Requirements *(mandatory)*

### Testing Requirements (Project-Wide Policy)

**All features** implemented via spec-kit workflow MUST follow the **comprehensive test pyramid** approach with **90%+ coverage requirement**:

1. **Unit Tests**: Fast, isolated tests for business logic without external dependencies
   - Test individual functions, classes, and modules in isolation
   - Mock external services and database calls
   - **REQUIRED**: >90% code coverage for all business logic (enforced by CI/CD)
   - Execution time: <5 seconds total
   - Tools: pytest (backend), Jest (frontend)

2. **Integration Tests**: Tests verifying integration with real or mocked services
   - Test service integration layers (email service, database, job queue)
   - Use mocks/stubs for external APIs where appropriate
   - Verify data flow between components
   - **REQUIRED**: 100% coverage of all service integration points
   - Execution time: <30 seconds total
   - Tools: pytest with integration fixtures

3. **E2E Tests**: Full user workflow tests from UI to database
   - Test complete user journeys through actual UI using **Playwright**
   - Verify actual external service behavior (real email delivery via Mailtrap, etc.)
   - **REQUIRED**: 100% coverage of all critical user paths from acceptance scenarios
   - **REQUIRED**: All user stories must have at least one E2E test covering the primary scenario
   - Execution time: <5 minutes total
   - Tools: Playwright (browser automation)

**CI/CD Pipeline Gates**:
- Unit test coverage <90% → Build FAILS
- Missing integration tests for new services → Build FAILS
- Missing E2E test for user story acceptance scenario → Build FAILS
- Any test failure → Build FAILS (no exceptions)

**CI/CD Test Execution Policy** (Multi-Gate Approach):

1. **On Every Commit** (Developer Branch):
   - Run: Unit tests + Integration tests (parallel execution)
   - Skip: E2E tests (too slow for every commit)
   - Time target: <1 minute total
   - Fail: Block commit if unit/integration fails

2. **On PR Merge** (Pull Request to Main):
   - Run: Full test suite (unit + integration + E2E in parallel)
   - Time target: <5 minutes total
   - Fail: Block PR merge if any test fails
   - Required: 90%+ coverage check passes

3. **Pre-Deployment** (Before Production Release):
   - Run: Full test suite + smoke tests on staging environment
   - Time target: <10 minutes total
   - Fail: Block deployment if any test fails
   - Required: All E2E tests pass with real Mailtrap sandbox

**Parallel Execution Strategy**:
- Unit tests run in parallel across test files (pytest-xdist)
- Integration tests run in parallel by service (email, database, queue)
- E2E tests run in parallel by user story (Playwright workers)
- Target: 4-8 parallel workers depending on CI/CD resources

**Rationale**: This high-coverage approach ensures production-quality code:
- 90%+ unit coverage catches logic errors and edge cases during development
- Full integration coverage prevents service contract violations
- Mandatory E2E tests validate actual user experience with real external services
- High bar prevents technical debt accumulation and regression bugs
- Multi-gate approach balances speed (fast feedback on commits) with thoroughness (full validation before merge/deploy)

### Functional Requirements

- **FR-001**: System MUST send email notification within 2 minutes when volunteer is assigned to event
- **FR-002**: System MUST include event details in notification: date, time, duration, role, location, organization name
- **FR-003**: System MUST provide direct link to volunteer's schedule in all assignment emails
- **FR-004**: System MUST send automated reminder emails 24 hours before scheduled events
- **FR-005**: System MUST send update notifications when event time, location, or details change
- **FR-006**: System MUST send cancellation notifications when events are canceled
- **FR-007**: System MUST consolidate multiple notifications into single email when multiple assignments occur within 30-minute window
- **FR-008**: System MUST track notification delivery status (sent, delivered, failed, bounced)
- **FR-009**: System MUST retry failed notifications up to 3 times with exponential backoff (1 hour, 4 hours, 24 hours)
- **FR-010**: System MUST allow volunteers to set email preferences (immediate, daily digest, weekly digest, opt-out per type)
- **FR-011**: System MUST respect volunteer timezone preferences for displaying event times in emails
- **FR-012**: System MUST support translations for all notification text in 6 languages (EN, ES, PT, ZH-CN, ZH-TW, KO)
- **FR-013**: System MUST provide admin dashboard showing notification delivery statistics
- **FR-014**: System MUST send weekly summary emails to organization admins with engagement metrics
- **FR-015**: System MUST log all notification attempts for audit trail

### Non-Functional Requirements

- **NFR-001**: Email delivery must complete within 2 minutes of triggering event (95th percentile)
- **NFR-002**: System must support sending 1000+ emails per organization per day
- **NFR-003**: Email templates must render correctly in major email clients (Gmail, Outlook, Apple Mail, mobile clients)
- **NFR-004**: Notification system must handle email service outages gracefully with retry queue
- **NFR-005**: All email content must comply with CAN-SPAM Act (unsubscribe link, physical address, clear sender)
- **NFR-006**: System must rate-limit outbound emails to respect provider limits (max 100/minute default, configurable)

### Key Entities

- **Notification**: Represents a single email notification to be sent, includes type (assignment, reminder, update, cancellation), recipient, status, retry count, delivery timestamp
- **Notification Template**: Email template with placeholders for dynamic content, supports translations, versioned for A/B testing
- **Email Preference**: Volunteer's notification settings including frequency (immediate, daily, weekly), enabled types, preferred language, timezone
- **Delivery Log**: Audit trail of notification attempts including status, timestamps, error messages, email provider response codes
- **Notification Queue**: Job queue for batching and rate-limiting outbound emails, handles retries and prioritization

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of volunteers receive assignment notifications within 2 minutes of being assigned
- **SC-002**: Volunteer no-show rate decreases by 30% within 3 months of reminder implementation
- **SC-003**: 90% of notification emails are successfully delivered (not bounced or marked as spam)
- **SC-004**: Email open rate exceeds 60% for assignment notifications and 40% for reminders
- **SC-005**: Email click-through rate (schedule link) exceeds 70% for assignment notifications
- **SC-006**: Support tickets related to "didn't know I was scheduled" decrease by 80%
- **SC-007**: System processes 1000 notifications per hour without performance degradation
- **SC-008**: Volunteer satisfaction score for "communication clarity" improves from 3.2 to 4.5 (out of 5)
- **SC-009**: Administrators report saving 5+ hours per week previously spent on manual volunteer communication
- **SC-010**: Email delivery failure rate stays below 5% with automatic retry recovery

### User Experience Goals

- Volunteers feel informed and prepared for their scheduled events
- Email content is clear, concise, and actionable (requires single action: view schedule or add to calendar)
- Notification frequency feels appropriate (not overwhelming, not too sparse)
- Administrators have visibility into communication effectiveness and delivery issues

## Constraints *(if applicable)*

### Technical Constraints

- Must integrate with existing JWT authentication system for generating secure schedule links
- Must respect existing RBAC permissions (admins can configure org-wide settings, volunteers only their own preferences)
- Must maintain multi-tenant isolation (org A emails never reference org B data)
- Must work with current SQLite development database and future PostgreSQL production database

### Business Constraints

- Email service provider budget: Assume 10,000 emails/month free tier initially, paid tier at scale
- Must comply with CAN-SPAM Act and GDPR for international users
- Unsubscribe must be honored within 10 business days per regulation
- No personally identifiable information (PII) stored in email service provider logs

### Integration Constraints

- Must support multiple email service providers (SendGrid, Mailgun, AWS SES) via adapter pattern for future flexibility
- Must provide webhook endpoint for email provider delivery status callbacks
- Calendar integration: Must generate valid ICS attachments for "add to calendar" functionality

## Assumptions *(if applicable)*

1. **Email Service Provider**: Using Mailtrap for all environments - sandbox API (sandbox.api.mailtrap.io) for development/testing/CI, production Email API for real delivery (already configured with API token)
2. **Email Format**: Assume HTML emails with plain-text fallback for accessibility and older email clients
3. **Volunteer Email Verification**: Assume all volunteers have verified email addresses (from existing signup flow with confirmation link)
4. **Default Preferences**: Assume new volunteers default to "immediate notifications, all types enabled" until they customize preferences
5. **Timezone Handling**: Assume volunteer timezone is stored in their profile (existing `timezone` field in Person model)
6. **Translation**: Assume notification text follows same i18n pattern as UI (translation keys in 6 language files)
7. **Notification Prioritization**: Assume assignment/cancellation notifications are higher priority than reminders (sent immediately vs. can batch)
8. **Delivery SLA**: Assume 2-minute delivery target is achievable with async job queue (existing infra can be extended)
9. **Reminder Timing**: Assume 24-hour reminder is optimal based on industry research (can be made configurable in future iteration)
10. **Admin Permissions**: Assume organization admins can view notification logs for their org only (RBAC enforcement)

## Out of Scope *(if applicable)*

The following are explicitly **NOT** included in this initial implementation:

1. **SMS notifications**: Voice/text message notifications via Twilio (future feature, requires separate budget)
2. **Push notifications**: Mobile app push notifications (no mobile app exists yet)
3. **Slack/Teams integration**: Third-party messaging platform integrations (future feature)
4. **Custom email templates**: Admin-configurable email template editor (use pre-designed templates only)
5. **A/B testing dashboard**: Email content experiments and analytics (future feature)
6. **Advanced segmentation**: Target specific volunteer groups with custom messaging (future feature)
7. **Two-way email**: Volunteers cannot reply to notifications to accept/decline assignments (future feature)
8. **Calendar sync**: Automatic sync to Google Calendar/Outlook (ICS export only in this phase)
9. **Attachment support**: Volunteers cannot receive PDF schedules or additional documents via email
10. **White-labeling**: Custom sender domain and branding for enterprise tier (use system default sender)

## Dependencies *(if applicable)*

### External Dependencies

1. **Email Service Provider Account**: SendGrid account with API key (free tier sufficient for pilot)
2. **Email Domain Verification**: DNS records configured to verify sender domain (SPF, DKIM, DMARC)
3. **Unsubscribe Page Hosting**: Public-facing unsubscribe preference page (can use existing web server)

### Internal Dependencies

1. **Async Job Queue**: Background job processing system for sending emails (use existing infrastructure or add Celery/RQ)
2. **i18n Translation Files**: Notification text translations in all 6 supported languages
3. **Existing Authentication**: JWT token generation for secure schedule links (already implemented)
4. **RBAC System**: Permission checks for admin notification settings (already implemented)
5. **Database Schema**: New tables for notifications, delivery logs, email preferences (migration required)

### Blocking Dependencies

- None identified - all dependencies are achievable within project scope

## Risks *(if applicable)*

### High Risk

1. **Email Deliverability**: Risk that emails land in spam folders, reducing effectiveness
   - *Mitigation*: Implement SPF/DKIM/DMARC, start with low volume, monitor spam reports, use reputable provider

2. **Email Provider Outage**: Risk that SendGrid downtime prevents notification delivery
   - *Mitigation*: Implement retry queue, consider multi-provider fallback in future, monitor provider status page

### Medium Risk

3. **Email Fatigue**: Risk that volunteers opt-out due to notification overload
   - *Mitigation*: Smart batching (consolidate within 30 min window), default to digest mode for low-priority notifications, easy preference management

4. **Rate Limiting**: Risk of hitting email provider rate limits during bulk operations
   - *Mitigation*: Implement queue-based sending with configurable rate limit, prioritize critical notifications

### Low Risk

5. **Translation Quality**: Risk that machine-translated notification text is unclear or incorrect
   - *Mitigation*: Use professional translation for critical templates, allow volunteers to report translation issues

6. **Timezone Confusion**: Risk that event times display incorrectly in different timezones
   - *Mitigation*: Use volunteer's stored timezone, include timezone abbreviation in email, test with international volunteers

## Open Questions *(if any)*

**Reminder Timing Configurability** - RESOLVED

**Decision**: Start with fixed 24-hour reminder for all organizations (Option A)

**Rationale**:
- Follows MVP principles: start simple, iterate based on user feedback
- 24 hours is industry standard based on behavioral research (optimal balance between too early and too late)
- Reduces implementation complexity - no admin UI or per-org configuration needed
- Faster time to market - can launch feature sooner and validate with real users
- Easy to add configurability in future iteration once we have usage data showing what timing preferences users actually want
- Avoids premature optimization - we don't yet know if organizations need different timings

**Future Iteration**: After gathering 3 months of usage data, evaluate whether to add organization-level or volunteer-level configurability based on user feedback and support requests.
