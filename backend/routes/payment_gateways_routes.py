"""
Routes Payment Gateways
PayPal, Apple Pay, Google Pay, Stripe Checkout, Crypto
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict
from decimal import Decimal
import os

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payment Gateways"])


# ============================================
# MODELS
# ============================================

class PaymentIntent(BaseModel):
    amount: float
    currency: str = "MAD"
    gateway: str  # stripe, paypal, apple_pay, google_pay, crypto
    order_id: Optional[str] = None
    metadata: Optional[Dict] = {}


class PayPalOrder(BaseModel):
    amount: float
    currency: str = "USD"
    return_url: str
    cancel_url: str


# ============================================
# STRIPE
# ============================================

@router.post("/stripe/create-checkout")
async def create_stripe_checkout(
    payment: PaymentIntent,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une session Stripe Checkout

    NOTE: Nécessite stripe module (pip install stripe)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Importer Stripe (optionnel)
        try:
            import stripe
            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

            if not stripe.api_key:
                raise HTTPException(status_code=500, detail="Stripe non configuré")

            # Créer une session Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': payment.currency.lower(),
                        'unit_amount': int(payment.amount * 100),  # Centimes
                        'product_data': {
                            'name': f'Paiement GetYourShare',
                            'description': payment.metadata.get('description', 'Paiement')
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://app.getyourshare.com/payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://app.getyourshare.com/payment/cancel',
                metadata={
                    'user_id': user_id,
                    'order_id': payment.order_id,
                    **payment.metadata
                }
            )

            # Sauvegarder la transaction
            transaction_data = {
                'user_id': user_id,
                'gateway': 'stripe',
                'amount': payment.amount,
                'currency': payment.currency,
                'status': 'pending',
                'session_id': session.id,
                'order_id': payment.order_id,
                'metadata': payment.metadata
            }

            self.supabase.table('payment_transactions').insert(transaction_data).execute()

            return {
                'success': True,
                'gateway': 'stripe',
                'session_id': session.id,
                'checkout_url': session.url
            }

        except ImportError:
            raise HTTPException(status_code=500, detail="Stripe module non installé (pip install stripe)")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """
    Webhook Stripe pour confirmer les paiements
    """
    try:
        import stripe

        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Gérer les événements
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Mettre à jour la transaction
            supabase.table('payment_transactions').update({
                'status': 'completed',
                'completed_at': session.get('created')
            }).eq('session_id', session['id']).execute()

            logger.info(f"Payment completed: {session['id']}")

        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']

            supabase.table('payment_transactions').update({
                'status': 'expired'
            }).eq('session_id', session['id']).execute()

        return {'received': True}

    except ImportError:
        return {'error': 'Stripe not installed'}
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {'error': str(e)}


# ============================================
# PAYPAL
# ============================================

@router.post("/paypal/create-order")
async def create_paypal_order(
    payment: PayPalOrder,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un ordre PayPal

    NOTE: Nécessite paypalrestsdk (pip install paypalrestsdk)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        try:
            import paypalrestsdk

            paypalrestsdk.configure({
                "mode": os.getenv("PAYPAL_MODE", "sandbox"),  # sandbox or live
                "client_id": os.getenv("PAYPAL_CLIENT_ID"),
                "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
            })

            # Créer le paiement
            payment_obj = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": payment.return_url,
                    "cancel_url": payment.cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Paiement GetYourShare",
                            "sku": "001",
                            "price": str(payment.amount),
                            "currency": payment.currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(payment.amount),
                        "currency": payment.currency
                    },
                    "description": "Paiement sur GetYourShare"
                }]
            })

            if payment_obj.create():
                # Trouver l'URL d'approbation
                approval_url = None
                for link in payment_obj.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break

                # Sauvegarder
                transaction_data = {
                    'user_id': user_id,
                    'gateway': 'paypal',
                    'amount': payment.amount,
                    'currency': payment.currency,
                    'status': 'pending',
                    'payment_id': payment_obj.id,
                    'metadata': {}
                }

                supabase.table('payment_transactions').insert(transaction_data).execute()

                return {
                    'success': True,
                    'gateway': 'paypal',
                    'payment_id': payment_obj.id,
                    'approval_url': approval_url
                }
            else:
                raise Exception(payment_obj.error)

        except ImportError:
            raise HTTPException(status_code=500, detail="PayPal SDK non installé (pip install paypalrestsdk)")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PayPal order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paypal/execute")
async def execute_paypal_payment(
    payment_id: str,
    payer_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Exécuter le paiement PayPal après approbation
    """
    try:
        import paypalrestsdk

        paypalrestsdk.configure({
            "mode": os.getenv("PAYPAL_MODE", "sandbox"),
            "client_id": os.getenv("PAYPAL_CLIENT_ID"),
            "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
        })

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Mettre à jour la transaction
            supabase.table('payment_transactions').update({
                'status': 'completed',
                'payer_id': payer_id
            }).eq('payment_id', payment_id).execute()

            return {
                'success': True,
                'payment_id': payment_id,
                'status': 'completed'
            }
        else:
            raise Exception(payment.error)

    except ImportError:
        raise HTTPException(status_code=500, detail="PayPal SDK non installé")
    except Exception as e:
        logger.error(f"PayPal execute error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# APPLE PAY
# ============================================

@router.post("/apple-pay/session")
async def create_apple_pay_session(
    payment: PaymentIntent,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une session Apple Pay

    NOTE: Nécessite certificat Apple Pay Merchant Identity
    """
    return {
        'success': False,
        'message': 'Apple Pay nécessite configuration certificat merchant',
        'note': 'Implémenter avec Apple Pay JS + certificat merchant identity',
        'docs': 'https://developer.apple.com/apple-pay/implementation/'
    }


# ============================================
# GOOGLE PAY
# ============================================

@router.post("/google-pay/session")
async def create_google_pay_session(
    payment: PaymentIntent,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une session Google Pay

    NOTE: Intégrer avec Google Pay API
    """
    return {
        'success': False,
        'message': 'Google Pay nécessite configuration Merchant ID',
        'note': 'Implémenter avec Google Pay API + Merchant ID',
        'docs': 'https://developers.google.com/pay/api'
    }


# ============================================
# CRYPTO PAYMENTS
# ============================================

@router.post("/crypto/create-invoice")
async def create_crypto_invoice(
    payment: PaymentIntent,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une invoice crypto (Bitcoin, Ethereum, etc.)

    NOTE: Intégrer avec CoinBase Commerce ou BTCPay Server
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Simulation (à remplacer par vraie API CoinBase Commerce)
        import uuid

        invoice_data = {
            'user_id': user_id,
            'gateway': 'crypto',
            'amount': payment.amount,
            'currency': payment.currency,
            'crypto_currency': 'BTC',  # ou ETH, USDT, etc.
            'status': 'pending',
            'invoice_id': str(uuid.uuid4()),
            'payment_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Adresse de démo
            'metadata': payment.metadata
        }

        supabase.table('payment_transactions').insert(invoice_data).execute()

        return {
            'success': True,
            'gateway': 'crypto',
            'invoice_id': invoice_data['invoice_id'],
            'payment_address': invoice_data['payment_address'],
            'amount_crypto': 0.001,  # Conversion simulée
            'currency': 'BTC',
            'note': 'Implémenter avec CoinBase Commerce API pour production'
        }

    except Exception as e:
        logger.error(f"Crypto invoice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TRANSACTIONS HISTORY
# ============================================

@router.get("/transactions")
async def get_payment_transactions(
    status: Optional[str] = None,
    gateway: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Historique des transactions de paiement
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('payment_transactions').select('*').eq('user_id', user_id)

        if status:
            query = query.eq('status', status)

        if gateway:
            query = query.eq('gateway', gateway)

        query = query.order('created_at', desc=True)

        response = query.execute()

        return {
            'success': True,
            'transactions': response.data or [],
            'total': len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
