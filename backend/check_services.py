#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier les services dans la base de données"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

def main():
    # Créer le client Supabase
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    print("=" * 60)
    print("VÉRIFICATION DES SERVICES DANS LA BASE DE DONNÉES")
    print("=" * 60)
    
    try:
        # Méthode 1: Count exact
        print("\n📊 Méthode 1: Count avec head=True")
        result_count = supabase.table('services').select('id', count='exact', head=True).execute()
        print(f"✅ Nombre total de services (count): {result_count.count}")
        
        # Méthode 2: Récupérer tous les services
        print("\n📊 Méthode 2: Select all")
        result_all = supabase.table('services').select('*').execute()
        services = result_all.data or []
        print(f"✅ Nombre de services récupérés: {len(services)}")
        
        if services:
            print("\n📋 Premiers services dans la base:")
            for i, service in enumerate(services[:5], 1):
                print(f"\n  Service {i}:")
                print(f"    - ID: {service.get('id', 'N/A')}")
                print(f"    - Nom: {service.get('nom', 'N/A')}")
                print(f"    - Type: {service.get('type', 'N/A')}")
                print(f"    - Tarif: {service.get('tarif', 'N/A')} MAD")
                print(f"    - Statut: {service.get('statut', 'N/A')}")
        else:
            print("\n⚠️  Aucun service trouvé dans la base de données")
            
        # Méthode 3: Vérifier la structure de la table
        print("\n📊 Méthode 3: Colonnes de la table")
        if services:
            print(f"✅ Colonnes disponibles: {list(services[0].keys())}")
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la récupération des services: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
