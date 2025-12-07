"""
Script pour vérifier et créer des produits de test
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import uuid
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Créer le client Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 60)
print("🔍 VÉRIFICATION DES PRODUITS")
print("=" * 60)

# 1. Compter les produits existants
products_result = supabase.table('products').select('id, name, category, merchant_id, price, stock').execute()
products_count = len(products_result.data)

print(f"\n📦 Nombre de produits dans la base: {products_count}")

if products_count > 0:
    print(f"\n✅ Il y a déjà {products_count} produits!")
    print("\nPremiers 5 produits:")
    for i, product in enumerate(products_result.data[:5], 1):
        print(f"{i}. {product.get('name')} - Prix: {product.get('price')}€ - Stock: {product.get('stock')} - Catégorie: {product.get('category', 'N/A')}")
else:
    print("\n❌ Aucun produit trouvé! Création de produits de test...\n")
    
    # 2. Récupérer un merchant
    merchants_result = supabase.table('users').select('id').eq('role', 'merchant').limit(1).execute()
    
    if not merchants_result.data:
        print("❌ Aucun merchant trouvé! Impossible de créer des produits.")
        exit(1)
    
    merchant_id = merchants_result.data[0]['id']
    print(f"✅ Merchant trouvé: {merchant_id}")
    
    # 3. Créer des produits de test
    test_products = [
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "iPhone 15 Pro Max",
            "description": "Le dernier iPhone avec des performances incroyables",
            "category": "Électronique",
            "price": 1299.99,
            "commission_rate": 5.0,
            "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400",
            "product_url": "https://example.com/iphone-15",
            "sku": "IPHONE-15-PRO-MAX",
            "stock": 50,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "MacBook Pro M3",
            "description": "Ordinateur portable puissant pour professionnels",
            "category": "Électronique",
            "price": 2499.99,
            "commission_rate": 4.5,
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
            "product_url": "https://example.com/macbook-pro",
            "sku": "MACBOOK-PRO-M3",
            "stock": 30,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "Nike Air Max 2024",
            "description": "Chaussures de sport confortables et stylées",
            "category": "Mode",
            "price": 149.99,
            "commission_rate": 8.0,
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "product_url": "https://example.com/nike-air-max",
            "sku": "NIKE-AIR-MAX-2024",
            "stock": 100,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "Sac à dos Premium",
            "description": "Sac à dos élégant et spacieux pour voyages",
            "category": "Mode",
            "price": 89.99,
            "commission_rate": 10.0,
            "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
            "product_url": "https://example.com/backpack",
            "sku": "BACKPACK-PREMIUM",
            "stock": 75,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "Montre connectée Pro",
            "description": "Montre intelligente avec suivi santé complet",
            "category": "Électronique",
            "price": 399.99,
            "commission_rate": 6.0,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            "product_url": "https://example.com/smartwatch",
            "sku": "SMARTWATCH-PRO",
            "stock": 60,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "Casque Audio Sans Fil",
            "description": "Casque avec réduction de bruit active",
            "category": "Électronique",
            "price": 249.99,
            "commission_rate": 7.0,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "product_url": "https://example.com/headphones",
            "sku": "HEADPHONES-WIRELESS",
            "stock": 80,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "T-shirt Premium Coton",
            "description": "T-shirt de qualité supérieure, 100% coton",
            "category": "Mode",
            "price": 29.99,
            "commission_rate": 12.0,
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
            "product_url": "https://example.com/tshirt",
            "sku": "TSHIRT-PREMIUM",
            "stock": 200,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "name": "Enceinte Bluetooth",
            "description": "Enceinte portable avec son puissant",
            "category": "Électronique",
            "price": 79.99,
            "commission_rate": 8.5,
            "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400",
            "product_url": "https://example.com/speaker",
            "sku": "SPEAKER-BLUETOOTH",
            "stock": 90,
            "is_active": True,
            "type": "physical",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Insérer les produits
    for i, product in enumerate(test_products, 1):
        try:
            result = supabase.table('products').insert(product).execute()
            print(f"✅ {i}. Produit créé: {product['name']}")
        except Exception as e:
            print(f"❌ Erreur création produit {product['name']}: {e}")
    
    print(f"\n✅ {len(test_products)} produits de test créés!")

print("\n" + "=" * 60)
print("✅ VÉRIFICATION TERMINÉE")
print("=" * 60)
