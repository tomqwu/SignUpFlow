# GUI Manual Test Guide

This document provides step-by-step instructions for manually testing the frontend GUI.

## Setup

1. **Start the server**: `poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000`
2. **Open browser**: Navigate to `http://localhost:8000/frontend/index.html`
3. **Open DevTools**: Press F12 to monitor console for errors

---

## Test Suite 1: Authentication Flow

### Test 1.1: Signup New User
**Steps:**
1. Click "Get Started" on welcome page
2. Select "Demo Organization" from the list
3. Click "Continue"
4. Fill in profile form:
   - Name: "Test User"
   - Email: "newuser@test.com"
   - Password: "test123456"
   - Select roles: "Volunteer", "Musician"
5. Click "Continue →"

**Expected:**
- ✅ Should redirect to main app
- ✅ Header should show "Test User"
- ✅ Navigation should show 3 tabs (no admin tab)

**Status:** [ ] Pass [ ] Fail

---

### Test 1.2: Signup Admin User
**Steps:**
1. Clear localStorage or use incognito mode
2. Repeat signup steps but:
   - Email: "newadmin@test.com"
   - Check "Administrator" role

**Expected:**
- ✅ Should redirect to main app
- ✅ Navigation should show 4 tabs including "👑 Admin Dashboard"

**Status:** [ ] Pass [ ] Fail

---

### Test 1.3: Login Existing User
**Steps:**
1. Clear localStorage or reload page
2. Click "Sign in" on welcome page
3. Enter credentials:
   - Email: "admin@demo.com"
   - Password: "admin123"
4. Click "Sign In →"

**Expected:**
- ✅ Should redirect to main app
- ✅ Should show admin dashboard tab

**Status:** [ ] Pass [ ] Fail

---

### Test 1.4: Login Wrong Password
**Steps:**
1. Reload page
2. Click "Sign in"
3. Enter:
   - Email: "admin@demo.com"
   - Password: "wrongpassword"
4. Click "Sign In →"

**Expected:**
- ✅ Should show error message "Invalid email or password"
- ✅ Should stay on login page

**Status:** [ ] Pass [ ] Fail

---

## Test Suite 2: User Features

### Test 2.1: View Calendar
**Steps:**
1. Login as any user
2. Ensure "My Calendar" tab is active

**Expected:**
- ✅ Calendar grid should load
- ✅ Should show events if any exist
- ✅ Month selector should work

**Status:** [ ] Pass [ ] Fail

---

### Test 2.2: Add Time-Off
**Steps:**
1. Click "Availability" tab
2. Select from date (e.g., 7 days from now)
3. Select to date (e.g., 10 days from now)
4. Click "Block These Dates"

**Expected:**
- ✅ Success message appears
- ✅ Time-off appears in the list below
- ✅ Shows date range in red

**Status:** [ ] Pass [ ] Fail

---

### Test 2.3: Remove Time-Off
**Steps:**
1. In Availability tab
2. Click "Remove" on a time-off period

**Expected:**
- ✅ Time-off period is removed from list

**Status:** [ ] Pass [ ] Fail

---

### Test 2.4: View Schedule
**Steps:**
1. Click "My Schedule" tab

**Expected:**
- ✅ Shows upcoming assignments count
- ✅ Shows this month count
- ✅ Timeline loads (may be empty if no schedule generated)

**Status:** [ ] Pass [ ] Fail

---

## Test Suite 3: Admin Features

**Prerequisites:** Login as admin user

### Test 3.1: View Admin Dashboard
**Steps:**
1. Login as admin
2. Click "👑 Admin Dashboard" tab

**Expected:**
- ✅ Shows stats: People count, Events count, Schedules count
- ✅ Shows event management section
- ✅ Shows schedule generation section
- ✅ Shows people list
- ✅ Shows solutions list

**Status:** [ ] Pass [ ] Fail

---

### Test 3.2: Create Event
**Steps:**
1. In Admin Dashboard tab
2. Click "+ Create Event" button
3. Fill in form:
   - Event Type: "Bible Study"
   - Date & Time: Select future date/time
   - Duration: 2 hours
   - Location: "Room 101"
   - Roles: "volunteer, leader"
4. Click "Create Event"

**Expected:**
- ✅ Success message appears
- ✅ Modal closes
- ✅ Event appears in events list
- ✅ Events count increments

**Status:** [ ] Pass [ ] Fail

---

### Test 3.3: Delete Event
**Steps:**
1. In Admin Dashboard > Event Management
2. Click "Delete" on an event
3. Confirm deletion

**Expected:**
- ✅ Event is removed from list
- ✅ Success message appears
- ✅ Events count decrements

**Status:** [ ] Pass [ ] Fail

---

### Test 3.4: Generate Schedule
**Steps:**
1. Ensure at least 1 event and 2 people exist
2. In Admin Dashboard
3. Click "🔄 Generate Schedule" button

**Expected:**
- ✅ Shows "Generating schedule..." message
- ✅ Shows success message with:
   - Solution ID
   - Assignment count
   - Health score
- ✅ Solutions list updates
- ✅ Schedules count increments

**Status:** [ ] Pass [ ] Fail

---

### Test 3.5: View Generated Schedule
**Steps:**
1. After generating schedule
2. In "Generated Schedules" section
3. Click "View" button on a solution

**Expected:**
- ✅ CSV file downloads
- ✅ File contains assignment data

**Status:** [ ] Pass [ ] Fail

---

## Test Suite 4: Export Features

### Test 4.1: Export Calendar to ICS
**Steps:**
1. Login as regular user
2. In "My Calendar" tab
3. Click "📥 Export to Calendar"

**Expected:**
- ✅ ICS file downloads
- ✅ Can be imported into Google Calendar/Outlook

**Status:** [ ] Pass [ ] Fail

---

## Test Suite 5: Session Management

### Test 5.1: Session Persistence
**Steps:**
1. Login as any user
2. Refresh the page (F5)

**Expected:**
- ✅ Should remain logged in
- ✅ Should show same user data

**Status:** [ ] Pass [ ] Fail

---

### Test 5.2: Logout
**Steps:**
1. Click settings icon (⚙️) in header
2. Click "Sign Out"

**Expected:**
- ✅ Redirects to welcome page
- ✅ localStorage is cleared
- ✅ Cannot access main app without login

**Status:** [ ] Pass [ ] Fail

---

## Test Suite 6: Error Handling

### Test 6.1: Network Error
**Steps:**
1. Stop the API server
2. Try to login

**Expected:**
- ✅ Shows "Connection error" message

**Status:** [ ] Pass [ ] Fail

---

## Test Results Summary

Total Tests: 17
- Passed: ___
- Failed: ___
- Skipped: ___

**Overall Status:** [ ] All Pass [ ] Some Failures

---

## Notes

Use this section to document any bugs found or additional observations:

```
[Add your notes here]
```
