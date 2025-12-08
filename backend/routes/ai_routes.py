"""
Routes IA (Intelligence Artificielle)
Recommendations + Chatbot
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from auth import get_current_user_from_cookie
from db_helpers import supabase
from services.ai_recommendations_service import AIRecommendationsService

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI"])

# Initialize AI service
ai_recommendations = AIRecommendationsService(supabase)


# ============================================
# MODELS
# ============================================

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None


# ============================================
# RECOMMENDATIONS
# ============================================

@router.get("/recommendations/for-you")
async def get_personalized_recommendations(
    limit: int = 20,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Recommandations personnalisées complètes

    Sections:
    - Based on your purchases
    - Trending now
    - You might like
    - Similar products
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        recommendations = ai_recommendations.get_personalized_for_you(user_id, limit)

        return recommendations

    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/collaborative")
async def get_collaborative_recommendations(
    limit: int = 10,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Recommandations basées sur utilisateurs similaires

    Algorithme de filtrage collaboratif
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        recommendations = ai_recommendations.get_collaborative_recommendations(user_id, limit)

        return {
            "success": True,
            "algorithm": "collaborative_filtering",
            "recommendations": recommendations,
            "total": len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error getting collaborative recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/content-based")
async def get_content_based_recommendations(
    limit: int = 10,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Recommandations basées sur attributs des produits

    Algorithme de filtrage par contenu
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        recommendations = ai_recommendations.get_content_based_recommendations(user_id, limit)

        return {
            "success": True,
            "algorithm": "content_based_filtering",
            "recommendations": recommendations,
            "total": len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error getting content-based recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/hybrid")
async def get_hybrid_recommendations(
    limit: int = 10,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Recommandations hybrides (collaborative + content-based)

    Combine les deux algorithmes pour de meilleurs résultats
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        recommendations = ai_recommendations.get_hybrid_recommendations(user_id, limit)

        return {
            "success": True,
            "algorithm": "hybrid",
            "recommendations": recommendations,
            "total": len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error getting hybrid recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/trending")
async def get_trending_recommendations(
    limit: int = 10
):
    """
    Produits en tendance (derniers 7 jours)
    """
    try:
        recommendations = ai_recommendations.get_trending_products(limit)

        return {
            "success": True,
            "period": "7d",
            "recommendations": recommendations,
            "total": len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = 5
):
    """
    Produits similaires à un produit donné
    """
    try:
        similar = ai_recommendations.get_similar_products(product_id, limit)

        return {
            "success": True,
            "product_id": product_id,
            "similar_products": similar,
            "total": len(similar)
        }

    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CHATBOT
# ============================================

@router.post("/chatbot")
async def chat_with_bot(
    msg: ChatMessage,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Chatbot IA conversationnel

    NOTE: Intégrer avec OpenAI GPT-4 pour production
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Simuler une réponse (à remplacer par OpenAI GPT-4)
        user_message = msg.message.lower()

        # Patterns de réponse
        if "bonjour" in user_message or "salut" in user_message or "hello" in user_message:
            response = "Bonjour ! 👋 Comment puis-je vous aider aujourd'hui ?"

        elif "produit" in user_message or "product" in user_message:
            response = "Je peux vous aider à trouver des produits ! Quel type de produit recherchez-vous ?"

        elif "vente" in user_message or "sale" in user_message:
            response = "Pour suivre vos ventes, consultez votre tableau de bord Analytics. Vous y trouverez toutes vos statistiques détaillées !"

        elif "commission" in user_message:
            response = "Les commissions sont calculées automatiquement. Consultez la section Commissions pour voir vos gains !"

        elif "aide" in user_message or "help" in user_message:
            response = """Je peux vous aider avec :

📊 Analytics et statistiques
🛍️ Gestion de produits
💰 Commissions et paiements
📱 Réseaux sociaux
👥 Gestion d'équipe

Que souhaitez-vous savoir ?"""

        elif "merci" in user_message or "thank" in user_message:
            response = "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. 😊"

        else:
            response = "Je suis là pour vous aider ! Posez-moi vos questions sur les produits, ventes, commissions, ou l'utilisation de la plateforme."

        # Sauvegarder l'historique
        chat_entry = {
            'user_id': user_id,
            'user_message': msg.message,
            'bot_response': response,
            'context': msg.context,
            'created_at': datetime.now().isoformat()
        }

        try:
            supabase.table('chatbot_history').insert(chat_entry).execute()
        except:
            pass  # Table might not exist

        return {
            "success": True,
            "response": response,
            "note": "Intégrer OpenAI GPT-4 pour conversations avancées"
        }

    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbot/history")
async def get_chatbot_history(
    limit: int = 50,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Historique des conversations avec le chatbot
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        history = supabase.table('chatbot_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()

        return {
            "success": True,
            "history": history.data or [],
            "total": len(history.data) if history.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting chatbot history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI INSIGHTS
# ============================================

@router.get("/insights")
async def get_ai_insights(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Insights IA sur les performances

    Analyse automatique et suggestions d'amélioration
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        insights = []

        # Analyser les ventes
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=30)).isoformat()

        if role == "influencer":
            conversions = supabase.table('conversions').select('*').eq('influencer_id', user_id).gte('created_at', start_date).execute()
        else:
            conversions = supabase.table('conversions').select('*').eq('merchant_id', user_id).gte('created_at', start_date).execute()

        total_sales = len(conversions.data or [])

        # Insight sur les ventes
        if total_sales == 0:
            insights.append({
                "type": "warning",
                "category": "sales",
                "message": "Aucune vente ce mois. Essayez de publier plus de contenu sur les réseaux sociaux !",
                "action": "Créer un post",
                "priority": "high"
            })
        elif total_sales < 10:
            insights.append({
                "type": "tip",
                "category": "sales",
                "message": f"Vous avez {total_sales} ventes ce mois. Pour augmenter, essayez nos templates de contenu viral !",
                "action": "Voir templates",
                "priority": "medium"
            })
        else:
            insights.append({
                "type": "success",
                "category": "sales",
                "message": f"Excellent ! {total_sales} ventes ce mois. Continuez comme ça !",
                "action": None,
                "priority": "low"
            })

        # Insight sur les réseaux sociaux
        social_connections = supabase.table('social_media_connections').select('*', count='exact').eq('user_id', user_id).eq('status', 'connected').execute()
        social_count = social_connections.count if hasattr(social_connections, 'count') else 0

        if social_count < 2:
            insights.append({
                "type": "tip",
                "category": "social_media",
                "message": "Connectez plus de réseaux sociaux pour augmenter votre portée !",
                "action": "Connecter comptes",
                "priority": "high"
            })

        # Insight sur l'équipe
        if role == "merchant":
            team_members = supabase.table('team_members').select('*', count='exact').eq('team_owner_id', user_id).execute()
            team_count = team_members.count if hasattr(team_members, 'count') else 0

            if team_count == 0:
                insights.append({
                    "type": "tip",
                    "category": "team",
                    "message": "Invitez des membres à votre équipe pour collaborer efficacement !",
                    "action": "Inviter membre",
                    "priority": "medium"
                })

        return {
            "success": True,
            "insights": insights,
            "total": len(insights)
        }

    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime
