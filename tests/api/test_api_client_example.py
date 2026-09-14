"""Execute the retained API client example against the real in-process application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from examples.api_client_example import run_workflow


@pytest.mark.no_mock_auth
def test_api_client_example_completes_local_basketball_workflow(client: TestClient) -> None:
    """The example bootstraps, invites, schedules, and publishes through canonical routes."""
    result = run_workflow(client, suffix="api-example")

    assert result["org_id"] == "riverside-basketball-api-example"
    assert result["assignment_count"] == 1
    assert result["published"] is True
