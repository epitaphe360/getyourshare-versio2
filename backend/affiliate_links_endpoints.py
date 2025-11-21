"""
Affiliate Links Management Endpoints
Gestion des liens d'affiliation des influenceurs avec publication auto

Endpoints:
- GET /api/affiliate/my-links - Mes liens affiliés
- POST /api/affiliate/generate-link - Générer nouveau lien
- GET /api/affiliate/link/{id}/stats - Stats d'un lien
- POST /api/affiliate/link/{id}/publish - Publier sur réseaux sociaux
- GET /api/affiliate/publications - Historique publications
- DELETE /api/affiliate/link/{id} - Désactiver lien
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import hashlib
import secrets
import structlog

from auth import get_current_user
from supabase_client import supabase
from services.social_auto_publish_service import auto_publisher

router = APIRouter(prefix="/api/affiliate", tags=["Affiliate Links"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class GenerateLinkRequest(BaseModel):
    """Générer un lien d'affiliation"""
    product_id: str = Field(..., description="ID du produit")
    custom_slug: Optional[str] = Field(None, max_length=50, description="Slug personnalisé (optionnel)")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "uuid-product-123",
                "custom_slug": "ma-promo-beaute"
            }
        }


class PublishToSocialRequest(BaseModel):
    """Publier lien sur réseaux sociaux"""
    platforms: List[str] = Field(..., description="Plateformes (instagram, tiktok, facebook)")
    custom_caption: Optional[str] = Field(None, description="Caption personnalisée (optionnel)")
    media_urls: Optional[dict] = Field(None, description="URLs des médias par plateforme")

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": ["instagram", "facebook"],
                "custom_caption": "Découvrez cette offre incroyable! 🔥",
                "media_urls": {
                    "instagram": "https://...",
                    "facebook": "https://..."
                }
            }
        }


# ============================================
# ENDPOINTS
# ============================================

@router.get("/my-links", response_model=dict)
async def get_my_affiliate_links(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer tous mes liens d'affiliation

    **Returns:**
    - Liste des liens avec produit associé
    - Stats par lien (clics, conversions, commissions)
    - Lien généré complet
    """
    user_id = current_user.get("id")

    try:
        offset = (page - 1) * limit

        # Récupérer liens avec info produit
        result = supabase.table('affiliate_links').select(
            '*',
            'products(id, name, description, images, discounted_price, merchant_id)'
        ).eq('influencer_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        links = result.data or []

        # Enrichir avec stats
        for link in links:
            link_id = link['id']

            # Stats tracking
            stats_result = supabase.table('tracking_events').select('*', count='exact').eq('link_id', link_id).execute()

            clicks_count = stats_result.count or 0

            # Conversions
            conv_result = supabase.table('conversions').select('*', count='exact').eq('link_id', link_id).execute()
            conversions_count = conv_result.count or 0

            # Commissions
            comm_result = supabase.table('commissions').select('amount').eq('link_id', link_id).eq('status', 'approved').execute()
            total_commissions = sum(c.get('amount', 0) for c in (comm_result.data or []))

            link['stats'] = {
                'clicks': clicks_count,
                'conversions': conversions_count,
                'total_commissions': float(total_commissions) if total_commissions else 0.0,
                'conversion_rate': round((conversions_count / clicks_count * 100), 2) if clicks_count > 0 else 0.0
            }

            # Générer lien complet
            link['full_url'] = f"https://shareyoursales.ma/r/{link['short_code']}"

            # QR code URL
            link['qr_code_url'] = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={link['full_url']}"

        return {
            "success": True,
            "links": links,
            "total": len(links),
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_my_affiliate_links_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des liens"
        )


@router.post("/generate-link", response_model=dict, status_code=201)
async def generate_affiliate_link(
    request_data: GenerateLinkRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Générer un nouveau lien d'affiliation

    **Requis:**
    - Être approuvé comme affilié pour ce produit

    **Returns:**
    - Lien court généré
    - QR code
    - Statistiques à 0
    """
    user_id = current_user.get("id")
    product_id = request_data.product_id

    try:
        # Vérifier que l'utilisateur est approuvé pour ce produit
        # Table is 'affiliation_requests', status is 'active'
        affiliate_result = supabase.table('affiliation_requests').select('*').eq('influencer_id', user_id).eq('product_id', product_id).eq('status', 'active').execute()

        if not affiliate_result.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous devez être approuvé comme affilié pour ce produit"
            )

        affiliate_request = affiliate_result.data[0]
        merchant_id = affiliate_request['merchant_id']
        commission_rate = affiliate_request.get('commission_rate', 5.0)

        # Vérifier si lien déjà existe
        # Removed .eq('is_active', True) as column doesn't exist
        existing_link = supabase.table('affiliate_links').select('*').eq('influencer_id', user_id).eq('product_id', product_id).execute()

        if existing_link.data:
            # Retourner lien existant
            link = existing_link.data[0]
            # Map unique_code to short_code
            code = link.get('unique_code')
            return {
                "success": True,
                "message": "Lien existant retourné",
                "link": {
                    **link,
                    "short_code": code,
                    "full_url": f"https://shareyoursales.ma/r/{code}",
                    "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://shareyoursales.ma/r/{code}"
                }
            }

        # Générer short code unique
        if request_data.custom_slug:
            # Vérifier disponibilité
            check_slug = supabase.table('affiliate_links').select('id').eq('unique_code', request_data.custom_slug).execute()
            if check_slug.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce slug est déjà utilisé"
                )
            short_code = request_data.custom_slug
        else:
            # Générer code aléatoire (8 caractères)
            while True:
                short_code = secrets.token_urlsafe(6)[:8]
                check = supabase.table('affiliate_links').select('id').eq('unique_code', short_code).execute()
                if not check.data:
                    break

        # Créer lien
        affiliate_link = {
            'influencer_id': user_id,
            # 'merchant_id': merchant_id, # Removed
            'product_id': product_id,
            'unique_code': short_code, # Changed from short_code
            'url': f"https://shareyoursales.ma/r/{short_code}", # Added url
            # 'commission_rate': commission_rate, # Removed
            # 'is_active': True, # Removed
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('affiliate_links').insert(affiliate_link).execute()

        if not result.data:
            raise Exception("Failed to create affiliate link")

        link = result.data[0]

        logger.info("affiliate_link_generated", user_id=user_id, product_id=product_id, short_code=short_code)

        return {
            "success": True,
            "message": "Lien d'affiliation créé avec succès",
            "link": {
                **link,
                "full_url": f"https://shareyoursales.ma/r/{short_code}",
                "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://shareyoursales.ma/r/{short_code}",
                "stats": {
                    "clicks": 0,
                    "conversions": 0,
                    "total_commissions": 0.0,
                    "conversion_rate": 0.0
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("generate_affiliate_link_failed", user_id=user_id, product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération du lien"
        )


@router.get("/link/{link_id}/stats", response_model=dict)
async def get_link_stats(
    link_id: str,
    period: str = "all",  # all, today, week, month
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques détaillées d'un lien

    **Métriques:**
    - Clics totaux
    - Conversions
    - Taux de conversion
    - Commissions gagnées
    - Evolution dans le temps
    - Origine du trafic (platform)
    """
    user_id = current_user.get("id")

    try:
        # Vérifier ownership
        link_result = supabase.table('affiliate_links').select('*').eq('id', link_id).eq('influencer_id', user_id).execute()

        if not link_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lien non trouvé"
            )

        # TODO: Implémenter filtres par période

        # Récupérer stats
        stats = {}

        # Clics
        clicks_result = supabase.table('tracking_events').select('*', count='exact').eq('link_id', link_id).eq('event_type', 'click').execute()
        stats['clicks'] = clicks_result.count or 0

        # Conversions
        conversions_result = supabase.table('conversions').select('*', count='exact').eq('link_id', link_id).execute()
        stats['conversions'] = conversions_result.count or 0

        # Commissions
        commissions_result = supabase.table('commissions').select('amount, status').eq('link_id', link_id).execute()
        commissions = commissions_result.data or []

        stats['total_commissions'] = sum(c['amount'] for c in commissions)
        stats['pending_commissions'] = sum(c['amount'] for c in commissions if c['status'] == 'pending')
        stats['paid_commissions'] = sum(c['amount'] for c in commissions if c['status'] == 'paid')

        # Taux conversion
        stats['conversion_rate'] = round((stats['conversions'] / stats['clicks'] * 100), 2) if stats['clicks'] > 0 else 0.0

        return {
            "success": True,
            "link_id": link_id,
            "stats": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_link_stats_failed", link_id=link_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des stats"
        )


@router.post("/link/{link_id}/publish", response_model=dict)
async def publish_link_to_social(
    link_id: str,
    publish_data: PublishToSocialRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Publier le lien d'affiliation sur les réseaux sociaux

    **Process:**
    1. Vérifier ownership du lien
    2. Récupérer info produit
    3. Générer caption optimisée (ou utiliser custom)
    4. Publier sur plateformes sélectionnées
    5. Sauvegarder publications

    **Plateformes supportées:**
    - instagram
    - tiktok
    - facebook
    """
    user_id = current_user.get("id")

    try:
        # Vérifier ownership
        link_result = supabase.table('affiliate_links').select(
            '*',
            'products(id, name, description, images)'
        ).eq('id', link_id).eq('influencer_id', user_id).execute()

        if not link_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lien non trouvé"
            )

        link = link_result.data[0]
        product = link['products']
        short_code = link['short_code']
        affiliate_url = f"https://shareyoursales.ma/r/{short_code}"

        # Médias (images produit par défaut)
        if not publish_data.media_urls:
            product_images = product.get('images', [])
            default_image = product_images[0] if product_images else "https://via.placeholder.com/800x600"

            media_urls = {
                "default": default_image,
                "instagram": default_image,
                "facebook": default_image,
                "tiktok": default_image  # Vidéo requise normalement
            }
        else:
            media_urls = publish_data.media_urls

        # Publier sur toutes les plateformes
        result = await auto_publisher.publish_to_all_platforms(
            user_id=user_id,
            product_id=product['id'],
            affiliate_link=affiliate_url,
            media_urls=media_urls,
            platforms=publish_data.platforms
        )

        logger.info("link_published_to_social",
                   user_id=user_id,
                   link_id=link_id,
                   platforms=publish_data.platforms,
                   published=len(result.get('published', [])),
                   failed=len(result.get('failed', [])))

        return {
            "success": result.get('success', False),
            "message": f"Publication effectuée sur {len(result.get('published', []))} plateformes",
            "published": result.get('published', []),
            "failed": result.get('failed', [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("publish_link_to_social_failed", link_id=link_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la publication"
        )


@router.get("/publications", response_model=dict)
async def get_my_publications(
    page: int = 1,
    limit: int = 20,
    platform: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Historique de mes publications sur réseaux sociaux

    **Filtres:**
    - platform: Filtrer par plateforme
    """
    user_id = current_user.get("id")

    try:
        offset = (page - 1) * limit

        query = supabase.table('social_media_publications').select(
            '*',
            'products(name, images)'
        ).eq('user_id', user_id)

        if platform:
            query = query.eq('platform', platform)

        query = query.order('published_at', desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        return {
            "success": True,
            "publications": result.data or [],
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_my_publications_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des publications"
        )


@router.delete("/link/{link_id}", response_model=dict)
async def deactivate_affiliate_link(
    link_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Désactiver un lien d'affiliation

    Le lien ne sera plus trackable
    """
    user_id = current_user.get("id")

    try:
        # Vérifier ownership
        link_result = supabase.table('affiliate_links').select('id').eq('id', link_id).eq('influencer_id', user_id).execute()

        if not link_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lien non trouvé"
            )

        # Désactiver
        supabase.table('affiliate_links').update({
            'is_active': False,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', link_id).execute()

        logger.info("affiliate_link_deactivated", user_id=user_id, link_id=link_id)

        return {
            "success": True,
            "message": "Lien désactivé avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("deactivate_affiliate_link_failed", link_id=link_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la désactivation du lien"
        )
