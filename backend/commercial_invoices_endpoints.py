"""
Endpoints API pour la gestion des factures commerciaux
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import tempfile
import zipfile
import csv
from io import BytesIO, StringIO

# Supabase client
from supabase import create_client, Client

# Service de factures
from services.commercial_invoice_service import CommercialInvoiceService

router = APIRouter(prefix="/api/invoices/commercials", tags=["Commercial Invoices"])

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://iamezkmapbhlhhvvsits.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_KEY", ""))

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


class CreateCommercialInvoiceRequest(BaseModel):
    commission_id: Optional[str] = None
    commercial_id: str
    amount: float
    commission_type: str = 'commission'  # 'lead', 'subscription', 'bonus', 'commission'
    deal_id: Optional[str] = None
    lead_id: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    description: Optional[str] = None


@router.get("")
async def list_commercial_invoices(
    year: Optional[int] = Query(None, description="Année fiscale"),
    country: Optional[str] = Query(None, description="Code pays (MA, FR, US)"),
    commercial_id: Optional[str] = Query(None, description="ID du commercial"),
    commission_type: Optional[str] = Query(None, description="Type de commission"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Liste les factures des commerciaux
    - Pour admin: toutes les factures
    - Filtres: année, pays, commercial, type
    """
    try:
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        if commercial_id:
            invoices = service.get_invoices_for_commercial(
                commercial_id, 
                year=year, 
                commission_type=commission_type,
                limit=limit
            )
        else:
            invoices = service.get_all_invoices(
                year=year,
                country=country,
                limit=limit
            )
        
        return {
            "success": True,
            "data": invoices,
            "count": len(invoices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_invoice_stats(
    year: Optional[int] = Query(None, description="Année fiscale"),
    commercial_id: Optional[str] = Query(None, description="ID du commercial")
):
    """
    Statistiques des factures commerciaux
    """
    try:
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        if not year:
            year = datetime.now().year
        
        summary = service.get_annual_summary(year, commercial_id)
        
        # Ajouter des statistiques par pays
        invoices = service.get_all_invoices(year=year, limit=1000)
        
        by_country = {}
        for inv in invoices:
            country = inv.get('commercial_country', 'FR')
            if country not in by_country:
                by_country[country] = {'count': 0, 'total': 0}
            by_country[country]['count'] += 1
            by_country[country]['total'] += inv.get('gross_amount', 0)
        
        return {
            "success": True,
            "data": {
                **summary,
                "by_country": by_country
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}")
async def get_commercial_invoice(invoice_id: str):
    """
    Récupère une facture spécifique
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table('commercial_invoices')\
            .select('*')\
            .eq('id', invoice_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        return {
            "success": True,
            "data": result.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: str):
    """
    Télécharge le PDF d'une facture
    """
    try:
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        # Récupérer la facture
        result = supabase.table('commercial_invoices')\
            .select('*')\
            .eq('id', invoice_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        invoice_data = result.data
        
        # Générer le PDF
        pdf_bytes = service.generate_pdf(invoice_data)
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Impossible de générer le PDF")
        
        invoice_number = invoice_data.get('invoice_number', 'facture')
        filename = f"{invoice_number}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_commercial_invoice(request: CreateCommercialInvoiceRequest):
    """
    Crée une nouvelle facture pour un commercial
    """
    try:
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        period_start = None
        period_end = None
        
        if request.period_start:
            period_start = datetime.fromisoformat(request.period_start)
        if request.period_end:
            period_end = datetime.fromisoformat(request.period_end)
        
        invoice = service.create_invoice_from_commission(
            commission_id=request.commission_id,
            commercial_id=request.commercial_id,
            amount=request.amount,
            commission_type=request.commission_type,
            deal_id=request.deal_id,
            lead_id=request.lead_id,
            period_start=period_start,
            period_end=period_end,
            description=request.description
        )
        
        return {
            "success": True,
            "data": invoice,
            "message": f"Facture {invoice.get('invoice_number')} créée avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annual/export")
async def export_annual_invoices(
    year: int = Query(..., description="Année à exporter"),
    commercial_id: Optional[str] = Query(None, description="ID du commercial (optionnel)")
):
    """
    Exporte toutes les factures d'une année en ZIP (PDFs + CSV récapitulatif)
    """
    try:
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        # Récupérer les factures
        query = supabase.table('commercial_invoices')\
            .select('*')\
            .gte('invoice_date', f"{year}-01-01")\
            .lte('invoice_date', f"{year}-12-31")\
            .order('invoice_date', desc=False)
        
        if commercial_id:
            query = query.eq('commercial_id', commercial_id)
        
        result = query.execute()
        invoices = result.data if result.data else []
        
        if not invoices:
            raise HTTPException(status_code=404, detail=f"Aucune facture trouvée pour {year}")
        
        # Créer le ZIP
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Générer chaque PDF
            for invoice in invoices:
                pdf_bytes = service.generate_pdf(invoice)
                if pdf_bytes:
                    filename = f"{invoice.get('invoice_number', 'facture')}.pdf"
                    zip_file.writestr(f"factures/{filename}", pdf_bytes)
            
            # Créer le CSV récapitulatif
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)
            
            # En-têtes
            writer.writerow([
                'Numéro Facture',
                'Date',
                'Commercial',
                'Email',
                'Pays',
                'ID Fiscal',
                'Type Commission',
                'Montant Brut',
                'Taxes Retenues',
                'Montant Net',
                'Devise',
                'Description'
            ])
            
            # Données
            for inv in invoices:
                writer.writerow([
                    inv.get('invoice_number', ''),
                    inv.get('invoice_date', '')[:10] if inv.get('invoice_date') else '',
                    inv.get('commercial_name', ''),
                    inv.get('commercial_email', ''),
                    inv.get('commercial_country', ''),
                    inv.get('commercial_tax_id', ''),
                    inv.get('commission_type', ''),
                    inv.get('gross_amount', 0),
                    inv.get('tax_amount', 0),
                    inv.get('net_amount', 0),
                    inv.get('currency', 'EUR'),
                    inv.get('description', '')
                ])
            
            zip_file.writestr(f"recapitulatif_commerciaux_{year}.csv", csv_buffer.getvalue())
            
            # Ajouter le résumé annuel en JSON
            summary = service.get_annual_summary(year, commercial_id)
            import json
            zip_file.writestr(f"resume_annuel_{year}.json", json.dumps(summary, indent=2, ensure_ascii=False))
        
        zip_buffer.seek(0)
        
        filename = f"factures_commerciaux_{year}"
        if commercial_id:
            filename += f"_{commercial_id[:8]}"
        filename += ".zip"
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my/list")
async def get_my_invoices(
    year: Optional[int] = Query(None, description="Année fiscale"),
    limit: int = Query(100, ge=1, le=500),
    # Pour les tests, on passe le commercial_id en param
    # En production, utiliser l'authentification
    commercial_id: Optional[str] = Query(None)
):
    """
    Récupère les factures du commercial connecté
    """
    try:
        if not commercial_id:
            raise HTTPException(status_code=400, detail="commercial_id requis")
        
        supabase = get_supabase()
        service = CommercialInvoiceService(supabase)
        
        invoices = service.get_invoices_for_commercial(
            commercial_id,
            year=year,
            limit=limit
        )
        
        return {
            "success": True,
            "data": invoices,
            "count": len(invoices)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
