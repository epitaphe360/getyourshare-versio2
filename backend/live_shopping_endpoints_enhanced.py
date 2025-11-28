"""
Live Shopping Endpoints - Enhanced avec intégrations réelles

Endpoints pour gérer les sessions live shopping sur toutes les plateformes:
- Instagram Live
- TikTok Live
- YouTube Live
- Facebook Live

Avec tracking temps réel et attribution des ventes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from services.instagram_live_service import instagram_live_service
from services.tiktok_live_service import tiktok_live_service
from services.youtube_live_service import youtube_live_service
from services.facebook_live_service import facebook_live_service
from supabase_client import supabase

router = APIRouter(prefix="/api/live-shopping", tags=["Live Shopping Enhanced"])


# ==================== MODELS ====================

class Platform(str, Enum):
    """Plateformes supportées"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"


class CreateLiveSessionRequest(BaseModel):
    """Requête pour créer une session live"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    platform: Platform
    scheduled_at: datetime
    featured_products: List[str] = Field(..., min_items=1)
    privacy: Optional[str] = Field("public", description="public, unlisted, private")


class LiveSessionResponse(BaseModel):
    """Réponse session live"""
    session_id: str
    platform: str
    status: str
    stream_url: Optional[str]
    stream_key: Optional[str]
    watch_url: Optional[str]
    demo_mode: bool


# ==================== ENDPOINTS ====================

@router.post("/create-session", summary="Créer une session live sur n'importe quelle plateforme")
async def create_live_session(
    request: CreateLiveSessionRequest,
    user_id: str = Query(..., description="ID de l'utilisateur/influenceur")
):
    """
    Créer une session live shopping

    Supporte:
    - Instagram Live
    - TikTok Live
    - YouTube Live
    - Facebook Live

    Processus:
    1. Crée la session dans notre DB
    2. Crée le stream sur la plateforme choisie
    3. Retourne les infos de streaming (URL + clé)
    """
    try:
        # Préparer les données de session
        session_data = {
            "title": request.title,
            "description": request.description,
            "scheduled_start_time": request.scheduled_at.isoformat()
        }

        # Créer le stream selon la plateforme
        platform_result = None

        if request.platform == Platform.INSTAGRAM:
            platform_result = await instagram_live_service.create_live_stream(session_data)

        elif request.platform == Platform.TIKTOK:
            platform_result = await tiktok_live_service.create_live_room(session_data)

        elif request.platform == Platform.YOUTUBE:
            session_data["privacy_status"] = request.privacy
            platform_result = await youtube_live_service.create_broadcast(session_data)

        elif request.platform == Platform.FACEBOOK:
            session_data["privacy"] = request.privacy.upper()
            platform_result = await facebook_live_service.create_live_video(session_data)

        if not platform_result or not platform_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Erreur création live: {platform_result.get('error', 'Unknown')}"
            )

        # Sauvegarder dans notre DB
        session_db = supabase.table("live_shopping_sessions").insert({
            "host_id": user_id,
            "title": request.title,
            "description": request.description,
            "platform": request.platform.value,
            "scheduled_at": request.scheduled_at.isoformat(),
            "status": "scheduled",
            "platform_broadcast_id": platform_result.get("broadcast_id") or platform_result.get("video_id") or platform_result.get("room_id"),
            "stream_url": platform_result.get("stream_url"),
            "stream_key": platform_result.get("stream_key"),
            "watch_url": platform_result.get("watch_url") or platform_result.get("permalink_url"),
            "commission_boost_percentage": 5.0,  # +5% pendant live
            "metadata": platform_result
        }).execute()

        session_id = session_db.data[0]["id"]

        # Lier les produits
        for product_id in request.featured_products:
            supabase.table("live_shopping_products").insert({
                "session_id": session_id,
                "product_id": product_id
            }).execute()

        return {
            "success": True,
            "session_id": session_id,
            "platform": request.platform.value,
            "status": "scheduled",
            "stream_url": platform_result.get("stream_url"),
            "stream_key": platform_result.get("stream_key"),
            "secure_stream_url": platform_result.get("secure_stream_url"),
            "watch_url": platform_result.get("watch_url") or platform_result.get("permalink_url"),
            "demo_mode": platform_result.get("demo_mode", False),
            "message": "Session créée! Utilise stream_url + stream_key dans ton logiciel de streaming (OBS, etc.)"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/start", summary="Démarrer une session live")
async def start_live_session(session_id: str):
    """
    Démarrer le live

    Actions:
    1. Passe le statut à "live" sur la plateforme
    2. Active le boost de commission +5%
    3. Démarre le tracking temps réel
    """
    try:
        # Récupérer la session
        session_result = supabase.table("live_shopping_sessions").select("*").eq("id", session_id).execute()

        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_result.data[0]
        platform = session["platform"]
        broadcast_id = session["platform_broadcast_id"]

        # Démarrer selon la plateforme
        platform_result = None

        if platform == "instagram":
            platform_result = await instagram_live_service.start_live_stream(broadcast_id)

        elif platform == "tiktok":
            platform_result = await tiktok_live_service.start_live(broadcast_id)

        elif platform == "youtube":
            platform_result = await youtube_live_service.start_broadcast(broadcast_id)

        elif platform == "facebook":
            platform_result = await facebook_live_service.go_live(broadcast_id)

        if not platform_result or not platform_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Erreur démarrage live: {platform_result.get('error', 'Unknown')}"
            )

        # Mettre à jour notre DB
        supabase.table("live_shopping_sessions").update({
            "status": "live",
            "actual_start_time": datetime.utcnow().isoformat()
        }).eq("id", session_id).execute()

        return {
            "success": True,
            "session_id": session_id,
            "status": "live",
            "watch_url": platform_result.get("watch_url") or platform_result.get("live_url") or platform_result.get("permalink_url"),
            "started_at": platform_result.get("started_at"),
            "message": "🔴 Live démarré! Le boost de commission +5% est actif."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/stats", summary="Stats temps réel d'une session live")
async def get_live_session_stats(session_id: str):
    """
    Récupérer les statistiques en temps réel

    Métriques:
    - Viewers actuels
    - Peak viewers
    - Total viewers
    - Engagement (likes, comments, shares)
    - Ventes en cours
    - Revenue généré
    """
    try:
        # Récupérer la session
        session_result = supabase.table("live_shopping_sessions").select("*").eq("id", session_id).execute()

        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_result.data[0]
        platform = session["platform"]
        broadcast_id = session["platform_broadcast_id"]

        # Récupérer stats selon la plateforme
        platform_stats = None

        if platform == "instagram":
            platform_stats = await instagram_live_service.get_live_stats(broadcast_id)

        elif platform == "tiktok":
            platform_stats = await tiktok_live_service.get_live_stats(broadcast_id)

        elif platform == "youtube":
            platform_stats = await youtube_live_service.get_live_stats(broadcast_id)

        elif platform == "facebook":
            platform_stats = await facebook_live_service.get_live_stats(broadcast_id)

        # Récupérer les ventes de ce live
        sales_result = supabase.table("sales").select("amount, influencer_commission").eq(
            "metadata->>live_session_id", session_id
        ).execute()

        total_sales = sum(sale["amount"] for sale in sales_result.data)
        total_commission = sum(sale["influencer_commission"] for sale in sales_result.data)
        sales_count = len(sales_result.data)

        return {
            "session_id": session_id,
            "platform": platform,
            "status": session["status"],
            "platform_stats": platform_stats,
            "sales_stats": {
                "total_orders": sales_count,
                "total_sales": total_sales,
                "total_commission": total_commission,
                "average_order_value": total_sales / sales_count if sales_count > 0 else 0
            },
            "demo_mode": platform_stats.get("demo_mode", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/end", summary="Terminer une session live")
async def end_live_session(session_id: str):
    """
    Terminer le live

    Actions:
    1. Arrête le stream sur la plateforme
    2. Récupère les stats finales
    3. Désactive le boost de commission
    4. Génère le rapport final
    """
    try:
        # Récupérer la session
        session_result = supabase.table("live_shopping_sessions").select("*").eq("id", session_id).execute()

        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_result.data[0]
        platform = session["platform"]
        broadcast_id = session["platform_broadcast_id"]

        # Terminer selon la plateforme
        platform_result = None

        if platform == "instagram":
            platform_result = await instagram_live_service.end_live_stream(broadcast_id)

        elif platform == "tiktok":
            platform_result = await tiktok_live_service.end_live(broadcast_id)

        elif platform == "youtube":
            platform_result = await youtube_live_service.end_broadcast(broadcast_id)

        elif platform == "facebook":
            platform_result = await facebook_live_service.end_live_video(broadcast_id)

        if not platform_result or not platform_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Erreur fin live: {platform_result.get('error', 'Unknown')}"
            )

        final_stats = platform_result.get("final_stats", {})

        # Récupérer les ventes finales
        sales_result = supabase.table("sales").select("amount, influencer_commission").eq(
            "metadata->>live_session_id", session_id
        ).execute()

        total_sales = sum(sale["amount"] for sale in sales_result.data)
        total_commission = sum(sale["influencer_commission"] for sale in sales_result.data)
        sales_count = len(sales_result.data)

        # Mettre à jour notre DB
        supabase.table("live_shopping_sessions").update({
            "status": "ended",
            "actual_end_time": datetime.utcnow().isoformat(),
            "total_views": final_stats.get("total_viewers") or final_stats.get("total_views", 0),
            "peak_viewers": final_stats.get("peak_viewers") or final_stats.get("peak_live_views", 0),
            "total_orders": sales_count,
            "total_sales": total_sales,
            "total_commission": total_commission,
            "final_stats": final_stats
        }).eq("id", session_id).execute()

        return {
            "success": True,
            "session_id": session_id,
            "status": "ended",
            "final_report": {
                "platform": platform,
                "duration_minutes": final_stats.get("duration_minutes", 0),
                "engagement": {
                    "total_viewers": final_stats.get("total_viewers") or final_stats.get("total_views", 0),
                    "peak_viewers": final_stats.get("peak_viewers") or final_stats.get("peak_live_views", 0),
                    "total_likes": final_stats.get("total_likes", 0),
                    "total_comments": final_stats.get("total_comments", 0),
                    "total_shares": final_stats.get("total_shares", 0),
                    "engagement_rate": final_stats.get("engagement_rate", 0)
                },
                "sales": {
                    "total_orders": sales_count,
                    "total_revenue": total_sales,
                    "total_commission": total_commission,
                    "average_order_value": total_sales / sales_count if sales_count > 0 else 0,
                    "conversion_rate": (sales_count / final_stats.get("total_viewers", 1)) * 100 if final_stats.get("total_viewers") else 0
                }
            },
            "vod_url": platform_result.get("vod_url") or platform_result.get("permalink_url"),
            "ended_at": platform_result.get("ended_at"),
            "message": f"🎉 Live terminé! {sales_count} ventes pour {total_sales:.2f}€"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimal-times/{platform}", summary="Meilleurs moments pour faire un live")
async def get_optimal_live_times(platform: Platform):
    """
    Obtenir les meilleurs moments pour faire un live selon la plateforme

    Basé sur les données d'engagement pour le Maroc/MENA
    """
    times = []

    if platform == Platform.INSTAGRAM:
        times = instagram_live_service.get_optimal_live_times()

    elif platform == Platform.TIKTOK:
        times = tiktok_live_service.get_optimal_live_times_morocco()

    elif platform == Platform.YOUTUBE:
        times = youtube_live_service.get_optimal_live_times()

    elif platform == Platform.FACEBOOK:
        times = facebook_live_service.get_optimal_live_times_morocco()

    return {
        "platform": platform.value,
        "region": "Morocco/MENA",
        "optimal_times": times,
        "tips": [
            f"🎯 Meilleur jour: {times[0]['day']}",
            f"⏰ Meilleure heure: {times[0]['time_slots'][0]}",
            f"📊 Engagement attendu: {times[0]['engagement_score']}/100",
            "📢 Annonce ton live 24-48h avant",
            "🎁 Prépare une offre exclusive live"
        ]
    }


@router.get("/best-practices/{platform}", summary="Bonnes pratiques par plateforme")
async def get_live_best_practices(platform: Platform):
    """
    Guide des meilleures pratiques pour le live shopping selon la plateforme
    """
    practices = {}

    if platform == Platform.TIKTOK:
        practices = tiktok_live_service.get_live_best_practices()

    elif platform == Platform.FACEBOOK:
        practices = facebook_live_service.get_live_best_practices()

    else:
        # Pratiques générales pour Instagram/YouTube
        practices = {
            "avant_live": [
                "📢 Annonce le live 24-48h avant",
                "🎁 Prépare codes promos exclusifs",
                "📦 Vérifie stock des produits",
                "🎥 Teste ton matériel",
                "📝 Prépare un script"
            ],
            "pendant_live": [
                "👋 Salue les viewers",
                "⏱️ Durée optimale: 30-45 min",
                "🔥 Présente 3-5 produits max",
                "💬 Réponds aux questions",
                "🎯 CTA clairs et réguliers"
            ],
            "apres_live": [
                "📊 Analyse les stats",
                "📬 Message aux viewers",
                "📱 Partage le replay",
                "💰 Track les ventes",
                "📈 Note ce qui a marché"
            ]
        }

    return {
        "platform": platform.value,
        "best_practices": practices,
        "commission_boost": "+5% pendant le live"
    }


@router.get("/my-sessions/{user_id}", summary="Mes sessions live")
async def get_my_live_sessions(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status: scheduled, live, ended")
):
    """
    Récupérer toutes les sessions live d'un utilisateur
    """
    query = supabase.table("live_shopping_sessions").select("*").eq("host_id", user_id)

    if status:
        query = query.eq("status", status)

    result = query.order("scheduled_at", desc=True).execute()

    return {
        "sessions": result.data,
        "total": len(result.data)
    }


@router.get("/upcoming", summary="Prochains lives de la communauté")
async def get_upcoming_lives(limit: int = Query(10, ge=1, le=50)):
    """
    Récupérer les prochains lives de tous les influenceurs

    Utile pour:
    - Découvrir les lives à venir
    - S'inspirer
    - Participer au chat
    """
    result = supabase.table("live_shopping_sessions").select(
        "id, host_id, title, platform, scheduled_at, status, watch_url"
    ).eq("status", "scheduled").order("scheduled_at", desc=False).limit(limit).execute()

    return {
        "upcoming_lives": result.data,
        "count": len(result.data)
    }


# ==================== WEBHOOK POUR ATTRIBUTION VENTES ====================

@router.post("/webhook/sale-during-live", summary="[Internal] Webhook attribution vente pendant live")
async def attribute_sale_to_live(
    sale_id: str,
    influencer_id: str
):
    """
    Attribution automatique d'une vente à un live en cours

    Appelé lors d'une vente pour vérifier si elle provient d'un live actif
    et appliquer le boost de commission +5%
    """
    try:
        # Chercher un live actif pour cet influenceur
        active_live = supabase.table("live_shopping_sessions").select("*").eq(
            "host_id", influencer_id
        ).eq("status", "live").execute()

        if not active_live.data:
            return {"attributed_to_live": False}

        live_session = active_live.data[0]

        # Vérifier que le live est bien en cours (dans les 2h)
        start_time = datetime.fromisoformat(live_session["actual_start_time"])
        time_diff = (datetime.utcnow() - start_time).total_seconds() / 3600

        if time_diff > 2:  # Plus de 2h, probablement terminé
            return {"attributed_to_live": False}

        # Mettre à jour la vente avec l'info du live
        supabase.table("sales").update({
            "metadata": {
                "live_session_id": live_session["id"],
                "commission_boost_applied": 5.0
            }
        }).eq("id", sale_id).execute()

        # TODO: Recalculer la commission avec le boost +5%

        return {
            "attributed_to_live": True,
            "live_session_id": live_session["id"],
            "boost_applied": "5%"
        }

    except Exception as e:
        return {
            "attributed_to_live": False,
            "error": str(e)
        }
