import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Erreur: Variables d'environnement manquantes")
    sys.exit(1)

supabase: Client = create_client(url, key)

tables_to_check = [
    "transactions", "rate_limits", "email_campaigns", "sms_campaigns", 
    "product_collections", "wishlists", "shipments", "warehouses", 
    "coupons", "conversations", "events", "analytics_reports", 
    "support_tickets", "integrations", "subscriptions"
]

missing_tables = []
print("Vérification des tables...")

for table in tables_to_check:
    try:
        # On essaie de sélectionner 1 ligne, peu importe s'il y a des données
        supabase.table(table).select("*").limit(1).execute()
        print(f"✅ Table '{table}' existe")
    except Exception as e:
        print(f"❌ Table '{table}' inaccessible: {e}")
        missing_tables.append(table)

# Vérification des colonnes spécifiques dans users
print("\nVérification des colonnes users...")
try:
    # On essaie de sélectionner les colonnes spécifiques
    supabase.table("users").select("kyc_verified,kyc_verified_at").limit(1).execute()
    print("✅ Colonnes kyc_verified dans 'users' existent")
except Exception as e:
    print(f"❌ Colonnes kyc_verified manquantes dans 'users': {e}")
    missing_tables.append("users.kyc_verified")

if missing_tables:
    print(f"\n⚠️ Il manque {len(missing_tables)} tables/colonnes.")
    sys.exit(1)
else:
    print("\n🎉 TOUTES LES TABLES SONT PRÉSENTES !")
    sys.exit(0)
