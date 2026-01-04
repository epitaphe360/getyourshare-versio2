"""
Unified Notification Services Endpoints for ShareYourSales
Supports Email, Push Notifications (FCM), and SMS/WhatsApp (Twilio) via API

Endpoints:
    POST /api/notification-services/send - Send notification via any channel
    POST /api/notification-services/email - Send email
    POST /api/notification-services/push - Send push notification
    POST /api/notification-services/sms - Send SMS
    POST /api/notification-services/multi - Send to multiple channels
    GET /api/notification-services/test - Test all notification services
    POST /api/notification-services/preferences - Update user notification preferences
    GET /api/notification-services/preferences/{user_id} - Get user notification preferences

Dependencies:
    pip install fastapi pydantic

Usage:
    from fastapi import FastAPI
    from notification_services_endpoints import router as notification_services_router

    app = FastAPI()
    app.include_router(notification_services_router, prefix="/api/notification-services", tags=["notification-services"])
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, EmailStr, Field

# Import notification services
from services.email_notification_service import EmailNotificationService
from services.push_notification_service import (
    PushNotificationService,
    PushNotification,
    NotificationPriority as PushPriority,
    NotificationCategory as PushCategory
)
from services.sms_notification_service import (
    SMSNotificationService,
    SMSMessage,
    MessageType,
    MessagePriority as SMSPriority
)


logger = logging.getLogger(__name__)
router = APIRouter()


# ===== Pydantic Models =====

class NotificationChannel(str, Enum):
    """Available notification channels"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationPriority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class EmailRequest(BaseModel):
    """Email notification request"""
    to: EmailStr
    subject: Optional[str] = None
    template: Optional[str] = None  # Template name
    variables: Optional[Dict[str, str]] = None  # Template variables
    html_content: Optional[str] = None  # Custom HTML
    reply_to: Optional[EmailStr] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

    class Config:
        schema_extra = {
            "example": {
                "to": "user@example.com",
                "template": "payment_confirmation",
                "variables": {
                    "user_name": "Mohammed",
                    "amount": "100.50",
                    "currency": "MAD",
                    "transaction_id": "txn_12345"
                }
            }
        }


class PushRequest(BaseModel):
    """Push notification request"""
    device_token: Optional[str] = None
    device_tokens: Optional[List[str]] = None
    topic: Optional[str] = None
    title: str
    body: str
    data: Optional[Dict[str, str]] = None
    image_url: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: str = "system"
    click_action: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "device_token": "fcm_device_token_here",
                "title": "💰 Paiement confirmé",
                "body": "Votre paiement de 100 MAD a été confirmé",
                "priority": "high",
                "category": "payment",
                "click_action": "/payments/history"
            }
        }


class SMSRequest(BaseModel):
    """SMS/WhatsApp notification request"""
    phone_number: str = Field(..., description="Phone number in international format (+212...)")
    message: str = Field(..., max_length=1600, description="SMS message text")
    use_whatsapp: bool = False
    priority: NotificationPriority = NotificationPriority.NORMAL

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+212612345678",
                "message": "Votre code de vérification est: 123456",
                "use_whatsapp": False,
                "priority": "high"
            }
        }


class MultiChannelRequest(BaseModel):
    """Send notification to multiple channels"""
    channels: List[NotificationChannel]
    user_id: Optional[str] = None  # Auto-lookup contact info
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    device_token: Optional[str] = None
    title: str
    body: str
    template: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    priority: NotificationPriority = NotificationPriority.NORMAL

    class Config:
        schema_extra = {
            "example": {
                "channels": ["email", "push", "sms"],
                "email": "user@example.com",
                "phone_number": "+212612345678",
                "device_token": "fcm_token",
                "title": "Paiement confirmé",
                "body": "Votre paiement a été traité avec succès",
                "priority": "high"
            }
        }


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True
    whatsapp_enabled: bool = True
    email_payments: bool = True
    email_commissions: bool = True
    email_leads: bool = True
    email_marketing: bool = False
    push_payments: bool = True
    push_commissions: bool = True
    push_leads: bool = True
    push_marketing: bool = False
    sms_payments: bool = True
    sms_commissions: bool = False
    sms_security: bool = True


# ===== Service Initialization =====

def get_email_service() -> EmailNotificationService:
    """Get email notification service instance"""
    return EmailNotificationService()


def get_push_service() -> Optional[PushNotificationService]:
    """Get push notification service instance"""
    try:
        return PushNotificationService()
    except Exception as e:
        logger.warning(f"Push service not available: {e}")
        return None


def get_sms_service() -> Optional[SMSNotificationService]:
    """Get SMS notification service instance"""
    try:
        return SMSNotificationService()
    except Exception as e:
        logger.warning(f"SMS service not available: {e}")
        return None


# ===== Helper Functions =====

def get_user_contact_info(user_id: str) -> Dict[str, str]:
    """
    Get user contact information from database

    In production, this would query Supabase:
    supabase.table("users").select("email, phone, fcm_token").eq("id", user_id).single()
    """
    # TODO: Implement actual database lookup
    # For now, return empty dict
    return {}


def check_notification_preferences(user_id: str, channel: NotificationChannel, category: str) -> bool:
    """
    Check if user wants to receive notifications on this channel for this category

    In production, query user preferences from database
    """
    # TODO: Implement actual preference checking
    # For now, allow all notifications
    return True


# ===== API Endpoints =====

@router.post("/send")
async def send_notification(
    channel: NotificationChannel,
    to: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    priority: NotificationPriority = NotificationPriority.NORMAL
):
    """
    Send notification via specified channel

    Universal endpoint for sending notifications
    """
    try:
        if channel == NotificationChannel.EMAIL:
            service = get_email_service()
            result = service.send_email(
                to=to,
                subject=title,
                html_content=f"<html><body><h2>{title}</h2><p>{body}</p></body></html>"
            )

        elif channel == NotificationChannel.PUSH:
            service = get_push_service()
            if not service or not service.is_available():
                raise HTTPException(503, "Push notification service not available")

            notification = PushNotification(
                title=title,
                body=body,
                token=to,
                data=data,
                priority=PushPriority.HIGH if priority == NotificationPriority.HIGH else PushPriority.NORMAL
            )
            result = service.send_notification(notification)

        elif channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP]:
            service = get_sms_service()
            if not service or not service.is_available():
                raise HTTPException(503, "SMS service not available")

            message = SMSMessage(
                to=to,
                body=f"{title}\n\n{body}",
                message_type=MessageType.WHATSAPP if channel == NotificationChannel.WHATSAPP else MessageType.SMS,
                priority=SMSPriority.HIGH if priority == NotificationPriority.HIGH else SMSPriority.NORMAL
            )
            result = service.send_message(message)

        else:
            raise HTTPException(400, f"Unsupported channel: {channel}")

        if not result.get("success"):
            raise HTTPException(500, f"Failed to send notification: {result.get('error', 'Unknown error')}")

        return {
            "success": True,
            "channel": channel,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(500, str(e))


@router.post("/email")
async def send_email(request: EmailRequest):
    """Send email notification"""
    service = get_email_service()

    try:
        if request.template:
            # Use pre-built template
            result = service.send_template_email(
                to=request.to,
                template_name=request.template,
                variables=request.variables or {}
            )
        elif request.html_content and request.subject:
            # Custom email
            result = service.send_email(
                to=request.to,
                subject=request.subject,
                html_content=request.html_content,
                reply_to=request.reply_to,
                cc=request.cc,
                bcc=request.bcc
            )
        else:
            raise HTTPException(400, "Either 'template' or both 'subject' and 'html_content' required")

        if not result.get("success"):
            raise HTTPException(500, f"Failed to send email: {result.get('error')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(500, str(e))


@router.post("/push")
async def send_push(request: PushRequest):
    """Send push notification"""
    service = get_push_service()

    if not service or not service.is_available():
        raise HTTPException(503, "Push notification service not available")

    try:
        # Map priority
        priority = PushPriority.HIGH if request.priority == NotificationPriority.HIGH else PushPriority.NORMAL

        # Map category
        category_map = {
            "payment": PushCategory.PAYMENT,
            "commission": PushCategory.COMMISSION,
            "lead": PushCategory.LEAD,
            "social": PushCategory.SOCIAL,
            "marketing": PushCategory.MARKETING,
            "system": PushCategory.SYSTEM
        }
        category = category_map.get(request.category, PushCategory.SYSTEM)

        notification = PushNotification(
            title=request.title,
            body=request.body,
            token=request.device_token,
            tokens=request.device_tokens,
            topic=request.topic,
            data=request.data,
            image_url=request.image_url,
            priority=priority,
            category=category,
            click_action=request.click_action
        )

        result = service.send_notification(notification)

        if not result.get("success"):
            raise HTTPException(500, f"Failed to send push: {result.get('error')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        raise HTTPException(500, str(e))


@router.post("/sms")
async def send_sms(request: SMSRequest):
    """Send SMS or WhatsApp notification"""
    service = get_sms_service()

    if not service or not service.is_available():
        raise HTTPException(503, "SMS service not available")

    try:
        priority = SMSPriority.HIGH if request.priority == NotificationPriority.HIGH else SMSPriority.NORMAL

        message = SMSMessage(
            to=request.phone_number,
            body=request.message,
            message_type=MessageType.WHATSAPP if request.use_whatsapp else MessageType.SMS,
            priority=priority
        )

        result = service.send_message(message)

        if not result.get("success"):
            raise HTTPException(500, f"Failed to send SMS: {result.get('error')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(500, str(e))


@router.post("/multi")
async def send_multi_channel(request: MultiChannelRequest):
    """Send notification to multiple channels"""
    results = {}
    success_count = 0
    failure_count = 0

    # If user_id provided, lookup contact info
    if request.user_id:
        contact_info = get_user_contact_info(request.user_id)
        email = request.email or contact_info.get("email")
        phone_number = request.phone_number or contact_info.get("phone")
        device_token = request.device_token or contact_info.get("fcm_token")
    else:
        email = request.email
        phone_number = request.phone_number
        device_token = request.device_token

    # Send to each requested channel
    for channel in request.channels:
        try:
            # Check user preferences
            if request.user_id and not check_notification_preferences(request.user_id, channel, "general"):
                results[channel.value] = {"success": False, "error": "User preferences disabled"}
                failure_count += 1
                continue

            if channel == NotificationChannel.EMAIL and email:
                service = get_email_service()
                if request.template:
                    result = service.send_template_email(email, request.template, request.variables or {})
                else:
                    result = service.send_email(
                        email,
                        request.title,
                        f"<html><body><h2>{request.title}</h2><p>{request.body}</p></body></html>"
                    )
                results[channel.value] = result

            elif channel == NotificationChannel.PUSH and device_token:
                service = get_push_service()
                if service and service.is_available():
                    notification = PushNotification(
                        title=request.title,
                        body=request.body,
                        token=device_token,
                        priority=PushPriority.HIGH if request.priority == NotificationPriority.HIGH else PushPriority.NORMAL
                    )
                    result = service.send_notification(notification)
                    results[channel.value] = result
                else:
                    results[channel.value] = {"success": False, "error": "Service not available"}

            elif channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP] and phone_number:
                service = get_sms_service()
                if service and service.is_available():
                    message = SMSMessage(
                        to=phone_number,
                        body=f"{request.title}\n\n{request.body}",
                        message_type=MessageType.WHATSAPP if channel == NotificationChannel.WHATSAPP else MessageType.SMS
                    )
                    result = service.send_message(message)
                    results[channel.value] = result
                else:
                    results[channel.value] = {"success": False, "error": "Service not available"}

            else:
                results[channel.value] = {"success": False, "error": "Missing contact information"}

            if results[channel.value].get("success"):
                success_count += 1
            else:
                failure_count += 1

        except Exception as e:
            logger.error(f"Error sending to {channel}: {e}")
            results[channel.value] = {"success": False, "error": str(e)}
            failure_count += 1

    return {
        "success": success_count > 0,
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results
    }


@router.get("/test")
async def test_services():
    """Test all notification services availability"""
    email_service = get_email_service()
    push_service = get_push_service()
    sms_service = get_sms_service()

    return {
        "email": {
            "available": True,
            "providers": {
                "resend": email_service.resend is not None,
                "smtp": email_service.smtp is not None
            }
        },
        "push": {
            "available": push_service is not None and push_service.is_available() if push_service else False,
            "provider": "firebase"
        },
        "sms": {
            "available": sms_service is not None and sms_service.is_available() if sms_service else False,
            "provider": "twilio"
        }
    }


@router.post("/preferences")
async def update_notification_preferences(preferences: NotificationPreferences):
    """Update user notification preferences"""
    # TODO: Save to database
    # supabase.table("notification_preferences").upsert(preferences.dict())

    return {
        "success": True,
        "message": "Preferences updated successfully",
        "preferences": preferences
    }


@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """Get user notification preferences"""
    # TODO: Query from database
    # result = supabase.table("notification_preferences").select("*").eq("user_id", user_id).single()

    # Return default preferences for now
    return NotificationPreferences(user_id=user_id)


# ===== Quick Send Functions (for use in other endpoints) =====

async def quick_send_payment_confirmation(
    user_id: str,
    amount: float,
    currency: str = "MAD",
    transaction_id: Optional[str] = None,
    channels: List[NotificationChannel] = None
):
    """Quick helper to send payment confirmation across channels"""
    if channels is None:
        channels = [NotificationChannel.EMAIL, NotificationChannel.PUSH]

    # Get user contact info
    contact = get_user_contact_info(user_id)

    request = MultiChannelRequest(
        channels=channels,
        user_id=user_id,
        email=contact.get("email"),
        phone_number=contact.get("phone"),
        device_token=contact.get("fcm_token"),
        title="💰 Paiement confirmé",
        body=f"Votre paiement de {amount} {currency} a été confirmé avec succès",
        template="payment_confirmation",
        variables={
            "amount": str(amount),
            "currency": currency,
            "transaction_id": transaction_id or ""
        },
        priority=NotificationPriority.HIGH
    )

    return await send_multi_channel(request)


# Export router
__all__ = ["router"]
