"""
Réinitialiser les mots de passe de tous les comptes de test à Test123!
"""
import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Générer le hash pour Test123!
password = "Test123!"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Liste des comptes à mettre à jour
accounts = [
    "influencer1@fashion.com",
    "influencer2@tech.com", 
    "influencer3@lifestyle.com",
    "influencer4@fitness.com",
    "influencer5@food.com",
    "merchant1@fashionstore.com",
    "merchant2@techgadgets.com",
    "merchant3@beautyparis.com",
    "merchant4@sportshop.com",
    "merchant5@fooddelights.com",
    "commercial1@getyourshare.com",
    "commercial2@getyourshare.com",
    "commercial3@getyourshare.com",
]

print("=" * 70)
print("RÉINITIALISATION DES MOTS DE PASSE À Test123!")
print("=" * 70)

for email in accounts:
    try:
        response = supabase.table("users").update({
            "password_hash": hashed
        }).eq("email", email).execute()
        
        if response.data:
            print(f"✓ {email}")
        else:
            print(f"✗ {email} - non trouvé")
    except Exception as e:
        print(f"✗ {email} - Erreur: {str(e)}")

print("\n" + "=" * 70)
print("TERMINÉ! Mot de passe pour tous: Test123!")
print("=" * 70)
