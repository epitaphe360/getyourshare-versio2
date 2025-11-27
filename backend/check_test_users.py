"""Vérifier les comptes de test"""
from supabase_client import supabase
from utils.logger import logger

emails = [
    "admin@getyourshare.com",
    "boutique.maroc@getyourshare.com",
    "hassan.oudrhiri@getyourshare.com",
    "sofia.chakir@getyourshare.com"
]

logger.info("=== VÉRIFICATION DES COMPTES ===\n")

for email in emails:
    try:
        result = supabase.table("users").select("id, email, role, is_active").eq("email", email).execute()
        if result.data:
            user = result.data[0]
            logger.info(f"✅ {email}")
            logger.info(f"   ID: {user['id']}")
            logger.info(f"   Role: {user['role']}")
            logger.info(f"   Active: {user['is_active']}\n")
        else:
            logger.info(f"❌ {email} N'EXISTE PAS\n")
    except Exception as e:
        logger.info(f"❌ Erreur pour {email}: {e}\n")
