# Feature Specification: Billing & Subscription System

**Feature Branch**: `002-billing-subscription-system`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Billing and subscription system with Stripe integration for Free, Starter, Pro, and Enterprise plans. Include usage limit enforcement (10/50/200/unlimited volunteers), self-service billing portal, invoice generation, payment method management, subscription upgrade/downgrade, trial period support (14-day trial for paid plans), failed payment handling with retry logic, cancellation workflow with data retention policy, and webhook integration for payment events. Must integrate with existing Organization and Person models to enforce volunteer limits based on subscription tier. Support annual/monthly billing cycles with discount for annual. Include admin dashboard for subscription analytics."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Self-Service Subscription Sign-Up (Priority: P1)

Organization administrators can select and subscribe to a paid plan directly through the application without requiring sales contact. They can start with a 14-day free trial, enter payment information securely, and immediately unlock higher volunteer limits.

**Why this priority**: This is the core monetization flow. Without self-service sign-up, the product cannot generate revenue. This is the minimum viable billing feature that enables commercial launch.

**Independent Test**: Can be fully tested by creating a new organization account, selecting the Starter plan ($29/mo), entering test payment information, and verifying the organization's volunteer limit increases from 10 to 50 volunteers immediately.

**Acceptance Scenarios**:

1. **Given** an organization on the Free plan with 8 volunteers, **When** admin selects Starter plan and completes payment, **Then** volunteer limit increases to 50 and admin receives confirmation email with invoice
2. **Given** an organization selecting a paid plan, **When** admin chooses annual billing, **Then** system shows 15% discount applied and charges annual amount upfront
3. **Given** admin entering payment information, **When** payment fails (insufficient funds), **Then** system shows clear error message and allows retry without losing plan selection
4. **Given** an organization starting a 14-day trial, **When** trial begins, **Then** organization gains full plan features and trial end date is clearly displayed
5. **Given** trial period ending in 3 days, **When** admin logs in, **Then** system displays prominent reminder to add payment method

---

### User Story 2 - Usage Limit Enforcement (Priority: P1)

System automatically enforces volunteer limits based on the organization's current subscription tier. When an organization reaches their volunteer limit, admins receive clear messaging and guidance to upgrade their plan.

**Why this priority**: Without limit enforcement, there's no incentive to upgrade from Free plan. This is essential for the business model and must work immediately at launch to prevent revenue loss.

**Independent Test**: Can be fully tested by creating a Free plan organization (10 volunteer limit), adding 10 volunteers successfully, then attempting to add an 11th volunteer and verifying the system blocks creation with upgrade prompt.

**Acceptance Scenarios**:

1. **Given** a Free plan organization with 10 volunteers, **When** admin attempts to add 11th volunteer, **Then** system displays "Volunteer limit reached. Upgrade to Starter plan for 50 volunteers" with upgrade button
2. **Given** an organization with 45 volunteers on Starter plan (50 limit), **When** admin views people list, **Then** system shows "5 volunteer slots remaining" indicator
3. **Given** an organization at volunteer limit, **When** admin removes a volunteer, **Then** system immediately allows adding a new volunteer
4. **Given** an organization upgrading from Free to Starter, **When** upgrade completes, **Then** system immediately allows adding volunteers up to new limit (50)
5. **Given** a Pro plan organization (200 limit), **When** admin attempts to add 201st volunteer, **Then** system shows upgrade prompt for Enterprise plan

---

### User Story 3 - Subscription Upgrade/Downgrade (Priority: P2)

Organization administrators can upgrade to a higher plan immediately or downgrade to a lower plan (effective at next billing cycle). Upgrades are prorated, and downgrades preserve data until next cycle.

**Why this priority**: Allows customers to self-manage their subscription lifecycle, reducing support burden and improving customer satisfaction. Critical for customer retention but not required for initial launch.

**Independent Test**: Can be fully tested by subscribing to Starter plan, using it for 15 days, upgrading to Pro, and verifying prorated charge calculation and immediate limit increase to 200 volunteers.

**Acceptance Scenarios**:

1. **Given** an organization on Starter plan ($29/mo) 15 days into billing cycle, **When** admin upgrades to Pro plan ($99/mo), **Then** system charges prorated amount ($35 for remaining 15 days) and updates limit immediately
2. **Given** an organization on Pro plan, **When** admin requests downgrade to Starter, **Then** system schedules downgrade for next billing date and shows "Downgrade scheduled for [date]" confirmation
3. **Given** an organization scheduled to downgrade from Pro (200 limit) to Starter (50 limit) with 120 volunteers, **When** downgrade date arrives, **Then** system prevents downgrade and notifies admin to reduce volunteers first
4. **Given** an organization on monthly billing, **When** admin switches to annual billing, **Then** system calculates prorated credit and charges annual amount minus credit
5. **Given** an organization upgrading from Starter to Enterprise, **When** upgrade button clicked, **Then** system shows "Contact sales for Enterprise pricing" and creates sales inquiry

---

### User Story 4 - Payment Method Management (Priority: P2)

Organization administrators can view, add, update, and remove payment methods through a secure self-service portal. System handles card expiration notifications and allows updating payment methods before billing failures.

**Why this priority**: Reduces involuntary churn from expired cards and payment failures. Important for revenue retention but not blocking initial launch since initial payment capture works via Story 1.

**Independent Test**: Can be fully tested by subscribing to a plan, navigating to billing settings, adding a second payment method, setting it as default, and verifying next invoice charges the new card.

**Acceptance Scenarios**:

1. **Given** an organization with active subscription, **When** admin navigates to billing settings, **Then** system displays current payment method (last 4 digits, expiration date, card brand)
2. **Given** admin viewing payment methods, **When** admin clicks "Add payment method", **Then** secure Stripe-hosted form appears for entering card details
3. **Given** an organization with card expiring in 30 days, **When** billing date approaches, **Then** system emails admin reminder to update payment method
4. **Given** admin adding a new payment method, **When** new card is saved, **Then** system offers to set it as default payment method
5. **Given** an organization with payment method set to expire, **When** admin updates card, **Then** system confirms successful update and removes expiration warning

---

### User Story 5 - Failed Payment Recovery (Priority: P2)

System automatically retries failed payments using intelligent retry logic, sends notifications to admins, and gracefully downgrades organizations only after multiple retry attempts fail.

**Why this priority**: Minimizes involuntary churn and revenue loss from temporary payment failures. Important for revenue retention but can be implemented after launch with manual intervention initially.

**Independent Test**: Can be fully tested by simulating a failed payment (test card with insufficient funds), verifying system retries after 3 days, 5 days, and 7 days, then finally downgrades to Free plan after all retries fail.

**Acceptance Scenarios**:

1. **Given** a subscription payment fails due to insufficient funds, **When** initial charge fails, **Then** system sends immediate email notification to admin with "Update payment method" link
2. **Given** initial payment retry fails, **When** 3 days pass, **Then** system attempts second retry and sends reminder email if it fails
3. **Given** two payment retries have failed, **When** 7 days pass after first failure, **Then** system attempts final retry before downgrade
4. **Given** all payment retries have failed (days 1, 3, 7), **When** final retry fails, **Then** system sends "Subscription suspended" email and schedules downgrade to Free plan in 3 days
5. **Given** organization in grace period after failed payments, **When** admin updates payment method and confirms retry, **Then** system immediately attempts charge and restores full access if successful

---

### User Story 6 - Invoice Generation & History (Priority: P3)

Organization administrators can view, download, and email invoices for all subscription charges. Invoices include detailed line items, tax information, and organization details for accounting purposes.

**Why this priority**: Important for B2B customers and accounting compliance but not blocking launch. Can be added post-launch as invoices are generated automatically by payment processor initially.

**Independent Test**: Can be fully tested by completing a subscription payment, navigating to billing history, and downloading a PDF invoice that includes organization name, charge amount, date, and line items.

**Acceptance Scenarios**:

1. **Given** an organization with active subscription, **When** admin navigates to billing history, **Then** system displays list of all invoices with date, amount, status, and download link
2. **Given** admin viewing invoice list, **When** admin clicks "Download PDF", **Then** system generates PDF invoice with organization details, line items, subtotal, tax, and total
3. **Given** a subscription charge completes, **When** payment succeeds, **Then** system automatically emails invoice PDF to organization admin
4. **Given** an organization upgrading mid-cycle, **When** prorated charge occurs, **Then** invoice clearly shows prorated calculation and remaining days
5. **Given** admin viewing invoice, **When** organization details (name, address) are updated, **Then** future invoices reflect updated information while past invoices remain unchanged

---

### User Story 7 - Subscription Cancellation (Priority: P3)

Organization administrators can cancel their subscription at any time with clear understanding of what happens to their data. Cancelled subscriptions remain active until the end of the paid period, then downgrade to Free plan with data preserved according to retention policy.

**Why this priority**: Required for customer trust and legal compliance but not blocking launch. Can be handled manually via support initially while building automated flow.

**Independent Test**: Can be fully tested by subscribing to Starter plan, using it for 10 days, cancelling subscription, verifying access continues for remaining 20 days, then confirming automatic downgrade to Free plan with volunteer limit enforced.

**Acceptance Scenarios**:

1. **Given** an organization on paid plan, **When** admin clicks "Cancel subscription", **Then** system displays confirmation modal explaining access continues until end of billing period
2. **Given** admin confirming cancellation, **When** cancellation is processed, **Then** system sends confirmation email with cancellation date and data retention details
3. **Given** a cancelled subscription with 15 days remaining, **When** admin logs in, **Then** dashboard shows "Subscription cancelled - access until [date]" banner
4. **Given** cancelled subscription reaching end date, **When** billing period ends, **Then** system automatically downgrades to Free plan and enforces 10 volunteer limit
5. **Given** an organization downgrading from Pro (200 volunteers) to Free (10 volunteers) with 50 volunteers, **When** downgrade occurs, **Then** system preserves all volunteer data but blocks creating new volunteers until count is reduced

---

### User Story 8 - Admin Subscription Analytics Dashboard (Priority: P3)

Platform administrators (SignUpFlow team) can view subscription analytics including revenue metrics, churn rate, plan distribution, trial conversion rates, and failed payment statistics through an internal dashboard.

**Why this priority**: Important for business monitoring and decision-making but not customer-facing. Can be built post-launch using database queries initially while automated dashboard is developed.

**Independent Test**: Can be fully tested by accessing the admin analytics dashboard and verifying it displays current subscriber counts by plan, monthly recurring revenue (MRR), trial conversion rate, and churn rate for the last 30 days.

**Acceptance Scenarios**:

1. **Given** platform admin accessing analytics dashboard, **When** dashboard loads, **Then** displays key metrics: total active subscriptions, MRR, annual recurring revenue (ARR), and month-over-month growth
2. **Given** admin viewing plan distribution, **When** dashboard renders, **Then** shows breakdown of organizations by plan tier (Free, Starter, Pro, Enterprise) with counts and percentages
3. **Given** admin analyzing trial performance, **When** viewing trial metrics, **Then** displays trial-to-paid conversion rate, average trial length, and reasons for trial abandonment
4. **Given** admin monitoring payment health, **When** viewing payment metrics, **Then** shows failed payment rate, successful retry rate, and involuntary churn rate
5. **Given** admin analyzing revenue trends, **When** viewing revenue charts, **Then** displays MRR growth over time, plan upgrade/downgrade patterns, and customer lifetime value by cohort

---

### Edge Cases

- What happens when an organization exceeds their volunteer limit after a downgrade is scheduled?
  - System prevents downgrade from completing and notifies admin to reduce volunteers before downgrade can proceed
  - Admin receives email: "Scheduled downgrade blocked: You have 120 volunteers but Starter plan allows 50. Remove 70 volunteers to complete downgrade."

- How does system handle payment failures during trial period?
  - Trial continues regardless of payment method issues
  - At trial end, if payment method is invalid, system blocks upgrade to paid features and sends notification
  - Organization reverts to Free plan features if payment cannot be captured

- What happens when Stripe webhook fails to deliver payment event?
  - System includes webhook retry logic (attempts delivery 3 times with exponential backoff)
  - Failed webhooks are logged for manual review in admin dashboard
  - System polls Stripe API every 15 minutes as backup to catch missed events

- How does system handle subscription changes during billing cycle?
  - Upgrades: Applied immediately with prorated charge for remaining days
  - Downgrades: Scheduled for next billing cycle, current plan benefits continue until then
  - Plan changes during trial: Trial period resets to 14 days for the new plan

- What happens when organization attempts to add 11th volunteer on Free plan but upgrade payment fails?
  - Volunteer creation remains blocked until payment succeeds
  - System displays: "Volunteer limit reached. Upgrade failed: [payment error]. Please update payment method and retry."
  - Admin can retry upgrade or remove existing volunteer to stay on Free plan

- How does system handle annual to monthly billing cycle changes?
  - System calculates unused portion of annual subscription (remaining months ÷ 12 × annual charge)
  - Credit is applied to account and used against monthly charges until depleted
  - After credit depletes, normal monthly billing resumes

- What happens when Enterprise customer cancels and has 500 volunteers (exceeding all paid plan limits)?
  - System preserves all 500 volunteers in read-only mode
  - Organization cannot add/edit volunteers until they upgrade or reduce count
  - Data is not deleted; only volunteer limit enforcement is applied

- How does system handle payment method removal when it's the only active payment method?
  - System prevents removal and displays: "Cannot remove only payment method. Add a new payment method first."
  - If organization wants to cancel, they must use subscription cancellation flow instead

## Requirements *(mandatory)*

### Functional Requirements

#### Subscription Management

- **FR-001**: System MUST support four subscription tiers: Free (10 volunteers, $0/mo), Starter (50 volunteers, $29/mo), Pro (200 volunteers, $99/mo), Enterprise (unlimited volunteers, custom pricing)
- **FR-002**: System MUST enforce volunteer limits based on organization's current subscription tier, blocking creation of volunteers when limit is reached
- **FR-003**: System MUST allow organization administrators to view current subscription details including plan name, billing cycle, next billing date, and volunteer usage
- **FR-004**: System MUST support both monthly and annual billing cycles with 15% discount applied to annual subscriptions
- **FR-005**: System MUST offer 14-day free trial for all paid plans (Starter, Pro, Enterprise) with full feature access during trial period
- **FR-006**: System MUST capture payment method during trial sign-up and automatically charge when trial ends
- **FR-007**: System MUST allow administrators to upgrade subscription immediately with prorated charges calculated for remaining billing cycle days
- **FR-008**: System MUST allow administrators to downgrade subscription effective at next billing cycle to preserve current paid benefits
- **FR-009**: System MUST prevent downgrades when organization's volunteer count exceeds target plan's limit
- **FR-010**: System MUST persist subscription status to Organization model with fields: plan_tier, billing_cycle, trial_end_date, subscription_status, volunteer_limit

#### Payment Processing

- **FR-011**: System MUST integrate with Stripe for payment processing using Stripe Checkout for secure card entry
- **FR-012**: System MUST store Stripe customer ID and subscription ID on Organization model for webhook correlation
- **FR-013**: System MUST support adding, updating, and removing payment methods via Stripe billing portal
- **FR-014**: System MUST set default payment method for subscription charges
- **FR-015**: System MUST handle webhook events from Stripe including: payment_succeeded, payment_failed, customer.subscription.updated, customer.subscription.deleted
- **FR-016**: System MUST implement webhook signature verification to prevent fraudulent events
- **FR-017**: System MUST retry webhook processing up to 3 times with exponential backoff (5s, 25s, 125s) for failed deliveries
- **FR-018**: System MUST implement idempotency for webhook processing to prevent duplicate actions from retry deliveries

#### Failed Payment Handling

- **FR-019**: System MUST implement automatic payment retry logic: Day 0 (initial attempt), Day 3 (first retry), Day 7 (second retry), Day 10 (final retry before suspension)
- **FR-020**: System MUST send email notification to organization admin immediately when payment fails with clear instructions to update payment method
- **FR-021**: System MUST send reminder emails on Day 3 and Day 7 if payment retries continue to fail
- **FR-022**: System MUST send final warning email on Day 10 before subscription suspension
- **FR-023**: System MUST suspend subscription after all retry attempts fail, scheduling downgrade to Free plan to occur 3 days after suspension
- **FR-024**: System MUST allow admin to update payment method and manually retry payment during grace period (Days 0-13)
- **FR-025**: System MUST restore full subscription access immediately when failed payment is successfully captured during grace period

#### Invoice Management

- **FR-026**: System MUST generate invoices automatically for all subscription charges including trial-to-paid conversions, monthly charges, annual charges, and upgrade prorations
- **FR-027**: System MUST store invoice data including: invoice_number, organization_id, charge_date, amount, status, line_items, stripe_invoice_id
- **FR-028**: System MUST email invoice PDF to organization admin within 24 hours of successful payment
- **FR-029**: System MUST allow administrators to view invoice history with filters by date range and status
- **FR-030**: System MUST allow administrators to download invoice PDFs for accounting purposes
- **FR-031**: System MUST include organization details (name, address, tax ID) on invoices that can be updated for future invoices
- **FR-032**: System MUST support invoice line items showing: plan name, billing period, quantity (volunteer count for usage-based), unit price, subtotal, tax, and total

#### Cancellation & Data Retention

- **FR-033**: System MUST allow organization administrators to cancel subscription at any time through self-service portal
- **FR-034**: System MUST continue subscription access until end of paid billing period after cancellation
- **FR-035**: System MUST automatically downgrade organization to Free plan at end of billing period after cancellation
- **FR-036**: System MUST enforce volunteer limit (10) when downgrading to Free plan but preserve all existing volunteer data
- **FR-037**: System MUST preserve all organization data indefinitely when downgrading to Free plan (events, assignments, availability, teams)
- **FR-038**: System MUST allow organization to upgrade from cancelled/downgraded state to paid plan at any time without data loss
- **FR-039**: System MUST send cancellation confirmation email including: cancellation date, access end date, data retention policy, and reactivation instructions

#### Admin Analytics Dashboard

- **FR-040**: System MUST provide internal admin dashboard accessible only to SignUpFlow platform administrators (not organization admins)
- **FR-041**: Dashboard MUST display key revenue metrics: total active subscriptions, monthly recurring revenue (MRR), annual recurring revenue (ARR), month-over-month growth percentage
- **FR-042**: Dashboard MUST show subscription distribution: count and percentage of organizations on each plan tier (Free, Starter, Pro, Enterprise)
- **FR-043**: Dashboard MUST track trial metrics: trial-to-paid conversion rate, average trial length, active trials count, trials ending in next 7 days
- **FR-044**: Dashboard MUST monitor payment health: failed payment rate, successful retry rate, involuntary churn rate (cancellations due to payment failure)
- **FR-045**: Dashboard MUST display revenue trends over time with charts showing MRR growth, upgrade/downgrade patterns, and customer lifetime value by cohort
- **FR-046**: Dashboard MUST provide webhook delivery monitoring showing: successful deliveries, failed deliveries requiring manual review, and retry statistics

#### Integration with Existing Models

- **FR-047**: System MUST extend Organization model with subscription fields: stripe_customer_id, stripe_subscription_id, plan_tier (enum), billing_cycle (enum), subscription_status (enum), trial_end_date, volunteer_limit (integer)
- **FR-048**: System MUST validate volunteer count against volunteer_limit field when creating new Person records with role "volunteer"
- **FR-049**: System MUST update volunteer_limit immediately when subscription changes (upgrade/downgrade/trial start)
- **FR-050**: System MUST add GET /api/organizations/{org_id}/subscription endpoint returning current subscription details
- **FR-051**: System MUST add POST /api/billing/create-checkout-session endpoint to initiate Stripe Checkout for plan selection
- **FR-052**: System MUST add POST /api/billing/create-portal-session endpoint to redirect admin to Stripe billing portal for payment method management
- **FR-053**: System MUST add POST /api/billing/webhooks endpoint to receive and process Stripe webhook events
- **FR-054**: System MUST add GET /api/billing/invoices endpoint to retrieve organization's invoice history with pagination

### Key Entities

- **Subscription**: Represents an organization's billing relationship including plan tier (Free/Starter/Pro/Enterprise), billing cycle (monthly/annual), status (active/trialing/past_due/cancelled), trial period, volunteer limit, and Stripe identifiers

- **Invoice**: Represents a billing charge including invoice number, organization reference, charge date, amount, payment status, line items (plan details, prorations, credits), and PDF download link

- **PaymentMethod**: Represents a stored payment instrument including card brand, last 4 digits, expiration date, default status, and Stripe payment method ID

- **WebhookEvent**: Represents an incoming Stripe webhook including event type, payload, processing status, retry count, and correlation to affected subscription/invoice

- **SubscriptionTier**: Configuration entity defining plan limits and pricing including tier name, volunteer limit, monthly price, annual price (with discount), feature flags, and display order

- **UsageMetric**: Tracks organization resource usage including current volunteer count, event count, and other countable resources used for limit enforcement and analytics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Organization administrators can complete self-service subscription sign-up from plan selection to payment confirmation in under 5 minutes
- **SC-002**: System enforces volunteer limits with 100% accuracy - no organization can exceed their plan's volunteer limit
- **SC-003**: Failed payment recovery rate of at least 40% through automatic retry logic before subscription suspension
- **SC-004**: Invoice generation occurs within 24 hours of successful payment for 99% of charges
- **SC-005**: Subscription upgrade applies new volunteer limits within 60 seconds of payment confirmation
- **SC-006**: Webhook processing completes within 30 seconds for 95% of events
- **SC-007**: Admin analytics dashboard loads within 3 seconds and displays current metrics without manual refresh
- **SC-008**: Trial-to-paid conversion rate of at least 25% for organizations that add more than 5 volunteers during trial
- **SC-009**: Zero involuntary data loss during subscription downgrades or cancellations
- **SC-010**: 90% of organizations successfully update payment method when card expiration notification is sent
- **SC-011**: Support ticket volume related to billing questions remains below 5% of active subscriptions per month
- **SC-012**: Payment processing errors (excluding legitimate declines) occur in less than 0.5% of transactions

## Assumptions

1. **Stripe as Payment Processor**: Specification assumes Stripe is the chosen payment processor. Alternative processors (PayPal, Braintree) would require different integration approach.

2. **US Dollar Pricing**: Pricing is specified in USD ($29, $99). Multi-currency support is not included in this specification but may be required for international expansion.

3. **Sales-Assisted Enterprise Plan**: Enterprise tier requires "Contact Sales" rather than self-service sign-up. This is industry standard for unlimited/custom pricing tiers.

4. **Email as Primary Communication**: All notifications (payment failures, trial reminders, invoices) use email. SMS or in-app notifications are not included but could be added later.

5. **14-Day Trial Standard**: 14 days is chosen as industry standard for SaaS free trials. This duration may need adjustment based on actual user onboarding data.

6. **15% Annual Discount**: Annual billing discount set at 15% (roughly 2 months free) as competitive industry standard. This can be adjusted based on financial modeling.

7. **Data Preservation Policy**: All organization data is preserved indefinitely when downgrading to Free plan. Alternative policies (90-day retention, archive-then-delete) may be required for storage cost management at scale.

8. **Volunteer Count as Primary Limit**: Subscription tiers differentiate primarily on volunteer count limits. Future iterations may add feature-based differentiation (advanced analytics, priority support, custom branding).

9. **Immediate Upgrade, Deferred Downgrade**: Upgrades apply immediately (good UX), downgrades defer to next billing cycle (prevents revenue loss from accidental downgrades). This is SaaS best practice.

10. **Webhook as Primary Integration**: Stripe webhooks are primary mechanism for payment event processing. Polling Stripe API is backup only. This requires webhook endpoint reliability.

11. **Self-Service Billing Portal**: Organizations manage their own payment methods via Stripe-hosted billing portal rather than custom UI. This reduces PCI compliance burden and development time.

12. **No Metered Billing**: Volunteer limits are binary (under limit = allowed, at limit = blocked) rather than metered charges. Metered billing (pay per volunteer) would require different data model.

## Dependencies

- **Stripe Account**: Requires SignUpFlow business Stripe account with API keys (publishable key and secret key) and webhook signing secret
- **Email Service**: Depends on email notification system (Feature 001) for sending payment failure alerts, trial reminders, and invoice delivery
- **Organization Model**: Extends existing Organization model with subscription-related fields (must not break existing functionality)
- **Person Model**: Integrates with existing Person creation logic to enforce volunteer limits (requires volunteer count validation before save)
- **Authentication System**: Requires current user authentication to identify organization admin and verify permissions for billing operations
- **Existing API Structure**: Billing endpoints must follow existing FastAPI patterns (security dependencies, error handling, response schemas)

## Out of Scope

- **Multi-currency Support**: Only USD pricing included in initial version. International currency support deferred to future iteration.
- **Tax Calculation**: Basic tax handling via Stripe Tax is assumed. Complex tax rules (VAT, GST by jurisdiction) are out of scope for initial version.
- **Usage-Based Billing**: Metered billing (pay per volunteer per month) is not included. Only tier-based pricing with hard limits.
- **Reseller/Partner Pricing**: No support for partner discounts, reseller pricing, or referral credits in initial version.
- **Purchase Orders**: B2B purchase order workflow not included. Only credit card payments via Stripe.
- **Dunning Management**: Advanced dunning campaigns (personalized recovery emails, special offers for churning customers) not included beyond basic retry logic.
- **Revenue Recognition**: Accounting-grade revenue recognition and deferred revenue tracking not included. Financial reporting uses Stripe's built-in reporting.
- **Refund Processing**: Customer-initiated refunds not included in self-service portal. Handled via support with manual Stripe refund.
- **Billing Disputes**: Chargeback handling and payment dispute workflows not included in initial version.
- **Contract Management**: No support for custom contracts, non-standard payment terms, or net-30 invoicing.

