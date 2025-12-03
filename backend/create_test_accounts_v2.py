"""Créer les comptes de test pour l'application"""
import bcrypt
from supabase_client import supabase
from utils.logger import logger

def hash_password(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Mot de passe par défaut pour tous les comptes: "Test123!"
DEFAULT_PASSWORD = "Test123!"
password_hash = hash_password(DEFAULT_PASSWORD)

logger.info("=== CRÉATION DES COMPTES DE TEST ===")
logger.info(f"Mot de passe pour tous les comptes: {DEFAULT_PASSWORD}\n")

def get_or_create_user(email, role, **kwargs):
    """Récupère un utilisateur existant ou le crée"""
    try:
        # Vérifier si l'utilisateur existe
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            logger.info(f"   ℹ️ L'utilisateur {email} existe déjà (ID: {existing.data[0]['id']})")
            return existing.data[0]["id"]
        
        # Créer l'utilisateur
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "is_verified": True,
            "two_fa_enabled": False
        }
        # Ajouter les kwargs
        user_data.update(kwargs)
        
        result = supabase.table("users").insert(user_data).execute()
        if result.data:
            logger.info(f"   ✅ Utilisateur {email} créé avec succès")
            return result.data[0]["id"]
        return None
    except Exception as e:
        logger.error(f"   ❌ Erreur lors de la création de {email}: {e}")
        return None

# 1. Admin Enterprise
logger.info("1. Création du compte ADMIN...")
get_or_create_user("admin@getyourshare.com", "admin")

# 2. Influenceurs
logger.info("\n2. Création des INFLUENCEURS...")
influencers = [
    {
        "email": "hassan.oudrhiri@getyourshare.com",
        "username": "Hassan Oudrhiri",
        "full_name": "Hassan Oudrhiri",
        "subscription_plan": "starter",
        "category": "Food & Cuisine",
        "audience_size": 67000,
        "influencer_type": "micro"
    },
    {
        "email": "sarah.benali@getyourshare.com",
        "username": "Sarah Benali",
        "full_name": "Sarah Benali",
        "subscription_plan": "pro",
        "category": "Lifestyle",
        "audience_size": 125000,
        "influencer_type": "macro"
    },
    {
        "email": "karim.benjelloun@getyourshare.com",
        "username": "Karim Benjelloun",
        "full_name": "Karim Benjelloun",
        "subscription_plan": "pro",
        "category": "Tech & Gaming",
        "audience_size": 285000,
        "influencer_type": "macro"
    }
]

for inf in influencers:
    try:
        user_id = get_or_create_user(inf["email"], "influencer")
        
        if user_id:
            # Vérifier si le profil existe déjà
            existing_profile = supabase.table("influencers").select("id").eq("user_id", user_id).execute()
            
            if not existing_profile.data:
                # Créer le profil influencer
                influencer_data = {
                    "user_id": user_id,
                    "username": inf["username"],
                    "full_name": inf["full_name"],
                    "subscription_plan": inf["subscription_plan"],
                    "category": inf["category"],
                    "audience_size": inf["audience_size"],
                    "influencer_type": inf["influencer_type"]
                }
                supabase.table("influencers").insert(influencer_data).execute()
                logger.info(f"   ✅ Profil {inf['username']} créé")
            else:
                logger.info(f"   ℹ️ Profil {inf['username']} existe déjà")
    except Exception as e:
        logger.info(f"   ❌ Erreur pour {inf['username']}: {e}")

# 3. Marchands
logger.info("\n3. Création des MARCHANDS...")
merchants = [
    {
        "email": "boutique.maroc@getyourshare.com",
        "company_name": "Boutique Maroc",
        "subscription_plan": "starter",
        "category": "Mode et lifestyle",
        "description": "Artisanat traditionnel marocain"
    },
    {
        "email": "luxury.crafts@getyourshare.com",
        "company_name": "Luxury Crafts",
        "subscription_plan": "pro",
        "category": "Mode et lifestyle",
        "description": "Artisanat Premium"
    },
    {
        "email": "electro.maroc@getyourshare.com",
        "company_name": "ElectroMaroc",
        "subscription_plan": "enterprise",
        "category": "Technologie",
        "description": "Électronique & High-Tech"
    }
]

for mer in merchants:
    try:
        user_id = get_or_create_user(mer["email"], "merchant")
        
        if user_id:
            # Vérifier si le profil existe déjà
            existing_profile = supabase.table("merchants").select("id").eq("user_id", user_id).execute()
            
            if not existing_profile.data:
                # Créer le profil merchant
                merchant_data = {
                    "user_id": user_id,
                    "company_name": mer["company_name"],
                    "subscription_plan": mer["subscription_plan"],
                    "category": mer["category"],
                    "description": mer["description"]
                }
                supabase.table("merchants").insert(merchant_data).execute()
                logger.info(f"   ✅ Profil {mer['company_name']} créé")
            else:
                logger.info(f"   ℹ️ Profil {mer['company_name']} existe déjà")
    except Exception as e:
        logger.info(f"   ❌ Erreur pour {mer['company_name']}: {e}")

# 4. Commercial
logger.info("\n4. Création du compte COMMERCIAL...")
try:
    # Créer l'utilisateur commercial avec le bon rôle 'commercial' maintenant que la contrainte est fixée
    get_or_create_user("sofia.chakir@getyourshare.com", "commercial")
except Exception as e:
    logger.info(f"   ❌ Erreur: {e}")

logger.info("\n\n=== RÉSUMÉ DES COMPTES CRÉÉS ===")
logger.info(f"Email: [nom]@getyourshare.com")
logger.info(f"Mot de passe: {DEFAULT_PASSWORD}")
logger.info("\nComptes disponibles:")
logger.info("  - admin@getyourshare.com (ADMIN - ENTERPRISE)")
logger.info("  - hassan.oudrhiri@getyourshare.com (INFLUENCER - STARTER)")
logger.info("  - sarah.benali@getyourshare.com (INFLUENCER - PRO)")
logger.info("  - karim.benjelloun@getyourshare.com (INFLUENCER - ENTERPRISE)")
logger.info("  - boutique.maroc@getyourshare.com (MERCHANT - STARTER)")
logger.info("  - luxury.crafts@getyourshare.com (MERCHANT - PRO)")
logger.info("  - electro.maroc@getyourshare.com (MERCHANT - ENTERPRISE)")
logger.info("  - sofia.chakir@getyourshare.com (COMMERCIAL - ENTERPRISE)")
