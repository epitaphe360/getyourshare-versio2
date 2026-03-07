#!/usr/bin/env python3
"""
Vérifier et ajouter device_type à tracking_events
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔧 Vérification de TOUTES les colonnes tracking_events...")
print("=" * 70)

# Récupérer un link_id valide
links = supabase.table('tracking_links').select('id').limit(1).execute()
link_id = links.data[0]['id']

# Test complet avec toutes les colonnes
test_data = {
    "tracking_link_id": link_id,
    "event_type": "test_complet",
    "ip_address": "127.0.0.1",
    "user_agent": "Test Agent",
    "browser": "Chrome",
    "device": "Desktop",
    "device_type": "desktop",
    "country": "Test",
    "city": "Test City",
    "referrer": "https://test.com"
}

print(f"\n📋 Test avec colonnes: {list(test_data.keys())}")

try:
    result = supabase.table('tracking_events').insert(test_data).execute()
    print("\n✅ SUCCÈS! Toutes les colonnes existent!")
    print(f"📊 Colonnes dans la table: {list(result.data[0].keys())}")
    
    # Nettoyer
    supabase.table('tracking_events').delete().eq('id', result.data[0]['id']).execute()
    print("\n🎉 tracking_events est prêt pour l'automation!")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    if 'Could not find' in str(e):
        import re
        match = re.search(r"'([^']+)' column", str(e))
        if match:
            missing_col = match.group(1)
            print(f"\n💡 Colonne manquante: {missing_col}")
            print("\n📋 Exécutez ce SQL dans Supabase:")
            print(f"ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS {missing_col} TEXT;")

print("\n" + "=" * 70)
