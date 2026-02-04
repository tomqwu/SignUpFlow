"""
Unit tests for EmailService.

Tests the email sending functionality with mocked SMTP/SendGrid.

Coverage target: >90% for api/services/email_service.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from api.services.email_service import EmailService
from api.models import NotificationType


class TestEmailService:
    """Test suite for EmailService class."""

    @patch('api.services.email_service.smtplib.SMTP')
    def test_send_email_with_template_renders_correctly(self, mock_smtp):
        """Test that email with template renders correctly."""
        # Arrange
        service = EmailService()
        recipient_email = "volunteer@example.com"
        template_data = {
            "volunteer_name": "John Doe",
            "event_title": "Sunday Service",
            "event_date": "2025-11-01",
            "event_time": "10:00 AM",
            "role": "Usher",
            "schedule_link": "https://app.com/schedule"
        }

        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Act (force email enabled for unit test)
        with patch.dict('os.environ', {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()
            result = service.send_email(
                to_email=recipient_email,
                subject="New Assignment: Sunday Service",
                template_name="assignment",
                template_data=template_data,
                language="en"
            )

        # Assert
        assert result is not None  # Should return message ID
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('api.services.email_service.smtplib.SMTP')
    def test_send_email_with_spanish_language(self, mock_smtp):
        """Test that Spanish language template is used."""
        # Arrange
        service = EmailService()
        recipient_email = "voluntario@example.com"
        template_data = {"event_title": "Servicio Dominical"}

        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Act
        with patch.dict('os.environ', {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()
            service.send_email(
                to_email=recipient_email,
                subject="Nueva Asignación",
                template_name="assignment",
                template_data=template_data,
                language="es"
            )

        # Assert - should not raise, Spanish template should render
        mock_server.sendmail.assert_called_once()

    @patch('api.services.email_service.smtplib.SMTP')
    def test_send_email_falls_back_to_english(self, mock_smtp):
        """Test that English is used if unsupported language specified."""
        # Arrange
        service = EmailService()
        recipient_email = "volunteer@example.com"
        template_data = {"event_title": "Event"}

        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Act - use unsupported language
        with patch.dict('os.environ', {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()
            service.send_email(
                to_email=recipient_email,
                subject="Assignment",
                template_name="assignment",
                template_data=template_data,
                language="unsupported_language"
            )

        # Assert - should fall back to English and still send
        mock_server.sendmail.assert_called_once()

    @patch('api.services.email_service.smtplib.SMTP')
    @patch('api.services.email_service.time.sleep')
    def test_send_email_handles_smtp_failure(self, mock_sleep, mock_smtp):
        """Test that SMTP failure is handled gracefully."""
        # Arrange
        with patch.dict('os.environ', {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()

        # Speed up retries
        service.retry_delay = 0

        recipient_email = "volunteer@example.com"

        # Mock SMTP to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")

        # Act
        result = service.send_email(
            to_email=recipient_email,
            subject="Test",
            html_content="<p>Test</p>"
        )

        # Assert - should return None on failure
        assert result is None
        # Should have retried
        assert mock_smtp.call_count > 1

    @patch('api.services.email_service.smtplib.SMTP')
    def test_send_email_direct_html_content(self, mock_smtp):
        """Test sending email with direct HTML content (no template)."""
        # Arrange
        with patch.dict('os.environ', {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()

        recipient_email = "test@example.com"
        html_content = "<h1>Test Email</h1><p>This is a test.</p>"

        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Act
        result = service.send_email(
            to_email=recipient_email,
            subject="Test Email",
            html_content=html_content
        )

        # Assert
        assert result is not None
        mock_server.sendmail.assert_called_once()

    def test_send_email_disabled_returns_none(self):
        """Test that email sending respects EMAIL_ENABLED=false."""
        # Arrange
        service = EmailService()
        service.enabled = False

        # Act
        result = service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<p>Test</p>"
        )

        # Assert - should return None when disabled
        assert result is None


class TestEmailServiceConfiguration:
    """Test EmailService configuration and initialization."""

    def test_default_smtp_configuration(self):
        """Test that SMTP defaults are set correctly."""
        # Act
        service = EmailService()

        # Assert
        assert service.smtp_host == "sandbox.smtp.mailtrap.io"
        assert service.smtp_port == 2525
        assert service.from_email == "noreply@signupflow.io"
        assert service.from_name == "SignUpFlow"

    def test_custom_smtp_configuration(self):
        """Test that custom SMTP configuration is used."""
        # Act
        service = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="password123",
            from_email="custom@example.com",
            from_name="Custom Name"
        )

        # Assert
        assert service.smtp_host == "smtp.example.com"
        assert service.smtp_port == 587
        assert service.smtp_user == "user@example.com"
        assert service.from_email == "custom@example.com"
        assert service.from_name == "Custom Name"


# Run tests with: poetry run pytest tests/unit/test_email_service.py -v
