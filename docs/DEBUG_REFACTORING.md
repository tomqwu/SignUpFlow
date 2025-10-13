# Debug Console Refactoring Guide

## Overview

We've introduced a centralized debug utility (`/js/debug.js`) that provides conditional console logging based on environment detection. This allows debug statements to remain in the codebase but only execute in non-production environments.

## Debug Utility Features

### Debug Mode Control

Debug mode is **OFF by default**. You can enable it through:
- URL parameter: `?debug=true`
- localStorage: `localStorage.setItem('debug', 'true')`
- Browser console: `debug.enable()`

To disable:
- URL parameter: `?debug=false`
- Browser console: `debug.disable()`

### API Methods

```javascript
// Conditional logging (only in debug mode)
debug.log('message', data);       // Standard log
debug.warn('warning', data);      // Warning
debug.info('info', data);         // Info
debug.table(arrayData);           // Table view

// Always logs (even in production)
debug.error('error', data);       // Errors

// Grouping (for organizing related logs)
debug.group('Group Name');
debug.log('item 1');
debug.log('item 2');
debug.groupEnd();

// Control debug mode
debug.enable();   // Turn on and reload
debug.disable();  // Turn off and reload
```

## Refactoring Examples

### Before:
```javascript
console.log('User loaded:', user);
console.log('Roles:', user.roles);
```

### After:
```javascript
debug.log('User loaded:', user);
debug.log('Roles:', user.roles);
```

---

### Before (grouped logs):
```javascript
console.log('🔍 DEBUG updateRoleBadgesDisplay:');
console.log('  - roles:', roles);
console.log('  - Type:', typeof roles);
console.log('  - IsArray:', Array.isArray(roles));
```

### After:
```javascript
debug.group('updateRoleBadgesDisplay');
debug.log('roles:', roles);
debug.log('Type:', typeof roles);
debug.log('IsArray:', Array.isArray(roles));
debug.groupEnd();
```

---

### Before (errors - should always log):
```javascript
console.error('Failed to load:', error);
```

### After:
```javascript
debug.error('Failed to load:', error);
```

## Files Already Refactored

- ✅ `/js/app-user.js` - Updated updateRoleBadgesDisplay()

## Files Remaining to Refactor

Based on grep analysis, these files have console statements:

- `/js/role-management.js` - 1 console.error
- `/js/auth-fetch.js` - 2 console statements
- `/js/recurring-events.js` - 2 console statements
- `/js/router.js` - 5 console statements
- `/js/i18n.js` - 3 console statements
- `/js/conflict-detection.js` - 1 console statement
- `/js/app-user.js` - ~50 more console statements
- `/js/app-admin.js` - 1 console statement
- `/js/app.js` - 1 console statement

## Refactoring Guidelines

1. **Keep the debug utility first**: Load `/js/debug.js` before other scripts
2. **Preserve error logging**: Use `debug.error()` for all errors (always logs)
3. **Use grouping for related logs**: Wrap related debug statements in `debug.group()` / `debug.groupEnd()`
4. **Don't remove debug code**: Keep debug statements; they won't execute in production
5. **Test in production mode**: Verify logs don't appear with `?debug=false`

## Testing

### Enable debug mode:
```javascript
// In browser console
debug.enable()

// Or use URL parameter
http://localhost:8000/?debug=true
```

### Disable debug mode:
```javascript
// In browser console
debug.disable()

// Or use URL parameter
http://localhost:8000/?debug=false
```

### Check debug status:
```javascript
// In browser console
debug.enabled  // Returns true/false
```

## Benefits

1. **No more production noise**: Debug logs won't clutter production console
2. **Easy toggling**: Turn debugging on/off with a URL parameter or console command
3. **Preserves debugging info**: No need to remove debug statements before deployment
4. **Better organization**: Grouped logs make debugging easier
5. **Performance**: Conditional execution means zero overhead in production

## Migration Priority

**High Priority** (most verbose):
- `/js/app-user.js` (50+ statements)

**Medium Priority** (multiple statements):
- `/js/router.js` (5 statements)
- `/js/i18n.js` (3 statements)
- `/js/auth-fetch.js` (2 statements)
- `/js/recurring-events.js` (2 statements)

**Low Priority** (single statements):
- `/js/role-management.js`
- `/js/conflict-detection.js`
- `/js/app-admin.js`
- `/js/app.js`
