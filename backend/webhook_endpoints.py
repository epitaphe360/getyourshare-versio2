"""
WEBHOOK ENDPOINTS - Gestion des webhooks et logs
Table utilisée: webhook_logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from supabase_config import get_supabase_client
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity
import json

router = APIRouter()

# ============================================
# MODELS
# ============================================

class WebhookLog(BaseModel):
    id: Optional[str] = None
    event_type: str
    source: str
    payload: dict
    status: str
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class TestWebhookRequest(BaseModel):
    event_type: str
    source: str
    payload: dict

# ============================================
# GET /api/webhooks/logs
# Liste des logs de webhooks
# ============================================
@router.get("/logs")
async def get_webhook_logs(
    source: Optional[str] = Query(None, description="Filtrer par source (stripe, paypal, etc)"),
    event_type: Optional[str] = Query(None, description="Filtrer par type d'événement"),
    status: Optional[str] = Query(None, description="Filtrer par statut (success, failed, pending)"),
    limit: int = Query(50, description="Nombre de logs"),
    offset: int = Query(0, description="Offset pour pagination")
):
    """Récupère les logs de webhooks"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('webhook_logs').select('*')
        
        if source:
            query = query.eq('source', source)
        if event_type:
            query = query.eq('event_type', event_type)
        if status:
            query = query.eq('status', status)
        
        response = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Calculer statistiques
        total_logs = len(response.data)
        success_count = len([log for log in response.data if log['status'] == 'success'])
        failed_count = len([log for log in response.data if log['status'] == 'failed'])
        pending_count = len([log for log in response.data if log['status'] == 'pending'])
        
        success_rate = (success_count / total_logs * 100) if total_logs > 0 else 0
        
        # Grouper par source
        by_source = {}
        for log in response.data:
            src = log['source']
            if src not in by_source:
                by_source[src] = {'count': 0, 'success': 0, 'failed': 0}
            by_source[src]['count'] += 1
            if log['status'] == 'success':
                by_source[src]['success'] += 1
            elif log['status'] == 'failed':
                by_source[src]['failed'] += 1
        
        return {
            "success": True,
            "logs": response.data,
            "total": total_logs,
            "stats": {
                "success_count": success_count,
                "failed_count": failed_count,
                "pending_count": pending_count,
                "success_rate": round(success_rate, 1)
            },
            "by_source": by_source
        }
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la récupération des logs de webhooks",
            context={"source": source, "event_type": event_type, "status": status}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# GET /api/webhooks/stats
# Statistiques des webhooks
# ============================================
@router.get("/stats")
async def get_webhook_stats(
    period: str = Query("30d", description="Période (7d, 30d, 90d)"),
    source: Optional[str] = Query(None, description="Filtrer par source")
):
    """Récupère les statistiques des webhooks"""
    try:
        supabase = get_supabase_client()
        
        # Calculer date de début
        period_days = {"7d": 7, "30d": 30, "90d": 90}
        days = period_days.get(period, 30)
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Récupérer logs de la période
        query = supabase.table('webhook_logs')\
            .select('*')\
            .gte('created_at', start_date)
        
        if source:
            query = query.eq('source', source)
        
        response = query.execute()
        logs = response.data
        
        total_webhooks = len(logs)
        success = [log for log in logs if log['status'] == 'success']
        failed = [log for log in logs if log['status'] == 'failed']
        
        success_rate = (len(success) / total_webhooks * 100) if total_webhooks > 0 else 0
        
        # Par type d'événement
        by_event_type = {}
        for log in logs:
            event = log['event_type']
            if event not in by_event_type:
                by_event_type[event] = {'count': 0, 'success': 0, 'failed': 0}
            by_event_type[event]['count'] += 1
            if log['status'] == 'success':
                by_event_type[event]['success'] += 1
            elif log['status'] == 'failed':
                by_event_type[event]['failed'] += 1
        
        # Par source
        by_source = {}
        for log in logs:
            src = log['source']
            if src not in by_source:
                by_source[src] = {'count': 0, 'success': 0, 'failed': 0}
            by_source[src]['count'] += 1
            if log['status'] == 'success':
                by_source[src]['success'] += 1
            elif log['status'] == 'failed':
                by_source[src]['failed'] += 1
        
        # Temps de traitement moyen
        processed_logs = [log for log in logs if log.get('processed_at')]
        avg_processing_time = 0
        if processed_logs:
            processing_times = []
            for log in processed_logs:
                created = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                processed = datetime.fromisoformat(log['processed_at'].replace('Z', '+00:00'))
                delta = (processed - created).total_seconds()
                processing_times.append(delta)
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Erreurs récentes
        recent_errors = [
            {
                'event_type': log['event_type'],
                'source': log['source'],
                'error': log.get('error_message'),
                'created_at': log['created_at']
            }
            for log in sorted(logs, key=lambda x: x['created_at'], reverse=True)[:10]
            if log['status'] == 'failed'
        ]
        
        return {
            "success": True,
            "period": period,
            "stats": {
                "total_webhooks": total_webhooks,
                "success_count": len(success),
                "failed_count": len(failed),
                "success_rate": round(success_rate, 1),
                "avg_processing_time_seconds": round(avg_processing_time, 2)
            },
            "by_event_type": by_event_type,
            "by_source": by_source,
            "recent_errors": recent_errors
        }
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la récupération des statistiques",
            context={"period": period}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# POST /api/webhooks/test
# Tester un webhook
# ============================================
@router.post("/test")
async def test_webhook(request: TestWebhookRequest):
    """Teste un webhook en créant un log de test"""
    try:
        supabase = get_supabase_client()
        
        # Créer log de test
        new_log = {
            'event_type': request.event_type,
            'source': request.source,
            'payload': request.payload,
            'status': 'success',
            'response_code': 200,
            'processed_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('webhook_logs').insert(new_log).execute()
        
        return {
            "success": True,
            "message": "Webhook de test créé",
            "log": result.data[0] if result.data else None
        }
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.LOW,
            user_friendly_message="Erreur lors de la création du webhook de test",
            context={"event_type": request.event_type, "source": request.source}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# POST /api/webhooks/stripe
# Webhook Stripe
# ============================================
@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Endpoint pour recevoir les webhooks Stripe"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer payload
        payload = await request.json()
        
        # TODO: Vérifier signature Stripe
        # stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        event_type = payload.get('type', 'unknown')
        
        # Logger le webhook
        log_entry = {
            'event_type': event_type,
            'source': 'stripe',
            'payload': payload,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        log_result = supabase.table('webhook_logs').insert(log_entry).execute()
        log_id = log_result.data[0]['id'] if log_result.data else None
        
        # Traiter selon type d'événement
        try:
            if event_type == 'payment_intent.succeeded':
                # TODO: Mettre à jour transaction correspondante
                pass
            elif event_type == 'payment_intent.payment_failed':
                # TODO: Marquer transaction comme échouée
                pass
            elif event_type == 'customer.subscription.created':
                # TODO: Créer abonnement
                pass
            elif event_type == 'customer.subscription.deleted':
                # TODO: Annuler abonnement
                pass
            
            # Marquer comme traité avec succès
            if log_id:
                supabase.table('webhook_logs')\
                    .update({
                        'status': 'success',
                        'response_code': 200,
                        'processed_at': datetime.now().isoformat()
                    })\
                    .eq('id', log_id)\
                    .execute()
            
            return {"success": True, "event_type": event_type}
            
        except Exception as processing_error:
            # Marquer comme échoué
            if log_id:
                supabase.table('webhook_logs')\
                    .update({
                        'status': 'failed',
                        'error_message': str(processing_error),
                        'processed_at': datetime.now().isoformat()
                    })\
                    .eq('id', log_id)\
                    .execute()
            raise
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/webhooks/paypal
# Webhook PayPal
# ============================================
@router.post("/paypal")
async def paypal_webhook(request: Request):
    """Endpoint pour recevoir les webhooks PayPal"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer payload
        payload = await request.json()
        
        # TODO: Vérifier signature PayPal
        
        event_type = payload.get('event_type', 'unknown')
        
        # Logger le webhook
        log_entry = {
            'event_type': event_type,
            'source': 'paypal',
            'payload': payload,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        log_result = supabase.table('webhook_logs').insert(log_entry).execute()
        log_id = log_result.data[0]['id'] if log_result.data else None
        
        # Traiter selon type d'événement
        try:
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                # TODO: Mettre à jour transaction
                pass
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                # TODO: Marquer comme échoué
                pass
            
            # Marquer comme traité
            if log_id:
                supabase.table('webhook_logs')\
                    .update({
                        'status': 'success',
                        'response_code': 200,
                        'processed_at': datetime.now().isoformat()
                    })\
                    .eq('id', log_id)\
                    .execute()
            
            return {"success": True, "event_type": event_type}
            
        except Exception as processing_error:
            if log_id:
                supabase.table('webhook_logs')\
                    .update({
                        'status': 'failed',
                        'error_message': str(processing_error),
                        'processed_at': datetime.now().isoformat()
                    })\
                    .eq('id', log_id)\
                    .execute()
            raise
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/webhooks/logs/{log_id}
# Détails d'un log
# ============================================
@router.get("/logs/{log_id}")
async def get_webhook_log_details(log_id: str):
    """Récupère les détails d'un log de webhook"""
    try:
        supabase = get_supabase_client()
        
        log = supabase.table('webhook_logs')\
            .select('*')\
            .eq('id', log_id)\
            .single()\
            .execute()
        
        if not log.data:
            raise HTTPException(status_code=404, detail="Log non trouvé")
        
        # Formater payload pour affichage
        payload_formatted = json.dumps(log.data['payload'], indent=2)
        
        return {
            "success": True,
            "log": log.data,
            "payload_formatted": payload_formatted
        }
    except HTTPException:
        raise
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la récupération des détails du log",
            context={"log_id": log_id}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# POST /api/webhooks/retry/{log_id}
# Réessayer un webhook échoué
# ============================================
@router.post("/retry/{log_id}")
async def retry_webhook(log_id: str):
    """Réessaye le traitement d'un webhook échoué"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer log
        log = supabase.table('webhook_logs')\
            .select('*')\
            .eq('id', log_id)\
            .single()\
            .execute()
        
        if not log.data:
            raise HTTPException(status_code=404, detail="Log non trouvé")
        
        if log.data['status'] != 'failed':
            raise HTTPException(status_code=400, detail="Le webhook n'est pas en échec")
        
        # Marquer comme en attente
        supabase.table('webhook_logs')\
            .update({
                'status': 'pending',
                'error_message': None,
                'processed_at': None
            })\
            .eq('id', log_id)\
            .execute()
        
        # TODO: Réexécuter le traitement du webhook
        # Pour l'instant, on le marque juste comme "pending"
        
        return {
            "success": True,
            "message": "Webhook en cours de réexécution",
            "log_id": log_id
        }
    except HTTPException:
        raise
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la réexécution du webhook",
            context={"log_id": log_id}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# DELETE /api/webhooks/logs/old
# Nettoyer les vieux logs
# ============================================
@router.delete("/logs/old")
async def cleanup_old_logs(
    days: int = Query(90, description="Supprimer logs plus vieux que X jours")
):
    """Supprime les logs de webhooks anciens (admin)"""
    try:
        supabase = get_supabase_client()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Compter d'abord
        count_result = supabase.table('webhook_logs')\
            .select('id', count='exact')\
            .lt('created_at', cutoff_date)\
            .execute()
        
        count = len(count_result.data) if count_result.data else 0
        
        if count == 0:
            return {
                "success": True,
                "message": "Aucun log à supprimer",
                "deleted_count": 0
            }
        
        # Supprimer
        supabase.table('webhook_logs')\
            .delete()\
            .lt('created_at', cutoff_date)\
            .execute()
        
        return {
            "success": True,
            "message": f"{count} logs supprimés",
            "deleted_count": count,
            "cutoff_date": cutoff_date
        }
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.LOW,
            user_friendly_message="Erreur lors du nettoyage des logs",
            context={"days": days}
        )
        raise HTTPException(status_code=500, detail=error_response["message"])
