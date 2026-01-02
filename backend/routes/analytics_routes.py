"""
Routes Analytics COMPLÈTES avec vraie logique
Remplace les stubs de missing_endpoints.py
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/performance")
async def get_analytics_performance(
    period: str = "7d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Performance analytics RÉELLE (pas stub)

    Calcule: clicks, conversions, revenue, conversion_rate
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Calculer la date de début selon la période
        if period == "7d":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.now() - timedelta(days=30)
        elif period == "90d":
            start_date = datetime.now() - timedelta(days=90)
        else:
            start_date = datetime.now() - timedelta(days=7)

        start_date_str = start_date.isoformat()

        # Récupérer les clicks (tracking_events)
        clicks_query = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'click').gte('created_at', start_date_str)
        clicks_result = clicks_query.execute()
        total_clicks = clicks_result.count if hasattr(clicks_result, 'count') else len(clicks_result.data or [])

        # Récupérer les conversions
        if role == "influencer":
            conversions_result = supabase.table('conversions').select('*', count='exact').eq('influencer_id', user_id).gte('created_at', start_date_str).execute()
        else:
            conversions_result = supabase.table('conversions').select('*', count='exact').eq('merchant_id', user_id).gte('created_at', start_date_str).execute()

        total_conversions = conversions_result.count if hasattr(conversions_result, 'count') else len(conversions_result.data or [])

        # Calculer le revenue
        conversions_data = conversions_result.data or []
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)

        # Conversion rate
        conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0

        return {
            "success": True,
            "period": period,
            "clicks": total_clicks,
            "conversions": total_conversions,
            "revenue": float(total_revenue),
            "conversion_rate": conversion_rate,
            "currency": "MAD"
        }

    except Exception as e:
        logger.error(f"Error getting analytics performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_analytics_trends(
    metric: str = "clicks",
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Tendances temporelles RÉELLES

    Retourne les données par jour/semaine
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Calculer période
        if period == "7d":
            start_date = datetime.now() - timedelta(days=7)
            granularity = "day"
        elif period == "30d":
            start_date = datetime.now() - timedelta(days=30)
            granularity = "day"
        else:
            start_date = datetime.now() - timedelta(days=90)
            granularity = "week"

        start_date_str = start_date.isoformat()

        # Récupérer les données selon la métrique
        if metric == "clicks":
            data = supabase.table('tracking_events').select('created_at').eq('user_id', user_id).eq('event_type', 'click').gte('created_at', start_date_str).execute()
        elif metric == "conversions":
            if role == "influencer":
                data = supabase.table('conversions').select('created_at, sale_amount').eq('influencer_id', user_id).gte('created_at', start_date_str).execute()
            else:
                data = supabase.table('conversions').select('created_at, sale_amount').eq('merchant_id', user_id).gte('created_at', start_date_str).execute()
        elif metric == "revenue":
            if role == "influencer":
                data = supabase.table('conversions').select('created_at, sale_amount').eq('influencer_id', user_id).gte('created_at', start_date_str).execute()
            else:
                data = supabase.table('conversions').select('created_at, sale_amount').eq('merchant_id', user_id).gte('created_at', start_date_str).execute()
        else:
            raise ValueError("Invalid metric")

        # Grouper par jour
        daily_data = {}
        for item in (data.data or []):
            date_str = item['created_at'][:10]  # YYYY-MM-DD

            if date_str not in daily_data:
                daily_data[date_str] = 0

            if metric == "revenue":
                daily_data[date_str] += float(item.get('sale_amount', 0))
            else:
                daily_data[date_str] += 1

        # Convertir en liste triée
        trend_data = [
            {"date": date, "value": value}
            for date, value in sorted(daily_data.items())
        ]

        # Déterminer la tendance (croissant/stable/décroissant)
        if len(trend_data) >= 2:
            first_half = sum(d['value'] for d in trend_data[:len(trend_data)//2])
            second_half = sum(d['value'] for d in trend_data[len(trend_data)//2:])

            if second_half > first_half * 1.1:
                trend = "increasing"
            elif second_half < first_half * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "success": True,
            "metric": metric,
            "period": period,
            "data": trend_data,
            "trend": trend
        }

    except Exception as e:
        logger.error(f"Error getting analytics trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-trends")
async def get_revenue_trends(
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """Tendances des revenus"""
    return await get_analytics_trends(metric="revenue", period=period, payload=payload)


@router.get("/top-products")
async def get_top_products(
    limit: int = 5,
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Produits les plus performants RÉELS
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Calculer période
        if period == "7d":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=90)

        start_date_str = start_date.isoformat()

        # Récupérer les conversions avec produits
        conversions = supabase.table('conversions').select('product_id, sale_amount').eq('merchant_id', user_id).gte('created_at', start_date_str).execute()

        # Grouper par produit
        product_stats = {}
        for conv in (conversions.data or []):
            product_id = conv.get('product_id')
            if not product_id:
                continue

            if product_id not in product_stats:
                product_stats[product_id] = {
                    'product_id': product_id,
                    'sales_count': 0,
                    'total_revenue': Decimal('0')
                }

            product_stats[product_id]['sales_count'] += 1
            product_stats[product_id]['total_revenue'] += Decimal(str(conv.get('sale_amount', 0)))

        # Trier par revenue
        sorted_products = sorted(
            product_stats.values(),
            key=lambda x: x['total_revenue'],
            reverse=True
        )[:limit]

        # Enrichir avec les infos produits
        result = []
        for stat in sorted_products:
            try:
                product = supabase.table('products').select('id, name, price, image_url').eq('id', stat['product_id']).single().execute()
            except Exception:
                pass  # .single() might return no results

            if product.data:
                result.append({
                    **product.data,
                    'sales_count': stat['sales_count'],
                    'total_revenue': float(stat['total_revenue'])
                })

        return {
            "success": True,
            "period": period,
            "products": result
        }

    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-funnel")
async def get_conversion_funnel(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Entonnoir de conversion RÉEL
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Derniers 30 jours
        start_date = (datetime.now() - timedelta(days=30)).isoformat()

        # 1. Views (tracking_events type=view)
        views = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'view').gte('created_at', start_date).execute()
        total_views = views.count if hasattr(views, 'count') else len(views.data or [])

        # 2. Clicks (tracking_events type=click)
        clicks = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'click').gte('created_at', start_date).execute()
        total_clicks = clicks.count if hasattr(clicks, 'count') else len(clicks.data or [])

        # 3. Add to cart (tracking_events type=add_to_cart)
        add_to_cart = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'add_to_cart').gte('created_at', start_date).execute()
        total_add_to_cart = add_to_cart.count if hasattr(add_to_cart, 'count') else len(add_to_cart.data or [])

        # 4. Purchases (conversions)
        purchases = supabase.table('conversions').select('*', count='exact').eq('influencer_id', user_id).gte('created_at', start_date).execute()
        total_purchases = purchases.count if hasattr(purchases, 'count') else len(purchases.data or [])

        # Calculs taux
        click_rate = round((total_clicks / total_views * 100), 2) if total_views > 0 else 0
        cart_rate = round((total_add_to_cart / total_clicks * 100), 2) if total_clicks > 0 else 0
        purchase_rate = round((total_purchases / total_add_to_cart * 100), 2) if total_add_to_cart > 0 else 0

        return {
            "success": True,
            "funnel": {
                "views": total_views,
                "clicks": total_clicks,
                "add_to_cart": total_add_to_cart,
                "purchases": total_purchases
            },
            "rates": {
                "click_rate": click_rate,
                "cart_rate": cart_rate,
                "purchase_rate": purchase_rate,
                "overall_conversion": round((total_purchases / total_views * 100), 2) if total_views > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting conversion funnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audience-demographics")
async def get_audience_demographics(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Démographie de l'audience RÉELLE
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les conversions avec user info
        conversions = supabase.table('conversions').select('customer_id').eq('influencer_id', user_id).execute()

        customer_ids = list(set([c['customer_id'] for c in (conversions.data or []) if c.get('customer_id')]))

        if not customer_ids:
            return {
                "success": True,
                "age_groups": {},
                "gender": {},
                "locations": {}
            }

        # Récupérer les profiles des customers
        profiles = supabase.table('profiles').select('age, gender, city').in_('user_id', customer_ids).execute()

        # Grouper par âge
        age_groups = {'18-24': 0, '25-34': 0, '35-44': 0, '45+': 0}
        gender_stats = {'male': 0, 'female': 0, 'other': 0}
        locations = {}

        for profile in (profiles.data or []):
            # Age
            age = profile.get('age')
            if age:
                if 18 <= age <= 24:
                    age_groups['18-24'] += 1
                elif 25 <= age <= 34:
                    age_groups['25-34'] += 1
                elif 35 <= age <= 44:
                    age_groups['35-44'] += 1
                else:
                    age_groups['45+'] += 1

            # Gender
            gender = profile.get('gender', 'other')
            if gender in gender_stats:
                gender_stats[gender] += 1

            # Location
            city = profile.get('city')
            if city:
                locations[city] = locations.get(city, 0) + 1

        # Top 5 locations
        top_locations = dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5])

        return {
            "success": True,
            "age_groups": age_groups,
            "gender": gender_stats,
            "locations": top_locations
        }

    except Exception as e:
        logger.error(f"Error getting audience demographics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement-metrics")
async def get_engagement_metrics(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Métriques d'engagement RÉELLES
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        start_date = (datetime.now() - timedelta(days=30)).isoformat()

        # Likes (tracking_events type=like)
        likes = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'like').gte('created_at', start_date).execute()
        total_likes = likes.count if hasattr(likes, 'count') else len(likes.data or [])

        # Shares (tracking_events type=share)
        shares = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'share').gte('created_at', start_date).execute()
        total_shares = shares.count if hasattr(shares, 'count') else len(shares.data or [])

        # Comments (tracking_events type=comment)
        comments = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'comment').gte('created_at', start_date).execute()
        total_comments = comments.count if hasattr(comments, 'count') else len(comments.data or [])

        # Avg time on page (from tracking_events metadata)
        page_views = supabase.table('tracking_events').select('metadata').eq('user_id', user_id).eq('event_type', 'page_view').gte('created_at', start_date).execute()

        total_time = 0
        count = 0
        for pv in (page_views.data or []):
            metadata = pv.get('metadata', {})
            if isinstance(metadata, dict):
                time_spent = metadata.get('time_spent_seconds', 0)
                if time_spent > 0:
                    total_time += time_spent
                    count += 1

        avg_time_seconds = round(total_time / count) if count > 0 else 0
        avg_time_display = f"{avg_time_seconds // 60}m {avg_time_seconds % 60}s"

        return {
            "success": True,
            "likes": total_likes,
            "shares": total_shares,
            "comments": total_comments,
            "avg_time_on_page": avg_time_display,
            "avg_time_seconds": avg_time_seconds
        }

    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ltv")
async def get_ltv(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Lifetime Value RÉEL
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Récupérer toutes les conversions
        if role == "influencer":
            conversions = supabase.table('conversions').select('customer_id, sale_amount, commission_amount').eq('influencer_id', user_id).execute()
        else:
            conversions = supabase.table('conversions').select('customer_id, sale_amount, commission_amount').eq('merchant_id', user_id).execute()

        # Grouper par customer
        customer_ltv = {}
        for conv in (conversions.data or []):
            customer_id = conv.get('customer_id')
            if not customer_id:
                continue

            if customer_id not in customer_ltv:
                customer_ltv[customer_id] = Decimal('0')

            customer_ltv[customer_id] += Decimal(str(conv.get('sale_amount', 0)))

        # Calculer moyenne
        if customer_ltv:
            avg_ltv = sum(customer_ltv.values()) / len(customer_ltv)
        else:
            avg_ltv = Decimal('0')

        return {
            "success": True,
            "ltv": float(avg_ltv),
            "currency": "MAD",
            "total_customers": len(customer_ltv)
        }

    except Exception as e:
        logger.error(f"Error calculating LTV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
