#!/usr/bin/env python3
"""Test des endpoints des graphiques avec authentification"""
import requests
import json

API_URL = "http://127.0.0.1:5000"

def test_charts():
    print("🔐 Test des endpoints de graphiques")
    print("=" * 60)
    
    # 1. Login pour obtenir le token
    print("\n1️⃣ Connexion admin...")
    login_data = {
        "email": "admin@getyourshare.com",
        "password": "admin123"
    }
    
    session = requests.Session()
    login_response = session.post(f"{API_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Échec login: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("✅ Login réussi!")
    login_result = login_response.json()
    print(f"   User: {login_result.get('user', {}).get('email')}")
    print(f"   Role: {login_result.get('user', {}).get('role')}")
    
    # 2. Test Revenue Chart
    print("\n2️⃣ Test /api/analytics/revenue-chart...")
    revenue_response = session.get(f"{API_URL}/api/analytics/revenue-chart?period=7d")
    
    if revenue_response.status_code == 200:
        print("✅ Revenue Chart OK")
        data = revenue_response.json()
        print(f"   Points de données: {len(data.get('data', []))}")
        if data.get('data'):
            print(f"   Premier point: {data['data'][0]}")
            print(f"   Dernier point: {data['data'][-1]}")
    else:
        print(f"❌ Revenue Chart ERREUR: {revenue_response.status_code}")
        print(revenue_response.text)
    
    # 3. Test User Growth
    print("\n3️⃣ Test /api/analytics/user-growth...")
    growth_response = session.get(f"{API_URL}/api/analytics/user-growth?period=7d")
    
    if growth_response.status_code == 200:
        print("✅ User Growth OK")
        data = growth_response.json()
        print(f"   Points de données: {len(data.get('data', []))}")
        if data.get('data'):
            print(f"   Premier point: {data['data'][0]}")
            print(f"   Dernier point: {data['data'][-1]}")
    else:
        print(f"❌ User Growth ERREUR: {growth_response.status_code}")
        print(growth_response.text)
    
    # 4. Test Analytics Overview
    print("\n4️⃣ Test /api/analytics/overview...")
    overview_response = session.get(f"{API_URL}/api/analytics/overview")
    
    if overview_response.status_code == 200:
        print("✅ Analytics Overview OK")
        data = overview_response.json()
        stats = data.get('stats', {})
        print(f"   Revenu total: {stats.get('total_revenue', 0)}€")
        print(f"   Merchants: {stats.get('total_merchants', 0)}")
        print(f"   Influenceurs: {stats.get('total_influencers', 0)}")
        print(f"   Produits: {stats.get('total_products', 0)}")
    else:
        print(f"❌ Analytics Overview ERREUR: {overview_response.status_code}")
        print(overview_response.text)
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")

if __name__ == "__main__":
    test_charts()
