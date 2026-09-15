"""Durable delivery state transitions for committed notification intents."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from api.models import (
    EmailFrequency,
    EmailPreference,
    Notification,
    NotificationStatus,
    Organization,
)
from api.timeutils import utcnow

DEFAULT_LEASE_SECONDS = 120
DEFAULT_MAX_ATTEMPTS = 4
MAX_BACKOFF_SECONDS = 3600


def claim_notification(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
    now: datetime | None = None,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
) -> Notification | None:
    """Atomically claim a due intent or recover an expired worker lease."""
    if not lease_token:
        raise ValueError("delivery lease token is required")
    claimed_at = now or utcnow()
    due_pending = and_(
        Notification.status.in_(
            [
                NotificationStatus.PENDING,
                NotificationStatus.FAILED,
                NotificationStatus.RETRY,
            ]
        ),
        or_(Notification.next_attempt_at.is_(None), Notification.next_attempt_at <= claimed_at),
    )
    stale_sending = and_(
        Notification.status == NotificationStatus.SENDING,
        Notification.delivery_lease_expires_at.is_not(None),
        Notification.delivery_lease_expires_at <= claimed_at,
    )
    updated = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.org_id == org_id,
            or_(due_pending, stale_sending),
        )
        .update(
            {
                Notification.status: NotificationStatus.SENDING,
                Notification.delivery_attempts: Notification.delivery_attempts + 1,
                Notification.delivery_lease_token: lease_token,
                Notification.delivery_lease_expires_at: claimed_at
                + timedelta(seconds=max(1, lease_seconds)),
                Notification.last_attempt_at: claimed_at,
                Notification.next_attempt_at: None,
                Notification.error_message: None,
            },
            synchronize_session=False,
        )
    )
    db.commit()
    if updated != 1:
        return None
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.org_id == org_id)
        .one()
    )


def _leased_notification(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
) -> Notification:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.org_id == org_id)
        .one_or_none()
    )
    if (
        notification is None
        or notification.status != NotificationStatus.SENDING
        or notification.delivery_lease_token != lease_token
    ):
        raise ValueError("notification delivery lease is not current")
    return notification


def _clear_lease(notification: Notification) -> None:
    record = cast(Any, notification)
    record.delivery_lease_token = None
    record.delivery_lease_expires_at = None


def complete_notification(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
    message_id: str,
    now: datetime | None = None,
) -> Notification:
    """Record a provider-accepted message only for the current worker lease."""
    notification = _leased_notification(
        db,
        notification_id=notification_id,
        org_id=org_id,
        lease_token=lease_token,
    )
    record = cast(Any, notification)
    record.status = NotificationStatus.SENT
    record.sendgrid_message_id = message_id
    record.sent_at = now or utcnow()
    record.next_attempt_at = None
    record.error_message = None
    _clear_lease(notification)
    db.commit()
    db.refresh(notification)
    return notification


def fail_notification(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
    error: str,
    now: datetime | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> Notification:
    """Release a failed claim to bounded backoff or visible dead letter."""
    failed_at = now or utcnow()
    notification = _leased_notification(
        db,
        notification_id=notification_id,
        org_id=org_id,
        lease_token=lease_token,
    )
    record = cast(Any, notification)
    record.error_message = error[:2000]
    _clear_lease(notification)
    if record.delivery_attempts >= max(1, max_attempts):
        record.status = NotificationStatus.DEAD_LETTER
        record.next_attempt_at = None
    else:
        record.status = NotificationStatus.RETRY
        delay = min(MAX_BACKOFF_SECONDS, 60 * (2 ** (record.delivery_attempts - 1)))
        record.next_attempt_at = failed_at + timedelta(seconds=delay)
    db.commit()
    db.refresh(notification)
    return notification


def mark_notification_uncertain(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
    error: str,
) -> Notification:
    """Stop automatic retries when provider acceptance cannot be reconciled."""
    notification = _leased_notification(
        db,
        notification_id=notification_id,
        org_id=org_id,
        lease_token=lease_token,
    )
    record = cast(Any, notification)
    record.status = NotificationStatus.UNCERTAIN
    record.error_message = error[:2000]
    record.next_attempt_at = None
    _clear_lease(notification)
    db.commit()
    db.refresh(notification)
    return notification


def suppress_notification(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
    reason: str,
) -> Notification:
    """Retain the in-app intent while recording that email was not requested."""
    notification = _leased_notification(
        db,
        notification_id=notification_id,
        org_id=org_id,
        lease_token=lease_token,
    )
    record = cast(Any, notification)
    record.status = NotificationStatus.SUPPRESSED
    record.error_message = reason[:2000]
    record.next_attempt_at = None
    _clear_lease(notification)
    db.commit()
    db.refresh(notification)
    return notification


def defer_notification_to_digest(
    db: Session,
    *,
    notification_id: int,
    org_id: str,
    lease_token: str,
) -> Notification:
    """Release an immediate-delivery lease while retaining digest intent."""
    notification = _leased_notification(
        db,
        notification_id=notification_id,
        org_id=org_id,
        lease_token=lease_token,
    )
    record = cast(Any, notification)
    record.status = NotificationStatus.PENDING
    record.error_message = None
    record.next_attempt_at = None
    _clear_lease(notification)
    db.commit()
    db.refresh(notification)
    return notification


def due_notification_refs(
    db: Session,
    *,
    now: datetime | None = None,
    limit_per_org: int = 100,
) -> list[tuple[int, str]]:
    """List due intents per tenant without an unscoped notification query."""
    due_at = now or utcnow()
    references: list[tuple[int, str]] = []
    org_ids = [row[0] for row in db.query(Organization.id).all()]
    for org_id in org_ids:
        due_pending = and_(
            Notification.status.in_(
                [
                    NotificationStatus.PENDING,
                    NotificationStatus.FAILED,
                    NotificationStatus.RETRY,
                ]
            ),
            or_(
                Notification.next_attempt_at.is_(None),
                Notification.next_attempt_at <= due_at,
            ),
        )
        stale_sending = and_(
            Notification.status == NotificationStatus.SENDING,
            Notification.delivery_lease_expires_at.is_not(None),
            Notification.delivery_lease_expires_at <= due_at,
        )
        rows = (
            db.query(Notification.id)
            .outerjoin(
                EmailPreference,
                and_(
                    EmailPreference.person_id == Notification.recipient_id,
                    EmailPreference.org_id == Notification.org_id,
                ),
            )
            .filter(
                Notification.org_id == org_id,
                or_(due_pending, stale_sending),
                or_(
                    EmailPreference.id.is_(None),
                    EmailPreference.frequency.notin_([EmailFrequency.DAILY, EmailFrequency.WEEKLY]),
                ),
            )
            .order_by(Notification.created_at, Notification.id)
            .limit(max(1, limit_per_org))
            .all()
        )
        references.extend((notification_id, org_id) for (notification_id,) in rows)
    return references
