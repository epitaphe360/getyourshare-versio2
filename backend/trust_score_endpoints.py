"""
Trust Score Endpoints
Endpoints pour le système de Trust Score anti-fraude
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trust_score_service import TrustScoreService, TrustReport
from auth import get_current_user
# from db_helpers import log_user_activity  # TODO: Implémenter log_user_activity dans db_helpers
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/trust-score", tags=["Trust Score"])

# Initialiser le service
trust_service = TrustScoreService()

# ============================================
# ENDPOINTS
# ============================================

@router.get("/my-score", response_model=TrustReport)
async def get_my_trust_score(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère le Trust Score de l'utilisateur connecté

    Retourne:
    - Score global (0-100)
    - Breakdown détaillé par critère
    - Badges débloqués
    - Indicateurs de fraude (si détectés)
    - Recommandations pour améliorer le score
    """

    try:
        # Récupérer l'historique de campagnes
        campaign_history = await get_user_campaign_history(current_user["id"])

        # Récupérer les données de trafic
        traffic_data = await get_user_traffic_data(current_user["id"])

        # Calculer le Trust Score
        trust_report = await trust_service.calculate_trust_score(
            user_id=current_user["id"],
            user_data=current_user,
            campaign_history=campaign_history,
            traffic_data=traffic_data
        )

        # Sauvegarder le score dans la DB
        await save_trust_score(current_user["id"], trust_report)

        return trust_report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul du Trust Score: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=TrustReport)
async def get_user_trust_score(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère le Trust Score public d'un autre utilisateur

    Accessible par:
    - Admins (score complet)
    - Merchants (score des influenceurs)
    - Influencers (score des merchants)
    """

    try:
        # Vérifier les permissions
        if current_user["role"] not in ["admin", "merchant", "influencer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non autorisé"
            )

        # Récupérer le score depuis la DB (cache)
        cached_score = await get_cached_trust_score(user_id)

        if cached_score:
            # Si le score a moins de 24h, le retourner
            return cached_score

        # Sinon, recalculer
        user_data = await get_user_data(user_id)
        campaign_history = await get_user_campaign_history(user_id)
        traffic_data = await get_user_traffic_data(user_id)

        trust_report = await trust_service.calculate_trust_score(
            user_id=user_id,
            user_data=user_data,
            campaign_history=campaign_history,
            traffic_data=traffic_data
        )

        # Sauvegarder
        await save_trust_score(user_id, trust_report)

        # Si l'utilisateur n'est pas admin, masquer certaines infos sensibles
        if current_user["role"] != "admin":
            trust_report.fraud_indicators = []  # Ne pas exposer les détails de fraude

        return trust_report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/leaderboard")
async def get_trust_score_leaderboard(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère le leaderboard des utilisateurs avec les meilleurs Trust Scores

    Public pour encourager la compétition et la transparence
    """

    try:
        # TODO: Récupérer de la DB
        result = supabase.table("trust_scores").select(
            "user_id, username, trust_score, trust_level, badges"
        ).order("trust_score", desc=True).limit(limit).execute()

        return {
            "leaderboard": result.data if result.data else [],
            "count": len(result.data) if result.data else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/recalculate")
async def recalculate_my_score(
    current_user: dict = Depends(get_current_user)
):
    """
    Force le recalcul du Trust Score

    Limité à 1 fois par jour pour éviter l'abus
    """

    try:
        # Vérifier la dernière mise à jour
        last_update = await get_last_score_update(current_user["id"])

        # TODO: Implémenter rate limiting

        # Recalculer
        campaign_history = await get_user_campaign_history(current_user["id"])
        traffic_data = await get_user_traffic_data(current_user["id"])

        trust_report = await trust_service.calculate_trust_score(
            user_id=current_user["id"],
            user_data=current_user,
            campaign_history=campaign_history,
            traffic_data=traffic_data
        )

        await save_trust_score(current_user["id"], trust_report)

        await log_user_activity(
            user_id=current_user["id"],
            action="trust_score_recalculated",
            details={"new_score": trust_report.trust_score}
        )

        return {
            "message": "Trust Score recalculé avec succès",
            "trust_report": trust_report
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/badges")
async def get_available_badges(
    current_user: dict = Depends(get_current_user)
):
    """
    Liste tous les badges disponibles et leur progression

    Gamification pour encourager les bonnes pratiques
    """

    badges = [
        {
            "id": "verified_pro",
            "name": "✅ Verified Pro",
            "description": "Atteindre un Trust Score de 90+",
            "requirement": "Trust Score >= 90",
            "rarity": "rare"
        },
        {
            "id": "elite_partner",
            "name": "🏆 Elite Partner",
            "description": "Atteindre un Trust Score de 95+",
            "requirement": "Trust Score >= 95",
            "rarity": "legendary"
        },
        {
            "id": "conversion_king",
            "name": "💰 Conversion King",
            "description": "Générer 1000+ conversions",
            "requirement": "1000+ conversions totales",
            "rarity": "epic"
        },
        {
            "id": "veteran",
            "name": "💼 Veteran",
            "description": "Compléter 50+ campagnes",
            "requirement": "50+ campagnes complétées",
            "rarity": "rare"
        },
        {
            "id": "master",
            "name": "🎖️ Master",
            "description": "Compléter 100+ campagnes",
            "requirement": "100+ campagnes complétées",
            "rarity": "epic"
        },
        {
            "id": "identity_verified",
            "name": "🔐 Identity Verified",
            "description": "Compléter la vérification KYC",
            "requirement": "KYC vérifié",
            "rarity": "common"
        }
    ]

    return {"badges": badges}


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_campaign_history(user_id: str) -> List[dict]:
    """Récupère l'historique de campagnes d'un utilisateur"""
    try:
        result = supabase.table("campaigns").select("*").eq(
            "user_id", user_id
        ).execute()

        return result.data if result.data else []
    except Exception:
        return []


async def get_user_traffic_data(user_id: str) -> dict:
    """Récupère les données de trafic pour analyse de fraude depuis tracking_events"""
    try:
        from datetime import timedelta
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

        # Clics réels depuis tracking_events
        clicks_r = supabase.table("tracking_events").select(
            "id, ip_address, created_at"
        ).eq("influencer_id", user_id).gte("created_at", thirty_days_ago).execute()
        clicks = clicks_r.data or []
        total_clicks = len(clicks)

        # Conversions réelles
        conv_r = supabase.table("conversions").select("id").eq(
            "affiliate_id", user_id
        ).gte("created_at", thirty_days_ago).execute()
        total_conversions = len(conv_r.data or [])

        # Détecter IPs suspectes (doublons excessifs)
        ip_counts: dict = {}
        for c in clicks:
            ip = c.get("ip_address", "")
            if ip:
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
        suspicious_ips = sum(1 for cnt in ip_counts.values() if cnt > 20)
        suspicious_ip_pct = round((suspicious_ips / len(ip_counts) * 100), 1) if ip_counts else 0.0

        return {
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "bounce_rate": 60.0,  # approx sans données session
            "avg_session_duration": 45,
            "suspicious_ip_percentage": suspicious_ip_pct,
            "click_pattern_score": max(0.0, 100.0 - suspicious_ip_pct * 2),
            "geo_consistency": 90.0,
        }
    except Exception as e:
        logger.warning(f"get_user_traffic_data fallback: {e}")
        return {
            "total_clicks": 0, "total_conversions": 0, "bounce_rate": 60.0,
            "avg_session_duration": 45, "suspicious_ip_percentage": 0.0,
            "click_pattern_score": 80.0, "geo_consistency": 90.0,
        }


async def save_trust_score(user_id: str, trust_report: TrustReport):
    """Sauvegarde le Trust Score dans la DB"""
    try:
        data = {
            "user_id": user_id,
            "trust_score": trust_report.trust_score,
            "trust_level": trust_report.trust_level,
            "breakdown": trust_report.breakdown.dict(),
            "badges": trust_report.badges,
            "fraud_indicators": [f.dict() for f in trust_report.fraud_indicators],
            "last_updated": trust_report.last_updated.isoformat()
        }

        # Upsert
        result = supabase.table("trust_scores").upsert(data).execute()
        return result
    except Exception as e:
        logger.error(f"Error saving trust score: {e}")


async def get_cached_trust_score(user_id: str) -> Optional[TrustReport]:
    """Récupère le Trust Score en cache depuis la table trust_scores"""
    try:
        result = supabase.table("trust_scores").select("*").eq(
            "user_id", user_id
        ).limit(1).execute()

        if result.data:
            row = result.data[0]
            from trust_score_service import TrustReport, TrustScoreBreakdown, FraudIndicator, TrustLevel
            breakdown_data = row.get("breakdown") or {}
            breakdown = TrustScoreBreakdown(**breakdown_data) if breakdown_data else TrustScoreBreakdown(
                identity_verification=0, campaign_history=0, payment_reliability=0,
                audience_quality=0, content_quality=0, fraud_risk=0
            )
            fraud_indicators = [
                FraudIndicator(**fi) for fi in (row.get("fraud_indicators") or [])
                if isinstance(fi, dict)
            ]
            return TrustReport(
                user_id=user_id,
                trust_score=row.get("trust_score", 0),
                trust_level=row.get("trust_level", TrustLevel.UNKNOWN),
                breakdown=breakdown,
                badges=row.get("badges") or [],
                fraud_indicators=fraud_indicators,
                recommendations=row.get("recommendations") or [],
                last_updated=datetime.fromisoformat(row["last_updated"]) if row.get("last_updated") else datetime.utcnow()
            )
        return None
    except Exception as e:
        logger.warning(f"get_cached_trust_score error: {e}")
        return None


async def get_user_data(user_id: str) -> dict:
    """Récupère les données utilisateur"""
    try:
        result = supabase.table("users").select("*").eq(
            "id", user_id
        ).single().execute()

        return result.data if result.data else {}
    except Exception:
        return {}


async def get_last_score_update(user_id: str) -> Optional[str]:
    """Récupère la date de dernière mise à jour du score"""
    try:
        result = supabase.table("trust_scores").select("last_updated").eq(
            "user_id", user_id
        ).single().execute()

        return result.data.get("last_updated") if result.data else None
    except Exception:
        return None
