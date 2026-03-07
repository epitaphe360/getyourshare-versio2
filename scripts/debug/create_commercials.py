import sys
import os
from datetime import datetime, timedelta
import bcrypt

# Naviguer vers le répertoire backend
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv("backend/.env")

from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Vérifier les tables disponibles et les plans
print("\n📋 Vérification de la structure...")

# Les plans d'abonnement sont en fait des valeurs dans subscription_plan de la table users
# Pas besoin de table séparée - on va utiliser: free, starter, professional, premium
print("✅ Plans disponibles: free, starter, professional, premium")

# Créer des commerciaux avec différents types d'abonnement
commercials = [
    {
        "email": "commercial.free@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "commercial_free",
        "subscription_plan": "free",
        "phone": "+212600000001",
        "city": "Casablanca",
        "country": "MA",
        "language_preference": "fr"
    },
    {
        "email": "commercial.starter@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "commercial_starter",
        "subscription_plan": "starter",
        "phone": "+212600000002",
        "city": "Rabat",
        "country": "MA",
        "language_preference": "fr"
    },
    {
        "email": "commercial.pro@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "commercial_pro",
        "subscription_plan": "professional",
        "phone": "+212600000003",
        "city": "Marrakech",
        "country": "MA",
        "language_preference": "fr"
    },
    {
        "email": "commercial.premium@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "commercial_premium",
        "subscription_plan": "premium",
        "phone": "+212600000004",
        "city": "Tanger",
        "country": "MA",
        "language_preference": "fr"
    },
    {
        "email": "youssef.alami@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "youssef_alami",
        "subscription_plan": "professional",
        "phone": "+212600000005",
        "city": "Fès",
        "country": "MA",
        "language_preference": "fr"
    },
    {
        "email": "fatima.bennani@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "username": "fatima_bennani",
        "subscription_plan": "starter",
        "phone": "+212600000006",
        "city": "Agadir",
        "country": "MA",
        "language_preference": "fr"
    }
]

print("\n🚀 Création des commerciaux...\n")

created_count = 0
for commercial in commercials:
    try:
        # Vérifier si l'email existe déjà
        existing = supabase.from_("users").select("id,email").eq("email", commercial["email"]).execute()
        
        if existing.data:
            print(f"⚠️  {commercial['email']} existe déjà - Mise à jour du rôle en 'commercial'")
            # Mettre à jour le rôle
            supabase.from_("users").update({
                "role": "commercial",
                "subscription_plan": commercial["subscription_plan"]
            }).eq("email", commercial["email"]).execute()
            created_count += 1
        else:
            # Hasher le mot de passe
            password_hash = bcrypt.hashpw(commercial["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Créer l'utilisateur
            user_data = {
                "email": commercial["email"],
                "password_hash": password_hash,
                "role": commercial["role"],
                "username": commercial["username"],
                "subscription_plan": commercial["subscription_plan"],
                "phone": commercial["phone"],
                "city": commercial["city"],
                "country": commercial["country"],
                "language_preference": commercial["language_preference"],
                "email_verified": True,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = supabase.from_("users").insert(user_data).execute()
            
            if result.data:
                print(f"✅ Créé: {commercial['email']} - Plan: {commercial['subscription_plan']}")
                created_count += 1
            else:
                print(f"❌ Erreur lors de la création de {commercial['email']}")
                
    except Exception as e:
        print(f"❌ Erreur pour {commercial['email']}: {str(e)}")

print(f"\n✅ {created_count}/{len(commercials)} commerciaux créés/mis à jour avec succès!\n")

# Vérifier le résultat
result = supabase.from_("users").select("email,role,subscription_plan").eq("role", "commercial").execute()
print(f"📊 Total de commerciaux dans la base: {len(result.data)}\n")

if result.data:
    for u in result.data:
        print(f"  - {u.get('email')} - Plan: {u.get('subscription_plan')}")
