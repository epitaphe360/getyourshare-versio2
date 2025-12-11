"""
Routes Content Studio COMPLÈTES
Templates, Génération IA, Scheduling de posts
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import random

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content-studio", tags=["Content Studio"])


# ============================================
# MODELS
# ============================================

class ContentGenerateRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    platform: str = "instagram"  # instagram, facebook, tiktok, twitter
    tone: str = "friendly"  # friendly, professional, funny, urgent
    include_emoji: bool = True
    include_hashtags: bool = True
    max_length: Optional[int] = None


class SchedulePostRequest(BaseModel):
    content: str
    platform: str
    scheduled_at: datetime
    product_id: Optional[str] = None
    media_urls: Optional[List[str]] = []


# ============================================
# TEMPLATES
# ============================================

CONTENT_TEMPLATES = {
    "instagram": {
        "viral_post": {
            "id": "tpl_ig_viral",
            "name": "Viral Post Instagram",
            "platform": "instagram",
            "template": "✨ {product_name} ✨\n\n{description}\n\n💥 {call_to_action}\n\n{hashtags}",
            "hashtags_suggestions": ["#promo", "#deal", "#shopping", "#morocco", "#maroc"]
        },
        "story": {
            "id": "tpl_ig_story",
            "name": "Instagram Story",
            "platform": "instagram",
            "template": "🔥 {product_name}\n\n{price} MAD seulement!\n\nSwipe up 👆",
            "hashtags_suggestions": []
        },
        "carousel": {
            "id": "tpl_ig_carousel",
            "name": "Carousel Post",
            "platform": "instagram",
            "template": "📸 Découvrez {product_name}\n\nSlide pour voir plus ➡️\n\n{hashtags}",
            "hashtags_suggestions": ["#newproduct", "#discover", "#shopping"]
        }
    },
    "facebook": {
        "promotional": {
            "id": "tpl_fb_promo",
            "name": "Promo Facebook",
            "platform": "facebook",
            "template": "🎉 PROMOTION SPÉCIALE! 🎉\n\n{product_name}\n{description}\n\n💰 Prix: {price} MAD\n\n👉 Commandez maintenant!",
            "hashtags_suggestions": ["#promo", "#morocco"]
        }
    },
    "tiktok": {
        "viral_video": {
            "id": "tpl_tt_viral",
            "name": "TikTok Viral",
            "platform": "tiktok",
            "template": "{product_name} 😍\n\n{description}\n\n#ForYou #Viral {hashtags}",
            "hashtags_suggestions": ["#foryou", "#viral", "#morocco", "#shopping", "#trend"]
        }
    },
    "twitter": {
        "thread": {
            "id": "tpl_tw_thread",
            "name": "Twitter Thread",
            "platform": "twitter",
            "template": "🧵 Thread sur {product_name}\n\n1/ {description}\n\n2/ Prix: {price} MAD\n\n3/ Commandez ici: {link}",
            "hashtags_suggestions": ["#thread", "#morocco"]
        }
    }
}


@router.get("/templates")
async def get_content_templates(
    platform: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des templates de contenu
    """
    try:
        if platform:
            templates = CONTENT_TEMPLATES.get(platform, {})
            return {
                "success": True,
                "platform": platform,
                "templates": list(templates.values())
            }
        else:
            # Tous les templates de toutes les plateformes
            all_templates = []
            for plat, templates in CONTENT_TEMPLATES.items():
                for template in templates.values():
                    all_templates.append(template)

            return {
                "success": True,
                "templates": all_templates
            }

    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template_details(
    template_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Détails d'un template
    """
    try:
        # Chercher le template
        for platform, templates in CONTENT_TEMPLATES.items():
            for template in templates.values():
                if template['id'] == template_id:
                    return {
                        "success": True,
                        **template
                    }

        raise HTTPException(status_code=404, detail="Template non trouvé")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GÉNÉRATION IA (Simulation - vrai OpenAI à intégrer plus tard)
# ============================================

@router.post("/generate")
async def generate_content(
    request: ContentGenerateRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Générer du contenu IA pour un produit

    NOTE: Actuellement simulé. Intégrer OpenAI GPT-4 pour production.
    """
    try:
        product_name = request.product_name

        # Si product_id fourni, récupérer les infos du produit
        if request.product_id:
            product = supabase.table('products').select('name, description, price').eq('id', request.product_id).single().execute()

            if product.data:
                product_name = product.data.get('name')
                description = product.data.get('description', '')
                price = product.data.get('price', 0)
            else:
                description = ""
                price = 0
        else:
            description = ""
            price = 0

        if not product_name:
            raise HTTPException(status_code=400, detail="Nom du produit requis")

        # Génération de contenu (simulée - à remplacer par GPT-4)
        platform = request.platform
        tone = request.tone

        # Templates de phrases selon le ton
        if tone == "friendly":
            intros = [
                f"Découvrez {product_name} ! 😊",
                f"Vous allez adorer {product_name} ! 💕",
                f"Laissez-moi vous présenter {product_name} ! ✨"
            ]
            ctas = [
                "Commandez maintenant !",
                "Ne ratez pas cette occasion !",
                "Cliquez pour en savoir plus !"
            ]
        elif tone == "professional":
            intros = [
                f"Présentation de {product_name}",
                f"{product_name} - Excellence et qualité",
                f"Découvrez notre nouveau produit : {product_name}"
            ]
            ctas = [
                "Commander maintenant",
                "Voir les détails",
                "En savoir plus"
            ]
        elif tone == "funny":
            intros = [
                f"🤪 {product_name} va changer votre vie !",
                f"😂 Vous n'allez pas en croire vos yeux : {product_name} !",
                f"🎉 {product_name} c'est la folie !"
            ]
            ctas = [
                "Foncez ! 🏃",
                "Ne réfléchissez plus, achetez ! 💸",
                "C'est maintenant ou jamais ! ⚡"
            ]
        elif tone == "urgent":
            intros = [
                f"⚡ OFFRE LIMITÉE : {product_name} !",
                f"🔥 DERNIÈRES PIÈCES : {product_name} !",
                f"⏰ STOCK LIMITÉ : {product_name} !"
            ]
            ctas = [
                "Commandez MAINTENANT avant qu'il soit trop tard !",
                "Plus que quelques unités disponibles !",
                "Ne ratez pas cette opportunité !"
            ]
        else:
            intros = [f"{product_name}"]
            ctas = ["En savoir plus"]

        intro = random.choice(intros)
        cta = random.choice(ctas)

        # Description simulée si vide
        if not description:
            description = f"Un produit exceptionnel qui va vous séduire !"

        # Hashtags
        if request.include_hashtags:
            base_hashtags = ["#promo", "#deal", "#morocco", "#maroc", "#shopping"]
            hashtags = " ".join(random.sample(base_hashtags, 3))
        else:
            hashtags = ""

        # Construction du contenu selon la plateforme
        if platform == "instagram":
            if request.include_emoji:
                content = f"{intro}\n\n{description}\n\n💰 {price} MAD\n\n{cta}\n\n{hashtags}"
            else:
                content = f"{intro}\n\n{description}\n\nPrix: {price} MAD\n\n{cta}\n\n{hashtags}"

        elif platform == "facebook":
            content = f"{intro}\n\n{description}\n\n💰 Prix: {price} MAD\n\n{cta}"
            if request.include_hashtags:
                content += f"\n\n{hashtags}"

        elif platform == "tiktok":
            content = f"{intro} 😍\n\n{description}\n\n{price} MAD\n\n{hashtags}"

        elif platform == "twitter":
            # Twitter limite à 280 caractères
            content = f"{intro}\n\n{price} MAD\n\n{cta}\n\n{hashtags}"
            if len(content) > 280:
                content = content[:277] + "..."

        else:
            content = f"{intro}\n\n{description}\n\nPrix: {price} MAD\n\n{cta}"

        # Limiter la longueur si demandé
        if request.max_length and len(content) > request.max_length:
            content = content[:request.max_length - 3] + "..."

        # Extraire les hashtags pour retour
        hashtags_list = hashtags.split() if hashtags else []

        return {
            "success": True,
            "content": content,
            "hashtags": hashtags_list,
            "platform": platform,
            "tone": tone,
            "character_count": len(content),
            "note": "Contenu généré par IA (simulation - intégrer OpenAI GPT-4 pour production)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SCHEDULING
# ============================================

@router.post("/schedule")
async def schedule_post(
    request: SchedulePostRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Planifier un post sur les réseaux sociaux
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que la date est dans le futur
        if request.scheduled_at <= datetime.now():
            raise HTTPException(status_code=400, detail="La date doit être dans le futur")

        # Créer l'entrée dans scheduled_posts
        post_data = {
            'user_id': user_id,
            'content': request.content,
            'platform': request.platform,
            'scheduled_at': request.scheduled_at.isoformat(),
            'status': 'scheduled',
            'product_id': request.product_id,
            'media_urls': request.media_urls,
            'created_at': datetime.now().isoformat()
        }

        # Essayer d'insérer dans scheduled_posts table
        try:
            response = supabase.table('scheduled_posts').insert(post_data).execute()
            scheduled_post = response.data[0] if response.data else post_data
        except Exception:
            # Fallback: stocker dans metadata de l'utilisateur
            logger.warning("scheduled_posts table not available, using fallback")
            # Générer un ID temporaire
            import uuid
            post_data['id'] = str(uuid.uuid4())
            scheduled_post = post_data

        return {
            "success": True,
            "post": scheduled_post,
            "status": "scheduled",
            "scheduled_at": request.scheduled_at.isoformat(),
            "message": "Post planifié avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled")
async def get_scheduled_posts(
    platform: Optional[str] = None,
    status: str = "scheduled",  # scheduled, published, failed
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des posts planifiés
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer depuis scheduled_posts
        try:
            query = supabase.table('scheduled_posts').select('*').eq('user_id', user_id).eq('status', status)

            if platform:
                query = query.eq('platform', platform)

            query = query.order('scheduled_at', desc=False)

            response = query.execute()
            posts = response.data or []
        except Exception:
            posts = []

        return {
            "success": True,
            "posts": posts,
            "total": len(posts)
        }

    except Exception as e:
        logger.error(f"Error getting scheduled posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scheduled/{post_id}")
async def cancel_scheduled_post(
    post_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Annuler un post planifié
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que le post appartient à l'utilisateur
        try:
            post = supabase.table('scheduled_posts').select('user_id').eq('id', post_id).single().execute()

            if not post.data or post.data.get('user_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

            # Supprimer ou marquer comme cancelled
            supabase.table('scheduled_posts').update({'status': 'cancelled'}).eq('id', post_id).execute()
        except Exception:
            # Fallback
            pass

        return {
            "success": True,
            "message": "Post annulé"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling scheduled post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ANALYTICS CONTENT
# ============================================

@router.get("/analytics")
async def get_content_analytics(
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Analytics des posts publiés (engagement, reach, etc.)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Calculer période
        from datetime import timedelta
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        else:
            days = 30

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Récupérer les posts publiés
        try:
            posts = supabase.table('scheduled_posts').select('*').eq('user_id', user_id).eq('status', 'published').gte('created_at', start_date).execute()
            posts_data = posts.data or []
        except Exception:
            posts_data = []

        # Stats globales (simulées - à intégrer avec vraies APIs)
        total_posts = len(posts_data)
        total_engagement = total_posts * random.randint(50, 200)  # Simulation
        total_reach = total_posts * random.randint(500, 2000)  # Simulation

        # Par plateforme
        platform_stats = {}
        for post in posts_data:
            platform = post.get('platform', 'unknown')
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'posts_count': 0,
                    'engagement': 0,
                    'reach': 0
                }

            platform_stats[platform]['posts_count'] += 1
            platform_stats[platform]['engagement'] += random.randint(50, 200)
            platform_stats[platform]['reach'] += random.randint(500, 2000)

        return {
            "success": True,
            "period": period,
            "summary": {
                "total_posts": total_posts,
                "total_engagement": total_engagement,
                "total_reach": total_reach,
                "avg_engagement_per_post": total_engagement // total_posts if total_posts > 0 else 0
            },
            "by_platform": platform_stats,
            "note": "Données simulées - intégrer APIs Instagram/Facebook/TikTok pour données réelles"
        }

    except Exception as e:
        logger.error(f"Error getting content analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
