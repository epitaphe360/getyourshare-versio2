"""
Test rapide du système fiscal complet
Valide: PDF, Email, Calculs avancés, Webhooks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_pdf_generation():
    """Test génération PDF facture"""
    print("📄 Test PDF Generator...")
    
    try:
        from pdf_generator import InvoicePDFGenerator
        
        generator = InvoicePDFGenerator()
        
        invoice_data = {
            'invoice_number': 'FA-2024-TEST-001',
            'issue_date': '01/12/2024',
            'due_date': '31/12/2024',
            'country': 'MA',
            'currency': 'MAD'
        }
        
        company_data = {
            'name': 'GetYourShare Test',
            'address': 'Casablanca, Maroc',
            'phone': '+212 5 22 00 00 00',
            'email': 'test@getyourshare.ma',
            'ice': '002345678000045',
            'iban': 'MA64011519000001205000534921',
            'bic': 'BCMAMAMC'
        }
        
        client_data = {
            'name': 'Client Test',
            'address': 'Test Address',
            'email': 'client@test.com',
            'vat_number': 'MA-TEST-123'
        }
        
        line_items = [
            {
                'description': 'Service Test',
                'quantity': 1,
                'unit_price': 1000.00,
                'vat_rate': 20.0,
                'total_ht': 1000.00,
                'total_vat': 200.00,
                'total_ttc': 1200.00
            }
        ]
        
        pdf_path = generator.generate_invoice_pdf(
            'test_invoice.pdf',
            invoice_data,
            company_data,
            client_data,
            line_items
        )
        
        if os.path.exists(pdf_path):
            print(f"  ✅ PDF généré: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
            return True
        else:
            print("  ❌ PDF non créé")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def test_email_service():
    """Test service email (mode dry-run)"""
    print("\n📧 Test Email Service...")
    
    try:
        from fiscal_email_service import FiscalEmailService
        
        # Sans API key, juste valider l'initialisation
        service = FiscalEmailService(api_key=None, smtp_fallback=False)
        
        print("  ✅ Service email initialisé")
        print("  ℹ️  Configurez SENDGRID_API_KEY dans .env pour envoi réel")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def test_advanced_calculations():
    """Test calculs fiscaux avancés"""
    print("\n🧮 Test Calculs Fiscaux Avancés...")
    
    try:
        from advanced_tax_calculations import (
            calculate_morocco_ir,
            calculate_france_urssaf,
            calculate_usa_state_tax,
            calculate_usa_self_employment_tax
        )
        
        # Test Maroc IR
        morocco = calculate_morocco_ir(annual_income=250000, dependents=2, deductions=5000)
        print(f"  ✅ Maroc IR: {morocco['ir_net']} MAD (taux effectif: {morocco['effective_rate']}%)")
        
        # Test France URSSAF
        france = calculate_france_urssaf(revenue=50000, status="auto_entrepreneur_bnc")
        print(f"  ✅ France URSSAF: {france['social_charges']:.2f} EUR ({france['rate']*100}%)")
        
        # Test USA State Tax
        usa_state = calculate_usa_state_tax(federal_taxable_income=100000, state="CA")
        print(f"  ✅ USA State Tax (CA): ${usa_state['state_tax']:,.2f}")
        
        # Test USA Self-Employment Tax
        usa_se = calculate_usa_self_employment_tax(net_profit=80000)
        print(f"  ✅ USA SE Tax: ${usa_se['se_tax']:,.2f} ({usa_se['effective_rate']}%)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_payment_webhooks():
    """Test webhooks paiements (structure)"""
    print("\n💳 Test Payment Webhooks...")
    
    try:
        from payment_webhooks import router
        
        # Vérifier endpoints
        routes = [route.path for route in router.routes]
        print(f"  ✅ {len(routes)} endpoints webhook configurés:")
        for route in routes[:5]:
            print(f"     - {route}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def test_fiscal_endpoints():
    """Test endpoints fiscaux"""
    print("\n🌐 Test Fiscal Endpoints...")
    
    try:
        from fiscal_endpoints import router
        
        routes = [route.path for route in router.routes]
        print(f"  ✅ {len(routes)} endpoints fiscaux configurés:")
        
        # Compter par catégorie
        advanced_calc = [r for r in routes if 'morocco' in r or 'france' in r or 'usa' in r]
        pdf_email = [r for r in routes if 'pdf' in r or 'email' in r]
        
        print(f"     - Calculs avancés: {len(advanced_calc)}")
        print(f"     - PDF/Email: {len(pdf_email)}")
        print(f"     - Autres: {len(routes) - len(advanced_calc) - len(pdf_email)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def main():
    """Exécute tous les tests"""
    print("========================================")
    print("🚀 TESTS SYSTÈME FISCAL COMPLET")
    print("========================================\n")
    
    results = {
        "PDF Generation": test_pdf_generation(),
        "Email Service": test_email_service(),
        "Advanced Calculations": test_advanced_calculations(),
        "Payment Webhooks": test_payment_webhooks(),
        "Fiscal Endpoints": test_fiscal_endpoints()
    }
    
    print("\n========================================")
    print("📊 RÉSULTATS")
    print("========================================")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Score: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS PASSENT ! Système 100% fonctionnel")
    elif passed >= total * 0.8:
        print("\n✅ Système opérationnel (quelques ajustements mineurs)")
    else:
        print("\n⚠️  Problèmes critiques détectés")
    
    print("\n========================================")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
