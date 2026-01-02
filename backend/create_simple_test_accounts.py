"""Créer les comptes de test SIMPLIFIÉS pour l'application"""
import bcrypt
from supabase_client import supabase
from utils.logger import logger

def hash_password(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Mot de passe par défaut pour tous les comptes: "Test123!"
DEFAULT_PASSWORD = "Test123!"
password_hash = hash_password(DEFAULT_PASSWORD)

logger.info("=== CRÉATION DES COMPTES DE TEST (SIMPLIFIÉE) ===")
logger.info(f"Mot de passe pour tous les comptes: {DEFAULT_PASSWORD}\n")

# Liste des utilisateurs à créer
users = [
    {
        "email": "hassan.oudrhiri@getyourshare.com",
        "role": "influencer",
        "full_name": "Hassan Oudrhiri",
        "niche": "Food & Cuisine",
        "followers_count": 67000,
        "subscription_plan": "starter"
    },
    {
        "email": "boutique.maroc@getyourshare.com",
        "role": "merchant",
        "company_name": "Boutique Maroc",
        "niche": "Mode et lifestyle",
        "subscription_plan": "starter"
    },
    {
        "email": "sofia.chakir@getyourshare.com",
        "role": "admin",
        "full_name": "Sofia Chakir",
        "subscription_plan": "enterprise"
    }
]

for user in users:
    try:
        user_data = {
            "email": user["email"],
            "password_hash": password_hash,
            "role": user["role"],
            "is_active": True,
            "is_verified": True,
            "two_fa_enabled": False,
            "subscription_plan": user.get("subscription_plan", "starter")
        }
        
        # Ajouter les champs optionnels s'ils existent
        if "full_name" in user:
            user_data["full_name"] = user["full_name"]
        if "company_name" in user:
            user_data["company_name"] = user["company_name"]
        if "niche" in user:
            user_data["niche"] = [user["niche"]]  # niche est un array
        if "followers_count" in user:
            user_data["followers_count"] = user["followers_count"]
        
        result = supabase.table("users").insert(user_data).execute()
        logger.info(f"✅ {user['email']} ({user['role'].upper()}) créé avec succès")
    except Exception as e:
        logger.info(f"❌ Erreur pour {user['email']}: {e}")

logger.info("\n\n=== RÉSUMÉ DES COMPTES CRÉÉS ===")
logger.info(f"Mot de passe: {DEFAULT_PASSWORD}")
logger.info("\nComptes disponibles:")
logger.info("  - admin@getyourshare.com (ADMIN)")
logger.info("  - hassan.oudrhiri@getyourshare.com (INFLUENCER)")
logger.info("  - boutique.maroc@getyourshare.com (MERCHANT)")
logger.info("  - sofia.chakir@getyourshare.com (COMMERCIAL/ADMIN)")
