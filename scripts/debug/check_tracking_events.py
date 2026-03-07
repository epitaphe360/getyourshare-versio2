#!/usr/bin/env python3
"""
Vérifier la structure de la table tracking_events
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Vérification de la structure de tracking_events...")
print("=" * 70)

try:
    # Tenter de récupérer un enregistrement pour voir la structure
    result = supabase.table('tracking_events').select('*').limit(1).execute()
    
    if result.data and len(result.data) > 0:
        print(f"✅ Table tracking_events existe avec {len(result.data[0])} colonnes:")
        print(f"\n📊 Colonnes: {list(result.data[0].keys())}")
        print("\nStructure détaillée:")
        for col, val in result.data[0].items():
            print(f"  - {col}: {type(val).__name__}")
    else:
        print("⚠️  Table tracking_events vide")
        print("Tentative d'insertion test pour découvrir la structure...")
        
        # Test avec structure minimale
        test_data = {
            "tracking_link_id": "00000000-0000-0000-0000-000000000000",
            "event_type": "test",
            "created_at": "2024-12-06T00:00:00"
        }
        
        try:
            result = supabase.table('tracking_events').insert(test_data).execute()
            print(f"✅ Structure minimale acceptée: {list(test_data.keys())}")
            # Nettoyer
            if result.data:
                supabase.table('tracking_events').delete().eq('event_type', 'test').execute()
        except Exception as e:
            print(f"❌ Erreur: {e}")
            if 'Could not find' in str(e):
                import re
                match = re.search(r"'([^']+)' column", str(e))
                if match:
                    print(f"💡 Colonne manquante: {match.group(1)}")

except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 70)
