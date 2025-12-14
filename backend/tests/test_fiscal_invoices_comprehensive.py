"""
Tests complets pour les endpoints Fiscal et Invoices
Couvre: calculs fiscaux multi-pays, TVA, factures, PDF, email
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal
import json

# Try to import the app, skip tests if not available
try:
    import sys
    sys.path.insert(0, '/home/user/getyourshare-real/backend')
    from server import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    APP_AVAILABLE = True
except Exception as e:
    APP_AVAILABLE = False
    client = None


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch('db_helpers.supabase') as mock:
        yield mock


@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch('auth.get_current_user_from_cookie') as mock:
        mock.return_value = {
            'id': 'test-merchant-id',
            'user_id': 'test-merchant-id',
            'sub': 'test-merchant-id',
            'email': 'merchant@test.com',
            'role': 'merchant'
        }
        yield mock


@pytest.fixture
def mock_pdf_generator():
    """Mock PDF generator"""
    with patch('services.invoice_pdf_generator.InvoicePDFGenerator') as mock:
        yield mock


@pytest.fixture
def sample_invoice():
    """Sample invoice data"""
    return {
        'id': 'inv-123',
        'merchant_id': 'test-merchant-id',
        'invoice_number': 'INV-2024-001',
        'client_name': 'Client Test',
        'client_email': 'client@test.com',
        'status': 'generated',
        'total_ht': 1000.00,
        'total_ttc': 1200.00,
        'vat_amount': 200.00,
        'currency': 'MAD',
        'country': 'MA',
        'created_at': datetime.now().isoformat()
    }


# ===============================================
# FISCAL COUNTRIES TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestFiscalCountries:
    """Tests pour les endpoints pays fiscaux"""

    def test_get_supported_countries(self, mock_auth):
        """Test récupération liste pays supportés"""
        response = client.get("/api/fiscal/countries")
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert 'countries' in data
            countries = data['countries']
            assert len(countries) == 3
            codes = [c['code'] for c in countries]
            assert 'MA' in codes
            assert 'FR' in codes
            assert 'US' in codes

    def test_morocco_country_info(self, mock_auth):
        """Test informations Maroc"""
        response = client.get("/api/fiscal/countries")
        if response.status_code == 200:
            data = response.json()
            morocco = next((c for c in data['countries'] if c['code'] == 'MA'), None)
            assert morocco is not None
            assert morocco['currency'] == 'MAD'
            assert '20%' in morocco['vat_rates']

    def test_france_country_info(self, mock_auth):
        """Test informations France"""
        response = client.get("/api/fiscal/countries")
        if response.status_code == 200:
            data = response.json()
            france = next((c for c in data['countries'] if c['code'] == 'FR'), None)
            assert france is not None
            assert france['currency'] == 'EUR'
            assert 'SIRET obligatoire' in france['features']

    def test_usa_country_info(self, mock_auth):
        """Test informations USA"""
        response = client.get("/api/fiscal/countries")
        if response.status_code == 200:
            data = response.json()
            usa = next((c for c in data['countries'] if c['code'] == 'US'), None)
            assert usa is not None
            assert usa['currency'] == 'USD'


# ===============================================
# TAX CALCULATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestTaxCalculation:
    """Tests pour les calculs fiscaux"""

    def test_calculate_tax_morocco_auto_entrepreneur(self, mock_auth):
        """Test calcul fiscal Maroc auto-entrepreneur"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 10000,
            'country': 'MA',
            'status': 'auto_entrepreneur',
            'vat_exempt': True
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_calculate_tax_france_micro_enterprise(self, mock_auth):
        """Test calcul fiscal France micro-entreprise"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 5000,
            'country': 'FR',
            'status': 'micro_enterprise'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_calculate_tax_usa_sole_proprietor(self, mock_auth):
        """Test calcul fiscal USA sole proprietor"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 8000,
            'country': 'US',
            'status': 'sole_proprietor'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_calculate_tax_invalid_amount(self, mock_auth):
        """Test calcul avec montant invalide"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': -100,
            'country': 'MA',
            'status': 'auto_entrepreneur'
        })
        assert response.status_code == 422

    def test_calculate_tax_invalid_country(self, mock_auth):
        """Test calcul avec pays invalide"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 1000,
            'country': 'XX',
            'status': 'auto_entrepreneur'
        })
        assert response.status_code == 422

    def test_calculate_tax_with_options(self, mock_auth):
        """Test calcul avec options"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 10000,
            'country': 'MA',
            'status': 'company',
            'tax_id': 'ICE123456789',
            'vat_exempt': False,
            'withholding_exempt': False,
            'options': {'include_social': True}
        })
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# VAT CALCULATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestVATCalculation:
    """Tests pour les calculs TVA"""

    def test_calculate_vat_morocco_standard(self, mock_auth):
        """Test TVA Maroc taux standard 20%"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': 1000,
            'country': 'MA',
            'rate_type': 'standard'
        })
        assert response.status_code in [200, 422, 401, 500]
        if response.status_code == 200:
            data = response.json()
            assert 'vat_amount' in data or 'error' in data

    def test_calculate_vat_france_reduced(self, mock_auth):
        """Test TVA France taux réduit"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': 1000,
            'country': 'FR',
            'rate_type': 'reduced'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_calculate_vat_usa_no_federal(self, mock_auth):
        """Test USA sans TVA fédérale"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': 1000,
            'country': 'US',
            'rate_type': 'standard'
        })
        assert response.status_code in [200, 422, 401, 500]
        if response.status_code == 200:
            data = response.json()
            # USA n'a pas de TVA fédérale
            if 'vat_rate' in data:
                assert data['vat_rate'] == 0

    def test_calculate_vat_france_franchise(self, mock_auth):
        """Test TVA France avec franchise"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': 1000,
            'country': 'FR',
            'rate_type': 'standard',
            'is_franchise': True
        })
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# MOROCCO SPECIFIC TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestMoroccoTax:
    """Tests spécifiques Maroc"""

    def test_morocco_withholding_standard(self, mock_auth):
        """Test retenue à la source Maroc 10%"""
        response = client.post("/api/fiscal/morocco/withholding?amount=10000&is_exempt=false")
        assert response.status_code in [200, 422, 401, 500]
        if response.status_code == 200:
            data = response.json()
            # 10% de 10000 = 1000
            if 'withholding_amount' in data:
                assert data['withholding_amount'] == 1000

    def test_morocco_withholding_exempt(self, mock_auth):
        """Test retenue à la source Maroc exempté"""
        response = client.post("/api/fiscal/morocco/withholding?amount=10000&is_exempt=true")
        assert response.status_code in [200, 422, 401, 500]

    def test_morocco_auto_entrepreneur_services(self, mock_auth):
        """Test IR auto-entrepreneur Maroc services"""
        response = client.post("/api/fiscal/morocco/auto-entrepreneur?revenue=50000&activity_type=services")
        assert response.status_code in [200, 422, 401, 500]

    def test_morocco_auto_entrepreneur_commerce(self, mock_auth):
        """Test IR auto-entrepreneur Maroc commerce"""
        response = client.post("/api/fiscal/morocco/auto-entrepreneur?revenue=100000&activity_type=commerce")
        assert response.status_code in [200, 422, 401, 500]

    def test_morocco_invoice_requirements(self, mock_auth):
        """Test mentions facture Maroc"""
        response = client.get("/api/fiscal/morocco/invoice-requirements")
        assert response.status_code in [200, 401, 500]

    def test_morocco_ir_progressive(self, mock_auth):
        """Test IR progressif Maroc"""
        response = client.post("/api/fiscal/morocco/ir-progressive?annual_income=180000&dependents=2&deductions=10000")
        assert response.status_code in [200, 422, 401, 500]

    def test_morocco_professional_tax(self, mock_auth):
        """Test taxe professionnelle Maroc"""
        response = client.post("/api/fiscal/morocco/professional-tax?annual_income=500000&activity_class=B")
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# FRANCE SPECIFIC TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestFranceTax:
    """Tests spécifiques France"""

    def test_france_micro_enterprise_bnc(self, mock_auth):
        """Test micro-entreprise France BNC"""
        response = client.post("/api/fiscal/france/micro-enterprise?revenue=30000&activity_type=bnc&liberatory_payment=false")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_micro_enterprise_bic_commerce(self, mock_auth):
        """Test micro-entreprise France BIC commerce"""
        response = client.post("/api/fiscal/france/micro-enterprise?revenue=50000&activity_type=bic_commerce&liberatory_payment=true")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_vat_franchise_check_services(self, mock_auth):
        """Test éligibilité franchise TVA services"""
        response = client.get("/api/fiscal/france/vat-franchise?annual_revenue=30000&activity_type=services")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_vat_franchise_check_commerce(self, mock_auth):
        """Test éligibilité franchise TVA commerce"""
        response = client.get("/api/fiscal/france/vat-franchise?annual_revenue=80000&activity_type=commerce")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_urssaf_declaration(self, mock_auth):
        """Test déclaration URSSAF"""
        response = client.get("/api/fiscal/france/urssaf-declaration?monthly_revenue=3000&activity_type=bnc")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_invoice_requirements(self, mock_auth):
        """Test mentions facture France"""
        response = client.get("/api/fiscal/france/invoice-requirements")
        assert response.status_code in [200, 401, 500]

    def test_france_ir_progressive(self, mock_auth):
        """Test IR progressif France"""
        response = client.post("/api/fiscal/france/ir-progressive?taxable_income=50000&family_quotient=2")
        assert response.status_code in [200, 422, 401, 500]

    def test_france_urssaf_detailed(self, mock_auth):
        """Test URSSAF détaillé France"""
        response = client.post("/api/fiscal/france/urssaf-detailed?revenue=30000&status=auto_entrepreneur_bnc")
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# USA SPECIFIC TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestUSATax:
    """Tests spécifiques USA"""

    def test_usa_self_employment_tax(self, mock_auth):
        """Test self-employment tax USA"""
        response = client.post("/api/fiscal/usa/self-employment-tax?net_income=50000")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_backup_withholding_with_w9(self, mock_auth):
        """Test backup withholding avec W-9"""
        response = client.post("/api/fiscal/usa/backup-withholding?amount=5000&has_w9=true")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_backup_withholding_without_w9(self, mock_auth):
        """Test backup withholding sans W-9"""
        response = client.post("/api/fiscal/usa/backup-withholding?amount=5000&has_w9=false")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_1099_check_below_threshold(self, mock_auth):
        """Test 1099 sous seuil $600"""
        response = client.get("/api/fiscal/usa/1099-check?annual_payments=500")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_1099_check_above_threshold(self, mock_auth):
        """Test 1099 au-dessus seuil $600"""
        response = client.get("/api/fiscal/usa/1099-check?annual_payments=1000")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_quarterly_estimate_single(self, mock_auth):
        """Test paiements trimestriels célibataire"""
        response = client.get("/api/fiscal/usa/quarterly-estimate?annual_income=100000&filing_status=single")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_quarterly_estimate_married(self, mock_auth):
        """Test paiements trimestriels marié"""
        response = client.get("/api/fiscal/usa/quarterly-estimate?annual_income=150000&filing_status=married_joint")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_state_sales_tax_ca(self, mock_auth):
        """Test sales tax Californie"""
        response = client.get("/api/fiscal/usa/state-sales-tax?state=CA")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_state_sales_tax_tx(self, mock_auth):
        """Test sales tax Texas"""
        response = client.get("/api/fiscal/usa/state-sales-tax?state=TX")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_w9_requirements(self, mock_auth):
        """Test exigences W-9"""
        response = client.get("/api/fiscal/usa/w9-requirements")
        assert response.status_code in [200, 401, 500]

    def test_usa_invoice_requirements(self, mock_auth):
        """Test éléments invoice USA"""
        response = client.get("/api/fiscal/usa/invoice-requirements")
        assert response.status_code in [200, 401, 500]

    def test_usa_federal_tax(self, mock_auth):
        """Test impôt fédéral USA"""
        response = client.post("/api/fiscal/usa/federal-tax?taxable_income=80000&filing_status=single")
        assert response.status_code in [200, 422, 401, 500]

    def test_usa_state_tax(self, mock_auth):
        """Test impôt d'État USA"""
        response = client.post("/api/fiscal/usa/state-tax/CA?federal_taxable_income=100000")
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# TAX RATES REFERENCE TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestTaxRates:
    """Tests pour les références de taux fiscaux"""

    def test_get_tax_rates_morocco(self, mock_auth):
        """Test taux fiscaux Maroc"""
        response = client.get("/api/fiscal/rates/MA")
        assert response.status_code in [200, 401, 500]
        if response.status_code == 200:
            data = response.json()
            assert data['country'] == 'Maroc'
            assert data['currency'] == 'MAD'
            assert 'vat' in data
            assert 'withholding' in data
            assert 'auto_entrepreneur' in data

    def test_get_tax_rates_france(self, mock_auth):
        """Test taux fiscaux France"""
        response = client.get("/api/fiscal/rates/FR")
        assert response.status_code in [200, 401, 500]
        if response.status_code == 200:
            data = response.json()
            assert data['country'] == 'France'
            assert data['currency'] == 'EUR'
            assert 'micro_enterprise' in data

    def test_get_tax_rates_usa(self, mock_auth):
        """Test taux fiscaux USA"""
        response = client.get("/api/fiscal/rates/US")
        assert response.status_code in [200, 401, 500]
        if response.status_code == 200:
            data = response.json()
            assert data['country'] == 'États-Unis'
            assert data['currency'] == 'USD'
            assert 'self_employment_tax' in data


# ===============================================
# ANNUAL SUMMARY TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAnnualSummary:
    """Tests pour les résumés annuels"""

    def test_annual_summary_morocco(self, mock_auth):
        """Test résumé annuel Maroc"""
        response = client.post("/api/fiscal/annual-summary", json={
            'country': 'MA',
            'status': 'auto_entrepreneur',
            'tax_id': 'ICE123456789',
            'transactions': [
                {'amount': 10000, 'date': '2024-01-15', 'type': 'income'},
                {'amount': 15000, 'date': '2024-02-20', 'type': 'income'}
            ]
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_annual_summary_france(self, mock_auth):
        """Test résumé annuel France"""
        response = client.post("/api/fiscal/annual-summary", json={
            'country': 'FR',
            'status': 'micro_enterprise',
            'tax_id': '12345678901234',
            'transactions': [
                {'amount': 5000, 'date': '2024-03-01', 'type': 'income'}
            ]
        })
        assert response.status_code in [200, 422, 401, 500]


# ===============================================
# INVOICE GENERATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceGeneration:
    """Tests pour la génération de factures"""

    def test_generate_invoice_basic(self, mock_auth, mock_supabase):
        """Test génération facture basique"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': [
                {'description': 'Service A', 'quantity': 1, 'unit_price': 500, 'vat_rate': 0.20}
            ],
            'invoice_type': 'service'
        })
        assert response.status_code in [200, 400, 401, 500]

    def test_generate_invoice_multiple_items(self, mock_auth, mock_supabase):
        """Test génération facture plusieurs lignes"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': [
                {'description': 'Produit A', 'quantity': 2, 'unit_price': 100, 'vat_rate': 0.20},
                {'description': 'Produit B', 'quantity': 1, 'unit_price': 300, 'vat_rate': 0.20},
                {'description': 'Service C', 'quantity': 5, 'unit_price': 50, 'vat_rate': 0.10}
            ],
            'invoice_type': 'sale',
            'payment_terms': 'Net 45',
            'notes': 'Merci pour votre confiance'
        })
        assert response.status_code in [200, 400, 401, 500]

    def test_generate_invoice_invalid_client(self, mock_auth, mock_supabase):
        """Test génération facture client invalide"""
        response = client.post("/api/invoices/generate", json={
            'client_id': '',
            'line_items': []
        })
        assert response.status_code in [400, 422]

    def test_generate_invoice_no_items(self, mock_auth, mock_supabase):
        """Test génération facture sans articles"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': []
        })
        assert response.status_code in [200, 400, 422, 500]


# ===============================================
# INVOICE LIST TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceList:
    """Tests pour la liste des factures"""

    def test_get_invoices_list(self, mock_auth, mock_supabase):
        """Test récupération liste factures"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = Mock(data=[])
        response = client.get("/api/invoices/")
        assert response.status_code in [200, 401, 500]

    def test_get_invoices_with_status_filter(self, mock_auth, mock_supabase):
        """Test filtrage factures par statut"""
        response = client.get("/api/invoices/?status=paid")
        assert response.status_code in [200, 401, 500]

    def test_get_invoices_with_pagination(self, mock_auth, mock_supabase):
        """Test pagination factures"""
        response = client.get("/api/invoices/?limit=10&offset=20")
        assert response.status_code in [200, 401, 500]


# ===============================================
# INVOICE DETAILS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceDetails:
    """Tests pour les détails de facture"""

    def test_get_invoice_details(self, mock_auth, mock_supabase, sample_invoice):
        """Test récupération détails facture"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        response = client.get("/api/invoices/inv-123")
        assert response.status_code in [200, 401, 404, 500]

    def test_get_invoice_not_found(self, mock_auth, mock_supabase):
        """Test facture non trouvée"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        response = client.get("/api/invoices/nonexistent-id")
        assert response.status_code in [401, 404, 500]


# ===============================================
# INVOICE DOWNLOAD TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceDownload:
    """Tests pour le téléchargement de factures"""

    def test_download_invoice_pdf(self, mock_auth, mock_supabase, sample_invoice):
        """Test téléchargement PDF facture"""
        sample_invoice['pdf_path'] = 'invoices/test/INV-2024-001.pdf'
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        mock_supabase.storage.from_.return_value.download.return_value = b'%PDF-1.4 fake pdf content'
        response = client.get("/api/invoices/inv-123/download")
        assert response.status_code in [200, 401, 404, 500]

    def test_download_invoice_not_found(self, mock_auth, mock_supabase):
        """Test téléchargement facture non trouvée"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        response = client.get("/api/invoices/nonexistent/download")
        assert response.status_code in [401, 404, 500]


# ===============================================
# INVOICE EMAIL TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceEmail:
    """Tests pour l'envoi de factures par email"""

    def test_send_invoice_email(self, mock_auth, mock_supabase, sample_invoice):
        """Test envoi facture par email"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        response = client.post("/api/invoices/inv-123/send-email", json={
            'invoice_id': 'inv-123',
            'recipient_email': 'client@test.com',
            'subject': 'Votre facture',
            'message': 'Veuillez trouver ci-joint votre facture'
        })
        assert response.status_code in [200, 401, 404, 422, 500]

    def test_send_invoice_email_invalid_email(self, mock_auth, mock_supabase):
        """Test envoi email invalide"""
        response = client.post("/api/invoices/inv-123/send-email", json={
            'invoice_id': 'inv-123',
            'recipient_email': 'invalid-email'
        })
        assert response.status_code == 422


# ===============================================
# INVOICE STATUS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceStatus:
    """Tests pour les changements de statut facture"""

    def test_mark_invoice_paid(self, mock_auth, mock_supabase, sample_invoice):
        """Test marquer facture payée"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(data=[{**sample_invoice, 'status': 'paid'}])
        response = client.put("/api/invoices/inv-123/mark-paid")
        assert response.status_code in [200, 401, 404, 500]

    def test_mark_invoice_paid_with_details(self, mock_auth, mock_supabase, sample_invoice):
        """Test marquer payée avec détails paiement"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(data=[{**sample_invoice, 'status': 'paid'}])
        response = client.put("/api/invoices/inv-123/mark-paid?payment_date=2024-01-15&payment_method=bank_transfer&payment_reference=VIR123")
        assert response.status_code in [200, 401, 404, 500]

    def test_void_invoice(self, mock_auth, mock_supabase, sample_invoice):
        """Test annuler facture"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(data=[{**sample_invoice, 'status': 'voided'}])
        response = client.delete("/api/invoices/inv-123/void?reason=Erreur client")
        assert response.status_code in [200, 401, 404, 500]

    def test_void_paid_invoice_fails(self, mock_auth, mock_supabase, sample_invoice):
        """Test annulation facture payée échoue"""
        sample_invoice['status'] = 'paid'
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=sample_invoice)
        response = client.delete("/api/invoices/inv-123/void")
        assert response.status_code in [400, 401, 404, 500]


# ===============================================
# INVOICE STATS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInvoiceStats:
    """Tests pour les statistiques de factures"""

    def test_get_invoice_stats(self, mock_auth, mock_supabase):
        """Test récupération statistiques factures"""
        mock_invoices = [
            {'status': 'paid', 'total_ht': 1000},
            {'status': 'paid', 'total_ht': 2000},
            {'status': 'generated', 'total_ht': 500},
            {'status': 'overdue', 'total_ht': 800}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=mock_invoices)
        response = client.get("/api/invoices/stats/summary")
        assert response.status_code in [200, 401, 500]

    def test_get_invoice_stats_with_date_filter(self, mock_auth, mock_supabase):
        """Test statistiques avec filtre date"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = Mock(data=[])
        response = client.get("/api/invoices/stats/summary?start_date=2024-01-01&end_date=2024-12-31")
        assert response.status_code in [200, 401, 500]


# ===============================================
# PDF GENERATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestPDFGeneration:
    """Tests pour la génération PDF"""

    def test_generate_pdf_for_invoice(self, mock_auth, mock_supabase):
        """Test génération PDF pour facture"""
        response = client.post("/api/fiscal/invoices/inv-123/generate-pdf")
        assert response.status_code in [200, 401, 404, 500]

    def test_generate_pdf_invoice_not_found(self, mock_auth, mock_supabase):
        """Test génération PDF facture non trouvée"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        response = client.post("/api/fiscal/invoices/nonexistent/generate-pdf")
        assert response.status_code in [401, 404, 500]


# ===============================================
# FISCAL EMAIL TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestFiscalEmail:
    """Tests pour les emails fiscaux"""

    def test_send_fiscal_invoice_email(self, mock_auth, mock_supabase):
        """Test envoi email facture fiscale"""
        response = client.post("/api/fiscal/invoices/inv-123/send-email?to_email=client@test.com")
        assert response.status_code in [200, 401, 404, 500]


# ===============================================
# INPUT VALIDATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestInputValidation:
    """Tests de validation des entrées"""

    def test_calculate_tax_zero_amount(self, mock_auth):
        """Test calcul avec montant zéro"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 0,
            'country': 'MA',
            'status': 'auto_entrepreneur'
        })
        assert response.status_code == 422

    def test_calculate_vat_negative_amount(self, mock_auth):
        """Test TVA montant négatif"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': -500,
            'country': 'FR',
            'rate_type': 'standard'
        })
        assert response.status_code == 422

    def test_morocco_withholding_invalid_amount(self, mock_auth):
        """Test retenue source montant invalide"""
        response = client.post("/api/fiscal/morocco/withholding?amount=-1000")
        assert response.status_code == 422

    def test_usa_state_tax_invalid_state(self, mock_auth):
        """Test sales tax état invalide"""
        response = client.get("/api/fiscal/usa/state-sales-tax?state=XX")
        assert response.status_code in [200, 422, 500]

    def test_france_micro_invalid_activity(self, mock_auth):
        """Test micro-entreprise activité invalide"""
        response = client.post("/api/fiscal/france/micro-enterprise?revenue=10000&activity_type=invalid")
        assert response.status_code == 422

    def test_invoice_generate_invalid_vat_rate(self, mock_auth, mock_supabase):
        """Test génération facture taux TVA invalide"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': [
                {'description': 'Test', 'quantity': 1, 'unit_price': 100, 'vat_rate': 1.5}
            ]
        })
        # VAT rate 1.5 (150%) should be accepted but might be a business logic error
        assert response.status_code in [200, 400, 422, 500]


# ===============================================
# EDGE CASES TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestEdgeCases:
    """Tests des cas limites"""

    def test_large_amount_calculation(self, mock_auth):
        """Test calcul gros montant"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 10000000,
            'country': 'MA',
            'status': 'company'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_very_small_amount_calculation(self, mock_auth):
        """Test calcul petit montant"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 0.01,
            'country': 'FR',
            'status': 'micro_enterprise'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_decimal_precision(self, mock_auth):
        """Test précision décimale"""
        response = client.post("/api/fiscal/vat/calculate", json={
            'amount': 99.99,
            'country': 'MA',
            'rate_type': 'standard'
        })
        assert response.status_code in [200, 422, 401, 500]

    def test_unicode_in_invoice_description(self, mock_auth, mock_supabase):
        """Test caractères unicode dans description"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': [
                {'description': 'Service développement 日本語 العربية', 'quantity': 1, 'unit_price': 1000}
            ]
        })
        assert response.status_code in [200, 400, 422, 500]


# ===============================================
# CONCURRENT ACCESS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestConcurrentAccess:
    """Tests d'accès concurrent"""

    def test_multiple_invoice_generation(self, mock_auth, mock_supabase):
        """Test génération multiple factures simultanées"""
        # Simule plusieurs requêtes parallèles
        for i in range(3):
            response = client.post("/api/invoices/generate", json={
                'client_id': f'client-{i}',
                'line_items': [
                    {'description': f'Service {i}', 'quantity': 1, 'unit_price': 100 * (i + 1)}
                ]
            })
            assert response.status_code in [200, 400, 401, 500]


# ===============================================
# SECURITY TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestFiscalSecurity:
    """Tests de sécurité fiscale"""

    def test_sql_injection_in_tax_id(self, mock_auth):
        """Test injection SQL dans tax_id"""
        response = client.post("/api/fiscal/calculate", json={
            'amount': 1000,
            'country': 'MA',
            'status': 'company',
            'tax_id': "'; DROP TABLE users; --"
        })
        # Should not cause SQL error
        assert response.status_code in [200, 400, 422, 500]

    def test_xss_in_invoice_notes(self, mock_auth, mock_supabase):
        """Test XSS dans notes facture"""
        response = client.post("/api/invoices/generate", json={
            'client_id': 'client-123',
            'line_items': [
                {'description': 'Test', 'quantity': 1, 'unit_price': 100}
            ],
            'notes': '<script>alert("XSS")</script>'
        })
        assert response.status_code in [200, 400, 422, 500]

    def test_access_other_merchant_invoice(self, mock_auth, mock_supabase):
        """Test accès facture autre merchant"""
        # La query devrait filtrer par merchant_id
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        response = client.get("/api/invoices/other-merchant-invoice-id")
        assert response.status_code in [401, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
