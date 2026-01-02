"""Réinitialiser les mots de passe des comptes de test"""
import bcrypt
from supabase_client import supabase
from utils.logger import logger

def hash_password(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

DEFAULT_PASSWORD = "Test1234!" # Note: Le script d'audit utilise Test1234! (avec un 4)
password_hash = hash_password(DEFAULT_PASSWORD)

logger.info(f"=== RÉINITIALISATION DES MOTS DE PASSE ===")
logger.info(f"Nouveau mot de passe: {DEFAULT_PASSWORD}\n")

emails = [
    "admin@getyourshare.com",
    "merchant1@fashionstore.com",
    "influencer1@fashion.com",
    "commercial1@shareyoursales.ma",
    "hassan.oudrhiri@getyourshare.com",
    "sarah.benali@getyourshare.com",
    "karim.benjelloun@getyourshare.com",
    "boutique.maroc@getyourshare.com",
    "luxury.crafts@getyourshare.com",
    "electro.maroc@getyourshare.com",
    "sofia.chakir@getyourshare.com"
]

for email in emails:
    try:
        # Vérifier si l'utilisateur existe
        user = supabase.table("users").select("id").eq("email", email).execute()
        
        if user.data:
            user_id = user.data[0]["id"]
            # Mettre à jour le mot de passe
            supabase.table("users").update({
                "password_hash": password_hash
            }).eq("id", user_id).execute()
            logger.info(f"   ✅ Mot de passe mis à jour pour {email}")
        else:
            logger.info(f"   ⚠️ Utilisateur non trouvé: {email}")
            
    except Exception as e:
        logger.error(f"   ❌ Erreur pour {email}: {e}")

logger.info("\n=== TERMINÉ ===")
