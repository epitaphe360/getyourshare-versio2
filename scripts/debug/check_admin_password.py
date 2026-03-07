import os
import sys
import bcrypt
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin courant au path pour les imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from supabase_client import supabase_admin

def check_admin_password():
    email = "admin@getyourshare.com"
    test_password = "admin123"
    
    print(f"🔍 Vérification du mot de passe pour {email}...")
    
    try:
        # Récupérer l'utilisateur
        result = supabase_admin.table("users").select("id, email, password_hash").eq("email", email).execute()
        
        if not result.data:
            print(f"❌ Erreur: L'utilisateur {email} n'existe pas!")
            return
            
        user = result.data[0]
        stored_hash = user['password_hash']
        
        print(f"\n✅ Utilisateur trouvé (ID: {user['id']})")
        print(f"📝 Hash actuel en base: {stored_hash[:50]}...")
        
        # Tester le mot de passe
        is_valid = bcrypt.checkpw(test_password.encode("utf-8"), stored_hash.encode("utf-8"))
        
        if is_valid:
            print(f"✅ Le mot de passe '{test_password}' est VALIDE!")
        else:
            print(f"❌ Le mot de passe '{test_password}' est INVALIDE!")
            print(f"\n🔄 Génération d'un nouveau hash...")
            
            # Générer un nouveau hash
            new_hash = bcrypt.hashpw(test_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            print(f"📝 Nouveau hash: {new_hash[:50]}...")
            
            # Mettre à jour
            update_result = supabase_admin.table("users").update({
                "password_hash": new_hash
            }).eq("id", user['id']).execute()
            
            if update_result.data:
                print(f"✅ Hash mis à jour avec succès!")
                
                # Vérifier à nouveau
                is_valid_now = bcrypt.checkpw(test_password.encode("utf-8"), new_hash.encode("utf-8"))
                print(f"✅ Vérification post-mise à jour: {'VALIDE' if is_valid_now else 'INVALIDE'}")
            else:
                print("❌ Erreur lors de la mise à jour")
            
    except Exception as e:
        print(f"❌ Une erreur est survenue: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin_password()
