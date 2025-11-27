"""
Routes du dashboard - Statistiques et activités récentes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from db_helpers import get_dashboard_stats, supabase
from auth import get_current_user_from_cookie
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_statistics(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Statistiques du dashboard pour l'utilisateur connecté"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    role = payload.get("role")
    
    try:
        stats = get_dashboard_stats(user_id, role)
        return stats
    except Exception as e:
        # Retourner des stats vides plutôt qu'une erreur
        return {
            "total_clicks": 0,
            "total_sales": 0,
            "total_revenue": 0,
            "conversion_rate": 0,
            "active_campaigns": 0,
            "pending_payouts": 0
        }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Activités récentes de l'utilisateur"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    role = payload.get("role")
    
    try:
        activities = []
        
        # Pour les influenceurs - derniers clics et conversions
        if role == "influencer":
            # Derniers clics
            clicks_response = supabase.table("clicks") \
                .select("*, affiliate_links(*)") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if clicks_response.data:
                for click in clicks_response.data[:5]:
                    activities.append({
                        "type": "click",
                        "description": f"Clic sur un lien d'affiliation",
                        "created_at": click.get("created_at"),
                        "amount": None
                    })
            
            # Dernières conversions
            conversions_response = supabase.table("conversions") \
                .select("*") \
                .eq("influencer_id", user_id) \
                .order("created_at", desc=True) \
                .limit(5) \
                .execute()
            
            if conversions_response.data:
                for conv in conversions_response.data:
                    activities.append({
                        "type": "conversion",
                        "description": f"Vente réalisée",
                        "created_at": conv.get("created_at"),
                        "amount": conv.get("amount")
                    })
        
        # Pour les marchands - dernières commandes et campagnes
        elif role == "merchant":
            # Dernières conversions de leurs produits
            conversions_response = supabase.table("conversions") \
                .select("*") \
                .eq("merchant_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if conversions_response.data:
                for conv in conversions_response.data:
                    activities.append({
                        "type": "sale",
                        "description": f"Nouvelle vente via affiliation",
                        "created_at": conv.get("created_at"),
                        "amount": conv.get("amount")
                    })
        
        # Trier par date décroissante
        activities.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return activities[:limit]
    
    except Exception as e:
        return []


@router.get("/overview")
async def get_dashboard_overview(
    period: str = "7d",  # 7d, 30d, 90d
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Vue d'ensemble du dashboard avec métriques clés"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    role = payload.get("role")
    
    # Calculer la date de début selon la période
    period_days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 7)
    start_date = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
    
    try:
        overview = {
            "period": period,
            "start_date": start_date,
            "metrics": {}
        }
        
        if role == "influencer":
            # Métriques influenceur
            clicks_response = supabase.table("clicks") \
                .select("*", count="exact") \
                .eq("user_id", user_id) \
                .gte("created_at", start_date) \
                .execute()
            
            conversions_response = supabase.table("conversions") \
                .select("amount") \
                .eq("influencer_id", user_id) \
                .gte("created_at", start_date) \
                .execute()
            
            total_clicks = clicks_response.count if clicks_response.count else 0
            total_amount = sum(c.get("amount", 0) for c in (conversions_response.data or []))
            
            overview["metrics"] = {
                "total_clicks": total_clicks,
                "total_conversions": len(conversions_response.data or []),
                "total_revenue": total_amount,
                "conversion_rate": (len(conversions_response.data or []) / total_clicks * 100) if total_clicks > 0 else 0
            }
        
        elif role == "merchant":
            # Métriques marchand
            conversions_response = supabase.table("conversions") \
                .select("amount") \
                .eq("merchant_id", user_id) \
                .gte("created_at", start_date) \
                .execute()
            
            products_response = supabase.table("products") \
                .select("*", count="exact") \
                .eq("merchant_id", user_id) \
                .execute()
            
            total_sales = sum(c.get("amount", 0) for c in (conversions_response.data or []))
            
            overview["metrics"] = {
                "total_sales": total_sales,
                "total_orders": len(conversions_response.data or []),
                "total_products": products_response.count if products_response.count else 0,
                "average_order_value": total_sales / len(conversions_response.data) if conversions_response.data else 0
            }
        
        return overview
    
    except Exception as e:
        return {
            "period": period,
            "start_date": start_date,
            "metrics": {}
        }
