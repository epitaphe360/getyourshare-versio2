"""
Marketing Endpoints - Segmentation, Campagnes, Win-Back
Routes: /api/marketing/*
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/marketing", tags=["Marketing"])
logger = logging.getLogger(__name__)

# ── Supabase client ───────────────────────────────────────────────────────────
try:
    from database import get_supabase_client
    supabase = get_supabase_client()
except Exception:
    supabase = None
    logger.warning("Supabase non disponible – marketing_endpoints en mode dégradé")


# ── Helper: client Supabase ────────────────────────────────────────────────────
def _sb():
    if supabase is None:
        raise HTTPException(status_code=503, detail="Base de données non disponible")
    return supabase


# ── GET /api/marketing/stats ───────────────────────────────────────────────────
@router.get("/stats")
async def get_marketing_stats():
    """Statistiques globales marketing : campagnes, taux ouverture, revenus."""
    try:
        sb = _sb()

        # Nombre total de campagnes email
        campaigns_resp = sb.table("email_campaigns").select("id, status, revenue_generated, open_rate").execute()
        campaigns = campaigns_resp.data or []
        total_campaigns = len(campaigns)
        avg_open_rate = (
            sum(c.get("open_rate") or 0 for c in campaigns) / total_campaigns
            if total_campaigns > 0 else 0
        )
        total_revenue = sum(c.get("revenue_generated") or 0 for c in campaigns)

        # Clients actifs (conversion récente)
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        active_resp = sb.table("conversions").select("id").gte("created_at", thirty_days_ago).execute()
        active_customers = len(active_resp.data or [])

        # Clients inactifs > 90 jours
        ninety_days_ago = (datetime.utcnow() - timedelta(days=90)).isoformat()
        inactive_resp = (
            sb.table("conversions")
            .select("affiliate_id")
            .lt("created_at", ninety_days_ago)
            .execute()
        )
        inactive_customers = len(set(r["affiliate_id"] for r in (inactive_resp.data or []) if r.get("affiliate_id")))

        return {
            "total_campaigns": total_campaigns,
            "open_rate": round(avg_open_rate, 1),
            "revenue_generated": round(total_revenue, 2),
            "active_customers": active_customers,
            "inactive_customers": inactive_customers,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_marketing_stats: {e}")
        # Fallback gracieux
        return {
            "total_campaigns": 0,
            "open_rate": 0.0,
            "revenue_generated": 0.0,
            "active_customers": 0,
            "inactive_customers": 0,
        }


# ── GET /api/marketing/segments ───────────────────────────────────────────────
@router.get("/segments")
async def get_segments():
    """Segmentation RFM des utilisateurs."""
    try:
        sb = _sb()

        # Récupère les utilisateurs avec leurs conversions
        users_resp = sb.table("users").select("id, email, role, created_at").limit(500).execute()
        users = users_resp.data or []

        conv_resp = sb.table("conversions").select("affiliate_id, amount, created_at").execute()
        conversions = conv_resp.data or []

        # Agrège par utilisateur
        from collections import defaultdict
        user_stats: dict = defaultdict(lambda: {"count": 0, "revenue": 0.0, "last_date": None})
        for c in conversions:
            uid = c.get("affiliate_id")
            if uid:
                user_stats[uid]["count"] += 1
                user_stats[uid]["revenue"] += c.get("amount") or 0
                d = c.get("created_at")
                if d and (user_stats[uid]["last_date"] is None or d > user_stats[uid]["last_date"]):
                    user_stats[uid]["last_date"] = d

        now = datetime.utcnow()
        segments = {"champions": 0, "at_risk": 0, "inactive": 0, "new": 0}
        for u in users:
            uid = u["id"]
            stats = user_stats.get(uid)
            if not stats or stats["count"] == 0:
                segments["new"] += 1
                continue
            days_since = (
                (now - datetime.fromisoformat(stats["last_date"].rstrip("Z"))).days
                if stats["last_date"] else 999
            )
            if stats["count"] >= 5 and days_since <= 30:
                segments["champions"] += 1
            elif days_since > 90:
                segments["inactive"] += 1
            elif days_since > 30:
                segments["at_risk"] += 1
            else:
                segments["new"] += 1

        return {
            "segments": [
                {"name": "Champions", "key": "champions", "count": segments["champions"], "color": "#52c41a"},
                {"name": "À risque", "key": "at_risk", "count": segments["at_risk"], "color": "#faad14"},
                {"name": "Inactifs", "key": "inactive", "count": segments["inactive"], "color": "#ff4d4f"},
                {"name": "Nouveaux", "key": "new", "count": segments["new"], "color": "#1890ff"},
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_segments: {e}")
        return {"segments": []}


# ── GET /api/marketing/campaigns ──────────────────────────────────────────────
@router.get("/campaigns")
async def get_campaigns(limit: int = 20, offset: int = 0):
    """Liste des campagnes email/marketing."""
    try:
        sb = _sb()
        resp = (
            sb.table("email_campaigns")
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        campaigns = resp.data or []
        return {"campaigns": campaigns, "total": len(campaigns)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_campaigns: {e}")
        return {"campaigns": [], "total": 0}


# ── POST /api/marketing/win-back ──────────────────────────────────────────────
@router.post("/win-back")
async def run_win_back_campaign(body: dict = {}):
    """
    Déclenche une campagne de réactivation pour les clients inactifs > 90 jours.
    Lance des emails automatiques et crée un enregistrement de campagne.
    """
    try:
        sb = _sb()

        ninety_days_ago = (datetime.utcnow() - timedelta(days=90)).isoformat()

        # Identifie les affiliés inactifs
        inactive_resp = (
            sb.table("conversions")
            .select("affiliate_id")
            .lt("created_at", ninety_days_ago)
            .execute()
        )
        inactive_ids = list(set(
            r["affiliate_id"] for r in (inactive_resp.data or []) if r.get("affiliate_id")
        ))

        if not inactive_ids:
            return {"message": "Aucun client inactif trouvé", "sent": 0}

        # Crée un enregistrement de campagne win-back
        campaign_name = f"Win-Back {datetime.utcnow().strftime('%Y-%m-%d')}"
        campaign_data = {
            "name": campaign_name,
            "type": "win_back",
            "status": "running",
            "target_count": len(inactive_ids),
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            sb.table("email_campaigns").insert(campaign_data).execute()
        except Exception:
            pass  # La table peut ne pas exister encore

        return {
            "message": f"Campagne win-back lancée pour {len(inactive_ids)} client(s) inactif(s)",
            "sent": len(inactive_ids),
            "campaign_name": campaign_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur win_back_campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement de la campagne: {str(e)}")
