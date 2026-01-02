"""
Script simplifié pour mettre à jour uniquement full_name et username
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Données simples à mettre à jour
updates = [
    ("influencer1@fashion.com", "Sarah El Fassi", "sarah_fashion"),
    ("influencer2@food.com", "Karim Benali", "karim_food"),
    ("influencer3@tech.com", "Amine Ziani", "amine_tech"),
    ("influencer4@travel.com", "Leila Amrani", "leila_travel"),
    ("influencer5@food.com", "Youssef Alami", "youssef_food")
]

print("=" * 70)
print("MISE À JOUR DES NOMS ET USERNAMES")
print("=" * 70)

for email, full_name, username in updates:
    try:
        # Mettre à jour le full_name dans users
        response = supabase.table("users").update({
            "full_name": full_name
        }).eq("email", email).execute()
        
        if response.data:
            # Récupérer l'user_id
            user_response = supabase.table("users").select("id").eq("email", email).execute()
            if user_response.data:
                user_id = user_response.data[0]["id"]
                
                # Mettre à jour le username dans influencers
                inf_response = supabase.table("influencers").update({
                    "username": username
                }).eq("user_id", user_id).execute()
                
                print(f"✓ {email} → {full_name} (@{username})")
        else:
            print(f"✗ {email} non trouvé")
            
    except Exception as e:
        print(f"✗ Erreur pour {email}: {str(e)}")

print("\n" + "=" * 70)
print("TERMINÉ!")
print("=" * 70)
