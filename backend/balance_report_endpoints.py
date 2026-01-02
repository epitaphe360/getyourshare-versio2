"""
Balance Report Endpoints - Rapport de solde des affiliés
Endpoints pour récupérer les données de balance des influenceurs/affiliés
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from db_helpers import supabase, get_user_by_id
from auth import get_current_user_from_cookie

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/balance-report", tags=["Balance Report"])


class BalanceSummary(BaseModel):
    total_balance: float
    pending_payouts: float
    paid_payouts: float
    affiliates_with_balance: int
    total_affiliates: int
    total_commissions: float


class AffiliateBalance(BaseModel):
    id: str
    name: str
    email: str
    balance: float
    pending: float
    paid: float
    last_payout: Optional[str] = None
    status: str


@router.get("/summary")
async def get_balance_summary(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Récupère le résumé des soldes des affiliés"""
    try:
        user = get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        # Seuls les merchants et admins peuvent voir ce rapport
        if user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Récupérer tous les influenceurs
        influencers_result = supabase.table("users").select("*").eq("role", "influencer").execute()
        influencers = influencers_result.data or []
        total_affiliates = len(influencers)
        
        # Récupérer tous les payouts
        payouts_query = supabase.table("payouts").select("*")
        if start_date:
            payouts_query = payouts_query.gte("created_at", start_date)
        if end_date:
            payouts_query = payouts_query.lte("created_at", end_date + "T23:59:59")
        payouts_result = payouts_query.execute()
        payouts = payouts_result.data or []
        
        # Calculer les totaux
        pending_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") == "pending")
        paid_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "completed"])
        processing_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") == "processing")
        
        # Récupérer les commissions pour calculer le balance total
        commissions_query = supabase.table("commissions").select("amount, influencer_id, status")
        if start_date:
            commissions_query = commissions_query.gte("created_at", start_date)
        if end_date:
            commissions_query = commissions_query.lte("created_at", end_date + "T23:59:59")
        commissions_result = commissions_query.execute()
        commissions = commissions_result.data or []
        
        total_commissions = sum(float(c.get("amount", 0)) for c in commissions)
        
        # Balance = commissions - payouts payés
        total_balance = total_commissions - paid_amount
        
        # Affiliés avec un solde > 0
        affiliates_with_balance = set()
        for c in commissions:
            if c.get("influencer_id"):
                affiliates_with_balance.add(c["influencer_id"])
        
        return {
            "success": True,
            "data": {
                "total_balance": round(total_balance, 2),
                "pending_payouts": round(pending_amount + processing_amount, 2),
                "paid_payouts": round(paid_amount, 2),
                "affiliates_with_balance": len(affiliates_with_balance),
                "total_affiliates": total_affiliates,
                "total_commissions": round(total_commissions, 2),
                "period": {
                    "start": start_date,
                    "end": end_date
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/affiliates")
async def get_affiliates_balances(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Recherche par nom ou email"),
    min_balance: Optional[float] = Query(None),
    status: Optional[str] = Query(None, description="pending, active, inactive"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Liste détaillée des soldes par affilié"""
    try:
        user = get_user_by_id(current_user["id"])
        if not user or user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Récupérer tous les influenceurs
        influencers_query = supabase.table("users").select("id, username, email, full_name, first_name, last_name, status, created_at").eq("role", "influencer")
        if search:
            influencers_query = influencers_query.or_(f"username.ilike.%{search}%,email.ilike.%{search}%,full_name.ilike.%{search}%")
        influencers_result = influencers_query.execute()
        influencers = influencers_result.data or []
        
        # Récupérer payouts et commissions pour chaque influenceur
        affiliates_data = []
        
        for inf in influencers:
            inf_id = inf["id"]
            
            # Commissions de cet influenceur
            comm_query = supabase.table("commissions").select("amount, status").eq("influencer_id", inf_id)
            if start_date:
                comm_query = comm_query.gte("created_at", start_date)
            if end_date:
                comm_query = comm_query.lte("created_at", end_date + "T23:59:59")
            comm_result = comm_query.execute()
            commissions = comm_result.data or []
            total_earned = sum(float(c.get("amount", 0)) for c in commissions)
            
            # Payouts de cet influenceur
            payout_query = supabase.table("payouts").select("amount, status, created_at, paid_at").eq("influencer_id", inf_id)
            if start_date:
                payout_query = payout_query.gte("created_at", start_date)
            if end_date:
                payout_query = payout_query.lte("created_at", end_date + "T23:59:59")
            payout_result = payout_query.execute()
            payouts = payout_result.data or []
            
            paid_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "completed"])
            pending_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") == "pending")
            
            balance = total_earned - paid_amount
            
            # Dernier payout
            last_payout = None
            paid_payouts = [p for p in payouts if p.get("status") in ["paid", "completed"]]
            if paid_payouts:
                sorted_payouts = sorted(paid_payouts, key=lambda x: x.get("paid_at") or x.get("created_at") or "", reverse=True)
                if sorted_payouts:
                    last_payout = sorted_payouts[0].get("paid_at") or sorted_payouts[0].get("created_at")
            
            # Nom complet
            name = inf.get("full_name") or inf.get("username") or "Inconnu"
            if not name or name == "Inconnu":
                first = inf.get("first_name") or ""
                last = inf.get("last_name") or ""
                name = f"{first} {last}".strip() or inf.get("email", "Inconnu").split("@")[0]
            
            # Filtrer par balance minimum
            if min_balance is not None and balance < min_balance:
                continue
            
            affiliate_status = inf.get("status") or "active"
            if status and affiliate_status != status:
                continue
            
            affiliates_data.append({
                "id": inf_id,
                "name": name,
                "email": inf.get("email", ""),
                "balance": round(balance, 2),
                "total_earned": round(total_earned, 2),
                "pending": round(pending_amount, 2),
                "paid": round(paid_amount, 2),
                "last_payout": last_payout,
                "status": affiliate_status,
                "created_at": inf.get("created_at")
            })
        
        # Trier par balance décroissant
        affiliates_data.sort(key=lambda x: x["balance"], reverse=True)
        
        # Pagination
        total = len(affiliates_data)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated = affiliates_data[start_idx:end_idx]
        
        return {
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching affiliates balances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/affiliate/{affiliate_id}")
async def get_affiliate_details(
    affiliate_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Détails complets d'un affilié avec historique"""
    try:
        user = get_user_by_id(current_user["id"])
        if not user or user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Info affilié
        affiliate_result = supabase.table("users").select("*").eq("id", affiliate_id).single().execute()
        affiliate = affiliate_result.data
        if not affiliate:
            raise HTTPException(status_code=404, detail="Affilié non trouvé")
        
        # Commissions
        comm_query = supabase.table("commissions").select("*").eq("influencer_id", affiliate_id).order("created_at", desc=True)
        if start_date:
            comm_query = comm_query.gte("created_at", start_date)
        if end_date:
            comm_query = comm_query.lte("created_at", end_date + "T23:59:59")
        commissions = comm_query.execute().data or []
        
        # Payouts
        payout_query = supabase.table("payouts").select("*").eq("influencer_id", affiliate_id).order("created_at", desc=True)
        if start_date:
            payout_query = payout_query.gte("created_at", start_date)
        if end_date:
            payout_query = payout_query.lte("created_at", end_date + "T23:59:59")
        payouts = payout_query.execute().data or []
        
        # Calculs
        total_earned = sum(float(c.get("amount", 0)) for c in commissions)
        paid_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "completed"])
        pending_amount = sum(float(p.get("amount", 0)) for p in payouts if p.get("status") == "pending")
        balance = total_earned - paid_amount
        
        # Historique mensuel (derniers 12 mois)
        monthly_history = []
        now = datetime.now()
        for i in range(12):
            month_date = now - timedelta(days=30 * i)
            month_str = month_date.strftime("%Y-%m")
            month_commissions = sum(
                float(c.get("amount", 0)) 
                for c in commissions 
                if c.get("created_at", "").startswith(month_str)
            )
            month_payouts = sum(
                float(p.get("amount", 0)) 
                for p in payouts 
                if p.get("status") in ["paid", "completed"] and (p.get("paid_at") or p.get("created_at") or "").startswith(month_str)
            )
            monthly_history.append({
                "month": month_str,
                "earned": round(month_commissions, 2),
                "paid": round(month_payouts, 2)
            })
        
        name = affiliate.get("full_name") or affiliate.get("username") or "Inconnu"
        if not name or name == "Inconnu":
            first = affiliate.get("first_name") or ""
            last = affiliate.get("last_name") or ""
            name = f"{first} {last}".strip() or affiliate.get("email", "Inconnu").split("@")[0]
        
        return {
            "success": True,
            "data": {
                "affiliate": {
                    "id": affiliate_id,
                    "name": name,
                    "email": affiliate.get("email"),
                    "status": affiliate.get("status") or "active",
                    "created_at": affiliate.get("created_at"),
                    "country": affiliate.get("country"),
                    "payment_method": affiliate.get("payment_method")
                },
                "balance": {
                    "total_earned": round(total_earned, 2),
                    "total_paid": round(paid_amount, 2),
                    "pending": round(pending_amount, 2),
                    "current_balance": round(balance, 2)
                },
                "commissions": commissions[:50],  # Dernières 50
                "payouts": payouts[:50],
                "monthly_history": monthly_history
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching affiliate details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_balance_report(
    format: str = Query("csv", description="csv ou json"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Exporte le rapport de balance en CSV ou JSON"""
    try:
        from fastapi.responses import StreamingResponse
        import csv
        import io
        import json
        
        user = get_user_by_id(current_user["id"])
        if not user or user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Récupérer toutes les données
        affiliates_response = await get_affiliates_balances(
            start_date=start_date,
            end_date=end_date,
            search=None,
            min_balance=None,
            status=None,
            page=1,
            limit=1000,
            current_user=current_user
        )
        
        affiliates = affiliates_response["data"]
        
        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow([
                "ID", "Nom", "Email", "Solde", "Total Gagné", 
                "En Attente", "Payé", "Dernier Paiement", "Statut"
            ])
            
            for aff in affiliates:
                writer.writerow([
                    aff["id"],
                    aff["name"],
                    aff["email"],
                    aff["balance"],
                    aff["total_earned"],
                    aff["pending"],
                    aff["paid"],
                    aff["last_payout"] or "N/A",
                    aff["status"]
                ])
            
            output.seek(0)
            filename = f"balance_report_{datetime.now().strftime('%Y%m%d')}.csv"
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:  # JSON
            filename = f"balance_report_{datetime.now().strftime('%Y%m%d')}.json"
            content = json.dumps({
                "export_date": datetime.now().isoformat(),
                "period": {"start": start_date, "end": end_date},
                "affiliates": affiliates
            }, indent=2)
            
            return StreamingResponse(
                iter([content]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting balance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_balance_statistics(
    period: str = Query("month", description="day, week, month, year"),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Statistiques des balances pour graphiques"""
    try:
        user = get_user_by_id(current_user["id"])
        if not user or user.get("role") not in ["merchant", "admin"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        now = datetime.now()
        
        if period == "day":
            days = 7
            format_str = "%Y-%m-%d"
        elif period == "week":
            days = 28
            format_str = "%Y-%m-%d"
        elif period == "year":
            days = 365
            format_str = "%Y-%m"
        else:  # month
            days = 30
            format_str = "%Y-%m-%d"
        
        start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Récupérer commissions et payouts
        commissions = supabase.table("commissions").select("amount, created_at").gte("created_at", start_date).execute().data or []
        payouts = supabase.table("payouts").select("amount, status, created_at, paid_at").gte("created_at", start_date).execute().data or []
        
        # Grouper par période
        data_points = {}
        
        for i in range(days + 1):
            date = now - timedelta(days=days - i)
            key = date.strftime(format_str)
            if key not in data_points:
                data_points[key] = {"date": key, "commissions": 0, "payouts": 0}
        
        for c in commissions:
            if c.get("created_at"):
                key = c["created_at"][:10] if period != "year" else c["created_at"][:7]
                if key in data_points:
                    data_points[key]["commissions"] += float(c.get("amount", 0))
        
        for p in payouts:
            if p.get("status") in ["paid", "completed"]:
                date_field = p.get("paid_at") or p.get("created_at")
                if date_field:
                    key = date_field[:10] if period != "year" else date_field[:7]
                    if key in data_points:
                        data_points[key]["payouts"] += float(p.get("amount", 0))
        
        chart_data = sorted(data_points.values(), key=lambda x: x["date"])
        
        return {
            "success": True,
            "data": {
                "period": period,
                "chart_data": chart_data,
                "totals": {
                    "commissions": sum(d["commissions"] for d in chart_data),
                    "payouts": sum(d["payouts"] for d in chart_data)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
