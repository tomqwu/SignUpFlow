# RBAC Audit & Best Practices Analysis

**Date:** 2025-10-13
**Status:** 🟡 NEEDS IMPROVEMENT

---

## 📊 Current RBAC Implementation

### Current Roles
From code analysis, Rostio currently supports:
- `admin` - Full access
- `super_admin` - Full access (treated same as admin)
- Other roles (volunteer, leader, musician, etc.) - **NO special permissions**

### Current Permission Checks

**Location:** `api/dependencies.py`

```python
def check_admin_permission(person: Person) -> bool:
    """Check if person has admin or super_admin role."""
    return "admin" in person.roles or "super_admin" in person.roles
```

**Problem:** Only 2 levels - admin or not admin. No middle tier.

---

## 🔍 Current Permissions by Feature

### ✅ What's Protected (Admin-only)

| Feature | Endpoint | Permission Check |
|---------|----------|------------------|
| **Invitations** | POST /api/invitations | ✅ `get_current_admin_user` |
| **Invitations** | GET /api/invitations | ✅ `get_current_admin_user` |
| **Invitations** | DELETE /api/invitations/{id} | ✅ `verify_admin_access` |
| **Invitations** | POST /api/invitations/{id}/resend | ✅ `verify_admin_access` |
| **Calendar (Org)** | GET /api/calendar/org/export | ✅ Admin check in code |

### ⚠️ What's NOT Protected (Anyone can access)

| Feature | Endpoint | Issue |
|---------|----------|-------|
| **Events** | POST /api/events | ❌ No admin check |
| **Events** | PUT /api/events/{id} | ❌ No admin check |
| **Events** | DELETE /api/events/{id} | ❌ No admin check |
| **Schedules** | POST /api/schedules/generate | ❌ No admin check |
| **People** | GET /api/people (all) | ❌ No admin check |
| **People** | PUT /api/people/{id} | ⚠️ Can edit anyone |
| **People** | DELETE /api/people/{id} | ❌ No admin check |
| **Teams** | POST /api/teams | ❌ No admin check |
| **Teams** | DELETE /api/teams/{id} | ❌ No admin check |
| **Organizations** | PUT /api/organizations/{id} | ❌ No admin check |

---

## 🏢 Industry Best Practices

### Typical RBAC Hierarchy

```
SUPER_ADMIN (System level)
└─ Full system access
   └─ Manage organizations
   └─ System configuration

ADMIN (Organization level)
└─ Full org access
   └─ Manage users & roles
   └─ Create/edit/delete events
   └─ Generate schedules
   └─ View all data
   └─ Export reports
   └─ Organization settings

MANAGER (Department/Team level)
└─ Limited admin access
   └─ View all data (read-only org level)
   └─ Create/edit events (own team)
   └─ Assign volunteers (own team)
   └─ View reports (own team)
   └─ Cannot delete or manage users

VOLUNTEER (User level)
└─ Self-service only
   └─ View own schedule
   └─ Set availability
   └─ Request time-off
   └─ Update own profile
   └─ Export own calendar
   └─ Cannot see others' data

VIEWER (Read-only)
└─ Limited visibility
   └─ View public schedules
   └─ View event calendar
   └─ Cannot edit anything
```

---

## 🎯 Recommended RBAC Structure for Rostio

### Proposed Roles

#### 1. **SUPER_ADMIN** (Platform Owner)
**Use Case:** SaaS platform administrator

**Permissions:**
- ✅ Manage all organizations
- ✅ View all data across orgs
- ✅ System configuration
- ✅ Billing & subscriptions
- ✅ User impersonation (support)
- ⚠️ **Should NOT be assigned to regular users**

#### 2. **ADMIN** (Organization Owner)
**Use Case:** Church pastor, non-profit director

**Permissions:**
- ✅ Full org access
- ✅ **User Management:**
  - Invite/remove users
  - Assign/revoke roles
  - View all users
- ✅ **Event Management:**
  - Create/edit/delete events
  - Set event requirements
  - Manage recurring events
- ✅ **Schedule Management:**
  - Generate schedules (AI)
  - Manually edit assignments
  - Approve/reject changes
- ✅ **Team Management:**
  - Create/delete teams
  - Assign team leaders
- ✅ **Organization Settings:**
  - Update org profile
  - Configure preferences
  - Manage custom roles
- ✅ **Reports & Analytics:**
  - Export all data
  - View statistics
  - Download PDF/ICS
- ❌ Cannot access other organizations
- ❌ Cannot modify billing (handled by super_admin)

#### 3. **MANAGER** (Team Leader)
**Use Case:** Worship leader, youth pastor, department head

**Permissions:**
- ✅ **View Access:**
  - View all events (read-only)
  - View all schedules (read-only)
  - View all volunteers (read-only)
- ✅ **Limited Management:**
  - Create/edit events (requires admin approval)
  - Suggest assignments (requires admin approval)
  - View team statistics
- ✅ **Team Specific:**
  - Full access to assigned team(s)
  - Assign volunteers to own team
  - View team availability
- ❌ Cannot create/delete users
- ❌ Cannot generate final schedules
- ❌ Cannot modify org settings
- ❌ Cannot delete events/assignments

**Example:**
```
Worship Leader (Manager role):
- Can create Sunday service events
- Can suggest musicians for worship team
- Can view who's available
- Cannot approve final schedule (admin does)
- Cannot delete volunteers
```

#### 4. **VOLUNTEER** (Standard User)
**Use Case:** Church member, volunteer

**Permissions:**
- ✅ **Self-Service:**
  - View own schedule
  - Set availability (dates available)
  - Request time-off (blocked dates)
  - Update own profile
  - Change password
  - Set timezone/language
- ✅ **Calendar:**
  - Export own schedule (ICS)
  - Subscribe to calendar (webcal)
- ✅ **Limited View:**
  - View public events
  - View event details
  - See event requirements
- ❌ Cannot view others' schedules
- ❌ Cannot view full volunteer list
- ❌ Cannot create events
- ❌ Cannot assign themselves

#### 5. **VIEWER** (Read-Only)
**Use Case:** Congregation member, guest

**Permissions:**
- ✅ **View Only:**
  - View public event calendar
  - View event times/locations
- ❌ Cannot see volunteer assignments
- ❌ Cannot see availability
- ❌ Cannot edit anything
- ⚠️ **Optional role** - may not be needed for MVP

---

## 🚨 Current Security Issues

### Critical Issues (P0)

#### 1. **Anyone Can Create/Delete Events**
**Issue:** No permission check on event endpoints
**Impact:** Volunteer can delete all events
**Fix:** Add `Depends(get_current_admin_user)` to endpoints

```python
# CURRENT (BAD):
@app.post("/api/events")
async def create_event(data: EventCreate, db: Session = Depends(get_db)):
    # Anyone can create events!

# SHOULD BE:
@app.post("/api/events")
async def create_event(
    data: EventCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # Only admins can create events
```

#### 2. **Anyone Can Edit Any User**
**Issue:** No permission check on people update
**Impact:** Volunteer can make themselves admin
**Fix:** Check if current_user == person_id OR is_admin

```python
# CURRENT (BAD):
@app.put("/api/people/{person_id}")
async def update_person(person_id: str, data: PersonUpdate, db: Session = Depends(get_db)):
    # Anyone can edit anyone!

# SHOULD BE:
@app.put("/api/people/{person_id}")
async def update_person(
    person_id: str,
    data: PersonUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check permission
    if current_user.id != person_id and not check_admin_permission(current_user):
        raise HTTPException(403, "Can only edit your own profile")
```

#### 3. **Anyone Can Generate Schedules**
**Issue:** Schedule generation not protected
**Impact:** Could trigger expensive AI operations
**Fix:** Admin-only

#### 4. **No Organization Isolation**
**Issue:** Users can access data from other orgs
**Impact:** Data leak between organizations
**Fix:** Check `current_user.org_id == resource.org_id`

---

## ✅ Recommended Implementation Plan

### Phase 1: Fix Critical Security Issues (Week 1) - **URGENT**

**Priority P0 - Security Vulnerabilities:**

1. **Protect Event Management**
   ```python
   # api/routers/events.py
   @app.post("/api/events")
   async def create_event(
       data: EventCreate,
       current_admin: Person = Depends(get_current_admin_user),
       db: Session = Depends(get_db)
   ):
       # Verify org membership
       verify_org_member(current_admin, data.org_id)
       # Create event
   ```

2. **Protect People Management**
   ```python
   @app.put("/api/people/{person_id}")
   async def update_person(
       person_id: str,
       data: PersonUpdate,
       current_user: Person = Depends(get_current_user),
       db: Session = Depends(get_db)
   ):
       # Allow: edit self OR admin edits anyone in same org
       person = get_person_by_id(person_id, db)

       if current_user.id != person_id:
           if not check_admin_permission(current_user):
               raise HTTPException(403, "Can only edit your own profile")
           verify_org_member(current_user, person.org_id)

       # Prevent role escalation (volunteer can't make self admin)
       if "roles" in data and current_user.id == person_id:
           if not check_admin_permission(current_user):
               raise HTTPException(403, "Cannot modify your own roles")

       # Update person
   ```

3. **Protect Schedule Generation**
   ```python
   @app.post("/api/schedules/generate")
   async def generate_schedule(
       data: ScheduleRequest,
       current_admin: Person = Depends(get_current_admin_user),
       db: Session = Depends(get_db)
   ):
       # Only admins can generate schedules
   ```

4. **Protect Team Management**
   ```python
   @app.post("/api/teams")
   async def create_team(
       data: TeamCreate,
       current_admin: Person = Depends(get_current_admin_user),
       db: Session = Depends(get_db)
   ):
       # Only admins can create teams
   ```

5. **Protect Organization Settings**
   ```python
   @app.put("/api/organizations/{org_id}")
   async def update_organization(
       org_id: str,
       data: OrgUpdate,
       current_admin: Person = Depends(get_current_admin_user),
       db: Session = Depends(get_db)
   ):
       verify_org_member(current_admin, org_id)
       # Update org
   ```

### Phase 2: Add Manager Role (Week 2)

1. **Create role check helpers:**
   ```python
   # api/dependencies.py

   def check_manager_permission(person: Person) -> bool:
       """Check if person has manager, admin, or super_admin role."""
       if not person or not person.roles:
           return False
       return any(role in person.roles for role in ["manager", "admin", "super_admin"])

   async def get_current_manager_user(
       current_user: Person = Depends(get_current_user)
   ) -> Person:
       """Get current user and verify they have manager+ permissions."""
       if not check_manager_permission(current_user):
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Manager access required"
           )
       return current_user
   ```

2. **Allow managers to view all data (read-only):**
   ```python
   @app.get("/api/people")
   async def list_people(
       current_manager: Person = Depends(get_current_manager_user),  # Changed from get_current_user
       db: Session = Depends(get_db)
   ):
       # Managers can view all people in their org
       people = db.query(Person).filter_by(org_id=current_manager.org_id).all()
       return people
   ```

3. **Allow managers to create events (with restrictions):**
   ```python
   @app.post("/api/events")
   async def create_event(
       data: EventCreate,
       current_manager: Person = Depends(get_current_manager_user),  # Changed from admin-only
       db: Session = Depends(get_db)
   ):
       # Managers can create events, but mark as pending approval
       if not check_admin_permission(current_manager):
           data.status = "pending_approval"
       # Create event
   ```

### Phase 3: Add Fine-Grained Permissions (Week 3)

1. **Implement resource ownership:**
   ```python
   # Volunteers can only view their own data
   @app.get("/api/availability/{person_id}")
   async def get_availability(
       person_id: str,
       current_user: Person = Depends(get_current_user),
       db: Session = Depends(get_db)
   ):
       # Check permission: view self OR is manager/admin
       if current_user.id != person_id:
           if not check_manager_permission(current_user):
               raise HTTPException(403, "Can only view your own availability")

       # Return availability
   ```

2. **Implement org isolation:**
   ```python
   def verify_same_org(current_user: Person, resource_org_id: str):
       """Verify current user and resource are in same org."""
       if current_user.org_id != resource_org_id:
           raise HTTPException(403, "Access denied: resource in different organization")
   ```

---

## 📋 Permission Matrix (Recommended)

| Feature | Super Admin | Admin | Manager | Volunteer | Viewer |
|---------|-------------|-------|---------|-----------|--------|
| **Users** |
| View all users | ✅ | ✅ | ✅ (read-only) | ❌ | ❌ |
| Invite users | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit users | ✅ | ✅ | ❌ | ❌ (self only) | ❌ |
| Delete users | ✅ | ✅ | ❌ | ❌ | ❌ |
| Assign roles | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Events** |
| View events | ✅ | ✅ | ✅ | ✅ (public) | ✅ (public) |
| Create events | ✅ | ✅ | ✅ (pending) | ❌ | ❌ |
| Edit events | ✅ | ✅ | ✅ (own, pending) | ❌ | ❌ |
| Delete events | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Schedules** |
| View schedules | ✅ | ✅ | ✅ | ✅ (own) | ❌ |
| Generate schedules | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit assignments | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Availability** |
| Set own availability | ✅ | ✅ | ✅ | ✅ | ❌ |
| View others' availability | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Teams** |
| View teams | ✅ | ✅ | ✅ | ✅ (own) | ❌ |
| Create teams | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit teams | ✅ | ✅ | ✅ (assigned) | ❌ | ❌ |
| Delete teams | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Organization** |
| View org settings | ✅ | ✅ | ✅ (read-only) | ❌ | ❌ |
| Edit org settings | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Reports** |
| Export all data | ✅ | ✅ | ✅ (own team) | ✅ (own) | ❌ |
| View statistics | ✅ | ✅ | ✅ (own team) | ✅ (own) | ❌ |

---

## 🧪 Testing RBAC

### Current Test Coverage

**Existing Tests:**
- ✅ `tests/security/test_authentication.py` - JWT auth tests
- ✅ `tests/unit/test_dependencies.py` - Permission check tests
- ⚠️ Missing: Comprehensive RBAC tests per endpoint

### Recommended Tests

```python
# tests/security/test_rbac.py

def test_volunteer_cannot_create_events():
    """Volunteers should not be able to create events."""
    volunteer_token = login_as_volunteer()
    response = client.post(
        "/api/events",
        headers={"Authorization": f"Bearer {volunteer_token}"},
        json={"name": "Test Event", ...}
    )
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

def test_admin_can_create_events():
    """Admins should be able to create events."""
    admin_token = login_as_admin()
    response = client.post(
        "/api/events",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Test Event", ...}
    )
    assert response.status_code == 200

def test_volunteer_cannot_edit_other_users():
    """Volunteers can only edit their own profile."""
    volunteer_token = login_as("volunteer@test.com")
    response = client.put(
        "/api/people/admin@test.com",
        headers={"Authorization": f"Bearer {volunteer_token}"},
        json={"name": "Hacked Admin"}
    )
    assert response.status_code == 403

def test_volunteer_cannot_escalate_roles():
    """Volunteers cannot make themselves admin."""
    volunteer_token = login_as("volunteer@test.com")
    response = client.put(
        "/api/people/volunteer@test.com",
        headers={"Authorization": f"Bearer {volunteer_token}"},
        json={"roles": ["admin"]}
    )
    assert response.status_code == 403
    assert "Cannot modify your own roles" in response.json()["detail"]

def test_org_isolation():
    """Users cannot access data from other organizations."""
    org1_admin_token = login_as("admin@org1.com")
    org2_event = create_event_in_org2()

    response = client.get(
        f"/api/events/{org2_event.id}",
        headers={"Authorization": f"Bearer {org1_admin_token}"}
    )
    assert response.status_code == 403
    assert "different organization" in response.json()["detail"]
```

---

## 📝 Summary & Recommendations

### Current State: 🔴 VULNERABLE

**Critical Issues:**
- ❌ No permission checks on most endpoints
- ❌ Anyone can create/delete events
- ❌ Anyone can edit any user
- ❌ Anyone can generate schedules
- ❌ No organization isolation
- ❌ No role escalation prevention

### Recommended Action Plan

**Week 1 (URGENT):**
1. Add admin checks to all sensitive endpoints
2. Implement "can only edit self" checks
3. Prevent role escalation
4. Add organization isolation checks
5. Write comprehensive RBAC tests

**Week 2 (HIGH):**
1. Implement Manager role
2. Add read-only access for managers
3. Allow managers to create events (pending approval)

**Week 3 (MEDIUM):**
1. Add fine-grained permissions
2. Implement resource ownership checks
3. Add permission matrix UI (show what user can do)

**Estimated Effort:** 2-3 weeks (should be done BEFORE SaaS launch)

---

## 🎯 Next Steps

1. **Review this document** with stakeholders
2. **Prioritize fixes** - Recommend starting with Week 1 (security issues)
3. **Create GitHub issues** for each fix
4. **Write tests first** (TDD approach)
5. **Implement fixes** systematically
6. **Update API documentation** with permission requirements

**This is a SECURITY ISSUE and should be addressed before production launch.**
