#!/usr/bin/env python3
"""Vérifier les statuts autorisés pour payouts"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("🧪 Test des statuts payouts:")

test_statuses = ['pending', 'processing', 'completed', 'paid', 'cancelled', 'rejected', 'failed']

for status in test_statuses:
    try:
        data = {
            "influencer_id": "ae90dc37-c76f-45cc-ac65-51183d44fae5",
            "user_id": "ae90dc37-c76f-45cc-ac65-51183d44fae5",
            "amount": 0.01,
            "status": status,
            "currency": "EUR",
            "payment_method": "test"
        }
        result = supabase.table('payouts').insert(data).execute()
        payout_id = result.data[0]['id']
        supabase.table('payouts').delete().eq('id', payout_id).execute()
        print(f"✅ '{status}' - VALIDE")
    except Exception as e:
        if '23514' in str(e):
            print(f"❌ '{status}' - INTERDIT (CHECK constraint)")
        else:
            print(f"⚠️  '{status}' - Autre erreur: {str(e)[:80]}")
