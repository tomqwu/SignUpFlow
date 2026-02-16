"""
Celery tasks for billing and subscription management.

Background tasks for:
- Daily trial expiration checks
- Failed payment retries
- Invoice generation
- Usage limit warnings
- Subscription event notifications
"""

from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import logging

from api.database import SessionLocal
from api.services.billing_service import BillingService

logger = logging.getLogger(__name__)

# Use the same Celery app instance
from api.tasks.sms_tasks import celery_app


@celery_app.task(bind=True, max_retries=3)
def check_expired_trials(self) -> Dict[str, Any]:
    """
    Daily scheduled task to check and downgrade expired trials.

    This task:
    1. Finds all subscriptions with status="trialing" and trial_end_date < now()
    2. Checks if payment method on file
    3. If no payment method, downgrades to free plan
    4. If has payment method, allows Stripe to convert to paid
    5. Records subscription events for audit trail
    6. Sends trial expiration emails (future)

    Scheduled: Daily at 2:00 AM UTC

    Returns:
        dict: Summary of downgraded trials
        {
            "success": bool,
            "downgraded_count": int,
            "downgraded_orgs": List[str],
            "message": str
        }
    """
    logger.info("Starting daily trial expiration check...")
    db = SessionLocal()

    try:
        billing_service = BillingService(db)
        result = billing_service.auto_downgrade_expired_trials()

        logger.info(
            f"Trial expiration check complete: "
            f"{result['downgraded_count']} organizations downgraded"
        )

        if result['downgraded_orgs']:
            logger.info(f"Downgraded organizations: {result['downgraded_orgs']}")

        return result

    except Exception as e:
        logger.error(f"Error during trial expiration check: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def send_trial_expiration_warning(
    self,
    org_id: str,
    days_remaining: int
) -> Dict[str, Any]:
    """
    Send warning email when trial is expiring soon.

    Args:
        org_id: Organization ID
        days_remaining: Days until trial expires

    Returns:
        dict: Email sending result
    """
    logger.info(f"Sending trial expiration warning to org {org_id} ({days_remaining} days remaining)")
    db = SessionLocal()

    try:
        # TODO: Implement email sending when email service ready
        # For now, just log the warning
        logger.info(
            f"Trial expiration warning: org={org_id}, "
            f"days_remaining={days_remaining}"
        )

        return {
            "success": True,
            "org_id": org_id,
            "days_remaining": days_remaining,
            "message": "Trial expiration warning logged (email pending)"
        }

    except Exception as e:
        logger.error(f"Error sending trial expiration warning: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def check_usage_limits(self) -> Dict[str, Any]:
    """
    Daily task to check organizations approaching volunteer limits.

    Sends warning emails when:
    - 80% of limit reached
    - 90% of limit reached
    - 100% of limit reached (over limit)

    Scheduled: Daily at 3:00 AM UTC

    Returns:
        dict: Summary of organizations warned
    """
    logger.info("Starting daily usage limit check...")
    db = SessionLocal()

    try:
        from api.services.usage_service import UsageService
        from api.models import Organization

        usage_service = UsageService(db)
        warned_orgs = []

        # Get all organizations
        organizations = db.query(Organization).all()

        for org in organizations:
            usage = usage_service.get_usage_summary(org.id)
            percentage = usage["volunteer_usage"]["percentage_used"]

            # Check thresholds
            if percentage >= 100:
                logger.warning(f"Organization {org.id} is OVER volunteer limit")
                warned_orgs.append({
                    "org_id": org.id,
                    "percentage": percentage,
                    "status": "over_limit"
                })
                # TODO: Send over-limit email

            elif percentage >= 90:
                logger.info(f"Organization {org.id} at 90% volunteer limit")
                warned_orgs.append({
                    "org_id": org.id,
                    "percentage": percentage,
                    "status": "90_percent"
                })
                # TODO: Send 90% warning email

            elif percentage >= 80:
                logger.info(f"Organization {org.id} at 80% volunteer limit")
                warned_orgs.append({
                    "org_id": org.id,
                    "percentage": percentage,
                    "status": "80_percent"
                })
                # TODO: Send 80% warning email

        return {
            "success": True,
            "warned_count": len(warned_orgs),
            "warned_orgs": warned_orgs,
            "message": f"Checked usage limits for {len(organizations)} organizations"
        }

    except Exception as e:
        logger.error(f"Error during usage limit check: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def apply_pending_downgrades(self) -> Dict[str, Any]:
    """
    Daily task to apply scheduled downgrades at period end.

    This task:
    1. Finds all subscriptions with pending_downgrade
    2. Checks if effective_date <= now()
    3. Applies the downgrade to new plan tier
    4. Applies credit to Stripe customer balance
    5. Clears pending_downgrade field
    6. Records subscription event for audit trail
    7. Sends downgrade confirmation email (future)

    Scheduled: Daily at 1:00 AM UTC (before trial check at 2:00 AM)

    Returns:
        dict: Summary of applied downgrades
        {
            "success": bool,
            "applied_count": int,
            "applied_downgrades": List[dict],
            "message": str
        }
    """
    logger.info("Starting daily pending downgrades check...")
    db = SessionLocal()

    try:
        billing_service = BillingService(db)
        result = billing_service.apply_pending_downgrades()

        logger.info(
            f"Pending downgrades check complete: "
            f"{result['applied_count']} downgrades applied"
        )

        if result['applied_downgrades']:
            logger.info(f"Applied downgrades: {result['applied_downgrades']}")

        return result

    except Exception as e:
        logger.error(f"Error during pending downgrades check: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def process_cancelled_subscriptions(self) -> Dict[str, Any]:
    """
    Daily task to process cancelled subscriptions at period end.

    This task:
    1. Finds all subscriptions with cancel_at_period_end=True
    2. Checks if current_period_end <= now()
    3. Downgrades subscription to free tier
    4. Updates organization cancelled_at and data_retention_until (period_end + 30 days)
    5. Records subscription event for audit trail
    6. Sends cancellation confirmation email (future)

    Scheduled: Daily at 4:00 AM UTC (after usage checks)

    Returns:
        dict: Summary of processed cancellations
        {
            "success": bool,
            "cancelled_count": int,
            "cancelled_orgs": List[str],
            "message": str
        }
    """
    logger.info("Starting daily cancelled subscriptions check...")
    db = SessionLocal()

    try:
        from datetime import datetime, timedelta, UTC
        from api.models import Subscription, Organization, SubscriptionEvent

        now = datetime.now(UTC).replace(tzinfo=None)
        cancelled_orgs = []

        # Find all subscriptions marked for cancellation at period end
        subscriptions = db.query(Subscription).filter(
            Subscription.cancel_at_period_end == True,
            Subscription.current_period_end <= now
        ).all()

        logger.info(f"Found {len(subscriptions)} subscriptions to process")

        for subscription in subscriptions:
            try:
                org_id = subscription.org_id
                previous_plan = subscription.plan_tier

                # Downgrade to free tier
                subscription.plan_tier = "free"
                subscription.status = "cancelled"
                subscription.cancel_at_period_end = False
                subscription.stripe_subscription_id = None  # Clear Stripe reference
                subscription.stripe_customer_id = None  # Clear customer reference
                subscription.current_period_start = None
                subscription.current_period_end = None
                subscription.updated_at = now

                # Update organization cancellation and retention fields
                org = db.query(Organization).filter(Organization.id == org_id).first()
                if org:
                    org.cancelled_at = now
                    org.data_retention_until = now + timedelta(days=30)
                    logger.info(
                        f"Set data retention for org {org_id} until "
                        f"{org.data_retention_until.isoformat()}"
                    )

                db.commit()
                db.refresh(subscription)

                # Record subscription event
                event = SubscriptionEvent(
                    org_id=org_id,
                    event_type="cancelled_completed",
                    new_plan="free",
                    previous_plan=previous_plan,
                    notes=f"Subscription cancelled at period end. Data retained until {org.data_retention_until.isoformat() if org and org.data_retention_until else 'N/A'}"
                )
                db.add(event)
                db.commit()

                cancelled_orgs.append(org_id)
                logger.info(f"Processed cancellation for org {org_id}: {previous_plan} → free")

                # TODO: Send cancellation confirmation email

            except Exception as e:
                logger.error(f"Error processing cancellation for subscription {subscription.id}: {e}", exc_info=True)
                db.rollback()
                # Continue with next subscription

        return {
            "success": True,
            "cancelled_count": len(cancelled_orgs),
            "cancelled_orgs": cancelled_orgs,
            "message": f"Processed {len(cancelled_orgs)} cancelled subscriptions"
        }

    except Exception as e:
        logger.error(f"Error during cancelled subscriptions check: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def mark_organizations_for_deletion(self) -> Dict[str, Any]:
    """
    Daily task to mark organizations for deletion after retention period expires.

    This task:
    1. Finds all organizations with data_retention_until < now()
    2. Marks them for deletion by setting deletion_scheduled_at
    3. Logs organizations scheduled for deletion
    4. In production, would trigger actual deletion after admin review

    Scheduled: Daily at 5:00 AM UTC (after cancelled subscription processing)

    Returns:
        dict: Summary of organizations marked for deletion
        {
            "success": bool,
            "marked_count": int,
            "marked_orgs": List[dict],
            "message": str
        }
    """
    logger.info("Starting daily organization deletion check...")
    db = SessionLocal()

    try:
        from datetime import datetime, UTC
        from api.models import Organization

        now = datetime.now(UTC).replace(tzinfo=None)
        marked_orgs = []

        # Find organizations past retention period
        organizations = db.query(Organization).filter(
            Organization.data_retention_until.isnot(None),
            Organization.data_retention_until <= now,
            Organization.deletion_scheduled_at.is_(None)  # Not already marked
        ).all()

        logger.info(f"Found {len(organizations)} organizations past retention period")

        for org in organizations:
            try:
                # Mark for deletion
                org.deletion_scheduled_at = now
                db.commit()
                db.refresh(org)

                marked_orgs.append({
                    "org_id": org.id,
                    "org_name": org.name,
                    "cancelled_at": org.cancelled_at.isoformat() if org.cancelled_at else None,
                    "retention_expired": org.data_retention_until.isoformat() if org.data_retention_until else None,
                    "marked_at": now.isoformat()
                })

                logger.warning(
                    f"Marked organization {org.id} ({org.name}) for deletion - "
                    f"retention expired on {org.data_retention_until.isoformat()}"
                )

                # TODO: In production:
                # 1. Send notification to admins
                # 2. Create backup before deletion
                # 3. Trigger actual deletion after admin confirmation
                # 4. Or automatically delete after additional grace period (e.g., 7 days)

            except Exception as e:
                logger.error(f"Error marking organization {org.id} for deletion: {e}", exc_info=True)
                db.rollback()
                # Continue with next organization

        return {
            "success": True,
            "marked_count": len(marked_orgs),
            "marked_orgs": marked_orgs,
            "message": f"Marked {len(marked_orgs)} organizations for deletion"
        }

    except Exception as e:
        logger.error(f"Error during organization deletion check: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Apply pending downgrades daily at 1:00 AM UTC (before trial check)
    "apply-pending-downgrades": {
        "task": "api.tasks.billing_tasks.apply_pending_downgrades",
        "schedule": crontab(hour=1, minute=0),
    },

    # Check expired trials daily at 2:00 AM UTC
    "check-expired-trials": {
        "task": "api.tasks.billing_tasks.check_expired_trials",
        "schedule": crontab(hour=2, minute=0),
    },

    # Check usage limits daily at 3:00 AM UTC
    "check-usage-limits": {
        "task": "api.tasks.billing_tasks.check_usage_limits",
        "schedule": crontab(hour=3, minute=0),
    },

    # Process cancelled subscriptions daily at 4:00 AM UTC (after usage checks)
    "process-cancelled-subscriptions": {
        "task": "api.tasks.billing_tasks.process_cancelled_subscriptions",
        "schedule": crontab(hour=4, minute=0),
    },

    # Mark organizations for deletion daily at 5:00 AM UTC (after cancellation processing)
    "mark-organizations-for-deletion": {
        "task": "api.tasks.billing_tasks.mark_organizations_for_deletion",
        "schedule": crontab(hour=5, minute=0),
    },
}
