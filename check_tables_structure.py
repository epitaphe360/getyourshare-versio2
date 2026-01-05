import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv('backend/.env')

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("🔍 VÉRIFICATION DE LA STRUCTURE DES TABLES\n")

# Liste des tables à vérifier
tables = ['users', 'subscriptions', 'transactions', 'invoices', 'email_campaigns', 
          'shipments', 'conversations', 'events']

for table in tables:
    try:
        # Essayer de récupérer une ligne pour voir la structure
        result = supabase.table(table).select("*").limit(1).execute()
        
        if result.data:
            print(f"✅ Table '{table}' - Colonnes disponibles:")
            print(f"   {', '.join(result.data[0].keys())}\n")
        else:
            # Si pas de données, essayer juste de lire la structure
            result = supabase.table(table).select("*").limit(0).execute()
            print(f"⚠️  Table '{table}' existe mais est vide\n")
            
    except Exception as e:
        print(f"❌ Table '{table}': {str(e)}\n")
