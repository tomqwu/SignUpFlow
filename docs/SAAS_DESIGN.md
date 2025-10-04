# Rostio SaaS Design - User Stories & Best Practices

## Executive Summary
This document outlines the enhanced SaaS architecture for Rostio based on 2025 best practices for event management systems, focusing on improved RBAC, user invitation workflows, and enhanced admin experience.

---

## User Roles & Permissions (RBAC)

### Role Hierarchy
1. **Super Admin** - Organization owner
   - Full access to all features
   - Can invite/remove admins
   - Can delete organization
   - Manage billing (future)

2. **Admin** - Team coordinator/staff
   - Manage events, schedules, and assignments
   - Invite volunteers
   - View all reports
   - Cannot delete organization or remove super admin

3. **Volunteer** - Regular user
   - View assigned schedules
   - Manage own availability/time-off
   - Accept/decline assignments
   - Swap shifts with others (with approval)

4. **Viewer** - Read-only access
   - View schedules and events
   - No editing capabilities
   - Useful for families or external stakeholders

### Permission Matrix

| Feature | Super Admin | Admin | Volunteer | Viewer |
|---------|-------------|-------|-----------|--------|
| Create/Edit Events | ✓ | ✓ | ✗ | ✗ |
| Generate Schedules | ✓ | ✓ | ✗ | ✗ |
| Assign Volunteers | ✓ | ✓ | ✗ | ✗ |
| Invite Users | ✓ | ✓ (volunteers only) | ✗ | ✗ |
| Remove Users | ✓ | ✓ (volunteers only) | ✗ | ✗ |
| View All Schedules | ✓ | ✓ | Own only | ✓ |
| Manage Own Availability | ✓ | ✓ | ✓ | ✗ |
| Export Reports | ✓ | ✓ | ✗ | ✗ |
| Edit Organization Settings | ✓ | ✗ | ✗ | ✗ |

---

## User Stories

### Epic 1: User Invitation & Onboarding

**US-1.1: Admin Invites Volunteer**
```
As an Admin
I want to invite volunteers via email
So that they can join the organization without creating an account first

Acceptance Criteria:
- Admin can enter email, name, and assign initial roles
- System sends invitation email with unique signup link
- Link expires after 7 days
- Invitee can complete signup with minimal friction
- Admin can view pending invitations and resend/cancel
```

**US-1.2: Volunteer Accepts Invitation**
```
As a Volunteer
I want to accept an invitation via email link
So that I can quickly join my church's scheduling system

Acceptance Criteria:
- Click email link → pre-filled signup form
- Only need to set password
- Account automatically linked to organization
- Roles pre-assigned from invitation
- Redirect to availability setup after signup
```

**US-1.3: Track Invitation Status**
```
As an Admin
I want to see the status of all invitations
So that I can follow up with volunteers who haven't joined

Acceptance Criteria:
- Dashboard shows: Pending, Accepted, Expired, Cancelled
- Can resend invitation emails
- Can cancel pending invitations
- Expired invitations auto-archive after 30 days
```

### Epic 2: Enhanced Admin Console

**US-2.1: Tabbed Admin Interface**
```
As an Admin
I want the admin console organized into clear tabs
So that I can efficiently navigate between different management tasks

Acceptance Criteria:
- Tabs: Events | Roles | Schedule | People | Reports
- Each tab loads independently
- Current tab highlighted in navigation
- URL reflects current tab for bookmarking
```

**US-2.2: Event Management Tab**
```
As an Admin
I want a dedicated Events tab
So that I can manage all event configurations in one place

Acceptance Criteria:
- List all events with filters (upcoming, recurring, past)
- Create/Edit/Delete events
- Configure role requirements per event
- Set recurrence patterns
- Bulk operations (duplicate, delete multiple)
```

**US-2.3: Role Management Tab**
```
As an Admin
I want a Roles tab to manage all volunteer roles
So that I can define skills and requirements clearly

Acceptance Criteria:
- CRUD operations for roles
- Define role descriptions and requirements
- Assign colors for visual identification
- View which volunteers have each role
- Role usage statistics
```

**US-2.4: Schedule Management Tab**
```
As an Admin
I want a dedicated Schedule tab
So that I can generate and manage assignments efficiently

Acceptance Criteria:
- Calendar view of all scheduled events
- Generate schedule with conflict detection
- Manual override assignments
- View blocked dates and conflicts
- Publish/unpublish schedules
```

**US-2.5: People Management Tab**
```
As an Admin
I want a People tab to manage all users
So that I can see volunteer info and availability

Acceptance Criteria:
- List all people with role filters
- View individual availability calendars
- See assignment history
- Invite new people
- Edit roles and permissions
- Deactivate users
```

### Epic 3: ICS Calendar Export

**US-3.1: Export Personal Schedule**
```
As a Volunteer
I want to export my schedule as an ICS file
So that I can add it to my Google/Apple/Outlook calendar

Acceptance Criteria:
- "Export to Calendar" button on My Schedule page
- Downloads .ics file with all assigned events
- Includes event details: title, time, location, role
- Works with Google Calendar, Apple Calendar, Outlook
- Updates when schedule changes (subscribe URL)
```

**US-3.2: Subscribe to Live Calendar**
```
As a Volunteer
I want a calendar subscription URL
So that my schedule auto-updates in my calendar app

Acceptance Criteria:
- Generate unique webcal:// URL per user
- URL stays valid until user resets it
- Calendar apps auto-refresh updates
- Includes only user's assigned events
- Option to reset URL if compromised
```

**US-3.3: Admin Export All Events**
```
As an Admin
I want to export all organization events
So that I can share the full schedule externally

Acceptance Criteria:
- Export all events or filtered subset
- ICS file with all event details
- Include assigned people per role
- Works for printing or sharing
```

### Epic 4: Enhanced Self-Service

**US-4.1: Shift Swap Request**
```
As a Volunteer
I want to request a shift swap with another volunteer
So that I can manage my own schedule conflicts

Acceptance Criteria:
- Select assignment to swap
- Choose replacement from eligible volunteers
- Replacement gets notification
- Admin gets notification of swap request
- Admin can approve/deny swap
- Both parties notified of outcome
```

**US-4.2: Find Substitute**
```
As a Volunteer
I want to find a substitute for my assignment
So that I can notify the team when I'm unavailable

Acceptance Criteria:
- Click "Find Substitute" on assignment
- System shows available people with same role
- Send substitute request to selected person
- Substitute can accept/decline
- Admin notified of substitution
```

---

## Technical Architecture

### Database Schema Changes

**Invitations Table**
```python
class Invitation(Base):
    id: str (PK)
    org_id: str (FK)
    email: str
    name: str
    roles: list[str]
    invited_by: str (FK to Person)
    token: str (unique)
    status: enum (pending, accepted, expired, cancelled)
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime
```

**Enhanced Person Model**
```python
class Person(Base):
    # Existing fields...
    status: enum (active, inactive, invited)
    invited_by: str (FK to Person) nullable
    last_login: datetime
```

**Swap Requests Table**
```python
class SwapRequest(Base):
    id: str (PK)
    assignment_id: str (FK)
    requestor_id: str (FK to Person)
    substitute_id: str (FK to Person)
    status: enum (pending, approved, denied, cancelled)
    reason: str
    admin_notes: str
    created_at: datetime
    resolved_at: datetime
    resolved_by: str (FK to Person)
```

### API Endpoints

**Invitation APIs**
```
POST   /api/invitations              - Create invitation
GET    /api/invitations              - List invitations (admin)
GET    /api/invitations/{token}      - Verify invitation
POST   /api/invitations/{token}/accept - Accept invitation
DELETE /api/invitations/{id}         - Cancel invitation
POST   /api/invitations/{id}/resend  - Resend invitation
```

**ICS Export APIs**
```
GET    /api/calendar/export          - Export personal schedule (ICS)
GET    /api/calendar/subscribe       - Get webcal:// URL
POST   /api/calendar/reset-token     - Reset subscribe URL
GET    /api/calendar/org/export      - Export all org events (admin)
```

**Swap APIs**
```
POST   /api/swaps                    - Request swap/substitute
GET    /api/swaps                    - List swap requests
PUT    /api/swaps/{id}/approve       - Approve swap (admin)
PUT    /api/swaps/{id}/deny          - Deny swap (admin)
DELETE /api/swaps/{id}               - Cancel swap request
```

---

## UI/UX Improvements

### Admin Console - Tab Navigation
```
┌─────────────────────────────────────────────────────┐
│ Rostio - Admin Console                    [Profile] │
├─────────────────────────────────────────────────────┤
│ [Events] [Roles] [Schedule] [People] [Reports]      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Active Tab Content Here]                          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Invitation Flow
```
Admin → Invite Button → Modal:
  Email: ___________
  Name:  ___________
  Role:  [x] Volunteer [ ] Admin
  → Send Invitation

Email Template:
  Subject: You're invited to join [Org Name] on Rostio

  Hi [Name],

  [Admin Name] has invited you to join [Org Name]'s volunteer
  scheduling system.

  [Accept Invitation Button]

  This link expires in 7 days.
```

---

## Testing Requirements

### Unit Tests
- ✓ Invitation CRUD operations
- ✓ Invitation token generation and validation
- ✓ Invitation expiry logic
- ✓ ICS file generation
- ✓ ICS calendar URL generation
- ✓ Swap request workflows
- ✓ RBAC permission checks

### Integration Tests
- ✓ Complete invitation flow (send → accept → signup)
- ✓ ICS export with timezone handling
- ✓ Calendar subscription updates
- ✓ Swap request approval flow
- ✓ Admin tab navigation

### E2E GUI Tests
- ✓ Admin invites volunteer via UI
- ✓ Volunteer accepts invitation and signs up
- ✓ Volunteer exports calendar ICS
- ✓ Volunteer requests shift swap
- ✓ Admin approves swap request
- ✓ Tab navigation in admin console

---

## Implementation Priority

**Phase 1: RBAC & Invitations (High Priority)**
1. Database migrations for invitations
2. Invitation API endpoints
3. Admin UI for sending invitations
4. Email template system
5. Invitation acceptance flow
6. Tests for invitation system

**Phase 2: Admin Console Redesign (High Priority)**
1. Implement tab navigation
2. Reorganize existing features into tabs
3. Events tab enhancements
4. People tab with invitation status
5. Tests for new UI

**Phase 3: ICS Export (Medium Priority)**
1. Add icalendar library
2. Personal schedule export endpoint
3. Calendar subscription URL generation
4. Frontend export buttons
5. Tests for ICS generation

**Phase 4: Self-Service Features (Lower Priority)**
1. Swap request database schema
2. Swap request API endpoints
3. Frontend UI for swap requests
4. Admin approval workflow
5. Tests for swap system

---

## Success Metrics

- **Onboarding**: 80% of invitations accepted within 3 days
- **Engagement**: 60% of volunteers use calendar export
- **Admin Efficiency**: 50% reduction in manual scheduling time
- **User Satisfaction**: NPS score > 40
- **System Reliability**: 99.5% uptime, all tests passing
