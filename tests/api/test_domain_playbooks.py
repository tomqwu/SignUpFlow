"""Apply the registered workflow to every discovered playbook with real JWT auth."""

import pytest

from tests.playbooks.workflows import run_six_week_roster

pytestmark = pytest.mark.no_mock_auth


def test_six_week_playbook(client, playbook_spec):
    run_six_week_roster(client, playbook_spec)
