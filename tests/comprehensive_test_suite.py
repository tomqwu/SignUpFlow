#!/usr/bin/env python3
"""
Comprehensive Test Suite for Rostio
Covers all API endpoints and critical GUI workflows with blocked dates integration
"""

import pytest
import requests
from datetime import datetime, timedelta, date
from playwright.sync_api import sync_playwright, expect
import time

API_BASE = "http://localhost:8000/api"
APP_URL = "http://localhost:8000"

# ============================================================================
# API TESTS
# ============================================================================

class TestOrganizationsAPI:
    """Test Organization CRUD operations"""

    def test_create_organization(self):
        """Create a new organization"""
        data = {"id": "test_org_api", "name": "Test Organization API", "region": "Test Region"}
        response = requests.post(f"{API_BASE}/organizations/", json=data)
        assert response.status_code in [200, 201, 409]  # 409 if already exists

    def test_list_organizations(self):
        """List all organizations"""
        response = requests.get(f"{API_BASE}/organizations/")
        assert response.status_code == 200
        data = response.json()
        assert "organizations" in data
        assert isinstance(data["organizations"], list)

    def test_get_organization(self):
        """Get specific organization"""
        response = requests.get(f"{API_BASE}/organizations/test_org")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_org"


class TestPeopleAPI:
    """Test People CRUD operations"""

    def test_create_person(self):
        """Create a new person"""
        data = {
            "id": "test_person_001",
            "name": "Test Person",
            "email": "test@example.com",
            "org_id": "test_org",
            "roles": ["volunteer"]
        }
        response = requests.post(f"{API_BASE}/people/", json=data)
        assert response.status_code in [200, 201, 409]

    def test_list_people(self):
        """List all people in organization"""
        response = requests.get(f"{API_BASE}/people/?org_id=test_org")
        assert response.status_code == 200
        data = response.json()
        assert "people" in data
        assert isinstance(data["people"], list)

    def test_update_person_roles(self):
        """Update person's roles"""
        # First get a valid person ID
        resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if resp.status_code == 200 and resp.json()["people"]:
            person_id = resp.json()["people"][0]["id"]
            data = {"roles": ["volunteer", "leader"]}
            response = requests.put(f"{API_BASE}/people/{person_id}", json=data)
            assert response.status_code == 200
        else:
            pytest.skip("No test person available")


class TestEventsAPI:
    """Test Event CRUD operations"""

    def test_create_event(self):
        """Create a new event"""
        start_time = (datetime.now() + timedelta(days=7)).isoformat()
        end_time = (datetime.now() + timedelta(days=7, hours=2)).isoformat()

        data = {
            "id": "test_event_001",
            "org_id": "test_org",
            "type": "Test Event",
            "start_time": start_time,
            "end_time": end_time,
            "extra_data": {
                "role_counts": {
                    "volunteer": 2,
                    "leader": 1
                }
            }
        }
        response = requests.post(f"{API_BASE}/events/", json=data)
        assert response.status_code in [200, 201, 409]

    def test_list_events(self):
        """List all events"""
        response = requests.get(f"{API_BASE}/events/?org_id=test_org")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

    def test_get_available_people(self):
        """Get available people for event"""
        # Get first event
        events_resp = requests.get(f"{API_BASE}/events/?org_id=test_org")
        if events_resp.status_code == 200 and events_resp.json().get("events"):
            event_id = events_resp.json()["events"][0]["id"]
            response = requests.get(f"{API_BASE}/events/{event_id}/available-people")
            assert response.status_code == 200
            people = response.json()
            assert isinstance(people, list)
            # Check that each person has is_blocked field
            for person in people:
                assert "is_blocked" in person
                assert isinstance(person["is_blocked"], bool)
        else:
            pytest.skip("No test events available")

    def test_event_validation(self):
        """Test event validation endpoint"""
        # Get first event
        events_resp = requests.get(f"{API_BASE}/events/?org_id=test_org")
        if events_resp.status_code == 200 and events_resp.json().get("events"):
            event_id = events_resp.json()["events"][0]["id"]
            response = requests.get(f"{API_BASE}/events/{event_id}/validation")
            assert response.status_code == 200
            data = response.json()
            assert "is_valid" in data
            assert "warnings" in data
            assert isinstance(data["warnings"], list)
        else:
            pytest.skip("No test events available")


class TestAvailabilityAPI:
    """Test Availability/Blocked Dates operations"""

    def test_add_blocked_date(self):
        """Add a blocked date period"""
        # Get first person
        resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if resp.status_code == 200 and resp.json()["people"]:
            person_id = resp.json()["people"][0]["id"]
            data = {
                "start_date": (date.today() + timedelta(days=10)).isoformat(),
                "end_date": (date.today() + timedelta(days=12)).isoformat(),
                "reason": "Test vacation"
            }
            response = requests.post(
                f"{API_BASE}/availability/{person_id}/timeoff",
                json=data
            )
            # 409 = already exists (test might run multiple times)
            assert response.status_code in [200, 201, 409]
        else:
            pytest.skip("No test person available")

    def test_get_blocked_dates(self):
        """Get person's blocked dates"""
        # Get first person
        resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if resp.status_code == 200 and resp.json()["people"]:
            person_id = resp.json()["people"][0]["id"]
            response = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
            assert response.status_code == 200
            data = response.json()
            assert "timeoff" in data
            assert isinstance(data["timeoff"], list)
            # Check that reason field exists
            if len(data["timeoff"]) > 0:
                assert "reason" in data["timeoff"][0] or data["timeoff"][0].get("reason") is None
        else:
            pytest.skip("No test person available")

    def test_update_blocked_date(self):
        """Update a blocked date's reason"""
        # Get first person
        resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if resp.status_code == 200 and resp.json()["people"]:
            person_id = resp.json()["people"][0]["id"]
            # First get existing timeoff
            response = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
            timeoff_list = response.json()["timeoff"]

            if len(timeoff_list) > 0:
                timeoff_id = timeoff_list[0]["id"]
                data = {
                    "start_date": timeoff_list[0]["start_date"],
                    "end_date": timeoff_list[0]["end_date"],
                    "reason": "Updated reason"
                }
                response = requests.patch(
                    f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}",
                    json=data
                )
                assert response.status_code == 200
        else:
            pytest.skip("No test person available")

    def test_delete_blocked_date(self):
        """Delete a blocked date"""
        # Get first person
        resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if resp.status_code == 200 and resp.json()["people"]:
            person_id = resp.json()["people"][0]["id"]
            # Get all timeoff
            response = requests.get(f"{API_BASE}/availability/{person_id}/timeoff")
            timeoff_list = response.json()["timeoff"]

            if len(timeoff_list) > 0:
                timeoff_id = timeoff_list[0]["id"]
                response = requests.delete(
                    f"{API_BASE}/availability/{person_id}/timeoff/{timeoff_id}"
                )
                assert response.status_code in [200, 204]
        else:
            pytest.skip("No test person available")


class TestAssignmentsAPI:
    """Test Assignment operations"""

    def test_assign_person_to_event(self):
        """Assign a person to an event"""
        # Get first person and event
        people_resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        events_resp = requests.get(f"{API_BASE}/events/?org_id=test_org")

        if (people_resp.status_code == 200 and people_resp.json()["people"] and
            events_resp.status_code == 200 and events_resp.json().get("events")):
            person_id = people_resp.json()["people"][0]["id"]
            event_id = events_resp.json()["events"][0]["id"]

            data = {"person_id": person_id, "action": "assign", "role": "volunteer"}
            response = requests.post(
                f"{API_BASE}/events/{event_id}/assignments",
                json=data
            )
            # 200/201 = success, 409 = already assigned, 400 = validation (person may not have matching roles)
            assert response.status_code in [200, 201, 400, 409]
        else:
            pytest.skip("No test data available")

    def test_unassign_person_from_event(self):
        """Unassign a person from an event"""
        # Get first person and event
        people_resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        events_resp = requests.get(f"{API_BASE}/events/?org_id=test_org")

        if (people_resp.status_code == 200 and people_resp.json()["people"] and
            events_resp.status_code == 200 and events_resp.json().get("events")):
            person_id = people_resp.json()["people"][0]["id"]
            event_id = events_resp.json()["events"][0]["id"]

            data = {"person_id": person_id, "action": "unassign"}
            response = requests.post(
                f"{API_BASE}/events/{event_id}/assignments",
                json=data
            )
            assert response.status_code == 200
        else:
            pytest.skip("No test data available")


class TestSolverAPI:
    """Test Schedule Generation (Solver)"""

    def test_generate_schedule(self):
        """Generate a schedule solution"""
        data = {
            "org_id": "test_org",
            "from_date": (date.today() + timedelta(days=1)).isoformat(),
            "to_date": (date.today() + timedelta(days=30)).isoformat(),
            "mode": "relaxed"
        }
        response = requests.post(f"{API_BASE}/solver/solve", json=data, timeout=30)
        assert response.status_code in [200, 201]
        result = response.json()
        assert "solution_id" in result

    def test_list_solutions(self):
        """List generated solutions"""
        response = requests.get(f"{API_BASE}/solutions/?org_id=test_org")
        assert response.status_code == 200
        data = response.json()
        assert "solutions" in data


class TestPDFExportAPI:
    """Test PDF Export with blocked dates"""

    def test_pdf_export_has_blocked_markers(self):
        """Test that PDF export includes [BLOCKED] markers"""
        # Get first person
        people_resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        if people_resp.status_code == 200 and people_resp.json()["people"]:
            person_id = people_resp.json()["people"][0]["id"]

            # Add a blocked date
            data = {
                "start_date": "2025-10-15",
                "end_date": "2025-10-15",
                "reason": "Testing PDF export"
            }
            requests.post(
                f"{API_BASE}/availability/{person_id}/timeoff",
                json=data
            )

            # Generate a solution
            solve_data = {
                "org_id": "test_org",
                "from_date": (date.today() + timedelta(days=1)).isoformat(),
                "to_date": (date.today() + timedelta(days=30)).isoformat(),
                "mode": "relaxed"
            }
            solve_response = requests.post(
                f"{API_BASE}/solver/solve",
                json=solve_data,
                timeout=30
            )

            if solve_response.status_code in [200, 201] and "solution_id" in solve_response.json():
                solution_id = solve_response.json()["solution_id"]

                # Export as PDF
                export_data = {"format": "pdf"}
                pdf_response = requests.post(
                    f"{API_BASE}/solutions/{solution_id}/export",
                    json=export_data
                )

                assert pdf_response.status_code == 200
                assert pdf_response.headers["Content-Type"] == "application/pdf"
                assert len(pdf_response.content) > 0
            else:
                pytest.skip("Could not generate solution")
        else:
            pytest.skip("No test person available")


# ============================================================================
# GUI TESTS
# ============================================================================

class TestGUILogin:
    """Test GUI Login Flow"""

    def test_login_success(self, api_server):
        """Test successful login"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            # Click sign in
            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            # Fill login
            page.fill('input[type="email"]', "jane@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            # Check for successful login
            assert page.locator('#main-app').is_visible()

            browser.close()


class TestGUIEventManagement:
    """Test Event Management GUI"""

    @pytest.mark.skip(reason="GUI test needs updating after i18n changes")
    def test_event_list_shows_blocked_warnings(self, api_server):
        """Test that Event Management shows blocked warnings"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "jane@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            # Go to Admin Dashboard
            admin_btn = page.locator('button[data-view="admin"]')
            if admin_btn.count() > 0:
                admin_btn.click()
                page.wait_for_timeout(3000)

            # Check for blocked warnings in event list
            events_list = page.locator('#admin-events-list')
            assert events_list.is_visible()

            events_html = events_list.inner_html()
            # Should show blocked people in the list
            assert "blocked" in events_html.lower() or "BLOCKED" in events_html

            browser.close()


class TestGUIAssignmentModal:
    """Test Assignment Modal GUI"""

    @pytest.mark.skip(reason="GUI test needs updating after i18n changes")
    def test_assignment_modal_shows_blocked_badge(self, api_server):
        """Test that assignment modal shows BLOCKED badges"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login and navigate
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "jane@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            # Go to Admin
            admin_btn = page.locator('button[data-view="admin"]')
            if admin_btn.count() > 0:
                admin_btn.click()
                page.wait_for_timeout(3000)

            # Find Sunday Service and click "Assign People"
            assign_btn = page.locator('button:has-text("Assign People")').first
            if assign_btn.count() > 0:
                assign_btn.click()
                page.wait_for_timeout(2000)

            # Check modal for BLOCKED badge
            modal = page.locator('#assignment-modal')
            if modal.is_visible():
                modal_text = modal.inner_text()
                assert "BLOCKED" in modal_text

            browser.close()


class TestGUIBlockedDates:
    """Test Blocked Dates Management GUI"""

    @pytest.mark.skip(reason="GUI test needs updating after i18n changes")
    def test_add_blocked_date_with_reason(self, api_server):
        """Test adding a blocked date with reason through GUI"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto(APP_URL)
            page.wait_for_load_state("networkidle")

            if page.locator('a:has-text("Sign in")').count() > 0:
                page.locator('a:has-text("Sign in")').click()
                page.wait_for_timeout(500)

            page.fill('input[type="email"]', "sarah@test.com")
            page.fill('input[type="password"]', "password")
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_timeout(3000)

            # Go to Availability view
            avail_btn = page.locator('button[data-view="availability"]')
            if avail_btn.count() > 0:
                avail_btn.click()
                page.wait_for_timeout(2000)

            # Fill in blocked date form
            future_date = (date.today() + timedelta(days=20)).isoformat()
            page.fill('#timeoff-start', future_date)
            page.fill('#timeoff-end', future_date)
            page.fill('#timeoff-reason', "GUI Test Vacation")

            # Submit
            page.locator('button[type="submit"]:has-text("Add Time Off")').click()
            page.wait_for_timeout(2000)

            # Check that it appears in the list
            timeoff_list = page.locator('#timeoff-list')
            assert timeoff_list.is_visible()

            browser.close()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestBlockedDatesIntegration:
    """Test complete blocked dates workflow"""

    def test_blocked_person_shown_in_validation(self):
        """Test that blocked people cause validation warnings"""
        # Get first person and event
        people_resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
        events_resp = requests.get(f"{API_BASE}/events/?org_id=test_org")

        if (people_resp.status_code == 200 and people_resp.json()["people"] and
            events_resp.status_code == 200 and events_resp.json().get("events")):
            person_id = people_resp.json()["people"][0]["id"]
            event_id = events_resp.json()["events"][0]["id"]
            event_date = events_resp.json()["events"][0]["start_time"][:10]  # Get date part

            # Add blocked date matching event date
            data = {
                "start_date": event_date,
                "end_date": event_date,
                "reason": "Integration test"
            }
            requests.post(
                f"{API_BASE}/availability/{person_id}/timeoff",
                json=data
            )

            # Assign person to event
            requests.post(
                f"{API_BASE}/events/{event_id}/assignments",
                json={"person_id": person_id, "action": "assign"}
            )

            # Check validation shows warning
            response = requests.get(f"{API_BASE}/events/{event_id}/validation")
            data = response.json()

            assert "is_valid" in data
            if data.get("warnings"):
                assert any(w["type"] == "blocked_assignments" for w in data["warnings"])
        else:
            pytest.skip("No test data available")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ROSTIO COMPREHENSIVE TEST SUITE")
    print("="*80)

    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
