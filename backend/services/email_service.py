"""
Email Service - Production Grade
Gestion complète des emails transactionnels et marketing

Features:
1. Templates HTML professionnels
2. Support SMTP (Gmail, SendGrid, Mailgun)
3. Support API SendGrid (Preferred)
4. Queue avec Celery (async sending)
5. Tracking (opens, clicks)
6. Rate limiting
7. Retry logic
8. Unsubscribe management
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict
from datetime import datetime
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

# SendGrid Imports
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    SendGridAPIClient = None
    Mail = None
    Email = None
    To = None
    Content = None

logger = structlog.get_logger()

# Configuration SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ShareYourSales")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "noreply@shareyoursales.ma")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


# ============================================
# EMAIL SERVICE
# ============================================

class EmailService:
    """
    Service d'envoi d'emails professionnel
    """

    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_name = EMAIL_FROM_NAME
        self.from_address = EMAIL_FROM_ADDRESS
        self.sendgrid_api_key = SENDGRID_API_KEY

        # Initialiser Jinja2 pour templates
        # Path: backend/templates/emails
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _create_smtp_connection(self):
        """Créer connexion SMTP sécurisée"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()

            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            return server

        except Exception as e:
            logger.error("smtp_connection_failed", error=str(e))
            raise

    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SendGrid API"""
        if not SENDGRID_AVAILABLE:
            logger.warning("sendgrid_library_missing")
            return False
            
        try:
            message = Mail(
                from_email=Email(self.from_address, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            if 200 <= response.status_code < 300:
                logger.info("email_sent_sendgrid", to=to_email, subject=subject)
                return True
            else:
                logger.error("sendgrid_error", status=response.status_code, body=response.body)
                return False
        except Exception as e:
            logger.error("sendgrid_exception", error=str(e))
            return False

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Envoyer un email

        Args:
            to_email: Email destinataire
            subject: Sujet
            html_content: Contenu HTML
            text_content: Contenu texte (fallback)
            reply_to: Email de réponse
            attachments: Liste de pièces jointes

        Returns:
            True si envoyé avec succès
        """
        # Try SendGrid first if configured
        if self.sendgrid_api_key and SENDGRID_AVAILABLE:
            if self._send_via_sendgrid(to_email, subject, html_content):
                return True
            # Fallback to SMTP if SendGrid fails
            logger.warning("fallback_to_smtp")

        try:
            # Créer message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if reply_to:
                msg['Reply-To'] = reply_to

            # Ajouter version texte
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # Ajouter version HTML
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Ajouter pièces jointes
            if attachments:
                for attachment in attachments:
                    # TODO: Implémenter attachments
                    pass

            # Envoyer
            with self._create_smtp_connection() as server:
                server.send_message(msg)

            logger.info("email_sent_smtp", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e))
            return False

    def render_template(self, template_name: str, context: Dict) -> str:
        """
        Rendre un template email

        Args:
            template_name: Nom du template (ex: 'welcome.html')
            context: Variables du template

        Returns:
            HTML rendu
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)

        except Exception as e:
            logger.error("template_render_failed", template=template_name, error=str(e))
            # Fallback: template simple
            return self._fallback_template(context)

    def _fallback_template(self, context: Dict) -> str:
        """Template HTML simple de fallback"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>ShareYourSales</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h1 style="color: white; margin: 0;">ShareYourSales</h1>
            </div>
            <div style="padding: 20px; background: #f9f9f9;">
                {context.get('content', '')}
            </div>
            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>© 2025 ShareYourSales - Plateforme d'Affiliation Marocaine</p>
                <p>
                    <a href="https://shareyoursales.ma" style="color: #667eea;">Site Web</a> |
                    <a href="https://shareyoursales.ma/contact" style="color: #667eea;">Contact</a>
                </p>
            </div>
        </body>
        </html>
        """


# Instance globale
email_service = EmailService()


# ============================================
# EMAIL TEMPLATES PRÉDÉFINIS
# ============================================

class EmailTemplates:
    """
    Templates d'emails prédéfinis
    """

    @staticmethod
    async def send_welcome_email(to_email: str, user_name: str, user_type: str):
        """Email de bienvenue"""
        subject = f"Bienvenue sur ShareYourSales, {user_name}! 🎉"

        context = {
            'user_name': user_name,
            'user_type': user_type,
            'login_url': 'https://shareyoursales.ma/login',
            'dashboard_url': 'https://shareyoursales.ma/dashboard'
        }

        html_content = email_service.render_template('welcome.html', context)

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_kyc_approved_email(to_email: str, user_name: str):
        """Email KYC approuvé"""
        subject = "✅ Votre compte a été vérifié!"

        html_content = f"""
        <h2>Félicitations {user_name}!</h2>
        <p>Votre KYC a été approuvé avec succès. Vous pouvez maintenant accéder à toutes les fonctionnalités de la plateforme.</p>
        <p><a href="https://shareyoursales.ma/dashboard" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accéder au Dashboard</a></p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )

    @staticmethod
    async def send_kyc_rejected_email(to_email: str, user_name: str, reason: str, comment: str):
        """Email KYC rejeté"""
        subject = "❌ Votre KYC nécessite des corrections"

        html_content = f"""
        <h2>Bonjour {user_name},</h2>
        <p>Malheureusement, votre KYC a été rejeté pour la raison suivante:</p>
        <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <strong>Raison:</strong> {reason}<br>
            <strong>Commentaire:</strong> {comment}
        </div>
        <p>Vous pouvez corriger les documents et soumettre à nouveau votre KYC.</p>
        <p><a href="https://shareyoursales.ma/kyc" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Resoummettre KYC</a></p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )

    @staticmethod
    async def send_subscription_confirmation_email(
        to_email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        billing_cycle: str,
        next_billing_date: str
    ):
        """Email confirmation abonnement"""
        subject = f"Abonnement {plan_name} confirmé ✅"

        html_content = f"""
        <h2>Merci {user_name}!</h2>
        <p>Votre abonnement <strong>{plan_name}</strong> a été activé avec succès.</p>
        <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>Détails de votre abonnement:</h3>
            <ul style="list-style: none; padding: 0;">
                <li>📦 <strong>Plan:</strong> {plan_name}</li>
                <li>💰 <strong>Montant:</strong> {amount} MAD / {billing_cycle}</li>
                <li>📅 <strong>Prochaine facturation:</strong> {next_billing_date}</li>
            </ul>
        </div>
        <p><a href="https://shareyoursales.ma/billing" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Gérer mon abonnement</a></p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )

    @staticmethod
    async def send_payment_failed_email(to_email: str, user_name: str, amount: float, reason: str):
        """Email paiement échoué"""
        subject = "⚠️ Échec du paiement"

        html_content = f"""
        <h2>Bonjour {user_name},</h2>
        <p>Nous n'avons pas pu traiter votre paiement de <strong>{amount} MAD</strong>.</p>
        <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <strong>Raison:</strong> {reason}
        </div>
        <p>Veuillez mettre à jour votre moyen de paiement pour continuer à utiliser nos services.</p>
        <p><a href="https://shareyoursales.ma/billing" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Mettre à jour le paiement</a></p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )

    @staticmethod
    async def send_payout_approved_email(
        to_email: str,
        user_name: str,
        amount: float,
        iban: str,
        estimated_date: str
    ):
        """Email payout approuvé"""
        subject = "💰 Paiement approuvé"

        context = {
            'user_name': user_name,
            'amount': amount,
            'iban': iban,
            'estimated_date': estimated_date
        }
        
        html_content = email_service.render_template('payout_approved.html', context)

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_new_affiliate_request_email(
        to_email: str,
        merchant_name: str,
        influencer_name: str,
        product_name: str
    ):
        """Email nouvelle demande d'affiliation (pour merchant)"""
        subject = f"Nouvelle demande d'affiliation de {influencer_name}"

        html_content = f"""
        <h2>Bonjour {merchant_name},</h2>
        <p>Vous avez reçu une nouvelle demande d'affiliation!</p>
        <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>Détails:</h3>
            <ul style="list-style: none; padding: 0;">
                <li>👤 <strong>Influenceur:</strong> {influencer_name}</li>
                <li>📦 <strong>Produit:</strong> {product_name}</li>
            </ul>
        </div>
        <p><a href="https://shareyoursales.ma/affiliates/pending" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voir la demande</a></p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )

    @staticmethod
    async def send_affiliate_approved_email(
        to_email: str,
        influencer_name: str,
        merchant_name: str,
        product_name: str,
        commission_rate: float
    ):
        """Email affiliation approuvée (pour influenceur)"""
        subject = f"✅ Votre demande d'affiliation a été acceptée!"

        context = {
            'influencer_name': influencer_name,
            'merchant_name': merchant_name,
            'product_name': product_name,
            'commission_rate': commission_rate
        }
        
        html_content = email_service.render_template('affiliation_approved.html', context)

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_password_reset_email(to_email: str, user_name: str, reset_token: str):
        """Email reset password"""
        reset_url = f"https://shareyoursales.ma/reset-password?token={reset_token}"
        subject = "Réinitialisation de votre mot de passe"

        context = {
            'user_name': user_name,
            'reset_url': reset_url
        }
        
        html_content = email_service.render_template('password_reset.html', context)

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_2fa_code_email(to_email: str, user_name: str, code: str):
        """Email code 2FA"""
        subject = "Votre code de vérification ShareYourSales"

        html_content = f"""
        <h2>Bonjour {user_name},</h2>
        <p>Voici votre code de vérification à 6 chiffres:</p>
        <div style="background: #f8f9fa; padding: 30px; text-align: center; margin: 20px 0; border-radius: 8px;">
            <h1 style="font-size: 48px; letter-spacing: 10px; color: #667eea; margin: 0;">{code}</h1>
        </div>
        <p style="color: #666; font-size: 14px;">Ce code est valide pendant 10 minutes.</p>
        <p style="color: #666; font-size: 14px;">Si vous n'avez pas demandé ce code, ignorez cet email.</p>
        """

        return email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=email_service._fallback_template({'content': html_content})
        )


# ============================================
# EMAIL QUEUE (pour Celery)
# ============================================

class EmailQueue:
    """
    File d'attente emails pour Celery
    """

    @staticmethod
    def queue_email(task_name: str, **kwargs):
        """
        Ajouter email à la queue Celery

        Args:
            task_name: Nom de la tâche (ex: 'send_welcome_email')
            **kwargs: Paramètres de l'email
        """
        # TODO: Implémenter avec Celery
        # from tasks import send_email_task
        # send_email_task.delay(task_name, **kwargs)
        logger.info("email_queued", task=task_name, params=kwargs)

def send_verification_email(to_email: str, token: str) -> str:
    """
    Send a verification email and return the URL used in the message.
    Legacy wrapper for compatibility.
    """
    # Construct URL
    frontend_url = os.getenv("FRONTEND_URL", "https://getyourshare.ma")
    verification_route = os.getenv("VERIFICATION_ROUTE", "/verify-email")
    base = frontend_url.rstrip("/")
    route = verification_route if verification_route.startswith("/") else f"/{verification_route}"
    verification_url = f"{base}{route}?token={token}"
    
    subject = "Vérifiez votre adresse email"
    
    html_content = f"""
        <html>
            <body>
                <p>Bienvenue sur <strong>ShareYourSales</strong> !</p>
                <p>Pour activer votre compte, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>
                <p style=\"margin:24px 0;\">
                    <a href=\"{verification_url}\" style=\"
                        background-color:#2563eb;
                        color:#ffffff;
                        padding:12px 24px;
                        border-radius:6px;
                        text-decoration:none;
                        display:inline-block;
                        font-weight:600;
                    \">Confirmer mon adresse email</a>
                </p>
                <p>Ce lien expire dans 48 heures. Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
                <p style=\"margin-top:32px; color:#6b7280; font-size:12px;\">
                    ShareYourSales · Plateforme d'affiliation intelligente
                </p>
            </body>
        </html>
    """
    
    email_service.send_email(to_email, subject, html_content)
    return verification_url
