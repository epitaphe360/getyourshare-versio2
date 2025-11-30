"""
============================================
COUPON MANAGEMENT ENDPOINTS
Système de gestion des coupons promotionnels
============================================
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from auth import get_current_admin
from supabase_client import supabase
from utils.logger import logger
import secrets
import string

router = APIRouter(prefix="/api/coupons", tags=["Coupons"])

# ============================================
# MODELS
# ============================================

class CouponCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    type: str = Field(..., pattern="^(percentage|fixed|trial_extension|free_upgrade)$")
    value: float = Field(..., gt=0)  # Pourcentage ou montant fixe
    duration_type: str = Field(..., pattern="^(once|repeating|forever)$")
    duration_months: Optional[int] = Field(None, ge=1, le=12)
    max_redemptions: Optional[int] = Field(None, ge=1)
    max_redemptions_per_user: int = Field(1, ge=1)
    valid_from: datetime
    valid_until: Optional[datetime] = None
    eligible_plans: Optional[List[str]] = None  # Liste de codes de plans
    new_customers_only: bool = False
    description: Optional[str] = None

class CouponUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_redemptions: Optional[int] = None
    valid_until: Optional[datetime] = None
    description: Optional[str] = None

class CouponValidate(BaseModel):
    code: str
    user_id: str
    plan_code: Optional[str] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_coupon_code(length=8):
    """Générer un code coupon aléatoire"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

async def check_coupon_validity(coupon_data: dict, user_id: str, plan_code: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """Vérifier la validité d'un coupon"""
    
    # 1. Vérifier si actif
    if not coupon_data.get("is_active"):
        return False, "Coupon désactivé"
    
    # 2. Vérifier les dates
    now = datetime.utcnow()
    valid_from = datetime.fromisoformat(coupon_data["valid_from"].replace("Z", "+00:00"))
    
    if now < valid_from:
        return False, "Coupon pas encore valide"
    
    if coupon_data.get("valid_until"):
        valid_until = datetime.fromisoformat(coupon_data["valid_until"].replace("Z", "+00:00"))
        if now > valid_until:
            return False, "Coupon expiré"
    
    # 3. Vérifier le nombre total d'utilisations
    if coupon_data.get("max_redemptions"):
        current_redemptions = coupon_data.get("redemption_count", 0)
        if current_redemptions >= coupon_data["max_redemptions"]:
            return False, "Coupon épuisé (limite atteinte)"
    
    # 4. Vérifier les utilisations par utilisateur
    redemptions_res = supabase.table("coupon_redemptions").select("id").eq("coupon_id", coupon_data["id"]).eq("user_id", user_id).execute()
    user_redemptions = len(redemptions_res.data) if redemptions_res.data else 0
    
    if user_redemptions >= coupon_data.get("max_redemptions_per_user", 1):
        return False, "Vous avez déjà utilisé ce coupon"
    
    # 5. Vérifier si réservé aux nouveaux clients
    if coupon_data.get("new_customers_only"):
        subs_res = supabase.table("subscriptions").select("id").eq("user_id", user_id).execute()
        if subs_res.data and len(subs_res.data) > 0:
            return False, "Coupon réservé aux nouveaux clients"
    
    # 6. Vérifier les plans éligibles
    if coupon_data.get("eligible_plans") and plan_code:
        eligible_plans = coupon_data["eligible_plans"]
        if isinstance(eligible_plans, str):
            # Si stocké comme string JSON
            import json
            eligible_plans = json.loads(eligible_plans)
        if plan_code not in eligible_plans:
            return False, f"Coupon non valide pour le plan {plan_code}"
    
    return True, None

# ============================================
# ENDPOINTS
# ============================================

@router.post("/admin/create", dependencies=[Depends(get_current_admin)])
async def create_coupon(coupon: CouponCreate):
    """[ADMIN] Créer un nouveau coupon"""
    try:
        # Vérifier si le code existe déjà
        existing = supabase.table("coupons").select("id").eq("code", coupon.code.upper()).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Ce code coupon existe déjà")
        
        # Créer le coupon
        coupon_data = {
            "code": coupon.code.upper(),
            "type": coupon.type,
            "value": coupon.value,
            "duration_type": coupon.duration_type,
            "duration_months": coupon.duration_months,
            "max_redemptions": coupon.max_redemptions,
            "max_redemptions_per_user": coupon.max_redemptions_per_user,
            "redemption_count": 0,
            "valid_from": coupon.valid_from.isoformat(),
            "valid_until": coupon.valid_until.isoformat() if coupon.valid_until else None,
            "eligible_plans": coupon.eligible_plans,
            "new_customers_only": coupon.new_customers_only,
            "description": coupon.description,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("coupons").insert(coupon_data).execute()
        
        return {
            "success": True,
            "message": f"Coupon {coupon.code} créé avec succès",
            "coupon": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/all", dependencies=[Depends(get_current_admin)])
async def get_all_coupons(active_only: bool = False):
    """[ADMIN] Récupérer tous les coupons"""
    try:
        query = supabase.table("coupons").select("*")
        
        if active_only:
            query = query.eq("is_active", True)
        
        result = query.order("created_at", desc=True).execute()
        
        # Calculer les stats pour chaque coupon
        coupons = []
        for coupon in result.data if result.data else []:
            # Récupérer les utilisations
            redemptions_res = supabase.table("coupon_redemptions").select("*").eq("coupon_id", coupon["id"]).execute()
            redemptions = redemptions_res.data if redemptions_res.data else []
            
            # Calculer le revenu généré (si applicable)
            revenue_generated = 0
            for redemption in redemptions:
                if redemption.get("subscription_amount"):
                    revenue_generated += redemption["subscription_amount"]
            
            coupon["stats"] = {
                "redemptions": len(redemptions),
                "unique_users": len(set(r["user_id"] for r in redemptions)),
                "revenue_generated": revenue_generated,
                "discount_given": sum(r.get("discount_amount", 0) for r in redemptions)
            }
            
            coupons.append(coupon)
        
        return {"success": True, "coupons": coupons}
    except Exception as e:
        logger.error(f"Error fetching coupons: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/{coupon_id}", dependencies=[Depends(get_current_admin)])
async def get_coupon_details(coupon_id: str):
    """[ADMIN] Détails d'un coupon avec historique d'utilisation"""
    try:
        # Récupérer le coupon
        coupon_res = supabase.table("coupons").select("*").eq("id", coupon_id).single().execute()
        if not coupon_res.data:
            raise HTTPException(status_code=404, detail="Coupon non trouvé")
        
        coupon = coupon_res.data
        
        # Récupérer les utilisations avec détails utilisateurs
        redemptions_res = supabase.table("coupon_redemptions").select("*, users(email, full_name)").eq("coupon_id", coupon_id).order("redeemed_at", desc=True).execute()
        
        return {
            "success": True,
            "coupon": coupon,
            "redemptions": redemptions_res.data if redemptions_res.data else []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching coupon details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/admin/{coupon_id}", dependencies=[Depends(get_current_admin)])
async def update_coupon(coupon_id: str, update: CouponUpdate):
    """[ADMIN] Mettre à jour un coupon"""
    try:
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        
        if "valid_until" in update_data and update_data["valid_until"]:
            update_data["valid_until"] = update_data["valid_until"].isoformat()
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.table("coupons").update(update_data).eq("id", coupon_id).execute()
        
        return {
            "success": True,
            "message": "Coupon mis à jour",
            "coupon": result.data[0] if result.data else None
        }
    except Exception as e:
        logger.error(f"Error updating coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/{coupon_id}", dependencies=[Depends(get_current_admin)])
async def delete_coupon(coupon_id: str):
    """[ADMIN] Supprimer un coupon (soft delete)"""
    try:
        # Désactiver plutôt que supprimer (pour conserver l'historique)
        supabase.table("coupons").update({
            "is_active": False,
            "deleted_at": datetime.utcnow().isoformat()
        }).eq("id", coupon_id).execute()
        
        return {"success": True, "message": "Coupon supprimé"}
    except Exception as e:
        logger.error(f"Error deleting coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_coupon(validation: CouponValidate):
    """Valider un code coupon pour un utilisateur"""
    try:
        # Récupérer le coupon
        coupon_res = supabase.table("coupons").select("*").eq("code", validation.code.upper()).single().execute()
        if not coupon_res.data:
            return {"valid": False, "message": "Code coupon invalide"}
        
        coupon = coupon_res.data
        
        # Vérifier la validité
        is_valid, error_message = await check_coupon_validity(coupon, validation.user_id, validation.plan_code)
        
        if not is_valid:
            return {"valid": False, "message": error_message}
        
        return {
            "valid": True,
            "coupon": {
                "code": coupon["code"],
                "type": coupon["type"],
                "value": coupon["value"],
                "duration_type": coupon["duration_type"],
                "duration_months": coupon.get("duration_months"),
                "description": coupon.get("description")
            }
        }
    except Exception as e:
        logger.error(f"Error validating coupon: {e}")
        return {"valid": False, "message": "Erreur lors de la validation"}

@router.post("/apply")
async def apply_coupon(validation: CouponValidate):
    """Appliquer un coupon à une souscription (enregistrer l'utilisation)"""
    try:
        # Valider d'abord
        coupon_res = supabase.table("coupons").select("*").eq("code", validation.code.upper()).single().execute()
        if not coupon_res.data:
            raise HTTPException(status_code=404, detail="Coupon non trouvé")
        
        coupon = coupon_res.data
        is_valid, error_message = await check_coupon_validity(coupon, validation.user_id, validation.plan_code)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Enregistrer l'utilisation
        redemption_data = {
            "coupon_id": coupon["id"],
            "coupon_code": coupon["code"],
            "user_id": validation.user_id,
            "redeemed_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("coupon_redemptions").insert(redemption_data).execute()
        
        # Incrémenter le compteur
        supabase.table("coupons").update({
            "redemption_count": coupon.get("redemption_count", 0) + 1
        }).eq("id", coupon["id"]).execute()
        
        return {
            "success": True,
            "message": f"Coupon {coupon['code']} appliqué avec succès",
            "discount": {
                "type": coupon["type"],
                "value": coupon["value"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/stats", dependencies=[Depends(get_current_admin)])
async def get_coupon_stats():
    """[ADMIN] Statistiques globales des coupons"""
    try:
        # Tous les coupons
        coupons_res = supabase.table("coupons").select("*").execute()
        all_coupons = coupons_res.data if coupons_res.data else []
        
        # Toutes les utilisations
        redemptions_res = supabase.table("coupon_redemptions").select("*").execute()
        all_redemptions = redemptions_res.data if redemptions_res.data else []
        
        # Calculer les stats
        active_coupons = len([c for c in all_coupons if c.get("is_active")])
        total_redemptions = len(all_redemptions)
        unique_users = len(set(r["user_id"] for r in all_redemptions))
        
        # Revenus et remises
        total_discount = sum(r.get("discount_amount", 0) for r in all_redemptions)
        total_revenue = sum(r.get("subscription_amount", 0) for r in all_redemptions)
        
        # Top coupons par utilisation
        coupon_usage = {}
        for redemption in all_redemptions:
            code = redemption.get("coupon_code", "Unknown")
            coupon_usage[code] = coupon_usage.get(code, 0) + 1
        
        top_coupons = sorted(coupon_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "success": True,
            "stats": {
                "total_coupons": len(all_coupons),
                "active_coupons": active_coupons,
                "total_redemptions": total_redemptions,
                "unique_users": unique_users,
                "total_discount_given": total_discount,
                "total_revenue_generated": total_revenue,
                "top_coupons": [{"code": code, "redemptions": count} for code, count in top_coupons]
            }
        }
    except Exception as e:
        logger.error(f"Error fetching coupon stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
