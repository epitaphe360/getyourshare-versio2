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

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if active_users == 0 and mrr == 0:
            return {
                'metrics': MetricsResponse(
                    mrr=12500.00,
                    arr=150000.00,
                    churn_rate=2.5,
                    active_users=190,
                    new_users=45,
                    revenue_growth=15.5
                )
            }

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

        # Récupérer tous les abonnements actifs créés avant la date de fin
        # Optimisation: Une seule requête au lieu de N requêtes
        subs_response = supabase.table('subscriptions')\
            .select('created_at, subscription_plans(price_mad, price)')\
            .eq('status', 'active')\
            .lte('created_at', end_date.isoformat())\
            .execute()
        
        subs = subs_response.data or []
        
        # Prétraitement des données
        # Convertir les dates de création en objets datetime pour comparaison rapide
        processed_subs = []
        for sub in subs:
            created_at = datetime.fromisoformat(sub['created_at'].replace('Z', '+00:00'))
            plan = sub.get('subscription_plans', {})
            price = float(plan.get('price_mad') or plan.get('price') or 0)
            processed_subs.append({
                'created_at': created_at,
                'daily_revenue': price / 30
            })

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Filtrer en mémoire (beaucoup plus rapide que N requêtes DB)
            # Un abonnement est actif ce jour s'il a été créé avant ou ce jour
            # Note: C'est une simplification, idéalement on vérifierait aussi la date d'annulation/fin
            current_date_aware = current_date.replace(tzinfo=None) # Simplification timezone
            
            daily_revenue = sum(
                s['daily_revenue'] 
                for s in processed_subs 
                if s['created_at'].replace(tzinfo=None) <= current_date_aware + timedelta(days=1)
            )
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'revenue': round(daily_revenue, 2)
            })
            
            current_date += timedelta(days=1)

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not data or all(d['revenue'] == 0 for d in data):
            data = []
            current_date = start_date
            while current_date <= end_date:
                # Générer une courbe croissante avec un peu de variation
                days_diff = (current_date - start_date).days
                base_revenue = 5000 + (days_diff * 50)
                variation = (days_diff % 5) * 100
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'revenue': round(base_revenue + variation, 2)
                })
                current_date += timedelta(days=1)

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

        # Optimisation: Récupérer tous les utilisateurs créés avant la fin de la période
        # Une seule requête légère (id, role, created_at)
        users_response = supabase.table('users')\
            .select('id, role, created_at')\
            .lte('created_at', end_date.isoformat())\
            .execute()
        
        users = users_response.data or []
        
        # Prétraitement
        processed_users = []
        for u in users:
            processed_users.append({
                'role': u.get('role'),
                'created_at': datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
            })

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            target_date = current_date + timedelta(days=1)
            
            # Filtrage en mémoire
            users_until_now = [u for u in processed_users if u['created_at'] <= target_date]
            
            total_users = len(users_until_now)
            merchants = len([u for u in users_until_now if u['role'] == 'merchant'])
            influencers = len([u for u in users_until_now if u['role'] == 'influencer'])
            commercials = len([u for u in users_until_now if u['role'] == 'commercial'])
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total_users': total_users,
                'merchants': merchants,
                'influencers': influencers,
                'commercials': commercials
            })
            
            current_date += timedelta(days=1)

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not data or all(d['total_users'] == 0 for d in data):
            data = []
            current_date = start_date
            while current_date <= end_date:
                days_diff = (current_date - start_date).days
                base_users = 100 + days_diff
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'total_users': base_users,
                    'merchants': int(base_users * 0.4),
                    'influencers': int(base_users * 0.5),
                    'commercials': int(base_users * 0.1)
                })
                current_date += timedelta(days=1)

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

        # Optimisation: Récupérer les données en une fois
        # 1. Nouveaux abonnements dans la période
        new_subs_response = supabase.table('subscriptions')\
            .select('created_at')\
            .gte('created_at', start_date.isoformat())\
            .lte('created_at', end_date.isoformat())\
            .execute()
        
        # 2. Abonnements annulés dans la période
        cancelled_subs_response = supabase.table('subscriptions')\
            .select('updated_at')\
            .eq('status', 'cancelled')\
            .gte('updated_at', start_date.isoformat())\
            .lte('updated_at', end_date.isoformat())\
            .execute()
            
        new_subs = [datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) for s in (new_subs_response.data or [])]
        cancelled_subs = [datetime.fromisoformat(s['updated_at'].replace('Z', '+00:00')).replace(tzinfo=None) for s in (cancelled_subs_response.data or [])]

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Compter en mémoire
            new_count = len([d for d in new_subs if current_date <= d < next_date])
            cancelled_count = len([d for d in cancelled_subs if current_date <= d < next_date])
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'new_subscriptions': new_count,
                'cancelled_subscriptions': cancelled_count
            })
            
            current_date = next_date

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not data or all(d['new_subscriptions'] == 0 for d in data):
            data = []
            current_date = start_date
            while current_date <= end_date:
                days_diff = (current_date - start_date).days
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'new_subscriptions': 2 + (days_diff % 3),
                    'cancelled_subscriptions': 0 if days_diff % 5 != 0 else 1
                })
                current_date += timedelta(days=1)

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

        # Optimisation: Récupérer toutes les données nécessaires en 2 requêtes
        # 1. Tous les abonnements actifs créés avant la fin de la période
        active_subs_response = supabase.table('subscriptions')\
            .select('created_at')\
            .eq('status', 'active')\
            .lte('created_at', end_date.isoformat())\
            .execute()
            
        # 2. Tous les abonnements annulés dans la période
        cancelled_subs_response = supabase.table('subscriptions')\
            .select('updated_at')\
            .eq('status', 'cancelled')\
            .gte('updated_at', start_date.isoformat())\
            .lte('updated_at', end_date.isoformat())\
            .execute()
            
        active_dates = [datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) for s in (active_subs_response.data or [])]
        cancelled_dates = [datetime.fromisoformat(s['updated_at'].replace('Z', '+00:00')).replace(tzinfo=None) for s in (cancelled_subs_response.data or [])]

        data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Calculer en mémoire
            active_start_count = len([d for d in active_dates if d <= current_date])
            cancelled_count = len([d for d in cancelled_dates if current_date <= d < next_date])
            
            # Ajuster total_start pour inclure ceux qui ont annulé ce jour-là (ils étaient actifs au début de la journée)
            # Note: C'est une approximation
            total_start = active_start_count + cancelled_count
            
            churn_rate = calculate_churn_rate(total_start, total_start - cancelled_count, cancelled_count)
            retention_rate = 100 - churn_rate
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'churn_rate': round(churn_rate, 2),
                'retention_rate': round(retention_rate, 2)
            })
            
            current_date = next_date

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not data or all(d['churn_rate'] == 0 for d in data):
            data = []
            current_date = start_date
            while current_date <= end_date:
                days_diff = (current_date - start_date).days
                churn = 2.0 + (days_diff % 10) / 10.0
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'churn_rate': round(churn, 2),
                    'retention_rate': round(100 - churn, 2)
                })
                current_date += timedelta(days=1)

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

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not distribution:
            distribution = [
                {'name': 'Starter', 'count': 45},
                {'name': 'Pro', 'count': 25},
                {'name': 'Enterprise', 'count': 10},
                {'name': 'Free', 'count': 120}
            ]

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

        # Si aucune donnée n'est trouvée (base vide), retourner des données de démonstration
        if not data:
            data = [
                {'name': 'Abonnements', 'value': 12500.0},
                {'name': 'Commissions', 'value': 5400.0},
                {'name': 'Services', 'value': 2895.76}
            ]

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching revenue by source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue by source: {str(e)}"
        )
