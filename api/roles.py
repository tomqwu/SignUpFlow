"""Role policy shared by API and web onboarding paths."""

from __future__ import annotations

import re
from collections.abc import Iterable

PERMISSION_ROLES = frozenset({"admin", "volunteer"})
QUALIFICATION_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def parse_qualifications(raw: str) -> list[str]:
    """Parse comma/semicolon input into safe, ordered scheduling identifiers."""
    qualifications: list[str] = []
    for value in re.split(r"[,;]", raw):
        qualification = value.strip()
        if not qualification:
            continue
        if qualification.casefold() in PERMISSION_ROLES:
            raise ValueError(f"{qualification!r} is a reserved permission role")
        if not QUALIFICATION_PATTERN.fullmatch(qualification):
            raise ValueError(
                "Qualifications must be lowercase identifiers using letters, numbers, and underscores"
            )
        if qualification not in qualifications:
            qualifications.append(qualification)
    return qualifications


def build_roles(access_role: str, qualifications: Iterable[str]) -> list[str]:
    """Combine one exact permission role with validated scheduling qualifications."""
    if access_role not in PERMISSION_ROLES:
        raise ValueError("Select a valid access role")
    parsed = parse_qualifications(",".join(qualifications))
    return [access_role, *parsed]


def replace_qualifications(
    existing_roles: Iterable[str], qualifications: Iterable[str]
) -> list[str]:
    """Replace qualifications while preserving, and never escalating, account access."""
    existing = list(existing_roles)
    access_role = "admin" if "admin" in existing else "volunteer"
    return build_roles(access_role, qualifications)
