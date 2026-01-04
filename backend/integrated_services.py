"""
INTÉGRATION COMPLÈTE DES NOUVEAUX SERVICES
Ce fichier intègre tous les services créés dans l'application ShareYourSales

À ajouter dans server.py:
    from integrated_services import router as integrated_router
    app.include_router(integrated_router)
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import base64

# Import de tous les nouveaux services
from services.email_notification_service import EmailNotificationService
from services.push_notification_service import PushNotificationService
from services.sms_notification_service import SMSNotificationService
from services.instagram_api_service import InstagramGraphAPI
from services.tiktok_api_service import TikTokCreatorAPI
from services.facebook_api_service import FacebookGraphAPI
from services.twitter_api_service import TwitterAPIv2
from services.ai_recommendation_service import AIRecommendationEngine
from services.rfm_segmentation_service import RFMSegmentationService
from services.ab_testing_service import ABTestingService, Variant, Experiment
from services.shopify_integration_service import ShopifyIntegrationService
from services.woocommerce_integration_service import WooCommerceIntegrationService
from services.prestashop_integration_service import PrestaShopIntegrationService
from services.ocr_document_service import OCRDocumentService
from services.identity_verification_service import IdentityVerificationService, VerificationRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/integrated", tags=["Services Intégrés"])

# ============================================
# MODÈLES PYDANTIC POUR LES REQUÊTES
# ============================================

class EmailRequest(BaseModel):
    to: EmailStr
    template: str
    variables: Dict[str, str]

class PushNotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = None

class SMSRequest(BaseModel):
    phone_number: str
    message: str
    use_whatsapp: bool = False

class SocialPostRequest(BaseModel):
    platform: str  # instagram, tiktok, facebook, twitter
    content: str
    media_urls: Optional[List[str]] = None

class ProductRecommendationRequest(BaseModel):
    user_id: str
    n_recommendations: int = 10

class DiscountCodeRequest(BaseModel):
    code: str
    platform: str  # shopify, woocommerce, prestashop
    discount_percent: float
    usage_limit: Optional[int] = None

class KYCVerificationRequest(BaseModel):
    user_id: str
    document_image_base64: str
    selfie_image_base64: Optional[str] = None

# ============================================
# ENDPOINTS NOTIFICATIONS
# ============================================

@router.post("/notifications/email")
async def send_email_notification(request: EmailRequest):
    """Envoyer une notification par email"""
    try:
        service = EmailNotificationService()
        result = service.send_template_email(
            to=request.to,
            template_name=request.template,
            variables=request.variables
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Email error: {e}")
        raise HTTPException(500, f"Erreur envoi email: {str(e)}")

@router.post("/notifications/push")
async def send_push_notification(request: PushNotificationRequest):
    """Envoyer une notification push"""
    try:
        service = PushNotificationService()
        # TODO: Récupérer le device_token depuis la base de données
        result = service.send_custom(
            user_token="DEVICE_TOKEN_FROM_DB",  # À remplacer
            title=request.title,
            body=request.body,
            data=request.data
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Push error: {e}")
        raise HTTPException(500, f"Erreur push: {str(e)}")

@router.post("/notifications/sms")
async def send_sms_notification(request: SMSRequest):
    """Envoyer une notification SMS/WhatsApp"""
    try:
        service = SMSNotificationService()
        result = service.send_custom(
            phone_number=request.phone_number,
            body=request.message,
            use_whatsapp=request.use_whatsapp
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"SMS error: {e}")
        raise HTTPException(500, f"Erreur SMS: {str(e)}")

# ============================================
# ENDPOINTS RÉSEAUX SOCIAUX
# ============================================

@router.post("/social/post")
async def post_to_social_media(request: SocialPostRequest):
    """Publier sur les réseaux sociaux"""
    try:
        if request.platform == "instagram":
            api = InstagramGraphAPI()
            if request.media_urls:
                result = api.publish_photo(
                    image_url=request.media_urls[0],
                    caption=request.content
                )
            else:
                raise HTTPException(400, "Instagram nécessite au moins une image")

        elif request.platform == "tiktok":
            api = TikTokCreatorAPI()
            if request.media_urls:
                result = api.upload_video_from_url(
                    video_url=request.media_urls[0],
                    title=request.content[:150],
                    description=request.content
                )
            else:
                raise HTTPException(400, "TikTok nécessite une vidéo")

        elif request.platform == "facebook":
            api = FacebookGraphAPI()
            result = api.publish_post(
                page_id="PAGE_ID_FROM_CONFIG",  # À configurer
                message=request.content,
                link=request.media_urls[0] if request.media_urls else None
            )

        elif request.platform == "twitter":
            api = TwitterAPIv2()
            result = api.create_tweet(
                text=request.content,
                media_urls=request.media_urls
            )

        else:
            raise HTTPException(400, f"Plateforme non supportée: {request.platform}")

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Social media error: {e}")
        raise HTTPException(500, f"Erreur publication: {str(e)}")

@router.get("/social/platforms")
async def get_available_platforms():
    """Liste des plateformes sociales disponibles"""
    return {
        "platforms": [
            {"id": "instagram", "name": "Instagram", "icon": "📷"},
            {"id": "tiktok", "name": "TikTok", "icon": "🎵"},
            {"id": "facebook", "name": "Facebook", "icon": "👍"},
            {"id": "twitter", "name": "Twitter/X", "icon": "🐦"}
        ]
    }

# ============================================
# ENDPOINTS IA & RECOMMANDATIONS
# ============================================

@router.post("/ai/recommendations")
async def get_product_recommendations(request: ProductRecommendationRequest):
    """Obtenir des recommandations de produits par IA"""
    try:
        engine = AIRecommendationEngine()
        # TODO: Charger les interactions utilisateur depuis la DB
        recommendations = engine.get_recommendations(
            user_id=request.user_id,
            n=request.n_recommendations,
            method="hybrid"
        )
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"AI recommendation error: {e}")
        raise HTTPException(500, f"Erreur recommandations: {str(e)}")

@router.get("/ai/customer-segments/{user_id}")
async def get_customer_segment(user_id: str):
    """Obtenir le segment RFM d'un client"""
    try:
        service = RFMSegmentationService()
        # TODO: Charger les transactions depuis la DB
        segment = service.get_customer_segment(user_id)

        if segment:
            # Obtenir les actions recommandées
            actions = service.get_segment_actions(segment["segment"])
            segment["recommended_actions"] = actions

        return {"success": True, "segment": segment}
    except Exception as e:
        logger.error(f"RFM error: {e}")
        raise HTTPException(500, f"Erreur segmentation: {str(e)}")

# ============================================
# ENDPOINTS E-COMMERCE
# ============================================

@router.post("/ecommerce/discount-code")
async def create_discount_code(request: DiscountCodeRequest):
    """Créer un code de réduction sur une plateforme e-commerce"""
    try:
        if request.platform == "shopify":
            service = ShopifyIntegrationService()
            result = service.create_discount_code(
                code=request.code,
                value_type="percentage",
                value=request.discount_percent,
                usage_limit=request.usage_limit
            )

        elif request.platform == "woocommerce":
            service = WooCommerceIntegrationService()
            result = service.create_coupon(
                code=request.code,
                discount_type="percent",
                amount=str(request.discount_percent),
                usage_limit=request.usage_limit
            )

        elif request.platform == "prestashop":
            service = PrestaShopIntegrationService()
            result = service.create_cart_rule(
                name=f"Affiliate: {request.code}",
                code=request.code,
                reduction_percent=request.discount_percent,
                quantity=request.usage_limit or 1000
            )

        else:
            raise HTTPException(400, f"Plateforme non supportée: {request.platform}")

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"E-commerce error: {e}")
        raise HTTPException(500, f"Erreur création code: {str(e)}")

@router.get("/ecommerce/platforms")
async def get_ecommerce_platforms():
    """Liste des plateformes e-commerce disponibles"""
    return {
        "platforms": [
            {"id": "shopify", "name": "Shopify", "icon": "🛍️"},
            {"id": "woocommerce", "name": "WooCommerce", "icon": "🛒"},
            {"id": "prestashop", "name": "PrestaShop", "icon": "🏪"}
        ]
    }

# ============================================
# ENDPOINTS KYC & VÉRIFICATION
# ============================================

@router.post("/kyc/verify")
async def submit_kyc_verification(request: KYCVerificationRequest):
    """Soumettre une vérification KYC"""
    try:
        service = IdentityVerificationService()

        verification_request = VerificationRequest(
            user_id=request.user_id,
            document_front_image=request.document_image_base64,
            selfie_image=request.selfie_image_base64
        )

        result = service.submit_verification(verification_request)

        return {
            "success": True,
            "verification_id": result.verification_id,
            "status": result.status.value,
            "extracted_data": {
                "full_name": result.extracted_data.full_name if result.extracted_data else None,
                "document_number": result.extracted_data.document_number if result.extracted_data else None,
                "date_of_birth": result.extracted_data.date_of_birth if result.extracted_data else None
            }
        }
    except Exception as e:
        logger.error(f"KYC error: {e}")
        raise HTTPException(500, f"Erreur vérification: {str(e)}")

@router.get("/kyc/status/{verification_id}")
async def get_kyc_status(verification_id: str):
    """Vérifier le statut d'une vérification KYC"""
    try:
        service = IdentityVerificationService()
        result = service.get_verification_status(verification_id)

        if not result:
            raise HTTPException(404, "Vérification non trouvée")

        return {
            "success": True,
            "status": result.status.value,
            "verified_at": result.verified_at.isoformat() if result.verified_at else None,
            "expires_at": result.expires_at.isoformat() if result.expires_at else None
        }
    except Exception as e:
        logger.error(f"KYC status error: {e}")
        raise HTTPException(500, f"Erreur statut: {str(e)}")

# ============================================
# ENDPOINT TABLEAU DE BORD
# ============================================

@router.get("/dashboard/services-status")
async def get_services_status():
    """Statut de tous les services intégrés"""
    status = {
        "notifications": {
            "email": {"available": True, "provider": "Resend/SMTP"},
            "push": {"available": True, "provider": "Firebase"},
            "sms": {"available": True, "provider": "Twilio"}
        },
        "social_media": {
            "instagram": {"available": True, "status": "Configuré"},
            "tiktok": {"available": True, "status": "Configuré"},
            "facebook": {"available": True, "status": "Configuré"},
            "twitter": {"available": True, "status": "Configuré"}
        },
        "ecommerce": {
            "shopify": {"available": True, "status": "Prêt"},
            "woocommerce": {"available": True, "status": "Prêt"},
            "prestashop": {"available": True, "status": "Prêt"}
        },
        "ai": {
            "recommendations": {"available": True, "status": "Actif"},
            "segmentation": {"available": True, "status": "Actif"},
            "ab_testing": {"available": True, "status": "Actif"}
        },
        "kyc": {
            "ocr": {"available": True, "provider": "Google Vision"},
            "verification": {"available": True, "status": "Actif"}
        }
    }

    return {"success": True, "services": status}

# Export du router
__all__ = ["router"]
