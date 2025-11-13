"""
Script pour créer toutes les tables dans Supabase
Exécute le fichier database/schema.sql
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialiser le client Supabase avec la clé service_role pour admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def read_sql_file(filepath):
    """Lit le fichier SQL"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def create_tables():
    """Créer toutes les tables depuis schema.sql"""
    logger.info("🚀 Création des tables dans Supabase...")
    logger.info(f"📍 URL: {SUPABASE_URL}")

    # Lire le fichier schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    sql_content = read_sql_file(schema_path)

    # Supabase utilise PostgREST, donc on doit exécuter le SQL directement via l'API SQL
    # Pour créer les tables, il faut utiliser l'interface Supabase SQL Editor ou psycopg2

    logger.info(
        """
    ⚠️  IMPORTANT:

    Pour créer les tables, vous devez :

    1. Aller sur https://iamezkmapbhlhhvvsits.supabase.co/project/_/sql
    2. Copier le contenu de database/schema.sql
    3. Coller dans l'éditeur SQL et exécuter

    OU utiliser psycopg2 pour exécuter le SQL directement.

    Je vais essayer d'utiliser psycopg2...
    """
    )

    # Essayer avec psycopg2
    try:
        import psycopg2
        from urllib.parse import urlparse
from utils.logger import logger

        # Construire l'URL PostgreSQL depuis l'URL Supabase
        # Format: postgres://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
        project_ref = SUPABASE_URL.split("//")[1].split(".")[0]

        # Pour Supabase, l'URL de connexion PostgreSQL est différente
        logger.info("\n📝 Pour obtenir l'URL de connexion PostgreSQL:")
        logger.info("1. Allez sur https://iamezkmapbhlhhvvsits.supabase.co/project/_/settings/database")
        logger.info("2. Copiez la 'Connection string' sous 'Direct connection'")
        logger.info("3. Remplacez [YOUR-PASSWORD] par votre mot de passe de base de données")

        logger.info("\n💡 Ou utilisez l'éditeur SQL de Supabase pour créer les tables.")
        logger.info(f"\n📄 Fichier SQL à exécuter: {schema_path}")

        return False

    except ImportError:
        logger.info("❌ psycopg2 n'est pas installé. Utilisez l'éditeur SQL de Supabase.")
        return False


if __name__ == "__main__":
    create_tables()
