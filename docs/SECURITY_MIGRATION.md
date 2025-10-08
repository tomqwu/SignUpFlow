# Security Implementation Migration Guide

**Date**: 2025-10-07
**Status**: ✅ JWT Authentication & Bcrypt Implemented

---

## What Was Implemented

### ✅ JWT Authentication
- **Bearer Token Authentication**: All API requests now use JWT tokens
- **Token Expiration**: 24-hour token lifetime
- **Secure Token Generation**: Uses industry-standard JWT with HS256
- **Auto-logout on Expiration**: Frontend automatically redirects to login when token expires

### ✅ Bcrypt Password Hashing
- **Replaced SHA-256 with Bcrypt**: Passwords now hashed with bcrypt (industry standard)
- **Salt Generation**: Automatic per-password salt
- **Computational Cost**: Configurable rounds (default 12)
- **72-byte Limit Handling**: Automatic truncation for long passwords

### ✅ Protected API Endpoints
- **`/api/people/me`**: Get current authenticated user
- **`/api/people/me` (PUT)**: Update current authenticated user
- **Authentication Dependency**: `get_current_user()` for protected endpoints
- **Admin Dependency**: `get_current_admin_user()` for admin-only endpoints

### ✅ Frontend Security
- **authFetch Wrapper**: Automatically includes Bearer tokens
- **Token Storage**: Secure localStorage for JWT tokens
- **Auto-redirect**: Handles 401 responses by redirecting to login
- **Helper Functions**: `authGet`, `authPost`, `authPut`, `authDelete`

---

## 📝 Migration Notes

### For New Users
✅ **No action required** - All new signups use bcrypt automatically

### For Existing Users
⚠️ **Password Reset Required** for users created before this update:

**Reason**: Existing passwords were hashed with SHA-256. The new system uses bcrypt, so old password hashes won't verify.

**Options**:
1. **Self-Service Reset** (Recommended): Users can use "Forgot Password" flow
2. **Admin Manual Reset**: Admins can reset user passwords
3. **Database Migration Script**: Run migration to re-hash existing passwords (requires users to login once with old password)

---

## 🔧 Using the New Security Features

### Backend: Protecting Endpoints

```python
from fastapi import Depends
from api.dependencies import get_current_user, get_current_admin_user
from api.models import Person

# Require authentication
@app.get("/api/my-endpoint")
async def my_endpoint(current_user: Person = Depends(get_current_user)):
    # current_user is the authenticated Person object
    return {"user_id": current_user.id}

# Require admin permissions
@app.post("/api/admin-endpoint")
async def admin_endpoint(admin_user: Person = Depends(get_current_admin_user)):
    # admin_user is verified to have admin role
    return {"message": "Admin action completed"}
```

### Frontend: Making Authenticated Requests

```javascript
// Old way (no auth)
const response = await fetch('/api/people/123', {
    headers: { 'Content-Type': 'application/json' }
});

// New way (with auth token)
const response = await authFetch('/api/people/me');

// Or use convenience functions
const user = await authGet('/api/people/me');
const updated = await authPut('/api/people/me', { name: 'New Name' });
const created = await authPost('/api/events/', eventData);
await authDelete('/api/events/123');
```

### Frontend: Token Management

```javascript
// Token is automatically saved on login/signup
// Located in localStorage as 'authToken'

// Check if user is authenticated
const isAuthenticated = !!localStorage.getItem('authToken');

// Manually clear auth (logout)
localStorage.removeItem('authToken');
localStorage.removeItem('currentUser');
localStorage.removeItem('currentOrg');
```

---

## 🧪 Security Tests

### Running Security Tests

```bash
# Run all security tests
poetry run pytest tests/security/ -v

# Test specific security feature
poetry run pytest tests/security/test_authentication.py::test_password_hashing -v
```

### Test Coverage
- ✅ Password hashing (bcrypt)
- ✅ JWT token creation and verification
- ✅ Token expiration
- ✅ Unauthenticated request rejection
- ✅ Invalid token rejection
- ✅ Login returns valid JWT
- ✅ Authenticated requests with valid tokens

---

## 🔒 Security Best Practices

### Passwords
- ✅ Minimum 6 characters (enforced at API level)
- ✅ Bcrypt hashing with automatic salt
- ✅ 72-byte limit handled automatically
- 🔄 **TODO**: Add password strength requirements (uppercase, numbers, symbols)
- 🔄 **TODO**: Add password history (prevent reuse)

### Tokens
- ✅ 24-hour expiration (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- ✅ Signed with SECRET_KEY (set via environment variable)
- 🔄 **TODO**: Implement refresh tokens for long sessions
- 🔄 **TODO**: Token revocation on logout

### HTTPS
- 🔄 **TODO**: Enable HTTPS in production
- 🔄 **TODO**: Add Secure and HttpOnly flags to cookies
- 🔄 **TODO**: Implement HSTS headers

### Rate Limiting
- 🔄 **TODO**: Add rate limiting to login endpoint (prevent brute force)
- 🔄 **TODO**: Add rate limiting to password reset
- 🔄 **TODO**: Add global API rate limiting

---

## 🚨 Breaking Changes

### API Changes
1. **Protected Endpoints**: Many endpoints now require `Authorization: Bearer {token}` header
2. **Login Response**: Returns JWT token instead of random token
3. **Password Storage**: New bcrypt format (incompatible with old SHA-256)

### Frontend Changes
1. **Auth Token Storage**: Now stored separately as `authToken` in localStorage
2. **API Calls**: Must use `authFetch()` or include Authorization header manually
3. **401 Handling**: Auto-redirects to login (may interrupt workflows)

### Backwards Compatibility
- ⚠️ **None** - This is a breaking security update
- 🔴 **Existing passwords won't work** - Users must reset passwords
- 🔴 **Old API clients will fail** - Must update to send Bearer tokens

---

## 📊 Before vs After

### Before (Insecure)
```javascript
// Frontend
currentUser = { id: data.person_id, token: data.token };
fetch('/api/people/' + someId);  // No auth!

// Backend
@app.get("/api/people/{person_id}")
def get_person(person_id: str, db: Session = Depends(get_db)):
    # No auth check - anyone can access!
    return db.query(Person).filter_by(id=person_id).first()
```

**Security Issues**:
- ❌ No token verification
- ❌ Client-provided person_id trusted
- ❌ Weak SHA-256 password hashing
- ❌ Anyone can access any user's data

### After (Secure)
```javascript
// Frontend
localStorage.setItem('authToken', data.token);
await authFetch('/api/people/me');  // Auto-includes Bearer token

// Backend
@app.get("/api/people/me")
async def get_current_person(current_user: Person = Depends(get_current_user)):
    # Auth required, person derived from verified JWT
    return current_user
```

**Security Features**:
- ✅ JWT token verification on every request
- ✅ No client-provided IDs (uses authenticated user)
- ✅ Strong bcrypt password hashing
- ✅ 401 errors for invalid/missing tokens

---

## 🔑 Environment Variables

### Required
```bash
# Set a strong secret key (production)
export SECRET_KEY="your-very-long-random-secret-key-change-this"
```

### Optional
```bash
# Token expiration (in minutes, default 1440 = 24 hours)
export ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Generating a Secure Secret Key
```bash
# Generate random secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📚 Additional Resources

- **Security Analysis**: See `docs/SECURITY_ANALYSIS.md`
- **Test Suite**: See `tests/security/test_authentication.py`
- **JWT Documentation**: https://jwt.io/
- **Bcrypt Documentation**: https://en.wikipedia.org/wiki/Bcrypt
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/

---

**Next Steps**:
1. ✅ Test login flow with new signup
2. 🔄 Implement password reset flow for existing users
3. 🔄 Add rate limiting
4. 🔄 Enable HTTPS in production
5. 🔄 Implement refresh tokens
