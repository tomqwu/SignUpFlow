"""
End-to-end test for organization creation matching frontend behavior.
"""
import pytest
import requests

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")


def test_create_org(app_config: AppConfig):
    """Test creating an organization exactly as the frontend does."""

    # This simulates what the frontend sends
    org_data = {
        "id": "test_e2e_org",
        "name": "Test E2E Organization",
        "region": "US",
        "config": {}
    }

    print("Testing organization creation...")
    print(f"Request data: {org_data}")

    response = requests.post(
        f"{app_config.app_url}/api/organizations/",
        json=org_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 201:
        print("✅ Organization created successfully!")
        return True
    elif response.status_code == 409:
        print("⚠️  Organization already exists (409 Conflict)")
        # Try with unique ID
        import time
        org_data["id"] = f"test_e2e_org_{int(time.time())}"
        print(f"\nRetrying with unique ID: {org_data['id']}")
        response = requests.post(
            f"{app_config.app_url}/api/organizations/",
            json=org_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            print("✅ Organization created successfully!")
            return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Details: {response.text}")
        return False

if __name__ == "__main__":
    success = test_create_org()
    exit(0 if success else 1)
