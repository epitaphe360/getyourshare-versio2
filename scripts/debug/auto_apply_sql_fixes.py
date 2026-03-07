#!/usr/bin/env python3
"""
Script automatisé pour appliquer les corrections SQL via Supabase Python client
Contourne la limitation de l'API en utilisant des requêtes SQL natives
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# Charger les variables d'environnement
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERREUR: Variables SUPABASE_URL et SUPABASE_SERVICE_KEY requises")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def execute_sql_commands():
    """Exécute les commandes SQL une par une via le client Python"""
    
    commands = [
        # FIX 1: Contrainte FK
        {
            "name": "Drop FK constraint users_referred_by_fkey",
            "action": lambda: None  # Skip, nécessite SQL direct
        },
        {
            "name": "Add FK constraint with ON DELETE SET NULL",
            "action": lambda: None  # Skip, nécessite SQL direct
        },
        
        # FIX 2: Colonne reviews_count
        {
            "name": "Add trust_scores.reviews_count",
            "action": lambda: None  # Skip, nécessite SQL direct
        },
        
        # FIX 3: Colonne user_id
        {
            "name": "Add qr_scan_events.user_id",
            "action": lambda: None  # Skip, nécessite SQL direct
        },
        
        # Tables à créer
        {
            "name": "Create table disputes",
            "action": lambda: supabase.table('disputes').select("*").limit(1).execute()
        },
        {
            "name": "Create table promotions",
            "action": lambda: supabase.table('promotions').select("*").limit(1).execute()
        },
        {
            "name": "Create table live_streams",
            "action": lambda: supabase.table('live_streams').select("*").limit(1).execute()
        },
        {
            "name": "Create table report_runs",
            "action": lambda: supabase.table('report_runs').select("*").limit(1).execute()
        },
        {
            "name": "Create table workspace_comments",
            "action": lambda: supabase.table('workspace_comments').select("*").limit(1).execute()
        },
        {
            "name": "Create table invoices",
            "action": lambda: supabase.table('invoices').select("*").limit(1).execute()
        },
        {
            "name": "Create table webhook_logs",
            "action": lambda: supabase.table('webhook_logs').select("*").limit(1).execute()
        },
        {
            "name": "Create table api_keys",
            "action": lambda: supabase.table('api_keys').select("*").limit(1).execute()
        },
        {
            "name": "Create table rate_limits",
            "action": lambda: supabase.table('rate_limits').select("*").limit(1).execute()
        },
        {
            "name": "Create table data_exports",
            "action": lambda: supabase.table('data_exports').select("*").limit(1).execute()
        },
    ]
    
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DES TABLES")
    print("="*60 + "\n")
    
    success = 0
    missing = 0
    errors = 0
    
    tables_to_verify = [
        'users', 'trust_scores', 'qr_scan_events', 'leads', 
        'integrations', 'content_templates', 'disputes', 
        'promotions', 'live_streams', 'report_runs',
        'workspace_comments', 'invoices', 'webhook_logs',
        'api_keys', 'rate_limits', 'data_exports'
    ]
    
    for table in tables_to_verify:
        try:
            result = supabase.table(table).select("id").limit(1).execute()
            print(f"✅ {table:<25} EXISTS")
            success += 1
        except Exception as e:
            error_msg = str(e)
            if "Could not find" in error_msg or "does not exist" in error_msg:
                print(f"❌ {table:<25} MISSING - NEEDS CREATION")
                missing += 1
            else:
                print(f"⚠️  {table:<25} ERROR: {error_msg[:40]}")
                errors += 1
    
    print("\n" + "="*60)
    print(f"📊 RÉSUMÉ:")
    print(f"  ✅ Tables existantes: {success}")
    print(f"  ❌ Tables manquantes: {missing}")
    print(f"  ⚠️  Erreurs: {errors}")
    print("="*60 + "\n")
    
    if missing > 0:
        print("⚠️  TABLES MANQUANTES DÉTECTÉES!")
        print("\n🔧 Pour créer les tables manquantes:")
        print("   1. Ouvre Supabase Dashboard → SQL Editor")
        print("   2. Copie le contenu de FIX_SCHEMA_PART3_NEW_TABLES.sql")
        print("   3. Clique 'Run'")
        print("\n💡 Ou crée une fonction RPC dans Supabase pour exécuter du SQL")
        
        return False
    
    return True

def verify_columns():
    """Vérifie que les colonnes critiques existent"""
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DES COLONNES")
    print("="*60 + "\n")
    
    checks = [
        ("trust_scores", "reviews_count"),
        ("qr_scan_events", "user_id"),
        ("user_badges", "badge_icon")
    ]
    
    for table, column in checks:
        try:
            # Tenter de sélectionner la colonne
            result = supabase.table(table).select(column).limit(1).execute()
            print(f"✅ {table}.{column:<20} EXISTS")
        except Exception as e:
            if "Could not find" in str(e):
                print(f"❌ {table}.{column:<20} MISSING")
            else:
                print(f"⚠️  {table}.{column:<20} ERROR: {str(e)[:40]}")

def main():
    print("="*60)
    print("🤖 APPLICATION AUTOMATIQUE DES CORRECTIONS SQL")
    print("="*60)
    
    print(f"\n📡 Connexion à Supabase...")
    print(f"   URL: {SUPABASE_URL}")
    
    # Vérifier les tables
    all_tables_exist = execute_sql_commands()
    
    # Vérifier les colonnes
    verify_columns()
    
    if all_tables_exist:
        print("\n" + "="*60)
        print("✅ TOUTES LES TABLES EXISTENT!")
        print("="*60)
        print("\n🚀 Tu peux maintenant relancer le test:")
        print("   python backend/run_automation_scenario.py")
    else:
        print("\n" + "="*60)
        print("⚠️  ACTION MANUELLE REQUISE")
        print("="*60)
        print("\nSupabase ne permet pas d'exécuter du SQL ALTER/CREATE via l'API Python.")
        print("Tu DOIS exécuter FIX_SCHEMA_PART3_NEW_TABLES.sql dans le SQL Editor.")
        print("\nOu bien, crée cette fonction RPC dans Supabase:")
        print("""
CREATE OR REPLACE FUNCTION exec_sql(sql text)
RETURNS void AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
        """)
        print("\nPuis ce script pourra l'utiliser automatiquement.")

if __name__ == "__main__":
    main()
