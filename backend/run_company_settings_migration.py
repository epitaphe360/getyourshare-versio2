"""
Script pour exécuter la migration company_settings
"""

from supabase_client import supabase
import os
from utils.logger import logger


def run_migration():
    """Exécute la migration pour ajouter la table company_settings"""

    migration_file = os.path.join(
        os.path.dirname(__file__), "..", "database", "migrations", "add_company_settings.sql"
    )

    logger.info("📄 Lecture du fichier de migration...")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql = f.read()

    logger.info("🚀 Exécution de la migration company_settings...")

    try:
        # Supabase ne permet pas d'exécuter du SQL directement via l'API Python
        # Il faut utiliser l'interface SQL Editor de Supabase
        logger.info("⚠️  Pour exécuter cette migration:")
        logger.info("1. Ouvrez votre dashboard Supabase: https://supabase.com/dashboard")
        logger.info("2. Allez dans 'SQL Editor'")
        logger.info("3. Collez le contenu du fichier add_company_settings.sql")
        logger.info("4. Cliquez sur 'Run'")
        logger.info("")
        logger.info("📋 Contenu SQL à exécuter:")
        logger.info("=" * 60)
        logger.info(sql)
        logger.info("=" * 60)
        logger.info("")
        logger.info("✅ Une fois exécuté dans Supabase, les paramètres d'entreprise seront disponibles!")

    except Exception as e:
        logger.info(f"❌ Erreur: {e}")
        return False

    return True


if __name__ == "__main__":
    run_migration()
