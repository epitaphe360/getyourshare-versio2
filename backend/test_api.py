#!/usr/bin/env python
"""
Test de l'API Backend
Vérifie que le backend peut récupérer les données de Supabase
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("="*60)
print("🔍 TEST ENDPOINTS BACKEND")
print("="*60)

# Test 1: Vérifier que l'API répond
print("\n1️⃣  Test de connectivité API...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✅ API Backend accessible")
    else:
        print(f"   ⚠️  Status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# Test 2: Essayer de récupérer des données sans authentification
print("\n2️⃣  Test d'endpoints publics...")
endpoints = [
    ("/", "Racine"),
    ("/api", "API racine"),
    ("/api/dashboard/stats", "Dashboard stats"),
]

for endpoint, description in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"   {description}: {response.status_code} - ", end="")
        if response.status_code in [200, 401, 403]:
            print("✅")
        else:
            print(response.text[:50])
    except Exception as e:
        print(f"   {description}: ❌ {type(e).__name__}")

# Test 3: Vérifier que le backend peut accéder à Supabase
print("\n3️⃣  Test d'accès Supabase depuis backend...")
try:
    # Créer un test utilisateur pour vérifier la connexion
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@shareyoursales.ma", "password": "TestPassword123!"},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Connexion réussie")
        print(f"      Token: {data.get('token', 'N/A')[:30]}...")
        print(f"      User: {data.get('user', {}).get('email', 'N/A')}")
    elif response.status_code == 401:
        print(f"   ⚠️  Authentification requise (credentials invalides)")
        print(f"      Message: {response.json().get('detail', 'Unknown')}")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
        print(f"      Response: {response.text[:100]}")
        
except Exception as e:
    print(f"   ❌ Erreur: {type(e).__name__}: {e}")

print("\n" + "="*60)
print("✅ Tests complétés")
print("="*60)
