"""
Routes Admin Dashboard
Platform Stats, User Management, Content Moderation, System Monitoring
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


# ============================================
# MODELS
# ============================================

class UserAction(BaseModel):
    action: str  # suspend, activate, delete, verify
    reason: Optional[str] = None


class ContentModeration(BaseModel):
    content_type: str  # product, review, post, comment
    content_id: str
    action: str  # approve, reject, flag
    reason: Optional[str] = None


# ============================================
# MIDDLEWARE: ADMIN ONLY
# ============================================

def require_admin(payload: dict = Depends(get_current_user_from_cookie)):
    """Vérifier que l'utilisateur est admin"""
    role = payload.get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    return payload


# ============================================
# PLATFORM STATISTICS
# ============================================

@router.get("/stats/overview")
async def get_platform_overview(
    payload: dict = Depends(require_admin)
):
    """
    Vue d'ensemble de la plateforme
    """
    try:
        # Statistiques utilisateurs
        total_users = supabase.table('users').select('*', count='exact').execute()
        total_users_count = total_users.count if hasattr(total_users, 'count') else len(total_users.data or [])

        # Nouveaux utilisateurs (7 derniers jours)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        new_users = supabase.table('users').select('*', count='exact').gte('created_at', week_ago).execute()
        new_users_count = new_users.count if hasattr(new_users, 'count') else len(new_users.data or [])

        # Utilisateurs actifs (30 derniers jours)
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        active_conversions = supabase.table('conversions').select('influencer_id').gte('created_at', month_ago).execute()
        active_users_count = len(set(c['influencer_id'] for c in (active_conversions.data or [])))

        # Produits
        total_products = supabase.table('products').select('*', count='exact').execute()
        total_products_count = total_products.count if hasattr(total_products, 'count') else len(total_products.data or [])

        active_products = supabase.table('products').select('*', count='exact').eq('is_active', True).execute()
        active_products_count = active_products.count if hasattr(active_products, 'count') else len(active_products.data or [])

        # Conversions
        total_conversions = supabase.table('conversions').select('*', count='exact').execute()
        total_conversions_count = total_conversions.count if hasattr(total_conversions, 'count') else len(total_conversions.data or [])

        # Conversions récentes (30j)
        recent_conversions = supabase.table('conversions').select('*', count='exact').gte('created_at', month_ago).execute()
        recent_conversions_count = recent_conversions.count if hasattr(recent_conversions, 'count') else len(recent_conversions.data or [])

        # Revenue total
        all_conversions = supabase.table('conversions').select('sale_amount').execute()
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in (all_conversions.data or []))

        # Revenue récent (30j)
        recent_conv_data = supabase.table('conversions').select('sale_amount').gte('created_at', month_ago).execute()
        recent_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in (recent_conv_data.data or []))

        # Campagnes
        total_campaigns = supabase.table('campaigns').select('*', count='exact').execute()
        total_campaigns_count = total_campaigns.count if hasattr(total_campaigns, 'count') else len(total_campaigns.data or [])

        active_campaigns = supabase.table('campaigns').select('*', count='exact').eq('status', 'active').execute()
        active_campaigns_count = active_campaigns.count if hasattr(active_campaigns, 'count') else len(active_campaigns.data or [])

        return {
            "success": True,
            "users": {
                "total": total_users_count,
                "new_last_7_days": new_users_count,
                "active_last_30_days": active_users_count,
                "growth_rate": round((new_users_count / total_users_count * 100), 2) if total_users_count > 0 else 0
            },
            "products": {
                "total": total_products_count,
                "active": active_products_count,
                "inactive": total_products_count - active_products_count
            },
            "conversions": {
                "total": total_conversions_count,
                "last_30_days": recent_conversions_count,
                "conversion_rate": round((recent_conversions_count / active_users_count * 100), 2) if active_users_count > 0 else 0
            },
            "revenue": {
                "total": float(total_revenue),
                "last_30_days": float(recent_revenue),
                "avg_per_conversion": float(total_revenue / total_conversions_count) if total_conversions_count > 0 else 0
            },
            "campaigns": {
                "total": total_campaigns_count,
                "active": active_campaigns_count,
                "completed": total_campaigns_count - active_campaigns_count
            }
        }

    except Exception as e:
        logger.error(f"Error getting platform overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/revenue-trend")
async def get_revenue_trend(
    period: str = "month",  # week, month, year
    payload: dict = Depends(require_admin)
):
    """
    Tendance du revenu
    """
    try:
        # Déterminer la période
        if period == "week":
            days = 7
            format_str = "%Y-%m-%d"
        elif period == "year":
            days = 365
            format_str = "%Y-%m"
        else:  # month
            days = 30
            format_str = "%Y-%m-%d"

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Récupérer toutes les conversions de la période
        conversions = supabase.table('conversions').select('sale_amount, created_at').gte('created_at', start_date).execute()

        # Grouper par jour/mois
        revenue_by_period = {}

        for conv in (conversions.data or []):
            created_at = datetime.fromisoformat(conv['created_at'].replace('Z', '+00:00'))
            period_key = created_at.strftime(format_str)

            if period_key not in revenue_by_period:
                revenue_by_period[period_key] = {
                    'period': period_key,
                    'revenue': Decimal('0'),
                    'conversions': 0
                }

            revenue_by_period[period_key]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))
            revenue_by_period[period_key]['conversions'] += 1

        # Convertir en liste et trier
        trend = sorted(
            [
                {
                    'period': k,
                    'revenue': float(v['revenue']),
                    'conversions': v['conversions']
                }
                for k, v in revenue_by_period.items()
            ],
            key=lambda x: x['period']
        )

        return {
            "success": True,
            "period": period,
            "trend": trend,
            "total_periods": len(trend)
        }

    except Exception as e:
        logger.error(f"Error getting revenue trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# USER MANAGEMENT
# ============================================

@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    payload: dict = Depends(require_admin)
):
    """
    Liste de tous les utilisateurs
    """
    try:
        query = supabase.table('users').select('*')

        if role:
            query = query.eq('role', role)

        if status:
            query = query.eq('status', status)

        # TODO: Implémenter la recherche par email/nom

        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)

        response = query.execute()

        # Enrichir avec infos profile
        users_enriched = []
        for user in (response.data or []):
            user_id = user.get('id')

            # Récupérer profile
            try:
            profile = supabase.table('profiles').select('full_name, avatar_url').eq('user_id', user_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            # Statistiques
            conversions = supabase.table('conversions').select('*', count='exact').eq('influencer_id', user_id).execute()
            conversions_count = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])

            users_enriched.append({
                **user,
                'full_name': profile.data.get('full_name') if profile.data else None,
                'avatar_url': profile.data.get('avatar_url') if profile.data else None,
                'total_conversions': conversions_count
            })

        return {
            "success": True,
            "users": users_enriched,
            "total": len(users_enriched),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    payload: dict = Depends(require_admin)
):
    """
    Détails d'un utilisateur
    """
    try:
        # Récupérer l'utilisateur
        user = supabase.table('users').select('*').eq('id', user_id).single().execute()

        if not user.data:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Profile
        profile = supabase.table('profiles').select('*').eq('user_id', user_id).single().execute()

        # Statistiques détaillées
        conversions = supabase.table('conversions').select('*').eq('influencer_id', user_id).execute()
        conversions_count = len(conversions.data or [])
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in (conversions.data or []))

        products = supabase.table('products').select('*', count='exact').eq('merchant_id', user_id).execute()
        products_count = products.count if hasattr(products, 'count') else len(products.data or [])

        campaigns = supabase.table('campaigns').select('*', count='exact').eq('merchant_id', user_id).execute()
        campaigns_count = campaigns.count if hasattr(campaigns, 'count') else len(campaigns.data or [])

        # Activité récente
        recent_activity = supabase.table('audit_logs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()

        return {
            "success": True,
            "user": user.data,
            "profile": profile.data if profile.data else {},
            "statistics": {
                "total_conversions": conversions_count,
                "total_revenue": float(total_revenue),
                "total_products": products_count,
                "total_campaigns": campaigns_count
            },
            "recent_activity": recent_activity.data or []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/action")
async def user_action(
    user_id: str,
    action: UserAction,
    payload: dict = Depends(require_admin)
):
    """
    Actions sur un utilisateur (suspend, activate, delete, verify)
    """
    try:
        admin_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        if action.action == "suspend":
            supabase.table('users').update({
                'status': 'suspended',
                'suspended_at': datetime.now().isoformat(),
                'suspension_reason': action.reason
            }).eq('id', user_id).execute()

            message = "Utilisateur suspendu"

        elif action.action == "activate":
            supabase.table('users').update({
                'status': 'active',
                'suspended_at': None,
                'suspension_reason': None
            }).eq('id', user_id).execute()

            message = "Utilisateur activé"

        elif action.action == "delete":
            # Soft delete
            supabase.table('users').update({
                'status': 'deleted',
                'deleted_at': datetime.now().isoformat(),
                'deletion_reason': action.reason
            }).eq('id', user_id).execute()

            message = "Utilisateur supprimé"

        elif action.action == "verify":
            supabase.table('users').update({
                'verified': True,
                'verified_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()

            message = "Utilisateur vérifié"

        else:
            raise HTTPException(status_code=400, detail="Action invalide")

        # Log l'action
        supabase.table('audit_logs').insert({
            'user_id': admin_id,
            'action': f"user_{action.action}",
            'target_user_id': user_id,
            'reason': action.reason,
            'created_at': datetime.now().isoformat()
        }).execute()

        return {
            "success": True,
            "message": message,
            "action": action.action
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing user action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CONTENT MODERATION
# ============================================

@router.get("/moderation/queue")
async def get_moderation_queue(
    content_type: Optional[str] = None,
    status: str = "pending",
    limit: int = 50,
    payload: dict = Depends(require_admin)
):
    """
    File d'attente de modération
    """
    try:
        query = supabase.table('moderation_queue').select('*')

        if content_type:
            query = query.eq('content_type', content_type)

        query = query.eq('status', status).order('created_at', desc=False).limit(limit)

        response = query.execute()

        return {
            "success": True,
            "queue": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting moderation queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderation/moderate")
async def moderate_content(
    moderation: ContentModeration,
    payload: dict = Depends(require_admin)
):
    """
    Modérer du contenu
    """
    try:
        admin_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Selon le type de contenu
        if moderation.content_type == "product":
            if moderation.action == "approve":
                supabase.table('products').update({
                    'is_active': True,
                    'moderation_status': 'approved',
                    'moderated_at': datetime.now().isoformat(),
                    'moderated_by': admin_id
                }).eq('id', moderation.content_id).execute()

            elif moderation.action == "reject":
                supabase.table('products').update({
                    'is_active': False,
                    'moderation_status': 'rejected',
                    'rejection_reason': moderation.reason,
                    'moderated_at': datetime.now().isoformat(),
                    'moderated_by': admin_id
                }).eq('id', moderation.content_id).execute()

        elif moderation.content_type == "review":
            if moderation.action == "approve":
                supabase.table('reviews').update({
                    'is_visible': True,
                    'moderation_status': 'approved',
                    'moderated_at': datetime.now().isoformat()
                }).eq('id', moderation.content_id).execute()

            elif moderation.action == "reject":
                supabase.table('reviews').update({
                    'is_visible': False,
                    'moderation_status': 'rejected',
                    'rejection_reason': moderation.reason,
                    'moderated_at': datetime.now().isoformat()
                }).eq('id', moderation.content_id).execute()

        # Mettre à jour la queue de modération
        supabase.table('moderation_queue').update({
            'status': moderation.action + 'd',  # approved, rejected, flagged
            'moderated_by': admin_id,
            'moderated_at': datetime.now().isoformat(),
            'reason': moderation.reason
        }).eq('content_id', moderation.content_id).execute()

        return {
            "success": True,
            "message": f"Contenu {moderation.action}",
            "content_type": moderation.content_type,
            "content_id": moderation.content_id
        }

    except Exception as e:
        logger.error(f"Error moderating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SYSTEM MONITORING
# ============================================

@router.get("/system/health")
async def get_system_health(
    payload: dict = Depends(require_admin)
):
    """
    Santé du système
    """
    try:
        # Database status
        try:
            db_test = supabase.table('users').select('id').limit(1).execute()
            database_status = "healthy"
        except Exception as e:
            database_status = f"error: {str(e)}"

        # Vérifier les tables critiques
        tables_status = {}
        critical_tables = ['users', 'products', 'conversions', 'campaigns']

        for table in critical_tables:
            try:
                result = supabase.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data or [])
                tables_status[table] = {"status": "ok", "count": count}
            except Exception as e:
                tables_status[table] = {"status": "error", "error": str(e)}

        # Activité récente (dernière heure)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

        recent_conversions = supabase.table('conversions').select('*', count='exact').gte('created_at', one_hour_ago).execute()
        recent_conversions_count = recent_conversions.count if hasattr(recent_conversions, 'count') else len(recent_conversions.data or [])

        recent_users = supabase.table('users').select('*', count='exact').gte('created_at', one_hour_ago).execute()
        recent_users_count = recent_users.count if hasattr(recent_users, 'count') else len(recent_users.data or [])

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": database_status,
                "tables": tables_status
            },
            "activity_last_hour": {
                "new_users": recent_users_count,
                "conversions": recent_conversions_count
            },
            "overall_status": "healthy" if database_status == "healthy" else "degraded"
        }

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/logs")
async def get_system_logs(
    level: Optional[str] = None,  # info, warning, error
    limit: int = 100,
    payload: dict = Depends(require_admin)
):
    """
    Logs système
    """
    try:
        query = supabase.table('system_logs').select('*')

        if level:
            query = query.eq('level', level)

        query = query.order('created_at', desc=True).limit(limit)

        response = query.execute()

        return {
            "success": True,
            "logs": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/errors")
async def get_recent_errors(
    hours: int = 24,
    limit: int = 50,
    payload: dict = Depends(require_admin)
):
    """
    Erreurs récentes
    """
    try:
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        errors = supabase.table('error_logs').select('*').gte('created_at', start_time).order('created_at', desc=True).limit(limit).execute()

        # Grouper par type d'erreur
        error_types = {}
        for error in (errors.data or []):
            error_type = error.get('error_type', 'unknown')
            if error_type not in error_types:
                error_types[error_type] = {
                    'type': error_type,
                    'count': 0,
                    'examples': []
                }

            error_types[error_type]['count'] += 1
            if len(error_types[error_type]['examples']) < 3:
                error_types[error_type]['examples'].append(error)

        return {
            "success": True,
            "period_hours": hours,
            "total_errors": len(errors.data) if errors.data else 0,
            "errors_by_type": list(error_types.values()),
            "recent_errors": errors.data or []
        }

    except Exception as e:
        logger.error(f"Error getting recent errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AUDIT LOGS
# ============================================

@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    payload: dict = Depends(require_admin)
):
    """
    Logs d'audit
    """
    try:
        query = supabase.table('audit_logs').select('*')

        if user_id:
            query = query.eq('user_id', user_id)

        if action:
            query = query.eq('action', action)

        query = query.order('created_at', desc=True).limit(limit)

        response = query.execute()

        return {
            "success": True,
            "logs": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
