"""Pure parser/validator for bulk people import.

Sprint 4 PR 4.3 introduces an admin-only `POST /people/bulk` endpoint that
accepts a JSON array of `PersonCreate` payloads. Validation logic lives here
so it can be unit-tested without DB or HTTP setup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from api.schemas.person import PersonCreate

#: Maximum number of items accepted in a single bulk import request.
MAX_BULK_IMPORT_ITEMS = 1000


@dataclass
class BulkImportError:
    """One failure entry returned to the caller."""

    index: int
    id: str | None
    reason: str


@dataclass
class BulkImportParseResult:
    """Pure parse outcome: which rows are valid, which were rejected, and why.

    The router consumes `valid` and persists rows that don't already exist,
    appending duplicates to `skipped` and DB-level failures to `errors`.
    """

    valid: list[PersonCreate] = field(default_factory=list)
    errors: list[BulkImportError] = field(default_factory=list)
    duplicate_indexes: list[int] = field(default_factory=list)


def parse_bulk_people(
    items: list[dict[str, Any]],
    expected_org_id: str,
) -> BulkImportParseResult:
    """Validate raw JSON items and detect intra-payload duplicate IDs.

    Rules:
      * Any row whose `org_id` differs from `expected_org_id` is rejected.
      * Schema errors (missing fields, bad types, bad email) → `errors`.
      * Repeated IDs within `items` → keep the first, flag the rest as
        duplicates so the router can surface them as `skipped`.
    """
    result = BulkImportParseResult()
    seen_ids: set[str] = set()

    for index, raw in enumerate(items):
        raw_id = raw.get("id") if isinstance(raw, dict) else None

        if not isinstance(raw, dict):
            result.errors.append(
                BulkImportError(index=index, id=None, reason="item must be a JSON object")
            )
            continue

        if raw.get("org_id") not in (None, expected_org_id):
            result.errors.append(
                BulkImportError(
                    index=index,
                    id=raw_id,
                    reason=f"org_id mismatch: expected '{expected_org_id}'",
                )
            )
            continue

        # Inject the expected org_id when omitted so callers can post a flat list.
        payload = {**raw, "org_id": expected_org_id}

        try:
            person = PersonCreate(**payload)
        except ValidationError as exc:
            result.errors.append(
                BulkImportError(index=index, id=raw_id, reason=_summarize_validation(exc))
            )
            continue

        if person.id in seen_ids:
            result.duplicate_indexes.append(index)
            continue

        seen_ids.add(person.id)
        result.valid.append(person)

    return result


def _summarize_validation(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()))
        parts.append(f"{loc}: {err.get('msg')}" if loc else err.get("msg", "invalid"))
    return "; ".join(parts) or "validation failed"
