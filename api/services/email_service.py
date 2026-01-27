"""
Email service for sending transactional emails via SMTP or SendGrid.

Supports:
- SMTP (Mailtrap for testing, any SMTP server for production)
- SendGrid API (production email delivery with tracking)
- Jinja2 template rendering with i18n support
- Retry logic with exponential backoff
- Database notification tracking
"""

import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

logger = logging.getLogger("email_service")

# Try to import SendGrid (optional dependency)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid library not available - install with: poetry add sendgrid")


class EmailService:
    """
    Email service for sending transactional emails.

    Features:
    - Dual backend: SMTP (Mailtrap/testing) or SendGrid (production)
    - Jinja2 template rendering with i18n support (6 languages)
    - Retry logic with exponential backoff
    - Database notification tracking
    - Batch email sending
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        sendgrid_api_key: Optional[str] = None,
        use_sendgrid: bool = False
    ):
        """
        Initialize email service.

        Reads configuration from environment variables if not provided:
        - MAILTRAP_SMTP_HOST (default: sandbox.smtp.mailtrap.io)
        - MAILTRAP_SMTP_PORT (default: 2525)
        - MAILTRAP_SMTP_USER
        - MAILTRAP_SMTP_PASSWORD
        - EMAIL_FROM (default: noreply@signupflow.io)
        - EMAIL_FROM_NAME (default: SignUpFlow)
        - SENDGRID_API_KEY (for production)
        - EMAIL_ENABLED (default: true)

        Args:
            smtp_host: SMTP server hostname (overrides env var)
            smtp_port: SMTP server port (overrides env var)
            smtp_user: SMTP username (overrides env var)
            smtp_password: SMTP password (overrides env var)
            from_email: Sender email address (overrides env var)
            from_name: Sender display name (overrides env var)
            sendgrid_api_key: SendGrid API key (overrides env var)
            use_sendgrid: Use SendGrid instead of SMTP (auto-detected if SENDGRID_API_KEY set)
        """
        # SMTP configuration (Mailtrap for testing)
        self.smtp_host = smtp_host or os.getenv("MAILTRAP_SMTP_HOST", "sandbox.smtp.mailtrap.io")
        self.smtp_port = smtp_port or int(os.getenv("MAILTRAP_SMTP_PORT", "2525"))
        self.smtp_user = smtp_user or os.getenv("MAILTRAP_SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("MAILTRAP_SMTP_PASSWORD", "")

        # Email sender configuration
        self.from_email = from_email or os.getenv("EMAIL_FROM", "noreply@signupflow.io")
        self.from_name = from_name or os.getenv("EMAIL_FROM_NAME", "SignUpFlow")

        # SendGrid configuration (production)
        self.sendgrid_api_key = sendgrid_api_key or os.getenv("SENDGRID_API_KEY")
        self.use_sendgrid = use_sendgrid or bool(self.sendgrid_api_key)

        # Initialize SendGrid client if available and configured
        self.sendgrid_client = None
        if self.use_sendgrid and SENDGRID_AVAILABLE and self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
            logger.info("SendGrid client initialized for production email sending")
        elif self.use_sendgrid:
            logger.warning("SendGrid requested but not available - falling back to SMTP")
            self.use_sendgrid = False

        # Email enabled flag
        # Auto-enable if explicit SMTP credentials provided (for integration tests)
        # Otherwise respect EMAIL_ENABLED environment variable (defaults to true)
        explicit_smtp_config = bool(smtp_user and smtp_password)
        env_enabled = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
        self.enabled = explicit_smtp_config or env_enabled

        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 60  # 1 minute base delay
        self.retry_backoff = 2  # Exponential backoff multiplier

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        plain_content: Optional[str] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        language: str = "en",
        notification: Optional[Any] = None,
        db: Optional[Session] = None
    ) -> Optional[str]:
        """
        Send email via SMTP or SendGrid with retry logic.

        Supports two modes:
        1. Direct HTML/plain text content
        2. Jinja2 template rendering (template_name + template_data)

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: Pre-rendered HTML content (optional if using template)
            plain_content: Plain text email body (optional)
            template_name: Jinja2 template name without extension (e.g., "assignment")
            template_data: Dictionary of template variables
            language: Email language code (en, es, pt, zh-CN, zh-TW, fr)
            notification: Optional Notification model instance for tracking
            db: Optional database session for updating notification status

        Returns:
            SendGrid message ID (str) or SMTP success marker (str) on success, None on failure

        Example (direct content):
            >>> service = EmailService()
            >>> service.send_email(
            ...     to_email="user@example.com",
            ...     subject="Welcome",
            ...     html_content="<h1>Hello!</h1>"
            ... )

        Example (template rendering):
            >>> service = EmailService()
            >>> message_id = service.send_email(
            ...     to_email="volunteer@example.com",
            ...     subject="New Assignment",
            ...     template_name="assignment",
            ...     template_data={"event_title": "Sunday Service", "role": "Greeter"},
            ...     language="en"
            ... )
        """
        if not self.enabled:
            logger.warning(f"Email sending disabled - would send to {to_email}")
            return None

        # Render template if template_name provided
        if template_name and template_data:
            try:
                html_content = self._render_template(template_name, template_data, language)
            except Exception as e:
                logger.error(f"Template rendering failed: {e}")
                if notification and db:
                    self._update_notification_status(
                        notification, "failed", db, error_message=str(e)
                    )
                return None

        # Ensure we have HTML content
        if not html_content:
            logger.error("No HTML content or template provided")
            return None

        # Send via appropriate backend with retry logic
        retry_count = 0
        last_error = None

        while retry_count <= self.max_retries:
            try:
                # Update notification status to sending
                if notification and db:
                    self._update_notification_status(notification, "sending", db)

                # Send via SendGrid or SMTP
                if self.use_sendgrid and self.sendgrid_client:
                    message_id = self._send_via_sendgrid(to_email, subject, html_content)
                else:
                    message_id = self._send_via_smtp(to_email, subject, html_content, plain_content)

                # Update notification status to sent
                if notification and db:
                    self._update_notification_status(
                        notification,
                        "sent",
                        db,
                        sendgrid_message_id=message_id
                    )

                backend = "SendGrid" if self.use_sendgrid else "SMTP"
                logger.info(f"Email sent successfully to {to_email} via {backend} (id={message_id})")
                return message_id

            except Exception as e:
                last_error = str(e)
                retry_count += 1

                logger.warning(
                    f"Email send failed (attempt {retry_count}/{self.max_retries + 1}): {last_error}"
                )

                # Update notification retry count
                if notification and db:
                    notification.retry_count = retry_count
                    db.commit()

                # If max retries reached, mark as failed
                if retry_count > self.max_retries:
                    logger.error(f"Email send failed after {self.max_retries} retries: {last_error}")
                    if notification and db:
                        self._update_notification_status(
                            notification, "failed", db, error_message=last_error
                        )
                    return None

                # Exponential backoff delay
                delay = self.retry_delay * (self.retry_backoff ** (retry_count - 1))
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

        return None

    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str) -> str:
        """
        Send email via SendGrid API.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content

        Returns:
            SendGrid message ID

        Raises:
            Exception: On SendGrid API error
        """
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        response = self.sendgrid_client.send(message)

        # Extract message ID from response headers
        message_id = response.headers.get('X-Message-Id', 'unknown')
        return message_id

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> str:
        """
        Send email via SMTP (Mailtrap or custom SMTP server).

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            plain_content: Plain text content (optional)

        Returns:
            Message identifier (timestamp-based for SMTP)

        Raises:
            Exception: On SMTP error
        """
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

        # Send email (with 5-second timeout to prevent hangs)
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=5) as server:
            # Skip TLS and login for local mock SMTP (e.g., MailHog, Mailtrap mock, or internal test mock)
            is_mock_server = self.smtp_host in ["127.0.0.1", "localhost"] and str(self.smtp_port) in ["1025", "8025"]
            
            if not is_mock_server:
                # Production/Standard SMTP
                try:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                except smtplib.SMTPNotSupportedError:
                    # Some servers might not support STARTTLS or are already secure
                    pass
            elif self.smtp_user and self.smtp_password:
                # If credentials provided for mock, try login but ignore TLS
                try: 
                    server.login(self.smtp_user, self.smtp_password)
                except Exception:
                    pass

            server.sendmail(self.from_email, to_email, message.as_string())

        # Generate pseudo message ID for SMTP (since SMTP doesn't return message IDs)
        import datetime
        message_id = f"smtp-{int(datetime.datetime.utcnow().timestamp())}"
        return message_id

    def _render_template(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Render Jinja2 email template with data.

        Args:
            template_name: Template name without extension (e.g., "assignment")
            template_data: Dictionary of template variables
            language: Language code (en, es, pt, zh-CN, zh-TW, fr)

        Returns:
            Rendered HTML content

        Raises:
            TemplateNotFound: If template file doesn't exist
            TemplateSyntaxError: If template has syntax errors
        """
        # Template naming convention: {template_name}_{language}.html
        # Example: assignment_en.html, reminder_es.html
        template_filename = f"{template_name}_{language}.html"

        try:
            template = self.template_env.get_template(template_filename)
            return template.render(**template_data)
        except Exception as e:
            # Fallback to English if language-specific template not found
            if language != "en":
                logger.warning(
                    f"Template {template_filename} not found, falling back to English"
                )
                template_filename = f"{template_name}_en.html"
                template = self.template_env.get_template(template_filename)
                return template.render(**template_data)
            raise

    def _update_notification_status(
        self,
        notification: Any,
        status: str,
        db: Session,
        sendgrid_message_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Update notification status in database.

        Args:
            notification: Notification instance
            status: New status (from NotificationStatus)
            db: Database session
            sendgrid_message_id: Optional SendGrid message ID
            error_message: Optional error message
        """
        from datetime import datetime

        notification.status = status

        if sendgrid_message_id:
            notification.sendgrid_message_id = sendgrid_message_id

        if error_message:
            notification.error_message = error_message

        if status == "sent":
            notification.sent_at = datetime.utcnow()

        db.commit()

    def send_batch_emails(
        self,
        emails: List[Dict[str, Any]],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send multiple emails in batch.

        Args:
            emails: List of email dictionaries with keys:
                - to_email: Recipient email
                - subject: Email subject
                - html_content: HTML content (optional if using template)
                - template_name: Template name (optional)
                - template_data: Template variables (optional)
                - notification: Optional Notification instance
                - language: Optional language (default: en)
            db: Optional database session

        Returns:
            Dictionary with success count, failure count, and message IDs

        Example:
            >>> service = EmailService()
            >>> results = service.send_batch_emails([
            ...     {
            ...         "to_email": "user1@example.com",
            ...         "subject": "Assignment",
            ...         "template_name": "assignment",
            ...         "template_data": {"event_title": "Event 1"},
            ...     },
            ...     {
            ...         "to_email": "user2@example.com",
            ...         "subject": "Reminder",
            ...         "template_name": "reminder",
            ...         "template_data": {"event_title": "Event 2"},
            ...     }
            ... ])
            >>> print(results["success_count"])
            2
        """
        success_count = 0
        failure_count = 0
        message_ids = []

        for email_data in emails:
            message_id = self.send_email(
                to_email=email_data["to_email"],
                subject=email_data["subject"],
                html_content=email_data.get("html_content"),
                plain_content=email_data.get("plain_content"),
                template_name=email_data.get("template_name"),
                template_data=email_data.get("template_data"),
                notification=email_data.get("notification"),
                db=db,
                language=email_data.get("language", "en")
            )

            if message_id:
                success_count += 1
                message_ids.append(message_id)
            else:
                failure_count += 1

        logger.info(
            f"Batch email send complete: {success_count} succeeded, {failure_count} failed"
        )

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "message_ids": message_ids
        }

    def get_unsubscribe_url(self, unsubscribe_token: str) -> str:
        """
        Generate unsubscribe URL for email preference management.

        Args:
            unsubscribe_token: User's unique unsubscribe token

        Returns:
            Full URL for unsubscribe page

        Example:
            >>> service = EmailService()
            >>> url = service.get_unsubscribe_url("abc123def456")
            >>> print(url)
            http://localhost:8000/unsubscribe?token=abc123def456
        """
        app_url = os.getenv("APP_URL", "http://localhost:8000")
        return f"{app_url}/unsubscribe?token={unsubscribe_token}"

    def send_assignment_email(
        self,
        volunteer_email: str,
        volunteer_name: str,
        event_title: str,
        role: str,
        event_datetime: str,
        event_location: Optional[str] = None,
        event_duration: Optional[str] = None,
        additional_info: Optional[str] = None,
        calendar_url: Optional[str] = None,
        schedule_url: Optional[str] = None,
        availability_url: Optional[str] = None,
        unsubscribe_token: Optional[str] = None,
        notification: Optional[Any] = None,
        db: Optional[Session] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Send assignment notification email to volunteer.

        Args:
            volunteer_email: Volunteer's email address
            volunteer_name: Volunteer's name
            event_title: Event title
            role: Volunteer's assigned role
            event_datetime: Event date and time (formatted string)
            event_location: Event location (optional)
            event_duration: Event duration (optional, e.g., "2 hours")
            additional_info: Additional information (optional)
            calendar_url: URL to add event to calendar (optional)
            schedule_url: URL to view full schedule (optional)
            availability_url: URL to update availability (optional)
            unsubscribe_token: User's unsubscribe token (optional)
            notification: Notification model instance for tracking (optional)
            db: Database session (optional)
            language: Email language (en, es, pt, zh-CN, zh-TW, fr)

        Returns:
            Message ID on success, None on failure

        Example:
            >>> service = EmailService()
            >>> message_id = service.send_assignment_email(
            ...     volunteer_email="volunteer@example.com",
            ...     volunteer_name="John Doe",
            ...     event_title="Sunday Service",
            ...     role="Greeter",
            ...     event_datetime="Sunday, December 25, 2025 at 10:00 AM",
            ...     event_location="Main Auditorium",
            ...     language="en"
            ... )
        """
        app_url = os.getenv("APP_URL", "http://localhost:8000")

        # Build template data
        template_data = {
            "volunteer_name": volunteer_name,
            "event_title": event_title,
            "role": role,
            "event_datetime": event_datetime,
            "event_location": event_location,
            "event_duration": event_duration,
            "additional_info": additional_info,
            "calendar_url": calendar_url or f"{app_url}/app/calendar",
            "schedule_url": schedule_url or f"{app_url}/app/schedule",
            "availability_url": availability_url or f"{app_url}/app/schedule",
            "unsubscribe_url": self.get_unsubscribe_url(unsubscribe_token) if unsubscribe_token else f"{app_url}/settings"
        }

        # Email subject
        subject = f"New Assignment: {event_title}"

        # Send email using template
        return self.send_email(
            to_email=volunteer_email,
            subject=subject,
            template_name="assignment",
            template_data=template_data,
            language=language,
            notification=notification,
            db=db
        )

    def send_reminder_email(
        self,
        volunteer_email: str,
        volunteer_name: str,
        event_title: str,
        role: str,
        event_datetime: str,
        hours_remaining: int,
        event_location: Optional[str] = None,
        event_duration: Optional[str] = None,
        what_to_bring: Optional[str] = None,
        additional_info: Optional[str] = None,
        calendar_url: Optional[str] = None,
        schedule_url: Optional[str] = None,
        unsubscribe_token: Optional[str] = None,
        notification: Optional[Any] = None,
        db: Optional[Session] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Send reminder notification email to volunteer 24 hours before event.

        Args:
            volunteer_email: Volunteer's email address
            volunteer_name: Volunteer's name
            event_title: Event title
            role: Volunteer's assigned role
            event_datetime: Event date and time (formatted string)
            hours_remaining: Hours until event (typically 24)
            event_location: Event location (optional)
            event_duration: Event duration (optional, e.g., "2 hours")
            what_to_bring: Items to bring (optional)
            additional_info: Additional information (optional)
            calendar_url: URL to add event to calendar (optional)
            schedule_url: URL to view full schedule (optional)
            unsubscribe_token: User's unsubscribe token (optional)
            notification: Notification model instance for tracking (optional)
            db: Database session (optional)
            language: Email language (en, es, pt, zh-CN, zh-TW, fr)

        Returns:
            Message ID on success, None on failure

        Example:
            >>> service = EmailService()
            >>> message_id = service.send_reminder_email(
            ...     volunteer_email="volunteer@example.com",
            ...     volunteer_name="John Doe",
            ...     event_title="Sunday Service",
            ...     role="Greeter",
            ...     event_datetime="Sunday, December 25, 2025 at 10:00 AM",
            ...     hours_remaining=24,
            ...     event_location="Main Auditorium",
            ...     language="en"
            ... )
        """
        app_url = os.getenv("APP_URL", "http://localhost:8000")

        # Build template data
        template_data = {
            "volunteer_name": volunteer_name,
            "event_title": event_title,
            "role": role,
            "event_datetime": event_datetime,
            "hours_remaining": hours_remaining,
            "event_location": event_location,
            "event_duration": event_duration,
            "what_to_bring": what_to_bring,
            "additional_info": additional_info,
            "calendar_url": calendar_url or f"{app_url}/app/calendar",
            "schedule_url": schedule_url or f"{app_url}/app/schedule",
            "unsubscribe_url": self.get_unsubscribe_url(unsubscribe_token) if unsubscribe_token else f"{app_url}/settings"
        }

        # Email subject
        subject = f"Reminder: {event_title} in {hours_remaining} hours"

        # Send email using template
        return self.send_email(
            to_email=volunteer_email,
            subject=subject,
            template_name="reminder",
            template_data=template_data,
            language=language,
            notification=notification,
            db=db
        )

    def send_update_email(
        self,
        volunteer_email: str,
        volunteer_name: str,
        event_title: str,
        role: str,
        new_datetime: str,
        old_datetime: Optional[str] = None,
        new_location: Optional[str] = None,
        old_location: Optional[str] = None,
        event_duration: Optional[str] = None,
        other_changes: Optional[str] = None,
        schedule_url: Optional[str] = None,
        unsubscribe_token: Optional[str] = None,
        notification: Optional[Any] = None,
        db: Optional[Session] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Send update notification email when event details change.

        Args:
            volunteer_email: Volunteer's email address
            volunteer_name: Volunteer's name
            event_title: Event title
            role: Volunteer's assigned role
            new_datetime: New event date and time (formatted string)
            old_datetime: Previous event date and time (optional)
            new_location: New event location (optional)
            old_location: Previous event location (optional)
            event_duration: Event duration (optional, e.g., "2 hours")
            other_changes: Description of other changes (optional)
            schedule_url: URL to view full schedule (optional)
            unsubscribe_token: User's unsubscribe token (optional)
            notification: Notification model instance for tracking (optional)
            db: Database session (optional)
            language: Email language (en, es, pt, zh-CN, zh-TW, fr)

        Returns:
            Message ID on success, None on failure

        Example:
            >>> service = EmailService()
            >>> message_id = service.send_update_email(
            ...     volunteer_email="volunteer@example.com",
            ...     volunteer_name="John Doe",
            ...     event_title="Sunday Service",
            ...     role="Greeter",
            ...     new_datetime="Sunday, December 25, 2025 at 11:00 AM",
            ...     old_datetime="Sunday, December 25, 2025 at 10:00 AM",
            ...     language="en"
            ... )
        """
        app_url = os.getenv("APP_URL", "http://localhost:8000")

        # Determine what changed
        time_changed = bool(old_datetime and old_datetime != new_datetime)
        location_changed = bool(old_location and old_location != new_location)

        # Build template data
        template_data = {
            "volunteer_name": volunteer_name,
            "event_title": event_title,
            "role": role,
            "new_datetime": new_datetime,
            "old_datetime": old_datetime,
            "time_changed": time_changed,
            "new_location": new_location,
            "old_location": old_location,
            "location_changed": location_changed,
            "event_duration": event_duration,
            "other_changes": other_changes,
            "schedule_url": schedule_url or f"{app_url}/app/schedule",
            "unsubscribe_url": self.get_unsubscribe_url(unsubscribe_token) if unsubscribe_token else f"{app_url}/settings"
        }

        # Email subject
        subject = f"Schedule Update: {event_title}"

        # Send email using template
        return self.send_email(
            to_email=volunteer_email,
            subject=subject,
            template_name="update",
            template_data=template_data,
            language=language,
            notification=notification,
            db=db
        )

    def send_cancellation_email(
        self,
        volunteer_email: str,
        volunteer_name: str,
        event_title: str,
        role: str,
        event_datetime: str,
        event_location: Optional[str] = None,
        cancellation_reason: Optional[str] = None,
        apology_message: Optional[str] = None,
        schedule_url: Optional[str] = None,
        unsubscribe_token: Optional[str] = None,
        notification: Optional[Any] = None,
        db: Optional[Session] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Send cancellation notification email when event is cancelled.

        Args:
            volunteer_email: Volunteer's email address
            volunteer_name: Volunteer's name
            event_title: Event title
            role: Volunteer's assigned role
            event_datetime: Event date and time (formatted string)
            event_location: Event location (optional)
            cancellation_reason: Reason for cancellation (optional)
            apology_message: Apology message (optional)
            schedule_url: URL to view full schedule (optional)
            unsubscribe_token: User's unsubscribe token (optional)
            notification: Notification model instance for tracking (optional)
            db: Database session (optional)
            language: Email language (en, es, pt, zh-CN, zh-TW, fr)

        Returns:
            Message ID on success, None on failure

        Example:
            >>> service = EmailService()
            >>> message_id = service.send_cancellation_email(
            ...     volunteer_email="volunteer@example.com",
            ...     volunteer_name="John Doe",
            ...     event_title="Sunday Service",
            ...     role="Greeter",
            ...     event_datetime="Sunday, December 25, 2025 at 10:00 AM",
            ...     cancellation_reason="Inclement weather",
            ...     language="en"
            ... )
        """
        app_url = os.getenv("APP_URL", "http://localhost:8000")

        # Build template data
        template_data = {
            "volunteer_name": volunteer_name,
            "event_title": event_title,
            "role": role,
            "event_datetime": event_datetime,
            "event_location": event_location,
            "cancellation_reason": cancellation_reason,
            "apology_message": apology_message or "We apologize for any inconvenience this may cause.",
            "schedule_url": schedule_url or f"{app_url}/app/schedule",
            "unsubscribe_url": self.get_unsubscribe_url(unsubscribe_token) if unsubscribe_token else f"{app_url}/settings"
        }

        # Email subject
        subject = f"Event Cancelled: {event_title}"

        # Send email using template
        return self.send_email(
            to_email=volunteer_email,
            subject=subject,
            template_name="cancellation",
            template_data=template_data,
            language=language,
            notification=notification,
            db=db
        )

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
