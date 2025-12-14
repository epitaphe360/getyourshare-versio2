"""
Predictive Dashboard Endpoints
Endpoints pour le dashboard prédictif Netflix-Style
"""

from fastapi import APIRouter, Depends, HTTPException, status

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

        # Filtrer par année si nécessaire
        # TODO: Implémenter le filtrage par année

        wrapped_stats = dashboard_service._generate_wrapped_stats(
            campaign_history=campaign_history,
            user_data=current_user
        )

        return {
            "year": year,
            "wrapped": wrapped_stats,
            "shareable_image_url": None  # TODO: Générer une image partageable
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
        from datetime import datetime, timedelta

        # Calculer le début du mois
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Top Earners - Récupérer les meilleurs revenus ce mois
        top_earners_result = supabase.table("commissions")\
            .select("user_id, amount, users(username, avatar_url)")\
            .gte("created_at", month_start.isoformat())\
            .order("amount", desc=True)\
            .limit(10)\
            .execute()

        # Agréger par utilisateur
        earners_by_user = {}
        for record in (top_earners_result.data or []):
            user_id = record.get("user_id")
            if user_id not in earners_by_user:
                earners_by_user[user_id] = {
                    "username": record.get("users", {}).get("username", "Anonyme"),
                    "avatar": record.get("users", {}).get("avatar_url"),
                    "value": 0
                }
            earners_by_user[user_id]["value"] += record.get("amount", 0)

        # Trier et formater
        sorted_earners = sorted(earners_by_user.values(), key=lambda x: x["value"], reverse=True)[:3]
        top_earners = [
            {"rank": i+1, "username": e["username"], "value": round(e["value"], 2), "avatar": e["avatar"]}
            for i, e in enumerate(sorted_earners)
        ]

        # Calculer le rang de l'utilisateur actuel
        user_earnings = earners_by_user.get(current_user["id"], {}).get("value", 0)
        user_rank_earners = sum(1 for e in earners_by_user.values() if e["value"] > user_earnings) + 1

        # Top Conversion Rates - Récupérer les meilleurs taux
        conversion_result = supabase.table("campaign_stats")\
            .select("user_id, clicks, conversions, users(username, avatar_url)")\
            .gte("created_at", month_start.isoformat())\
            .gt("clicks", 0)\
            .execute()

        # Calculer les taux par utilisateur
        rates_by_user = {}
        for record in (conversion_result.data or []):
            user_id = record.get("user_id")
            clicks = record.get("clicks", 0)
            conversions = record.get("conversions", 0)
            if clicks > 0:
                rate = (conversions / clicks) * 100
                if user_id not in rates_by_user or rate > rates_by_user[user_id]["value"]:
                    rates_by_user[user_id] = {
                        "username": record.get("users", {}).get("username", "Anonyme"),
                        "avatar": record.get("users", {}).get("avatar_url"),
                        "value": round(rate, 2)
                    }

        sorted_rates = sorted(rates_by_user.values(), key=lambda x: x["value"], reverse=True)[:3]
        top_converters = [
            {"rank": i+1, "username": r["username"], "value": r["value"], "avatar": r["avatar"]}
            for i, r in enumerate(sorted_rates)
        ]

        # Rang utilisateur pour conversions
        user_rate = rates_by_user.get(current_user["id"], {}).get("value", 0)
        user_rank_conversion = sum(1 for r in rates_by_user.values() if r["value"] > user_rate) + 1

        # Compter le total d'utilisateurs
        total_users_result = supabase.table("users").select("id", count="exact").execute()
        total_users = total_users_result.count or len(earners_by_user) or 100

        leaderboards = [
            {
                "category": "Top Earners (Ce mois)",
                "user_rank": user_rank_earners,
                "total_users": total_users,
                "top_users": top_earners if top_earners else [
                    {"rank": 1, "username": "Pas encore de données", "value": 0, "avatar": None}
                ]
            },
            {
                "category": "Meilleurs Taux de Conversion",
                "user_rank": user_rank_conversion,
                "total_users": total_users,
                "top_users": top_converters if top_converters else [
                    {"rank": 1, "username": "Pas encore de données", "value": 0, "avatar": None}
                ]
            }
        ]

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
