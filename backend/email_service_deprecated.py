"""
Email Service for ShareYourSales.
Handles transactional emails using SendGrid (preferred) or SMTP fallback.
Supports HTML templates via Jinja2.
"""

import logging
import os
from typing import Any, Dict, Optional, List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Fallback imports
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

logger = logging.getLogger("shareyoursales.email")

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("EMAIL_FROM", "no-reply@shareyoursales.com")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "ShareYourSales")
        
        # Setup Jinja2 for templates
        template_dir = Path(__file__).parent / "email_templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # SMTP Fallback config
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renders a Jinja2 template with the given context."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return ""

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Sends an email using SendGrid or SMTP fallback."""
        
        if self.sendgrid_api_key:
            return self._send_via_sendgrid(to_email, subject, html_content)
        elif self.smtp_host and self.smtp_user:
            return self._send_via_smtp(to_email, subject, html_content, text_content)
        else:
            logger.info(
                f"[EMAIL MOCK] To: {to_email} | Subject: {subject}\nContent: {text_content or 'HTML Content'}"
            )
            return True

    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            if 200 <= response.status_code < 300:
                logger.info(f"Email sent via SendGrid to {to_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return False

    def _send_via_smtp(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str]
    ) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if self.smtp_use_tls:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False

    def send_welcome_email(self, to_email: str, dashboard_url: str) -> bool:
        html = self._render_template("welcome.html", {"dashboard_url": dashboard_url})
        return self.send_email(to_email, "Bienvenue sur ShareYourSales!", html)

    def send_invoice_email(self, to_email: str, amount: float, date: str, invoice_url: str) -> bool:
        html = self._render_template("invoice.html", {
            "amount": amount,
            "date": date,
            "invoice_url": invoice_url
        })
        return self.send_email(to_email, "Votre facture ShareYourSales", html)

    def send_payout_email(self, to_email: str, amount: float, dashboard_url: str) -> bool:
        html = self._render_template("payout.html", {
            "amount": amount,
            "dashboard_url": dashboard_url
        })
        return self.send_email(to_email, "Paiement envoyé!", html)

    def send_affiliation_approved(self, to_email: str, product_name: str, commission: float, dashboard_url: str) -> bool:
        html = self._render_template("affiliation_approved.html", {
            "product_name": product_name,
            "commission": commission,
            "dashboard_url": dashboard_url
        })
        return self.send_email(to_email, "Affiliation Approuvée", html)

    def send_password_reset(self, to_email: str, reset_url: str) -> bool:
        html = self._render_template("password_reset.html", {"reset_url": reset_url})
        return self.send_email(to_email, "Réinitialisation de mot de passe", html)

# Singleton instance
email_service = EmailService()

# Legacy compatibility functions
def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None, reply_to: Optional[str] = None) -> bool:
    return email_service.send_email(to_email, subject, html_body, text_body)

def build_verification_url(token: str) -> str:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_route = os.getenv("VERIFICATION_ROUTE", "/verify-email")
    base = frontend_url.rstrip("/")
    route = verification_route if verification_route.startswith("/") else f"/{verification_route}"
    return f"{base}{route}?token={token}"

def send_verification_email(to_email: str, token: str) -> str:
    """Send a verification email and return the URL used in the message."""
    verification_url = build_verification_url(token)

    subject = "Vérifiez votre adresse email"
    text_body = (
        "Bienvenue sur ShareYourSales !\n\n"
        "Pour activer votre compte, cliquez sur le lien suivant :\n"
        f"{verification_url}\n\n"
        "Ce lien expire dans 48 heures."
    )
    html_body = f"""
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

    send_email(to_email=to_email, subject=subject, html_body=html_body, text_body=text_body)
    return verification_url
