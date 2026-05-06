"""Cross-tenant query safety net.

A SQLAlchemy `do_orm_execute` listener that flags SELECTs against models
carrying a direct `org_id` column when the WHERE clause does not constrain
`org_id`. This catches the common "forgot to filter by org_id" leak before
it reaches a response.

Modes (env var `TENANCY_GUARD`):
- `off` — listener does nothing (recommended only for migrations).
- `warn` — log a warning and continue (recommended for production).
- `strict` — raise `TenancyViolationError` (recommended for tests).

This is a defense-in-depth check, not a primary control. The primary
control remains explicit `verify_org_member()` in route handlers.
"""

from __future__ import annotations

import os

from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session

from api.logging_config import logger


class TenancyViolationError(RuntimeError):
    """Raised when a select against a tenant-scoped model omits org_id filtering."""


def _mode() -> str:
    return os.getenv("TENANCY_GUARD", "warn").strip().lower()


def _tenant_scoped_entities(state: ORMExecuteState) -> set[str]:
    """Return names of selected entities that have a direct `org_id` column."""
    names: set[str] = set()
    try:
        descs = state.statement.column_descriptions or []
    except Exception:
        return names
    for desc in descs:
        entity = desc.get("entity") if isinstance(desc, dict) else None
        if entity is None:
            continue
        if hasattr(entity, "org_id"):
            cls_name = getattr(entity, "__name__", None)
            if cls_name:
                names.add(cls_name)
    return names


# Filter substrings that count as "sufficiently restrictive": tenant scoping
# (`org_id`) plus globally-unique identifiers used for legitimate single-row
# lookups (signup duplicate check, login, password reset, invitation accept).
# This is a heuristic — the primary tenant control is `verify_org_member()` in
# route handlers; the listener catches the common "forgot to filter" leak.
_SAFE_FILTER_FRAGMENTS = (
    "org_id",
    ".id =",
    ".id IN",
    ".email =",
    ".email IN",
    ".token =",
    ".calendar_token =",
)


def _where_is_safe(state: ORMExecuteState) -> bool:
    where = getattr(state.statement, "whereclause", None)
    if where is None:
        return False
    try:
        rendered = str(where.compile(compile_kwargs={"literal_binds": False}))
    except Exception:
        return False
    return any(fragment in rendered for fragment in _SAFE_FILTER_FRAGMENTS)


def _check(state: ORMExecuteState) -> None:
    mode = _mode()
    if mode == "off":
        return
    if not state.is_select:
        return
    # Relationship loads (e.g., parent.children lazy-load on delete cascade)
    # are scoped by the parent row's PK, not by org_id. The parent's tenancy
    # was already enforced when the parent was loaded.
    if getattr(state, "is_relationship_load", False):
        return
    entities = _tenant_scoped_entities(state)
    if not entities:
        return
    if _where_is_safe(state):
        return

    msg = (
        f"Tenancy guard: SELECT against {sorted(entities)} without org_id filter. "
        f"This is a multi-tenant data leak risk."
    )
    if mode == "strict":
        raise TenancyViolationError(msg)
    logger.warning(msg)


_INSTALLED = False


def install_tenancy_guard(target: type = Session) -> None:
    """Install the listener on a Session class. Idempotent."""
    global _INSTALLED
    if _INSTALLED:
        return
    event.listen(target, "do_orm_execute", _check)
    _INSTALLED = True
