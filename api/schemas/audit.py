"""Schemas for the audit-log read endpoint."""

from datetime import datetime
from typing import Any

from pydantic import ConfigDict

from api.schemas._serializers import BaseResponse


class AuditLogResponse(BaseResponse):
    """One audit log row."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    user_email: str | None
    organization_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    details: dict[str, Any] | None
    timestamp: datetime
    ip_address: str | None
    user_agent: str | None
    status: str
    error_message: str | None
