from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from auth import get_current_user_from_cookie, get_optional_user_from_cookie
from db_helpers import (
    get_all_services,
    get_service_by_id,
    update_service,
    delete_service,
    create_service,
    get_merchant_by_user_id,
    get_leads_by_service
)
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api", tags=["services"])

# ============================================
# MODELS
# ============================================

class ServiceUpdate(BaseModel):
    is_active: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    budget_total: Optional[float] = None
    category_id: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@router.get("/categories")
async def get_categories_endpoint():
    """Liste toutes les catégories de services"""
    try:
        result = supabase.table("categories").select("*").order("name").execute()
        categories = result.data or []
        return {"categories": categories, "total": len(categories)}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return {"categories": [], "total": 0}

@router.get("/services")
async def get_services_endpoint(
    category: Optional[str] = None, 
    merchant_id: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_optional_user_from_cookie)
):
    """Liste tous les services avec filtres optionnels"""
    try:
        user = current_user
        
        # Construire la requête avec jointures
        # Note: db_helpers.get_all_services exists but server.py had custom logic with joins
        # We will reproduce server.py logic here for compatibility
        
        query = supabase.table("services").select("""
            *,
            users!services_merchant_id_fkey(id, email, full_name, company_name)
        """)
        
        # Si merchant, filtrer par ses propres services (sauf si admin)
        if user and user.get("role") == "merchant" and not merchant_id:
            query = query.eq("merchant_id", user["id"])
        elif merchant_id:
            query = query.eq("merchant_id", merchant_id)
        
        if category:
            query = query.eq("category", category)
        
        # Filtrer services actifs pour non-admin
        if not user or user.get("role") not in ["admin", "super_admin"]:
            query = query.eq("is_active", True)
        
        result = query.order("created_at", desc=True).execute()
        
        services = result.data or []
        
        # Enrichir avec le nombre de leads pour chaque service
        for service in services:
            leads_count = supabase.table("service_leads").select("id", count="exact").eq("service_id", service["id"]).execute()
            service["leads_count"] = leads_count.count if leads_count.count is not None else 0
            
            # Renommer le merchant pour uniformité
            if "users" in service:
                service["merchant"] = service.pop("users")
        
        return {"services": services, "total": len(services)}
        
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        return {"services": [], "total": 0}

@router.get("/services/{service_id}")
async def get_service_endpoint(service_id: str):
    """Récupère les détails d'un service"""
    try:
        result = supabase.table("services").select("""
            *,
            users!services_merchant_id_fkey(id, email, full_name, company_name)
        """).eq("id", service_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        service = result.data[0]
        
        # Enrichir avec le nombre de leads
        leads_count = supabase.table("service_leads").select("id", count="exact").eq("service_id", service_id).execute()
        service["leads_count"] = leads_count.count if leads_count.count is not None else 0
        
        # Renommer le merchant
        if "users" in service:
            service["merchant"] = service.pop("users")
        
        return service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}/leads")
async def get_service_leads_endpoint(
    service_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Récupère tous les leads d'un service spécifique"""
    try:
        # Vérifier que le service existe
        service_result = supabase.table("services").select("*").eq("id", service_id).execute()
        if not service_result.data:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        service = service_result.data[0]
        
        # Vérifier les permissions
        if current_user["role"] not in ["admin", "super_admin"]:
            if current_user["role"] == "merchant" and service.get("merchant_id") != current_user["id"]:
                raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Récupérer les leads
        result = supabase.table("service_leads").select("*").eq("service_id", service_id).order("created_at", desc=True).execute()
        
        leads = result.data or []
        return {"leads": leads, "total": len(leads)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/services/{service_id}")
async def update_service_endpoint(
    service_id: str,
    service_data: ServiceUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour un service (PATCH)"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
            
        # Vérifier l'existence
        existing_service = get_service_by_id(service_id)
        if not existing_service:
            raise HTTPException(status_code=404, detail="Service introuvable")
            
        # Vérifier droits merchant
        if current_user.get("role") == "merchant" and existing_service.get("merchant_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
            
        # Update
        update_data = {k: v for k, v in service_data.dict().items() if v is not None}
        
        success = update_service(service_id, update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
            
        return {"success": True, "message": "Service mis à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))
