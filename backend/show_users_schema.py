"""Afficher la structure de la table users"""
from supabase_client import supabase
from utils.logger import logger

logger.info("=== STRUCTURE TABLE USERS ===\n")

try:
    # Récupérer un utilisateur existant pour voir les colonnes
    result = supabase.table("users").select("*").limit(1).execute()
    if result.data:
        user = result.data[0]
        logger.info("Colonnes disponibles:")
        for key in user.keys():
            logger.info(f"  - {key}")
    else:
        logger.info("Aucun utilisateur trouvé")
except Exception as e:
    logger.info(f"Erreur: {e}")
