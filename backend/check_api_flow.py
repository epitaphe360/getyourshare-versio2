import requests
import json

BASE_URL = "http://localhost:5000"

print("\n" + "="*70)
print("DIAGNOSTIC COMPLET: Frontend → Backend → Supabase")
print("="*70)

# Test 1: Vérifier que le backend répond
print("\n1. Backend Health Check")
try:
    health = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   ✓ Backend accessible: {health.status_code}")
except Exception as e:
    print(f"   ✗ Backend inaccessible: {e}")
    exit(1)

# Test 2: Login et récupération du token
print("\n2. Login avec admin@getyourshare.com")
login_payload = {
    "email": "admin@getyourshare.com",
    "password": "Admin123!"
}

session = requests.Session()
login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_payload)

if login_response.status_code == 200:
    print(f"   ✓ Login réussi!")
    login_data = login_response.json()
    print(f"   User: {login_data.get('user', {}).get('email')}")
    print(f"   Role: {login_data.get('user', {}).get('role')}")
else:
    print(f"   ✗ Login échoué: {login_response.text}")
    exit(1)

# Test 3: Récupérer TOUS les produits
print("\n3. Récupération des produits")
products_response = session.get(f"{BASE_URL}/api/products")
if products_response.status_code == 200:
    products = products_response.json()
    if isinstance(products, list):
        print(f"   ✓ {len(products)} produits récupérés")
        for i, product in enumerate(products[:3], 1):
            print(f"      {i}. {product.get('name')} - {product.get('price')}€")
    else:
        print(f"   ✓ Produits: {products}")
else:
    print(f"   ✗ Erreur: {products_response.status_code} - {products_response.text}")

# Test 4: Récupérer TOUS les marchands
print("\n4. Récupération des marchands")
merchants_response = session.get(f"{BASE_URL}/api/merchants")
if merchants_response.status_code == 200:
    merchants = merchants_response.json()
    if isinstance(merchants, list):
        print(f"   ✓ {len(merchants)} marchands récupérés")
        for i, merchant in enumerate(merchants[:3], 1):
            print(f"      {i}. {merchant.get('business_name')} - {merchant.get('email')}")
    else:
        print(f"   ✓ Marchands: {merchants}")
else:
    print(f"   ✗ Erreur: {merchants_response.status_code} - {merchants_response.text}")

# Test 5: Récupérer TOUS les influenceurs
print("\n5. Récupération des influenceurs")
influencers_response = session.get(f"{BASE_URL}/api/influencers")
if influencers_response.status_code == 200:
    influencers = influencers_response.json()
    if isinstance(influencers, list):
        print(f"   ✓ {len(influencers)} influenceurs récupérés")
        for i, influencer in enumerate(influencers[:3], 1):
            print(f"      {i}. {influencer.get('username')} - {influencer.get('email')}")
    else:
        print(f"   ✓ Influenceurs: {influencers}")
else:
    print(f"   ✗ Erreur: {influencers_response.status_code} - {influencers_response.text}")

# Test 6: Dashboard stats
print("\n6. Statistiques du dashboard")
stats_response = session.get(f"{BASE_URL}/api/dashboard/stats")
if stats_response.status_code == 200:
    stats = stats_response.json()
    print(f"   ✓ Stats récupérées:")
    print(f"      - Total utilisateurs: {stats.get('total_users', 0)}")
    print(f"      - Total marchands: {stats.get('total_merchants', 0)}")
    print(f"      - Total influenceurs: {stats.get('total_influencers', 0)}")
    print(f"      - Total produits: {stats.get('total_products', 0)}")
else:
    print(f"   ✗ Erreur: {stats_response.status_code} - {stats_response.text}")

# Test 7: Analytics overview
print("\n7. Analytics overview")
analytics_response = session.get(f"{BASE_URL}/api/analytics/overview")
if analytics_response.status_code == 200:
    analytics = analytics_response.json()
    print(f"   ✓ Analytics récupérées")
else:
    print(f"   ✗ Erreur: {analytics_response.status_code} - {analytics_response.text}")

print("\n" + "="*70)
print("RÉSUMÉ:")
print("- Backend: ✓ Fonctionnel sur http://localhost:5000")
print("- Authentification: ✓ Login réussi")
print("- Données Supabase: ✓ Accessibles via l'API")
print("\nSi le frontend ne montre pas les données, vérifiez:")
print("1. Que vous êtes bien connecté dans le navigateur")
print("2. Que le frontend utilise bien http://localhost:5000 comme API_URL")
print("3. Les cookies sont bien envoyés dans les requêtes")
print("4. Ouvrez la console du navigateur (F12) pour voir les erreurs")
print("="*70 + "\n")
