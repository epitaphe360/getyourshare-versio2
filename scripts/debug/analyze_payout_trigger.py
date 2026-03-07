#!/usr/bin/env python3
"""
Analyser le trigger de validation des payouts
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Analyse du trigger payouts...")
print("=" * 70)

# Test d'insertion avec différentes configurations
inf = supabase.table('users').select('id, email, balance').eq('email', 'influenceur@test.com').execute()
if not inf.data:
    print("❌ Influenceur non trouvé")
    exit(1)

inf_id = inf.data[0]['id']
print(f"👤 Influenceur: {inf_id}")
print(f"   Balance: {inf.data[0]['balance']} EUR\n")

# Vérifier les conversions
convs = supabase.table('conversions').select('status, commission_amount, influencer_id').eq('influencer_id', inf_id).execute()
print(f"📊 Conversions pour influencer_id={inf_id}:")
total_completed = 0
for c in convs.data:
    print(f"   - Status: {c['status']}, Commission: {c['commission_amount']} EUR")
    if c['status'] == 'completed':
        total_completed += c['commission_amount']

print(f"\n💰 Total commissions completed: {total_completed} EUR")

# Vérifier les payouts existants
payouts = supabase.table('payouts').select('amount, status, influencer_id, user_id').eq('influencer_id', inf_id).execute()
print(f"\n📤 Payouts existants pour influencer_id={inf_id}:")
total_payouts = 0
for p in payouts.data:
    print(f"   - Amount: {p['amount']}, Status: {p['status']}")
    total_payouts += p['amount']

print(f"   Total: {total_payouts} EUR")
print(f"\n✅ Solde disponible théorique: {total_completed - total_payouts} EUR")

# Test d'insertion avec status='pending' au lieu de 'completed'
print("\n🧪 Test 1: Payout avec status='pending'...")
test1_data = {
    "influencer_id": inf_id,
    "user_id": inf_id,
    "amount": 50.00,
    "status": "pending",  # Essayer pending
    "currency": "EUR",
    "payment_method": "bank_transfer"
}

try:
    result = supabase.table('payouts').insert(test1_data).execute()
    print("✅ Succès avec status='pending'!")
    print(f"   ID: {result.data[0]['id']}")
    # Nettoyer
    supabase.table('payouts').delete().eq('id', result.data[0]['id']).execute()
except Exception as e:
    print(f"❌ Échec: {str(e)[:200]}")

# Test 2: Payout avec montant plus petit
print("\n🧪 Test 2: Payout de 10 EUR avec status='completed'...")
test2_data = {
    "influencer_id": inf_id,
    "user_id": inf_id,
    "amount": 10.00,
    "status": "completed",
    "currency": "EUR",
    "payment_method": "bank_transfer"
}

try:
    result = supabase.table('payouts').insert(test2_data).execute()
    print("✅ Succès avec 10 EUR!")
    # Nettoyer
    supabase.table('payouts').delete().eq('id', result.data[0]['id']).execute()
except Exception as e:
    print(f"❌ Échec: {str(e)[:200]}")

# Test 3: Sans status (défaut)
print("\n🧪 Test 3: Payout sans status (défaut DB)...")
test3_data = {
    "influencer_id": inf_id,
    "user_id": inf_id,
    "amount": 50.00,
    "currency": "EUR",
    "payment_method": "bank_transfer"
}

try:
    result = supabase.table('payouts').insert(test3_data).execute()
    print(f"✅ Succès! Status par défaut: {result.data[0]['status']}")
    # Nettoyer
    supabase.table('payouts').delete().eq('id', result.data[0]['id']).execute()
except Exception as e:
    print(f"❌ Échec: {str(e)[:200]}")

print("\n" + "=" * 70)
print("\n💡 DIAGNOSTIC:")
print("   Le trigger vérifie probablement:")
print("   - Les conversions avec status='completed'")
print("   - Les payouts avec status='completed' ou 'processed'")
print("   - Il faut créer le payout avec status='pending' puis le valider")
