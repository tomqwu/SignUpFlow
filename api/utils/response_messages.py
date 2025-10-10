"""Utilities for creating i18n-compatible API responses."""

from typing import Dict, Any, Optional
from fastapi import HTTPException


def success_response(
    message_key: str,
    data: Optional[Dict[str, Any]] = None,
    **params
) -> Dict[str, Any]:
    """
    Create a success response with i18n message key.

    The frontend will translate the message_key using the user's selected language.

    Args:
        message_key: Translation key (e.g., "events.assign.success")
        data: Additional response data (optional)
        **params: Variables to interpolate in translation (e.g., person="John", event="Sunday Service")

    Returns:
        Response dict with message_key, message_params, and any additional data

    Example:
        return success_response(
            "events.assign.success",
            {"assignment_id": assignment.id},
            person=person.name,
            event=event.type
        )

        # Returns:
        # {
        #     "message_key": "events.assign.success",
        #     "message_params": {"person": "John", "event": "Sunday Service"},
        #     "assignment_id": "abc123"
        # }
    """
    response = {
        "message_key": message_key,
        "message_params": params
    }
    if data:
        response.update(data)
    return response


def error_response(
    message_key: str,
    status_code: int = 400,
    **params
) -> HTTPException:
    """
    Create an error response with i18n message key.

    The frontend will translate the message_key using the user's selected language.

    Args:
        message_key: Translation key (e.g., "events.person_not_found")
        status_code: HTTP status code (default: 400)
        **params: Variables to interpolate in translation (e.g., person_id="123")

    Returns:
        HTTPException with structured detail containing message_key and message_params

    Example:
        raise error_response(
            "events.person_not_found",
            status_code=404,
            person_id=person_id
        )

        # Raises HTTPException with detail:
        # {
        #     "message_key": "events.person_not_found",
        #     "message_params": {"person_id": "123"}
        # }
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "message_key": message_key,
            "message_params": params
        }
    )


def validation_warning(
    warning_type: str,
    message_key: str,
    **params
) -> Dict[str, Any]:
    """
    Create a validation warning with i18n message key.

    Args:
        warning_type: Type of warning (e.g., "blocked_assignments", "insufficient_people")
        message_key: Translation key (e.g., "events.validation.blocked_people_assigned")
        **params: Variables to interpolate in translation

    Returns:
        Warning dict with type, message_key, and message_params

    Example:
        warning = validation_warning(
            "blocked_assignments",
            "events.validation.blocked_people_assigned",
            people=", ".join(blocked_people)
        )

        # Returns:
        # {
        #     "type": "blocked_assignments",
        #     "message_key": "events.validation.blocked_people_assigned",
        #     "message_params": {"people": "John, Jane"}
        # }
    """
    return {
        "type": warning_type,
        "message_key": message_key,
        "message_params": params
    }
