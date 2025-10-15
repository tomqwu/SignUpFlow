# i18n UI Translation Completion Guide

## Current Status

**✅ Working Demo Implemented** - Language switching now works for:
- Navigation buttons (My Schedule, All Events, Availability, Admin Dashboard)
- Settings modal (all labels and buttons)
- View headers (main headings for each section)

**📊 Progress:** ~15% of UI text is now translatable (20 out of ~150 elements)

---

## How the Translation System Works

### 1. HTML Elements with `data-i18n`

Any HTML element with a `data-i18n` attribute will be automatically translated:

```html
<!-- Original (hardcoded) -->
<button>Save Changes</button>

<!-- Translated (with data-i18n) -->
<button data-i18n="common.buttons.save">Save Changes</button>
```

The English text is kept as a fallback for when translations load.

### 2. Translation Keys

Translation keys follow this pattern: `namespace.section.key`

Examples:
- `common.buttons.save` → "Save" / "Guardar" / "保存"
- `schedule.my_schedule` → "My Schedule" / "Mi Horario" / "我的日程"
- `settings.timezone` → "Timezone" / "Zona Horaria" / "时区"

### 3. Automatic Translation

The `translatePage()` function runs automatically:
- On page load (after i18n initialization)
- When user changes language in Settings
- Finds all `[data-i18n]` elements and translates them

```javascript
function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = i18n.t(key);
        el.textContent = translated;
    });
}
```

---

## Completing the Remaining Translations

### Phase 1: Common Buttons (Priority: HIGH)

**Estimated Time:** 30 minutes

Add `data-i18n` to all buttons across the app:

```html
<!-- Before -->
<button onclick="saveEvent()">Save</button>
<button onclick="cancel()">Cancel</button>
<button onclick="delete()">Delete</button>

<!-- After -->
<button onclick="saveEvent()" data-i18n="common.buttons.save">Save</button>
<button onclick="cancel()" data-i18n="common.buttons.cancel">Cancel</button>
<button onclick="deleteItem()" data-i18n="common.buttons.delete">Delete</button>
```

**Files to Update:**
- `frontend/index.html` - Search for `<button` tags

**Translation Keys Available:**
```
common.buttons.save
common.buttons.cancel
common.buttons.delete
common.buttons.edit
common.buttons.add
common.buttons.create
common.buttons.close
common.buttons.back
common.buttons.next
common.buttons.submit
common.buttons.confirm
```

### Phase 2: Form Labels (Priority: HIGH)

**Estimated Time:** 45 minutes

Add `data-i18n` to all `<label>` elements:

```html
<!-- Before -->
<label>Name</label>
<label>Email</label>
<label>Phone</label>

<!-- After -->
<label data-i18n="common.labels.name">Name</label>
<label data-i18n="common.labels.email">Email</label>
<label data-i18n="common.labels.phone">Phone</label>
```

**Files to Update:**
- `frontend/index.html` - All forms and modals

**Translation Keys Available:**
```
common.labels.name
common.labels.email
common.labels.phone
common.labels.date
common.labels.time
common.labels.description
common.labels.status
```

### Phase 3: Modal Dialogs (Priority: MEDIUM)

**Estimated Time:** 1 hour

Update all modal dialogs (event creation, role assignment, etc.):

```html
<!-- Example: Event Modal -->
<div class="modal-header">
    <h3 data-i18n="events.create_event">Create Event</h3>
</div>
<div class="modal-body">
    <label data-i18n="events.event_type">Event Type</label>
    <label data-i18n="events.start_time">Start Time</label>
    <label data-i18n="events.end_time">End Time</label>
</div>
```

**Modals to Update:**
- ✅ Settings Modal (DONE)
- Add Role Modal
- Create Event Modal
- Edit Event Modal
- Time Off Modal
- Calendar Subscription Modal
- Invite People Modal

### Phase 4: Dynamic Content (Priority: MEDIUM)

**Estimated Time:** 45 minutes

Update JavaScript strings (toasts, alerts, error messages):

```javascript
// Before
showToast('Settings saved successfully!', 'success');
showToast('Error saving settings', 'error');

// After
showToast(i18n.t('messages.success.saved'), 'success');
showToast(i18n.t('messages.errors.save_failed'), 'error');
```

**Files to Update:**
- `frontend/js/app-user.js` - All `showToast()` calls
- `frontend/js/app-user.js` - All `confirm()` dialogs
- `frontend/js/app-user.js` - All `alert()` messages

**Translation Keys Available:**
```
messages.success.saved
messages.success.created
messages.success.deleted
messages.errors.generic
messages.errors.network
messages.errors.save_failed
messages.confirmations.delete
messages.confirmations.cancel
```

### Phase 5: Help Text & Instructions (Priority: LOW)

**Estimated Time:** 30 minutes

Update help text, placeholders, and instructions:

```html
<!-- Before -->
<p class="help-text">Changes take effect immediately</p>
<input placeholder="Enter your name">

<!-- After -->
<p class="help-text" data-i18n="settings.help_immediate">Changes take effect immediately</p>
<input data-i18n="common.placeholders.name" placeholder="Enter your name">
```

**Note:** For placeholders, update `translatePage()` to handle them:

```javascript
function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = i18n.t(key);

        // Handle placeholders
        if (el.hasAttribute('placeholder')) {
            el.setAttribute('placeholder', translated);
        } else {
            el.textContent = translated;
        }
    });
}
```

---

## Testing Checklist

After adding translations, test each language:

### 1. English (en)
- [ ] All buttons display correctly
- [ ] All labels readable
- [ ] No missing text
- [ ] Modals work correctly

### 2. Spanish (es)
- [ ] Navigation translates
- [ ] Settings modal translates
- [ ] Forms translate
- [ ] No truncated text

### 3. Portuguese (pt)
- [ ] All elements translate
- [ ] Text fits in buttons
- [ ] Modals display correctly

### 4. Chinese (zh-CN, zh-TW)
- [ ] Chinese characters display
- [ ] Text doesn't overflow
- [ ] Layout remains intact

### 5. French (fr)
- [ ] All translations load
- [ ] Longer French text fits
- [ ] No layout issues

---

## Quick Reference: Finding Elements

### Find all untranslated buttons:
```bash
grep -n "<button" frontend/index.html | grep -v "data-i18n"
```

### Find all untranslated labels:
```bash
grep -n "<label" frontend/index.html | grep -v "data-i18n"
```

### Find all untranslated h2/h3:
```bash
grep -n "<h[23]" frontend/index.html | grep -v "data-i18n"
```

### Find all showToast calls:
```bash
grep -n "showToast" frontend/js/app-user.js
```

---

## Translation Key Reference

### Common Keys (common.json)
```
buttons: save, cancel, delete, edit, add, create, update, remove, close, back, next, submit, confirm, yes, no
labels: name, email, phone, address, date, time, description, status
errors: required_field, invalid_email, network_error
```

### Schedule Keys (schedule.json)
```
my_schedule, upcoming, past, today, this_week, next_week
no_events, view_details, export_calendar, subscribe
```

### Events Keys (events.json)
```
title, create_event, edit_event, delete_event
event_type, start_time, end_time, location, notes
join_event, leave_event, assignments
```

### Settings Keys (settings.json)
```
title, profile, account, preferences
name, email, timezone, language, permissions, roles
save_changes, cancel, logout
```

### Messages Keys (messages.json)
```
success: saved, created, updated, deleted
errors: generic, network, validation, server
confirmations: delete, leave, cancel
```

---

## Estimated Completion Time

| Phase | Elements | Time | Priority |
|-------|----------|------|----------|
| ✅ Demo (Done) | 20 | - | Complete |
| Phase 1: Buttons | 30 | 30 min | HIGH |
| Phase 2: Labels | 40 | 45 min | HIGH |
| Phase 3: Modals | 50 | 1 hour | MEDIUM |
| Phase 4: JavaScript | 25 | 45 min | MEDIUM |
| Phase 5: Help Text | 20 | 30 min | LOW |
| **Total** | **185** | **~3.5 hours** | |

---

## How to Test Your Changes

1. **Start the server:**
   ```bash
   poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Open browser:**
   ```
   http://localhost:8000
   ```

3. **Login** and go to Settings

4. **Change language** and verify:
   - Navigation buttons change
   - Settings modal changes
   - View headers change
   - Any new elements you added change

5. **Check browser console** for errors:
   - Press F12 → Console tab
   - Should see: `i18n initialized with locale: en`
   - Should NOT see: `Failed to load translations`

---

## Need Help?

If you see missing translations:

1. **Check translation files exist:**
   ```bash
   ls -la locales/es/
   # Should show: common.json, events.json, schedule.json, settings.json, admin.json, messages.json, auth.json
   ```

2. **Verify translation key exists:**
   ```bash
   cat locales/en/common.json | grep "save"
   ```

3. **Check browser console:**
   - Missing keys will show warnings
   - Falls back to English if translation missing

4. **Add missing translations:**
   - Edit the appropriate JSON file in `locales/{lang}/`
   - Follow the existing structure
   - Restart server or refresh browser

---

## Example: Complete Modal Translation

Here's a complete example of translating a modal:

**Before:**
```html
<div class="modal">
    <div class="modal-header">
        <h3>Create Event</h3>
        <button onclick="close()">×</button>
    </div>
    <div class="modal-body">
        <label>Event Name</label>
        <input type="text">
        <label>Event Type</label>
        <select>...</select>
    </div>
    <div class="modal-footer">
        <button onclick="save()">Save</button>
        <button onclick="cancel()">Cancel</button>
    </div>
</div>
```

**After:**
```html
<div class="modal">
    <div class="modal-header">
        <h3 data-i18n="events.create_event">Create Event</h3>
        <button onclick="close()">×</button>
    </div>
    <div class="modal-body">
        <label data-i18n="events.event_name">Event Name</label>
        <input type="text">
        <label data-i18n="events.event_type">Event Type</label>
        <select>...</select>
    </div>
    <div class="modal-footer">
        <button onclick="save()" data-i18n="common.buttons.save">Save</button>
        <button onclick="cancel()" data-i18n="common.buttons.cancel">Cancel</button>
    </div>
</div>
```

That's it! The `translatePage()` function handles the rest.

---

## Ready to Complete?

Follow this workflow:

1. Pick a phase (start with Phase 1: Buttons)
2. Find all untranslated elements using grep commands above
3. Add `data-i18n="appropriate.key"` to each element
4. Test in browser by switching languages
5. Fix any issues
6. Move to next phase
7. Commit when complete

Good luck! 🚀
