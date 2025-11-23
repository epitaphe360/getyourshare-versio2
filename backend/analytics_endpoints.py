"""
ANALYTICS ENDPOINTS - Statistiques et métriques pour dashboards
Tables utilisées: users, products, sales, conversions, tracking_links, commissions, payouts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from supabase_config import get_supabase_client

router = APIRouter()

# ============================================
# GET /api/analytics/overview
# Vue d'ensemble admin (dashboard)
# ============================================
@router.get("/overview")
async def get_analytics_overview():
    """Statistiques générales pour le dashboard admin"""
    try:
        supabase = get_supabase_client()
        
        # Compter utilisateurs par rôle
        merchants = supabase.table('users').select('id', count='exact').eq('role', 'merchant').execute()
        influencers = supabase.table('users').select('id', count='exact').eq('role', 'influencer').execute()
        commercials = supabase.table('users').select('id', count='exact').eq('role', 'commercial').execute()
        
        # Compter products & services
        products = supabase.table('products').select('id', count='exact').execute()
        services = supabase.table('services').select('id', count='exact').execute()
        campaigns = supabase.table('campaigns').select('id', count='exact').execute()
        
        # Calculer revenus (total des ventes)
        sales = supabase.table('sales').select('amount').execute()
        total_revenue = sum([float(s.get('amount', 0)) for s in (sales.data or [])])
        
        # Calculer commissions
        commissions = supabase.table('commissions').select('amount').execute()
        total_commissions = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        
        # Stats tracking
        tracking_links = supabase.table('tracking_links').select('clicks').execute()
        total_clicks = sum([int(t.get('clicks', 0)) for t in (tracking_links.data or [])])
        
        conversions_count = supabase.table('conversions').select('id', count='exact').execute()
        
        # Taux de conversion
        conversion_rate = (conversions_count.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Payouts
        payouts = supabase.table('payouts').select('amount, status').execute()
        total_payouts = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'paid'])
        pending_payouts = len([p for p in (payouts.data or []) if p.get('status') == 'pending'])
        
        # Leads (commerciaux)
        leads = supabase.table('leads').select('id', count='exact').execute()
        
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
                "net_revenue": round(total_revenue - total_commissions - total_payouts, 2)
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
        
        conversions = supabase.table('conversions').select('id', count='exact').execute()
        conversion_rate = (conversions.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Clics mensuels (30 derniers jours)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_conversions = supabase.table('conversions').select('id', count='exact').gte('created_at', thirty_days_ago).execute()
        monthly_clicks = recent_conversions.count or 0
        
        # Croissance trimestrielle (simulée - comparer avec 3 mois avant)
        ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat()
        old_sales = supabase.table('sales').select('amount').lt('created_at', thirty_days_ago).gte('created_at', ninety_days_ago).execute()
        recent_sales = supabase.table('sales').select('amount').gte('created_at', thirty_days_ago).execute()
        
        old_revenue = sum([float(s.get('amount', 0)) for s in (old_sales.data or [])])
        recent_revenue = sum([float(s.get('amount', 0)) for s in (recent_sales.data or [])])
        
        quarterly_growth = ((recent_revenue - old_revenue) / old_revenue * 100) if old_revenue > 0 else 0
        
        # Active users (derniers 7 jours)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        active_users = supabase.table('users').select('id', count='exact').gte('last_login', seven_days_ago).execute()
        
        # Active users (dernières 24h)
        one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
        active_users_24h = supabase.table('users').select('id', count='exact').gte('last_login', one_day_ago).execute()

        # Nouvelles inscriptions (30 jours)
        new_signups = supabase.table('users').select('id', count='exact').gte('created_at', thirty_days_ago).execute()

        return {
            "success": True,
            "avg_conversion_rate": round(conversion_rate, 2),
            "monthly_clicks": monthly_clicks,
            "quarterly_growth": round(quarterly_growth, 2),
            "active_users_7d": active_users.count or 0,
            "active_users_24h": active_users_24h.count or 0,
            "new_signups_30d": new_signups.count or 0,
            "total_tracking_links": len(tracking_links.data or [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/merchant/sales-chart
# Graphique des ventes pour un marchand
# ============================================
@router.get("/merchant/sales-chart")
async def get_merchant_sales_chart(merchant_id: Optional[str] = Query(None), days: int = Query(30)):
    """Graphique des ventes d'un marchand sur X jours"""
    try:
        supabase = get_supabase_client()
        
        # Si merchant_id n'est pas fourni, prendre toutes les ventes
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Récupérer les ventes
        query = supabase.table('sales').select('amount, created_at, merchant_id')
        if merchant_id:
            query = query.eq('merchant_id', merchant_id)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/merchant/performance
# Performance d'un marchand
# ============================================
@router.get("/merchant/performance")
async def get_merchant_performance(merchant_id: Optional[str] = Query(None)):
    """Métriques de performance pour un marchand"""
    try:
        supabase = get_supabase_client()
        
        # Statistiques de base
        query = supabase.table('sales').select('amount, status')
        if merchant_id:
            query = query.eq('merchant_id', merchant_id)
        sales = query.execute()
        
        total_sales = len(sales.data or [])
        completed_sales = len([s for s in (sales.data or []) if s.get('status') == 'completed'])
        total_revenue = sum([float(s.get('amount', 0)) for s in (sales.data or [])])
        
        # Produits
        prod_query = supabase.table('products').select('id', count='exact')
        if merchant_id:
            prod_query = prod_query.eq('merchant_id', merchant_id)
        products = prod_query.execute()
        
        # Tracking links et conversions
        links_query = supabase.table('tracking_links').select('clicks')
        if merchant_id:
            links_query = links_query.eq('merchant_id', merchant_id)
        links = links_query.execute()
        
        total_clicks = sum([int(l.get('clicks', 0)) for l in (links.data or [])])
        
        conv_query = supabase.table('conversions').select('id', count='exact')
        if merchant_id:
            conv_query = conv_query.eq('merchant_id', merchant_id)
        conversions = conv_query.execute()
        
        conversion_rate = (conversions.count / total_clicks * 100) if total_clicks > 0 else 0
        
        # Affiliés actifs (influencers avec liens vers ce merchant)
        affiliates_query = supabase.table('tracking_links').select('influencer_id')
        if merchant_id:
            affiliates_query = affiliates_query.eq('merchant_id', merchant_id)
        affiliates = affiliates_query.execute()
        unique_affiliates = len(set([a.get('influencer_id') for a in (affiliates.data or []) if a.get('influencer_id')]))
        
        # Engagement rate (conversions / ventes)
        engagement_rate = (conversions.count / total_sales * 100) if total_sales > 0 else 0
        
        # Satisfaction rate (ventes complétées / total ventes)
        satisfaction_rate = (completed_sales / total_sales * 100) if total_sales > 0 else 0
        
        # Objectif mensuel (simulé - 10000€)
        monthly_goal = 10000
        monthly_goal_progress = (total_revenue / monthly_goal * 100) if monthly_goal > 0 else 0
        
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
            "total_clicks": total_clicks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/influencer/earnings-chart
# Graphique des gains pour un influenceur
# ============================================
@router.get("/influencer/earnings-chart")
async def get_influencer_earnings_chart(influencer_id: Optional[str] = Query(None), days: int = Query(30)):
    """Graphique des commissions d'un influenceur sur X jours"""
    try:
        supabase = get_supabase_client()
        
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Récupérer les commissions
        query = supabase.table('commissions').select('amount, created_at, influencer_id')
        if influencer_id:
            query = query.eq('influencer_id', influencer_id)
        commissions = query.execute()
        
        # Grouper par jour
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
            data.append({
                "date": date_str,
                "earnings": round(day_data['amount'], 2),
                "commissions": day_data['count'],
                "formatted_date": current_date.strftime('%d/%m')
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "data": data,
            "total_days": len(data),
            "total_earnings": round(sum([d['earnings'] for d in data]), 2),
            "total_commissions": sum([d['commissions'] for d in data])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/analytics/influencer/overview
# Vue d'ensemble pour un influenceur
# ============================================
@router.get("/influencer/overview")
async def get_influencer_overview(influencer_id: Optional[str] = Query(None)):
    """Statistiques complètes pour un influenceur"""
    try:
        supabase = get_supabase_client()
        
        # Commissions totales
        comm_query = supabase.table('commissions').select('amount, created_at')
        if influencer_id:
            comm_query = comm_query.eq('influencer_id', influencer_id)
        commissions = comm_query.execute()
        
        total_earnings = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        
        # Tracking links et clics
        links_query = supabase.table('tracking_links').select('clicks, conversions')
        if influencer_id:
            links_query = links_query.eq('influencer_id', influencer_id)
        links = links_query.execute()
        
        total_clicks = sum([int(l.get('clicks', 0)) for l in (links.data or [])])
        total_conversions = sum([int(l.get('conversions', 0)) for l in (links.data or [])])
        
        # Payouts pour calculer balance
        payout_query = supabase.table('payouts').select('amount, status')
        if influencer_id:
            payout_query = payout_query.eq('influencer_id', influencer_id)
        payouts = payout_query.execute()
        
        total_withdrawn = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'paid'])
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
        recent_links = [l for l in (links.data or []) if l.get('created_at', '') >= fifteen_days_ago] # Note: tracking_links might not have created_at for clicks, assuming created_at of link or we need a clicks history table. 
        # Actually tracking_links table usually has created_at. But clicks are aggregated. 
        # If we don't have click history, we can't calculate growth accurately without a clicks table.
        # However, let's check if we can use 'conversions' table for sales growth.
        
        conversions_query = supabase.table('conversions').select('created_at')
        if influencer_id:
            conversions_query = conversions_query.eq('influencer_id', influencer_id)
        conversions_data = conversions_query.execute()
        
        recent_conv = [c for c in (conversions_data.data or []) if c.get('created_at', '') >= fifteen_days_ago]
        old_conv = [c for c in (conversions_data.data or []) if thirty_days_ago <= c.get('created_at', '') < fifteen_days_ago]
        
        sales_growth = ((len(recent_conv) - len(old_conv)) / len(old_conv) * 100) if len(old_conv) > 0 else 0
        
        # For clicks, since we only have total clicks in tracking_links, we can't easily calculate growth without a clicks history.
        # We will keep the hardcoded value for clicks_growth or set it to 0 if we can't calculate it, 
        # OR we can try to estimate it if we had a daily_stats table.
        # For now, let's leave clicks_growth as is or set to 0 to avoid misleading "5.5".
        clicks_growth = 0 
        
        return {
            "success": True,
            "total_earnings": round(total_earnings, 2),
            "total_clicks": total_clicks,
            "total_sales": total_conversions,
            "balance": round(balance, 2),
            "earnings_growth": round(earnings_growth, 2),
            "clicks_growth": round(clicks_growth, 2),
            "sales_growth": round(sales_growth, 2),
            "pending_amount": round(balance * 0.25, 2),  # Simuler montant en attente
            "total_links": len(links.data or [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
