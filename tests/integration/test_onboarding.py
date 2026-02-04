"""
Integration tests for onboarding API endpoints.

Tests onboarding progress tracking, wizard state management,
and sample data generation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from api.models import Person, Organization, OnboardingProgress, Event, Team
from api.database import get_db
from tests.conftest import create_test_user, create_test_org


client = TestClient(app)


def test_get_onboarding_progress_creates_if_not_exists(db: Session):
    """
    Test GET /api/onboarding/progress creates progress if it doesn't exist.

    Scenario:
      Given a user without OnboardingProgress record
      When GET /api/onboarding/progress is called
      Then a new OnboardingProgress record should be created
      And default values should be returned
    """
    # Note: The test fixture mocks get_current_user to return test_admin user
    # So we need to ensure that user exists in the database
    from api.models import Organization

    # Create the test org that the mocked user belongs to
    test_org = db.query(Organization).filter(Organization.id == "test_org").first()
    if not test_org:
        test_org = Organization(id="test_org", name="Test Organization", region="US", config={})
        db.add(test_org)
        db.commit()

    # Create the mocked admin user
    user = db.query(Person).filter(Person.id == "test_admin").first()
    if not user:
        user = create_test_user(db, "test_org", roles=["admin"], email="admin@test.com")
        # Override the ID to match what the mock returns
        user.id = "test_admin"
        db.merge(user)
        db.commit()

    # Delete any existing onboarding progress
    db.query(OnboardingProgress).filter(OnboardingProgress.person_id == "test_admin").delete()
    db.commit()

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "password"  # Password used in seeded test_admin
    })
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    # Get onboarding progress
    response = client.get(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify default values (test_admin user from mock)
    assert data["person_id"] == "test_admin"
    assert data["org_id"] == "test_org"
    assert data["wizard_step_completed"] == 0
    assert data["wizard_data"] == {}
    assert data["checklist_state"] == {}
    assert data["tutorials_completed"] == []
    assert data["features_unlocked"] == []
    assert data["videos_watched"] == []
    assert data["onboarding_skipped"] is False
    assert data["checklist_dismissed"] is False
    assert data["tutorials_dismissed"] is False

    # Verify record was created in database
    progress = db.query(OnboardingProgress).filter(
        OnboardingProgress.person_id == user.id
    ).first()
    assert progress is not None


def test_save_wizard_progress(db: Session):
    """
    Test PUT /api/onboarding/progress saves wizard state.

    Scenario:
      Given a user on Step 2 of wizard
      When wizard progress is saved
      Then wizard_step_completed should be updated
      And wizard_data should be persisted
      And subsequent GET should return saved state
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Save wizard progress for Step 2
    wizard_data = {
        "org": {
            "name": "Test Church",
            "location": "Test City, ST",
            "timezone": "America/New_York"
        },
        "event": {
            "title": "Sunday Service",
            "datetime": "2025-11-01T10:00:00",
            "duration": 90
        }
    }

    response = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "wizard_step_completed": 2,
            "wizard_data": wizard_data
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["wizard_step_completed"] == 2

    # Verify persistence - GET should return saved state
    get_response = client.get(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert get_response.status_code == 200
    saved_data = get_response.json()
    assert saved_data["wizard_step_completed"] == 2

    # Verify wizard_data was persisted correctly
    assert saved_data["wizard_data"] == wizard_data
    assert saved_data["wizard_data"]["org"]["name"] == "Test Church"
    assert saved_data["wizard_data"]["event"]["title"] == "Sunday Service"


def test_update_checklist_state(db: Session):
    """
    Test PUT /api/onboarding/progress updates checklist items.

    Scenario:
      Given a user with empty checklist
      When checklist items are marked complete
      Then checklist_state should be updated
      And existing items should be preserved
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Mark "complete_profile" as complete
    response = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "checklist_state": {"complete_profile": True}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["checklist_state"]["complete_profile"] is True

    # Mark "create_event" as complete (should merge, not replace)
    response2 = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "checklist_state": {"create_event": True}
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()
    # Both should be present
    assert data2["checklist_state"]["complete_profile"] is True
    assert data2["checklist_state"]["create_event"] is True


def test_update_tutorials_completed(db: Session):
    """
    Test PUT /api/onboarding/progress tracks tutorial completion.

    Scenario:
      Given a user who completed "event_creation" tutorial
      When tutorial completion is saved
      Then tutorials_completed should include the tutorial ID
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Mark tutorial as completed
    response = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tutorials_completed": ["event_creation"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "event_creation" in data["tutorials_completed"]

    # Add another tutorial
    response2 = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tutorials_completed": ["event_creation", "team_management"]
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert "event_creation" in data2["tutorials_completed"]
    assert "team_management" in data2["tutorials_completed"]


def test_update_features_unlocked(db: Session):
    """
    Test PUT /api/onboarding/progress tracks feature unlocks.

    Scenario:
      Given a user who unlocked "recurring_events" feature
      When feature unlock is saved
      Then features_unlocked should include the feature ID
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Mark feature as unlocked
    response = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "features_unlocked": ["recurring_events"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "recurring_events" in data["features_unlocked"]


def test_skip_onboarding(db: Session):
    """
    Test POST /api/onboarding/skip marks onboarding as skipped.

    Scenario:
      Given an experienced user
      When they skip onboarding
      Then wizard_step_completed should be 4 (completed)
      And onboarding_skipped should be True
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Skip onboarding
    response = client.post(
        "/api/onboarding/skip",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Onboarding skipped successfully"

    # Verify state
    get_response = client.get(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = get_response.json()
    assert data["wizard_step_completed"] == 4
    assert data["onboarding_skipped"] is True


def test_reset_onboarding(db: Session):
    """
    Test POST /api/onboarding/reset clears all progress.

    Scenario:
      Given a user with completed onboarding
      When they reset onboarding
      Then all progress should be cleared
      And they can go through wizard again
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Set some progress
    client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "wizard_step_completed": 4,
            "checklist_state": {"complete_profile": True},
            "tutorials_completed": ["event_creation"],
            "features_unlocked": ["recurring_events"]
        }
    )

    # Reset onboarding
    response = client.post(
        "/api/onboarding/reset",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Verify all cleared
    get_response = client.get(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = get_response.json()
    assert data["wizard_step_completed"] == 0
    assert data["checklist_state"] == {}
    assert data["tutorials_completed"] == []
    assert data["features_unlocked"] == []
    assert data["onboarding_skipped"] is False


def test_wizard_step_validation(db: Session):
    """
    Test PUT /api/onboarding/progress validates wizard step range.

    Scenario:
      Given invalid wizard_step_completed value
      When progress update is attempted
      Then 422 error should be returned
    """
    # Create test org and user
    org = create_test_org(db)
    user = create_test_user(db, org.id)

    # Get auth token
    login_response = client.post("/api/auth/login", json={
        "email": user.email,
        "password": "TestPassword123!"
    })
    token = login_response.json()["token"]

    # Try invalid step (> 4)
    response = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "wizard_step_completed": 5
        }
    )

    assert response.status_code == 422
    # Pydantic v2 returns a structured list in detail
    detail = response.json()["detail"]
    assert any("must be between 0 and 4" in err.get("msg", "") for err in detail)

    # Try negative step
    response2 = client.put(
        "/api/onboarding/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "wizard_step_completed": -1
        }
    )

    assert response2.status_code == 422
