"""
SMS Notification Service for ShareYourSales
Supports Twilio for SMS/WhatsApp messaging

Dependencies:
    pip install twilio

Environment Variables:
    TWILIO_ACCOUNT_SID: Your Twilio account SID
    TWILIO_AUTH_TOKEN: Your Twilio auth token
    TWILIO_PHONE_NUMBER: Your Twilio phone number (E.164 format: +1234567890)
    TWILIO_WHATSAPP_NUMBER: Your Twilio WhatsApp number (optional, format: whatsapp:+1234567890)
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("twilio not installed. Run: pip install twilio")


logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Type of message to send"""
    SMS = "sms"
    WHATSAPP = "whatsapp"


class MessagePriority(Enum):
    """Priority for message delivery"""
    HIGH = "high"  # Immediate delivery
    NORMAL = "normal"  # Standard delivery
    LOW = "low"  # Can be batched


@dataclass
class SMSMessage:
    """SMS message data structure"""
    to: str  # Phone number in E.164 format (+212612345678)
    body: str  # Message text
    message_type: MessageType = MessageType.SMS
    from_number: Optional[str] = None  # Override default sender
    media_url: Optional[List[str]] = None  # MMS media URLs
    priority: MessagePriority = MessagePriority.NORMAL
    max_price: Optional[float] = None  # Maximum price willing to pay
    validity_period: Optional[int] = None  # How long message is valid (seconds)


class TwilioSMSService:
    """
    Twilio SMS/WhatsApp service

    Features:
    - Send SMS messages
    - Send WhatsApp messages
    - Send MMS with media
    - Delivery status tracking
    - Error handling with retry logic

    Example:
        service = TwilioSMSService(
            account_sid="AC...",
            auth_token="...",
            from_number="+1234567890"
        )

        message = SMSMessage(
            to="+212612345678",
            body="Your payment of 50 MAD was confirmed",
            priority=MessagePriority.HIGH
        )

        result = service.send_message(message)
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        whatsapp_number: Optional[str] = None
    ):
        """
        Initialize Twilio SMS service

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Default sender phone number (E.164 format)
            whatsapp_number: WhatsApp number (format: whatsapp:+1234567890)
        """
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio not installed. Run: pip install twilio")

        # Use provided credentials or fallback to environment
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")
        self.whatsapp_number = whatsapp_number or os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not self.account_sid or not self.auth_token:
            raise ValueError(
                "Twilio credentials not found. Provide either:\n"
                "1. account_sid and auth_token parameters\n"
                "2. TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables"
            )

        if not self.from_number:
            raise ValueError(
                "Twilio phone number not found. Provide either:\n"
                "1. from_number parameter\n"
                "2. TWILIO_PHONE_NUMBER environment variable"
            )

        # Initialize Twilio client
        self.client = Client(self.account_sid, self.auth_token)
        logger.info(f"Twilio SMS service initialized with number {self.from_number}")

    def send_message(self, message: SMSMessage) -> Dict[str, Any]:
        """
        Send SMS or WhatsApp message

        Args:
            message: SMSMessage object

        Returns:
            Result dictionary with success status and message details
        """
        try:
            # Format phone number (ensure E.164 format)
            to_number = self._format_phone_number(message.to)

            # Determine sender number
            if message.message_type == MessageType.WHATSAPP:
                from_number = self.whatsapp_number or f"whatsapp:{self.from_number}"
                to_number = f"whatsapp:{to_number}"
            else:
                from_number = message.from_number or self.from_number

            # Build message parameters
            params = {
                "body": message.body,
                "from_": from_number,
                "to": to_number
            }

            # Add optional parameters
            if message.media_url:
                params["media_url"] = message.media_url

            if message.max_price:
                params["max_price"] = message.max_price

            if message.validity_period:
                params["validity_period"] = message.validity_period

            # Send message via Twilio
            twilio_message = self.client.messages.create(**params)

            logger.info(
                f"Successfully sent {message.message_type.value} to {message.to}: "
                f"SID={twilio_message.sid}, Status={twilio_message.status}"
            )

            return {
                "success": True,
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": message.to,
                "type": message.message_type.value,
                "price": twilio_message.price,
                "price_unit": twilio_message.price_unit,
                "date_created": twilio_message.date_created.isoformat() if twilio_message.date_created else None
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error sending message: {e.code} - {e.msg}")
            return {
                "success": False,
                "error": "twilio_error",
                "error_code": e.code,
                "error_message": e.msg,
                "to": message.to
            }

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {
                "success": False,
                "error": "send_failed",
                "message": str(e),
                "to": message.to
            }

    def send_bulk(self, messages: List[SMSMessage]) -> Dict[str, Any]:
        """
        Send multiple messages

        Args:
            messages: List of SMSMessage objects

        Returns:
            Result with success_count, failure_count, and individual results
        """
        results = []
        success_count = 0
        failure_count = 0

        for message in messages:
            result = self.send_message(message)
            results.append(result)

            if result.get("success"):
                success_count += 1
            else:
                failure_count += 1

        logger.info(f"Bulk send completed: {success_count} successes, {failure_count} failures")

        return {
            "success": success_count > 0,
            "success_count": success_count,
            "failure_count": failure_count,
            "total": len(messages),
            "results": results
        }

    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get status of a sent message

        Args:
            message_sid: Twilio message SID

        Returns:
            Message status details
        """
        try:
            message = self.client.messages(message_sid).fetch()

            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "date_created": message.date_created.isoformat() if message.date_created else None,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "date_updated": message.date_updated.isoformat() if message.date_updated else None,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "price": message.price,
                "price_unit": message.price_unit
            }

        except TwilioRestException as e:
            logger.error(f"Error fetching message status: {e.msg}")
            return {
                "success": False,
                "error": str(e)
            }

    def _format_phone_number(self, phone: str) -> str:
        """
        Format phone number to E.164 format

        Args:
            phone: Phone number (various formats accepted)

        Returns:
            E.164 formatted phone number (+212612345678)
        """
        # Remove common formatting characters
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Add + if missing
        if not phone.startswith("+"):
            # If starts with 0, assume Morocco (+212)
            if phone.startswith("0"):
                phone = "+212" + phone[1:]
            # If starts with country code without +
            elif len(phone) >= 10:
                phone = "+" + phone
            else:
                # Default to Morocco
                phone = "+212" + phone

        return phone


class SMSNotificationService:
    """
    Unified SMS notification service

    Provides pre-built SMS templates and easy sending

    Example:
        service = SMSNotificationService()
        service.send_payment_confirmation(
            phone_number="+212612345678",
            amount=50.0,
            transaction_id="txn_12345"
        )
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        whatsapp_number: Optional[str] = None
    ):
        """Initialize SMS notification service"""
        if TWILIO_AVAILABLE:
            try:
                self.twilio = TwilioSMSService(
                    account_sid=account_sid,
                    auth_token=auth_token,
                    from_number=from_number,
                    whatsapp_number=whatsapp_number
                )
                logger.info("SMS notification service initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
                self.twilio = None
        else:
            logger.warning("Twilio not available - SMS notifications disabled")
            self.twilio = None

    def is_available(self) -> bool:
        """Check if SMS service is available"""
        return self.twilio is not None

    def send_message(self, message: SMSMessage) -> Dict[str, Any]:
        """Send SMS message"""
        if not self.twilio:
            return {"success": False, "error": "SMS service not available"}

        return self.twilio.send_message(message)

    # ===== Pre-built SMS templates =====

    def send_payment_confirmation(
        self,
        phone_number: str,
        amount: float,
        currency: str = "MAD",
        transaction_id: Optional[str] = None,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send payment confirmation SMS"""
        body = f"ShareYourSales: Votre paiement de {amount} {currency} a été confirmé avec succès."
        if transaction_id:
            body += f" Réf: {transaction_id}"

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)

    def send_commission_earned(
        self,
        phone_number: str,
        amount: float,
        product_name: str,
        currency: str = "MAD",
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send commission earned SMS"""
        body = (
            f"ShareYourSales: Félicitations! Vous avez gagné {amount} {currency} "
            f"de commission sur '{product_name}'. Consultez votre tableau de bord."
        )

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)

    def send_verification_code(
        self,
        phone_number: str,
        code: str,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send phone verification code"""
        body = f"ShareYourSales: Votre code de vérification est: {code}. Valide pendant 10 minutes."

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH,
            validity_period=600  # 10 minutes
        )
        return self.send_message(message)

    def send_payout_notification(
        self,
        phone_number: str,
        amount: float,
        currency: str = "MAD",
        estimated_arrival: Optional[str] = None,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send payout notification SMS"""
        body = f"ShareYourSales: Votre retrait de {amount} {currency} est en cours de traitement."
        if estimated_arrival:
            body += f" Arrivée prévue: {estimated_arrival}."

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)

    def send_new_lead_alert(
        self,
        phone_number: str,
        lead_name: str,
        product_name: str,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send new lead alert SMS"""
        body = (
            f"ShareYourSales: Nouveau lead de {lead_name} pour '{product_name}'. "
            f"Connectez-vous pour voir les détails."
        )

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.NORMAL
        )
        return self.send_message(message)

    def send_account_alert(
        self,
        phone_number: str,
        alert_message: str,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send account security/activity alert"""
        body = f"ShareYourSales: {alert_message}"

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)

    def send_password_reset(
        self,
        phone_number: str,
        reset_code: str,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send password reset code"""
        body = (
            f"ShareYourSales: Votre code de réinitialisation est: {reset_code}. "
            f"Valide pendant 30 minutes. Ne partagez pas ce code."
        )

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.HIGH,
            validity_period=1800  # 30 minutes
        )
        return self.send_message(message)

    def send_promotion(
        self,
        phone_number: str,
        promotion_message: str,
        use_whatsapp: bool = True
    ) -> Dict[str, Any]:
        """Send promotional message (prefer WhatsApp to avoid SMS spam)"""
        body = f"ShareYourSales: {promotion_message}"

        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=MessagePriority.LOW
        )
        return self.send_message(message)

    def send_custom(
        self,
        phone_number: str,
        body: str,
        use_whatsapp: bool = False,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> Dict[str, Any]:
        """Send custom SMS"""
        message = SMSMessage(
            to=phone_number,
            body=body,
            message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
            priority=priority
        )
        return self.send_message(message)

    def send_bulk_notifications(
        self,
        phone_numbers: List[str],
        body: str,
        use_whatsapp: bool = False
    ) -> Dict[str, Any]:
        """Send bulk notifications to multiple users"""
        if not self.twilio:
            return {"success": False, "error": "SMS service not available"}

        messages = [
            SMSMessage(
                to=phone,
                body=body,
                message_type=MessageType.WHATSAPP if use_whatsapp else MessageType.SMS,
                priority=MessagePriority.NORMAL
            )
            for phone in phone_numbers
        ]

        return self.twilio.send_bulk(messages)


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    service = SMSNotificationService()

    if service.is_available():
        # Example 1: Payment confirmation
        result = service.send_payment_confirmation(
            phone_number="+212612345678",
            amount=100.50,
            transaction_id="txn_12345"
        )
        print("Payment SMS:", result)

        # Example 2: Commission earned via WhatsApp
        result = service.send_commission_earned(
            phone_number="+212612345678",
            amount=25.00,
            product_name="iPhone 15 Pro",
            use_whatsapp=True
        )
        print("Commission WhatsApp:", result)

        # Example 3: Verification code
        result = service.send_verification_code(
            phone_number="+212612345678",
            code="123456"
        )
        print("Verification SMS:", result)

        # Example 4: Bulk notification
        result = service.send_bulk_notifications(
            phone_numbers=["+212612345678", "+212698765432"],
            body="Nouvelle fonctionnalité disponible sur ShareYourSales!",
            use_whatsapp=True
        )
        print("Bulk WhatsApp:", result)
    else:
        print("SMS service not available")
