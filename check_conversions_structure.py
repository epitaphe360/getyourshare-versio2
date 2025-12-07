#!/usr/bin/env python3
"""
Découvrir la structure de conversions
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("🔍 Découverte de la structure conversions...")
print("=" * 70)

try:
    # Tenter de récupérer un enregistrement
    result = supabase.table('conversions').select('*').limit(1).execute()
    
    if result.data and len(result.data) > 0:
        print(f"✅ Table conversions avec {len(result.data[0])} colonnes:")
        print(f"\n📊 Colonnes: {list(result.data[0].keys())}")
    else:
        print("⚠️  Table conversions vide")
        print("\nTentative d'insertion test pour découvrir la structure...")
        
        # Récupérer un tracking_link_id valide
        links = supabase.table('tracking_links').select('id, influencer_id, merchant_id, product_id').limit(1).execute()
        if not links.data:
            print("❌ Aucun tracking_link trouvé")
            exit(1)
        
        link = links.data[0]
        
        # Essayer différentes structures
        structures = [
            {
                "tracking_link_id": link['id'],
                "status": "pending"
            },
            {
                "tracking_link_id": link['id'],
                "influencer_id": link['influencer_id'],
                "merchant_id": link['merchant_id'],
                "product_id": link['product_id'],
                "status": "pending"
            }
        ]
        
        for i, test_data in enumerate(structures, 1):
            print(f"\nTentative {i}: {list(test_data.keys())}")
            try:
                result = supabase.table('conversions').insert(test_data).execute()
                print(f"✅ Succès!")
                print(f"\n📊 Colonnes: {list(result.data[0].keys())}")
                # Nettoyer
                supabase.table('conversions').delete().eq('id', result.data[0]['id']).execute()
                break
            except Exception as e:
                print(f"❌ Échec: {e}")

except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 70)
