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


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
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
}
