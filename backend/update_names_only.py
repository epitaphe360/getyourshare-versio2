"""
Script pour mettre à jour uniquement full_name dans users
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

updates = [
    ("influencer1@fashion.com", "Sarah El Fassi"),
    ("influencer2@food.com", "Karim Benali"),
    ("influencer3@tech.com", "Amine Ziani"),
    ("influencer4@travel.com", "Leila Amrani"),
    ("influencer5@food.com", "Youssef Alami")
]

print("=" * 70)
print("MISE À JOUR DES NOMS COMPLETS")
print("=" * 70)

for email, full_name in updates:
    try:
        response = supabase.table("users").update({
            "full_name": full_name
        }).eq("email", email).execute()
        
        if response.data:
            print(f"✓ {email} → {full_name}")
        else:
            print(f"✗ {email} non trouvé")
            
    except Exception as e:
        print(f"✗ Erreur pour {email}: {str(e)}")

print("\n" + "=" * 70)
print("TERMINÉ!")
print("=" * 70)
