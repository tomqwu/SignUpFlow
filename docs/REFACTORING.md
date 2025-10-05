# Refactoring Documentation

## Overview

This document outlines the refactoring work completed to improve code quality, reduce duplication, and enhance maintainability across the Rostio codebase.

## Date

2025-10-05

## Summary

Successfully refactored the authentication and authorization code by:
- Extracting common patterns into reusable utilities
- Creating centralized dependency injection functions
- Consolidating duplicate database query patterns
- Improving code organization and reducing technical debt

## Changes Made

### 1. Created Shared Dependencies ([api/dependencies.py](../api/dependencies.py))

**Purpose:** Centralize authentication and authorization logic

**Functions Added:**
- `check_admin_permission(person: Person) -> bool` - Check if user has admin role
- `get_person_by_id(person_id, db) -> Person` - Get person or raise 404
- `get_organization_by_id(org_id, db) -> Organization` - Get organization or raise 404
- `verify_admin_access(person_id, db) -> Person` - Verify admin permissions (dependency)
- `verify_org_member(person, org_id)` - Verify organization membership

**Benefits:**
- Eliminates duplicate permission checking code across routers
- Provides consistent error handling
- FastAPI dependency injection for cleaner endpoint signatures

### 2. Created Security Utilities ([api/utils/security.py](../api/utils/security.py))

**Purpose:** Centralize token generation and password hashing

**Functions Added:**
- `generate_token(length: int = 32) -> str` - Generic secure token generator
- `generate_invitation_token() -> str` - Invitation-specific token
- `generate_auth_token() -> str` - Authentication token
- `generate_calendar_token() -> str` - Calendar subscription token
- `hash_password(password: str) -> str` - Hash password with SHA-256
- `verify_password(plain_password, hashed_password) -> bool` - Verify password

**Benefits:**
- Eliminates duplicate token/hash generation code
- Centralized security logic for easier auditing
- Consistent token generation across the application

### 3. Created Database Helpers ([api/utils/db_helpers.py](../api/utils/db_helpers.py))

**Purpose:** Consolidate common database query patterns

**Functions Added:**
- `get_person_with_org_check(db, person_id, org_id)` - Get person with org verification
- `check_email_exists(db, email, org_id) -> bool` - Check email existence
- `get_team_members(db, team_id) -> List[Person]` - Get team members
- `get_person_assignments(db, person_id, start_date, end_date)` - Get assignments with date filtering
- `is_person_blocked_on_date(db, person_id, date)` - Check if person is blocked
- `get_event_assignments(db, event_id)` - Get event assignments
- `get_organization_events(db, org_id, ...)` - Get org events with filters
- `get_available_people_for_event(db, event, role_filter)` - Get available people

**Benefits:**
- Reduces code duplication across routers
- Provides consistent query patterns
- Makes complex queries reusable and testable

### 4. Refactored Routers

#### Invitations Router ([api/routers/invitations.py](../api/routers/invitations.py))

**Before:**
- 427 lines with duplicate helper functions
- Inline permission checks and database queries
- Repeated token generation code

**After:**
- Uses `verify_admin_access` dependency
- Uses `verify_org_member` for organization checks
- Imports security utilities for tokens and hashing
- Imports db helpers for email checking
- Cleaner, more maintainable code

**Example Improvement:**
```python
# Before (15 lines)
def create_invitation(..., invited_by_id: str = Query(...), ...):
    inviter = db.query(Person).filter(Person.id == invited_by_id).first()
    if not inviter:
        raise HTTPException(status_code=404, detail="Inviter not found")

    if not check_admin_permission(inviter):
        raise HTTPException(status_code=403, detail="Only admins...")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if inviter.org_id != org_id:
        raise HTTPException(status_code=403, detail="Cannot invite...")

# After (3 lines)
def create_invitation(..., inviter: Person = Depends(verify_admin_access), ...):
    org = get_organization_by_id(org_id, db)
    verify_org_member(inviter, org_id)
```

#### Auth Router ([api/routers/auth.py](../api/routers/auth.py))

**Before:**
- 153 lines with duplicate hash/token functions
- Inline organization validation

**After:**
- Uses security utilities for hashing and token generation
- Uses `get_organization_by_id` dependency
- Removed duplicate helper functions (15 lines eliminated)

#### Calendar Utils ([api/utils/calendar_utils.py](../api/utils/calendar_utils.py))

**Before:**
- Own token generation function

**After:**
- Imports `generate_calendar_token` from security utilities
- Consistent token generation across app

## Metrics

### Code Reduction
- **Duplicate functions eliminated:** ~50 lines
- **Boilerplate code reduced:** ~100+ lines across routers
- **New reusable utilities:** 3 new modules with 20+ functions

### Files Modified
- ✅ Created: `api/dependencies.py`
- ✅ Created: `api/utils/security.py`
- ✅ Created: `api/utils/db_helpers.py`
- ✅ Modified: `api/routers/invitations.py`
- ✅ Modified: `api/routers/auth.py`
- ✅ Modified: `api/utils/calendar_utils.py`

### Testing
- ✅ Import validation successful
- ✅ Security utilities tested and working
- ✅ Password hashing/verification functional
- ✅ Token generation functional

## Benefits Achieved

### 1. **Reduced Code Duplication**
   - Authentication logic centralized
   - Token generation consolidated
   - Database queries reusable

### 2. **Improved Maintainability**
   - Changes to auth logic only need updates in one place
   - Easier to add new security features
   - Consistent patterns across codebase

### 3. **Better Testability**
   - Utility functions can be unit tested independently
   - Mock dependencies easier in tests
   - Isolated business logic

### 4. **Enhanced Security**
   - Centralized security functions easier to audit
   - Consistent security patterns
   - Single source of truth for authentication

### 5. **Cleaner API Endpoints**
   - Less boilerplate code in routes
   - FastAPI dependency injection utilized properly
   - More readable endpoint functions

## Next Steps (Future Improvements)

### Immediate Opportunities
1. **Refactor Events Router** - Apply same patterns to events.py (365 lines)
2. **Refactor Solutions Router** - Apply patterns to solutions.py (306 lines)
3. **Refactor Solver Router** - Consolidate solver logic (221 lines)

### Medium-term Improvements
1. **Replace SHA-256 with bcrypt/argon2** - More secure password hashing
2. **Add JWT tokens** - Replace simple tokens with JWT for stateless auth
3. **Create service layer** - Separate business logic from routes
4. **Add caching** - Cache common queries for better performance

### Long-term Enhancements
1. **Type hints everywhere** - Full mypy compliance
2. **Async database operations** - Use async SQLAlchemy
3. **Repository pattern** - Abstract database access further
4. **Event-driven architecture** - For notifications and webhooks

## Migration Guide

### For Developers

If you're working on routers, use these new utilities:

#### Authentication & Authorization
```python
from api.dependencies import verify_admin_access, verify_org_member

@router.post("/endpoint")
def my_endpoint(
    admin: Person = Depends(verify_admin_access),  # Auto-validates admin
    db: Session = Depends(get_db)
):
    verify_org_member(admin, org_id)  # Check org membership
    ...
```

#### Security Operations
```python
from api.utils.security import (
    hash_password,
    verify_password,
    generate_invitation_token,
    generate_auth_token
)

# Hash a password
hashed = hash_password(plain_password)

# Verify password
if verify_password(plain_password, hashed):
    # Generate auth token
    token = generate_auth_token()
```

#### Database Queries
```python
from api.utils.db_helpers import (
    check_email_exists,
    get_person_assignments,
    is_person_blocked_on_date
)

# Check email
if check_email_exists(db, email, org_id):
    raise HTTPException(409, "Email exists")

# Get assignments
assignments = get_person_assignments(db, person_id, start_date, end_date)

# Check availability
blocked, reason = is_person_blocked_on_date(db, person_id, date)
```

## Conclusion

This refactoring significantly improves code quality by:
- Eliminating ~150+ lines of duplicate code
- Creating 20+ reusable utility functions
- Establishing patterns for future development
- Improving security and maintainability

The codebase is now more maintainable, testable, and follows better software engineering practices.

---

**Author:** Claude
**Date:** 2025-10-05
**Version:** 1.0
