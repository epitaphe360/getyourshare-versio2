"""
Script pour ajouter des données de test dans les tables vides
et corriger les structures manquantes
"""
import os
import sys
import json
from datetime import datetime, timedelta
import uuid

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

def add_test_data():
    print("🔧 AJOUT DE DONNÉES DE TEST DANS LES TABLES VIDES")
    print("=" * 60)
    
    # 1. Vérifier social_media_publications
    print("\n📱 1. SOCIAL MEDIA PUBLICATIONS")
    print("-" * 60)
    
    try:
        result = supabase.table('social_media_publications').select('*').limit(1).execute()
        
        if not result.data:
            print("⚠️  Table vide - tentative d'ajout de données test...")
            
            # Récupérer des utilisateurs et produits existants
            users = supabase.table('users').select('id, role').eq('role', 'influencer').limit(2).execute()
            products = supabase.table('products').select('id').limit(2).execute()
            
            if users.data and products.data:
                test_pubs = []
                
                # Essayer différentes structures possibles
                structures_to_try = [
                    # Structure 1: user_id + product_id
                    {
                        "user_id": users.data[0]['id'],
                        "product_id": products.data[0]['id'],
                        "platform": "instagram",
                        "status": "approved",
                        "created_at": datetime.utcnow().isoformat()
                    },
                    # Structure 2: influencer_id + product_id
                    {
                        "influencer_id": users.data[0]['id'],
                        "product_id": products.data[0]['id'],
                        "platform": "instagram",
                        "status": "approved",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ]
                
                success = False
                for i, pub_data in enumerate(structures_to_try, 1):
                    try:
                        print(f"\n   Tentative {i}: Structure avec {list(pub_data.keys())}")
                        res = supabase.table('social_media_publications').insert(pub_data).execute()
                        print(f"   ✅ Succès! Structure correcte trouvée")
                        print(f"   Colonnes: {list(res.data[0].keys())}")
                        success = True
                        break
                    except Exception as e:
                        error_msg = str(e)
                        print(f"   ❌ Échec: {error_msg[:100]}")
                        
                        # Extraire la colonne manquante de l'erreur
                        if "Could not find the" in error_msg and "column" in error_msg:
                            import re
                            match = re.search(r"'(\w+)' column", error_msg)
                            if match:
                                missing_col = match.group(1)
                                print(f"   💡 Colonne manquante: {missing_col}")
                
                if not success:
                    print("\n   ⚠️  Impossible de déterminer la structure automatiquement")
                    print("   📋 Vérification manuelle requise dans Supabase Dashboard")
            else:
                print("   ⚠️  Pas assez de données (users/products) pour créer des publications test")
        else:
            print("✅ Table contient déjà des données")
            print(f"   Colonnes disponibles: {list(result.data[0].keys())}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # 2. Vérifier autres tables critiques
    tables_to_check = [
        'tracking_links',
        'conversions', 
        'transactions',
        'campaigns',
        'leads',
        'trust_scores',
        'payment_accounts'
    ]
    
    print("\n\n🔍 2. VÉRIFICATION AUTRES TABLES")
    print("-" * 60)
    
    for table_name in tables_to_check:
        try:
            result = supabase.table(table_name).select('*').limit(1).execute()
            status = "✅ Contient des données" if result.data else "⚠️  Table vide"
            print(f"{table_name:30} {status}")
            
            if result.data:
                print(f"   Colonnes: {', '.join(list(result.data[0].keys())[:8])}...")
        except Exception as e:
            print(f"{table_name:30} ❌ Erreur: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("✅ Vérification terminée!")
    print("=" * 60)

if __name__ == "__main__":
    add_test_data()
