#!/usr/bin/env python
"""
Test de connexion à Supabase
Vérifie que la configuration est correcte et que les données sont accessibles
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")
anon_key = os.getenv("SUPABASE_ANON_KEY")
key = service_key or anon_key

print("="*60)
print("🔍 VÉRIFICATION SUPABASE")
print("="*60)
print(f"URL: {url}")
print(f"Service Key définie: {bool(service_key)}")
print(f"Anon Key définie: {bool(anon_key)}")
print(f"Clé utilisée: {'SERVICE_KEY' if service_key else 'ANON_KEY'}")

try:
    supabase = create_client(url, key)
    print("\n✅ Client Supabase créé avec succès")
    
    # Tester l'accès à plusieurs tables
    tables = ["users", "products", "merchants", "influencers"]
    
    for table_name in tables:
        try:
            response = supabase.table(table_name).select("count", count="exact").execute()
            count = response.count if response.count is not None else "?"
            print(f"   ✅ Table '{table_name}': {count} enregistrements")
        except Exception as table_error:
            print(f"   ⚠️  Table '{table_name}': {type(table_error).__name__}")
    
    print("\n" + "="*60)
    print("✅ Configuration Supabase valide!")
    print("="*60)
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Erreur: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print("\n" + "="*60)
    print("❌ Problème de connexion à Supabase")
    print("="*60)
    import traceback
    print("\nDétail de l'erreur:")
    traceback.print_exc()
    sys.exit(1)
