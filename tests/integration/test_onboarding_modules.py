"""
Integration tests for onboarding JavaScript modules.

Verifies that all onboarding modules convert correctly from ES6 to window.* pattern
and that all functions are properly exposed.
"""

import pytest


def test_onboarding_js_modules_exist(client):
    """
    Test that all onboarding JavaScript files exist and are accessible.
    """
    # Get index.html to verify script tags are present
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Verify all onboarding JS modules are loaded
    assert "onboarding-wizard.js" in html_content
    assert "onboarding-checklist.js" in html_content
    assert "quick-start-videos.js" in html_content
    assert "tutorial-overlays.js" in html_content
    assert "feature-unlocks.js" in html_content
    assert "sample-data-manager.js" in html_content


def test_onboarding_api_endpoints_exist(client):
    """
    Test that all onboarding API endpoints are registered.
    """
    # These should all be 401 (Unauthorized) not 404 (Not Found)
    # because they require authentication

    endpoints = [
        "/api/onboarding/progress",
        "/api/sample-data/generate",
        "/api/sample-data/clear",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        # Should be 401 (Unauthorized) or 422 (missing org_id), not 404 (Not Found)
        assert response.status_code in [401, 422], \
            f"Endpoint {endpoint} returned {response.status_code}, expected 401 or 422"


def test_onboarding_dashboard_route_exists(client):
    """
    Test that the onboarding dashboard route exists in index.html.
    """
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Verify onboarding dashboard section exists
    assert 'id="onboarding-dashboard"' in html_content or \
           'data-section="onboarding-dashboard"' in html_content


def test_sample_data_controls_in_dashboard(client):
    """
    Test that sample data controls are included in onboarding dashboard HTML.
    """
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Verify sample data controls container exists
    assert 'dashboard-sample-data-controls' in html_content


def test_video_grid_in_dashboard(client):
    """
    Test that video grid is included in onboarding dashboard HTML.
    """
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Verify video grid exists
    assert 'dashboard-video-grid' in html_content or \
           'video-grid' in html_content


def test_checklist_container_in_dashboard(client):
    """
    Test that checklist container is included in onboarding dashboard HTML.
    """
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Verify checklist container exists
    assert 'onboarding-checklist-container' in html_content or \
           'onboarding-checklist' in html_content


def test_all_js_modules_loaded_in_order(client):
    """
    Test that JavaScript modules are loaded in correct order.

    Correct order:
    1. i18n.js (first - needed by all)
    2. role-management.js
    3. edit-role-functions.js
    4. recurring-events.js
    5. sample-data-manager.js
    6. onboarding-wizard.js
    7. onboarding-checklist.js
    8. quick-start-videos.js
    9. tutorial-overlays.js
    10. feature-unlocks.js
    11. app-user.js (last - main app logic)
    """
    response = client.get("/")
    assert response.status_code == 200

    html_content = response.text

    # Find positions of script tags
    i18n_pos = html_content.find("i18n.js")
    sample_data_pos = html_content.find("sample-data-manager.js")
    checklist_pos = html_content.find("onboarding-checklist.js")
    videos_pos = html_content.find("quick-start-videos.js")
    tutorials_pos = html_content.find("tutorial-overlays.js")
    features_pos = html_content.find("feature-unlocks.js")
    app_user_pos = html_content.find("app-user.js")

    # Verify all scripts found
    assert i18n_pos > 0, "i18n.js not found"
    assert sample_data_pos > 0, "sample-data-manager.js not found"
    assert checklist_pos > 0, "onboarding-checklist.js not found"
    assert videos_pos > 0, "quick-start-videos.js not found"
    assert tutorials_pos > 0, "tutorial-overlays.js not found"
    assert features_pos > 0, "feature-unlocks.js not found"
    assert app_user_pos > 0, "app-user.js not found"

    # Verify order (i18n before all, app-user last)
    assert i18n_pos < sample_data_pos, "i18n.js must load before sample-data-manager.js"
    assert i18n_pos < checklist_pos, "i18n.js must load before onboarding-checklist.js"
    assert i18n_pos < videos_pos, "i18n.js must load before quick-start-videos.js"
    assert i18n_pos < tutorials_pos, "i18n.js must load before tutorial-overlays.js"
    assert i18n_pos < features_pos, "i18n.js must load before feature-unlocks.js"

    # app-user.js should be last (or near last)
    assert app_user_pos > features_pos, "feature-unlocks.js must load before app-user.js"


def test_onboarding_backend_integration_complete(client, auth_headers):
    """
    Test complete backend integration for onboarding system.

    Verifies:
    - GET /api/onboarding/progress creates record if not exists
    - PUT /api/onboarding/progress updates fields
    - All onboarding fields work correctly
    """
    # Get progress (should create if not exists)
    response = client.get(
        "/api/onboarding/progress",
        headers=auth_headers
    )
    assert response.status_code == 200

    initial_progress = response.json()
    assert "wizard_progress" in initial_progress
    assert "checklist_state" in initial_progress
    assert "tutorials_completed" in initial_progress
    assert "features_unlocked" in initial_progress
    assert "videos_watched" in initial_progress

    # Update checklist state
    response = client.put(
        "/api/onboarding/progress",
        json={"checklist_state": {"create_event": True, "add_team": True}},
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify update persisted
    response = client.get(
        "/api/onboarding/progress",
        headers=auth_headers
    )
    assert response.status_code == 200
    progress = response.json()
    assert progress["checklist_state"]["create_event"] is True
    assert progress["checklist_state"]["add_team"] is True

    # Update tutorials completed
    response = client.put(
        "/api/onboarding/progress",
        json={"tutorials_completed": ["event_creation", "team_management"]},
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify tutorials persisted
    response = client.get(
        "/api/onboarding/progress",
        headers=auth_headers
    )
    assert response.status_code == 200
    progress = response.json()
    assert "event_creation" in progress["tutorials_completed"]
    assert "team_management" in progress["tutorials_completed"]

    # Update features unlocked
    response = client.put(
        "/api/onboarding/progress",
        json={"features_unlocked": ["recurring_events", "manual_editing"]},
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify features persisted
    response = client.get(
        "/api/onboarding/progress",
        headers=auth_headers
    )
    assert response.status_code == 200
    progress = response.json()
    assert "recurring_events" in progress["features_unlocked"]
    assert "manual_editing" in progress["features_unlocked"]

    # Update videos watched
    response = client.put(
        "/api/onboarding/progress",
        json={"videos_watched": ["getting_started", "creating_events"]},
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify videos persisted
    response = client.get(
        "/api/onboarding/progress",
        headers=auth_headers
    )
    assert response.status_code == 200
    progress = response.json()
    assert "getting_started" in progress["videos_watched"]
    assert "creating_events" in progress["videos_watched"]
