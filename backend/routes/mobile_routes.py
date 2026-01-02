"""
Routes Mobile Features
WhatsApp Business API + Mobile Payments Morocco (Orange Money, inwi money, Maroc Telecom Cash)
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import requests
import os

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Mobile"])


# ============================================
# MODELS
# ============================================

class WhatsAppMessage(BaseModel):
    to: str  # Numéro de téléphone (format: +212...)
    message: str
    media_url: Optional[str] = None


class MobilePaymentRequest(BaseModel):
    phone_number: str  # Format: +212XXXXXXXXX
    amount: float
    provider: str  # orange_money, inwi_money, maroc_telecom_cash
    order_id: Optional[str] = None


# ============================================
# WHATSAPP BUSINESS
# ============================================

@router.post("/api/whatsapp/send")
async def send_whatsapp(
    msg: WhatsAppMessage,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Envoyer un message WhatsApp via WhatsApp Business API

    NOTE: Nécessite:
    - Meta Business Account
    - WhatsApp Business API access
    - Numéro de téléphone professionnel vérifié
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Configuration WhatsApp Business API
        whatsapp_token = os.getenv("WHATSAPP_BUSINESS_TOKEN")
        whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

        if not whatsapp_token or not whatsapp_phone_id:
            raise HTTPException(status_code=500, detail="WhatsApp Business API non configuré")

        # Nettoyer le numéro
        to_number = msg.to.replace('+', '').replace(' ', '').replace('-', '')

        # Envoyer via WhatsApp Business API
        url = f"https://graph.facebook.com/v18.0/{whatsapp_phone_id}/messages"

        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }

        # Message texte
        if not msg.media_url:
            payload_data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": msg.message
                }
            }
        else:
            # Message avec media
            payload_data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "image",
                "image": {
                    "link": msg.media_url,
                    "caption": msg.message
                }
            }

        response = requests.post(url, headers=headers, json=payload_data, timeout=10)

        if response.status_code != 200:
            raise Exception(f"WhatsApp API error: {response.text}")

        wa_response = response.json()

        # Sauvegarder dans DB
        message_data = {
            'user_id': user_id,
            'to_number': to_number,
            'message': msg.message,
            'media_url': msg.media_url,
            'whatsapp_message_id': wa_response.get('messages', [{}])[0].get('id'),
            'status': 'sent',
            'sent_at': datetime.now().isoformat()
        }

        supabase.table('whatsapp_messages').insert(message_data).execute()

        return {
            "success": True,
            "status": "sent",
            "message_id": wa_response.get('messages', [{}])[0].get('id'),
            "to": to_number
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook WhatsApp Business pour recevoir les messages et les statuts

    Events gérés:
    - messages (message reçu)
    - message_status (delivered, read, failed)
    """
    try:
        payload = await request.body()
        data = json.loads(payload) if payload else {}

        # Vérifier le token de vérification (lors de la configuration)
        if request.method == "GET":
            verify_token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")

            expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "getyourshare_webhook_token")

            if verify_token == expected_token:
                return int(challenge)
            else:
                raise HTTPException(status_code=403, detail="Invalid verify token")

        # Gérer les événements
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        # Message reçu
        if 'messages' in value:
            for message in value.get('messages', []):
                from_number = message.get('from')
                message_id = message.get('id')
                message_type = message.get('type')

                if message_type == 'text':
                    text = message.get('text', {}).get('body')

                    # Sauvegarder
                    supabase.table('whatsapp_messages').insert({
                        'from_number': from_number,
                        'message': text,
                        'whatsapp_message_id': message_id,
                        'direction': 'inbound',
                        'received_at': datetime.now().isoformat()
                    }).execute()

                    logger.info(f"WhatsApp message received from {from_number}: {text}")

        # Statut du message
        if 'statuses' in value:
            for status in value.get('statuses', []):
                message_id = status.get('id')
                status_type = status.get('status')  # sent, delivered, read, failed

                # Mettre à jour le statut
                supabase.table('whatsapp_messages').update({
                    'status': status_type,
                    'updated_at': datetime.now().isoformat()
                }).eq('whatsapp_message_id', message_id).execute()

        return {"received": True}

    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return {"error": str(e)}


# ============================================
# MOBILE PAYMENTS MOROCCO
# ============================================

@router.post("/api/mobile-payments-ma/initiate")
async def initiate_mobile_payment(
    payment: MobilePaymentRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Initier un paiement mobile au Maroc

    Providers:
    - orange_money (Orange Money)
    - inwi_money (inwi money)
    - maroc_telecom_cash (Maroc Telecom Cash)

    NOTE: Nécessite intégration avec les API des opérateurs:
    - Orange Money API
    - inwi money API
    - Maroc Telecom Cash API
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Valider le provider
        valid_providers = ['orange_money', 'inwi_money', 'maroc_telecom_cash']
        if payment.provider not in valid_providers:
            raise HTTPException(status_code=400, detail="Provider invalide")

        # Valider le numéro (Maroc)
        if not payment.phone_number.startswith('+212') and not payment.phone_number.startswith('212') and not payment.phone_number.startswith('0'):
            raise HTTPException(status_code=400, detail="Numéro invalide (Maroc uniquement)")

        # Nettoyer le numéro
        phone = payment.phone_number.replace('+', '').replace(' ', '')
        if phone.startswith('212'):
            phone = '0' + phone[3:]

        # Générer transaction ID
        import uuid
        transaction_id = f"MA_{payment.provider.upper()}_{uuid.uuid4().hex[:12]}"

        # Initier le paiement selon le provider
        if payment.provider == 'orange_money':
            # Orange Money API (simulation)
            # Dans la réalité, appeler l'API Orange Money
            payment_status = "pending"
            external_reference = f"OM_{uuid.uuid4().hex[:8]}"

            # TODO: Intégrer vraie API Orange Money
            # response = requests.post("https://api.orange.com/mobile-money/...", ...)

        elif payment.provider == 'inwi_money':
            # inwi money API (simulation)
            payment_status = "pending"
            external_reference = f"IW_{uuid.uuid4().hex[:8]}"

            # TODO: Intégrer vraie API inwi money

        elif payment.provider == 'maroc_telecom_cash':
            # Maroc Telecom Cash API (simulation)
            payment_status = "pending"
            external_reference = f"MT_{uuid.uuid4().hex[:8]}"

            # TODO: Intégrer vraie API Maroc Telecom

        else:
            raise HTTPException(status_code=400, detail="Provider non supporté")

        # Sauvegarder la transaction
        transaction_data = {
            'user_id': user_id,
            'transaction_id': transaction_id,
            'provider': payment.provider,
            'phone_number': phone,
            'amount': payment.amount,
            'currency': 'MAD',
            'status': payment_status,
            'external_reference': external_reference,
            'order_id': payment.order_id,
            'initiated_at': datetime.now().isoformat()
        }

        supabase.table('mobile_payments').insert(transaction_data).execute()

        return {
            "success": True,
            "transaction_id": transaction_id,
            "provider": payment.provider,
            "amount": payment.amount,
            "currency": "MAD",
            "status": payment_status,
            "message": "Paiement initié. Confirmez sur votre téléphone.",
            "note": "Intégrer avec API Orange Money/inwi money/Maroc Telecom pour production"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mobile payment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/mobile-payments-ma/status/{transaction_id}")
async def get_mobile_payment_status(
    transaction_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Vérifier le statut d'un paiement mobile
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer la transaction
        transaction = supabase.table('mobile_payments').select('*').eq('transaction_id', transaction_id).eq('user_id', user_id).single().execute()

        if not transaction.data:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        # Dans la réalité, on interrogerait l'API du provider pour obtenir le statut réel
        # Pour la démo, on simule
        current_status = transaction.data.get('status')

        # Simuler une progression (pending → processing → completed)
        if current_status == 'pending':
            # Simuler un changement de statut aléatoire
            import random
            if random.random() > 0.5:
                new_status = 'processing'
                supabase.table('mobile_payments').update({'status': new_status}).eq('transaction_id', transaction_id).execute()
                transaction.data['status'] = new_status

        return {
            "success": True,
            **transaction.data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/mobile-payments-ma/webhook/{provider}")
async def mobile_payment_webhook(
    provider: str,
    request: Request
):
    """
    Webhook pour recevoir les notifications des opérateurs mobiles

    Providers: orange_money, inwi_money, maroc_telecom_cash
    """
    try:
        payload = await request.body()
        data = json.loads(payload) if payload else {}

        # Log le webhook
        webhook_log = {
            'provider': provider,
            'payload': data,
            'received_at': datetime.now().isoformat()
        }

        supabase.table('mobile_payment_webhooks').insert(webhook_log).execute()

        # Traiter selon le provider
        if provider == 'orange_money':
            # Mapper les champs Orange Money
            transaction_id = data.get('transaction_id')
            status = data.get('status')  # success, failed, cancelled

            if transaction_id:
                supabase.table('mobile_payments').update({
                    'status': 'completed' if status == 'success' else 'failed',
                    'completed_at': datetime.now().isoformat()
                }).eq('external_reference', transaction_id).execute()

        elif provider == 'inwi_money':
            # Mapper les champs inwi money
            pass

        elif provider == 'maroc_telecom_cash':
            # Mapper les champs Maroc Telecom
            pass

        return {"received": True}

    except Exception as e:
        logger.error(f"Mobile payment webhook error: {e}")
        return {"error": str(e)}


# ============================================
# HISTORY
# ============================================

@router.get("/api/mobile-payments-ma/history")
async def get_mobile_payments_history(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Historique des paiements mobiles
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('mobile_payments').select('*').eq('user_id', user_id)

        if provider:
            query = query.eq('provider', provider)

        if status:
            query = query.eq('status', status)

        query = query.order('initiated_at', desc=True).limit(limit)

        response = query.execute()

        return {
            "success": True,
            "payments": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
