"""
Routes Campaigns COMPLÈTES avec vraie logique
Gestion complète des campagnes marketing/affiliation
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


# ============================================
# MODELS
# ============================================

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: str = "affiliate"  # affiliate, influencer, email, social
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    target_audience: Optional[Dict] = None
    products: Optional[List[str]] = []  # Liste de product_ids
    commission_boost: Optional[float] = None  # Bonus de commission en %
    metadata: Optional[Dict] = {}


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    target_audience: Optional[Dict] = None
    products: Optional[List[str]] = None
    commission_boost: Optional[float] = None
    metadata: Optional[Dict] = None


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.get("")
async def get_campaigns(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,  # active, paused, completed, scheduled
    campaign_type: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des campagnes avec filtres RÉELS
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Query de base
        query = supabase.table("campaigns").select("*", count="exact")

        # Filtre par créateur (sauf admin)
        if role != "admin":
            query = query.eq("created_by", user_id)

        # Filtres optionnels
        if status:
            query = query.eq("status", status)

        if campaign_type:
            query = query.eq("campaign_type", campaign_type)

        # Pagination
        query = query.range(offset, offset + limit - 1)
        query = query.order("created_at", desc=True)

        response = query.execute()

        # Enrichir avec des stats pour chaque campagne
        campaigns = response.data or []
        for campaign in campaigns:
            campaign_id = campaign.get('id')

            # Compter les conversions liées à cette campagne
            conversions = supabase.table('conversions').select('*', count='exact').eq('campaign_id', campaign_id).execute()
            total_conversions = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])

            conversions_data = conversions.data or []
            total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)

            campaign['stats'] = {
                'conversions': total_conversions,
                'revenue': float(total_revenue),
                'currency': 'MAD'
            }

        return {
            "success": True,
            "campaigns": campaigns,
            "total": response.count if hasattr(response, 'count') else len(campaigns),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}")
async def get_campaign_details(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Détails complets d'une campagne
    """
    try:
        response = supabase.table("campaigns").select("*").eq("id", campaign_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")

        campaign = response.data

        # Stats complètes
        conversions = supabase.table('conversions').select('*').eq('campaign_id', campaign_id).execute()
        conversions_data = conversions.data or []

        total_conversions = len(conversions_data)
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)

        # Compter les clicks (tracking_events)
        clicks = supabase.table('tracking_events').select('*', count='exact').eq('campaign_id', campaign_id).eq('event_type', 'click').execute()
        total_clicks = clicks.count if hasattr(clicks, 'count') else len(clicks.data or [])

        # Conversion rate
        conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0

        # Budget vs dépenses (basé sur commissions payées)
        total_commissions = sum(Decimal(str(c.get('commission_amount', 0))) for c in conversions_data)

        campaign['stats'] = {
            'clicks': total_clicks,
            'conversions': total_conversions,
            'revenue': float(total_revenue),
            'conversion_rate': conversion_rate,
            'total_commissions_paid': float(total_commissions),
            'budget': campaign.get('budget', 0),
            'budget_remaining': float(Decimal(str(campaign.get('budget', 0))) - total_commissions) if campaign.get('budget') else None,
            'currency': 'MAD'
        }

        return {
            "success": True,
            **campaign
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_campaign(
    campaign: CampaignCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une nouvelle campagne
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # SECURITY: Only merchants can create campaigns
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can create campaigns. Influencers and commercials cannot create campaigns."
            )

        campaign_data = campaign.dict()
        campaign_data['created_by'] = user_id

        # Déterminer le statut initial
        now = datetime.now()
        start_date = campaign.start_date or now

        if start_date > now:
            status = "scheduled"
        elif campaign.end_date and campaign.end_date < now:
            status = "completed"
        else:
            status = "active"

        campaign_data['status'] = status

        response = supabase.table("campaigns").insert(campaign_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création de la campagne")

        return {
            "success": True,
            "campaign": response.data[0],
            "message": "Campagne créée avec succès"
        }

    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{campaign_id}")
async def edit_campaign(
    campaign_id: str,
    campaign: CampaignUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Modifier une campagne
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            existing = supabase.table("campaigns").select("created_by").eq("id", campaign_id).single().execute()
            if not existing.data or existing.data.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Mettre à jour
        update_data = {k: v for k, v in campaign.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        response = supabase.table("campaigns").update(update_data).eq("id", campaign_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")

        return {
            "success": True,
            "campaign": response.data[0],
            "message": "Campagne mise à jour"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre en pause une campagne
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            existing = supabase.table("campaigns").select("created_by").eq("id", campaign_id).single().execute()
            if not existing.data or existing.data.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        response = supabase.table("campaigns").update({"status": "paused"}).eq("id", campaign_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")

        return {
            "success": True,
            "status": "paused",
            "message": "Campagne mise en pause"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Reprendre une campagne en pause
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            existing = supabase.table("campaigns").select("created_by, status").eq("id", campaign_id).single().execute()
            if not existing.data or existing.data.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

            if existing.data.get('status') != "paused":
                raise HTTPException(status_code=400, detail="La campagne n'est pas en pause")

        response = supabase.table("campaigns").update({"status": "active"}).eq("id", campaign_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")

        return {
            "success": True,
            "status": "active",
            "message": "Campagne reprise"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Supprimer une campagne (soft delete: status = deleted)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            existing = supabase.table("campaigns").select("created_by").eq("id", campaign_id).single().execute()
            if not existing.data or existing.data.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Soft delete
        response = supabase.table("campaigns").update({"status": "deleted"}).eq("id", campaign_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")

        return {
            "success": True,
            "message": "Campagne supprimée"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ANALYTICS
# ============================================

@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Analytics détaillées d'une campagne RÉELLES
    """
    try:
        # Calculer période
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        else:
            days = 30

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Récupérer les conversions de la campagne
        conversions = supabase.table('conversions').select('*').eq('campaign_id', campaign_id).gte('created_at', start_date).execute()
        conversions_data = conversions.data or []

        total_conversions = len(conversions_data)
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)
        total_commissions = sum(Decimal(str(c.get('commission_amount', 0))) for c in conversions_data)

        # Clicks
        clicks = supabase.table('tracking_events').select('*', count='exact').eq('campaign_id', campaign_id).eq('event_type', 'click').gte('created_at', start_date).execute()
        total_clicks = clicks.count if hasattr(clicks, 'count') else len(clicks.data or [])

        # Views
        views = supabase.table('tracking_events').select('*', count='exact').eq('campaign_id', campaign_id).eq('event_type', 'view').gte('created_at', start_date).execute()
        total_views = views.count if hasattr(views, 'count') else len(views.data or [])

        # Tendances par jour
        daily_data = {}
        for conv in conversions_data:
            date_str = conv['created_at'][:10]
            if date_str not in daily_data:
                daily_data[date_str] = {'conversions': 0, 'revenue': Decimal('0')}

            daily_data[date_str]['conversions'] += 1
            daily_data[date_str]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))

        trend_data = [
            {
                "date": date,
                "conversions": data['conversions'],
                "revenue": float(data['revenue'])
            }
            for date, data in sorted(daily_data.items())
        ]

        # Top produits de la campagne
        product_stats = {}
        for conv in conversions_data:
            product_id = conv.get('product_id')
            if product_id:
                if product_id not in product_stats:
                    product_stats[product_id] = {'sales': 0, 'revenue': Decimal('0')}

                product_stats[product_id]['sales'] += 1
                product_stats[product_id]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))

        top_products = sorted(
            [{'product_id': pid, **stats} for pid, stats in product_stats.items()],
            key=lambda x: x['revenue'],
            reverse=True
        )[:5]

        # Enrichir avec noms de produits
        for product in top_products:
            try:
                product_data = supabase.table('products').select('name').eq('id', product['product_id']).single().execute()
            except Exception:
                pass  # .single() might return no results
            if product_data.data:
                product['product_name'] = product_data.data.get('name')
            product['revenue'] = float(product['revenue'])

        # Conversion rate
        conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0
        click_rate = round((total_clicks / total_views * 100), 2) if total_views > 0 else 0

        return {
            "success": True,
            "campaign_id": campaign_id,
            "period": period,
            "summary": {
                "views": total_views,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "revenue": float(total_revenue),
                "commissions_paid": float(total_commissions),
                "click_rate": click_rate,
                "conversion_rate": conversion_rate,
                "avg_order_value": float(total_revenue / total_conversions) if total_conversions > 0 else 0,
                "currency": "MAD"
            },
            "trends": trend_data,
            "top_products": top_products
        }

    except Exception as e:
        logger.error(f"Error getting campaign analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PARTICIPANTS (Influenceurs de la campagne)
# ============================================

@router.get("/{campaign_id}/participants")
async def get_campaign_participants(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des influenceurs participant à cette campagne
    """
    try:
        # Récupérer les conversions uniques par influenceur
        conversions = supabase.table('conversions').select('influencer_id, sale_amount, commission_amount').eq('campaign_id', campaign_id).execute()

        # Grouper par influenceur
        influencer_stats = {}
        for conv in (conversions.data or []):
            influencer_id = conv.get('influencer_id')
            if not influencer_id:
                continue

            if influencer_id not in influencer_stats:
                influencer_stats[influencer_id] = {
                    'sales_count': 0,
                    'total_revenue': Decimal('0'),
                    'total_commission': Decimal('0')
                }

            influencer_stats[influencer_id]['sales_count'] += 1
            influencer_stats[influencer_id]['total_revenue'] += Decimal(str(conv.get('sale_amount', 0)))
            influencer_stats[influencer_id]['total_commission'] += Decimal(str(conv.get('commission_amount', 0)))

        # Enrichir avec infos influenceurs
        participants = []
        for influencer_id, stats in influencer_stats.items():
            try:
                user_data = supabase.table('users').select('email').eq('id', influencer_id).single().execute()
            except Exception:
                pass  # .single() might return no results
            try:
                profile_data = supabase.table('profiles').select('full_name').eq('user_id', influencer_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            participants.append({
                'influencer_id': influencer_id,
                'name': profile_data.data.get('full_name') if profile_data.data else None,
                'email': user_data.data.get('email') if user_data.data else None,
                'sales_count': stats['sales_count'],
                'total_revenue': float(stats['total_revenue']),
                'total_commission': float(stats['total_commission'])
            })

        # Trier par revenue
        participants.sort(key=lambda x: x['total_revenue'], reverse=True)

        return {
            "success": True,
            "campaign_id": campaign_id,
            "participants": participants,
            "total_participants": len(participants)
        }

    except Exception as e:
        logger.error(f"Error getting campaign participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))
