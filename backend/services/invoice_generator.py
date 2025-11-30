"""
Générateur de factures PDF conformes
Supporte Maroc, France et USA
"""

import io
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import base64


@dataclass
class InvoiceItem:
    """Ligne de facture"""
    description: str
    quantity: float
    unit_price: float
    vat_rate: float = 0.0
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price
    
    @property
    def vat_amount(self) -> float:
        return self.subtotal * self.vat_rate
    
    @property
    def total(self) -> float:
        return self.subtotal + self.vat_amount


@dataclass
class CompanyInfo:
    """Informations entreprise"""
    name: str
    address: str
    city: str
    postal_code: str
    country: str
    email: Optional[str] = None
    phone: Optional[str] = None
    # Identifiants fiscaux
    tax_id: Optional[str] = None  # ICE (MA), SIRET (FR), EIN (US)
    vat_number: Optional[str] = None
    # Maroc spécifique
    ice: Optional[str] = None
    if_number: Optional[str] = None  # Identifiant Fiscal
    rc: Optional[str] = None  # Registre de Commerce
    cnss: Optional[str] = None
    # France spécifique
    siret: Optional[str] = None
    siren: Optional[str] = None
    rcs: Optional[str] = None
    capital: Optional[str] = None
    # USA spécifique
    ein: Optional[str] = None
    state: Optional[str] = None


@dataclass
class Invoice:
    """Structure de facture"""
    invoice_number: str
    invoice_date: date
    due_date: date
    seller: CompanyInfo
    buyer: CompanyInfo
    items: List[InvoiceItem]
    currency: str = "EUR"
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    bank_details: Optional[Dict] = None
    # Mentions légales
    legal_mentions: List[str] = field(default_factory=list)
    
    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_vat(self) -> float:
        return sum(item.vat_amount for item in self.items)
    
    @property
    def total(self) -> float:
        return self.subtotal + self.total_vat
    
    @property
    def vat_breakdown(self) -> Dict[float, Dict]:
        """Décomposition TVA par taux"""
        breakdown = {}
        for item in self.items:
            rate = item.vat_rate
            if rate not in breakdown:
                breakdown[rate] = {'base': 0, 'vat': 0}
            breakdown[rate]['base'] += item.subtotal
            breakdown[rate]['vat'] += item.vat_amount
        return breakdown


class InvoiceGenerator:
    """Générateur de factures"""
    
    CURRENCY_SYMBOLS = {
        'MAD': 'DH',
        'EUR': '€',
        'USD': '$'
    }
    
    def __init__(self):
        pass
    
    def generate_invoice_number(self, prefix: str = "INV", year: int = None) -> str:
        """Génère un numéro de facture unique"""
        if year is None:
            year = datetime.now().year
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{year}-{timestamp[-6:]}"
    
    def create_morocco_invoice(self, seller: CompanyInfo, buyer: CompanyInfo,
                                items: List[InvoiceItem], **kwargs) -> Invoice:
        """Crée une facture conforme aux normes marocaines"""
        
        legal_mentions = [
            f"ICE: {seller.ice or 'Non renseigné'}",
            f"IF: {seller.if_number or 'Non renseigné'}",
            f"RC: {seller.rc or 'Non renseigné'}",
        ]
        
        if seller.cnss:
            legal_mentions.append(f"CNSS: {seller.cnss}")
        
        # Vérifier si exonéré de TVA
        if kwargs.get('vat_exempt'):
            legal_mentions.append("Exonéré de TVA conformément à l'article 91 du CGI")
        
        # Mention retenue à la source si applicable
        if kwargs.get('withholding'):
            legal_mentions.append("Retenue à la source de 10% applicable sur le montant HT")
        
        invoice = Invoice(
            invoice_number=kwargs.get('invoice_number') or self.generate_invoice_number("FAC"),
            invoice_date=kwargs.get('invoice_date') or date.today(),
            due_date=kwargs.get('due_date') or date.today(),
            seller=seller,
            buyer=buyer,
            items=items,
            currency="MAD",
            notes=kwargs.get('notes'),
            payment_terms=kwargs.get('payment_terms', "Paiement à réception de facture"),
            bank_details=kwargs.get('bank_details'),
            legal_mentions=legal_mentions
        )
        
        return invoice
    
    def create_france_invoice(self, seller: CompanyInfo, buyer: CompanyInfo,
                               items: List[InvoiceItem], **kwargs) -> Invoice:
        """Crée une facture conforme aux normes françaises"""
        
        legal_mentions = []
        
        # SIRET obligatoire
        if seller.siret:
            legal_mentions.append(f"SIRET: {seller.siret}")
        
        # Numéro TVA intra si assujetti
        if seller.vat_number:
            legal_mentions.append(f"N° TVA Intracommunautaire: {seller.vat_number}")
        
        # RCS
        if seller.rcs:
            legal_mentions.append(f"RCS: {seller.rcs}")
        
        # Capital si société
        if seller.capital:
            legal_mentions.append(f"Capital: {seller.capital}")
        
        # Micro-entreprise - franchise TVA
        if kwargs.get('vat_franchise'):
            legal_mentions.append("TVA non applicable, art. 293 B du CGI")
        
        # Mentions obligatoires paiement
        legal_mentions.extend([
            "Pénalités de retard: 3 fois le taux d'intérêt légal",
            "Indemnité forfaitaire pour frais de recouvrement: 40€"
        ])
        
        invoice = Invoice(
            invoice_number=kwargs.get('invoice_number') or self.generate_invoice_number("FA"),
            invoice_date=kwargs.get('invoice_date') or date.today(),
            due_date=kwargs.get('due_date') or date.today(),
            seller=seller,
            buyer=buyer,
            items=items,
            currency="EUR",
            notes=kwargs.get('notes'),
            payment_terms=kwargs.get('payment_terms', "Paiement à 30 jours"),
            bank_details=kwargs.get('bank_details'),
            legal_mentions=legal_mentions
        )
        
        return invoice
    
    def create_usa_invoice(self, seller: CompanyInfo, buyer: CompanyInfo,
                           items: List[InvoiceItem], **kwargs) -> Invoice:
        """Crée une invoice conforme aux normes US"""
        
        legal_mentions = []
        
        # EIN si disponible
        if seller.ein:
            legal_mentions.append(f"EIN: {seller.ein}")
        
        # État
        if seller.state:
            legal_mentions.append(f"State: {seller.state}")
        
        # Sales tax notice si applicable
        if kwargs.get('sales_tax_state'):
            legal_mentions.append(f"Sales Tax applies in {kwargs['sales_tax_state']}")
        
        invoice = Invoice(
            invoice_number=kwargs.get('invoice_number') or self.generate_invoice_number("INV"),
            invoice_date=kwargs.get('invoice_date') or date.today(),
            due_date=kwargs.get('due_date') or date.today(),
            seller=seller,
            buyer=buyer,
            items=items,
            currency="USD",
            notes=kwargs.get('notes'),
            payment_terms=kwargs.get('payment_terms', "Net 30"),
            bank_details=kwargs.get('bank_details'),
            legal_mentions=legal_mentions
        )
        
        return invoice
    
    def generate_html(self, invoice: Invoice) -> str:
        """Génère le HTML de la facture"""
        currency_symbol = self.CURRENCY_SYMBOLS.get(invoice.currency, invoice.currency)
        
        # Générer les lignes d'articles
        items_html = ""
        for item in invoice.items:
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{item.description}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item.quantity}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{item.unit_price:,.2f} {currency_symbol}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item.vat_rate * 100:.0f}%</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{item.total:,.2f} {currency_symbol}</td>
            </tr>
            """
        
        # Générer le détail TVA
        vat_details_html = ""
        for rate, amounts in invoice.vat_breakdown.items():
            if rate > 0:
                vat_details_html += f"""
                <tr>
                    <td style="padding: 8px;">TVA {rate * 100:.0f}%</td>
                    <td style="padding: 8px; text-align: right;">{amounts['base']:,.2f} {currency_symbol}</td>
                    <td style="padding: 8px; text-align: right;">{amounts['vat']:,.2f} {currency_symbol}</td>
                </tr>
                """
        
        # Mentions légales
        legal_html = "<br>".join(invoice.legal_mentions)
        
        # Informations bancaires
        bank_html = ""
        if invoice.bank_details:
            bank_html = f"""
            <div style="margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #374151;">Coordonnées Bancaires</h4>
                <p style="margin: 5px 0; color: #6b7280;">
                    {invoice.bank_details.get('bank_name', '')}<br>
                    IBAN: {invoice.bank_details.get('iban', '')}<br>
                    BIC: {invoice.bank_details.get('bic', '')}
                </p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Facture {invoice.invoice_number}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: #f3f4f6;
                }}
                .invoice-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e5e7eb;
                }}
                .invoice-title {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4f46e5;
                    margin: 0;
                }}
                .invoice-number {{
                    font-size: 14px;
                    color: #6b7280;
                    margin-top: 5px;
                }}
                .parties {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 40px;
                }}
                .party {{
                    width: 45%;
                }}
                .party-label {{
                    font-size: 12px;
                    text-transform: uppercase;
                    color: #9ca3af;
                    margin-bottom: 8px;
                    letter-spacing: 1px;
                }}
                .party-name {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #111827;
                    margin-bottom: 8px;
                }}
                .party-details {{
                    font-size: 14px;
                    color: #6b7280;
                    line-height: 1.6;
                }}
                .dates {{
                    display: flex;
                    gap: 40px;
                    margin-bottom: 30px;
                }}
                .date-item {{
                    padding: 15px 20px;
                    background: #f8fafc;
                    border-radius: 8px;
                }}
                .date-label {{
                    font-size: 12px;
                    color: #9ca3af;
                    text-transform: uppercase;
                }}
                .date-value {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #111827;
                    margin-top: 4px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }}
                th {{
                    background: #4f46e5;
                    color: white;
                    padding: 14px 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                th:first-child {{
                    border-radius: 8px 0 0 0;
                }}
                th:last-child {{
                    border-radius: 0 8px 0 0;
                    text-align: right;
                }}
                .totals {{
                    display: flex;
                    justify-content: flex-end;
                    margin-bottom: 30px;
                }}
                .totals-table {{
                    width: 300px;
                }}
                .totals-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .totals-row.grand-total {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #4f46e5;
                    border-bottom: none;
                    padding-top: 15px;
                }}
                .legal-mentions {{
                    font-size: 12px;
                    color: #6b7280;
                    padding: 20px;
                    background: #f8fafc;
                    border-radius: 8px;
                    line-height: 1.8;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    text-align: center;
                    font-size: 12px;
                    color: #9ca3af;
                }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <div class="header">
                    <div>
                        <h1 class="invoice-title">FACTURE</h1>
                        <div class="invoice-number">N° {invoice.invoice_number}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 24px; font-weight: bold; color: #111827;">{invoice.total:,.2f} {currency_symbol}</div>
                        <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">Montant Total TTC</div>
                    </div>
                </div>
                
                <div class="parties">
                    <div class="party">
                        <div class="party-label">De</div>
                        <div class="party-name">{invoice.seller.name}</div>
                        <div class="party-details">
                            {invoice.seller.address}<br>
                            {invoice.seller.postal_code} {invoice.seller.city}<br>
                            {invoice.seller.country}
                            {f'<br>{invoice.seller.email}' if invoice.seller.email else ''}
                            {f'<br>{invoice.seller.phone}' if invoice.seller.phone else ''}
                        </div>
                    </div>
                    <div class="party">
                        <div class="party-label">À</div>
                        <div class="party-name">{invoice.buyer.name}</div>
                        <div class="party-details">
                            {invoice.buyer.address}<br>
                            {invoice.buyer.postal_code} {invoice.buyer.city}<br>
                            {invoice.buyer.country}
                            {f'<br>{invoice.buyer.email}' if invoice.buyer.email else ''}
                        </div>
                    </div>
                </div>
                
                <div class="dates">
                    <div class="date-item">
                        <div class="date-label">Date de facture</div>
                        <div class="date-value">{invoice.invoice_date.strftime('%d/%m/%Y')}</div>
                    </div>
                    <div class="date-item">
                        <div class="date-label">Date d'échéance</div>
                        <div class="date-value">{invoice.due_date.strftime('%d/%m/%Y')}</div>
                    </div>
                    <div class="date-item">
                        <div class="date-label">Conditions</div>
                        <div class="date-value">{invoice.payment_terms or 'À réception'}</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th style="text-align: center;">Qté</th>
                            <th style="text-align: right;">Prix Unit.</th>
                            <th style="text-align: center;">TVA</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div class="totals">
                    <div class="totals-table">
                        <div class="totals-row">
                            <span>Sous-total HT</span>
                            <span>{invoice.subtotal:,.2f} {currency_symbol}</span>
                        </div>
                        <div class="totals-row">
                            <span>TVA</span>
                            <span>{invoice.total_vat:,.2f} {currency_symbol}</span>
                        </div>
                        <div class="totals-row grand-total">
                            <span>Total TTC</span>
                            <span>{invoice.total:,.2f} {currency_symbol}</span>
                        </div>
                    </div>
                </div>
                
                {bank_html}
                
                <div class="legal-mentions">
                    <strong>Mentions légales:</strong><br>
                    {legal_html}
                </div>
                
                {f'<div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 8px; color: #92400e;"><strong>Notes:</strong> {invoice.notes}</div>' if invoice.notes else ''}
                
                <div class="footer">
                    Facture générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')} | GetYourShare
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def to_dict(self, invoice: Invoice) -> Dict:
        """Convertit une facture en dictionnaire"""
        return {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.isoformat(),
            'due_date': invoice.due_date.isoformat(),
            'currency': invoice.currency,
            'seller': {
                'name': invoice.seller.name,
                'address': invoice.seller.address,
                'city': invoice.seller.city,
                'postal_code': invoice.seller.postal_code,
                'country': invoice.seller.country,
                'email': invoice.seller.email,
                'tax_id': invoice.seller.tax_id,
                'vat_number': invoice.seller.vat_number
            },
            'buyer': {
                'name': invoice.buyer.name,
                'address': invoice.buyer.address,
                'city': invoice.buyer.city,
                'postal_code': invoice.buyer.postal_code,
                'country': invoice.buyer.country,
                'email': invoice.buyer.email
            },
            'items': [
                {
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'vat_rate': item.vat_rate,
                    'subtotal': item.subtotal,
                    'vat_amount': item.vat_amount,
                    'total': item.total
                }
                for item in invoice.items
            ],
            'subtotal': invoice.subtotal,
            'total_vat': invoice.total_vat,
            'total': invoice.total,
            'vat_breakdown': {
                f"{rate * 100:.0f}%": amounts 
                for rate, amounts in invoice.vat_breakdown.items()
            },
            'payment_terms': invoice.payment_terms,
            'notes': invoice.notes,
            'legal_mentions': invoice.legal_mentions
        }
