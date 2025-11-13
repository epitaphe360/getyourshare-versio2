"""
Réinitialise TOUS les mots de passe à Test123!
"""
from supabase_client import supabase
from db_helpers import hash_password
from utils.logger import logger

# Nouveau mot de passe pour TOUS les comptes
NEW_PASSWORD = "Test123!"
hashed = hash_password(NEW_PASSWORD)

logger.info("Mise à jour de TOUS les comptes avec le mot de passe: Test123!")
logger.info("="*60)

# Récupérer tous les utilisateurs
result = supabase.table("users").select("id, email, role").execute()
users = result.data

count = 0
for user in users:
    try:
        supabase.table("users").update({
            "password_hash": hashed,
            "is_active": True,
            "status": "active"
        }).eq("id", user["id"]).execute()
        
        logger.info(f"✅ {user['email']} ({user['role']})")
        count += 1
    except Exception as e:
        logger.info(f"❌ {user['email']}: {e}")

logger.info("="*60)
logger.info(f"✅ {count} comptes mis à jour")
logger.info(f"\n🔑 Mot de passe universel: {NEW_PASSWORD}")
logger.info("\nVous pouvez maintenant vous connecter avec:")
logger.info("  - N'importe quel email de la base")
logger.info(f"  - Mot de passe: {NEW_PASSWORD}")
