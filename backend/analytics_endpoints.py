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
from utils.cache import cache
import asyncio
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

# ============================================
# GET /api/analytics/overview
# Vue d'ensemble admin (dashboard)
# ============================================
@router.get("/overview")
@cache(ttl_seconds=60)
async def get_analytics_overview(current_user: dict = Depends(get_current_user_from_cookie)):
    """Statistiques générales pour le dashboard admin"""
    # Verify admin role
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["admin", "superadmin"]:
         raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    try:
        supabase = get_supabase_client()
        
        # Compter utilisateurs par rôle
        try:
            merchants = supabase.table('users').select('id', count='exact', head=True).eq('role', 'merchant').execute()
            merchants_count = merchants.count or 0
        except Exception:
            merchants_count = 0

        try:
            influencers = supabase.table('users').select('id', count='exact', head=True).eq('role', 'influencer').execute()
            influencers_count = influencers.count or 0
        except Exception:
            influencers_count = 0

        try:
            commercials = supabase.table('users').select('id', count='exact', head=True).eq('role', 'commercial').execute()
            commercials_count = commercials.count or 0
        except Exception:
            commercials_count = 0
        
        # Utilisateurs actifs dernières 24h
        try:
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            active_users_res = supabase.table("users").select("id", count="exact", head=True).gt("last_login", yesterday).execute()
            active_users_24h = active_users_res.count or 0
        except Exception:
            active_users_24h = 0
        
        # Compter products & services
        try:
            products = supabase.table('products').select('id', count='exact', head=True).execute()
            products_count = products.count or 0
        except Exception:
            products_count = 0

        try:
            services = supabase.table('services').select('id', count='exact', head=True).execute()
            services_count = services.count or 0
        except Exception:
            services_count = 0

        try:
            campaigns = supabase.table('campaigns').select('id', count='exact', head=True).execute()
            campaigns_count = campaigns.count or 0
        except Exception:
            campaigns_count = 0
        
        # Calculer revenus (total des ventes avec commissions)
        try:
            sales = supabase.table('sales').select('amount, platform_commission, commission_amount').eq('status', 'completed').execute()
            sales_data = sales.data or []
            total_revenue = sum([float(s.get('amount', 0) or 0) for s in sales_data])
            platform_commission = sum([float(s.get('platform_commission', 0) or 0) for s in sales_data])
            influencer_commission = sum([float(s.get('commission_amount', 0) or 0) for s in sales_data])
        except Exception:
            total_revenue = 0
            platform_commission = 0
            influencer_commission = 0
        
        # Calculer commissions (table legacy)
        try:
            commissions = supabase.table('commissions').select('amount').execute()
            total_commissions = sum([float(c.get('amount', 0) or 0) for c in (commissions.data or [])])
        except Exception:
            total_commissions = 0
        
        # Stats tracking
        try:
            tracking_links = supabase.table('tracking_links').select('clicks').execute()
            tracking_data = tracking_links.data or []
            total_clicks = sum([int(t.get('clicks', 0) or 0) for t in tracking_data])
            total_links_count = len(tracking_data)
        except Exception:
            total_clicks = 0
            total_links_count = 0
        
        try:
            # Count only conversions that came from tracking links (have tracking_link_id)
            conversions_res = supabase.table('conversions').select('id', count='exact', head=True).not_.is_('tracking_link_id', 'null').execute()
            conversions_count = conversions_res.count or 0
        except Exception:
            conversions_count = 0

        # Taux de conversion - capped at 100% max (can't have more conversions than clicks)
        if total_clicks > 0:
            raw_rate = (conversions_count / total_clicks * 100)
            conversion_rate = min(raw_rate, 100.0)  # Cap at 100%
        else:
            conversion_rate = 0
        
        # Payouts
        try:
            payouts = supabase.table('payouts').select('amount, status').execute()
            payouts_data = payouts.data or []
            total_payouts = sum([float(p.get('amount', 0) or 0) for p in payouts_data if p.get('status') == 'paid'])
            pending_payouts = len([p for p in payouts_data if p.get('status') == 'pending'])
        except Exception:
            total_payouts = 0
            pending_payouts = 0
        
        # Leads (commerciaux)
        try:
            leads = supabase.table('leads').select('id', count='exact', head=True).execute()
            leads_count = leads.count or 0
        except Exception:
            leads_count = 0
        
        # Abonnements (subscriptions)
        active_subs_count = 0
        subscription_revenue = 0
        try:
            active_subs = supabase.table('subscriptions').select('id, plan_id', count='exact', head=True).in_('status', ['active', 'trialing']).execute()
            active_subs_count = active_subs.count or 0
            
            # Revenus des abonnements
            if active_subs_count > 0:
                # Récupérer les détails des plans pour calculer le revenu
                all_subs = supabase.table('subscriptions').select('plan_id').in_('status', ['active', 'trialing']).execute()
                if all_subs.data:
                    plan_ids = list(set([s.get('plan_id') for s in all_subs.data if s.get('plan_id')]))
                    if plan_ids:
                        plans = supabase.table('subscription_plans').select('id, price').in_('id', plan_ids).execute()
                        plan_prices = {p.get('id'): float(p.get('price', 0) or 0) for p in (plans.data or [])}
                        subscription_revenue = sum([plan_prices.get(s.get('plan_id'), 0) for s in all_subs.data])
        except Exception:
            pass # Keep defaults 0
        
        return {
            "success": True,
            "users": {
                "total_merchants": merchants_count,
                "total_influencers": influencers_count,
                "total_commercials": commercials_count,
                "active_users_24h": active_users_24h,
                "total": merchants_count + influencers_count + commercials_count
            },
            "catalog": {
                "total_products": products_count,
                "total_services": services_count,
                "total_campaigns": campaigns_count
            },
            "subscriptions": {
                "active_subscriptions": active_subs_count,
                "subscription_revenue": round(subscription_revenue, 2)
            },
            "financial": {
                "total_revenue": round(total_revenue, 2),
                "platform_commission": round(platform_commission, 2),
                "total_commissions": round(total_commissions, 2),
                "total_payouts": round(total_payouts, 2),
                "pending_payouts": pending_payouts,
                "net_revenue": round(total_revenue - total_commissions, 2)
            },
            "tracking": {
                "total_clicks": total_clicks,
                "total_conversions": conversions_count,
                "conversion_rate": round(conversion_rate, 2),
                "total_links": total_links_count
            },
            "leads": {
                "total": leads_count
            }
        }
    except Exception as e:
        # Log error but return empty structure instead of 500
        print(f"❌ Error in analytics overview: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "users": {"total_merchants": 0, "total_influencers": 0, "total_commercials": 0, "active_users_24h": 0, "total": 0},
            "catalog": {"total_products": 0, "total_services": 0, "total_campaigns": 0},
            "subscriptions": {"active_subscriptions": 0, "subscription_revenue": 0},
            "financial": {"total_revenue": 0, "platform_commission": 0, "total_commissions": 0, "total_payouts": 0, "pending_payouts": 0, "net_revenue": 0},
            "tracking": {"total_clicks": 0, "total_conversions": 0, "conversion_rate": 0, "total_links": 0},
            "leads": {"total": 0}
        }

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
                "revenue": round(revenue_by_day.get(date_str, 0), 2),  # Changé de 'revenus' à 'revenue'
                "formatted_date": current_date.strftime('%d/%m')
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "data": data,
            "total_days": len(data),
            "total_revenue": round(sum([d['revenue'] for d in data]), 2)  # Changé de 'revenus' à 'revenue'
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
    """Top influenceurs par commissions gagnées avec clics et conversions"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer toutes les commissions
        commissions = supabase.table('commissions').select('influencer_id, amount').execute()
        
        # Récupérer tous les tracking links pour les clics
        tracking_links = supabase.table('tracking_links').select('influencer_id, clicks').execute()
        
        # Récupérer toutes les conversions
        conversions = supabase.table('conversions').select('influencer_id').execute()
        
        # Grouper par influencer
        influencers_data = {}
        
        # Calculer les earnings
        for commission in (commissions.data or []):
            influencer_id = commission.get('influencer_id')
            if influencer_id:
                if influencer_id not in influencers_data:
                    influencers_data[influencer_id] = {'earnings': 0, 'clicks': 0, 'conversions': 0}
                influencers_data[influencer_id]['earnings'] += float(commission.get('amount', 0))
        
        # Calculer les clics
        for link in (tracking_links.data or []):
            influencer_id = link.get('influencer_id')
            if influencer_id:
                if influencer_id not in influencers_data:
                    influencers_data[influencer_id] = {'earnings': 0, 'clicks': 0, 'conversions': 0}
                influencers_data[influencer_id]['clicks'] += int(link.get('clicks', 0))
        
        # Calculer les conversions
        for conversion in (conversions.data or []):
            influencer_id = conversion.get('influencer_id')
            if influencer_id:
                if influencer_id not in influencers_data:
                    influencers_data[influencer_id] = {'earnings': 0, 'clicks': 0, 'conversions': 0}
                influencers_data[influencer_id]['conversions'] += 1
        
        # Récupérer infos des influencers et construire le résultat
        top_influencers = []
        for influencer_id, data in sorted(influencers_data.items(), key=lambda x: x[1]['earnings'], reverse=True)[:limit]:
            user = supabase.table('users').select('id, full_name, email').eq('id', influencer_id).single().execute()
            if user.data:
                top_influencers.append({
                    "influencer_id": influencer_id,
                    "name": user.data.get('full_name') or user.data.get('email', 'Inconnu'),
                    "email": user.data.get('email'),
                    "total_earnings": round(data['earnings'], 2),
                    "total_clicks": data['clicks'],
                    "total_conversions": data['conversions']
                })
        
        return {
            "success": True,
            "influencers": top_influencers,
            "total": len(top_influencers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/top-products
# Top produits par revenus
# ============================================
@router.get("/top-products")
async def get_top_products(
    period: str = Query("30days", description="Période: 7days, 30days, 90days, 1year, all"),
    limit: int = Query(10, description="Nombre de produits")
):
    """Top produits par revenus générés"""
    try:
        supabase = get_supabase_client()

        # Calculer la date de début selon la période
        if period == "7days":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif period == "30days":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif period == "90days":
            start_date = (datetime.now() - timedelta(days=90)).isoformat()
        elif period == "1year":
            start_date = (datetime.now() - timedelta(days=365)).isoformat()
        else:  # all
            start_date = None

        products_revenue = {}
        products_count = {}
        
        # 1. Essayer d'abord avec les conversions (colonne sale_amount)
        try:
            conversions_query = supabase.table('conversions').select('product_id, sale_amount')
            if start_date:
                conversions_query = conversions_query.gte('created_at', start_date)
            conversions = conversions_query.execute()
            
            for conversion in (conversions.data or []):
                product_id = conversion.get('product_id')
                if product_id:
                    if product_id not in products_revenue:
                        products_revenue[product_id] = 0
                        products_count[product_id] = 0
                    products_revenue[product_id] += float(conversion.get('sale_amount', 0))
                    products_count[product_id] += 1
        except Exception as e:
            print(f"⚠️ Erreur conversions: {e}")
        
        # 2. Compléter/Utiliser les ventes de la table sales
        try:
            sales_query = supabase.table('sales').select('product_id, amount')
            if start_date:
                sales_query = sales_query.gte('created_at', start_date)
            sales = sales_query.execute()
            
            for sale in (sales.data or []):
                product_id = sale.get('product_id')
                if product_id:
                    if product_id not in products_revenue:
                        products_revenue[product_id] = 0
                        products_count[product_id] = 0
                    products_revenue[product_id] += float(sale.get('amount', 0))
                    products_count[product_id] += 1
        except Exception as e:
            print(f"⚠️ Erreur sales: {e}")

        # Récupérer infos des produits
        top_products = []
        for product_id, revenue in sorted(products_revenue.items(), key=lambda x: x[1], reverse=True)[:limit]:
            try:
                product = supabase.table('products').select('id, name, price, category').eq('id', product_id).single().execute()
                if product.data:
                    top_products.append({
                        "id": product_id,
                        "name": product.data.get('name', 'Produit sans nom'),
                        "revenue": round(revenue, 2),
                        "conversions": products_count.get(product_id, 0),
                        "price": float(product.data.get('price', 0))
                    })
            except Exception as e:
                # Produit non trouvé, on l'ajoute quand même avec les données disponibles
                top_products.append({
                    "id": product_id,
                    "name": f"Produit #{product_id[:8]}",
                    "revenue": round(revenue, 2),
                    "conversions": products_count.get(product_id, 0),
                    "price": 0
                })

        return top_products
    except Exception as e:
        print(f"Erreur top-products: {str(e)}")
        return []

# ============================================
# GET /api/analytics/platform-metrics
# Métriques de la plateforme
# ============================================
@router.get("/platform-metrics")
@cache(ttl_seconds=60)
async def get_platform_metrics():
    """Métriques globales de la plateforme"""
    try:
        supabase = get_supabase_client()
        
        # Dates de référence
        now = datetime.now()
        thirty_days_ago = (now - timedelta(days=30))
        sixty_days_ago = (now - timedelta(days=60))
        seven_days_ago = (now - timedelta(days=7))
        one_day_ago = (now - timedelta(days=1))
        
        # Parallelize queries
        async def fetch_users():
            return await run_in_threadpool(lambda: supabase.table('users').select('id, role, created_at, last_login').execute())
            
        async def fetch_products():
            return await run_in_threadpool(lambda: supabase.table('products').select('created_at').execute())
            
        async def fetch_services():
            return await run_in_threadpool(lambda: supabase.table('services').select('created_at').execute())
            
        async def fetch_conversions():
            return await run_in_threadpool(lambda: supabase.table('conversions').select('created_at').execute())
            
        async def fetch_sales():
            return await run_in_threadpool(lambda: supabase.table('sales').select('amount, created_at').execute())
            
        async def fetch_links():
            return await run_in_threadpool(lambda: supabase.table('tracking_links').select('clicks').execute())

        users_res, products_res, services_res, conversions_res, sales_res, links_res = await asyncio.gather(
            fetch_users(), fetch_products(), fetch_services(), fetch_conversions(), fetch_sales(), fetch_links()
        )
        
        users = users_res.data or []
        products = products_res.data or []
        services = services_res.data or []
        conversions = conversions_res.data or []
        sales = sales_res.data or []
        links = links_res.data or []
        
        # Process Users
        active_users_7d = 0
        active_users_24h = 0
        new_signups = 0
        old_signups = 0
        recent_merchants = 0
        old_merchants = 0
        recent_influencers = 0
        old_influencers = 0
        total_recent_users = 0
        total_old_users = 0
        
        for u in users:
            created_at = None
            if u.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            last_login = None
            if u.get('last_login'):
                try:
                    last_login = datetime.fromisoformat(u['last_login'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            role = u.get('role')
            
            if last_login:
                if last_login >= seven_days_ago:
                    active_users_7d += 1
                if last_login >= one_day_ago:
                    active_users_24h += 1
            
            if created_at:
                if created_at >= thirty_days_ago:
                    new_signups += 1
                    total_recent_users += 1
                    if role == 'merchant': recent_merchants += 1
                    if role == 'influencer': recent_influencers += 1
                elif created_at >= sixty_days_ago:
                    old_signups += 1
                    total_old_users += 1
                    if role == 'merchant': old_merchants += 1
                    if role == 'influencer': old_influencers += 1

        # Process Products
        recent_products = 0
        old_products = 0
        for p in products:
            created_at = None
            if p.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(p['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            if created_at:
                if created_at >= thirty_days_ago:
                    recent_products += 1
                elif created_at >= sixty_days_ago:
                    old_products += 1

        # Process Services
        recent_services = 0
        old_services = 0
        for s in services:
            created_at = None
            if s.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            if created_at:
                if created_at >= thirty_days_ago:
                    recent_services += 1
                elif created_at >= sixty_days_ago:
                    old_services += 1

        # Process Conversions
        total_conversions = len(conversions)
        recent_conversions = 0
        old_conversions = 0
        
        for c in conversions:
            created_at = None
            if c.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            if created_at:
                if created_at >= thirty_days_ago:
                    recent_conversions += 1
                elif created_at >= sixty_days_ago:
                    old_conversions += 1

        # Process Sales
        recent_revenue = 0.0
        old_revenue = 0.0
        for s in sales:
            created_at = None
            if s.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            
            amount = float(s.get('amount', 0))
            if created_at:
                if created_at >= thirty_days_ago:
                    recent_revenue += amount
                elif created_at >= sixty_days_ago:
                    old_revenue += amount

        # Process Tracking Links (Clicks)
        total_clicks = sum([int(l.get('clicks', 0)) for l in links])
        
        # Calculations
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        growth_rate = ((recent_revenue - old_revenue) / old_revenue * 100) if old_revenue > 0 else 0
        signup_trend = ((new_signups - old_signups) / (old_signups or 1) * 100) if old_signups else 0
        merchant_growth = ((recent_merchants - old_merchants) / (old_merchants or 1) * 100) if old_merchants else 0
        influencer_growth = ((recent_influencers - old_influencers) / (old_influencers or 1) * 100) if old_influencers else 0
        product_growth = ((recent_products - old_products) / (old_products or 1) * 100) if old_products else 0
        service_growth = ((recent_services - old_services) / (old_services or 1) * 100) if old_services else 0
        conversion_trend = ((recent_conversions - old_conversions) / (old_conversions or 1) * 100) if old_conversions else 0
        user_growth_rate = ((total_recent_users - total_old_users) / (total_old_users or 1) * 100) if total_old_users else 0

        return {
            "success": True,
            "avg_conversion_rate": round(conversion_rate, 2),
            "monthly_clicks": recent_conversions,
            "quarterly_growth": round(growth_rate, 2),
            "active_users_7d": active_users_7d,
            "active_users_24h": active_users_24h,
            "new_signups_30d": new_signups,
            "total_tracking_links": len(links),
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
