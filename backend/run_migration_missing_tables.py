"""
Script pour exécuter la migration des tables manquantes
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.logger import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.info("❌ ERREUR: Variables d'environnement Supabase manquantes")
    logger.info("   Vérifiez SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY dans .env")
    exit(1)

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

logger.info("=" * 70)
logger.info("🚀 MIGRATION - Tables manquantes ShareYourSales")
logger.info("=" * 70)
logger.info(f"📍 URL: {SUPABASE_URL}\n")

# Lire le fichier SQL
migration_path = os.path.join(
    os.path.dirname(__file__), "..", "database", "migrations", "add_only_missing_tables.sql"
)

logger.info(f"📄 Lecture du fichier: {migration_path}")

try:
    with open(migration_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info(f"✅ Fichier lu: {len(sql_content)} caractères\n")

    logger.info("⚠️  IMPORTANT: Ce script ne peut pas exécuter directement le SQL.")
    logger.info("   Supabase Python SDK ne supporte pas l'exécution de DDL (CREATE TABLE).\n")

    logger.info("📋 INSTRUCTIONS POUR EXÉCUTER LA MIGRATION:")
    logger.info("-" * 70)
    logger.info("1. Ouvrez votre navigateur:")
    logger.info(f"   https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql/new")
    logger.info("")
    logger.info("2. Copiez le contenu du fichier:")
    logger.info(f"   {migration_path}")
    logger.info("")
    logger.info("3. Collez dans l'éditeur SQL de Supabase")
    logger.info("")
    logger.info("4. Cliquez sur 'RUN' (bouton vert en haut à droite)")
    logger.info("")
    logger.info("5. Vérifiez les résultats:")
    logger.info("   - 8 nouvelles tables créées")
    logger.info("   - 28 permissions insérées")
    logger.info("   - 5 templates d'emails insérés")
    logger.info("")
    logger.info("=" * 70)
    logger.info("📋 TABLES QUI SERONT CRÉÉES:")
    logger.info("=" * 70)
    tables = [
        "1. company_settings       - Paramètres entreprise",
        "2. payment_gateways       - Gateways paiement (CMI, PayZen, SG Maroc)",
        "3. invoices               - Facturation automatique",
        "4. activity_log           - Journal d'activité",
        "5. mlm_commissions        - Commissions MLM multi-niveaux",
        "6. permissions            - Permissions granulaires par rôle",
        "7. traffic_sources        - Sources de trafic UTM",
        "8. email_templates        - Templates emails transactionnels",
    ]
    for table in tables:
        logger.info(f"   {table}")

    logger.info("")
    logger.info("=" * 70)
    logger.info("💡 ALTERNATIVE: Copier-coller manuel")
    logger.info("=" * 70)
    logger.info("Si vous préférez copier le SQL directement, tapez:")
    logger.info(f"   cat {migration_path}")
    logger.info("")
    logger.info("Puis copiez tout le contenu et collez dans Supabase SQL Editor.")
    logger.info("")

except FileNotFoundError:
    logger.info(f"❌ ERREUR: Fichier non trouvé: {migration_path}")
    logger.info("   Vérifiez que le fichier existe dans database/migrations/")
    exit(1)
except Exception as e:
    logger.info(f"❌ ERREUR: {e}")
    exit(1)

logger.info("✅ Script terminé")
logger.info("   Suivez les instructions ci-dessus pour exécuter la migration.")
