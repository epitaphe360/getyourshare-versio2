#!/usr/bin/env python3
"""
Découvrir les statuts valides pour conversions
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Test des statuts conversions...")
print("=" * 70)

# Récupérer des IDs valides
links = supabase.table('tracking_links').select('id, influencer_id, merchant_id, product_id').limit(1).execute()
link = links.data[0]

# Tester différents statuts
statuts_a_tester = ["paid", "validated", "confirmed", "completed", "approved", "pending", "cancelled"]

for status in statuts_a_tester:
    test_data = {
        "tracking_link_id": link['id'],
        "influencer_id": link['influencer_id'],
        "merchant_id": link['merchant_id'],
        "product_id": link['product_id'],
        "sale_amount": 100.0,
        "commission_amount": 10.0,
        "status": status
    }
    
    try:
        result = supabase.table('conversions').insert(test_data).execute()
        print(f"✅ '{status}' - VALIDE")
        # Nettoyer
        supabase.table('conversions').delete().eq('id', result.data[0]['id']).execute()
    except Exception as e:
        if 'check constraint' in str(e).lower():
            print(f"❌ '{status}' - INVALIDE (contrainte CHECK)")
        else:
            print(f"⚠️  '{status}' - Erreur: {str(e)[:80]}")

print("\n" + "=" * 70)
