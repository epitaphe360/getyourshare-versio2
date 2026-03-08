"""
Endpoints API pour la gestion fiscale
Maroc, France, USA
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

from services.tax_calculator import (
    UnifiedTaxCalculator, 
    TaxProfile, 
    Country, 
    TaxStatus,
    MoroccoTaxCalculator,
    FranceTaxCalculator,
    USATaxCalculator
)

router = APIRouter(prefix="/api/fiscal", tags=["Fiscal"])

# Initialize calculators
unified_calculator = UnifiedTaxCalculator()
morocco_calc = MoroccoTaxCalculator()
france_calc = FranceTaxCalculator()
usa_calc = USATaxCalculator()


# ============ SCHEMAS ============

class CountryEnum(str, Enum):
    MA = "MA"
    FR = "FR"
    US = "US"


class TaxStatusEnum(str, Enum):
    auto_entrepreneur = "auto_entrepreneur"
    micro_enterprise = "micro_enterprise"
    company = "company"
    individual = "individual"
    sole_proprietor = "sole_proprietor"
    llc = "llc"


class TaxProfileCreate(BaseModel):
    country: CountryEnum
    status: TaxStatusEnum
    tax_id: Optional[str] = None  # ICE, SIRET, EIN
    vat_number: Optional[str] = None
    vat_exempt: bool = False
    withholding_exempt: bool = False


class TaxProfileResponse(BaseModel):
    user_id: str
    country: str
    status: str
    tax_id: Optional[str]
    vat_number: Optional[str]
    vat_exempt: bool
    withholding_exempt: bool
    created_at: Optional[datetime]


class TaxCalculationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Montant brut")
    country: CountryEnum
    status: TaxStatusEnum
    tax_id: Optional[str] = None
    vat_exempt: bool = False
    withholding_exempt: bool = False
    options: Optional[Dict] = None


class TaxCalculationResponse(BaseModel):
    gross_amount: float
    net_amount: float
    vat_amount: float
    vat_rate: float
    withholding_amount: float
    withholding_rate: float
    social_charges: float
    social_rate: float
    total_taxes: float
    currency: str
    breakdown: Dict


class VATCalculationRequest(BaseModel):
    amount: float = Field(..., gt=0)
    country: CountryEnum
    rate_type: str = "standard"
    is_franchise: bool = False


class InvoiceRequirementsResponse(BaseModel):
    country: str
    required_fields: List[str]
    optional_fields: Optional[List[str]] = None
    notes: List[str]


class AnnualSummaryRequest(BaseModel):
    country: CountryEnum
    status: TaxStatusEnum
    tax_id: Optional[str] = None
    transactions: List[Dict]


# ============ ENDPOINTS ============

@router.get("/countries")
async def get_supported_countries():
    """Liste des pays supportés avec leurs spécificités"""
    return {
        "countries": [
            {
                "code": "MA",
                "name": "Maroc",
                "currency": "MAD",
                "vat_rates": ["20%", "14%", "10%", "7%", "0%"],
                "features": [
                    "TVA",
                    "Retenue à la source 10%",
                    "IR Auto-entrepreneur",
                    "ICE/IF/RC obligatoires"
                ]
            },
            {
                "code": "FR",
                "name": "France",
                "currency": "EUR",
                "vat_rates": ["20%", "10%", "5.5%", "2.1%"],
                "features": [
                    "TVA",
                    "Franchise TVA micro-entreprise",
                    "Cotisations URSSAF ~22%",
                    "Versement libératoire IR",
                    "SIRET obligatoire"
                ]
            },
            {
                "code": "US",
                "name": "États-Unis",
                "currency": "USD",
                "vat_rates": ["Pas de TVA fédérale"],
                "features": [
                    "Self-employment tax 15.3%",
                    "Backup withholding 24%",
                    "Formulaire W-9",
                    "1099-NEC si > $600",
                    "Taxes trimestrielles"
                ]
            }
        ]
    }


@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_taxes(request: TaxCalculationRequest):
    """Calcul fiscal complet selon le profil"""
    try:
        country_map = {
            CountryEnum.MA: Country.MOROCCO,
            CountryEnum.FR: Country.FRANCE,
            CountryEnum.US: Country.USA
        }
        
        status_map = {
            TaxStatusEnum.auto_entrepreneur: TaxStatus.AUTO_ENTREPRENEUR,
            TaxStatusEnum.micro_enterprise: TaxStatus.MICRO_ENTERPRISE,
            TaxStatusEnum.company: TaxStatus.COMPANY,
            TaxStatusEnum.individual: TaxStatus.INDIVIDUAL,
            TaxStatusEnum.sole_proprietor: TaxStatus.SOLE_PROPRIETOR,
            TaxStatusEnum.llc: TaxStatus.LLC
        }
        
        profile = TaxProfile(
            user_id="temp",
            country=country_map[request.country],
            status=status_map[request.status],
            tax_id=request.tax_id,
            vat_exempt=request.vat_exempt,
            withholding_exempt=request.withholding_exempt
        )
        
        result = unified_calculator.calculate_full_tax(
            profile,
            Decimal(str(request.amount)),
            request.options or {}
        )
        
        return TaxCalculationResponse(
            gross_amount=float(result.gross_amount),
            net_amount=float(result.net_amount),
            vat_amount=float(result.vat_amount),
            vat_rate=float(result.vat_rate),
            withholding_amount=float(result.withholding_amount),
            withholding_rate=float(result.withholding_rate),
            social_charges=float(result.social_charges),
            social_rate=float(result.social_rate),
            total_taxes=float(result.total_taxes),
            currency=result.currency,
            breakdown=_convert_breakdown(result.breakdown)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/vat/calculate")
async def calculate_vat(request: VATCalculationRequest):
    """Calcul de TVA simple"""
    amount = Decimal(str(request.amount))
    
    if request.country == CountryEnum.MA:
        result = morocco_calc.calculate_vat(amount, request.rate_type)
    elif request.country == CountryEnum.FR:
        result = france_calc.calculate_vat(amount, request.rate_type, request.is_franchise)
    else:
        # USA - pas de TVA fédérale
        result = {
            'base_amount': float(amount),
            'vat_rate': 0,
            'vat_amount': 0,
            'total_ttc': float(amount),
            'note': 'No federal VAT in USA. Check state sales tax.'
        }
    
    return _convert_decimal_dict(result)


# ============ MOROCCO SPECIFIC ============

@router.post("/morocco/withholding")
async def calculate_morocco_withholding(
    amount: float = Query(..., gt=0),
    is_exempt: bool = Query(False)
):
    """Calcul retenue à la source Maroc (10%)"""
    result = morocco_calc.calculate_withholding(Decimal(str(amount)), is_exempt)
    return _convert_decimal_dict(result)


@router.post("/morocco/auto-entrepreneur")
async def calculate_morocco_auto_entrepreneur(
    revenue: float = Query(..., gt=0),
    activity_type: str = Query("services", regex="^(services|commerce|artisanat)$")
):
    """Calcul IR auto-entrepreneur Maroc"""
    result = morocco_calc.calculate_auto_entrepreneur_tax(
        Decimal(str(revenue)), 
        activity_type
    )
    return _convert_decimal_dict(result)


@router.get("/morocco/invoice-requirements")
async def get_morocco_invoice_requirements():
    """Mentions obligatoires facture Maroc"""
    return morocco_calc.generate_invoice_requirements()


# ============ FRANCE SPECIFIC ============

@router.post("/france/micro-enterprise")
async def calculate_france_micro_enterprise(
    revenue: float = Query(..., gt=0),
    activity_type: str = Query("bnc", regex="^(bnc|bic_services|bic_commerce)$"),
    liberatory_payment: bool = Query(False)
):
    """Calcul charges micro-entreprise France"""
    result = france_calc.calculate_micro_enterprise_charges(
        Decimal(str(revenue)),
        activity_type,
        liberatory_payment
    )
    return _convert_decimal_dict(result)


@router.get("/france/vat-franchise")
async def check_france_vat_franchise(
    annual_revenue: float = Query(..., gt=0),
    activity_type: str = Query("services", regex="^(services|commerce)$")
):
    """Vérification éligibilité franchise TVA France"""
    result = france_calc.check_vat_franchise(
        Decimal(str(annual_revenue)),
        activity_type
    )
    return _convert_decimal_dict(result)


@router.get("/france/urssaf-declaration")
async def get_france_urssaf_declaration(
    monthly_revenue: float = Query(..., gt=0),
    activity_type: str = Query("bnc")
):
    """Prépare déclaration URSSAF mensuelle"""
    result = france_calc.calculate_urssaf_declaration(
        Decimal(str(monthly_revenue)),
        activity_type
    )
    return _convert_decimal_dict(result)


@router.get("/france/invoice-requirements")
async def get_france_invoice_requirements():
    """Mentions obligatoires facture France"""
    return france_calc.generate_invoice_requirements()


# ============ USA SPECIFIC ============

@router.post("/usa/self-employment-tax")
async def calculate_usa_self_employment_tax(
    net_income: float = Query(..., gt=0)
):
    """Calcul self-employment tax USA (15.3%)"""
    result = usa_calc.calculate_self_employment_tax(Decimal(str(net_income)))
    return _convert_decimal_dict(result)


@router.post("/usa/backup-withholding")
async def calculate_usa_backup_withholding(
    amount: float = Query(..., gt=0),
    has_w9: bool = Query(True)
):
    """Calcul backup withholding USA (24% si pas de W-9)"""
    result = usa_calc.calculate_backup_withholding(Decimal(str(amount)), has_w9)
    return _convert_decimal_dict(result)


@router.get("/usa/1099-check")
async def check_usa_1099_requirement(
    annual_payments: float = Query(..., gt=0)
):
    """Vérifie si formulaire 1099-NEC requis"""
    result = usa_calc.check_1099_requirement(Decimal(str(annual_payments)))
    return _convert_decimal_dict(result)


@router.get("/usa/quarterly-estimate")
async def calculate_usa_quarterly_estimate(
    annual_income: float = Query(..., gt=0),
    filing_status: str = Query("single")
):
    """Calcul paiements trimestriels estimés"""
    result = usa_calc.calculate_quarterly_estimate(
        Decimal(str(annual_income)),
        filing_status
    )
    return _convert_decimal_dict(result)


@router.get("/usa/state-sales-tax")
async def get_usa_state_sales_tax(state: str = Query(..., min_length=2, max_length=2)):
    """Taux sales tax par État"""
    rate = usa_calc.get_state_sales_tax(state.upper())
    return {
        "state": state.upper(),
        "sales_tax_rate": float(rate),
        "sales_tax_percent": f"{float(rate) * 100:.2f}%"
    }


@router.get("/usa/w9-requirements")
async def get_usa_w9_requirements():
    """Informations formulaire W-9"""
    return usa_calc.generate_w9_requirements()


@router.get("/usa/invoice-requirements")
async def get_usa_invoice_requirements():
    """Éléments recommandés invoice USA"""
    return usa_calc.generate_invoice_requirements()


# ============ ANNUAL SUMMARY ============

@router.post("/annual-summary")
async def get_annual_summary(request: AnnualSummaryRequest):
    """Génère un résumé fiscal annuel"""
    country_map = {
        CountryEnum.MA: Country.MOROCCO,
        CountryEnum.FR: Country.FRANCE,
        CountryEnum.US: Country.USA
    }
    
    status_map = {
        TaxStatusEnum.auto_entrepreneur: TaxStatus.AUTO_ENTREPRENEUR,
        TaxStatusEnum.micro_enterprise: TaxStatus.MICRO_ENTERPRISE,
        TaxStatusEnum.company: TaxStatus.COMPANY,
        TaxStatusEnum.individual: TaxStatus.INDIVIDUAL,
        TaxStatusEnum.sole_proprietor: TaxStatus.SOLE_PROPRIETOR,
        TaxStatusEnum.llc: TaxStatus.LLC
    }
    
    profile = TaxProfile(
        user_id="temp",
        country=country_map[request.country],
        status=status_map[request.status],
        tax_id=request.tax_id
    )
    
    return unified_calculator.get_annual_summary(profile, request.transactions)


# ============ TAX RATES REFERENCE ============

@router.get("/rates/{country}")
async def get_tax_rates(country: CountryEnum):
    """Référence des taux fiscaux par pays"""
    if country == CountryEnum.MA:
        return {
            "country": "Maroc",
            "currency": "MAD",
            "vat": {
                "standard": "20%",
                "reduced_14": "14%",
                "reduced_10": "10%",
                "reduced_7": "7%",
                "zero": "0%"
            },
            "withholding": {
                "services": "10%"
            },
            "auto_entrepreneur": {
                "services": "2%",
                "commerce": "1%",
                "artisanat": "0.5%",
                "threshold": "500,000 MAD/an"
            }
        }
    elif country == CountryEnum.FR:
        return {
            "country": "France",
            "currency": "EUR",
            "vat": {
                "standard": "20%",
                "intermediate": "10%",
                "reduced": "5.5%",
                "super_reduced": "2.1%"
            },
            "vat_franchise_thresholds": {
                "services": "34,400 €",
                "commerce": "85,800 €"
            },
            "micro_enterprise": {
                "social_charges_bnc": "22%",
                "social_charges_bic_services": "22%",
                "social_charges_bic_commerce": "12.8%",
                "liberatory_bnc": "2.2%",
                "liberatory_bic_services": "1.7%",
                "liberatory_bic_commerce": "1%"
            }
        }
    else:  # USA
        return {
            "country": "États-Unis",
            "currency": "USD",
            "self_employment_tax": "15.3%",
            "backup_withholding": "24%",
            "form_1099_threshold": "$600",
            "federal_tax_brackets_2024": [
                {"up_to": "$11,600", "rate": "10%"},
                {"up_to": "$47,150", "rate": "12%"},
                {"up_to": "$100,525", "rate": "22%"},
                {"up_to": "$191,950", "rate": "24%"},
                {"up_to": "$243,725", "rate": "32%"},
                {"up_to": "$609,350", "rate": "35%"},
                {"above": "$609,350", "rate": "37%"}
            ],
            "quarterly_due_dates": [
                "April 15",
                "June 15", 
                "September 15",
                "January 15 (following year)"
            ]
        }


# ============ ADVANCED TAX CALCULATIONS ============

@router.post("/morocco/ir-progressive")
async def calculate_morocco_ir_progressive(
    annual_income: float = Query(..., gt=0, description="Revenu annuel brut (MAD)"),
    dependents: int = Query(0, ge=0, description="Nombre de personnes à charge"),
    deductions: float = Query(0, ge=0, description="Déductions fiscales (CNSS, CIMR)")
):
    """
    Calcule l'IR Maroc avec barème progressif 2024 (0% à 38%)
    - Tranches: 0-30k (0%), 30-50k (10%), 50-60k (20%), 60-80k (30%), 80-180k (34%), >180k (38%)
    - Déduction forfaitaire 20% (max 30k MAD)
    - Déduction pour charges de famille: 360 MAD/personne (max 2160 MAD)
    """
    from advanced_tax_calculations import calculate_morocco_ir
    
    result = calculate_morocco_ir(annual_income, dependents, deductions)
    return result


@router.post("/morocco/professional-tax")
async def calculate_morocco_professional_tax(
    annual_income: float = Query(..., gt=0),
    activity_class: str = Query("B", regex="^[ABCD]$", description="Classe A/B/C/D")
):
    """
    Calcule Taxe Professionnelle Maroc
    - Classe A (vente): 600 MAD/an
    - Classe B (services): 1200 MAD/an
    - Classe C (libéral): 2400 MAD/an
    - Classe D (financier): 6000 MAD/an
    + 0.5% du CA excédentaire après 5M MAD
    """
    from advanced_tax_calculations import calculate_morocco_professional_tax
    
    result = calculate_morocco_professional_tax(annual_income, activity_class)
    return result


@router.post("/france/urssaf-detailed")
async def calculate_france_urssaf_detailed(
    revenue: float = Query(..., gt=0, description="CA ou revenu (EUR)"),
    status: str = Query("auto_entrepreneur_bnc", description="auto_entrepreneur_bnc | micro_entreprise_bic_services")
):
    """
    Calcule cotisations URSSAF France détaillées
    - Auto-entrepreneur BNC (services): 22.2%
    - Auto-entrepreneur BIC services: 22.2%
    - Auto-entrepreneur BIC commerce: 12.8%
    - Régime réel: Maladie 6.85%, Alloc familiales 3.1%, CSG/CRDS 9.7%, Retraite 17.75%, etc.
    """
    from advanced_tax_calculations import calculate_france_urssaf
    
    result = calculate_france_urssaf(revenue, status)
    return result


@router.post("/france/ir-progressive")
async def calculate_france_ir_progressive(
    taxable_income: float = Query(..., gt=0, description="Revenu net imposable (EUR)"),
    family_quotient: float = Query(1.0, gt=0, description="Parts fiscales (1 célibataire, 2 couple, +0.5/enfant)")
):
    """
    Calcule IR France barème progressif 2024
    - Tranches: 0-11.3k (0%), 11.3-28.8k (11%), 28.8-82.3k (30%), 82.3-177k (41%), >177k (45%)
    - Système quotient familial
    - Décote si IR < 1929€ (célibataire) ou 3209€ (couple)
    """
    from advanced_tax_calculations import calculate_france_ir
    
    result = calculate_france_ir(taxable_income, family_quotient)
    return result


@router.post("/usa/state-tax/{state}")
async def calculate_usa_state_tax(
    state: str,
    federal_taxable_income: float = Query(..., gt=0, description="Revenu imposable fédéral (USD)")
):
    """
    Calcule impôt d'État USA (50 États)
    - 8 États sans impôt: AK, FL, NV, SD, TN, TX, WA, WY
    - Taux fixe: CO 4.4%, IL 4.95%, PA 3.07%, etc.
    - Taux progressif: CA max 13.3%, NY max 10.9%, NJ max 10.75%, etc.
    """
    from advanced_tax_calculations import calculate_usa_state_tax
    
    result = calculate_usa_state_tax(federal_taxable_income, state)
    return result


@router.post("/usa/federal-tax")
async def calculate_usa_federal_tax(
    taxable_income: float = Query(..., gt=0),
    filing_status: str = Query("single", regex="^(single|married_joint|married_separate|head_of_household)$")
):
    """
    Calcule impôt fédéral USA barème 2024
    - Single: 10% jusqu'à $11.6k, 12% $11.6-47k, 22% $47-100k, 24% $100-192k, 32% $192-244k, 35% $244-609k, 37% >$609k
    - Married joint: Tranches doublées
    """
    from advanced_tax_calculations import calculate_usa_federal_tax_2024
    
    result = calculate_usa_federal_tax_2024(taxable_income, filing_status)
    return result


@router.post("/usa/self-employment-tax")
async def calculate_usa_self_employment_tax(
    net_profit: float = Query(..., gt=0, description="Bénéfice net activité (USD)")
):
    """
    Calcule Self-Employment Tax USA
    - Social Security: 12.4% jusqu'à $160,200 (plafond 2024)
    - Medicare: 2.9% (déplafonné) + 0.9% additionnel si > $200k
    - Total: ~15.3% (déductible à 50% pour IR)
    """
    from advanced_tax_calculations import calculate_usa_self_employment_tax
    
    result = calculate_usa_self_employment_tax(net_profit)
    return result


# ============ PDF GENERATION & EMAIL ============

@router.post("/invoices/{invoice_id}/generate-pdf")
async def generate_invoice_pdf(invoice_id: str):
    """
    Génère PDF pour facture fiscale
    - Mentions légales conformes (MA/FR/US)
    - QR code paiement
    - Logo entreprise
    - Sauvegarde dans storage Supabase
    """
    from supabase_client import supabase
    from pdf_generator import InvoicePDFGenerator
    import os
    
    # Récupérer facture + lignes
    try:
        invoice = supabase.table('fiscal_invoices').select('*').eq('id', invoice_id).single().execute()
    except Exception:
        pass  # .single() might return no results
    if not invoice.data:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    lines = supabase.table('fiscal_invoice_lines').select('*').eq('invoice_id', invoice_id).execute()

    # Récupérer config fiscale
    try:
        settings = supabase.table('fiscal_settings').select('*').eq('user_id', invoice.data['user_id']).single().execute()
    except Exception:
        pass  # .single() might return no results
    
    # Préparer données
    invoice_data = {
        'invoice_number': invoice.data['invoice_number'],
        'issue_date': invoice.data['issue_date'],
        'due_date': invoice.data['due_date'],
        'country': invoice.data['country'],
        'currency': invoice.data['currency']
    }
    
    company_data = {
        'name': settings.data.get('company_name', 'GetYourShare'),
        'address': settings.data.get('address', ''),
        'phone': settings.data.get('phone', ''),
        'email': settings.data.get('email', 'contact@getyourshare.com'),
        'ice': settings.data.get('registration_number', ''),
        'siret': settings.data.get('registration_number', ''),
        'ein': settings.data.get('registration_number', ''),
        'vat_number': settings.data.get('vat_number', ''),
        'iban': settings.data.get('iban', ''),
        'bic': settings.data.get('bic', '')
    }
    
    client_data = {
        'name': invoice.data['client_name'],
        'address': invoice.data.get('client_address', ''),
        'email': invoice.data['client_email'],
        'vat_number': invoice.data.get('client_vat_number', 'N/A')
    }
    
    line_items = [{
        'description': line['description'],
        'quantity': line['quantity'],
        'unit_price': line['unit_price_ht'],
        'vat_rate': line['vat_rate'],
        'total_ht': line['total_ht'],
        'total_vat': line['total_vat'],
        'total_ttc': line['total_ttc']
    } for line in lines.data]
    
    # Générer PDF
    generator = InvoicePDFGenerator()
    output_path = f"temp/{invoice.data['invoice_number']}.pdf"
    os.makedirs("temp", exist_ok=True)
    
    pdf_path = generator.generate_invoice_pdf(
        output_path,
        invoice_data,
        company_data,
        client_data,
        line_items
    )
    
    # Upload vers Supabase Storage
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    storage_path = f"invoices/{invoice.data['user_id']}/{invoice.data['invoice_number']}.pdf"
    supabase.storage.from_('fiscal-documents').upload(storage_path, pdf_bytes, {"content-type": "application/pdf"})
    
    pdf_url = supabase.storage.from_('fiscal-documents').get_public_url(storage_path)
    
    # Mettre à jour facture avec URL PDF
    supabase.table('invoices').update({'pdf_url': pdf_url}).eq('id', invoice_id).execute()
    
    # Nettoyer fichier temporaire
    os.remove(pdf_path)
    
    return {
        "pdf_url": pdf_url,
        "invoice_number": invoice.data['invoice_number']
    }


@router.post("/invoices/{invoice_id}/send-email")
async def send_invoice_email(invoice_id: str, to_email: Optional[str] = None):
    """
    Envoie facture par email avec PDF
    - Template HTML professionnel
    - PDF en pièce jointe
    - Lien paiement
    """
    from supabase_client import supabase
    from fiscal_email_service import FiscalEmailService
    from pdf_generator import InvoicePDFGenerator
    import os
    
    # Récupérer facture
    try:
        invoice = supabase.table('fiscal_invoices').select('*').eq('id', invoice_id).single().execute()
    except Exception:
        pass  # .single() might return no results
    if not invoice.data:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    # Générer PDF si pas déjà fait
    if not invoice.data.get('pdf_url'):
        pdf_result = await generate_invoice_pdf(invoice_id)
        pdf_path = pdf_result['pdf_url']
    else:
        # Télécharger depuis Supabase Storage si disponible
        pdf_url = invoice.data.get('pdf_url', '')
        pdf_path = f"temp/{invoice.data['invoice_number']}.pdf"
        os.makedirs("temp", exist_ok=True)
        if pdf_url:
            try:
                import httpx
                resp = httpx.get(pdf_url, follow_redirects=True, timeout=15)
                if resp.status_code == 200:
                    with open(pdf_path, 'wb') as f:
                        f.write(resp.content)
                else:
                    # Régénérer
                    pdf_result = await generate_invoice_pdf(invoice_id)
                    pdf_path = pdf_result['pdf_url']
            except Exception:
                pdf_result = await generate_invoice_pdf(invoice_id)
                pdf_path = pdf_result['pdf_url']
        else:
            pdf_result = await generate_invoice_pdf(invoice_id)
            pdf_path = pdf_result['pdf_url']
    
    email_service = FiscalEmailService()
    
    invoice_data = {
        'invoice_number': invoice.data['invoice_number'],
        'issue_date': invoice.data['issue_date'],
        'due_date': invoice.data['due_date'],
        'amount_ttc': invoice.data['amount_ttc'],
        'currency': invoice.data['currency']
    }
    
    recipient = to_email or invoice.data['client_email']
    
    success = email_service.send_invoice_email(
        recipient,
        invoice.data['client_name'],
        invoice_data,
        pdf_path,
        invoice.data['country']
    )
    
    if success:
        # Mettre à jour statut facture
        supabase.table('fiscal_invoices').update({
            'status': 'sent',
            'sent_at': datetime.now().isoformat()
        }).eq('id', invoice_id).execute()
        
        return {"success": True, "message": f"Facture envoyée à {recipient}"}
    else:
        raise HTTPException(status_code=500, detail="Échec envoi email")


# ============ HELPER FUNCTIONS ============

def _convert_decimal_dict(d: Dict) -> Dict:
    """Convertit les Decimal en float pour JSON"""
    result = {}
    for key, value in d.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, dict):
            result[key] = _convert_decimal_dict(value)
        else:
            result[key] = value
    return result


def _convert_breakdown(breakdown: Dict) -> Dict:
    """Convertit le breakdown en format JSON-friendly"""
    result = {}
    for key, value in breakdown.items():
        if value is None:
            result[key] = None
        elif isinstance(value, dict):
            result[key] = _convert_decimal_dict(value)
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result
