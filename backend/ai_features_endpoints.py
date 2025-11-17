"""
Endpoints des Fonctionnalités IA
Smart Product Matching + Content Templates + Live Shopping
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import os
from utils.logger import logger
from supabase_client import supabase

router = APIRouter(prefix="/api/ai", tags=["AI Features"])

# Configuration OpenAI (optionnel)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ============================================
# MODELS
# ============================================

class ProductRecommendation(BaseModel):
    product_id: str
    product_name: str
    merchant_name: str
    price: float
    category: str
    match_score: int
    match_reasons: List[str]
    estimated_commission: float

class ContentGenerationRequest(BaseModel):
    product_id: str
    platform: str  # instagram, tiktok, facebook
    content_type: str  # post, story, reel, caption
    language: str = "fr"
    tone: Optional[str] = "professional"

class ContentTemplate(BaseModel):
    id: str
    platform: str
    content_type: str
    title: Optional[str]
    content: str
    hashtags: List[str]
    call_to_action: str
    best_post_time: Optional[str]
    best_post_day: Optional[str]

class LiveSessionCreate(BaseModel):
    title: str
    description: Optional[str]
    platform: str
    scheduled_at: datetime
    featured_products: List[str]

# ============================================
# SMART PRODUCT MATCHING
# ============================================

@router.post("/product-recommendations/{influencer_id}")
async def generate_product_recommendations(influencer_id: str, force_refresh: bool = False):
    """
    Générer les recommandations de produits IA pour un influenceur
    """
    try:
        supabase = get_supabase_client()

        # Vérifier si recommandations déjà générées récemment
        if not force_refresh:
            existing = supabase.table('product_recommendations').select('*')\
                .eq('influencer_id', influencer_id)\
                .gte('expires_at', datetime.utcnow().isoformat())\
                .execute()

            if existing.data and len(existing.data) > 0:
                logger.info(f"Recommandations existantes pour {influencer_id}")
                return await get_product_recommendations(influencer_id)

        # Appeler fonction SQL pour générer recommandations
        supabase.rpc('generate_product_recommendations', {'p_influencer_id': influencer_id}).execute()

        logger.info(f"✅ Recommandations générées pour {influencer_id}")

        # Retourner les recommandations
        return await get_product_recommendations(influencer_id)

    except Exception as e:
        logger.error(f"Erreur génération recommandations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-recommendations/{influencer_id}")
async def get_product_recommendations(influencer_id: str, limit: int = 10):
    """
    Récupérer les top recommandations de produits
    """
    try:
        supabase = get_supabase_client()

        # Récupérer top recommandations
        recommendations = supabase.table('product_recommendations').select('''
            *,
            products:product_id(
                name,
                price,
                category,
                image_url,
                commission_rate,
                users:merchant_id(username)
            )
        ''').eq('influencer_id', influencer_id)\
            .eq('is_active', True)\
            .gte('expires_at', datetime.utcnow().isoformat())\
            .order('match_score', desc=True)\
            .limit(limit)\
            .execute()

        results = []
        for rec in recommendations.data:
            product = rec.get('products', {})
            merchant = product.get('users', {})

            # Calculer commission estimée
            estimated_commission = float(product.get('price', 0)) * float(product.get('commission_rate', 0)) / 100

            results.append({
                "product_id": rec['product_id'],
                "product_name": product.get('name', 'N/A'),
                "merchant_name": merchant.get('username', 'N/A'),
                "price": float(product.get('price', 0)),
                "category": product.get('category', 'N/A'),
                "image_url": product.get('image_url'),
                "match_score": rec['match_score'],
                "match_reasons": rec.get('match_reasons', []),
                "estimated_commission": estimated_commission,
                "commission_rate": float(product.get('commission_rate', 0)),
                "expires_at": rec['expires_at']
            })

        return {
            "recommendations": results,
            "total": len(results),
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur récupération recommandations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/product-recommendations/{recommendation_id}/click")
async def track_recommendation_click(recommendation_id: str):
    """
    Tracker un clic sur une recommandation
    """
    try:
        supabase = get_supabase_client()

        supabase.table('product_recommendations').update({
            'clicked': True,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', recommendation_id).execute()

        return {"success": True, "message": "Clic enregistré"}

    except Exception as e:
        logger.error(f"Erreur tracking clic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI CONTENT TEMPLATES
# ============================================

@router.post("/generate-content")
async def generate_content_template(request: ContentGenerationRequest, influencer_id: str):
    """
    Générer un template de contenu avec IA
    """
    try:
        supabase = get_supabase_client()

        # Récupérer info produit
        product = supabase.table('products').select('*').eq('id', request.product_id).execute()

        if not product.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        product_data = product.data[0]

        # Générer contenu selon plateforme et type
        content = await _generate_content_with_ai(
            product_data,
            request.platform,
            request.content_type,
            request.language,
            request.tone
        )

        # Sauvegarder le template
        template_data = {
            'user_id': influencer_id,
            'product_id': request.product_id,
            'platform': request.platform,
            'content_type': request.content_type,
            'title': content.get('title'),
            'content': content.get('content'),
            'hashtags': content.get('hashtags', []),
            'call_to_action': content.get('cta'),
            'language': request.language,
            'tone': request.tone,
            'best_post_time': content.get('best_time'),
            'best_post_day': content.get('best_day'),
            'generated_by': 'gpt-4' if OPENAI_API_KEY else 'template'
        }

        result = supabase.table('ai_content_templates').insert(template_data).execute()

        logger.info(f"✅ Contenu généré pour {influencer_id} - {request.platform}")

        return {
            "template_id": result.data[0]['id'],
            "content": content,
            "message": "Contenu généré avec succès"
        }

    except Exception as e:
        logger.error(f"Erreur génération contenu: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_content_with_ai(product: dict, platform: str, content_type: str, language: str, tone: str) -> dict:
    """
    Générer contenu avec IA (OpenAI ou fallback template)
    """

    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY

            prompt = f"""
Génère un {content_type} {platform} pour promouvoir ce produit:

Produit: {product['name']}
Description: {product.get('description', 'N/A')}
Prix: {product['price']} MAD
Catégorie: {product.get('category', 'N/A')}

Langue: {language}
Ton: {tone}

Format demandé:
- Titre accrocheur (optionnel pour story)
- Contenu principal (2-3 phrases émotionnelles)
- 5 hashtags pertinents
- Call-to-action fort
- Meilleur moment de publication

Réponds en JSON avec: title, content, hashtags (array), cta, best_time, best_day
"""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.warning(f"Erreur OpenAI, utilisation template fallback: {e}")

    # Fallback: Template pré-défini
    templates = {
        'instagram_post': {
            'title': f"Découvrez {product['name']}! 🔥",
            'content': f"J'ai découvert {product['name']} et c'est incroyable! 😍\n\nPrix: {product['price']} MAD\n\nLien en bio 👆",
            'hashtags': ['#maroc', '#shopping', '#promo', f"#{product.get('category', 'produit')}", '#getyourshare'],
            'cta': "Clique sur le lien en bio pour profiter de l'offre!",
            'best_time': '18:00',
            'best_day': 'Mercredi'
        },
        'instagram_story': {
            'content': f"🔥 {product['name']}\n\nSwipe up pour acheter!\n\n{product['price']} MAD",
            'hashtags': [],
            'cta': "Swipe up maintenant!",
            'best_time': '20:00',
            'best_day': 'Vendredi'
        },
        'tiktok_reel': {
            'title': f"POV: Tu découvres {product['name']}",
            'content': f"[Montrer le produit]\n\nProduit: {product['name']}\nPrix: {product['price']} MAD\n\n#tiktokmademebuyit",
            'hashtags': ['#tiktokmademebuyit', '#maroc', '#shopping', '#viral', '#fyp'],
            'cta': "Lien dans ma bio!",
            'best_time': '21:00',
            'best_day': 'Dimanche'
        }
    }

    key = f"{platform}_{content_type}"
    return templates.get(key, templates['instagram_post'])


@router.get("/content-templates/{influencer_id}")
async def get_content_templates(influencer_id: str, limit: int = 20):
    """
    Récupérer les templates de contenu générés
    """
    try:
        supabase = get_supabase_client()

        templates = supabase.table('ai_content_templates').select('*')\
            .eq('user_id', influencer_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        return {
            "templates": templates.data,
            "total": len(templates.data)
        }

    except Exception as e:
        logger.error(f"Erreur récupération templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content-templates/{template_id}/use")
async def mark_template_used(template_id: str):
    """
    Marquer un template comme utilisé
    """
    try:
        supabase = get_supabase_client()

        supabase.table('ai_content_templates').update({
            'used': True
        }).eq('id', template_id).execute()

        return {"success": True, "message": "Template marqué comme utilisé"}

    except Exception as e:
        logger.error(f"Erreur update template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# LIVE SHOPPING
# ============================================

@router.post("/live-shopping/create")
async def create_live_session(session: LiveSessionCreate, host_id: str):
    """
    Créer une session de live shopping
    """
    try:
        supabase = get_supabase_client()

        session_data = {
            'host_id': host_id,
            'title': session.title,
            'description': session.description,
            'platform': session.platform,
            'scheduled_at': session.scheduled_at.isoformat(),
            'featured_products': session.featured_products,
            'status': 'scheduled',
            'commission_boost_percentage': 5.0  # Boost de 5% pendant le live
        }

        result = supabase.table('live_shopping_sessions').insert(session_data).execute()

        session_id = result.data[0]['id']

        # Ajouter les produits au live
        for product_id in session.featured_products:
            supabase.table('live_shopping_products').insert({
                'session_id': session_id,
                'product_id': product_id,
                'display_order': session.featured_products.index(product_id)
            }).execute()

        logger.info(f"✅ Live session créée: {session_id} par {host_id}")

        return {
            "session_id": session_id,
            "message": "Session live créée avec succès",
            "commission_boost": "5%",
            "scheduled_at": session.scheduled_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur création live session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/live-shopping/{session_id}/start")
async def start_live_session(session_id: str):
    """
    Démarrer une session live
    """
    try:
        supabase = get_supabase_client()

        supabase.table('live_shopping_sessions').update({
            'status': 'live',
            'started_at': datetime.utcnow().isoformat()
        }).eq('id', session_id).execute()

        logger.info(f"▶️ Live session démarrée: {session_id}")

        return {"success": True, "message": "Live démarré", "status": "live"}

    except Exception as e:
        logger.error(f"Erreur démarrage live: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/live-shopping/{session_id}/end")
async def end_live_session(session_id: str):
    """
    Terminer une session live
    """
    try:
        supabase = get_supabase_client()

        # Récupérer stats
        session = supabase.table('live_shopping_sessions').select('*').eq('id', session_id).execute()

        if not session.data:
            raise HTTPException(status_code=404, detail="Session non trouvée")

        # Calculer stats finales
        orders = supabase.table('live_shopping_orders').select('*').eq('session_id', session_id).execute()

        total_orders = len(orders.data)
        total_sales = sum(float(o['amount']) for o in orders.data)

        # Mettre à jour session
        supabase.table('live_shopping_sessions').update({
            'status': 'ended',
            'ended_at': datetime.utcnow().isoformat(),
            'total_orders': total_orders,
            'total_sales': total_sales
        }).eq('id', session_id).execute()

        logger.info(f"⏹️ Live session terminée: {session_id} - {total_orders} ventes")

        return {
            "success": True,
            "message": "Live terminé",
            "stats": {
                "total_orders": total_orders,
                "total_sales": total_sales,
                "viewers": session.data[0].get('viewers_count', 0)
            }
        }

    except Exception as e:
        logger.error(f"Erreur fin live: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live-shopping/upcoming")
async def get_upcoming_live_sessions(limit: int = 10):
    """
    Récupérer les prochaines sessions live
    """
    try:
        supabase = get_supabase_client()

        sessions = supabase.table('live_shopping_sessions').select('''
            *,
            users:host_id(username, role)
        ''').eq('status', 'scheduled')\
            .gte('scheduled_at', datetime.utcnow().isoformat())\
            .order('scheduled_at')\
            .limit(limit)\
            .execute()

        results = []
        for session in sessions.data:
            host = session.get('users', {})
            results.append({
                "session_id": session['id'],
                "title": session['title'],
                "host_username": host.get('username', 'N/A'),
                "platform": session['platform'],
                "scheduled_at": session['scheduled_at'],
                "featured_products_count": len(session.get('featured_products', [])),
                "commission_boost": f"{session['commission_boost_percentage']}%"
            })

        return {
            "upcoming_lives": results,
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"Erreur récupération lives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live-shopping/my-sessions/{host_id}")
async def get_my_live_sessions(host_id: str):
    """
    Récupérer les sessions live d'un host
    """
    try:
        supabase = get_supabase_client()

        sessions = supabase.table('live_shopping_sessions').select('*')\
            .eq('host_id', host_id)\
            .order('created_at', desc=True)\
            .execute()

        return {
            "sessions": sessions.data,
            "total": len(sessions.data)
        }

    except Exception as e:
        logger.error(f"Erreur récupération mes lives: {e}")
        raise HTTPException(status_code=500, detail=str(e))
