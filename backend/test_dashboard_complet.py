import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TEST COMPLET DE CONNEXION AU TABLEAU DE BORD")
print("=" * 70)

# Simulation de la requête frontend avec cookies
session = requests.Session()  # Utilise la même session pour garder les cookies

# Test 1: Login avec Origin header (simulation frontend)
print("\n1. Login depuis le frontend (http://localhost:3000)")
print("-" * 70)

headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:3000"
}

login_data = {
    "email": "admin@getyourshare.com",
    "password": "Admin123!"
}

try:
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Login réussi!")
        print(f"   User: {data.get('user', {}).get('email')}")
        print(f"   Role: {data.get('user', {}).get('role')}")
        
        # Vérifier les cookies
        cookies = session.cookies
        print(f"\n   Cookies reçus:")
        for cookie in cookies:
            print(f"   - {cookie.name}: {cookie.value[:30]}...")
        
        # Test 2: Vérifier /api/auth/me avec les cookies
        print(f"\n2. Vérification de la session (/api/auth/me)")
        print("-" * 70)
        
        me_response = session.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Origin": "http://localhost:3000"}
        )
        
        print(f"   Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"   ✓ Session valide!")
            print(f"   User: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   ID: {user_data.get('id')}")
        else:
            print(f"   ✗ Erreur: {me_response.text}")
        
        # Test 3: Dashboard stats
        print(f"\n3. Accès aux statistiques du tableau de bord")
        print("-" * 70)
        
        stats_response = session.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers={"Origin": "http://localhost:3000"}
        )
        
        print(f"   Status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✓ Dashboard accessible!")
            print(f"\n   Statistiques:")
            print(f"   - Utilisateurs: {stats.get('total_users', 0)}")
            print(f"   - Marchands: {stats.get('total_merchants', 0)}")
            print(f"   - Influenceurs: {stats.get('total_influencers', 0)}")
            print(f"   - Produits: {stats.get('total_products', 0)}")
            print(f"   - Services: {stats.get('total_services', 0)}")
            print(f"   - Revenu total: {stats.get('total_revenue', 0):.2f} €")
        else:
            print(f"   ✗ Erreur: {stats_response.text}")
        
        # Test 4: Produits
        print(f"\n4. Récupération des produits")
        print("-" * 70)
        
        products_response = session.get(
            f"{BASE_URL}/api/products",
            headers={"Origin": "http://localhost:3000"}
        )
        
        print(f"   Status: {products_response.status_code}")
        
        if products_response.status_code == 200:
            products = products_response.json()
            print(f"   ✓ Produits récupérés: {len(products)} produits")
            if len(products) > 0:
                print(f"   Premier produit: {products[0].get('name', 'N/A')}")
        else:
            print(f"   ✗ Erreur: {products_response.text}")
            
    else:
        print(f"   ✗ Login échoué!")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ✗ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("RÉSUMÉ: Tous les tests doivent afficher ✓ pour une connexion réussie")
print("=" * 70)
