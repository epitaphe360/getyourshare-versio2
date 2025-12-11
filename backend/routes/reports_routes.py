"""
Routes Reports COMPLÈTES avec vraie logique
Rapports détaillés et exports (sales, commissions, performance)
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv
import io

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])


# ============================================
# SUMMARY REPORTS
# ============================================

@router.get("/summary")
async def get_reports_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Résumé des rapports RÉEL (période personnalisable)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Dates par défaut (30 derniers jours)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.now().isoformat()

        # Query conversions
        if role == "influencer":
            conversions = supabase.table('conversions').select('*').eq('influencer_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
        elif role == "merchant":
            conversions = supabase.table('conversions').select('*').eq('merchant_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
        else:
            # Admin voit tout
            conversions = supabase.table('conversions').select('*').gte('created_at', start_date).lte('created_at', end_date).execute()

        conversions_data = conversions.data or []

        # Clicks
        if role == "influencer":
            clicks = supabase.table('tracking_events').select('*', count='exact').eq('user_id', user_id).eq('event_type', 'click').gte('created_at', start_date).lte('created_at', end_date).execute()
        else:
            clicks = supabase.table('tracking_events').select('*', count='exact').eq('event_type', 'click').gte('created_at', start_date).lte('created_at', end_date).execute()

        total_clicks = clicks.count if hasattr(clicks, 'count') else len(clicks.data or [])

        # Calculs
        total_conversions = len(conversions_data)
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)
        total_commissions = sum(Decimal(str(c.get('commission_amount', 0))) for c in conversions_data)

        # Conversion rate
        conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0

        # AOV (Average Order Value)
        aov = total_revenue / total_conversions if total_conversions > 0 else Decimal('0')

        return {
            "success": True,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_revenue": float(total_revenue),
                "total_commissions": float(total_commissions),
                "conversion_rate": conversion_rate,
                "average_order_value": float(aov),
                "currency": "MAD"
            }
        }

    except Exception as e:
        logger.error(f"Error getting reports summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DETAILED REPORTS
# ============================================

@router.get("/detailed")
async def get_reports_detailed(
    report_type: str = "sales",  # sales, commissions, products, affiliates
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "day",  # day, week, month
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Rapport détaillé avec groupement RÉEL
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Dates par défaut
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.now().isoformat()

        if report_type == "sales":
            # Rapport des ventes
            if role == "merchant":
                conversions = supabase.table('conversions').select('*').eq('merchant_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            elif role == "influencer":
                conversions = supabase.table('conversions').select('*').eq('influencer_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            else:
                conversions = supabase.table('conversions').select('*').gte('created_at', start_date).lte('created_at', end_date).execute()

            # Grouper par période
            grouped_data = {}
            for conv in (conversions.data or []):
                date_str = conv['created_at'][:10]  # YYYY-MM-DD

                # Groupement
                if group_by == "week":
                    date_obj = datetime.fromisoformat(conv['created_at'])
                    week_start = date_obj - timedelta(days=date_obj.weekday())
                    date_key = week_start.strftime("%Y-%W")
                elif group_by == "month":
                    date_key = conv['created_at'][:7]  # YYYY-MM
                else:
                    date_key = date_str

                if date_key not in grouped_data:
                    grouped_data[date_key] = {
                        'period': date_key,
                        'sales_count': 0,
                        'revenue': Decimal('0'),
                        'commissions': Decimal('0')
                    }

                grouped_data[date_key]['sales_count'] += 1
                grouped_data[date_key]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))
                grouped_data[date_key]['commissions'] += Decimal(str(conv.get('commission_amount', 0)))

            # Convertir en liste
            data = [
                {
                    **val,
                    'revenue': float(val['revenue']),
                    'commissions': float(val['commissions'])
                }
                for val in sorted(grouped_data.values(), key=lambda x: x['period'])
            ]

        elif report_type == "products":
            # Rapport par produit
            if role == "merchant":
                conversions = supabase.table('conversions').select('product_id, sale_amount').eq('merchant_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            else:
                conversions = supabase.table('conversions').select('product_id, sale_amount').gte('created_at', start_date).lte('created_at', end_date).execute()

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
                        'revenue': Decimal('0')
                    }

                product_stats[product_id]['sales_count'] += 1
                product_stats[product_id]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))

            # Enrichir avec noms
            data = []
            for stats in sorted(product_stats.values(), key=lambda x: x['revenue'], reverse=True):
                try:
                    product = supabase.table('products').select('name').eq('id', stats['product_id']).single().execute()
                except Exception:
                    pass  # .single() might return no results
                data.append({
                    'product_id': stats['product_id'],
                    'product_name': product.data.get('name') if product.data else None,
                    'sales_count': stats['sales_count'],
                    'revenue': float(stats['revenue'])
                })

        elif report_type == "affiliates":
            # Rapport par affilié (merchant only)
            if role != "merchant" and role != "admin":
                raise HTTPException(status_code=403, detail="Non autorisé")

            if role == "merchant":
                conversions = supabase.table('conversions').select('influencer_id, sale_amount, commission_amount').eq('merchant_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            else:
                conversions = supabase.table('conversions').select('influencer_id, sale_amount, commission_amount').gte('created_at', start_date).lte('created_at', end_date).execute()

            # Grouper par influenceur
            influencer_stats = {}
            for conv in (conversions.data or []):
                influencer_id = conv.get('influencer_id')
                if not influencer_id:
                    continue

                if influencer_id not in influencer_stats:
                    influencer_stats[influencer_id] = {
                        'influencer_id': influencer_id,
                        'sales_count': 0,
                        'revenue': Decimal('0'),
                        'commissions': Decimal('0')
                    }

                influencer_stats[influencer_id]['sales_count'] += 1
                influencer_stats[influencer_id]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))
                influencer_stats[influencer_id]['commissions'] += Decimal(str(conv.get('commission_amount', 0)))

            # Enrichir avec noms
            data = []
            for stats in sorted(influencer_stats.values(), key=lambda x: x['revenue'], reverse=True):
                try:
                    profile = supabase.table('profiles').select('full_name').eq('user_id', stats['influencer_id']).single().execute()
                except Exception:
                    pass  # .single() might return no results
                data.append({
                    'influencer_id': stats['influencer_id'],
                    'influencer_name': profile.data.get('full_name') if profile.data else None,
                    'sales_count': stats['sales_count'],
                    'revenue': float(stats['revenue']),
                    'commissions_paid': float(stats['commissions'])
                })

        elif report_type == "commissions":
            # Rapport commissions
            if role == "influencer":
                conversions = supabase.table('conversions').select('created_at, commission_amount').eq('influencer_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            else:
                conversions = supabase.table('conversions').select('created_at, commission_amount').gte('created_at', start_date).lte('created_at', end_date).execute()

            # Grouper
            grouped_data = {}
            for conv in (conversions.data or []):
                date_str = conv['created_at'][:10]

                if group_by == "week":
                    date_obj = datetime.fromisoformat(conv['created_at'])
                    week_start = date_obj - timedelta(days=date_obj.weekday())
                    date_key = week_start.strftime("%Y-%W")
                elif group_by == "month":
                    date_key = conv['created_at'][:7]
                else:
                    date_key = date_str

                if date_key not in grouped_data:
                    grouped_data[date_key] = Decimal('0')

                grouped_data[date_key] += Decimal(str(conv.get('commission_amount', 0)))

            data = [
                {'period': k, 'commissions': float(v)}
                for k, v in sorted(grouped_data.items())
            ]

        else:
            raise HTTPException(status_code=400, detail="Type de rapport invalide")

        return {
            "success": True,
            "report_type": report_type,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "group_by": group_by,
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detailed report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# EXPORT CSV
# ============================================

@router.get("/export/csv")
async def export_report_csv(
    report_type: str = "sales",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Exporter un rapport en CSV
    """
    try:
        # Récupérer les données du rapport
        detailed = await get_reports_detailed(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            payload=payload
        )

        data = detailed['data']

        if not data:
            raise HTTPException(status_code=404, detail="Aucune donnée à exporter")

        # Créer CSV
        output = io.StringIO()

        # Headers
        if data:
            headers = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        # Retourner comme téléchargement
        csv_content = output.getvalue()

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_type}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# EXPORT JSON
# ============================================

@router.get("/export/json")
async def export_report_json(
    report_type: str = "sales",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Exporter un rapport en JSON
    """
    try:
        # Récupérer les données du rapport
        detailed = await get_reports_detailed(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            payload=payload
        )

        # Retourner comme téléchargement JSON
        json_content = json.dumps(detailed, indent=2, ensure_ascii=False)

        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_type}_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))
