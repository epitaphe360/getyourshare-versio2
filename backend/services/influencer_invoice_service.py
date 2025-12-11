"""
Service de génération de factures pour les paiements aux influenceurs.
Génère automatiquement une facture conforme lors de chaque paiement.
Supporte MA (Maroc), FR (France), US (États-Unis)
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
import uuid
from io import BytesIO

# Pour la génération PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class InfluencerInvoiceService:
    """Service de génération de factures pour les influenceurs"""
    
    # Configuration des taxes par pays
    TAX_CONFIG = {
        'MA': {
            'name': 'Maroc',
            'currency': 'MAD',
            'currency_symbol': 'DH',
            'withholding_rate': 0.10,  # Retenue à la source 10%
            'withholding_name': 'Retenue à la source (10%)',
            'tax_id_label': 'ICE',
            'legal_mentions': [
                "Facture établie conformément à la législation marocaine",
                "Retenue à la source de 10% applicable sur les prestations de services",
                "Article 15 du CGI - Régime des auto-entrepreneurs"
            ]
        },
        'FR': {
            'name': 'France',
            'currency': 'EUR',
            'currency_symbol': '€',
            'withholding_rate': 0.0,  # Pas de retenue (l'influenceur déclare lui-même)
            'social_rate': 0.22,  # URSSAF micro-entrepreneur
            'social_name': 'Cotisations sociales (22%)',
            'tax_id_label': 'SIRET',
            'legal_mentions': [
                "TVA non applicable, article 293 B du CGI (micro-entreprise)",
                "Dispense d'immatriculation au RCS et au RM",
                "Auto-entrepreneur - Cotisations URSSAF: 22%"
            ]
        },
        'US': {
            'name': 'États-Unis',
            'currency': 'USD',
            'currency_symbol': '$',
            'withholding_rate': 0.24,  # Backup withholding si pas de W-9
            'withholding_name': 'Backup Withholding (24%)',
            'tax_id_label': 'SSN/EIN',
            'legal_mentions': [
                "Payment subject to IRS 1099-NEC reporting requirements",
                "Recipient is responsible for self-employment tax",
                "W-9 form required for tax compliance"
            ]
        }
    }
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.invoice_counter = 0
    
    def generate_invoice_number(self) -> str:
        """Génère un numéro de facture unique"""
        year = datetime.now().year
        # Récupérer le dernier numéro de facture
        try:
            result = self.supabase.table('influencer_invoices')\
                .select('invoice_number')\
                .like('invoice_number', f'INV-{year}-%')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                last_number = result.data[0]['invoice_number']
                # Extraire le numéro séquentiel
                seq = int(last_number.split('-')[-1]) + 1
            else:
                seq = 1
        except Exception:
            seq = 1
        
        return f"INV-{year}-{seq:05d}"
    
    def calculate_amounts(self, gross_amount: float, country: str, has_tax_id: bool = True) -> Dict:
        """
        Calcule les montants (brut, taxes, net) selon le pays
        
        Args:
            gross_amount: Montant brut de la commission
            country: Code pays (MA, FR, US)
            has_tax_id: Si l'influenceur a fourni son identifiant fiscal
        
        Returns:
            Dict avec gross, tax, net, tax_details
        """
        config = self.TAX_CONFIG.get(country, self.TAX_CONFIG['FR'])
        
        tax_amount = 0.0
        tax_details = []
        
        if country == 'MA':
            # Maroc: Retenue à la source de 10%
            tax_amount = gross_amount * config['withholding_rate']
            tax_details.append({
                'name': config['withholding_name'],
                'rate': config['withholding_rate'] * 100,
                'amount': tax_amount
            })
        
        elif country == 'FR':
            # France: Pas de retenue, l'influenceur paie ses cotisations
            # On peut afficher à titre informatif
            estimated_social = gross_amount * config['social_rate']
            tax_details.append({
                'name': f"{config['social_name']} (à payer par l'influenceur)",
                'rate': config['social_rate'] * 100,
                'amount': estimated_social,
                'informative': True  # Pas déduit, juste informatif
            })
        
        elif country == 'US':
            # USA: Backup withholding si pas de W-9
            if not has_tax_id:
                tax_amount = gross_amount * config['withholding_rate']
                tax_details.append({
                    'name': config['withholding_name'],
                    'rate': config['withholding_rate'] * 100,
                    'amount': tax_amount
                })
        
        net_amount = gross_amount - tax_amount
        
        return {
            'gross_amount': round(gross_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'net_amount': round(net_amount, 2),
            'currency': config['currency'],
            'currency_symbol': config['currency_symbol'],
            'tax_details': tax_details
        }
    
    def create_invoice_from_payout(
        self,
        payout_id: str,
        influencer_id: str,
        merchant_id: str,
        amount: float,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Crée une facture lors d'un paiement à un influenceur
        
        Args:
            payout_id: ID du paiement
            influencer_id: ID de l'influenceur
            merchant_id: ID du marchand qui paie
            amount: Montant brut
            period_start: Début de la période couverte
            period_end: Fin de la période couverte
            description: Description du paiement
        
        Returns:
            Dict avec les informations de la facture créée
        """
        # Récupérer les infos de l'influenceur
        influencer_result = self.supabase.table('users')\
            .select('*')\
            .eq('id', influencer_id)\
            .single()\
            .execute()
        
        influencer = influencer_result.data if influencer_result.data else {}
        
        # Récupérer les infos du marchand
        merchant_result = self.supabase.table('users')\
            .select('*')\
            .eq('id', merchant_id)\
            .single()\
            .execute()
        
        merchant = merchant_result.data if merchant_result.data else {}
        
        # Déterminer le pays de l'influenceur
        country = influencer.get('country', 'FR')
        if country not in self.TAX_CONFIG:
            country = 'FR'
        
        # Vérifier si l'influenceur a un ID fiscal
        tax_id = influencer.get('tax_id') or influencer.get('ice') or influencer.get('siret')
        has_tax_id = bool(tax_id)
        
        # Calculer les montants
        amounts = self.calculate_amounts(amount, country, has_tax_id)
        
        # Générer le numéro de facture
        invoice_number = self.generate_invoice_number()
        
        # Créer l'enregistrement de facture
        invoice_data = {
            'id': str(uuid.uuid4()),
            'invoice_number': invoice_number,
            'payout_id': payout_id,
            'influencer_id': influencer_id,
            'merchant_id': merchant_id,
            
            # Montants
            'gross_amount': amounts['gross_amount'],
            'tax_amount': amounts['tax_amount'],
            'net_amount': amounts['net_amount'],
            'currency': amounts['currency'],
            
            # Infos fiscales influenceur
            'influencer_name': f"{influencer.get('first_name', '')} {influencer.get('last_name', '')}".strip(),
            'influencer_email': influencer.get('email', ''),
            'influencer_address': influencer.get('address', ''),
            'influencer_country': country,
            'influencer_tax_id': tax_id,
            'influencer_tax_status': influencer.get('tax_status', 'individual'),
            
            # Infos marchand
            'merchant_name': merchant.get('company_name') or f"{merchant.get('first_name', '')} {merchant.get('last_name', '')}".strip(),
            'merchant_email': merchant.get('email', ''),
            'merchant_address': merchant.get('address', ''),
            'merchant_tax_id': merchant.get('tax_id') or merchant.get('ice') or merchant.get('siret'),
            
            # Période et description
            'period_start': period_start.isoformat() if period_start else None,
            'period_end': period_end.isoformat() if period_end else None,
            'description': description or 'Commission d\'affiliation',
            
            # Détails des taxes (JSON)
            'tax_details': amounts['tax_details'],
            
            # Statut
            'status': 'generated',
            'invoice_date': datetime.now().isoformat(),
            
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Sauvegarder dans la base de données
        try:
            result = self.supabase.table('influencer_invoices')\
                .insert(invoice_data)\
                .execute()
            
            if result.data:
                invoice_data['id'] = result.data[0]['id']
        except Exception as e:
            print(f"Erreur lors de la création de la facture: {e}")
            # Continuer même si l'insertion échoue
        
        return invoice_data
    
    def generate_pdf(self, invoice_data: Dict) -> Optional[bytes]:
        """
        Génère le PDF de la facture
        
        Args:
            invoice_data: Données de la facture
        
        Returns:
            bytes du PDF ou None si erreur
        """
        if not REPORTLAB_AVAILABLE:
            print("ReportLab non disponible pour la génération PDF")
            return None
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Style personnalisé
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb')
        )
        
        # En-tête
        elements.append(Paragraph("FACTURE", title_style))
        elements.append(Paragraph(f"N° {invoice_data.get('invoice_number', 'N/A')}", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Informations générales
        invoice_date = invoice_data.get('invoice_date', datetime.now().isoformat())
        if isinstance(invoice_date, str):
            try:
                invoice_date = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
            except Exception:
                invoice_date = datetime.now()
        
        info_data = [
            ['Date de facture:', invoice_date.strftime('%d/%m/%Y')],
            ['Devise:', invoice_data.get('currency', 'EUR')],
        ]
        
        if invoice_data.get('period_start') and invoice_data.get('period_end'):
            info_data.append(['Période:', f"{invoice_data['period_start'][:10]} au {invoice_data['period_end'][:10]}"])
        
        info_table = Table(info_data, colWidths=[4*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Bloc Émetteur (Influenceur) et Destinataire (Marchand)
        country = invoice_data.get('influencer_country', 'FR')
        config = self.TAX_CONFIG.get(country, self.TAX_CONFIG['FR'])
        
        from_to_data = [
            ['ÉMETTEUR (Prestataire)', 'DESTINATAIRE (Client)'],
            [
                f"{invoice_data.get('influencer_name', 'N/A')}\n"
                f"{invoice_data.get('influencer_email', '')}\n"
                f"{invoice_data.get('influencer_address', '')}\n"
                f"{config['tax_id_label']}: {invoice_data.get('influencer_tax_id', 'Non renseigné')}",
                
                f"{invoice_data.get('merchant_name', 'N/A')}\n"
                f"{invoice_data.get('merchant_email', '')}\n"
                f"{invoice_data.get('merchant_address', '')}\n"
                f"ID Fiscal: {invoice_data.get('merchant_tax_id', 'Non renseigné')}"
            ]
        ]
        
        from_to_table = Table(from_to_data, colWidths=[8*cm, 8*cm])
        from_to_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(from_to_table)
        elements.append(Spacer(1, 30))
        
        # Tableau des prestations
        currency_symbol = config['currency_symbol']
        
        prestations_data = [
            ['Description', 'Montant'],
            [invoice_data.get('description', 'Commission d\'affiliation'), 
             f"{invoice_data.get('gross_amount', 0):,.2f} {currency_symbol}"],
        ]
        
        prestations_table = Table(prestations_data, colWidths=[12*cm, 4*cm])
        prestations_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(prestations_table)
        elements.append(Spacer(1, 20))
        
        # Totaux
        totals_data = [
            ['Sous-total HT:', f"{invoice_data.get('gross_amount', 0):,.2f} {currency_symbol}"],
        ]
        
        # Ajouter les détails des taxes
        tax_details = invoice_data.get('tax_details', [])
        for tax in tax_details:
            if not tax.get('informative', False):
                totals_data.append([
                    f"{tax['name']}:",
                    f"-{tax['amount']:,.2f} {currency_symbol}"
                ])
        
        totals_data.append(['TOTAL NET À PAYER:', f"{invoice_data.get('net_amount', 0):,.2f} {currency_symbol}"])
        
        totals_table = Table(totals_data, colWidths=[12*cm, 4*cm])
        totals_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2563eb')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#2563eb')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        # Mentions légales
        elements.append(Paragraph("Mentions légales", styles['Heading3']))
        for mention in config['legal_mentions']:
            elements.append(Paragraph(f"• {mention}", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Note informative pour les cotisations (France)
        if country == 'FR':
            for tax in tax_details:
                if tax.get('informative'):
                    note_style = ParagraphStyle(
                        'Note',
                        parent=styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#6b7280'),
                        backColor=colors.HexColor('#fef3c7'),
                        borderPadding=10
                    )
                    elements.append(Paragraph(
                        f"<b>Note:</b> {tax['name']} estimées à {tax['amount']:,.2f} {currency_symbol} "
                        f"(non déduites, à déclarer par le prestataire)",
                        note_style
                    ))
        
        # Générer le PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def get_invoices_for_merchant(
        self, 
        merchant_id: str, 
        year: Optional[int] = None,
        influencer_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Récupère les factures des influenceurs pour un marchand
        
        Args:
            merchant_id: ID du marchand
            year: Année fiscale (optionnel)
            influencer_id: Filtrer par influenceur (optionnel)
            limit: Nombre max de résultats
        
        Returns:
            Liste des factures
        """
        query = self.supabase.table('influencer_invoices')\
            .select('*')\
            .eq('merchant_id', merchant_id)\
            .order('created_at', desc=True)\
            .limit(limit)
        
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            query = query.gte('invoice_date', start_date).lte('invoice_date', end_date)
        
        if influencer_id:
            query = query.eq('influencer_id', influencer_id)
        
        result = query.execute()
        return result.data if result.data else []
    
    def get_annual_summary(self, merchant_id: str, year: int) -> Dict:
        """
        Génère un récapitulatif annuel pour les impôts
        
        Args:
            merchant_id: ID du marchand
            year: Année fiscale
        
        Returns:
            Dict avec le récapitulatif
        """
        invoices = self.get_invoices_for_merchant(merchant_id, year)
        
        # Grouper par influenceur
        by_influencer = {}
        total_gross = 0
        total_tax = 0
        total_net = 0
        
        for inv in invoices:
            inf_id = inv.get('influencer_id')
            if inf_id not in by_influencer:
                by_influencer[inf_id] = {
                    'influencer_id': inf_id,
                    'influencer_name': inv.get('influencer_name', 'N/A'),
                    'influencer_tax_id': inv.get('influencer_tax_id'),
                    'influencer_country': inv.get('influencer_country'),
                    'total_gross': 0,
                    'total_tax': 0,
                    'total_net': 0,
                    'invoice_count': 0
                }
            
            by_influencer[inf_id]['total_gross'] += inv.get('gross_amount', 0)
            by_influencer[inf_id]['total_tax'] += inv.get('tax_amount', 0)
            by_influencer[inf_id]['total_net'] += inv.get('net_amount', 0)
            by_influencer[inf_id]['invoice_count'] += 1
            
            total_gross += inv.get('gross_amount', 0)
            total_tax += inv.get('tax_amount', 0)
            total_net += inv.get('net_amount', 0)
        
        return {
            'year': year,
            'merchant_id': merchant_id,
            'total_invoices': len(invoices),
            'total_gross': round(total_gross, 2),
            'total_tax_withheld': round(total_tax, 2),
            'total_net_paid': round(total_net, 2),
            'by_influencer': list(by_influencer.values()),
            'generated_at': datetime.now().isoformat()
        }
