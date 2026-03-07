#!/usr/bin/env python3
"""
Vérifier les conversions et les retraits de l'influenceur
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Analyse des conversions et retraits...")
print("=" * 70)

# Récupérer l'influenceur
inf = supabase.table('users').select('id, email, balance').eq('email', 'influenceur@test.com').execute()
if not inf.data:
    print("❌ Influenceur non trouvé")
    exit(1)

inf_id = inf.data[0]['id']
print(f"👤 Influenceur: {inf.data[0]['email']}")
print(f"   ID: {inf_id}")
print(f"   Balance: {inf.data[0]['balance']} EUR\n")

# Vérifier les conversions
convs = supabase.table('conversions').select('*').eq('influencer_id', inf_id).execute()
print(f"📊 Conversions (influencer_id = {inf_id}):")
for c in convs.data:
    print(f"   - {c['status']}: {c['commission_amount']} EUR (Order: {c.get('order_id', 'N/A')})")

total_completed = sum([c['commission_amount'] for c in convs.data if c['status'] == 'completed'])
print(f"\n💰 Total commissions completed: {total_completed} EUR")

# Vérifier les payouts
payouts = supabase.table('payouts').select('*').eq('user_id', inf_id).execute()
print(f"\n💸 Payouts (user_id = {inf_id}):")
for p in payouts.data:
    print(f"   - {p['status']}: {p['amount']} EUR")

total_payouts = sum([p['amount'] for p in payouts.data])
print(f"\n📤 Total payouts: {total_payouts} EUR")
print(f"✅ Solde disponible: {total_completed - total_payouts} EUR")

print("\n" + "=" * 70)
