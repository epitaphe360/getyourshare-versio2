"""
Endpoints admin pour la gestion des paiements et demandes de retrait
"""

from fastapi import APIRouter, Query, Depends, HTTPException, Body
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from auth import get_current_user_from_cookie
from supabase_config import get_supabase_client

router = APIRouter(prefix="/api/admin", tags=["Admin Payouts"])

# ============================================
# GET /api/admin/payouts
# Liste des demandes de paiement (admin)
# ============================================
@router.get("/payouts")
async def get_admin_payouts(
    status: Optional[str] = Query(None, description="Filtrer par statut: pending, completed, rejected"),
    limit: int = Query(50, description="Nombre de paiements", ge=1, le=200),
    offset: int = Query(0, description="Offset pour pagination", ge=0),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère toutes les demandes de paiement pour l'admin
    Avec filtres et pagination
    """
    try:
        # Vérifier que l'utilisateur est admin
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

        supabase = get_supabase_client()

        # Construire la requête
        query = supabase.table('payouts')\
            .select('*, users!inner(id, email, full_name, role)')

        # Filtrer par statut si spécifié
        if status:
            query = query.eq('status', status)

        # Trier par date de création (plus récent en premier)
        query = query.order('created_at', desc=True)

        # Appliquer pagination
        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        payouts = []
        total_amount = 0

        for payout in (result.data or []):
            user_data = payout.get('users', {})

            payout_info = {
                'id': payout.get('id'),
                'user_id': payout.get('user_id'),
                'user_email': user_data.get('email', 'N/A'),
                'user_name': user_data.get('full_name', 'N/A'),
                'user_role': user_data.get('role', 'unknown'),
                'amount': float(payout.get('amount', 0)),
                'method': payout.get('method', 'bank_transfer'),
                'status': payout.get('status', 'pending'),
                'created_at': payout.get('created_at'),
                'processed_at': payout.get('processed_at'),
                'notes': payout.get('notes'),
                'payment_details': payout.get('payment_details', {})
            }

            payouts.append(payout_info)

            # Calculer le total des montants
            if payout.get('status') == 'pending':
                total_amount += float(payout.get('amount', 0))

        # Compter le total de paiements en attente
        pending_count_result = supabase.table('payouts')\
            .select('id', count='exact')\
            .eq('status', 'pending')\
            .execute()

        return {
            "success": True,
            "payouts": payouts,
            "count": len(payouts),
            "total_pending": pending_count_result.count or 0,
            "total_pending_amount": round(total_amount, 2),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(payouts) == limit
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur get_admin_payouts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des paiements: {str(e)}")


# ============================================
# GET /api/admin/payouts/{payout_id}
# Détails d'une demande de paiement
# ============================================
@router.get("/payouts/{payout_id}")
async def get_payout_details(
    payout_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Récupère les détails d'une demande de paiement"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

        supabase = get_supabase_client()

        result = supabase.table('payouts')\
            .select('*, users!inner(id, email, full_name, role, phone)')\
            .eq('id', payout_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Paiement non trouvé")

        payout = result.data
        user_data = payout.get('users', {})

        return {
            "success": True,
            "payout": {
                'id': payout.get('id'),
                'user': {
                    'id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'full_name': user_data.get('full_name'),
                    'role': user_data.get('role'),
                    'phone': user_data.get('phone')
                },
                'amount': float(payout.get('amount', 0)),
                'method': payout.get('method'),
                'status': payout.get('status'),
                'created_at': payout.get('created_at'),
                'processed_at': payout.get('processed_at'),
                'notes': payout.get('notes'),
                'payment_details': payout.get('payment_details', {}),
                'rejection_reason': payout.get('rejection_reason')
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# POST /api/admin/payouts/{payout_id}/approve
# Approuver une demande de paiement
# ============================================
@router.post("/payouts/{payout_id}/approve")
async def approve_payout(
    payout_id: str,
    notes: Optional[str] = Body(None, embed=True),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Approuver et marquer comme complété une demande de paiement"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

        supabase = get_supabase_client()

        # Récupérer le paiement
        payout_result = supabase.table('payouts')\
            .select('*')\
            .eq('id', payout_id)\
            .single()\
            .execute()

        if not payout_result.data:
            raise HTTPException(status_code=404, detail="Paiement non trouvé")

        # Vérifier que le statut est pending
        if payout_result.data.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Ce paiement a déjà été traité")

        # Mettre à jour le statut
        update_result = supabase.table('payouts')\
            .update({
                'status': 'completed',
                'processed_at': datetime.utcnow().isoformat(),
                'processed_by': current_user.get('id'),
                'notes': notes or payout_result.data.get('notes')
            })\
            .eq('id', payout_id)\
            .execute()

        return {
            "success": True,
            "message": "Paiement approuvé avec succès",
            "payout": update_result.data[0] if update_result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# POST /api/admin/payouts/{payout_id}/reject
# Rejeter une demande de paiement
# ============================================
@router.post("/payouts/{payout_id}/reject")
async def reject_payout(
    payout_id: str,
    reason: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Rejeter une demande de paiement"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

        if not reason:
            raise HTTPException(status_code=400, detail="La raison du rejet est obligatoire")

        supabase = get_supabase_client()

        # Récupérer le paiement
        payout_result = supabase.table('payouts')\
            .select('*')\
            .eq('id', payout_id)\
            .single()\
            .execute()

        if not payout_result.data:
            raise HTTPException(status_code=404, detail="Paiement non trouvé")

        # Vérifier que le statut est pending
        if payout_result.data.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Ce paiement a déjà été traité")

        # Mettre à jour le statut
        update_result = supabase.table('payouts')\
            .update({
                'status': 'rejected',
                'processed_at': datetime.utcnow().isoformat(),
                'processed_by': current_user.get('id'),
                'rejection_reason': reason
            })\
            .eq('id', payout_id)\
            .execute()

        return {
            "success": True,
            "message": "Paiement rejeté",
            "payout": update_result.data[0] if update_result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# GET /api/admin/payouts/stats
# Statistiques des paiements
# ============================================
@router.get("/payouts/stats")
async def get_payouts_stats(
    days: int = Query(30, description="Nombre de jours", ge=1, le=365),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Statistiques des paiements sur une période"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

        supabase = get_supabase_client()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Paiements par statut
        all_payouts = supabase.table('payouts')\
            .select('status, amount')\
            .gte('created_at', start_date)\
            .execute()

        stats_by_status = {
            'pending': {'count': 0, 'amount': 0},
            'completed': {'count': 0, 'amount': 0},
            'rejected': {'count': 0, 'amount': 0}
        }

        for payout in (all_payouts.data or []):
            status = payout.get('status', 'pending')
            amount = float(payout.get('amount', 0))

            if status in stats_by_status:
                stats_by_status[status]['count'] += 1
                stats_by_status[status]['amount'] += amount

        return {
            "success": True,
            "period_days": days,
            "stats": {
                "pending": {
                    "count": stats_by_status['pending']['count'],
                    "total_amount": round(stats_by_status['pending']['amount'], 2)
                },
                "completed": {
                    "count": stats_by_status['completed']['count'],
                    "total_amount": round(stats_by_status['completed']['amount'], 2)
                },
                "rejected": {
                    "count": stats_by_status['rejected']['count'],
                    "total_amount": round(stats_by_status['rejected']['amount'], 2)
                },
                "total": {
                    "count": sum(s['count'] for s in stats_by_status.values()),
                    "amount": round(sum(s['amount'] for s in stats_by_status.values()), 2)
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
