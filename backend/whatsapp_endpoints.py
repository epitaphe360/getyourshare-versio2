"""
WhatsApp Business API Endpoints

Endpoints pour gérer l'intégration WhatsApp:
- Envoyer des messages
- Envoyer des notifications
- Partager des liens d'affiliation
- Support client
- Catalogues produits
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

from services.whatsapp_business_service import whatsapp_service

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Business"])


# ==================== MODELS ====================

class SendMessageRequest(BaseModel):
    """Requête pour envoyer un message WhatsApp"""
    to_phone: str = Field(..., description="Numéro de téléphone au format international")
    message: str = Field(..., description="Contenu du message")
    preview_url: bool = Field(default=False, description="Activer l'aperçu des liens")

class SendTemplateRequest(BaseModel):
    """Requête pour envoyer un template WhatsApp"""
    to_phone: str
    template_name: str = Field(..., description="Nom du template pré-approuvé")
    language_code: str = Field(default="fr", description="Code langue (fr, ar, en)")
    parameters: Optional[List[str]] = Field(default=None, description="Paramètres du template")

class SendAffiliateLinkRequest(BaseModel):
    """Requête pour partager un lien d'affiliation"""
    to_phone: str
    product_id: str
    product_name: str
    affiliate_link: str
    commission_rate: float
    product_image_url: Optional[str] = None

class SendNotificationRequest(BaseModel):
    """Requête pour envoyer une notification"""
    to_phone: str
    notification_type: str = Field(..., description="Type: new_commission, payout_approved, new_sale, new_message")
    data: Dict[str, Any] = Field(..., description="Données de la notification")

class SendInteractiveRequest(BaseModel):
    """Requête pour envoyer un message interactif"""
    to_phone: str
    body_text: str
    buttons: List[Dict[str, str]] = Field(..., max_items=3, description="Max 3 boutons")
    header_text: Optional[str] = None
    footer_text: Optional[str] = None

class CreateCatalogRequest(BaseModel):
    """Requête pour créer un catalogue produits"""
    catalog_name: str
    products: List[Dict[str, Any]]

class WhatsAppWebhookEvent(BaseModel):
    """Événement reçu du webhook WhatsApp"""
    object: str
    entry: List[Dict[str, Any]]


# ==================== ENDPOINTS ====================

@router.post("/send-message", summary="Envoyer un message texte simple")
async def send_message(request: SendMessageRequest):
    """
    Envoyer un message WhatsApp texte simple

    Cas d'usage:
    - Messages de support client
    - Confirmations manuelles
    - Communications ad-hoc
    """
    result = await whatsapp_service.send_text_message(
        to_phone=request.to_phone,
        message=request.message,
        preview_url=request.preview_url
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur envoi WhatsApp: {result.get('error')}"
        )

    return {
        "success": True,
        "message_id": result["message_id"],
        "status": result["status"],
        "demo_mode": result.get("demo_mode", False)
    }


@router.post("/send-template", summary="Envoyer un template pré-approuvé")
async def send_template(request: SendTemplateRequest):
    """
    Envoyer un message template WhatsApp

    Templates disponibles:
    - new_commission: Nouvelle commission gagnée
    - payout_approved: Paiement approuvé
    - new_sale: Nouvelle vente réalisée
    - welcome_influencer: Bienvenue influenceur

    Note: Les templates doivent être créés et approuvés dans Meta Business Manager
    """
    result = await whatsapp_service.send_template_message(
        to_phone=request.to_phone,
        template_name=request.template_name,
        language_code=request.language_code,
        parameters=request.parameters
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur envoi template: {result.get('error')}"
        )

    return {
        "success": True,
        "message_id": result["message_id"],
        "template_name": result["template_name"],
        "demo_mode": result.get("demo_mode", False)
    }


@router.post("/send-affiliate-link", summary="Partager un lien d'affiliation")
async def send_affiliate_link(request: SendAffiliateLinkRequest):
    """
    Envoyer un lien d'affiliation via WhatsApp

    Le message inclut:
    - Nom du produit
    - Taux de commission
    - Lien d'affiliation avec aperçu
    - Message motivant

    Cas d'usage:
    - Influenceur partage un produit à ses contacts
    - Partage rapide depuis le dashboard
    """
    result = await whatsapp_service.send_affiliate_link(
        to_phone=request.to_phone,
        product_name=request.product_name,
        affiliate_link=request.affiliate_link,
        commission_rate=request.commission_rate,
        product_image_url=request.product_image_url
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur partage lien: {result.get('error')}"
        )

    return {
        "success": True,
        "message_id": result["message_id"],
        "product_name": request.product_name,
        "demo_mode": result.get("demo_mode", False)
    }


@router.post("/send-notification", summary="Envoyer une notification transactionnelle")
async def send_notification(request: SendNotificationRequest):
    """
    Envoyer une notification WhatsApp

    Types supportés:
    - new_commission: {"amount": "500", "product_name": "Produit X"}
    - payout_approved: {"amount": "1000", "method": "Cash Plus"}
    - new_sale: {"product_name": "Produit Y", "commission": "50"}
    - new_message: {"sender_name": "John Doe"}

    Utilise automatiquement le bon template selon le type
    """
    result = await whatsapp_service.send_notification(
        to_phone=request.to_phone,
        notification_type=request.notification_type,
        data=request.data
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur envoi notification: {result.get('error')}"
        )

    return {
        "success": True,
        "message_id": result["message_id"],
        "notification_type": request.notification_type,
        "demo_mode": result.get("demo_mode", False)
    }


@router.post("/send-interactive", summary="Envoyer un message avec boutons")
async def send_interactive(request: SendInteractiveRequest):
    """
    Envoyer un message WhatsApp avec boutons interactifs

    Cas d'usage:
    - Validation de commandes
    - Choix multiples (accepter/refuser)
    - Actions rapides

    Limite: 3 boutons maximum
    """
    result = await whatsapp_service.send_interactive_buttons(
        to_phone=request.to_phone,
        body_text=request.body_text,
        buttons=request.buttons,
        header_text=request.header_text,
        footer_text=request.footer_text
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur envoi message interactif: {result.get('error')}"
        )

    return {
        "success": True,
        "message_id": result["message_id"],
        "buttons_count": len(request.buttons),
        "demo_mode": result.get("demo_mode", False)
    }


@router.post("/create-catalog", summary="Créer un catalogue produits")
async def create_catalog(request: CreateCatalogRequest):
    """
    Créer ou mettre à jour un catalogue produits WhatsApp Business

    Permet aux clients de voir vos produits directement dans WhatsApp

    Structure produit:
    {
        "name": "Nom du produit",
        "price": 299.99,
        "currency": "MAD",
        "description": "Description",
        "image_url": "https://...",
        "url": "https://..."
    }
    """
    result = await whatsapp_service.create_product_catalog(
        catalog_name=request.catalog_name,
        products=request.products
    )

    return {
        "success": result["success"],
        "catalog_id": result.get("catalog_id"),
        "products_count": result.get("products_count"),
        "demo_mode": result.get("demo_mode", False)
    }


@router.get("/share-url", summary="Générer une URL de partage WhatsApp")
async def get_share_url(
    text: str,
    url: Optional[str] = None
):
    """
    Générer une URL pour partager du contenu sur WhatsApp

    Ouvre WhatsApp (mobile ou desktop) avec le message pré-rempli

    Cas d'usage:
    - Bouton "Partager sur WhatsApp" dans l'interface
    - Partage de liens d'affiliation
    - Partage de produits
    """
    share_url = whatsapp_service.get_whatsapp_share_url(text, url)

    return {
        "share_url": share_url,
        "text": text,
        "url": url
    }


@router.get("/direct-url", summary="Générer une URL de message direct")
async def get_direct_url(
    phone: str,
    text: str = "Bonjour"
):
    """
    Générer une URL pour envoyer un message direct à un numéro

    Cas d'usage:
    - Support client (lien "Contacter sur WhatsApp")
    - Communication influenceur-marchand
    """
    direct_url = whatsapp_service.get_whatsapp_direct_url(phone, text)

    return {
        "direct_url": direct_url,
        "phone": phone,
        "text": text
    }


@router.post("/webhook", summary="Webhook pour recevoir les messages WhatsApp")
async def whatsapp_webhook(
    event: WhatsAppWebhookEvent,
    background_tasks: BackgroundTasks
):
    """
    Webhook pour recevoir les événements WhatsApp

    Configure cette URL dans Meta Business Manager:
    https://your-api.com/api/whatsapp/webhook

    Événements reçus:
    - Messages entrants
    - Status des messages envoyés
    - Réponses aux boutons interactifs
    """
    # Traiter en arrière-plan pour répondre rapidement
    background_tasks.add_task(process_webhook_event, event)

    return {"status": "received"}


@router.get("/webhook", summary="Vérification du webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """
    Endpoint de vérification du webhook WhatsApp

    Meta envoie une requête GET pour vérifier que vous possédez l'URL
    """
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "shareyoursales_webhook_2025")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Token de vérification invalide")


# ==================== BACKGROUND TASKS ====================

async def process_webhook_event(event: WhatsAppWebhookEvent):
    """
    Traiter les événements reçus du webhook WhatsApp

    Actions possibles:
    - Sauvegarder le message en DB
    - Envoyer notification au destinataire
    - Répondre automatiquement (chatbot)
    - Analyser les métriques
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        for entry in event.entry:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    message_id = message.get("id")
                    from_number = message.get("from")
                    message_type = message.get("type")
                    timestamp = message.get("timestamp")
                    
                    text_body = ""
                    if message_type == "text":
                        text_body = message.get("text", {}).get("body", "")

                    logger.info(f"📱 Message WhatsApp reçu de {from_number}: {message_type} - {text_body}")

                    # Sauvegarder en DB (Exemple avec Supabase si table existe)
                    # supabase.table("whatsapp_messages").insert({
                    #     "message_id": message_id,
                    #     "from_number": from_number,
                    #     "type": message_type,
                    #     "content": text_body,
                    #     "raw_data": message
                    # }).execute()
                    
                    # Auto-réponse simple (Echo)
                    if message_type == "text":
                        await whatsapp_service.send_text_message(
                            to_phone=from_number,
                            message=f"Merci pour votre message: '{text_body}'. Nous vous répondrons bientôt."
                        )

    except Exception as e:
        logger.error(f"❌ Erreur traitement webhook WhatsApp: {str(e)}")
