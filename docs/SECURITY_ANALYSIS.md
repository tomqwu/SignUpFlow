# Security Analysis: Backend API ↔ Frontend Communication

**Analysis Date**: 2025-10-07
**Status**: ⚠️ SECURITY GAPS IDENTIFIED

---

## Current Security Implementation

### ✅ What's Implemented

#### 1. Password Hashing
**Location**: `api/utils/security.py`
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```
- ✅ Passwords are hashed (SHA-256)
- ⚠️ **Warning**: SHA-256 is NOT recommended for passwords
- 🔴 **Recommendation**: Use bcrypt or argon2

#### 2. Token Generation
**Location**: `api/utils/security.py`
```python
def generate_auth_token() -> str:
    return secrets.token_urlsafe(32)
```
- ✅ Cryptographically secure tokens
- ✅ Uses `secrets` module (correct)

#### 3. Role-Based Access Control (RBAC)
**Location**: `api/dependencies.py`
```python
def check_admin_permission(person: Person) -> bool:
    return "admin" in person.roles or "super_admin" in person.roles

def verify_admin_access(person_id: str, db: Session) -> Person:
    if not check_admin_permission(person):
        raise HTTPException(status_code=403, detail="Admin access required")
```
- ✅ Admin permission checks exist
- ✅ Organization membership verification

---

## 🔴 Critical Security Gaps

### 1. **NO Authentication Token Usage**
**Severity**: 🔴 CRITICAL

**Issue**: The backend generates auth tokens, but they are **NEVER used** for authentication.

**Evidence**:
```javascript
// Frontend stores token (app-user.js:184)
currentUser = {
    id: data.person_id,
    token: data.token  // Token is stored...
};

// But NEVER sent with API requests!
const response = await fetch(`${API_BASE_URL}/people/...`, {
    headers: { 'Content-Type': 'application/json' }  // ❌ No Authorization header
});
```

**Impact**:
- Anyone can call any API endpoint with any `person_id`
- No session validation
- Tokens are generated but ignored

**Example Attack**:
```javascript
// Attacker can impersonate ANY user by just knowing their ID
fetch('http://localhost:8001/api/people/admin@rostio.com', {
    method: 'GET'
    // No auth required!
});
```

---

### 2. **No Authentication Middleware**
**Severity**: 🔴 CRITICAL

**Issue**: FastAPI endpoints have **NO authentication dependency**.

**Current**:
```python
@app.get("/api/people/{person_id}")
async def get_person(person_id: str, db: Session = Depends(get_db)):
    # ❌ No authentication check!
    person = db.query(Person).filter_by(id=person_id).first()
    return person
```

**Should be**:
```python
@app.get("/api/people/{person_id}")
async def get_person(
    person_id: str,
    current_user: Person = Depends(get_current_user),  # ✅ Auth required
    db: Session = Depends(get_db)
):
    # Verify current_user has permission to access this person
    if current_user.id != person_id and not is_admin(current_user):
        raise HTTPException(403, "Access denied")
    return person
```

---

### 3. **Person ID in Query Params**
**Severity**: 🟡 MEDIUM

**Issue**: Many endpoints accept `person_id` as a query parameter instead of deriving it from the authenticated session.

**Current**:
```python
@app.post("/api/availability/{person_id}/timeoff")
async def add_timeoff(person_id: str, ...):
    # ❌ Trusts person_id from client
```

**Attack Vector**:
```javascript
// User can modify other users' data
fetch('/api/availability/admin@rostio.com/timeoff', {
    method: 'POST',
    body: JSON.stringify({ start_date: '2025-01-01', end_date: '2025-12-31' })
});
// Now admin appears unavailable all year!
```

**Should be**:
```python
@app.post("/api/availability/timeoff")
async def add_timeoff(
    current_user: Person = Depends(get_current_user),  # ✅ From auth token
    data: TimeOffCreate,
    db: Session = Depends(get_db)
):
    # Use current_user.id instead of trusting client
    create_timeoff(db, current_user.id, data)
```

---

### 4. **Weak Password Hashing**
**Severity**: 🟡 MEDIUM

**Issue**: SHA-256 is fast, making brute-force attacks feasible.

**Current**:
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

**Problems**:
- No salt (rainbow table attacks possible)
- Too fast (billions of hashes/second on GPU)
- Not designed for passwords

**Recommendation**:
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

---

### 5. **No HTTPS Enforcement**
**Severity**: 🟡 MEDIUM (for production)

**Issue**: Currently running on HTTP, not HTTPS.

**Impact**:
- Passwords sent in plain text over network
- Session tokens visible to network sniffers
- Man-in-the-middle attacks possible

**Recommendation**:
- Use HTTPS in production
- Add `Secure` and `HttpOnly` flags to cookies
- Implement HSTS headers

---

### 6. **No Rate Limiting**
**Severity**: 🟡 MEDIUM

**Issue**: No rate limiting on sensitive endpoints.

**Attack Vectors**:
- Brute force password attacks
- API abuse
- DDoS

**Recommendation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(credentials: LoginRequest):
    ...
```

---

### 7. **No CORS Configuration Review**
**Severity**: 🟡 MEDIUM

**Issue**: CORS might be too permissive.

**Current**: Need to check `api/main.py` CORS settings.

**Recommendation**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Recommended Security Implementation

### Phase 1: JWT Authentication (CRITICAL)

#### Step 1: Install Dependencies
```bash
poetry add python-jose[cryptography] passlib[bcrypt]
```

#### Step 2: Create JWT Utilities
```python
# api/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid authentication credentials")
```

#### Step 3: Create Authentication Dependency
```python
# api/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Person:
    token = credentials.credentials
    payload = verify_token(token)
    person_id = payload.get("sub")

    person = db.query(Person).filter_by(id=person_id).first()
    if not person:
        raise HTTPException(401, "User not found")

    return person
```

#### Step 4: Protect Endpoints
```python
# api/routes/people.py
@app.get("/api/people/me")
async def get_current_person(
    current_user: Person = Depends(get_current_user)
):
    return current_user

@app.put("/api/people/me")
async def update_current_person(
    data: PersonUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update current_user, not arbitrary person_id
    return update_person(db, current_user.id, data)
```

#### Step 5: Update Frontend
```javascript
// frontend/js/app-user.js

// After login, store token
localStorage.setItem('authToken', data.token);

// Create authenticated fetch wrapper
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('authToken');

    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        // Token expired, redirect to login
        logout();
        return;
    }

    return response;
}

// Use authFetch for all API calls
const response = await authFetch(`${API_BASE_URL}/people/me`);
```

---

### Phase 2: Additional Security Hardening

1. **Implement bcrypt password hashing**
2. **Add rate limiting** (slowapi)
3. **Enable HTTPS** in production
4. **Add CSRF protection** for state-changing operations
5. **Implement session expiration** and refresh tokens
6. **Add API request logging** for security auditing
7. **Implement input validation** (Pydantic models)
8. **Add SQL injection prevention** (already using SQLAlchemy ORM ✅)
9. **Configure secure CORS** policies
10. **Add security headers** (CSP, X-Frame-Options, etc.)

---

## Testing Security

### Security Test Suite Needed

```python
# tests/security/test_authentication.py

def test_unauthenticated_request_rejected():
    """Test that API calls without token are rejected."""
    response = client.get("/api/people/me")
    assert response.status_code == 401

def test_invalid_token_rejected():
    """Test that invalid tokens are rejected."""
    response = client.get(
        "/api/people/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_expired_token_rejected():
    """Test that expired tokens are rejected."""
    # Create expired token
    expired_token = create_access_token(
        data={"sub": "user@example.com"},
        expires_delta=timedelta(minutes=-1)
    )
    response = client.get(
        "/api/people/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_user_cannot_access_other_user_data():
    """Test that users can only access their own data."""
    token = login_as("user1@example.com")
    response = client.get(
        "/api/people/user2@example.com",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
```

---

## Summary

### Current State: ⚠️ VULNERABLE

| Security Feature | Status | Priority |
|------------------|--------|----------|
| Authentication Tokens | 🔴 Not Used | CRITICAL |
| Authorization Checks | 🔴 Missing | CRITICAL |
| Password Hashing | 🟡 Weak (SHA-256) | HIGH |
| HTTPS | 🔴 Not Enabled | HIGH |
| Rate Limiting | 🔴 Missing | MEDIUM |
| CORS Configuration | 🟡 Unknown | MEDIUM |
| Input Validation | 🟢 Pydantic | Good |
| SQL Injection | 🟢 ORM Protected | Good |

### Recommended Actions (Priority Order)

1. 🔴 **CRITICAL**: Implement JWT authentication with Bearer tokens
2. 🔴 **CRITICAL**: Add authentication middleware to all protected endpoints
3. 🔴 **CRITICAL**: Remove `person_id` from query params, use auth token
4. 🟡 **HIGH**: Replace SHA-256 with bcrypt for password hashing
5. 🟡 **HIGH**: Enable HTTPS in production
6. 🟡 **MEDIUM**: Add rate limiting to auth endpoints
7. 🟡 **MEDIUM**: Review and restrict CORS policies
8. 🟢 **LOW**: Add security headers
9. 🟢 **LOW**: Implement refresh tokens for long sessions
10. 🟢 **LOW**: Add comprehensive security test suite

---

**Conclusion**: The application currently has **minimal security** for backend-frontend communication. While some security primitives exist (token generation, role checks), they are **not being enforced**. Implementing JWT authentication is **critical** before production deployment.
