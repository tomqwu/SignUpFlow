# Rate Limiting Configuration

Rostio includes built-in rate limiting to prevent spam and bot abuse on critical endpoints.

## Overview

Rate limiting is implemented using a **token bucket algorithm** that:
- Tracks requests per IP address
- Automatically refills tokens over time
- Returns HTTP 429 (Too Many Requests) when limits are exceeded
- Is disabled during tests (when `TESTING=true`)

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

Rate limits are tracked per IP address. The system checks:
1. **X-Forwarded-For header** (for requests through proxies/load balancers)
2. **Direct client IP** (fallback for direct connections)

This ensures accurate rate limiting behind reverse proxies like Nginx or CDNs.

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

To test rate limiting manually:
1. Unset `TESTING` environment variable
2. Make multiple rapid requests to an endpoint
3. Observe HTTP 429 after exceeding the limit

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

The current implementation uses **in-memory storage**, suitable for:
- Single-server deployments
- Development environments
- Small-scale production

For **distributed deployments** with multiple servers, consider:
- Redis-based rate limiting (shared state across servers)
- API Gateway rate limiting (AWS API Gateway, Kong, etc.)

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
