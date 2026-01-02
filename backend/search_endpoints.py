from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from auth import get_current_user_from_cookie
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/global")
async def global_search(
    q: str = Query(..., min_length=1),
    type: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Recherche globale (Produits, Campagnes, Utilisateurs)
    """
    try:
        results = {
            "products": [],
            "campaigns": [],
            "merchants": [],
            "influencers": []
        }
        
        # Search Products
        if not type or type == "product":
            products = supabase.table("products").select("id, name, description, price, image_url")\
                .ilike("name", f"%{q}%")\
                .limit(5).execute()
            results["products"] = products.data or []

        # Search Campaigns
        if not type or type == "campaign":
            campaigns = supabase.table("campaigns").select("id, name, description, budget")\
                .ilike("name", f"%{q}%")\
                .limit(5).execute()
            results["campaigns"] = campaigns.data or []

        # Search Merchants
        if not type or type == "merchant":
            merchants = supabase.table("merchants").select("user_id, company_name, industry")\
                .ilike("company_name", f"%{q}%")\
                .limit(5).execute()
            results["merchants"] = merchants.data or []

        # Search Influencers
        if not type or type == "influencer":
            # Try to search in influencers table first
            try:
                influencers = supabase.table("influencers").select("user_id, username, full_name")\
                    .or_(f"username.ilike.%{q}%,full_name.ilike.%{q}%")\
                    .limit(5).execute()
                results["influencers"] = influencers.data or []
            except Exception:
                # Fallback to users table if influencers table structure is different
                pass

        return {
            "query": q,
            "results": results,
            "total": sum(len(v) for v in results.values())
        }

    except Exception as e:
        logger.error(f"Error in global search: {e}")
        # Return empty results instead of 500 to avoid breaking UI
        return {
            "query": q,
            "results": {
                "products": [],
                "campaigns": [],
                "merchants": [],
                "influencers": []
            },
            "total": 0
        }
