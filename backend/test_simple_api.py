"""
Test simple de l'API sans UI
"""
import requests

print("=" * 80)
print("TEST SIMPLE API ANALYTICS")
print("=" * 80)

# Test 1: Login
print("\n1️⃣ Login...")
try:
    login_resp = requests.post(
        "http://localhost:5000/api/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
        timeout=5
    )
    print(f"Status: {login_resp.status_code}")
    if login_resp.status_code == 200:
        print("✅ Login OK")
        cookies = login_resp.cookies
    else:
        print(f"❌ Erreur: {login_resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Exception: {e}")
    exit(1)

# Test 2: Analytics
print("\n2️⃣ Récupération analytics...")
try:
    analytics_resp = requests.get(
        "http://localhost:5000/api/analytics/overview",
        cookies=cookies,
        timeout=10
    )
    print(f"Status: {analytics_resp.status_code}")
    
    if analytics_resp.status_code == 200:
        data = analytics_resp.json()
        
        # Vérifier les métriques clés
        active_users = data.get("users", {}).get("active_users_24h", 0)
        platform_commission = data.get("financial", {}).get("platform_commission", 0)
        
        print("\n" + "=" * 80)
        print("RÉSULTATS:")
        print("=" * 80)
        print(f"Utilisateurs actifs 24h: {active_users} {'✅' if active_users > 0 else '❌ PROBLÈME'}")
        print(f"Commission plateforme: {platform_commission:.2f} MAD {'✅' if platform_commission > 0 else '❌ PROBLÈME'}")
        print("=" * 80)
    else:
        print(f"❌ Erreur: {analytics_resp.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
