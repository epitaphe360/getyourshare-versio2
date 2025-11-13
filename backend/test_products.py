"""
Test - Vérifier les produits dans la base de données
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.logger import logger

load_dotenv()

# Connexion Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

logger.info("\n" + "="*50)
logger.info("🔍 VÉRIFICATION DES PRODUITS")
logger.info("="*50 + "\n")

# 1. Compter les produits
products_result = supabase.table("products").select("*", count="exact").execute()
total_products = products_result.count if hasattr(products_result, 'count') else len(products_result.data)

logger.info(f"📦 Total produits: {total_products}")

if products_result.data:
    logger.info(f"\n✅ Premiers produits:\n")
    for i, product in enumerate(products_result.data[:5], 1):
        logger.info(f"{i}. {product.get('name', 'Sans nom')}")
        logger.info(f"   - Prix: {product.get('price', 0)}€")
        logger.info(f"   - Catégorie: {product.get('category', 'N/A')}")
        logger.info(f"   - Merchant ID: {product.get('merchant_id', 'N/A')}")
        logger.info(f"   - Statut: {'Actif' if product.get('is_available') else 'Inactif'}")
        print()

# 2. Vérifier merchants
merchants_result = supabase.table("users").select("id, email, company_name").eq("role", "merchant").execute()
logger.info(f"🏪 Total merchants: {len(merchants_result.data)}")

if merchants_result.data:
    logger.info(f"\n✅ Premiers merchants:\n")
    for i, merchant in enumerate(merchants_result.data[:3], 1):
        # Compter produits par merchant
        merchant_id = merchant.get('id')
        products_count = supabase.table("products").select("id", count="exact").eq("merchant_id", merchant_id).execute()
        count = products_count.count if hasattr(products_count, 'count') else len(products_count.data)
        
        logger.info(f"{i}. {merchant.get('email')}")
        logger.info(f"   - Entreprise: {merchant.get('company_name', 'N/A')}")
        logger.info(f"   - ID: {merchant_id}")
        logger.info(f"   - Produits: {count}")
        print()

logger.info("="*50)
logger.info("✅ Test terminé")
logger.info("="*50)
