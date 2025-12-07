"""
Routes API pour la génération et gestion des factures
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase
from services.invoice_pdf_generator import InvoicePDFGenerator

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

# Initialize service
invoice_generator = InvoicePDFGenerator(supabase)


# ============================================
# MODELS
# ============================================

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    vat_rate: Optional[float] = 0.20


class GenerateInvoiceRequest(BaseModel):
    client_id: str
    line_items: List[LineItem]
    invoice_type: str = 'sale'  # sale, service, deposit
    payment_terms: Optional[str] = 'Net 30'
    payment_methods: Optional[str] = 'Bank Transfer, Credit Card'
    sales_tax_rate: Optional[float] = 0
    notes: Optional[str] = None


class SendInvoiceEmailRequest(BaseModel):
    invoice_id: str
    recipient_email: EmailStr
    subject: Optional[str] = None
    message: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@router.post("/generate")
async def generate_invoice(
    request: GenerateInvoiceRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Génère une facture PDF conforme selon le pays du merchant

    Détection automatique du pays (MA/FR/US) selon le profil merchant.
    Génère un numéro chronologique unique.
    Upload PDF vers Supabase Storage.
    Retourne l'URL publique + bytes PDF.
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Convertir les line items en dict
        line_items = [item.dict() for item in request.line_items]

        # Métadonnées
        metadata = {
            'payment_terms': request.payment_terms,
            'payment_methods': request.payment_methods,
            'sales_tax_rate': request.sales_tax_rate,
            'notes': request.notes
        }

        # Générer la facture
        result = invoice_generator.generate_invoice(
            merchant_id=merchant_id,
            client_id=request.client_id,
            line_items=line_items,
            invoice_type=request.invoice_type,
            metadata=metadata
        )

        return {
            "success": True,
            "invoice_id": result['invoice_id'],
            "invoice_number": result['invoice_number'],
            "pdf_url": result['pdf_url'],
            "country": result['country'],
            "message": "Facture générée avec succès"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_invoices(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des factures du merchant
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('invoices').select('*').eq('merchant_id', merchant_id)

        if status:
            query = query.eq('status', status)

        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        return {
            "success": True,
            "invoices": result.data or [],
            "total": len(result.data) if result.data else 0
        }

    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}")
async def get_invoice_details(
    invoice_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Détails d'une facture
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        result = supabase.table('invoices').select('*').eq('id', invoice_id).eq('merchant_id', merchant_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        return {
            "success": True,
            "invoice": result.data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}/download")
async def download_invoice(
    invoice_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Télécharger le PDF d'une facture
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer l'invoice
        invoice = supabase.table('invoices').select('*').eq('id', invoice_id).eq('merchant_id', merchant_id).single().execute()

        if not invoice.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        invoice_data = invoice.data

        # Télécharger le PDF depuis storage
        pdf_bytes = supabase.storage.from_('invoices').download(invoice_data['pdf_path'])

        # Retourner le PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_data['invoice_number']}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{invoice_id}/send-email")
async def send_invoice_email(
    invoice_id: str,
    request: SendInvoiceEmailRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Envoyer la facture par email
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que la facture appartient au merchant
        invoice = supabase.table('invoices').select('*').eq('id', invoice_id).eq('merchant_id', merchant_id).single().execute()

        if not invoice.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        # Envoyer l'email
        success = await invoice_generator.send_invoice_email(
            invoice_id=invoice_id,
            recipient_email=request.recipient_email,
            subject=request.subject
        )

        if success:
            return {
                "success": True,
                "message": "Facture envoyée par email"
            }
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de l'envoi email")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending invoice email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    payment_date: Optional[str] = None,
    payment_method: Optional[str] = None,
    payment_reference: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Marquer une facture comme payée
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier la facture
        invoice = supabase.table('invoices').select('*').eq('id', invoice_id).eq('merchant_id', merchant_id).single().execute()

        if not invoice.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        # Mettre à jour
        update_data = {
            'status': 'paid',
            'paid_at': payment_date or datetime.now().isoformat(),
            'payment_method': payment_method,
            'payment_reference': payment_reference
        }

        result = supabase.table('invoices').update(update_data).eq('id', invoice_id).execute()

        return {
            "success": True,
            "message": "Facture marquée comme payée",
            "invoice": result.data[0] if result.data else {}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking invoice as paid: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{invoice_id}/void")
async def void_invoice(
    invoice_id: str,
    reason: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Annuler une facture
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier la facture
        invoice = supabase.table('invoices').select('*').eq('id', invoice_id).eq('merchant_id', merchant_id).single().execute()

        if not invoice.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")

        # Vérifier qu'elle n'est pas payée
        if invoice.data.get('status') == 'paid':
            raise HTTPException(status_code=400, detail="Impossible d'annuler une facture payée")

        # Marquer comme annulée
        result = supabase.table('invoices').update({
            'status': 'voided',
            'voided_at': datetime.now().isoformat(),
            'void_reason': reason
        }).eq('id', invoice_id).execute()

        return {
            "success": True,
            "message": "Facture annulée",
            "invoice": result.data[0] if result.data else {}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voiding invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_invoice_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Statistiques des factures
    """
    try:
        merchant_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('invoices').select('*').eq('merchant_id', merchant_id)

        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)

        result = query.execute()
        invoices = result.data or []

        # Calculer les stats
        total_invoices = len(invoices)
        total_amount = sum(Decimal(str(inv.get('total_ht', 0))) for inv in invoices)
        paid_invoices = sum(1 for inv in invoices if inv.get('status') == 'paid')
        pending_invoices = sum(1 for inv in invoices if inv.get('status') in ['generated', 'sent'])
        overdue_invoices = sum(1 for inv in invoices if inv.get('status') == 'overdue')

        paid_amount = sum(
            Decimal(str(inv.get('total_ht', 0)))
            for inv in invoices
            if inv.get('status') == 'paid'
        )

        return {
            "success": True,
            "stats": {
                "total_invoices": total_invoices,
                "total_amount": float(total_amount),
                "paid_invoices": paid_invoices,
                "pending_invoices": pending_invoices,
                "overdue_invoices": overdue_invoices,
                "paid_amount": float(paid_amount),
                "pending_amount": float(total_amount - paid_amount),
                "payment_rate": round(paid_invoices / total_invoices * 100, 2) if total_invoices > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting invoice stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
