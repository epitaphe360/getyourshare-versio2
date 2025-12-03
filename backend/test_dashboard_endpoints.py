#!/usr/bin/env python3
"""Test complet des endpoints du dashboard avec détails des erreurs"""
import requests
import json

API_URL = "http://127.0.0.1:5000"

def test_all_dashboard_endpoints():
    print("🔍 DIAGNOSTIC COMPLET DU DASHBOARD")
    print("=" * 80)
    
    # 1. Login
    print("\n1️⃣ CONNEXION ADMIN...")
    login_data = {
        "email": "admin@getyourshare.com",
        "password": "admin123"
    }
    
    session = requests.Session()
    try:
        login_response = session.post(f"{API_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ ÉCHEC LOGIN: {login_response.status_code}")
            print(f"   Réponse: {login_response.text}")
            return
        
        print("✅ Login réussi!")
        login_result = login_response.json()
        print(f"   User: {login_result.get('user', {}).get('email')}")
        print(f"   Role: {login_result.get('user', {}).get('role')}")
    except Exception as e:
        print(f"❌ ERREUR LOGIN: {e}")
        return
    
    # Liste des endpoints à tester
    endpoints = [
        ("Analytics Overview", "GET", "/api/analytics/overview", None),
        ("Revenue Chart", "GET", "/api/analytics/revenue-chart?period=30d", None),
        ("User Growth", "GET", "/api/analytics/user-growth?period=30d", None),
        ("Activity Recent", "GET", "/api/activity/recent?limit=10", None),
        ("Notifications", "GET", "/api/notifications", None),
        ("User Profile", "GET", "/api/users/me", None),
    ]
    
    results = {
        "success": [],
        "failed": []
    }
    
    print(f"\n{'=' * 80}")
    print("2️⃣ TEST DES ENDPOINTS DU DASHBOARD")
    print(f"{'=' * 80}\n")
    
    for idx, (name, method, endpoint, data) in enumerate(endpoints, 1):
        print(f"\n[{idx}/{len(endpoints)}] Test: {name}")
        print(f"    Endpoint: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = session.get(f"{API_URL}{endpoint}", timeout=5)
            else:
                response = session.post(f"{API_URL}{endpoint}", json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"    ✅ STATUS: {response.status_code} OK")
                try:
                    json_data = response.json()
                    
                    # Afficher des infos selon le type de réponse
                    if "data" in json_data:
                        data_content = json_data["data"]
                        if isinstance(data_content, list):
                            print(f"    📊 Données: {len(data_content)} éléments")
                            if len(data_content) > 0:
                                print(f"    📝 Premier élément: {list(data_content[0].keys()) if isinstance(data_content[0], dict) else data_content[0]}")
                        elif isinstance(data_content, dict):
                            print(f"    📊 Données: {len(data_content)} champs")
                            print(f"    📝 Champs: {list(data_content.keys())[:5]}")
                    
                    if "stats" in json_data:
                        stats = json_data["stats"]
                        print(f"    📊 Stats: {len(stats)} métriques")
                        # Afficher quelques stats importantes
                        for key in ["total_revenue", "total_merchants", "total_influencers"]:
                            if key in stats:
                                print(f"       • {key}: {stats[key]}")
                    
                    results["success"].append(name)
                except json.JSONDecodeError:
                    print(f"    ⚠️  Réponse non-JSON: {response.text[:100]}")
                    results["success"].append(f"{name} (non-JSON)")
            else:
                print(f"    ❌ STATUS: {response.status_code}")
                print(f"    📄 Réponse: {response.text[:200]}")
                results["failed"].append({
                    "name": name,
                    "status": response.status_code,
                    "error": response.text[:200]
                })
        
        except requests.exceptions.Timeout:
            print(f"    ⏱️  TIMEOUT (>5s)")
            results["failed"].append({
                "name": name,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"    ❌ ERREUR: {e}")
            results["failed"].append({
                "name": name,
                "error": str(e)
            })
    
    # Résumé
    print(f"\n{'=' * 80}")
    print("📊 RÉSUMÉ")
    print(f"{'=' * 80}")
    print(f"\n✅ Réussis: {len(results['success'])}/{len(endpoints)}")
    for name in results["success"]:
        print(f"   • {name}")
    
    if results["failed"]:
        print(f"\n❌ Échoués: {len(results['failed'])}/{len(endpoints)}")
        for failure in results["failed"]:
            print(f"\n   • {failure['name']}")
            if "status" in failure:
                print(f"     Status: {failure['status']}")
            print(f"     Erreur: {failure['error']}")
    
    print(f"\n{'=' * 80}")
    if len(results["failed"]) == 0:
        print("🎉 TOUS LES ENDPOINTS FONCTIONNENT!")
    else:
        print(f"⚠️  {len(results['failed'])} ENDPOINT(S) À CORRIGER")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    test_all_dashboard_endpoints()
