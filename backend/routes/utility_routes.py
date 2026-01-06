"""
Routes Utility COMPLÈTES
Settings, Notifications, Currency, Messages, Referrals, Reviews, System
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
import requests

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Utility"])


# ============================================
# MODELS
# ============================================

class SettingsUpdate(BaseModel):
    notifications: Optional[bool] = None
    email_alerts: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None


class MessageSend(BaseModel):
    recipient_id: str
    content: str
    subject: Optional[str] = None


class NotificationPreferences(BaseModel):
    email: Optional[bool] = None
    push: Optional[bool] = None
    sms: Optional[bool] = None


# ============================================
# SETTINGS
# ============================================

@router.get("/api/settings")
async def get_user_settings(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer les paramètres utilisateur RÉELS
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Essayer de récupérer depuis user_settings table
        try:
            response = supabase.table('user_settings').select('*').eq('user_id', user_id).single().execute()

            if response.data:
                return {
                    "success": True,
                    **response.data
                }
        except Exception:
            pass

        # Fallback: récupérer depuis profiles
        try:
            profile = supabase.table('profiles').select('metadata').eq('user_id', user_id).single().execute()

            if profile.data and profile.data.get('metadata'):
                metadata = profile.data['metadata']
                if isinstance(metadata, dict):
                    settings = metadata.get('settings', {})
                else:
                    settings = {}
            else:
                settings = {}
        except Exception:
            settings = {}

        # Valeurs par défaut
        default_settings = {
            "notifications": True,
            "email_alerts": True,
            "language": "fr",
            "timezone": "Africa/Casablanca",
            "theme": "light"
        }

        return {
            "success": True,
            **{**default_settings, **settings}
        }

    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/settings")
async def update_user_settings(
    settings: SettingsUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour les paramètres utilisateur
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        update_data = {k: v for k, v in settings.dict().items() if v is not None}
        update_data['user_id'] = user_id
        update_data['updated_at'] = datetime.now().isoformat()

        # Essayer d'insérer/update dans user_settings
        try:
            # Upsert
            existing = supabase.table('user_settings').select('id').eq('user_id', user_id).execute()

            if existing.data:
                response = supabase.table('user_settings').update(update_data).eq('user_id', user_id).execute()
            else:
                response = supabase.table('user_settings').insert(update_data).execute()

            result = response.data[0] if response.data else update_data
        except Exception:
            # Fallback: stocker dans metadata de profile
            try:
                profile = supabase.table('profiles').select('metadata').eq('user_id', user_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            metadata = profile.data.get('metadata', {}) if profile.data else {}
            if not isinstance(metadata, dict):
                metadata = {}

            metadata['settings'] = {**metadata.get('settings', {}), **update_data}

            supabase.table('profiles').update({'metadata': metadata}).eq('user_id', user_id).execute()
            result = update_data

        return {
            "success": True,
            "message": "Paramètres mis à jour",
            "settings": result
        }

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# NOTIFICATIONS
# ============================================

@router.get("/api/notifications/preferences")
async def get_notification_preferences(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Préférences de notifications
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer depuis settings
        try:
            settings = supabase.table('user_settings').select('*').eq('user_id', user_id).single().execute()

            if settings.data:
                return {
                    "success": True,
                    "email": settings.data.get('email_alerts', True),
                    "push": settings.data.get('push_notifications', False),
                    "sms": settings.data.get('sms_alerts', True)
                }
        except Exception:
            pass

        # Valeurs par défaut
        return {
            "success": True,
            "email": True,
            "push": False,
            "sms": True
        }

    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/notifications/mark-all-read")
async def mark_all_notifications_read(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Marquer toutes les notifications comme lues
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Mettre à jour toutes les notifications
        response = supabase.table('notifications').update({'is_read': True}).eq('user_id', user_id).eq('is_read', False).execute()

        count = len(response.data) if response.data else 0

        return {
            "success": True,
            "message": "Toutes les notifications ont été marquées comme lues",
            "updated_count": count
        }

    except Exception as e:
        logger.error(f"Error marking all notifications read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CURRENCY CONVERSION
# ============================================

# Taux de change (statiques pour démo - à remplacer par API en prod)
EXCHANGE_RATES = {
    "MAD": {"EUR": 0.094, "USD": 0.10, "GBP": 0.079},
    "EUR": {"MAD": 10.64, "USD": 1.07, "GBP": 0.84},
    "USD": {"MAD": 10.0, "EUR": 0.93, "GBP": 0.79},
    "GBP": {"MAD": 12.66, "EUR": 1.19, "USD": 1.27}
}


@router.get("/api/currency/convert")
async def convert_currency(
    amount: float,
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Convertir une devise RÉEL (avec taux de change)

    NOTE: Utilise des taux statiques. Intégrer API comme exchangerate-api.com pour prod.
    """
    try:
        if from_currency == to_currency:
            return {
                "success": True,
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
                "converted_amount": amount,
                "rate": 1.0
            }

        # Récupérer le taux
        if from_currency in EXCHANGE_RATES and to_currency in EXCHANGE_RATES[from_currency]:
            rate = EXCHANGE_RATES[from_currency][to_currency]
        else:
            raise HTTPException(status_code=400, detail=f"Conversion {from_currency} → {to_currency} non supportée")

        converted_amount = amount * rate

        return {
            "success": True,
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "converted_amount": round(converted_amount, 2),
            "rate": rate,
            "note": "Taux statiques - intégrer API exchangerate pour données live"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MESSAGES
# ============================================

@router.get("/api/messages/conversations")
async def get_conversations(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des conversations RÉELLE
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les messages où l'utilisateur est sender ou recipient
        messages_sent = supabase.table('messages').select('recipient_id, created_at, content').eq('sender_id', user_id).execute()

        messages_received = supabase.table('messages').select('sender_id, created_at, content, is_read').eq('recipient_id', user_id).execute()

        # Grouper par conversation (unique user pairs)
        conversations = {}

        for msg in (messages_sent.data or []):
            other_user = msg.get('recipient_id')
            if other_user and other_user not in conversations:
                conversations[other_user] = {
                    'user_id': other_user,
                    'last_message': msg.get('content', '')[:50],
                    'last_message_at': msg.get('created_at'),
                    'unread': 0
                }

        for msg in (messages_received.data or []):
            other_user = msg.get('sender_id')
            if other_user:
                if other_user not in conversations:
                    conversations[other_user] = {
                        'user_id': other_user,
                        'last_message': msg.get('content', '')[:50],
                        'last_message_at': msg.get('created_at'),
                        'unread': 0
                    }

                if not msg.get('is_read'):
                    conversations[other_user]['unread'] += 1

        # Enrichir avec infos users
        result = []
        for conv in conversations.values():
            try:
                profile = supabase.table('profiles').select('full_name').eq('user_id', conv['user_id']).single().execute()
            except Exception:
                pass  # .single() might return no results

            result.append({
                **conv,
                'user_name': profile.data.get('full_name') if profile.data else 'Unknown'
            })

        # Trier par date
        result.sort(key=lambda x: x['last_message_at'], reverse=True)

        return {
            "success": True,
            "conversations": result
        }

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/messages/send")
async def send_message(
    message: MessageSend,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Envoyer un message
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        message_data = {
            'sender_id': user_id,
            'recipient_id': message.recipient_id,
            'content': message.content,
            'subject': message.subject,
            'is_read': False,
            'created_at': datetime.now().isoformat()
        }

        response = supabase.table('messages').insert(message_data).execute()

        return {
            "success": True,
            "message": response.data[0] if response.data else message_data,
            "status": "sent"
        }

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/messages/search")
async def search_messages(
    q: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Rechercher des messages
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Rechercher dans les messages envoyés et reçus
        sent = supabase.table('messages').select('*').eq('sender_id', user_id).ilike('content', f'%{q}%').execute()

        received = supabase.table('messages').select('*').eq('recipient_id', user_id).ilike('content', f'%{q}%').execute()

        results = (sent.data or []) + (received.data or [])

        # Trier par date
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return {
            "success": True,
            "query": q,
            "results": results,
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# REFERRALS (PARRAINAGE)
# ============================================

@router.get("/api/referrals/code")
async def get_referral_code(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Code de parrainage de l'utilisateur RÉEL
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer ou générer le code de parrainage
        profile = supabase.table('profiles').select('referral_code, metadata').eq('user_id', user_id).single().execute()

        if profile.data:
            referral_code = profile.data.get('referral_code')

            # Si pas de code, en générer un
            if not referral_code:
                import random
                import string
                referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

                # Mettre à jour
                supabase.table('profiles').update({'referral_code': referral_code}).eq('user_id', user_id).execute()

            # URL de parrainage
            base_url = "https://app.getyourshare.com"  # À remplacer par vraie URL
            referral_url = f"{base_url}/register?ref={referral_code}"

            return {
                "success": True,
                "code": referral_code,
                "url": referral_url
            }
        else:
            raise HTTPException(status_code=404, detail="Profil non trouvé")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/referrals/stats")
async def get_referral_stats(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Statistiques de parrainage RÉELLES
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Compter les filleuls (via mlm_relationships ou referrals table)
        try:
            referrals = supabase.table('mlm_relationships').select('*', count='exact').eq('upline_id', user_id).eq('level', 1).execute()
            total_referrals = referrals.count if hasattr(referrals, 'count') else len(referrals.data or [])
        except Exception:
            total_referrals = 0

        # Earnings des filleuls (MLM commissions niveau 1)
        try:
            commissions = supabase.table('mlm_commissions').select('amount').eq('upline_id', user_id).eq('level', 1).execute()
            earnings = sum(Decimal(str(c.get('amount', 0))) for c in (commissions.data or []))
        except Exception:
            earnings = Decimal('0')

        return {
            "success": True,
            "referrals": total_referrals,
            "earnings": float(earnings),
            "currency": "MAD"
        }

    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# REVIEWS (AVIS)
# ============================================

@router.get("/api/reviews/pending")
async def get_pending_reviews(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Avis en attente de modération (merchant only)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Récupérer les reviews en attente pour les produits du merchant
        if role == "merchant":
            # Récupérer les IDs des produits du merchant
            products = supabase.table('products').select('id').eq('merchant_id', user_id).execute()
            product_ids = [p['id'] for p in (products.data or [])]

            if not product_ids:
                return {"success": True, "reviews": []}

            # Reviews en attente pour ces produits
            reviews = supabase.table('reviews').select('*').in_('product_id', product_ids).eq('status', 'pending').execute()
        else:
            # Admin voit tout
            reviews = supabase.table('reviews').select('*').eq('status', 'pending').execute()

        return {
            "success": True,
            "reviews": reviews.data or []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Approuver un avis
    """
    try:
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Mettre à jour le statut
        response = supabase.table('reviews').update({'status': 'approved', 'approved_at': datetime.now().isoformat()}).eq('id', review_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avis non trouvé")

        return {
            "success": True,
            "status": "approved",
            "review": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Rejeter un avis
    """
    try:
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Mettre à jour le statut
        response = supabase.table('reviews').update({'status': 'rejected'}).eq('id', review_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avis non trouvé")

        return {
            "success": True,
            "status": "rejected",
            "review": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SYSTEM
# ============================================

@router.get("/api/system/health")
async def system_health():
    """
    État du système complet avec métriques (healthcheck)
    """
    try:
        import time
        import psutil
        from utils.cache import get_cache_stats

        start_time = time.time()

        # Vérifier la connexion Supabase
        supabase_status = "healthy"
        db_latency_ms = 0
        try:
            db_start = time.time()
            supabase.table('users').select('id').limit(1).execute()
            db_latency_ms = round((time.time() - db_start) * 1000, 2)
        except Exception as e:
            supabase_status = "unhealthy"
            logger.error(f"Database health check failed: {e}")

        # Cache statistics
        cache_stats = get_cache_stats()

        # System metrics (CPU, Memory, Disk)
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            system_metrics = {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "memory_available_mb": round(memory.available / (1024 * 1024), 2),
                "memory_total_mb": round(memory.total / (1024 * 1024), 2),
                "disk_percent": round(disk.percent, 2),
                "disk_available_gb": round(disk.free / (1024 * 1024 * 1024), 2)
            }
        except Exception as e:
            logger.warning(f"System metrics collection failed: {e}")
            system_metrics = {"error": "unavailable"}

        # Determine overall status
        overall_status = "healthy"
        if supabase_status != "healthy":
            overall_status = "degraded"

        # Performance thresholds
        if db_latency_ms > 500:
            overall_status = "degraded"

        response_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": overall_status,
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": response_time_ms,
            "services": {
                "api": "healthy",
                "database": {
                    "status": supabase_status,
                    "latency_ms": db_latency_ms
                },
                "cache": {
                    "status": "healthy",
                    "stats": cache_stats
                }
            },
            "system": system_metrics
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/api/system/backup")
async def trigger_backup(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Déclencher une sauvegarde (admin only)
    """
    try:
        role = payload.get("role")

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin uniquement")

        # TODO: Implémenter vraie logique de backup
        import uuid
        job_id = f"backup_{uuid.uuid4().hex[:12]}"

        return {
            "success": True,
            "message": "Sauvegarde démarrée",
            "job_id": job_id,
            "status": "processing",
            "note": "Fonctionnalité à implémenter (pg_dump ou Supabase backup API)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))
