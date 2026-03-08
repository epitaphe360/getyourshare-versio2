"""
TRANSACTION ENDPOINTS - Gestion des transactions de paiement
Table utilisée: gateway_transactions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from supabase_config import get_supabase_client

router = APIRouter()

# ============================================
# MODELS
# ============================================

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    transaction_type: str
    amount: float
    currency: str
    status: str
    gateway: str
    gateway_transaction_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

class ProcessTransactionRequest(BaseModel):
    user_id: str
    transaction_type: str
    amount: float
    currency: str = "EUR"
    gateway: str = "stripe"
    metadata: Optional[dict] = None

# ============================================
# GET /api/transactions/history
# Historique des transactions
# ============================================
@router.get("/history")
async def get_transaction_history(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    transaction_type: Optional[str] = Query(None, description="Type de transaction"),
    status: Optional[str] = Query(None, description="Statut"),
    gateway: Optional[str] = Query(None, description="Gateway"),
    limit: int = Query(50, description="Nombre de transactions"),
    offset: int = Query(0, description="Offset pour pagination")
):
    """Récupère l'historique des transactions d'un utilisateur"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('user_id', user_id)
        
        if transaction_type:
            query = query.eq('transaction_type', transaction_type)
        if status:
            query = query.eq('status', status)
        if gateway:
            query = query.eq('gateway', gateway)
        
        response = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Calculer totaux
        total_amount = sum(t['amount'] for t in response.data if t['status'] == 'completed')
        pending_amount = sum(t['amount'] for t in response.data if t['status'] == 'pending')
        failed_count = len([t for t in response.data if t['status'] == 'failed'])
        
        return {
            "success": True,
            "transactions": response.data,
            "total": len(response.data),
            "summary": {
                "total_amount": round(total_amount, 2),
                "pending_amount": round(pending_amount, 2),
                "failed_count": failed_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/transactions/{transaction_id}
# Détails d'une transaction
# ============================================
@router.get("/{transaction_id}")
async def get_transaction_details(
    transaction_id: str,
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Récupère les détails d'une transaction spécifique"""
    try:
        supabase = get_supabase_client()
        
        transaction = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('id', transaction_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not transaction.data:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        # Enrichir avec infos metadata
        metadata = transaction.data.get('metadata', {})
        
        return {
            "success": True,
            "transaction": transaction.data,
            "details": {
                "payment_method": metadata.get('payment_method'),
                "payout_id": metadata.get('payout_id'),
                "invoice_id": metadata.get('invoice_id'),
                "description": metadata.get('description')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/transactions/stats
# Statistiques des transactions
# ============================================
@router.get("/stats")
async def get_transaction_stats(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    period: str = Query("30d", description="Période (7d, 30d, 90d, 1y)")
):
    """Récupère les statistiques des transactions"""
    try:
        supabase = get_supabase_client()
        
        # Calculer date de début selon période
        period_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        days = period_days.get(period, 30)
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Récupérer transactions de la période
        transactions = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', start_date)\
            .execute()
        
        # Calculer statistiques
        total_transactions = len(transactions.data)
        completed = [t for t in transactions.data if t['status'] == 'completed']
        pending = [t for t in transactions.data if t['status'] == 'pending']
        failed = [t for t in transactions.data if t['status'] == 'failed']
        
        total_volume = sum(t['amount'] for t in completed)
        pending_volume = sum(t['amount'] for t in pending)
        avg_transaction = total_volume / len(completed) if completed else 0
        
        success_rate = (len(completed) / total_transactions * 100) if total_transactions > 0 else 0
        
        # Par gateway
        by_gateway = {}
        for t in transactions.data:
            gateway = t['gateway']
            if gateway not in by_gateway:
                by_gateway[gateway] = {'count': 0, 'volume': 0}
            by_gateway[gateway]['count'] += 1
            if t['status'] == 'completed':
                by_gateway[gateway]['volume'] += t['amount']
        
        # Par type
        by_type = {}
        for t in transactions.data:
            ttype = t['transaction_type']
            if ttype not in by_type:
                by_type[ttype] = {'count': 0, 'volume': 0}
            by_type[ttype]['count'] += 1
            if t['status'] == 'completed':
                by_type[ttype]['volume'] += t['amount']
        
        return {
            "success": True,
            "period": period,
            "stats": {
                "total_transactions": total_transactions,
                "completed_count": len(completed),
                "pending_count": len(pending),
                "failed_count": len(failed),
                "success_rate": round(success_rate, 1),
                "total_volume": round(total_volume, 2),
                "pending_volume": round(pending_volume, 2),
                "average_transaction": round(avg_transaction, 2),
                "currency": transactions.data[0]['currency'] if transactions.data else "EUR"
            },
            "by_gateway": by_gateway,
            "by_type": by_type,
            "recent_transactions": transactions.data[:5]  # 5 dernières
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/transactions/process
# Traiter une nouvelle transaction
# ============================================
@router.post("/process")
async def process_transaction(request: ProcessTransactionRequest):
    """Traite une nouvelle transaction de paiement"""
    try:
        supabase = get_supabase_client()
        
        # Valider montant
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Le montant doit être positif")
        
        # Créer transaction
        new_transaction = {
            'user_id': request.user_id,
            'transaction_type': request.transaction_type,
            'amount': request.amount,
            'currency': request.currency,
            'status': 'pending',
            'gateway': request.gateway,
            'gateway_transaction_id': f"{request.gateway}_{datetime.now().timestamp()}",
            'metadata': request.metadata or {},
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('gateway_transactions').insert(new_transaction).execute()
        
        transaction_id = result.data[0]['id']

        # Intégration réelle selon le gateway
        checkout_url = None
        if request.gateway == 'stripe':
            try:
                import stripe as stripe_lib
                import os as _os
                stripe_lib.api_key = _os.getenv('STRIPE_SECRET_KEY')
                session = stripe_lib.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': request.currency.lower(),
                            'product_data': {'name': request.metadata.get('description', 'Paiement GetYourShare') if request.metadata else 'Paiement GetYourShare'},
                            'unit_amount': int(request.amount * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{_os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success?tx={transaction_id}",
                    cancel_url=f"{_os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel",
                    metadata={'transaction_id': transaction_id, 'user_id': request.user_id},
                )
                checkout_url = session.url
                supabase.table('gateway_transactions').update({
                    'gateway_transaction_id': session.id,
                }).eq('id', transaction_id).execute()
            except ImportError:
                pass
            except Exception as stripe_err:
                logger.warning(f"Stripe checkout creation failed: {stripe_err}")
        
        return {
            "success": True,
            "message": "Transaction créée",
            "transaction_id": transaction_id,
            "transaction": result.data[0],
            "checkout_url": checkout_url,
            "next_steps": {
                "stripe": checkout_url or "Rediriger vers Stripe Checkout",
                "paypal": "Rediriger vers PayPal",
                "bank_transfer": "Afficher coordonnées bancaires"
            }.get(request.gateway, "Suivre les instructions du gateway")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/transactions/{transaction_id}/confirm
# Confirmer une transaction (webhook simulation)
# ============================================
@router.post("/{transaction_id}/confirm")
async def confirm_transaction(
    transaction_id: str,
    gateway_transaction_id: Optional[str] = None
):
    """Confirme une transaction (normalement appelé par webhook)"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer transaction
        transaction = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('id', transaction_id)\
            .single()\
            .execute()
        
        if not transaction.data:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        if transaction.data['status'] == 'completed':
            raise HTTPException(status_code=400, detail="Transaction déjà complétée")
        
        # Mettre à jour
        update_data = {
            'status': 'completed',
            'processed_at': datetime.now().isoformat()
        }
        
        if gateway_transaction_id:
            update_data['gateway_transaction_id'] = gateway_transaction_id
        
        supabase.table('gateway_transactions')\
            .update(update_data)\
            .eq('id', transaction_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Transaction confirmée",
            "transaction_id": transaction_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/transactions/{transaction_id}/fail
# Marquer une transaction comme échouée
# ============================================
@router.post("/{transaction_id}/fail")
async def fail_transaction(
    transaction_id: str,
    error_message: str = Query(..., description="Message d'erreur")
):
    """Marque une transaction comme échouée"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer transaction
        transaction = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('id', transaction_id)\
            .single()\
            .execute()
        
        if not transaction.data:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")
        
        # Mettre à jour metadata avec erreur
        metadata = transaction.data.get('metadata', {})
        metadata['error'] = error_message
        metadata['failed_at'] = datetime.now().isoformat()
        
        supabase.table('gateway_transactions')\
            .update({
                'status': 'failed',
                'metadata': metadata,
                'processed_at': datetime.now().isoformat()
            })\
            .eq('id', transaction_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Transaction marquée comme échouée",
            "error": error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/transactions/pending
# Récupérer transactions en attente
# ============================================
@router.get("/pending")
async def get_pending_transactions(
    user_id: Optional[str] = Query(None, description="ID utilisateur (admin: tous si omis)"),
    limit: int = Query(20, description="Nombre de transactions")
):
    """Récupère les transactions en attente"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('gateway_transactions')\
            .select('*')\
            .eq('status', 'pending')
        
        if user_id:
            query = query.eq('user_id', user_id)
        
        response = query.order('created_at', desc=True).limit(limit).execute()
        
        total_pending_amount = sum(t['amount'] for t in response.data)
        
        return {
            "success": True,
            "pending_transactions": response.data,
            "count": len(response.data),
            "total_amount": round(total_pending_amount, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
