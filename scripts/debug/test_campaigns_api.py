import requests
import json

# Test de l'endpoint /api/campaigns
BASE_URL = "http://localhost:5000"

# D'abord, on doit se connecter pour avoir un cookie de session
# Utilisons l'admin
login_data = {
    "email": "admin@getyourshare.com",
    "password": "Admin123!"
}

session = requests.Session()

# Login
print("=" * 60)
print("1. TENTATIVE DE CONNEXION")
print("=" * 60)
login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
print(f"Status: {login_response.status_code}")
if login_response.status_code == 200:
    print(f"Login réussi!")
    print(f"User: {login_response.json().get('user', {}).get('email')}")
    print(f"Role: {login_response.json().get('user', {}).get('role')}")
else:
    print(f"Erreur: {login_response.text}")

# Test campagnes
print("\n" + "=" * 60)
print("2. TEST /api/campaigns")
print("=" * 60)
campaigns_response = session.get(f"{BASE_URL}/api/campaigns")
print(f"Status: {campaigns_response.status_code}")

if campaigns_response.status_code == 200:
    data = campaigns_response.json()
    print(f"Total: {data.get('total', 0)}")
    print(f"Campagnes: {len(data.get('data', []))}")
    
    for c in data.get('data', [])[:5]:
        print(f"\n  - {c.get('name')}")
        print(f"    ID: {c.get('id')}")
        print(f"    Status: {c.get('status')}")
        print(f"    merchant_id: {c.get('merchant_id')}")
else:
    print(f"Erreur: {campaigns_response.text}")
