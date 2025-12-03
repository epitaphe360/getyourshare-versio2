import os
import sys
import bcrypt
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

def reset_admin_password():
    email = "admin@getyourshare.com"
    new_password = "admin123"
    
    print(f"🔄 Réinitialisation du mot de passe pour {email}...")
    
    # Hasher le mot de passe
    password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    try:
        # Vérifier si l'utilisateur existe
        result = supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            print(f"❌ Erreur: L'utilisateur {email} n'existe pas!")
            return
            
        user_id = result.data[0]['id']
        print(f"✅ Utilisateur trouvé (ID: {user_id})")
        
        # Mettre à jour le mot de passe
        update_result = supabase.table("users").update({
            "password_hash": password_hash
        }).eq("id", user_id).execute()
        
        if update_result.data:
            print(f"✅ Mot de passe mis à jour avec succès pour {email}")
            print(f"🔑 Nouveau mot de passe: {new_password}")
        else:
            print("❌ Erreur lors de la mise à jour du mot de passe")
            
    except Exception as e:
        print(f"❌ Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    reset_admin_password()
