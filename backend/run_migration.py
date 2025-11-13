"""
Script de migration pour ajouter les colonnes et tables nécessaires
au système de paiement automatique
"""

from supabase_client import supabase
import os
from utils.logger import logger


def run_migration():
    """Exécute la migration SQL"""

    logger.info("\n" + "=" * 60)
    logger.info("🔄 MIGRATION: Paiements Automatiques")
    logger.info("=" * 60 + "\n")

    # Lire le fichier SQL
    migration_file = os.path.join(
        os.path.dirname(__file__), "..", "database", "migrations", "add_payment_columns.sql"
    )

    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        logger.info("📄 Fichier de migration chargé")
        logger.info(f"   Taille: {len(sql_content)} caractères\n")

        # Supabase ne supporte pas l'exécution directe de SQL via l'API Python
        # On doit utiliser l'éditeur SQL dans le dashboard Supabase
        # Ou créer les tables manuellement via l'API

        logger.info("⚠️  IMPORTANT:")
        logger.info("   Supabase nécessite d'exécuter le SQL via le Dashboard\n")
        logger.info("📋 INSTRUCTIONS:")
        logger.info("   1. Ouvrez: https://supabase.com/dashboard")
        logger.info("   2. Sélectionnez votre projet: iamezkmapbhlhhvvsits")
        logger.info("   3. Allez dans 'SQL Editor'")
        logger.info("   4. Copiez-collez le contenu du fichier:")
        logger.info(f"      {migration_file}")
        logger.info("   5. Cliquez sur 'Run'\n")

        # Alternative: Créer les tables via l'API REST
        logger.info("🔧 Création alternative via API...\n")

        # 1. Créer la table payouts
        try:
            # Vérifier si la table existe déjà
            result = supabase.table("payouts").select("id").limit(1).execute()
            logger.info("✅ Table 'payouts' existe déjà")
        except Exception as e:
            if "PGRST205" in str(e):  # Table n'existe pas
                logger.info("❌ Table 'payouts' manquante")
                logger.info("   → Créez-la via le Dashboard SQL Editor")
            else:
                logger.info(f"⚠️  Erreur vérification 'payouts': {e}")

        # 2. Créer la table notifications
        try:
            result = supabase.table("notifications").select("id").limit(1).execute()
            logger.info("✅ Table 'notifications' existe déjà")
        except Exception as e:
            if "PGRST205" in str(e):
                logger.info("❌ Table 'notifications' manquante")
                logger.info("   → Créez-la via le Dashboard SQL Editor")
            else:
                logger.info(f"⚠️  Erreur vérification 'notifications': {e}")

        # 3. Vérifier les colonnes
        try:
            result = supabase.table("sales").select("updated_at").limit(1).execute()
            logger.info("✅ Colonne 'sales.updated_at' existe")
        except Exception as e:
            if "PGRST204" in str(e):
                logger.info("❌ Colonne 'sales.updated_at' manquante")
                logger.info("   → Ajoutez-la via le Dashboard SQL Editor")
            else:
                logger.info(f"⚠️  Erreur vérification 'sales.updated_at': {e}")

        try:
            result = supabase.table("commissions").select("approved_at").limit(1).execute()
            logger.info("✅ Colonne 'commissions.approved_at' existe")
        except Exception as e:
            if "PGRST204" in str(e):
                logger.info("❌ Colonne 'commissions.approved_at' manquante")
                logger.info("   → Ajoutez-la via le Dashboard SQL Editor")
            else:
                logger.info(f"⚠️  Erreur vérification 'commissions.approved_at': {e}")

        logger.info("\n" + "=" * 60)
        logger.info("📝 RÉSUMÉ")
        logger.info("=" * 60)
        logger.info("\nPour finaliser la migration:")
        logger.info("1. Copiez le contenu de:")
        logger.info(f"   {migration_file}")
        logger.info("\n2. Exécutez-le dans Supabase SQL Editor:")
        logger.info("   https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql")
        logger.info("\n3. Relancez ce script pour vérifier")
        logger.info("\n" + "=" * 60 + "\n")

    except FileNotFoundError:
        logger.info(f"❌ Fichier de migration non trouvé: {migration_file}")
        logger.info("   Créez-le d'abord avec create_migration_file()")
    except Exception as e:
        logger.info(f"❌ Erreur: {e}")


def create_tables_manually():
    """Crée les tables manuellement (alternative)"""

    logger.info("\n🔧 Création manuelle des tables...\n")

    # Note: Supabase API ne permet pas de créer des tables directement
    # Il faut utiliser le SQL Editor du Dashboard

    logger.info("⚠️  Impossible de créer les tables via l'API Python")
    logger.info("   Utilisez le Dashboard Supabase SQL Editor\n")


if __name__ == "__main__":
    logger.info(
        """
╔═══════════════════════════════════════════════════════════╗
║   MIGRATION - SYSTÈME DE PAIEMENT AUTOMATIQUE            ║
╚═══════════════════════════════════════════════════════════╝
    """
    )

    run_migration()

    logger.info("\n✅ Vérification terminée")
    logger.info("\nAprès avoir exécuté le SQL dans Supabase Dashboard,")
    logger.info("relancez les tests avec: python test_payment_system.py\n")
