# Feature Specification: Billing and Subscription System

**Feature Branch**: `011-billing-subscription-system`
**Created**: 2025-01-22
**Status**: Draft
**Input**: User description: "Billing and subscription system with Stripe integration for Free, Starter, Pro, and Enterprise plans. Include usage limit enforcement (10/50/200/unlimited volunteers), self-service billing portal, invoice generation, payment method management, subscription upgrade/downgrade, trial period support (14-day trial for paid plans), failed payment handling with retry logic, cancellation workflow with data retention policy, and webhook integration for payment events. Must integrate with existing Organization and Person models to enforce volunteer limits based on subscription tier. Support annual/monthly billing cycles with discount for annual. Include admin dashboard for subscription analytics."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Organization Signs Up for Free Plan (Priority: P1)

A new organization administrator creates an account and is automatically placed on the Free plan (10 volunteer limit) to start using SignUpFlow immediately without payment.

**Why this priority**: Foundation for all other billing features. Users must be able to start using the product before they pay. This delivers immediate value and reduces friction for new signups.

**Independent Test**: Create new organization account → verify organization assigned to Free plan → verify can add up to 10 volunteers → verify blocked from adding 11th volunteer with upgrade prompt

**Acceptance Scenarios**:

1. **Given** a new user signs up, **When** they complete registration, **Then** their organization is automatically assigned to Free plan with 10 volunteer limit
2. **Given** organization on Free plan with 9 volunteers, **When** admin adds 10th volunteer, **Then** volunteer is added successfully
3. **Given** organization on Free plan with 10 volunteers, **When** admin attempts to add 11th volunteer, **Then** system blocks action and displays "Upgrade to Starter plan to add more volunteers" message with upgrade link

---

### User Story 2 - Organization Upgrades to Paid Plan (Priority: P1)

An organization administrator upgrades from Free to Starter/Pro/Enterprise plan through self-service billing portal using credit card payment via Stripe.

**Why this priority**: Revenue generation critical path. Without this, product cannot monetize. This is the primary conversion funnel.

**Independent Test**: Login as Free plan admin → click "Upgrade" → select Starter plan (monthly) → enter payment details → complete checkout → verify organization upgraded to Starter plan → verify can now add 50 volunteers

**Acceptance Scenarios**:

1. **Given** organization on Free plan, **When** admin clicks "Upgrade Plan" button, **Then** billing portal displays plan options (Starter $29/mo, Pro $79/mo, Enterprise $199/mo)
2. **Given** admin selects Starter plan (monthly), **When** admin enters valid credit card, **Then** Stripe processes payment and organization upgraded to Starter plan immediately
3. **Given** organization just upgraded to Starter plan, **When** admin views dashboard, **Then** volunteer limit increased from 10 to 50
4. **Given** organization upgraded successfully, **When** admin checks email, **Then** receives confirmation email with invoice and plan details

---

### User Story 3 - Organization Starts 14-Day Trial (Priority: P2)

An organization on Free plan starts a 14-day trial of Pro or Enterprise plan to evaluate features before committing to payment, with automatic downgrade to Free if not upgraded before trial ends.

**Why this priority**: Increases conversion rates by allowing users to experience premium features risk-free. Reduces purchase anxiety and supports sales cycle.

**Independent Test**: Free plan admin → start Pro trial → verify upgraded to Pro immediately → wait 14 days → verify auto-downgraded to Free if no payment added

**Acceptance Scenarios**:

1. **Given** organization on Free plan, **When** admin clicks "Start Pro Trial", **Then** organization immediately upgraded to Pro plan (200 volunteer limit) with trial end date displayed
2. **Given** organization in trial period, **When** admin views billing page, **Then** sees "Trial ends in X days" with option to "Add Payment Method to Keep Pro Plan"
3. **Given** trial expires without payment method, **When** trial period ends, **Then** organization auto-downgraded to Free plan and admin receives email notification
4. **Given** organization has 150 volunteers during Pro trial, **When** trial ends and downgrades to Free, **Then** all volunteers retained but cannot add more until under Free limit or upgrade

---

### User Story 4 - Failed Payment Handling with Retry (Priority: P2)

When a subscription renewal payment fails (expired card, insufficient funds, etc.), system automatically retries payment and notifies admin, with grace period before service disruption.

**Why this priority**: Prevents revenue loss from unintentional churn. Maintains customer relationships by giving opportunity to fix payment issues before losing service.

**Independent Test**: Simulate failed payment in Stripe → verify retry attempts over 7 days → verify admin receives email notifications → verify organization not immediately downgraded

**Acceptance Scenarios**:

1. **Given** organization with Starter plan renewal due, **When** payment fails (expired card), **Then** system sends email to admin "Payment Failed - Update Payment Method"
2. **Given** payment failed, **When** first retry attempted (day 1), **Then** Stripe retries payment automatically
3. **Given** payment still failing, **When** 3 retry attempts over 7 days all fail, **Then** system sends final warning email "Service will be downgraded in 24 hours"
4. **Given** admin updates payment method during grace period, **When** payment successful, **Then** subscription continues without interruption and admin receives confirmation
5. **Given** all retries failed and grace period expired, **When** 8 days pass, **Then** organization downgraded to Free plan and admin notified

---

### User Story 5 - Subscription Upgrade/Downgrade (Priority: P2)

An organization administrator changes their subscription tier (Starter to Pro, Pro to Starter, etc.) with prorated billing and immediate access to new limits.

**Why this priority**: Flexibility to match growing or shrinking organization needs. Prevents forced cancellations when users need different tier.

**Independent Test**: Starter plan admin → upgrade to Pro mid-month → verify prorated charge → verify immediate access to 200 volunteer limit → verify next renewal at Pro price

**Acceptance Scenarios**:

1. **Given** organization on Starter plan ($29/mo), **When** admin upgrades to Pro ($79/mo) mid-month, **Then** charged prorated difference ($25 for remaining 15 days) immediately
2. **Given** organization just upgraded to Pro, **When** admin views limits, **Then** volunteer limit immediately increased from 50 to 200
3. **Given** organization on Pro plan, **When** admin downgrades to Starter, **Then** receives credit for unused Pro time applied to next Starter invoice
4. **Given** organization downgrades from Pro to Starter, **When** downgrade takes effect, **Then** volunteer limit reduced from 200 to 50 at end of current billing period (not immediately)

---

### User Story 6 - Annual Subscription with Discount (Priority: P3)

An organization administrator chooses annual billing instead of monthly to receive 20% discount (2 months free), paying upfront for 12 months.

**Why this priority**: Improves cash flow and reduces churn through longer commitment. Incentivizes larger upfront payments.

**Independent Test**: Admin on monthly Starter plan → switch to annual → verify discount applied → verify charged $278.40 (12 months - 20%) instead of $348 → verify next renewal in 12 months

**Acceptance Scenarios**:

1. **Given** organization on Starter monthly ($29/mo), **When** admin switches to annual billing, **Then** pricing page shows annual cost $278.40 (save $69.60 = 20% off)
2. **Given** admin confirms annual Starter plan, **When** payment processed, **Then** charged $278.40 upfront for full year
3. **Given** organization on annual plan, **When** admin views billing, **Then** sees "Next renewal: [date 12 months from now]"
4. **Given** organization wants to downgrade annual plan, **When** admin requests downgrade, **Then** refund calculated for unused time and new plan activated

---

### User Story 7 - Cancellation with Data Retention (Priority: P3)

An organization administrator cancels their paid subscription, with service continuing until end of current billing period and data retained for 30 days before permanent deletion.

**Why this priority**: Provides graceful exit path and re-activation opportunity. Prevents negative experiences from immediate data loss.

**Independent Test**: Admin cancels Pro plan → verify service continues until period end → verify data accessible for retention period → verify data deletion after retention period expires

**Acceptance Scenarios**:

1. **Given** organization on Pro plan with 15 days remaining, **When** admin clicks "Cancel Subscription", **Then** shown confirmation "Service continues until [end date], then downgrades to Free"
2. **Given** admin confirms cancellation, **When** cancellation processed, **Then** receives email "Subscription will end on [date]. Data retained for [retention period] for reactivation"
3. **Given** subscription cancelled, **When** billing period ends, **Then** organization downgraded to Free plan (10 volunteer limit)
4. **Given** organization downgraded but within retention period, **When** admin re-activates subscription, **Then** all data restored and immediately upgraded to selected plan
5. **Given** retention period expires without reactivation, **When** [retention period] days pass, **Then** organization data deleted and admin receives final notification email

---

### User Story 8 - Self-Service Billing Portal Management (Priority: P3)

An organization administrator manages billing details (payment methods, billing address, download invoices) through self-service portal without contacting support.

**Why this priority**: Reduces support burden and improves user autonomy. Essential for scalable SaaS business model.

**Independent Test**: Admin logs in → accesses billing portal → updates payment method → downloads invoice PDF → verifies changes reflected immediately

**Acceptance Scenarios**:

1. **Given** admin on paid plan, **When** clicks "Billing Settings", **Then** billing portal displays current plan, payment method, and billing history
2. **Given** admin in billing portal, **When** clicks "Update Payment Method", **Then** Stripe modal opens to enter new credit card details
3. **Given** admin updates payment method successfully, **When** changes saved, **Then** new card shown as primary payment method and old card removed
4. **Given** admin wants past invoices, **When** views billing history, **Then** sees list of all invoices with download PDF links
5. **Given** admin clicks download invoice, **When** PDF generates, **Then** invoice includes organization name, plan details, amount paid, and date

---

### User Story 9 - Admin Dashboard Subscription Analytics (Priority: P3)

An organization administrator views subscription analytics dashboard showing usage metrics (volunteers used vs limit, storage, API calls) and billing forecast.

**Why this priority**: Helps organizations manage their subscription tier effectively and predict costs. Informs upgrade/downgrade decisions.

**Independent Test**: Admin views analytics dashboard → verify shows volunteer usage (35/50) → verify shows current plan cost → verify shows projected next invoice amount

**Acceptance Scenarios**:

1. **Given** organization on Starter plan (50 volunteer limit), **When** admin views analytics dashboard, **Then** sees "Volunteers: 35/50 (70% used)"
2. **Given** organization approaching volunteer limit, **When** usage reaches 90% (45/50 volunteers), **Then** dashboard displays "Nearing limit - Consider upgrading to Pro for 200 volunteers"
3. **Given** organization on monthly Pro plan, **When** admin views billing forecast, **Then** shows "Next charge: $79 on [renewal date]"
4. **Given** organization exceeds volunteer limit temporarily during trial, **When** trial ends, **Then** analytics shows "Currently over Free plan limit (25/10) - Upgrade required to add more volunteers"

---

### Edge Cases

- **What happens when organization exceeds volunteer limit?**
  System prevents adding new volunteers beyond limit. Displays upgrade prompt with specific messaging: "You've reached your [plan name] limit of [X] volunteers. Upgrade to [next tier] for [Y] volunteers." Existing volunteers remain accessible.

- **How does system handle payment failures during trial period?**
  Trial continues even if payment method on file fails (since trial is free). Admin notified that payment method needs updating before trial ends to maintain service.

- **What if user downgrade would put them over new limit?**
  Downgrade allowed but organization placed in "over-limit" state: cannot add new volunteers until under limit OR re-upgrade. Existing volunteers remain active (no forced deletion).

- **How are partial months handled for annual-to-monthly switch?**
  Unused annual time calculated as credit, applied to monthly invoices until credit exhausted. Example: 6 months remaining on annual Starter ($139.20 credit) = ~4.8 months free on monthly Starter ($29/mo).

- **What happens to subscription if organization deleted?**
  Subscription cancelled immediately in Stripe. No further charges. Organization data deleted per retention policy (30 days). No refunds issued for mid-billing period deletions (service remains active until current period ends if user chooses to continue using it).

- **How does system handle Stripe webhook failures?**
  Webhook events queued with retry logic (exponential backoff). System polls Stripe API every 6 hours as fallback to sync subscription status if webhooks fail. Admin dashboard shows "Billing sync pending" if webhook delayed.

- **What if enterprise customer needs custom limits?**
  Enterprise plan has soft limit of 2000 volunteers. Organizations requiring more can contact sales for custom pricing and higher limits. This prevents system abuse while covering 99.9% of use cases (largest churches typically have 500-800 active volunteers).

## Requirements *(mandatory)*

### Functional Requirements

**Subscription Management**

- **FR-001**: System MUST support four subscription tiers: Free (10 volunteers), Starter ($29/mo, 50 volunteers), Pro ($79/mo, 200 volunteers), Enterprise ($199/mo, unlimited volunteers)
- **FR-002**: System MUST automatically assign Free plan to all new organizations upon signup
- **FR-003**: System MUST enforce volunteer limits based on organization's current subscription tier (prevent adding volunteers beyond limit)
- **FR-004**: System MUST integrate with existing Organization model to track current subscription tier and limits
- **FR-005**: System MUST integrate with existing Person model to count active volunteers for limit enforcement

**Payment Processing**

- **FR-006**: System MUST integrate with Stripe API for payment processing and subscription management
- **FR-007**: System MUST support credit card payments through Stripe checkout flow
- **FR-008**: System MUST process subscription upgrades immediately with prorated billing
- **FR-009**: System MUST process subscription downgrades at end of current billing period (no immediate limit reduction)
- **FR-010**: System MUST support both monthly and annual billing cycles
- **FR-011**: System MUST apply 20% discount to annual subscriptions (equivalent to 2 months free)

**Trial Management**

- **FR-012**: System MUST support 14-day free trial for Pro and Enterprise plans (not applicable to Free or Starter plans without trials)
- **FR-013**: System MUST immediately grant trial tier access when trial started
- **FR-014**: System MUST automatically downgrade organization to Free plan when trial expires without payment method added
- **FR-015**: System MUST send email notifications at trial start, 7 days remaining, 3 days remaining, and trial expiration

**Failed Payment Handling**

- **FR-016**: System MUST automatically retry failed payments using Stripe's retry logic (3 attempts over 7 days)
- **FR-017**: System MUST send email notification to admin immediately after payment failure
- **FR-018**: System MUST send warning emails at 3 days and 1 day before service downgrade after failed payment
- **FR-019**: System MUST downgrade organization to Free plan 8 days after initial payment failure if all retries fail
- **FR-020**: System MUST allow admin to update payment method during grace period to prevent downgrade

**Cancellation & Data Retention**

- **FR-021**: System MUST allow admin to cancel subscription at any time through billing portal
- **FR-022**: System MUST continue service until end of current billing period after cancellation
- **FR-023**: System MUST downgrade cancelled organization to Free plan at end of billing period
- **FR-024**: System MUST retain all organization data for [specified retention period] after downgrade to Free
- **FR-025**: System MUST allow reactivation of subscription during retention period with full data restoration
- **FR-026**: System MUST permanently delete organization data after retention period expires if not reactivated

**Billing Portal**

- **FR-027**: System MUST provide self-service billing portal for admins to view current plan, payment methods, and billing history
- **FR-028**: System MUST allow admins to update payment methods through Stripe billing portal
- **FR-029**: System MUST allow admins to update billing address and tax information
- **FR-030**: System MUST display list of all past invoices with download PDF links
- **FR-031**: System MUST generate invoice PDFs containing organization name, plan details, amount, date, and line items

**Webhook Integration**

- **FR-032**: System MUST listen for Stripe webhook events (payment succeeded, payment failed, subscription updated, subscription deleted)
- **FR-033**: System MUST update organization subscription status based on webhook events within 60 seconds
- **FR-034**: System MUST queue webhook events with retry logic if initial processing fails
- **FR-035**: System MUST verify webhook signatures to prevent unauthorized requests
- **FR-036**: System MUST log all webhook events for audit trail

**Analytics Dashboard**

- **FR-037**: System MUST display admin analytics dashboard showing volunteer usage vs limit
- **FR-038**: System MUST show current plan name, pricing, and next renewal date on dashboard
- **FR-039**: System MUST calculate and display billing forecast for next invoice
- **FR-040**: System MUST alert admin when volunteer usage reaches 90% of limit with upgrade suggestion
- **FR-041**: System MUST show historical billing chart (last 12 months of charges)

**Usage Limit Enforcement**

- **FR-042**: System MUST block admin from adding volunteers when at plan limit with specific error message
- **FR-043**: System MUST display "Upgrade to [next tier]" prompt when admin attempts to exceed volunteer limit
- **FR-044**: System MUST allow organizations to view but not add volunteers when in over-limit state after downgrade
- **FR-045**: System MUST automatically re-enable volunteer additions when organization upgrades to higher tier

### Key Entities

- **Subscription**: Represents organization's current subscription tier and billing status
  - Current plan tier (Free, Starter, Pro, Enterprise)
  - Billing cycle (monthly, annual)
  - Status (active, trialing, past_due, cancelled, incomplete)
  - Trial end date (if applicable)
  - Current period start and end dates
  - Stripe subscription ID (for paid plans)
  - Created and updated timestamps

- **BillingHistory**: Historical record of all billing events
  - Organization reference
  - Event type (charge, refund, subscription change, trial start/end)
  - Amount charged or refunded
  - Payment status (succeeded, failed, pending)
  - Invoice URL for PDF download
  - Stripe invoice ID
  - Event timestamp

- **PaymentMethod**: Organization's stored payment information (managed by Stripe)
  - Organization reference
  - Stripe payment method ID
  - Card brand (Visa, Mastercard, etc.)
  - Last 4 digits of card
  - Expiration month/year
  - Billing address
  - Is primary payment method flag
  - Added timestamp

- **UsageMetrics**: Tracks organization resource consumption
  - Organization reference
  - Metric type (volunteers_count, events_count, storage_mb, api_calls)
  - Current value
  - Plan limit for this metric
  - Percentage used (calculated)
  - Last updated timestamp

- **SubscriptionEvent**: Audit log of all subscription changes
  - Organization reference
  - Event type (created, upgraded, downgraded, trial_started, cancelled, reactivated)
  - Previous plan (if applicable)
  - New plan
  - Admin who initiated change
  - Event timestamp
  - Additional metadata (reason, notes)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New organizations can be assigned to Free plan automatically within 1 second of signup completion
- **SC-002**: Users can upgrade from Free to paid plan in under 3 minutes (from clicking "Upgrade" to confirmation)
- **SC-003**: Volunteer limit enforcement prevents 100% of attempts to add volunteers beyond plan limit with clear upgrade messaging
- **SC-004**: 90% of failed payments successfully retry and recover within 7-day grace period
- **SC-005**: Subscription downgrades take effect within 24 hours of billing period end
- **SC-006**: Admin billing portal loads all information (plan, payment method, invoices) in under 2 seconds
- **SC-007**: Invoice PDFs generate and download in under 5 seconds
- **SC-008**: Stripe webhook events processed and organization status updated within 60 seconds of event
- **SC-009**: Analytics dashboard shows current usage metrics accurate within 5 minutes of data changes
- **SC-010**: Trial-to-paid conversion tracked accurately with 100% of trials either converting or downgrading at expiration
- **SC-011**: Zero billing errors or double-charges due to webhook sync issues (99.9% webhook reliability)
- **SC-012**: Admin can complete full subscription lifecycle (sign up → trial → upgrade → downgrade → cancel → reactivate) in single session for testing purposes

