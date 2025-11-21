import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Query pour obtenir TOUTES les foreign keys qui référencent users
query = """
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND ccu.table_name = 'users'
ORDER BY tc.table_name, kcu.column_name;
"""

try:
    result = supabase.rpc('exec_sql', {'sql': query}).execute()
    print("=== TOUTES LES FOREIGN KEYS VERS USERS ===\n")
    for row in result.data:
        print(f"Table: {row['table_name']}")
        print(f"  Colonne: {row['column_name']}")
        print(f"  Référence: {row['foreign_table_name']}.{row['foreign_column_name']}")
        print(f"  Contrainte: {row['constraint_name']}\n")
except Exception as e:
    print(f"Erreur: {e}")
    print("\nEssai avec méthode alternative...")
    
    # Liste manuelle basée sur les erreurs rencontrées
    tables_with_fk = [
        ("commissions", "sale_id", "sales.id"),
        ("commissions", "influencer_id", "users.id"),
        ("sales", "merchant_id", "users.id"),
        ("sales", "influencer_id", "users.id"),
        ("conversions", "merchant_id", "users.id"),
        ("invoices", "user_id", "users.id"),
        ("subscriptions", "user_id", "users.id"),
        ("leads", "commercial_id", "users.id"),
        ("leads", "merchant_id", "users.id"),
        ("messages", "sender_id", "users.id"),
        ("notifications", "user_id", "users.id"),
        ("user_gamification", "user_id", "users.id"),
        ("user_kyc_profile", "user_id", "users.id"),
        ("trust_scores", "user_id", "users.id"),
        ("merchant_deposits", "merchant_id", "users.id"),
        ("invitations", "campaign_id", "campaigns.id"),
        ("collaboration_requests", "campaign_id", "campaigns.id"),
    ]
    
    print("\n=== FOREIGN KEYS CONNUES ===\n")
    for table, column, ref in tables_with_fk:
        print(f"{table}.{column} → {ref}")
