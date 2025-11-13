"""
Service d'automatisation des paiements pour système LEADS
Gestion automatique des recharges et génération de reçus
"""

import os
import stripe
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from supabase import Client
from utils.logger import logger


# Configuration Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


class PaymentAutomationService:
    """Service d'automatisation des paiements"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def create_deposit_payment(
        self, 
        merchant_id: str, 
        amount: Decimal,
        payment_method: str = 'stripe',
        auto_recharge: bool = False
    ) -> Dict:
        """
        Créer un paiement pour recharger un dépôt
        
        Args:
            merchant_id: ID du merchant
            amount: Montant à recharger
            payment_method: 'stripe' ou 'cmi'
            auto_recharge: Activer la recharge automatique
        
        Returns:
            {
                'payment_url': 'https://...',
                'payment_id': 'pi_xxx',
                'amount': 5000.00
            }
        """
        if amount < 500:
            raise ValueError("Montant minimum: 500 dhs")
        
        # Récupérer les infos merchant
        merchant_response = self.supabase.table('merchants')\
            .select('*, users(email, first_name, last_name)')\
            .eq('id', merchant_id)\
            .execute()
        
        if not merchant_response.data:
            raise ValueError("Merchant non trouvé")
        
        merchant = merchant_response.data[0]
        user = merchant.get('users', {})
        
        if payment_method == 'stripe':
            return self._create_stripe_payment(merchant, user, amount)
        elif payment_method == 'cmi':
            return self._create_cmi_payment(merchant, user, amount)
        else:
            raise ValueError(f"Méthode de paiement non supportée: {payment_method}")
    
    def _create_stripe_payment(self, merchant: Dict, user: Dict, amount: Decimal) -> Dict:
        """Créer un paiement Stripe"""
        try:
            # Créer une session de paiement Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'mad',  # Dirham marocain
                        'product_data': {
                            'name': 'Recharge dépôt LEADS',
                            'description': f"Recharge pour {merchant.get('company_name', 'votre compte')}"
                        },
                        'unit_amount': int(float(amount) * 100),  # Convertir en centimes
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard/deposits?payment=success',
                cancel_url=os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard/deposits?payment=cancel',
                customer_email=user.get('email'),
                metadata={
                    'merchant_id': merchant['id'],
                    'type': 'deposit_recharge',
                    'amount': str(amount)
                }
            )
            
            # Enregistrer la transaction en attente
            self.supabase.table('deposit_transactions').insert({
                'merchant_id': merchant['id'],
                'transaction_type': 'recharge',
                'amount': float(amount),
                'payment_method': 'stripe',
                'payment_reference': session.id,
                'description': f'Recharge Stripe - En attente',
                'metadata': {
                    'stripe_session_id': session.id,
                    'status': 'pending'
                }
            }).execute()
            
            return {
                'payment_url': session.url,
                'payment_id': session.id,
                'amount': float(amount),
                'status': 'pending'
            }
        
        except Exception as e:
            logger.info(f"❌ Erreur création paiement Stripe: {e}")
            raise ValueError(f"Impossible de créer le paiement: {str(e)}")
    
    def _create_cmi_payment(self, merchant: Dict, user: Dict, amount: Decimal) -> Dict:
        """Créer un paiement CMI (Maroc)"""
        # TODO: Implémenter l'intégration CMI
        # Pour l'instant, retourner un placeholder
        return {
            'payment_url': 'https://cmi.payment.gateway/pay',
            'payment_id': 'CMI_' + str(int(datetime.now().timestamp())),
            'amount': float(amount),
            'status': 'pending'
        }
    
    def handle_stripe_webhook(self, event: Dict) -> Dict:
        """
        Gérer les webhooks Stripe
        
        Events supportés:
        - checkout.session.completed: Paiement réussi
        - payment_intent.payment_failed: Paiement échoué
        """
        event_type = event.get('type')
        
        if event_type == 'checkout.session.completed':
            return self._handle_payment_success(event['data']['object'])
        
        elif event_type == 'payment_intent.payment_failed':
            return self._handle_payment_failed(event['data']['object'])
        
        return {'status': 'ignored', 'event': event_type}
    
    def _handle_payment_success(self, session: Dict) -> Dict:
        """Traiter un paiement réussi"""
        try:
            merchant_id = session['metadata'].get('merchant_id')
            amount = float(session['metadata'].get('amount', 0))
            
            if not merchant_id or amount <= 0:
                raise ValueError("Données de paiement invalides")
            
            # Récupérer ou créer le dépôt
            deposit_response = self.supabase.table('company_deposits')\
                .select('*')\
                .eq('merchant_id', merchant_id)\
                .eq('status', 'active')\
                .limit(1)\
                .execute()
            
            if deposit_response.data and len(deposit_response.data) > 0:
                deposit = deposit_response.data[0]
                deposit_id = deposit['id']
                
                # Mettre à jour le solde
                new_balance = float(deposit['current_balance']) + amount
                
                self.supabase.table('company_deposits')\
                    .update({
                        'current_balance': new_balance,
                        'status': 'active',
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', deposit_id)\
                    .execute()
            else:
                # Créer un nouveau dépôt
                deposit_data = {
                    'merchant_id': merchant_id,
                    'initial_amount': amount,
                    'current_balance': amount,
                    'reserved_amount': 0,
                    'status': 'active'
                }
                
                deposit_response = self.supabase.table('company_deposits')\
                    .insert(deposit_data)\
                    .execute()
                
                deposit_id = deposit_response.data[0]['id']
            
            # Enregistrer la transaction
            self.supabase.table('deposit_transactions').insert({
                'deposit_id': deposit_id,
                'merchant_id': merchant_id,
                'transaction_type': 'recharge',
                'amount': amount,
                'balance_before': 0,  # TODO: Calculer
                'balance_after': amount,
                'payment_method': 'stripe',
                'payment_reference': session.get('id'),
                'description': f'Recharge Stripe - Paiement confirmé',
                'metadata': {
                    'stripe_session_id': session.get('id'),
                    'status': 'completed'
                }
            }).execute()
            
            # Générer le reçu PDF
            receipt_path = self.generate_receipt_pdf(
                merchant_id=merchant_id,
                amount=amount,
                payment_reference=session.get('id'),
                payment_date=datetime.now()
            )
            
            # Envoyer le reçu par email
            # TODO: Envoyer l'email avec le reçu en pièce jointe
            
            logger.info(f"✅ Paiement confirmé: {amount} dhs pour merchant {merchant_id}")
            
            return {
                'status': 'success',
                'deposit_id': deposit_id,
                'amount': amount,
                'receipt_path': receipt_path
            }
        
        except Exception as e:
            logger.info(f"❌ Erreur traitement paiement: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _handle_payment_failed(self, payment_intent: Dict) -> Dict:
        """Traiter un paiement échoué"""
        logger.info(f"⚠️ Paiement échoué: {payment_intent.get('id')}")
        
        # TODO: Notifier le merchant
        
        return {
            'status': 'failed',
            'payment_id': payment_intent.get('id')
        }
    
    def generate_receipt_pdf(
        self,
        merchant_id: str,
        amount: float,
        payment_reference: str,
        payment_date: datetime
    ) -> str:
        """
        Générer un reçu PDF pour une recharge
        
        Returns:
            Chemin du fichier PDF généré
        """
        # Récupérer les infos merchant
        merchant_response = self.supabase.table('merchants')\
            .select('*, users(email, first_name, last_name)')\
            .eq('id', merchant_id)\
            .execute()
        
        if not merchant_response.data:
            raise ValueError("Merchant non trouvé")
        
        merchant = merchant_response.data[0]
        user = merchant.get('users', {})
        
        # Créer le répertoire receipts s'il n'existe pas
        receipts_dir = os.path.join(os.getcwd(), 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)
        
        # Nom du fichier
        filename = f"receipt_{merchant_id}_{int(payment_date.timestamp())}.pdf"
        filepath = os.path.join(receipts_dir, filename)
        
        # Créer le PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # En-tête
        elements.append(Paragraph("<b>REÇU DE PAIEMENT</b>", styles['Title']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Informations
        info_data = [
            ['Date:', payment_date.strftime('%d/%m/%Y %H:%M')],
            ['Référence:', payment_reference],
            ['Merchant:', merchant.get('company_name', 'N/A')],
            ['Email:', user.get('email', 'N/A')],
            ['', ''],
            ['<b>Montant rechargé:</b>', f'<b>{amount} MAD</b>'],
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 1*cm))
        
        # Footer
        elements.append(Paragraph(
            "<i>Merci d'utiliser ShareYourSales - Système LEADS</i>",
            styles['Normal']
        ))
        
        # Générer le PDF
        doc.build(elements)
        
        logger.info(f"📄 Reçu généré: {filepath}")
        
        return filepath
    
    def setup_auto_recharge(
        self,
        merchant_id: str,
        deposit_id: str,
        recharge_amount: Decimal,
        trigger_threshold: Decimal = Decimal('500')
    ) -> Dict:
        """
        Configurer la recharge automatique
        
        Args:
            merchant_id: ID du merchant
            deposit_id: ID du dépôt
            recharge_amount: Montant à recharger automatiquement
            trigger_threshold: Seuil déclencheur (quand solde < threshold)
        """
        # Mettre à jour le dépôt
        self.supabase.table('company_deposits')\
            .update({
                'auto_recharge': True,
                'auto_recharge_amount': float(recharge_amount),
                'alert_threshold': float(trigger_threshold),
                'updated_at': datetime.now().isoformat()
            })\
            .eq('id', deposit_id)\
            .execute()
        
        return {
            'success': True,
            'deposit_id': deposit_id,
            'auto_recharge_amount': float(recharge_amount),
            'trigger_threshold': float(trigger_threshold)
        }
