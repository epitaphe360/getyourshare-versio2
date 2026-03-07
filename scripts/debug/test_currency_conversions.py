#!/usr/bin/env python3
"""
Vérifier et ajouter currency à conversions
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔧 Test de la colonne currency dans conversions...")
print("=" * 70)

# Récupérer un tracking_link_id valide
links = supabase.table('tracking_links').select('id').limit(1).execute()
if not links.data:
    print("❌ Aucun tracking_link trouvé")
    exit(1)

link_id = links.data[0]['id']

# Test avec currency
test_data = {
    "tracking_link_id": link_id,
    "status": "pending",
    "amount": 100.0,
    "currency": "EUR"
}

try:
    result = supabase.table('conversions').insert(test_data).execute()
    print("✅ currency existe déjà!")
    print(f"📊 Colonnes: {list(result.data[0].keys())}")
    # Nettoyer
    supabase.table('conversions').delete().eq('id', result.data[0]['id']).execute()
except Exception as e:
    if 'Could not find' in str(e) and 'currency' in str(e):
        print("⚠️  currency n'existe pas")
        print("\n📋 SQL à exécuter dans Supabase:")
        print("ALTER TABLE conversions ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';")
    else:
        print(f"❌ Erreur: {e}")

print("\n" + "=" * 70)
