# Quick Start: Billing & Subscription System

**Feature**: 011-billing-subscription-system | **Date**: 2025-10-22
**Purpose**: Get Stripe sandbox setup and local development environment running in 15 minutes

---

## Prerequisites

✅ **Before starting, verify you have:**
- [ ] Stripe account (create at https://stripe.com)
- [ ] Stripe test API keys (from https://dashboard.stripe.com/test/apikeys)
- [ ] Poetry installed (`poetry --version`)
- [ ] Redis installed and running (`redis-cli ping` returns PONG)
- [ ] Python 3.11+ (`python --version`)
- [ ] SignUpFlow repository cloned

---

## Step 1: Stripe Sandbox Setup (5 minutes)

### 1.1 Create Stripe Account
```bash
# Navigate to Stripe signup
open https://stripe.com/register

# Use a real email (you'll need to verify it)
# Choose "Platform or Marketplace" as business type
```

### 1.2 Get Test API Keys
```bash
# Navigate to API keys page (TEST MODE)
open https://dashboard.stripe.com/test/apikeys

# Copy both keys:
# - Publishable key: pk_test_...
# - Secret key: sk_test_... (click "Reveal test key token")
```

### 1.3 Add Keys to .env
```bash
# Edit .env file
nano .env

# Add these lines (replace with your actual keys):
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_TEST_MODE=true

# Save and exit (Ctrl+X, Y, Enter)
```

### 1.4 Configure Stripe Products (Dashboard)
```bash
# Navigate to Products page
open https://dashboard.stripe.com/test/products

# Create 4 products:
# 1. Free Plan (no price, metadata: tier=free, volunteers=10)
# 2. Starter Plan ($29/month, $290/year, metadata: tier=starter, volunteers=50)
# 3. Pro Plan ($79/month, $790/year, metadata: tier=pro, volunteers=200)
# 4. Enterprise Plan ($199/month, $1990/year, metadata: tier=enterprise, volunteers=2000)
```

**Product Configuration Example (Starter Plan)**:
- Product name: `Starter Plan`
- Description: `Perfect for small teams - 50 volunteers`
- Statement descriptor: `SIGNUPFLOW STARTER`
- Metadata: `{"tier": "starter", "volunteers": "50"}`

**Price Configuration (Monthly)**:
- Price: `$29.00 USD`
- Billing period: `Monthly`
- Price description: `Starter Plan - Monthly`
- Price ID: Copy `price_1ABC...` (save for later)

**Price Configuration (Annual)**:
- Price: `$290.00 USD` (20% discount: $29 × 12 × 0.8)
- Billing period: `Yearly`
- Price description: `Starter Plan - Annual`
- Price ID: Copy `price_1XYZ...` (save for later)

### 1.5 Save Price IDs to Configuration
```bash
# Create billing config file
cat > api/core/billing_config.py << 'EOF'
"""Stripe pricing configuration."""

STRIPE_PRICE_IDS = {
    "starter": {
        "monthly": "price_1ABC...",  # Replace with your actual price ID
        "annual": "price_1XYZ...",   # Replace with your actual price ID
    },
    "pro": {
        "monthly": "price_1DEF...",
        "annual": "price_1UVW...",
    },
    "enterprise": {
        "monthly": "price_1GHI...",
        "annual": "price_1RST...",
    }
}

PLAN_LIMITS = {
    "free": {"volunteers": 10},
    "starter": {"volunteers": 50},
    "pro": {"volunteers": 200},
    "enterprise": {"volunteers": 2000}
}
EOF
```

---

## Step 2: Local Development Setup (5 minutes)

### 2.1 Install Dependencies
```bash
# Install Python dependencies (includes Stripe SDK)
poetry install

# Install Celery and Redis for queue processing
poetry add celery redis

# Verify Stripe SDK installed
poetry run python -c "import stripe; print(f'Stripe SDK {stripe.__version__}')"
```

### 2.2 Start Redis (Queue Backend)
```bash
# Start Redis server (required for Celery)
redis-server &

# Verify Redis is running
redis-cli ping
# Should output: PONG
```

### 2.3 Start Celery Worker (Webhook Processing)
```bash
# Start Celery worker in background
poetry run celery -A api.celery_app worker --loglevel=info &

# Verify worker started (check logs)
tail -f celery.log
# Should see: "[tasks]" with registered webhook handlers
```

### 2.4 Run Database Migrations
```bash
# Apply billing schema migrations
poetry run alembic upgrade head

# Verify tables created
poetry run python -c "
from api.database import get_db
from api.models import Subscription, BillingHistory, PaymentMethod, UsageMetrics, SubscriptionEvent
print('✅ All billing tables created successfully')
"
```

### 2.5 Start FastAPI Server
```bash
# Start development server
make run
# OR: poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Verify server started
curl http://localhost:8000/docs
# Should return Swagger UI HTML
```

---

## Step 3: Create Test Data (3 minutes)

### 3.1 Create Test Organization & User
```bash
# Run test data script
poetry run python << 'EOF'
from api.database import get_db
from api.models import Organization, Person
from api.core.security import hash_password
import uuid

db = next(get_db())

# Create test organization
org = Organization(
    id=f"org_test_{uuid.uuid4().hex[:8]}",
    name="Test Church",
    location="Toronto, ON",
    timezone="America/Toronto"
)
db.add(org)

# Create admin user
admin = Person(
    id=f"person_admin_{uuid.uuid4().hex[:8]}",
    email="admin@testchurch.com",
    name="Admin User",
    org_id=org.id,
    roles=["admin"],
    hashed_password=hash_password("testpassword123")
)
db.add(admin)

db.commit()

print(f"✅ Created organization: {org.id}")
print(f"✅ Created admin user: {admin.email}")
print(f"✅ Login credentials: admin@testchurch.com / testpassword123")
EOF
```

### 3.2 Assign Free Plan (Default)
```bash
# Create default Free subscription
poetry run python << 'EOF'
from api.database import get_db
from api.models import Organization, Subscription
from datetime import datetime, timedelta
import uuid

db = next(get_db())
org = db.query(Organization).filter(Organization.name == "Test Church").first()

subscription = Subscription(
    id=f"sub_{uuid.uuid4().hex[:12]}",
    org_id=org.id,
    plan_tier="free",
    billing_cycle="monthly",
    status="active",
    current_period_start=datetime.utcnow(),
    current_period_end=datetime.utcnow() + timedelta(days=30),
    cancel_at_period_end=False
)
db.add(subscription)
db.commit()

print(f"✅ Created Free subscription: {subscription.id}")
print(f"✅ Volunteer limit: 10")
EOF
```

---

## Step 4: Test API Endpoints (2 minutes)

### 4.1 Login and Get JWT Token
```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testchurch.com",
    "password": "testpassword123"
  }'

# Save token from response
export AUTH_TOKEN="eyJ0eXAi..."  # Replace with actual token
```

### 4.2 Test: Get Current Subscription
```bash
# Get subscription details
curl http://localhost:8000/api/billing/subscription?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Expected output:
{
  "subscription": {
    "id": "sub_abc123",
    "org_id": "org_test_12345678",
    "plan_tier": "free",
    "billing_cycle": "monthly",
    "status": "active"
  },
  "usage": {
    "volunteers_count": {
      "current": 0,
      "limit": 10,
      "percentage": 0.0
    }
  }
}
```

### 4.3 Test: Start Pro Trial
```bash
# Create test payment method first
curl -X POST http://localhost:8000/api/billing/payment-method?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stripe_payment_method_id": "pm_card_visa"
  }'

# Start 14-day Pro trial
curl -X POST http://localhost:8000/api/billing/subscription/trial?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "pro",
    "payment_method_id": "pm_card_visa"
  }'

# Expected output:
{
  "subscription": {
    "plan_tier": "pro",
    "status": "trialing",
    "trial_end_date": "2025-11-05T00:00:00Z",
    "trial_days_remaining": 14
  },
  "message": "Pro trial started. Full access for 14 days."
}
```

### 4.4 Test: Upgrade to Paid Plan
```bash
# Upgrade from trial to paid Pro (annual)
curl -X POST http://localhost:8000/api/billing/subscription/upgrade?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_plan": "pro",
    "billing_cycle": "annual",
    "payment_method_id": "pm_card_visa"
  }'

# Expected output:
{
  "subscription": {
    "plan_tier": "pro",
    "billing_cycle": "annual",
    "status": "active"
  },
  "prorated_invoice": {
    "amount_cents": 79000,
    "description": "Annual Pro plan"
  },
  "new_limits": {
    "volunteers": 200
  }
}
```

---

## Step 5: Webhook Testing (Optional, 3 minutes)

### 5.1 Install Stripe CLI
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
curl -s https://packages.stripe.com/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg
echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.com/stripe-cli-deb stable main" | sudo tee -a /etc/apt/sources.list.d/stripe.list
sudo apt update
sudo apt install stripe

# Verify installation
stripe --version
```

### 5.2 Authenticate Stripe CLI
```bash
# Login to Stripe
stripe login

# Follow browser prompt to authenticate
# Should output: "Done! Your CLI is now configured."
```

### 5.3 Forward Webhooks to Local Server
```bash
# Start webhook forwarding
stripe listen --forward-to localhost:8000/api/webhooks/stripe

# Should output webhook signing secret:
# Ready! Your webhook signing secret is whsec_...

# Copy webhook secret to .env
echo "STRIPE_WEBHOOK_SECRET=whsec_..." >> .env
```

### 5.4 Trigger Test Webhook
```bash
# Open new terminal, trigger test payment
stripe trigger customer.subscription.created

# Check logs in webhook forwarding terminal
# Should see: "✓ Webhooks delivered to local server"

# Verify webhook processed
curl http://localhost:8000/api/billing/history?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Should see billing history entry with event_type="subscription_change"
```

---

## Troubleshooting

### Issue: "STRIPE_SECRET_KEY not found"
**Cause**: Missing .env configuration

**Fix**:
```bash
# Verify .env exists
ls -la .env

# Check Stripe keys present
grep STRIPE .env

# Should output:
# STRIPE_PUBLISHABLE_KEY=pk_test_...
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_TEST_MODE=true
```

### Issue: "Redis connection refused"
**Cause**: Redis not running

**Fix**:
```bash
# Start Redis server
redis-server &

# Verify running
redis-cli ping
# Should output: PONG
```

### Issue: "Celery worker not processing webhooks"
**Cause**: Worker not started or crashed

**Fix**:
```bash
# Check worker status
ps aux | grep celery

# Restart worker
pkill -f celery
poetry run celery -A api.celery_app worker --loglevel=info &

# Check logs
tail -f celery.log
```

### Issue: "422 Unprocessable Entity on upgrade"
**Cause**: Invalid payment method ID

**Fix**:
```bash
# Use Stripe test payment methods
# Successful payment: pm_card_visa
# Declined payment: pm_card_chargeDecline

# Create test payment method first
curl -X POST http://localhost:8000/api/billing/payment-method?org_id=org_test_12345678 \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stripe_payment_method_id": "pm_card_visa"}'
```

### Issue: "Webhook signature verification failed"
**Cause**: Missing or incorrect webhook secret

**Fix**:
```bash
# Get webhook secret from Stripe CLI
stripe listen --print-secret

# Add to .env
echo "STRIPE_WEBHOOK_SECRET=whsec_..." >> .env

# Restart server
make run
```

### Issue: "403 Forbidden on billing endpoints"
**Cause**: User not admin or wrong organization

**Fix**:
```bash
# Verify user has admin role
poetry run python << 'EOF'
from api.database import get_db
from api.models import Person

db = next(get_db())
user = db.query(Person).filter(Person.email == "admin@testchurch.com").first()
print(f"User roles: {user.roles}")
# Should output: ['admin']

# If not admin, update roles
if "admin" not in user.roles:
    user.roles = ["admin"]
    db.commit()
    print("✅ Admin role added")
EOF
```

---

## Testing Checklist

Before marking quickstart complete, verify:

- [ ] Stripe account created and test mode enabled
- [ ] Test API keys added to .env (pk_test_... and sk_test_...)
- [ ] 4 products configured in Stripe Dashboard (Free, Starter, Pro, Enterprise)
- [ ] Price IDs saved to billing_config.py
- [ ] Redis running (`redis-cli ping` returns PONG)
- [ ] Celery worker running (check `ps aux | grep celery`)
- [ ] Database migrations applied (5 billing tables exist)
- [ ] Test organization and admin user created
- [ ] Free subscription assigned to test org
- [ ] Login successful and JWT token obtained
- [ ] GET /api/billing/subscription returns 200 OK
- [ ] POST /api/billing/subscription/trial returns 201 Created
- [ ] POST /api/billing/subscription/upgrade returns 200 OK
- [ ] Stripe CLI installed (optional, for webhook testing)
- [ ] Webhooks forwarding to local server (optional)
- [ ] Test webhook triggered and processed (optional)

---

## Next Steps

### For Development:
1. Read `data-model.md` to understand database schema
2. Read `contracts/billing-api.md` for full API reference
3. Read `contracts/webhook-api.md` for webhook event handling
4. Review `research.md` for architectural decisions

### For Testing:
1. Run unit tests: `poetry run pytest tests/unit/test_billing_service.py -v`
2. Run integration tests: `poetry run pytest tests/integration/test_billing_api.py -v`
3. Run E2E tests: `poetry run pytest tests/e2e/test_subscription_upgrade.py -v`

### For Production:
1. Replace test keys with live keys (pk_live_... and sk_live_...)
2. Configure production webhook endpoint in Stripe Dashboard
3. Enable Stripe Tax for automatic tax calculation
4. Set up monitoring alerts for webhook failures
5. Configure Redis with persistence enabled

---

**Quick Start Version**: 1.0
**Last Updated**: 2025-10-22
**Status**: Ready for Development

**Estimated Setup Time**: 15 minutes (20 minutes with webhook testing)
