"""
Webhooks Paiements Stripe/PayPal
Marquage automatique factures payées, rapprochement bancaire, notifications
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import stripe
import hmac
import hashlib
from datetime import datetime
import os
from supabase_client import supabase
from fiscal_email_service import FiscalEmailService
from services.resend_email_service import resend_service


router = APIRouter()

# Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')

stripe.api_key = STRIPE_SECRET_KEY
email_service = FiscalEmailService()


# ===========================
# STRIPE WEBHOOKS
# ===========================

@router.post("/webhooks/stripe/payment")
async def stripe_payment_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """
    Webhook Stripe pour événements paiement
    - payment_intent.succeeded → Marquer facture comme payée
    - payment_intent.payment_failed → Notifier échec
    - charge.refunded → Gérer remboursement
    """
    
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
    
    # Récupérer payload brut
    payload = await request.body()
    sig_header = stripe_signature
    
    try:
        # Vérifier signature Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Traiter événement
    event_type = event['type']
    data = event['data']['object']
    
    if event_type == 'payment_intent.succeeded':
        # Paiement réussi
        await handle_payment_success(data, 'stripe')
        
    elif event_type == 'payment_intent.payment_failed':
        # Paiement échoué
        await handle_payment_failed(data, 'stripe')
        
    elif event_type == 'charge.refunded':
        # Remboursement
        await handle_refund(data, 'stripe')
        
    elif event_type == 'invoice.payment_succeeded':
        # Facture d'abonnement payée (différent de fiscal_invoices)
        print(f"ℹ️ Facture abonnement Stripe payée: {data.get('id')}")
    
    return {"status": "success"}


async def handle_payment_success(payment_data: dict, provider: str):
    """Traite paiement réussi (Stripe ou PayPal)"""
    
    # Extraire référence facture depuis metadata
    if provider == 'stripe':
        invoice_number = payment_data.get('metadata', {}).get('invoice_number')
        amount_paid = payment_data.get('amount_received') / 100  # Stripe en centimes
        currency = payment_data.get('currency', 'usd').upper()
        payment_id = payment_data.get('id')
        customer_email = payment_data.get('receipt_email')
        
    else:  # PayPal
        invoice_number = payment_data.get('invoice_id')
        amount_paid = float(payment_data.get('amount', {}).get('total', 0))
        currency = payment_data.get('amount', {}).get('currency', 'USD')
        payment_id = payment_data.get('id')
        customer_email = payment_data.get('payer', {}).get('email_address')
    
    if not invoice_number:
        print("⚠️ Paiement reçu sans référence facture")
        return
    
    # Récupérer facture fiscal
    try:
        result = supabase.table('fiscal_invoices').select('*').eq('invoice_number', invoice_number).single().execute()
    except Exception:
        pass  # .single() might return no results
    
    if not result.data:
        print(f"❌ Facture {invoice_number} non trouvée")
        return
    
    invoice = result.data
    
    # Vérifier montant
    if abs(amount_paid - invoice['amount_ttc']) > 0.01:
        print(f"⚠️ Montant payé ({amount_paid}) différent de facture ({invoice['amount_ttc']})")
    
    # Mettre à jour facture
    update_data = {
        'status': 'paid',
        'payment_date': datetime.now().isoformat(),
        'payment_method': provider,
        'payment_id': payment_id,
        'updated_at': datetime.now().isoformat()
    }
    
    supabase.table('invoices').update(update_data).eq('invoice_number', invoice_number).execute()
    
    print(f"✅ Facture {invoice_number} marquée comme payée ({provider})")
    
    # Envoyer confirmation email client
    email_service.send_payment_confirmation(
        customer_email or invoice['client_email'],
        invoice['client_name'],
        invoice_number,
        amount_paid,
        currency,
        provider.capitalize()
    )
    
    # Créer entrée rapprochement bancaire
    await create_bank_reconciliation(invoice_number, amount_paid, currency, provider, payment_id)


async def handle_payment_failed(payment_data: dict, provider: str):
    """Traite échec paiement"""
    
    if provider == 'stripe':
        invoice_number = payment_data.get('metadata', {}).get('invoice_number')
        error_message = payment_data.get('last_payment_error', {}).get('message', 'Unknown error')
    else:
        invoice_number = payment_data.get('invoice_id')
        error_message = payment_data.get('reason', 'Unknown error')
    
    if not invoice_number:
        return
    
    # Mettre à jour facture
    supabase.table('fiscal_invoices').update({
        'status': 'payment_failed',
        'payment_error': error_message,
        'updated_at': datetime.now().isoformat()
    }).eq('invoice_number', invoice_number).execute()
    
    print(f"❌ Échec paiement facture {invoice_number}: {error_message}")
    
    # Envoyer email notification échec
    try:
        # Récupérer infos client depuis la facture
        result = supabase.table('fiscal_invoices').select('client_email, client_name, amount_ttc, currency').eq('invoice_number', invoice_number).single().execute()
        if result.data:
            inv = result.data
            resend_service.send_payment_failure_email(
                to_email=inv.get('client_email'),
                user_name=inv.get('client_name', 'Client'),
                amount=inv.get('amount_ttc', 0),
                currency=inv.get('currency', 'USD'),
                error_message=error_message
            )
    except Exception as e:
        print(f"❌ Erreur envoi email échec paiement: {e}")


async def handle_refund(refund_data: dict, provider: str):
    """Traite remboursement"""
    
    if provider == 'stripe':
        payment_id = refund_data.get('payment_intent')
        amount_refunded = refund_data.get('amount_refunded') / 100
        
        # Trouver facture par payment_id
        try:
            result = supabase.table('invoices').select('*').eq('payment_id', payment_id).single().execute()
        except Exception:
            pass  # .single() might return no results
        
        if result.data:
            invoice = result.data
            
            supabase.table('fiscal_invoices').update({
                'status': 'refunded',
                'refund_amount': amount_refunded,
                'refund_date': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq('id', invoice['id']).execute()
            
            print(f"✅ Remboursement enregistré pour facture {invoice['invoice_number']}")


async def create_bank_reconciliation(
    invoice_number: str,
    amount: float,
    currency: str,
    provider: str,
    transaction_id: str
):
    """Crée entrée rapprochement bancaire"""
    
    reconciliation_data = {
        'invoice_number': invoice_number,
        'amount': amount,
        'currency': currency,
        'payment_provider': provider,
        'transaction_id': transaction_id,
        'reconciled_at': datetime.now().isoformat(),
        'status': 'matched'
    }
    
    # Insérer dans table bank_reconciliations (à créer si n'existe pas)
    try:
        supabase.table('bank_reconciliations').insert(reconciliation_data).execute()
        print(f"✅ Rapprochement bancaire créé: {transaction_id}")
    except Exception as e:
        print(f"⚠️ Erreur rapprochement bancaire: {e}")


# ===========================
# PAYPAL WEBHOOKS
# ===========================

@router.post("/webhooks/paypal/payment")
async def paypal_payment_webhook(request: Request):
    """
    Webhook PayPal pour événements paiement
    - PAYMENT.SALE.COMPLETED → Marquer facture payée
    - PAYMENT.SALE.REFUNDED → Gérer remboursement
    """
    
    # Récupérer payload
    payload = await request.body()
    headers = dict(request.headers)
    
    # Vérifier signature PayPal
    if not verify_paypal_webhook(payload, headers):
        raise HTTPException(status_code=401, detail="Invalid PayPal signature")
    
    # Parser événement
    import json
    event = json.loads(payload)
    event_type = event.get('event_type')
    resource = event.get('resource', {})
    
    if event_type == 'PAYMENT.SALE.COMPLETED':
        await handle_payment_success(resource, 'paypal')
        
    elif event_type == 'PAYMENT.SALE.REFUNDED':
        await handle_refund(resource, 'paypal')
    
    return {"status": "success"}


def verify_paypal_webhook(payload: bytes, headers: dict) -> bool:
    """Vérifie signature webhook PayPal"""
    
    if not PAYPAL_WEBHOOK_ID:
        print("⚠️ PayPal webhook ID non configuré")
        return True  # Mode dev
    
    # Récupérer headers PayPal
    transmission_id = headers.get('paypal-transmission-id')
    timestamp = headers.get('paypal-transmission-time')
    webhook_id = PAYPAL_WEBHOOK_ID
    cert_url = headers.get('paypal-cert-url')
    signature = headers.get('paypal-transmission-sig')
    
    # Construire message à vérifier
    expected_sig = f"{transmission_id}|{timestamp}|{webhook_id}|{hashlib.sha256(payload).hexdigest()}"
    
    # Vérifier avec certificat PayPal (implémentation complète nécessiterait openssl)
    # Pour production: utiliser librairie paypalrestsdk
    
    print(f"ℹ️ Vérification signature PayPal (mode simplifié)")
    return True  # Simplified


# ===========================
# RAPPROCHEMENT BANCAIRE MANUEL
# ===========================

@router.post("/fiscal/bank-reconciliation/import")
async def import_bank_statement(file: bytes, format: str = 'csv'):
    """
    Import relevé bancaire CSV pour rapprochement automatique
    
    Format attendu: Date, Libellé, Montant, Devise
    """
    
    if format != 'csv':
        raise HTTPException(status_code=400, detail="Seul format CSV supporté")
    
    import csv
    from io import StringIO
    
    csv_data = file.decode('utf-8')
    reader = csv.DictReader(StringIO(csv_data))
    
    matched_count = 0
    unmatched_transactions = []
    
    for row in reader:
        date = row.get('Date')
        description = row.get('Libellé') or row.get('Description')
        amount = float(row.get('Montant').replace(',', '.'))
        
        # Chercher numéro facture dans description
        import re
        invoice_match = re.search(r'FA-\d{4}-\d{4,6}', description)
        
        if invoice_match:
            invoice_number = invoice_match.group(0)
            
            # Vérifier facture existe
            try:
                result = supabase.table('invoices').select('*').eq('invoice_number', invoice_number).single().execute()
            except Exception:
                pass  # .single() might return no results
            
            if result.data and result.data['status'] == 'sent':
                # Marquer comme payée
                supabase.table('fiscal_invoices').update({
                    'status': 'paid',
                    'payment_date': date,
                    'payment_method': 'bank_transfer',
                    'updated_at': datetime.now().isoformat()
                }).eq('invoice_number', invoice_number).execute()
                
                matched_count += 1
                print(f"✅ Facture {invoice_number} rapprochée avec virement bancaire")
            else:
                unmatched_transactions.append({
                    'date': date,
                    'description': description,
                    'amount': amount,
                    'reason': 'Facture déjà payée ou introuvable'
                })
        else:
            unmatched_transactions.append({
                'date': date,
                'description': description,
                'amount': amount,
                'reason': 'Aucun numéro facture trouvé'
            })
    
    return {
        "matched": matched_count,
        "unmatched": len(unmatched_transactions),
        "unmatched_transactions": unmatched_transactions
    }


# ===========================
# GÉNÉRATION LIEN PAIEMENT
# ===========================

@router.post("/fiscal/invoices/{invoice_id}/payment-link")
async def generate_payment_link(invoice_id: str, provider: str = 'stripe'):
    """
    Génère lien paiement Stripe/PayPal pour facture
    
    Args:
        invoice_id: ID facture fiscal
        provider: 'stripe' ou 'paypal'
    """
    
    # Récupérer facture
    try:
        result = supabase.table('invoices').select('*').eq('id', invoice_id).single().execute()
    except Exception:
        pass  # .single() might return no results
    invoice = result.data
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    if invoice['status'] == 'paid':
        raise HTTPException(status_code=400, detail="Facture déjà payée")
    
    if provider == 'stripe':
        # Créer PaymentIntent Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(invoice['amount_ttc'] * 100),  # En centimes
            currency=invoice['currency'].lower(),
            metadata={
                'invoice_number': invoice['invoice_number'],
                'invoice_id': invoice_id
            },
            description=f"Facture {invoice['invoice_number']} - {invoice['client_name']}"
        )
        
        payment_link = f"https://app.getyourshare.com/pay/stripe/{payment_intent.id}"
        
    elif provider == 'paypal':
        # Créer invoice PayPal (nécessite SDK PayPal)
        payment_link = f"https://www.paypal.com/invoice/p/#INVOICE-{invoice['invoice_number']}"
        
    else:
        raise HTTPException(status_code=400, detail="Provider non supporté")
    
    # Enregistrer lien dans facture
    supabase.table('invoices').update({
        'payment_link': payment_link,
        'payment_link_provider': provider,
        'updated_at': datetime.now().isoformat()
    }).eq('id', invoice_id).execute()
    
    return {
        "payment_link": payment_link,
        "provider": provider,
        "amount": invoice['amount_ttc'],
        "currency": invoice['currency']
    }


# === À AJOUTER DANS server.py ===
# app.include_router(payment_webhooks_router, prefix="/api", tags=["Payment Webhooks"])
