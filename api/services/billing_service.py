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
from sqlalchemy.orm import Session
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
            # Get organization and subscription
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
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

    def _get_plan_amount(self, price_id: str) -> int:
        """
        Get plan amount in cents from price ID.

        Args:
            price_id: Stripe price ID

        Returns:
            int: Amount in cents
        """
        # Price mapping (in cents)
        price_map = {
            "starter_monthly": 2900,   # $29/month
            "starter_annual": 29000,   # $290/year
            "pro_monthly": 9900,       # $99/month
            "pro_annual": 99000,       # $990/year
            "enterprise": 0            # Contact sales
        }

        price_lower = price_id.lower()

        for key, amount in price_map.items():
            if key in price_lower:
                return amount

        logger.warning(f"Unknown price ID: {price_id}, defaulting to $29")
        return 2900  # Default to starter monthly

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
