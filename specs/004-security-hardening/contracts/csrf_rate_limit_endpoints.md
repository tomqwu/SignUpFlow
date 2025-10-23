# API Contract: CSRF Protection & Rate Limiting Endpoints

**Feature**: Security Hardening & Compliance
**Purpose**: CSRF token management and rate limit status endpoints

---

## Endpoint Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/csrf-token` | GET | Required | Generate CSRF token for form submission |
| `/api/rate-limit/status` | GET | Required | Check current rate limit status |

**Note**: CSRF validation and rate limiting are implemented as middleware, automatically applied to relevant endpoints.

---

## 1. Get CSRF Token

### Request

**Method**: `GET`
**Path**: `/api/csrf-token`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**: None

**Example Request**:
```bash
curl https://signupflow.io/api/csrf-token \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "csrf_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "expires_in_seconds": 1800,
  "expires_at": "2025-10-20T15:00:00Z"
}
```

**Field Definitions**:
- `csrf_token`: 256-bit random token (URL-safe base64 encoded, 43 characters)
- `expires_in_seconds`: Time until token expires (30 minutes = 1800 seconds)
- `expires_at`: ISO 8601 timestamp when token expires (UTC)

**Error (401 Unauthorized)** - No Authentication:
```json
{
  "error": "authentication_required",
  "message": "Authentication required to generate CSRF token."
}
```

**Error (429 Too Many Requests)** - Rate Limit Exceeded:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many CSRF token requests. Please try again in 5 minutes.",
  "retry_after_seconds": 300
}
```

**Rate Limit**: 20 token requests per minute per user

---

## 2. Check Rate Limit Status

### Request

**Method**: `GET`
**Path**: `/api/rate-limit/status`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scope` | String | No | Rate limit scope: `login`, `api`, `admin`, `csrf` (default: api) |

**Example Request**:
```bash
# Check API rate limit status
curl "https://signupflow.io/api/rate-limit/status?scope=api" \
  -H "Authorization: Bearer eyJ0eXAi..."

# Check login rate limit status
curl "https://signupflow.io/api/rate-limit/status?scope=login" \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)** - Normal Status:
```json
{
  "scope": "api",
  "limit": 100,
  "window": "1 minute",
  "current_usage": 23,
  "remaining": 77,
  "reset_at": "2025-10-20T14:31:00Z",
  "reset_in_seconds": 45,
  "status": "ok"
}
```

**Success (200 OK)** - Near Limit:
```json
{
  "scope": "api",
  "limit": 100,
  "window": "1 minute",
  "current_usage": 95,
  "remaining": 5,
  "reset_at": "2025-10-20T14:31:00Z",
  "reset_in_seconds": 15,
  "status": "warning"
}
```

**Success (200 OK)** - Locked Out:
```json
{
  "scope": "login",
  "limit": 5,
  "window": "15 minutes",
  "current_usage": 6,
  "remaining": 0,
  "locked_until": "2025-10-20T15:00:00Z",
  "locked_for_seconds": 1800,
  "status": "locked",
  "message": "Too many failed login attempts. Account locked for 30 minutes."
}
```

**Field Definitions**:
- `scope`: Rate limit scope queried
- `limit`: Maximum allowed requests in window
- `window`: Time window for rate limit
- `current_usage`: Number of requests used in current window
- `remaining`: Requests remaining before limit hit
- `reset_at`: When current window resets (UTC)
- `reset_in_seconds`: Seconds until window reset
- `status`: `ok` (normal), `warning` (>90% used), `locked` (limit exceeded)
- `locked_until`: (Only if locked) When lockout expires
- `locked_for_seconds`: (Only if locked) Seconds remaining in lockout

**Error (401 Unauthorized)** - No Authentication:
```json
{
  "error": "authentication_required",
  "message": "Authentication required."
}
```

---

## CSRF Validation Middleware

### How CSRF Protection Works

**Middleware Applied To**:
- All `POST`, `PUT`, `DELETE` requests (state-changing operations)
- Excludes: `/api/auth/login`, `/api/auth/signup`, `/api/csrf-token` (no CSRF on authentication endpoints)

**Client Workflow**:
1. Get CSRF token: `GET /api/csrf-token`
2. Include token in request: `X-CSRF-Token: {token}` header
3. Server validates token: Checks Redis for token existence
4. Token consumed: Deleted from Redis after validation (single-use)

**Example Protected Request**:
```bash
# Get CSRF token
curl https://signupflow.io/api/csrf-token \
  -H "Authorization: Bearer eyJ0eXAi..." \
  | jq -r '.csrf_token'

# Use token in state-changing request
curl -X POST https://signupflow.io/api/events?org_id=org_church_12345 \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "X-CSRF-Token: a1b2c3d4e5f6g7h8..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Sunday Service", "datetime": "2025-10-27T10:00:00Z"}'
```

**CSRF Validation Error (403 Forbidden)**:
```json
{
  "error": "csrf_token_invalid",
  "message": "CSRF token is invalid, expired, or missing. Please refresh the page and try again.",
  "hint": "Include X-CSRF-Token header in POST/PUT/DELETE requests"
}
```

---

## Rate Limiting Middleware

### Rate Limit Rules

| Scope | Endpoint Pattern | Limit | Window | Lockout |
|-------|------------------|-------|--------|---------|
| **Login** | `/api/auth/login` | 5 attempts | 15 minutes | 30 minutes |
| **Password Reset** | `/api/auth/password-reset-request` | 3 attempts | 1 hour | 2 hours |
| **2FA Validation** | `/api/auth/2fa-validate` | 3 attempts | 15 minutes | 30 minutes |
| **API (General)** | `/api/*` (all endpoints) | 100 requests | 1 minute | 5 minutes |
| **Admin Actions** | `/api/events/*`, `/api/people/*` (POST/PUT/DELETE) | 50 requests | 1 minute | 5 minutes |
| **CSRF Token Gen** | `/api/csrf-token` | 20 requests | 1 minute | 5 minutes |

### Rate Limit Headers

**Response Headers** (included in ALL API responses):
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 77
X-RateLimit-Reset: 1698156660
```

**Header Definitions**:
- `X-RateLimit-Limit`: Maximum requests allowed in window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets

### Rate Limit Exceeded Response

**HTTP Status**: `429 Too Many Requests`

**Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698156660
Retry-After: 45
```

**Body**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 45 seconds.",
  "details": {
    "limit": 100,
    "window": "1 minute",
    "retry_after_seconds": 45,
    "reset_at": "2025-10-20T14:31:00Z"
  }
}
```

**Field Definitions**:
- `retry_after_seconds`: Seconds until client can retry
- `reset_at`: ISO 8601 timestamp when rate limit window resets

---

## Frontend Implementation

### CSRF Token Management

**JavaScript Module** (`frontend/js/csrf.js`):
```javascript
// CSRF Token Manager
class CSRFTokenManager {
    constructor() {
        this.token = null;
        this.expiresAt = null;
    }

    async getToken() {
        // Return cached token if still valid
        if (this.token && this.expiresAt && new Date() < this.expiresAt) {
            return this.token;
        }

        // Fetch new token
        const response = await authFetch('/api/csrf-token');
        const data = await response.json();

        this.token = data.csrf_token;
        this.expiresAt = new Date(data.expires_at);

        return this.token;
    }

    async refreshToken() {
        this.token = null;
        this.expiresAt = null;
        return await this.getToken();
    }

    attachToRequest(headers = {}) {
        return {
            ...headers,
            'X-CSRF-Token': this.token || ''
        };
    }
}

// Global instance
window.csrfManager = new CSRFTokenManager();

// Auto-refresh token every 15 minutes (before 30-minute expiration)
setInterval(() => {
    window.csrfManager.refreshToken();
}, 15 * 60 * 1000);
```

**Usage in Form Submission**:
```javascript
// frontend/js/app-admin.js
async function createEvent(eventData) {
    // Get CSRF token
    const csrfToken = await window.csrfManager.getToken();

    // Submit form with CSRF token
    const response = await authFetch(`/api/events?org_id=${currentUser.org_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(eventData)
    });

    if (response.status === 403) {
        // CSRF validation failed - refresh token and retry
        await window.csrfManager.refreshToken();
        showToast(i18n.t('messages.error.csrf_invalid'), 'error');
        return;
    }

    const data = await response.json();
    showToast(i18n.t('messages.success.event_created'), 'success');
}
```

### Rate Limit Handling

**JavaScript Handler** (`frontend/js/app.js`):
```javascript
// Handle rate limit errors globally
async function handleRateLimitError(response) {
    const data = await response.json();

    // Show user-friendly message
    showToast(
        i18n.t('messages.error.rate_limit_exceeded', {
            retry_after: Math.ceil(data.details.retry_after_seconds / 60)
        }),
        'error',
        10000  // Show for 10 seconds
    );

    // Disable submit buttons temporarily
    disableFormSubmits(data.details.retry_after_seconds);
}

// Disable form submits during rate limit
function disableFormSubmits(seconds) {
    const submitButtons = document.querySelectorAll('button[type="submit"]');

    submitButtons.forEach(btn => {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = i18n.t('common.buttons.please_wait');
    });

    setTimeout(() => {
        submitButtons.forEach(btn => {
            btn.disabled = false;
            btn.textContent = btn.dataset.originalText;
        });
    }, seconds * 1000);
}

// Enhanced authFetch with rate limit handling
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('authToken');

    if (!token) {
        throw new Error('No authentication token found');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    // Handle rate limit
    if (response.status === 429) {
        await handleRateLimitError(response);
        throw new Error('Rate limit exceeded');
    }

    // Handle CSRF error
    if (response.status === 403) {
        const data = await response.json();
        if (data.error === 'csrf_token_invalid') {
            // Refresh CSRF token and suggest retry
            await window.csrfManager.refreshToken();
        }
    }

    // Handle auth error
    if (response.status === 401) {
        localStorage.clear();
        navigateTo('/login');
        throw new Error('Authentication expired');
    }

    return response;
}
```

---

## Security Headers Middleware

### Headers Applied

**All API Responses Include**:
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Header Explanations**:

| Header | Purpose | Configuration |
|--------|---------|---------------|
| `Strict-Transport-Security` | Force HTTPS | 1 year max-age, include subdomains |
| `X-Content-Type-Options` | Prevent MIME sniffing | nosniff |
| `X-Frame-Options` | Prevent clickjacking | DENY (no iframes) |
| `X-XSS-Protection` | Enable XSS filter | Browser XSS protection |
| `Content-Security-Policy` | Restrict resource loading | Self-hosted only, no external scripts |
| `Referrer-Policy` | Control referer header | strict-origin-when-cross-origin |
| `Permissions-Policy` | Disable browser features | No geolocation, mic, camera |

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_csrf_protection.py
def test_generate_csrf_token():
    """Test CSRF token generation (256-bit entropy)."""

def test_validate_csrf_token_single_use():
    """Test CSRF token deleted after validation (single-use)."""

def test_csrf_token_expiration():
    """Test expired CSRF tokens rejected."""

# tests/unit/test_rate_limiter.py
def test_rate_limit_check():
    """Test rate limit counter increments correctly."""

def test_rate_limit_lockout():
    """Test lockout triggered after limit exceeded."""

def test_rate_limit_window_reset():
    """Test counter resets after window expires."""
```

### Integration Tests

```python
# tests/integration/test_csrf_middleware.py
def test_csrf_validation_blocks_invalid_token():
    """Test POST request without CSRF token returns 403."""

def test_csrf_validation_allows_valid_token():
    """Test POST request with valid CSRF token succeeds."""

def test_csrf_token_consumed_after_use():
    """Test CSRF token cannot be reused (single-use)."""

# tests/integration/test_rate_limit_middleware.py
def test_rate_limit_headers_included():
    """Test all responses include rate limit headers."""

def test_rate_limit_lockout_returns_429():
    """Test exceeding rate limit returns 429 status."""

def test_rate_limit_reset_after_window():
    """Test rate limit counter resets after window expires."""
```

### E2E Tests

```python
# tests/e2e/test_csrf_protection.py
def test_form_submission_with_csrf_token(page: Page):
    """
    Test CSRF protection workflow:
    1. Admin opens event creation form
    2. JavaScript fetches CSRF token automatically
    3. Submit form (CSRF token included in header)
    4. Form submission succeeds
    5. Verify event created
    """

def test_form_submission_without_csrf_token_blocked(page: Page):
    """
    Test CSRF protection blocks invalid submissions:
    1. Disable JavaScript CSRF token fetch
    2. Submit form without CSRF token
    3. Verify 403 error shown
    4. Verify error message: "CSRF token invalid"
    """

# tests/e2e/test_rate_limiting.py
def test_login_rate_limit_lockout(page: Page):
    """
    Test rate limit lockout:
    1. Attempt login with wrong password 6 times
    2. 6th attempt shows lockout message
    3. Verify "Try again in 30 minutes" displayed
    4. Verify login button disabled
    """
```

---

## Internationalization (i18n)

**Translation Keys**:
```json
// locales/en/messages.json
{
  "error": {
    "csrf_invalid": "Security token invalid. Please refresh the page and try again.",
    "csrf_expired": "Security token expired. Please refresh the page.",
    "rate_limit_exceeded": "Too many requests. Please try again in {retry_after} minutes.",
    "rate_limit_login": "Too many failed login attempts. Please try again in {retry_after} minutes."
  }
}
```

---

**Last Updated**: 2025-10-20
**Status**: Complete API specification for CSRF and rate limiting
**Related**: data-model.md (CSRFToken, RateLimitEntry), research.md (Redis-backed tokens)
