#!/usr/bin/env python3
"""
Tester et ajouter colonnes à conversions
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔧 Test des colonnes conversions...")
print("=" * 70)

# Récupérer des IDs valides
links = supabase.table('tracking_links').select('id, influencer_id, merchant_id, product_id').limit(1).execute()
if not links.data:
    print("❌ Aucun tracking_link trouvé")
    exit(1)

link = links.data[0]
users = supabase.table('users').select('id').eq('role', 'influencer').limit(1).execute()
user_id = users.data[0]['id'] if users.data else link['influencer_id']

# Test avec toutes les colonnes
test_data = {
    "tracking_link_id": link['id'],
    "influencer_id": link['influencer_id'],
    "user_id": user_id,
    "merchant_id": link['merchant_id'],
    "product_id": link['product_id'],
    "order_id": "TEST-ORDER-123",
    "sale_amount": 100.0,
    "commission_amount": 10.0,
    "platform_fee": 2.0,
    "status": "pending",
    "currency": "EUR",
    "payment_method": "credit_card",
    "customer_email": "test@test.com"
}

print(f"\n📋 Test avec colonnes: {list(test_data.keys())}")

try:
    result = supabase.table('conversions').insert(test_data).execute()
    print("\n✅ SUCCÈS! Toutes les colonnes existent!")
    print(f"📊 Colonnes dans la table: {list(result.data[0].keys())}")
    
    # Nettoyer
    supabase.table('conversions').delete().eq('id', result.data[0]['id']).execute()
    print("\n🎉 conversions est prêt pour l'automation!")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    if 'Could not find' in str(e):
        import re
        match = re.search(r"'([^']+)' column", str(e))
        if match:
            missing_col = match.group(1)
            print(f"\n💡 Colonne manquante: {missing_col}")
            print("\n📋 Exécutez ce SQL dans Supabase:")
            print(f"ALTER TABLE conversions ADD COLUMN IF NOT EXISTS {missing_col} TEXT;")

print("\n" + "=" * 70)
