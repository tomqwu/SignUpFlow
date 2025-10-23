# Developer Quickstart: Security Hardening & Compliance

**Feature**: Security Hardening & Compliance
**Audience**: Developers testing security features locally
**Time**: 20-25 minutes

---

## Prerequisites

Before starting, ensure you have:
- ✅ Feature 003 (Production Infrastructure) complete (PostgreSQL + Redis running)
- ✅ Python 3.11+ with Poetry installed
- ✅ Redis running locally or via Docker (from Feature 003)
- ✅ PostgreSQL 14+ running locally or via Docker (from Feature 003)
- ✅ Test authenticator app installed (Google Authenticator, Authy, or `oathtool` CLI)

**Check Prerequisites**:
```bash
# Verify Redis running
docker exec signupflow-redis-1 redis-cli ping
# Expected: PONG

# Verify PostgreSQL running
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c "SELECT 1;"
# Expected: 1 row returned

# Verify Poetry installed
poetry --version
# Expected: Poetry version 1.0+

# (Optional) Install oathtool for CLI TOTP testing
sudo apt-get install oathtool  # Linux
brew install oath-toolkit        # macOS
```

---

## Quick Start (5 Minutes)

### Step 1: Install Security Dependencies

```bash
# Add security libraries to pyproject.toml
poetry add pyotp qrcode slowapi bleach python-multipart

# Install dependencies
poetry install

# Verify installation
poetry run python -c "import pyotp; print(pyotp.__version__)"
# Expected: Version number (e.g., 2.9.0)
```

**Dependencies Added**:
- `pyotp` - TOTP (RFC 6238) implementation for 2FA
- `qrcode` - QR code generation for authenticator app setup
- `slowapi` - Rate limiting middleware for FastAPI
- `bleach` - HTML sanitization for XSS prevention
- `python-multipart` - CSRF token handling (form data parsing)

---

### Step 2: Configure Environment Variables

Add security configuration to `.env` file:

```bash
# Add to existing .env file
cat >> .env << 'EOF'

# Security Configuration (Feature 004)
ENCRYPTION_KEY=your-32-byte-encryption-key-change-in-production
CSRF_SECRET_KEY=your-csrf-secret-key-change-in-production
SECURITY_SCAN_ENABLED=true

# Rate Limiting (uses Redis from Feature 003)
RATE_LIMIT_STORAGE_URL=${REDIS_URL}

# Audit Log Retention
AUDIT_LOG_RETENTION_DAYS=365

EOF

# Generate secure encryption keys
poetry run python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
poetry run python -c "import secrets; print('CSRF_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Update .env with generated keys (replace placeholder values)
```

**Environment Variables Explained**:
- `ENCRYPTION_KEY`: 32-byte key for encrypting 2FA secrets at rest (PostgreSQL pgcrypto)
- `CSRF_SECRET_KEY`: Secret key for CSRF token signing (if using signed tokens instead of Redis)
- `RATE_LIMIT_STORAGE_URL`: Redis URL for distributed rate limiting (same as REDIS_URL from Feature 003)
- `AUDIT_LOG_RETENTION_DAYS`: Audit log retention period (default: 365 days for SOC 2 compliance)

---

### Step 3: Run Database Migrations

Create database tables for security features:

```bash
# Create migration for security tables
poetry run alembic revision --autogenerate -m "Add security hardening tables"

# Review generated migration
ls -la alembic/versions/
# Expected: New migration file (e.g., 20251020_add_security_hardening_tables_abc123.py)

# Apply migration
poetry run alembic upgrade head

# Verify tables created
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c "\dt"
# Expected: audit_logs, two_factor_secrets, password_reset_tokens tables
```

**Tables Created**:
- `audit_logs` - Immutable audit trail for admin actions
- `two_factor_secrets` - Encrypted TOTP secrets for 2FA
- `password_reset_tokens` - Time-limited password reset tokens
- Rate limit data stored in Redis (no database table needed)

---

### Step 4: Start Application with Security Features

```bash
# Start development server with security enabled
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Or use Makefile
make run
```

**Verify security features loaded**:
```bash
# Check security headers
curl -I http://localhost:8000/health

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: default-src 'self'; ...

# Check rate limit headers
curl -I http://localhost:8000/api/people/?org_id=test_org \
  -H "Authorization: Bearer {valid_jwt_token}"

# Expected headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 1698156660
```

---

## Testing Security Features Locally

### 1. Test Rate Limiting

**Scenario**: Trigger login rate limit by failing 6 login attempts

```bash
# Attempt 1-5: Should succeed (with failure message)
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@example.com", "password": "wrong_password"}' \
    -w "\nAttempt $i: %{http_code}\n"
done

# Expected: 401 Unauthorized for each attempt

# Attempt 6: Should trigger rate limit
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "wrong_password"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: 429 Too Many Requests
# Body: {"error": "rate_limit_exceeded", "message": "Too many login attempts...", "retry_after_seconds": 900}
```

**Verify Rate Limit in Redis**:
```bash
docker exec signupflow-redis-1 redis-cli KEYS "rate_limit:login:*"
# Expected: rate_limit:login:127.0.0.1:20251020_1430

docker exec signupflow-redis-1 redis-cli GET "rate_limit:login:127.0.0.1:20251020_1430"
# Expected: 6 (number of attempts)
```

**Reset Rate Limit** (for testing):
```bash
# Delete rate limit key in Redis
docker exec signupflow-redis-1 redis-cli FLUSHDB
# WARNING: This clears ALL Redis data (including sessions)
```

---

### 2. Test Two-Factor Authentication (2FA)

**Scenario**: Enable 2FA, scan QR code, verify TOTP code

#### Step 1: Enable 2FA

```bash
# Login to get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "correct_password"}' \
  | jq -r '.token')

# Enable 2FA
curl -X POST http://localhost:8000/api/2fa/enable \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Expected response:
# {
#   "secret_key": "JBSWY3DPEHPK3PXP",
#   "qr_code_url": "/api/2fa/qr-code?temp_token=abc123",
#   "backup_codes": ["A1B2C3D4", "E5F6G7H8", ...],
#   "enabled": false
# }

# Save secret key for testing
SECRET="JBSWY3DPEHPK3PXP"
```

#### Step 2: Generate TOTP Code (CLI)

```bash
# Using oathtool (CLI authenticator)
oathtool --totp --base32 "$SECRET"
# Expected: 6-digit code (e.g., 123456)

# Or using Python
poetry run python -c "import pyotp; print(pyotp.TOTP('$SECRET').now())"
# Expected: 6-digit code
```

#### Step 3: Verify 2FA Code

```bash
# Get current TOTP code
CODE=$(oathtool --totp --base32 "$SECRET")

# Verify code to activate 2FA
curl -X POST http://localhost:8000/api/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}" \
  | jq

# Expected: {"verified": true, "enabled": true, "message": "..."}
```

#### Step 4: Test 2FA Login Flow

```bash
# Step 1: Initial login (returns temp token)
TEMP_TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "correct_password"}' \
  | jq -r '.temp_token')

echo "Temp token: $TEMP_TOKEN"
# Expected: requires_2fa=true, temp_token returned

# Step 2: Get new TOTP code
CODE=$(oathtool --totp --base32 "$SECRET")

# Step 3: Validate 2FA code
curl -X POST http://localhost:8000/api/auth/2fa-validate \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\": \"$TEMP_TOKEN\", \"code\": \"$CODE\"}" \
  | jq

# Expected: Full JWT token returned, user logged in
```

#### Step 5: Test Backup Code Login

```bash
# Login with backup code instead of TOTP
curl -X POST http://localhost:8000/api/auth/2fa-validate \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\": \"$TEMP_TOKEN\", \"code\": \"A1B2C3D4\"}" \
  | jq

# Expected: Login successful, backup code consumed (can't be reused)
```

---

### 3. Test CSRF Protection

**Scenario**: Submit form without CSRF token → blocked, then with token → succeeds

#### Step 1: Try Form Submission Without CSRF Token

```bash
# Attempt to create event without CSRF token
curl -X POST "http://localhost:8000/api/events?org_id=org_test_12345" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sunday Service", "datetime": "2025-10-27T10:00:00Z"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: 403 Forbidden
# Body: {"error": "csrf_token_invalid", "message": "CSRF token is invalid..."}
```

#### Step 2: Get CSRF Token

```bash
# Fetch CSRF token
CSRF_TOKEN=$(curl http://localhost:8000/api/csrf-token \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.csrf_token')

echo "CSRF Token: $CSRF_TOKEN"
# Expected: 43-character URL-safe base64 string
```

#### Step 3: Submit Form With CSRF Token

```bash
# Create event with CSRF token
curl -X POST "http://localhost:8000/api/events?org_id=org_test_12345" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sunday Service", "datetime": "2025-10-27T10:00:00Z"}' \
  | jq

# Expected: 201 Created, event created successfully
```

#### Step 4: Verify CSRF Token Single-Use

```bash
# Try to reuse same CSRF token
curl -X POST "http://localhost:8000/api/events?org_id=org_test_12345" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Another Event", "datetime": "2025-10-28T10:00:00Z"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: 403 Forbidden (token already consumed)
```

**Verify CSRF Token in Redis**:
```bash
# Check Redis for CSRF token
docker exec signupflow-redis-1 redis-cli KEYS "csrf:*"
# Expected: Empty (token deleted after use)
```

---

### 4. Test Audit Logging

**Scenario**: Perform admin action, verify audit log entry created

#### Step 1: Perform Admin Action

```bash
# Change user role (admin action that triggers audit log)
curl -X PUT http://localhost:8000/api/people/person_volunteer_11111 \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $(curl -s http://localhost:8000/api/csrf-token -H "Authorization: Bearer $TOKEN" | jq -r '.csrf_token')" \
  -H "Content-Type: application/json" \
  -d '{"roles": ["volunteer", "admin"]}' \
  | jq

# Expected: User role updated successfully
```

#### Step 2: Verify Audit Log Entry

```bash
# List audit logs
curl "http://localhost:8000/api/audit-logs?org_id=org_test_12345&limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Expected: Recent audit log entry with action_type="user_role_changed"
```

**Query PostgreSQL Directly**:
```bash
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c \
  "SELECT id, action_type, resource_type, changes FROM audit_logs ORDER BY timestamp DESC LIMIT 5;"

# Expected: Recent audit log entry visible
```

---

### 5. Test Security Headers

**Scenario**: Verify security headers present in all responses

```bash
# Check health endpoint headers
curl -I http://localhost:8000/health

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Verify CSP Blocks External Resources**:
```html
<!-- Try loading external script (should be blocked by CSP) -->
<script src="https://evil.com/malicious.js"></script>

<!-- Open browser console, expected error:
     "Refused to load the script 'https://evil.com/malicious.js' because it violates the following Content Security Policy directive: "script-src 'self' 'unsafe-inline'"
-->
```

---

## Running Security Tests

### Unit Tests

```bash
# Run security unit tests
poetry run pytest tests/unit/test_csrf_protection.py -v
poetry run pytest tests/unit/test_rate_limiter.py -v
poetry run pytest tests/unit/test_2fa_service.py -v

# Expected: All tests pass
```

### Integration Tests

```bash
# Run security integration tests
poetry run pytest tests/integration/test_csrf_middleware.py -v
poetry run pytest tests/integration/test_rate_limit_middleware.py -v
poetry run pytest tests/integration/test_2fa_endpoints.py -v
poetry run pytest tests/integration/test_audit_log_endpoints.py -v

# Expected: All tests pass
```

### E2E Tests

```bash
# Run security E2E tests (requires browser)
poetry run pytest tests/e2e/test_rate_limiting.py -v
poetry run pytest tests/e2e/test_2fa_workflow.py -v
poetry run pytest tests/e2e/test_csrf_protection.py -v
poetry run pytest tests/e2e/test_audit_logging.py -v

# Expected: All tests pass (Playwright browser automation)
```

### Security Scanning (Local)

```bash
# Run Bandit (Python SAST)
poetry run bandit -r api/ -ll
# Expected: No HIGH/MEDIUM severity issues

# Run Safety (dependency vulnerabilities)
poetry run safety check
# Expected: No known vulnerabilities in dependencies

# Run npm audit (frontend dependencies)
npm audit --audit-level=high
# Expected: No HIGH/CRITICAL vulnerabilities
```

---

## Common Development Tasks

### Reset Rate Limits

```bash
# Clear all rate limits (Redis flush)
docker exec signupflow-redis-1 redis-cli FLUSHDB

# WARNING: This also clears sessions and CSRF tokens
```

### Clear Audit Logs

```bash
# Truncate audit logs (PostgreSQL)
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c \
  "TRUNCATE TABLE audit_logs;"

# WARNING: This deletes ALL audit logs (for testing only)
```

### Disable 2FA for User

```bash
# Disable 2FA via SQL (for testing)
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c \
  "DELETE FROM two_factor_secrets WHERE person_id = 'person_admin_67890';"
```

### Generate Fake Audit Logs

```bash
# Insert test audit log (PostgreSQL)
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c \
  "INSERT INTO audit_logs (id, org_id, actor_person_id, action_type, resource_type, resource_id, changes, ip_address, timestamp)
   VALUES ('audit_test_001', 'org_test_12345', 'person_admin_67890', 'user_role_changed', 'person', 'person_volunteer_11111', '{\"before\": {\"roles\": [\"volunteer\"]}, \"after\": {\"roles\": [\"admin\"]}}', '127.0.0.1', NOW());"
```

---

## Troubleshooting

### Issue 1: Redis Connection Refused

**Symptom**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.`

**Solution**: Verify Redis container running

```bash
# Check Redis status
docker ps | grep redis

# If not running, start it
docker-compose up -d redis

# Verify connection
docker exec signupflow-redis-1 redis-cli ping
# Expected: PONG
```

---

### Issue 2: CSRF Token Always Invalid

**Symptom**: `403 Forbidden - csrf_token_invalid` even with valid token

**Solution**: Check Redis connection and token expiration

```bash
# Check if CSRF tokens being stored in Redis
docker exec signupflow-redis-1 redis-cli KEYS "csrf:*"

# If empty, check Redis connection in application
# Verify REDIS_URL in .env matches Redis container

# Check application logs for Redis errors
docker logs signupflow-app-1 | grep -i redis
```

---

### Issue 3: 2FA QR Code Not Displaying

**Symptom**: `GET /api/2fa/qr-code` returns 404

**Solution**: Verify qrcode library installed and secret exists

```bash
# Verify qrcode installed
poetry run python -c "import qrcode; print('qrcode installed')"

# Check 2FA secret in database
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c \
  "SELECT id, person_id, enabled FROM two_factor_secrets;"

# If no secret, re-enable 2FA via API
```

---

### Issue 4: Audit Logs Not Appearing

**Symptom**: Admin actions not creating audit log entries

**Solution**: Verify audit log middleware active

```bash
# Check audit_logs table exists
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c "\dt audit_logs"

# Check if middleware is registered in main.py
grep -r "audit_log" api/main.py

# Manually create test audit log
curl -X POST http://localhost:8000/api/internal/audit-logs \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

### Issue 5: Security Scanning Fails

**Symptom**: `bandit` or `safety` command not found

**Solution**: Install security tools

```bash
# Install Bandit
poetry add --group dev bandit

# Install Safety
poetry add --group dev safety

# Verify installation
poetry run bandit --version
poetry run safety --version
```

---

## Browser Testing (Manual)

### 1. Test 2FA Setup in Browser

1. Open http://localhost:8000/login
2. Login as admin user
3. Navigate to Settings → Security
4. Click "Enable Two-Factor Authentication"
5. Scan QR code with Google Authenticator (or use manual entry)
6. Enter 6-digit code from app
7. Verify backup codes displayed
8. Logout and login again → verify 2FA code required

### 2. Test Rate Limiting in Browser

1. Open http://localhost:8000/login
2. Enter wrong password 6 times
3. Verify lockout message: "Too many failed attempts. Try again in 30 minutes."
4. Verify login button disabled
5. Open browser DevTools → Network → check 429 response

### 3. Test CSRF Protection in Browser

1. Login to admin console
2. Open DevTools → Network tab
3. Create new event (form submission)
4. Verify `X-CSRF-Token` header sent in POST request
5. Manually delete CSRF token from request (via DevTools)
6. Verify 403 Forbidden error shown

### 4. Test Audit Log Viewer

1. Login as admin
2. Navigate to Admin Console → Audit Log tab
3. Perform admin action (create event, change user role)
4. Refresh Audit Log tab
5. Verify new log entry appears
6. Click "View Changes" → verify before/after values shown
7. Export CSV → verify download works

---

## Production Deployment Notes

**Environment Variables** (update for production):
```bash
# Production .env
ENCRYPTION_KEY=<generate-secure-32-byte-key>
CSRF_SECRET_KEY=<generate-secure-secret-key>
REDIS_URL=<production-redis-url>
DATABASE_URL=<production-postgres-url>
SECURITY_SCAN_ENABLED=true
AUDIT_LOG_RETENTION_DAYS=365
```

**Security Checklist**:
- [ ] ENCRYPTION_KEY rotated (not default value)
- [ ] CSRF_SECRET_KEY rotated (not default value)
- [ ] Redis TLS enabled in production
- [ ] PostgreSQL SSL enabled in production
- [ ] Security headers enforced (HSTS with long max-age)
- [ ] Rate limiting enabled on all endpoints
- [ ] Audit logs backed up regularly
- [ ] Security scanning integrated into CI/CD

---

## Next Steps

After local security testing complete:

1. **Run Full Test Suite**: `make test-all` to verify security features integrated
2. **Test Production Build**: Build Docker image and test in production-like environment
3. **Security Audit**: Run penetration testing (OWASP ZAP) against local instance
4. **Documentation Review**: Review user-facing security documentation (2FA setup guide)
5. **Team Training**: Train admins on audit log usage and security features

---

## Useful Commands

### Security Testing

```bash
# Test rate limiting
for i in {1..10}; do curl -X POST http://localhost:8000/api/auth/login -d '{"email":"test@example.com","password":"wrong"}' -H "Content-Type: application/json"; done

# Test CSRF protection
curl -X POST http://localhost:8000/api/events?org_id=test -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"title":"test"}'

# Generate TOTP code
oathtool --totp --base32 "JBSWY3DPEHPK3PXP"

# Check Redis keys
docker exec signupflow-redis-1 redis-cli KEYS "*"

# Check audit logs
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;"
```

### Database

```bash
# Connect to PostgreSQL
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow

# List security tables
\dt

# Count audit logs
SELECT COUNT(*) FROM audit_logs;

# Check 2FA users
SELECT person_id, enabled FROM two_factor_secrets;
```

### Redis

```bash
# Connect to Redis
docker exec -it signupflow-redis-1 redis-cli

# List all keys
KEYS *

# Check CSRF tokens
KEYS csrf:*

# Check rate limits
KEYS rate_limit:*

# Clear all data (WARNING)
FLUSHDB
```

---

## Resources

- **TOTP RFC 6238**: https://datatracker.ietf.org/doc/html/rfc6238
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **SOC 2 Controls**: https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome
- **GDPR Compliance**: https://gdpr.eu/
- **pyotp Documentation**: https://pyauth.github.io/pyotp/
- **slowapi Documentation**: https://github.com/laurents/slowapi

---

**Last Updated**: 2025-10-20
**Maintainer**: SignUpFlow Security Team
**Support**: security@signupflow.io
