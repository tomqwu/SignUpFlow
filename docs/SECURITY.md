# SignUpFlow Security Guide

> Historical security guide. Its production-ready and compliance statements below are
> not current certification. Use [API_AUTHORIZATION.md](API_AUTHORIZATION.md) for the
> maintained route and browser request-integrity policy, [TESTING.md](TESTING.md) for
> local evidence, and [ROADMAP.md](ROADMAP.md) for unresolved release evidence.

**Last Updated:** 2024-10-24
**Version:** 1.0.0
**Status:** Historical snapshot, not production certification

## Current Maintained Browser Controls

Unsafe requests under `/auth/`, `/a/`, and `/v/` require an exact same-origin `Origin`
header and a valid signed double-submit CSRF token. The shared middleware injects the
token into standard forms and HTMX requests and returns `403` before route execution for
missing, foreign, mismatched, or forged input. SameSite cookies remain defense in depth.

Browser login, signup, invitation, and password-reset routes use the same operation-specific
rate-limit operations as their API counterparts. Development limits are thread-safe and
process-local; production requires atomic Redis counters shared across workers and fails
protected requests closed with a retryable `503` during storage loss.
Forwarded client addresses are trusted only when the direct peer is listed in
`TRUSTED_PROXY_IPS`; otherwise the peer address is used for both limits and audit logs.
Owned Redis acceptance covers multi-worker quota enforcement, limiter outage, and recovery.
Proxy/TLS deployment verification remains external release evidence under #271.

Current monitoring behavior supersedes the historical examples below. `/health` is
dependency-free process liveness; `/ready` is sanitized database readiness and is the
container health target. Production logs are structured on stdout and require an exact
`RELEASE_SHA`. `api/observability.py` initializes optional Sentry reporting with default
PII and tracing disabled. Local signal tests do not prove external operator receipt.

Current dependency, secret, container, SBOM, exception, and Pages action policy lives in
[SECURITY_VALIDATION.md](SECURITY_VALIDATION.md). It uses local-only exact-revision
evidence and supersedes the historical `poetry audit` and automated-scanner proposals
below. It is not a compliance certification or deployed-environment assessment.

---

## 🛡️ Security Overview

SignUpFlow implements comprehensive security measures addressing OWASP Top 10 vulnerabilities and compliance requirements (SOC 2, HIPAA, GDPR ready).

**Security Features Implemented:**
- ✅ JWT Authentication with bcrypt password hashing
- ✅ Role-Based Access Control (RBAC)
- ✅ Rate Limiting (prevent brute force attacks)
- ✅ Security Headers (HSTS, CSP, X-Frame-Options)
- ✅ Audit Logging (compliance trail)
- ✅ Input Validation & Sanitization (prevent XSS/SQL injection)
- ✅ Database Connection Security
- ✅ Error Tracking (Sentry integration)
- ✅ Health Check Monitoring

---

## 📋 Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Rate Limiting](#rate-limiting)
3. [Security Headers](#security-headers)
4. [Audit Logging](#audit-logging)
5. [Input Validation](#input-validation)
6. [Error Tracking & Monitoring](#error-tracking--monitoring)
7. [Security Configuration](#security-configuration)
8. [Compliance](#compliance)
9. [Security Best Practices](#security-best-practices)
10. [Incident Response](#incident-response)

---

## Authentication & Authorization

### JWT (JSON Web Tokens)

**Implementation:** `api/core/security.py`

**Configuration:**
```python
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
SECRET_KEY = os.getenv("SECRET_KEY")  # Must be 32+ characters
```

**Token Structure:**
```json
{
  "sub": "person_admin_123456",
  "exp": 1730000000,
  "iat": 1729914000
}
```

**Security Features:**
- Tokens expire after 24 hours
- HMAC-SHA256 signing algorithm
- Secure secret key from environment (never hardcoded)
- Automatic validation on every protected endpoint

### Password Hashing (bcrypt)

**Implementation:** `api/core/security.py`

**Configuration:**
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Features:**
- 12 rounds of bcrypt (industry standard)
- Automatic salting
- One-way hashing (passwords cannot be decrypted)
- Constant-time comparison (prevent timing attacks)

**Example:**
```python
# Hash password on signup
hashed_password = hash_password("user_password")

# Verify password on login
is_valid = verify_password("user_password", hashed_password)
```

### Role-Based Access Control (RBAC)

**Implementation:** `api/core/security.py`, `api/dependencies.py`

**Roles:**
- `volunteer`: Basic access (view schedule, manage own availability)
- `admin`: Full access (create events, manage users, run solver)

**Permission Checks:**
```python
# Require authentication
current_user: Person = Depends(get_current_user)

# Require admin role
admin: Person = Depends(verify_admin_access)

# Verify organization membership
verify_org_member(user, org_id)
```

**27 RBAC Tests:** `tests/e2e/test_rbac_security.py`

---

## Rate Limiting

**Implementation:** `api/utils/rate_limit_middleware.py`, `api/utils/rate_limiter.py`

**Purpose:** Bound repeated authentication operations. Development uses a process-local
token bucket; production requires an atomic Redis fixed-window counter shared by every
application process. This remains an application control, not a network DDoS service.

### Default Rate Limits

| Operation | Default limit | Window |
|----------|-------|--------|
| Login | 5 attempts | 5 minutes |
| Signup | 3 attempts | 1 hour |
| Create organization | 2 attempts | 1 hour |
| Create invitation | 10 attempts | 5 minutes |
| Verify invitation | 10 attempts | 1 minute |
| Request password reset | 3 attempts | 1 hour |
| Confirm password reset | 5 attempts | 5 minutes |
| Refresh token | 60 attempts | 1 hour |

### Configuration

**Environment Variables:** see `.env.example` for every per-operation maximum/window.
```bash
RATE_LIMIT_LOGIN_MAX=5
RATE_LIMIT_LOGIN_WINDOW=300
TRUSTED_PROXY_IPS=10.0.0.0/8
RATE_LIMIT_STORAGE=redis
REDIS_URL=redis://:password@redis:6379/0
```

Production startup rejects missing, unauthenticated, or non-Redis quota storage. If
Redis becomes unavailable, protected operations return 503 with `Retry-After: 5`
instead of allowing unlimited requests. Only direct peers listed in
`TRUSTED_PROXY_IPS` may supply a forwarded-address chain.

There is no Redis-backed limiter in the current application. Do not configure a Redis URL
or run multiple workers expecting a shared quota until #261's distributed work is complete.

### Rate Limit Response

**HTTP 429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Try again in 14 minutes.",
  "retry_after": 840
}
```

## Security Headers

**Implementation:** `api/utils/security_headers_middleware.py`

**All responses include security headers:**

### Headers Applied

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
X-XSS-Protection: 1; mode=block
```

### Purpose

| Header | Protection |
|--------|------------|
| **HSTS** | Force HTTPS for 1 year (prevent downgrade attacks) |
| **CSP** | Prevent XSS by restricting resource loading |
| **X-Frame-Options** | Prevent clickjacking attacks |
| **X-Content-Type-Options** | Prevent MIME sniffing attacks |
| **Referrer-Policy** | Control referrer information leakage |
| **Permissions-Policy** | Disable unnecessary browser features |

### Configuration

```bash
# .env
SECURITY_HSTS_ENABLED=true
SECURITY_HSTS_MAX_AGE=31536000  # 1 year
SECURITY_CSP_ENABLED=true
SECURITY_FRAME_OPTIONS=DENY
```

---

## Audit Logging

**Implementation:** `api/utils/audit_logger.py`

**Purpose:** Compliance trail (SOC 2, HIPAA, GDPR), security monitoring

### What Gets Logged

**Admin Actions (High Sensitivity):**
- User creation, modification, deletion
- Role changes
- Event creation, modification, deletion
- Team management
- Invitation sending/revoking
- Schedule generation (solver runs)
- Organization settings changes

### Audit Log Schema

```python
class AuditLog:
    id: str                    # "audit_xxxxx"
    timestamp: datetime        # ISO 8601 UTC
    user_id: str              # Who performed action
    user_email: str           # Email at time of action
    organization_id: str      # Organization context
    action: str               # "user.create", "event.update", etc.
    resource_type: str        # "person", "event", "team"
    resource_id: str          # ID of affected resource
    details: dict             # Before/after values, context
    ip_address: str           # Client IP
    user_agent: str           # Browser/client
    status: str               # "success", "failure", "denied"
    error_message: str        # If status = "failure"
```

### Usage Example

```python
from api.utils.audit_logger import log_audit_from_request

@router.post("/api/people")
def create_person(
    request: Request,
    person_data: PersonCreate,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    # Create person
    new_person = Person(**person_data.dict())
    db.add(new_person)
    db.commit()

    # Log audit event
    log_audit_from_request(
        db=db,
        request=request,
        action="person.create",
        user_id=admin.id,
        user_email=admin.email,
        organization_id=person_data.org_id,
        resource_type="person",
        resource_id=new_person.id,
        details={"email": person_data.email, "roles": person_data.roles},
        status="success"
    )

    return {"id": new_person.id}
```

### Querying Audit Logs

```python
# Get all actions by user
logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()

# Get all changes to resource
logs = db.query(AuditLog).filter(
    AuditLog.resource_type == "event",
    AuditLog.resource_id == event_id
).all()

# Compliance report (last 90 days)
logs = db.query(AuditLog).filter(
    AuditLog.organization_id == org_id,
    AuditLog.timestamp >= datetime.utcnow() - timedelta(days=90)
).all()
```

### Retention Policy

- **Active logs:** Stored in PostgreSQL database
- **Retention:** 90 days (configurable via `AUDIT_LOG_RETENTION_DAYS`)
- **Archive:** Old logs exported to S3/cloud storage (future feature)
- **Immutable:** Audit logs cannot be modified after creation

---

## Input Validation

**Implementation:** Pydantic schemas (`api/schemas/`), `bleach` library

### Backend Validation (Pydantic)

```python
from pydantic import BaseModel, Field, validator
import bleach

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(None, max_length=5000)
    datetime: datetime
    duration: int = Field(..., ge=15, le=480)  # 15 min to 8 hours

    @validator('title')
    def sanitize_title(cls, v):
        # Remove HTML tags, prevent XSS
        return bleach.clean(v, tags=[], strip=True)

    @validator('description')
    def sanitize_description(cls, v):
        if v is None:
            return v
        # Allow basic formatting tags only
        return bleach.clean(
            v,
            tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
            strip=True
        )
```

### SQL Injection Prevention

**ORM Protection:** SQLAlchemy automatically parameterizes queries

```python
# ✅ SAFE - Uses parameterized query
person = db.query(Person).filter(Person.email == user_email).first()

# ❌ NEVER DO THIS - Vulnerable to SQL injection
db.execute(f"SELECT * FROM persons WHERE email = '{user_email}'")
```

### XSS Prevention

**Sanitization:** All user input is sanitized before storage

```python
import bleach

# Remove all HTML tags
clean_text = bleach.clean(user_input, tags=[], strip=True)

# Allow only safe HTML tags
safe_html = bleach.clean(
    user_input,
    tags=['p', 'br', 'strong', 'em'],
    strip=True
)
```

---

## Error Tracking & Monitoring

### Sentry Integration

**Implementation:** `api/main.py`

**Configuration:**
```bash
# .env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
ENVIRONMENT=production  # development, staging, or production
```

**Features:**
- Automatic error capture and stack traces
- Performance monitoring (10% sample rate)
- Release tracking
- User context (without PII)
- Database query monitoring (SQLAlchemy integration)

**Initialization:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if sentry_dsn and environment != "development":
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,   # Privacy protection
        attach_stacktrace=True,
    )
```

### Health Check Monitoring

**Endpoint:** `GET /health`

**Response (Healthy):**
```json
{
  "status": "healthy",
  "service": "signupflow-api",
  "version": "1.0.0",
  "database": "connected"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "service": "signupflow-api",
  "version": "1.0.0",
  "database": "disconnected",
  "error": "Connection timeout"
}
```

**Status Code:** 503 Service Unavailable (unhealthy)

**Monitoring Tools:**
- Docker health checks: `HEALTHCHECK CMD curl -f http://localhost:8000/health`
- Uptime Robot: Monitor `/health` endpoint every 5 minutes
- Better Stack: Log aggregation and alerting
- Sentry: Error tracking and performance monitoring

---

## Security Configuration

### Environment Variables Checklist

**Required for Production:**

```bash
# Security (CRITICAL - Generate strong values!)
SECRET_KEY=<random-32-char-string>  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Database (Use strong passwords!)
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis (Use strong password!)
REDIS_PASSWORD=<strong-password>
REDIS_URL=redis://:password@host:6379/0

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
ENVIRONMENT=production

# Features
RATE_LIMITING_ENABLED=true
SESSION_TTL_HOURS=24

# SSL/HTTPS (via reverse proxy - Nginx, Cloudflare)
# No environment variables needed - handled at infrastructure level
```

### Never Commit to Version Control

**Secrets to NEVER commit:**
- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- Database connection strings
- `STRIPE_SECRET_KEY` (live keys)
- `SENDGRID_API_KEY`
- `TWILIO_AUTH_TOKEN`
- `SENTRY_DSN` (optional, but recommended to keep secret)

**Already in `.gitignore`:**
- `.env`
- `.env.local`
- `.env.production`
- `*.key`
- `*.pem`

### Generate Strong Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -hex 20
```

---

## Compliance

### GDPR (General Data Protection Regulation)

SignUpFlow has not completed a GDPR or SOC 2 assessment. Existing product controls include
authenticated profile access, member deletion endpoints, calendar export, selected audit
events, and cancellation timestamps. They do not establish legal consent, complete data
subject rights, eventual deletion, log/backup retention, production TLS, or encryption at
rest. The local SQLite recovery bundle is AES-GCM encrypted, but production database and
backup controls remain unverified under #268/#269.

### SOC 2 Type II Readiness

The repository contains RBAC, audit, health, validation, and local monitoring primitives.
No SOC 2 readiness or operating-effectiveness conclusion has been established.

### HIPAA Compliance (if handling health data)

**Required but not certified here:**
- Access controls and a reviewed authorization model
- Complete audit coverage and retention
- Production encryption in transit and at rest
- ⚠️ Encryption at rest (enable PostgreSQL encryption)
- ⚠️ Business Associate Agreement (BAA) with vendors
- ⚠️ Risk assessment (conduct annually)

**Note:** SignUpFlow does not collect health data by default, but organizations using it for medical volunteer coordination should enable additional safeguards.

---

## Security Best Practices

### For Administrators

**1. Use Strong Passwords**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Use a password manager (1Password, Bitwarden, LastPass)

**2. Enable Two-Factor Authentication (2FA)**
- Coming soon: TOTP support
- For now: Use strong, unique passwords per admin

**3. Limit Admin Access**
- Only grant admin role to trusted users
- Regularly audit admin list
- Remove admin access when no longer needed

**4. Review Audit Logs**
- Check audit logs weekly for suspicious activity
- Monitor for unexpected role changes
- Investigate failed login attempts

**5. Keep Software Updated**
- Update SignUpFlow regularly (watch GitHub releases)
- Apply security patches promptly
- Update dependencies: `poetry update`

### For Developers

**1. Never Commit Secrets**
- Always use environment variables
- Review commits before pushing: `git diff --staged`
- Use `.gitignore` properly

**2. Input Validation**
- Validate all user input (frontend AND backend)
- Sanitize HTML to prevent XSS
- Use Pydantic schemas for API validation

**3. Least Privilege Principle**
- Grant minimum permissions needed
- Use `Depends(get_current_user)` for authentication
- Use `Depends(verify_admin_access)` for admin endpoints

**4. Secure Dependencies**
- Regularly update: `poetry update`
- Check for vulnerabilities: `poetry audit` (future)
- Review dependency security advisories

**5. Code Review**
- All code reviewed before merging
- Security-focused reviews for auth/permissions
- Test security features thoroughly

---

## Incident Response

### If You Suspect a Security Breach

**1. Immediate Actions:**
```bash
# Invalidate all active sessions (future feature)
# For now, change SECRET_KEY to force re-authentication
# Update .env with new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Restart application
docker-compose restart api

# Review audit logs for suspicious activity
docker-compose exec db psql -U signupflow -d signupflow
SELECT * FROM audit_logs WHERE timestamp > NOW() - INTERVAL '24 hours' ORDER BY timestamp DESC;
```

**2. Investigation:**
- Check Sentry for error spikes
- Review access logs (Nginx/Cloudflare)
- Check audit logs for unauthorized access
- Identify affected users/data

**3. Containment:**
- Change all passwords (database, Redis, API keys)
- Revoke compromised API tokens
- Block suspicious IP addresses (firewall/Cloudflare)
- Notify affected users

**4. Recovery:**
- Restore from clean backup if needed
- Patch vulnerability
- Update security documentation

**5. Post-Incident:**
- Document incident timeline
- Update security procedures
- Conduct security audit
- Train team on lessons learned

### Security Contact

**Report vulnerabilities:**
- Email: security@signupflow.io
- GitHub: Private security advisory
- Response time: 24 hours

**Bug Bounty:** Coming soon

---

## Security Testing

### Automated Tests

**281 Tests Including:**
- 27 RBAC tests (`test_rbac_security.py`)
- 7 authentication tests (`test_auth_flows.py`)
- Input validation tests (all schemas)
- Rate limiting tests (future)
- Audit logging tests (future)

**Run Security Tests:**
```bash
# All security tests
poetry run pytest tests/security/ -v

# RBAC tests
poetry run pytest tests/e2e/test_rbac_security.py -v

# Authentication tests
poetry run pytest tests/e2e/test_auth_flows.py -v
```

### Manual Security Testing

**Penetration Testing Checklist:**
- [ ] SQL injection attempts (all input fields)
- [ ] XSS attacks (HTML in all text fields)
- [ ] CSRF attacks (state-changing operations)
- [ ] Brute force login attempts (verify rate limiting)
- [ ] Privilege escalation (volunteer → admin)
- [ ] Session hijacking (stolen JWT tokens)
- [ ] API abuse (excessive requests)

**Tools:**
- OWASP ZAP (automated security scanner)
- Burp Suite (manual penetration testing)
- SQLMap (SQL injection testing)
- Nikto (web server scanner)

---

## Security Updates

**Stay Informed:**
- Watch GitHub repo for security advisories
- Subscribe to security mailing list (coming soon)
- Follow @signupflow on Twitter

**Update Frequency:**
- Critical: Immediate (within 24 hours)
- High: Weekly
- Medium: Monthly
- Low: Quarterly

---

## Appendix

### Security Glossary

- **RBAC:** Role-Based Access Control
- **JWT:** JSON Web Token (authentication token format)
- **XSS:** Cross-Site Scripting (injecting malicious JavaScript)
- **CSRF:** Cross-Site Request Forgery (unauthorized state-changing requests)
- **SQL Injection:** Injecting malicious SQL queries
- **HSTS:** HTTP Strict Transport Security (force HTTPS)
- **CSP:** Content Security Policy (prevent XSS)
- **OWASP:** Open Web Application Security Project
- **PII:** Personally Identifiable Information

### Useful Commands

```bash
# Generate strong password
openssl rand -base64 32

# Check open ports
nmap -p- localhost

# View active database connections
docker-compose exec db psql -U signupflow -d signupflow -c "SELECT * FROM pg_stat_activity;"

# Monitor real-time logs
docker-compose logs -f api | grep ERROR

# Check SSL certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

**Last Updated:** 2024-10-24
**Next Review:** 2025-01-24
**Security Auditor:** Claude Code (AI Assistant)

---

*For technical implementation details, see:*
- `api/core/security.py` - Authentication & password hashing
- `api/utils/rate_limit_middleware.py` - Rate limiting
- `api/utils/security_headers_middleware.py` - Security headers
- `api/utils/audit_logger.py` - Audit logging
- `tests/e2e/test_rbac_security.py` - RBAC tests (27 tests)
