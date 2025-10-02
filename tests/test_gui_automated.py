#!/usr/bin/env python3
"""
Automated GUI/Frontend Test Suite

Tests that the frontend files load correctly and JavaScript API calls work.
This version works with fresh or existing databases.
"""

import httpx
import re

API_BASE = "http://localhost:8000"


def test_frontend_loads():
    """Test that frontend HTML loads."""
    print("\n🧪 Testing frontend loads...", end=" ")

    client = httpx.Client()
    response = client.get(f"{API_BASE}/frontend/index.html")

    assert response.status_code == 200, f"Frontend not accessible: {response.status_code}"
    assert "Welcome to Roster" in response.text, "Welcome message not found"
    assert "Sign in" in response.text, "Login link not found"
    assert "Get Started" in response.text, "Get Started button not found"

    print("✅ PASS")


def test_css_loads():
    """Test that CSS file loads."""
    print("🧪 Testing CSS loads...", end=" ")

    client = httpx.Client()
    response = client.get(f"{API_BASE}/frontend/css/styles.css")

    assert response.status_code == 200, f"CSS not accessible: {response.status_code}"
    assert ".welcome-card" in response.text, "CSS styles not found"

    print("✅ PASS")


def test_javascript_loads():
    """Test that JavaScript file loads."""
    print("🧪 Testing JavaScript loads...", end=" ")

    client = httpx.Client()
    response = client.get(f"{API_BASE}/frontend/js/app-user.js")

    assert response.status_code == 200, f"JavaScript not accessible: {response.status_code}"
    assert "API_BASE_URL" in response.text, "API base URL not found"
    assert "handleLogin" in response.text, "Login function not found"
    assert "createProfile" in response.text, "Profile creation function not found"
    assert "generateSchedule" in response.text, "Admin function not found"

    print("✅ PASS")


def test_all_html_pages():
    """Test that all HTML pages are accessible."""
    print("🧪 Testing all HTML pages...", end=" ")

    client = httpx.Client()

    pages = [
        "/frontend/index.html",
        "/frontend/index-admin.html",
    ]

    for page in pages:
        response = client.get(f"{API_BASE}{page}")
        assert response.status_code == 200, f"{page} not accessible"

    print("✅ PASS")


def test_api_endpoints_accessible():
    """Test that all main API endpoints are accessible."""
    print("🧪 Testing API endpoints accessible...", end=" ")

    client = httpx.Client()

    # These should all return 200 (even if empty results)
    endpoints = [
        "/organizations/",
        "/people/",
        "/events/",
        "/solutions/",
        "/health",
    ]

    for endpoint in endpoints:
        response = client.get(f"{API_BASE}{endpoint}")
        assert response.status_code == 200, f"{endpoint} not accessible: {response.status_code}"

    print("✅ PASS")


def test_auth_endpoints_exist():
    """Test that auth endpoints exist (don't test with real data)."""
    print("🧪 Testing auth endpoints exist...", end=" ")

    client = httpx.Client()

    # Test with invalid data to check endpoints exist
    response = client.post(f"{API_BASE}/auth/login", json={
        "email": "invalid@test.com",
        "password": "invalid"
    })
    # Should return 401 (unauthorized) not 404 (not found)
    assert response.status_code in [401, 422], f"Login endpoint issue: {response.status_code}"

    print("✅ PASS")


def test_frontend_integration():
    """Test frontend can call API endpoints."""
    print("🧪 Testing frontend-API integration...", end=" ")

    client = httpx.Client()

    # Simulate what frontend does on load
    # 1. Load organizations list
    response = client.get(f"{API_BASE}/organizations/")
    assert response.status_code == 200
    orgs = response.json()
    assert "organizations" in orgs
    assert "total" in orgs

    # 2. Check health
    response = client.get(f"{API_BASE}/health")
    assert response.status_code == 200
    health = response.json()
    assert health["status"] == "healthy"

    print("✅ PASS")


def main():
    """Run all GUI tests."""
    print("\n" + "="*70)
    print("AUTOMATED GUI TEST SUITE")
    print("="*70)
    print("Testing frontend files and API integration...")

    passed = 0
    failed = 0

    tests = [
        test_frontend_loads,
        test_css_loads,
        test_javascript_loads,
        test_all_html_pages,
        test_api_endpoints_accessible,
        test_auth_endpoints_exist,
        test_frontend_integration,
    ]

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print("="*70)
    print("\nNote: These tests verify the frontend loads and can communicate")
    print("with the API. Full integration tests are in test_api_complete.py")
    print("="*70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
