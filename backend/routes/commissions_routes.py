"""
Routes Commissions COMPLÈTES avec calcul réel
Calcul automatique des commissions (standard + MLM + boost campagne)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from decimal import Decimal
from datetime import datetime

from auth import get_current_user_from_cookie
from db_helpers import supabase
from services.mlm_service import MLMService

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/commissions", tags=["Commissions"])

# Initialize MLM service
mlm_service = MLMService(supabase)


# ============================================
# MODELS
# ============================================

class CommissionCalculateRequest(BaseModel):
    product_id: str
    sale_amount: float
    influencer_id: Optional[str] = None
    campaign_id: Optional[str] = None


# ============================================
# CALCULATE COMMISSION
# ============================================

@router.post("/calculate")
async def calculate_commission(
    request: CommissionCalculateRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Calculer la commission pour une vente RÉELLE

    Prend en compte:
    1. Taux de commission du produit
    2. Boost de commission de la campagne (si applicable)
    3. Commission plateforme (5%)
    4. Commissions MLM (cascade 10 niveaux)

    Retourne le breakdown complet
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        influencer_id = request.influencer_id or user_id

        sale_amount = Decimal(str(request.sale_amount))

        # Récupérer le produit
        product = supabase.table('products').select('commission_rate, merchant_id').eq('id', request.product_id).single().execute()

        if not product.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        base_commission_rate = Decimal(str(product.data.get('commission_rate', 10)))  # Default 10%
        merchant_id = product.data.get('merchant_id')

        # Commission de base
        base_commission = (sale_amount * base_commission_rate) / 100

        # Vérifier si campagne avec boost
        campaign_boost = Decimal('0')
        if request.campaign_id:
            try:
                campaign = supabase.table('campaigns').select('commission_boost').eq('id', request.campaign_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            if campaign.data and campaign.data.get('commission_boost'):
                campaign_boost = Decimal(str(campaign.data['commission_boost']))

        # Commission totale influenceur (base + boost)
        total_boost_rate = base_commission_rate + campaign_boost
        influencer_commission = (sale_amount * total_boost_rate) / 100

        # Commission plateforme (5% du sale_amount)
        platform_commission_rate = Decimal('5')
        platform_commission = (sale_amount * platform_commission_rate) / 100

        # MLM Commissions (calculer cascade)
        mlm_commissions = []
        try:
            mlm_result = mlm_service.calculate_mlm_commission(
                sale_id=None,  # Pas encore de sale_id
                sale_amount=float(sale_amount),
                seller_id=influencer_id
            )
            mlm_commissions = mlm_result.get('commissions', [])
        except Exception as e:
            logger.warning(f"MLM calculation failed: {e}")

        # Total MLM
        total_mlm_commission = sum(Decimal(str(c['amount'])) for c in mlm_commissions)

        # Ce que le merchant reçoit
        merchant_receives = sale_amount - influencer_commission - platform_commission - total_mlm_commission

        return {
            "success": True,
            "sale_amount": float(sale_amount),
            "currency": "MAD",
            "breakdown": {
                "base_commission_rate": float(base_commission_rate),
                "campaign_boost_rate": float(campaign_boost),
                "total_commission_rate": float(total_boost_rate),
                "influencer_commission": float(influencer_commission),
                "platform_commission": float(platform_commission),
                "platform_rate": float(platform_commission_rate),
                "mlm_total": float(total_mlm_commission),
                "mlm_commissions": mlm_commissions,
                "merchant_receives": float(merchant_receives)
            },
            "merchant_id": merchant_id,
            "influencer_id": influencer_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating commission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# USER COMMISSIONS
# ============================================

@router.get("/my-earnings")
async def get_my_earnings(
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Earnings de l'utilisateur connecté (commissions + MLM)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Calculer période
        from datetime import timedelta
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "all":
            days = 3650  # 10 ans
        else:
            days = 30

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Commissions directes (influenceur)
        direct_conversions = supabase.table('conversions').select('commission_amount, created_at').eq('influencer_id', user_id).gte('created_at', start_date).execute()

        direct_data = direct_conversions.data or []
        total_direct = sum(Decimal(str(c.get('commission_amount', 0))) for c in direct_data)

        # Commissions MLM
        mlm_commissions = supabase.table('mlm_commissions').select('amount, created_at').eq('upline_id', user_id).gte('created_at', start_date).execute()

        mlm_data = mlm_commissions.data or []
        total_mlm = sum(Decimal(str(c.get('amount', 0))) for c in mlm_data)

        # Total
        total_earnings = total_direct + total_mlm

        # Déjà payé (payouts)
        payouts = supabase.table('payouts').select('amount').eq('influencer_id', user_id).eq('status', 'completed').gte('created_at', start_date).execute()

        payouts_data = payouts.data or []
        total_paid = sum(Decimal(str(p.get('amount', 0))) for p in payouts_data)

        # Pending
        pending = total_earnings - total_paid

        return {
            "success": True,
            "period": period,
            "earnings": {
                "direct_commissions": float(total_direct),
                "mlm_commissions": float(total_mlm),
                "total_earned": float(total_earnings),
                "already_paid": float(total_paid),
                "pending": float(pending),
                "currency": "MAD"
            }
        }

    except Exception as e:
        logger.error(f"Error getting my earnings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_commission_history(
    limit: int = 20,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Historique des commissions (directes + MLM)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Commissions directes
        direct = supabase.table('conversions').select('id, sale_amount, commission_amount, created_at, product_id').eq('influencer_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        direct_history = []
        for conv in (direct.data or []):
            direct_history.append({
                'type': 'direct',
                'amount': conv.get('commission_amount'),
                'sale_amount': conv.get('sale_amount'),
                'product_id': conv.get('product_id'),
                'created_at': conv.get('created_at')
            })

        # Commissions MLM
        mlm = supabase.table('mlm_commissions').select('amount, level, downline_id, sale_id, created_at').eq('upline_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        mlm_history = []
        for comm in (mlm.data or []):
            mlm_history.append({
                'type': 'mlm',
                'amount': comm.get('amount'),
                'level': comm.get('level'),
                'downline_id': comm.get('downline_id'),
                'created_at': comm.get('created_at')
            })

        # Merger et trier par date
        all_history = direct_history + mlm_history
        all_history.sort(key=lambda x: x['created_at'], reverse=True)

        return {
            "success": True,
            "history": all_history[:limit],
            "total": len(all_history)
        }

    except Exception as e:
        logger.error(f"Error getting commission history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TAX CALCULATION
# ============================================

@router.post("/tax/calculate")
async def calculate_tax(
    amount: float,
    country: str = "MA",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Calculer les taxes sur un montant

    Maroc (MA): TVA 20%
    France (FR): TVA 20%
    USA (US): Varie par état (moyenne 8%)
    """
    try:
        amount_decimal = Decimal(str(amount))

        # Taux de TVA par pays
        tax_rates = {
            "MA": Decimal('20'),  # Maroc
            "FR": Decimal('20'),  # France
            "US": Decimal('8'),   # USA (moyenne)
            "default": Decimal('0')
        }

        tax_rate = tax_rates.get(country, tax_rates['default'])
        tax_amount = (amount_decimal * tax_rate) / 100
        total_with_tax = amount_decimal + tax_amount

        return {
            "success": True,
            "amount": float(amount_decimal),
            "tax_rate": float(tax_rate),
            "tax_amount": float(tax_amount),
            "total_with_tax": float(total_with_tax),
            "country": country,
            "currency": "MAD" if country == "MA" else ("EUR" if country == "FR" else "USD")
        }

    except Exception as e:
        logger.error(f"Error calculating tax: {e}")
        raise HTTPException(status_code=500, detail=str(e))
