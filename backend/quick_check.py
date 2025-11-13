"""Quick check des utilisateurs"""
from supabase_client import supabase
from utils.logger import logger

try:
    result = supabase.table("users").select("email, role, password_hash").limit(5).execute()
    logger.info("\n=== PREMIERS UTILISATEURS ===")
    for user in result.data:
        has_hash = "OUI" if user.get("password_hash") else "NON"
        logger.info(f"{user['email']} ({user['role']}) - Hash: {has_hash}")
except Exception as e:
    logger.info(f"Erreur: {e}")
