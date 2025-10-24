# API Contract: SMS Preferences Endpoints

**Feature**: SMS Notification System | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23

Phone verification, notification preference management, and TCPA compliance endpoints for volunteer SMS setup.

---

## Endpoints

### 1. Get SMS Preferences

**Endpoint**: `GET /api/sms/preferences`

**Purpose**: Retrieve volunteer's SMS preferences (phone number, notification types, verification status)

**Authentication**: Required (JWT Bearer token)

**Authorization**:
- Volunteers: Can view only own preferences
- Admins: Can view any volunteer's preferences in their organization

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID
- `person_id` (optional, integer): Person ID to query (admins only; volunteers auto-filtered to self)

**Response**:

**Success (200 OK)** - Preferences exist:
```json
{
  "person_id": 123,
  "phone_number": "+15551234567",
  "phone_number_masked": "+1•••••••4567",
  "verified": true,
  "notification_types": ["assignment", "reminder", "broadcast"],
  "opt_in_date": "2024-12-15T10:30:00Z",
  "opt_out_date": null,
  "language": "en",
  "timezone": "America/New_York",
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-15T10:30:00Z"
}
```

**Success (200 OK)** - No preferences (never set up SMS):
```json
{
  "person_id": 123,
  "phone_number": null,
  "verified": false,
  "notification_types": [],
  "opt_in_date": null,
  "opt_out_date": null,
  "language": "en",
  "timezone": "UTC"
}
```

**Field Descriptions**:
- `phone_number`: Full E.164 format phone number (admins only)
- `phone_number_masked`: Masked phone for volunteers viewing own preferences
- `verified`: Phone verification status via SMS code
- `notification_types`: Array of enabled notification types
- `opt_in_date`: When volunteer completed SMS verification (TCPA audit trail)
- `opt_out_date`: When volunteer replied STOP (null if not opted out)

**Error Responses**:

**403 Forbidden** - Volunteer trying to access other volunteer's preferences:
```json
{
  "detail": "Access denied: can only view your own preferences"
}
```

---

### 2. Update SMS Preferences

**Endpoint**: `PUT /api/sms/preferences`

**Purpose**: Update notification types (which message types volunteer wants to receive)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Self-service (volunteers update own preferences)

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "notification_types": ["assignment", "reminder"],
  "language": "es"
}
```

**Field Specifications**:
- `notification_types` (required, array[string]): Notification types to enable
  - Valid values: `assignment`, `reminder`, `broadcast`, `system`
  - Empty array `[]` disables all notifications (keeps phone verified for re-enable)
- `language` (optional, string, default: current): Language for SMS content (`en`, `es`)

**Validation Rules**:
1. Phone must be verified before updating notification types
2. Cannot update if opted out (opt_out_date not null) - must re-verify phone
3. Notification types must be valid values
4. Language must be supported (`en`, `es`)

**Response**:

**Success (200 OK)**:
```json
{
  "person_id": 123,
  "phone_number_masked": "+1•••••••4567",
  "verified": true,
  "notification_types": ["assignment", "reminder"],
  "language": "es",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

**Error Responses**:

**400 Bad Request** - Phone not verified:
```json
{
  "detail": "Phone number must be verified before updating preferences. Complete verification first."
}
```

**400 Bad Request** - Opted out:
```json
{
  "detail": "SMS notifications are disabled (opted out). Verify phone number again to re-enable."
}
```

**422 Unprocessable Entity** - Invalid notification type:
```json
{
  "detail": "Invalid notification type: 'marketing'. Valid types: assignment, reminder, broadcast, system"
}
```

---

### 3. Send Verification Code

**Endpoint**: `POST /api/sms/preferences/verify-phone`

**Purpose**: Send 6-digit SMS verification code to phone number (TCPA opt-in step 1)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Self-service (volunteers verify own phone)

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "phone_number": "+15551234567"
}
```

**Field Specifications**:
- `phone_number` (required, string): E.164 format phone number (+1XXXXXXXXXX for US)

**Validation Rules**:
1. Phone number must be valid E.164 format
2. Phone number must be mobile (no landlines - validated via Twilio Lookup API)
3. Phone number must not be in use by another verified volunteer in same organization
4. Rate limit: Max 3 verification attempts per 10 minutes per volunteer
5. Previous verification code expires when new one sent

**Response**:

**Success (200 OK)**:
```json
{
  "message": "Verification code sent to +15551234567",
  "phone_number_masked": "+1•••••••4567",
  "expires_at": "2025-01-01T10:10:00Z",
  "attempts_remaining": 3
}
```

**Field Descriptions**:
- `expires_at`: Code expiration time (10 minutes from send)
- `attempts_remaining`: Number of verification attempts left before rate limit

**Error Responses**:

**400 Bad Request** - Invalid phone format:
```json
{
  "detail": "Invalid phone number format. Must be E.164 format (e.g., +15551234567)"
}
```

**400 Bad Request** - Landline detected:
```json
{
  "detail": "Landlines cannot receive SMS. Please enter a mobile phone number."
}
```

**409 Conflict** - Phone already verified by another volunteer:
```json
{
  "detail": "This phone number is already registered to another volunteer in your organization"
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Too many verification attempts. Please try again in 10 minutes.",
  "retry_after": "2025-01-01T10:10:00Z"
}
```

---

### 4. Confirm Verification Code

**Endpoint**: `POST /api/sms/preferences/confirm-verification`

**Purpose**: Confirm 6-digit code and complete SMS opt-in (TCPA opt-in step 2)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Self-service (volunteers verify own phone)

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**:
```json
{
  "phone_number": "+15551234567",
  "code": 123456,
  "notification_types": ["assignment", "reminder", "broadcast"]
}
```

**Field Specifications**:
- `phone_number` (required, string): Phone number being verified (must match pending verification)
- `code` (required, integer): 6-digit verification code received via SMS
- `notification_types` (required, array[string]): Initial notification types to enable

**Validation Rules**:
1. Phone number must have pending verification code
2. Code must match stored verification code
3. Code must not be expired (10-minute expiration)
4. Maximum 3 attempts per verification code (security)
5. After 3 failed attempts, must request new code
6. Notification types must be valid values

**Response**:

**Success (201 Created)** - SMS preferences created and verified:
```json
{
  "person_id": 123,
  "phone_number_masked": "+1•••••••4567",
  "verified": true,
  "notification_types": ["assignment", "reminder", "broadcast"],
  "opt_in_date": "2025-01-01T10:00:00Z",
  "language": "en",
  "timezone": "America/New_York",
  "confirmation_sms_sent": true
}
```

**Field Descriptions**:
- `opt_in_date`: Timestamp of successful opt-in (TCPA audit trail)
- `confirmation_sms_sent`: Confirmation SMS sent with opt-out instructions (TCPA requirement)

**Error Responses**:

**400 Bad Request** - Invalid code:
```json
{
  "detail": "Invalid verification code",
  "attempts_remaining": 2
}
```

**400 Bad Request** - Code expired:
```json
{
  "detail": "Verification code expired. Request a new code."
}
```

**429 Too Many Requests** - Too many failed attempts:
```json
{
  "detail": "Too many failed attempts. Request a new verification code.",
  "max_attempts": 3
}
```

---

### 5. Delete SMS Preferences (Opt-Out)

**Endpoint**: `DELETE /api/sms/preferences`

**Purpose**: Manually opt out of SMS notifications via UI (alternative to replying STOP)

**Authentication**: Required (JWT Bearer token)

**Authorization**: Self-service (volunteers delete own preferences)

**Request Parameters**:

**Query Parameters**:
- `org_id` (required, string): Organization ID

**Request Body**: None

**Response**:

**Success (200 OK)**:
```json
{
  "message": "SMS notifications disabled successfully",
  "phone_number_masked": "+1•••••••4567",
  "opt_out_date": "2025-01-01T10:00:00Z",
  "alternative_notifications": "You will receive email notifications instead"
}
```

**Error Responses**:

**404 Not Found** - No SMS preferences to delete:
```json
{
  "detail": "No SMS preferences found for this volunteer"
}
```

---

## Phone Verification Flow

### Complete TCPA-Compliant Opt-In Workflow

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: User Enters Phone Number                             │
│ POST /api/sms/preferences/verify-phone                        │
│ {phone_number: "+15551234567"}                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Twilio Lookup API Validation                         │
│ - Validate E.164 format                                       │
│ - Check carrier type (reject landlines)                       │
│ - Get carrier name for logging                                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Generate & Send 6-Digit Code                         │
│ - Generate: secrets.randbelow(900000) + 100000               │
│ - Store: sms_verification_codes table (expires: 10 min)      │
│ - Send SMS: "SignUpFlow verification code: 123456"           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: User Enters Code                                     │
│ POST /api/sms/preferences/confirm-verification               │
│ {phone_number: "+15551234567", code: 123456,                │
│  notification_types: ["assignment", "reminder"]}             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Verify Code & Create Preferences                     │
│ - Check code matches (max 3 attempts)                        │
│ - Check not expired (10-minute TTL)                          │
│ - Create sms_preferences record (verified=true)              │
│ - Log opt-in action (TCPA audit trail)                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 6: Send Confirmation SMS (TCPA Requirement)             │
│ "SMS notifications enabled for SignUpFlow.                   │
│  Reply STOP to unsubscribe anytime."                         │
└──────────────────────────────────────────────────────────────┘
```

### Security Measures

1. **Rate Limiting**: Max 3 verification requests per 10 minutes per volunteer
2. **Code Expiration**: Verification codes expire after 10 minutes
3. **Attempt Limit**: Max 3 failed code entry attempts before requiring new code
4. **Landline Detection**: Twilio Lookup API rejects landlines (SMS-incompatible)
5. **Phone Uniqueness**: One phone number per verified volunteer per organization
6. **Audit Trail**: All opt-in/opt-out actions logged with timestamp

---

## TCPA Compliance

### Legal Requirements

**Telephone Consumer Protection Act (TCPA)** regulates SMS marketing/notifications in the US:

1. **Explicit Opt-In Required**: Volunteer must actively consent to receive SMS
2. **Clear Disclosure**: Must inform what types of messages they'll receive
3. **Opt-Out Instructions**: Every message must provide way to unsubscribe
4. **Prompt Opt-Out Processing**: STOP replies must disable SMS within 60 seconds
5. **Audit Trail**: Must maintain records of opt-in/opt-out actions
6. **Non-Commercial Use**: Event notifications are informational (not marketing)

**Penalties**: $500-$1,500 per violation

### Compliance Implementation

| Requirement | Implementation | Endpoint |
|-------------|----------------|----------|
| Explicit Opt-In | Two-step verification (enter phone → confirm code) | POST /api/sms/preferences/verify-phone |
| Clear Disclosure | Notification types selection during opt-in | POST /api/sms/preferences/confirm-verification |
| Opt-Out Instructions | Confirmation SMS: "Reply STOP to unsubscribe anytime" | Auto-sent after verification |
| Prompt Opt-Out | STOP keyword disables SMS within 60 seconds | POST /webhooks/twilio/incoming (see webhooks-api.md) |
| Audit Trail | opt_in_date, opt_out_date in sms_preferences table | Database logging |
| Re-Opt-In | START keyword re-enables (requires verification again) | POST /webhooks/twilio/incoming |

---

## Frontend Integration

### Phone Verification UI Workflow

```javascript
// frontend/js/sms-preferences.js

async function startPhoneVerification() {
    const phoneNumber = document.getElementById('phone-input').value;

    // Step 1: Send verification code
    const response = await authFetch(`${API_BASE_URL}/sms/preferences/verify-phone?org_id=${currentUser.org_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber })
    });

    if (response.ok) {
        const data = await response.json();
        showToast(i18n.t('sms.verification_code_sent'), 'success');
        showVerificationCodeInput();  // Display code entry UI
        startCodeExpirationTimer(data.expires_at);  // 10-minute countdown
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
    }
}

async function confirmVerificationCode() {
    const phoneNumber = document.getElementById('phone-input').value;
    const code = document.getElementById('code-input').value;
    const notificationTypes = getSelectedNotificationTypes();  // Checkboxes

    // Step 2: Confirm code
    const response = await authFetch(`${API_BASE_URL}/sms/preferences/confirm-verification?org_id=${currentUser.org_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone_number: phoneNumber,
            code: parseInt(code),
            notification_types: notificationTypes
        })
    });

    if (response.ok) {
        showToast(i18n.t('sms.verification_complete'), 'success');
        loadSmsPreferences();  // Reload UI with verified preferences
    } else {
        const error = await response.json();
        showToast(error.detail, 'error');
        if (error.attempts_remaining !== undefined) {
            showAttemptsRemaining(error.attempts_remaining);
        }
    }
}

async function updateNotificationPreferences() {
    const notificationTypes = getSelectedNotificationTypes();

    const response = await authFetch(`${API_BASE_URL}/sms/preferences?org_id=${currentUser.org_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notification_types: notificationTypes })
    });

    if (response.ok) {
        showToast(i18n.t('sms.preferences_updated'), 'success');
    }
}
```

---

## Error Handling

### Common Error Scenarios

| Scenario | Status Code | Error Message | User Action |
|----------|-------------|---------------|-------------|
| Invalid phone format | 400 | "Invalid phone number format. Must be E.164 format" | Re-enter phone in +1XXXXXXXXXX format |
| Landline entered | 400 | "Landlines cannot receive SMS. Please enter mobile number" | Provide mobile phone number |
| Phone already used | 409 | "This phone number is already registered to another volunteer" | Contact administrator |
| Code expired | 400 | "Verification code expired. Request a new code" | Click "Resend Code" |
| Wrong code | 400 | "Invalid verification code" (attempts_remaining: 2) | Re-enter code (2 attempts left) |
| Too many attempts | 429 | "Too many failed attempts. Request a new code" | Click "Resend Code" after 10 min |
| Rate limit hit | 429 | "Too many verification attempts. Try again in 10 minutes" | Wait 10 minutes |

---

## Testing

### Unit Tests

```python
# tests/unit/test_sms_preferences.py

def test_verify_phone_rejects_landline():
    """Test that landline phone numbers are rejected."""
    response = client.post(
        "/api/sms/preferences/verify-phone?org_id=test_org",
        json={"phone_number": "+15551234567"},  # Mock landline
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Landlines cannot receive SMS" in response.json()["detail"]

def test_verification_code_expires_after_10_minutes():
    """Test that verification codes expire."""
    # Send verification code
    # Wait 11 minutes (mocked)
    # Attempt to confirm code
    # Should return 400 with "expired" message
```

### Integration Tests

```python
# tests/integration/test_sms_preferences.py

def test_complete_phone_verification_flow(client, auth_headers):
    """Test full phone verification flow."""
    # Step 1: Send verification code
    response = client.post(
        "/api/sms/preferences/verify-phone?org_id=test_org",
        json={"phone_number": "+15551234567"},
        headers=auth_headers
    )
    assert response.status_code == 200

    # Step 2: Get code from database (test helper)
    code = get_verification_code_from_db(person_id=123)

    # Step 3: Confirm code
    response = client.post(
        "/api/sms/preferences/confirm-verification?org_id=test_org",
        json={
            "phone_number": "+15551234567",
            "code": code,
            "notification_types": ["assignment", "reminder"]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["verified"] == True
```

### E2E Tests

```python
# tests/e2e/test_sms_preferences.py

def test_phone_verification_complete_workflow(page: Page):
    """Test complete phone verification from UI."""
    page.goto("http://localhost:8000/app/settings")
    page.locator('[data-i18n="settings.tabs.sms"]').click()

    # Enter phone number
    page.locator('#phone-input').fill("+15551234567")
    page.locator('[data-i18n="sms.send_code"]').click()

    # Wait for code sent message
    expect(page.locator('.success-message')).to_contain_text("Verification code sent")

    # Enter code (retrieved from test database)
    code = get_test_verification_code()
    page.locator('#code-input').fill(str(code))

    # Select notification types
    page.locator('#notification-assignment').check()
    page.locator('#notification-reminder').check()

    # Confirm verification
    page.locator('[data-i18n="sms.confirm_code"]').click()

    # Verify success
    expect(page.locator('.success-message')).to_contain_text("SMS notifications enabled")
    expect(page.locator('#phone-verified-badge')).to_be_visible()
```

---

## Related Documentation

- **Data Model**: `../data-model.md` - sms_preferences, sms_verification_codes schemas
- **SMS API**: `sms-api.md` - Message sending endpoints that check preferences
- **Webhooks API**: `webhooks-api.md` - STOP/START keyword processing for opt-out
- **Quick Start**: `../quickstart.md` - Twilio Lookup API setup for phone validation
- **Research**: `../research.md` - TCPA compliance decision analysis

---

**Last Updated**: 2025-10-23
**API Version**: v1
**Feature**: 019 - SMS Notification System
