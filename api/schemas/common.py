"""Shared list-response envelope and pagination params for all list endpoints."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    """Uniform shape for paginated list responses.

    Every `GET /api/v1/<resource>/` endpoint returns this shape so the Flutter
    client (and any future codegen consumer) gets one envelope to unwrap.

    Fields:
        items: the page slice
        total: total rows matching the query, regardless of pagination
        limit: the page size used to produce `items`
        offset: the offset applied to produce `items`
    """

    items: list[T]
    total: int
    limit: int
    offset: int


@dataclass
class PaginationParams:
    """Page slice carried into list endpoints via Depends."""

    limit: int
    offset: int


def get_pagination_params(
    limit: int = Query(50, ge=1, le=200, description="Page size, max 200"),
    offset: int = Query(0, ge=0, description="Number of rows to skip"),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)
