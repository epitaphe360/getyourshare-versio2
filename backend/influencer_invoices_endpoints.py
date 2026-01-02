"""
API Endpoints pour la gestion des factures influenceurs.
Permet aux marchands de récupérer, télécharger et exporter les factures.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from io import BytesIO
import zipfile
import csv

# Import du service de factures
try:
    from services.influencer_invoice_service import InfluencerInvoiceService
except ImportError:
    from backend.services.influencer_invoice_service import InfluencerInvoiceService

# Import de la connexion Supabase
try:
    from database import get_supabase_client
except ImportError:
    try:
        from backend.database import get_supabase_client
    except ImportError:
        def get_supabase_client():
            import os
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
            return create_client(url, key)


router = APIRouter(prefix="/api/invoices/influencers", tags=["Influencer Invoices"])


# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class InvoiceCreate(BaseModel):
    payout_id: str
    influencer_id: str
    merchant_id: str
    amount: float
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    description: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    influencer_name: str
    influencer_country: str
    gross_amount: float
    tax_amount: float
    net_amount: float
    currency: str
    status: str
    invoice_date: str
    description: Optional[str] = None


class AnnualSummaryResponse(BaseModel):
    year: int
    total_invoices: int
    total_gross: float
    total_tax_withheld: float
    total_net_paid: float
    by_influencer: List[dict]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("")
async def get_invoices(
    merchant_id: Optional[str] = Query(None, description="ID du marchand"),
    year: Optional[int] = Query(None, description="Année fiscale"),
    influencer_id: Optional[str] = Query(None, description="Filtrer par influenceur"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    limit: int = Query(100, description="Nombre max de résultats"),
    offset: int = Query(0, description="Offset pour pagination")
):
    """
    Récupère la liste des factures influenceurs.
    Accessible par les marchands et admins.
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('influencer_invoices')\
            .select('*')\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)
        
        if merchant_id:
            query = query.eq('merchant_id', merchant_id)
        
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            query = query.gte('invoice_date', start_date).lte('invoice_date', end_date)
        
        if influencer_id:
            query = query.eq('influencer_id', influencer_id)
        
        if status:
            query = query.eq('status', status)
        
        result = query.execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "count": len(result.data) if result.data else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_invoice_stats(
    merchant_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None)
):
    """
    Récupère les statistiques des factures.
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('influencer_invoices').select('*')
        
        if merchant_id:
            query = query.eq('merchant_id', merchant_id)
        
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            query = query.gte('invoice_date', start_date).lte('invoice_date', end_date)
        
        result = query.execute()
        invoices = result.data if result.data else []
        
        # Calculer les stats
        total_gross = sum(inv.get('gross_amount', 0) for inv in invoices)
        total_tax = sum(inv.get('tax_amount', 0) for inv in invoices)
        total_net = sum(inv.get('net_amount', 0) for inv in invoices)
        
        # Stats par pays
        by_country = {}
        for inv in invoices:
            country = inv.get('influencer_country', 'OTHER')
            if country not in by_country:
                by_country[country] = {'count': 0, 'total': 0}
            by_country[country]['count'] += 1
            by_country[country]['total'] += inv.get('gross_amount', 0)
        
        return {
            "success": True,
            "data": {
                "total_invoices": len(invoices),
                "total_gross": round(total_gross, 2),
                "total_tax_withheld": round(total_tax, 2),
                "total_net_paid": round(total_net, 2),
                "by_country": by_country,
                "year": year or "all"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}")
async def get_invoice_detail(invoice_id: str):
    """
    Récupère le détail d'une facture.
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('influencer_invoices')\
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
    
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: str):
    """
    Télécharge la facture au format PDF.
    """
    try:
        supabase = get_supabase_client()
        
        # Récupérer la facture
        result = supabase.table('influencer_invoices')\
            .select('*')\
            .eq('id', invoice_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        invoice_data = result.data
        
        # Générer le PDF
        service = InfluencerInvoiceService(supabase)
        pdf_bytes = service.generate_pdf(invoice_data)
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Erreur lors de la génération du PDF")
        
        # Retourner le PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_data.get('invoice_number', 'invoice')}.pdf"
            }
        )
    
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_invoice(invoice: InvoiceCreate):
    """
    Crée manuellement une facture pour un influenceur.
    Normalement appelé automatiquement lors d'un paiement.
    """
    try:
        supabase = get_supabase_client()
        service = InfluencerInvoiceService(supabase)
        
        # Parser les dates
        period_start = None
        period_end = None
        
        if invoice.period_start:
            period_start = datetime.fromisoformat(invoice.period_start.replace('Z', '+00:00'))
        if invoice.period_end:
            period_end = datetime.fromisoformat(invoice.period_end.replace('Z', '+00:00'))
        
        # Créer la facture
        invoice_data = service.create_invoice_from_payout(
            payout_id=invoice.payout_id,
            influencer_id=invoice.influencer_id,
            merchant_id=invoice.merchant_id,
            amount=invoice.amount,
            period_start=period_start,
            period_end=period_end,
            description=invoice.description
        )
        
        return {
            "success": True,
            "message": "Facture créée avec succès",
            "data": invoice_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annual/summary")
async def get_annual_summary(
    merchant_id: str = Query(..., description="ID du marchand"),
    year: int = Query(..., description="Année fiscale")
):
    """
    Génère un récapitulatif annuel pour la déclaration fiscale.
    """
    try:
        supabase = get_supabase_client()
        service = InfluencerInvoiceService(supabase)
        
        summary = service.get_annual_summary(merchant_id, year)
        
        return {
            "success": True,
            "data": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annual/export")
async def export_annual_invoices(
    merchant_id: str = Query(..., description="ID du marchand"),
    year: int = Query(..., description="Année fiscale")
):
    """
    Exporte toutes les factures d'une année en ZIP (PDFs + CSV récapitulatif).
    Idéal pour transmettre à votre comptable.
    """
    try:
        supabase = get_supabase_client()
        service = InfluencerInvoiceService(supabase)
        
        # Récupérer toutes les factures de l'année
        invoices = service.get_invoices_for_merchant(merchant_id, year)
        
        if not invoices:
            raise HTTPException(status_code=404, detail=f"Aucune facture trouvée pour {year}")
        
        # Créer le fichier ZIP
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Ajouter chaque facture en PDF
            for inv in invoices:
                try:
                    pdf_bytes = service.generate_pdf(inv)
                    if pdf_bytes:
                        filename = f"factures/{inv.get('invoice_number', 'invoice')}.pdf"
                        zip_file.writestr(filename, pdf_bytes)
                except Exception as e:
                    print(f"Erreur PDF pour {inv.get('invoice_number')}: {e}")
            
            # Créer le CSV récapitulatif
            csv_buffer = BytesIO()
            csv_writer = csv.writer(csv_buffer.getfilesIO())
            
            # En-têtes CSV
            csv_data = [
                ['Numéro Facture', 'Date', 'Influenceur', 'Pays', 'ID Fiscal', 
                 'Montant Brut', 'Retenue/Taxe', 'Net Payé', 'Devise', 'Description']
            ]
            
            for inv in invoices:
                csv_data.append([
                    inv.get('invoice_number', ''),
                    inv.get('invoice_date', '')[:10] if inv.get('invoice_date') else '',
                    inv.get('influencer_name', ''),
                    inv.get('influencer_country', ''),
                    inv.get('influencer_tax_id', 'Non renseigné'),
                    inv.get('gross_amount', 0),
                    inv.get('tax_amount', 0),
                    inv.get('net_amount', 0),
                    inv.get('currency', 'EUR'),
                    inv.get('description', '')
                ])
            
            # Ligne de total
            total_gross = sum(inv.get('gross_amount', 0) for inv in invoices)
            total_tax = sum(inv.get('tax_amount', 0) for inv in invoices)
            total_net = sum(inv.get('net_amount', 0) for inv in invoices)
            
            csv_data.append([])
            csv_data.append(['TOTAL', '', '', '', '', total_gross, total_tax, total_net, '', ''])
            
            # Écrire le CSV
            csv_content = '\n'.join([';'.join(map(str, row)) for row in csv_data])
            zip_file.writestr(f'recapitulatif_{year}.csv', csv_content.encode('utf-8-sig'))
            
            # Ajouter le résumé JSON
            summary = service.get_annual_summary(merchant_id, year)
            zip_file.writestr(f'resume_{year}.json', json.dumps(summary, indent=2, ensure_ascii=False))
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=factures_influenceurs_{year}.zip"
            }
        )
    
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/influencers/list")
async def get_influencers_with_invoices(
    merchant_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None)
):
    """
    Récupère la liste des influenceurs ayant des factures.
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('influencer_invoices')\
            .select('influencer_id, influencer_name, influencer_country, influencer_tax_id')
        
        if merchant_id:
            query = query.eq('merchant_id', merchant_id)
        
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            query = query.gte('invoice_date', start_date).lte('invoice_date', end_date)
        
        result = query.execute()
        
        # Dédupliquer par influencer_id
        influencers = {}
        for inv in (result.data or []):
            inf_id = inv.get('influencer_id')
            if inf_id and inf_id not in influencers:
                influencers[inf_id] = {
                    'id': inf_id,
                    'name': inv.get('influencer_name', 'N/A'),
                    'country': inv.get('influencer_country', ''),
                    'tax_id': inv.get('influencer_tax_id', '')
                }
        
        return {
            "success": True,
            "data": list(influencers.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
