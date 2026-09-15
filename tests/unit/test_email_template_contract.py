"""Executable inventory and rendering contract for localized scheduling email."""

from itertools import product

import pytest

from api.services.email_service import EmailService

TEMPLATE_NAMES = ("assignment", "cancellation", "reminder", "update")
LANGUAGES = ("en", "es", "fr", "pt", "zh-CN", "zh-TW")
TEMPLATE_CASES = tuple(product(TEMPLATE_NAMES, LANGUAGES))
TEMPLATE_DATA = {
    "volunteer_name": "Template Volunteer",
    "event_title": "Template Event",
    "role": "Template Role",
    "event_datetime": "2099-01-01 10:00 UTC",
    "event_location": "Template Gym",
    "event_duration": "60 minutes",
    "additional_info": "Template details",
    "calendar_url": "https://example.test/calendar",
    "schedule_url": "https://example.test/schedule",
    "availability_url": "https://example.test/availability",
    "unsubscribe_url": "https://example.test/preferences",
    "hours_remaining": 24,
    "what_to_bring": "Template equipment",
    "new_datetime": "2099-01-02 10:00 UTC",
    "old_datetime": "2099-01-01 10:00 UTC",
    "time_changed": True,
    "new_location": "New Template Gym",
    "old_location": "Old Template Gym",
    "location_changed": True,
    "other_changes": "Template change",
    "cancellation_reason": "Template reason",
    "apology_message": "Template apology",
}


def test_email_template_inventory_is_complete(tmp_path) -> None:
    service = EmailService(capture_dir=tmp_path)

    assert set(service.template_env.list_templates()) == {
        f"{template_name}_{language}.html" for template_name, language in TEMPLATE_CASES
    }


@pytest.mark.parametrize(("template_name", "language"), TEMPLATE_CASES)
def test_localized_email_template_renders_with_matching_language(
    tmp_path, template_name: str, language: str
) -> None:
    service = EmailService(capture_dir=tmp_path)

    rendered = service._render_template(template_name, TEMPLATE_DATA, language)

    assert f'<html lang="{language}">' in rendered
    assert "Template Volunteer" in rendered
    assert "Template Event" in rendered
    assert "https://example.test/" in rendered
    assert "{{" not in rendered
    if language != "en":
        english = service._render_template(template_name, TEMPLATE_DATA, "en")
        assert rendered != english.replace('<html lang="en">', f'<html lang="{language}">')


@pytest.mark.parametrize(("template_name", "language"), TEMPLATE_CASES)
def test_notification_subject_is_localized(tmp_path, template_name: str, language: str) -> None:
    service = EmailService(capture_dir=tmp_path)

    subject = service._notification_subject(
        template_name,
        language,
        event_title="Template Event",
        hours_remaining=24,
    )

    assert "Template Event" in subject
    if language != "en":
        english = service._notification_subject(
            template_name,
            "en",
            event_title="Template Event",
            hours_remaining=24,
        )
        assert subject != english
