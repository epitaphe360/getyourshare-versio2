"""
Predictive Dashboard Endpoints
Endpoints pour le dashboard prédictif Netflix-Style
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import os

from predictive_dashboard_service import (
    PredictiveDashboardService,
    DashboardData,
    PredictionTimeframe
)
from auth import get_current_user
from db_helpers import log_user_activity
from db_queries_real import get_user_campaigns
from supabase_client import supabase

router = APIRouter(prefix="/api/dashboard", tags=["Predictive Dashboard"])

# Initialiser le service
dashboard_service = PredictiveDashboardService()

# ============================================
# ENDPOINTS
# ============================================

@router.get("/predictive", response_model=DashboardData)
async def get_predictive_dashboard(
    timeframe: PredictionTimeframe = PredictionTimeframe.MONTH,
    current_user: dict = Depends(get_current_user)
):
    """
    Dashboard Netflix-Style avec prédictions ML et gamification

    Retourne:
    - Stats actuelles
    - Prédictions futures (revenus, conversions, etc.)
    - Comparaisons avec autres utilisateurs
    - Achievements et niveau
    - Leaderboards
    - Insights intelligents
    - Wrapped stats (style Spotify)
    """

    try:
        # Récupérer l'historique de campagnes
        campaign_history = await get_user_campaigns(current_user["id"])

        # Générer le dashboard complet
        dashboard_data = await dashboard_service.generate_dashboard(
            user_id=current_user["id"],
            user_data=current_user,
            campaign_history=campaign_history,
            timeframe=timeframe
        )

        log_user_activity(
            user_id=current_user["id"],
            action="viewed_predictive_dashboard",
            details={"timeframe": timeframe}
        )

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du dashboard: {str(e)}"
        )


@router.get("/predictions")
async def get_predictions_only(
    timeframe: PredictionTimeframe = PredictionTimeframe.MONTH,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère uniquement les prédictions sans le dashboard complet

    Plus léger pour des requêtes rapides
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        predictions = await dashboard_service._generate_predictions(
            campaign_history=campaign_history,
            timeframe=timeframe
        )

        return {
            "timeframe": timeframe,
            "predictions": predictions,
            "generated_at": "2025-10-26T00:00:00Z"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/wrapped")
async def get_wrapped_stats(
    year: int = 2025,
    current_user: dict = Depends(get_current_user)
):
    """
    Stats Wrapped style Spotify / Netflix Year in Review

    Résumé annuel avec stats impressionnantes et partageables
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        filtered_history = []
        for campaign in (campaign_history or []):
            date_candidate = (
                campaign.get("created_at")
                or campaign.get("date")
                or campaign.get("campaign_date")
            )
            if not date_candidate:
                continue
            try:
                year_candidate = datetime.fromisoformat(str(date_candidate).replace("Z", "+00:00")).year
                if year_candidate == year:
                    filtered_history.append(campaign)
            except Exception:
                continue

        campaign_history = filtered_history

        wrapped_stats = dashboard_service._generate_wrapped_stats(
            campaign_history=campaign_history,
            user_data=current_user
        )

        return {
            "year": year,
            "wrapped": wrapped_stats,
            "shareable_image_url": f"{os.getenv('FRONTEND_URL', '').rstrip('/')}/dashboard/predictive/wrapped?year={year}" if os.getenv('FRONTEND_URL') else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/achievements")
async def get_my_achievements(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les achievements de l'utilisateur

    Affiche la progression pour chaque achievement
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])

        achievements = await dashboard_service._calculate_achievements(
            user_data=current_user,
            campaign_history=campaign_history
        )

        level_data = dashboard_service._calculate_level(campaign_history)

        return {
            "achievements": achievements,
            "level": level_data["level"],
            "xp": level_data["xp"],
            "xp_for_next_level": level_data["xp_for_next_level"],
            "progress_to_next_level": level_data["progress"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/leaderboards")
async def get_all_leaderboards(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les leaderboards

    Catégories:
    - Top Earners
    - Best Conversion Rates
    - Most Campaigns
    - Highest Trust Score
    """

    try:
        users_resp = supabase.table("users").select("id,username,avatar_url").limit(200).execute()
        users = users_resp.data or []
        user_map = {u.get("id"): u for u in users}

        conv_resp = supabase.table("conversions").select("user_id,amount").limit(5000).execute()
        conversions = conv_resp.data or []

        revenue_by_user = {}
        for conv in conversions:
            uid = conv.get("user_id")
            if not uid:
                continue
            revenue_by_user[uid] = revenue_by_user.get(uid, 0.0) + float(conv.get("amount") or 0.0)

        ranked = sorted(revenue_by_user.items(), key=lambda item: item[1], reverse=True)
        top_users = []
        for idx, (uid, value) in enumerate(ranked[:10], start=1):
            user = user_map.get(uid, {})
            top_users.append({
                "rank": idx,
                "username": user.get("username") or f"user_{str(uid)[:8]}",
                "value": round(value, 2),
                "avatar": user.get("avatar_url")
            })

        current_uid = current_user.get("id")
        user_rank = None
        for idx, (uid, _) in enumerate(ranked, start=1):
            if uid == current_uid:
                user_rank = idx
                break

        leaderboards = [{
            "category": "Top Earners (Global)",
            "user_rank": user_rank,
            "total_users": len(ranked),
            "top_users": top_users
        }]

        return {"leaderboards": leaderboards}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/insights")
async def get_smart_insights(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les insights intelligents personnalisés

    Suggestions basées sur l'IA pour améliorer les performances
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])
        current_stats = dashboard_service._calculate_current_stats(campaign_history)
        predictions = await dashboard_service._generate_predictions(
            campaign_history,
            PredictionTimeframe.MONTH
        )

        insights = await dashboard_service._generate_insights(
            user_data=current_user,
            campaign_history=campaign_history,
            current_stats=current_stats,
            predictions=predictions
        )

        return {"insights": insights, "count": len(insights)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/comparisons")
async def get_my_comparisons(
    current_user: dict = Depends(get_current_user)
):
    """
    Compare les stats de l'utilisateur avec la moyenne de la plateforme

    "Tu es dans le top 15% des influenceurs !"
    """

    try:
        campaign_history = await get_user_campaigns(current_user["id"])
        current_stats = dashboard_service._calculate_current_stats(campaign_history)

        comparisons = await dashboard_service._generate_comparisons(
            user_id=current_user["id"],
            current_stats=current_stats
        )

        return comparisons

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_campaigns(user_id: str):
    """Récupère l'historique de campagnes d'un utilisateur"""
    try:
        result = supabase.table("campaigns").select("*").eq(
            "user_id", user_id
        ).execute()

        return result.data if result.data else []
    except Exception:
        return []
