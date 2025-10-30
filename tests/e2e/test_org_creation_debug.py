"""
Debug test for organization creation to see exact error responses.
"""
import pytest
from playwright.sync_api import Page, expect, Route
import json


def test_create_organization_with_network_inspection(page: Page):
    """Test org creation and inspect all network traffic."""
    import time

    # Generate unique org name using timestamp to prevent 409 conflicts
    timestamp = int(time.time() * 1000)
    unique_org_name = f"Debug Test Org {timestamp}"
    unique_location = f"Test Location {timestamp}"

    # Track all network requests and responses
    requests = []
    responses = []

    def handle_request(request):
        if '/api/' in request.url:
            requests.append({
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data
            })

    def handle_response(response):
        if '/api/' in response.url:
            try:
                body = response.body()
                try:
                    body_json = json.loads(body.decode('utf-8'))
                except:
                    body_json = body.decode('utf-8')
            except:
                body_json = None

            responses.append({
                'url': response.url,
                'status': response.status,
                'headers': dict(response.headers),
                'body': body_json
            })

    page.on("request", handle_request)
    page.on("response", handle_response)

    # Track console messages
    console_messages = []
    page.on("console", lambda msg: console_messages.append({
        'type': msg.type,
        'text': msg.text
    }))

    # Navigate to the app
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")

    # Click "Get Started"
    page.locator('button:has-text("Get Started")').click()
    page.wait_for_timeout(500)

    # Click "Create New Organization"
    page.locator('button:has-text("Create New Organization")').click()
    page.wait_for_timeout(500)

    # Fill in form with unique names to prevent 409 conflicts
    page.locator('#new-org-name').fill(unique_org_name)
    page.locator('#new-org-region').fill(unique_location)

    # Submit
    page.locator('#create-org-section button[type="submit"]').click()

    # Wait a bit for the request to complete
    page.wait_for_timeout(3000)

    # Print all network activity
    print("\n" + "="*80)
    print("NETWORK REQUESTS:")
    print("="*80)
    for i, req in enumerate(requests):
        print(f"\n[{i+1}] {req['method']} {req['url']}")
        if req['post_data']:
            print(f"    Body: {req['post_data']}")
        print(f"    Headers: {json.dumps({k:v for k,v in req['headers'].items() if k.lower() in ['content-type', 'x-recaptcha-token', 'authorization']}, indent=2)}")

    print("\n" + "="*80)
    print("NETWORK RESPONSES:")
    print("="*80)
    for i, res in enumerate(responses):
        print(f"\n[{i+1}] {res['status']} {res['url']}")
        if res['body']:
            print(f"    Body: {json.dumps(res['body'], indent=2) if isinstance(res['body'], dict) else res['body']}")

    print("\n" + "="*80)
    print("CONSOLE MESSAGES:")
    print("="*80)
    for msg in console_messages[-10:]:  # Last 10 messages
        print(f"[{msg['type']}] {msg['text']}")

    # Check for errors
    org_creation_responses = [r for r in responses if '/api/organizations/' in r['url'] and r['url'].endswith('/')]

    if org_creation_responses:
        last_response = org_creation_responses[-1]
        print("\n" + "="*80)
        print(f"ORG CREATION RESPONSE: {last_response['status']}")
        print("="*80)
        if last_response['status'] != 201:
            print(f"❌ ERROR: Expected 201, got {last_response['status']}")
            print(f"Error body: {json.dumps(last_response['body'], indent=2) if isinstance(last_response['body'], dict) else last_response['body']}")

            # Find the matching request
            matching_req = [r for r in requests if '/api/organizations/' in r['url'] and r['url'].endswith('/')]
            if matching_req:
                print(f"\nRequest that failed:")
                print(f"  Method: {matching_req[-1]['method']}")
                print(f"  Body: {matching_req[-1]['post_data']}")
                print(f"  Headers: {json.dumps({k:v for k,v in matching_req[-1]['headers'].items() if k.lower() in ['content-type', 'x-recaptcha-token', 'authorization']}, indent=2)}")

            raise AssertionError(f"Organization creation failed with {last_response['status']}: {last_response['body']}")
        else:
            print("✅ Organization created successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
