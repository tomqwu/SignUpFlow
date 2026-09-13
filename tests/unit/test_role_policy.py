"""Permission roles and scheduling qualifications remain distinct."""

import pytest

from api.roles import build_roles, parse_qualifications, replace_qualifications

pytestmark = pytest.mark.unit


def test_parse_qualifications_accepts_domain_identifiers_and_deduplicates():
    assert parse_qualifications("worship_leader, sound;worship_leader") == [
        "worship_leader",
        "sound",
    ]


@pytest.mark.parametrize("value", ["admin", "Admin", "ADMIN", "volunteer", "Volunteer"])
def test_parse_qualifications_rejects_reserved_permission_names(value):
    with pytest.raises(ValueError, match="reserved"):
        parse_qualifications(value)


@pytest.mark.parametrize("value", ["lead pastor", "usher!", "-coach", "score/keeper"])
def test_parse_qualifications_rejects_invalid_identifiers(value):
    with pytest.raises(ValueError, match="lowercase"):
        parse_qualifications(value)


def test_build_roles_requires_an_exact_access_role():
    assert build_roles("volunteer", ["usher"]) == ["volunteer", "usher"]
    assert build_roles("admin", ["coach"]) == ["admin", "coach"]
    with pytest.raises(ValueError, match="access role"):
        build_roles("owner", ["coach"])


def test_replace_qualifications_preserves_access_without_escalation():
    assert replace_qualifications(["volunteer", "usher"], ["sound"]) == [
        "volunteer",
        "sound",
    ]
    assert replace_qualifications(["admin", "usher"], ["sound"]) == ["admin", "sound"]
    assert replace_qualifications(["coach"], ["scorekeeper"]) == [
        "volunteer",
        "scorekeeper",
    ]
