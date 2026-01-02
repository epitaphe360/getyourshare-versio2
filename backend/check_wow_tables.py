import os
from dotenv import load_dotenv
from supabase_client import get_supabase_client

load_dotenv()

def check_tables():
    supabase = get_supabase_client()
    tables = [
        'referral_codes',
        'referrals',
        'referral_rewards',
        'referral_earnings',
        'product_recommendations',
        'ai_generated_content',
        'live_shopping_events'
    ]

    print("🔍 Vérification des tables 'Wow Features' dans Supabase...\n")
    
    all_exist = True
    for table in tables:
        try:
            # Try to select 1 row, just to check if table exists
            # If table doesn't exist, Supabase API usually returns an error
            response = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ Table '{table}' existe.")
        except Exception as e:
            print(f"❌ Table '{table}' MANQUANTE ou erreur: {e}")
            all_exist = False

    print("\n" + "-"*50)
    if all_exist:
        print("🎉 Toutes les tables sont présentes ! Les fonctionnalités devraient fonctionner.")
    else:
        print("⚠️  Certaines tables sont manquantes.")
        print("👉 Veuillez exécuter le script SQL 'backend/sql/create_wow_features_tables.sql' dans Supabase SQL Editor.")

if __name__ == "__main__":
    check_tables()
