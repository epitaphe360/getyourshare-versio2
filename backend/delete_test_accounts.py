"""Supprimer les comptes de test existants"""
from supabase_client import supabase
from utils.logger import logger

emails = [
    "hassan.oudrhiri@getyourshare.com",
    "sarah.benali@getyourshare.com",
    "karim.benjelloun@getyourshare.com",
    "boutique.maroc@getyourshare.com",
    "luxury.crafts@getyourshare.com",
    "electro.maroc@getyourshare.com",
    "sofia.chakir@getyourshare.com"
]

logger.info("=== SUPPRESSION DES COMPTES DE TEST ===\n")

for email in emails:
    try:
        result = supabase.table("users").delete().eq("email", email).execute()
        logger.info(f"✅ {email} supprimé")
    except Exception as e:
        logger.info(f"⚠️  {email}: {e}")

logger.info("\n✅ Nettoyage terminé")
