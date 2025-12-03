"""
Script pour initialiser les tables premium dans Supabase
Exécute le SQL contenu dans CREATE_PREMIUM_TABLES.sql
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Construit l'URL de connexion PostgreSQL depuis les variables d'environnement"""
    supabase_url = os.getenv("SUPABASE_URL")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")

    if not supabase_url:
        print("❌ SUPABASE_URL non trouvé dans .env")
        return None

    # Extraire le project_ref de l'URL Supabase
    # Format: https://[project_ref].supabase.co
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")

    # URL PostgreSQL format
    db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    return db_url

def init_tables():
    """Initialise les tables premium"""
    print("🚀 Initialisation des tables premium...")

    # Lire le fichier SQL
    sql_file = os.path.join(os.path.dirname(__file__), "CREATE_PREMIUM_TABLES.sql")

    if not os.path.exists(sql_file):
        print(f"❌ Fichier SQL non trouvé: {sql_file}")
        return False

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Se connecter à la base de données
    db_url = get_database_url()

    if not db_url:
        print("\n" + "="*80)
        print("⚠️  INSTRUCTIONS MANUELLES")
        print("="*80)
        print("\n1. Connectez-vous à votre dashboard Supabase:")
        print("   https://app.supabase.com/")
        print("\n2. Sélectionnez votre projet")
        print("\n3. Allez dans 'SQL Editor' dans le menu de gauche")
        print("\n4. Créez une nouvelle requête et collez le contenu du fichier:")
        print(f"   {sql_file}")
        print("\n5. Exécutez la requête")
        print("\n" + "="*80)
        return False

    try:
        print(f"📡 Connexion à Supabase...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print(f"⚙️  Exécution du script SQL...")
        cursor.execute(sql_content)

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Tables premium créées avec succès!")
        print("\nTables créées:")
        print("  - content_posts (Calendrier éditorial)")
        print("  - unified_messages (Boîte de réception unifiée)")
        print("  - reviews (Gestion des avis)")

        return True

    except psycopg2.Error as e:
        print(f"❌ Erreur lors de la création des tables:")
        print(f"   {str(e)}")
        print("\n⚠️  Veuillez exécuter le SQL manuellement (voir instructions ci-dessus)")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("INITIALISATION DES TABLES PREMIUM - DASHBOARDS 10/10")
    print("="*80 + "\n")

    success = init_tables()

    if success:
        print("\n✅ SUCCÈS! Les tables sont prêtes.")
        print("   Vous pouvez maintenant utiliser les dashboards premium.")
    else:
        print("\n⚠️  Veuillez créer les tables manuellement dans Supabase.")

    print("\n" + "="*80 + "\n")
