"""Wire format tests: API responses serialize datetimes as ISO 8601 with `Z`."""

import re
from datetime import UTC, datetime

import pytest

from api.schemas.event import EventResponse
from api.schemas.organization import OrganizationResponse
from api.schemas.person import PersonResponse

# ISO 8601 with mandatory Z suffix and optional fractional seconds.
ISO_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


@pytest.fixture
def utc_dt() -> datetime:
    return datetime(2026, 5, 5, 12, 30, 45, tzinfo=UTC)


@pytest.fixture
def naive_dt() -> datetime:
    """Naive datetime (no tzinfo). Wire format should still produce Z."""
    return datetime(2026, 5, 5, 12, 30, 45)


def _person(dt: datetime) -> PersonResponse:
    return PersonResponse(
        id="p1",
        org_id="o1",
        name="Test Person",
        email="t@example.com",
        roles=["volunteer"],
        timezone="UTC",
        extra_data={},
        created_at=dt,
        updated_at=dt,
    )


def _organization(dt: datetime) -> OrganizationResponse:
    return OrganizationResponse(
        id="o1",
        name="Test Org",
        region="Test",
        config={},
        created_at=dt,
        updated_at=dt,
    )


def _event(dt: datetime) -> EventResponse:
    return EventResponse(
        id="e1",
        org_id="o1",
        type="service",
        start_time=dt,
        end_time=dt,
        extra_data={},
        created_at=dt,
        updated_at=dt,
    )


@pytest.mark.parametrize("factory", [_person, _organization, _event])
def test_response_serializes_utc_datetime_with_z_suffix(factory, utc_dt):
    payload = factory(utc_dt).model_dump(mode="json")
    for field in ("created_at", "updated_at"):
        value = payload[field]
        assert ISO_Z_RE.match(value), f"{field} = {value!r} is not ISO 8601 with Z"


@pytest.mark.parametrize("factory", [_person, _organization, _event])
def test_response_treats_naive_datetime_as_utc(factory, naive_dt):
    payload = factory(naive_dt).model_dump(mode="json")
    for field in ("created_at", "updated_at"):
        assert payload[field].endswith("Z"), f"{field} should end in Z, got {payload[field]!r}"


def test_event_start_and_end_time_serialize_with_z(utc_dt):
    payload = _event(utc_dt).model_dump(mode="json")
    assert ISO_Z_RE.match(payload["start_time"])
    assert ISO_Z_RE.match(payload["end_time"])
