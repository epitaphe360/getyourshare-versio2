"""
============================================
ADVANCED SETTINGS & EMAIL & API ENDPOINTS
GetYourShare - Configuration + Email + API
============================================
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import secrets
from auth import get_current_user, get_current_admin
from supabase_client import supabase
from utils.logger import logger

# ============================================
# SETTINGS ROUTER
# ============================================

settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SMTPConfig(BaseModel):
    smtp_config: Dict[str, Any]

class BrandingConfig(BaseModel):
    branding: Dict[str, Any]

@settings_router.get("/platform")
async def get_platform_settings(current_user: Dict = Depends(get_current_admin)):
    """Récupère les paramètres de la plateforme"""
    try:
        response = supabase.table('platform_settings').select('*').limit(1).execute()
        settings = response.data[0] if response.data else {}
        return {'settings': settings}
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        return {'settings': {}}

@settings_router.put("/smtp")
async def update_smtp_settings(
    config: SMTPConfig,
    current_user: Dict = Depends(get_current_admin)
):
    """Met à jour la configuration SMTP"""
    try:
        response = supabase.table('platform_settings')\
            .upsert({'smtp': config.smtp_config, 'updated_at': datetime.utcnow().isoformat()})\
            .execute()
        return {'success': True, 'message': 'SMTP settings updated'}
    except Exception as e:
        logger.error(f"Error updating SMTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@settings_router.put("/branding")
async def update_branding(
    config: BrandingConfig,
    current_user: Dict = Depends(get_current_admin)
):
    """Met à jour le branding"""
    try:
        response = supabase.table('platform_settings')\
            .upsert({'branding': config.branding, 'updated_at': datetime.utcnow().isoformat()})\
            .execute()
        return {'success': True, 'message': 'Branding updated'}
    except Exception as e:
        logger.error(f"Error updating branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# EMAIL MARKETING ROUTER
# ============================================

email_router = APIRouter(prefix="/api/emails", tags=["Email Marketing"])

class CampaignCreate(BaseModel):
    name: str
    subject: str
    template_id: Optional[str]
    recipients: List[str]

@email_router.get("/campaigns")
async def get_campaigns(current_user: Dict = Depends(get_current_user)):
    """Liste des campagnes email"""
    try:
        response = supabase.table('email_campaigns')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        return {'campaigns': response.data or []}
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        return {'campaigns': []}

@email_router.post("/campaigns", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Crée une campagne email"""
    try:
        data = {
            'user_id': current_user['id'],
            'name': campaign.name,
            'subject': campaign.subject,
            'template_id': campaign.template_id,
            'recipients': campaign.recipients,
            'status': 'draft',
            'created_at': datetime.utcnow().isoformat()
        }
        response = supabase.table('email_campaigns').insert(data).execute()
        return {'success': True, 'campaign': response.data[0]}
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@email_router.get("/templates")
async def get_templates(current_user: Dict = Depends(get_current_user)):
    """Liste des templates email"""
    templates = [
        {'id': '1', 'name': 'Welcome Email', 'description': 'Email de bienvenue'},
        {'id': '2', 'name': 'Newsletter', 'description': 'Newsletter mensuelle'},
        {'id': '3', 'name': 'Promotion', 'description': 'Email promotionnel'}
    ]
    return {'templates': templates}

# ============================================
# PUBLIC API ROUTER
# ============================================

api_router = APIRouter(prefix="/api/v1", tags=["Public API"])

class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str]
    permissions: Optional[Dict[str, bool]]

@api_router.get("/keys")
async def get_api_keys(current_user: Dict = Depends(get_current_user)):
    """Liste des clés API de l'utilisateur"""
    try:
        response = supabase.table('api_keys')\
            .select('id, name, key_preview, active, last_used, created_at')\
            .eq('user_id', current_user['id'])\
            .execute()
        return {'keys': response.data or []}
    except Exception as e:
        logger.error(f"Error fetching API keys: {e}")
        return {'keys': []}

@api_router.post("/keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Crée une nouvelle clé API"""
    try:
        # Générer une clé sécurisée
        api_key = f"gys_{secrets.token_urlsafe(32)}"
        key_preview = api_key[:12]
        
        data = {
            'user_id': current_user['id'],
            'name': key_data.name,
            'description': key_data.description,
            'api_key': api_key,
            'key_preview': key_preview,
            'permissions': key_data.permissions or {'read': True, 'write': False},
            'active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('api_keys').insert(data).execute()
        
        return {
            'success': True,
            'api_key': api_key,  # Retourner seulement à la création
            'key_id': response.data[0]['id']
        }
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Supprime une clé API"""
    try:
        response = supabase.table('api_keys')\
            .delete()\
            .eq('id', key_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        return {'success': True, 'message': 'API key deleted'}
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Public API endpoints (with API key authentication)
async def _verify_api_key(request: Request) -> dict:
    """Vérifie la clé API depuis header ou query param"""
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Clé API requise (header X-API-Key ou param api_key)")
    result = supabase.table("api_keys").select("*").eq("key", api_key).eq("is_active", True).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Clé API invalide ou désactivée")
    key_data = result.data[0]
    # Mettre à jour last_used_at
    supabase.table("api_keys").update({"last_used_at": datetime.utcnow().isoformat(), "usage_count": (key_data.get("usage_count") or 0) + 1}).eq("key", api_key).execute()
    return key_data


@api_router.get("/public/products")
async def public_get_products(request: Request):
    """API publique - Liste des produits"""
    await _verify_api_key(request)
    try:
        response = supabase.table('products').select('id, name, description, price, category, image_url, rating, review_count').eq('is_active', True).limit(100).execute()
        return {'products': response.data or []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return {'products': []}

@api_router.get("/public/statistics")
async def public_get_statistics(request: Request):
    """API publique - Statistiques"""
    await _verify_api_key(request)
    try:
        products_res = supabase.table('products').select('id', count='exact').eq('is_active', True).execute()
        campaigns_res = supabase.table('campaigns').select('id', count='exact').eq('status', 'active').execute()
        clicks_res = supabase.table('tracking_events').select('id', count='exact').eq('event_type', 'click').execute()
        return {
            'total_products': products_res.count or 0,
            'total_campaigns': campaigns_res.count or 0,
            'total_clicks': clicks_res.count or 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return {'total_products': 0, 'total_campaigns': 0, 'total_clicks': 0}
