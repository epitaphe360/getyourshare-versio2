"""
SERVICE DE NOTIFICATIONS EMAIL
Système complet de gestion des emails pour ShareYourSales

Providers supportés:
- Resend (recommandé pour production)
- SendGrid (backup)
- SMTP générique (fallback)

Types d'emails:
1. Emails transactionnels (confirmation, facture, etc.)
2. Emails marketing (newsletters, promotions)
3. Emails système (alertes, notifications)

Author: ShareYourSales Team
Date: 2026-01-04
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests

logger = logging.getLogger(__name__)

# ============================================
# EMAIL TEMPLATES
# ============================================

EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Bienvenue sur ShareYourSales! 🎉",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Bienvenue {name}!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Merci de vous être inscrit sur ShareYourSales! Nous sommes ravis de vous compter parmi nous.</p>
                <p>Voici ce que vous pouvez faire maintenant:</p>
                <ul>
                    <li>Compléter votre profil</li>
                    <li>Explorer le catalogue de produits</li>
                    <li>Créer vos premiers liens d'affiliation</li>
                </ul>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Accéder à mon dashboard
                    </a>
                </div>
                <p style="color: #666; font-size: 12px;">
                    Si vous avez des questions, n'hésitez pas à nous contacter à support@shareyoursales.com
                </p>
            </div>
        </body>
        </html>
        """
    },

    "email_verification": {
        "subject": "Vérifiez votre email - ShareYourSales",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Vérification de votre email</h2>
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Merci de vous être inscrit! Pour activer votre compte, veuillez vérifier votre adresse email en cliquant sur le bouton ci-dessous:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Vérifier mon email
                    </a>
                </div>
                <p style="color: #666; font-size: 12px;">
                    Ce lien expire dans 24 heures. Si vous n'avez pas créé de compte, ignorez cet email.
                </p>
                <p style="color: #666; font-size: 12px;">
                    Si le bouton ne fonctionne pas, copiez ce lien: {verification_url}
                </p>
            </div>
        </body>
        </html>
        """
    },

    "password_reset": {
        "subject": "Réinitialisation de mot de passe - ShareYourSales",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Réinitialisation de mot de passe</h2>
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Réinitialiser mon mot de passe
                    </a>
                </div>
                <p style="color: #666; font-size: 12px;">
                    Ce lien expire dans 1 heure. Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
                </p>
            </div>
        </body>
        </html>
        """
    },

    "payment_confirmation": {
        "subject": "Confirmation de paiement - Commande #{order_id}",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>✅ Paiement confirmé</h2>
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Votre paiement a été confirmé avec succès!</p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Commande:</strong></td>
                            <td style="text-align: right;">#{order_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Montant:</strong></td>
                            <td style="text-align: right; color: #28a745; font-size: 18px;">{amount} {currency}</td>
                        </tr>
                        <tr>
                            <td><strong>Méthode:</strong></td>
                            <td style="text-align: right;">{payment_method}</td>
                        </tr>
                        <tr>
                            <td><strong>Date:</strong></td>
                            <td style="text-align: right;">{payment_date}</td>
                        </tr>
                    </table>
                </div>
                <p>Vous recevrez un email de confirmation séparé avec les détails de livraison.</p>
            </div>
        </body>
        </html>
        """
    },

    "commission_earned": {
        "subject": "💰 Nouvelle commission gagnée - {amount} {currency}",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #28a745; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">💰 Nouvelle Commission!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <p>Félicitations <strong>{name}</strong>!</p>
                <p>Vous venez de gagner une nouvelle commission:</p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <div style="font-size: 36px; color: #28a745; font-weight: bold;">
                        {amount} {currency}
                    </div>
                    <div style="color: #666; margin-top: 10px;">
                        Commission sur la vente #{sale_id}
                    </div>
                </div>
                <p>Détails de la vente:</p>
                <ul>
                    <li>Produit: {product_name}</li>
                    <li>Montant vente: {sale_amount} {currency}</li>
                    <li>Taux commission: {commission_rate}%</li>
                    <li>Date: {sale_date}</li>
                </ul>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{dashboard_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Voir mes gains
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    },

    "payout_processed": {
        "subject": "💸 Paiement effectué - {amount} {currency}",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>💸 Votre paiement a été traité</h2>
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Votre demande de retrait a été approuvée et traitée:</p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Montant:</strong></td>
                            <td style="text-align: right; font-size: 20px; color: #28a745;">{amount} {currency}</td>
                        </tr>
                        <tr>
                            <td><strong>Méthode:</strong></td>
                            <td style="text-align: right;">{payout_method}</td>
                        </tr>
                        <tr>
                            <td><strong>Référence:</strong></td>
                            <td style="text-align: right;">#{payout_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Date:</strong></td>
                            <td style="text-align: right;">{payout_date}</td>
                        </tr>
                    </table>
                </div>
                <p>Le montant sera crédité sur votre compte sous 2-5 jours ouvrés.</p>
            </div>
        </body>
        </html>
        """
    },

    "new_lead": {
        "subject": "🎯 Nouveau lead reçu - {service_name}",
        "template": """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>🎯 Nouveau Lead!</h2>
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Vous avez reçu un nouveau lead pour votre service <strong>{service_name}</strong>:</p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Client:</strong> {client_name}</p>
                    <p><strong>Email:</strong> {client_email}</p>
                    <p><strong>Téléphone:</strong> {client_phone}</p>
                    <p><strong>Message:</strong><br>{client_message}</p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{lead_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Voir le lead
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    }
}

# ============================================
# RESEND EMAIL SERVICE
# ============================================

class ResendEmailService:
    """
    Service d'envoi d'emails via Resend API
    Documentation: https://resend.com/docs
    """

    def __init__(self, api_key: str, from_email: str = "noreply@shareyoursales.com"):
        """
        Initialise le service Resend

        Args:
            api_key: Clé API Resend
            from_email: Email expéditeur par défaut
        """
        self.api_key = api_key
        self.from_email = from_email
        self.base_url = "https://api.resend.com"

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Envoie un email via Resend

        Args:
            to: Email destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML
            from_email: Email expéditeur (override)
            reply_to: Email de réponse
            cc: Liste emails en copie
            bcc: Liste emails en copie cachée
            attachments: Liste de pièces jointes
            tags: Tags pour tracking

        Returns:
            Dict avec résultat de l'envoi
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": from_email or self.from_email,
            "to": [to] if isinstance(to, str) else to,
            "subject": subject,
            "html": html_content
        }

        if reply_to:
            payload["reply_to"] = reply_to

        if cc:
            payload["cc"] = cc

        if bcc:
            payload["bcc"] = bcc

        if attachments:
            payload["attachments"] = attachments

        if tags:
            payload["tags"] = tags

        try:
            response = requests.post(
                f"{self.base_url}/emails",
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"Email sent successfully via Resend to {to}")

            return {
                "success": True,
                "message_id": data.get("id"),
                "provider": "resend"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Resend API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "resend"
            }

# ============================================
# SMTP EMAIL SERVICE (Fallback)
# ============================================

class SMTPEmailService:
    """
    Service d'envoi d'emails via SMTP générique
    Peut être utilisé avec Gmail, Office365, etc.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        use_tls: bool = True
    ):
        """
        Initialise le service SMTP

        Args:
            smtp_host: Serveur SMTP
            smtp_port: Port SMTP
            smtp_user: Utilisateur SMTP
            smtp_password: Mot de passe SMTP
            from_email: Email expéditeur
            use_tls: Utiliser TLS/SSL
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.use_tls = use_tls

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envoie un email via SMTP

        Args:
            to: Email destinataire
            subject: Sujet
            html_content: Contenu HTML
            from_email: Email expéditeur (override)
            reply_to: Email de réponse

        Returns:
            Dict avec résultat
        """
        try:
            # Créer message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email or self.from_email
            msg["To"] = to

            if reply_to:
                msg["Reply-To"] = reply_to

            # Ajouter contenu HTML
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Envoyer via SMTP
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully via SMTP to {to}")

            return {
                "success": True,
                "provider": "smtp"
            }

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "smtp"
            }

# ============================================
# NOTIFICATION SERVICE (Unified)
# ============================================

class EmailNotificationService:
    """
    Service unifié de notifications email
    Supporte multiples providers avec fallback
    """

    def __init__(self):
        """Initialise le service avec config depuis ENV"""
        self.resend = None
        self.smtp = None

        # Configurer Resend si disponible
        resend_api_key = os.getenv("RESEND_API_KEY")
        if resend_api_key:
            self.resend = ResendEmailService(
                api_key=resend_api_key,
                from_email=os.getenv("FROM_EMAIL", "noreply@shareyoursales.com")
            )

        # Configurer SMTP si disponible
        smtp_host = os.getenv("SMTP_HOST")
        if smtp_host:
            self.smtp = SMTPEmailService(
                smtp_host=smtp_host,
                smtp_port=int(os.getenv("SMTP_PORT", 587)),
                smtp_user=os.getenv("SMTP_USER", ""),
                smtp_password=os.getenv("SMTP_PASSWORD", ""),
                from_email=os.getenv("FROM_EMAIL", "noreply@shareyoursales.com"),
                use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            )

    def send_template_email(
        self,
        to: str,
        template_name: str,
        variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Envoie un email en utilisant un template

        Args:
            to: Email destinataire
            template_name: Nom du template
            variables: Variables pour le template

        Returns:
            Dict avec résultat
        """
        if template_name not in EMAIL_TEMPLATES:
            return {
                "success": False,
                "error": f"Template {template_name} not found"
            }

        template = EMAIL_TEMPLATES[template_name]
        subject = template["subject"].format(**variables)
        html_content = template["template"].format(**variables)

        return self.send_email(to, subject, html_content)

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envoie un email avec fallback automatique

        Args:
            to: Email destinataire
            subject: Sujet
            html_content: Contenu HTML
            **kwargs: Paramètres additionnels

        Returns:
            Dict avec résultat
        """
        # Essayer Resend en premier
        if self.resend:
            result = self.resend.send_email(to, subject, html_content, **kwargs)
            if result.get("success"):
                return result

            logger.warning(f"Resend failed, trying SMTP fallback: {result.get('error')}")

        # Fallback sur SMTP
        if self.smtp:
            return self.smtp.send_email(to, subject, html_content, **kwargs)

        # Aucun provider disponible
        logger.error("No email provider configured!")
        return {
            "success": False,
            "error": "No email provider configured"
        }

    def is_configured(self) -> bool:
        """Vérifie si au moins un provider est configuré"""
        return self.resend is not None or self.smtp is not None
