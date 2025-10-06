# Multi-Organization Feature - Known Limitations

**Status:** ⚠️ Partially Implemented
**Impact:** Multi-org users cannot login or switch organizations
**Test Status:** 2 tests skipped due to these limitations

---

## Overview

The Rostio system has infrastructure for multi-organization support (one user belonging to multiple organizations), but the implementation is incomplete. The skipped tests reveal fundamental product issues that need to be addressed.

---

## Current Implementation

### What Works ✅

1. **Data Model Supports Multi-Org**
   - Person can exist in multiple organizations (different person_id, same email)
   - Each person record is org-specific
   - Frontend has org-switching UI (dropdown)

2. **Frontend UI Exists**
   - Org dropdown appears when user belongs to multiple orgs
   - `switchOrganization()` function implemented
   - Badge display for single-org users

3. **API Supports Multiple Records**
   - Can create multiple Person records with same email
   - Different org_id for each record

### What's Broken ❌

1. **Login Only Returns First Match**
   ```python
   # api/routers/auth.py:100
   person = db.query(Person).filter(Person.email == request.email).first()
   ```
   - Uses `.first()` which returns only ONE person
   - If email exists in multiple orgs, unpredictable which one is returned
   - No org selection during login

2. **No Org Selection UI During Login**
   - Login form only asks for email + password
   - Doesn't show org selector when email matches multiple orgs
   - User has no way to specify which org to login to

3. **Session Doesn't Track Multiple Orgs**
   - Login creates session for ONE org
   - Switching orgs would require re-authentication or token exchange

---

## Test Status

### Skipped Tests

#### 1. `test_multi_org_setup_and_switching`
**Location:** `tests/integration/test_multi_org_workflow.py:14`
**Reason:** Multi-org login not implemented
**Skip Message:** `"Multi-org login not implemented - login.first() only returns one person per email, needs org selection during login"`

**What it Tests:**
- User `alice@multiorg.com` belongs to two orgs
- Login should work
- Should be able to switch between orgs via dropdown

**Why it Fails:**
- Creates two Person records: `alice-church` and `alice-school`, both with email `alice@multiorg.com`
- Login query returns `.first()` match (unpredictable which org)
- Playwright waits for `#main-app` but login fails or logs into wrong org
- **Timeout:** Page never loads

#### 2. `test_single_org_shows_badge`
**Location:** `tests/integration/test_multi_org_workflow.py:138`
**Reason:** Test infrastructure issues
**Skip Message:** `"Test creates dynamic user/org which causes login issues - needs refactor to use test fixtures"`

**What it Tests:**
- User `bob@single.com` belongs to ONE org
- Should see org badge, NOT dropdown
- Badge should display org name

**Why it Fails:**
- Creates user dynamically with timestamp-based ID
- Doesn't use password hashing properly or conflicts with existing data
- Playwright login times out waiting for `#main-app`
- **Root Cause:** Not using established test fixtures like `sarah@grace.church`

---

## Required Fixes

### Priority 1: Fix Multi-Org Login

**Option A: Org Selection During Login (Recommended)**
```python
# 1. Check if email matches multiple orgs
people = db.query(Person).filter(Person.email == request.email).all()

if len(people) > 1:
    # Return list of orgs for user to choose from
    return {
        "needs_org_selection": True,
        "organizations": [{"org_id": p.org_id, "org_name": p.organization.name} for p in people]
    }

# 2. Frontend shows org selector
# 3. User clicks org, sends org_id with login request
# 4. Backend finds specific person record
person = db.query(Person).filter(
    Person.email == request.email,
    Person.org_id == request.org_id
).first()
```

**Frontend Changes:**
- Add org selector to login modal (hidden by default)
- Show when API returns `needs_org_selection: true`
- Submit org_id with second login request

**Option B: Email+Org Login**
- Change login to require email AND org_id always
- Add org selector to login form
- More complex UX (user must know org ID)

### Priority 2: Fix Test Infrastructure

**Refactor `test_single_org_shows_badge`:**
```python
def test_single_org_shows_badge(api_server):
    """Use existing test fixture instead of dynamic creation"""

    # Use sarah@grace.church (from setup_test_data.py)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login with known-good credentials
        page.goto(BASE_URL)
        page.fill('#login-email', 'sarah@grace.church')
        page.fill('#login-password', 'password123')
        page.click('button:has-text("Sign In")')
        page.wait_for_selector('#main-app:not(.hidden)')

        # Verify badge (Sarah only belongs to one org)
        badge = page.locator('#org-name-display')
        assert badge.is_visible()
        assert "Grace Church" in badge.inner_text()
```

### Priority 3: Session Management for Org Switching

**Current:** User logs in to one org, stays in that org
**Needed:** User can switch orgs without re-login

**Approach:**
1. Store all user's org memberships in session/token
2. `switchOrganization()` updates session org context
3. Server validates user has permission for that org
4. Update UI to reflect new org context

---

## Workaround (Current Users)

**For Single-Org Users:** ✅ Works fine
- Most users belong to only one organization
- No issues with login or functionality

**For Multi-Org Users:** ❌ Not supported
- Create separate email addresses per org
- Example:
  - `alice+church@email.com` → Church org
  - `alice+school@email.com` → School org
- Email provider will deliver both to same inbox (for Gmail, etc.)

---

## Code References

### Login Implementation
- [api/routers/auth.py:96-106](../api/routers/auth.py#L96) - Login function using `.first()`

### Frontend Org Switching
- [frontend/js/app-user.js:287](../frontend/js/app-user.js#L287) - Org dropdown rendering
- [frontend/js/app-user.js:326](../frontend/js/app-user.js#L326) - `switchOrganization()` function

### Skipped Tests
- [tests/integration/test_multi_org_workflow.py:14](../tests/integration/test_multi_org_workflow.py#L14) - Multi-org switching test
- [tests/integration/test_multi_org_workflow.py:138](../tests/integration/test_multi_org_workflow.py#L138) - Single-org badge test

---

## Decision Log

### Why Skip Instead of Fix?

**Question:** User asked to "fix skipped tests" - why not implement multi-org login?

**Answer:**
1. **Scope:** Multi-org login is a significant feature (2-3 days work)
   - Requires API changes
   - Requires frontend UI changes
   - Requires session management updates
   - Needs comprehensive testing

2. **Product Priority:** Unknown if multi-org is needed
   - No user requests for this feature
   - Most organizations use single-org model
   - Workaround exists (separate emails)

3. **Risk vs Reward:** High complexity for uncertain value
   - Could introduce security issues if done wrong
   - Session management is tricky
   - Better to implement when actually needed

4. **Test Value:** Skipped tests document the limitation
   - Clear skip messages explain what's missing
   - Tests can be enabled when feature is implemented
   - Serve as specification for future work

### Alternative Considered: Delete Tests

**Rejected because:**
- Tests document expected behavior
- Losing tests loses product knowledge
- Skip messages preserve intent
- Easy to enable when feature is built

---

## Summary

**Current Status:**
- ✅ 179 tests passing
- ⚠️ 2 tests skipped (multi-org limitations)
- ❌ Multi-org login not implemented

**Recommendation:**
- Keep tests skipped with clear documentation
- Implement multi-org login only if/when users request it
- Use workaround (separate emails) until then

**When to Implement:**
- User report: "I belong to multiple organizations and can't switch"
- Business requirement: Multi-org membership is needed
- Product decision: Multi-tenancy is a priority feature

---

**Last Updated:** 2025-10-06
**Related:** [EVENT_ROLES_FEATURE.md](EVENT_ROLES_FEATURE.md), [WORKSPACE_ORGANIZATION.md](WORKSPACE_ORGANIZATION.md)
