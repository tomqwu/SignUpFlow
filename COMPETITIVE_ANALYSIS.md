# Competitive Analysis & Best Practices

## Research Date: 2025-10-01

## Industry Leaders Analyzed

**General Employee Scheduling:**
- Deputy (AI-powered, labor cost optimization)
- 7shifts (Restaurant-focused)
- When I Work (Ease of use, team communication)
- Connecteam
- Sling

**Church/Volunteer Scheduling:**
- Ministry Scheduler Pro
- Planning Center Services
- Church Crew
- ChurchScheduling.com
- Pushpay Church Scheduling

---

## Essential Features (Industry Standard)

### ✅ Features We Have

1. **Availability Tracking** - Backend API exists (`/availability` endpoints)
2. **Role-Based Scheduling** - Constraint system supports role matching
3. **Event Management** - Full CRUD for events
4. **Admin Dashboard** - Admin role with management interface
5. **Mobile-Friendly UI** - Responsive design
6. **Constraint-Based Scheduling** - Core solver with hard/soft constraints
7. **Schedule Export** - CSV/ICS export capability

### ⚠️ Features We Have (Partial Implementation)

8. **Automated Reminders** - Backend supports it, but no notification system
9. **Team Communication** - No in-app messaging
10. **Reporting & Analytics** - Basic stats in admin dashboard, needs expansion

### ❌ Missing Critical Features

### **HIGH PRIORITY (P0)**

11. **Shift Swap/Trade System**
   - Employees can't request to swap shifts with colleagues
   - No approval workflow for shift changes
   - **Impact:** Major pain point in all competitor products
   - **Implementation:** New endpoints for swap requests, approval workflow

12. **Shift Templates & Recurring Events**
   - Can't save recurring patterns (e.g., "every Sunday at 10am")
   - Have to manually create each event
   - **Impact:** Tedious for weekly church services
   - **Implementation:** Add recurrence rules to Event model (RFC 5545 RRULE)

13. **Auto-Scheduling with Fairness**
   - Current solver works but no fairness metrics visible to users
   - No "last scheduled date" tracking visible
   - **Impact:** Volunteers feel overworked or underutilized
   - **Implementation:** Surface fairness metrics, add "days since last assignment" to UI

14. **Real-Time Notifications**
   - No email/SMS when assigned to shift
   - No reminders before shift starts
   - **Impact:** People forget or miss assignments
   - **Implementation:** Email service integration (SendGrid/AWS SES), cron job for reminders

15. **Mobile App (Native or PWA)**
   - Current UI is mobile-responsive but not a PWA
   - No offline capability
   - No push notifications
   - **Impact:** Volunteers check schedules on phones
   - **Implementation:** Add PWA manifest, service worker, push notifications

### **MEDIUM PRIORITY (P1)**

16. **Time-Off Request Approval Workflow**
   - Current availability API just stores dates
   - No approval/rejection flow
   - No visibility for admins to approve requests
   - **Implementation:** Add approval_status to availability, admin UI for requests

17. **Conflict Detection & Alerts**
   - No warnings for double-booking
   - No alerts for overtime/fatigue
   - **Implementation:** Real-time validation, warning badges in UI

18. **Integration with Calendar Apps**
   - ICS export exists but not live sync
   - Can't subscribe to personal schedule
   - **Implementation:** Generate per-person ICS feed URLs, caldav support

19. **Shift Notes & Instructions**
   - Can't add notes like "bring equipment" or "arrive 15min early"
   - **Implementation:** Add notes field to assignments, display in schedule view

20. **Team/Department Hierarchies**
   - Current team model is flat
   - No sub-teams or complex org structures
   - **Implementation:** Add parent_team_id for hierarchy

### **NICE TO HAVE (P2)**

21. **AI-Powered Demand Forecasting**
   - Deputy uses sales data to predict staffing needs
   - We have no forecasting
   - **Implementation:** Analyze historical event attendance, suggest staffing levels

22. **Shift Marketplace**
   - Open shifts that anyone can claim
   - Gamification (points, leaderboard)
   - **Implementation:** New "open_shifts" view, claim button

23. **Skills/Certification Tracking**
   - Track who is trained for what
   - Ensure certified people are scheduled
   - **Implementation:** Add skills to Person model, validate in constraints

24. **Payroll Integration**
   - Export hours worked for payroll
   - Not critical for volunteer orgs
   - **Implementation:** Timesheet export API

25. **Advanced Reporting Dashboard**
   - Hours by person/team over time
   - Attendance rates
   - Fairness charts
   - **Implementation:** New `/reports` endpoints, chart.js visualizations

26. **Multi-Language Support**
   - i18n for global churches
   - **Implementation:** i18next or similar

---

## Church/Volunteer-Specific Best Practices

### **Burnout Prevention**
- **Best Practice:** Schedule volunteers every other week minimum, with goal of 1-2 times per month
- **Our Status:** Solver considers fairness but not visible, no "max frequency" constraint
- **Action:** Add max_shifts_per_month constraint type

### **Gift-Based Matching**
- **Best Practice:** Match volunteers to roles based on their gifts/preferences
- **Our Status:** Roles exist but no preference ranking
- **Action:** Add role_preferences (ranked list) to Person model

### **Pre-Service Requirements**
- **Best Practice:** Ensure volunteers completed background checks, training before scheduling
- **Our Status:** No certification tracking
- **Action:** Add requirements to roles, validation before assignment

### **Appreciation & Recognition**
- **Best Practice:** Send thank-you messages, track volunteer hours for recognition
- **Our Status:** No communication system, no hours tracking
- **Action:** Add total_hours_served metric, automated thank-you emails

---

## Feature Gaps Summary

| Category | We Have | Missing |
|----------|---------|---------|
| **Scheduling** | Manual event creation, constraint solver | Shift swaps, recurring events, templates, auto-fill |
| **Communication** | None | In-app messaging, email/SMS notifications, reminders |
| **Availability** | Backend API | Approval workflow, conflict detection |
| **Mobile** | Responsive web | PWA, push notifications, offline mode |
| **Analytics** | Basic stats | Advanced reporting, fairness charts, forecasting |
| **Volunteer Management** | Roles, teams | Skills tracking, certifications, preferences |
| **Export** | CSV/ICS one-time | Live calendar sync, caldav feeds |

---

## Recommended Implementation Phases

### **Phase 1: Critical Fixes (Week 1-2)**
1. Fix solver to generate assignments (currently 0 assignments)
2. Add recurring events (RRULE support)
3. Add shift swap requests with approval
4. Add email notifications (assigned, reminder, confirmation)
5. Surface fairness metrics in UI

### **Phase 2: Core Enhancements (Week 3-4)**
1. Time-off approval workflow
2. Conflict detection & warnings
3. Shift templates
4. Personal calendar feed (live ICS URL)
5. Shift notes/instructions

### **Phase 3: Advanced Features (Week 5-6)**
1. Convert to PWA with push notifications
2. Skills/certification tracking
3. Advanced reporting dashboard
4. In-app team communication
5. Shift marketplace (open shifts)

### **Phase 4: Polish (Week 7-8)**
1. AI demand forecasting
2. Multi-language support
3. Payroll integration
4. Mobile native apps (optional)

---

## Testing Requirements

Based on best practices, EVERY feature above needs:
- **Unit tests** - Test individual functions/endpoints
- **Integration tests** - Test workflows (create event → assign people → export)
- **GUI tests** - Test UI interactions
- **E2E tests** - Test complete user journeys
- **Load tests** - Test with realistic data (100+ people, 1000+ events)
- **Accessibility tests** - WCAG 2.1 AA compliance
- **Mobile tests** - Test on iOS/Android browsers

Current testing coverage: **~25%** (32 tests out of 130+ planned)
