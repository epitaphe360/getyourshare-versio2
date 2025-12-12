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
    total_revenue: float = 0.0
    total_transactions: int = 0

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

        # Récupérer les abonnements actifs (sans jointure)
        active_subs_response = supabase.table('subscriptions')\
            .select('id, plan_id, status')\
            .eq('is_active', True)\
            .execute()
        
        active_subs = active_subs_response.data or []
        
        # Récupérer les plans séparément
        plans_response = supabase.table('subscription_plans')\
            .select('id, price_mad, price')\
            .execute()
        plans_dict = {p['id']: p for p in (plans_response.data or [])}

        # Calculer le MRR
        mrr = 0.0
        for sub in active_subs:
            plan = plans_dict.get(sub.get('plan_id'), {})
            price = plan.get('price_mad') or plan.get('price') or 0
            mrr += float(price)

        # ARR = MRR * 12
        arr = mrr * 12

        # Utilisateurs actifs
        active_users_response = supabase.table('users')\
            .select('id', count='exact')\
            .eq('is_active', True)\
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
            .select('id, plan_id')\
            .eq('is_active', True)\
            .lte('created_at', start_date.isoformat())\
            .execute()
        
        prev_mrr = 0.0
        for sub in (prev_subs_response.data or []):
            plan = plans_dict.get(sub.get('plan_id'), {})
            price = plan.get('price_mad') or plan.get('price') or 0
            prev_mrr += float(price)

        revenue_growth = ((mrr - prev_mrr) / prev_mrr * 100) if prev_mrr > 0 else 0

        # Calculer le revenu total et les transactions depuis la table sales
        sales_result = supabase.table("sales").select("amount", count="exact").gte("created_at", start_date.isoformat()).execute()
        total_revenue = sum(float(s.get("amount", 0)) for s in sales_result.data) if sales_result.data else 0
        total_transactions = sales_result.count if hasattr(sales_result, 'count') else len(sales_result.data)

        return {
            'metrics': MetricsResponse(
                mrr=mrr,
                arr=arr,
                churn_rate=round(churn_rate, 2),
                active_users=active_users,
                new_users=new_users,
                revenue_growth=round(revenue_growth, 2),
                total_revenue=total_revenue,
                total_transactions=total_transactions
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
    Récupère les données d'évolution des revenus (basé sur les ventes)
    """
    try:
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Utiliser la table sales pour le revenu réel
        result = supabase.table("sales")\
            .select("amount, created_at")\
            .gte("created_at", start_date)\
            .order("created_at", desc=False)\
            .execute()

        # Agréger par jour
        daily_revenue = {}
        if result.data:
            for sale in result.data:
                created_at = sale.get("created_at")
                if not created_at:
                    continue

                date = str(created_at)[:10]
                amount_value = sale.get("amount")

                try:
                    amount = float(amount_value) if amount_value is not None else 0.0
                except (ValueError, TypeError):
                    amount = 0.0

                daily_revenue[date] = daily_revenue.get(date, 0) + amount

        # Convertir en liste triée pour le graphique
        revenue_data = []
        current_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            revenue_data.append({
                "date": date_str,
                "revenue": round(daily_revenue.get(date_str, 0), 2)
            })
            current_date += timedelta(days=1)

        return {'revenue_data': revenue_data, 'data': revenue_data}

    except Exception as e:
        logger.error(f"Error fetching revenue data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
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
            .eq('is_active', True)\
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
                .eq('is_active', True)\
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
        
        # 1. Récupérer les commissions (Influencers & Commercials)
        commissions_res = supabase.table('commissions')\
            .select('influencer_id, amount')\
            .eq('status', 'approved')\
            .gte('created_at', start_date.isoformat())\
            .execute()
            
        user_stats = {}
        
        for comm in (commissions_res.data or []):
            uid = comm.get('influencer_id')
            if not uid: continue
            
            if uid not in user_stats:
                user_stats[uid] = {'revenue': 0.0, 'transactions': 0}
            
            user_stats[uid]['revenue'] += float(comm.get('amount', 0))
            user_stats[uid]['transactions'] += 1
            
        # 2. Récupérer les ventes (Merchants) - Utilisation de la table sales car invoices est vide
        sales_res = supabase.table('sales')\
            .select('merchant_id, amount')\
            .gte('created_at', start_date.isoformat())\
            .execute()
            
        for sale in (sales_res.data or []):
            uid = sale.get('merchant_id')
            if not uid: continue
            
            if uid not in user_stats:
                user_stats[uid] = {'revenue': 0.0, 'transactions': 0}
                
            user_stats[uid]['revenue'] += float(sale.get('amount', 0))
            user_stats[uid]['transactions'] += 1
            
        # 3. Récupérer les infos utilisateurs
        if not user_stats:
            return {'data': []}
            
        user_ids = list(user_stats.keys())
        users_res = supabase.table('users')\
            .select('id, first_name, last_name, email, role')\
            .in_('id', user_ids)\
            .execute()
            
        users_map = {u['id']: u for u in (users_res.data or [])}
        
        # 4. Construire la liste finale
        performers = []
        for uid, stats in user_stats.items():
            user = users_map.get(uid, {})
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            if not name:
                name = user.get('email', 'Unknown')
                
            performers.append({
                'user_id': uid,
                'user_name': name,
                'email': user.get('email'),
                'role': user.get('role'),
                'revenue': round(stats['revenue'], 2),
                'transactions_count': stats['transactions']
            })
            
        # Trier par revenu décroissant
        performers.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Ajouter le rang
        for i, p in enumerate(performers):
            p['rank'] = i + 1

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

        # Récupérer les plans d'abord
        plans_response = supabase.table('subscription_plans')\
            .select('id, name, price_mad, price, type')\
            .execute()
        plans_dict = {p['id']: p for p in (plans_response.data or [])}

        # Récupérer les abonnements actifs (sans jointure)
        subs_response = supabase.table('subscriptions')\
            .select('id, plan_id')\
            .eq('is_active', True)\
            .gte('created_at', start_date.isoformat())\
            .execute()

        # Grouper par type de plan (Abonnements)
        sources = {}
        for sub in (subs_response.data or []):
            plan = plans_dict.get(sub.get('plan_id'), {})
            plan_type = plan.get('type', 'standard')
            price = plan.get('price_mad') or plan.get('price') or 0
            
            key = f"Abonnement {plan_type.capitalize()}"
            if key not in sources:
                sources[key] = 0.0
            sources[key] += float(price)

        # Ajouter les revenus des ventes (Sales)
        sales_response = supabase.table('sales')\
            .select('amount, campaign_id, product_id')\
            .gte('created_at', start_date.isoformat())\
            .execute()
            
        for sale in (sales_response.data or []):
            amount = float(sale.get('amount', 0))
            if sale.get('campaign_id'):
                key = "Campagnes"
            else:
                key = "Ventes Directes"
                
            if key not in sources:
                sources[key] = 0.0
            sources[key] += amount

        # Formatter pour le PieChart
        data = [{'name': k, 'value': round(v, 2)} for k, v in sources.items() if v > 0]

        return {'data': data}

    except Exception as e:
        logger.error(f"Error fetching revenue by source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue by source: {str(e)}"
        )
