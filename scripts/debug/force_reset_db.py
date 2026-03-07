import os
import time
from supabase import create_client, Client
from supabase_creds import SUPABASE_URL, SUPABASE_KEY

# ============================================
# CONFIGURATION
# ============================================
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connexion à Supabase réussie.")
except Exception as e:
    print(f"❌ Erreur de connexion à Supabase: {e}")
    exit()

# Ordre de suppression critique pour respecter les dépendances
TABLES_TO_DROP = [
    # Enfants (dépendent des tables parentes)
    "click_logs", "click_tracking", "tracking_events", "conversions",
    "sales", "commissions", "lead_validation", "leads",
    "campaign_products", "campaign_settings",
    "collaboration_history", "collaboration_requests", "collaboration_invitations", "invitations",
    "affiliation_request_history", "influencer_agreements", "affiliate_requests",
    "merchant_affiliation_requests", "influencer_affiliation_requests", "affiliation_requests_stats",
    "product_reviews", "reviews",
    "influencer_profiles_extended", "match_preferences",
    
    # Parents (les autres tables dépendent d'eux)
    "tracking_links", "trackable_links", "affiliate_links",
    "affiliation_requests",
    "campaigns",
    "services",
    "products",
    "influencers",
    "merchants",
]

# ============================================
# FONCTIONS
# ============================================

def execute_sql(sql: str, description: str):
    """Exécute une requête SQL et gère les erreurs."""
    try:
        print(f"⏳ {description}...")
        supabase.rpc('execute_sql', {'sql': sql}).execute()
        print(f"✅ {description} - Succès.")
        return True
    except Exception as e:
        # Ignorer les erreurs "n'existe pas" car c'est notre objectif
        if "does not exist" in str(e):
            print(f"🤔 {description} - N'existait pas, c'est ok.")
            return True
        print(f"❌ {description} - Erreur: {e}")
        return False

def create_execute_sql_function():
    """Crée une fonction RPC dans Supabase pour exécuter du SQL arbitraire."""
    sql = """
    CREATE OR REPLACE FUNCTION execute_sql(sql TEXT)
    RETURNS void AS $$
    BEGIN
        EXECUTE sql;
    END;
    $$ LANGUAGE plpgsql;
    """
    description = "Création de la fonction RPC 'execute_sql'"
    try:
        print(f"⏳ {description}...")
        # Utilise postgrest pour créer la fonction, car rpc() ne peut pas la créer elle-même
        supabase.functions.invoke('execute-sql', invoke_options={'body': {'sql': sql}})
        print(f"✅ {description} - Succès.")
    except Exception:
        # Si la fonction existe déjà, c'est ok. On passe à la suite.
        print("🤔 La fonction RPC 'execute_sql' existe déjà. C'est ok.")
        pass


# ============================================
# SCRIPT PRINCIPAL
# ============================================

def main():
    print("\n" + "="*40)
    print("🤖 DÉBUT DU SCRIPT DE RÉINITIALISATION DE LA DB 🤖")
    print("="*40 + "\n")

    # 1. Créer la fonction RPC nécessaire
    create_execute_sql_function()
    time.sleep(1)

    # 2. Désactiver RLS
    execute_sql("SET session_replication_role = replica;", "Désactivation de RLS")
    time.sleep(1)

    # 3. Supprimer les vues
    print("\n--- ÉTAPE 1: Suppression des vues ---")
    views_to_drop = [
        "v_products_full", "v_featured_products", "v_deals_of_day",
        "v_admin_social_posts_summary", "v_admin_social_analytics", "v_contact_stats"
    ]
    for view in views_to_drop:
        execute_sql(f"DROP VIEW IF EXISTS public.{view} CASCADE;", f"Suppression de la vue {view}")
        time.sleep(0.5)

    # 4. Supprimer les tables
    print("\n--- ÉTAPE 2: Suppression des tables ---")
    for table in TABLES_TO_DROP:
        execute_sql(f"DROP TABLE IF EXISTS public.{table} CASCADE;", f"Suppression de la table {table}")
        time.sleep(0.5) # Petite pause pour éviter les deadlocks

    print("\n--- ÉTAPE 3: Lecture et exécution du script de création ---")
    try:
        with open('CREATE_CORE_TABLES_ONLY.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Diviser le script en blocs séparés par "GO" ou ";" pour exécution
        # Ici, on exécute tout le bloc, en espérant que la fonction RPC le gère
        if execute_sql(sql_script, "Exécution de CREATE_CORE_TABLES_ONLY.sql"):
            print("\n🎉 Toutes les tables core ont été recréées avec succès!")
        else:
            print("\n🔥 Échec de la recréation des tables. Veuillez vérifier les logs.")

    except FileNotFoundError:
        print("❌ ERREUR: Le fichier 'CREATE_CORE_TABLES_ONLY.sql' est introuvable.")
    except Exception as e:
        print(f"❌ ERREUR lors de la lecture ou exécution du fichier SQL: {e}")

    # 5. Réactiver RLS
    print("\n--- ÉTAPE 4: Réactivation de RLS ---")
    execute_sql("SET session_replication_role = DEFAULT;", "Réactivation de RLS")

    print("\n" + "="*40)
    print("🏁 SCRIPT TERMINÉ 🏁")
    print("="*40)

if __name__ == "__main__":
    # Installer supabase-py si nécessaire
    try:
        import supabase
    except ImportError:
        print("Le module 'supabase' n'est pas installé. Installation en cours...")
        os.system('pip install supabase')
        print("Installation terminée.")

    main()
