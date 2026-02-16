"""Usage tracking and limit enforcement service.

This service tracks organization resource consumption and enforces
subscription plan limits for volunteers, events, storage, and API calls.

Example Usage:
    from api.services.usage_service import UsageService

    usage_service = UsageService(db)

    # Check if org can add another volunteer
    if usage_service.can_add_volunteer("org_123"):
        # Add volunteer...
        usage_service.track_volunteer_added("org_123")
    else:
        raise Exception("Volunteer limit reached")
"""

import os
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, UTC

from api.models import Organization, Subscription, UsageMetrics, Person
from api.logging_config import logger


class UsageService:
    """Service for tracking usage and enforcing limits."""

    # Plan limits configuration
    PLAN_LIMITS = {
        "free": {
            "volunteers": 10,
            "events_per_month": 50,
            "storage_mb": 100,
            "api_calls_per_day": 1000
        },
        "starter": {
            "volunteers": 50,
            "events_per_month": 200,
            "storage_mb": 1000,
            "api_calls_per_day": 10000
        },
        "pro": {
            "volunteers": 200,
            "events_per_month": 1000,
            "storage_mb": 10000,
            "api_calls_per_day": 50000
        },
        "enterprise": {
            "volunteers": None,  # Unlimited
            "events_per_month": None,  # Unlimited
            "storage_mb": None,  # Unlimited
            "api_calls_per_day": None  # Unlimited
        }
    }

    def __init__(self, db: Session):
        """
        Initialize usage service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_plan_limits(self, plan_tier: str) -> Dict[str, Optional[int]]:
        """
        Get limits for a specific plan tier.

        Args:
            plan_tier: Plan tier (free, starter, pro, enterprise)

        Returns:
            dict: Limits for the plan
                {
                    "volunteers": int or None (unlimited),
                    "events_per_month": int or None,
                    "storage_mb": int or None,
                    "api_calls_per_day": int or None
                }
        """
        return self.PLAN_LIMITS.get(plan_tier, self.PLAN_LIMITS["free"])

    def can_add_volunteer(self, org_id: str) -> bool:
        """
        Check if organization can add another volunteer.

        Args:
            org_id: Organization ID

        Returns:
            bool: True if can add, False if at limit

        Example:
            if not usage_service.can_add_volunteer("org_123"):
                raise HTTPException(
                    status_code=403,
                    detail="Volunteer limit reached. Please upgrade your plan."
                )
        """
        try:
            if os.getenv("DISABLE_USAGE_LIMITS", "").lower() == "true" or os.getenv("TESTING", "").lower() == "true":
                return True
            # Get organization and subscription (with eager loading)
            org = self.db.query(Organization).options(
                joinedload(Organization.subscription)
            ).filter(Organization.id == org_id).first()
            if not org:
                return False

            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription:
                return False

            # Get plan limit
            limits = self.get_plan_limits(subscription.plan_tier)
            volunteer_limit = limits["volunteers"]

            if volunteer_limit is None:  # Unlimited
                return True

            # Count current volunteers
            current_volunteers = len([
                p for p in org.people
                if "volunteer" in (p.roles or [])
            ])

            return current_volunteers < volunteer_limit

        except Exception as e:
            logger.error(f"Error checking volunteer limit for org {org_id}: {e}")
            return False

    def track_volunteer_added(self, org_id: str) -> Optional[UsageMetrics]:
        """
        Update volunteer count metric when a volunteer is added.

        Args:
            org_id: Organization ID

        Returns:
            UsageMetrics: Updated metrics
            None: If update fails

        Example:
            # After adding volunteer to database
            usage_service.track_volunteer_added("org_123")
        """
        return self._update_volunteer_count(org_id)

    def track_volunteer_removed(self, org_id: str) -> Optional[UsageMetrics]:
        """
        Update volunteer count metric when a volunteer is removed.

        Args:
            org_id: Organization ID

        Returns:
            UsageMetrics: Updated metrics
            None: If update fails

        Example:
            # After removing volunteer from database
            usage_service.track_volunteer_removed("org_123")
        """
        return self._update_volunteer_count(org_id)

    def get_usage_summary(self, org_id: str) -> Dict[str, Any]:
        """
        Get complete usage summary for organization.

        Args:
            org_id: Organization ID

        Returns:
            dict: Usage summary
                {
                    "plan_tier": str,
                    "limits": {...},
                    "usage": {
                        "volunteers": {"current": int, "limit": int, "percentage": float},
                        "events": {...},
                        "storage": {...},
                        "api_calls": {...}
                    },
                    "warnings": [str]  # List of approaching limits
                }

        Example:
            summary = usage_service.get_usage_summary("org_123")
            print(f"Volunteers: {summary['usage']['volunteers']['current']}/{summary['usage']['volunteers']['limit']}")
        """
        try:
            # Get subscription
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription:
                return {"error": "No subscription found"}

            # Get plan limits
            limits = self.get_plan_limits(subscription.plan_tier)

            # Get all usage metrics
            metrics = self.db.query(UsageMetrics).filter(
                UsageMetrics.org_id == org_id
            ).all()

            # Build usage summary
            usage = {}
            warnings = []

            for metric in metrics:
                metric_data = {
                    "current": metric.current_value,
                    "limit": metric.plan_limit,
                    "percentage": metric.percentage_used
                }
                usage[metric.metric_type] = metric_data

                # Add warning if approaching limit (>80%)
                if metric.plan_limit and metric.percentage_used > 80:
                    warnings.append(
                        f"{metric.metric_type}: {metric.current_value}/{metric.plan_limit} "
                        f"({metric.percentage_used:.0f}% used)"
                    )

            return {
                "plan_tier": subscription.plan_tier,
                "limits": limits,
                "usage": usage,
                "warnings": warnings
            }

        except Exception as e:
            logger.error(f"Error getting usage summary for org {org_id}: {e}")
            return {"error": str(e)}

    def enforce_volunteer_limit(self, org_id: str) -> Dict[str, Any]:
        """
        Check volunteer limit and return enforcement result.

        Args:
            org_id: Organization ID

        Returns:
            dict: Enforcement result
                {
                    "allowed": bool,
                    "current": int,
                    "limit": int,
                    "message": str
                }

        Example:
            result = usage_service.enforce_volunteer_limit("org_123")
            if not result["allowed"]:
                raise HTTPException(403, detail=result["message"])
        """
        try:
            if self.can_add_volunteer(org_id):
                metric = self.db.query(UsageMetrics).filter(
                    UsageMetrics.org_id == org_id,
                    UsageMetrics.metric_type == "volunteers_count"
                ).first()

                if metric:
                    return {
                        "allowed": True,
                        "current": metric.current_value,
                        "limit": metric.plan_limit,
                        "message": "Within volunteer limit"
                    }

            # Over limit
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            metric = self.db.query(UsageMetrics).filter(
                UsageMetrics.org_id == org_id,
                UsageMetrics.metric_type == "volunteers_count"
            ).first()

            if metric:
                return {
                    "allowed": False,
                    "current": metric.current_value,
                    "limit": metric.plan_limit,
                    "message": (
                        f"Volunteer limit reached ({metric.current_value}/{metric.plan_limit}). "
                        f"Upgrade to {self._get_next_tier(subscription.plan_tier)} plan for more volunteers."
                    )
                }

            return {
                "allowed": False,
                "message": "Unable to determine volunteer limit"
            }

        except Exception as e:
            logger.error(f"Error enforcing volunteer limit for org {org_id}: {e}")
            return {
                "allowed": False,
                "message": f"Error checking limit: {str(e)}"
            }

    def _update_volunteer_count(self, org_id: str) -> Optional[UsageMetrics]:
        """Update volunteer count metric (internal helper)."""
        try:
            # Get organization and subscription (with eager loading)
            org = self.db.query(Organization).options(
                joinedload(Organization.subscription)
            ).filter(Organization.id == org_id).first()
            if not org:
                return None

            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription:
                return None

            # Count current volunteers
            volunteer_count = len([
                p for p in org.people
                if "volunteer" in (p.roles or [])
            ])

            # Get plan limit
            limits = self.get_plan_limits(subscription.plan_tier)
            plan_limit = limits["volunteers"]

            # Calculate percentage
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
                metric.last_updated = datetime.now(UTC)
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

    def _get_next_tier(self, current_tier: str) -> str:
        """Get next higher plan tier."""
        tier_order = ["free", "starter", "pro", "enterprise"]
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
            return "enterprise"
        except ValueError:
            return "starter"
