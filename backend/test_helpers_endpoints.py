"""
Test Helpers Endpoints - Pour simulation et tests
Ces endpoints permettent aux admins de créer des données de test
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, validator
from typing import Optional, Dict
from datetime import datetime, timedelta
import json
import uuid

from auth import get_current_user_from_cookie
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/test", tags=["Test Helpers"])

# ============================================
# MODELS
# ============================================

class ConversionSimulate(BaseModel):
    tracking_link_id: str
    sale_amount: float
    commission_rate: Optional[float] = 10.0
    status: str = "completed"
    payment_method: str = "credit_card"
    customer_email: Optional[str] = "test@example.com"
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ['pending', 'completed', 'refunded', 'cancelled']
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @validator('sale_amount')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Amount must be positive")
        return v

class ClickSimulate(BaseModel):
    tracking_link_id: str
    ip_address: Optional[str] = "192.168.1.1"
    country: Optional[str] = "France"
    city: Optional[str] = "Paris"
    device_type: Optional[str] = "mobile"
    browser: Optional[str] = "Chrome"
    referrer: Optional[str] = None

class SubscriptionCreate(BaseModel):
    user_id: str
    plan_id: str
    status: str = "active"
    duration_days: int = 30
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ['active', 'cancelled', 'expired', 'suspended']
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

# ============================================
# ENDPOINTS
# ============================================

def require_admin(current_user: dict):
    """Helper pour vérifier que l'utilisateur est admin"""
    if not current_user or current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user

@router.post("/conversions/simulate")
async def simulate_conversion(
    data: ConversionSimulate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Simuler une conversion pour tests (ADMIN ONLY)
    
    Cette fonction crée une conversion de test avec tous les calculs :
    - Commission influenceur
    - Frais de plateforme
    - Distribution automatique des balances
    """
    require_admin(current_user)
    
    try:
        # 1. Récupérer le tracking link
        link_result = supabase.table('tracking_links').select('*').eq('id', data.tracking_link_id).execute()
        if not link_result.data:
            raise HTTPException(404, "Tracking link introuvable")
        
        link = link_result.data[0]
        
        # 2. Calculer les montants
        commission_amount = data.sale_amount * (data.commission_rate / 100)
        platform_fee = data.sale_amount * 0.02  # 2% pour la plateforme
        
        # 3. Créer la conversion
        order_id = f"TEST-ORD-{str(uuid.uuid4())[:8].upper()}"
        
        conv_data = {
            "tracking_link_id": data.tracking_link_id,
            "user_id": link['influencer_id'],
            "product_id": link.get('product_id'),
            "merchant_id": link['merchant_id'],
            "order_id": order_id,
            "sale_amount": data.sale_amount,
            "commission_amount": commission_amount,
            "platform_fee": platform_fee,
            "status": data.status,
            "currency": "EUR",
            "payment_method": data.payment_method,
            "customer_email": data.customer_email,
            "metadata": json.dumps({
                "test": True,
                "simulated": True,
                "created_by": current_user['id']
            }),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('conversions').insert(conv_data).execute()
        conversion_id = result.data[0]['id']
        
        # 4. Mettre à jour le compteur de conversions du lien
        current_conversions = link.get('conversions', 0)
        supabase.table('tracking_links').update({
            "conversions": current_conversions + 1
        }).eq('id', data.tracking_link_id).execute()
        
        # 5. Si status = completed, distribuer les balances
        if data.status == "completed":
            # Influenceur
            inf_result = supabase.table('users').select('balance').eq('id', link['influencer_id']).execute()
            if inf_result.data:
                current_balance = inf_result.data[0]['balance'] or 0.0
                supabase.table('users').update({
                    "balance": current_balance + commission_amount
                }).eq('id', link['influencer_id']).execute()
            
            # Admin (plateforme)
            admin_result = supabase.table('users').select('id, balance').eq('role', 'admin').limit(1).execute()
            if admin_result.data:
                admin_id = admin_result.data[0]['id']
                admin_balance = admin_result.data[0]['balance'] or 0.0
                supabase.table('users').update({
                    "balance": admin_balance + platform_fee
                }).eq('id', admin_id).execute()
        
        logger.info(
            "test_conversion_simulated",
            conversion_id=conversion_id,
            amount=data.sale_amount,
            commission=commission_amount
        )
        
        return {
            "success": True,
            "conversion": {
                "id": conversion_id,
                "order_id": order_id,
                "sale_amount": data.sale_amount,
                "commission_amount": commission_amount,
                "platform_fee": platform_fee,
                "status": data.status
            },
            "message": "Conversion de test créée avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("simulate_conversion_failed", error=str(e))
        raise HTTPException(500, f"Erreur lors de la simulation: {str(e)}")


@router.post("/tracking/simulate-click")
async def simulate_click(
    data: ClickSimulate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Simuler un clic sur un lien d'affiliation (ADMIN ONLY)
    
    Cette fonction :
    - Incrémente le compteur de clics
    - Crée un tracking_event avec métadonnées
    """
    require_admin(current_user)
    
    try:
        # 1. Vérifier que le lien existe
        link_result = supabase.table('tracking_links').select('clicks').eq('id', data.tracking_link_id).execute()
        if not link_result.data:
            raise HTTPException(404, "Tracking link introuvable")
        
        current_clicks = link_result.data[0]['clicks'] or 0
        
        # 2. Incrémenter les clics
        supabase.table('tracking_links').update({
            "clicks": current_clicks + 1
        }).eq('id', data.tracking_link_id).execute()
        
        # 3. Créer le tracking event
        event_data = {
            "tracking_link_id": data.tracking_link_id,
            "event_type": "click",
            "ip_address": data.ip_address,
            "user_agent": f"Mozilla/5.0 ({data.device_type}; Test)",
            "country": data.country,
            "city": data.city,
            "device_type": data.device_type,
            "browser": data.browser,
            "referrer": data.referrer,
            "event_data": json.dumps({
                "test": True,
                "simulated": True,
                "session_id": str(uuid.uuid4())
            }),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('tracking_events').insert(event_data).execute()
        event_id = result.data[0]['id']
        
        logger.info(
            "test_click_simulated",
            event_id=event_id,
            link_id=data.tracking_link_id
        )
        
        return {
            "success": True,
            "event": {
                "id": event_id,
                "tracking_link_id": data.tracking_link_id,
                "total_clicks": current_clicks + 1
            },
            "message": "Clic de test enregistré avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("simulate_click_failed", error=str(e))
        raise HTTPException(500, f"Erreur lors de la simulation: {str(e)}")


@router.post("/subscriptions/create")
async def create_subscription_manual(
    data: SubscriptionCreate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un abonnement manuellement pour tests (ADMIN ONLY)
    
    Permet de créer des abonnements sans passer par le process de paiement
    """
    require_admin(current_user)
    
    try:
        # 1. Vérifier que l'utilisateur existe
        user_result = supabase.table('users').select('id, email').eq('id', data.user_id).execute()
        if not user_result.data:
            raise HTTPException(404, "Utilisateur introuvable")
        
        # 2. Vérifier que le plan existe
        plan_result = supabase.table('plans').select('*').eq('id', data.plan_id).execute()
        if not plan_result.data:
            raise HTTPException(404, "Plan introuvable")
        
        plan = plan_result.data[0]
        
        # 3. Créer l'abonnement
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=data.duration_days)
        
        sub_data = {
            "user_id": data.user_id,
            "plan_id": data.plan_id,
            "status": data.status,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "amount": plan.get('price', 0),
            "currency": plan.get('currency', 'EUR'),
            "payment_method": "manual_test",
            "metadata": json.dumps({
                "test": True,
                "created_by": current_user['id'],
                "manual": True
            })
        }
        
        result = supabase.table('subscriptions').insert(sub_data).execute()
        subscription_id = result.data[0]['id']
        
        logger.info(
            "test_subscription_created",
            subscription_id=subscription_id,
            user_id=data.user_id,
            plan_id=data.plan_id
        )
        
        return {
            "success": True,
            "subscription": {
                "id": subscription_id,
                "user_id": data.user_id,
                "plan_id": data.plan_id,
                "status": data.status,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "message": "Abonnement de test créé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_subscription_manual_failed", error=str(e))
        raise HTTPException(500, f"Erreur lors de la création: {str(e)}")


@router.delete("/cleanup")
async def cleanup_test_data(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Nettoyer toutes les données de test (ADMIN ONLY)
    
    Supprime les conversions, events, abonnements marqués comme "test"
    """
    require_admin(current_user)
    
    try:
        deleted_counts = {}
        
        # Supprimer les conversions de test
        conv_result = supabase.rpc('delete_test_conversions').execute()
        deleted_counts['conversions'] = conv_result.data if conv_result.data else 0
        
        # Supprimer les tracking events de test
        events_result = supabase.rpc('delete_test_tracking_events').execute()
        deleted_counts['tracking_events'] = events_result.data if events_result.data else 0
        
        # Supprimer les abonnements de test
        subs_result = supabase.rpc('delete_test_subscriptions').execute()
        deleted_counts['subscriptions'] = subs_result.data if subs_result.data else 0
        
        logger.info("test_data_cleaned", counts=deleted_counts)
        
        return {
            "success": True,
            "deleted": deleted_counts,
            "message": "Données de test nettoyées avec succès"
        }
        
    except Exception as e:
        logger.error("cleanup_test_data_failed", error=str(e))
        raise HTTPException(500, f"Erreur lors du nettoyage: {str(e)}")
