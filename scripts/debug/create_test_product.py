#!/usr/bin/env python
"""Script pour créer un produit de test et vérifier le système de modération IA (Version Async)"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Ajouter le répertoire courant au path pour importer backend
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.server import app
    from httpx import AsyncClient, ASGITransport
    USE_DIRECT_APP = True
    print("✅ Utilisation de httpx.AsyncClient avec l'application FastAPI directement")
except ImportError as e:
    import requests
    USE_DIRECT_APP = False
    print(f"⚠️ Utilisation de requests (HTTP) - Erreur import: {e}")

BASE_URL = "http://localhost:5000"

async def make_request(method, endpoint, **kwargs):
    if USE_DIRECT_APP:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            if method.lower() == 'get':
                return await client.get(endpoint, **kwargs)
            elif method.lower() == 'post':
                return await client.post(endpoint, **kwargs)
    else:
        url = f"{BASE_URL}{endpoint}"
        if method.lower() == 'get':
            return requests.get(url, **kwargs)
        elif method.lower() == 'post':
            return requests.post(url, **kwargs)

async def login_as_merchant():
    """Se connecter en tant que merchant"""
    print("🔐 Connexion en tant que merchant...")
    
    response = await make_request(
        "post",
        "/api/auth/login",
        json={
            "email": "luxury.crafts@getyourshare.com",
            "password": "Test123!"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Connexion réussie")
        return token
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        print(response.text)
        return None

async def create_test_product(token):
    """Créer un produit de test"""
    print("\n📦 Création d'un produit de test...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    product_data = {
        "name": "🧪 Produit Test - Modération IA",
        "description": "Ceci est un produit de test pour vérifier le système de modération automatique par intelligence artificielle. Il devrait être détecté et analysé par l'IA.",
        "price": 99.99,
        "commission_rate": 10.0,
        "category": "electronics",
        "image_url": "https://via.placeholder.com/400x400.png?text=Test+Product",
        "stock": 50,
        "sku": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "is_active": True
    }
    
    response = await make_request(
        "post",
        "/api/products",
        headers=headers,
        json=product_data
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        product = data.get('product', data)
        print(f"✅ Produit créé avec succès!")
        print(f"   ID: {product.get('id')}")
        print(f"   Nom: {product.get('name')}")
        print(f"   Status: {product.get('moderation_status', 'N/A')}")
        return product
    else:
        print(f"❌ Échec de création: {response.status_code}")
        print(response.text)
        return None

async def check_moderation_queue(token):
    """Vérifier la file d'attente de modération"""
    print("\n🔍 Vérification de la file de modération...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = await make_request(
        "get",
        "/api/admin/moderation/my-pending",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("pending_products", [])
        print(f"✅ {len(products)} produit(s) en attente de modération")
        
        for product in products:
            print(f"\n   📦 {product.get('product_name')}")
            print(f"      ID: {product.get('id')}")
            print(f"      Score risque: {product.get('ai_risk_level', 'N/A')}")
            print(f"      Raison: {product.get('ai_reason', 'N/A')}")
        
        return products
    else:
        print(f"❌ Échec: {response.status_code}")
        print(response.text)
        return []

async def get_product_analysis(token, product_id):
    """Obtenir l'analyse IA d'un produit"""
    # Note: L'endpoint d'analyse détaillée est réservé aux admins.
    # En tant que merchant, on a déjà les infos dans my-pending.
    print(f"\n🤖 Analyse IA du produit {product_id}...")
    print("ℹ️  L'analyse détaillée est disponible pour les administrateurs.")
    return None

async def main():
    print("=" * 60)
    print("🧪 TEST DU SYSTÈME DE MODÉRATION IA (ASYNC)")
    print("=" * 60)
    
    # 1. Connexion
    token = await login_as_merchant()
    if not token:
        print("\n❌ Impossible de se connecter.")
        return
    
    # 2. Créer un produit de test
    product = await create_test_product(token)
    if not product:
        print("\n❌ Échec de création du produit")
        return
    
    # 3. Vérifier la file de modération
    print("\n⏳ Attente de 2 secondes pour le traitement IA...")
    await asyncio.sleep(2)
    
    pending_products = await check_moderation_queue(token)
    
    # 4. Obtenir l'analyse détaillée
    if product.get('id'):
        await get_product_analysis(token, product['id'])
    
    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)
    print("\n💡 Vous pouvez maintenant:")
    print("   1. Actualiser la page de modération dans le frontend")
    print("   2. Voir le produit apparaître dans la liste")
    print("   3. Approuver ou rejeter le produit")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
