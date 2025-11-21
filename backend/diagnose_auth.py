#!/usr/bin/env python
"""Test avec les deux méthodes d'authentification"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("="*70)
print("🔍 DIAGNOSTIC - AUTHENTIFICATION")
print("="*70)

# Authentification d'abord
print("\n1️⃣  LOGIN POUR OBTENIR LES TOKENS")
print("-" * 70)

login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "admin@getyourshare.com", "password": "Admin123!"},
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

# Récupérer le token depuis les cookies
access_token = None
for cookie in login_response.cookies:
    if cookie.name == "access_token":
        access_token = cookie.value
        break

print(f"✅ Login successful")
print(f"   Access Token: {access_token[:50] if access_token else 'NOT IN RESPONSE'}...")
print(f"   Set-Cookie header: {login_response.headers.get('set-cookie', 'NONE')[:100]}...")

# Test 1: Avec les cookies de la session
print("\n2️⃣  TEST AVEC COOKIES (Session)")
print("-" * 70)

session = requests.Session()
session.cookies.update(login_response.cookies)

endpoints = [
    "/api/analytics/overview",
    "/api/merchants",
    "/api/influencers",
    "/api/products",
]

for endpoint in endpoints:
    response = session.get(f"{BASE_URL}{endpoint}")
    print(f"   {endpoint}: {response.status_code}")

# Test 2: Avec Bearer Token dans le header
print("\n3️⃣  TEST AVEC BEARER TOKEN (Header)")
print("-" * 70)

if access_token:
    headers = {"Authorization": f"Bearer {access_token}"}
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"   {endpoint}: {response.status_code}")
else:
    print("❌ No access token found in response to test Bearer method")

# Test 3: Voir la structure de la réponse du login
print("\n4️⃣  STRUCTURE DE LA RÉPONSE LOGIN")
print("-" * 70)

print(json.dumps(login_response.json(), indent=2, default=str)[:500])
