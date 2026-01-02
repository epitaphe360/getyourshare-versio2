import sys
import os
import time

# Add current directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

def execute_sql(sql: str, description: str):
    """Exécute une requête SQL via RPC et gère les erreurs."""
    try:
        print(f"⏳ {description}...")
        response = supabase.rpc('execute_sql', {'sql': sql}).execute()
        print(f"✅ {description} - Succès.")
        return True
    except Exception as e:
        print(f"❌ {description} - Erreur: {e}")
        return False

def main():
    print("\n🔧 Correction du schéma de base de données pour le rôle 'commercial'...\n")

    # 1. Ajouter la colonne commercial_id à la table leads
    sql_add_column = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'commercial_id') THEN
            ALTER TABLE leads ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE SET NULL;
            CREATE INDEX IF NOT EXISTS idx_leads_commercial_id ON leads(commercial_id);
        END IF;
    END $$;
    """
    execute_sql(sql_add_column, "Ajout de la colonne commercial_id à la table leads")

    # 2. Mettre à jour la contrainte de rôle sur la table users
    sql_update_role_check = """
    DO $$
    BEGIN
        ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
        ALTER TABLE users ADD CONSTRAINT users_role_check 
        CHECK (role IN ('admin', 'merchant', 'influencer', 'commercial', 'affiliate'));
    END $$;
    """
    execute_sql(sql_update_role_check, "Mise à jour de la contrainte users_role_check")

    print("\n🏁 Correction terminée.")

if __name__ == "__main__":
    main()
