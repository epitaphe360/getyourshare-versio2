"""
Service de génération PDF factures conformes
Maroc (ICE/IF/RC), France (SIRET), USA (EIN/SSN)
Utilise ReportLab pour génération PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import os
import tempfile
from io import BytesIO
from supabase import Client

from services.tax_calculator import (
    UnifiedTaxCalculator,
    TaxProfile,
    Country,
    TaxStatus
)

import logging
logger = logging.getLogger(__name__)


class InvoicePDFGenerator:
    """Générateur de factures PDF conformes multi-pays"""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.tax_calculator = UnifiedTaxCalculator()

        # Configuration chemins
        self.storage_bucket = "invoices"
        self.temp_dir = tempfile.gettempdir()


    def generate_invoice_morocco(
        self,
        invoice_data: Dict,
        company_data: Dict,
        client_data: Dict,
        line_items: List[Dict],
        tax_profile: TaxProfile
    ) -> bytes:
        """
        Génère une facture PDF conforme Maroc

        Args:
            invoice_data: {invoice_number, date, due_date}
            company_data: {name, ice, if, rc, address, phone, email}
            client_data: {name, address, phone, email}
            line_items: [{description, quantity, unit_price, vat_rate}]
            tax_profile: Profil fiscal

        Returns:
            Bytes du PDF généré
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Style personnalisé
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )

        # En-tête FACTURE
        elements.append(Paragraph("FACTURE", title_style))
        elements.append(Spacer(1, 12))

        # Informations société (obligatoire Maroc)
        company_info = f"""
        <b>{company_data['name']}</b><br/>
        {company_data['address']}<br/>
        ICE: {company_data['ice']}<br/>
        IF: {company_data.get('if', 'N/A')}<br/>
        RC: {company_data.get('rc', 'N/A')}<br/>
        Tél: {company_data['phone']}<br/>
        Email: {company_data['email']}
        """

        client_info = f"""
        <b>Client:</b><br/>
        {client_data['name']}<br/>
        {client_data.get('address', '')}<br/>
        {client_data.get('phone', '')}<br/>
        {client_data.get('email', '')}
        """

        # Table en-tête (2 colonnes)
        header_table = Table([
            [Paragraph(company_info, header_style), Paragraph(client_info, header_style)]
        ], colWidths=[3*inch, 3*inch])

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Informations facture
        invoice_info_data = [
            ['Numéro de facture:', invoice_data['invoice_number']],
            ['Date d\'émission:', invoice_data['date']],
            ['Date d\'échéance:', invoice_data.get('due_date', 'À réception')],
        ]

        invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch])
        invoice_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(invoice_info_table)
        elements.append(Spacer(1, 20))

        # Tableau des articles
        items_data = [['Description', 'Qté', 'P.U. HT', 'TVA', 'Total HT', 'Total TTC']]

        subtotal_ht = Decimal('0')
        total_vat = Decimal('0')

        for item in line_items:
            qty = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            vat_rate = Decimal(str(item.get('vat_rate', 0.20)))

            line_total_ht = qty * unit_price
            line_vat = line_total_ht * vat_rate
            line_total_ttc = line_total_ht + line_vat

            subtotal_ht += line_total_ht
            total_vat += line_vat

            items_data.append([
                item['description'],
                str(qty),
                f"{unit_price:.2f} MAD",
                f"{vat_rate * 100:.0f}%",
                f"{line_total_ht:.2f} MAD",
                f"{line_total_ttc:.2f} MAD"
            ])

        items_table = Table(items_data, colWidths=[2.5*inch, 0.5*inch, 1*inch, 0.7*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 20))

        # Totaux
        total_ttc = subtotal_ht + total_vat

        totals_data = [
            ['Total HT:', f"{subtotal_ht:.2f} MAD"],
            ['Total TVA:', f"{total_vat:.2f} MAD"],
            ['Total TTC:', f"{total_ttc:.2f} MAD"],
        ]

        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EEF2FF')),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4F46E5')),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 30))

        # Mentions légales obligatoires Maroc
        legal_text = f"""
        <b>Mentions légales:</b><br/>
        Facture conforme aux dispositions de la loi marocaine.<br/>
        ICE: {company_data['ice']} | IF: {company_data.get('if', 'N/A')} | RC: {company_data.get('rc', 'N/A')}<br/>
        TVA détaillée par taux appliqué.<br/>
        Paiement par virement bancaire ou chèque à l'ordre de {company_data['name']}.<br/>
        """

        if invoice_data.get('payment_terms'):
            legal_text += f"Conditions de paiement: {invoice_data['payment_terms']}<br/>"

        legal_style = ParagraphStyle(
            'Legal',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leading=10
        )

        elements.append(Paragraph(legal_text, legal_style))

        # Générer PDF
        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


    def generate_invoice_france(
        self,
        invoice_data: Dict,
        company_data: Dict,
        client_data: Dict,
        line_items: List[Dict],
        tax_profile: TaxProfile
    ) -> bytes:
        """
        Génère une facture PDF conforme France
        Mentions obligatoires: SIRET, TVA intracommunautaire, pénalités retard
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Similaire à Maroc mais avec mentions françaises
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        elements.append(Paragraph("FACTURE", title_style))
        elements.append(Spacer(1, 12))

        # Informations société (obligatoire France)
        company_info = f"""
        <b>{company_data['name']}</b><br/>
        {company_data.get('legal_form', 'SARL')} au capital de {company_data.get('capital', '10,000')} EUR<br/>
        {company_data['address']}<br/>
        SIRET: {company_data['siret']}<br/>
        """

        if tax_profile.vat_number:
            company_info += f"TVA intracommunautaire: {tax_profile.vat_number}<br/>"
        else:
            company_info += "TVA non applicable, art. 293 B du CGI<br/>"

        company_info += f"""
        Tél: {company_data['phone']}<br/>
        Email: {company_data['email']}
        """

        client_info = f"""
        <b>Client:</b><br/>
        {client_data['name']}<br/>
        {client_data.get('address', '')}<br/>
        {client_data.get('phone', '')}<br/>
        {client_data.get('email', '')}
        """

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )

        header_table = Table([
            [Paragraph(company_info, header_style), Paragraph(client_info, header_style)]
        ], colWidths=[3*inch, 3*inch])

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Numéro de facture (chronologique obligatoire)
        invoice_info_data = [
            ['Numéro de facture:', invoice_data['invoice_number']],
            ['Date d\'émission:', invoice_data['date']],
            ['Date de prestation:', invoice_data.get('service_date', invoice_data['date'])],
            ['Date d\'échéance:', invoice_data.get('due_date', 'À réception')],
        ]

        invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch])
        invoice_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        elements.append(invoice_info_table)
        elements.append(Spacer(1, 20))

        # Tableau des articles
        items_data = [['Description', 'Qté', 'P.U. HT', 'TVA', 'Total HT', 'Total TTC']]

        subtotal_ht = Decimal('0')
        total_vat = Decimal('0')

        for item in line_items:
            qty = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            vat_rate = Decimal(str(item.get('vat_rate', 0.20 if not tax_profile.vat_exempt else 0)))

            line_total_ht = qty * unit_price
            line_vat = line_total_ht * vat_rate
            line_total_ttc = line_total_ht + line_vat

            subtotal_ht += line_total_ht
            total_vat += line_vat

            vat_display = f"{vat_rate * 100:.1f}%" if not tax_profile.vat_exempt else "N/A"

            items_data.append([
                item['description'],
                str(qty),
                f"{unit_price:.2f} €",
                vat_display,
                f"{line_total_ht:.2f} €",
                f"{line_total_ttc:.2f} €"
            ])

        items_table = Table(items_data, colWidths=[2.5*inch, 0.5*inch, 1*inch, 0.7*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 20))

        # Totaux
        total_ttc = subtotal_ht + total_vat

        totals_data = [
            ['Total HT:', f"{subtotal_ht:.2f} €"],
        ]

        if not tax_profile.vat_exempt:
            totals_data.append(['Total TVA:', f"{total_vat:.2f} €"])

        totals_data.append(['Total TTC:', f"{total_ttc:.2f} €"])

        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EEF2FF')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4F46E5')),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 30))

        # Mentions légales obligatoires France
        legal_text = f"""
        <b>Conditions de paiement:</b><br/>
        Échéance: {invoice_data.get('due_date', 'À réception')}<br/>
        Pénalités de retard: 3 fois le taux d'intérêt légal (L. 441-10 du Code de commerce)<br/>
        Indemnité forfaitaire pour frais de recouvrement: 40 € (Art. L. 441-10 et D. 441-5)<br/>
        """

        if tax_profile.vat_exempt:
            legal_text += "<b>TVA non applicable, art. 293 B du CGI</b><br/>"

        legal_text += f"""
        <br/>
        SIRET: {company_data['siret']}<br/>
        Conservation obligatoire: 10 ans<br/>
        """

        legal_style = ParagraphStyle(
            'Legal',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leading=10
        )

        elements.append(Paragraph(legal_text, legal_style))

        # Générer PDF
        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


    def generate_invoice_usa(
        self,
        invoice_data: Dict,
        company_data: Dict,
        client_data: Dict,
        line_items: List[Dict],
        tax_profile: TaxProfile
    ) -> bytes:
        """
        Génère une facture PDF conforme USA
        Pas de VAT, Sales Tax optionnel par État
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)  # Letter pour USA
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 12))

        # Company info
        company_info = f"""
        <b>{company_data['name']}</b><br/>
        {company_data['address']}<br/>
        """

        if tax_profile.tax_id:
            company_info += f"EIN/SSN: {tax_profile.tax_id}<br/>"

        company_info += f"""
        Phone: {company_data['phone']}<br/>
        Email: {company_data['email']}
        """

        client_info = f"""
        <b>Bill To:</b><br/>
        {client_data['name']}<br/>
        {client_data.get('address', '')}<br/>
        {client_data.get('phone', '')}<br/>
        {client_data.get('email', '')}
        """

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )

        header_table = Table([
            [Paragraph(company_info, header_style), Paragraph(client_info, header_style)]
        ], colWidths=[3*inch, 3*inch])

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Invoice info
        invoice_info_data = [
            ['Invoice Number:', invoice_data['invoice_number']],
            ['Invoice Date:', invoice_data['date']],
            ['Due Date:', invoice_data.get('due_date', 'Upon Receipt')],
        ]

        invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch])
        invoice_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        elements.append(invoice_info_table)
        elements.append(Spacer(1, 20))

        # Line items
        items_data = [['Description', 'Qty', 'Unit Price', 'Amount']]

        subtotal = Decimal('0')

        for item in line_items:
            qty = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            line_total = qty * unit_price

            subtotal += line_total

            items_data.append([
                item['description'],
                str(qty),
                f"${unit_price:.2f}",
                f"${line_total:.2f}"
            ])

        items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 20))

        # Totals (avec Sales Tax optionnel)
        totals_data = [
            ['Subtotal:', f"${subtotal:.2f}"],
        ]

        # Sales Tax si applicable
        sales_tax_rate = invoice_data.get('sales_tax_rate', 0)
        if sales_tax_rate > 0:
            sales_tax = subtotal * Decimal(str(sales_tax_rate))
            total = subtotal + sales_tax
            totals_data.append(['Sales Tax:', f"${sales_tax:.2f}"])
        else:
            total = subtotal

        totals_data.append(['Total Due:', f"${total:.2f}"])

        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EEF2FF')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4F46E5')),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 30))

        # Payment terms
        legal_text = f"""
        <b>Payment Terms:</b><br/>
        {invoice_data.get('payment_terms', 'Payment due upon receipt')}<br/>
        <br/>
        <b>Payment Methods:</b><br/>
        {invoice_data.get('payment_methods', 'Bank transfer, Check, Credit Card')}<br/>
        """

        if tax_profile.tax_id:
            legal_text += f"<br/>EIN/SSN: {tax_profile.tax_id}<br/>"

        legal_text += "<br/>Thank you for your business!<br/>"

        legal_style = ParagraphStyle(
            'Legal',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leading=10
        )

        elements.append(Paragraph(legal_text, legal_style))

        # Générer PDF
        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


    def generate_invoice(
        self,
        merchant_id: str,
        client_id: str,
        line_items: List[Dict],
        invoice_type: str = 'sale',
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Génère une facture complète (détection automatique du pays)

        Args:
            merchant_id: ID du merchant
            client_id: ID du client
            line_items: Liste des articles
            invoice_type: Type de facture (sale, service, deposit)
            metadata: Métadonnées additionnelles

        Returns:
            {invoice_id, invoice_number, pdf_url, pdf_bytes}
        """
        try:
            # Récupérer les infos merchant
            merchant = self.supabase.table('users').select('*, profiles(*)').eq('id', merchant_id).single().execute()
            if not merchant.data:
                raise ValueError("Merchant not found")

            merchant_data = merchant.data
            merchant_profile = merchant_data.get('profiles', {})

            # Récupérer les infos client
            client = self.supabase.table('users').select('*, profiles(*)').eq('id', client_id).single().execute()
            if not client.data:
                raise ValueError("Client not found")

            client_data = client.data
            client_profile = client_data.get('profiles', {})

            # Déterminer le pays
            country_code = merchant_profile.get('country', 'MA')
            if country_code == 'MA':
                country = Country.MOROCCO
            elif country_code == 'FR':
                country = Country.FRANCE
            elif country_code == 'US':
                country = Country.USA
            else:
                country = Country.MOROCCO  # Défaut

            # Créer le profil fiscal
            tax_profile = TaxProfile(
                user_id=merchant_id,
                country=country,
                status=TaxStatus.COMPANY,
                tax_id=merchant_profile.get('tax_id'),
                vat_number=merchant_profile.get('vat_number'),
                vat_exempt=merchant_profile.get('vat_exempt', False)
            )

            # Générer le numéro de facture (chronologique)
            invoice_number = self._generate_invoice_number(merchant_id, country)

            # Données facture
            invoice_data = {
                'invoice_number': invoice_number,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'payment_terms': metadata.get('payment_terms', 'Net 30'),
                'payment_methods': metadata.get('payment_methods', 'Bank Transfer'),
                'sales_tax_rate': metadata.get('sales_tax_rate', 0)
            }

            # Préparer company_data
            company_data = {
                'name': merchant_profile.get('company_name', merchant_data.get('email')),
                'address': merchant_profile.get('address', ''),
                'phone': merchant_profile.get('phone', ''),
                'email': merchant_data.get('email'),
            }

            if country == Country.MOROCCO:
                company_data.update({
                    'ice': merchant_profile.get('ice', 'N/A'),
                    'if': merchant_profile.get('if_number'),
                    'rc': merchant_profile.get('rc'),
                })
            elif country == Country.FRANCE:
                company_data.update({
                    'siret': merchant_profile.get('siret', 'N/A'),
                    'legal_form': merchant_profile.get('legal_form', 'SARL'),
                    'capital': merchant_profile.get('capital', '10,000'),
                })

            # Préparer client_data
            client_data_formatted = {
                'name': client_profile.get('company_name') or f"{client_profile.get('first_name', '')} {client_profile.get('last_name', '')}".strip() or client_data.get('email'),
                'address': client_profile.get('address', ''),
                'phone': client_profile.get('phone', ''),
                'email': client_data.get('email'),
            }

            # Générer le PDF selon le pays
            if country == Country.MOROCCO:
                pdf_bytes = self.generate_invoice_morocco(
                    invoice_data, company_data, client_data_formatted, line_items, tax_profile
                )
            elif country == Country.FRANCE:
                pdf_bytes = self.generate_invoice_france(
                    invoice_data, company_data, client_data_formatted, line_items, tax_profile
                )
            elif country == Country.USA:
                pdf_bytes = self.generate_invoice_usa(
                    invoice_data, company_data, client_data_formatted, line_items, tax_profile
                )
            else:
                raise ValueError(f"Unsupported country: {country}")

            # Sauvegarder dans la DB
            invoice_record = {
                'invoice_number': invoice_number,
                'merchant_id': merchant_id,
                'client_id': client_id,
                'invoice_type': invoice_type,
                'country': country.value,
                'total_ht': sum(Decimal(str(item['quantity'])) * Decimal(str(item['unit_price'])) for item in line_items),
                'status': 'generated',
                'metadata': metadata or {}
            }

            result = self.supabase.table('invoices').insert(invoice_record).execute()

            if not result.data:
                raise Exception("Error creating invoice record")

            invoice_id = result.data[0]['id']

            # Upload PDF vers Supabase Storage
            filename = f"{invoice_number}.pdf"
            pdf_path = f"{merchant_id}/{filename}"

            # Upload vers storage
            upload_result = self.supabase.storage.from_(self.storage_bucket).upload(
                pdf_path,
                pdf_bytes,
                file_options={"content-type": "application/pdf"}
            )

            # Générer URL publique
            pdf_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(pdf_path)

            # Mettre à jour l'invoice avec l'URL
            self.supabase.table('invoices').update({
                'pdf_url': pdf_url,
                'pdf_path': pdf_path
            }).eq('id', invoice_id).execute()

            return {
                'invoice_id': invoice_id,
                'invoice_number': invoice_number,
                'pdf_url': pdf_url,
                'pdf_bytes': pdf_bytes,
                'country': country.value
            }

        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            raise


    def _generate_invoice_number(self, merchant_id: str, country: Country) -> str:
        """
        Génère un numéro de facture chronologique unique
        Format: {YEAR}-{COUNTRY}-{SEQUENCE}
        Exemple: 2025-MA-00001
        """
        year = datetime.now().year
        country_code = country.value

        # Récupérer la dernière facture de l'année en cours
        result = self.supabase.table('invoices').select('invoice_number').eq('merchant_id', merchant_id).like('invoice_number', f"{year}-{country_code}-%").order('created_at', desc=True).limit(1).execute()

        if result.data and len(result.data) > 0:
            last_number = result.data[0]['invoice_number']
            # Extraire le numéro séquentiel
            sequence = int(last_number.split('-')[-1]) + 1
        else:
            sequence = 1

        return f"{year}-{country_code}-{sequence:05d}"


    async def send_invoice_email(
        self,
        invoice_id: str,
        recipient_email: str,
        subject: Optional[str] = None
    ) -> bool:
        """
        Envoie la facture par email avec PDF en pièce jointe
        """
        try:
            # Récupérer l'invoice
            invoice = self.supabase.table('invoices').select('*').eq('id', invoice_id).single().execute()

            if not invoice.data:
                raise ValueError("Invoice not found")

            invoice_data = invoice.data

            # Télécharger le PDF depuis storage
            pdf_bytes = self.supabase.storage.from_(self.storage_bucket).download(invoice_data['pdf_path'])

            # TODO: Implémenter l'envoi email avec le service email
            # Pour l'instant, retourner True (à implémenter avec email_service.py)

            # Marquer comme envoyée
            self.supabase.table('invoices').update({
                'status': 'sent',
                'sent_at': datetime.now().isoformat()
            }).eq('id', invoice_id).execute()

            return True

        except Exception as e:
            logger.error(f"Error sending invoice email: {e}")
            return False
