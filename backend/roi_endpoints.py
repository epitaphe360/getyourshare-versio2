from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from supabase_client import supabase, get_supabase_client
from utils.logger import logger

router = APIRouter()

class ROICalculationRequest(BaseModel):
    # Support both old format (budget, campaign_type) and new format (monthly_traffic, conversion_rate)
    budget: Optional[float] = None
    industry: str
    campaign_type: Optional[str] = "influencer" # influencer, ads, email
    average_order_value: float = 50.0
    # New format fields
    monthly_traffic: Optional[int] = None
    conversion_rate: Optional[float] = None

class ROICalculationResponse(BaseModel):
    estimated_clicks: int
    estimated_conversions: int
    estimated_revenue: float
    roi_percentage: float
    net_profit: float
    metrics: Dict[str, Union[float, str]]

class ROISaveRequest(BaseModel):
    user_id: str
    campaign_name: str
    budget: float
    industry: str
    campaign_type: str
    estimated_revenue: float
    roi_percentage: float
    metrics: Dict[str, Any]

# Benchmarks par industrie (mock data based on real averages)
BENCHMARKS = {
    "fashion": {"cpc": 0.45, "ctr": 2.5, "cr": 3.2},
    "beauty": {"cpc": 0.60, "ctr": 3.1, "cr": 4.5},
    "tech": {"cpc": 1.20, "ctr": 1.8, "cr": 2.1},
    "home": {"cpc": 0.70, "ctr": 2.0, "cr": 2.8},
    "fitness": {"cpc": 0.55, "ctr": 2.8, "cr": 3.5},
    "food": {"cpc": 0.30, "ctr": 3.5, "cr": 4.0},
    "general": {"cpc": 0.50, "ctr": 2.0, "cr": 3.0}
}

@router.post("/calculate")
async def calculate_roi(request: ROICalculationRequest):
    """
    Calcule le ROI estimé pour une campagne
    Supporte deux formats:
    1. Ancien format: budget + campaign_type
    2. Nouveau format: monthly_traffic + conversion_rate
    """
    try:
        industry = request.industry.lower()
        if industry not in BENCHMARKS:
            industry = "general"

        # Use copy to avoid modifying global state
        metrics = BENCHMARKS[industry].copy()

        # Determine which format is being used
        if request.monthly_traffic is not None and request.conversion_rate is not None:
            # NEW FORMAT: Calculate based on traffic and conversion rate
            monthly_conversions = int(request.monthly_traffic * (request.conversion_rate / 100))
            potential_revenue = monthly_conversions * request.average_order_value

            # Estimate with 20% commission improvement from our platform
            boosted_conversion_rate = request.conversion_rate * 1.2
            boosted_conversions = int(request.monthly_traffic * (boosted_conversion_rate / 100))
            boosted_revenue = boosted_conversions * request.average_order_value

            additional_revenue = boosted_revenue - potential_revenue
            roi_multiplier = round(boosted_revenue / potential_revenue, 2) if potential_revenue > 0 else 1.0

            # Determine recommended tier based on traffic
            if request.monthly_traffic < 5000:
                recommended_tier = "basic"
            elif request.monthly_traffic < 20000:
                recommended_tier = "pro"
            else:
                recommended_tier = "enterprise"

            return {
                "potential_revenue": round(additional_revenue, 2),
                "roi_multiplier": roi_multiplier,
                "recommended_tier": recommended_tier,
                "estimated_clicks": request.monthly_traffic,
                "estimated_conversions": boosted_conversions,
                "estimated_revenue": round(boosted_revenue, 2),
                "roi_percentage": round((additional_revenue / potential_revenue) * 100 if potential_revenue > 0 else 0, 2),
                "net_profit": round(additional_revenue, 2),
                "metrics": {
                    "current_conversion_rate": request.conversion_rate,
                    "boosted_conversion_rate": round(boosted_conversion_rate, 2),
                    "industry": industry
                }
            }
        else:
            # OLD FORMAT: Calculate based on budget
            if request.budget is None:
                raise ValueError("Either provide (monthly_traffic + conversion_rate) or (budget + campaign_type)")

            # Ajustements selon le type de campagne
            campaign_type = request.campaign_type or "influencer"
            if campaign_type == "influencer":
                metrics["cpc"] = float(metrics["cpc"]) * 1.2
                metrics["cr"] = float(metrics["cr"]) * 1.5
            elif campaign_type == "email":
                metrics["cpc"] = 0.1
                metrics["cr"] = float(metrics["cr"]) * 2.0

            # Calculs
            cpc = float(metrics["cpc"]) if float(metrics["cpc"]) > 0 else 0.1
            estimated_clicks = int(request.budget / cpc)

            estimated_conversions = int(estimated_clicks * (float(metrics["cr"]) / 100))
            estimated_revenue = estimated_conversions * request.average_order_value

            net_profit = estimated_revenue - request.budget
            roi_percentage = (net_profit / request.budget) * 100 if request.budget > 0 else 0

            return {
                "estimated_clicks": estimated_clicks,
                "estimated_conversions": estimated_conversions,
                "estimated_revenue": round(estimated_revenue, 2),
                "roi_percentage": round(roi_percentage, 2),
                "net_profit": round(net_profit, 2),
                "metrics": metrics
            }
    except Exception as e:
        import traceback
        print(f"Error in calculate_roi: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Erreur de calcul: {str(e)}")

@router.get("/benchmarks")
async def get_benchmarks():
    """
    Retourne les benchmarks par industrie
    """
    return {
        "success": True,
        "benchmarks": BENCHMARKS,
        "industries": list(BENCHMARKS.keys())
    }

@router.post("/save")
async def save_roi_calculation(request: ROISaveRequest):
    """
    Sauvegarder un calcul de ROI
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "user_id": request.user_id,
            "campaign_name": request.campaign_name,
            "budget": request.budget,
            "industry": request.industry,
            "campaign_type": request.campaign_type,
            "estimated_revenue": request.estimated_revenue,
            "roi_percentage": request.roi_percentage,
            "metrics": request.metrics,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("roi_calculations").insert(data).execute()
        
        return {"success": True, "message": "Calcul sauvegardé", "id": result.data[0]['id']}
    except Exception as e:
        logger.error(f"Erreur sauvegarde ROI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_roi_history(user_id: str):
    """
    Récupérer l'historique des calculs ROI
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("roi_calculations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        return {"history": result.data}
    except Exception as e:
        logger.error(f"Erreur historique ROI: {e}")
        raise HTTPException(status_code=500, detail=str(e))
