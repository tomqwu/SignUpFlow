# reCAPTCHA Bot Protection

Rostio uses Google reCAPTCHA v3 to protect critical endpoints from automated bot abuse.

## Overview

reCAPTCHA v3 provides invisible, score-based bot detection without requiring user interaction. It analyzes user behavior and returns a score from 0.0 (likely bot) to 1.0 (likely human).

reCAPTCHA is applied to the following high-risk endpoints:
- Password reset requests (`/api/auth/forgot-password` and `/api/auth/reset-password`)
- Organization creation (`/api/organizations/`)

These endpoints are particularly vulnerable to abuse and reCAPTCHA adds an additional layer of protection beyond rate limiting.

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# reCAPTCHA v3 Keys (get from https://www.google.com/recaptcha/admin)
RECAPTCHA_SITE_KEY=6LfErOwrAAAAAFyK2JxgXjTW_BqrsGbY6-qecC_J
RECAPTCHA_SECRET_KEY=6LfErOwrAAAAALX8XV9uWy8hoE6Ht9BeiCCELdvq

# reCAPTCHA v3 Score Threshold (0.0-1.0, default 0.5)
# Lower = more permissive (may allow some bots)
# Higher = more restrictive (may block some humans)
RECAPTCHA_MIN_SCORE=0.5
```

### Getting reCAPTCHA Keys

1. Visit [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin)
2. Register your site
3. Choose **reCAPTCHA v3**
4. Add your domains
5. Copy the **Site Key** and **Secret Key**

## How It Works

### Backend

The backend uses two utilities:

**`api/utils/recaptcha.py`**
- `verify_recaptcha(token, remote_ip, expected_action, min_score)` - Verifies reCAPTCHA v3 token with Google API
  - Returns tuple of `(is_valid: bool, score: float)`
  - Checks score threshold (default 0.5)
  - Optionally verifies action name matches
- `get_recaptcha_site_key()` - Returns site key for frontend use
- Automatically disabled during testing (when `TESTING=true`)

**`api/utils/recaptcha_middleware.py`**
- `require_recaptcha` - FastAPI dependency for endpoints
- Checks `X-Recaptcha-Token` header
- Returns 400 error if verification fails

### Frontend

**`frontend/js/recaptcha.js`**
- Loads reCAPTCHA v3 configuration from backend
- Dynamically loads reCAPTCHA v3 script when enabled
- `getRecaptchaToken(action)` - Gets v3 token for an action (e.g., 'password_reset', 'create_org')
- `addRecaptchaToken(action, fetchOptions)` - Adds reCAPTCHA token to fetch request headers

### Example Usage

#### Backend Endpoint

```python
from api.utils.recaptcha_middleware import require_recaptcha

@router.post("/forgot-password", dependencies=[Depends(require_recaptcha)])
def request_password_reset(...):
    # This endpoint is protected by reCAPTCHA
    pass
```

#### Frontend Request

```javascript
// Get reCAPTCHA v3 token for an action
let fetchOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
};

// Add reCAPTCHA token automatically
fetchOptions = await addRecaptchaToken('password_reset', fetchOptions);

// Send request
const response = await fetch('/api/auth/forgot-password', fetchOptions);
```

**Action Names:**
- `password_reset` - For forgot password requests
- `password_reset_confirm` - For password reset confirmation
- `create_org` - For organization creation
- Add more as needed for other protected endpoints

## Security Features

### 1. Score-Based Bot Detection
- reCAPTCHA v3 returns a score from 0.0 (bot) to 1.0 (human)
- Configurable threshold via `RECAPTCHA_MIN_SCORE` (default 0.5)
- No user interaction required (completely invisible)
- Analyzes user behavior patterns

### 2. Server-Side Verification
- All reCAPTCHA tokens are verified server-side
- Frontend cannot bypass verification
- Tokens are single-use only
- Action name verification prevents token reuse

### 3. IP Address Tracking
- User's IP is included in verification request
- Helps Google detect suspicious patterns
- Improves bot detection accuracy

### 4. Testing Mode
- reCAPTCHA automatically disabled when `TESTING=true`
- Tests run without reCAPTCHA overhead
- Prevents false failures in CI/CD

### 5. Fail-Safe Behavior
- If no secret key configured, requests are denied (fail closed)
- If reCAPTCHA API is unavailable (timeout), requests are allowed (fail open)
- Prevents legitimate users from being blocked due to infrastructure issues
- High-security scenarios can modify timeout behavior to fail closed

## Protected Endpoints

| Endpoint | Method | Action | Protection |
|----------|--------|--------|------------|
| `/api/auth/forgot-password` | POST | `password_reset` | reCAPTCHA v3 + Rate Limiting (3/hour) |
| `/api/auth/reset-password` | POST | `password_reset_confirm` | reCAPTCHA v3 + Rate Limiting (3/hour) |
| `/api/organizations/` | POST | `create_org` | reCAPTCHA v3 + Rate Limiting (2/hour) |

## Error Handling

### Client-Side

```javascript
try {
    let fetchOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    };

    // This handles reCAPTCHA gracefully - if disabled or unavailable, request proceeds
    fetchOptions = await addRecaptchaToken('password_reset', fetchOptions);

    const response = await fetch('/api/auth/forgot-password', fetchOptions);
    // Handle response...
} catch (error) {
    console.error('Request failed:', error);
    // Show user-friendly error message
}
```

### Server-Side

```python
@router.post("/endpoint", dependencies=[Depends(require_recaptcha)])
def protected_endpoint():
    # If we reach here, reCAPTCHA passed
    pass

# If reCAPTCHA fails:
# HTTP 400: "reCAPTCHA verification failed. Please try again."
```

## Troubleshooting

### reCAPTCHA Not Showing

1. Check site key is configured in `.env`
2. Verify domain is registered in reCAPTCHA admin
3. Check browser console for JavaScript errors

### Verification Always Failing

1. Verify secret key is correct
2. Check server can reach `https://www.google.com/recaptcha/api/siteverify`
3. Ensure clock is synchronized (reCAPTCHA tokens expire)

### Tests Failing

1. Ensure `TESTING=true` in test environment
2. Check `tests/conftest.py` sets environment variable
3. Verify reCAPTCHA is disabled in test mode

## Performance Considerations

### Impact
- **Frontend**: ~30KB additional JavaScript load (v3 is lighter than v2)
- **Backend**: ~100-300ms API call to Google per verification
- **User Experience**: Completely invisible - no user interaction required

### Optimization
- reCAPTCHA v3 script loads asynchronously and dynamically (only when enabled)
- Configuration fetched from backend on page load
- Token generated on-demand for each action
- Single async call per form submission

## Privacy & Compliance

### Data Collected by Google
- User IP address
- Browser fingerprint
- Mouse/click patterns
- Time spent on page

### GDPR/Privacy
- Add reCAPTCHA notice to privacy policy
- Inform users of Google's data collection
- reCAPTCHA is necessary for security (legitimate interest)

### Example Privacy Notice

```
We use Google reCAPTCHA to protect our website from spam and abuse.
reCAPTCHA collects hardware and software information such as device
and application data and sends it to Google for analysis.
See Google's Privacy Policy: https://policies.google.com/privacy
```

## Alternative: hCaptcha

To switch to hCaptcha (privacy-friendly alternative):

1. Get hCaptcha keys from https://www.hcaptcha.com/
2. Update `api/utils/recaptcha.py`:
   ```python
   RECAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"
   ```
3. Update frontend to load hCaptcha script
4. Minimal code changes required

## References

- [Google reCAPTCHA v3 Docs](https://developers.google.com/recaptcha/docs/v3)
- [reCAPTCHA Verification API](https://developers.google.com/recaptcha/docs/verify)
- [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
- [Privacy Policy](https://policies.google.com/privacy)
- [hCaptcha Alternative](https://www.hcaptcha.com/)

## Status

reCAPTCHA v3 is **ENABLED** in production and **DISABLED** during testing.

Current endpoints protected:
- ✅ Password reset request (`/api/auth/forgot-password`)
- ✅ Password reset confirmation (`/api/auth/reset-password`)
- ✅ Organization creation (`/api/organizations/`)

Future considerations:
- Login endpoint with adaptive challenge (low score after X failed attempts)
- User invitation acceptance
- Contact/feedback forms
- Admin actions (if exposed publicly)
