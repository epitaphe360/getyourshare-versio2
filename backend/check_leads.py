#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier les leads (services) dans la base de données"""

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
    print("VÉRIFICATION DES LEADS (SERVICES) DANS LA BD")
    print("=" * 60)
    
    try:
        # Count total
        print("\n📊 Comptage des leads")
        result_count = supabase.table('leads').select('id', count='exact', head=True).execute()
        print(f"✅ Nombre total de leads: {result_count.count}")
        
        # Récupérer tous les leads
        print("\n📊 Récupération des leads")
        result_all = supabase.table('leads').select('*').execute()
        leads = result_all.data or []
        print(f"✅ Nombre de leads récupérés: {len(leads)}")
        
        if leads:
            print(f"\n📋 Colonnes disponibles: {list(leads[0].keys())}")
            print("\n📋 Premiers leads dans la base:")
            for i, lead in enumerate(leads[:5], 1):
                print(f"\n  Lead {i}:")
                print(f"    - ID: {lead.get('id', 'N/A')}")
                print(f"    - Nom: {lead.get('nom', lead.get('name', 'N/A'))}")
                print(f"    - Type: {lead.get('type_service', lead.get('type', 'N/A'))}")
                print(f"    - Prix: {lead.get('prix', lead.get('price', 'N/A'))} MAD")
                print(f"    - Commercial ID: {lead.get('commercial_id', 'N/A')}")
                print(f"    - Statut: {lead.get('statut', lead.get('status', 'N/A'))}")
        else:
            print("\n⚠️  Aucun lead trouvé dans la base de données")
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la récupération des leads: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
