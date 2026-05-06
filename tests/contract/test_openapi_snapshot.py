"""Contract test: the published OpenAPI schema must not drift unexpectedly.

`mobile/` consumes this schema via openapi-generator-cli (Dart-Dio target). Any change
to paths, request/response models, or operation IDs reaches the Flutter client as a
generated-code diff. This snapshot test fails when the schema changes so the dev can
inspect the diff before regenerating the client.

To intentionally update the snapshot:

    poetry run python -m tests.contract.test_openapi_snapshot --update

or via Makefile: `make update-openapi-snapshot`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from api.main import app

SNAPSHOT_PATH = Path(__file__).parent / "openapi.snapshot.json"


def _normalize(schema: dict[str, Any]) -> str:
    """Return a deterministic textual form of the OpenAPI schema."""
    return json.dumps(schema, sort_keys=True, indent=2) + "\n"


def _current_schema_text() -> str:
    return _normalize(app.openapi())


def _write_snapshot(text: str) -> None:
    SNAPSHOT_PATH.write_text(text)


def test_openapi_schema_matches_snapshot() -> None:
    """Diff the live schema against the committed snapshot."""
    if not SNAPSHOT_PATH.exists():
        _write_snapshot(_current_schema_text())
        raise AssertionError(
            f"Wrote initial snapshot to {SNAPSHOT_PATH}. " "Review and commit it, then re-run."
        )

    expected = SNAPSHOT_PATH.read_text()
    actual = _current_schema_text()

    if actual != expected:
        raise AssertionError(
            "OpenAPI schema drifted from the committed snapshot. "
            "If the change is intentional: review impact on `mobile/`, "
            "run `make mobile-codegen` to regenerate the Flutter client, "
            "then `make update-openapi-snapshot` to refresh this snapshot."
        )


if __name__ == "__main__":  # pragma: no cover
    if "--update" in sys.argv:
        _write_snapshot(_current_schema_text())
        print(f"Updated snapshot at {SNAPSHOT_PATH}")
    else:
        # Quick local verification path that doesn't require pytest.
        try:
            test_openapi_schema_matches_snapshot()
        except AssertionError as exc:
            print(f"FAIL: {exc}")
            sys.exit(1)
        print("OK: schema matches snapshot")
