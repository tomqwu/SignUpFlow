"""Unit tests for backend i18n message helpers."""

import pytest
from fastapi import HTTPException

from api.utils.response_messages import success_response, error_response, validation_warning


class TestBackendI18n:
    """Test backend i18n helper functions."""

    def test_success_response_basic(self):
        """Test success_response creates correct structure."""
        result = success_response(
            "events.assign.success",
            {"assignment_id": "123"},
            person="John"
        )

        assert result["message_key"] == "events.assign.success"
        assert result["message_params"] == {"person": "John"}
        assert result["assignment_id"] == "123"

    def test_success_response_no_data(self):
        """Test success_response without additional data."""
        result = success_response(
            "events.assign.unassigned",
            person="Jane"
        )

        assert result["message_key"] == "events.assign.unassigned"
        assert result["message_params"] == {"person": "Jane"}
        assert "assignment_id" not in result

    def test_error_response_structure(self):
        """Test error_response creates HTTPException with correct structure."""
        with pytest.raises(HTTPException) as exc_info:
            raise error_response(
                "events.errors.person_not_found",
                status_code=404,
                person_id="123"
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["message_key"] == "events.errors.person_not_found"
        assert exc_info.value.detail["message_params"] == {"person_id": "123"}

    def test_error_response_default_status(self):
        """Test error_response uses 400 as default status code."""
        with pytest.raises(HTTPException) as exc_info:
            raise error_response("events.assign.already_assigned", person="John")

        assert exc_info.value.status_code == 400

    def test_validation_warning_structure(self):
        """Test validation_warning creates correct warning dict."""
        warning = validation_warning(
            "blocked_assignments",
            "events.validation.blocked_people_assigned",
            people="John, Jane"
        )

        assert warning["type"] == "blocked_assignments"
        assert warning["message_key"] == "events.validation.blocked_people_assigned"
        assert warning["message_params"] == {"people": "John, Jane"}

    def test_validation_warning_multiple_params(self):
        """Test validation_warning with multiple parameters."""
        warning = validation_warning(
            "insufficient_people",
            "events.validation.need_more_people",
            needed=3,
            role="usher",
            available=1
        )

        assert warning["type"] == "insufficient_people"
        assert warning["message_key"] == "events.validation.need_more_people"
        assert warning["message_params"]["needed"] == 3
        assert warning["message_params"]["role"] == "usher"
        assert warning["message_params"]["available"] == 1
