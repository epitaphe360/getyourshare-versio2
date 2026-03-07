from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from auth import get_current_user_from_cookie
from db_helpers import (
    get_user_by_id,
    update_user
)
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api", tags=["registrations"])

# ============================================
# MODELS
# ============================================

class RegistrationUpdate(BaseModel):
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
    admin_notes: Optional[str] = None

class RequestInfo(BaseModel):
    message: str

# ============================================
# ENDPOINTS
# ============================================

@router.get("/registrations")
async def get_registrations_endpoint(
    status: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Liste toutes les inscriptions (basé sur la table users)"""
    try:
        # Vérifier permissions admin
        if current_user["role"] not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        # On récupère les utilisateurs depuis la table users
        query = supabase.table("users").select("*", count="exact")
        
        if role:
            query = query.eq("role", role)
            
        # Pagination
        offset = (page - 1) * limit
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        users = result.data or []
        total = result.count or 0
        
        # Transformer en format "registration" pour le frontend
        registrations = []
        for u in users:
            # Ignorer les admins dans la liste des demandes
            if u.get("role") in ["admin", "super_admin"]:
                continue
            
            # Déterminer le statut
            reg_status = "approved" if u.get("is_active") else "pending"
            
            # Si on a stocké le statut dans metadata, on l'utilise
            if u.get("raw_user_meta_data") and u.get("raw_user_meta_data").get("registration_status"):
                reg_status = u.get("raw_user_meta_data").get("registration_status")
            
            registrations.append({
                "id": u.get("id"),
                "created_at": u.get("created_at"),
                "updated_at": u.get("updated_at") or u.get("created_at"),
                "status": reg_status,
                "requested_role": u.get("role"),
                "email": u.get("email"),
                "full_name": u.get("full_name") or u.get("email", "").split("@")[0],
                "company_name": u.get("company_name"),
                "phone": u.get("phone"),
                "admin_notes": u.get("raw_user_meta_data", {}).get("admin_notes"),
                "rejection_reason": u.get("raw_user_meta_data", {}).get("rejection_reason")
            })
            
        # Filtrer par statut si demandé (Note: Filtering after pagination is not ideal but status is computed)
        # To do this properly, we should store status in a column.
        # For now, we filter in memory but this messes up pagination if many are filtered out.
        if status and status != "all":
            registrations = [r for r in registrations if r["status"] == status]
            
        return {
            "registrations": registrations, 
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting registrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registrations/{registration_id}/timeline")
async def get_registration_timeline_endpoint(
    registration_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupère la timeline d'une inscription"""
    try:
        if current_user["role"] not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        # Récupérer l'utilisateur
        user = get_user_by_id(registration_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Construire la timeline
        timeline = [
            {
                "date": user.get("created_at"),
                "type": "created",
                "action": "Inscription reçue",
                "note": f"Rôle demandé: {user.get('role')}",
                "status": "info"
            }
        ]
        
        # Ajouter événements basés sur le statut actuel (simulation car pas d'historique réel)
        if user.get("is_active"):
            timeline.append({
                "date": user.get("updated_at") or user.get("created_at"),
                "type": "approved",
                "action": "Inscription approuvée",
                "status": "success"
            })
        elif user.get("raw_user_meta_data", {}).get("registration_status") == "rejected":
            timeline.append({
                "date": user.get("updated_at") or user.get("created_at"),
                "type": "rejected",
                "action": "Inscription rejetée",
                "note": user.get("raw_user_meta_data", {}).get("rejection_reason"),
                "status": "error"
            })
            
        return {"timeline": timeline}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/registrations/{registration_id}")
async def update_registration_endpoint(
    registration_id: str,
    update_data: RegistrationUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour le statut d'une inscription"""
    try:
        if current_user["role"] not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Accès admin requis")
            
        user = get_user_by_id(registration_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
        updates = {}
        meta_data = user.get("raw_user_meta_data") or {}
        
        if update_data.status:
            meta_data["registration_status"] = update_data.status
            
            if update_data.status == "approved":
                updates["is_active"] = True
            elif update_data.status == "rejected":
                updates["is_active"] = False
                if update_data.rejection_reason:
                    meta_data["rejection_reason"] = update_data.rejection_reason
            elif update_data.status == "pending":
                updates["is_active"] = False
                
        if update_data.admin_notes:
            meta_data["admin_notes"] = update_data.admin_notes
            
        updates["raw_user_meta_data"] = meta_data
        
        success = update_user(registration_id, updates)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
            
        return {"success": True, "message": "Inscription mise à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating registration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/registrations/{registration_id}/request-info")
async def request_info_endpoint(
    registration_id: str,
    info_request: RequestInfo,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Demander des informations supplémentaires"""
    try:
        if current_user["role"] not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Accès admin requis")
            
        user = get_user_by_id(registration_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
        # Mettre à jour le statut
        meta_data = user.get("raw_user_meta_data") or {}
        meta_data["registration_status"] = "info_requested"
        
        update_user(registration_id, {"raw_user_meta_data": meta_data})
        
        # Envoyer email de demande d'informations
        try:
            import os, resend as _resend
            _resend.api_key = os.getenv("RESEND_API_KEY", "")
            user_email = user.get("email") or (user.get("raw_user_meta_data") or {}).get("email")
            if _resend.api_key and user_email:
                first_name = (user.get("raw_user_meta_data") or {}).get("first_name", "")
                _resend.Emails.send({
                    "from": "noreply@getyourshare.ma",
                    "to": user_email,
                    "subject": "GetYourShare - Informations supplémentaires requises",
                    "html": f"""<h2>Bonjour {first_name},</h2>
<p>Nous avons besoin d'informations supplémentaires pour traiter votre inscription.</p>
<p><strong>Message de notre équipe :</strong></p>
<blockquote>{info_request.message}</blockquote>
<p>Merci de vous connecter sur <a href='https://getyourshare.ma'>getyourshare.ma</a> pour soumettre les informations demandées.</p>"""
                })
        except Exception as email_err:
            logger.error(f"Erreur envoi email demande info: {email_err}")
        
        return {"success": True, "message": "Demande d'information envoyée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
