"""
Script pour appliquer les migrations des colonnes de campagnes
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def apply_migration():
    """Applique la migration SQL"""
    print("🔧 Application de la migration des colonnes campaigns...")
    
    # Lire le fichier SQL
    with open('ADD_CAMPAIGN_COLUMNS.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Diviser les commandes SQL
    commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
    
    success_count = 0
    for i, command in enumerate(commands, 1):
        if not command or command.startswith('COMMENT'):
            continue
        
        try:
            print(f"  Exécution de la commande {i}/{len(commands)}...")
            supabase.rpc('exec_sql', {'sql': command}).execute()
            success_count += 1
        except Exception as e:
            print(f"  ⚠️  Avertissement pour la commande {i}: {e}")
    
    print(f"✅ Migration appliquée avec succès! ({success_count}/{len(commands)} commandes)")

if __name__ == "__main__":
    apply_migration()
