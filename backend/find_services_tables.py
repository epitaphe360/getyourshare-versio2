#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour chercher des tables liées aux services"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

def main():
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    print("=" * 60)
    print("RECHERCHE DE TABLES LIÉES AUX SERVICES")
    print("=" * 60)
    
    # Tables possibles à vérifier
    possible_tables = [
        'services',
        'service',
        'leads_services',
        'commercial_services',
        'marketplace_services',
        'products',  # Peut-être que les services sont dans products
    ]
    
    for table_name in possible_tables:
        try:
            print(f"\n🔍 Vérification de la table: {table_name}")
            result = supabase.table(table_name).select('*', count='exact').limit(5).execute()
            count = result.count if hasattr(result, 'count') else len(result.data or [])
            
            if count > 0:
                print(f"  ✅ {count} enregistrements trouvés")
                if result.data:
                    print(f"  📋 Colonnes: {list(result.data[0].keys())}")
                    print(f"  📝 Premier enregistrement: {result.data[0]}")
            else:
                print(f"  ⚠️  Aucun enregistrement")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)[:100]}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
