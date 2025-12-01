"""
ANALYTICS ENDPOINTS - Statistiques et métriques pour dashboards
Tables utilisées: users, products, sales, conversions, tracking_links, commissions, payouts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from supabase_config import get_supabase_client
from auth import get_current_user_from_cookie
from db_helpers import get_user_by_id

router = APIRouter()

# ============================================
# GET /api/analytics/overview
# Vue d'ensemble admin (dashboard)
# ============================================
@router.get("/overview")
async def get_analytics_overview(current_user: dict = Depends(get_current_user_from_cookie)):
    """Statistiques générales pour le dashboard admin"""
    # Verify admin role
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["admin", "superadmin"]:
         raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    try:
        supabase = get_supabase_client()
        
        # Compter utilisateurs par rôle
        merchants = supabase.table('users').select('id', count='exact', head=True).eq('role', 'merchant').execute()
        influencers = supabase.table('users').select('id', count='exact', head=True).eq('role', 'influencer').execute()
        commercials = supabase.table('users').select('id', count='exact', head=True).eq('role', 'commercial').execute()
        
        # Compter products & services
        products = supabase.table('products').select('id', count='exact', head=True).execute()
        services = supabase.table('services').select('id', count='exact', head=True).execute()
        campaigns = supabase.table('campaigns').select('id', count='exact', head=True).execute()
        
        # Calculer revenus (total des ventes)
        sales = supabase.table('sales').select('amount').execute()
        total_revenue = sum([float(s.get('amount', 0)) for s in (sales.data or [])])
        
        # Calculer commissions
        commissions = supabase.table('commissions').select('amount').execute()
        total_commissions = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        
        # Stats tracking
        tracking_links = supabase.table('tracking_links').select('clicks').execute()
        total_clicks = sum([int(t.get('clicks', 0)) for t in (tracking_links.data or [])])
        
        conversions_count = supabase.table('conversions').select('id', count='exact', head=True).execute()
        
        # Taux de conversion
        conversion_rate = (conversions_count.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Payouts
        payouts = supabase.table('payouts').select('amount, status').execute()
        total_payouts = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'paid'])
        pending_payouts = len([p for p in (payouts.data or []) if p.get('status') == 'pending'])
        
        # Leads (commerciaux)
        leads = supabase.table('leads').select('id', count='exact', head=True).execute()
        
        return {
            "success": True,
            "users": {
                "total_merchants": merchants.count or 0,
                "total_influencers": influencers.count or 0,
                "total_commercials": commercials.count or 0,
                "total": (merchants.count or 0) + (influencers.count or 0) + (commercials.count or 0)
            },
            "catalog": {
                "total_products": products.count or 0,
                "total_services": services.count or 0,
                "total_campaigns": campaigns.count or 0
            },
            "financial": {
                "total_revenue": round(total_revenue, 2),
                "total_commissions": round(total_commissions, 2),
                "total_payouts": round(total_payouts, 2),
                "pending_payouts": pending_payouts,
                "net_revenue": round(total_revenue - total_commissions, 2)
            },
            "tracking": {
                "total_clicks": total_clicks,
                "total_conversions": conversions_count.count or 0,
                "conversion_rate": round(conversion_rate, 2),
                "total_links": len(tracking_links.data or [])
            },
            "leads": {
                "total": leads.count or 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/revenue-chart
# Graphique des revenus (30 derniers jours)
# ============================================
@router.get("/revenue-chart")
async def get_revenue_chart(days: int = Query(30, description="Nombre de jours")):
    """Revenus par jour pour graphique"""
    try:
        supabase = get_supabase_client()
        
        # Date de début
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Récupérer toutes les ventes
        sales = supabase.table('sales').select('amount, created_at').execute()
        
        # Grouper par jour
        revenue_by_day = {}
        for sale in (sales.data or []):
            created_at = sale.get('created_at', '')
            if created_at:
                # Extraire la date (YYYY-MM-DD)
                date_str = created_at[:10]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if date_obj >= start_date:
                    if date_str not in revenue_by_day:
                        revenue_by_day[date_str] = 0
                    revenue_by_day[date_str] += float(sale.get('amount', 0))
        
        # Créer tableau avec tous les jours (même ceux sans ventes = 0)
        data = []
        current_date = start_date
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            data.append({
                "date": date_str,
                "revenus": round(revenue_by_day.get(date_str, 0), 2),
                "formatted_date": current_date.strftime('%d/%m')
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "data": data,
            "total_days": len(data),
            "total_revenue": round(sum([d['revenus'] for d in data]), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/user-growth
# Graphique de croissance des utilisateurs
# ============================================
@router.get("/user-growth")
async def get_user_growth(period: str = Query("30days", description="Période: 7days, 30days, 90days, 1year")):
    """Croissance des utilisateurs par rôle pour graphique"""
    try:
        supabase = get_supabase_client()

        # Déterminer le nombre de jours selon la période
        period_days = {
            "7days": 7,
            "30days": 30,
            "90days": 90,
            "1year": 365,
            "all": 730  # 2 ans max
        }
        days = period_days.get(period, 30)

        # Date de début
        start_date = (datetime.now() - timedelta(days=days)).date()

        # Récupérer tous les utilisateurs avec leur date de création
        users = supabase.table('users').select('id, role, created_at').execute()

        # Grouper par jour et rôle
        data_by_day = {}

        for user in (users.data or []):
            created_at = user.get('created_at', '')
            role = user.get('role', 'unknown')

            if created_at:
                # Extraire la date (YYYY-MM-DD)
                date_str = created_at[:10]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                if date_obj >= start_date:
                    if date_str not in data_by_day:
                        data_by_day[date_str] = {
                            'merchants': 0,
                            'influencers': 0,
                            'commercials': 0,
                            'total': 0
                        }

                    if role == 'merchant':
                        data_by_day[date_str]['merchants'] += 1
                    elif role == 'influencer':
                        data_by_day[date_str]['influencers'] += 1
                    elif role == 'commercial':
                        data_by_day[date_str]['commercials'] += 1

                    data_by_day[date_str]['total'] += 1

        # Créer tableau avec cumul des utilisateurs (croissance cumulative)
        data = []
        current_date = start_date
        end_date = datetime.now().date()

        cumul_merchants = 0
        cumul_influencers = 0
        cumul_commercials = 0
        cumul_total = 0

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_data = data_by_day.get(date_str, {
                'merchants': 0,
                'influencers': 0,
                'commercials': 0,
                'total': 0
            })

            # Ajouter au cumul
            cumul_merchants += day_data['merchants']
            cumul_influencers += day_data['influencers']
            cumul_commercials += day_data['commercials']
            cumul_total += day_data['total']

            data.append({
                "date": current_date.strftime('%d/%m'),
                "merchants": cumul_merchants,
                "influencers": cumul_influencers,
                "commercials": cumul_commercials,
                "total": cumul_total
            })
            current_date += timedelta(days=1)

        # Calculer le taux de croissance
        if len(data) >= 2:
            first_total = data[0]['total'] or 1
            last_total = data[-1]['total']
            growth_rate = ((last_total - first_total) / first_total * 100)
        else:
            growth_rate = 0

        return {
            "success": True,
            "data": data,
            "period": period,
            "total_days": len(data),
            "growth_rate": round(growth_rate, 2),
            "final_counts": {
                "merchants": cumul_merchants,
                "influencers": cumul_influencers,
                "commercials": cumul_commercials,
                "total": cumul_total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/categories
# Répartition par catégorie de produits
# ============================================
@router.get("/categories")
async def get_categories_distribution():
    """Répartition des produits et revenus par catégorie"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer tous les produits avec catégorie
        products = supabase.table('products').select('id, category, price').execute()
        
        # Grouper par catégorie
        categories = {}
        for product in (products.data or []):
            category = product.get('category', 'Autre')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_value': 0
                }
            categories[category]['count'] += 1
            categories[category]['total_value'] += float(product.get('price', 0))
        
        # Formater pour graphique
        data = []
        for category, stats in categories.items():
            data.append({
                "name": category,
                "value": stats['count'],
                "total_value": round(stats['total_value'], 2)
            })
        
        # Trier par count
        data.sort(key=lambda x: x['value'], reverse=True)
        
        return {
            "success": True,
            "data": data,
            "total_categories": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/top-merchants
# Top marchands par revenus
# ============================================
@router.get("/top-merchants")
async def get_top_merchants(limit: int = Query(10, description="Nombre de marchands")):
    """Top marchands par revenus générés"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer toutes les ventes avec merchant_id
        sales = supabase.table('sales').select('merchant_id, amount').execute()
        
        # Grouper par merchant
        merchants_revenue = {}
        for sale in (sales.data or []):
            merchant_id = sale.get('merchant_id')
            if merchant_id:
                if merchant_id not in merchants_revenue:
                    merchants_revenue[merchant_id] = 0
                merchants_revenue[merchant_id] += float(sale.get('amount', 0))
        
        # Récupérer infos des merchants
        top_merchants = []
        for merchant_id, revenue in sorted(merchants_revenue.items(), key=lambda x: x[1], reverse=True)[:limit]:
            user = supabase.table('users').select('id, company_name, email').eq('id', merchant_id).single().execute()
            if user.data:
                top_merchants.append({
                    "merchant_id": merchant_id,
                    "company_name": user.data.get('company_name', 'Inconnu'),
                    "email": user.data.get('email'),
                    "total_revenue": round(revenue, 2)
                })
        
        return {
            "success": True,
            "merchants": top_merchants,
            "total": len(top_merchants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/top-influencers
# Top influenceurs par commissions
# ============================================
@router.get("/top-influencers")
async def get_top_influencers(limit: int = Query(10, description="Nombre d'influenceurs")):
    """Top influenceurs par commissions gagnées"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer toutes les commissions
        commissions = supabase.table('commissions').select('influencer_id, amount').execute()
        
        # Grouper par influencer
        influencers_earnings = {}
        for commission in (commissions.data or []):
            influencer_id = commission.get('influencer_id')
            if influencer_id:
                if influencer_id not in influencers_earnings:
                    influencers_earnings[influencer_id] = 0
                influencers_earnings[influencer_id] += float(commission.get('amount', 0))
        
        # Récupérer infos des influencers
        top_influencers = []
        for influencer_id, earnings in sorted(influencers_earnings.items(), key=lambda x: x[1], reverse=True)[:limit]:
            user = supabase.table('users').select('id, full_name, email').eq('id', influencer_id).single().execute()
            if user.data:
                top_influencers.append({
                    "influencer_id": influencer_id,
                    "name": user.data.get('full_name') or user.data.get('email', 'Inconnu'),
                    "email": user.data.get('email'),
                    "total_earnings": round(earnings, 2)
                })
        
        return {
            "success": True,
            "influencers": top_influencers,
            "total": len(top_influencers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/platform-metrics
# Métriques de la plateforme
# ============================================
@router.get("/platform-metrics")
async def get_platform_metrics():
    """Métriques globales de la plateforme"""
    try:
        supabase = get_supabase_client()
        
        # Taux de conversion moyen
        tracking_links = supabase.table('tracking_links').select('clicks').execute()
        total_clicks = sum([int(t.get('clicks', 0)) for t in (tracking_links.data or [])])
        
        conversions = supabase.table('conversions').select('id', count='exact', head=True).execute()
        conversion_rate = (conversions.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Dates de référence
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        sixty_days_ago = (datetime.now() - timedelta(days=60)).isoformat()
        
        # Clics mensuels (30 derniers jours)
        recent_conversions = supabase.table('conversions').select('id', count='exact', head=True).gte('created_at', thirty_days_ago).execute()
        monthly_clicks = recent_conversions.count or 0
        
        # Croissance mensuelle revenue (comparer 30 derniers jours vs 30 jours précédents)
        old_sales = supabase.table('sales').select('amount').lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        recent_sales = supabase.table('sales').select('amount').gte('created_at', thirty_days_ago).execute()
        
        old_revenue = sum([float(s.get('amount', 0)) for s in (old_sales.data or [])])
        recent_revenue = sum([float(s.get('amount', 0)) for s in (recent_sales.data or [])])
        
        growth_rate = ((recent_revenue - old_revenue) / old_revenue * 100) if old_revenue > 0 else 0
        
        # Active users (derniers 7 jours)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        active_users = supabase.table('users').select('id', count='exact', head=True).gte('last_login', seven_days_ago).execute()
        
        # Active users (dernières 24h)
        one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
        active_users_24h = supabase.table('users').select('id', count='exact', head=True).gte('last_login', one_day_ago).execute()

        # Nouvelles inscriptions (30 jours)
        new_signups = supabase.table('users').select('id', count='exact', head=True).gte('created_at', thirty_days_ago).execute()
        old_signups = supabase.table('users').select('id', count='exact', head=True).lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        signup_trend = ((new_signups.count - (old_signups.count or 0)) / (old_signups.count or 1) * 100) if old_signups.count else 0
        
        # ============================================
        # NOUVELLES MÉTRIQUES DE CROISSANCE PAR CATÉGORIE
        # ============================================
        
        # Croissance marchands (30j vs 30j précédents)
        recent_merchants = supabase.table('users').select('id', count='exact', head=True).eq('role', 'merchant').gte('created_at', thirty_days_ago).execute()
        old_merchants = supabase.table('users').select('id', count='exact', head=True).eq('role', 'merchant').lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        merchant_growth = ((recent_merchants.count - (old_merchants.count or 0)) / (old_merchants.count or 1) * 100) if old_merchants.count else 0
        
        # Croissance influenceurs
        recent_influencers = supabase.table('users').select('id', count='exact', head=True).eq('role', 'influencer').gte('created_at', thirty_days_ago).execute()
        old_influencers = supabase.table('users').select('id', count='exact', head=True).eq('role', 'influencer').lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        influencer_growth = ((recent_influencers.count - (old_influencers.count or 0)) / (old_influencers.count or 1) * 100) if old_influencers.count else 0
        
        # Croissance produits
        recent_products = supabase.table('products').select('id', count='exact', head=True).gte('created_at', thirty_days_ago).execute()
        old_products = supabase.table('products').select('id', count='exact', head=True).lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        product_growth = ((recent_products.count - (old_products.count or 0)) / (old_products.count or 1) * 100) if old_products.count else 0
        
        # Croissance services
        recent_services = supabase.table('services').select('id', count='exact', head=True).gte('created_at', thirty_days_ago).execute()
        old_services = supabase.table('services').select('id', count='exact', head=True).lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        service_growth = ((recent_services.count - (old_services.count or 0)) / (old_services.count or 1) * 100) if old_services.count else 0
        
        # Croissance taux de conversion
        old_conversions = supabase.table('conversions').select('id', count='exact', head=True).lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        conversion_trend = ((recent_conversions.count - (old_conversions.count or 0)) / (old_conversions.count or 1) * 100) if old_conversions.count else 0
        
        # User growth rate (total)
        total_recent_users = supabase.table('users').select('id', count='exact', head=True).gte('created_at', thirty_days_ago).execute()
        total_old_users = supabase.table('users').select('id', count='exact', head=True).lt('created_at', thirty_days_ago).gte('created_at', sixty_days_ago).execute()
        user_growth_rate = ((total_recent_users.count - (total_old_users.count or 0)) / (total_old_users.count or 1) * 100) if total_old_users.count else 0

        return {
            "success": True,
            "avg_conversion_rate": round(conversion_rate, 2),
            "monthly_clicks": monthly_clicks,
            "quarterly_growth": round(growth_rate, 2),
            "active_users_7d": active_users.count or 0,
            "active_users_24h": active_users_24h.count or 0,
            "new_signups_30d": new_signups.count or 0,
            "total_tracking_links": len(tracking_links.data or []),
            # Nouvelles métriques de croissance
            "user_growth_rate": round(user_growth_rate, 2),
            "signup_trend": round(signup_trend, 2),
            "conversion_trend": round(conversion_trend, 2),
            "merchant_growth": round(merchant_growth, 2),
            "influencer_growth": round(influencer_growth, 2),
            "product_growth": round(product_growth, 2),
            "service_growth": round(service_growth, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/merchant/sales-chart
# Graphique des ventes pour un marchand
# ============================================
@router.get("/merchant/sales-chart")
async def get_merchant_sales_chart(
    merchant_id: Optional[str] = Query(None), 
    days: int = Query(30),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Graphique des ventes d'un marchand sur X jours"""
    try:
        supabase = get_supabase_client()
        
        # Determine merchant_id from token if not provided or verify access
        user_id = current_user["id"]
        user = get_user_by_id(user_id)
        
        target_merchant_id = None
        
        if user["role"] == "merchant":
            # If user is merchant, force their own ID
            target_merchant_id = user_id
        elif user["role"] == "admin":
            # Admin can view any merchant
            target_merchant_id = merchant_id
        else:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
            
        if not target_merchant_id and user["role"] == "merchant":
             target_merchant_id = user_id

        # Si merchant_id n'est pas fourni, prendre toutes les ventes
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Récupérer les ventes
        query = supabase.table('sales').select('amount, created_at, merchant_id')
        if target_merchant_id:
            query = query.eq('merchant_id', target_merchant_id)
        sales = query.execute()
        
        # Grouper par jour
        sales_by_day = {}
        for sale in (sales.data or []):
            created_at = sale.get('created_at', '')
            if created_at:
                date_str = created_at[:10]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if date_obj >= start_date:
                    if date_str not in sales_by_day:
                        sales_by_day[date_str] = {'amount': 0, 'count': 0}
                    sales_by_day[date_str]['amount'] += float(sale.get('amount', 0))
                    sales_by_day[date_str]['count'] += 1
        
        # Créer tableau avec tous les jours
        data = []
        current_date = start_date
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_data = sales_by_day.get(date_str, {'amount': 0, 'count': 0})
            data.append({
                "date": date_str,
                "sales": round(day_data['amount'], 2),
                "orders": day_data['count'],
                "formatted_date": current_date.strftime('%d/%m')
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "data": data,
            "total_days": len(data),
            "total_sales": round(sum([d['sales'] for d in data]), 2),
            "total_orders": sum([d['orders'] for d in data])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/merchant/performance
# Performance d'un marchand
# ============================================
@router.get("/merchant/performance")
async def get_merchant_performance(
    merchant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Métriques de performance pour un marchand"""
    try:
        supabase = get_supabase_client()
        
        # Determine merchant_id from token if not provided or verify access
        user_id = current_user["id"]
        user = get_user_by_id(user_id)
        
        target_merchant_id = None
        
        if user["role"] == "merchant":
            # If user is merchant, force their own ID
            target_merchant_id = user_id
        elif user["role"] == "admin":
            # Admin can view any merchant
            target_merchant_id = merchant_id
        else:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
            
        if not target_merchant_id and user["role"] == "merchant":
             target_merchant_id = user_id
        
        # Statistiques de base
        query = supabase.table('sales').select('amount, status')
        if target_merchant_id:
            query = query.eq('merchant_id', target_merchant_id)
        sales = query.execute()
        
        total_sales = len(sales.data or [])
        completed_sales = len([s for s in (sales.data or []) if s.get('status') == 'completed'])
        total_revenue = sum([float(s.get('amount', 0)) for s in (sales.data or [])])
        
        # Produits
        prod_query = supabase.table('products').select('id', count='exact')
        if target_merchant_id:
            prod_query = prod_query.eq('merchant_id', target_merchant_id)
        products = prod_query.execute()
        
        # Tracking links et conversions
        links_query = supabase.table('tracking_links').select('clicks')
        if target_merchant_id:
            links_query = links_query.eq('merchant_id', target_merchant_id)
        links = links_query.execute()
        
        total_clicks = sum([int(l.get('clicks', 0)) for l in (links.data or [])])
        
        conv_query = supabase.table('conversions').select('id', count='exact')
        if target_merchant_id:
            conv_query = conv_query.eq('merchant_id', target_merchant_id)
        conversions = conv_query.execute()
        
        conversion_rate = (conversions.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Affiliés actifs (influencers avec liens vers ce merchant)
        affiliates_query = supabase.table('tracking_links').select('influencer_id')
        if target_merchant_id:
            affiliates_query = affiliates_query.eq('merchant_id', target_merchant_id)
        affiliates = affiliates_query.execute()
        unique_affiliates = len(set([a.get('influencer_id') for a in (affiliates.data or []) if a.get('influencer_id')]))
        
        # Engagement rate (Sales / Conversions ratio - Approval Rate)
        engagement_rate = (total_sales / conversions.count * 100) if conversions.count > 0 else 0
        
        # Satisfaction rate (ventes complétées / total ventes)
        satisfaction_rate = (completed_sales / total_sales * 100) if total_sales > 0 else 0
        
        # Objectif mensuel (simulé - 10000€)
        monthly_goal = 10000
        monthly_goal_progress = (total_revenue / monthly_goal * 100) if monthly_goal > 0 else 0
        
        # ROI Marketing réel: (Revenue - Coûts) / Coûts * 100
        # Coûts = commissions versées aux affiliés
        commissions_query = supabase.table('commissions').select('amount')
        if target_merchant_id:
            commissions_query = commissions_query.eq('merchant_id', target_merchant_id)
        commissions_result = commissions_query.execute()
        total_commissions_paid = sum([float(c.get('amount', 0)) for c in (commissions_result.data or [])])
        
        # ROI = (Revenue net / Investissement marketing) * 100
        # Investissement = commissions payées
        roi = ((total_revenue - total_commissions_paid) / total_commissions_paid * 100) if total_commissions_paid > 0 else 0
        
        return {
            "success": True,
            "conversion_rate": round(conversion_rate, 2),
            "engagement_rate": round(engagement_rate, 2),
            "satisfaction_rate": round(satisfaction_rate, 2),
            "monthly_goal_progress": round(min(monthly_goal_progress, 100), 2),
            "total_revenue": round(total_revenue, 2),
            "total_sales": total_sales,
            "products_count": products.count or 0,
            "affiliates_count": unique_affiliates,
            "total_clicks": total_clicks,
            "roi": round(roi, 2),
            "total_commissions_paid": round(total_commissions_paid, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/influencer/earnings-chart
# Graphique des gains pour un influenceur
# ============================================
@router.get("/influencer/earnings-chart")
async def get_influencer_earnings_chart(
    influencer_id: Optional[str] = Query(None), 
    days: int = Query(30),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Graphique des commissions d'un influenceur sur X jours"""
    try:
        supabase = get_supabase_client()
        
        # Determine influencer_id from token if not provided or verify access
        user_id = current_user["id"]
        user = get_user_by_id(user_id)
        
        target_influencer_id = None
        
        if user["role"] == "influencer":
            # If user is influencer, force their own ID
            target_influencer_id = user_id
        elif user["role"] == "admin":
            # Admin can view any influencer
            target_influencer_id = influencer_id
        else:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
            
        if not target_influencer_id and user["role"] == "influencer":
             target_influencer_id = user_id

        start_date = (datetime.now() - timedelta(days=days)).date()
        start_date_iso = start_date.isoformat()
        
        # Récupérer les commissions
        query = supabase.table('commissions').select('amount, created_at, influencer_id')
        if target_influencer_id:
            query = query.eq('influencer_id', target_influencer_id)
        commissions = query.execute()
        
        # Récupérer les conversions par jour (pour avoir les clics/ventes réels)
        conv_query = supabase.table('conversions').select('created_at, tracking_link_id')
        if target_influencer_id:
            conv_query = conv_query.eq('influencer_id', target_influencer_id)
        conversions = conv_query.gte('created_at', start_date_iso).execute()
        
        # Grouper les conversions par jour
        conversions_by_day = {}
        for conv in (conversions.data or []):
            created_at = conv.get('created_at', '')
            if created_at:
                date_str = created_at[:10]
                conversions_by_day[date_str] = conversions_by_day.get(date_str, 0) + 1
        
        # Grouper les gains par jour
        earnings_by_day = {}
        for commission in (commissions.data or []):
            created_at = commission.get('created_at', '')
            if created_at:
                date_str = created_at[:10]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if date_obj >= start_date:
                    if date_str not in earnings_by_day:
                        earnings_by_day[date_str] = {'amount': 0, 'count': 0}
                    earnings_by_day[date_str]['amount'] += float(commission.get('amount', 0))
                    earnings_by_day[date_str]['count'] += 1
        
        # Créer tableau avec tous les jours
        data = []
        current_date = start_date
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_data = earnings_by_day.get(date_str, {'amount': 0, 'count': 0})
            day_conversions = conversions_by_day.get(date_str, 0)
            data.append({
                "date": date_str,
                "earnings": round(day_data['amount'], 2),
                "commissions": day_data['count'],
                "conversions": day_conversions,
                "formatted_date": current_date.strftime('%d/%m')
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "data": data,
            "total_days": len(data),
            "total_earnings": round(sum([d['earnings'] for d in data]), 2),
            "total_commissions": sum([d['commissions'] for d in data]),
            "total_conversions": sum([d['conversions'] for d in data])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/influencer/overview
# Vue d'ensemble pour un influenceur
# ============================================
@router.get("/influencer/overview")
async def get_influencer_overview(
    influencer_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Statistiques complètes pour un influenceur"""
    try:
        supabase = get_supabase_client()
        
        # Determine influencer_id from token if not provided or verify access
        user_id = current_user["id"]
        user = get_user_by_id(user_id)
        
        target_influencer_id = None
        
        if user["role"] == "influencer":
            # If user is influencer, force their own ID
            target_influencer_id = user_id
        elif user["role"] == "admin":
            # Admin can view any influencer
            target_influencer_id = influencer_id
        else:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
            
        if not target_influencer_id and user["role"] == "influencer":
             target_influencer_id = user_id
        
        # Commissions totales
        comm_query = supabase.table('commissions').select('amount, created_at')
        if target_influencer_id:
            comm_query = comm_query.eq('influencer_id', target_influencer_id)
        commissions = comm_query.execute()
        
        total_earnings = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        
        # Tracking links et clics
        links_query = supabase.table('tracking_links').select('clicks, conversions')
        if target_influencer_id:
            links_query = links_query.eq('influencer_id', target_influencer_id)
        links = links_query.execute()
        
        total_clicks = sum([int(l.get('clicks', 0)) for l in (links.data or [])])
        total_conversions = sum([int(l.get('conversions', 0)) for l in (links.data or [])])
        
        # Payouts pour calculer balance
        payout_query = supabase.table('payouts').select('amount, status')
        if target_influencer_id:
            payout_query = payout_query.eq('influencer_id', target_influencer_id)
        payouts = payout_query.execute()
        
        total_withdrawn = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'paid'])
        pending_payouts_amount = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'pending'])
        balance = total_earnings - total_withdrawn
        
        # Calculer growth (comparer derniers 15 jours vs 15 jours précédents)
        fifteen_days_ago = (datetime.now() - timedelta(days=15)).isoformat()
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        recent_comm = [c for c in (commissions.data or []) if c.get('created_at', '') >= fifteen_days_ago]
        old_comm = [c for c in (commissions.data or []) if thirty_days_ago <= c.get('created_at', '') < fifteen_days_ago]
        
        recent_earnings = sum([float(c.get('amount', 0)) for c in recent_comm])
        old_earnings = sum([float(c.get('amount', 0)) for c in old_comm])
        
        earnings_growth = ((recent_earnings - old_earnings) / old_earnings * 100) if old_earnings > 0 else 0

        # Calculer growth pour clics et ventes
        # Note: tracking_links might not have created_at for clicks, assuming created_at of link or we need a clicks history table. 
        # Actually tracking_links table usually has created_at. But clicks are aggregated. 
        # If we don't have click history, we can't calculate growth accurately without a clicks table.
        # However, let's check if we can use 'conversions' table for sales growth.
        
        conversions_query = supabase.table('conversions').select('created_at')
        if target_influencer_id:
            conversions_query = conversions_query.eq('influencer_id', target_influencer_id)
        conversions_data = conversions_query.execute()
        
        recent_conv = [c for c in (conversions_data.data or []) if c.get('created_at', '') >= fifteen_days_ago]
        old_conv = [c for c in (conversions_data.data or []) if thirty_days_ago <= c.get('created_at', '') < fifteen_days_ago]
        
        sales_growth = ((len(recent_conv) - len(old_conv)) / len(old_conv) * 100) if len(old_conv) > 0 else 0
        
        # For clicks, since we only have total clicks in tracking_links, we can't easily calculate growth without a clicks history.
        # We will keep the hardcoded value for clicks_growth or set it to 0 if we can't calculate it, 
        # OR we can try to estimate it if we had a daily_stats table.
        # For now, let's leave clicks_growth as is or set to 0 to avoid misleading "5.5".
        clicks_growth = 0 
        
        # Calculer les gains du mois en cours
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        monthly_comm = [c for c in (commissions.data or []) if c.get('created_at', '') >= start_of_month]
        monthly_earnings = sum([float(c.get('amount', 0)) for c in monthly_comm])
        
        return {
            "success": True,
            "total_earnings": round(total_earnings, 2),
            "total_clicks": total_clicks,
            "total_sales": total_conversions,
            "balance": round(balance, 2),
            "earnings_growth": round(earnings_growth, 2),
            "clicks_growth": round(clicks_growth, 2),
            "sales_growth": round(sales_growth, 2),
            "pending_amount": round(pending_payouts_amount, 2),
            "total_links": len(links.data or []),
            "monthly_earnings": round(monthly_earnings, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
