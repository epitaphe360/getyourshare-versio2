#!/usr/bin/env python3
"""
Ajouter des données de test à tracking_events pour découvrir sa structure
"""
import os
from supabase import create_client, Client
from datetime import datetime

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Découverte de la structure tracking_events...")
print("=" * 70)

# Récupérer un tracking_link_id valide
links = supabase.table('tracking_links').select('id').limit(1).execute()
if not links.data:
    print("❌ Aucun tracking_link trouvé, impossible de tester")
    exit(1)

link_id = links.data[0]['id']
print(f"✅ Utilisation du tracking_link: {link_id}")

# Essayer différentes structures
structures = [
    {
        "tracking_link_id": link_id,
        "event_type": "click",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "tracking_link_id": link_id,
        "event_type": "click",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "tracking_link_id": link_id,
        "event_type": "click",
        "metadata": {"test": True}
    }
]

for i, test_data in enumerate(structures, 1):
    print(f"\nTentative {i}: Structure avec {list(test_data.keys())}")
    try:
        result = supabase.table('tracking_events').insert(test_data).execute()
        print(f"✅ Succès! Structure correcte trouvée")
        print(f"\n📊 Colonnes de tracking_events: {list(result.data[0].keys())}")
        print("\nStructure complète:")
        for col, val in result.data[0].items():
            print(f"  - {col}: {val} ({type(val).__name__})")
        
        # Nettoyer
        supabase.table('tracking_events').delete().eq('id', result.data[0]['id']).execute()
        break
    except Exception as e:
        print(f"❌ Échec: {e}")
        if 'Could not find' in str(e):
            import re
            match = re.search(r"'([^']+)' column", str(e))
            if match:
                print(f"💡 Colonne manquante: {match.group(1)}")

print("\n" + "=" * 70)
