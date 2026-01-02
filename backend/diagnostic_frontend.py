import requests
import json

print("=" * 60)
print("🔍 DIAGNOSTIC CONNEXION FRONTEND → BACKEND")
print("=" * 60)

# Test 1: Backend accessible
print("\n📡 Test 1: Backend accessible")
try:
    response = requests.get("http://127.0.0.1:5000/health", timeout=5)
    print(f"✅ Backend actif - Status: {response.status_code}")
except Exception as e:
    print(f"❌ Backend inaccessible: {e}")
    exit(1)

# Test 2: Login API
print("\n🔐 Test 2: API de login")
try:
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://127.0.0.1:3003"
    }
    data = {
        "email": "admin@getyourshare.com",
        "password": "admin123"
    }
    
    response = requests.post(
        "http://127.0.0.1:5000/api/auth/login",
        headers=headers,
        json=data,
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    print(f"Headers CORS:")
    for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials', 'Access-Control-Allow-Headers']:
        value = response.headers.get(header, "❌ Absent")
        print(f"  - {header}: {value}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login réussi")
        print(f"  - Email: {data.get('user', {}).get('email')}")
        print(f"  - Rôle: {data.get('user', {}).get('role')}")
        print(f"  - Token présent: {'✅' if data.get('access_token') else '❌'}")
    else:
        print(f"❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")

# Test 3: CORS Preflight
print("\n🌐 Test 3: CORS Preflight (OPTIONS)")
try:
    headers = {
        "Origin": "http://127.0.0.1:3003",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    
    response = requests.options(
        "http://127.0.0.1:5000/api/auth/login",
        headers=headers,
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', '❌ Absent'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', '❌ Absent'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', '❌ Absent'),
        'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials', '❌ Absent'),
    }
    
    for key, value in cors_headers.items():
        status = "✅" if value != "❌ Absent" else "❌"
        print(f"  {status} {key}: {value}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("📋 RÉSUMÉ")
print("=" * 60)
print("""
Si le backend fonctionne mais le frontend ne peut pas se connecter:
1. Vérifiez la console du navigateur (F12 → Console)
2. Vérifiez l'onglet Network pour voir les requêtes
3. Assurez-vous que l'URL de l'API est correcte dans le frontend
4. Vérifiez que withCredentials est à true dans axios

Identifiants de test:
📧 Email: admin@getyourshare.com
🔑 Mot de passe: admin123
""")
