"""
Script pour mettre à jour les données des influenceurs avec des noms et usernames réels
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Données des influenceurs à mettre à jour
influencers_data = [
    {
        "email": "influencer1@fashion.com",
        "full_name": "Sarah El Fassi",
        "username": "sarah_fashion",
        "category": "Fashion & Beauty",
        "influencer_type": "macro"
    },
    {
        "email": "influencer2@food.com",
        "full_name": "Karim Benali",
        "username": "karim_food",
        "category": "Food & Cuisine",
        "influencer_type": "micro"
    },
    {
        "email": "influencer3@tech.com",
        "full_name": "Amine Ziani",
        "username": "amine_tech",
        "category": "Tech & Innovation",
        "influencer_type": "nano"
    },
    {
        "email": "influencer4@travel.com",
        "full_name": "Leila Amrani",
        "username": "leila_travel",
        "category": "Travel & Tourism",
        "influencer_type": "micro"
    },
    {
        "email": "influencer5@food.com",
        "full_name": "Youssef Alami",
        "username": "youssef_food",
        "category": "Food & Lifestyle",
        "influencer_type": "micro"
    }
]

print("=" * 70)
print("MISE À JOUR DES DONNÉES DES INFLUENCEURS")
print("=" * 70)

for inf_data in influencers_data:
    try:
        # Récupérer l'influenceur par email
        response = supabase.table("users").select("*").eq("email", inf_data["email"]).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            user_id = user["id"]
            
            # Mettre à jour le nom complet dans la table users
            supabase.table("users").update({
                "full_name": inf_data["full_name"]
            }).eq("id", user_id).execute()
            
            # Mettre à jour les données de l'influenceur
            supabase.table("influencers").update({
                "username": inf_data["username"],
                "category": inf_data["category"],
                "influencer_type": inf_data["influencer_type"]
            }).eq("user_id", user_id).execute()
            
            print(f"✓ {inf_data['email']} → {inf_data['full_name']} (@{inf_data['username']})")
        else:
            print(f"✗ {inf_data['email']} non trouvé")
            
    except Exception as e:
        print(f"✗ Erreur pour {inf_data['email']}: {str(e)}")

print("\n" + "=" * 70)
print("MISE À JOUR TERMINÉE")
print("=" * 70)
