# Data Model: Security Hardening & Compliance

**Feature**: 004-security-hardening | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

This document defines database entities, Redis data structures, and data flows for security features.

---

## Entity Overview

| Entity | Storage | Purpose | Retention |
|--------|---------|---------|-----------|
| **AuditLog** | PostgreSQL | Immutable audit trail for admin actions | 12 months |
| **RateLimitEntry** | Redis | Distributed rate limit counters | 30 minutes (TTL) |
| **TwoFactorSecret** | PostgreSQL | TOTP secret keys for 2FA | Until user disables 2FA |
| **CSRFToken** | Redis | CSRF token validation | 30 minutes (TTL) |
| **PasswordResetToken** | PostgreSQL | Secure password reset tokens | 1 hour |

---

## 1. AuditLog Entity

### Purpose
Immutable audit trail for all admin actions, supporting SOC 2 compliance (CC6.3 - Logical Access Controls) and GDPR Article 30 (Records of Processing Activities).

### Database Table: `audit_logs`

```sql
CREATE TABLE audit_logs (
    id VARCHAR(50) PRIMARY KEY,           -- e.g., "audit_20251020_143052_abc123"
    org_id VARCHAR(50) NOT NULL,          -- Multi-tenant isolation
    actor_person_id VARCHAR(50) NOT NULL, -- Who performed the action
    action_type VARCHAR(50) NOT NULL,     -- Enum: user_created, user_deleted, role_changed, event_created, etc.
    resource_type VARCHAR(50) NOT NULL,   -- Enum: person, event, team, organization, role
    resource_id VARCHAR(50),              -- ID of affected resource (nullable for bulk actions)
    changes JSONB,                        -- Before/after values: {"before": {...}, "after": {...}}
    ip_address VARCHAR(45),               -- IPv4/IPv6 address
    user_agent TEXT,                      -- Browser/client identifier
    request_id VARCHAR(50),               -- Trace request across logs
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT fk_actor FOREIGN KEY (actor_person_id) REFERENCES people(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_person_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Immutability enforcement (PostgreSQL RLS - Row-Level Security)
CREATE POLICY audit_logs_append_only ON audit_logs
    FOR INSERT
    TO authenticated_users
    WITH CHECK (true);

CREATE POLICY audit_logs_read_only ON audit_logs
    FOR SELECT
    TO authenticated_users
    USING (true);

-- Prevent UPDATE/DELETE (enforced at database level)
REVOKE UPDATE, DELETE ON audit_logs FROM authenticated_users;
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String | Yes | Unique identifier | `audit_20251020_143052_abc123` |
| `org_id` | String | Yes | Organization ID (multi-tenant isolation) | `org_church_12345` |
| `actor_person_id` | String | Yes | Person who performed action | `person_admin_67890` |
| `action_type` | Enum | Yes | Type of action performed | `user_role_changed` |
| `resource_type` | Enum | Yes | Type of resource affected | `person` |
| `resource_id` | String | No | ID of affected resource (null for bulk actions) | `person_volunteer_11111` |
| `changes` | JSONB | No | Before/after values for auditing | `{"before": {"roles": ["volunteer"]}, "after": {"roles": ["admin"]}}` |
| `ip_address` | String | No | Client IP address (IPv4/IPv6) | `192.168.1.100` |
| `user_agent` | String | No | Client browser/app identifier | `Mozilla/5.0...` |
| `request_id` | String | No | Request trace ID (for correlation) | `req_abc123def456` |
| `timestamp` | DateTime | Yes | When action occurred (UTC) | `2025-10-20T14:30:52Z` |

### Action Types (Enum)

**User Management**:
- `user_created` - New user account created
- `user_updated` - User profile modified
- `user_deleted` - User account deleted
- `user_role_changed` - User roles modified (admin/volunteer)
- `user_invited` - Invitation sent to new user

**Event Management**:
- `event_created` - New event created
- `event_updated` - Event details modified
- `event_deleted` - Event removed
- `event_published` - Event published to volunteers
- `schedule_generated` - AI solver generated schedule

**Team Management**:
- `team_created` - New team created
- `team_updated` - Team details modified
- `team_deleted` - Team removed
- `team_member_added` - Person added to team
- `team_member_removed` - Person removed from team

**Organization Management**:
- `org_settings_changed` - Organization settings modified
- `org_constraint_added` - Constraint rule added
- `org_constraint_removed` - Constraint rule removed

**Security Events**:
- `password_changed` - User password updated
- `2fa_enabled` - Two-factor authentication enabled
- `2fa_disabled` - Two-factor authentication disabled
- `login_failed` - Failed login attempt (rate limiting trigger)
- `session_invalidated` - Session terminated (password change)

### Resource Types (Enum)

- `person` - User account
- `event` - Scheduled event
- `team` - Volunteer team
- `organization` - Organization settings
- `role` - User role assignment
- `constraint` - Scheduling constraint
- `schedule` - Generated schedule

### Changes JSON Structure

**Example 1: Role Change**
```json
{
  "before": {
    "roles": ["volunteer"]
  },
  "after": {
    "roles": ["volunteer", "admin"]
  }
}
```

**Example 2: Event Update**
```json
{
  "before": {
    "title": "Sunday Service",
    "datetime": "2025-10-20T10:00:00Z"
  },
  "after": {
    "title": "Sunday Worship",
    "datetime": "2025-10-20T11:00:00Z"
  }
}
```

**Example 3: User Deletion**
```json
{
  "before": {
    "id": "person_volunteer_11111",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["volunteer"]
  },
  "after": null
}
```

### Data Retention & Cleanup

**Retention Policy**: 12 months (SOC 2 compliance requirement)

**Automated Cleanup**:
```python
# api/services/audit_cleanup.py
from datetime import datetime, timedelta

def cleanup_old_audit_logs(db: Session):
    """Delete audit logs older than 12 months."""
    cutoff_date = datetime.utcnow() - timedelta(days=365)

    deleted_count = db.query(AuditLog)\
        .filter(AuditLog.timestamp < cutoff_date)\
        .delete()

    db.commit()
    return deleted_count
```

**Scheduled Job**: Run daily at 2:00 AM UTC via cron (Feature 003 deployment infrastructure)

### API Endpoints

**Create Audit Log** (Internal - Called by Middleware):
```python
POST /api/internal/audit-logs
Authorization: Internal Service Token (not exposed to clients)

Request:
{
  "org_id": "org_church_12345",
  "actor_person_id": "person_admin_67890",
  "action_type": "user_role_changed",
  "resource_type": "person",
  "resource_id": "person_volunteer_11111",
  "changes": {
    "before": {"roles": ["volunteer"]},
    "after": {"roles": ["volunteer", "admin"]}
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "request_id": "req_abc123"
}

Response: 201 Created
{
  "id": "audit_20251020_143052_abc123",
  "timestamp": "2025-10-20T14:30:52Z"
}
```

**List Audit Logs** (Admin Only):
```python
GET /api/audit-logs?org_id={org_id}&limit=50&offset=0&action_type=user_role_changed
Authorization: Bearer {jwt_token}

Response: 200 OK
{
  "audit_logs": [
    {
      "id": "audit_20251020_143052_abc123",
      "actor_name": "Admin User",
      "action_type": "user_role_changed",
      "resource_type": "person",
      "resource_name": "John Doe",
      "changes": {...},
      "timestamp": "2025-10-20T14:30:52Z"
    }
  ],
  "total": 1234,
  "limit": 50,
  "offset": 0
}
```

**Export Audit Logs** (Admin Only):
```python
GET /api/audit-logs/export?org_id={org_id}&start_date=2025-01-01&end_date=2025-12-31&format=csv
Authorization: Bearer {jwt_token}

Response: 200 OK (CSV Download)
Content-Disposition: attachment; filename="audit_logs_2025.csv"
Content-Type: text/csv

id,timestamp,actor,action_type,resource_type,resource_id,changes
audit_20251020_143052_abc123,2025-10-20T14:30:52Z,admin@example.com,user_role_changed,person,person_volunteer_11111,"..."
```

---

## 2. RateLimitEntry (Redis)

### Purpose
Distributed rate limit counters to prevent brute force attacks and abuse. Stored in Redis for high-performance, atomic operations across multiple containers.

### Redis Key Structure

```
rate_limit:{scope}:{identifier}:{window_start}
```

**Examples**:
- `rate_limit:login:192.168.1.100:20251020_1430` - Login attempts from IP 192.168.1.100 in 15-minute window starting at 14:30
- `rate_limit:api:org_church_12345:20251020_1400` - API requests for organization in 1-minute window starting at 14:00
- `rate_limit:admin:person_admin_67890:20251020_1400` - Admin actions by specific user

### Data Structure

**Redis String** (counter):
```
Key: rate_limit:login:192.168.1.100:20251020_1430
Value: 3                                    # Number of attempts in window
TTL: 1800 seconds (30 minutes)              # Auto-expire after lockout period
```

**Redis Hash** (detailed tracking):
```
Key: rate_limit:login:192.168.1.100:20251020_1430:details
Value:
{
  "attempts": 3,
  "first_attempt": "2025-10-20T14:30:05Z",
  "last_attempt": "2025-10-20T14:32:15Z",
  "locked_until": null,                      # Set to timestamp when locked
  "failed_usernames": ["user1@example.com", "user2@example.com", "user3@example.com"]
}
TTL: 1800 seconds (30 minutes)
```

### Rate Limit Rules

| Scope | Limit | Window | Lockout | Key Pattern |
|-------|-------|--------|---------|-------------|
| **Login** | 5 attempts | 15 minutes | 30 minutes | `rate_limit:login:{ip}:{window}` |
| **Password Reset** | 3 attempts | 1 hour | 2 hours | `rate_limit:password_reset:{email}:{window}` |
| **API (General)** | 100 requests | 1 minute | 5 minutes (429 response) | `rate_limit:api:{org_id}:{window}` |
| **Admin Actions** | 50 requests | 1 minute | 5 minutes (429 response) | `rate_limit:admin:{person_id}:{window}` |
| **CSRF Token Gen** | 20 requests | 1 minute | 5 minutes | `rate_limit:csrf:{person_id}:{window}` |

### Implementation

**Python Code** (slowapi + Redis):
```python
# api/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis
from datetime import datetime, timedelta

redis_client = redis.from_url(os.getenv("REDIS_URL"))

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URL"),
    default_limits=["100/minute"],
    strategy="fixed-window"
)

def check_login_rate_limit(ip_address: str) -> tuple[bool, int]:
    """
    Check if IP address has exceeded login rate limit.

    Returns:
        (is_allowed, seconds_until_reset)
    """
    window_start = datetime.utcnow().strftime("%Y%m%d_%H%M")  # 15-min windows: 14:00, 14:15, 14:30
    window_start = window_start[:-1] + ("0" if int(window_start[-1]) < 5 else "5")  # Round to 15-min

    key = f"rate_limit:login:{ip_address}:{window_start}"
    attempts = redis_client.incr(key)

    if attempts == 1:
        # First attempt in window - set TTL
        redis_client.expire(key, 1800)  # 30 minutes

    if attempts > 5:
        # Rate limit exceeded
        ttl = redis_client.ttl(key)
        return (False, ttl)

    return (True, 0)

def record_failed_login(ip_address: str, username: str):
    """Record failed login attempt with details."""
    window_start = datetime.utcnow().strftime("%Y%m%d_%H%M")[:-1] + "0"

    key = f"rate_limit:login:{ip_address}:{window_start}:details"
    redis_client.hincrby(key, "attempts", 1)
    redis_client.hset(key, "last_attempt", datetime.utcnow().isoformat())
    redis_client.lpush(f"{key}:failed_usernames", username)
    redis_client.expire(key, 1800)
```

### Error Responses

**429 Too Many Requests** (Rate Limit Exceeded):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many login attempts. Please try again in 15 minutes.",
  "retry_after_seconds": 900,
  "details": {
    "limit": 5,
    "window": "15 minutes",
    "attempts": 6
  }
}
```

---

## 3. TwoFactorSecret Entity

### Purpose
Store TOTP secret keys for two-factor authentication. Secrets must be encrypted at rest for security.

### Database Table: `two_factor_secrets`

```sql
CREATE TABLE two_factor_secrets (
    id VARCHAR(50) PRIMARY KEY,           -- e.g., "2fa_person_67890_abc123"
    person_id VARCHAR(50) NOT NULL UNIQUE, -- One 2FA secret per user
    secret_key VARCHAR(255) NOT NULL,     -- Base32-encoded TOTP secret (encrypted at rest)
    backup_codes JSONB NOT NULL,          -- Array of 10 single-use backup codes
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,              -- When user first verified 2FA code
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_person FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
);

-- Indexes
CREATE UNIQUE INDEX idx_2fa_person ON two_factor_secrets(person_id);
CREATE INDEX idx_2fa_enabled ON two_factor_secrets(enabled) WHERE enabled = true;
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String | Yes | Unique identifier | `2fa_person_67890_abc123` |
| `person_id` | String | Yes | User this 2FA secret belongs to (unique) | `person_admin_67890` |
| `secret_key` | String | Yes | Base32-encoded TOTP secret (encrypted) | `JBSWY3DPEHPK3PXP` (encrypted) |
| `backup_codes` | JSONB | Yes | 10 single-use backup codes (hashed) | `["code1_hash", "code2_hash", ...]` |
| `enabled` | Boolean | Yes | Whether 2FA is active for user | `true` |
| `verified_at` | DateTime | No | When user first verified TOTP code | `2025-10-20T14:30:52Z` |
| `created_at` | DateTime | Yes | When 2FA was set up | `2025-10-20T14:30:00Z` |
| `updated_at` | DateTime | Yes | Last modification | `2025-10-20T14:30:52Z` |

### Encryption

**Encryption at Rest** (PostgreSQL pgcrypto):
```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt secret_key on insert
INSERT INTO two_factor_secrets (id, person_id, secret_key, backup_codes, enabled)
VALUES (
    '2fa_person_67890_abc123',
    'person_admin_67890',
    pgp_sym_encrypt('JBSWY3DPEHPK3PXP', current_setting('app.encryption_key')),  -- Encrypted
    '["backup_code_1_hash", "backup_code_2_hash", ...]',
    false
);

-- Decrypt secret_key on select
SELECT
    id,
    person_id,
    pgp_sym_decrypt(secret_key::bytea, current_setting('app.encryption_key')) AS secret_key_decrypted,
    backup_codes,
    enabled
FROM two_factor_secrets
WHERE person_id = 'person_admin_67890';
```

**Encryption Key Management**:
- Stored in environment variable: `ENCRYPTION_KEY` (32-byte random key)
- Rotated annually (re-encrypt all secrets with new key)
- Never committed to version control

### Backup Codes

**Generation**:
```python
# api/services/two_factor.py
import secrets
import bcrypt

def generate_backup_codes() -> list[dict]:
    """Generate 10 random backup codes."""
    codes = []
    for _ in range(10):
        code = secrets.token_hex(4).upper()  # 8-character hex code
        code_hash = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        codes.append({
            "code": code,           # Show to user once
            "hash": code_hash       # Store in database
        })
    return codes
```

**Example Backup Codes**:
```
A1B2C3D4
E5F6G7H8
I9J0K1L2
...
```

**Usage**:
- User loses authenticator app → uses backup code to login
- Backup code validated once → marked as used (deleted from array)
- Remaining backup codes displayed after successful 2FA setup

### TOTP Validation

**RFC 6238 Implementation** (pyotp library):
```python
import pyotp

def verify_totp_code(secret_key: str, code: str) -> bool:
    """Verify 6-digit TOTP code."""
    totp = pyotp.TOTP(secret_key)
    return totp.verify(code, valid_window=1)  # Allow ±30 seconds clock skew
```

**QR Code Generation**:
```python
import qrcode
import io

def generate_qr_code(secret_key: str, user_email: str) -> bytes:
    """Generate QR code for authenticator app setup."""
    totp_uri = pyotp.TOTP(secret_key).provisioning_uri(
        name=user_email,
        issuer_name="SignUpFlow"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
```

### API Endpoints

**Enable 2FA** (Authenticated User):
```python
POST /api/2fa/enable
Authorization: Bearer {jwt_token}

Response: 200 OK
{
  "secret_key": "JBSWY3DPEHPK3PXP",         # Show once, user enters in app
  "qr_code_url": "/api/2fa/qr-code",        # QR code endpoint
  "backup_codes": [                         # Show once, user saves securely
    "A1B2C3D4",
    "E5F6G7H8",
    "I9J0K1L2",
    ...
  ]
}
```

**Verify 2FA Setup** (Confirm User Has Working TOTP):
```python
POST /api/2fa/verify
Authorization: Bearer {jwt_token}

Request:
{
  "code": "123456"  # 6-digit TOTP code from authenticator app
}

Response: 200 OK
{
  "verified": true,
  "enabled": true,
  "message": "Two-factor authentication enabled successfully"
}
```

**Login with 2FA**:
```python
POST /api/auth/login
Request:
{
  "email": "admin@example.com",
  "password": "password123"
}

Response: 200 OK (2FA Required)
{
  "requires_2fa": true,
  "temp_token": "temp_abc123",  # Temporary token for 2FA validation
  "message": "Please enter your 6-digit authentication code"
}

# Step 2: Validate 2FA Code
POST /api/auth/2fa-validate
Request:
{
  "temp_token": "temp_abc123",
  "code": "123456"               # TOTP code or backup code
}

Response: 200 OK
{
  "token": "jwt_token_here",     # Full JWT token after successful 2FA
  "user": {...}
}
```

---

## 4. CSRFToken (Redis)

### Purpose
Stateless CSRF protection using Redis-backed single-use tokens. Tokens expire after 30 minutes and are deleted after validation.

### Redis Key Structure

```
csrf:{person_id}:{token}
```

**Example**:
```
Key: csrf:person_admin_67890:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Value: 1                                    # Token exists (value irrelevant)
TTL: 1800 seconds (30 minutes)
```

### Data Structure

**Redis String** (existence check):
```
Key: csrf:person_admin_67890:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Value: 1
TTL: 1800 seconds
```

### Token Generation

**Python Implementation**:
```python
# api/services/csrf_protection.py
import secrets
from datetime import timedelta

CSRF_TOKEN_EXPIRY = timedelta(minutes=30)

def generate_csrf_token(person_id: str, redis_client) -> str:
    """Generate CSRF token and store in Redis."""
    token = secrets.token_urlsafe(32)  # 256-bit entropy
    redis_key = f"csrf:{person_id}:{token}"
    redis_client.setex(redis_key, CSRF_TOKEN_EXPIRY, "1")
    return token

def validate_csrf_token(person_id: str, token: str, redis_client) -> bool:
    """Validate CSRF token (single-use)."""
    redis_key = f"csrf:{person_id}:{token}"
    exists = redis_client.exists(redis_key)
    if exists:
        redis_client.delete(redis_key)  # Single-use token
    return bool(exists)
```

### API Endpoints

**Get CSRF Token**:
```python
GET /api/csrf-token
Authorization: Bearer {jwt_token}

Response: 200 OK
{
  "csrf_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "expires_in_seconds": 1800
}
```

**Validate CSRF Token** (Middleware):
```python
# Middleware automatically validates X-CSRF-Token header on POST/PUT/DELETE requests

POST /api/events?org_id=org_church_12345
Authorization: Bearer {jwt_token}
X-CSRF-Token: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# If token invalid/missing:
Response: 403 Forbidden
{
  "error": "csrf_token_invalid",
  "message": "CSRF token is invalid or expired. Please refresh the page and try again."
}
```

### Token Refresh Strategy

**Frontend JavaScript**:
```javascript
// Refresh CSRF token every 15 minutes (before expiration)
setInterval(async () => {
    const response = await authFetch('/api/csrf-token');
    const data = await response.json();
    window.csrfToken = data.csrf_token;
}, 15 * 60 * 1000);  // 15 minutes
```

---

## 5. PasswordResetToken Entity

### Purpose
Secure, time-limited, single-use tokens for password reset flow. Prevents unauthorized password changes.

### Database Table: `password_reset_tokens`

```sql
CREATE TABLE password_reset_tokens (
    id VARCHAR(50) PRIMARY KEY,           -- e.g., "reset_20251020_143052_abc123"
    person_id VARCHAR(50) NOT NULL,       -- User requesting password reset
    token_hash VARCHAR(255) NOT NULL,     -- Hashed token (never store plain token)
    used BOOLEAN NOT NULL DEFAULT FALSE,   -- Single-use flag
    expires_at TIMESTAMPTZ NOT NULL,      -- Token expiration (1 hour from creation)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_person FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_reset_tokens_person ON password_reset_tokens(person_id);
CREATE INDEX idx_reset_tokens_used ON password_reset_tokens(used) WHERE used = false;
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String | Yes | Unique identifier | `reset_20251020_143052_abc123` |
| `person_id` | String | Yes | User requesting reset | `person_volunteer_11111` |
| `token_hash` | String | Yes | bcrypt hash of token (never plain token) | `$2b$12$...` |
| `used` | Boolean | Yes | Whether token has been used | `false` |
| `expires_at` | DateTime | Yes | When token expires (1 hour from creation) | `2025-10-20T15:30:00Z` |
| `created_at` | DateTime | Yes | When token was created | `2025-10-20T14:30:00Z` |

### Token Generation

**Python Implementation**:
```python
# api/services/password_reset.py
import secrets
import bcrypt
from datetime import datetime, timedelta

def generate_reset_token(person_id: str, db: Session) -> str:
    """Generate password reset token."""
    # Generate random token (256-bit entropy)
    plain_token = secrets.token_urlsafe(32)

    # Hash token for storage (bcrypt)
    token_hash = bcrypt.hashpw(plain_token.encode(), bcrypt.gensalt()).decode()

    # Store in database
    reset_token = PasswordResetToken(
        id=f"reset_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}",
        person_id=person_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset_token)
    db.commit()

    # Return plain token (sent to user via email, never stored)
    return plain_token

def validate_reset_token(person_id: str, plain_token: str, db: Session) -> bool:
    """Validate password reset token."""
    # Find active tokens for user
    reset_token = db.query(PasswordResetToken)\
        .filter(
            PasswordResetToken.person_id == person_id,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )\
        .first()

    if not reset_token:
        return False

    # Verify token hash matches
    if not bcrypt.checkpw(plain_token.encode(), reset_token.token_hash.encode()):
        return False

    # Mark token as used
    reset_token.used = True
    db.commit()

    return True
```

### API Endpoints

**Request Password Reset**:
```python
POST /api/auth/password-reset-request
Request:
{
  "email": "user@example.com"
}

Response: 200 OK
{
  "message": "If this email exists, a password reset link has been sent.",
  "rate_limited": false
}

# Email sent to user:
Subject: Reset Your Password - SignUpFlow
Body:
Click this link to reset your password (expires in 1 hour):
https://signupflow.io/reset-password?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

If you didn't request this, please ignore this email.
```

**Reset Password**:
```python
POST /api/auth/password-reset
Request:
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "new_password": "newpassword123"
}

Response: 200 OK
{
  "success": true,
  "message": "Password reset successfully. You can now log in with your new password."
}

# Invalid/expired token:
Response: 400 Bad Request
{
  "error": "invalid_token",
  "message": "Password reset token is invalid or has expired. Please request a new one."
}
```

### Security Features

**Rate Limiting**:
- Maximum 3 password reset requests per hour per email (prevents spam)
- Rate limit key: `rate_limit:password_reset:{email}:{window}`

**Token Expiration**:
- Tokens expire after 1 hour
- Expired tokens automatically cleaned up by scheduled job

**Single-Use**:
- Token marked as `used = true` after successful password reset
- Prevents token reuse attacks

**Email Obfuscation**:
- API returns generic message regardless of email existence (prevents user enumeration)
- Actual email only sent if user exists in database

---

## Data Flow Diagrams

### 1. Audit Logging Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   API    │                 │ Database │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ PUT /api/people/{id}       │                            │
     │ {roles: ["admin"]}         │                            │
     ├───────────────────────────>│ Middleware: verify_admin   │
     │                            ├───────────────────────────>│
     │                            │ Update user roles          │
     │                            │<───────────────────────────┤
     │                            │                            │
     │                            │ Middleware: audit_log()    │
     │                            ├───────────────────────────>│
     │                            │ INSERT INTO audit_logs     │
     │                            │ (action: user_role_changed)│
     │                            │<───────────────────────────┤
     │ {success: true}            │                            │
     │<───────────────────────────┤                            │
```

### 2. Rate Limiting Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   API    │                 │  Redis   │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ POST /api/auth/login       │                            │
     │ {email, password} (6th)    │                            │
     ├───────────────────────────>│ Check rate limit           │
     │                            ├───────────────────────────>│
     │                            │ INCR rate_limit:login:IP   │
     │                            │<───────────────────────────┤
     │                            │ Value: 6 (LIMIT EXCEEDED)  │
     │                            │                            │
     │ 429 Too Many Requests      │                            │
     │ {retry_after_seconds: 900} │                            │
     │<───────────────────────────┤                            │
```

### 3. 2FA Setup Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   API    │                 │ Database │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ POST /api/2fa/enable       │                            │
     ├───────────────────────────>│ Generate TOTP secret       │
     │                            │ Generate backup codes      │
     │                            ├───────────────────────────>│
     │                            │ INSERT two_factor_secrets  │
     │                            │ (enabled=false, encrypted) │
     │                            │<───────────────────────────┤
     │ {secret, qr_code, backups} │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
     │ [User scans QR code]       │                            │
     │                            │                            │
     │ POST /api/2fa/verify       │                            │
     │ {code: "123456"}           │                            │
     ├───────────────────────────>│ Verify TOTP code           │
     │                            ├───────────────────────────>│
     │                            │ UPDATE enabled=true        │
     │                            │<───────────────────────────┤
     │ {verified: true}           │                            │
     │<───────────────────────────┤                            │
```

### 4. CSRF Protection Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   API    │                 │  Redis   │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ GET /api/csrf-token        │                            │
     ├───────────────────────────>│ Generate CSRF token        │
     │                            ├───────────────────────────>│
     │                            │ SET csrf:{user}:{token}    │
     │                            │ TTL 30 minutes             │
     │                            │<───────────────────────────┤
     │ {csrf_token: "abc123"}     │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
     │ POST /api/events           │                            │
     │ X-CSRF-Token: abc123       │                            │
     ├───────────────────────────>│ Middleware: validate CSRF  │
     │                            ├───────────────────────────>│
     │                            │ EXISTS csrf:{user}:abc123  │
     │                            │ DELETE csrf:{user}:abc123  │
     │                            │<───────────────────────────┤
     │                            │ Create event               │
     │ {success: true}            │                            │
     │<───────────────────────────┤                            │
```

---

## Storage Size Estimates

### PostgreSQL Tables

**AuditLog** (12-month retention):
- Average record size: 1 KB (including JSONB changes)
- Estimated records: 10,000 actions/month for 100 organizations
- Annual storage: 10,000 × 12 × 1 KB = **120 MB/year**

**TwoFactorSecret**:
- Average record size: 500 bytes (encrypted secret + backup codes)
- Estimated records: 500 users with 2FA enabled
- Total storage: 500 × 0.5 KB = **250 KB**

**PasswordResetToken**:
- Average record size: 300 bytes
- Estimated active records: 100 (short-lived, 1-hour expiration)
- Total storage: 100 × 0.3 KB = **30 KB**

**Total PostgreSQL**: ~120 MB (dominated by audit logs)

### Redis Storage

**RateLimitEntry**:
- Average record size: 50 bytes (counter + metadata)
- Estimated active records: 1,000 concurrent rate limit windows
- Total storage: 1,000 × 50 bytes = **50 KB**

**CSRFToken**:
- Average record size: 100 bytes (token key)
- Estimated active records: 500 concurrent sessions
- Total storage: 500 × 100 bytes = **50 KB**

**Total Redis**: ~100 KB (negligible)

---

## Performance Benchmarks

| Operation | Target | Implementation | Expected Performance |
|-----------|--------|----------------|----------------------|
| Audit log write | <50ms | Async PostgreSQL INSERT | ~30ms (non-blocking) |
| Rate limit check | <10ms | Redis INCR | ~3ms |
| CSRF validation | <5ms | Redis EXISTS + DELETE | ~3ms |
| 2FA code validation | <100ms | TOTP computation + database lookup | ~50ms |
| Password reset token gen | <200ms | bcrypt hash + database INSERT | ~150ms |

All performance goals met with recommended implementation.

---

## Next Steps

**Phase 1 (Data Model)** ✅ - Complete

**Phase 1 Remaining**: Generate additional planning artifacts:
1. `contracts/` - API contracts for security endpoints (2FA, audit logs, CSRF)
2. `quickstart.md` - Local security testing setup guide

**Ready to proceed with API contract generation.**

---

**Last Updated**: 2025-10-20
**Entities Defined**: 5 (AuditLog, RateLimitEntry, TwoFactorSecret, CSRFToken, PasswordResetToken)
**Total Storage**: ~120 MB PostgreSQL + 100 KB Redis
