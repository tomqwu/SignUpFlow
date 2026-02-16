"""
SMS cost tracking and budget management.

Tracks SMS usage and costs per organization with budget alerts.
- Cost: $0.0079 per SMS segment (160 chars)
- Budget alerts at 80% and 100% utilization
- Auto-pause at budget limit (optional)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from api.models import SmsUsage


class CostTracker:
    """SMS cost tracking and budget management."""

    def __init__(self):
        """Initialize cost tracker."""
        self.cost_per_segment_cents = 1  # $0.0079 ≈ 1 cent for simplicity
        self.segment_length = 160  # Standard SMS segment length

    def calculate_cost(self, message_text: str) -> int:
        """
        Calculate cost in cents for message.

        Args:
            message_text: SMS message text

        Returns:
            Cost in cents (1 cent per 160 chars)
        """
        segments = self._calculate_segments(message_text)
        return segments * self.cost_per_segment_cents

    def track_usage(
        self,
        db: Session,
        organization_id: int,
        message_type: str,
        cost_cents: int,
    ) -> Dict[str, Any]:
        """
        Track SMS usage and update budget counters.

        Args:
            db: Database session
            organization_id: Organization ID
            message_type: Type of message ('assignment', 'reminder', 'broadcast', 'system')
            cost_cents: Cost of message in cents

        Returns:
            Dictionary with budget status and alert info
        """
        # Get or create usage record for current month
        from api.timeutils import utcnow
        month_year = utcnow().strftime("%Y-%m")

        usage = (
            db.query(SmsUsage)
            .filter(
                SmsUsage.organization_id == organization_id,
                SmsUsage.month_year == month_year,
            )
            .first()
        )

        if not usage:
            # Create new usage record with default $100 budget
            usage = SmsUsage(
                organization_id=organization_id,
                month_year=month_year,
                assignment_count=0,
                reminder_count=0,
                broadcast_count=0,
                system_count=0,
                total_cost_cents=0,
                budget_limit_cents=10000,  # $100 default
                alert_threshold_percent=80,
                alert_sent_at_80=False,
                alert_sent_at_100=False,
                auto_pause_enabled=True,
            )
            db.add(usage)

        # Increment counters
        usage.total_cost_cents += cost_cents

        if message_type == "assignment":
            usage.assignment_count += 1
        elif message_type == "reminder":
            usage.reminder_count += 1
        elif message_type == "broadcast":
            usage.broadcast_count += 1
        elif message_type == "system":
            usage.system_count += 1

        db.commit()

        # Calculate budget utilization
        utilization_percent = (
            usage.total_cost_cents / usage.budget_limit_cents * 100
        )

        # Check for budget alerts
        alert_needed = None
        if utilization_percent >= 100 and not usage.alert_sent_at_100:
            alert_needed = "budget_limit_reached"
            usage.alert_sent_at_100 = True
            db.commit()
        elif (
            utilization_percent >= usage.alert_threshold_percent
            and not usage.alert_sent_at_80
        ):
            alert_needed = "budget_threshold_warning"
            usage.alert_sent_at_80 = True
            db.commit()

        return {
            "month_year": month_year,
            "total_cost_cents": usage.total_cost_cents,
            "budget_limit_cents": usage.budget_limit_cents,
            "utilization_percent": round(utilization_percent, 2),
            "remaining_cents": usage.budget_limit_cents - usage.total_cost_cents,
            "alert_needed": alert_needed,
            "auto_pause_enabled": usage.auto_pause_enabled,
        }

    def check_budget(
        self, db: Session, organization_id: int
    ) -> Dict[str, Any]:
        """
        Check current budget status for organization.

        Args:
            db: Database session
            organization_id: Organization ID

        Returns:
            Dictionary with budget status
        """
        from api.timeutils import utcnow
        month_year = utcnow().strftime("%Y-%m")

        usage = (
            db.query(SmsUsage)
            .filter(
                SmsUsage.organization_id == organization_id,
                SmsUsage.month_year == month_year,
            )
            .first()
        )

        if not usage:
            # No usage yet this month
            return {
                "month_year": month_year,
                "total_cost_cents": 0,
                "budget_limit_cents": 10000,  # Default $100
                "utilization_percent": 0,
                "remaining_cents": 10000,
                "budget_exceeded": False,
                "can_send": True,
            }

        utilization_percent = (
            usage.total_cost_cents / usage.budget_limit_cents * 100
        )
        budget_exceeded = utilization_percent >= 100

        return {
            "month_year": month_year,
            "total_cost_cents": usage.total_cost_cents,
            "budget_limit_cents": usage.budget_limit_cents,
            "utilization_percent": round(utilization_percent, 2),
            "remaining_cents": usage.budget_limit_cents - usage.total_cost_cents,
            "budget_exceeded": budget_exceeded,
            "can_send": not budget_exceeded or not usage.auto_pause_enabled,
        }

    def _calculate_segments(self, message_text: str) -> int:
        """
        Calculate number of SMS segments for message.

        Args:
            message_text: SMS message text

        Returns:
            Number of 160-character segments (minimum 1)
        """
        length = len(message_text)
        if length == 0:
            return 1

        # Standard SMS: 160 chars per segment
        # For multi-part: 153 chars per segment (7 chars for concatenation header)
        if length <= self.segment_length:
            return 1
        else:
            # Multi-part message
            return (length + 152) // 153  # Ceiling division
