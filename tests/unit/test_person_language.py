"""
Unit tests for Person language field
"""
import pytest
import time
from fastapi.testclient import TestClient
from api.main import app

API_BASE = "http://localhost:8000/api"


class TestPersonLanguageField:
    """Test language field in Person model"""

    def test_person_defaults_to_english(self, client):
        """New person should default to English language"""
        org_id = f"lang_test_org_{int(time.time())}"

        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Lang Test Org"}
        )

        # Create person without language specified
        response = client.post(
            f"{API_BASE}/people/",
            json={
                "id": f"test_person_lang_default_{int(time.time())}",
                "org_id": org_id,
                "name": "Test Person",
                "email": f"lang_test_{int(time.time())}@example.com"
            }
        )

        assert response.status_code in [200, 201]
        data = response.json()
        # Language defaults to 'en' if not specified
        assert data.get("language", "en") == "en"

    def test_update_person_language(self, client):
        """Person language can be updated"""
        org_id = f"lang_test_org2_{int(time.time())}"
        person_id = f"test_person_lang_update_{int(time.time())}"

        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Lang Test Org 2"}
        )

        # Create person
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": person_id,
                "org_id": org_id,
                "name": "Test Person",
                "email": f"lang_test2_{int(time.time())}@example.com"
            }
        )

        # Update language to Chinese
        response = client.put(
            f"{API_BASE}/people/{person_id}",
            json={"language": "zh-CN"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "zh-CN"

    def test_update_language_and_timezone_together(self, client):
        """Can update both language and timezone"""
        org_id = f"lang_test_org3_{int(time.time())}"
        person_id = f"test_person_lang_tz_{int(time.time())}"

        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Lang Test Org 3"}
        )

        # Create person
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": person_id,
                "org_id": org_id,
                "name": "Test Person",
                "email": f"lang_test3_{int(time.time())}@example.com"
            }
        )

        # Update both
        response = client.put(
            f"{API_BASE}/people/{person_id}",
            json={
                "language": "pt",
                "timezone": "America/Sao_Paulo"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "pt"
        assert data.get("timezone") == "America/Sao_Paulo"

    def test_language_persists_after_update(self, client):
        """Language setting persists across requests"""
        org_id = f"lang_test_org4_{int(time.time())}"
        person_id = f"test_person_lang_persist_{int(time.time())}"

        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Lang Test Org 4"}
        )

        # Create person
        client.post(
            f"{API_BASE}/people/",
            json={
                "id": person_id,
                "org_id": org_id,
                "name": "Test Person",
                "email": f"lang_test4_{int(time.time())}@example.com"
            }
        )

        # Set language
        client.put(
            f"{API_BASE}/people/{person_id}",
            json={"language": "fr"}
        )

        # Fetch person again
        response = client.get(f"{API_BASE}/people/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "fr"

    def test_language_supports_multiple_locales(self, client):
        """Test that all supported language codes work"""
        org_id = f"lang_test_org5_{int(time.time())}"

        # Create org
        client.post(
            f"{API_BASE}/organizations/",
            json={"id": org_id, "name": "Lang Test Org 5"}
        )

        # Test each language
        languages = ["en", "es", "pt", "fr", "zh-CN", "zh-TW"]

        for lang in languages:
            person_id = f"test_person_{lang.replace('-', '_')}_{int(time.time())}"

            # Create person
            client.post(
                f"{API_BASE}/people/",
                json={
                    "id": person_id,
                    "org_id": org_id,
                    "name": f"Test Person {lang}",
                    "email": f"test_{lang.replace('-', '_')}_{int(time.time())}@example.com"
                }
            )

            # Set language
            response = client.put(
                f"{API_BASE}/people/{person_id}",
                json={"language": lang}
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("language") == lang
