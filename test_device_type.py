#!/usr/bin/env python3
"""
Tester et ajouter device_type à tracking_events
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔧 Test de la colonne device_type...")
print("=" * 70)

# Récupérer un tracking_link_id valide
links = supabase.table('tracking_links').select('id').limit(1).execute()
if not links.data:
    print("❌ Aucun tracking_link trouvé")
    exit(1)

link_id = links.data[0]['id']

# Tenter d'insérer avec device_type
test_data = {
    "tracking_link_id": link_id,
    "event_type": "test_device_type",
    "ip_address": "127.0.0.1",
    "user_agent": "Test",
    "device_type": "mobile"
}

try:
    result = supabase.table('tracking_events').insert(test_data).execute()
    print("✅ device_type existe déjà!")
    print(f"📊 Colonnes: {list(result.data[0].keys())}")
    # Nettoyer
    supabase.table('tracking_events').delete().eq('id', result.data[0]['id']).execute()
except Exception as e:
    if 'Could not find' in str(e) and 'device_type' in str(e):
        print("⚠️  device_type n'existe pas")
        print("\n📋 SQL à exécuter dans Supabase:")
        print("ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS device_type TEXT;")
    else:
        print(f"❌ Erreur: {e}")

print("\n" + "=" * 70)
