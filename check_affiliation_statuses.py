#!/usr/bin/env python3
"""Vérifier les statuts autorisés pour affiliation_requests"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Get test IDs
users = supabase.table('users').select('id, email').limit(2).execute()
if len(users.data) < 2:
    print("❌ Pas assez d'utilisateurs")
    exit(1)

products = supabase.table('products').select('id').limit(1).execute()
if not products.data:
    print("❌ Pas de produits")
    exit(1)

inf_id = users.data[0]['id']
merch_id = users.data[1]['id']
prod_id = products.data[0]['id']

print("🧪 Test des statuts affiliation_requests:")

test_statuses = ['pending', 'approved', 'rejected', 'cancelled', 'under_review', 'active']

for status in test_statuses:
    try:
        data = {
            "influencer_id": inf_id,
            "merchant_id": merch_id,
            "product_id": prod_id,
            "status": status
        }
        result = supabase.table('affiliation_requests').insert(data).execute()
        req_id = result.data[0]['id']
        supabase.table('affiliation_requests').delete().eq('id', req_id).execute()
        print(f"✅ '{status}' - VALIDE")
    except Exception as e:
        if '23514' in str(e):
            print(f"❌ '{status}' - INTERDIT (CHECK constraint)")
        else:
            print(f"⚠️  '{status}' - Autre erreur: {str(e)[:100]}")
