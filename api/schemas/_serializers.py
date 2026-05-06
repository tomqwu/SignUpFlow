"""Shared response-schema mixin: emit ISO 8601 UTC datetimes with `Z` suffix on the wire.

Pydantic 2 already serializes timezone-aware UTC datetimes as `...Z`. The DB layer in
this project stores naive UTC (`api/utils/timeutils.utcnow()` strips tzinfo for SQLite
portability), so without help the wire would emit `2026-05-05T12:30:45` with no offset
hint — Dart's `DateTime.parse` then assumes local time. `BaseResponse` localizes any
naive datetime field to UTC after model construction so the existing Pydantic
serializer produces the desired `...Z` form.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class BaseResponse(BaseModel):
    """Mixin for API response models. Treats naive datetime fields as UTC."""

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _localize_naive_datetimes(self) -> "BaseResponse":
        for field_name, value in list(self.__dict__.items()):
            if isinstance(value, datetime) and value.tzinfo is None:
                object.__setattr__(self, field_name, value.replace(tzinfo=UTC))
        return self
