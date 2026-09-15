# Rate Limiting Configuration

Rostio includes built-in rate limiting to prevent spam and bot abuse on critical endpoints.

## Overview

Development rate limiting uses a process-local token bucket. Production uses an atomic
Redis fixed-window counter shared across application workers. Both implementations:
- Tracks requests per IP address
- Automatically refills tokens over time
- Returns HTTP 429 (Too Many Requests) when limits are exceeded
- Is disabled during tests (when `TESTING=true`)

Production requires `RATE_LIMIT_STORAGE=redis` and an authenticated `REDIS_URL` (or
dedicated `RATE_LIMIT_REDIS_URL`). Missing or unavailable shared storage returns a
retryable 503 for protected operations instead of silently allowing traffic.

## Default Rate Limits

| Endpoint | Default Limit | Window | Purpose |
|----------|--------------|---------|---------|
| **Signup** | 3 requests | 1 hour | Prevent mass account creation |
| **Login** | 5 requests | 5 minutes | Prevent brute force attacks |
| **Create Organization** | 2 requests | 1 hour | Prevent spam organizations |
| **Create Invitation** | 10 requests | 5 minutes | Prevent invitation spam |
| **Verify Invitation** | 10 requests | 1 minute | Prevent token enumeration |

## Configuration

Rate limits are **fully configurable** via environment variables. This allows you to:
- Adjust limits without code changes
- Set different limits for development vs production
- Tighten or relax limits based on observed traffic

### Environment Variables

Create a `.env` file in the project root (or set environment variables):

```bash
# Signup Rate Limit
RATE_LIMIT_SIGNUP_MAX=3              # Maximum requests
RATE_LIMIT_SIGNUP_WINDOW=3600        # Time window in seconds (1 hour)

# Login Rate Limit
RATE_LIMIT_LOGIN_MAX=5               # Maximum requests
RATE_LIMIT_LOGIN_WINDOW=300          # Time window in seconds (5 minutes)

# Create Organization Rate Limit
RATE_LIMIT_CREATE_ORG_MAX=2          # Maximum requests
RATE_LIMIT_CREATE_ORG_WINDOW=3600    # Time window in seconds (1 hour)

# Create Invitation Rate Limit
RATE_LIMIT_CREATE_INVITATION_MAX=10  # Maximum requests
RATE_LIMIT_CREATE_INVITATION_WINDOW=300  # Time window in seconds (5 minutes)

# Verify Invitation Rate Limit
RATE_LIMIT_VERIFY_INVITATION_MAX=10  # Maximum requests
RATE_LIMIT_VERIFY_INVITATION_WINDOW=60   # Time window in seconds (1 minute)
```

### Example Configurations

**Stricter Limits (High Security)**
```bash
RATE_LIMIT_SIGNUP_MAX=2
RATE_LIMIT_SIGNUP_WINDOW=7200        # 2 hours
RATE_LIMIT_LOGIN_MAX=3
RATE_LIMIT_LOGIN_WINDOW=600          # 10 minutes
RATE_LIMIT_CREATE_ORG_MAX=1
RATE_LIMIT_CREATE_ORG_WINDOW=86400   # 24 hours
```

**Relaxed Limits (Development)**
```bash
RATE_LIMIT_SIGNUP_MAX=10
RATE_LIMIT_SIGNUP_WINDOW=300         # 5 minutes
RATE_LIMIT_LOGIN_MAX=20
RATE_LIMIT_LOGIN_WINDOW=60           # 1 minute
RATE_LIMIT_CREATE_ORG_MAX=5
RATE_LIMIT_CREATE_ORG_WINDOW=3600    # 1 hour
```

## How It Works

### Token Bucket Algorithm

This algorithm describes the development fallback. Production increments one Redis key
atomically and expires the fixed window; the key contains a SHA-256 digest rather than
the raw client address.

1. **Initial State**: Each IP starts with a full bucket of tokens (e.g., 3 tokens for signup)
2. **Request**: Each request consumes 1 token
3. **Refill**: Tokens automatically refill at a constant rate over time
4. **Block**: When tokens run out, requests are rejected with HTTP 429

### Example Timeline (Signup: 3 requests per hour)

```
Time    | Tokens | Action              | Result
--------|--------|---------------------|--------
0:00    | 3      | Request 1           | ✅ Allowed (2 tokens left)
0:10    | 2      | Request 2           | ✅ Allowed (1 token left)
0:20    | 1      | Request 3           | ✅ Allowed (0 tokens left)
0:30    | 0      | Request 4           | ❌ Blocked (429)
0:40    | 0.5    | (tokens refilling)  | ❌ Blocked (429)
1:00    | 1      | Request 5           | ✅ Allowed
```

## IP Address Detection

Rate limits are tracked per client address. The direct peer is authoritative unless it
belongs to `TRUSTED_PROXY_IPS`; only then is the forwarded chain considered. An
attacker-supplied `X-Forwarded-For` header from any other peer is ignored.

## Response Format

When rate limit is exceeded:

```json
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Testing

Rate limiting is **automatically disabled** during tests when `TESTING=true` is set in the environment.

Run `make test-redis` for repeatable owned Redis acceptance. It proves two limiter
instances share one quota and that hashed keys expire. Focused unit tests cover backend
outage and recovery without contacting a provider.

## Production Considerations

### Proxy Configuration

If running behind a proxy (Nginx, Cloudflare, etc.), ensure the proxy passes the real client IP:

**Nginx Example:**
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Distributed Deployments

Application workers share Redis quota state. Keep network-edge limits and volumetric
attack controls at the reverse proxy, load balancer, or dedicated edge service; this
application limiter is not a replacement for them.

### Monitoring

Monitor rate limit rejections to:
- Detect bot attacks (high 429 rates)
- Identify false positives (legitimate users hitting limits)
- Tune limits based on real-world usage

## Security Benefits

✅ **Prevents brute force attacks** on login endpoints
✅ **Stops mass account creation** by bots
✅ **Blocks invitation token enumeration**
✅ **Prevents organization spam**
✅ **Mitigates DoS attempts**

## Troubleshooting

**Problem**: Legitimate users hitting rate limits

**Solution**:
- Increase `MAX` values or decrease `WINDOW` values
- Check if users are behind shared IPs (corporate proxies, VPNs)
- Consider implementing user-based rate limiting (requires authentication)

**Problem**: Bots still getting through

**Solution**:
- Decrease `MAX` values or increase `WINDOW` values
- Add CAPTCHA for additional protection
- Implement additional bot detection mechanisms

## Related Files

- `api/utils/rate_limiter.py` - Core rate limiting logic
- `api/utils/rate_limit_middleware.py` - FastAPI integration
- `tests/unit/test_rate_limiting.py` - Test suite
- `.env.example` - Configuration template
