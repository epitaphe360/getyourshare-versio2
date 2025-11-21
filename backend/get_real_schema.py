"""
Récupère la structure RÉELLE de toutes les tables depuis Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def get_table_columns(table_name):
    """Récupère les colonnes réelles d'une table"""
    try:
        result = supabase.table(table_name).select('*').limit(1).execute()
        if result.data and len(result.data) > 0:
            return list(result.data[0].keys())
        else:
            # Table vide, essayer avec une erreur forcée
            return []
    except Exception as e:
        return []

tables = [
    'users',
    'campaigns', 
    'products',
    'commissions',
    'payouts',
    'conversations',
    'messages',
    'leads',
    'invoices',
    'subscriptions'
]

print("STRUCTURE RÉELLE DES TABLES:")
print("=" * 80)

for table in tables:
    columns = get_table_columns(table)
    print(f"\n{table.upper()}:")
    if columns:
        print(f"  Colonnes: {', '.join(columns)}")
    else:
        print(f"  ⚠️ Table vide ou inexistante")
