"""
Smart Notifications Multi-canal
Email, SMS, Push, In-App, WhatsApp avec routage intelligent
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import requests

from utils.logger import logger
from supabase_client import supabase
from services.email_service import email_service


class NotificationChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    SLACK = "slack"


class NotificationPriority(Enum):
    """Priorités de notification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SmartNotificationService:
    """Service de notifications intelligent multi-canal"""

    def __init__(self):
        # Configuration SMTP
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

        # Twilio pour SMS
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')

        # Firebase Cloud Messaging pour Push
        self.fcm_server_key = os.getenv('FCM_SERVER_KEY')

        # WhatsApp Business API
        self.whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

        # Slack Webhooks
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

        # Préférences utilisateurs (stocké en DB normalement)
        self.user_preferences = {}

        # Compteurs pour rate limiting
        self.notification_counts = {}

    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Dict[str, bool]:
        """
        Envoyer notification avec routage intelligent

        Args:
            user_id: ID utilisateur
            title: Titre notification
            message: Message
            notification_type: Type (info, success, warning, error)
            priority: Priorité
            data: Données additionnelles
            channels: Canaux forcés (sinon auto-sélection)

        Returns:
            Dict avec succès par canal: {'email': True, 'sms': False, ...}
        """
        # Récupérer préférences utilisateur
        preferences = await self._get_user_preferences(user_id)

        # Déterminer canaux à utiliser
        if channels is None:
            channels = await self._select_channels(
                user_id,
                priority,
                notification_type,
                preferences
            )

        # Envoyer sur chaque canal
        results = {}

        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    success = await self._send_email(user_id, title, message, data)
                    results['email'] = success

                elif channel == NotificationChannel.SMS:
                    success = await self._send_sms(user_id, message)
                    results['sms'] = success

                elif channel == NotificationChannel.PUSH:
                    success = await self._send_push(user_id, title, message, data)
                    results['push'] = success

                elif channel == NotificationChannel.IN_APP:
                    success = await self._send_in_app(user_id, title, message, data)
                    results['in_app'] = success

                elif channel == NotificationChannel.WHATSAPP:
                    success = await self._send_whatsapp(user_id, message)
                    results['whatsapp'] = success

                elif channel == NotificationChannel.SLACK:
                    success = await self._send_slack(title, message, data)
                    results['slack'] = success

            except Exception as e:
                logger.error(f"Notification failed on {channel.value}: {e}")
                results[channel.value] = False

        # Logger résultats
        successful = sum(1 for v in results.values() if v)
        logger.info(
            f"Notification sent to user {user_id}: "
            f"{successful}/{len(results)} channels successful"
        )

        return results

    async def _send_email(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Envoyer email via EmailService"""
        try:
            # Récupérer email utilisateur
            user_email = await self._get_user_email(user_id)
            if not user_email:
                return False

            # Envoyer via EmailService
            html_content = email_service._fallback_template({'content': f"<h2>{title}</h2><p>{message}</p>"})
            
            return email_service.send_email(
                to_email=user_email,
                subject=title,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def _send_sms(self, user_id: str, message: str) -> bool:
        """Envoyer SMS via Twilio"""
        if not self.twilio_sid or not self.twilio_token:
            logger.warning("Twilio not configured")
            return False

        try:
            from twilio.rest import Client

            user_phone = await self._get_user_phone(user_id)
            if not user_phone:
                return False

            client = Client(self.twilio_sid, self.twilio_token)

            client.messages.create(
                body=message[:160],  # Limite SMS
                from_=self.twilio_phone,
                to=user_phone
            )

            logger.info(f"SMS sent to {user_phone}")
            return True

        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False

    async def _send_push(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Envoyer push notification via FCM"""
        if not self.fcm_server_key:
            logger.warning("FCM not configured")
            return False

        try:
            # Récupérer device tokens utilisateur
            device_tokens = await self._get_user_device_tokens(user_id)
            if not device_tokens:
                return False

            url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'registration_ids': device_tokens,
                'notification': {
                    'title': title,
                    'body': message,
                    'icon': '/logo192.png',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                },
                'data': data or {}
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"Push sent to {len(device_tokens)} devices")
            return True

        except Exception as e:
            logger.error(f"Push send failed: {e}")
            return False

    async def _send_in_app(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Créer notification in-app (stockée en DB)"""
        try:
            # En production: INSERT dans table notifications
            notification = {
                'user_id': user_id,
                'title': title,
                'message': message,
                'data': data,
                'read': False,
                'created_at': datetime.utcnow().isoformat()
            }

            # Ici: stocker en DB
            # db.notifications.insert(notification)

            # Publier via WebSocket pour notification temps réel
            # await realtime_analytics.broadcast_metric(
            #     'notification',
            #     notification,
            #     dashboard_type=f'user:{user_id}'
            # )

            logger.info(f"In-app notification created for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"In-app notification failed: {e}")
            return False

    async def _send_whatsapp(self, user_id: str, message: str) -> bool:
        """Envoyer message WhatsApp Business"""
        if not self.whatsapp_token:
            logger.warning("WhatsApp not configured")
            return False

        try:
            user_phone = await self._get_user_phone(user_id, international=True)
            if not user_phone:
                return False

            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'to': user_phone,
                'type': 'text',
                'text': {'body': message}
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"WhatsApp sent to {user_phone}")
            return True

        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return False

    async def _send_slack(
        self,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Envoyer notification Slack (pour équipe)"""
        if not self.slack_webhook:
            logger.warning("Slack not configured")
            return False

        try:
            payload = {
                'text': title,
                'blocks': [
                    {
                        'type': 'header',
                        'text': {'type': 'plain_text', 'text': title}
                    },
                    {
                        'type': 'section',
                        'text': {'type': 'mrkdwn', 'text': message}
                    }
                ]
            }

            if data:
                payload['blocks'].append({
                    'type': 'context',
                    'elements': [
                        {'type': 'mrkdwn', 'text': f"*Data:* `{data}`"}
                    ]
                })

            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Slack notification sent")
            return True

        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return False

    async def _select_channels(
        self,
        user_id: str,
        priority: NotificationPriority,
        notification_type: str,
        preferences: Dict
    ) -> List[NotificationChannel]:
        """
        Sélection intelligente des canaux selon contexte

        Règles:
        - URGENT: Email + SMS + Push
        - HIGH: Email + Push
        - MEDIUM: Push + In-App
        - LOW: In-App seulement

        + Respect des préférences utilisateur
        """
        channels = []

        # Déterminer canaux selon priorité
        if priority == NotificationPriority.URGENT:
            channels = [
                NotificationChannel.EMAIL,
                NotificationChannel.SMS,
                NotificationChannel.PUSH,
                NotificationChannel.IN_APP
            ]
        elif priority == NotificationPriority.HIGH:
            channels = [
                NotificationChannel.EMAIL,
                NotificationChannel.PUSH,
                NotificationChannel.IN_APP
            ]
        elif priority == NotificationPriority.MEDIUM:
            channels = [
                NotificationChannel.PUSH,
                NotificationChannel.IN_APP
            ]
        else:  # LOW
            channels = [NotificationChannel.IN_APP]

        # Filtrer selon préférences utilisateur
        enabled_channels = preferences.get('enabled_channels', [])
        if enabled_channels:
            channels = [
                c for c in channels
                if c.value in enabled_channels
            ]

        # Rate limiting: ne pas spammer
        if not await self._check_rate_limit(user_id):
            # Garder seulement in-app si rate limited
            channels = [NotificationChannel.IN_APP]

        return channels

    async def _check_rate_limit(self, user_id: str) -> bool:
        """Vérifier si l'utilisateur n'est pas rate limited"""
        key = f"notif_count:{user_id}"

        # Limite: max 10 notifications par heure
        count = self.notification_counts.get(key, 0)

        if count >= 10:
            logger.warning(f"User {user_id} rate limited (10/hour)")
            return False

        self.notification_counts[key] = count + 1
        return True

    def _generate_email_html(
        self,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> str:
        """Générer template HTML email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f7fafc; padding: 30px; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #718096; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            <p>{message}</p>
        </div>
        <div class="footer">
            <p>GetYourShare &copy; 2025</p>
        </div>
    </div>
</body>
</html>
"""

    # Méthodes de récupération données utilisateur
    async def _get_user_preferences(self, user_id: str) -> Dict:
        """Récupérer préférences utilisateur"""
        # TODO: Implémenter table user_preferences
        return {
            'enabled_channels': ['email', 'push', 'in_app'],
            'quiet_hours': {'start': 22, 'end': 8},
            'email_frequency': 'immediate'
        }

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Récupérer email utilisateur"""
        try:
            result = supabase.table('users').select('email').eq('id', user_id).single().execute()
            return result.data['email'] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None

    async def _get_user_phone(
        self,
        user_id: str,
        international: bool = False
    ) -> Optional[str]:
        """Récupérer téléphone utilisateur"""
        try:
            result = supabase.table('users').select('phone').eq('id', user_id).single().execute()
            return result.data['phone'] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user phone: {e}")
            return None

    async def _get_user_device_tokens(self, user_id: str) -> List[str]:
        """Récupérer device tokens FCM"""
        # TODO: Implémenter table device_tokens
        return []


# Instance globale
notification_service = SmartNotificationService()
