# Rostio User Stories & Workflows

> **Purpose**: This document defines end-to-end user workflows for Rostio, ensuring every user scenario is complete and functional. Based on research from Planning Center Services, Ministry Scheduler Pro, and church volunteer management best practices (2025).

## 📋 Table of Contents

1. [New Volunteer User Journey](#1-new-volunteer-user-journey)
2. [Existing Volunteer Workflows](#2-existing-volunteer-workflows)
3. [Admin/Coordinator Workflows](#3-admincoordinator-workflows)
4. [Multi-Organization User Workflows](#4-multi-organization-user-workflows)
5. [Communication & Notification Workflows](#5-communication--notification-workflows)
6. [Team Leader Workflows](#6-team-leader-workflows)
7. [Edge Cases & Error Scenarios](#7-edge-cases--error-scenarios)

---

## 1. New Volunteer User Journey

### 1.1 First-Time Signup & Onboarding

**User Goal**: Sarah wants to join Grace Community Church's volunteer roster and see when she's scheduled to serve.

**Current Implementation Status**: ✅ Partially Implemented

#### Workflow Steps:

1. **Landing** → User visits `http://rostio.church` or `http://localhost:8000/`
   - ✅ Sees welcome screen with "Welcome to Rostio"
   - ✅ Shows 3-step onboarding preview
   - ✅ "Get Started" button visible

2. **Join Organization** → User clicks "Get Started"
   - ✅ Sees list of available organizations
   - ✅ Can search/filter organizations by name or location
   - ✅ Selects "Grace Community Church"
   - ⚠️ **MISSING**: Organization preview (member count, location, upcoming events)

3. **Create Profile** → User fills out personal information
   - ✅ Full name, email, password, phone (optional)
   - ✅ Selects roles they can serve in (checkboxes)
   - ⚠️ **MISSING**: Role descriptions/tooltips (what does "Tech/AV" involve?)
   - ⚠️ **MISSING**: Skill level selection (beginner, experienced, trainer)
   - ⚠️ **MISSING**: Preferred frequency (weekly, biweekly, monthly)

4. **Account Creation** → System creates account
   - ✅ Password hashing (bcrypt)
   - ✅ Creates Person record in database
   - ✅ Associates with organization
   - ⚠️ **MISSING**: Welcome email sent to user
   - ⚠️ **MISSING**: Admin notification of new signup

5. **Initial Availability** → User sets when they're available
   - ✅ Directed to Availability tab
   - ⚠️ **MISSING**: Guided tour/tutorial
   - ⚠️ **MISSING**: Pre-filled common patterns (e.g., "Available every Sunday morning")
   - ⚠️ **MISSING**: Recurring unavailability (e.g., "Every 2nd weekend I'm away")

6. **View Schedule** → User sees their calendar
   - ✅ Calendar view with month selector
   - ✅ Empty state message: "No assignments yet"
   - ⚠️ **MISSING**: Explanation of what happens next ("Admin will review and schedule you")
   - ⚠️ **MISSING**: Link to help docs or video tutorial

#### Success Criteria:
- [ ] User can complete signup in < 3 minutes
- [ ] User understands next steps (when will I be scheduled?)
- [ ] User receives confirmation email
- [ ] Admin is notified of new volunteer

#### Current Gaps:
1. No onboarding tutorial or help system
2. Missing email notifications
3. No "what happens next" messaging
4. Limited role selection (static list, no customization)

---

## 2. Existing Volunteer Workflows

### 2.1 View My Upcoming Schedule

**User Goal**: Sarah wants to see when she's serving in the next month.

**Current Implementation Status**: ✅ Implemented

#### Workflow Steps:

1. **Login** → User signs in
   - ✅ Email + password authentication
   - ✅ Session management
   - ✅ Redirect to My Calendar view

2. **Calendar View** → User sees calendar grid
   - ✅ Month selector (this month, next month, next 3 months)
   - ✅ Calendar grid with dates
   - ✅ Events displayed on calendar
   - ✅ Color coding by event type
   - ⚠️ **MISSING**: Filter by role (only show my "Worship Leader" assignments)
   - ⚠️ **MISSING**: Print view / PDF export

3. **Schedule List View** → User switches to list view
   - ✅ "My Schedule" tab
   - ✅ Chronological list of assignments
   - ✅ Shows: Date, Time, Event Type, Role
   - ⚠️ **MISSING**: Team members serving with me
   - ⚠️ **MISSING**: Event location/venue
   - ⚠️ **MISSING**: Preparation checklist per role

4. **Export Calendar** → User downloads to personal calendar
   - ✅ "Export to Calendar" button
   - ✅ Generates ICS file
   - ⚠️ **MISSING**: Choose date range for export
   - ⚠️ **MISSING**: Option to sync (not just download)
   - ⚠️ **MISSING**: Google Calendar integration
   - ⚠️ **MISSING**: Outlook integration

#### Success Criteria:
- [ ] User can see all assignments at a glance
- [ ] User can export to their personal calendar app
- [ ] User knows who else is serving with them
- [ ] User can access on mobile devices

#### Current Gaps:
1. No team member visibility
2. Limited export options (ICS only)
3. No calendar sync/integration
4. Missing event details (location, notes)

---

### 2.2 Update My Availability

**User Goal**: Sarah is going on vacation and needs to mark herself unavailable Oct 15-25.

**Current Implementation Status**: ✅ Implemented

#### Workflow Steps:

1. **Navigate to Availability** → User clicks "Availability" tab
   - ✅ Availability view with form
   - ✅ Add time off form visible

2. **Add Time Off** → User blocks dates
   - ✅ From date picker
   - ✅ To date picker
   - ✅ Reason field (optional)
   - ✅ Saves to database
   - ⚠️ **MISSING**: Recurring patterns (every 3rd weekend)
   - ⚠️ **MISSING**: Partial day unavailability (afternoon only)
   - ⚠️ **MISSING**: Warning if already scheduled during these dates

3. **View Blocked Dates** → User sees list of unavailability
   - ✅ List of time-off entries
   - ✅ Shows date range and reason
   - ⚠️ **MISSING**: Edit existing time-off
   - ⚠️ **MISSING**: Delete time-off entries
   - ⚠️ **MISSING**: Calendar visualization of blocked dates

4. **Confirmation** → System updates scheduling
   - ⚠️ **MISSING**: Confirmation message shown
   - ⚠️ **MISSING**: Email to admin about availability change
   - ⚠️ **MISSING**: Check if conflicts with existing assignments

#### Success Criteria:
- [ ] User can add/edit/delete time-off easily
- [ ] System warns if conflicts exist
- [ ] Admin is notified of changes
- [ ] User sees confirmation

#### Current Gaps:
1. Cannot edit/delete existing availability blocks
2. No conflict detection with scheduled assignments
3. No admin notification
4. Missing recurring patterns

---

### 2.3 Swap/Decline an Assignment

**User Goal**: Sarah is scheduled for Oct 20 but realizes she can't make it. She needs to find a replacement or decline.

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **View Assignment Details** → User clicks on calendar event
   - ⚠️ **MISSING**: Modal/dialog with full event details
   - ⚠️ **MISSING**: Role, time, location, team members
   - ⚠️ **MISSING**: "I can't make it" button

2. **Decline Assignment** → User indicates they can't serve
   - ⚠️ **MISSING**: Decline with reason (sick, conflict, etc.)
   - ⚠️ **MISSING**: Option to find replacement vs. notify admin
   - ⚠️ **MISSING**: Deadline for declining (e.g., must decline 48hr in advance)

3. **Find Replacement** → User requests swap
   - ⚠️ **MISSING**: See list of eligible replacements (same role, available that day)
   - ⚠️ **MISSING**: Send swap request to specific person
   - ⚠️ **MISSING**: Broadcast to all eligible people

4. **Approve Swap** → Replacement accepts
   - ⚠️ **MISSING**: Notification to proposed replacement
   - ⚠️ **MISSING**: Accept/decline swap request
   - ⚠️ **MISSING**: Admin approval (optional)

5. **Confirmation** → System updates schedule
   - ⚠️ **MISSING**: Both people notified
   - ⚠️ **MISSING**: Calendar updated automatically
   - ⚠️ **MISSING**: Admin notified of swap

#### Success Criteria:
- [ ] User can decline within X days before event
- [ ] System suggests eligible replacements
- [ ] Swaps don't require manual admin work
- [ ] All parties notified automatically

#### Current Gaps:
1. Entire swap/decline workflow missing
2. No replacement suggestion engine
3. No approval workflow
4. Critical gap for volunteer retention!

---

### 2.4 Request Specific Dates/Roles

**User Goal**: Sarah loves being worship leader and wants to request to serve Dec 24 (Christmas Eve).

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **Request to Serve** → User proactively volunteers
   - ⚠️ **MISSING**: "Request to Serve" button
   - ⚠️ **MISSING**: Calendar view showing unassigned slots
   - ⚠️ **MISSING**: Filter by role

2. **Select Event** → User picks specific date/role
   - ⚠️ **MISSING**: Click on calendar date
   - ⚠️ **MISSING**: See available roles for that event
   - ⚠️ **MISSING**: Submit request with optional note

3. **Admin Review** → Coordinator reviews request
   - ⚠️ **MISSING**: Requests queue in admin dashboard
   - ⚠️ **MISSING**: Approve/deny with one click
   - ⚠️ **MISSING**: Auto-approve if slots available

4. **Confirmation** → User notified
   - ⚠️ **MISSING**: Email/SMS notification
   - ⚠️ **MISSING**: Shows on calendar as "Requested" vs. "Confirmed"

#### Success Criteria:
- [ ] Users can proactively volunteer
- [ ] Admin can approve quickly
- [ ] Reduces admin workload
- [ ] Increases volunteer engagement

#### Current Gaps:
1. No self-serve request system
2. Entirely admin-driven scheduling
3. Reduces volunteer autonomy
4. Important for engagement!

---

## 3. Admin/Coordinator Workflows

### 3.1 Create Organization & Setup

**User Goal**: Pastor John wants to set up Grace Community Church in Rostio.

**Current Implementation Status**: ✅ Partially Implemented

#### Workflow Steps:

1. **Create Organization** → Admin creates org
   - ✅ Organization name
   - ✅ Location/region
   - ⚠️ **MISSING**: Organization logo upload
   - ⚠️ **MISSING**: Time zone selection
   - ⚠️ **MISSING**: First day of week (Sunday vs. Monday)

2. **Define Custom Roles** → Admin configures roles
   - ✅ Add role button
   - ✅ Role name and description
   - ⚠️ **MISSING**: Role requirements (training, background check)
   - ⚠️ **MISSING**: Role capacity per event (max 2 worship leaders)
   - ⚠️ **MISSING**: Role priority (critical vs. optional)

3. **Create Resources/Venues** → Admin sets up locations
   - ✅ Resource type (worship hall, classroom)
   - ✅ Location name
   - ✅ Capacity
   - ⚠️ **MISSING**: Equipment list per venue
   - ⚠️ **MISSING**: Setup requirements

4. **Import Existing Volunteers** → Bulk add people
   - ⚠️ **MISSING**: CSV upload
   - ⚠️ **MISSING**: Field mapping tool
   - ⚠️ **MISSING**: Send invite emails to all
   - ⚠️ **MISSING**: Preview before import

#### Success Criteria:
- [ ] Admin can set up org in < 15 minutes
- [ ] Can import existing volunteer list
- [ ] Custom roles reflect organization's needs
- [ ] Clear setup wizard/checklist

#### Current Gaps:
1. No bulk import functionality
2. Manual volunteer entry only
3. Missing setup wizard
4. No invite email system

---

### 3.2 Create Events (Recurring & One-Time)

**User Goal**: Admin creates weekly Sunday services + special Christmas Eve service.

**Current Implementation Status**: ✅ Partially Implemented

#### Workflow Steps:

1. **Open Event Creation** → Admin clicks "Create Event"
   - ✅ Event creation modal
   - ✅ Event type dropdown

2. **Event Details** → Admin fills form
   - ✅ Event type (Sunday Service, Bible Study, etc.)
   - ✅ Start date & time
   - ✅ Duration
   - ✅ Location (resource)
   - ⚠️ **MISSING**: Recurrence pattern UI
   - ⚠️ **MISSING**: End recurrence date
   - ⚠️ **MISSING**: Exception dates (skip July 4th)

3. **Define Role Requirements** → Specify needed roles
   - ✅ Roles needed (comma-separated)
   - ⚠️ **MISSING**: Quantity per role (need 2 ushers)
   - ⚠️ **MISSING**: Required vs. optional roles
   - ⚠️ **MISSING**: Role-specific notes ("Bring guitar")

4. **Save & Generate** → Create events
   - ✅ Single event created
   - ⚠️ **MISSING**: Generate series (all Sundays for next 3 months)
   - ⚠️ **MISSING**: Bulk edit series
   - ⚠️ **MISSING**: Template system (save common configurations)

#### Success Criteria:
- [ ] Admin can create 3 months of weekly services in < 2 minutes
- [ ] Can specify quantity per role
- [ ] Can create exceptions easily
- [ ] Templates for common events

#### Current Gaps:
1. Recurrence only works via API, not in UI
2. Must manually create each event in GUI
3. No bulk operations
4. Critical usability gap!

---

### 3.3 Generate Schedule (Auto-Assign Volunteers)

**User Goal**: Admin wants to auto-generate assignments for the next month.

**Current Implementation Status**: ✅ Implemented

#### Workflow Steps:

1. **Review Requirements** → Admin checks readiness
   - ✅ See count of people, events, roles
   - ⚠️ **MISSING**: Pre-flight checklist (Are there enough worship leaders?)
   - ⚠️ **MISSING**: Warning if insufficient volunteers

2. **Run Solver** → Admin clicks "Generate Schedule"
   - ✅ Solver runs in background
   - ✅ Creates assignments based on availability, roles
   - ✅ Shows progress/status
   - ⚠️ **MISSING**: Solver progress bar
   - ⚠️ **MISSING**: Estimated time remaining

3. **Review Generated Schedule** → Admin previews
   - ✅ Schedule list shows assignment count
   - ✅ Health score displayed
   - ✅ Can view details
   - ⚠️ **MISSING**: Side-by-side comparison of multiple solutions
   - ⚠️ **MISSING**: Warnings (person serving 3 weeks in a row)
   - ⚠️ **MISSING**: Unassigned roles highlighted

4. **Manual Adjustments** → Admin tweaks assignments
   - ⚠️ **MISSING**: Drag-drop interface
   - ⚠️ **MISSING**: Search and replace person
   - ⚠️ **MISSING**: Lock specific assignments (don't auto-change Sarah for Dec 24)

5. **Publish Schedule** → Make live
   - ⚠️ **MISSING**: "Publish" vs. "Draft" status
   - ⚠️ **MISSING**: Send notifications to all volunteers
   - ⚠️ **MISSING**: Confirmation dialog

#### Success Criteria:
- [ ] Solver generates viable schedule in < 30 seconds
- [ ] Admin can make manual tweaks easily
- [ ] System warns of issues (conflicts, overload)
- [ ] One-click publish & notify

#### Current Gaps:
1. No manual editing interface
2. No publish workflow
3. No bulk notifications
4. Generated schedules go live immediately (no draft mode)

---

### 3.4 Export & Communicate Schedule

**User Goal**: Admin wants to export and email the schedule to all volunteers.

**Current Implementation Status**: ✅ Partially Implemented

#### Workflow Steps:

1. **Export Schedule** → Admin downloads
   - ✅ Click "View" button
   - ✅ CSV download
   - ⚠️ **MISSING**: PDF export (printable)
   - ⚠️ **MISSING**: Excel/XLSX format
   - ⚠️ **MISSING**: Filtered exports (just worship team)

2. **Send Notifications** → Inform volunteers
   - ⚠️ **MISSING**: Bulk email system
   - ⚠️ **MISSING**: SMS notifications
   - ⚠️ **MISSING**: Customizable message template
   - ⚠️ **MISSING**: Send to specific teams only

3. **Print/Display** → Physical distribution
   - ⚠️ **MISSING**: Print-friendly view
   - ⚠️ **MISSING**: Large display mode (TV in lobby)
   - ⚠️ **MISSING**: QR code for mobile access

#### Success Criteria:
- [ ] One-click export in multiple formats
- [ ] Built-in email/SMS notifications
- [ ] Print-ready views
- [ ] Mobile-friendly sharing

#### Current Gaps:
1. CSV only (no PDF, Excel)
2. No communication system
3. External email tool required
4. Major usability gap!

---

### 3.5 Monitor & Manage Volunteers

**User Goal**: Admin wants to see volunteer participation trends and identify issues.

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **People Dashboard** → View volunteer list
   - ✅ List of all people
   - ✅ Shows name, email, roles
   - ⚠️ **MISSING**: Last served date
   - ⚠️ **MISSING**: Times served this year
   - ⚠️ **MISSING**: Availability status
   - ⚠️ **MISSING**: Sort by activity level

2. **Participation Reports** → Analyze trends
   - ⚠️ **MISSING**: Chart of serves per month
   - ⚠️ **MISSING**: Burnout alerts (serving too often)
   - ⚠️ **MISSING**: Inactive volunteers (haven't served in 3 months)
   - ⚠️ **MISSING**: Role coverage gaps

3. **Volunteer Outreach** → Re-engage inactive
   - ⚠️ **MISSING**: Filter by "inactive"
   - ⚠️ **MISSING**: Send reminder emails
   - ⚠️ **MISSING**: Request updated availability

#### Success Criteria:
- [ ] Admin can spot burnout risks
- [ ] Can identify inactive volunteers
- [ ] Can re-engage with one click
- [ ] Reports show trends over time

#### Current Gaps:
1. No reporting/analytics
2. No participation tracking
3. Manual spreadsheet tracking required
4. Important for volunteer retention!

---

## 4. Multi-Organization User Workflows

### 4.1 Member of Multiple Organizations

**User Goal**: Sarah serves at Grace Community Church AND volunteers at her kids' school. She needs to manage both schedules.

**Current Implementation Status**: ✅ Partially Implemented

#### Workflow Steps:

1. **Join Second Organization** → User adds another org
   - ⚠️ **MISSING**: UI to join additional org while logged in
   - ⚠️ **MISSING**: Keep same email/password
   - ⚠️ **MISSING**: Different roles per org

2. **Switch Between Organizations** → Toggle active org
   - ✅ Org dropdown in header (exists in code but hidden)
   - ⚠️ **MISSING**: Actually show dropdown when user has 2+ orgs
   - ⚠️ **MISSING**: Remember last selected org

3. **Unified Calendar View** → See all assignments
   - ⚠️ **MISSING**: Combined calendar showing both orgs
   - ⚠️ **MISSING**: Color-code by organization
   - ⚠️ **MISSING**: Filter by org

4. **Conflict Detection** → Prevent double-booking
   - ⚠️ **MISSING**: Warn if scheduled at 2 places same time
   - ⚠️ **MISSING**: Cross-org availability sync

#### Success Criteria:
- [ ] User can belong to multiple orgs
- [ ] Easy switching between org contexts
- [ ] Unified view of all commitments
- [ ] Conflict prevention

#### Current Gaps:
1. Org dropdown exists but hidden
2. No cross-org calendar
3. No conflict detection
4. Partially implemented feature!

---

## 5. Communication & Notification Workflows

### 5.1 Assignment Notifications

**User Goal**: Sarah wants to be notified when she's scheduled or when schedule changes.

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **Email Notification** → User receives email
   - ⚠️ **MISSING**: Email sent when assigned
   - ⚠️ **MISSING**: Subject: "You're scheduled for Worship Leader on Dec 24"
   - ⚠️ **MISSING**: Email body with event details
   - ⚠️ **MISSING**: "Add to Calendar" button in email
   - ⚠️ **MISSING**: Link to accept/decline

2. **SMS Notification** (Optional) → Text message
   - ⚠️ **MISSING**: SMS opt-in preference
   - ⚠️ **MISSING**: Integration with Twilio or similar
   - ⚠️ **MISSING**: Short message with link

3. **Reminder Notifications** → Before event
   - ⚠️ **MISSING**: Reminder 1 week before
   - ⚠️ **MISSING**: Reminder 1 day before
   - ⚠️ **MISSING**: Reminder 1 hour before (optional)
   - ⚠️ **MISSING**: Configurable reminder timing

4. **Change Notifications** → When schedule updates
   - ⚠️ **MISSING**: Email if assignment changes
   - ⚠️ **MISSING**: Email if assignment cancelled
   - ⚠️ **MISSING**: Change summary (was Sunday 10am, now Sunday 11am)

#### Success Criteria:
- [ ] 100% of volunteers receive assignments by email
- [ ] Reminders reduce no-shows
- [ ] Changes communicated immediately
- [ ] User can customize notification preferences

#### Current Gaps:
1. No email infrastructure
2. No SMS capability
3. Entirely manual communication
4. Critical missing feature!

---

### 5.2 Team Communication

**User Goal**: Worship team needs to coordinate rehearsal and discuss song list.

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **Team Chat** → Message team members
   - ⚠️ **MISSING**: Team messaging interface
   - ⚠️ **MISSING**: Group threads per event
   - ⚠️ **MISSING**: @mention team members
   - ⚠️ **MISSING**: Share files/links

2. **Event Notes** → Shared preparation info
   - ⚠️ **MISSING**: Admin can add notes to event
   - ⚠️ **MISSING**: Team members can see notes
   - ⚠️ **MISSING**: Checklist per event

3. **Announcements** → Broadcast to all
   - ⚠️ **MISSING**: Admin announcement system
   - ⚠️ **MISSING**: Targeted announcements (worship team only)

#### Success Criteria:
- [ ] Teams can coordinate without external tools
- [ ] Important info doesn't get lost
- [ ] Admin can broadcast updates

#### Current Gaps:
1. No messaging system
2. Requires external tools (email, Slack, WhatsApp)
3. Future enhancement (not MVP)

---

## 6. Team Leader Workflows

### 6.1 Worship Leader Manages Worship Team

**User Goal**: Emily is worship leader. She's not full admin but needs to manage the worship team's schedule.

**Current Implementation Status**: ❌ NOT Implemented

#### Workflow Steps:

1. **Team Leader Dashboard** → Limited admin access
   - ⚠️ **MISSING**: Role-based permissions
   - ⚠️ **MISSING**: Team-specific view
   - ⚠️ **MISSING**: See only worship team events/people

2. **Assign Team Members** → Manage worship team
   - ⚠️ **MISSING**: Assign people to worship team
   - ⚠️ **MISSING**: Request specific volunteers
   - ⚠️ **MISSING**: Approve/deny swap requests for my team

3. **Team Roster** → Maintain team list
   - ⚠️ **MISSING**: Add new worship team volunteers
   - ⚠️ **MISSING**: Edit team member profiles
   - ⚠️ **MISSING**: Mark people as inactive

#### Success Criteria:
- [ ] Delegated management reduces admin burden
- [ ] Team leaders have autonomy
- [ ] Permissions prevent overstep

#### Current Gaps:
1. No role-based permissions system
2. Binary admin/non-admin only
3. All management requires full admin
4. Future enhancement

---

## 7. Edge Cases & Error Scenarios

### 7.1 Insufficient Volunteers

**Scenario**: Admin runs solver but there aren't enough worship leaders for all Sunday services.

**Current Behavior**:
- ✅ Solver runs
- ⚠️ May generate incomplete schedule
- ⚠️ No clear warning to admin

**Desired Behavior**:
- [ ] Pre-flight check before running solver
- [ ] Warning: "Need 4 worship leaders for 5 services"
- [ ] Suggestions: "Recruit 1 more, or reduce services"
- [ ] Show which dates/events won't be covered

---

### 7.2 Volunteer Never Sets Availability

**Scenario**: Sarah signs up but never sets her availability. Admin runs solver.

**Current Behavior**:
- ✅ Solver assumes Sarah is always available
- ⚠️ Sarah may get assigned when she's actually busy

**Desired Behavior**:
- [ ] Default to "not available" until user confirms
- [ ] Email reminder to set availability
- [ ] Admin sees which volunteers haven't set availability
- [ ] Solver deprioritizes unconfirmed volunteers

---

### 7.3 Last-Minute Cancellation

**Scenario**: 2 hours before Sunday service, worship leader Sarah calls in sick.

**Current Behavior**:
- ⚠️ Manual phone tree to find replacement
- ⚠️ Nothing in system

**Desired Behavior**:
- [ ] Sarah marks herself as "can't make it" in app
- [ ] System sends emergency request to all backup worship leaders
- [ ] First to accept gets the slot
- [ ] All parties notified instantly

---

### 7.4 Schedule Conflicts (Double-Booking)

**Scenario**: User is scheduled at 2 different events at the same time.

**Current Behavior**:
- ⚠️ No conflict detection
- ⚠️ User only discovers when viewing calendar

**Desired Behavior**:
- [ ] Solver prevents conflicts
- [ ] If manual edit creates conflict, show error
- [ ] Cross-org conflict detection
- [ ] User sees warning on calendar

---

### 7.5 Deleted User/Event

**Scenario**: Admin deletes a volunteer who's assigned to 5 upcoming events.

**Current Behavior**:
- ✅ Database cascade delete removes assignments
- ⚠️ No warning to admin
- ⚠️ Events now underassigned

**Desired Behavior**:
- [ ] Warning: "Sarah is assigned to 5 events. Delete anyway?"
- [ ] Option to reassign first
- [ ] Soft delete (archive) instead of hard delete
- [ ] Restore capability

---

## 📊 Implementation Priority Matrix

| Workflow | Severity | Effort | Priority |
|----------|----------|--------|----------|
| **Recurring events in UI** | 🔴 Critical | Medium | P0 |
| **Manual schedule editing** | 🔴 Critical | High | P0 |
| **Email notifications** | 🔴 Critical | Medium | P0 |
| **Edit/delete availability** | 🟡 High | Low | P1 |
| **Swap/decline assignments** | 🟡 High | High | P1 |
| **CSV import volunteers** | 🟡 High | Medium | P1 |
| **Multi-org dropdown visibility** | 🟡 High | Low | P1 |
| **PDF export** | 🟢 Medium | Low | P2 |
| **Role quantities per event** | 🟢 Medium | Low | P2 |
| **Self-serve requests** | 🟢 Medium | Medium | P2 |
| **Participation analytics** | 🔵 Nice-to-have | Medium | P3 |
| **Team messaging** | 🔵 Nice-to-have | High | P3 |
| **Role-based permissions** | 🔵 Nice-to-have | High | P3 |

---

## 🎯 Next Steps

### Immediate Actions (P0 - Week 1-2)

1. **Recurring Events UI**
   - Add recurrence pattern selector to event creation form
   - Implement "Generate Series" functionality
   - Add bulk edit for event series

2. **Manual Schedule Editing**
   - Create drag-drop assignment interface
   - Add "lock" feature for assignments
   - Implement unassigned roles warning

3. **Email Notifications**
   - Set up email infrastructure (SMTP/SendGrid)
   - Create email templates
   - Implement assignment notification triggers

### Short Term (P1 - Week 3-4)

4. **Availability Management**
   - Add edit/delete to time-off entries
   - Implement conflict warnings
   - Add recurring patterns

5. **Volunteer Import**
   - CSV upload interface
   - Field mapping tool
   - Bulk invite emails

6. **Swap/Decline Workflow**
   - Assignment detail modal
   - Decline with replacement suggestion
   - Notification workflow

### Medium Term (P2 - Month 2)

7. **Enhanced Exports**
   - PDF generation
   - Excel format
   - Print views

8. **Self-Serve Requests**
   - Request-to-serve UI
   - Admin approval queue
   - Auto-approve logic

### Long Term (P3 - Month 3+)

9. **Analytics Dashboard**
   - Participation tracking
   - Burnout detection
   - Engagement reports

10. **Advanced Features**
    - Team messaging
    - Role-based permissions
    - Mobile app

---

## 📝 User Story Format

Each feature should follow this template:

```
As a [user type]
I want to [action]
So that [benefit]

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2

Current Status: [✅ Done | ⚠️ Partial | ❌ Not Started]
Files Involved: [list of files]
API Endpoints: [list of endpoints]
Database Changes: [schema updates needed]
```

---

## 🔄 Workflow Validation Checklist

Before marking any workflow as "complete", verify:

- [ ] End-to-end test exists (GUI automated test)
- [ ] Error cases handled gracefully
- [ ] User receives feedback (success/error messages)
- [ ] Mobile responsive
- [ ] Accessible (keyboard navigation, screen readers)
- [ ] Documented in help system
- [ ] Performance acceptable (< 2s load time)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Next Review**: After P0 features complete
