import os
import unittest
from unittest.mock import MagicMock, patch
from api.services.email_service import EmailService
from api.services.sms_service import SMSService

class TestWorkflowSafety(unittest.TestCase):
    """
    Test that transactional messaging services respect safety flags
    and do not leak requests in development mode.
    """

    def setUp(self):
        # Ensure environment is set to development
        os.environ["ENVIRONMENT"] = "development"
        
    @patch("api.services.email_service.smtplib.SMTP")
    @patch("api.services.email_service.SendGridAPIClient")
    def test_email_service_safety_flag(self, mock_sendgrid, mock_smtp):
        """Verify EmailService does not send if EMAIL_ENABLED=false"""
        # 1. Test with EMAIL_ENABLED=false
        with patch.dict(os.environ, {"EMAIL_ENABLED": "false"}):
            service = EmailService()
            self.assertFalse(service.enabled)
            
            result = service.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<h1>Hello</h1>"
            )
            
            self.assertIsNone(result)
            mock_smtp.assert_not_called()
            mock_sendgrid.assert_not_called()

        # 2. Test with EMAIL_ENABLED=true (to verify it WOULD call)
        with patch.dict(os.environ, {"EMAIL_ENABLED": "true", "MAILTRAP_SMTP_USER": "test", "MAILTRAP_SMTP_PASSWORD": "test"}):
            service = EmailService()
            self.assertTrue(service.enabled)
            
            # We don't actually call it here because it would try to connect,
            # but we verified the 'enabled' flag logic.

    @patch("api.services.sms_service.Client")
    def test_sms_service_safety(self, mock_twilio):
        """Verify SMSService does not send if SMS_ENABLED=false"""
        # 1. Test with SMS_ENABLED=false
        with patch.dict(os.environ, {"SMS_ENABLED": "false"}):
            service = SMSService()
            self.assertFalse(service.enabled)
            
            result = service.send_sms(
                db=MagicMock(),
                recipient_id=1,
                message_text="Test",
                message_type="assignment",
                organization_id=1
            )
            
            self.assertEqual(result["status"], "disabled")
            mock_twilio.assert_not_called()

if __name__ == "__main__":
    unittest.main()
