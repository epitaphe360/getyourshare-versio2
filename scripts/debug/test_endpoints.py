"""
Script de test des endpoints Influenceur et Commercial
Usage: python test_endpoints.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "VOTRE_TOKEN_JWT_ICI"  # Remplacer par un vrai token

# Headers avec authentification
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(method, endpoint, description, data=None):
    """Teste un endpoint et affiche le résultat"""
    print(f"\n📍 {description}")
    print(f"   {method} {endpoint}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"   ❌ Méthode {method} non supportée")
            return
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS ({response.status_code})")
            
            # Afficher un résumé des données
            data = response.json()
            if isinstance(data, dict):
                # Afficher les clés principales
                keys = list(data.keys())[:5]  # Limite à 5 clés
                print(f"   📦 Clés: {', '.join(keys)}")
                
                # Afficher des infos utiles
                if "total" in data:
                    print(f"   📊 Total: {data['total']}")
                if "links" in data and isinstance(data["links"], list):
                    print(f"   🔗 Liens: {len(data['links'])}")
                if "deals" in data and isinstance(data["deals"], list):
                    print(f"   💼 Deals: {len(data['deals'])}")
                if "leads" in data and isinstance(data["leads"], list):
                    print(f"   👥 Leads: {len(data['leads'])}")
                if "leaderboard" in data and isinstance(data["leaderboard"], list):
                    print(f"   🏆 Classement: {len(data['leaderboard'])} commerciaux")
        else:
            print(f"   ❌ ERREUR ({response.status_code})")
            print(f"   💬 {response.text[:200]}")
    
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERREUR: Impossible de se connecter au serveur")
        print(f"   💡 Vérifiez que le backend tourne sur {BASE_URL}")
    except Exception as e:
        print(f"   ❌ ERREUR: {str(e)}")

def test_influencer_endpoints():
    """Teste tous les endpoints Influenceur"""
    print_section("🎯 TESTS DASHBOARD INFLUENCEUR")
    
    test_endpoint("GET", "/api/analytics/overview", 
                  "1. Stats overview (earnings, clicks, sales, balance)")
    
    test_endpoint("GET", "/api/affiliate-links", 
                  "2. Liste des liens d'affiliation")
    
    test_endpoint("GET", "/api/subscriptions/current", 
                  "3. Abonnement actif (Free/Pro/Elite)")
    
    test_endpoint("POST", "/api/payouts/request", 
                  "4. Demander un payout (minimum 50€)")
    
    test_endpoint("GET", "/api/invitations", 
                  "5. Invitations reçues")

def test_commercial_endpoints():
    """Teste tous les endpoints Commercial"""
    print_section("💼 TESTS DASHBOARD COMMERCIAL")
    
    test_endpoint("GET", "/api/sales/dashboard/me", 
                  "1. Dashboard complet (stats, pipeline, gamification)")
    
    test_endpoint("GET", "/api/sales/leads/me", 
                  "2. Liste des leads (prospects)")
    
    test_endpoint("GET", "/api/sales/deals/me", 
                  "3. Liste des deals (opportunités)")
    
    test_endpoint("GET", "/api/sales/leaderboard", 
                  "4. Classement des commerciaux")

def test_authentication():
    """Teste si le token est valide"""
    print_section("🔐 TEST AUTHENTIFICATION")
    
    print(f"\n📍 Vérification du token JWT")
    print(f"   Token: {TOKEN[:20]}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=headers)
        
        if response.status_code == 200:
            print(f"   ✅ Token valide")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Token invalide ou expiré")
            print(f"   💡 Connectez-vous pour obtenir un nouveau token")
            return False
        else:
            print(f"   ⚠️  Réponse inattendue ({response.status_code})")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Impossible de se connecter au serveur")
        print(f"   💡 Lancez le backend: python backend/server.py")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("\n" + "🚀"*30)
    print("   TEST DES ENDPOINTS - DASHBOARDS INFLUENCEUR & COMMERCIAL")
    print("🚀"*30)
    
    # Vérifier la connexion au serveur
    print(f"\n📡 Serveur: {BASE_URL}")
    
    # Vérifier l'authentification
    if TOKEN == "VOTRE_TOKEN_JWT_ICI":
        print("\n" + "⚠️ "*30)
        print("   ATTENTION: Vous devez remplacer le token JWT dans le script!")
        print("   Éditez test_endpoints.py et remplacez TOKEN = '...'")
        print("⚠️ "*30)
        return
    
    if not test_authentication():
        print("\n❌ Arrêt des tests: authentification échouée")
        return
    
    # Menu de sélection
    print("\n" + "📋"*30)
    print("   CHOISISSEZ LES TESTS À EXÉCUTER:")
    print("   1. Endpoints Influenceur uniquement")
    print("   2. Endpoints Commercial uniquement")
    print("   3. Tous les endpoints (Influenceur + Commercial)")
    print("   4. Quitter")
    print("📋"*30)
    
    choice = input("\n👉 Votre choix (1-4): ").strip()
    
    if choice == "1":
        test_influencer_endpoints()
    elif choice == "2":
        test_commercial_endpoints()
    elif choice == "3":
        test_influencer_endpoints()
        test_commercial_endpoints()
    elif choice == "4":
        print("\n👋 Au revoir!")
        return
    else:
        print("\n❌ Choix invalide")
        return
    
    # Résumé final
    print("\n" + "✅"*30)
    print("   TESTS TERMINÉS!")
    print("✅"*30)
    print("\n💡 PROCHAINES ÉTAPES:")
    print("   1. Vérifier les résultats ci-dessus")
    print("   2. Si des erreurs 404: vérifier que les tables existent")
    print("   3. Si des données vides: exécuter INSERT_TEST_DATA.sql")
    print("   4. Tester dans le frontend (http://localhost:3000)")
    print("\n")

if __name__ == "__main__":
    main()
