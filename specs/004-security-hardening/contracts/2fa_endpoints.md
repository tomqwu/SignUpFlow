# API Contract: Two-Factor Authentication (2FA) Endpoints

**Feature**: Security Hardening & Compliance
**Purpose**: TOTP-based two-factor authentication for admin accounts

---

## Endpoint Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/2fa/enable` | POST | Required | Generate 2FA secret and QR code |
| `/api/2fa/verify` | POST | Required | Verify TOTP code and activate 2FA |
| `/api/2fa/disable` | POST | Required | Disable 2FA for user account |
| `/api/2fa/qr-code` | GET | Required | Get QR code image for authenticator app |
| `/api/2fa/backup-codes` | GET | Required | Get new backup codes (regenerate) |
| `/api/auth/2fa-validate` | POST | None | Validate 2FA code during login |

---

## 1. Enable 2FA

### Request

**Method**: `POST`
**Path**: `/api/2fa/enable`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Query Parameters**: None

**Request Body**: None

**Example Request**:
```bash
curl -X POST https://signupflow.io/api/2fa/enable \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Response

**Success (200 OK)**:
```json
{
  "secret_key": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "/api/2fa/qr-code?temp_token=abc123",
  "backup_codes": [
    "A1B2C3D4",
    "E5F6G7H8",
    "I9J0K1L2",
    "M3N4O5P6",
    "Q7R8S9T0",
    "U1V2W3X4",
    "Y5Z6A7B8",
    "C9D0E1F2",
    "G3H4I5J6",
    "K7L8M9N0"
  ],
  "enabled": false,
  "message": "Two-factor authentication initiated. Please scan the QR code with your authenticator app and verify with a code."
}
```

**Field Definitions**:
- `secret_key`: Base32-encoded TOTP secret (show once, user manually enters if QR fails)
- `qr_code_url`: Temporary URL to fetch QR code image (1-hour expiration)
- `backup_codes`: 10 single-use recovery codes (show once, user saves securely)
- `enabled`: false until user verifies TOTP code
- `message`: User-friendly instruction

**Error (400 Bad Request)** - 2FA Already Enabled:
```json
{
  "error": "2fa_already_enabled",
  "message": "Two-factor authentication is already enabled for your account. Disable it first to re-enable."
}
```

**Error (401 Unauthorized)** - No Authentication:
```json
{
  "error": "authentication_required",
  "message": "Authentication required. Please log in."
}
```

---

## 2. Verify 2FA (Activate)

### Request

**Method**: `POST`
**Path**: `/api/2fa/verify`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "code": "123456"
}
```

**Field Definitions**:
- `code`: 6-digit TOTP code from authenticator app (required, string)

**Example Request**:
```bash
curl -X POST https://signupflow.io/api/2fa/verify \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

### Response

**Success (200 OK)**:
```json
{
  "verified": true,
  "enabled": true,
  "message": "Two-factor authentication enabled successfully. You will now be required to enter a code from your authenticator app when logging in."
}
```

**Error (400 Bad Request)** - Invalid Code:
```json
{
  "error": "invalid_code",
  "message": "The authentication code is incorrect. Please try again."
}
```

**Error (400 Bad Request)** - 2FA Not Initiated:
```json
{
  "error": "2fa_not_initiated",
  "message": "Please enable 2FA first before verifying."
}
```

**Error (422 Unprocessable Entity)** - Missing Code:
```json
{
  "error": "validation_error",
  "message": "Code is required.",
  "field": "code"
}
```

---

## 3. Disable 2FA

### Request

**Method**: `POST`
**Path**: `/api/2fa/disable`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "code": "123456",
  "password": "current_password"
}
```

**Field Definitions**:
- `code`: 6-digit TOTP code or backup code (required, string)
- `password`: Current account password (required, string, security verification)

**Example Request**:
```bash
curl -X POST https://signupflow.io/api/2fa/disable \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"code": "123456", "password": "mypassword"}'
```

### Response

**Success (200 OK)**:
```json
{
  "disabled": true,
  "message": "Two-factor authentication has been disabled for your account."
}
```

**Error (400 Bad Request)** - Invalid Code:
```json
{
  "error": "invalid_code",
  "message": "The authentication code is incorrect."
}
```

**Error (403 Forbidden)** - Incorrect Password:
```json
{
  "error": "invalid_password",
  "message": "Incorrect password. Please try again."
}
```

**Error (400 Bad Request)** - 2FA Not Enabled:
```json
{
  "error": "2fa_not_enabled",
  "message": "Two-factor authentication is not enabled for your account."
}
```

---

## 4. Get QR Code

### Request

**Method**: `GET`
**Path**: `/api/2fa/qr-code`
**Authentication**: Required (temporary token OR JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
- `temp_token`: Temporary token from `/api/2fa/enable` response (optional if using JWT)

**Example Request**:
```bash
# Using JWT token
curl https://signupflow.io/api/2fa/qr-code \
  -H "Authorization: Bearer eyJ0eXAi..."

# Using temporary token (for immediate display after enable)
curl https://signupflow.io/api/2fa/qr-code?temp_token=abc123
```

### Response

**Success (200 OK)**:
```http
Content-Type: image/png
Content-Disposition: inline; filename="2fa-qr-code.png"

[PNG Image Data - QR Code containing TOTP provisioning URI]
```

**TOTP Provisioning URI Format**:
```
otpauth://totp/SignUpFlow:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=SignUpFlow
```

**Error (401 Unauthorized)** - No Authentication:
```json
{
  "error": "authentication_required",
  "message": "Authentication required."
}
```

**Error (404 Not Found)** - No 2FA Secret:
```json
{
  "error": "2fa_not_found",
  "message": "No two-factor authentication setup found. Please enable 2FA first."
}
```

---

## 5. Get Backup Codes (Regenerate)

### Request

**Method**: `GET`
**Path**: `/api/2fa/backup-codes`
**Authentication**: Required (JWT Bearer token)

**Headers**:
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body** (for security verification):
```json
{
  "password": "current_password"
}
```

**Example Request**:
```bash
curl https://signupflow.io/api/2fa/backup-codes \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{"password": "mypassword"}'
```

### Response

**Success (200 OK)**:
```json
{
  "backup_codes": [
    "N1O2P3Q4",
    "R5S6T7U8",
    "V9W0X1Y2",
    "Z3A4B5C6",
    "D7E8F9G0",
    "H1I2J3K4",
    "L5M6N7O8",
    "P9Q0R1S2",
    "T3U4V5W6",
    "X7Y8Z9A0"
  ],
  "message": "New backup codes generated. Your old backup codes have been invalidated. Please save these codes securely."
}
```

**Field Definitions**:
- `backup_codes`: 10 new single-use recovery codes (previous codes invalidated)
- `message`: User warning about old codes being invalid

**Error (403 Forbidden)** - Incorrect Password:
```json
{
  "error": "invalid_password",
  "message": "Incorrect password. Password verification required to regenerate backup codes."
}
```

**Error (400 Bad Request)** - 2FA Not Enabled:
```json
{
  "error": "2fa_not_enabled",
  "message": "Two-factor authentication is not enabled."
}
```

---

## 6. Validate 2FA During Login

### Request

**Method**: `POST`
**Path**: `/api/auth/2fa-validate`
**Authentication**: None (uses temporary token from initial login)

**Headers**:
```http
Content-Type: application/json
```

**Request Body**:
```json
{
  "temp_token": "temp_abc123def456",
  "code": "123456"
}
```

**Field Definitions**:
- `temp_token`: Temporary token from initial login response (required, string)
- `code`: 6-digit TOTP code OR 8-character backup code (required, string)

**Example Request**:
```bash
curl -X POST https://signupflow.io/api/auth/2fa-validate \
  -H "Content-Type: application/json" \
  -d '{"temp_token": "temp_abc123", "code": "123456"}'
```

### Response

**Success (200 OK)** - Full Authentication Complete:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "person_admin_67890",
    "email": "admin@example.com",
    "name": "Admin User",
    "org_id": "org_church_12345",
    "roles": ["admin"]
  },
  "organization": {
    "id": "org_church_12345",
    "name": "First Baptist Church"
  },
  "message": "Login successful"
}
```

**Error (400 Bad Request)** - Invalid Code:
```json
{
  "error": "invalid_code",
  "message": "The authentication code is incorrect. Please try again.",
  "attempts_remaining": 2
}
```

**Error (429 Too Many Requests)** - Rate Limit Exceeded:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many failed 2FA attempts. Please try again in 15 minutes.",
  "retry_after_seconds": 900
}
```

**Error (401 Unauthorized)** - Invalid/Expired Temp Token:
```json
{
  "error": "invalid_temp_token",
  "message": "Temporary token is invalid or expired. Please log in again."
}
```

---

## Login Flow with 2FA

### Standard Login Flow (2FA Enabled Users)

**Step 1: Initial Login**

```bash
POST /api/auth/login
{
  "email": "admin@example.com",
  "password": "password123"
}

Response: 200 OK (2FA Required)
{
  "requires_2fa": true,
  "temp_token": "temp_abc123def456",
  "message": "Please enter your 6-digit authentication code from your authenticator app."
}
```

**Step 2: Validate 2FA Code**

```bash
POST /api/auth/2fa-validate
{
  "temp_token": "temp_abc123def456",
  "code": "123456"
}

Response: 200 OK (Full Authentication)
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...},
  "organization": {...}
}
```

**Step 3: Client Stores JWT Token**

```javascript
localStorage.setItem('authToken', response.token);
localStorage.setItem('currentUser', JSON.stringify(response.user));
```

---

## Security Features

### Rate Limiting

**Login Endpoint** (`/api/auth/login`):
- 5 failed attempts per 15 minutes → 30-minute lockout
- Rate limit key: `rate_limit:login:{ip_address}:{window}`

**2FA Validation** (`/api/auth/2fa-validate`):
- 3 failed attempts per 15 minutes → 30-minute lockout
- Rate limit key: `rate_limit:2fa:{temp_token}:{window}`

### Temporary Token Security

**Temp Token Format**:
- Generated on successful password validation (Step 1)
- Valid for 5 minutes only
- Single-use (invalidated after successful 2FA validation)
- Stored in Redis: `temp_2fa:{token}` → `{person_id}` (TTL: 5 minutes)

### Backup Code Usage

**Backup Code Validation**:
- User submits backup code instead of TOTP code
- Code is hashed and compared against stored hashes
- Successful use → code marked as used (removed from array)
- Remaining backup codes displayed after login

**Security Warning**:
```json
{
  "token": "eyJ0eXAi...",
  "user": {...},
  "warning": "You used a backup code to log in. Consider regenerating backup codes in Settings.",
  "backup_codes_remaining": 7
}
```

---

## Internationalization (i18n)

All user-facing messages support 6 languages (EN, ES, PT, ZH-CN, ZH-TW, KO).

**Translation Keys**:
```json
// locales/en/auth.json
{
  "2fa": {
    "enable_success": "Two-factor authentication enabled successfully",
    "enter_code": "Please enter your 6-digit authentication code",
    "invalid_code": "The authentication code is incorrect. Please try again.",
    "scan_qr": "Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)",
    "backup_codes_title": "Backup Codes",
    "backup_codes_warning": "Save these codes securely. Each code can only be used once.",
    "disable_confirm": "Are you sure you want to disable two-factor authentication? This will reduce your account security."
  }
}
```

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_2fa_service.py
def test_generate_totp_secret():
    """Test TOTP secret generation (32-character base32)."""

def test_verify_totp_code_valid():
    """Test valid TOTP code verification."""

def test_verify_totp_code_invalid():
    """Test invalid TOTP code rejection."""

def test_verify_totp_code_clock_skew():
    """Test ±30 second clock skew tolerance."""

def test_generate_backup_codes():
    """Test 10 backup code generation."""

def test_backup_code_validation():
    """Test backup code hashing and validation."""
```

### Integration Tests

```python
# tests/integration/test_2fa_endpoints.py
def test_enable_2fa_returns_secret_and_qr():
    """Test POST /api/2fa/enable returns secret, QR URL, backup codes."""

def test_verify_2fa_activates_account():
    """Test POST /api/2fa/verify with valid code sets enabled=true."""

def test_disable_2fa_requires_password():
    """Test POST /api/2fa/disable rejects without password."""

def test_2fa_login_flow_complete():
    """Test complete login → temp token → 2FA validation → full JWT."""
```

### E2E Tests

```python
# tests/e2e/test_2fa_workflow.py
def test_2fa_setup_workflow(page: Page):
    """
    Complete 2FA setup workflow:
    1. User clicks Enable 2FA in settings
    2. Scan QR code (simulate with manual secret entry)
    3. Enter TOTP code from authenticator app
    4. Verify backup codes displayed
    5. Verify 2FA badge shown in UI
    """

def test_2fa_login_workflow(page: Page):
    """
    Complete 2FA login workflow:
    1. User enters email/password
    2. 2FA prompt appears
    3. User enters TOTP code
    4. User successfully logged in
    5. Verify schedule visible
    """

def test_2fa_backup_code_login(page: Page):
    """
    Test backup code login:
    1. User loses authenticator app
    2. Enter email/password
    3. Use backup code instead of TOTP
    4. Successfully logged in
    5. Warning message about backup codes displayed
    """
```

---

## Frontend Implementation Example

**2FA Setup UI** (`frontend/index.html`):
```html
<div id="2fa-setup-modal" class="modal">
  <h2 data-i18n="auth.2fa.enable_title">Enable Two-Factor Authentication</h2>

  <div id="qr-code-section">
    <p data-i18n="auth.2fa.scan_qr">Scan this QR code with your authenticator app</p>
    <img id="qr-code-img" src="" alt="2FA QR Code">
    <p>
      <span data-i18n="auth.2fa.manual_entry">Or enter this code manually</span>:
      <code id="manual-secret"></code>
    </p>
  </div>

  <div id="backup-codes-section" style="display:none;">
    <h3 data-i18n="auth.2fa.backup_codes_title">Backup Codes</h3>
    <p data-i18n="auth.2fa.backup_codes_warning">Save these securely</p>
    <ul id="backup-codes-list"></ul>
    <button data-i18n="common.buttons.download">Download</button>
  </div>

  <div id="verify-section">
    <label>
      <span data-i18n="auth.2fa.enter_code">Enter 6-digit code</span>:
      <input type="text" id="2fa-verify-code" maxlength="6" pattern="[0-9]{6}">
    </label>
    <button id="verify-2fa-btn" data-i18n="common.buttons.verify">Verify</button>
  </div>
</div>
```

**JavaScript Handler** (`frontend/js/app-user.js`):
```javascript
// Enable 2FA
async function enable2FA() {
    const response = await authFetch('/api/2fa/enable', { method: 'POST' });
    const data = await response.json();

    // Display QR code
    document.getElementById('qr-code-img').src = data.qr_code_url;
    document.getElementById('manual-secret').textContent = data.secret_key;

    // Store backup codes for later display
    window.backupCodes = data.backup_codes;
}

// Verify 2FA code
async function verify2FA() {
    const code = document.getElementById('2fa-verify-code').value;

    const response = await authFetch('/api/2fa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    });

    const data = await response.json();

    if (data.verified) {
        // Show backup codes
        const backupCodesList = document.getElementById('backup-codes-list');
        window.backupCodes.forEach(code => {
            const li = document.createElement('li');
            li.textContent = code;
            backupCodesList.appendChild(li);
        });

        document.getElementById('backup-codes-section').style.display = 'block';
        showToast(i18n.t('auth.2fa.enable_success'), 'success');
    } else {
        showToast(i18n.t('auth.2fa.invalid_code'), 'error');
    }
}
```

---

**Last Updated**: 2025-10-20
**Status**: Complete API specification for 2FA endpoints
**Related**: data-model.md (TwoFactorSecret entity), research.md (TOTP implementation decision)
