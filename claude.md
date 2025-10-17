# Claude Development Rules

## 🚨 CRITICAL: Read This EVERY Time Before Starting Work

### The Golden Rule
**If a user can see it, click it, or type in it → it MUST have an e2e test that simulates the EXACT user journey. NO EXCEPTIONS.**

---

## Mandatory Workflow for ALL Features

### Step 1: Plan (5 minutes)
Before writing ANY code, write down:
1. **User Journey** - What does the user do? (click what? type what? see what?)
2. **Dependencies** - Does this need i18n? Timezone? Roles? Validation?
3. **Success Criteria** - What does success look like on the screen?

### Step 2: Write E2E Test FIRST (10 minutes)
```python
def test_[feature]_complete_user_journey(page: Page):
    # 1. User starts here
    page.goto("...")

    # 2. User clicks this
    page.locator('button:has-text("...")').click()

    # 3. User fills this
    page.locator('#field').fill("...")

    # 4. User submits
    page.locator('button[type="submit"]').click()

    # 5. User SEES this (VERIFY UI STATE!)
    expect(page.locator('#result')).to_be_visible()
    expect(page.locator('#result')).to_have_text("...")

    # 6. Verify all UI elements correct
    # - Correct things visible?
    # - Correct things hidden?
    # - Timezone auto-detected?
    # - i18n text showing?
```

**Test should FAIL at this point** (because feature not implemented yet)

### Step 3: Implement Feature
Write minimum code to make e2e test pass.

**Check ALL dependencies:**
- [ ] i18n translations (all languages: en, zh, es)
- [ ] Timezone auto-detection
- [ ] Role/permission checks
- [ ] Form validation (frontend AND backend)
- [ ] Error messages (user-friendly, translated)
- [ ] Loading states (no blank screens)

### Step 4: Verify
- [ ] Run e2e test → MUST PASS
- [ ] Run ALL e2e tests → ALL MUST PASS
- [ ] Open browser → manually test
- [ ] Check console → NO ERRORS
- [ ] Check network → NO FAILED REQUESTS

### Step 5: Before Saying "Done"
```bash
# Run this command and ALL must pass
poetry run pytest tests/e2e/ -v

# If ANY test fails → NOT DONE
# If console has errors → NOT DONE
# If you didn't manually test → NOT DONE
```

---

## What to Test in E2E

### ✅ ALWAYS Test These:
1. **Complete User Journey** - From start to finish
2. **UI State** - What user SEES on screen
3. **Form Validation** - Empty, invalid, valid inputs
4. **Navigation** - Screen transitions
5. **Dependencies**:
   - Timezone auto-detection working?
   - i18n showing correct language?
   - Roles/permissions enforced?
   - Error messages appearing?

### ❌ NEVER Skip These Checks:
- [ ] Is timezone auto-detected (not defaulting to UTC)?
- [ ] Are invitation-specific fields hidden for non-invitation flows?
- [ ] Are form fields pre-filled correctly?
- [ ] Do error messages appear IN THE UI?
- [ ] Does success navigate to correct screen?
- [ ] Are all translations present?

---

## Red Flags = STOP IMMEDIATELY

🚩 **"The API test passes"** → NOT ENOUGH! Test the UI!

🚩 **"The backend works"** → NOT ENOUGH! Test the frontend!

🚩 **"It should work"** → PROVE IT! Run e2e test!

🚩 **"Can you test it?"** → NO! Test it yourself FIRST!

🚩 **"I'll add tests later"** → NO! Tests come FIRST!

🚩 **"I tested the function"** → NOT ENOUGH! Test the USER JOURNEY!

---

## Common Mistakes That Waste Time

### ❌ Testing Only the API
```python
# BAD - Only tests backend
response = requests.post("/api/organizations/", json={...})
assert response.status_code == 201
# ❌ Didn't test what user SEES
```

### ✅ Testing User Journey
```python
# GOOD - Tests what user experiences
page.locator('button:has-text("Create")').click()
page.locator('#org-name').fill("My Org")
page.locator('button[type="submit"]').click()
expect(page.locator('#success-message')).to_be_visible()
# ✅ Tested what user SEES
```

### ❌ Not Checking UI State
```python
# BAD
# Set timezone in code
# Don't verify it shows in UI
# ❌ User might see UTC when expecting America/Toronto
```

### ✅ Checking UI State
```python
# GOOD
timezone = page.locator('#user-timezone').input_value()
assert timezone == "America/Toronto"  # Not "UTC"
# ✅ Verified user sees correct value
```

---

## Quick Reference Commands

```bash
# Run all e2e tests (DO THIS BEFORE SAYING "DONE")
poetry run pytest tests/e2e/ -v

# Run specific test
poetry run pytest tests/e2e/test_org_creation.py -v -s

# Run with browser visible (debugging)
poetry run pytest tests/e2e/ -v --headed --slowmo 500

# Start backend server
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Feature Checklist Template

Use this for EVERY feature:

```markdown
## Feature: [Name]

### User Journey
1. User clicks [button]
2. User fills [fields]
3. User submits
4. User sees [result]

### E2E Test Status
- [ ] Test written BEFORE implementation
- [ ] Test simulates exact user clicks
- [ ] Test verifies UI state
- [ ] Test passes consistently
- [ ] Manually tested in browser

### Dependencies Checked
- [ ] i18n translations (en, zh, es)
- [ ] Timezone auto-detection
- [ ] Role/permission checks
- [ ] Form validation (frontend + backend)
- [ ] Error messages (user-friendly)
- [ ] Loading states

### Final Verification
- [ ] All e2e tests pass: `poetry run pytest tests/e2e/ -v`
- [ ] No console errors
- [ ] No network errors
- [ ] Manually tested in browser
- [ ] No TODOs or FIXMEs in code
```

---

## When User Reports Bug

### DO NOT:
- ❌ Say "it works for me"
- ❌ Say "the API is fine"
- ❌ Ask user to test again

### DO:
1. ✅ Write e2e test that reproduces the bug
2. ✅ Test should FAIL (confirming bug exists)
3. ✅ Fix the bug
4. ✅ Test should now PASS
5. ✅ Run ALL e2e tests to ensure no regression

---

## Key Principle

> **Test what the user EXPERIENCES, not what the code DOES.**

Bad: "The function returns 201"
Good: "The user sees the success message on screen"

Bad: "The API endpoint works"
Good: "The user can complete the entire flow from start to finish"

Bad: "The backend saves to database"
Good: "The user sees their saved data displayed in the UI"

---

## Summary: The Only Way Forward

1. **Write e2e test FIRST** (simulate user journey)
2. **Implement feature** (make test pass)
3. **Verify in browser** (manual check)
4. **Run ALL tests** (no regressions)
5. **Only then say "done"**

**NO SHORTCUTS. NO EXCUSES. NO EXCEPTIONS.**

---

## See Also
- [E2E_TESTING_CHECKLIST.md](docs/E2E_TESTING_CHECKLIST.md) - Detailed testing guidelines
- [CONTRIBUTING.md](CONTRIBUTING.md) - Full development workflow
