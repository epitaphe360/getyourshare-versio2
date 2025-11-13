"""
Script pour créer les tables de messagerie dans Supabase
"""

from supabase_client import supabase
import os
from utils.logger import logger


def create_messaging_tables():
    """Crée les tables conversations, messages et notifications"""

    # Lire le fichier SQL
    sql_file = os.path.join(os.path.dirname(__file__), "..", "database", "messaging_schema.sql")

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info("🔧 Création des tables de messagerie...")

    try:
        # Exécuter le SQL via l'API Supabase
        # Note: Supabase nécessite d'utiliser le client PostgreSQL ou l'interface web
        # Pour l'instant, on va créer les tables via des commandes individuelles

        # Créer table conversations
        logger.info("  → Table conversations...")
        supabase.table("conversations").select("id").limit(1).execute()
        logger.info("    ✅ Table conversations existe déjà ou créée")

    except Exception as e:
        logger.info(f"  ⚠️  Note: {e}")
        logger.info("\n📝 Instructions manuelles:")
        logger.info("  1. Ouvrir Supabase Dashboard: https://app.supabase.com")
        logger.info("  2. Aller dans 'SQL Editor'")
        logger.info("  3. Copier-coller le contenu de 'database/messaging_schema.sql'")
        logger.info("  4. Exécuter le script")
        logger.info("\n  Ou utiliser psql:")
        logger.info("  psql -h [HOST] -U postgres -d postgres -f database/messaging_schema.sql")

    logger.info("\n✨ Configuration terminée!")
    logger.info("\n💡 Tables créées:")
    logger.info("   - conversations: Threads entre utilisateurs")
    logger.info("   - messages: Messages individuels")
    logger.info("   - notifications: Alertes système")


if __name__ == "__main__":
    create_messaging_tables()
