"""
============================================
COMMERCIAL & INFLUENCER DASHBOARDS ENDPOINTS
GetYourShare - Dashboards Spécifiques
============================================

Endpoints pour dashboards commerciaux et influenceurs:
- Stats personnalisées
- Pipeline et performances
- Commissions et revenus
- Graphiques analytiques
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from auth import get_current_user
from supabase_client import supabase
from utils.logger import logger

# Routers séparés
commercial_router = APIRouter(prefix="/api/commercial", tags=["Commercial"])
influencer_router = APIRouter(prefix="/api/influencer", tags=["Influencer"])

# ============================================
# COMMERCIAL ENDPOINTS
# ============================================

@commercial_router.get("/stats")
async def get_commercial_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Statistiques dashboard commercial"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # TODO: Implémenter avec vraies données
        stats = {
            "total_leads": 45,
            "qualified_leads": 30,
            "conversions": 12,
            "commission_earned": 8500.00,
            "commission_pending": 2300.00,
            "conversion_rate": 26.67,
            "avg_deal_value": 750.00,
            "deals_this_month": 12
        }
        
        return {"stats": stats}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching commercial stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@commercial_router.get("/pipeline")
async def get_commercial_pipeline(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Données pipeline commercial"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Générer données de démonstration
        pipeline = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            pipeline.append({
                "date": date,
                "leads": 2 + (i % 5),
                "conversions": 0 + (i % 3)
            })
        
        return {"pipeline": pipeline}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@commercial_router.get("/performance")
async def get_commercial_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Performance commerciale mensuelle"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        performance = [
            {"month": "Jan", "deals": 8, "revenue": 6000},
            {"month": "Fév", "deals": 10, "revenue": 7500},
            {"month": "Mar", "deals": 12, "revenue": 9000},
            {"month": "Avr", "deals": 9, "revenue": 6750},
            {"month": "Mai", "deals": 11, "revenue": 8250},
            {"month": "Juin", "deals": 13, "revenue": 9750}
        ]
        
        return {"performance": performance}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@commercial_router.get("/commissions")
async def get_commercial_commissions(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Historique commissions"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        history = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            history.append({
                "date": date,
                "earned": 100 + (i * 50),
                "pending": 50 + (i * 20)
            })
        
        return {"history": history}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching commissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@commercial_router.get("/recent-deals")
async def get_recent_deals(
    current_user: Dict = Depends(get_current_user)
):
    """Derniers deals conclus"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        deals = [
            {
                "id": "1",
                "client_name": "Mohammed Alami",
                "company": "Tech Solutions",
                "deal_type": "subscription",
                "value": 1500,
                "commission": 300,
                "status": "closed",
                "date": datetime.now().isoformat()
            },
            {
                "id": "2",
                "client_name": "Fatima Zahra",
                "company": "Digital Agency",
                "deal_type": "service",
                "value": 2000,
                "commission": 400,
                "status": "closed",
                "date": (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "id": "3",
                "client_name": "Youssef Bennani",
                "company": "E-commerce Store",
                "deal_type": "product",
                "value": 800,
                "commission": 160,
                "status": "pending",
                "date": (datetime.now() - timedelta(days=5)).isoformat()
            }
        ]
        
        return {"deals": deals}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@commercial_router.get("/top-clients")
async def get_top_clients(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Top clients"""
    try:
        if current_user.get("role") != "commercial":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        clients = [
            {"name": "Tech Solutions", "deals": 5, "value": 7500},
            {"name": "Digital Agency", "deals": 4, "value": 6000},
            {"name": "E-commerce Store", "deals": 3, "value": 4500}
        ]
        
        return {"clients": clients}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# INFLUENCER ENDPOINTS
# ============================================

@influencer_router.get("/stats")
async def get_influencer_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Statistiques dashboard influenceur"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        stats = {
            "total_clicks": 1250,
            "unique_clicks": 890,
            "conversions": 45,
            "conversion_rate": 3.6,
            "commission_earned": 6750.00,
            "commission_pending": 1500.00,
            "avg_commission": 150.00,
            "top_campaign": "Summer Sale"
        }
        
        return {"stats": stats}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching influencer stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/clicks")
async def get_influencer_clicks(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Évolution des clics"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        clicks = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            clicks.append({
                "date": date,
                "clicks": 20 + (i % 15)
            })
        
        return {"clicks": clicks}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clicks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/conversions")
async def get_influencer_conversions(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Conversions et revenus"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        conversions = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            conversions.append({
                "date": date,
                "conversions": 1 + (i % 3),
                "revenue": (1 + (i % 3)) * 150
            })
        
        return {"conversions": conversions}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/campaign-performance")
async def get_campaign_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Performance par campagne"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        campaigns = [
            {"campaign": "Summer Sale", "clicks": 450, "conversions": 18},
            {"campaign": "Black Friday", "clicks": 380, "conversions": 15},
            {"campaign": "New Year", "clicks": 280, "conversions": 10},
            {"campaign": "Spring Promo", "clicks": 140, "conversions": 2}
        ]
        
        return {"campaigns": campaigns}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/product-performance")
async def get_product_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Performance par produit"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        products = [
            {"name": "Produit A", "value": 35},
            {"name": "Produit B", "value": 25},
            {"name": "Produit C", "value": 20},
            {"name": "Produit D", "value": 12},
            {"name": "Autres", "value": 8}
        ]
        
        return {"products": products}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/affiliate-links")
async def get_affiliate_links(
    current_user: Dict = Depends(get_current_user)
):
    """Liens d'affiliation"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        links = [
            {
                "id": "1",
                "campaign_name": "Summer Sale",
                "product_name": "Produit Premium",
                "link": "https://getyourshare.ma/aff/summer-2024",
                "clicks": 450,
                "conversions": 18,
                "commission": 2700
            },
            {
                "id": "2",
                "campaign_name": "Black Friday",
                "product_name": "Pack Starter",
                "link": "https://getyourshare.ma/aff/blackfriday-2024",
                "clicks": 380,
                "conversions": 15,
                "commission": 2250
            },
            {
                "id": "3",
                "campaign_name": "New Year",
                "product_name": "Service Pro",
                "link": "https://getyourshare.ma/aff/newyear-2025",
                "clicks": 280,
                "conversions": 10,
                "commission": 1500
            }
        ]
        
        return {"links": links}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching links: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@influencer_router.get("/commissions")
async def get_influencer_commissions(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
):
    """Historique commissions influenceur"""
    try:
        if current_user.get("role") != "influencer":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        history = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            history.append({
                "date": date,
                "earned": 50 + (i * 30)
            })
        
        return {"history": history}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching commissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
