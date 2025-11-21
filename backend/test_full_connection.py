import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("TEST DE CONNEXION COMPLÈTE FRONTEND → BACKEND → SUPABASE")
print("=" * 60)

# Test 1: Login
print("\n1. TEST LOGIN avec admin@getyourshare.com")
login_data = {
    "email": "admin@getyourshare.com",
    "password": "Admin123!"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Login réussi!")
        
        # Récupérer le token des cookies
        cookies = response.cookies
        print(f"   Cookies reçus: {list(cookies.keys())}")
        
        # Test 2: Récupérer les produits avec les cookies
        print("\n2. TEST GET /api/products (avec cookies)")
        products_response = requests.get(f"{BASE_URL}/api/products", cookies=cookies)
        print(f"   Status: {products_response.status_code}")
        
        if products_response.status_code == 200:
            products = products_response.json()
            print(f"   ✓ {len(products)} produits récupérés")
            if products:
                print(f"   Premier produit: {products[0].get('name', 'N/A')}")
        else:
            print(f"   ✗ Erreur: {products_response.text}")
        
        # Test 3: Récupérer les merchants
        print("\n3. TEST GET /api/merchants (avec cookies)")
        merchants_response = requests.get(f"{BASE_URL}/api/merchants", cookies=cookies)
        print(f"   Status: {merchants_response.status_code}")
        
        if merchants_response.status_code == 200:
            merchants = merchants_response.json()
            print(f"   ✓ {len(merchants)} marchands récupérés")
            if merchants:
                print(f"   Premier marchand: {merchants[0].get('business_name', 'N/A')}")
        else:
            print(f"   ✗ Erreur: {merchants_response.text}")
        
        # Test 4: Récupérer les influenceurs
        print("\n4. TEST GET /api/influencers (avec cookies)")
        influencers_response = requests.get(f"{BASE_URL}/api/influencers", cookies=cookies)
        print(f"   Status: {influencers_response.status_code}")
        
        if influencers_response.status_code == 200:
            influencers = influencers_response.json()
            print(f"   ✓ {len(influencers)} influenceurs récupérés")
            if influencers:
                print(f"   Premier influenceur: {influencers[0].get('username', 'N/A')}")
        else:
            print(f"   ✗ Erreur: {influencers_response.text}")
        
        # Test 5: Dashboard stats
        print("\n5. TEST GET /api/dashboard/stats (avec cookies)")
        stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", cookies=cookies)
        print(f"   Status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✓ Stats récupérées: {json.dumps(stats, indent=2)}")
        else:
            print(f"   ✗ Erreur: {stats_response.text}")
            
    else:
        print(f"   ✗ Login échoué: {response.text}")
        
except Exception as e:
    print(f"   ✗ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)
