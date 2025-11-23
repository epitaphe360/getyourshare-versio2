"""
Tâches Celery pour les notifications

Notifications envoyées:
- Token OAuth expirant bientôt
- Échec de synchronisation
- Rapports hebdomadaires
- Nouvelles demandes d'affiliation
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from database import get_db_connection

logger = get_task_logger(__name__)

# Configuration email
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@shareyoursales.ma')

def mask_email(email: str) -> str:
    """Masquer l'email pour les logs"""
    if not email or "@" not in email:
        return "******"
    try:
        user, domain = email.split("@")
        if len(user) > 1:
            return f"{user[0]}***@{domain}"
        return f"***@{domain}"
    except:
        return "******"

# ============================================
# TÂCHES DE NOTIFICATION
# ============================================

@shared_task(
    name='celery_tasks.notification_tasks.notify_expiring_tokens',
    bind=True
)
def notify_expiring_tokens(self, days_before: int = 3):
    """
    Notifier les influenceurs dont les tokens expirent bientôt

    Args:
        days_before: Nombre de jours avant expiration
    """
    try:
        logger.info(f"📧 Notifying users about tokens expiring in {days_before} days")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les connexions expirant bientôt
        cursor.execute("""
            SELECT
                smc.id,
                smc.user_id,
                smc.platform,
                smc.token_expires_at,
                u.email,
                u.full_name,
                EXTRACT(DAY FROM (smc.token_expires_at - NOW()))::INTEGER as days_until_expiry
            FROM social_media_connections smc
            JOIN users u ON smc.user_id = u.id
            WHERE smc.connection_status = 'active'
            AND smc.token_expires_at IS NOT NULL
            AND smc.token_expires_at <= NOW() + INTERVAL '%s days'
            AND smc.token_expires_at > NOW()
            -- Éviter de spammer: notifier seulement une fois
            AND NOT EXISTS (
                SELECT 1 FROM notifications
                WHERE user_id = smc.user_id
                AND type = 'token_expiring'
                AND metadata->>'connection_id' = smc.id::text
                AND created_at > NOW() - INTERVAL '7 days'
            )
        """, (days_before,))

        connections = cursor.fetchall()

        logger.info(f"Found {len(connections)} connections with expiring tokens")

        notifications_sent = 0

        for conn_data in connections:
            connection_id, user_id, platform, expires_at, email, full_name, days_left = conn_data

            try:
                # Envoyer l'email
                send_token_expiration_email.delay(
                    email=email,
                    full_name=full_name,
                    platform=platform,
                    days_left=days_left
                )

                # Créer une notification dans la DB
                cursor.execute("""
                    INSERT INTO notifications (user_id, type, title, message, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id,
                    'token_expiring',
                    f'Token {platform} expirant bientôt',
                    f'Votre connexion {platform} expire dans {days_left} jour(s). Reconnectez votre compte pour continuer à suivre vos statistiques.',
                    {'connection_id': str(connection_id), 'platform': platform, 'days_left': days_left}
                ))

                notifications_sent += 1

            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {str(e)}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ Sent {notifications_sent} token expiration notifications")

        return {
            'total_expiring': len(connections),
            'notifications_sent': notifications_sent,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Token expiration notification failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='celery_tasks.notification_tasks.send_token_expiration_email',
    rate_limit='50/m'
)
def send_token_expiration_email(email: str, full_name: str, platform: str, days_left: int):
    """
    Envoyer un email de notification de token expirant
    """
    try:
        subject = f"🔔 Votre connexion {platform} expire bientôt"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ShareYourSales</h1>
                    <p>Notification importante</p>
                </div>
                <div class="content">
                    <p>Bonjour {full_name},</p>

                    <div class="warning">
                        ⚠️ <strong>Votre connexion {platform} expire dans {days_left} jour(s)</strong>
                    </div>

                    <p>
                        Pour continuer à bénéficier de la synchronisation automatique de vos statistiques {platform},
                        vous devez reconnecter votre compte.
                    </p>

                    <p>
                        Sans reconnexion, nous ne pourrons plus récupérer vos statistiques et votre profil
                        ne sera plus à jour pour les marchands.
                    </p>

                    <center>
                        <a href="https://shareyoursales.ma/influencer/social-media" class="button">
                            Reconnecter mon compte {platform}
                        </a>
                    </center>

                    <p>
                        Cette opération est rapide (moins de 30 secondes) et vos données ne seront pas perdues.
                    </p>

                    <hr>
                    <p style="font-size: 12px; color: #6b7280;">
                        Vous recevez cet email car vous avez connecté votre compte {platform} sur ShareYourSales.
                        <br>
                        Si vous ne souhaitez plus recevoir ces notifications, vous pouvez déconnecter votre compte
                        depuis vos paramètres.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        send_email(
            to_email=email,
            subject=subject,
            html_body=html_body
        )

        masked = mask_email(email)
        logger.info(f"✅ Token expiration email sent to {masked}")

        return {'status': 'sent', 'email': masked}

    except Exception as exc:
        logger.error(f"❌ Failed to send email to {mask_email(email)}: {str(exc)}")
        raise


@shared_task(
    name='celery_tasks.notification_tasks.notify_sync_failure',
    bind=True
)
def notify_sync_failure(self, user_id: str, platform: str, error_message: str):
    """
    Notifier un utilisateur d'un échec de synchronisation persistant
    """
    try:
        logger.info(f"📧 Notifying user {user_id} about sync failure for {platform}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer l'email de l'utilisateur
        cursor.execute("SELECT email, full_name FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"User {user_id} not found")
            return

        email, full_name = result

        # Créer une notification
        cursor.execute("""
            INSERT INTO notifications (user_id, type, title, message, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            'sync_failure',
            f'Erreur de synchronisation {platform}',
            f'Nous rencontrons des difficultés à synchroniser votre compte {platform}. Veuillez vérifier votre connexion.',
            {'platform': platform, 'error': error_message}
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # Envoyer l'email (si échec répété depuis 3 jours)
        send_sync_failure_email.delay(
            email=email,
            full_name=full_name,
            platform=platform,
            error_message=error_message
        )

        logger.info(f"✅ Sync failure notification sent to {mask_email(email)}")

        return {'status': 'notified', 'user_id': user_id}

    except Exception as exc:
        logger.error(f"❌ Sync failure notification failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='celery_tasks.notification_tasks.send_sync_failure_email',
    rate_limit='20/m'
)
def send_sync_failure_email(email: str, full_name: str, platform: str, error_message: str):
    """
    Envoyer un email de notification d'échec de synchronisation
    """
    try:
        subject = f"⚠️ Problème avec votre compte {platform}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ef4444;">⚠️ Problème de synchronisation</h2>

                <p>Bonjour {full_name},</p>

                <p>
                    Nous rencontrons des difficultés à synchroniser votre compte {platform} depuis plusieurs jours.
                </p>

                <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0;">
                    <strong>Erreur:</strong> {error_message}
                </div>

                <p><strong>Solutions possibles:</strong></p>
                <ul>
                    <li>Reconnecter votre compte {platform}</li>
                    <li>Vérifier que vous n'avez pas révoqué l'accès à ShareYourSales</li>
                    <li>Vérifier que votre compte {platform} est toujours actif</li>
                </ul>

                <center>
                    <a href="https://shareyoursales.ma/influencer/social-media"
                       style="display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                        Résoudre le problème
                    </a>
                </center>

                <p>
                    Si le problème persiste, contactez notre support: support@shareyoursales.ma
                </p>
            </div>
        </body>
        </html>
        """

        send_email(
            to_email=email,
            subject=subject,
            html_body=html_body
        )

        logger.info(f"✅ Sync failure email sent to {mask_email(email)}")

    except Exception as exc:
        logger.error(f"❌ Failed to send sync failure email: {str(exc)}")
        raise


# ============================================
# FONCTION UTILITAIRE D'ENVOI D'EMAIL
# ============================================

def send_email(to_email: str, subject: str, html_body: str):
    """
    Fonction utilitaire pour envoyer un email via SMTP

    Args:
        to_email: Adresse email du destinataire
        subject: Sujet de l'email
        html_body: Corps HTML de l'email
    """
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Ajouter le corps HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Connexion SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ Email sent successfully to {mask_email(to_email)}")

    except Exception as e:
        logger.error(f"❌ Failed to send email to {mask_email(to_email)}: {str(e)}")
        raise


@shared_task(
    name='celery_tasks.notification_tasks.send_email_task',
    rate_limit='50/m'
)
def send_email_task(to_email: str, subject: str, html_body: str):
    """
    Tâche Celery pour envoyer un email
    """
    return send_email(to_email=to_email, subject=subject, html_body=html_body)
