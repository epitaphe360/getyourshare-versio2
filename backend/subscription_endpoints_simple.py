"""
============================================
SUBSCRIPTION ENDPOINTS - VERSION SIMPLIFIÉE
Utilise les données existantes dans merchants/influencers
============================================
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from supabase import create_client, Client
import os
from auth import get_current_user
from utils.logger import logger

# Import des helpers pour éviter la duplication de code
from subscription_helpers_simple import (
    get_user_subscription_data,
    get_merchant_limits,
    get_influencer_limits,
    get_plan_features
)

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.warning("⚠️ Warning: Supabase credentials not configured")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# PYDANTIC MODELS POUR VALIDATION
# ============================================

class CheckLimitRequest(BaseModel):
    """Modèle pour vérifier une limite"""
    limit_type: str
    
    @validator('limit_type')
    def validate_limit_type(cls, v):
        valid_types = ['products', 'campaigns', 'affiliates', 'links']
        if v not in valid_types:
            raise ValueError(f"Invalid limit_type. Must be one of: {', '.join(valid_types)}")
        return v

class UpgradeRequest(BaseModel):
    """Modèle pour upgrade de plan"""
    new_plan: str
    
    @validator('new_plan')
    def validate_plan(cls, v):
        valid_plans = ['free', 'starter', 'pro', 'enterprise', 'elite']
        if v not in valid_plans:
            raise ValueError(f"Invalid plan: {v}. Must be one of: {', '.join(valid_plans)}")
        return v

class CancelRequest(BaseModel):
    """Modèle pour annulation"""
    reason: Optional[str] = None
    feedback: Optional[str] = None

# ============================================
# NOTE: Helper functions déplacées dans subscription_helpers_simple.py
# pour éviter les imports circulaires
# ============================================

# ============================================
# ENDPOINTS
# ============================================

@router.get("/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """
    Récupère l'abonnement actuel de l'utilisateur
    Compatible avec les dashboards existants
    """
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        if not user_id or not user_role:
            raise HTTPException(status_code=400, detail="Invalid user data")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            # Retourner un plan par défaut si pas trouvé
            return {
                "plan_name": "Free" if user_role == "merchant" else "Starter",
                "plan_code": "free" if user_role == "merchant" else "starter",
                "type": user_role,
                "status": "active",
                "monthly_fee": 0,
                "features": [],
                "limits": get_merchant_limits("free") if user_role == "merchant" else get_influencer_limits("starter"),
                "usage": {}
            }
        
        # Ajouter les features
        subscription_data["features"] = get_plan_features(
            subscription_data["plan_code"],
            subscription_data["type"]
        )
        
        return subscription_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching subscription: {str(e)}")

@router.get("/plans")
async def get_available_plans():
    """Liste tous les plans disponibles"""
    try:
        if not supabase:
            # Retourner des plans mockés si Supabase n'est pas configuré
            return {
                "merchants": [
                    {"name": "Free", "code": "free", "price": 0, "commission": 5},
                    {"name": "Starter", "code": "starter", "price": 299, "commission": 4},
                    {"name": "Pro", "code": "pro", "price": 799, "commission": 3},
                    {"name": "Enterprise", "code": "enterprise", "price": 1999, "commission": 2}
                ],
                "influencers": [
                    {"name": "Starter", "code": "starter", "price": 0, "fee": 5},
                    {"name": "Pro", "code": "pro", "price": 99, "fee": 3},
                    {"name": "Elite", "code": "elite", "price": 299, "fee": 2}
                ]
            }
        
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("is_active", True) \
            .order("display_order") \
            .execute()
        
        plans = response.data or []
        
        # Grouper par type
        merchants = [p for p in plans if p["type"] == "merchant"]
        influencers = [p for p in plans if p["type"] == "influencer"]
        
        return {
            "merchants": merchants,
            "influencers": influencers
        }
        
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/usage")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques d'utilisation vs limites"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            return {
                "error": "No subscription found"
            }
        
        limits = subscription_data.get("limits", {})
        usage = subscription_data.get("usage", {})
        
        result = {
            "plan_name": subscription_data["plan_name"],
            "plan_code": subscription_data["plan_code"]
        }
        
        # Ajouter les stats d'utilisation
        for key, limit in limits.items():
            if key.endswith("_rate"):
                continue  # Skip rate fields
            
            current = usage.get(key, 0)
            result[key] = {
                "current": current,
                "limit": limit,
                "available": None if limit is None else (limit - current),
                "can_add": True if limit is None else (current < limit),
                "percentage": 0 if limit is None or limit == 0 else round((current / limit) * 100, 1)
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/check-limit")
async def check_limit(
    request: CheckLimitRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Vérifie si l'utilisateur peut ajouter un élément (BUG 4 CORRIGÉ: validation avec Pydantic)"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            return {"allowed": False, "reason": "No active subscription"}
        
        limits = subscription_data.get("limits", {})
        usage = subscription_data.get("usage", {})
        
        limit = limits.get(request.limit_type)
        current = usage.get(request.limit_type, 0)
        
        if limit is None:  # Illimité
            return {
                "allowed": True,
                "reason": "Unlimited",
                "current": current,
                "limit": None
            }
        
        allowed = current < limit
        
        return {
            "allowed": allowed,
            "reason": "Limit reached" if not allowed else "OK",
            "current": current,
            "limit": limit,
            "remaining": limit - current
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking limit: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============================================
# ENDPOINTS MOCK POUR UPGRADE/CANCEL
# ============================================

@router.post("/upgrade")
async def upgrade_plan(
    request: UpgradeRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Placeholder pour upgrade de plan (BUG 5 CORRIGÉ: validation du plan)"""
    user_role = current_user.get("role")
    
    # Vérifier si le plan est approprié pour le rôle
    merchant_plans = ['free', 'starter', 'pro', 'enterprise']
    influencer_plans = ['starter', 'pro', 'elite']
    
    if user_role == "merchant" and request.new_plan not in merchant_plans:
        raise HTTPException(
            status_code=400,
            detail=f"Plan {request.new_plan} not available for merchants. Choose from: {', '.join(merchant_plans)}"
        )
    
    if user_role == "influencer" and request.new_plan not in influencer_plans:
        raise HTTPException(
            status_code=400,
            detail=f"Plan {request.new_plan} not available for influencers. Choose from: {', '.join(influencer_plans)}"
        )
    
    return {
        "success": True,
        "message": f"Upgrade vers {request.new_plan} sera disponible bientôt avec paiement CMI",
        "redirect_to_payment": True,
        "plan": request.new_plan
    }

@router.post("/cancel")
async def cancel_subscription(
    request: CancelRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Placeholder pour annulation (avec raison optionnelle)"""
    user_id = current_user.get("id")
    
    # Log de la raison d'annulation pour analytics
    if request.reason or request.feedback:
        logger.info(f"📊 Cancellation feedback from user {user_id}:")
        logger.info(f"   Reason: {request.reason}")
        logger.info(f"   Feedback: {request.feedback}")
    
    return {
        "success": True,
        "message": "L'annulation sera effective à la fin de la période en cours",
        "effective_date": "end_of_current_period"
    }
