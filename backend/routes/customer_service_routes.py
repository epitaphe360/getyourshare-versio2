"""
Routes Customer Service & Ticketing System
Support client, tickets, SLA tracking
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["Customer Service"])


# ============================================
# MODELS
# ============================================

class TicketCreate(BaseModel):
    subject: str
    description: str
    category: str  # technical, billing, product, account, other
    priority: str = "medium"  # low, medium, high, urgent
    attachments: Optional[List[str]] = []


class TicketReply(BaseModel):
    message: str
    attachments: Optional[List[str]] = []
    internal_note: bool = False  # Note interne (non visible client)


class TicketUpdate(BaseModel):
    status: Optional[str] = None  # open, in_progress, waiting_customer, resolved, closed
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    category: Optional[str] = None


# ============================================
# TICKETS CRUD
# ============================================

@router.post("/tickets")
async def create_ticket(
    ticket: TicketCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un nouveau ticket de support
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Générer ticket number
        import uuid
        ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        ticket_data = {
            'ticket_number': ticket_number,
            'user_id': user_id,
            'subject': ticket.subject,
            'description': ticket.description,
            'category': ticket.category,
            'priority': ticket.priority,
            'status': 'open',
            'attachments': ticket.attachments,
            'created_at': datetime.now().isoformat(),
            'sla_due_at': (datetime.now() + timedelta(hours=24)).isoformat()  # SLA 24h par défaut
        }

        result = supabase.table('support_tickets').insert(ticket_data).execute()

        # Envoyer notification à l'équipe support
        # TODO: Implémenter notification

        return {
            "success": True,
            "ticket": result.data[0] if result.data else ticket_data,
            "ticket_number": ticket_number,
            "message": "Ticket créé avec succès. Notre équipe vous répondra sous 24h."
        }

    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
async def get_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des tickets (utilisateur ou admin)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Admin voit tous les tickets, user voit seulement les siens
        if role == "admin" or role == "support":
            query = supabase.table('support_tickets').select('*', count='exact')
        else:
            query = supabase.table('support_tickets').select('*', count='exact').eq('user_id', user_id)

        # Filtres
        if status:
            query = query.eq('status', status)

        if category:
            query = query.eq('category', category)

        if priority:
            query = query.eq('priority', priority)

        # Pagination
        query = query.range(offset, offset + limit - 1).order('created_at', desc=True)

        response = query.execute()

        return {
            "success": True,
            "tickets": response.data or [],
            "total": response.count if hasattr(response, 'count') else len(response.data or []),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/{ticket_id}")
async def get_ticket_details(
    ticket_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Détails d'un ticket avec historique
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Récupérer le ticket
        ticket = supabase.table('support_tickets').select('*').eq('id', ticket_id).single().execute()

        if not ticket.data:
            raise HTTPException(status_code=404, detail="Ticket non trouvé")

        # Vérifier permissions (admin ou propriétaire)
        if role != "admin" and role != "support" and ticket.data.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Récupérer les réponses
        replies = supabase.table('support_ticket_replies').select('*').eq('ticket_id', ticket_id).order('created_at', desc=False).execute()

        # Filtrer les notes internes si pas admin
        if role != "admin" and role != "support":
            replies_data = [r for r in (replies.data or []) if not r.get('internal_note')]
        else:
            replies_data = replies.data or []

        return {
            "success": True,
            "ticket": ticket.data,
            "replies": replies_data,
            "total_replies": len(replies_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TICKET REPLIES
# ============================================

@router.post("/tickets/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: str,
    reply: TicketReply,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Répondre à un ticket
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier que le ticket existe
        ticket = supabase.table('support_tickets').select('user_id, status').eq('id', ticket_id).single().execute()

        if not ticket.data:
            raise HTTPException(status_code=404, detail="Ticket non trouvé")

        # Vérifier permissions
        if role != "admin" and role != "support" and ticket.data.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Créer la réponse
        reply_data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'message': reply.message,
            'attachments': reply.attachments,
            'internal_note': reply.internal_note if (role == "admin" or role == "support") else False,
            'is_staff': role in ["admin", "support"],
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('support_ticket_replies').insert(reply_data).execute()

        # Mettre à jour le statut du ticket
        if role in ["admin", "support"]:
            # Réponse du support -> waiting_customer
            new_status = "waiting_customer"
        else:
            # Réponse du client -> in_progress
            new_status = "in_progress"

        supabase.table('support_tickets').update({
            'status': new_status,
            'last_reply_at': datetime.now().isoformat()
        }).eq('id', ticket_id).execute()

        # TODO: Envoyer notification email

        return {
            "success": True,
            "reply": result.data[0] if result.data else reply_data,
            "ticket_status": new_status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replying to ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TICKET MANAGEMENT (ADMIN)
# ============================================

@router.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    update: TicketUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour un ticket (admin/support only)
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Admin/Support uniquement")

        # Préparer les données de mise à jour
        update_data = {k: v for k, v in update.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        update_data['updated_at'] = datetime.now().isoformat()

        # Si résolu, ajouter resolved_at
        if update.status == 'resolved':
            update_data['resolved_at'] = datetime.now().isoformat()

        result = supabase.table('support_tickets').update(update_data).eq('id', ticket_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Ticket non trouvé")

        return {
            "success": True,
            "ticket": result.data[0],
            "message": "Ticket mis à jour"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    agent_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Assigner un ticket à un agent (admin/support only)
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Admin/Support uniquement")

        result = supabase.table('support_tickets').update({
            'assigned_to': agent_id,
            'status': 'in_progress',
            'assigned_at': datetime.now().isoformat()
        }).eq('id', ticket_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Ticket non trouvé")

        return {
            "success": True,
            "message": "Ticket assigné",
            "assigned_to": agent_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    resolution_note: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Résoudre un ticket
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Admin/Support uniquement")

        update_data = {
            'status': 'resolved',
            'resolved_at': datetime.now().isoformat(),
            'resolved_by': payload.get("id")
        }

        if resolution_note:
            update_data['resolution_note'] = resolution_note

        result = supabase.table('support_tickets').update(update_data).eq('id', ticket_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Ticket non trouvé")

        return {
            "success": True,
            "message": "Ticket résolu",
            "ticket": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SLA TRACKING
# ============================================

@router.get("/sla/status")
async def get_sla_status(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Statut SLA (Service Level Agreement)

    Admin/Support only
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Admin/Support uniquement")

        # Tickets ouverts dépassant le SLA
        now = datetime.now().isoformat()

        breached = supabase.table('support_tickets').select('*', count='exact').in_('status', ['open', 'in_progress']).lt('sla_due_at', now).execute()

        # Tickets proches du SLA (< 2h)
        warning_time = (datetime.now() + timedelta(hours=2)).isoformat()

        warning = supabase.table('support_tickets').select('*', count='exact').in_('status', ['open', 'in_progress']).gte('sla_due_at', now).lt('sla_due_at', warning_time).execute()

        # Tickets OK
        ok = supabase.table('support_tickets').select('*', count='exact').in_('status', ['open', 'in_progress']).gte('sla_due_at', warning_time).execute()

        return {
            "success": True,
            "sla_status": {
                "breached": {
                    "count": breached.count if hasattr(breached, 'count') else 0,
                    "tickets": breached.data or []
                },
                "warning": {
                    "count": warning.count if hasattr(warning, 'count') else 0,
                    "tickets": warning.data or []
                },
                "ok": {
                    "count": ok.count if hasattr(ok, 'count') else 0
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SLA status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATS
# ============================================

@router.get("/stats")
async def get_support_stats(
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Statistiques du support client (admin/support only)
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Admin/Support uniquement")

        # Période
        if period == "7d":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif period == "30d":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        else:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()

        # Tous les tickets de la période
        tickets = supabase.table('support_tickets').select('*').gte('created_at', start_date).execute()

        tickets_data = tickets.data or []

        # Stats par statut
        status_counts = {}
        for ticket in tickets_data:
            status = ticket.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Stats par catégorie
        category_counts = {}
        for ticket in tickets_data:
            category = ticket.get('category', 'other')
            category_counts[category] = category_counts.get(category, 0) + 1

        # Temps moyen de résolution
        resolved_tickets = [t for t in tickets_data if t.get('resolved_at')]

        total_resolution_time = 0
        for ticket in resolved_tickets:
            created = datetime.fromisoformat(ticket['created_at'])
            resolved = datetime.fromisoformat(ticket['resolved_at'])
            total_resolution_time += (resolved - created).total_seconds()

        avg_resolution_hours = (total_resolution_time / 3600 / len(resolved_tickets)) if resolved_tickets else 0

        return {
            "success": True,
            "period": period,
            "stats": {
                "total_tickets": len(tickets_data),
                "by_status": status_counts,
                "by_category": category_counts,
                "resolved": len(resolved_tickets),
                "avg_resolution_hours": round(avg_resolution_hours, 1),
                "resolution_rate": round((len(resolved_tickets) / len(tickets_data) * 100), 1) if tickets_data else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting support stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
