#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse complète : où sont les services ?"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    print("=" * 70)
    print("ANALYSE COMPLÈTE: OÙ SONT LES SERVICES ?")
    print("=" * 70)
    
    # 1. Table services
    print("\n📊 1. TABLE SERVICES")
    services = supabase.table('services').select('*', count='exact').execute()
    print(f"   Nombre: {services.count}")
    
    # 2. Table leads
    print("\n📊 2. TABLE LEADS")
    leads = supabase.table('leads').select('*', count='exact').execute()
    print(f"   Nombre: {leads.count}")
    
    # 3. Table products - TOUS
    print("\n📊 3. TABLE PRODUCTS - TOUS")
    all_products = supabase.table('products').select('*').execute()
    print(f"   Total products: {len(all_products.data)}")
    
    # 4. Analyser les types dans products
    print("\n📊 4. ANALYSE DES TYPES DANS PRODUCTS")
    types_count = {}
    for p in all_products.data:
        ptype = p.get('type', 'no_type')
        types_count[ptype] = types_count.get(ptype, 0) + 1
    
    for ptype, count in types_count.items():
        print(f"   - type='{ptype}': {count} entrées")
    
    # 5. Afficher les produits de type 'service'
    services_in_products = [p for p in all_products.data if p.get('type') == 'service']
    print(f"\n📊 5. PRODUITS AVEC type='service': {len(services_in_products)}")
    
    if services_in_products:
        print("\n   📋 Liste des services:")
        for i, svc in enumerate(services_in_products[:10], 1):
            print(f"\n   Service {i}:")
            print(f"      - Nom: {svc.get('name')}")
            print(f"      - Prix: {svc.get('price')} MAD")
            print(f"      - Catégorie: {svc.get('category')}")
            print(f"      - Merchant: {svc.get('merchant_id')}")
    
    # 6. Afficher quelques produits normaux
    normal_products = [p for p in all_products.data if p.get('type') == 'product']
    print(f"\n📊 6. PRODUITS AVEC type='product': {len(normal_products)}")
    if normal_products:
        print(f"\n   📋 Exemples (premiers 3):")
        for i, prod in enumerate(normal_products[:3], 1):
            print(f"   {i}. {prod.get('name')} - {prod.get('price')} MAD")
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    
    if services_in_products:
        print(f"✅ TROUVÉ: {len(services_in_products)} services dans la table 'products'")
        print("   → Les services sont stockés dans 'products' avec type='service'")
        print("\n⚠️  PROBLÈME IDENTIFIÉ:")
        print("   Le dashboard compte la table 'services' (vide)")
        print("   mais devrait compter products WHERE type='service'")
    else:
        print("❌ Aucun service trouvé nulle part")
        print("   → Soit ils sont ailleurs, soit ils n'existent pas encore")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
