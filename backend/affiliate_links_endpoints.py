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
import qrcode
from io import BytesIO
import base64

from auth import get_current_user
from supabase_client import supabase
from services.social_auto_publish_service import auto_publisher

router = APIRouter(prefix="/api/affiliate", tags=["Affiliate Links"])
logger = structlog.get_logger()

def generate_qr_base64(url: str) -> str:
    """Génère un QR code en base64 localement"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()


# ============================================
# PYDANTIC MODELS
# ============================================

class GenerateLinkRequest(BaseModel):
    """Générer un lien d'affiliation"""
    product_id: Optional[str] = Field(None, description="ID du produit")
    service_id: Optional[str] = Field(None, description="ID du service")
    custom_slug: Optional[str] = Field(None, max_length=50, description="Slug personnalisé (optionnel)")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "uuid-product-123",
                "service_id": None,
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

        # Récupérer liens avec info produit et service
        # Fix ambiguous FK for products: use explicit relationship
        result = supabase.table('affiliate_links').select(
            '*',
            'products:products!affiliate_links_product_id_fkey(id, name, description, image_url, merchant_id)',
            'services(id, name, description, price_per_lead, merchant_id)'
        ).eq('influencer_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        links = result.data or []
        
        if not links:
             return {
                "success": True,
                "links": [],
                "total": 0,
                "page": page,
                "limit": limit
            }

        link_ids = [link['id'] for link in links]

        # Bulk fetch conversions (counts) and commissions from conversions table
        # We use conversions table for commissions because commissions table doesn't have link_id
        # And conversions table uses tracking_link_id
        conv_result = supabase.table('conversions').select('tracking_link_id, commission_amount').in_('tracking_link_id', link_ids).execute()
        conversions_map = {}
        commissions_map = {}
        for c in (conv_result.data or []):
            lid = c.get('tracking_link_id')
            conversions_map[lid] = conversions_map.get(lid, 0) + 1
            commissions_map[lid] = commissions_map.get(lid, 0) + float(c.get('commission_amount', 0))

        # Bulk fetch clicks (tracking_events)

        # Bulk fetch clicks (tracking_events)
        # Optimization: Fetch all clicks for these links in one query instead of N+1
        # tracking_events uses tracking_link_id
        clicks_result = supabase.table('tracking_events').select('tracking_link_id').in_('tracking_link_id', link_ids).eq('event_type', 'click').execute()
        clicks_map = {}
        for c in (clicks_result.data or []):
            lid = c.get('tracking_link_id')
            clicks_map[lid] = clicks_map.get(lid, 0) + 1

        # Enrichir avec stats
        for link in links:
            link_id = link['id']

            clicks_count = clicks_map.get(link_id, 0)
            conversions_count = conversions_map.get(link_id, 0)
            total_commissions = commissions_map.get(link_id, 0.0)

            link['stats'] = {
                'clicks': clicks_count,
                'conversions': conversions_count,
                'total_commissions': float(total_commissions),
                'conversion_rate': round((conversions_count / clicks_count * 100), 2) if clicks_count > 0 else 0.0
            }

            # Générer lien complet
            link['full_url'] = f"https://shareyoursales.ma/r/{link['unique_code']}"

            # QR code URL (Local Generation)
            link['qr_code_url'] = generate_qr_base64(link['full_url'])
            
            # Add short_code for frontend compatibility
            link['short_code'] = link['unique_code']
            
            # Normaliser l'objet pour le frontend (product ou service)
            if link.get('products'):
                link['item_type'] = 'product'
                link['item_details'] = link['products']
                # Polyfill images for frontend
                if 'image_url' in link['products']:
                     link['item_details']['images'] = [link['products']['image_url']]
            elif link.get('services'):
                link['item_type'] = 'service'
                # Mapper les champs service vers un format commun si besoin
                s = link['services']
                link['item_details'] = {
                    'id': s['id'],
                    'name': s.get('name', 'Service'),
                    'description': s['description'],
                    'price': s.get('price_per_lead', 0),
                    'merchant_id': s['merchant_id'],
                    'images': [] # Services n'ont pas d'images par défaut dans ce select
                }

        return {
            "success": True,
            "links": links,
            "total": len(links),
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_my_affiliate_links_failed", user_id=user_id, error=str(e))
        print(f"CRITICAL ERROR in get_my_affiliate_links: {e}") # Added print for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des liens: {str(e)}"
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
    service_id = request_data.service_id

    if not product_id and not service_id:
        raise HTTPException(status_code=400, detail="Product ID or Service ID required")

    try:
        # Vérifier que l'utilisateur est approuvé pour ce produit ou service
        query = supabase.table('affiliation_requests').select('*').eq('influencer_id', user_id).eq('status', 'active')
        
        if product_id:
            query = query.eq('product_id', product_id)
        else:
            query = query.eq('service_id', service_id)
            
        affiliate_result = query.execute()

        if not affiliate_result.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous devez être approuvé comme affilié pour cet élément"
            )

        affiliate_request = affiliate_result.data[0]
        # merchant_id = affiliate_request['merchant_id']
        # commission_rate = affiliate_request.get('commission_rate', 5.0)

        # Vérifier si lien déjà existe
        check_query = supabase.table('affiliate_links').select('*').eq('influencer_id', user_id)
        if product_id:
            check_query = check_query.eq('product_id', product_id)
        else:
            check_query = check_query.eq('service_id', service_id)
            
        existing_link = check_query.execute()

        if existing_link.data:
            # Retourner lien existant
            link = existing_link.data[0]
            # Map unique_code to short_code
            code = link.get('unique_code')
            full_url = f"https://shareyoursales.ma/r/{code}"
            return {
                "success": True,
                "message": "Lien existant retourné",
                "link": {
                    **link,
                    "short_code": code,
                    "full_url": full_url,
                    "qr_code_url": generate_qr_base64(full_url)
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
            'service_id': service_id,
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

        logger.info("affiliate_link_generated", user_id=user_id, product_id=product_id, service_id=service_id, short_code=short_code)
        
        full_url = f"https://shareyoursales.ma/r/{short_code}"

        return {
            "success": True,
            "message": "Lien d'affiliation créé avec succès",
            "link": {
                **link,
                "full_url": full_url,
                "qr_code_url": generate_qr_base64(full_url),
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
        logger.error("generate_affiliate_link_failed", user_id=user_id, error=str(e))
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
        clicks_result = supabase.table('tracking_events').select('id', count='exact', head=True).eq('tracking_link_id', link_id).eq('event_type', 'click').execute()
        stats['clicks'] = clicks_result.count or 0

        # Conversions & Commissions (from conversions table)
        conversions_result = supabase.table('conversions').select('commission_amount, status').eq('tracking_link_id', link_id).execute()
        conversions_data = conversions_result.data or []
        
        stats['conversions'] = len(conversions_data)

        # Calculate commissions from conversions
        stats['total_commissions'] = sum(float(c.get('commission_amount', 0)) for c in conversions_data)
        stats['pending_commissions'] = sum(float(c.get('commission_amount', 0)) for c in conversions_data if c.get('status') == 'pending')
        stats['paid_commissions'] = sum(float(c.get('commission_amount', 0)) for c in conversions_data if c.get('status') == 'paid')

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
            'products(id, name, description, images)',
            'services(id, title, description)'
        ).eq('id', link_id).eq('influencer_id', user_id).execute()

        if not link_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lien non trouvé"
            )

        link = link_result.data[0]
        product = link.get('products')
        service = link.get('services')
        short_code = link['unique_code'] # Changed from short_code to unique_code as per DB schema
        affiliate_url = f"https://shareyoursales.ma/r/{short_code}"
        
        product_id = None
        service_id = None
        item_images = []
        
        if product:
            product_id = product['id']
            item_images = product.get('images', [])
        elif service:
            service_id = service['id']
            item_images = [] # Services might not have images yet
        else:
             raise HTTPException(status_code=404, detail="Produit ou Service introuvable pour ce lien")

        # Médias (images produit par défaut)
        if not publish_data.media_urls:
            default_image = item_images[0] if item_images else "https://via.placeholder.com/800x600"

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
            product_id=product_id,
            service_id=service_id,
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
            'products(name, images)',
            'services(title)'
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
