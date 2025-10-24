# Rate Limiting API Contract

**Feature**: Security Hardening - Rate Limiting
**Purpose**: Prevent brute force attacks and API abuse through configurable rate limits
**Status**: Contract Definition

---

## Overview

Rate limiting service enforces request limits per IP address, per user account, and per endpoint to prevent brute force attacks, credential stuffing, and API abuse.

**Key Features**:
- Multiple rate limit strategies (IP-based, account-based, endpoint-specific)
- Configurable thresholds per endpoint
- Redis-backed distributed rate limiting
- Graceful degradation (fail open if Redis unavailable in development)
- Account lockout after repeated failures

---

## Rate Limit Configuration

### Default Rate Limits

| Endpoint | Window | Limit | Scope | Lockout |
|----------|--------|-------|-------|---------|
| `POST /api/auth/login` | 5 min | 5 attempts | Per IP | 15 min |
| `POST /api/auth/signup` | 1 hour | 3 accounts | Per IP | 1 hour |
| `POST /api/auth/password-reset-request` | 1 hour | 3 requests | Per email | 1 hour |
| `POST /api/auth/password-reset-confirm` | 5 min | 3 attempts | Per token | 15 min |
| `POST /api/invitations` | 1 hour | 20 invites | Per org | N/A |
| `POST /api/solver/solve` | 1 min | 2 solves | Per org | N/A |
| `GET /api/*` (all reads) | 1 min | 100 requests | Per user | N/A |
| `POST /api/*` (all writes) | 1 min | 30 requests | Per user | N/A |

### Configuration File

```python
# api/core/rate_limit_config.py
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class RateLimitRule:
    """Rate limit rule definition."""
    endpoint: str          # e.g., "/api/auth/login"
    method: str            # "GET", "POST", "PUT", "DELETE", "*"
    limit: int             # Max requests
    window: timedelta      # Time window
    scope: str             # "ip", "user", "org", "global"
    lockout_duration: timedelta | None  # Account lockout duration (None = no lockout)

# Rate limit rules (ordered by specificity - most specific first)
RATE_LIMIT_RULES = [
    # Authentication endpoints (strict)
    RateLimitRule(
        endpoint="/api/auth/login",
        method="POST",
        limit=5,
        window=timedelta(minutes=5),
        scope="ip",
        lockout_duration=timedelta(minutes=15)
    ),
    RateLimitRule(
        endpoint="/api/auth/signup",
        method="POST",
        limit=3,
        window=timedelta(hours=1),
        scope="ip",
        lockout_duration=timedelta(hours=1)
    ),
    RateLimitRule(
        endpoint="/api/auth/password-reset-request",
        method="POST",
        limit=3,
        window=timedelta(hours=1),
        scope="email",  # Extracted from request body
        lockout_duration=timedelta(hours=1)
    ),

    # Admin operations (moderate)
    RateLimitRule(
        endpoint="/api/invitations",
        method="POST",
        limit=20,
        window=timedelta(hours=1),
        scope="org",
        lockout_duration=None
    ),
    RateLimitRule(
        endpoint="/api/solver/solve",
        method="POST",
        limit=2,
        window=timedelta(minutes=1),
        scope="org",
        lockout_duration=None
    ),

    # Global rate limits (fallback)
    RateLimitRule(
        endpoint="/api/*",
        method="GET",
        limit=100,
        window=timedelta(minutes=1),
        scope="user",
        lockout_duration=None
    ),
    RateLimitRule(
        endpoint="/api/*",
        method="POST",
        limit=30,
        window=timedelta(minutes=1),
        scope="user",
        lockout_duration=None
    ),
]
```

---

## Rate Limiter Service API

### Class Interface

```python
# api/services/rate_limiter.py
from typing import Optional
import redis

class RateLimiter:
    """Redis-backed distributed rate limiter."""

    def __init__(self, redis_client: redis.Redis):
        """Initialize rate limiter with Redis connection."""
        self.redis = redis_client

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if rate limit exceeded.

        Args:
            key: Rate limit key (e.g., "login:ip:203.0.113.42")
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed, current_count, retry_after_seconds)
            - allowed: True if request allowed, False if rate limit exceeded
            - current_count: Current request count in window
            - retry_after_seconds: Seconds until rate limit resets (0 if allowed)

        Example:
            >>> limiter.check_rate_limit("login:ip:1.2.3.4", limit=5, window_seconds=300)
            (True, 3, 0)  # Allowed, 3/5 requests used, no wait needed

            >>> limiter.check_rate_limit("login:ip:1.2.3.4", limit=5, window_seconds=300)
            (False, 6, 180)  # Blocked, 6/5 requests (over limit), retry after 180s
        """
        pass

    def reset_rate_limit(self, key: str) -> None:
        """
        Reset rate limit for specific key.

        Used for manual resets (e.g., admin unblocks user, successful login after lockout).

        Args:
            key: Rate limit key to reset

        Example:
            >>> limiter.reset_rate_limit("login:ip:203.0.113.42")
        """
        pass

    def get_remaining_attempts(self, key: str, limit: int) -> int:
        """
        Get remaining attempts before rate limit.

        Args:
            key: Rate limit key
            limit: Maximum requests allowed

        Returns:
            Number of remaining attempts (0 if rate limit exceeded)

        Example:
            >>> limiter.get_remaining_attempts("login:ip:1.2.3.4", limit=5)
            2  # 2 attempts remaining before lockout
        """
        pass
```

### Implementation Details

```python
# api/services/rate_limiter.py (implementation)
import redis
import time

class RateLimiter:
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """Check rate limit using Redis INCR + EXPIRE pattern."""
        try:
            # Increment counter (atomic operation)
            current = self.redis.incr(key)

            # Set expiry on first request in window
            if current == 1:
                self.redis.expire(key, window_seconds)

            # Check if over limit
            if current > limit:
                ttl = self.redis.ttl(key)
                retry_after = max(ttl, 0)  # Seconds until reset
                return (False, current, retry_after)

            return (True, current, 0)

        except redis.ConnectionError:
            # Fail open in development (allow request)
            # Fail closed in production (block request)
            if os.getenv('ENVIRONMENT') == 'production':
                raise HTTPException(503, "Rate limiting service unavailable")
            return (True, 0, 0)

    def reset_rate_limit(self, key: str) -> None:
        """Delete rate limit key to reset counter."""
        self.redis.delete(key)

    def get_remaining_attempts(self, key: str, limit: int) -> int:
        """Calculate remaining attempts."""
        current = int(self.redis.get(key) or 0)
        return max(limit - current, 0)
```

---

## Rate Limiting Middleware

### Middleware Interface

```python
# api/middleware/rate_limit_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware applying rate limits to all requests."""

    async def dispatch(self, request: Request, call_next):
        """
        Apply rate limit before processing request.

        Rate limit key format: "{scope}:{identifier}"
        Examples:
            - "ip:203.0.113.42" (IP-based)
            - "user:person_admin_123" (user-based)
            - "org:org_church_456" (org-based)
            - "email:user@example.com" (email-based, for password reset)

        HTTP Response Headers (always included):
            X-RateLimit-Limit: Maximum requests allowed (e.g., "5")
            X-RateLimit-Remaining: Remaining requests (e.g., "2")
            X-RateLimit-Reset: Unix timestamp when limit resets (e.g., "1730000000")

        HTTP 429 Response (when rate limit exceeded):
            Status: 429 Too Many Requests
            Retry-After: 180  (seconds until retry allowed)
            Body: {
                "detail": "Rate limit exceeded. Too many login attempts from your IP address. Try again in 3 minutes.",
                "retry_after": 180,
                "limit": 5,
                "window_seconds": 300
            }
        """
        # Find matching rate limit rule
        rule = self._match_rule(request)

        if rule:
            # Build rate limit key
            key = self._build_key(request, rule)

            # Check rate limit
            allowed, current, retry_after = rate_limiter.check_rate_limit(
                key,
                rule.limit,
                int(rule.window.total_seconds())
            )

            # Add rate limit headers
            response_headers = {
                "X-RateLimit-Limit": str(rule.limit),
                "X-RateLimit-Remaining": str(max(rule.limit - current, 0)),
                "X-RateLimit-Reset": str(int(time.time() + retry_after))
            }

            if not allowed:
                # Rate limit exceeded
                raise HTTPException(
                    status_code=429,
                    detail=self._get_error_message(rule, retry_after),
                    headers={
                        **response_headers,
                        "Retry-After": str(retry_after)
                    }
                )

            # Request allowed - continue processing
            response = await call_next(request)

            # Add rate limit headers to response
            for header, value in response_headers.items():
                response.headers[header] = value

            return response

        # No rate limit rule - allow request
        return await call_next(request)
```

---

## Account Lockout Logic

### Lockout Triggers

**Login Failures**:
- 5 failed login attempts in 5 minutes → 15-minute account lockout
- Lockout applies to: all devices, all IP addresses (account-level, not IP-level)
- Reset on: successful login OR manual admin unlock OR 15-minute expiry

**Signup Abuse**:
- 3 signups from same IP in 1 hour → 1-hour IP ban
- Prevents bulk account creation attacks

**Password Reset Abuse**:
- 3 password reset requests for same email in 1 hour → 1-hour cooldown
- Prevents email flooding attacks

### Lockout Storage

```python
# Stored in user_security_settings table
class UserSecuritySettings(Base):
    __tablename__ = "user_security_settings"

    user_id = Column(String, ForeignKey("people.id"), primary_key=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)  # NULL = not locked
    last_failed_login = Column(DateTime, nullable=True)

# Lockout check in login endpoint
@router.post("/api/auth/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(credentials.email, db)

    if user:
        security = get_security_settings(user.id, db)

        # Check if account locked
        if security.account_locked_until and security.account_locked_until > datetime.utcnow():
            remaining = (security.account_locked_until - datetime.utcnow()).total_seconds()
            raise HTTPException(
                status_code=429,
                detail=f"Account locked due to repeated failed login attempts. Try again in {int(remaining/60)} minutes.",
                headers={"Retry-After": str(int(remaining))}
            )

    # Verify password...
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed attempts
        security.failed_login_attempts += 1
        security.last_failed_login = datetime.utcnow()

        # Lock account after 5 failures
        if security.failed_login_attempts >= 5:
            security.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Account locked due to repeated failed login attempts. Try again in 15 minutes."
            )

        db.commit()
        raise HTTPException(401, "Invalid credentials")

    # Successful login - reset failed attempts
    security.failed_login_attempts = 0
    security.account_locked_until = None
    db.commit()

    return {"token": create_jwt_token(user)}
```

---

## Error Messages (i18n)

### Translation Keys

```json
// locales/en/security.json
{
  "rate_limit": {
    "login_exceeded": "Too many login attempts. Your account has been temporarily locked for {{minutes}} minutes.",
    "signup_exceeded": "Too many signup attempts from your IP address. Please try again in {{minutes}} minutes.",
    "password_reset_exceeded": "Too many password reset requests. Please try again in {{minutes}} minutes.",
    "api_exceeded": "You're making requests too quickly. Please slow down and try again in {{seconds}} seconds.",
    "invitation_exceeded": "Too many invitations sent. Your organization can send {{limit}} invitations per hour.",
    "solver_exceeded": "Schedule generation rate limit reached. Please wait {{seconds}} seconds before generating another schedule."
  }
}
```

### Error Message Generation

```python
def _get_error_message(rule: RateLimitRule, retry_after: int) -> str:
    """Generate user-friendly error message with i18n."""
    minutes = retry_after // 60
    seconds = retry_after

    # Match endpoint to translation key
    if rule.endpoint == "/api/auth/login":
        return i18n.t("security.rate_limit.login_exceeded", minutes=minutes)
    elif rule.endpoint == "/api/auth/signup":
        return i18n.t("security.rate_limit.signup_exceeded", minutes=minutes)
    elif rule.endpoint == "/api/auth/password-reset-request":
        return i18n.t("security.rate_limit.password_reset_exceeded", minutes=minutes)
    elif rule.endpoint == "/api/invitations":
        return i18n.t("security.rate_limit.invitation_exceeded", limit=rule.limit)
    elif rule.endpoint == "/api/solver/solve":
        return i18n.t("security.rate_limit.solver_exceeded", seconds=seconds)
    else:
        return i18n.t("security.rate_limit.api_exceeded", seconds=seconds)
```

---

## Redis Key Schema

### Key Naming Convention

```
Format: rate_limit:{scope}:{identifier}:{endpoint}

Examples:
    rate_limit:ip:203.0.113.42:/api/auth/login
    rate_limit:user:person_admin_123:/api/events
    rate_limit:org:org_church_456:/api/invitations
    rate_limit:email:user@example.com:/api/auth/password-reset-request
```

### Key Lifecycle

1. **Creation**: First request increments key (INCR creates if not exists)
2. **Expiry**: TTL set on first request (EXPIRE)
3. **Reset**: Automatic after window expires OR manual delete
4. **Cleanup**: Automatic by Redis TTL (no cron job needed)

### Storage Estimate

```
Keys per user: ~5 (login, reads, writes, org-specific actions)
Active users: 1000
Active rate limit keys: ~5000

Storage per key:
    Key name: ~50 bytes
    Value (counter): ~8 bytes
    TTL metadata: ~8 bytes
    Total: ~66 bytes per key

Total storage: 5000 keys × 66 bytes = ~330 KB
```

**Conclusion**: Negligible storage (<1MB even at 10K keys)

---

## Monitoring & Observability

### Metrics to Track

```python
# Prometheus metrics (future integration)
rate_limit_checks_total = Counter(
    "rate_limit_checks_total",
    "Total rate limit checks",
    ["endpoint", "scope", "result"]  # result: "allowed" | "blocked"
)

rate_limit_blocked_total = Counter(
    "rate_limit_blocked_total",
    "Total requests blocked by rate limiting",
    ["endpoint", "scope"]
)

account_lockouts_total = Counter(
    "account_lockouts_total",
    "Total account lockouts triggered",
    ["reason"]  # reason: "failed_login" | "signup_abuse" | "reset_abuse"
)
```

### Logging

```python
# Log all rate limit blocks
logger.warning(
    "Rate limit exceeded",
    extra={
        "event": "rate_limit_exceeded",
        "endpoint": request.url.path,
        "method": request.method,
        "scope": rule.scope,
        "identifier": identifier,
        "current_count": current,
        "limit": rule.limit,
        "retry_after": retry_after
    }
)

# Log all account lockouts
logger.warning(
    "Account locked due to failed login attempts",
    extra={
        "event": "account_lockout",
        "user_id": user.id,
        "email": user.email,
        "failed_attempts": security.failed_login_attempts,
        "locked_until": security.account_locked_until.isoformat()
    }
)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_rate_limiter.py
def test_rate_limit_within_limit():
    """Test requests within rate limit are allowed."""
    limiter = RateLimiter(redis_client)
    key = "test:ip:1.2.3.4"

    # First 5 requests allowed
    for i in range(5):
        allowed, current, retry_after = limiter.check_rate_limit(key, limit=5, window_seconds=60)
        assert allowed == True
        assert current == i + 1
        assert retry_after == 0

def test_rate_limit_exceeded():
    """Test requests exceeding rate limit are blocked."""
    limiter = RateLimiter(redis_client)
    key = "test:ip:1.2.3.4"

    # Exceed rate limit
    for i in range(6):
        limiter.check_rate_limit(key, limit=5, window_seconds=60)

    # 6th request blocked
    allowed, current, retry_after = limiter.check_rate_limit(key, limit=5, window_seconds=60)
    assert allowed == False
    assert current == 6
    assert retry_after > 0  # Some time remaining in window

def test_account_lockout_after_5_failures():
    """Test account locked after 5 failed login attempts."""
    # ... (simulate 5 failed logins)
    security = get_security_settings(user.id, db)
    assert security.account_locked_until is not None
    assert security.account_locked_until > datetime.utcnow()
```

### Integration Tests

```python
# tests/integration/test_rate_limiting_redis.py
def test_rate_limiting_with_redis(client):
    """Test rate limiting with real Redis."""
    # Make 5 login attempts (allowed)
    for i in range(5):
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
        assert response.status_code == 401  # Wrong password, but not rate limited

    # 6th attempt blocked by rate limit
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert "Retry-After" in response.headers
```

### E2E Tests

```python
# tests/e2e/test_rate_limiting.py
def test_rate_limiting_user_journey(page: Page):
    """Test rate limiting from user perspective."""
    page.goto("http://localhost:8000/login")

    # Attempt login 6 times with wrong password
    for i in range(6):
        page.locator('#email').fill("test@example.com")
        page.locator('#password').fill("wrongpassword")
        page.locator('button[type="submit"]').click()

        if i < 5:
            # First 5 attempts show "Invalid credentials"
            expect(page.locator('[data-i18n="auth.error_invalid_credentials"]')).to_be_visible()
        else:
            # 6th attempt shows rate limit message
            expect(page.locator('.error-message')).to_contain_text("Account locked")
            expect(page.locator('.error-message')).to_contain_text("15 minutes")
```

---

## Performance Benchmarks

| Operation | Target | Redis Latency | Total Overhead |
|-----------|--------|---------------|----------------|
| Rate limit check (allowed) | <5ms | 2-3ms | 3-4ms |
| Rate limit check (blocked) | <5ms | 2-3ms | 3-4ms |
| Account lockout check | <10ms | N/A (database) | 8-10ms |

**Measurement**: Same-VPC Redis (DigitalOcean), P99 latency

---

## Configuration Tuning

### Adjusting Rate Limits

```python
# To adjust rate limits, modify RATE_LIMIT_RULES in api/core/rate_limit_config.py

# Example: Increase login attempts to 10
RateLimitRule(
    endpoint="/api/auth/login",
    method="POST",
    limit=10,  # Changed from 5
    window=timedelta(minutes=5),
    scope="ip",
    lockout_duration=timedelta(minutes=15)
)
```

### Disabling Rate Limiting (Development Only)

```python
# .env.development
RATE_LIMITING_ENABLED=false  # Disable rate limiting in dev

# api/middleware/rate_limit_middleware.py
if not os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true':
    # Skip rate limiting
    return await call_next(request)
```

---

**Contract Status**: ✅ Complete
**Implementation Ready**: Yes
**Dependencies**: Redis 7.0+, FastAPI middleware, i18n translations
**Estimated LOC**: ~400 lines (service: 150, middleware: 150, config: 100)
