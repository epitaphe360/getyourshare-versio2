"""
Test pour vérifier que la commission plateforme est correctement calculée
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Login en tant qu'admin
print("=" * 80)
print("1. LOGIN ADMIN")
print("=" * 80)
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "admin@test.com",
        "password": "Admin123!"
    }
)

if login_response.status_code == 200:
    print("✅ Login réussi")
    session_token = login_response.cookies.get('session_token')
    if session_token:
        print(f"Session token: {session_token[:20]}...")
    else:
        print("⚠️  Pas de session token dans les cookies, utilisation des données JSON")
        session_token = login_response.json().get('token')
else:
    print(f"❌ Erreur login: {login_response.status_code}")
    print(login_response.text)
    exit(1)

# 2. Récupérer les analytics
print("\n" + "=" * 80)
print("2. TEST /api/analytics/overview")
print("=" * 80)

analytics_response = requests.get(
    f"{BASE_URL}/api/analytics/overview",
    cookies={'session_token': session_token}
)

if analytics_response.status_code == 200:
    data = analytics_response.json()
    print("✅ Analytics récupérées avec succès\n")
    
    # Afficher les données financières
    financial = data.get('financial', {})
    print("💰 DONNÉES FINANCIÈRES:")
    print(f"  Total Revenue: {financial.get('total_revenue', 0)} MAD")
    print(f"  Platform Commission: {financial.get('platform_commission', 0)} MAD")
    print(f"  Pending Payouts: {financial.get('pending_payouts', 0)} MAD")
    print(f"  Revenue Growth: {financial.get('revenue_growth', 0)}%")
    
    # Vérifier si platform_commission est > 0
    platform_comm = financial.get('platform_commission', 0)
    if platform_comm > 0:
        print(f"\n✅ SUCCÈS: Commission plateforme = {platform_comm} MAD (> 0)")
    else:
        print(f"\n❌ ERREUR: Commission plateforme = {platform_comm} MAD (devrait être > 0)")
    
else:
    print(f"❌ Erreur analytics: {analytics_response.status_code}")
    print(analytics_response.text)

# 3. Tester l'endpoint spécifique platform-revenue
print("\n" + "=" * 80)
print("3. TEST /api/admin/platform-revenue")
print("=" * 80)

revenue_response = requests.get(
    f"{BASE_URL}/api/admin/platform-revenue",
    cookies={'session_token': session_token}
)

if revenue_response.status_code == 200:
    data = revenue_response.json()
    print("✅ Platform revenue récupéré avec succès\n")
    
    summary = data.get('summary', {})
    print("💰 RÉSUMÉ:")
    print(f"  Total Platform Revenue: {summary.get('total_platform_revenue', 0)} MAD")
    print(f"  Total Influencer Commission: {summary.get('total_influencer_commission', 0)} MAD")
    print(f"  Total Merchant Revenue: {summary.get('total_merchant_revenue', 0)} MAD")
    print(f"  Total Sales: {summary.get('total_sales', 0)}")
    print(f"  Average Commission/Sale: {summary.get('average_commission_per_sale', 0)} MAD")
    print(f"  Platform Commission Rate: {summary.get('platform_commission_rate', 0)}%")
    
    # Vérifier
    platform_rev = summary.get('total_platform_revenue', 0)
    if platform_rev > 0:
        print(f"\n✅ SUCCÈS: Total Platform Revenue = {platform_rev} MAD (> 0)")
    else:
        print(f"\n❌ ERREUR: Total Platform Revenue = {platform_rev} MAD (devrait être > 0)")
        
else:
    print(f"❌ Erreur platform revenue: {revenue_response.status_code}")
    print(revenue_response.text)

print("\n" + "=" * 80)
print("FIN DU TEST")
print("=" * 80)
