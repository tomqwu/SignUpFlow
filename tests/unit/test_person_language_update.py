"""Unit tests for person language update functionality."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

API_BASE = "http://localhost:8000/api"


class TestPersonLanguageUpdate:
    """Test updating person language field."""

    def test_update_person_language_to_chinese(self, client):
        """Test updating person language to Chinese (Simplified)."""
        # Create test organization
        org_response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_lang", "name": "Test Language Org", "config": {"roles": ["admin", "volunteer"]}}
        )
        assert org_response.status_code in [200, 201]

        # Create test person
        person_response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": "test_person_lang",
                "name": "Test Person",
                "email": "test_lang@example.com",
                "org_id": "test_org_lang",
                "roles": ["admin"],
                "timezone": "UTC",
                "language": "en"
            }
        )
        assert person_response.status_code in [200, 201], f"Failed to create person: {person_response.text}"

        # Update person language to Chinese
        response = client.put(
            f"{API_BASE}/people/test_person_lang",
            json={"language": "zh-CN"}
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["language"] == "zh-CN"
        assert data["id"] == "test_person_lang"

    def test_update_person_language_and_timezone(self, client):
        """Test updating both language and timezone together."""
        # Create test organization
        org_response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_lang2", "name": "Test Language Org 2", "config": {"roles": ["admin"]}}
        )
        assert org_response.status_code in [200, 201]

        # Create test person
        person_response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": "test_person_lang2",
                "name": "Test Person 2",
                "email": "test2_lang@example.com",
                "org_id": "test_org_lang2",
                "roles": ["admin"],
                "timezone": "UTC",
                "language": "en"
            }
        )
        assert person_response.status_code in [200, 201]

        # Update both language and timezone
        response = client.put(
            f"{API_BASE}/people/test_person_lang2",
            json={
                "language": "es",
                "timezone": "America/Mexico_City"
            }
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["language"] == "es"
        assert data["timezone"] == "America/Mexico_City"

    def test_update_person_language_multiple_times(self, client):
        """Test updating language multiple times in succession."""
        # Create test organization
        org_response = client.post(
            f"{API_BASE}/organizations/",
            json={"id": "test_org_lang3", "name": "Test Language Org 3", "config": {"roles": ["admin"]}}
        )
        assert org_response.status_code in [200, 201]

        # Create test person
        person_response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": "test_person_lang3",
                "name": "Test Person 3",
                "email": "test3_lang@example.com",
                "org_id": "test_org_lang3",
                "roles": ["admin"],
                "timezone": "UTC",
                "language": "en"
            }
        )
        assert person_response.status_code in [200, 201]

        # Test multiple language changes
        languages = ["zh-CN", "es", "pt", "fr", "en"]

        for lang in languages:
            response = client.put(
                f"{API_BASE}/people/test_person_lang3",
                json={"language": lang}
            )

            print(f"Language {lang} - Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response body: {response.text}")

            assert response.status_code == 200, \
                f"Failed to update to {lang}: {response.status_code} - {response.text}"

            data = response.json()
            assert data["language"] == lang, f"Expected language {lang}, got {data['language']}"

    def test_update_person_language_invalid_person(self, client):
        """Test updating language for non-existent person returns 404."""
        response = client.put(
            f"{API_BASE}/people/nonexistent_person",
            json={"language": "zh-CN"}
        )

        assert response.status_code == 404
