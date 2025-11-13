"""
Script complet pour configurer Supabase :
1. Créer toutes les tables
2. Migrer toutes les données MOCK
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import bcrypt
from datetime import datetime
import json

# Charger les variables d'environnement
load_dotenv()

# Importer les données MOCK
sys.path.insert(0, os.path.dirname(__file__))
from mock_data import MOCK_USERS, MOCK_PRODUCTS, MOCK_SALES
from utils.logger import logger

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

logger.info("=" * 70)
logger.info("🚀 SETUP SUPABASE - ShareYourSales")
logger.info("=" * 70)
logger.info(f"📍 URL: {SUPABASE_URL}\n")

# ============================================
# ÉTAPE 1: Créer les tables
# ============================================

logger.info("📋 ÉTAPE 1: Création des tables")
logger.info("-" * 70)


def read_sql_file():
    """Lit le fichier schema.sql"""
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()


# Pour créer les tables, on doit utiliser l'éditeur SQL de Supabase ou psycopg2
logger.info(
    """
⚠️  Pour créer les tables dans Supabase:

Méthode 1 (Recommandée):
1. Allez sur: https://iamezkmapbhlhhvvsits.supabase.co/project/_/sql
2. Copiez TOUT le contenu de 'database/schema.sql'
3. Collez dans l'éditeur SQL
4. Cliquez sur 'RUN' pour exécuter

Méthode 2 (Avancée):
Utilisez psycopg2 avec l'URL de connexion PostgreSQL directe.

Une fois les tables créées, relancez ce script pour migrer les données.
"""
)

response = input("\n✅ Tables créées? (o/n): ").strip().lower()

if response != "o":
    logger.info("❌ Veuillez d'abord créer les tables dans Supabase.")
    logger.info(f"📄 Fichier SQL: database/schema.sql")
    sys.exit(1)

# ============================================
# ÉTAPE 2: Migrer les utilisateurs
# ============================================

logger.info("\n📋 ÉTAPE 2: Migration des utilisateurs")
logger.info("-" * 70)


def migrate_users():
    """Migrer les utilisateurs MOCK vers Supabase"""
    logger.info(f"👤 Migration de {len(MOCK_USERS)} utilisateurs...")

    for user in MOCK_USERS:
        try:
            # Préparer les données utilisateur
            user_data = {
                "email": user["email"],
                "password_hash": user["password"],  # Déjà hashé avec bcrypt
                "role": user["role"],
                "phone": user.get("phone"),
                "phone_verified": user.get("phone_verified", False),
                "two_fa_enabled": user.get("two_fa_enabled", False),
                "last_login": user.get("last_login"),
                "is_active": user.get("is_active", True),
            }

            # Insérer dans Supabase
            result = supabase.table("users").insert(user_data).execute()

            logger.info(f"  ✅ {user['email']} ({user['role']})")

        except Exception as e:
            logger.info(f"  ❌ Erreur pour {user['email']}: {str(e)}")


migrate_users()

# ============================================
# ÉTAPE 3: Migrer les merchants
# ============================================

logger.info("\n📋 ÉTAPE 3: Migration des merchants")
logger.info("-" * 70)


def migrate_merchants():
    """Migrer les merchants MOCK vers Supabase"""
    logger.info(f"🏢 Migration de {len(MOCK_MERCHANTS)} merchants...")

    # D'abord, récupérer les user_id des merchants depuis Supabase
    users_result = supabase.table("users").select("id, email").eq("role", "merchant").execute()
    email_to_user_id = {u["email"]: u["id"] for u in users_result.data}

    for merchant in MOCK_MERCHANTS:
        try:
            # Trouver le user_id correspondant
            user_email = merchant.get("user_email")
            if not user_email:
                # Essayer de deviner basé sur l'index
                if merchant["id"] == "merchant_1":
                    user_email = "contact@techstyle.fr"
                elif merchant["id"] == "merchant_2":
                    user_email = "hello@beautypro.com"

            user_id = email_to_user_id.get(user_email)
            if not user_id:
                logger.info(f"  ⚠️  User introuvable pour {merchant['company_name']}")
                continue

            merchant_data = {
                "user_id": user_id,
                "company_name": merchant["company_name"],
                "industry": merchant.get("industry"),
                "category": merchant.get("category"),
                "website": merchant.get("website"),
                "description": merchant.get("description"),
                "subscription_plan": merchant.get("subscription_plan", "free"),
                "commission_rate": merchant.get("commission_rate", 5.0),
                "total_sales": merchant.get("total_sales", 0),
                "total_commission_paid": merchant.get("total_commission_paid", 0),
            }

            result = supabase.table("merchants").insert(merchant_data).execute()
            logger.info(f"  ✅ {merchant['company_name']}")

        except Exception as e:
            logger.info(f"  ❌ Erreur pour {merchant['company_name']}: {str(e)}")


migrate_merchants()

# ============================================
# ÉTAPE 4: Migrer les influencers
# ============================================

logger.info("\n📋 ÉTAPE 4: Migration des influencers")
logger.info("-" * 70)


def migrate_influencers():
    """Migrer les influencers MOCK vers Supabase"""
    logger.info(f"⭐ Migration de {len(MOCK_INFLUENCERS)} influencers...")

    # Récupérer les user_id des influencers depuis Supabase
    users_result = supabase.table("users").select("id, email").eq("role", "influencer").execute()
    email_to_user_id = {u["email"]: u["id"] for u in users_result.data}

    for influencer in MOCK_INFLUENCERS:
        try:
            # Trouver le user_id correspondant
            user_email = influencer.get("user_email")
            if not user_email:
                # Essayer de deviner
                if influencer["id"] == "influencer_1":
                    user_email = "emma.style@instagram.com"
                elif influencer["id"] == "influencer_2":
                    user_email = "lucas.tech@youtube.com"
                elif influencer["id"] == "influencer_3":
                    user_email = "julie.beauty@tiktok.com"

            user_id = email_to_user_id.get(user_email)
            if not user_id:
                logger.info(f"  ⚠️  User introuvable pour {influencer['full_name']}")
                continue

            influencer_data = {
                "user_id": user_id,
                "username": influencer["username"],
                "full_name": influencer["full_name"],
                "bio": influencer.get("bio"),
                "category": influencer.get("category"),
                "influencer_type": influencer.get("influencer_type"),
                "audience_size": influencer.get("audience_size", 0),
                "engagement_rate": influencer.get("engagement_rate", 0.0),
                "subscription_plan": influencer.get("subscription_plan", "starter"),
                "total_clicks": influencer.get("total_clicks", 0),
                "total_sales": influencer.get("total_sales", 0),
                "total_earnings": influencer.get("total_earnings", 0.0),
                "balance": influencer.get("balance", 0.0),
                "social_links": json.dumps(influencer.get("social_links", {})),
            }

            result = supabase.table("influencers").insert(influencer_data).execute()
            logger.info(f"  ✅ {influencer['full_name']} (@{influencer['username']})")

        except Exception as e:
            logger.info(f"  ❌ Erreur pour {influencer['full_name']}: {str(e)}")


migrate_influencers()

# ============================================
# ÉTAPE 5: Migrer les produits
# ============================================

logger.info("\n📋 ÉTAPE 5: Migration des produits")
logger.info("-" * 70)


def migrate_products():
    """Migrer les produits MOCK vers Supabase"""
    logger.info(f"📦 Migration de {len(MOCK_PRODUCTS)} produits...")

    # Récupérer les merchant_id depuis Supabase
    merchants_result = supabase.table("merchants").select("id, company_name").execute()
    company_to_merchant_id = {m["company_name"]: m["id"] for m in merchants_result.data}

    for product in MOCK_PRODUCTS:
        try:
            # Trouver le merchant_id
            merchant_name = product.get("merchant_name", "TechStyle")
            merchant_id = company_to_merchant_id.get(merchant_name)

            if not merchant_id:
                # Utiliser le premier merchant par défaut
                merchant_id = merchants_result.data[0]["id"] if merchants_result.data else None

            if not merchant_id:
                logger.info(f"  ⚠️  Merchant introuvable pour {product['name']}")
                continue

            product_data = {
                "merchant_id": merchant_id,
                "name": product["name"],
                "description": product.get("description"),
                "category": product["category"],
                "price": product["price"],
                "commission_rate": product["commission_rate"],
                "commission_type": "percentage",
                "images": json.dumps(product.get("images", [])),
                "slug": product.get("slug"),
                "stock_quantity": product.get("stock", 0),
                "is_available": product.get("is_available", True),
            }

            result = supabase.table("products").insert(product_data).execute()
            logger.info(f"  ✅ {product['name']} ({product['category']})")

        except Exception as e:
            logger.info(f"  ❌ Erreur pour {product['name']}: {str(e)}")


migrate_products()

# ============================================
# FINALISATION
# ============================================

logger.info("\n" + "=" * 70)
logger.info("✅ MIGRATION TERMINÉE !")
logger.info("=" * 70)
logger.info(
    """
Prochaines étapes:
1. Vérifiez les données dans Supabase
2. Testez l'application backend
3. L'application utilise maintenant Supabase au lieu des données MOCK

📊 Dashboard Supabase: https://iamezkmapbhlhhvvsits.supabase.co
"""
)
