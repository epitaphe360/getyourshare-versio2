"""
Script de test pour les nouveaux endpoints
"""

import requests
import json
from utils.logger import logger

BASE_URL = "http://localhost:8001"


def test_login():
    """Test de connexion"""
    logger.info("\n🔐 Test de connexion...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@shareyoursales.com", "password": "Admin123!"},
    )
    if response.status_code == 200:
        token = response.json().get("token")
        logger.info(f"✅ Connexion réussie - Token obtenu")
        return token
    else:
        logger.info(f"❌ Erreur de connexion: {response.status_code}")
        logger.info(response.text)
        return None


def test_products(token):
    """Test des endpoints produits"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n📦 Test GET /api/products...")
    response = requests.get(f"{BASE_URL}/api/products", headers=headers)
    if response.status_code == 200:
        products = response.json()
        logger.info(f"✅ {len(products)} produits trouvés")
        if products:
            logger.info(f"   Premier produit: {products[0].get('name', 'N/A')}")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def test_campaigns(token):
    """Test des endpoints campagnes"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n🎯 Test GET /api/campaigns...")
    response = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
    if response.status_code == 200:
        campaigns = response.json()
        logger.info(f"✅ {len(campaigns)} campagnes trouvées")
        if campaigns:
            logger.info(f"   Première campagne: {campaigns[0].get('name', 'N/A')}")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def test_sales(token):
    """Test des endpoints ventes"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n💰 Test GET /api/sales/1...")
    response = requests.get(f"{BASE_URL}/api/sales/1", headers=headers)
    if response.status_code == 200:
        sales = response.json()
        logger.info(f"✅ {len(sales)} ventes trouvées pour l'influenceur 1")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def test_commissions(token):
    """Test des endpoints commissions"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n💵 Test GET /api/commissions/1...")
    response = requests.get(f"{BASE_URL}/api/commissions/1", headers=headers)
    if response.status_code == 200:
        commissions = response.json()
        logger.info(f"✅ {len(commissions)} commissions trouvées pour l'influenceur 1")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def test_reports(token):
    """Test des endpoints rapports"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n📊 Test GET /api/reports/performance...")
    response = requests.get(
        f"{BASE_URL}/api/reports/performance",
        headers=headers,
        params={"user_id": 1, "start_date": "2024-01-01", "end_date": "2025-12-31"},
    )
    if response.status_code == 200:
        report = response.json()
        logger.info(f"✅ Rapport généré:")
        logger.info(f"   Total ventes: {report.get('total_sales', 0)}")
        logger.info(f"   Revenus: {report.get('total_revenue', 0)}€")
        logger.info(f"   Commissions: {report.get('total_commission', 0)}€")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def test_settings(token):
    """Test des endpoints paramètres"""
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("\n⚙️  Test GET /api/settings...")
    response = requests.get(f"{BASE_URL}/api/settings", headers=headers)
    if response.status_code == 200:
        settings = response.json()
        logger.info(f"✅ {len(settings)} paramètres trouvés")
    else:
        logger.info(f"❌ Erreur: {response.status_code} - {response.text}")


def main():
    logger.info("=" * 60)
    logger.info("🧪 TEST DES NOUVEAUX ENDPOINTS")
    logger.info("=" * 60)

    # Test de connexion
    token = test_login()
    if not token:
        logger.info("\n❌ Impossible de continuer sans token")
        return

    # Tests des différents endpoints
    test_products(token)
    test_campaigns(token)
    test_sales(token)
    test_commissions(token)
    test_reports(token)
    test_settings(token)

    logger.info("\n" + "=" * 60)
    logger.info("✅ Tests terminés")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
