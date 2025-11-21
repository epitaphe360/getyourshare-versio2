#!/usr/bin/env python
"""Test les endpoints publics vs protégés"""

import requests

BASE_URL = "http://localhost:5000"

session = requests.Session()

print("="*70)
print("🔍 VÉRIFICATION DES ENDPOINTS")
print("="*70)

# Endpoints publics
print("\n1️⃣  ENDPOINTS PUBLICS (sans authentification)")
print("-" * 70)

public_endpoints = [
    "/api",
    "/api/health",
    "/api/public/products",
    "/api/public/influencers",
]

for endpoint in public_endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        status = "✅" if response.status_code < 400 else "⚠️"
        print(f"{status} GET {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ GET {endpoint}: {type(e).__name__}")

# Authentification
print("\n2️⃣  AUTHENTIFICATION")
print("-" * 70)

login_response = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "admin@getyourshare.com", "password": "Admin123!"},
    timeout=5
)

if login_response.status_code == 200:
    print(f"✅ Login successful")
    print(f"   Cookies: {list(session.cookies.keys())}")
    
    # Essayer avec les cookies de la session
    print("\n3️⃣  ENDPOINTS PROTÉGÉS (avec cookies)")
    print("-" * 70)
    
    protected = [
        "/api/dashboard/stats",
        "/api/users",
        "/api/products",
        "/api/merchants",
    ]
    
    for endpoint in protected:
        try:
            response = session.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"{status} GET {endpoint}")
        except Exception as e:
            print(f"❌ GET {endpoint}: {type(e).__name__}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
