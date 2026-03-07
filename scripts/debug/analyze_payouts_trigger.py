#!/usr/bin/env python3
"""
Découvrir la structure de payouts et comprendre le trigger
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Analyse de payouts...")
print("=" * 70)

# Structure de payouts
try:
    result = supabase.table('payouts').select('*').limit(1).execute()
    if result.data:
        print(f"📊 Colonnes payouts: {list(result.data[0].keys())}")
    else:
        print("⚠️  Table payouts vide")
except Exception as e:
    print(f"Erreur: {e}")

# Vérifier les commissions gagnées de l'influenceur
users = supabase.table('users').select('id, email, wallet_balance, role').eq('email', 'influenceur@test.com').execute()
if users.data:
    inf = users.data[0]
    print(f"\n👤 Influenceur:")
    print(f"   ID: {inf['id']}")
    print(f"   Balance: {inf.get('wallet_balance', 0)} EUR")
    
    # Vérifier les conversions complétées
    convs = supabase.table('conversions').select('commission_amount, status').eq('influencer_id', inf['id']).execute()
    total_commissions = sum([c['commission_amount'] for c in convs.data if c['status'] == 'completed'])
    print(f"   Commissions gagnées: {total_commissions} EUR")
    
    # Vérifier les payouts existants
    payouts = supabase.table('payouts').select('amount, status').eq('user_id', inf['id']).execute()
    total_payouts = sum([p['amount'] for p in payouts.data])
    print(f"   Retraits effectués: {total_payouts} EUR")
    print(f"   Solde disponible: {total_commissions - total_payouts} EUR")

print("\n" + "=" * 70)
