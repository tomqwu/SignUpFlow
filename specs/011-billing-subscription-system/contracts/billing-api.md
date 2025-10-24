# API Contract: Billing Endpoints

**Feature**: 011-billing-subscription-system
**Router**: `api/routers/billing.py`
**Base Path**: `/api/billing`
**Date**: 2025-10-22

## Authentication

**All endpoints require**:
- JWT Bearer token authentication
- Admin role (`verify_admin_access()` dependency)
- Organization membership verification

**Headers**:
```
Authorization: Bearer {jwt_token}
```

---

## Endpoints

### 1. Get Current Subscription

**Purpose**: Retrieve organization's current subscription details

**Endpoint**: `GET /api/billing/subscription`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Example**:
```http
GET /api/billing/subscription?org_id=org_church_xyz
Authorization: Bearer eyJ0eXAi...
```

**Response 200 OK**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "org_id": "org_church_xyz",
    "plan_tier": "pro",
    "billing_cycle": "annual",
    "status": "active",
    "current_period_start": "2025-01-01T00:00:00Z",
    "current_period_end": "2026-01-01T00:00:00Z",
    "trial_end_date": null,
    "cancel_at_period_end": false,
    "stripe_customer_id": "cus_NQz8xY2I4rXVqP",
    "stripe_subscription_id": "sub_1OQz8xJ2eZvKYlo2"
  },
  "usage": {
    "volunteers_count": {
      "current": 35,
      "limit": 200,
      "percentage": 17.5
    }
  },
  "next_invoice": {
    "amount_cents": 75840,
    "currency": "usd",
    "date": "2026-01-01T00:00:00Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid/missing JWT token
- `403 Forbidden`: User not admin or not in organization
- `404 Not Found`: Organization has no subscription

---

### 2. Upgrade Subscription

**Purpose**: Upgrade organization to higher tier or change billing cycle

**Endpoint**: `POST /api/billing/subscription/upgrade`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**:
```json
{
  "new_plan": "pro",
  "billing_cycle": "annual",
  "payment_method_id": "pm_1OQz8xJ2eZvKYlo2CiU7C9Vn"
}
```

**Request Example**:
```http
POST /api/billing/subscription/upgrade?org_id=org_church_xyz
Authorization: Bearer eyJ0eXAi...
Content-Type: application/json

{
  "new_plan": "pro",
  "billing_cycle": "annual",
  "payment_method_id": "pm_1OQz8xJ2eZvKYlo2CiU7C9Vn"
}
```

**Response 200 OK**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "plan_tier": "pro",
    "billing_cycle": "annual",
    "status": "active",
    "upgraded_at": "2025-01-22T15:30:00Z"
  },
  "prorated_invoice": {
    "amount_cents": 6960,
    "description": "Prorated charge for upgrade from Starter to Pro",
    "invoice_url": "https://pay.stripe.com/invoice/..."
  },
  "new_limits": {
    "volunteers": 200
  }
}
```

**Validation Rules**:
- `new_plan`: Must be one of: `starter`, `pro`, `enterprise` (cannot downgrade via this endpoint)
- `billing_cycle`: Must be `monthly` or `annual`
- `payment_method_id`: Required for Free → Paid upgrade, optional for Paid → Paid

**Error Responses**:
- `400 Bad Request`: Invalid plan or billing cycle
- `402 Payment Required`: Payment method required but not provided
- `403 Forbidden`: Cannot upgrade (already on higher tier)
- `422 Unprocessable Entity`: Stripe payment failed

---

### 3. Downgrade Subscription

**Purpose**: Downgrade subscription to lower tier (takes effect at period end)

**Endpoint**: `POST /api/billing/subscription/downgrade`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**:
```json
{
  "new_plan": "starter",
  "reason": "reducing team size"
}
```

**Response 200 OK**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "plan_tier": "pro",
    "billing_cycle": "annual",
    "status": "active",
    "pending_downgrade": {
      "new_plan": "starter",
      "effective_date": "2026-01-01T00:00:00Z"
    },
    "cancel_at_period_end": false
  },
  "message": "Downgrade scheduled. Your Pro plan will continue until 2026-01-01, then switch to Starter."
}
```

**Business Rules**:
- Downgrade takes effect at end of current billing period (no refunds)
- Organization keeps higher tier access until period ends
- Can cancel downgrade before effective date

**Error Responses**:
- `400 Bad Request`: Invalid target plan
- `403 Forbidden`: Already on Free plan (cannot downgrade further)

---

### 4. Start Trial

**Purpose**: Start 14-day trial for Pro or Enterprise plan

**Endpoint**: `POST /api/billing/subscription/trial`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**:
```json
{
  "plan": "pro",
  "payment_method_id": "pm_1OQz8xJ2eZvKYlo2CiU7C9Vn"
}
```

**Response 201 Created**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "plan_tier": "pro",
    "status": "trialing",
    "trial_end_date": "2025-02-05T00:00:00Z",
    "trial_days_remaining": 14
  },
  "message": "Pro trial started. Full access for 14 days."
}
```

**Validation Rules**:
- Only `pro` and `enterprise` plans eligible for trial
- Must be on Free plan to start trial
- Payment method required (but not charged until trial ends)

**Error Responses**:
- `400 Bad Request`: Invalid plan (Starter not eligible for trial)
- `403 Forbidden`: Organization already had trial (one trial per org)
- `422 Unprocessable Entity`: Payment method verification failed

---

### 5. Cancel Subscription

**Purpose**: Cancel paid subscription (downgrades to Free at period end)

**Endpoint**: `POST /api/billing/subscription/cancel`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**:
```json
{
  "reason": "budget_constraints",
  "feedback": "Great product, but need to cut costs temporarily"
}
```

**Response 200 OK**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "plan_tier": "pro",
    "status": "active",
    "cancel_at_period_end": true,
    "cancels_at": "2026-01-01T00:00:00Z"
  },
  "retention_policy": {
    "data_retained_until": "2026-01-31T00:00:00Z",
    "reactivation_url": "/billing/reactivate"
  },
  "message": "Subscription will be cancelled on 2026-01-01. You can reactivate anytime before then."
}
```

**Business Rules**:
- Subscription continues until end of billing period
- No refunds for unused time
- Data retained for 30 days after cancellation
- Can reactivate before period ends (cancels cancellation)

**Error Responses**:
- `400 Bad Request`: Already on Free plan (nothing to cancel)

---

### 6. Reactivate Subscription

**Purpose**: Reactivate cancelled subscription before it takes effect

**Endpoint**: `POST /api/billing/subscription/reactivate`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**: (empty or optional)
```json
{}
```

**Response 200 OK**:
```json
{
  "subscription": {
    "id": "sub_a8f3e2c4d1b9",
    "plan_tier": "pro",
    "status": "active",
    "cancel_at_period_end": false
  },
  "message": "Subscription reactivated. Your Pro plan will continue renewing."
}
```

**Business Rules**:
- Can only reactivate if cancellation not yet effective
- Resumes normal renewal cycle
- No additional charges (still on current period)

**Error Responses**:
- `400 Bad Request`: Subscription not scheduled for cancellation
- `404 Not Found`: Subscription already cancelled (past period end)

---

### 7. Get Billing History

**Purpose**: Retrieve organization's billing transaction history

**Endpoint**: `GET /api/billing/history`

**Query Parameters**:
- `org_id` (required): Organization ID
- `limit` (optional, default: 10): Number of records to return
- `offset` (optional, default: 0): Pagination offset

**Request Example**:
```http
GET /api/billing/history?org_id=org_church_xyz&limit=10
Authorization: Bearer eyJ0eXAi...
```

**Response 200 OK**:
```json
{
  "billing_history": [
    {
      "id": "bh_9f2e1d3c4b5a",
      "event_type": "charge",
      "amount_cents": 75840,
      "currency": "usd",
      "payment_status": "succeeded",
      "description": "Annual Pro plan renewal",
      "invoice_pdf_url": "https://pay.stripe.com/invoice/...",
      "event_timestamp": "2025-01-01T00:00:00Z"
    },
    {
      "id": "bh_8e1d2c3b4a5f",
      "event_type": "subscription_change",
      "amount_cents": 5000,
      "currency": "usd",
      "payment_status": "succeeded",
      "description": "Upgraded from Starter to Pro",
      "event_timestamp": "2024-12-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

**Error Responses**:
- `403 Forbidden`: User not admin of organization

---

### 8. Download Invoice

**Purpose**: Generate and download invoice PDF

**Endpoint**: `GET /api/billing/invoice/{invoice_id}`

**Path Parameters**:
- `invoice_id`: Billing history record ID

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Example**:
```http
GET /api/billing/invoice/bh_9f2e1d3c4b5a?org_id=org_church_xyz
Authorization: Bearer eyJ0eXAi...
```

**Response 200 OK** (Redirect):
```http
HTTP/1.1 302 Found
Location: https://pay.stripe.com/invoice/acct_1032D82eZvKYlo2/test_YWNjdF8xMDMyRDgyZVp2S1lsbzIsX1BzVXhUckZvZ0RsdVBLaW9CNThRZlB4eUxpaUp6LDkwNTY5ODM1/pdf
```

**Business Rules**:
- Redirects to Stripe-hosted invoice PDF
- Invoice only accessible by organization owner
- PDFs available for 30 days after generation

**Error Responses**:
- `403 Forbidden`: Invoice belongs to different organization
- `404 Not Found`: Invoice ID not found

---

### 9. Get Usage Metrics

**Purpose**: Retrieve current usage metrics for analytics dashboard

**Endpoint**: `GET /api/billing/usage`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Example**:
```http
GET /api/billing/usage?org_id=org_church_xyz
Authorization: Bearer eyJ0eXAi...
```

**Response 200 OK**:
```json
{
  "plan": {
    "tier": "pro",
    "billing_cycle": "annual",
    "status": "active"
  },
  "metrics": [
    {
      "metric_type": "volunteers_count",
      "current_value": 35,
      "plan_limit": 200,
      "percentage_used": 17.5,
      "alert_threshold": 90,
      "show_alert": false
    }
  ],
  "forecast": {
    "next_invoice_date": "2026-01-01T00:00:00Z",
    "next_invoice_amount_cents": 75840,
    "projected_annual_cost_cents": 75840
  }
}
```

**Business Rules**:
- `show_alert: true` when `percentage_used >= 90%`
- Metrics updated in real-time (cached in `usage_metrics` table)

---

### 10. Update Payment Method

**Purpose**: Add or update organization's payment method

**Endpoint**: `POST /api/billing/payment-method`

**Query Parameters**:
- `org_id` (required): Organization ID

**Request Body**:
```json
{
  "stripe_payment_method_id": "pm_1OQz8xJ2eZvKYlo2CiU7C9Vn",
  "set_as_primary": true
}
```

**Response 200 OK**:
```json
{
  "payment_method": {
    "id": "pm_7e1f2d3c4b5a",
    "card_brand": "visa",
    "card_last4": "4242",
    "exp_month": 12,
    "exp_year": 2027,
    "is_primary": true
  },
  "message": "Payment method updated successfully"
}
```

**Validation Rules**:
- `stripe_payment_method_id`: Must be valid Stripe PaymentMethod ID
- Stripe validates card before accepting
- Old primary payment method marked as non-primary

**Error Responses**:
- `400 Bad Request`: Invalid payment method ID
- `402 Payment Required`: Card declined by Stripe
- `422 Unprocessable Entity`: Stripe validation failed

---

## Error Response Format

All error responses follow standard format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  }
}
```

**Common Error Codes**:
- `invalid_plan`: Plan tier not supported
- `payment_required`: Payment method needed
- `limit_exceeded`: Usage limit reached
- `trial_not_eligible`: Organization not eligible for trial
- `already_cancelled`: Subscription already cancelled
- `stripe_error`: Stripe API error (includes Stripe error code)

---

## Rate Limiting

**Limits**:
- 100 requests per minute per organization
- 10 subscription changes per hour per organization

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

---

## Webhook Events

When subscription changes occur, system emits internal events:

**Events**:
- `subscription.created`: New subscription created
- `subscription.upgraded`: Plan tier increased
- `subscription.downgraded`: Plan tier decreased
- `subscription.cancelled`: Subscription cancelled
- `subscription.reactivated`: Cancelled subscription resumed
- `trial.started`: Trial period started
- `trial.ending_soon`: 7/3 days before trial ends
- `trial.expired`: Trial ended without payment

**Event Payload**:
```json
{
  "event": "subscription.upgraded",
  "org_id": "org_church_xyz",
  "old_plan": "starter",
  "new_plan": "pro",
  "timestamp": "2025-01-22T15:30:00Z"
}
```

---

## Idempotency

**Idempotent Operations**:
- Upgrade/downgrade requests use idempotency keys
- Duplicate upgrade requests return existing subscription (no double-charge)

**Idempotency Key Header**:
```
Idempotency-Key: upgrade_org_church_xyz_1642694400
```

---

## Testing

**Test Mode**:
- Use Stripe test API keys: `sk_test_...`, `pk_test_...`
- Test payment methods: `pm_card_visa` (success), `pm_card_chargeDecline` (failure)
- Test webhooks with Stripe CLI: `stripe trigger customer.subscription.updated`

**E2E Test Scenarios**:
1. Free → Starter upgrade with valid payment method
2. Starter → Pro upgrade (prorated billing)
3. Pro → Enterprise upgrade
4. Pro → Starter downgrade (scheduled for period end)
5. Cancel Pro plan → Reactivate before cancellation
6. Start Pro trial → Convert to paid before trial ends
7. Start Pro trial → Expire trial without payment (auto-downgrade)
8. Payment failure → Retry logic → Downgrade after 3 failures

---

**API Contract Version**: 1.0
**Last Updated**: 2025-10-22
**Status**: Ready for Implementation
