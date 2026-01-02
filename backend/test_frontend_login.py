import requests
import json

# Configuration
BACKEND_URL = "http://localhost:5000"
FRONTEND_ORIGIN = "http://localhost:3000"

print("\n" + "="*70)
print("TEST DE CONNEXION AVEC SIMULATION FRONTEND")
print("="*70)

# Test 1: Vérifier que le backend accepte les requêtes du frontend
print("\n1. Test CORS - Requête OPTIONS (Preflight)")
try:
    headers = {
        "Origin": FRONTEND_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    response = requests.options(f"{BACKEND_URL}/api/auth/login", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NON DÉFINI')}")
    print(f"   Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'NON DÉFINI')}")
    
    if response.headers.get('Access-Control-Allow-Origin') == FRONTEND_ORIGIN:
        print("   ✓ CORS configuré correctement")
    else:
        print("   ✗ PROBLÈME CORS DÉTECTÉ!")
except Exception as e:
    print(f"   ✗ Erreur: {e}")

# Test 2: Login avec simulation de requête frontend
print("\n2. Test Login POST avec Origin")
try:
    headers = {
        "Origin": FRONTEND_ORIGIN,
        "Content-Type": "application/json"
    }
    data = {
        "email": "admin@getyourshare.com",
        "password": "Admin123!"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json=data,
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NON DÉFINI')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Login réussi!")
        print(f"   User: {result.get('user', {}).get('email')}")
        print(f"   Role: {result.get('user', {}).get('role')}")
        
        # Vérifier les cookies
        cookies = response.cookies
        if 'access_token' in cookies:
            print(f"   ✓ Cookie access_token présent: {cookies['access_token'][:30]}...")
        else:
            print(f"   ✗ Cookie access_token MANQUANT!")
            
    else:
        print(f"   ✗ Échec: {response.text}")
        
except Exception as e:
    print(f"   ✗ Erreur: {e}")

# Test 3: Vérifier la configuration API_URL dans le frontend
print("\n3. Configuration Frontend")
print(f"   REACT_APP_API_URL devrait pointer vers: {BACKEND_URL}")
print(f"   Vérifiez dans frontend/.env que:")
print(f"   REACT_APP_API_URL=http://localhost:5000")

# Test 4: Instructions de débogage
print("\n4. Instructions de débogage dans le navigateur:")
print("   a) Ouvrez http://localhost:3000 dans le navigateur")
print("   b) Ouvrez les DevTools (F12)")
print("   c) Allez dans l'onglet 'Network' (Réseau)")
print("   d) Essayez de vous connecter avec:")
print("      Email: admin@getyourshare.com")
print("      Password: Admin123!")
print("   e) Dans Network, cherchez la requête 'login'")
print("   f) Vérifiez:")
print("      - Request URL: devrait être http://localhost:5000/api/auth/login")
print("      - Status: devrait être 200")
print("      - Response: devrait contenir les données utilisateur")
print("   g) Dans l'onglet 'Console', vérifiez s'il y a des erreurs")

print("\n" + "="*70)
