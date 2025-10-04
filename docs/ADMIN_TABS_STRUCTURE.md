# Admin Console Tab Structure

## Visual Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Rostio - Admin Console                                    [Profile]│
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────┬───────┬──────────┬────────┬─────────┐                  │
│  │Events │ Roles │ Schedule │ People │ Reports │                  │
│  └───────┴───────┴──────────┴────────┴─────────┘                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                                                              │  │
│  │                     [Active Tab Content]                     │  │
│  │                                                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Tab 1: Events

**Purpose:** Manage all organization events

```
┌─────────────────────────────────────────────────┐
│ Event Management                  [+ Create] [🔄]│
├─────────────────────────────────────────────────┤
│                                                  │
│ Total Events: 12                                │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Sunday Service                              ││
│ │ 📅 Oct 6, 2025 10:00 AM                     ││
│ │ 📋 Needs: volunteer (2), musician (1)       ││
│ │                                              ││
│ │ [Assign People] [Edit] [Delete]             ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Bible Study                                 ││
│ │ 📅 Oct 7, 2025 7:00 PM                      ││
│ │ 📋 Needs: leader (1)                        ││
│ │                                              ││
│ │ [Assign People] [Edit] [Delete]             ││
│ └─────────────────────────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ Event creation with recurrence patterns
- ✅ Role requirements per event
- ✅ Assignment management
- ✅ Edit/delete capabilities
- ✅ Event statistics

---

## Tab 2: Roles

**Purpose:** Define and manage volunteer roles

```
┌─────────────────────────────────────────────────┐
│ Role Management                       [+ Add Role]│
├─────────────────────────────────────────────────┤
│                                                  │
│ Define custom roles for your organization       │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ 🔵 Volunteer                                ││
│ │ General volunteer role                       ││
│ │ 5 people have this role                      ││
│ │                                    [Delete]  ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ 🟡 Admin                                    ││
│ │ Administrator with full access               ││
│ │ 2 people have this role                      ││
│ │                                    [Delete]  ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ 🟣 Leader                                   ││
│ │ Team coordinator role                        ││
│ │ 3 people have this role                      ││
│ │                                    [Delete]  ││
│ └─────────────────────────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ CRUD operations for roles
- ✅ Role descriptions
- ✅ **NEW:** Visual color indicators
- ✅ **NEW:** Assignment statistics (people count)
- ✅ Custom role creation

**Role Colors:**
- 🔵 Volunteer: #3b82f6 (Blue)
- 🟡 Admin: #f59e0b (Amber)
- 🟣 Leader: #8b5cf6 (Purple)
- 🌸 Musician: #ec4899 (Pink)
- 🟢 Tech: #10b981 (Green)
- 🟠 Childcare: #f97316 (Orange)
- 🔷 Hospitality: #06b6d4 (Cyan)

---

## Tab 3: Schedule

**Purpose:** Generate and view schedules

```
┌─────────────────────────────────────────────────┐
│ Schedule Generation                              │
├─────────────────────────────────────────────────┤
│                                                  │
│        [🔄 Generate Schedule]                   │
│                                                  │
│ This will create assignments for all upcoming   │
│ events                                           │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ ✓ Schedule generated successfully!          ││
│ │ Solution ID: 123                             ││
│ │ Assignments: 45                              ││
│ │ Health Score: 87.5/100                       ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ─────────────────────────────────────────────── │
│                                                  │
│ Schedule Calendar                                │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Sunday, October 6, 2025                     ││
│ │                                              ││
│ │ ┌─────────────────────────────────────────┐││
│ │ │ 10:00 AM                                 │││
│ │ │ Sunday Service                           │││
│ │ │ John Doe                                 │││
│ │ └─────────────────────────────────────────┘││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ─────────────────────────────────────────────── │
│                                                  │
│ Generated Schedules                              │
│                                                  │
│ Total Schedules: 3                               │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Schedule 123                                ││
│ │ Created: Oct 4, 2025 2:30 PM                ││
│ │ Health Score: 87.5/100                       ││
│ │ Assignments: 45                              ││
│ │                            [View] [Delete]   ││
│ └─────────────────────────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ Schedule generation with conflict detection
- ✅ **NEW:** Admin calendar view (next 10 days)
- ✅ Generated schedules list
- ✅ Health score and metrics
- ✅ View/export/delete schedules

---

## Tab 4: People

**Purpose:** Manage team members and invitations

```
┌─────────────────────────────────────────────────┐
│ People & Invitations              [+ Invite User]│
├─────────────────────────────────────────────────┤
│                                                  │
│ Total People: 10                                 │
│                                                  │
│ ─────────────────────────────────────────────── │
│                                                  │
│ Invitation Status                                │
│                                                  │
│ ┌─────────┬─────────┬─────────┐                │
│ │    3    │    5    │    1    │                │
│ │ Pending │Accepted │ Expired │                │
│ └─────────┴─────────┴─────────┘                │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ John Smith                                  ││
│ │ john@example.com • Roles: volunteer         ││
│ │ Sent: Oct 1, 2025 • Expires: Oct 8, 2025    ││
│ │                                              ││
│ │ [pending] [Resend] [Cancel]                 ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Jane Doe                                    ││
│ │ jane@example.com • Roles: admin, volunteer  ││
│ │ Sent: Sep 28, 2025                           ││
│ │                                              ││
│ │ [accepted]                                   ││
│ └─────────────────────────────────────────────┘│
│                                                  │
│ ─────────────────────────────────────────────── │
│                                                  │
│ Team Members                                     │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ Alice Johnson                               ││
│ │ alice@example.com                            ││
│ │ Roles: volunteer, musician                   ││
│ │ Blocked Dates: Oct 15-17, Nov 1-3            ││
│ └─────────────────────────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ **NEW:** Invitation Status Dashboard
  - Pending/Accepted/Expired counts
  - Invitation list with actions
  - Resend/Cancel capabilities
- ✅ **NEW:** Invite User modal
- ✅ Team members list
- ✅ Availability/blocked dates display
- ✅ Role assignments

**Invite User Modal:**
```
┌────────────────────────────────┐
│ Invite User                [×] │
├────────────────────────────────┤
│                                │
│ Email Address:                 │
│ [_____________________]        │
│                                │
│ Full Name:                     │
│ [_____________________]        │
│                                │
│ Assign Roles:                  │
│ ☑ Volunteer  ☐ Admin           │
│                                │
│         [Cancel] [Send]        │
└────────────────────────────────┘
```

---

## Tab 5: Reports

**Purpose:** Export schedules and view statistics

```
┌─────────────────────────────────────────────────┐
│ Reports & Export                                 │
├─────────────────────────────────────────────────┤
│                                                  │
│ Export schedules and generate reports            │
│                                                  │
│ ┌──────────────┬──────────────┬──────────────┐ │
│ │              │              │              │ │
│ │  PDF Export  │  ICS Export  │  Statistics  │ │
│ │              │              │              │ │
│ │ Download a   │ Export all   │ View assign- │ │
│ │ printable    │ organization │ ment distri- │ │
│ │ schedule     │ events to    │ bution and   │ │
│ │              │ calendar     │ metrics      │ │
│ │              │              │              │ │
│ │ [📥 Export]  │ [📅 Export]  │ [📊 View]    │ │
│ │              │              │              │ │
│ └──────────────┴──────────────┴──────────────┘ │
│                                                  │
│ ─────────────────────────────────────────────── │
│                                                  │
│ Schedule Statistics                              │
│                                                  │
│ ┌─────────┬─────────┬─────────┬─────────┐      │
│ │   45    │   10    │   12    │   4.5   │      │
│ │ Assign- │ People  │ Events  │   Avg   │      │
│ │  ments  │Assigned │ Covered │ per P.  │      │
│ └─────────┴─────────┴─────────┴─────────┘      │
│                                                  │
│ Top 10 Most Assigned People                      │
│                                                  │
│ ┌─────────────────────────────────────────────┐│
│ │ 1. Alice Johnson         8 assignments      ││
│ │ 2. Bob Smith             7 assignments      ││
│ │ 3. Carol White           6 assignments      ││
│ │ 4. David Brown           5 assignments      ││
│ │ 5. Eve Davis             5 assignments      ││
│ │ ...                                          ││
│ └─────────────────────────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ **NEW:** PDF Schedule Export
- ✅ **NEW:** Calendar Export (ICS format)
- ✅ **NEW:** Schedule Statistics with metrics:
  - Total assignments
  - People assigned count
  - Events covered
  - Average assignments per person
  - Top 10 most assigned people
- ✅ Card-based report layout

---

## Navigation Flow

```
User Flow:
1. Login with admin role
2. Click "Admin Dashboard" in main navigation
3. See "Events" tab by default
4. Click any tab to switch views
5. URL updates: localhost:8080/#admin-{tab}
6. Refresh page → Last tab restored
7. Bookmark URL → Direct tab access

State Management:
- Current tab saved to localStorage
- URL hash reflects active tab
- Tab state persists across sessions
- Independent content loading per tab
```

---

## Technical Architecture

### HTML Structure
```
<div id="admin-view">
  <div class="admin-tabs">
    <button class="admin-tab-btn" data-tab="events">Events</button>
    <button class="admin-tab-btn" data-tab="roles">Roles</button>
    <button class="admin-tab-btn" data-tab="schedule">Schedule</button>
    <button class="admin-tab-btn" data-tab="people">People</button>
    <button class="admin-tab-btn" data-tab="reports">Reports</button>
  </div>

  <div class="admin-dashboard">
    <div id="admin-tab-events" class="admin-tab-content active">
      <!-- Events content -->
    </div>
    <div id="admin-tab-roles" class="admin-tab-content">
      <!-- Roles content -->
    </div>
    <div id="admin-tab-schedule" class="admin-tab-content">
      <!-- Schedule content -->
    </div>
    <div id="admin-tab-people" class="admin-tab-content">
      <!-- People content -->
    </div>
    <div id="admin-tab-reports" class="admin-tab-content">
      <!-- Reports content -->
    </div>
  </div>
</div>
```

### JavaScript Logic
```javascript
function switchAdminTab(tabName) {
  // 1. Update URL hash
  window.location.hash = `admin-${tabName}`;

  // 2. Save to localStorage
  localStorage.setItem('roster_admin_tab', tabName);

  // 3. Update button states
  document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });

  // 4. Show/hide content
  document.querySelectorAll('.admin-tab-content').forEach(content => {
    content.classList.remove('active');
  });
  document.getElementById(`admin-tab-${tabName}`).classList.add('active');

  // 5. Load data
  loadTabData(tabName);
}
```

### CSS Styling
```css
.admin-tabs {
  display: flex;
  gap: 5px;
  padding: 0 30px;
  border-bottom: 2px solid var(--border);
}

.admin-tab-btn {
  padding: 14px 28px;
  border: none;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.admin-tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
  background: white;
}

.admin-tab-content {
  display: none;
  animation: fadeIn 0.3s;
}

.admin-tab-content.active {
  display: block;
}
```

---

## Key Benefits

### Organization
- ✅ Logical grouping of admin features
- ✅ Clear separation of concerns
- ✅ Easy navigation between functions

### Usability
- ✅ Bookmarkable tabs via URL hash
- ✅ State persistence across sessions
- ✅ Smooth animations and transitions
- ✅ Responsive design

### Scalability
- ✅ Easy to add new tabs
- ✅ Modular code structure
- ✅ Independent tab loading
- ✅ Clean API integration points

### Performance
- ✅ Lazy loading of tab content
- ✅ Efficient DOM manipulation
- ✅ Minimal re-renders
- ✅ Optimized API calls

---

## Future Enhancements

### Phase 1: Backend Integration
- [ ] Implement `/api/invitations` endpoints
- [ ] Email notification system
- [ ] Invitation token validation

### Phase 2: Advanced Features
- [ ] Calendar subscription (webcal://)
- [ ] Live schedule updates
- [ ] Role-based tab visibility

### Phase 3: Analytics
- [ ] Advanced reporting dashboard
- [ ] Exportable metrics
- [ ] Custom report builder

---

This tabbed structure provides a modern, efficient, and user-friendly admin experience that scales with the organization's needs.
