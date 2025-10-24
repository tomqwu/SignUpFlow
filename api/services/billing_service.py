"""Billing service for subscription and payment management.

This service coordinates billing operations between the database and Stripe API.
It handles subscription lifecycle, usage tracking, and billing history.

Example Usage:
    from api.services.billing_service import BillingService

    billing = BillingService(db)
    subscription = billing.get_subscription(org_id="org_123")
    usage = billing.get_usage_metrics(org_id="org_123")
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from api.models import (
    Organization,
    Subscription,
    BillingHistory,
    PaymentMethod,
    UsageMetrics,
    SubscriptionEvent
)
from api.utils.stripe_client import StripeClient
from api.logging_config import logger


class BillingService:
    """Service for managing billing and subscriptions."""

    def __init__(self, db: Session):
        """
        Initialize billing service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.stripe_client = StripeClient()

    def get_subscription(self, org_id: str) -> Optional[Subscription]:
        """
        Get organization's current subscription.

        Args:
            org_id: Organization ID

        Returns:
            Subscription: Active subscription
            None: If no subscription exists

        Example:
            subscription = billing.get_subscription("org_123")
            print(f"Plan: {subscription.plan_tier}")
            print(f"Status: {subscription.status}")
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if subscription:
                logger.info(f"Retrieved subscription for org {org_id}: {subscription.plan_tier}")
            else:
                logger.info(f"No subscription found for org {org_id}")

            return subscription

        except Exception as e:
            logger.error(f"Error retrieving subscription for org {org_id}: {e}")
            return None

    def create_free_subscription(self, org_id: str) -> Optional[Subscription]:
        """
        Create a Free tier subscription for a new organization.

        This is called automatically when an organization is created.
        Free tier has no Stripe customer or subscription ID.

        Args:
            org_id: Organization ID

        Returns:
            Subscription: Created free subscription
            None: If creation fails

        Example:
            subscription = billing.create_free_subscription("org_123")
            # subscription.plan_tier == "free"
            # subscription.status == "active"
        """
        try:
            # Check if subscription already exists
            existing = self.get_subscription(org_id)
            if existing:
                logger.warning(f"Subscription already exists for org {org_id}")
                return existing

            # Create free subscription
            subscription = Subscription(
                org_id=org_id,
                plan_tier="free",
                status="active",
                billing_cycle=None,  # No billing for free tier
                stripe_customer_id=None,
                stripe_subscription_id=None
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Created free subscription for org {org_id}")

            # Record subscription event
            self._record_subscription_event(
                org_id=org_id,
                event_type="created",
                new_plan="free",
                notes="Organization created with free tier"
            )

            return subscription

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating free subscription for org {org_id}: {e}")
            return None

    def get_usage_metrics(self, org_id: str) -> List[UsageMetrics]:
        """
        Get all usage metrics for an organization.

        Args:
            org_id: Organization ID

        Returns:
            list: List of UsageMetrics objects

        Example:
            metrics = billing.get_usage_metrics("org_123")
            for metric in metrics:
                print(f"{metric.metric_type}: {metric.current_value}/{metric.plan_limit}")
        """
        try:
            metrics = self.db.query(UsageMetrics).filter(
                UsageMetrics.org_id == org_id
            ).all()

            logger.info(f"Retrieved {len(metrics)} usage metrics for org {org_id}")
            return metrics

        except Exception as e:
            logger.error(f"Error retrieving usage metrics for org {org_id}: {e}")
            return []

    def update_volunteer_count(self, org_id: str) -> Optional[UsageMetrics]:
        """
        Update the volunteer count usage metric.

        This is called whenever volunteers are added or removed.

        Args:
            org_id: Organization ID

        Returns:
            UsageMetrics: Updated volunteer count metric
            None: If update fails

        Example:
            metric = billing.update_volunteer_count("org_123")
            print(f"Volunteers: {metric.current_value}/{metric.plan_limit}")
        """
        try:
            # Get organization and subscription (with eager loading)
            org = self.db.query(Organization).options(
                joinedload(Organization.subscription)
            ).filter(Organization.id == org_id).first()
            if not org:
                logger.error(f"Organization {org_id} not found")
                return None

            subscription = self.get_subscription(org_id)
            if not subscription:
                logger.error(f"No subscription found for org {org_id}")
                return None

            # Count current volunteers
            volunteer_count = len([
                p for p in org.people
                if "volunteer" in (p.roles or [])
            ])

            # Get plan limit
            tier_limits = {
                "free": 10,
                "starter": 50,
                "pro": 200,
                "enterprise": None  # Unlimited
            }
            plan_limit = tier_limits.get(subscription.plan_tier, 10)

            # Calculate percentage used
            if plan_limit is None:
                percentage_used = 0.0  # Unlimited
            else:
                percentage_used = (volunteer_count / plan_limit * 100) if plan_limit > 0 else 0.0

            # Update or create metric
            metric = self.db.query(UsageMetrics).filter(
                UsageMetrics.org_id == org_id,
                UsageMetrics.metric_type == "volunteers_count"
            ).first()

            if metric:
                metric.current_value = volunteer_count
                metric.plan_limit = plan_limit
                metric.percentage_used = percentage_used
                metric.last_updated = datetime.utcnow()
            else:
                metric = UsageMetrics(
                    org_id=org_id,
                    metric_type="volunteers_count",
                    current_value=volunteer_count,
                    plan_limit=plan_limit,
                    percentage_used=percentage_used
                )
                self.db.add(metric)

            self.db.commit()
            self.db.refresh(metric)

            logger.info(
                f"Updated volunteer count for org {org_id}: "
                f"{volunteer_count}/{plan_limit} ({percentage_used:.1f}%)"
            )

            return metric

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating volunteer count for org {org_id}: {e}")
            return None

    def is_over_limit(self, org_id: str, metric_type: str = "volunteers_count") -> bool:
        """
        Check if organization is over its plan limit.

        Args:
            org_id: Organization ID
            metric_type: Type of metric to check (default: "volunteers_count")

        Returns:
            bool: True if over limit, False otherwise

        Example:
            if billing.is_over_limit("org_123"):
                raise HTTPException(
                    status_code=403,
                    detail="Volunteer limit exceeded. Please upgrade your plan."
                )
        """
        try:
            metric = self.db.query(UsageMetrics).filter(
                UsageMetrics.org_id == org_id,
                UsageMetrics.metric_type == metric_type
            ).first()

            if not metric:
                return False

            if metric.plan_limit is None:  # Unlimited
                return False

            return metric.current_value > metric.plan_limit

        except Exception as e:
            logger.error(f"Error checking limit for org {org_id}: {e}")
            return False

    def get_billing_history(
        self,
        org_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[BillingHistory]:
        """
        Get billing history for an organization.

        Args:
            org_id: Organization ID
            limit: Maximum number of records to return (default: 50)
            offset: Number of records to skip (default: 0)

        Returns:
            list: List of BillingHistory objects, newest first

        Example:
            history = billing.get_billing_history("org_123", limit=10)
            for record in history:
                print(f"{record.event_type}: ${record.amount_cents/100}")
        """
        try:
            history = self.db.query(BillingHistory).filter(
                BillingHistory.org_id == org_id
            ).order_by(
                BillingHistory.event_timestamp.desc()
            ).limit(limit).offset(offset).all()

            logger.info(f"Retrieved {len(history)} billing history records for org {org_id}")
            return history

        except Exception as e:
            logger.error(f"Error retrieving billing history for org {org_id}: {e}")
            return []

    def upgrade_subscription(
        self,
        org_id: str,
        price_id: str,
        trial_days: Optional[int] = 14,
        admin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upgrade organization subscription to paid plan.

        This coordinates the entire upgrade process:
        1. Creates Stripe subscription via StripeService
        2. Records billing history
        3. Records subscription event for audit trail
        4. Updates usage metrics with new limits
        5. Sends confirmation email (future)

        Args:
            org_id: Organization ID
            price_id: Stripe price ID
            trial_days: Number of trial days (default: 14)
            admin_id: Admin who initiated upgrade (optional)

        Returns:
            dict: Result with success status and details
                {
                    "success": bool,
                    "subscription": Subscription object,
                    "message": str
                }

        Example:
            billing = BillingService(db)
            result = billing.upgrade_subscription(
                org_id="org_123",
                price_id="price_starter_monthly",
                trial_days=14,
                admin_id="person_admin_123"
            )
            if result["success"]:
                print(f"Upgraded to {result['subscription'].plan_tier}")
        """
        try:
            # Get current subscription
            current_subscription = self.get_subscription(org_id)
            if not current_subscription:
                return {"success": False, "message": "No subscription found"}

            previous_plan = current_subscription.plan_tier

            # Use StripeService to upgrade
            from api.services.stripe_service import StripeService
            stripe_service = StripeService(self.db)

            upgrade_result = stripe_service.upgrade_to_paid(
                org_id=org_id,
                price_id=price_id,
                trial_days=trial_days
            )

            if not upgrade_result["success"]:
                return upgrade_result

            subscription = upgrade_result["subscription"]
            new_plan = subscription.plan_tier

            # Record billing history (if not in trial)
            if subscription.status == "active":  # Not trialing
                self._record_billing_history(
                    org_id=org_id,
                    event_type="subscription_created",
                    amount_cents=self._get_plan_amount(price_id),
                    payment_status="succeeded",
                    description=f"Upgraded from {previous_plan} to {new_plan}",
                    stripe_invoice_id=None  # Will be updated by webhook
                )

            # Record subscription event for audit trail
            self._record_subscription_event(
                org_id=org_id,
                event_type="upgraded",
                new_plan=new_plan,
                previous_plan=previous_plan,
                admin_id=admin_id,
                notes=f"Upgraded from {previous_plan} to {new_plan} plan"
            )

            # Update usage metrics with new volunteer limit
            self.update_volunteer_count(org_id)

            logger.info(
                f"Successfully upgraded org {org_id} from {previous_plan} to {new_plan}"
            )

            # TODO: Send confirmation email with invoice details
            # This will be implemented when email service is ready

            return {
                "success": True,
                "subscription": subscription,
                "message": f"Successfully upgraded to {new_plan} plan"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error upgrading subscription for org {org_id}: {e}")
            return {
                "success": False,
                "message": f"Upgrade failed: {str(e)}"
            }

    def _record_billing_history(
        self,
        org_id: str,
        event_type: str,
        amount_cents: int,
        payment_status: str,
        description: Optional[str] = None,
        stripe_invoice_id: Optional[str] = None,
        invoice_pdf_url: Optional[str] = None
    ) -> Optional[BillingHistory]:
        """
        Record a billing event in history.

        Args:
            org_id: Organization ID
            event_type: Event type (charge, refund, etc.)
            amount_cents: Amount in cents
            payment_status: Payment status (succeeded, failed, pending)
            description: Event description (optional)
            stripe_invoice_id: Stripe invoice ID (optional)
            invoice_pdf_url: Invoice PDF URL (optional)

        Returns:
            BillingHistory: Created record
            None: If creation fails
        """
        try:
            history = BillingHistory(
                org_id=org_id,
                event_type=event_type,
                amount_cents=amount_cents,
                currency="usd",
                payment_status=payment_status,
                description=description,
                stripe_invoice_id=stripe_invoice_id,
                invoice_pdf_url=invoice_pdf_url
            )

            self.db.add(history)
            self.db.commit()
            self.db.refresh(history)

            logger.info(
                f"Recorded billing history for org {org_id}: "
                f"{event_type} ${amount_cents/100:.2f} ({payment_status})"
            )

            return history

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording billing history for org {org_id}: {e}")
            return None

    def start_trial(
        self,
        org_id: str,
        plan_tier: str,
        trial_days: int = 14,
        admin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a trial period for an organization.

        This upgrades the organization to a paid plan tier with trial status.
        Trial automatically expires after trial_days and requires payment method.

        Args:
            org_id: Organization ID
            plan_tier: Plan tier to trial (starter, pro, enterprise)
            trial_days: Number of trial days (default: 14)
            admin_id: Admin who initiated trial (optional)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Subscription object,
                    "message": str,
                    "trial_end_date": datetime
                }

        Example:
            billing = BillingService(db)
            result = billing.start_trial(
                org_id="org_123",
                plan_tier="pro",
                trial_days=14,
                admin_id="person_admin_123"
            )
        """
        try:
            # Get current subscription
            subscription = self.get_subscription(org_id)
            if not subscription:
                return {"success": False, "message": "No subscription found"}

            # Only allow trials from free tier
            if subscription.plan_tier != "free":
                return {
                    "success": False,
                    "message": f"Cannot start trial from {subscription.plan_tier} plan"
                }

            # Validate plan tier
            if plan_tier not in ["starter", "pro", "enterprise"]:
                return {
                    "success": False,
                    "message": "Invalid plan tier for trial"
                }

            previous_plan = subscription.plan_tier

            # Calculate trial end date
            trial_end = datetime.utcnow() + timedelta(days=trial_days)

            # Update subscription to trial status
            subscription.plan_tier = plan_tier
            subscription.status = "trialing"
            subscription.trial_end_date = trial_end
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = trial_end

            self.db.commit()
            self.db.refresh(subscription)

            # Record subscription event
            self._record_subscription_event(
                org_id=org_id,
                event_type="trial_started",
                new_plan=plan_tier,
                previous_plan=previous_plan,
                admin_id=admin_id,
                notes=f"Started {trial_days}-day trial of {plan_tier} plan"
            )

            # Update usage metrics to new plan limits
            self.update_volunteer_count(org_id)

            logger.info(
                f"Started {trial_days}-day trial for org {org_id}: "
                f"{previous_plan} → {plan_tier} (expires {trial_end})"
            )

            # TODO: Send trial started email
            # This will be implemented when email service is ready

            return {
                "success": True,
                "subscription": subscription,
                "trial_end_date": trial_end,
                "message": f"Started {trial_days}-day trial of {plan_tier} plan"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting trial for org {org_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to start trial: {str(e)}"
            }

    def auto_downgrade_expired_trials(self) -> Dict[str, Any]:
        """
        Automatically downgrade subscriptions with expired trials.

        This should be called daily via Celery scheduled task.
        Downgrades all subscriptions where:
        - status is "trialing"
        - trial_end_date < now()
        - no payment method on file

        Returns:
            dict: Result with downgraded organization count
                {
                    "success": bool,
                    "downgraded_count": int,
                    "downgraded_orgs": list[str],
                    "message": str
                }

        Example:
            billing = BillingService(db)
            result = billing.auto_downgrade_expired_trials()
            # Called daily by Celery task
        """
        try:
            now = datetime.utcnow()

            # Find all expired trials
            expired_trials = self.db.query(Subscription).filter(
                Subscription.status == "trialing",
                Subscription.trial_end_date <= now
            ).all()

            downgraded_orgs = []

            for subscription in expired_trials:
                # Check if payment method on file
                payment_method = self.db.query(PaymentMethod).filter(
                    PaymentMethod.org_id == subscription.org_id,
                    PaymentMethod.is_primary == True,
                    PaymentMethod.is_active == True
                ).first()

                if payment_method:
                    # Has payment method - convert to paid subscription
                    # This will be handled by Stripe webhook when trial converts
                    logger.info(
                        f"Trial expired for org {subscription.org_id} but has payment method - "
                        f"will convert to paid"
                    )
                    continue

                # No payment method - downgrade to free
                previous_plan = subscription.plan_tier

                subscription.plan_tier = "free"
                subscription.status = "active"
                subscription.trial_end_date = None
                subscription.billing_cycle = None
                subscription.current_period_start = None
                subscription.current_period_end = None

                self.db.commit()
                self.db.refresh(subscription)

                # Record subscription event
                self._record_subscription_event(
                    org_id=subscription.org_id,
                    event_type="trial_expired",
                    new_plan="free",
                    previous_plan=previous_plan,
                    reason="Trial expired without payment method",
                    notes=f"Auto-downgraded from {previous_plan} trial to free plan"
                )

                # Update usage metrics to free plan limits
                self.update_volunteer_count(subscription.org_id)

                downgraded_orgs.append(subscription.org_id)

                logger.info(
                    f"Auto-downgraded org {subscription.org_id} from {previous_plan} trial to free"
                )

                # TODO: Send trial expired email
                # This will be implemented when email service is ready

            return {
                "success": True,
                "downgraded_count": len(downgraded_orgs),
                "downgraded_orgs": downgraded_orgs,
                "message": f"Downgraded {len(downgraded_orgs)} expired trials to free plan"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error auto-downgrading expired trials: {e}")
            return {
                "success": False,
                "downgraded_count": 0,
                "message": f"Failed to downgrade expired trials: {str(e)}"
            }

    def _get_plan_amount(self, price_id: str) -> int:
        """
        Get plan amount in cents from price ID.

        Args:
            price_id: Stripe price ID

        Returns:
            int: Amount in cents
        """
        # Price mapping (in cents)
        # Annual pricing: 20% off annual total (equivalent to 2 months free)
        price_map = {
            "starter_monthly": 2900,    # $29/month
            "starter_annual": 27840,    # $278.40/year (20% off $348 = save $69.60)
            "pro_monthly": 9900,        # $99/month
            "pro_annual": 95040,        # $950.40/year (20% off $1188 = save $237.60)
            "enterprise": 0             # Contact sales
        }

        price_lower = price_id.lower()

        for key, amount in price_map.items():
            if key in price_lower:
                return amount

        logger.warning(f"Unknown price ID: {price_id}, defaulting to $29")
        return 2900  # Default to starter monthly

    def calculate_annual_price(self, monthly_price_cents: int) -> int:
        """
        Calculate annual subscription price with 20% discount.

        Formula: monthly_price * 12 * 0.8
        Discount: 20% off (equivalent to 2 months free)

        Args:
            monthly_price_cents: Monthly price in cents

        Returns:
            int: Annual price in cents with 20% discount applied

        Example:
            >>> calculate_annual_price(2900)  # $29/month
            27840  # $278.40/year (20% off $348)

            >>> calculate_annual_price(9900)  # $99/month
            95040  # $950.40/year (20% off $1188)
        """
        annual_full_price = monthly_price_cents * 12
        annual_discounted_price = int(annual_full_price * 0.8)
        return annual_discounted_price

    def get_annual_savings(self, monthly_price_cents: int) -> int:
        """
        Calculate savings from annual billing vs monthly.

        Args:
            monthly_price_cents: Monthly price in cents

        Returns:
            int: Savings amount in cents (20% of annual price)

        Example:
            >>> get_annual_savings(2900)  # $29/month
            6960  # $69.60 savings (20% of $348)
        """
        annual_full_price = monthly_price_cents * 12
        annual_discounted_price = self.calculate_annual_price(monthly_price_cents)
        savings = annual_full_price - annual_discounted_price
        return savings

    def switch_billing_cycle(
        self,
        org_id: str,
        new_billing_cycle: str,
        admin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Switch subscription billing cycle between monthly and annual.

        This handles prorated charge/credit calculations:
        - Monthly → Annual: Charge prorated amount for remaining period
        - Annual → Monthly: Credit prorated amount for unused period

        Args:
            org_id: Organization ID
            new_billing_cycle: New billing cycle ("monthly" or "annual")
            admin_id: Admin who initiated switch (optional)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Subscription object,
                    "message": str,
                    "prorated_amount_cents": int  # Charge (positive) or credit (negative)
                }

        Example:
            billing = BillingService(db)
            result = billing.switch_billing_cycle(
                org_id="org_123",
                new_billing_cycle="annual",
                admin_id="person_admin_123"
            )
        """
        try:
            # Validate billing cycle
            if new_billing_cycle not in ["monthly", "annual"]:
                return {
                    "success": False,
                    "message": "Invalid billing cycle. Must be 'monthly' or 'annual'"
                }

            # Get current subscription
            subscription = self.get_subscription(org_id)
            if not subscription:
                return {"success": False, "message": "No subscription found"}

            # Only allow switching for active paid subscriptions
            if subscription.plan_tier == "free":
                return {
                    "success": False,
                    "message": "Cannot switch billing cycle for free plan"
                }

            if subscription.status != "active":
                return {
                    "success": False,
                    "message": f"Cannot switch billing cycle for {subscription.status} subscription"
                }

            current_cycle = subscription.billing_cycle
            if current_cycle == new_billing_cycle:
                return {
                    "success": False,
                    "message": f"Subscription is already on {new_billing_cycle} billing cycle"
                }

            # Calculate prorated amount
            prorated_amount = self._calculate_prorated_amount(
                subscription=subscription,
                new_billing_cycle=new_billing_cycle
            )

            # Get new price ID
            plan_tier = subscription.plan_tier
            new_price_id = f"{plan_tier}_{new_billing_cycle}"

            # Update subscription in Stripe
            from api.services.stripe_service import StripeService
            stripe_service = StripeService(self.db)

            if subscription.stripe_subscription_id:
                # Call Stripe to update billing cycle
                stripe_result = stripe_service.update_subscription_billing_cycle(
                    stripe_subscription_id=subscription.stripe_subscription_id,
                    new_price_id=new_price_id,
                    prorated_amount_cents=prorated_amount
                )

                if not stripe_result["success"]:
                    return stripe_result

            # Update local subscription
            previous_cycle = subscription.billing_cycle
            subscription.billing_cycle = new_billing_cycle

            self.db.commit()
            self.db.refresh(subscription)

            # Record billing history
            self._record_billing_history(
                org_id=org_id,
                event_type="billing_cycle_changed",
                amount_cents=abs(prorated_amount),
                payment_status="succeeded" if prorated_amount > 0 else "credited",
                description=f"Switched from {previous_cycle} to {new_billing_cycle} billing",
                stripe_invoice_id=None  # Will be updated by webhook
            )

            # Record subscription event
            self._record_subscription_event(
                org_id=org_id,
                event_type="billing_cycle_changed",
                new_plan=subscription.plan_tier,
                previous_plan=subscription.plan_tier,
                admin_id=admin_id,
                notes=f"Switched from {previous_cycle} to {new_billing_cycle} billing"
            )

            logger.info(
                f"Switched billing cycle for org {org_id}: {previous_cycle} → {new_billing_cycle} "
                f"(prorated: ${abs(prorated_amount)/100:.2f})"
            )

            return {
                "success": True,
                "subscription": subscription,
                "prorated_amount_cents": prorated_amount,
                "message": f"Successfully switched to {new_billing_cycle} billing"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error switching billing cycle for org {org_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to switch billing cycle: {str(e)}"
            }

    def _calculate_prorated_amount(
        self,
        subscription: Subscription,
        new_billing_cycle: str
    ) -> int:
        """
        Calculate prorated amount for billing cycle switch.

        Args:
            subscription: Current subscription
            new_billing_cycle: New billing cycle ("monthly" or "annual")

        Returns:
            int: Prorated amount in cents
                - Positive: Charge (monthly → annual)
                - Negative: Credit (annual → monthly)
        """
        now = datetime.utcnow()
        current_cycle = subscription.billing_cycle
        plan_tier = subscription.plan_tier

        # Get pricing
        monthly_price = self._get_plan_amount(f"{plan_tier}_monthly")
        annual_price = self._get_plan_amount(f"{plan_tier}_annual")

        # Calculate days remaining in current period
        if subscription.current_period_end:
            total_period_days = (subscription.current_period_end - subscription.current_period_start).days
            remaining_days = (subscription.current_period_end - now).days
            if remaining_days < 0:
                remaining_days = 0
        else:
            total_period_days = 30 if current_cycle == "monthly" else 365
            remaining_days = total_period_days

        # Calculate prorated amount
        if current_cycle == "monthly" and new_billing_cycle == "annual":
            # Monthly → Annual: Charge difference for remaining period
            # Credit unused monthly, charge annual prorated
            unused_monthly = int(monthly_price * (remaining_days / 30))
            annual_prorated = int(annual_price * (remaining_days / 365))
            prorated_amount = annual_prorated - unused_monthly

        elif current_cycle == "annual" and new_billing_cycle == "monthly":
            # Annual → Monthly: Credit unused annual
            unused_annual = int(annual_price * (remaining_days / 365))
            prorated_amount = -unused_annual  # Negative = credit

        else:
            prorated_amount = 0

        logger.info(
            f"Calculated prorated amount for {current_cycle} → {new_billing_cycle}: "
            f"${prorated_amount/100:.2f} ({remaining_days} days remaining)"
        )

        return prorated_amount

    def downgrade_subscription(
        self,
        org_id: str,
        new_plan_tier: str,
        reason: Optional[str] = None,
        admin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule subscription downgrade to execute at period end.

        Downgrades are scheduled rather than immediate to avoid service disruption.
        Credit for unused time is calculated and applied at downgrade execution.

        Args:
            org_id: Organization ID
            new_plan_tier: New plan tier (must be lower than current)
            reason: Reason for downgrade (optional)
            admin_id: Admin who initiated downgrade (optional)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Subscription object,
                    "message": str,
                    "effective_date": str,  # ISO format
                    "credit_amount_cents": int
                }

        Example:
            result = billing_service.downgrade_subscription(
                org_id="org_123",
                new_plan_tier="starter",
                reason="Reducing team size",
                admin_id="person_admin_123"
            )
        """
        try:
            # Get current subscription
            subscription = self.get_subscription(org_id)
            if not subscription:
                return {"success": False, "message": "No subscription found"}

            current_plan = subscription.plan_tier

            # Validate downgrade is allowed
            tier_hierarchy = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
            current_tier_level = tier_hierarchy.get(current_plan, 0)
            new_tier_level = tier_hierarchy.get(new_plan_tier, 0)

            if new_tier_level >= current_tier_level:
                return {
                    "success": False,
                    "message": f"Cannot downgrade from {current_plan} to {new_plan_tier}. Use upgrade instead."
                }

            # Only allow downgrades for active paid subscriptions
            if current_plan == "free":
                return {
                    "success": False,
                    "message": "Cannot downgrade free plan"
                }

            if subscription.status != "active":
                return {
                    "success": False,
                    "message": f"Cannot downgrade {subscription.status} subscription"
                }

            # Calculate effective date (end of current period)
            effective_date = subscription.current_period_end or datetime.utcnow()

            # Calculate credit for unused time
            credit_amount = self._calculate_downgrade_credit(
                subscription=subscription,
                new_plan_tier=new_plan_tier
            )

            # Store pending downgrade
            subscription.pending_downgrade = {
                "new_plan_tier": new_plan_tier,
                "effective_date": effective_date.isoformat(),
                "credit_amount_cents": credit_amount,
                "reason": reason,
                "scheduled_at": datetime.utcnow().isoformat()
            }

            self.db.commit()
            self.db.refresh(subscription)

            # Record subscription event
            self._record_subscription_event(
                org_id=org_id,
                event_type="downgrade_scheduled",
                new_plan=new_plan_tier,
                previous_plan=current_plan,
                admin_id=admin_id,
                reason=reason,
                notes=f"Downgrade from {current_plan} to {new_plan_tier} scheduled for {effective_date.isoformat()}"
            )

            logger.info(
                f"Scheduled downgrade for org {org_id}: {current_plan} → {new_plan_tier} "
                f"(effective {effective_date}, credit ${credit_amount/100:.2f})"
            )

            return {
                "success": True,
                "subscription": subscription,
                "effective_date": effective_date.isoformat(),
                "credit_amount_cents": credit_amount,
                "message": f"Downgrade to {new_plan_tier} scheduled for {effective_date.strftime('%Y-%m-%d')}"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error scheduling downgrade for org {org_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to schedule downgrade: {str(e)}"
            }

    def _calculate_downgrade_credit(
        self,
        subscription: Subscription,
        new_plan_tier: str
    ) -> int:
        """
        Calculate credit for unused time when downgrading.

        Args:
            subscription: Current subscription
            new_plan_tier: New (lower) plan tier

        Returns:
            int: Credit amount in cents
        """
        now = datetime.utcnow()
        current_plan = subscription.plan_tier
        billing_cycle = subscription.billing_cycle

        # Get pricing
        current_price = self._get_plan_amount(f"{current_plan}_{billing_cycle}")
        new_price = self._get_plan_amount(f"{new_plan_tier}_{billing_cycle}")

        # Calculate days remaining in period
        if subscription.current_period_end:
            total_period_days = (subscription.current_period_end - subscription.current_period_start).days
            remaining_days = (subscription.current_period_end - now).days
            if remaining_days < 0:
                remaining_days = 0
        else:
            total_period_days = 30 if billing_cycle == "monthly" else 365
            remaining_days = 0

        # Calculate credit: (current_price - new_price) * (remaining_days / total_period_days)
        price_difference = current_price - new_price
        if total_period_days > 0:
            credit_amount = int(price_difference * (remaining_days / total_period_days))
        else:
            credit_amount = 0

        logger.info(
            f"Calculated downgrade credit: {current_plan} → {new_plan_tier}, "
            f"{remaining_days}/{total_period_days} days remaining, "
            f"credit ${credit_amount/100:.2f}"
        )

        return credit_amount

    def apply_pending_downgrades(self) -> Dict[str, Any]:
        """
        Apply all pending downgrades that have reached their effective date.

        This method:
        1. Finds all subscriptions with pending_downgrade not null
        2. Checks if effective_date <= now()
        3. Applies the downgrade to new plan tier
        4. Applies credit to Stripe customer balance
        5. Clears pending_downgrade field
        6. Records subscription event for audit trail

        Returns:
            dict: Summary of applied downgrades
            {
                "success": bool,
                "applied_count": int,
                "applied_downgrades": List[dict],
                "message": str
            }
        """
        try:
            now = datetime.utcnow()
            applied_downgrades = []

            # Find all subscriptions with pending downgrades
            subscriptions = self.db.query(Subscription).filter(
                Subscription.pending_downgrade.isnot(None)
            ).all()

            logger.info(f"Found {len(subscriptions)} subscriptions with pending downgrades")

            for subscription in subscriptions:
                try:
                    pending = subscription.pending_downgrade
                    effective_date_str = pending.get("effective_date")
                    new_plan_tier = pending.get("new_plan_tier")
                    credit_amount_cents = pending.get("credit_amount_cents", 0)
                    reason = pending.get("reason")

                    # Parse effective date
                    effective_date = datetime.fromisoformat(effective_date_str)

                    # Check if effective date has passed
                    if effective_date > now:
                        logger.info(
                            f"Skipping downgrade for org {subscription.org_id}: "
                            f"effective date {effective_date} is in the future"
                        )
                        continue

                    logger.info(
                        f"Applying downgrade for org {subscription.org_id}: "
                        f"{subscription.plan_tier} → {new_plan_tier}"
                    )

                    # Store previous plan for event recording
                    previous_plan = subscription.plan_tier

                    # Apply the downgrade
                    subscription.plan_tier = new_plan_tier

                    # Apply credit to Stripe customer balance (T080)
                    if credit_amount_cents > 0 and subscription.stripe_customer_id:
                        try:
                            from api.services.stripe_service import StripeService
                            stripe_service = StripeService(self.db)
                            stripe_service.apply_customer_credit(
                                customer_id=subscription.stripe_customer_id,
                                amount_cents=credit_amount_cents,
                                description=f"Credit for downgrade from {previous_plan} to {new_plan_tier}"
                            )
                            logger.info(
                                f"Applied ${credit_amount_cents/100:.2f} credit to "
                                f"Stripe customer {subscription.stripe_customer_id}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to apply Stripe credit for org {subscription.org_id}: {e}"
                            )
                            # Continue anyway - don't block downgrade

                    # Clear pending_downgrade field
                    subscription.pending_downgrade = None
                    subscription.updated_at = now

                    self.db.commit()
                    self.db.refresh(subscription)

                    # Record subscription event
                    self._record_subscription_event(
                        org_id=subscription.org_id,
                        event_type="downgrade_applied",
                        new_plan=new_plan_tier,
                        previous_plan=previous_plan,
                        reason=reason,
                        notes=f"Scheduled downgrade applied: {previous_plan} → {new_plan_tier}, credit ${credit_amount_cents/100:.2f}"
                    )

                    applied_downgrades.append({
                        "org_id": subscription.org_id,
                        "previous_plan": previous_plan,
                        "new_plan": new_plan_tier,
                        "credit_amount_cents": credit_amount_cents,
                        "effective_date": effective_date_str
                    })

                    logger.info(
                        f"Successfully applied downgrade for org {subscription.org_id}: "
                        f"{previous_plan} → {new_plan_tier}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error applying downgrade for subscription {subscription.id}: {e}",
                        exc_info=True
                    )
                    self.db.rollback()
                    # Continue with next subscription

            return {
                "success": True,
                "applied_count": len(applied_downgrades),
                "applied_downgrades": applied_downgrades,
                "message": f"Applied {len(applied_downgrades)} pending downgrades"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in apply_pending_downgrades: {e}", exc_info=True)
            return {
                "success": False,
                "applied_count": 0,
                "applied_downgrades": [],
                "message": f"Failed to apply pending downgrades: {str(e)}"
            }

    def cancel_subscription(
        self,
        org_id: str,
        reason: Optional[str] = None,
        feedback: Optional[str] = None,
        admin_id: Optional[str] = None,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel organization's subscription.

        Service continues until period end if at_period_end=True.
        Organization downgraded to Free plan at period end.
        Data retained for 30 days after cancellation.

        Args:
            org_id: Organization ID
            reason: Cancellation reason (optional)
            feedback: User feedback (optional)
            admin_id: Admin who initiated cancellation
            at_period_end: Cancel at period end (True) or immediately (False)

        Returns:
            dict: Result with success status and subscription details
            {
                "success": bool,
                "subscription": Subscription object,
                "period_end": datetime,
                "data_retention_until": datetime,
                "message": str
            }

        Example:
            result = billing.cancel_subscription(
                org_id="org_123",
                reason="Cost reduction",
                feedback="Great service, just downsizing",
                admin_id="admin_456"
            )
        """
        try:
            # Get current subscription
            subscription = self.get_subscription(org_id)

            if not subscription:
                return {
                    "success": False,
                    "message": "No subscription found for organization"
                }

            # Validate subscription is paid (not free)
            if subscription.plan_tier == "free":
                return {
                    "success": False,
                    "message": "Cannot cancel free plan subscription"
                }

            # Cancel via StripeService
            from api.services.stripe_service import StripeService
            stripe_service = StripeService(self.db)

            result = stripe_service.cancel_subscription(
                org_id=org_id,
                at_period_end=at_period_end
            )

            if not result["success"]:
                return result

            # Refresh subscription after StripeService update
            self.db.refresh(subscription)

            # Calculate data retention period (30 days after period end)
            period_end = subscription.current_period_end
            data_retention_until = period_end + timedelta(days=30) if period_end else None

            # Record cancellation event
            notes_text = f"Subscription cancelled"
            if at_period_end:
                notes_text += f" (service continues until {period_end.isoformat() if period_end else 'N/A'})"
            else:
                notes_text += " (immediate cancellation)"

            if feedback:
                notes_text += f"\nFeedback: {feedback}"

            self._record_subscription_event(
                org_id=org_id,
                event_type="cancelled",
                new_plan=subscription.plan_tier,  # Will downgrade to free at period end
                previous_plan=subscription.plan_tier,
                admin_id=admin_id,
                reason=reason,
                notes=notes_text
            )

            logger.info(
                f"Cancelled subscription for org {org_id}: "
                f"plan={subscription.plan_tier}, at_period_end={at_period_end}, "
                f"period_end={period_end}"
            )

            return {
                "success": True,
                "subscription": subscription,
                "period_end": period_end,
                "data_retention_until": data_retention_until,
                "message": result["message"]
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling subscription for org {org_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to cancel subscription: {str(e)}"
            }

    def reactivate_subscription(
        self,
        org_id: str,
        admin_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reactivate a cancelled subscription within data retention period.

        Organization must be within 30-day data retention window.
        Subscription will be restored to previous plan tier.

        Args:
            org_id: Organization ID
            admin_id: Admin who initiated reactivation

        Returns:
            dict: Result with success status and subscription details
            {
                "success": bool,
                "subscription": Subscription object,
                "message": str
            }

        Example:
            result = billing.reactivate_subscription(
                org_id="org_123",
                admin_id="admin_456"
            )
        """
        try:
            # Get organization and subscription (with eager loading)
            org = self.db.query(Organization).options(
                joinedload(Organization.subscription)
            ).filter(Organization.id == org_id).first()

            if not org:
                return {
                    "success": False,
                    "message": "Organization not found"
                }

            subscription = self.get_subscription(org_id)

            if not subscription:
                return {
                    "success": False,
                    "message": "No subscription found for organization"
                }

            # Check if organization is in data retention period
            if not org.data_retention_until:
                return {
                    "success": False,
                    "message": "Subscription was not cancelled or retention period has expired"
                }

            now = datetime.utcnow()

            if now > org.data_retention_until:
                return {
                    "success": False,
                    "message": f"Data retention period expired on {org.data_retention_until.isoformat()}. Cannot reactivate subscription."
                }

            # Check current status
            if subscription.status not in ["cancelled", "canceled"]:
                return {
                    "success": False,
                    "message": f"Subscription status is {subscription.status}, not cancelled. Cannot reactivate."
                }

            # Get previous plan from subscription events
            from api.models import SubscriptionEvent

            last_event = self.db.query(SubscriptionEvent).filter(
                SubscriptionEvent.org_id == org_id,
                SubscriptionEvent.event_type.in_(["cancelled", "cancelled_completed"])
            ).order_by(SubscriptionEvent.event_timestamp.desc()).first()

            previous_plan = last_event.previous_plan if last_event and last_event.previous_plan else "starter"

            # Restore subscription
            subscription.plan_tier = previous_plan
            subscription.status = "active"
            subscription.cancel_at_period_end = False
            subscription.updated_at = now

            # Clear organization cancellation fields
            org.cancelled_at = None
            org.data_retention_until = None

            self.db.commit()
            self.db.refresh(subscription)
            self.db.refresh(org)

            # Record reactivation event
            self._record_subscription_event(
                org_id=org_id,
                event_type="reactivated",
                new_plan=previous_plan,
                previous_plan="free",
                admin_id=admin_id,
                notes=f"Subscription reactivated within data retention period. Restored to {previous_plan} plan."
            )

            logger.info(
                f"Reactivated subscription for org {org_id}: "
                f"restored to {previous_plan} plan"
            )

            return {
                "success": True,
                "subscription": subscription,
                "message": f"Subscription reactivated successfully. Restored to {previous_plan} plan."
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reactivating subscription for org {org_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to reactivate subscription: {str(e)}"
            }

    def _record_subscription_event(
        self,
        org_id: str,
        event_type: str,
        new_plan: str,
        previous_plan: Optional[str] = None,
        admin_id: Optional[str] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[SubscriptionEvent]:
        """
        Record a subscription change event for audit trail.

        Args:
            org_id: Organization ID
            event_type: Type of event (created, upgraded, downgraded, etc.)
            new_plan: New plan tier
            previous_plan: Previous plan tier (optional)
            admin_id: Admin who initiated change (optional)
            reason: Reason for change (optional)
            notes: Additional notes (optional)

        Returns:
            SubscriptionEvent: Created event record
            None: If creation fails
        """
        try:
            event = SubscriptionEvent(
                org_id=org_id,
                event_type=event_type,
                new_plan=new_plan,
                previous_plan=previous_plan,
                admin_id=admin_id,
                reason=reason,
                notes=notes
            )

            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)

            logger.info(
                f"Recorded subscription event for org {org_id}: "
                f"{event_type} from {previous_plan} to {new_plan}"
            )

            return event

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording subscription event for org {org_id}: {e}")
            return None
