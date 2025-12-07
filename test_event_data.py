#!/usr/bin/env python3
"""
Test event_data dans tracking_events
"""
import os
import json
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔧 Test de event_data...")

# Récupérer un link_id valide
links = supabase.table('tracking_links').select('id').limit(1).execute()
link_id = links.data[0]['id']

# Test avec event_data
test_data = {
    "tracking_link_id": link_id,
    "event_type": "test_event_data",
    "ip_address": "127.0.0.1",
    "user_agent": "Test",
    "event_data": json.dumps({"test": True, "session_id": "123"})
}

try:
    result = supabase.table('tracking_events').insert(test_data).execute()
    print("✅ event_data fonctionne!")
    print(f"Type de event_data: {type(result.data[0]['event_data'])}")
    print(f"Valeur: {result.data[0]['event_data']}")
    
    # Nettoyer
    supabase.table('tracking_events').delete().eq('id', result.data[0]['id']).execute()
    
    print("\n✅ Tous les tests réussis!")
    print("👉 Remplacer 'metadata' par 'event_data' dans le script")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
