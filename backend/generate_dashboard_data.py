#!/usr/bin/env python3
"""
Script simple pour générer des données de test pour les dashboards
Utilise l'API backend au lieu de Supabase direct
"""
import requests
import random
from datetime import datetime, timedelta

# Configuration
API_URL = "https://getyourshare-backend-production.up.railway.app"
ADMIN_EMAIL = "admin@getyourshare.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Se connecter en tant qu'admin"""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.cookies
    else:
        print(f"❌ Échec connexion admin: {response.status_code}")
        return None

def generate_test_sales(cookies):
    """Générer des ventes de test pour les 30 derniers jours"""
    print("\n📊 Génération de ventes de test...")

    # Récupérer les produits existants
    products_response = requests.get(f"{API_URL}/api/products", cookies=cookies)
    if products_response.status_code != 200:
        print(f"❌ Impossible de récupérer les produits: {products_response.status_code}")
        return

    products = products_response.json().get("products", [])
    if not products:
        print("⚠️  Aucun produit trouvé")
        return

    print(f"✅ {len(products)} produits trouvés")

    # Générer des ventes pour les 30 derniers jours
    sales_created = 0
    for days_ago in range(30):
        date = datetime.now() - timedelta(days=days_ago)

        # Générer 3-10 ventes par jour
        num_sales = random.randint(3, 10)

        for _ in range(num_sales):
            product = random.choice(products)
            amount = float(product.get("price", 100))

            sale_data = {
                "product_id": product["id"],
                "merchant_id": product.get("merchant_id"),
                "amount": amount,
                "platform_commission": amount * 0.1,  # 10% commission plateforme
                "commission_amount": amount * 0.05,   # 5% commission influenceur
                "status": "completed",
                "created_at": date.isoformat()
            }

            # Note: L'API pourrait ne pas avoir d'endpoint public pour créer des sales
            # On peut utiliser l'endpoint webhook Stripe à la place
            # Pour l'instant, on compte juste les ventes qu'on voudrait créer
            sales_created += 1

    print(f"📈 {sales_created} ventes seraient créées (API endpoint nécessaire)")
    print("\n💡 Pour créer les ventes, exécutez ce SQL dans Supabase:")
    print("=" * 60)

    # Générer du SQL pour insertion directe
    for days_ago in range(30):
        date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        num_sales = random.randint(3, 10)

        for _ in range(num_sales):
            amount = random.uniform(50, 500)
            print(f"INSERT INTO sales (amount, platform_commission, commission_amount, status, created_at) ")
            print(f"VALUES ({amount:.2f}, {amount * 0.1:.2f}, {amount * 0.05:.2f}, 'completed', '{date}');")

if __name__ == "__main__":
    print("="*70)
    print("🌱 GÉNÉRATEUR DE DONNÉES DE TEST POUR DASHBOARDS")
    print("="*70)

    # Se connecter en tant qu'admin
    cookies = login_admin()

    if cookies:
        print("✅ Connecté en tant qu'admin")
        generate_test_sales(cookies)
    else:
        print("❌ Impossible de se connecter")
        print("\n💡 Solution alternative: Exécutez ce SQL dans Supabase SQL Editor:")
        print("=" * 60)

        # Générer du SQL pour insertion directe sans connexion
        for days_ago in range(30):
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            num_sales = random.randint(5, 15)

            for _ in range(num_sales):
                amount = random.uniform(50, 500)
                print(f"INSERT INTO sales (amount, platform_commission, commission_amount, status, created_at) VALUES ({amount:.2f}, {amount * 0.1:.2f}, {amount * 0.05:.2f}, 'completed', '{date}');")
