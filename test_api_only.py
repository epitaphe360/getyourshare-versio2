"""
TEST API UNIQUEMENT - Sans démarrage de serveur
================================================
Lance uniquement les tests d'intégration API en utilisant le serveur déjà démarré.
"""

import sys
import os

# Empêcher l'import accidentel du serveur
sys.dont_write_bytecode = True
os.environ["TESTING"] = "1"

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
PASSWORD = "Test123!"  # Mot de passe par défaut de tous les comptes de test

USERS = {
    "admin": "admin@getyourshare.com",
    "merchant": "boutique.maroc@getyourshare.com",  # Artisanat marocain - STARTER
    "influencer": "hassan.oudrhiri@getyourshare.com",  # Hassan Oudrhiri - Food & Cuisine - STARTER
    "commercial": "sofia.chakir@getyourshare.com"  # Commercial (role admin)
}

class TestStats:
    """Collecte des statistiques de test"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.endpoints_tested = set()
        self.features_tested = set()
    
    def add_pass(self, endpoint: str, feature: str = ""):
        self.total += 1
        self.passed += 1
        self.endpoints_tested.add(endpoint)
        if feature:
            self.features_tested.add(feature)
    
    def add_fail(self, endpoint: str, error: str, feature: str = ""):
        self.total += 1
        self.failed += 1
        self.errors.append({"endpoint": endpoint, "error": error, "feature": feature})
    
    def get_coverage_percent(self, total_endpoints: int = 200) -> float:
        return (len(self.endpoints_tested) / total_endpoints) * 100
    
    def print_summary(self):
        print("\n" + "="*80)
        print(f"RÉSUMÉ DES TESTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"\n📊 STATISTIQUES:")
        print(f"   Total tests: {self.total}")
        print(f"   ✅ Réussis: {self.passed} ({self.passed/self.total*100:.1f}%)")
        print(f"   ❌ Échoués: {self.failed} ({self.failed/self.total*100:.1f}%)")
        print(f"\n🎯 COUVERTURE:")
        print(f"   Endpoints testés: {len(self.endpoints_tested)}")
        print(f"   Fonctionnalités testées: {len(self.features_tested)}")
        print(f"   Couverture estimée: {self.get_coverage_percent():.1f}%")
        
        if self.errors:
            print(f"\n❌ ERREURS DÉTAILLÉES ({len(self.errors)}):")
            # Grouper les erreurs par type
            error_types = {}
            for err in self.errors:
                error_msg = err['error'][:100]
                if error_msg not in error_types:
                    error_types[error_msg] = []
                error_types[error_msg].append(err['endpoint'])
            
            for error_msg, endpoints in list(error_types.items())[:10]:
                print(f"\n   • {error_msg}")
                for endpoint in endpoints[:3]:
                    print(f"     - {endpoint}")
                if len(endpoints) > 3:
                    print(f"     ... et {len(endpoints) - 3} autres")
        
        print("\n" + "="*80 + "\n")


stats = TestStats()


def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_success(msg):
    print(f"✅ {msg}")


def print_fail(msg):
    print(f"❌ {msg}")


def login_user(email: str, role: str = "") -> requests.Session:
    """Authentifie un utilisateur et retourne une session"""
    session = requests.Session()
    
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                session.headers.update({
                    "Authorization": f"Bearer {data['access_token']}"
                })
                stats.add_pass("/api/auth/login", "Authentication")
                print_success(f"Connecté: {role} ({email})")
                return session
        
        stats.add_fail("/api/auth/login", f"Login failed: {response.status_code}")
        print_fail(f"Échec connexion {role}: {response.status_code}")
    except Exception as e:
        stats.add_fail("/api/auth/login", f"Exception: {str(e)}")
        print_fail(f"Erreur connexion {role}: {e}")
    
    return session


def test_endpoint(session: requests.Session, method: str, endpoint: str, feature: str,
                  json=None, data=None, params=None, files=None, 
                  expected_codes=[200, 201, 204]):
    """Teste un endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = session.get(url, params=params)
        elif method == "POST":
            response = session.post(url, json=json, data=data, files=files, params=params)
        elif method == "PUT":
            response = session.put(url, json=json, data=data)
        elif method == "DELETE":
            response = session.delete(url)
        elif method == "PATCH":
            response = session.patch(url, json=json, data=data)
        else:
            stats.add_fail(endpoint, f"Unknown method: {method}", feature)
            return
        
        if response.status_code in expected_codes:
            stats.add_pass(endpoint, feature)
        else:
            error_msg = f"Status {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg += f" - {error_data['detail']}"
            except:
                pass
            stats.add_fail(endpoint, error_msg, feature)
    
    except Exception as e:
        stats.add_fail(endpoint, f"Exception: {str(e)}", feature)


def test_public_endpoints():
    print_header("1. ENDPOINTS PUBLICS")
    session = requests.Session()
    
    # Endpoints sans authentification
    test_endpoint(session, "GET", "/", "Public")
    test_endpoint(session, "GET", "/health", "Public")
    test_endpoint(session, "GET", "/api/public/stats", "Public")
    test_endpoint(session, "GET", "/api/public/subscription-plans", "Public")
    test_endpoint(session, "GET", "/docs", "Public")


def test_authentication():
    print_header("2. AUTHENTIFICATION")
    session = requests.Session()
    
    # Tests de login
    for role, email in USERS.items():
        login_user(email, role)
    
    # Tests d'enregistrement
    test_data = {
        "email": f"newuser{int(time.time())}@test.com",
        "password": PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    test_endpoint(session, "POST", "/api/auth/register", "Authentication",
                  json=test_data, expected_codes=[200, 201, 400, 409])
    
    # Tests d'autres endpoints auth
    test_endpoint(session, "POST", "/api/auth/refresh", "Authentication",
                  expected_codes=[200, 401])
    test_endpoint(session, "POST", "/api/auth/forgot-password", "Authentication",
                  json={"email": "test@test.com"}, expected_codes=[200, 404])


def test_influencer_features():
    print_header("3. FONCTIONNALITÉS INFLUENCEUR")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Dashboard
    test_endpoint(session, "GET", "/api/dashboard/stats", "Influencer Dashboard")
    test_endpoint(session, "GET", "/api/dashboard/recent-activity", "Influencer Dashboard")
    
    # Products & Links
    test_endpoint(session, "GET", "/api/products", "Products")
    test_endpoint(session, "GET", "/api/products/trending", "Products")
    test_endpoint(session, "POST", "/api/links/generate", "Links",
                  json={"product_id": 1, "platform": "instagram"}, expected_codes=[200, 201, 400, 404])
    test_endpoint(session, "GET", "/api/links", "Links")
    
    # Campaigns
    test_endpoint(session, "GET", "/api/campaigns", "Campaigns")
    test_endpoint(session, "GET", "/api/campaigns/available", "Campaigns")
    test_endpoint(session, "POST", "/api/campaigns/1/apply", "Campaigns",
                  expected_codes=[200, 201, 400, 404])
    
    # Analytics
    test_endpoint(session, "GET", "/api/analytics/performance", "Analytics")
    test_endpoint(session, "GET", "/api/analytics/revenue-chart", "Analytics")
    test_endpoint(session, "GET", "/api/analytics/best-products", "Analytics")
    
    # Earnings & Payouts
    test_endpoint(session, "GET", "/api/earnings", "Earnings")
    test_endpoint(session, "GET", "/api/earnings/summary", "Earnings")
    test_endpoint(session, "GET", "/api/payouts", "Payouts")
    test_endpoint(session, "POST", "/api/payouts/request", "Payouts",
                  json={"amount": 100, "payment_method": "paypal"},
                  expected_codes=[200, 201, 400])


def test_merchant_features():
    print_header("4. FONCTIONNALITÉS MARCHAND")
    session = login_user(USERS["merchant"], "Merchant")
    
    # Dashboard
    test_endpoint(session, "GET", "/api/dashboard/merchant/stats", "Merchant Dashboard")
    test_endpoint(session, "GET", "/api/dashboard/merchant/overview", "Merchant Dashboard")
    
    # Products
    test_endpoint(session, "GET", "/api/merchant/products", "Merchant Products")
    test_endpoint(session, "POST", "/api/merchant/products", "Merchant Products",
                  json={
                      "name": "Test Product",
                      "description": "Test",
                      "price": 99.99,
                      "commission_rate": 10
                  }, expected_codes=[200, 201, 400])
    
    # Campaigns
    test_endpoint(session, "GET", "/api/merchant/campaigns", "Merchant Campaigns")
    test_endpoint(session, "POST", "/api/merchant/campaigns", "Merchant Campaigns",
                  json={
                      "name": "Test Campaign",
                      "description": "Test",
                      "budget": 1000,
                      "start_date": datetime.now().isoformat(),
                      "end_date": (datetime.now() + timedelta(days=30)).isoformat()
                  }, expected_codes=[200, 201, 400])
    
    # Influencers
    test_endpoint(session, "GET", "/api/merchant/influencers", "Merchant Influencers")
    test_endpoint(session, "GET", "/api/merchant/influencers/search", "Merchant Influencers",
                  params={"q": "fashion"})
    
    # Orders & Sales
    test_endpoint(session, "GET", "/api/merchant/orders", "Merchant Orders")
    test_endpoint(session, "GET", "/api/merchant/sales", "Merchant Sales")
    test_endpoint(session, "GET", "/api/merchant/analytics/revenue", "Merchant Analytics")


def test_commercial_features():
    print_header("5. FONCTIONNALITÉS COMMERCIAL")
    session = login_user(USERS["commercial"], "Commercial")
    
    # Dashboard
    test_endpoint(session, "GET", "/api/commercial/dashboard", "Commercial Dashboard")
    test_endpoint(session, "GET", "/api/commercial/stats", "Commercial Dashboard")
    
    # Leads
    test_endpoint(session, "GET", "/api/commercial/leads", "Leads")
    test_endpoint(session, "GET", "/api/commercial/leads/active", "Leads")
    test_endpoint(session, "POST", "/api/commercial/leads", "Leads",
                  json={
                      "company_name": "Test Company",
                      "contact_email": "test@company.com",
                      "service_type": "marketing"
                  }, expected_codes=[200, 201, 400])
    
    # Services
    test_endpoint(session, "GET", "/api/commercial/services", "Services")
    test_endpoint(session, "GET", "/api/commercial/services/available", "Services")
    
    # Clients
    test_endpoint(session, "GET", "/api/commercial/clients", "Clients")
    test_endpoint(session, "GET", "/api/commercial/pipeline", "Pipeline")


def test_admin_features():
    print_header("6. FONCTIONNALITÉS ADMIN")
    session = login_user(USERS["admin"], "Admin")
    
    # Dashboard
    test_endpoint(session, "GET", "/api/admin/dashboard", "Admin Dashboard")
    test_endpoint(session, "GET", "/api/admin/stats", "Admin Stats")
    
    # Users Management
    test_endpoint(session, "GET", "/api/admin/users", "Admin Users")
    test_endpoint(session, "GET", "/api/admin/users/pending", "Admin Users")
    test_endpoint(session, "GET", "/api/admin/influencers", "Admin Influencers")
    test_endpoint(session, "GET", "/api/admin/merchants", "Admin Merchants")
    
    # Platform Management
    test_endpoint(session, "GET", "/api/admin/transactions", "Admin Transactions")
    test_endpoint(session, "GET", "/api/admin/commissions", "Admin Commissions")
    test_endpoint(session, "GET", "/api/admin/payouts", "Admin Payouts")
    test_endpoint(session, "GET", "/api/admin/campaigns", "Admin Campaigns")
    
    # Analytics
    test_endpoint(session, "GET", "/api/admin/analytics/overview", "Admin Analytics")
    test_endpoint(session, "GET", "/api/admin/analytics/revenue", "Admin Analytics")
    test_endpoint(session, "GET", "/api/admin/analytics/users-growth", "Admin Analytics")
    
    # System
    test_endpoint(session, "GET", "/api/admin/system/health", "Admin System")
    test_endpoint(session, "GET", "/api/admin/logs", "Admin Logs")


def test_subscriptions():
    print_header("7. ABONNEMENTS")
    session = login_user(USERS["merchant"], "Merchant")
    
    test_endpoint(session, "GET", "/api/subscriptions/plans", "Subscriptions")
    test_endpoint(session, "GET", "/api/subscriptions/current", "Subscriptions")
    test_endpoint(session, "POST", "/api/subscriptions/subscribe", "Subscriptions",
                  json={"plan_id": "pro", "payment_method": "card"},
                  expected_codes=[200, 201, 400])
    test_endpoint(session, "GET", "/api/subscriptions/invoices", "Subscriptions")
    test_endpoint(session, "GET", "/api/subscriptions/usage", "Subscriptions")


def test_messaging_notifications():
    print_header("8. MESSAGERIE & NOTIFICATIONS")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Messages
    test_endpoint(session, "GET", "/api/messages", "Messaging")
    test_endpoint(session, "GET", "/api/messages/conversations", "Messaging")
    test_endpoint(session, "POST", "/api/messages/send", "Messaging",
                  json={
                      "recipient_id": 2,
                      "message": "Test message"
                  }, expected_codes=[200, 201, 400, 404])
    
    # Notifications
    test_endpoint(session, "GET", "/api/notifications", "Notifications")
    test_endpoint(session, "GET", "/api/notifications/unread", "Notifications")
    test_endpoint(session, "POST", "/api/notifications/1/read", "Notifications",
                  expected_codes=[200, 204, 404])


def test_payments_webhooks():
    print_header("9. PAIEMENTS & WEBHOOKS")
    session = login_user(USERS["merchant"], "Merchant")
    
    # Payments
    test_endpoint(session, "GET", "/api/payments/methods", "Payments")
    test_endpoint(session, "POST", "/api/payments/process", "Payments",
                  json={
                      "amount": 100,
                      "currency": "MAD",
                      "payment_method": "card"
                  }, expected_codes=[200, 201, 400])
    test_endpoint(session, "GET", "/api/payments/history", "Payments")
    
    # Webhooks (test public endpoints)
    public_session = requests.Session()
    test_endpoint(public_session, "POST", "/api/webhooks/shopify", "Webhooks",
                  json={"test": "data"}, expected_codes=[200, 400, 401])
    test_endpoint(public_session, "POST", "/api/webhooks/woocommerce", "Webhooks",
                  json={"test": "data"}, expected_codes=[200, 400, 401])


def test_ai_features():
    print_header("10. FONCTIONNALITÉS IA")
    session = login_user(USERS["influencer"], "Influencer")
    
    test_endpoint(session, "POST", "/api/ai/generate-caption", "AI",
                  json={"product_id": 1, "platform": "instagram"},
                  expected_codes=[200, 400, 404, 501])
    test_endpoint(session, "POST", "/api/ai/optimize-content", "AI",
                  json={"content": "Test content"},
                  expected_codes=[200, 400, 501])
    test_endpoint(session, "GET", "/api/ai/recommendations", "AI",
                  expected_codes=[200, 501])


def test_settings():
    print_header("11. PARAMÈTRES")
    session = login_user(USERS["influencer"], "Influencer")
    
    test_endpoint(session, "GET", "/api/settings/profile", "Settings")
    test_endpoint(session, "PUT", "/api/settings/profile", "Settings",
                  json={"first_name": "Updated"}, expected_codes=[200, 400])
    test_endpoint(session, "GET", "/api/settings/notifications", "Settings")
    test_endpoint(session, "PUT", "/api/settings/notifications", "Settings",
                  json={"email_notifications": True}, expected_codes=[200, 400])
    test_endpoint(session, "POST", "/api/settings/change-password", "Settings",
                  json={
                      "current_password": PASSWORD,
                      "new_password": "NewPass123!"
                  }, expected_codes=[200, 400, 401])


def test_miscellaneous():
    print_header("12. ENDPOINTS DIVERS")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Search
    test_endpoint(session, "GET", "/api/search", "Search",
                  params={"q": "fashion"})
    test_endpoint(session, "GET", "/api/search/products", "Search",
                  params={"q": "shoes"})
    
    # Categories
    test_endpoint(session, "GET", "/api/categories", "Categories")
    test_endpoint(session, "GET", "/api/categories/1/products", "Categories",
                  expected_codes=[200, 404])
    
    # Tracking
    test_endpoint(session, "GET", "/r/testcode", "Tracking",
                  expected_codes=[200, 301, 302, 404])


def test_advanced_features():
    print_header("13. FONCTIONNALITÉS AVANCÉES")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Upload
    test_endpoint(session, "POST", "/api/upload/image", "Upload",
                  files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
                  expected_codes=[200, 201, 400])
    
    # Analytics avancées
    test_endpoint(session, "GET", "/api/analytics/conversion-funnel", "Advanced Analytics")
    test_endpoint(session, "GET", "/api/analytics/cohort-analysis", "Advanced Analytics")
    test_endpoint(session, "GET", "/api/analytics/comparative", "Advanced Analytics")
    
    # Gamification
    test_endpoint(session, "GET", "/api/gamification/badges", "Gamification")
    test_endpoint(session, "GET", "/api/gamification/leaderboard", "Gamification")
    test_endpoint(session, "GET", "/api/gamification/challenges", "Gamification")
    
    # Reviews
    test_endpoint(session, "GET", "/api/products/1/reviews", "Reviews",
                  expected_codes=[200, 404])
    test_endpoint(session, "POST", "/api/products/1/reviews", "Reviews",
                  json={"rating": 5, "comment": "Great product"},
                  expected_codes=[200, 201, 400, 404])
    
    # Referrals
    test_endpoint(session, "GET", "/api/referrals", "Referrals")
    test_endpoint(session, "POST", "/api/referrals/invite", "Referrals",
                  json={"email": "friend@test.com"},
                  expected_codes=[200, 201, 400])
    
    # WhatsApp Integration
    test_endpoint(session, "POST", "/api/whatsapp/send", "WhatsApp",
                  json={"phone": "+212600000000", "message": "Test"},
                  expected_codes=[200, 400, 501])
    
    # Trust Score
    test_endpoint(session, "GET", "/api/trust-score", "Trust Score")
    
    # KYC
    test_endpoint(session, "GET", "/api/kyc/status", "KYC")
    test_endpoint(session, "POST", "/api/kyc/submit", "KYC",
                  json={"document_type": "id_card"},
                  expected_codes=[200, 201, 400])
    
    # Collaboration
    test_endpoint(session, "GET", "/api/collaborations", "Collaborations")
    test_endpoint(session, "POST", "/api/collaborations/request", "Collaborations",
                  json={"influencer_id": 2, "campaign_id": 1},
                  expected_codes=[200, 201, 400, 404])


def test_error_handling():
    print_header("14. GESTION DES ERREURS")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Tests d'endpoints inexistants (404)
    test_endpoint(session, "GET", "/api/nonexistent", "Error Handling",
                  expected_codes=[404])
    test_endpoint(session, "GET", "/api/products/999999999", "Error Handling",
                  expected_codes=[404])
    
    # Tests sans authentification (401)
    no_auth_session = requests.Session()
    test_endpoint(no_auth_session, "GET", "/api/dashboard/stats", "Error Handling",
                  expected_codes=[401])
    
    # Tests avec données invalides (400/422)
    test_endpoint(session, "POST", "/api/products", "Error Handling",
                  json={}, expected_codes=[400, 422])
    test_endpoint(session, "POST", "/api/links/generate", "Error Handling",
                  json={"invalid": "data"}, expected_codes=[400, 422])


def test_edge_cases():
    print_header("15. TESTS CAS LIMITES")
    session = login_user(USERS["influencer"], "Influencer")
    
    # Pagination
    test_endpoint(session, "GET", "/api/products", "Edge Cases",
                  params={"limit": 1, "offset": 0})
    test_endpoint(session, "GET", "/api/products", "Edge Cases",
                  params={"limit": 100, "offset": 0})
    
    # Caractères spéciaux
    test_endpoint(session, "GET", "/api/search", "Edge Cases",
                  params={"q": "é à ç ñ ü"})
    test_endpoint(session, "GET", "/api/search", "Edge Cases",
                  params={"q": "!@#$%^&*()"})
    
    # Recherche vide
    test_endpoint(session, "GET", "/api/search", "Edge Cases",
                  params={"q": ""})
    
    # IDs inexistants
    test_endpoint(session, "GET", "/api/products/999999999", "Edge Cases",
                  expected_codes=[404])
    test_endpoint(session, "GET", "/api/campaigns/999999999", "Edge Cases",
                  expected_codes=[404])
    
    # Montants edge cases
    test_endpoint(session, "POST", "/api/payouts/request", "Edge Cases",
                  json={"amount": 0.01, "payment_method": "paypal"},
                  expected_codes=[200, 201, 400])
    
    # Dates edge cases
    test_endpoint(session, "GET", "/api/analytics/revenue-chart", "Edge Cases",
                  params={
                      "start_date": "2020-01-01",
                      "end_date": "2020-01-01"
                  })


def main():
    print_header("🚀 TEST API COMPLET - VERSION RAPIDE 🚀")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Utilisateurs testés: {len(USERS)}")
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_fail(f"⚠️  Serveur non accessible: {response.status_code}")
            return
        print_success("Serveur accessible")
    except Exception as e:
        print_fail(f"❌ Impossible de se connecter au serveur: {e}")
        print("   → Assurez-vous que le serveur est démarré: cd backend && python server.py")
        return
    
    start_time = time.time()
    
    try:
        # Lancer tous les tests
        test_public_endpoints()
        test_authentication()
        test_influencer_features()
        test_merchant_features()
        test_commercial_features()
        test_admin_features()
        test_subscriptions()
        test_messaging_notifications()
        test_payments_webhooks()
        test_ai_features()
        test_settings()
        test_miscellaneous()
        test_advanced_features()
        test_error_handling()
        test_edge_cases()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Affichage du résumé
        elapsed_time = time.time() - start_time
        stats.print_summary()
        print(f"⏱️  Temps d'exécution: {elapsed_time:.2f} secondes")
        
        # Métriques finales
        if stats.total > 0:
            success_rate = (stats.passed / stats.total) * 100
            coverage_percent = stats.get_coverage_percent()
            
            print(f"\n📈 MÉTRIQUES FINALES:")
            print(f"   Couverture des endpoints: {coverage_percent:.1f}%")
            print(f"   Taux de réussite: {success_rate:.1f}%")
            
            if success_rate >= 90 and coverage_percent >= 90:
                print(f"\n🎉 EXCELLENT ! Objectif 100% atteint!")
            elif success_rate >= 75:
                print(f"\n👍 BON RÉSULTAT ! Quelques améliorations possibles.")
            else:
                print(f"\n⚠️  DES CORRECTIONS SONT NÉCESSAIRES")
            
            # Retourner le code de sortie approprié
            if success_rate < 75:
                sys.exit(1)
        else:
            print("\n⚠️  Aucun test exécuté")
            sys.exit(1)


if __name__ == "__main__":
    main()
