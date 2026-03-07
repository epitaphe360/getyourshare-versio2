"""
============================================
CRM ENDPOINTS
Share Your Sales - Gestion des Leads CRM
============================================
Endpoints pour le CRM Dashboard:
- GET /api/crm/leads        → liste leads avec scoring
- GET /api/crm/stats        → statistiques agrégées
- POST /api/crm/leads/{id}/score   → re-calculer score IA
- GET /api/crm/leads/{id}/predict  → prédiction de fermeture
- POST /api/crm/sequence/start     → démarrer séquence mail
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
import os
from supabase import create_client, Client
from auth import get_current_user_from_cookie
from utils.logger import logger

router = APIRouter(prefix="/api/crm", tags=["CRM"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def _score_lead(lead: dict) -> dict:
    """Calcule un score IA léger basé sur les champs disponibles."""
    score = 0
    status = lead.get("lead_status", "new")

    status_scores = {"new": 20, "contacted": 35, "qualified": 60, "proposal": 75, "negotiation": 88, "won": 100}
    score = status_scores.get(status, 20)

    # Bonus pour valeur élevée
    value = float(lead.get("estimated_value") or 0)
    if value > 50000:
        score = min(100, score + 10)
    elif value > 20000:
        score = min(100, score + 5)

    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
    lead_status = "hot" if score >= 75 else "warm" if score >= 45 else "cold"

    closing_probability = min(95, score + 5)
    days_to_close = max(3, int(30 * (1 - score / 100)))
    predicted_close_date = (datetime.now() + timedelta(days=days_to_close)).isoformat()

    return {
        **lead,
        "score": score,
        "grade": grade,
        "status": lead_status,
        "email_opens": lead.get("email_opens", 0),
        "link_clicks": lead.get("link_clicks", 0),
        "visited_pricing_page": lead.get("visited_pricing_page", False),
        "requested_demo": lead.get("requested_demo", False),
        "closing_probability": closing_probability,
        "predicted_close_date": predicted_close_date,
        "first_name": lead.get("contact_name", "").split(" ")[0] if lead.get("contact_name") else "",
        "last_name": " ".join(lead.get("contact_name", "").split(" ")[1:]) if lead.get("contact_name") else "",
        "email": lead.get("contact_email", ""),
        "company": lead.get("company_name", ""),
        "job_title": lead.get("job_title", ""),
        "estimated_value": value,
    }


@router.get("/leads")
async def get_crm_leads(
    filter: str = Query("all", description="Filtre: all, hot, warm, cold"),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Liste les leads avec scoring automatique."""
    try:
        query = supabase.table("leads").select("*").order("created_at", desc=True).limit(limit)
        result = query.execute()
        leads = result.data or []

        scored = [_score_lead(l) for l in leads]

        if filter != "all":
            scored = [l for l in scored if l.get("status") == filter]

        return {"leads": scored, "total": len(scored)}
    except Exception as e:
        logger.error(f"CRM leads error: {e}")
        # Fallback → service_leads si leads vide
        try:
            res2 = supabase.table("service_leads").select("*").order("created_at", desc=True).limit(limit).execute()
            raw = res2.data or []
            formatted = []
            for l in raw:
                score_val = 50
                st = l.get("status", "new")
                status_map = {"new": "cold", "contacted": "warm", "qualified": "warm", "converted": "hot"}
                formatted.append({
                    "id": l.get("id"),
                    "first_name": l.get("full_name", "").split(" ")[0],
                    "last_name": " ".join(l.get("full_name", "Lead").split(" ")[1:]),
                    "email": l.get("email", ""),
                    "company": l.get("company", ""),
                    "job_title": "",
                    "score": score_val,
                    "grade": "B",
                    "status": status_map.get(st, "cold"),
                    "closing_probability": 50,
                    "estimated_value": 0,
                    "last_activity": l.get("created_at"),
                })
            if filter != "all":
                formatted = [l for l in formatted if l.get("status") == filter]
            return {"leads": formatted, "total": len(formatted)}
        except Exception as e2:
            logger.error(f"CRM fallback error: {e2}")
            return {"leads": [], "total": 0}


@router.get("/stats")
async def get_crm_stats(current_user: dict = Depends(get_current_user_from_cookie)):
    """Stats globales CRM."""
    try:
        result = supabase.table("leads").select("*").execute()
        leads = result.data or []
        scored = [_score_lead(l) for l in leads]

        hot = [l for l in scored if l.get("status") == "hot"]
        warm = [l for l in scored if l.get("status") == "warm"]
        cold = [l for l in scored if l.get("status") == "cold"]

        avg_score = int(sum(l["score"] for l in scored) / len(scored)) if scored else 0
        total_value = sum(l.get("estimated_value", 0) for l in scored)

        return {
            "total_leads": len(leads),
            "hot_leads": len(hot),
            "warm_leads": len(warm),
            "cold_leads": len(cold),
            "avg_score": avg_score,
            "conversion_rate": round(len(hot) / max(len(leads), 1) * 100, 1),
            "avg_closing_time": 12,
            "revenue_pipeline": total_value,
            "active_sequences": 0,
            "tasks_automated": 0
        }
    except Exception as e:
        logger.error(f"CRM stats error: {e}")
        return {
            "total_leads": 0, "hot_leads": 0, "warm_leads": 0, "cold_leads": 0,
            "avg_score": 0, "conversion_rate": 0, "avg_closing_time": 0,
            "revenue_pipeline": 0, "active_sequences": 0, "tasks_automated": 0
        }


@router.post("/leads/{lead_id}/score")
async def rescore_lead(lead_id: str, current_user: dict = Depends(get_current_user_from_cookie)):
    """Recalcule le score d'un lead."""
    try:
        result = supabase.table("leads").select("*").eq("id", lead_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        return {"lead": _score_lead(result.data)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CRM rescore error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}/predict")
async def predict_lead(lead_id: str, current_user: dict = Depends(get_current_user_from_cookie)):
    """Prédiction de fermeture d'un lead."""
    try:
        result = supabase.table("leads").select("*").eq("id", lead_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        scored = _score_lead(result.data)
        return {
            "lead_id": lead_id,
            "closing_probability": scored["closing_probability"],
            "predicted_close_date": scored["predicted_close_date"],
            "score": scored["score"],
            "recommendation": "Planifiez une démo" if scored["score"] >= 70 else "Envoyez du contenu de nurturing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CRM predict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sequence/start")
async def start_sequence(
    body: dict,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Démarre une séquence email (stub — à connecter à un service d'emailing)."""
    lead_id = body.get("lead_id")
    sequence_type = body.get("sequence_type", "nurturing")
    logger.info(f"Sequence '{sequence_type}' started for lead {lead_id} by {current_user.get('id')}")
    return {"success": True, "message": f"Séquence '{sequence_type}' démarrée pour le lead {lead_id}"}
