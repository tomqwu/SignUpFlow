"""
Email service for sending transactional emails via SMTP.

Uses Mailtrap for testing and can be configured for production SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger("email_service")


class EmailService:
    """Email service for sending transactional emails."""

    def __init__(
        self,
        smtp_host: str = "sandbox.smtp.mailtrap.io",
        smtp_port: int = 2525,
        smtp_user: str = "a336c0c4dec825",
        smtp_password: str = "bc41cad242b7fe",
        from_email: str = "noreply@signupflow.io",
        from_name: str = "SignUpFlow"
    ):
        """
        Initialize email service.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            from_name: Sender display name
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text email body (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add plain text part
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                message.attach(part1)

            # Add HTML part
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_invitation_email(
        self,
        to_email: str,
        admin_name: str,
        org_name: str,
        invitation_token: str,
        app_url: str = "http://localhost:8000"
    ) -> bool:
        """
        Send invitation email to new user.

        Args:
            to_email: Recipient email address
            admin_name: Name of admin sending invitation
            org_name: Organization name
            invitation_token: Invitation token for acceptance link
            app_url: Base application URL

        Returns:
            True if email sent successfully, False otherwise
        """
        invitation_url = f"{app_url}/accept-invitation?token={invitation_token}"

        subject = f"You're invited to join {org_name} on SignUpFlow"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>You're Invited!</h1>
            </div>
            <div class="content">
                <p>Hi,</p>

                <p>{admin_name} has invited you to join <strong>{org_name}</strong> on SignUpFlow!</p>

                <p>SignUpFlow makes volunteer scheduling simple with AI-powered schedule generation.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_url}" class="button">Accept Invitation</a>
                </div>

                <p>This invitation expires in 7 days.</p>

                <p>Questions? Reply to this email and we'll help you get started.</p>

                <p>Best,<br>
                The SignUpFlow Team</p>
            </div>
            <div class="footer">
                <p>SignUpFlow - Volunteer Scheduling Made Simple</p>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        You're invited to join {org_name} on SignUpFlow!

        {admin_name} has invited you to join their organization.

        SignUpFlow makes volunteer scheduling simple with AI-powered schedule generation.

        Accept your invitation: {invitation_url}

        This invitation expires in 7 days.

        Questions? Reply to this email and we'll help you get started.

        Best,
        The SignUpFlow Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)


# Global email service instance
email_service = EmailService()
