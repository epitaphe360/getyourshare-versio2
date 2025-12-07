"""
Vérifier la structure de social_media_publications
"""
import os
import sys
import json

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

print("🔍 Vérification de social_media_publications...")
try:
    result = supabase.table('social_media_publications').select('*').limit(1).execute()
    if result.data:
        print("✅ Structure:")
        print(json.dumps(result.data[0], indent=2, default=str))
        print("\n📋 Colonnes:")
        for col in result.data[0].keys():
            print(f"  - {col}")
    else:
        print("⚠️  Table vide")
except Exception as e:
    print(f"❌ Erreur: {e}")
