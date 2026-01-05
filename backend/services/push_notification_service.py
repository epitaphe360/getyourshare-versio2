"""
Push Notification Service for ShareYourSales
Supports Firebase Cloud Messaging (FCM) for mobile push notifications

Dependencies:
    pip install firebase-admin

Environment Variables:
    FIREBASE_PROJECT_ID: Your Firebase project ID
    FIREBASE_PRIVATE_KEY: Firebase service account private key
    FIREBASE_CLIENT_EMAIL: Firebase service account email

    OR (simpler):
    FIREBASE_CREDENTIALS_PATH: Path to Firebase service account JSON file
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("firebase-admin not installed. Run: pip install firebase-admin")


logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Priority levels for push notifications"""
    HIGH = "high"
    NORMAL = "normal"


class NotificationCategory(Enum):
    """Categories for organizing notifications"""
    PAYMENT = "payment"
    COMMISSION = "commission"
    LEAD = "lead"
    SYSTEM = "system"
    MARKETING = "marketing"
    SOCIAL = "social"


@dataclass
class PushNotification:
    """Push notification data structure"""
    title: str
    body: str
    token: Optional[str] = None  # Device token for single device
    topic: Optional[str] = None  # Topic for broadcast
    tokens: Optional[List[str]] = None  # Multiple device tokens
    data: Optional[Dict[str, str]] = None  # Custom data payload
    image_url: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: NotificationCategory = NotificationCategory.SYSTEM
    badge: Optional[int] = None  # iOS badge count
    sound: str = "default"
    click_action: Optional[str] = None  # Deep link URL
    ttl: int = 3600  # Time to live in seconds (1 hour default)


class FirebasePushService:
    """
    Firebase Cloud Messaging (FCM) service

    Features:
    - Send to single device via token
    - Send to multiple devices via tokens
    - Broadcast to topics
    - Rich notifications with images
    - Custom data payload
    - Priority control
    - Platform-specific configuration (Android/iOS)

    Example:
        service = FirebasePushService()
        notification = PushNotification(
            title="Payment Received",
            body="You received 50 MAD commission",
            token="device_token_here",
            data={"type": "commission", "amount": "50"},
            priority=NotificationPriority.HIGH
        )
        result = service.send_notification(notification)
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase service

        Args:
            credentials_path: Path to Firebase service account JSON file
                            If None, will try to use environment variables
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin not installed. Run: pip install firebase-admin")

        # Check if already initialized
        if not firebase_admin._apps:
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"Firebase initialized with credentials from {credentials_path}")
            else:
                # Try environment variables
                firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                if firebase_creds_path:
                    cred = credentials.Certificate(firebase_creds_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized from FIREBASE_CREDENTIALS_PATH")
                else:
                    # Try individual env vars
                    project_id = os.getenv("FIREBASE_PROJECT_ID")
                    private_key = os.getenv("FIREBASE_PRIVATE_KEY")
                    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")

                    if project_id and private_key and client_email:
                        # Replace literal \n with actual newlines in private key
                        private_key = private_key.replace('\\n', '\n')

                        cred_dict = {
                            "type": "service_account",
                            "project_id": project_id,
                            "private_key": private_key,
                            "client_email": client_email,
                        }
                        cred = credentials.Certificate(cred_dict)
                        firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized from environment variables")
                    else:
                        raise ValueError(
                            "Firebase credentials not found. Provide either:\n"
                            "1. credentials_path parameter\n"
                            "2. FIREBASE_CREDENTIALS_PATH environment variable\n"
                            "3. FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL environment variables"
                        )
        else:
            logger.info("Firebase already initialized")

    def send_notification(self, notification: PushNotification) -> Dict[str, Any]:
        """
        Send push notification

        Args:
            notification: PushNotification object

        Returns:
            Result dictionary with success status and message_id or error
        """
        try:
            # Build the notification message
            fcm_notification = messaging.Notification(
                title=notification.title,
                body=notification.body,
                image=notification.image_url
            )

            # Build Android config
            android_config = messaging.AndroidConfig(
                priority=notification.priority.value,
                ttl=notification.ttl,
                notification=messaging.AndroidNotification(
                    sound=notification.sound,
                    click_action=notification.click_action,
                    color="#4CAF50",  # ShareYourSales brand color
                    icon="ic_notification"
                )
            )

            # Build iOS config
            apns_payload = messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=notification.title,
                        body=notification.body
                    ),
                    badge=notification.badge,
                    sound=notification.sound,
                    category=notification.category.value
                )
            )
            apns_config = messaging.APNSConfig(payload=apns_payload)

            # Add custom data
            data = notification.data or {}
            data['timestamp'] = datetime.now().isoformat()
            data['category'] = notification.category.value

            # Convert all data values to strings (FCM requirement)
            data = {k: str(v) for k, v in data.items()}

            # Send based on target type
            if notification.token:
                # Send to single device
                message = messaging.Message(
                    notification=fcm_notification,
                    token=notification.token,
                    data=data,
                    android=android_config,
                    apns=apns_config
                )
                response = messaging.send(message)
                logger.info(f"Successfully sent notification to token: {response}")
                return {
                    "success": True,
                    "message_id": response,
                    "target": "token",
                    "count": 1
                }

            elif notification.tokens:
                # Send to multiple devices
                message = messaging.MulticastMessage(
                    notification=fcm_notification,
                    tokens=notification.tokens,
                    data=data,
                    android=android_config,
                    apns=apns_config
                )
                response = messaging.send_multicast(message)
                logger.info(f"Successfully sent to {response.success_count}/{len(notification.tokens)} devices")

                return {
                    "success": response.success_count > 0,
                    "success_count": response.success_count,
                    "failure_count": response.failure_count,
                    "target": "multicast",
                    "count": len(notification.tokens),
                    "responses": [
                        {"success": resp.success, "message_id": resp.message_id, "error": str(resp.exception) if resp.exception else None}
                        for resp in response.responses
                    ]
                }

            elif notification.topic:
                # Send to topic subscribers
                message = messaging.Message(
                    notification=fcm_notification,
                    topic=notification.topic,
                    data=data,
                    android=android_config,
                    apns=apns_config
                )
                response = messaging.send(message)
                logger.info(f"Successfully sent notification to topic {notification.topic}: {response}")
                return {
                    "success": True,
                    "message_id": response,
                    "target": "topic",
                    "topic": notification.topic
                }

            else:
                return {
                    "success": False,
                    "error": "No target specified (token, tokens, or topic required)"
                }

        except messaging.UnregisteredError as e:
            logger.warning(f"Device token unregistered: {e}")
            return {"success": False, "error": "device_unregistered", "message": str(e)}

        except messaging.InvalidArgumentError as e:
            logger.error(f"Invalid argument: {e}")
            return {"success": False, "error": "invalid_argument", "message": str(e)}

        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {"success": False, "error": "send_failed", "message": str(e)}

    def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """
        Subscribe device tokens to a topic

        Args:
            tokens: List of device tokens
            topic: Topic name (e.g., "all_users", "payment_updates")

        Returns:
            Result with success_count and failure_count
        """
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"Subscribed {response.success_count}/{len(tokens)} devices to topic '{topic}'")

            return {
                "success": response.success_count > 0,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "topic": topic
            }

        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return {"success": False, "error": str(e)}

    def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """
        Unsubscribe device tokens from a topic

        Args:
            tokens: List of device tokens
            topic: Topic name

        Returns:
            Result with success_count and failure_count
        """
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"Unsubscribed {response.success_count}/{len(tokens)} devices from topic '{topic}'")

            return {
                "success": response.success_count > 0,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "topic": topic
            }

        except Exception as e:
            logger.error(f"Error unsubscribing from topic: {e}")
            return {"success": False, "error": str(e)}


class PushNotificationService:
    """
    Unified push notification service

    Provides pre-built notification templates and easy sending

    Example:
        service = PushNotificationService()
        service.send_payment_confirmation(
            user_token="device_token",
            amount=50.0,
            currency="MAD"
        )
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize push notification service"""
        if FIREBASE_AVAILABLE:
            try:
                self.firebase = FirebasePushService(credentials_path)
                logger.info("Push notification service initialized with Firebase")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                self.firebase = None
        else:
            logger.warning("Firebase not available - push notifications disabled")
            self.firebase = None

    def is_available(self) -> bool:
        """Check if push notification service is available"""
        return self.firebase is not None

    def send_notification(self, notification: PushNotification) -> Dict[str, Any]:
        """Send push notification"""
        if not self.firebase:
            return {"success": False, "error": "Push notification service not available"}

        return self.firebase.send_notification(notification)

    # ===== Pre-built notification templates =====

    def send_payment_confirmation(
        self,
        user_token: str,
        amount: float,
        currency: str = "MAD",
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send payment confirmation notification"""
        notification = PushNotification(
            title="💰 Paiement confirmé",
            body=f"Votre paiement de {amount} {currency} a été confirmé avec succès",
            token=user_token,
            data={
                "type": "payment_confirmation",
                "amount": str(amount),
                "currency": currency,
                "transaction_id": transaction_id or ""
            },
            priority=NotificationPriority.HIGH,
            category=NotificationCategory.PAYMENT,
            click_action="/payments/history"
        )
        return self.send_notification(notification)

    def send_commission_earned(
        self,
        user_token: str,
        amount: float,
        product_name: str,
        currency: str = "MAD"
    ) -> Dict[str, Any]:
        """Send commission earned notification"""
        notification = PushNotification(
            title="🎉 Nouvelle commission",
            body=f"Vous avez gagné {amount} {currency} sur '{product_name}'",
            token=user_token,
            data={
                "type": "commission_earned",
                "amount": str(amount),
                "currency": currency,
                "product_name": product_name
            },
            priority=NotificationPriority.HIGH,
            category=NotificationCategory.COMMISSION,
            click_action="/dashboard/earnings"
        )
        return self.send_notification(notification)

    def send_new_lead(
        self,
        user_token: str,
        lead_name: str,
        product_name: str,
        potential_commission: Optional[float] = None
    ) -> Dict[str, Any]:
        """Send new lead notification"""
        body = f"Nouveau lead pour '{product_name}'"
        if potential_commission:
            body += f" - Commission potentielle: {potential_commission} MAD"

        notification = PushNotification(
            title="👤 Nouveau lead",
            body=body,
            token=user_token,
            data={
                "type": "new_lead",
                "lead_name": lead_name,
                "product_name": product_name,
                "potential_commission": str(potential_commission) if potential_commission else "0"
            },
            priority=NotificationPriority.HIGH,
            category=NotificationCategory.LEAD,
            click_action="/leads"
        )
        return self.send_notification(notification)

    def send_payout_processed(
        self,
        user_token: str,
        amount: float,
        currency: str = "MAD",
        method: str = "bank_transfer"
    ) -> Dict[str, Any]:
        """Send payout processed notification"""
        notification = PushNotification(
            title="✅ Retrait traité",
            body=f"Votre retrait de {amount} {currency} est en cours de traitement",
            token=user_token,
            data={
                "type": "payout_processed",
                "amount": str(amount),
                "currency": currency,
                "method": method
            },
            priority=NotificationPriority.HIGH,
            category=NotificationCategory.PAYMENT,
            click_action="/payouts/history"
        )
        return self.send_notification(notification)

    def send_account_verification(
        self,
        user_token: str,
        verification_status: str = "approved"
    ) -> Dict[str, Any]:
        """Send account verification notification"""
        if verification_status == "approved":
            title = "✅ Compte vérifié"
            body = "Votre compte a été vérifié avec succès"
        else:
            title = "⚠️ Vérification requise"
            body = "Des informations supplémentaires sont nécessaires"

        notification = PushNotification(
            title=title,
            body=body,
            token=user_token,
            data={
                "type": "account_verification",
                "status": verification_status
            },
            priority=NotificationPriority.HIGH,
            category=NotificationCategory.SYSTEM,
            click_action="/profile/verification"
        )
        return self.send_notification(notification)

    def send_social_post_performance(
        self,
        user_token: str,
        platform: str,
        views: int,
        engagement_rate: float
    ) -> Dict[str, Any]:
        """Send social media post performance notification"""
        notification = PushNotification(
            title=f"📊 Performance {platform}",
            body=f"Votre post a atteint {views:,} vues avec {engagement_rate:.1f}% d'engagement",
            token=user_token,
            data={
                "type": "social_performance",
                "platform": platform,
                "views": str(views),
                "engagement_rate": str(engagement_rate)
            },
            priority=NotificationPriority.NORMAL,
            category=NotificationCategory.SOCIAL,
            click_action="/analytics/social"
        )
        return self.send_notification(notification)

    def send_custom(
        self,
        user_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        click_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send custom notification"""
        notification = PushNotification(
            title=title,
            body=body,
            token=user_token,
            data=data,
            priority=priority,
            category=category,
            click_action=click_action
        )
        return self.send_notification(notification)


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    service = PushNotificationService()

    if service.is_available():
        # Example 1: Payment confirmation
        result = service.send_payment_confirmation(
            user_token="example_device_token",
            amount=100.50,
            currency="MAD",
            transaction_id="txn_12345"
        )
        print("Payment notification:", result)

        # Example 2: Commission earned
        result = service.send_commission_earned(
            user_token="example_device_token",
            amount=25.00,
            product_name="iPhone 15 Pro"
        )
        print("Commission notification:", result)

        # Example 3: Broadcast to topic
        notification = PushNotification(
            title="📢 Nouvelle fonctionnalité",
            body="Découvrez notre nouveau système de paiement mobile",
            topic="all_users",
            priority=NotificationPriority.NORMAL,
            category=NotificationCategory.MARKETING
        )
        result = service.send_notification(notification)
        print("Broadcast notification:", result)
    else:
        print("Push notification service not available")
