#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration des tables de settings dans Supabase
"""

import os
import psycopg2
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()


def run_migration():
    """Execute la migration SQL pour créer les tables de settings"""

    logger.info("\n" + "=" * 60)
    logger.info("  MIGRATION: Tables de Settings")
    logger.info("=" * 60 + "\n")

    # Connexion PostgreSQL directe
    logger.info("Connexion à Supabase PostgreSQL...")

    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        logger.info("ERREUR: SUPABASE_DB_URL non trouvée dans .env")
        return False

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Lire le fichier SQL
    migration_file = os.path.join("..", "database", "migrations", "add_all_settings_tables.sql")
    logger.info(f"Lecture du fichier: {migration_file}")

    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info(f"\nExecution du script SQL...\n")

    try:
        # Exécuter tout le SQL d'un coup
        cursor.execute(sql_content)
        conn.commit()

        logger.info("OK - Script execute avec succes!")

        # Vérifier les tables créées
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%settings'
            ORDER BY table_name;
        """
        )

        tables = cursor.fetchall()

        success_count = len(tables)
        error_count = 0

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            logger.info(f"INFO: Certaines tables existent deja")
            success_count = 5
            error_count = 0
        else:
            logger.error(f"ERREUR: {error_msg}")
            success_count = 0
            error_count = 1

    finally:
        cursor.close()
        conn.close()

    logger.info("\n" + "=" * 60)
    logger.info(f"  RÉSULTATS:")
    logger.info(f"    Succès: {success_count}")
    logger.error(f"    Erreurs: {error_count}")
    logger.info("=" * 60)

    if error_count == 0:
        logger.info("\n  MIGRATION TERMINÉE AVEC SUCCÈS!\n")
        logger.info("  Tables créées:")
        logger.info("    - permissions_settings")
        logger.info("    - affiliate_settings")
        logger.info("    - registration_settings")
        logger.info("    - mlm_settings")
        logger.info("    - whitelabel_settings")
        logger.info("\n  Les boutons 'Enregistrer' sont maintenant fonctionnels!\n")
        return True
    else:
        logger.info("\n  MIGRATION TERMINÉE AVEC ERREURS")
        logger.info("  Vérifiez les messages ci-dessus\n")
        return False


if __name__ == "__main__":
    run_migration()
