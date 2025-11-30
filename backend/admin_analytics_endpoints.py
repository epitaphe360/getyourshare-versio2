"""
============================================
ADMIN ANALYTICS ENDPOINTS
GetYourShare - Analytics Dashboard
============================================

Endpoints pour analytics avancés:
- Métriques MRR/ARR
- Croissance utilisateurs
- Analyse churn
- Distribution abonnements
- Top performers
- Prévisions revenus
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from auth import get_current_admin
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])

# ============================================
# PYDANTIC MODELS
# ============================================

class MetricsResponse(BaseModel):
    """Métriques principales"""
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    churn_rate: float
    active_users: int
    new_users: int
    revenue_growth: float

class DataPoint(BaseModel):
    """Point de données pour graphiques"""
    date: str
    value: float

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_date_range(days: int):
    """Retourne la plage de dates"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def calculate_mrr(subscriptions: List[Dict]) -> float:
    """Calcule le MRR (Monthly Recurring Revenue)"""
    mrr = 0.0
    for sub in subscriptions:
        if sub.get('status') == 'active':
            price = sub.get('price', 0) or 0
            mrr += float(price)
    return mrr

def calculate_churn_rate(total_start: int, total_end: int, cancelled: int) -> float:
    """Calcule le taux de churn"""
    if total_start == 0:
        return 0.0
    return (cancelled / total_start) * 100

# ============================================
# ENDPOINTS
# ============================================

@router.get("/metrics")
async def get_metrics(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les métriques principales du dashboard
    """
    try:
        start_date, end_date = get_date_range(days)
        prev_start_date = start_date - timedelta(days=days)

        # Récupérer les abonnements actifs
        active_subs_response = supabase.table('subscriptions')\
            .select('*, subscription_plans(price_mad, price, currency)')\
            .eq('status', 'active')\
            .execute()
        
        active_subs = active_subs_response.data or []

        # Calculer le MRR
        mrr = 0.0
        for sub in active_subs:
            plan = sub.get('subscription_plans', {})
            price = plan.get('price_mad') or plan.get('price') or 0
            mrr += float(price)

        # ARR = MRR * 12
        arr = mrr * 12

        # Utilisateurs actifs
        active_users_response = supabase.table('users')\
            .select('id', count='exact')\
            .eq('status', 'active')\
            .execute()
        active_users = active_users_response.count or 0

        # Nouveaux utilisateurs dans la période
        new_users_response = supabase.table('users')\
            .select('id', count='exact')\
            .gte('created_at', start_date.isoformat())\
            .execute()
        new_users = new_users_response.count or 0

        # Abonnements annulés dans la période
        cancelled_subs_response = supabase.table('subscriptions')\
            .select('id', count='exact')\
            .eq('status', 'cancelled')\
            .gte('updated_at', start_date.isoformat())\
            .execute()
        cancelled_count = cancelled_subs_response.count or 0

        # Taux de churn
        total_subs_start = len(active_subs) + cancelled_count
        churn_rate = calculate_churn_rate(total_subs_start, len(active_subs), cancelled_count)

        # Croissance des revenus (comparaison avec période précédente)
        prev_subs_response = supabase.table('subscriptions')\
            .select('*, subscription_plans(price_mad, price)')\
            .eq('status', 'active')\
            .lte('created_at', start_date.isoformat())\
            .execute()
        
        prev_mrr = 0.0
        for sub in (prev_subs_response.data or []):
            plan = sub.get('subscription_plans', {})
            price = plan.get('price_mad') or plan.get('price') or 0
            prev_mrr += float(price)

        revenue_growth = ((mrr - prev_mrr) / prev_mrr * 100) if prev_mrr > 0 else 0

        return {
            'metrics': MetricsResponse(
                mrr=mrr,
                arr=arr,
                churn_rate=round(churn_rate, 2),
                active_users=active_users,
                new_users=new_users,
                revenue_growth=round(revenue_growth, 2)
            )
        }

    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )

@router.get("/revenue")
async def get_revenue_data(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les données d'évolution des revenus
    """
    try:
        start_date, end_date = get_date_range(days)

        # Récupérer toutes les transactions/abonnements
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Abonnements actifs ce jour
            subs_response = supabase.table('subscriptions')\
                .select('*, subscription_plans(price_mad, price)')\
                .eq('status', 'active')\
                .lte('created_at', next_date.isoformat())\
                .execute()
            
            daily_revenue = 0.0
            for sub in (subs_response.data or []):
                plan = sub.get('subscription_plans', {})
                price = plan.get('price_mad') or plan.get('price') or 0
                # Prorata journalier (prix mensuel / 30)
                daily_revenue += float(price) / 30
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'revenue': round(daily_revenue, 2)
            })
            
            current_date = next_date

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching revenue data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue data: {str(e)}"
        )

@router.get("/users-growth")
async def get_users_growth(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les données de croissance des utilisateurs
    """
    try:
        start_date, end_date = get_date_range(days)

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Total utilisateurs créés jusqu'à cette date
            total_response = supabase.table('users')\
                .select('id', count='exact')\
                .lte('created_at', next_date.isoformat())\
                .execute()
            
            # Par rôle
            merchants_response = supabase.table('users')\
                .select('id', count='exact')\
                .eq('role', 'merchant')\
                .lte('created_at', next_date.isoformat())\
                .execute()
            
            influencers_response = supabase.table('users')\
                .select('id', count='exact')\
                .eq('role', 'influencer')\
                .lte('created_at', next_date.isoformat())\
                .execute()
            
            commercials_response = supabase.table('users')\
                .select('id', count='exact')\
                .eq('role', 'commercial')\
                .lte('created_at', next_date.isoformat())\
                .execute()
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_users': total_response.count or 0,
                'merchants': merchants_response.count or 0,
                'influencers': influencers_response.count or 0,
                'commercials': commercials_response.count or 0
            })
            
            current_date = next_date

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching users growth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users growth: {str(e)}"
        )

@router.get("/subscriptions")
async def get_subscriptions_data(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les données des abonnements
    """
    try:
        start_date, end_date = get_date_range(days)

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Nouveaux abonnements
            new_subs = supabase.table('subscriptions')\
                .select('id', count='exact')\
                .gte('created_at', current_date.isoformat())\
                .lt('created_at', next_date.isoformat())\
                .execute()
            
            # Abonnements annulés
            cancelled_subs = supabase.table('subscriptions')\
                .select('id', count='exact')\
                .eq('status', 'cancelled')\
                .gte('updated_at', current_date.isoformat())\
                .lt('updated_at', next_date.isoformat())\
                .execute()
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'new_subscriptions': new_subs.count or 0,
                'cancelled_subscriptions': cancelled_subs.count or 0
            })
            
            current_date = next_date

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching subscriptions data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscriptions data: {str(e)}"
        )

@router.get("/churn")
async def get_churn_data(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les données de churn et rétention
    """
    try:
        start_date, end_date = get_date_range(days)

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Abonnements actifs au début
            active_start = supabase.table('subscriptions')\
                .select('id', count='exact')\
                .eq('status', 'active')\
                .lte('created_at', current_date.isoformat())\
                .execute()
            
            # Annulations ce jour
            cancelled = supabase.table('subscriptions')\
                .select('id', count='exact')\
                .eq('status', 'cancelled')\
                .gte('updated_at', current_date.isoformat())\
                .lt('updated_at', next_date.isoformat())\
                .execute()
            
            total_start = active_start.count or 0
            cancelled_count = cancelled.count or 0
            
            churn_rate = calculate_churn_rate(total_start, total_start - cancelled_count, cancelled_count)
            retention_rate = 100 - churn_rate
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'churn_rate': round(churn_rate, 2),
                'retention_rate': round(retention_rate, 2)
            })
            
            current_date = next_date

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching churn data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch churn data: {str(e)}"
        )

@router.get("/plan-distribution")
async def get_plan_distribution(
    admin = Depends(get_current_admin)
):
    """
    Récupère la distribution des plans d'abonnement
    """
    try:
        # Récupérer tous les plans
        plans_response = supabase.table('subscription_plans').select('id, name').execute()
        plans = {p['id']: p['name'] for p in (plans_response.data or [])}

        # Compter les abonnements par plan
        distribution = []
        for plan_id, plan_name in plans.items():
            count_response = supabase.table('subscriptions')\
                .select('id', count='exact')\
                .eq('plan_id', plan_id)\
                .eq('status', 'active')\
                .execute()
            
            count = count_response.count or 0
            if count > 0:
                distribution.append({
                    'name': plan_name,
                    'count': count
                })

        return {'data': distribution}

    except Exception as e:
        logger.error(f"Error fetching plan distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plan distribution: {str(e)}"
        )

@router.get("/top-performers")
async def get_top_performers(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    admin = Depends(get_current_admin)
):
    """
    Récupère les meilleurs performeurs (top users)
    """
    try:
        start_date, end_date = get_date_range(days)

        # TODO: Implémenter avec une vraie table de transactions
        # Pour l'instant, retourner des données de démonstration
        performers = [
            {
                'rank': 1,
                'user_id': 'user_1',
                'user_name': 'Mohammed Alami',
                'email': 'mohammed@example.com',
                'role': 'merchant',
                'revenue': 15000.0,
                'transactions_count': 45
            },
            {
                'rank': 2,
                'user_id': 'user_2',
                'user_name': 'Fatima Zahra',
                'email': 'fatima@example.com',
                'role': 'influencer',
                'revenue': 12500.0,
                'transactions_count': 38
            },
            {
                'rank': 3,
                'user_id': 'user_3',
                'user_name': 'Youssef Bennani',
                'email': 'youssef@example.com',
                'role': 'commercial',
                'revenue': 10200.0,
                'transactions_count': 32
            }
        ]

        return {'data': performers[:limit]}

    except Exception as e:
        logger.error(f"Error fetching top performers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top performers: {str(e)}"
        )

@router.get("/revenue-by-source")
async def get_revenue_by_source(
    days: int = Query(30, ge=1, le=365),
    admin = Depends(get_current_admin)
):
    """
    Récupère les revenus par source
    """
    try:
        start_date, end_date = get_date_range(days)

        # Récupérer les abonnements actifs avec leurs plans
        subs_response = supabase.table('subscriptions')\
            .select('*, subscription_plans(name, price_mad, price, type)')\
            .eq('status', 'active')\
            .gte('created_at', start_date.isoformat())\
            .execute()

        # Grouper par type de plan
        sources = {}
        for sub in (subs_response.data or []):
            plan = sub.get('subscription_plans', {})
            plan_type = plan.get('type', 'standard')
            price = plan.get('price_mad') or plan.get('price') or 0
            
            if plan_type not in sources:
                sources[plan_type] = 0.0
            sources[plan_type] += float(price)

        # Formatter pour le PieChart
        data = [{'name': k.capitalize(), 'value': v} for k, v in sources.items()]

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching revenue by source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue by source: {str(e)}"
        )
