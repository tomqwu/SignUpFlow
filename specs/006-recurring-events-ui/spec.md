# Feature Specification: Recurring Events User Interface

**Feature Branch**: `006-recurring-events-ui`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Recurring events user interface for creating and managing repeating event patterns. Users can define weekly, biweekly, monthly, and custom recurring schedules with end dates or occurrence counts. Must support editing single occurrences versus entire series, handling exceptions for holidays or special dates, visual calendar preview showing generated occurrences, bulk editing capabilities for recurring series, and integration with existing event management and scheduling solver. Interface should make complex recurrence patterns intuitive through calendar-based selection and natural language descriptions."

## User Scenarios & Testing

### User Story 1 - Create Weekly Recurring Events (Priority: P1)

Admin users create weekly recurring events (Sunday services, weekly meetings) by selecting recurrence pattern, specifying which days of week, and setting end date or occurrence count. System generates all event occurrences automatically.

**Why this priority**: Most volunteer scheduling involves weekly recurring patterns (weekly services, regular meetings). This is core functionality that delivers immediate value and reduces repetitive event creation from dozens of individual events to single recurring template.

**Independent Test**: Can be fully tested by creating a recurring event with "Every Sunday" pattern, viewing generated occurrences in calendar, and verifying all Sundays through end date have events created. Delivers immediate value by automating weekly event creation.

**Acceptance Scenarios**:

1. **Given** admin creating new event, **When** admin selects "Repeat weekly every Sunday" and sets end date 3 months away, **Then** system generates 12-13 Sunday events spanning that date range
2. **Given** recurring pattern configured, **When** admin changes end date from 3 months to 6 months, **Then** system regenerates series with additional Sunday occurrences
3. **Given** weekly recurring event created, **When** admin views calendar, **Then** calendar displays all generated occurrences with visual indicator showing they belong to recurring series
4. **Given** recurring series exists, **When** admin edits series title, **Then** title updates for all future occurrences (past occurrences retain original title to preserve historical data)
5. **Given** recurring event template, **When** scheduling solver runs, **Then** solver assigns volunteers to all occurrences in recurring series treating each as independent event

---

### User Story 2 - Edit Single Occurrence vs Entire Series (Priority: P1)

Admin users choose whether changes apply to single occurrence or entire recurring series. Single-occurrence edits create exceptions while series edits update all future occurrences.

**Why this priority**: Essential for handling real-world scenarios: cancel one occurrence for holiday, reschedule single meeting, but leave rest of series intact. Without this, admins forced to recreate entire series whenever one event needs modification.

**Independent Test**: Can be fully tested by editing one occurrence of recurring series (changing time or canceling), verifying that occurrence differs from series while other occurrences remain unchanged. Delivers immediate value by allowing flexible exception handling.

**Acceptance Scenarios**:

1. **Given** recurring series with 10 occurrences, **When** admin clicks "Edit" on 5th occurrence, **Then** system displays dialog "Edit this occurrence only" or "Edit entire series"
2. **Given** admin selects "Edit this occurrence only", **When** admin changes time from 10am to 2pm, **Then** only that occurrence shows 2pm time while all other occurrences remain 10am
3. **Given** admin selects "Edit entire series", **When** admin changes time from 10am to 11am, **Then** all future occurrences (including current) update to 11am, past occurrences remain unchanged
4. **Given** single occurrence edited, **When** admin views occurrence details, **Then** interface displays "Exception to recurring series: [Series Name]" with option to remove exception
5. **Given** occurrence canceled (marked as exception), **When** scheduling solver runs, **Then** solver skips canceled occurrence but assigns volunteers to other series occurrences

---

### User Story 3 - Visual Calendar Preview (Priority: P1)

Users view visual calendar preview showing all generated occurrences before saving recurring event. Preview highlights date range, occurrence count, and allows scrolling through months to verify pattern correctness.

**Why this priority**: Complex recurrence patterns (every 2nd and 4th Sunday, monthly on 15th, biweekly) are error-prone. Visual confirmation prevents mistakes like creating 365 occurrences by accident or setting wrong days. Essential for user confidence before committing.

**Independent Test**: Can be fully tested by configuring complex pattern (e.g., "Every 2 weeks on Tuesday and Thursday"), viewing calendar preview showing highlighted dates, and verifying highlighted dates match expected pattern. Delivers immediate value by preventing recurrence pattern errors.

**Acceptance Scenarios**:

1. **Given** admin configuring recurring event, **When** admin selects recurrence pattern, **Then** calendar preview displays highlighted dates showing where events will be created
2. **Given** calendar preview displayed, **When** admin scrolls forward 3 months, **Then** calendar continues showing future occurrences following pattern
3. **Given** pattern generates 50+ occurrences, **When** calendar preview loads, **Then** preview displays warning "This pattern creates [X] events" with option to adjust end date
4. **Given** admin changes pattern from weekly to biweekly, **When** pattern updates, **Then** calendar preview immediately refreshes showing new occurrence dates
5. **Given** calendar preview showing occurrences, **When** admin hovers over highlighted date, **Then** tooltip displays "Event occurrence [N] of [Total]: [Event Title]"

---

### User Story 4 - Monthly Recurrence Patterns (Priority: P2)

Admin users create monthly recurring events with flexible patterns: specific date (15th of every month), specific weekday (2nd Sunday of every month, last Friday of every month). System handles months with varying days correctly.

**Why this priority**: Many organizations have monthly recurring needs (monthly board meetings on 2nd Tuesday, monthly volunteer appreciation on last Sunday). Flexible monthly patterns accommodate real-world scheduling complexity.

**Independent Test**: Can be fully tested by creating "2nd Sunday of every month" pattern, verifying system generates correct dates (accounting for months where 2nd Sunday falls on different calendar dates), and confirming pattern continues correctly for 12 months. Delivers immediate value by automating monthly event scheduling.

**Acceptance Scenarios**:

1. **Given** admin creating monthly recurring event, **When** admin selects "2nd Sunday of every month", **Then** system generates occurrences on 2nd Sunday of each month for specified duration
2. **Given** pattern set to "15th of every month", **When** system generates February occurrences, **Then** February occurrence falls on February 15th (not skipped for short month)
3. **Given** pattern set to "Last Friday of every month", **When** system generates occurrences, **Then** each occurrence correctly identifies last Friday regardless of whether month has 28, 29, 30, or 31 days
4. **Given** monthly pattern spanning 12 months, **When** admin views year calendar, **Then** calendar displays all 12 monthly occurrences in correct positions
5. **Given** monthly recurring event created, **When** admin edits single occurrence, **Then** system allows exception handling without disrupting other monthly occurrences

---

### User Story 5 - Biweekly and Custom Intervals (Priority: P2)

Admin users create biweekly (every 2 weeks) and custom interval recurring events (every 3 weeks, every 4 days). System maintains correct interval timing even when occurrences edited or exceptions created.

**Why this priority**: Many volunteer rotations use biweekly patterns (alternating week schedules, every-other-week assignments). Custom intervals support specialized scheduling needs without requiring manual event creation.

**Independent Test**: Can be fully tested by creating "Every 2 weeks on Wednesday" pattern, verifying system generates occurrences exactly 14 days apart, and confirming pattern maintains correct interval after creating exception. Delivers immediate value by supporting alternating-week scheduling.

**Acceptance Scenarios**:

1. **Given** admin selecting recurrence pattern, **When** admin chooses "Repeat every 2 weeks", **Then** system generates occurrences exactly 14 days apart
2. **Given** biweekly pattern configured, **When** admin sets start date as January 1st (Wednesday), **Then** occurrences appear on Jan 1, Jan 15, Jan 29, Feb 12, etc. (every 14 days)
3. **Given** custom interval "every 3 weeks" selected, **When** system generates occurrences, **Then** occurrences appear exactly 21 days apart
4. **Given** biweekly series with exception (one occurrence canceled), **When** admin views series, **Then** subsequent occurrences maintain correct biweekly interval from original start date (not shifted by exception)
5. **Given** custom interval pattern created, **When** calendar preview displays, **Then** preview shows occurrence count and confirms interval spacing visually

---

### User Story 6 - Bulk Editing Recurring Series (Priority: P2)

Admin users bulk edit recurring series properties (title, role requirements, duration, location) applying changes to all future occurrences simultaneously. Changes to series template automatically update all non-exception occurrences.

**Why this priority**: Updating 50+ individual occurrences manually is time-prohibitive and error-prone. Bulk editing makes recurring events truly manageable and practical for long-term scheduling. Essential for maintaining recurring series over time as organizational needs change.

**Independent Test**: Can be fully tested by bulk editing recurring series title and role requirements, verifying all future occurrences update instantly, and confirming exceptions retain their custom properties. Delivers immediate value by enabling efficient series-wide updates.

**Acceptance Scenarios**:

1. **Given** recurring series with 40 occurrences, **When** admin edits series title from "Sunday Service" to "Worship Service", **Then** all future occurrences (including today's) update title, past occurrences unchanged
2. **Given** series role requirements changing, **When** admin updates series to require 3 greeters instead of 2, **Then** all future occurrences reflect new requirement of 3 greeters
3. **Given** series with 5 exceptions (customized occurrences), **When** admin bulk edits series duration, **Then** non-exception occurrences update duration, exception occurrences retain custom duration
4. **Given** admin editing series properties, **When** changes saved, **Then** system displays confirmation "Updated [N] future occurrences, [M] exceptions unchanged"
5. **Given** bulk edit in progress, **When** scheduling solver has existing assignments for future occurrences, **Then** system warns "Changes may affect existing volunteer assignments, continue?"

---

### User Story 7 - Holiday Exception Handling (Priority: P3)

Admin users mark specific dates as holidays (Christmas, New Year's, organization-specific holidays), automatically excluding those dates from recurring series generation or creating flagged occurrences requiring manual review.

**Why this priority**: Prevents accidentally scheduling events on holidays. While admins can manually cancel occurrences, automatic holiday handling reduces administrative burden and prevents oversight errors. Quality-of-life improvement rather than core functionality.

**Independent Test**: Can be fully tested by creating holiday calendar with Christmas and New Year's, generating weekly recurring series spanning those dates, and verifying system either skips holiday dates or flags them for review. Delivers immediate value by reducing holiday scheduling errors.

**Acceptance Scenarios**:

1. **Given** organization holiday calendar configured with Christmas, **When** admin creates weekly recurring series spanning December 25, **Then** system skips December 25 or flags occurrence with "Holiday: Review Required"
2. **Given** recurring series already generated, **When** admin adds new holiday to calendar, **Then** system identifies affected occurrences and marks them as "Requires Review"
3. **Given** occurrence falls on holiday, **When** admin views occurrence details, **Then** interface displays holiday name and provides options: "Cancel this occurrence", "Keep as scheduled", "Reschedule to different date"
4. **Given** holiday exception handling configured, **When** calendar preview generates, **Then** preview highlights holiday conflicts in different color with warning indicator
5. **Given** multiple occurrences on holidays, **When** admin reviews series, **Then** system provides bulk action "Handle all holiday conflicts" allowing batch decisions

---

### Edge Cases

- **What happens when recurring series spans daylight saving time changes?** System stores event times in organization timezone with automatic DST adjustment. When occurrence crosses DST boundary (e.g., 10am time continues as 10am in new DST period), system maintains consistent local time. For edge cases like 2:30am during "spring forward" (non-existent time), system shifts forward by 1 hour automatically.

- **How does system handle "5th Sunday of the month" pattern when month only has 4 Sundays?** System skips that month's occurrence. Calendar preview clearly indicates months without 5th Sunday will have no event. Alternative option offered: "Last Sunday of month if 5th Sunday doesn't exist" allowing fallback behavior.

- **What happens when admin deletes recurring series template?** System displays confirmation dialog: "Delete all future occurrences?" with options: (1) Delete all future occurrences (recommended), (2) Convert occurrences to individual events (removes recurrence relationship), (3) Cancel. Past occurrences always preserved for historical record.

- **How does system handle editing occurrence that falls before today's date?** System prevents editing past occurrences (historical data preservation). Edit dialog displays "This occurrence is in the past and cannot be modified. Edit future occurrences only?" directing admin to series template for future changes.

- **What happens when recurring pattern creates conflicting events (multiple occurrences on same date)?** System detects overlap during generation and displays warning "Pattern creates overlapping events on [dates]" with options to adjust pattern or proceed with overlaps. Scheduling solver treats overlapping events as separate requiring distinct volunteer assignments.

- **How does system handle very long recurring series (2+ years, 100+ occurrences)?** System displays performance warning when series exceeds 100 occurrences: "Large series may impact performance. Consider shorter duration or review periodically." Generation happens in background with progress indicator. Option to archive old occurrences after 6 months keeping template active.

- **What happens when exception occurrence edited to match series pattern again?** System offers to "Remove exception and revert to series pattern" or "Keep as exception with same properties." Removing exception re-links occurrence to series template allowing future bulk edits to affect it.

- **How does system handle time zone changes for recurring events?** All occurrences created in series inherit organization timezone at creation time. If organization timezone changes later, existing occurrences remain in original timezone (prevents historical data corruption). New occurrences generated after timezone change use new timezone. Warning displayed when timezone mismatch detected.

## Requirements

### Functional Requirements

#### Recurrence Pattern Creation

- **FR-001**: System MUST support weekly recurrence patterns allowing selection of specific days (Sunday, Monday, etc.) with option for multiple days per week
- **FR-002**: System MUST support biweekly recurrence patterns generating occurrences every 14 days from start date
- **FR-003**: System MUST support monthly recurrence patterns with options: specific date (15th), specific weekday (2nd Sunday), last weekday (last Friday)
- **FR-004**: System MUST support custom intervals (every N days, every N weeks) where N is user-configurable integer 1-52
- **FR-005**: System MUST allow end condition specification: end date, number of occurrences, or indefinite (max 2 years)
- **FR-006**: System MUST validate recurrence patterns before generation preventing invalid patterns (e.g., February 30th) with user-friendly error messages

#### Visual Calendar Preview

- **FR-007**: System MUST display visual calendar preview showing all generated occurrence dates before saving recurring event
- **FR-008**: Calendar preview MUST allow navigation forward/backward through months to inspect full date range
- **FR-009**: Preview MUST display occurrence count total and date range summary (e.g., "Creates 52 events from Jan 1, 2025 to Dec 31, 2025")
- **FR-010**: Preview MUST highlight dates where occurrences will be created using distinct visual indicator (color, icon, border)
- **FR-011**: Preview MUST update in real-time as user modifies recurrence pattern (frequency, days, end date) with <1 second refresh
- **FR-012**: Preview MUST display warnings when pattern creates 50+ occurrences or spans 1+ year prompting user review

#### Single Occurrence vs Series Editing

- **FR-013**: System MUST prompt user when editing occurrence: "Edit this occurrence only" or "Edit entire series"
- **FR-014**: Editing single occurrence MUST create exception preserving original series template for other occurrences
- **FR-015**: Editing entire series MUST update series template affecting all future occurrences (including current), leaving past occurrences unchanged
- **FR-016**: Exception occurrences MUST display visual indicator showing they differ from series template with option to view/remove exception
- **FR-017**: System MUST allow converting exception back to series pattern removing custom properties and re-linking to template
- **FR-018**: Canceled/deleted occurrences MUST remain as exceptions (invisible/archived) preventing regeneration if series end date extended

#### Bulk Series Management

- **FR-019**: System MUST allow bulk editing series template properties (title, time, duration, role requirements, location) applying changes to all future non-exception occurrences
- **FR-020**: Bulk edits MUST preserve exception occurrence customizations keeping their unique properties intact
- **FR-021**: System MUST display confirmation summary before applying bulk edits: "[N] occurrences will be updated, [M] exceptions unchanged"
- **FR-022**: System MUST warn when bulk edits affect occurrences with existing volunteer assignments prompting admin review
- **FR-023**: System MUST support bulk deletion of series with options: delete all future, convert to individual events, or cancel

#### Series and Occurrence Visualization

- **FR-024**: Calendar views MUST display recurring event occurrences with visual indicator (icon, badge) showing series membership
- **FR-025**: Occurrence detail view MUST display series information: template name, pattern description (e.g., "Every Sunday"), link to series template
- **FR-026**: System MUST provide series management view listing all recurring series with pattern descriptions and occurrence counts
- **FR-027**: Series list MUST support filtering (active vs archived), sorting (by date, occurrence count), and search by event title
- **FR-028**: System MUST display natural language description of recurrence pattern (e.g., "Repeats weekly on Sunday and Wednesday until Dec 31, 2025")

#### Integration with Scheduling System

- **FR-029**: Scheduling solver MUST treat recurring event occurrences as independent events for volunteer assignment
- **FR-030**: System MUST allow running scheduling solver on entire recurring series simultaneously or per-occurrence basis
- **FR-031**: Volunteer assignments MUST persist separately for each occurrence allowing different volunteer assignments across series
- **FR-032**: System MUST support filtering events by recurring series when viewing schedules and assignments
- **FR-033**: Canceling/deleting occurrence MUST remove volunteer assignments for that occurrence only, preserving assignments for other series occurrences

#### Holiday and Exception Management

- **FR-034**: System MUST support organization holiday calendar configuration with holiday names and dates
- **FR-035**: When generating recurring series, system MUST detect occurrences falling on holidays and flag them for review or skip automatically based on configuration
- **FR-036**: Holiday-conflicting occurrences MUST display warning indicator with holiday name and options: cancel, keep, or reschedule
- **FR-037**: System MUST provide bulk holiday conflict resolution allowing admin to handle multiple holiday conflicts simultaneously
- **FR-038**: Manual exceptions (user-created) MUST be distinguished from automatic exceptions (holiday conflicts, DST adjustments) in interface

### Key Entities

- **RecurringSeries**: Series template defining recurrence pattern. Attributes: series ID, event template (title, duration, role requirements, location), recurrence pattern (frequency, interval, days of week/month), start date, end condition (end date or occurrence count), organization ID, created by user ID, active status.

- **RecurrencePattern**: Pattern definition for series generation. Attributes: pattern type (weekly, biweekly, monthly, custom), frequency interval (every N days/weeks), selected days (for weekly patterns), weekday position (2nd Sunday, last Friday for monthly), end condition type (date, occurrence count, indefinite), maximum duration (2 years).

- **EventOccurrence**: Individual event generated from recurring series. Attributes: occurrence ID, series ID (null for non-recurring), occurrence sequence number (1st, 2nd, 3rd in series), event data (title, datetime, duration, role requirements, location), exception status (normal or exception), exception type (manual edit, holiday conflict, canceled), link to series template.

- **RecurrenceException**: Customization applied to single occurrence. Attributes: occurrence ID, series ID, exception type (edited, canceled, holiday conflict), original values (from template), customized values (user changes), created timestamp, created by user ID, removable (can revert to series pattern).

- **HolidayCalendar**: Organization holiday configuration. Attributes: organization ID, holiday name, holiday date, recurring annually (yes/no), conflict handling policy (skip occurrence, flag for review, auto-reschedule), active status.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admin users create recurring weekly events in under 2 minutes including pattern configuration and calendar preview review, reducing time vs creating individual events by 90%
- **SC-002**: Visual calendar preview prevents 95% of recurrence pattern errors (wrong days, excessive occurrences) before series creation
- **SC-003**: Single occurrence vs entire series editing reduces administrative burden by 80% for handling exceptions (holidays, special dates, rescheduling)
- **SC-004**: Bulk editing recurring series properties (title, time, requirements) completes in under 10 seconds for series with 100+ occurrences
- **SC-005**: System correctly generates monthly recurrence patterns (2nd Sunday, last Friday, 15th of month) with 100% accuracy across all month lengths and leap years
- **SC-006**: Holiday conflict detection identifies 100% of occurrences falling on configured holidays before admin saves series
- **SC-007**: Recurring events feature reduces manual event creation workload by 75% for organizations with weekly/monthly recurring patterns
- **SC-008**: User satisfaction: 85% of admins report recurring events interface is "intuitive" or "easy to use" in post-deployment survey
- **SC-009**: Exception handling (edit single occurrence) maintains correct series integrity: 0% of cases where exception affects other series occurrences
- **SC-010**: System supports recurring series spanning 2+ years with 100+ occurrences without performance degradation (calendar loads <3 seconds)

## Assumptions

1. **Maximum Series Duration**: We assume 2-year maximum for recurring series is sufficient. Rationale: Most organizations review/renew volunteer schedules annually. Longer series risk becoming stale. Admins can extend series as end date approaches.

2. **Timezone Consistency**: We assume all events within single organization use same timezone (organization's configured timezone). Rationale: SignUpFlow targets single-location organizations (churches, local leagues). Multi-timezone support adds significant complexity for minimal benefit.

3. **Historical Data Preservation**: We assume past occurrences cannot be edited/deleted to preserve historical volunteer assignment records. Rationale: Organizations need accurate records of past assignments for compliance/reporting. Only future occurrences editable.

4. **Natural Language Description**: We assume natural language pattern descriptions (e.g., "Every Sunday") are generated by system, not user-editable. Rationale: Reduces user error. System generates accurate descriptions from structured pattern data.

5. **Single Series per Event**: We assume each event belongs to maximum one recurring series (no overlapping/nested series). Rationale: Simplifies data model and prevents complex conflict scenarios. Admins can create multiple separate series if needed.

6. **Exception Limit**: We assume maximum 30% of series occurrences can be exceptions before system recommends creating separate series. Rationale: If most occurrences are exceptions, series pattern isn't meaningful. Better to use individual events or multiple series.

7. **Generation Performance**: We assume recurring series generation (creating all occurrences) happens synchronously during save operation for series <100 occurrences, background generation for larger series. Rationale: Balances user experience (immediate feedback) with performance.

8. **DST Handling**: We assume system automatically adjusts for daylight saving time maintaining consistent local time (10am stays 10am) rather than UTC time. Rationale: Users think in local time. Maintaining "10am Sunday service" consistent across DST changes matches user expectations.

9. **Holiday Calendar Scope**: We assume single shared holiday calendar per organization (not per-event holiday handling). Rationale: Most organizations have consistent holiday schedule. Simplifies administration and prevents configuration fragmentation.

10. **Indefinite Series Limit**: We assume "indefinite" recurring series actually limited to 2 years from creation requiring manual extension. Rationale: Prevents runaway generation. Forces periodic review ensuring series still relevant.

## Dependencies

1. **Existing Event Management**: Feature extends existing event creation/editing functionality. Dependency: Current event management system must support all event properties that recurring events will inherit (title, duration, role requirements, location).

2. **Scheduling Solver Integration**: Recurring occurrences must integrate with existing constraint-based scheduling solver. Dependency: Solver must treat each occurrence as independent event while maintaining relationship metadata for bulk operations.

3. **Calendar Display Components**: Visual calendar preview requires calendar rendering component. Dependency: May need frontend calendar library (FullCalendar, React Big Calendar, or custom component) supporting month view, date highlighting, and navigation.

4. **Organization Timezone Configuration**: Recurring events use organization timezone for all occurrence generation. Dependency: Organization settings must include timezone configuration (already exists in SignUpFlow).

5. **Date/Time Utilities**: Complex recurrence pattern generation (2nd Sunday, last Friday, biweekly intervals) requires robust date manipulation utilities. Dependency: Backend date/time library supporting timezone-aware calculations, DST handling, and recurrence rules.

## Out of Scope

1. **iCalendar RFC 5545 Compliance**: Full RFC 5545 (iCalendar recurrence rule) support excluded. Feature implements common patterns only (weekly, biweekly, monthly). Complex rules like "every 3rd Tuesday and Thursday of odd-numbered months" excluded. Can add advanced patterns based on user demand.

2. **Recurring Event Templates Library**: Pre-built recurring event templates ("Sunday Service Schedule", "Monthly Board Meeting") excluded from initial scope. Feature provides pattern creation tools but no template library. Templates can be added based on usage patterns.

3. **Multi-Timezone Recurring Events**: Events spanning multiple timezones excluded. Feature assumes all occurrences use organization's single timezone. Multi-timezone support requires complex handling of DST differences and adds minimal value for target users.

4. **Recurring Event Analytics**: Analytics on recurring series usage (most common patterns, series completion rates, exception frequency) excluded from initial scope. Feature focuses on creation/management. Analytics can be added as separate feature.

5. **Recurring Event Import/Export**: Importing recurring events from external calendars (Google Calendar, Outlook) or exporting recurring series as iCalendar files excluded. Feature focuses on native creation. Import/export can be added for migration/integration use cases.

6. **Conditional Recurrence Rules**: Complex conditional rules ("repeat unless holiday", "skip if previous occurrence canceled", "repeat only if volunteer count >5") excluded. Feature supports manual exception handling only. Automated conditional logic adds significant complexity.

7. **Recurring Volunteer Assignments**: Automatically assigning same volunteers to all occurrences in series excluded. Each occurrence requires separate volunteer assignment through scheduling solver. Recurring assignments create complications with availability/time-off that manual assignment avoids.

8. **Occurrence Reordering**: Manually reordering occurrences within series (moving 3rd occurrence to 5th position) excluded. Occurrences follow strict chronological pattern from recurrence rules. Manual reordering destroys pattern integrity and confuses users.

9. **Nested Recurring Series**: Recurring series within recurring series (e.g., "Every Sunday in January and July") excluded. Feature supports single-level recurrence only. Nested patterns can be created as separate series.

10. **Recurring Availability**: Recurring time-off patterns for volunteers (e.g., "Every 3rd weekend unavailable") excluded from this feature. Feature focuses on event recurrence only. Recurring availability handled separately in volunteer availability management.
