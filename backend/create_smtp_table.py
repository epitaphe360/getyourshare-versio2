"""
Script pour créer la table smtp_settings dans Supabase
"""

from supabase_client import supabase
from utils.logger import logger


def create_smtp_settings_table():
    """Crée la table smtp_settings dans Supabase"""

    sql = """
    CREATE TABLE IF NOT EXISTS smtp_settings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
        host VARCHAR(255) NOT NULL DEFAULT 'smtp.gmail.com',
        port INTEGER NOT NULL DEFAULT 587,
        username VARCHAR(255),
        password VARCHAR(255),
        from_email VARCHAR(255) NOT NULL DEFAULT 'noreply@shareyoursales.com',
        from_name VARCHAR(255) NOT NULL DEFAULT 'Share Your Sales',
        encryption VARCHAR(10) CHECK (encryption IN ('tls', 'ssl', 'none')) DEFAULT 'tls',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Index pour améliorer les performances
    CREATE INDEX IF NOT EXISTS idx_smtp_settings_user_id ON smtp_settings(user_id);
    """

    try:
        logger.info("[START] Création de la table smtp_settings...")

        # Exécuter le SQL via l'API Supabase
        response = supabase.rpc("exec_sql", {"query": sql}).execute()

        logger.info("[OK] Table smtp_settings créée avec succès !")
        return True

    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la création de la table: {e}")
        logger.info(
            "[INFO] Si la fonction exec_sql n'existe pas, exécutez le SQL manuellement dans l'interface Supabase SQL Editor:"
        )
        logger.info("\n" + sql + "\n")
        return False


if __name__ == "__main__":
    create_smtp_settings_table()
