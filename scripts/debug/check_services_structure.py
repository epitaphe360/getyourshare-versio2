"""
Script pour vérifier la structure de la table services
"""
import os
import sys
import json

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

def check_services_structure():
    print("🔍 Vérification de la structure de la table services...")
    print("-" * 60)
    
    try:
        # Essayer de récupérer un service pour voir les colonnes
        result = supabase.table('services').select('*').limit(1).execute()
        
        if result.data:
            print("✅ Structure actuelle de la table services:")
            print(json.dumps(result.data[0], indent=2, default=str))
            print("\n📋 Colonnes disponibles:")
            for col in result.data[0].keys():
                print(f"  - {col}")
        else:
            print("⚠️  Aucun service trouvé, création d'un service test...")
            
            # Essayer différentes combinaisons de colonnes
            test_data = {
                "merchant_id": "00000000-0000-0000-0000-000000000000",
                "name": "Test Service",
                "description": "Service de test"
            }
            
            print("\n🧪 Test avec colonnes basiques:", list(test_data.keys()))
            try:
                result = supabase.table('services').insert(test_data).execute()
                print("✅ Insertion réussie!")
                print("Structure créée:", json.dumps(result.data[0], indent=2, default=str))
                
                # Supprimer le test
                supabase.table('services').delete().eq('name', 'Test Service').execute()
                print("🗑️  Service test supprimé")
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
                
                # Extraire les colonnes de l'erreur
                error_msg = str(e)
                if "Could not find the" in error_msg and "column" in error_msg:
                    print("\n💡 Suggestions:")
                    print("La table services peut avoir une structure différente.")
                    print("Colonnes probables: id, merchant_id, name, description, created_at, updated_at")
                    
    except Exception as e:
        print(f"❌ Erreur globale: {str(e)}")

if __name__ == "__main__":
    check_services_structure()
