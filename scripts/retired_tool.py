#!/usr/bin/env python3
"""Fail closed for repository tools that no longer have a safe supported contract."""

from __future__ import annotations

import sys

REPLACEMENTS = {
    "QUICK_DEMO.sh": "Use make test-all and docs/playbooks/README.md.",
    "build-binary.sh": "Release artifact construction remains tracked in GitHub issue #265.",
    "cleanup_maintenance.sh": "Remove only explicitly owned artifacts with their owning command.",
    "cleanup_servers.sh": "Terminate only the PID recorded by the command that started the server.",
    "migrate_add_role_to_assignments.py": "Use the current Alembic graph; role is in the initial revision.",
    "migrate_assignments.py": "Use the current Alembic graph; assignments are in the initial revision.",
    "migrate_invitations.py": "Use the current Alembic graph; invitations are in the initial revision.",
    "migrate_passwords_to_bcrypt.py": "Use password reset; never replace user passwords in bulk.",
    "migrate_timezone.py": "Use the current Alembic graph; timezone is in the initial revision.",
    "migrate_vacation_reason.py": "Use the current Alembic graph; vacation reason is in the initial revision.",
    "seed_sms_templates.py": "Paid SMS remains disabled and tracked in GitHub issue #257.",
    "test_docker_setup.sh": "Use documented Docker targets individually against an owned project.",
    "validate_email_system.sh": "Use local capture tests; provider acceptance requires explicit approval.",
}


def main(name: str) -> int:
    replacement = REPLACEMENTS.get(name)
    if replacement is None:
        print(f"Unknown retired tool: {name}", file=sys.stderr)
        return 2
    print(f"RETIRED: {name}. {replacement}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: retired_tool.py <tool-name>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
