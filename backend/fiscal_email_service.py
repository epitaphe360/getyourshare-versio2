"""
Service d'envoi d'emails fiscaux automatiques
Factures, rappels, alertes TVA, notifications déclarations
Version complète avec SendGrid + SMTP fallback
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import base64
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class FiscalEmailService:
    """Service d'emails automatiques pour système fiscal"""
    
    def __init__(self, api_key: Optional[str] = None, smtp_fallback: bool = True):
        """
        Args:
            api_key: SendGrid API key (ou depuis .env)
            smtp_fallback: Utiliser SMTP si SendGrid échoue
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'factures@getyourshare.com')
        self.smtp_fallback = smtp_fallback
        
        # SMTP fallback config
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    def _get_invoice_email_template(self, country: str) -> str:
        """Template HTML email facture selon pays"""
        if country == 'MA':
            subject = "Votre facture GetYourShare"
            greeting = "Bonjour"
            body = "Veuillez trouver ci-joint votre facture."
        elif country == 'FR':
            subject = "Votre facture GetYourShare"
            greeting = "Bonjour"
            body = "Veuillez trouver ci-joint votre facture conforme FEC."
        else:  # USA
            subject = "Your GetYourShare Invoice"
            greeting = "Hello"
            body = "Please find attached your invoice."
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #262626; }}
                .header {{ background: #1890ff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .invoice-box {{ border: 2px solid #1890ff; padding: 20px; margin: 20px 0; }}
                .button {{ background: #1890ff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #8c8c8c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GetYourShare</h1>
                <p>{subject}</p>
            </div>
            <div class="content">
                <p>{greeting} {{{{ client_name }}}},</p>
                <p>{body}</p>
                
                <div class="invoice-box">
                    <h3>📄 Facture N° {{{{ invoice_number }}}}</h3>
                    <p><strong>Date:</strong> {{{{ issue_date }}}}</p>
                    <p><strong>Échéance:</strong> {{{{ due_date }}}}</p>
                    <p><strong>Montant TTC:</strong> {{{{ amount_ttc }}}} {{{{ currency }}}}</p>
                </div>
                
                <a href="{{{{ payment_link }}}}" class="button">💳 Payer maintenant</a>
                
                <p style="margin-top: 30px;">Pour toute question, contactez-nous à {self.from_email}</p>
            </div>
            <div class="footer">
                <p>GetYourShare - Plateforme d'affiliation multi-pays</p>
                <p>Ce message est automatique, merci de ne pas y répondre</p>
            </div>
        </body>
        </html>
        """
        return template
    
    def _get_reminder_email_template(self, days_overdue: int) -> str:
        """Template email rappel paiement"""
        urgency = "⚠️ URGENT" if days_overdue > 30 else "⏰ Rappel"
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #262626; }}
                .header {{ background: #ff4d4f; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-box {{ border: 2px solid #ff4d4f; background: #fff1f0; padding: 20px; margin: 20px 0; }}
                .button {{ background: #ff4d4f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{urgency} - Facture impayée</h1>
            </div>
            <div class="content">
                <p>Bonjour {{{{ client_name }}}},</p>
                <p>Nous constatons que la facture suivante n'a pas encore été réglée :</p>
                
                <div class="alert-box">
                    <h3>📄 Facture N° {{{{ invoice_number }}}}</h3>
                    <p><strong>Date d'échéance:</strong> {{{{ due_date }}}}</p>
                    <p><strong>Montant dû:</strong> {{{{ amount_ttc }}}} {{{{ currency }}}}</p>
                    <p><strong>Retard:</strong> {days_overdue} jours</p>
                    <p><strong>Pénalités:</strong> {{{{ late_fees }}}} {{{{ currency }}}}</p>
                </div>
                
                <p>Merci de régulariser votre situation dans les plus brefs délais.</p>
                <a href="{{{{ payment_link }}}}" class="button">💳 Payer maintenant</a>
            </div>
        </body>
        </html>
        """
        return template
    
    def _get_vat_alert_template(self) -> str:
        """Template alerte déclaration TVA"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #262626; }
                .header { background: #faad14; color: white; padding: 20px; text-align: center; }
                .content { padding: 30px; }
                .alert-box { border: 2px solid #faad14; background: #fffbe6; padding: 20px; margin: 20px 0; }
                .button { background: #faad14; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Déclaration TVA à effectuer</h1>
            </div>
            <div class="content">
                <p>Bonjour {{ user_name }},</p>
                <p>Votre déclaration de TVA pour la période {{ period }} doit être effectuée avant le {{ deadline }}.</p>
                
                <div class="alert-box">
                    <h3>Récapitulatif TVA</h3>
                    <p><strong>TVA collectée:</strong> {{ vat_collected }} {{ currency }}</p>
                    <p><strong>TVA déductible:</strong> {{ vat_deductible }} {{ currency }}</p>
                    <p><strong>TVA à payer:</strong> {{ vat_to_pay }} {{ currency }}</p>
                </div>
                
                <a href="{{ declaration_link }}" class="button">📝 Déclarer maintenant</a>
            </div>
        </body>
        </html>
        """
        return template
    
    def send_invoice_email(
        self,
        to_email: str,
        client_name: str,
        invoice_data: Dict,
        pdf_path: str,
        country: str = 'FR'
    ) -> bool:
        """
        Envoie email avec facture PDF
        
        Args:
            to_email: Email client
            client_name: Nom client
            invoice_data: {invoice_number, issue_date, due_date, amount_ttc, currency}
            pdf_path: Chemin fichier PDF facture
            country: Pays (MA/FR/US)
        
        Returns:
            True si envoi réussi
        """
        try:
            # Template HTML
            html_template = Template(self._get_invoice_email_template(country))
            html_content = html_template.render(
                client_name=client_name,
                invoice_number=invoice_data['invoice_number'],
                issue_date=invoice_data['issue_date'],
                due_date=invoice_data['due_date'],
                amount_ttc=f"{invoice_data['amount_ttc']:.2f}",
                currency=invoice_data['currency'],
                payment_link=f"https://app.getyourshare.com/pay/{invoice_data['invoice_number']}"
            )
            
            # Lecture PDF
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            if self.api_key:
                # SendGrid
                return self._send_with_sendgrid(
                    to_email,
                    f"Facture {invoice_data['invoice_number']}",
                    html_content,
                    pdf_data,
                    f"facture_{invoice_data['invoice_number']}.pdf"
                )
            elif self.smtp_fallback:
                # SMTP fallback
                return self._send_with_smtp(
                    to_email,
                    f"Facture {invoice_data['invoice_number']}",
                    html_content,
                    pdf_data,
                    f"facture_{invoice_data['invoice_number']}.pdf"
                )
            else:
                print("❌ Aucun service email configuré")
                return False
                
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            return False
    
    def send_payment_reminder(
        self,
        to_email: str,
        client_name: str,
        invoice_data: Dict,
        days_overdue: int
    ) -> bool:
        """Envoie rappel paiement facture échue"""
        try:
            # Calcul pénalités (ex: 12% annuel Maroc, 18% USA)
            annual_rate = 0.12 if invoice_data.get('country') == 'MA' else 0.18
            late_fees = invoice_data['amount_ttc'] * annual_rate * (days_overdue / 365)
            
            html_template = Template(self._get_reminder_email_template(days_overdue))
            html_content = html_template.render(
                client_name=client_name,
                invoice_number=invoice_data['invoice_number'],
                due_date=invoice_data['due_date'],
                amount_ttc=f"{invoice_data['amount_ttc']:.2f}",
                currency=invoice_data['currency'],
                late_fees=f"{late_fees:.2f}",
                payment_link=f"https://app.getyourshare.com/pay/{invoice_data['invoice_number']}"
            )
            
            subject = f"⚠️ RAPPEL - Facture {invoice_data['invoice_number']} échue depuis {days_overdue} jours"
            
            if self.api_key:
                return self._send_with_sendgrid(to_email, subject, html_content)
            elif self.smtp_fallback:
                return self._send_with_smtp(to_email, subject, html_content)
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erreur envoi rappel: {e}")
            return False
    
    def send_vat_declaration_alert(
        self,
        to_email: str,
        user_name: str,
        period: str,
        deadline: str,
        vat_data: Dict
    ) -> bool:
        """Envoie alerte déclaration TVA"""
        try:
            html_template = Template(self._get_vat_alert_template())
            html_content = html_template.render(
                user_name=user_name,
                period=period,
                deadline=deadline,
                vat_collected=f"{vat_data['collected']:.2f}",
                vat_deductible=f"{vat_data['deductible']:.2f}",
                vat_to_pay=f"{vat_data['to_pay']:.2f}",
                currency=vat_data['currency'],
                declaration_link="https://app.getyourshare.com/fiscal/vat/declare"
            )
            
            subject = f"📊 Déclaration TVA {period} à effectuer avant le {deadline}"
            
            if self.api_key:
                return self._send_with_sendgrid(to_email, subject, html_content)
            elif self.smtp_fallback:
                return self._send_with_smtp(to_email, subject, html_content)
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erreur envoi alerte TVA: {e}")
            return False
    
    def send_payment_confirmation(
        self,
        to_email: str,
        client_name: str,
        invoice_number: str,
        amount: float,
        currency: str,
        payment_method: str
    ) -> bool:
        """Envoie confirmation paiement"""
        html_content = f"""
        <html>
        <body style="font-family: Arial;">
            <div style="background: #52c41a; color: white; padding: 20px; text-align: center;">
                <h1>✅ Paiement confirmé</h1>
            </div>
            <div style="padding: 30px;">
                <p>Bonjour {client_name},</p>
                <p>Nous avons bien reçu votre paiement de <strong>{amount:.2f} {currency}</strong> pour la facture <strong>{invoice_number}</strong>.</p>
                <p>Moyen de paiement: {payment_method}</p>
                <p>Merci de votre confiance !</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"✅ Paiement confirmé - Facture {invoice_number}"
        
        try:
            if self.api_key:
                return self._send_with_sendgrid(to_email, subject, html_content)
            elif self.smtp_fallback:
                return self._send_with_smtp(to_email, subject, html_content)
            else:
                return False
        except Exception as e:
            print(f"❌ Erreur envoi confirmation: {e}")
            return False
    
    def _send_with_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachment_data: Optional[bytes] = None,
        attachment_filename: Optional[str] = None
    ) -> bool:
        """Envoi via SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Pièce jointe si fournie
            if attachment_data and attachment_filename:
                encoded = base64.b64encode(attachment_data).decode()
                attachment = Attachment()
                attachment.file_content = encoded
                attachment.file_name = attachment_filename
                attachment.file_type = 'application/pdf'
                attachment.disposition = 'attachment'
                message.attachment = attachment
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email envoyé à {to_email}")
                return True
            else:
                print(f"⚠️ SendGrid status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur SendGrid: {e}")
            if self.smtp_fallback:
                return self._send_with_smtp(to_email, subject, html_content, attachment_data, attachment_filename)
            return False
    
    def _send_with_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachment_data: Optional[bytes] = None,
        attachment_filename: Optional[str] = None
    ) -> bool:
        """Envoi via SMTP (fallback)"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Pièce jointe
            if attachment_data and attachment_filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
                msg.attach(part)
            
            # Connexion SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email SMTP envoyé à {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur SMTP: {e}")
            return False


# === SCHEDULED TASKS (À intégrer dans APScheduler) ===
def check_overdue_invoices_daily():
    """Tâche quotidienne: vérifier factures échues et envoyer rappels"""
    from supabase_client import supabase
    from datetime import date
    
    email_service = FiscalEmailService()
    
    # Factures échues non payées
    today = date.today().isoformat()
    result = supabase.table('invoices').select('*').lt('due_date', today).eq('status', 'sent').execute()
    
    for invoice in result.data:
        due_date = datetime.fromisoformat(invoice['due_date'])
        days_overdue = (datetime.now() - due_date).days
        
        # Rappels à J+7, J+15, J+30
        if days_overdue in [7, 15, 30]:
            email_service.send_payment_reminder(
                invoice['client_email'],
                invoice['client_name'],
                invoice,
                days_overdue
            )


def check_vat_declarations_monthly():
    """Tâche mensuelle: alerter déclarations TVA à faire"""
    from supabase_client import supabase
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    email_service = FiscalEmailService()
    
    # Users avec régime TVA mensuel
    users = supabase.table('fiscal_settings').select('*').eq('vat_regime', 'monthly').execute()
    
    for user_settings in users.data:
        # Calculer TVA du mois dernier
        last_month_start = date.today().replace(day=1) - relativedelta(months=1)
        last_month_end = date.today().replace(day=1) - relativedelta(days=1)
        
        # Récupérer factures du mois
        invoices = supabase.table('invoices').select('*').gte('issue_date', last_month_start.isoformat()).lte('issue_date', last_month_end.isoformat()).eq('user_id', user_settings['user_id']).execute()
        
        vat_collected = sum(inv['vat_amount'] for inv in invoices.data)
        vat_deductible = 0  # À calculer depuis factures d'achat
        vat_to_pay = vat_collected - vat_deductible
        
        # Deadline: 20 du mois suivant
        deadline = (last_month_end + relativedelta(months=1)).replace(day=20)
        
        try:
        user = supabase.table('users').select('email, name').eq('id', user_settings['user_id']).single().execute()
        except Exception:
            pass  # .single() might return no results
        
        email_service.send_vat_declaration_alert(
            user.data['email'],
            user.data.get('name', 'Utilisateur'),
            f"{last_month_start.strftime('%m/%Y')}",
            deadline.strftime('%d/%m/%Y'),
            {
                'collected': vat_collected,
                'deductible': vat_deductible,
                'to_pay': vat_to_pay,
                'currency': user_settings['currency']
            }
        )


if __name__ == "__main__":
    service = FiscalEmailService()
    print("✅ Service email fiscal initialisé")
