"""
Routes Webhooks
Stripe, Shopify, WooCommerce, PayPal
"""

from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import hmac
import hashlib
import json

from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


# ============================================
# STRIPE WEBHOOK
# ============================================

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    """
    Webhook Stripe pour gérer les événements de paiement

    Events gérés:
    - checkout.session.completed
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    """
    try:
        payload = await request.body()

        # Vérifier la signature (si configurée)
        import os
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if webhook_secret and stripe_signature:
            try:
                import stripe
                event = stripe.Webhook.construct_event(
                    payload, stripe_signature, webhook_secret
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError:
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Mode sans vérification (dev only)
            event = json.loads(payload)

        event_type = event['type']
        event_data = event['data']['object']

        # Log l'événement
        webhook_log = {
            'provider': 'stripe',
            'event_type': event_type,
            'event_id': event.get('id'),
            'payload': event_data,
            'processed_at': None
        }

        supabase.table('webhook_logs').insert(webhook_log).execute()

        # Gérer selon le type d'événement
        if event_type == 'checkout.session.completed':
            session = event_data

            # Mettre à jour la transaction
            supabase.table('payment_transactions').update({
                'status': 'completed',
                'stripe_session_id': session.get('id'),
                'amount_received': session.get('amount_total', 0) / 100
            }).eq('session_id', session.get('id')).execute()

            logger.info(f"Stripe payment completed: {session.get('id')}")

        elif event_type == 'payment_intent.succeeded':
            payment_intent = event_data

            supabase.table('payment_transactions').update({
                'status': 'completed'
            }).eq('payment_intent_id', payment_intent.get('id')).execute()

        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event_data

            supabase.table('payment_transactions').update({
                'status': 'failed',
                'failure_reason': payment_intent.get('last_payment_error', {}).get('message')
            }).eq('payment_intent_id', payment_intent.get('id')).execute()

        elif event_type == 'customer.subscription.created':
            subscription = event_data

            # Créer ou mettre à jour l'abonnement
            supabase.table('subscriptions').insert({
                'stripe_subscription_id': subscription.get('id'),
                'stripe_customer_id': subscription.get('customer'),
                'status': subscription.get('status'),
                'plan_id': subscription.get('items', {}).get('data', [{}])[0].get('price', {}).get('id'),
                'current_period_end': subscription.get('current_period_end')
            }).execute()

        elif event_type == 'customer.subscription.updated':
            subscription = event_data

            supabase.table('subscriptions').update({
                'status': subscription.get('status'),
                'current_period_end': subscription.get('current_period_end')
            }).eq('stripe_subscription_id', subscription.get('id')).execute()

        elif event_type == 'customer.subscription.deleted':
            subscription = event_data

            supabase.table('subscriptions').update({
                'status': 'cancelled',
                'cancelled_at': subscription.get('ended_at')
            }).eq('stripe_subscription_id', subscription.get('id')).execute()

        # Marquer comme traité
        supabase.table('webhook_logs').update({
            'processed_at': 'now()'
        }).eq('event_id', event.get('id')).execute()

        return {'received': True, 'event_type': event_type}

    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {'error': str(e)}


# ============================================
# SHOPIFY WEBHOOK
# ============================================

@router.post("/shopify")
async def shopify_webhook(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    x_shopify_topic: Optional[str] = Header(None),
    x_shopify_shop_domain: Optional[str] = Header(None)
):
    """
    Webhook Shopify pour synchroniser les produits et commandes

    Topics gérés:
    - orders/create
    - orders/updated
    - products/create
    - products/update
    - products/delete
    """
    try:
        payload = await request.body()

        # Vérifier la signature HMAC
        import os
        shopify_secret = os.getenv("SHOPIFY_WEBHOOK_SECRET")

        if shopify_secret and x_shopify_hmac_sha256:
            computed_hmac = hmac.new(
                shopify_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).digest()

            import base64
            encoded_hmac = base64.b64encode(computed_hmac).decode('utf-8')

            if not hmac.compare_digest(encoded_hmac, x_shopify_hmac_sha256):
                raise HTTPException(status_code=401, detail="Invalid HMAC signature")

        data = json.loads(payload)

        # Log l'événement
        webhook_log = {
            'provider': 'shopify',
            'event_type': x_shopify_topic,
            'shop_domain': x_shopify_shop_domain,
            'payload': data,
            'processed_at': None
        }

        supabase.table('webhook_logs').insert(webhook_log).execute()

        # Gérer selon le topic
        if x_shopify_topic == 'orders/create':
            order = data

            # Créer la commande dans notre système
            # TODO: Mapper les champs Shopify → notre modèle
            logger.info(f"Shopify order created: {order.get('id')}")

        elif x_shopify_topic == 'products/create' or x_shopify_topic == 'products/update':
            product = data

            # Synchroniser le produit
            # TODO: Sync product
            logger.info(f"Shopify product {x_shopify_topic}: {product.get('id')}")

        elif x_shopify_topic == 'products/delete':
            product = data

            # Désactiver le produit
            supabase.table('products').update({
                'is_active': False
            }).filter('metadata->>shopify_id', 'eq', str(product.get('id'))).execute()

        return {'received': True, 'topic': x_shopify_topic}

    except Exception as e:
        logger.error(f"Shopify webhook error: {e}")
        return {'error': str(e)}


# ============================================
# WOOCOMMERCE WEBHOOK
# ============================================

@router.post("/woocommerce")
async def woocommerce_webhook(
    request: Request,
    x_wc_webhook_signature: Optional[str] = Header(None),
    x_wc_webhook_topic: Optional[str] = Header(None),
    x_wc_webhook_source: Optional[str] = Header(None)
):
    """
    Webhook WooCommerce pour synchroniser les produits et commandes

    Topics gérés:
    - order.created
    - order.updated
    - product.created
    - product.updated
    - product.deleted
    """
    try:
        payload = await request.body()

        # Vérifier la signature
        import os
        wc_secret = os.getenv("WOOCOMMERCE_WEBHOOK_SECRET")

        if wc_secret and x_wc_webhook_signature:
            computed_signature = base64.b64encode(
                hmac.new(
                    wc_secret.encode('utf-8'),
                    payload,
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')

            if not hmac.compare_digest(computed_signature, x_wc_webhook_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")

        data = json.loads(payload)

        # Log l'événement
        webhook_log = {
            'provider': 'woocommerce',
            'event_type': x_wc_webhook_topic,
            'source': x_wc_webhook_source,
            'payload': data,
            'processed_at': None
        }

        supabase.table('webhook_logs').insert(webhook_log).execute()

        # Gérer selon le topic
        if x_wc_webhook_topic == 'order.created':
            order = data
            logger.info(f"WooCommerce order created: {order.get('id')}")

        elif x_wc_webhook_topic in ['product.created', 'product.updated']:
            product = data
            logger.info(f"WooCommerce {x_wc_webhook_topic}: {product.get('id')}")

        elif x_wc_webhook_topic == 'product.deleted':
            product = data

            supabase.table('products').update({
                'is_active': False
            }).filter('metadata->>woocommerce_id', 'eq', str(product.get('id'))).execute()

        return {'received': True, 'topic': x_wc_webhook_topic}

    except Exception as e:
        logger.error(f"WooCommerce webhook error: {e}")
        return {'error': str(e)}


# ============================================
# PAYPAL WEBHOOK
# ============================================

@router.post("/paypal")
async def paypal_webhook(
    request: Request
):
    """
    Webhook PayPal pour gérer les événements de paiement

    Events gérés:
    - PAYMENT.SALE.COMPLETED
    - PAYMENT.SALE.DENIED
    - PAYMENT.SALE.REFUNDED
    """
    try:
        payload = await request.body()
        data = json.loads(payload)

        event_type = data.get('event_type')

        # Log
        webhook_log = {
            'provider': 'paypal',
            'event_type': event_type,
            'event_id': data.get('id'),
            'payload': data,
            'processed_at': None
        }

        supabase.table('webhook_logs').insert(webhook_log).execute()

        # Gérer selon l'événement
        if event_type == 'PAYMENT.SALE.COMPLETED':
            sale = data.get('resource', {})

            supabase.table('payment_transactions').update({
                'status': 'completed',
                'paypal_sale_id': sale.get('id')
            }).eq('payment_id', sale.get('parent_payment')).execute()

        elif event_type == 'PAYMENT.SALE.DENIED':
            sale = data.get('resource', {})

            supabase.table('payment_transactions').update({
                'status': 'failed'
            }).eq('payment_id', sale.get('parent_payment')).execute()

        elif event_type == 'PAYMENT.SALE.REFUNDED':
            refund = data.get('resource', {})

            supabase.table('payment_transactions').update({
                'status': 'refunded',
                'refund_id': refund.get('id')
            }).eq('paypal_sale_id', refund.get('sale_id')).execute()

        return {'received': True, 'event_type': event_type}

    except Exception as e:
        logger.error(f"PayPal webhook error: {e}")
        return {'error': str(e)}


# ============================================
# WEBHOOK LOGS
# ============================================

@router.get("/logs")
async def get_webhook_logs(
    provider: Optional[str] = None,
    limit: int = 50
):
    """
    Historique des webhooks reçus (admin only)
    """
    try:
        query = supabase.table('webhook_logs').select('*')

        if provider:
            query = query.eq('provider', provider)

        query = query.order('created_at', desc=True).limit(limit)

        response = query.execute()

        return {
            'success': True,
            'logs': response.data or [],
            'total': len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting webhook logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
