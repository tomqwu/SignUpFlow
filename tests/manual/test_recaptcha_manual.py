#!/usr/bin/env python3
"""Manual test for reCAPTCHA v3 implementation."""

import requests
import json

API_BASE = "http://localhost:8000"

def test_recaptcha_site_key():
    """Test that site key endpoint returns correct configuration."""
    print("\n1. Testing reCAPTCHA site key endpoint...")
    response = requests.get(f"{API_BASE}/api/auth/recaptcha-site-key")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")

    assert response.status_code == 200, "Site key endpoint should return 200"
    assert data["enabled"] == True, "reCAPTCHA should be enabled"
    assert data["site_key"] is not None, "Site key should not be None"
    print("   ✅ PASSED")

def test_password_reset_without_token():
    """Test password reset without reCAPTCHA token (should fail)."""
    print("\n2. Testing password reset WITHOUT reCAPTCHA token...")
    response = requests.post(
        f"{API_BASE}/api/auth/forgot-password",
        json={"email": "test@example.com"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    assert response.status_code == 400, "Should return 400 without reCAPTCHA token"
    assert "reCAPTCHA" in response.json()["detail"], "Error should mention reCAPTCHA"
    print("   ✅ PASSED - Correctly blocked request without token")

def test_password_reset_with_invalid_token():
    """Test password reset with invalid reCAPTCHA token (should fail)."""
    print("\n3. Testing password reset WITH INVALID reCAPTCHA token...")
    response = requests.post(
        f"{API_BASE}/api/auth/forgot-password",
        json={"email": "test@example.com"},
        headers={
            "Content-Type": "application/json",
            "X-Recaptcha-Token": "fake_invalid_token_12345"
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    assert response.status_code == 400, "Should return 400 with invalid token"
    assert "reCAPTCHA" in response.json()["detail"], "Error should mention reCAPTCHA"
    print("   ✅ PASSED - Correctly rejected invalid token")

def test_org_creation_without_token():
    """Test organization creation without reCAPTCHA token (should fail)."""
    print("\n4. Testing organization creation WITHOUT reCAPTCHA token...")
    response = requests.post(
        f"{API_BASE}/api/organizations/",
        json={
            "id": "test-org-recaptcha",
            "name": "Test Org",
            "config": {}
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Should fail with 400 (reCAPTCHA) or 429 (rate limit)
    assert response.status_code in [400, 429], "Should return 400 or 429"
    print("   ✅ PASSED - Request blocked by security measures")

if __name__ == "__main__":
    print("=" * 60)
    print("reCAPTCHA v3 Implementation Test Suite")
    print("=" * 60)

    try:
        test_recaptcha_site_key()
        test_password_reset_without_token()
        test_password_reset_with_invalid_token()
        test_org_creation_without_token()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNOTE: These tests verify that reCAPTCHA protection is active.")
        print("To test with REAL tokens, you need to:")
        print("1. Open the frontend in a browser")
        print("2. Use the actual forms (password reset, org creation)")
        print("3. The frontend will generate valid reCAPTCHA v3 tokens")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
