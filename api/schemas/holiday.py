"""Holiday schemas. Holidays are admin-managed exceptions used by the solver."""

from datetime import (
    date as DateType,  # noqa: N812 - field is named `date` to match the Holiday model column
)
from datetime import datetime

from pydantic import BaseModel, Field

from api.schemas._serializers import BaseResponse
from api.schemas.common import ListResponse


class HolidayBase(BaseModel):
    date: DateType
    label: str = Field(..., min_length=1, max_length=255)
    is_long_weekend: bool = False


class HolidayCreate(HolidayBase):
    org_id: str = Field(..., description="Organization ID")


class HolidayUpdate(BaseModel):
    date: DateType | None = None
    label: str | None = Field(None, min_length=1, max_length=255)
    is_long_weekend: bool | None = None


class HolidayResponse(BaseResponse, HolidayBase):
    id: int
    org_id: str
    created_at: datetime


HolidayList = ListResponse[HolidayResponse]


class HolidayBulkImportItem(HolidayBase):
    """One item in a holiday bulk-import payload (no `id`; assigned by DB)."""


class HolidayBulkImport(BaseModel):
    items: list[HolidayBulkImportItem] = Field(
        ..., min_length=1, max_length=500, description="Holidays to create (1-500 rows)"
    )


class HolidayBulkImportError(BaseModel):
    row: int
    label: str | None
    message: str


class HolidayBulkImportResponse(BaseModel):
    created: int
    skipped: int
    errors: list[HolidayBulkImportError] = Field(default_factory=list)
