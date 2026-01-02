"""
Générateur PDF Factures Professionnelles
Conforme aux normes légales Maroc/France/USA
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import qrcode
from io import BytesIO
import base64
from typing import Dict, List, Optional
import os


class InvoicePDFGenerator:
    """Générateur PDF factures multi-pays avec mentions légales"""
    
    def __init__(self, logo_path: Optional[str] = None):
        self.logo_path = logo_path or "assets/logo.png"
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Styles personnalisés pour factures"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#262626'),
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='LegalMentions',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#8c8c8c'),
            spaceAfter=3,
            alignment=TA_CENTER
        ))
    
    def _generate_qr_code(self, payment_data: Dict) -> BytesIO:
        """Génère QR code pour paiement"""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        
        # Format QR selon pays
        if payment_data.get('country') == 'MA':
            # Format CMI Maroc
            qr_text = f"CMI:{payment_data.get('iban')}:{payment_data.get('amount')}:{payment_data.get('reference')}"
        elif payment_data.get('country') == 'FR':
            # Format SEPA France
            qr_text = f"BCD\n002\n1\nSCT\n{payment_data.get('bic')}\n{payment_data.get('company_name')}\n{payment_data.get('iban')}\nEUR{payment_data.get('amount')}\n\n{payment_data.get('reference')}"
        else:
            # Format générique USA/Autres
            qr_text = f"PAY:{payment_data.get('amount')}:{payment_data.get('reference')}"
        
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def _get_legal_mentions(self, country: str, company_data: Dict) -> List[str]:
        """Mentions légales obligatoires selon pays"""
        mentions = []
        
        if country == 'MA':
            mentions = [
                f"ICE: {company_data.get('ice', 'N/A')}",
                f"IF: {company_data.get('if_number', 'N/A')}",
                f"RC: {company_data.get('rc', 'N/A')}",
                f"Patente: {company_data.get('patente', 'N/A')}",
                f"CNSS: {company_data.get('cnss', 'N/A')}",
                "TVA - Article 87 du CGI",
                "Paiement sous 30 jours. Pénalités de retard: 12% annuel",
                "Conservation obligatoire 10 ans - Art 146 CGI"
            ]
        elif country == 'FR':
            mentions = [
                f"SIRET: {company_data.get('siret', 'N/A')}",
                f"TVA: {company_data.get('vat_number', 'N/A')}",
                f"Capital social: {company_data.get('capital', '0')} EUR",
                f"RCS {company_data.get('rcs_city', 'Paris')} {company_data.get('rcs_number', 'N/A')}",
                "TVA sur les débits - Article 269-2 CGI",
                "Escompte pour paiement anticipé: 0%",
                "Pénalités de retard: 3 fois taux BCE (Art L441-10)",
                "Indemnité forfaitaire pour frais de recouvrement: 40 EUR",
                "Facture au format FEC - BOI-CF-IOR-60-40-20"
            ]
        else:  # USA
            mentions = [
                f"EIN: {company_data.get('ein', 'N/A')}",
                f"Business License: {company_data.get('business_license', 'N/A')}",
                "Payment due within 30 days",
                "Late payment fee: 1.5% per month (18% APR)",
                "This invoice is issued in accordance with IRS regulations",
                f"State: {company_data.get('state', 'CA')} - Sales Tax ID: {company_data.get('sales_tax_id', 'N/A')}"
            ]
        
        return mentions
    
    def generate_invoice_pdf(
        self,
        output_path: str,
        invoice_data: Dict,
        company_data: Dict,
        client_data: Dict,
        line_items: List[Dict]
    ) -> str:
        """
        Génère PDF facture professionnel
        
        Args:
            output_path: Chemin fichier PDF de sortie
            invoice_data: {invoice_number, issue_date, due_date, country, currency}
            company_data: {name, address, ice/siret/ein, logo_url, iban, bic}
            client_data: {name, address, vat_number, email}
            line_items: [{description, quantity, unit_price, vat_rate, total_ht, total_vat, total_ttc}]
        
        Returns:
            Chemin absolu du PDF généré
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # === EN-TÊTE AVEC LOGO ===
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=4*cm, height=2*cm)
            story.append(logo)
            story.append(Spacer(1, 0.5*cm))
        
        # Titre FACTURE
        invoice_title = f"FACTURE / INVOICE N° {invoice_data['invoice_number']}"
        story.append(Paragraph(invoice_title, self.styles['InvoiceTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # === INFOS ENTREPRISE + CLIENT ===
        company_client_data = [
            ['ÉMETTEUR / FROM', 'CLIENT / TO'],
            [
                Paragraph(f"<b>{company_data['name']}</b><br/>{company_data.get('address', '')}<br/>Tél: {company_data.get('phone', '')}<br/>Email: {company_data.get('email', '')}", self.styles['CompanyInfo']),
                Paragraph(f"<b>{client_data['name']}</b><br/>{client_data.get('address', '')}<br/>Email: {client_data.get('email', '')}<br/>N° TVA: {client_data.get('vat_number', 'N/A')}", self.styles['CompanyInfo'])
            ]
        ]
        
        company_client_table = Table(company_client_data, colWidths=[9*cm, 9*cm])
        company_client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#262626')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(company_client_table)
        story.append(Spacer(1, 0.8*cm))
        
        # === DATES ===
        dates_data = [
            ['Date émission', 'Date échéance', 'Devise'],
            [
                invoice_data['issue_date'],
                invoice_data['due_date'],
                invoice_data['currency']
            ]
        ]
        dates_table = Table(dates_data, colWidths=[6*cm, 6*cm, 6*cm])
        dates_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(dates_table)
        story.append(Spacer(1, 1*cm))
        
        # === LIGNES FACTURE ===
        items_header = ['Description', 'Qté', 'Prix HT', 'TVA %', 'Total HT', 'Total TTC']
        items_data = [items_header]
        
        total_ht = 0
        total_vat = 0
        total_ttc = 0
        
        for item in line_items:
            items_data.append([
                item['description'],
                str(item['quantity']),
                f"{item['unit_price']:.2f}",
                f"{item['vat_rate']}%",
                f"{item['total_ht']:.2f}",
                f"{item['total_ttc']:.2f}"
            ])
            total_ht += item['total_ht']
            total_vat += item['total_vat']
            total_ttc += item['total_ttc']
        
        items_table = Table(items_data, colWidths=[7*cm, 1.5*cm, 2*cm, 1.5*cm, 2.5*cm, 2.5*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.5*cm))
        
        # === TOTAUX ===
        totals_data = [
            ['', 'Total HT', f"{total_ht:.2f} {invoice_data['currency']}"],
            ['', 'Total TVA', f"{total_vat:.2f} {invoice_data['currency']}"],
            ['', 'TOTAL TTC', f"{total_ttc:.2f} {invoice_data['currency']}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[11*cm, 3.5*cm, 3.5*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (-1, -1), 11),
            ('BACKGROUND', (1, 2), (-1, 2), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (1, 2), (-1, 2), colors.whitesmoke),
            ('LINEABOVE', (1, 0), (-1, 0), 1, colors.grey),
            ('LINEABOVE', (1, 2), (-1, 2), 2, colors.HexColor('#1890ff'))
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 1*cm))
        
        # === QR CODE PAIEMENT ===
        qr_data = {
            'country': invoice_data['country'],
            'amount': total_ttc,
            'reference': invoice_data['invoice_number'],
            'iban': company_data.get('iban', ''),
            'bic': company_data.get('bic', ''),
            'company_name': company_data['name']
        }
        qr_buffer = self._generate_qr_code(qr_data)
        qr_image = Image(qr_buffer, width=3*cm, height=3*cm)
        
        payment_info = [
            [qr_image, Paragraph(f"<b>PAIEMENT / PAYMENT</b><br/>IBAN: {company_data.get('iban', 'N/A')}<br/>BIC: {company_data.get('bic', 'N/A')}<br/>Référence: {invoice_data['invoice_number']}", self.styles['Normal'])]
        ]
        payment_table = Table(payment_info, colWidths=[4*cm, 14*cm])
        payment_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1890ff'))
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 1*cm))
        
        # === MENTIONS LÉGALES ===
        legal_mentions = self._get_legal_mentions(invoice_data['country'], company_data)
        for mention in legal_mentions:
            story.append(Paragraph(mention, self.styles['LegalMentions']))
        
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Signature électronique à venir",
            self.styles['LegalMentions']
        ))
        
        # Génération PDF
        doc.build(story)
        return os.path.abspath(output_path)


# === EXEMPLE D'UTILISATION ===
if __name__ == "__main__":
    generator = InvoicePDFGenerator()
    
    # Exemple Maroc
    invoice_data = {
        'invoice_number': 'FA-2024-1001',
        'issue_date': '01/12/2024',
        'due_date': '31/12/2024',
        'country': 'MA',
        'currency': 'MAD'
    }
    
    company_data = {
        'name': 'GetYourShare SARL',
        'address': 'Casablanca, Maroc',
        'phone': '+212 5 22 00 00 00',
        'email': 'contact@getyourshare.ma',
        'ice': '002345678000045',
        'if_number': '12345678',
        'rc': 'Casa 123456',
        'patente': '78901234',
        'cnss': '9876543',
        'iban': 'MA64011519000001205000534921',
        'bic': 'BCMAMAMC'
    }
    
    client_data = {
        'name': 'Beauty Salon Casablanca',
        'address': 'Maarif, Casablanca',
        'email': 'beauty@example.ma',
        'vat_number': 'MA-123456'
    }
    
    line_items = [
        {
            'description': 'Abonnement Premium - 3 mois',
            'quantity': 1,
            'unit_price': 2500.00,
            'vat_rate': 20.0,
            'total_ht': 2500.00,
            'total_vat': 500.00,
            'total_ttc': 3000.00
        },
        {
            'description': 'Service d\'influence marketing',
            'quantity': 5,
            'unit_price': 300.00,
            'vat_rate': 20.0,
            'total_ht': 1500.00,
            'total_vat': 300.00,
            'total_ttc': 1800.00
        }
    ]
    
    output = generator.generate_invoice_pdf(
        'facture_test.pdf',
        invoice_data,
        company_data,
        client_data,
        line_items
    )
    
    print(f"✅ Facture PDF générée: {output}")
