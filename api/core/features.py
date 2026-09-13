"""Runtime feature boundaries for deferred external services."""

from fastapi import HTTPException

from api.core.config import settings


def billing_enabled() -> bool:
    """Return whether commercial billing surfaces may be used."""
    return settings.BILLING_ENABLED


def sms_enabled() -> bool:
    """Return whether paid SMS delivery surfaces may be used."""
    return settings.SMS_ENABLED


def require_billing_enabled() -> None:
    """Fail before auth, database, or provider work when billing is deferred."""
    if not billing_enabled():
        raise HTTPException(status_code=404, detail="Billing is not enabled")


def require_sms_enabled() -> None:
    """Fail before auth, database, or provider work when SMS is deferred."""
    if not sms_enabled():
        raise HTTPException(status_code=404, detail="SMS is not enabled")


def disabled_billing_task_result() -> dict[str, bool | str]:
    """Return the stable no-op result for deferred billing tasks."""
    return {"success": False, "status": "disabled", "message": "Billing is not enabled"}


def disabled_sms_task_result() -> dict[str, str]:
    """Return the stable no-op result for deferred SMS tasks."""
    return {"status": "disabled", "message": "SMS is not enabled"}
