# Feature Specification: Recurring Events User Interface

**Feature Branch**: `016-recurring-events-ui`
**Created**: 2025-10-22
**Status**: Draft
**Type**: User Experience Enhancement (High Value)

---

## Overview

**Purpose**: Enable administrators to efficiently create and manage repeating event patterns through an intuitive user interface that simplifies complex recurrence scheduling while maintaining full control over individual occurrences and exceptions.

**Business Value**: Reduces administrative time spent creating repetitive events by 80% (creating 52 weekly events manually takes ~45 minutes, with recurring patterns takes ~5 minutes), prevents scheduling errors in regular event series, and provides flexibility to handle real-world exceptions like holidays without recreating entire schedules.

**Target Users**: Organization administrators (pastors, coordinators, event managers) who manage regular recurring events like weekly services, monthly meetings, or seasonal programs.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Basic Recurring Event Pattern (Priority: P1)

Administrator creates a recurring event using common patterns (weekly, biweekly, monthly) with a visual calendar preview showing exactly when events will occur, eliminating the need to manually create dozens of individual events and reducing scheduling errors.

**Why this priority**: P1 - This is the core value proposition of the feature. Without basic recurrence creation, the feature provides no value. This alone reduces event creation time by 80% for regular schedules.

**Independent Test**: Create a weekly Sunday service recurring every week for 3 months. Verify calendar preview shows 12-13 Sunday occurrences. Verify all occurrences appear in event list after creation.

**Acceptance Scenarios**:

1. **Given** administrator is creating a new event, **When** they select "Make this recurring" option, **Then** recurrence pattern selector appears with weekly/biweekly/monthly options
2. **Given** administrator selects "Weekly" pattern, **When** they choose Sunday and set end date 3 months from now, **Then** calendar preview displays all 12-13 Sunday occurrences with event details
3. **Given** administrator has configured recurring pattern with preview, **When** they click "Create Recurring Events", **Then** all occurrences are created and visible in main event calendar within 3 seconds
4. **Given** recurring pattern end condition, **When** administrator chooses "After X occurrences" instead of end date, **Then** system generates exactly X event occurrences and stops
5. **Given** administrator creates monthly event on 31st, **When** month has fewer than 31 days, **Then** event is created on last day of that month (reasonable default behavior)

---

### User Story 2 - Visual Calendar Preview of Generated Occurrences (Priority: P1)

Administrator sees a visual calendar preview showing all future occurrences of the recurring pattern before committing, allowing them to verify the schedule matches their intentions and catch errors (wrong day of week, incorrect frequency) before creating dozens of events.

**Why this priority**: P1 - Critical for preventing mass scheduling errors. Without preview, users might create 52 incorrect events and need to delete them all. Preview provides confidence and catch errors early.

**Independent Test**: Set up a biweekly Wednesday event and verify calendar preview shows occurrences only on Wednesdays with 2-week gaps. Change to weekly and verify preview updates to show consecutive Wednesdays.

**Acceptance Scenarios**:

1. **Given** administrator is configuring recurrence pattern, **When** they change any pattern setting (frequency, day of week, interval), **Then** calendar preview updates within 1 second showing new occurrence dates
2. **Given** calendar preview is displaying occurrences, **When** administrator scrolls through months, **Then** preview highlights recurring event dates distinctly from existing one-time events
3. **Given** recurring pattern generates 50+ occurrences, **When** preview displays, **Then** system shows first 12 weeks with indicator "...and 38 more occurrences" to prevent performance issues
4. **Given** administrator hovers over occurrence in preview, **When** mouse hovers, **Then** tooltip shows event details (title, time, role requirements)
5. **Given** preview shows pattern conflicts with existing events (same time/volunteers), **When** preview loads, **Then** conflicting dates are visually marked with warning indicator

---

### User Story 3 - Edit Single Occurrence vs Entire Series (Priority: P2)

Administrator modifies a single event occurrence (e.g., changing time for holiday service) or the entire recurring series (e.g., moving all events to different day of week) with clear interface distinguishing between these operations to prevent accidental mass changes.

**Why this priority**: P2 - Important for handling real-world schedule adjustments, but core creation (P1) must exist first. Enables flexibility without recreating entire series.

**Independent Test**: Create weekly event series, edit one occurrence to different time, verify only that occurrence changes. Then edit series to different day, verify all future occurrences move to new day.

**Acceptance Scenarios**:

1. **Given** administrator clicks edit on recurring event occurrence, **When** edit dialog opens, **Then** prominent choice presented: "Edit only this occurrence" vs "Edit entire series" vs "Edit this and future occurrences"
2. **Given** administrator selects "Edit only this occurrence", **When** they change event time and save, **Then** only that single occurrence reflects the change, all other occurrences remain unchanged
3. **Given** administrator selects "Edit entire series", **When** they change event title and save, **Then** all occurrences (past and future) update with new title within 3 seconds
4. **Given** administrator selects "Edit this and future occurrences", **When** they change role requirements, **Then** selected occurrence and all subsequent occurrences update, previous occurrences remain unchanged
5. **Given** single occurrence was edited individually, **When** administrator later edits entire series, **Then** system prompts "2 occurrences have individual edits - overwrite them?" with option to preserve individual edits

---

### User Story 4 - Exception Handling for Holidays and Special Dates (Priority: P2)

Administrator marks specific dates as exceptions to skip recurring events (e.g., no service on Christmas Day) or modify them (e.g., combined Thanksgiving service at different time) without deleting and recreating the series.

**Why this priority**: P2 - Essential for real-world schedule management where holidays and special dates require exceptions. Without this, users must manually delete/modify dozens of individual occurrences.

**Independent Test**: Create weekly Sunday service series, add Christmas Day as exception to skip, verify that occurrence doesn't appear in calendar. Add Thanksgiving as modified occurrence with different time, verify time change.

**Acceptance Scenarios**:

1. **Given** administrator is viewing recurring series, **When** they access exception management, **Then** interface displays list of current exceptions and button "Add Exception"
2. **Given** administrator clicks "Add Exception", **When** they select date and choose "Skip this occurrence", **Then** event on that date is removed from calendar and marked as skipped exception
3. **Given** administrator adds exception to modify occurrence, **When** they change time/title/details for that date, **Then** modified occurrence appears with distinct visual indicator "Modified from series pattern"
4. **Given** multiple exceptions exist, **When** administrator views series summary, **Then** exception count displayed "Weekly series with 3 exceptions" with link to view exception details
5. **Given** administrator creates recurring series, **When** they select dates from exception library (common holidays: Christmas, Easter, Thanksgiving), **Then** system auto-applies skip exceptions for selected holidays

---

### User Story 5 - Bulk Editing for Recurring Series (Priority: P2)

Administrator applies changes to multiple occurrences simultaneously (e.g., updating volunteer requirements for all remaining events this year) through selection interface rather than editing each occurrence individually.

**Why this priority**: P2 - Improves efficiency for mid-series adjustments, but not critical for initial creation. Particularly valuable for large organizations making seasonal changes.

**Independent Test**: Create 52-week event series, select occurrences for Q2 (weeks 14-26), bulk update role requirements to add extra volunteer, verify only selected occurrences updated.

**Acceptance Scenarios**:

1. **Given** administrator views recurring series occurrence list, **When** they enable selection mode, **Then** checkboxes appear next to each occurrence with "Select All", "Select Range", "Select by Date Range" options
2. **Given** administrator has selected 10 occurrences, **When** they click "Bulk Edit", **Then** edit dialog opens showing which fields can be bulk-edited (title, role requirements, notes) and which cannot (date, time for consistency)
3. **Given** administrator bulk edits selected occurrences, **When** they change role requirements and save, **Then** all selected occurrences update and change log records "Bulk edit applied to 10 occurrences"
4. **Given** bulk edit is in progress, **When** administrator cancels before saving, **Then** no changes are applied to any occurrence (atomic operation)
5. **Given** bulk edit affects future assignments, **When** changes would create scheduling conflicts, **Then** system displays conflict warning with affected volunteer names before applying changes

---

### User Story 6 - Natural Language Recurrence Descriptions (Priority: P3)

System displays human-readable summaries of recurrence patterns (e.g., "Every 2 weeks on Wednesday, ending after 20 occurrences") helping administrators quickly understand complex patterns without decoding technical recurrence rules.

**Why this priority**: P3 - Improves user experience and reduces confusion, but not essential for functionality. Core pattern creation (P1) works without natural language descriptions.

**Independent Test**: Create complex pattern (every 2 weeks on Monday and Wednesday), verify summary reads "Every 2 weeks on Monday and Wednesday, ending December 31, 2025". Verify summary updates when pattern changes.

**Acceptance Scenarios**:

1. **Given** administrator creates recurrence pattern, **When** pattern is configured, **Then** natural language summary displays below pattern controls (e.g., "Weekly on Sunday, ending after 52 occurrences")
2. **Given** pattern has exceptions, **When** summary is displayed, **Then** exception count included in summary (e.g., "Monthly on 1st Sunday, 3 exceptions")
3. **Given** administrator views existing recurring series, **When** event details panel opens, **Then** natural language description shows prominently without needing to open edit mode
4. **Given** complex pattern with multiple days and interval, **When** summary generates, **Then** reads naturally (e.g., "Every 3 weeks on Monday, Wednesday, and Friday" not technical "FREQ=WEEKLY;INTERVAL=3;BYDAY=MO,WE,FR")

---

### User Story 7 - Custom Recurrence Patterns (Priority: P3)

Administrator creates advanced recurrence patterns beyond weekly/biweekly/monthly presets, such as "first Sunday of each month" or "every weekday" for organizations with complex scheduling needs.

**Why this priority**: P3 - Addresses advanced use cases but not needed for majority of users. Weekly/biweekly/monthly (P1) covers 90% of real-world recurring event needs.

**Independent Test**: Create "first Sunday of each month" pattern for 12 months, verify 12 occurrences all fall on first Sunday. Create "every weekday" pattern for 2 weeks, verify 10 occurrences (Mon-Fri only).

**Acceptance Scenarios**:

1. **Given** administrator selects "Monthly" pattern, **When** advanced options expand, **Then** choices include "On day X" vs "On the [first/second/third/fourth/last] [day of week]"
2. **Given** administrator creates "first Monday of month" pattern, **When** preview generates, **Then** all occurrences fall on first Monday of their respective months
3. **Given** administrator needs weekday-only pattern, **When** they select "Custom" frequency, **Then** day-of-week multi-select appears allowing Monday-Friday selection
4. **Given** custom pattern is complex, **When** natural language summary generates, **Then** description accurately reflects complexity (e.g., "On the 2nd and 4th Tuesday of each month")

---

### Edge Cases

- **Daylight Saving Time transitions**: When recurring event crosses DST change, event time remains consistent in local time (10:00 AM stays 10:00 AM, not shifting by 1 hour)
- **Month-end recurrence**: For monthly events on 29th-31st, when month has fewer days, event is created on last available day of month (31st becomes 28th/30th in shorter months)
- **Deleted series with future occurrences**: If administrator deletes recurring series, confirm dialog warns "This will delete X future occurrences - are you sure?" preventing accidental mass deletion
- **Editing past occurrences**: When administrator attempts to edit occurrence that already passed, system allows edit but displays warning "This event already occurred - changes won't affect past assignments"
- **Recurrence without end date**: If administrator creates recurring pattern with no end condition (infinite recurrence), system enforces maximum limit (e.g., 104 weeks / 2 years) and warns "Pattern will generate 104 occurrences - set end date for longer series"
- **Overlapping exceptions**: If administrator adds exception for date that already has individual modification, system prompts to choose: keep individual modification, replace with exception, or cancel
- **Bulk edit with conflicts**: When bulk edit creates volunteer assignment conflicts, system provides conflict report showing affected events and volunteers with option to proceed or cancel

---

## Requirements *(mandatory)*

### Functional Requirements

#### Recurrence Pattern Creation

- **FR-001**: System MUST provide recurrence frequency options: weekly, biweekly (every 2 weeks), monthly, and custom intervals
- **FR-002**: System MUST support multiple day-of-week selection for weekly/biweekly patterns (e.g., Monday and Wednesday)
- **FR-003**: System MUST support monthly recurrence on specific day of month (e.g., 15th of each month) or relative day (e.g., first Sunday of each month)
- **FR-004**: System MUST provide end condition options: specific end date, after X occurrences, or no end (maximum 104 occurrences enforced)
- **FR-005**: System MUST generate all occurrences within 3 seconds for patterns creating up to 104 events

#### Visual Calendar Preview

- **FR-006**: System MUST display visual calendar preview showing all generated occurrence dates before creation
- **FR-007**: Calendar preview MUST update within 1 second whenever recurrence pattern parameters change
- **FR-008**: Calendar preview MUST visually distinguish recurring event occurrences from existing one-time events
- **FR-009**: Calendar preview MUST show first 12 weeks of occurrences with summary count for patterns generating 50+ events
- **FR-010**: Calendar preview MUST highlight conflicts with existing events or volunteer availability

#### Series vs Individual Editing

- **FR-011**: When editing recurring event occurrence, system MUST present clear choice: "Edit only this occurrence", "Edit entire series", "Edit this and future occurrences"
- **FR-012**: "Edit only this occurrence" MUST modify single occurrence without affecting other occurrences in series
- **FR-013**: "Edit entire series" MUST apply changes to all occurrences (past and future) within 3 seconds
- **FR-014**: "Edit this and future" MUST apply changes from selected occurrence forward, leaving past occurrences unchanged
- **FR-015**: System MUST track which occurrences have individual modifications separate from series pattern
- **FR-016**: When editing series after individual occurrences were modified, system MUST prompt whether to preserve or overwrite individual modifications

#### Exception Management

- **FR-017**: System MUST allow marking specific dates as exceptions to skip occurrence entirely
- **FR-018**: System MUST allow marking specific dates as modified occurrences with different time, title, or details
- **FR-019**: Exception interface MUST display all current exceptions with dates and modification types (skipped vs modified)
- **FR-020**: System MUST provide common holiday exception library (Christmas, Easter, Thanksgiving, New Year's) for quick selection
- **FR-021**: When exception is added to skip occurrence, system MUST immediately remove that occurrence from calendar and scheduling solver

#### Bulk Operations

- **FR-022**: System MUST provide occurrence selection interface with checkboxes for individual selection
- **FR-023**: System MUST provide "Select All", "Select Range (by date)", and "Select by Criteria" options for bulk selection
- **FR-024**: Bulk edit MUST support modifying title, role requirements, notes, and volunteer assignments for selected occurrences
- **FR-025**: Bulk edit MUST be atomic operation - either all selected occurrences update successfully or none update (rollback on error)
- **FR-026**: Before bulk edit commits, system MUST display confirmation showing number of occurrences affected and preview of changes
- **FR-027**: When bulk edit creates scheduling conflicts, system MUST show conflict report with affected volunteers and option to proceed or cancel

#### Natural Language Descriptions

- **FR-028**: System MUST generate human-readable recurrence summary from pattern configuration (e.g., "Every 2 weeks on Monday, ending after 20 occurrences")
- **FR-029**: Recurrence summary MUST update in real-time as administrator modifies pattern parameters
- **FR-030**: Summary MUST include exception count when exceptions exist (e.g., "Weekly on Sunday, 3 exceptions")
- **FR-031**: For complex patterns (multiple days, custom intervals), summary MUST read naturally avoiding technical recurrence rule syntax

#### Integration with Event Management

- **FR-032**: Recurring event occurrences MUST integrate with existing event management system as individual Event records
- **FR-033**: Each occurrence MUST maintain link to parent recurring series for identification and batch operations
- **FR-034**: When scheduling solver runs, recurring event occurrences MUST be treated identically to one-time events for volunteer assignment
- **FR-035**: Deleting recurring series MUST prompt administrator with warning showing count of future occurrences that will be deleted
- **FR-036**: System MUST support converting one-time event to recurring series and vice versa

### Key Entities

- **Recurrence Rule**: Defines the repeating pattern for event series
  - Fields: frequency (weekly, biweekly, monthly, custom), interval (every X weeks/months), days of week (for weekly patterns), day of month (for monthly patterns), month day type (specific date vs relative like "first Sunday"), end condition type (date, count, none), end date, occurrence count, maximum occurrences enforced
  - Relationships: Belongs to recurring event series, generates event occurrences
  - Behavior: Generates occurrence dates based on pattern configuration, enforces maximum occurrence limit (104), handles month-end edge cases

- **Event Occurrence**: Individual event instance generated from recurrence rule
  - Fields: occurrence date, event ID, parent series ID, is exception (boolean), exception type (skip, modify, none), individual modifications (JSON storing field-level changes from series pattern), sequence number in series
  - Relationships: Belongs to event (standard Event entity), belongs to recurring series, may have exception details
  - Behavior: Inherits properties from parent series pattern unless individually modified, can be edited independently or as part of series, marks itself as exception when skipped or modified

- **Recurrence Exception**: Specific date excluded or modified in recurring pattern
  - Fields: exception date, exception type (skip occurrence, modify occurrence), modified fields (time, title, role requirements for modify type), reason (optional text explanation)
  - Relationships: Belongs to recurring series, references specific occurrence
  - Behavior: When skip type, prevents occurrence generation on that date; when modify type, overrides series pattern for that occurrence; appears in exception list UI

- **Recurring Series**: Container entity linking all occurrences of a repeating event
  - Fields: series ID, base event template (title, role requirements, duration), recurrence rule, creation date, created by administrator, total occurrences generated, active exceptions count
  - Relationships: Has one recurrence rule, has many event occurrences, has many exceptions
  - Behavior: Serves as parent for all generated occurrences, provides template for new occurrences, tracks series-level metadata and statistics

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators can create 52-week recurring event series in under 5 minutes compared to 45 minutes creating individual events manually (90% time reduction)
- **SC-002**: Visual calendar preview displays all occurrence dates within 1 second of pattern configuration changes
- **SC-003**: 95% of administrators successfully create their first recurring event series without help documentation or support tickets
- **SC-004**: Pattern conflicts (wrong day, incorrect frequency) are caught in preview before event creation in 100% of test scenarios
- **SC-005**: Editing single occurrence vs entire series choice is clear to 90% of users in usability testing (no accidental mass edits reported)
- **SC-006**: Bulk editing 20+ occurrences completes within 5 seconds without errors or timeouts
- **SC-007**: Exception handling (skipping holidays) reduces scheduling errors by 80% compared to manual deletion approach
- **SC-008**: Natural language recurrence summaries are understood by 95% of users in comprehension testing
- **SC-009**: Complex patterns (first Sunday of month, every weekday) generate correct occurrences in 100% of edge case tests
- **SC-010**: Recurring event occurrences integrate seamlessly with scheduling solver without performance degradation (solve time <10 seconds for 100 events)
- **SC-011**: Support tickets related to creating repetitive events decrease by 70% after recurring events feature launch
- **SC-012**: Administrators report satisfaction score of 8/10 or higher for recurring events feature in post-launch survey

---

## Assumptions

- Organizations primarily use weekly and monthly recurrence patterns; custom patterns serve <10% of use cases
- Maximum practical recurrence series length is 2 years (104 weeks); longer series should be recreated annually
- Administrators understand concepts of "series" vs "individual occurrence" without extensive training
- Visual calendar preview is sufficient for verification; numerical list view is secondary
- Recurrence rules follow standard RFC 5545 (iCalendar) semantics for compatibility with external calendar systems (future integration)
- Bulk operations typically affect 10-50 occurrences; UI optimized for this range
- Exception management for holidays covers 90% of real-world exception needs; complex exception patterns are rare

---

## Out of Scope

- **Recurring availability patterns**: This feature focuses on recurring *events*; recurring volunteer availability patterns are separate feature
- **Attendance tracking per occurrence**: Standard attendance tracking applies to each occurrence, but series-level attendance analytics are out of scope
- **Recurrence rule import/export**: Manual recurrence creation only; importing from external calendar systems (Google Calendar, Outlook) is future feature
- **Multi-timezone recurrence**: All occurrences in series use organization's timezone; individual occurrence timezone override is out of scope
- **Automated exception detection**: System does not automatically skip holidays; administrator must manually configure exceptions
- **Recurrence pattern suggestions**: System does not suggest recurrence patterns based on past event history; administrator creates patterns manually
- **Versioning of series edits**: No undo/redo for series-level changes; database-level rollback only in case of errors

