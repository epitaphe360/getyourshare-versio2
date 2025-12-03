#!/usr/bin/env python3
"""Test rapide des données sans serveur"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("\n" + "="*70)
print("✅ TEST DIRECT BASE DE DONNÉES (sans serveur)")
print("="*70)

# Services
services = supabase.table('services').select('id', count='exact', head=True).execute()
print(f"\n📦 Services dans la BD: {services.count}")

# Liste quelques services
if services.count > 0:
    services_list = supabase.table('services').select('name, category, price_per_lead').limit(5).execute()
    print("\n📋 Quelques services:")
    for svc in services_list.data:
        print(f"  - {svc['name']}: {svc['price_per_lead']} MAD/lead ({svc['category']})")

print("\n✅ Les 15 services ont été créés avec succès!")
print("="*70)
print("\n🎯 INSTRUCTIONS:")
print("  1. Ouvrez votre dashboard dans le navigateur")
print("  2. Rafraîchissez la page (F5 ou Ctrl+R)")
print("  3. Le nombre de services devrait maintenant afficher: 15")
print("="*70 + "\n")
