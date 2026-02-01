"""
SMS Service for Twilio integration and message handling.

Provides methods for:
- Sending SMS messages (individual and broadcast)
- Phone number verification
- Incoming reply processing
- Message composition and templating
"""

import os
import re
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from jinja2 import Template

from api.models import (
    SmsMessage,
    SmsPreference,
    SmsTemplate,
    SmsVerificationCode,
    SmsReply,
    SmsUsage,
    Person,
    Event,
    Assignment,
)
from api.utils.sms_rate_limiter import SmsRateLimiter
from api.utils.quiet_hours import QuietHours
from api.utils.cost_tracker import CostTracker


class SMSService:
    """Service class for SMS operations using Twilio API."""

    def __init__(self):
        """Initialize Twilio client with credentials from environment."""
        self.enabled = os.getenv("SMS_ENABLED", "false").lower() == "true"
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_phone = os.getenv("TWILIO_PHONE_NUMBER")

        if self.enabled and not all([self.account_sid, self.auth_token, self.from_phone]):
            raise ValueError(
                "Missing Twilio credentials. Please set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in environment."
            )

        if self.enabled:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None

        # Initialize utility classes
        self.rate_limiter = SmsRateLimiter()
        self.quiet_hours = QuietHours()
        self.cost_tracker = CostTracker()

    def send_sms(
        self,
        db: Session,
        recipient_id: int,
        message_text: str,
        message_type: str,
        organization_id: int,
        event_id: Optional[int] = None,
        template_id: Optional[int] = None,
        is_urgent: bool = False,
    ) -> Dict[str, Any]:
        """
        Send SMS message to single recipient.
        """
        if not self.enabled:
            import logging
            logging.getLogger("sms_service").warning(f"SMS sending disabled - would send to {recipient_id}")
            return {"status": "disabled", "message": "SMS sending disabled"}

        # 1. Get recipient SMS preferences
        sms_pref = (
            db.query(SmsPreference)
            .filter(SmsPreference.person_id == recipient_id)
            .first()
        )

        if not sms_pref:
            raise ValueError(f"No SMS preferences found for person {recipient_id}")

        # 2. Validate phone verified and not opted out
        if not sms_pref.verified:
            raise ValueError("Phone number not verified")

        if sms_pref.opt_out_date:
            raise ValueError("Recipient has opted out of SMS notifications")

        # 3. Check rate limits (unless is_urgent)
        allowed, remaining = self.rate_limiter.check_rate_limit(
            recipient_id, is_urgent
        )
        if not allowed:
            raise ValueError(
                "Daily SMS rate limit exceeded (3 messages per day). "
                "Limit resets at midnight."
            )

        # 4. Check quiet hours (unless is_urgent)
        is_quiet, reason = self.quiet_hours.is_quiet_hours(
            sms_pref.timezone, is_urgent
        )
        if is_quiet:
            raise ValueError(f"Cannot send SMS during quiet hours: {reason}")

        # 5. Calculate cost
        cost_cents = self.cost_tracker.calculate_cost(message_text)

        # 6. Send via Twilio API
        try:
            twilio_message = self.client.messages.create(
                body=message_text,
                from_=self.from_phone,
                to=sms_pref.phone_number,
            )

            # 7. Log to sms_messages table
            sms_message = SmsMessage(
                organization_id=organization_id,
                recipient_id=recipient_id,
                phone_number=sms_pref.phone_number,
                message_text=message_text,
                message_type=message_type,
                event_id=event_id,
                template_id=template_id,
                status="sent",
                twilio_message_sid=twilio_message.sid,
                cost_cents=cost_cents,
                is_urgent=is_urgent,
                sent_at=datetime.utcnow(),
            )
            db.add(sms_message)

            # 8. Increment rate limiter
            self.rate_limiter.increment_count(recipient_id, is_urgent)

            # 9. Track usage and cost
            self.cost_tracker.track_usage(
                db, organization_id, message_type, cost_cents
            )

            db.commit()

            return {
                "message_id": sms_message.id,
                "status": "sent",
                "twilio_message_sid": twilio_message.sid,
                "phone_number": sms_pref.phone_number,
                "cost_cents": cost_cents,
                "remaining_daily": remaining,
            }

        except TwilioRestException as e:
            # Log failed message
            sms_message = SmsMessage(
                organization_id=organization_id,
                recipient_id=recipient_id,
                phone_number=sms_pref.phone_number,
                message_text=message_text,
                message_type=message_type,
                event_id=event_id,
                template_id=template_id,
                status="failed",
                error_message=str(e),
                cost_cents=0,
                is_urgent=is_urgent,
                failed_at=datetime.utcnow(),
            )
            db.add(sms_message)
            db.commit()

            raise TwilioRestException(
                status=e.status, uri=e.uri, msg=f"Twilio API error: {e.msg}"
            )

    def send_broadcast(
        self,
        db: Session,
        recipient_ids: List[int],
        message_text: str,
        organization_id: int,
        is_urgent: bool = False,
        bypass_quiet_hours: bool = False,
    ) -> Dict[str, Any]:
        """
        Send same message to multiple recipients (broadcast).

        Args:
            db: Database session
            recipient_ids: List of person IDs to send to
            message_text: Broadcast message content
            organization_id: Organization ID
            is_urgent: Whether to bypass rate limits
            bypass_quiet_hours: Whether to send regardless of quiet hours

        Returns:
            Dictionary with broadcast_id, total_recipients, queued_count, skipped_count,
            skipped_reasons, estimated_cost_cents

        Raises:
            ValueError: If recipient_ids empty or exceeds 200
        """
        # 1. Validate recipient list (max 200 for Twilio rate limits)
        if not recipient_ids:
            raise ValueError("recipient_ids cannot be empty")

        if len(recipient_ids) > 200:
            raise ValueError(
                f"Too many recipients ({len(recipient_ids)}). Maximum 200 per broadcast."
            )

        # 2. Initialize tracking variables
        queued_count = 0
        skipped_count = 0
        skipped_reasons = []
        total_cost_cents = 0

        # Calculate cost per message
        cost_per_message = self.cost_tracker.calculate_cost(message_text)

        # 3. Process each recipient
        for person_id in recipient_ids:
            try:
                # Get SMS preferences
                sms_pref = (
                    db.query(SmsPreference)
                    .filter(SmsPreference.person_id == person_id)
                    .first()
                )

                # Skip if no preferences
                if not sms_pref:
                    skipped_count += 1
                    skipped_reasons.append(
                        f"Person {person_id}: No SMS preferences found"
                    )
                    continue

                # Skip if not verified
                if not sms_pref.verified:
                    skipped_count += 1
                    skipped_reasons.append(
                        f"Person {person_id}: Phone not verified"
                    )
                    continue

                # Skip if opted out
                if sms_pref.opt_out_date:
                    skipped_count += 1
                    skipped_reasons.append(f"Person {person_id}: Opted out")
                    continue

                # Check rate limits (unless urgent)
                allowed, remaining = self.rate_limiter.check_rate_limit(
                    person_id, is_urgent
                )
                if not allowed:
                    skipped_count += 1
                    skipped_reasons.append(
                        f"Person {person_id}: Rate limit exceeded"
                    )
                    continue

                # Check quiet hours (unless bypass or urgent)
                if not bypass_quiet_hours:
                    is_quiet, reason = self.quiet_hours.is_quiet_hours(
                        sms_pref.timezone, is_urgent
                    )
                    if is_quiet:
                        skipped_count += 1
                        skipped_reasons.append(f"Person {person_id}: {reason}")
                        continue

                # Send SMS (MVP: synchronous, Phase 3: Celery queue)
                self.send_sms(
                    db=db,
                    recipient_id=person_id,
                    message_text=message_text,
                    message_type="broadcast",
                    organization_id=organization_id,
                    is_urgent=is_urgent,
                )

                queued_count += 1
                total_cost_cents += cost_per_message

            except Exception as e:
                skipped_count += 1
                skipped_reasons.append(f"Person {person_id}: {str(e)}")

        # 4. Return broadcast summary
        return {
            "total_recipients": len(recipient_ids),
            "queued_count": queued_count,
            "skipped_count": skipped_count,
            "skipped_reasons": skipped_reasons[:10],  # Limit to first 10
            "estimated_cost_cents": total_cost_cents,
            "message": f"Broadcast sent to {queued_count}/{len(recipient_ids)} recipients",
        }

    def verify_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Verify phone number format and deliverability using Twilio Lookup API.

        Args:
            phone_number: Phone number to verify (E.164 format)

        Returns:
            Dictionary with valid (bool), carrier_type ('mobile' or 'landline'),
            formatted_number, deliverable (bool)

        Raises:
            ValueError: If phone number format invalid
        """
        # 1. Validate E.164 format regex
        if not self.validate_phone_format(phone_number):
            raise ValueError(
                f"Invalid phone number format. Must be E.164 format (e.g., +12345678900): {phone_number}"
            )

        # 2. Call Twilio Lookup API
        try:
            phone_info = self.client.lookups.v1.phone_numbers(phone_number).fetch(
                type=["carrier"]
            )

            # 3. Check carrier type (mobile vs landline)
            carrier_type = phone_info.carrier.get("type", "unknown")
            deliverable = carrier_type in ["mobile", "voip"]  # SMS-capable

            return {
                "valid": True,
                "carrier_type": carrier_type,
                "formatted_number": phone_info.phone_number,
                "deliverable": deliverable,
                "country_code": phone_info.country_code,
            }

        except TwilioRestException as e:
            # Phone number not found or invalid
            if e.status == 404:
                return {
                    "valid": False,
                    "carrier_type": "unknown",
                    "formatted_number": phone_number,
                    "deliverable": False,
                    "error": "Phone number not found",
                }
            raise

    def generate_verification_code(
        self, db: Session, person_id: int, phone_number: str
    ) -> int:
        """
        Generate 6-digit verification code and send via SMS.

        Args:
            db: Database session
            person_id: Person ID requesting verification
            phone_number: Phone number to verify

        Returns:
            Generated 6-digit verification code (100000-999999)

        Raises:
            TwilioRestException: If SMS sending fails
        """
        # 1. Generate random 6-digit code
        code = random.randint(100000, 999999)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # 2. Delete any existing verification codes for this person
        db.query(SmsVerificationCode).filter(
            SmsVerificationCode.person_id == person_id
        ).delete()

        # 3. Create new verification code record
        verification = SmsVerificationCode(
            person_id=person_id,
            phone_number=phone_number,
            verification_code=code,
            attempts=0,
            expires_at=expires_at,
        )
        db.add(verification)
        db.commit()

        # 4. Send code via SMS
        message_text = (
            f"Your SignUpFlow verification code is: {code}\n"
            f"This code expires in 10 minutes.\n"
            f"Reply STOP to unsubscribe."
        )

        try:
            twilio_message = self.client.messages.create(
                body=message_text,
                from_=self.from_phone,
                to=phone_number,
            )

            return code

        except TwilioRestException as e:
            raise TwilioRestException(
                status=e.status,
                uri=e.uri,
                msg=f"Failed to send verification code: {e.msg}",
            )

    def verify_code(
        self, db: Session, person_id: int, code: int
    ) -> Dict[str, Any]:
        """
        Verify SMS verification code and mark phone as verified.

        Args:
            db: Database session
            person_id: Person ID verifying phone
            code: 6-digit verification code entered by user

        Returns:
            Dictionary with verified (bool), message (str), phone_number (str)

        Raises:
            ValueError: If code expired or max attempts exceeded
        """
        # 1. Get verification code from database
        verification = (
            db.query(SmsVerificationCode)
            .filter(SmsVerificationCode.person_id == person_id)
            .first()
        )

        if not verification:
            raise ValueError("No verification code found. Please request a new code.")

        # 2. Check expiration (10 minutes)
        if datetime.utcnow() > verification.expires_at:
            db.delete(verification)
            db.commit()
            raise ValueError("Verification code expired. Please request a new code.")

        # 3. Check attempts (max 3)
        if verification.attempts >= 3:
            db.delete(verification)
            db.commit()
            raise ValueError(
                "Maximum verification attempts exceeded. Please request a new code."
            )

        # 4. Validate code match
        verification.attempts += 1
        db.commit()

        if verification.verification_code != code:
            raise ValueError(
                f"Invalid verification code. {3 - verification.attempts} attempts remaining."
            )

        # 5. Mark phone as verified in sms_preferences
        sms_pref = (
            db.query(SmsPreference)
            .filter(SmsPreference.person_id == person_id)
            .first()
        )

        if not sms_pref:
            # Create new SMS preferences
            sms_pref = SmsPreference(
                person_id=person_id,
                phone_number=verification.phone_number,
                verified=True,
                notification_types=["assignment", "reminder", "change", "cancellation"],
                opt_in_date=datetime.utcnow(),
                language="en",
                timezone="UTC",
            )
            db.add(sms_pref)
        else:
            sms_pref.verified = True
            sms_pref.phone_number = verification.phone_number
            sms_pref.opt_in_date = datetime.utcnow()

        # 6. Delete verification code record
        db.delete(verification)
        db.commit()

        # 7. Send opt-in confirmation SMS
        confirmation_text = (
            "Phone verified! You're now subscribed to SignUpFlow SMS notifications. "
            "Reply STOP anytime to unsubscribe."
        )

        try:
            self.client.messages.create(
                body=confirmation_text,
                from_=self.from_phone,
                to=verification.phone_number,
            )
        except TwilioRestException:
            # Don't fail verification if confirmation SMS fails
            pass

        # 8. Return verification result
        return {
            "verified": True,
            "message": "Phone number verified successfully",
            "phone_number": verification.phone_number,
        }

    def process_incoming_reply(
        self, db: Session, from_phone: str, message_text: str, twilio_message_sid: str
    ) -> Dict[str, Any]:
        """
        Process incoming SMS reply (YES/NO/STOP/START/HELP).

        Args:
            db: Database session
            from_phone: Phone number that sent reply
            message_text: Reply text content
            twilio_message_sid: Twilio message SID for incoming message

        Returns:
            Dictionary with reply_type, action_taken, response_message

        Raises:
            ValueError: If phone number not found in system
        """
        # 1. Normalize message text (uppercase, trim)
        normalized_text = message_text.strip().upper()

        # Find person by phone number
        sms_pref = (
            db.query(SmsPreference)
            .filter(SmsPreference.phone_number == from_phone)
            .first()
        )

        if not sms_pref:
            raise ValueError(f"Phone number not found in system: {from_phone}")

        person_id = sms_pref.person_id

        # 2. Determine reply type (YES/NO/STOP/START/HELP/UNKNOWN)
        if normalized_text in ["YES", "Y", "CONFIRM", "OK"]:
            reply_type = "yes"
            response = self.process_yes_reply(db, person_id, None)
            action = "confirmed_assignment"
        elif normalized_text in ["NO", "N", "DECLINE", "CANCEL"]:
            reply_type = "no"
            response = self.process_no_reply(db, person_id, None)
            action = "declined_assignment"
        elif normalized_text in ["STOP", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"]:
            reply_type = "stop"
            response = self.process_stop_reply(db, person_id)
            action = "opted_out"
        elif normalized_text in ["START", "SUBSCRIBE", "UNSTOP"]:
            reply_type = "start"
            response = self.process_start_reply(db, person_id)
            action = "opted_in"
        elif normalized_text in ["HELP", "INFO", "?"]:
            reply_type = "help"
            response = self.process_help_reply(db, person_id)
            action = "help_sent"
        else:
            reply_type = "unknown"
            response = self.process_unknown_reply(db, person_id, message_text)
            action = "unknown_reply"

        # 4. Log reply to sms_replies table
        sms_reply = SmsReply(
            person_id=person_id,
            phone_number=from_phone,
            message_text=message_text,
            reply_type=reply_type,
            original_message_id=None,  # TODO: Link to original message if possible
            event_id=None,
            action_taken=action,
            twilio_message_sid=twilio_message_sid,
            processed_at=datetime.utcnow(),
        )
        db.add(sms_reply)
        db.commit()

        # 5. Return action taken and response message
        return {
            "reply_type": reply_type,
            "action_taken": action,
            "response_message": response,
            "person_id": person_id,
        }

    def process_yes_reply(
        self, db: Session, person_id: int, original_message_id: Optional[int]
    ) -> str:
        """
        Process YES reply to assignment notification.

        Args:
            db: Database session
            person_id: Person ID who replied YES
            original_message_id: ID of original assignment message

        Returns:
            Response message to send back to user
        """
        # 1. Find most recent upcoming assignment for this person
        upcoming_assignment = (
            db.query(Assignment)
            .join(Event)
            .filter(
                Assignment.person_id == person_id,
                Event.datetime >= datetime.utcnow(),
            )
            .order_by(Event.datetime.asc())
            .first()
        )

        if not upcoming_assignment:
            return (
                "No upcoming assignments found. "
                "Please contact your administrator if you believe this is an error."
            )

        # 2. Get event details
        event = upcoming_assignment.event
        event_name = event.title
        event_date = event.datetime.strftime("%A, %B %d at %I:%M %p")
        role = upcoming_assignment.role or "volunteer"

        # 3. Return confirmation message
        # Note: For MVP, we're just confirming without updating status
        # Phase 3 will add assignment status tracking
        return (
            f"✅ Confirmed: {event_name}\n"
            f"Role: {role}\n"
            f"Date: {event_date}\n"
            f"Thank you for confirming!"
        )

    def process_no_reply(
        self, db: Session, person_id: int, original_message_id: Optional[int]
    ) -> str:
        """
        Process NO reply to assignment notification.

        Args:
            db: Database session
            person_id: Person ID who replied NO
            original_message_id: ID of original assignment message

        Returns:
            Response message to send back to user
        """
        # 1. Find most recent upcoming assignment for this person
        upcoming_assignment = (
            db.query(Assignment)
            .join(Event)
            .filter(
                Assignment.person_id == person_id,
                Event.datetime >= datetime.utcnow(),
            )
            .order_by(Event.datetime.asc())
            .first()
        )

        if not upcoming_assignment:
            return (
                "No upcoming assignments found. "
                "Please contact your administrator if you believe this is an error."
            )

        # 2. Get event details before removal
        event = upcoming_assignment.event
        event_name = event.title
        event_date = event.datetime.strftime("%A, %B %d at %I:%M %p")
        role = upcoming_assignment.role or "volunteer"

        # 3. Remove assignment (MVP approach - Phase 3 will add notification to admin)
        db.delete(upcoming_assignment)
        db.commit()

        # 4. Return declination message
        return (
            f"❌ Declined: {event_name}\n"
            f"Role: {role}\n"
            f"Date: {event_date}\n"
            f"Your assignment has been removed. Administrator will be notified."
        )

    def process_stop_reply(self, db: Session, person_id: int) -> str:
        """
        Process STOP reply (opt-out from SMS notifications).

        Args:
            db: Database session
            person_id: Person ID opting out

        Returns:
            Opt-out confirmation message
        """
        # 1. Get SMS preferences
        sms_pref = (
            db.query(SmsPreference)
            .filter(SmsPreference.person_id == person_id)
            .first()
        )

        if not sms_pref:
            return "You are not subscribed to SMS notifications."

        # 2. Update opt_out_date (TCPA compliance)
        sms_pref.opt_out_date = datetime.utcnow()
        db.commit()

        # 3. Return opt-out confirmation
        return (
            "You have unsubscribed from SignUpFlow SMS notifications. "
            "You will receive email notifications instead. Reply START to re-enable."
        )

    def process_start_reply(self, db: Session, person_id: int) -> str:
        """
        Process START reply (re-enable SMS after opt-out).

        Args:
            db: Database session
            person_id: Person ID re-enabling SMS

        Returns:
            Re-enablement message with verification code requirement
        """
        # 1. Get SMS preferences
        sms_pref = (
            db.query(SmsPreference)
            .filter(SmsPreference.person_id == person_id)
            .first()
        )

        if not sms_pref:
            return "Phone number not found. Please verify your phone first."

        # 2. Check if already opted in
        if not sms_pref.opt_out_date:
            return "You are already subscribed to SMS notifications."

        # 3. Clear opt_out_date to re-enable
        sms_pref.opt_out_date = None
        sms_pref.opt_in_date = datetime.utcnow()  # Update opt-in date
        db.commit()

        # 4. Return re-enablement confirmation
        return (
            "Welcome back! You have re-subscribed to SignUpFlow SMS notifications. "
            "Reply STOP anytime to unsubscribe."
        )

    def process_help_reply(self, db: Session, person_id: int) -> str:
        """
        Process HELP reply (send help instructions).

        Args:
            db: Database session
            person_id: Person ID requesting help

        Returns:
            Help message with valid commands
        """
        return (
            "SignUpFlow SMS Commands:\n"
            "YES - Confirm assignment\n"
            "NO - Decline assignment\n"
            "STOP - Unsubscribe\n"
            "START - Re-subscribe\n"
            "HELP - Show this message\n"
            "Support: support@signupflow.io"
        )

    def process_unknown_reply(self, db: Session, person_id: int, message_text: str) -> str:
        """
        Process unrecognized reply (send friendly error message).

        Args:
            db: Database session
            person_id: Person ID who sent unrecognized reply
            message_text: Original message text

        Returns:
            Error message explaining valid options
        """
        return (
            "Reply YES to confirm or NO to decline assignment for [Event Name]. "
            "Reply HELP for assistance, STOP to unsubscribe."
        )

    def compose_assignment_message(
        self, db: Session, event: Event, role: str, language: str = "en"
    ) -> str:
        """
        Compose assignment notification message from template.

        Args:
            db: Database session
            event: Event object
            role: Role name for assignment
            language: Message language ('en' or 'es')

        Returns:
            Formatted SMS message text
        """
        # 1. Get assignment template from sms_templates
        template = (
            db.query(SmsTemplate)
            .filter(
                SmsTemplate.organization_id == event.org_id,
                SmsTemplate.message_type == "assignment",
                SmsTemplate.is_system == True,
            )
            .first()
        )

        if not template:
            raise ValueError(
                f"No assignment template found for organization {event.org_id}"
            )

        # 2. Extract event details (name, date, time, location)
        event_datetime = event.datetime
        date_str = event_datetime.strftime("%A, %B %d")  # "Monday, January 15"
        time_str = event_datetime.strftime("%I:%M %p")  # "10:00 AM"

        # 3. Build context for template substitution
        context = {
            "volunteer_name": "Volunteer",  # Will be replaced with actual name when sending
            "event_name": event.title,
            "date": date_str,
            "time": time_str,
            "location": event.location or "TBD",
            "role": role,
        }

        # 4. Render template with context
        rendered_message = self.render_template(
            db=db, template_id=template.id, context=context, language=language
        )

        return rendered_message

    def render_template(
        self,
        db: Session,
        template_id: int,
        context: Dict[str, Any],
        language: str = "en",
    ) -> str:
        """
        Render SMS template with variable substitution.

        Args:
            db: Database session
            template_id: Template ID to render
            context: Dictionary with variable values (event_name, date, time, etc.)
            language: Language for template selection ('en' or 'es')

        Returns:
            Rendered message text with variables substituted
        """
        # 1. Get template from database
        template_record = (
            db.query(SmsTemplate).filter(SmsTemplate.id == template_id).first()
        )

        if not template_record:
            raise ValueError(f"Template {template_id} not found")

        # 2. Select correct translation based on language
        template_text = template_record.template_text  # Default English

        if language != "en" and template_record.translations:
            # Check if translation exists for requested language
            if language in template_record.translations:
                template_text = template_record.translations[language]

        # 3. Use Jinja2 to render template with context
        try:
            jinja_template = Template(template_text)
            rendered_text = jinja_template.render(**context)
        except Exception as e:
            # Handle missing variables gracefully
            raise ValueError(f"Template rendering failed: {str(e)}")

        # 4. Update usage count
        template_record.usage_count += 1
        db.commit()

        # 5. Return rendered text
        return rendered_text

    def validate_phone_format(self, phone_number: str) -> bool:
        """
        Validate phone number is in E.164 format.

        Args:
            phone_number: Phone number to validate

        Returns:
            True if valid E.164 format, False otherwise
        """
        # E.164 format: +[country code][number] (e.g., +12345678900)
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(e164_pattern, phone_number))
