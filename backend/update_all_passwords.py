"""
Mettre à jour tous les mots de passe des comptes de test
Pour un lancement rapide et facile
"""
from supabase_client import supabase
from db_helpers import hash_password
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOUVEAU MOT DE PASSE SIMPLE POUR TOUS LES COMPTES
NEW_PASSWORD = "password123"

logger.info("="*70)
logger.info("🔐 MISE À JOUR DE TOUS LES MOTS DE PASSE")
logger.info("="*70)
logger.info(f"\n✅ Nouveau mot de passe pour TOUS les comptes: {NEW_PASSWORD}\n")

# Hasher le nouveau mot de passe
password_hash = hash_password(NEW_PASSWORD)

# Liste de tous les comptes à mettre à jour
accounts = [
    "admin@getyourshare.com",
    "hassan.oudrhiri@getyourshare.com",
    "sarah.benali@getyourshare.com",
    "karim.benjelloun@getyourshare.com",
    "boutique.maroc@getyourshare.com",
    "luxury.crafts@getyourshare.com",
    "electro.maroc@getyourshare.com",
    "sofia.chakir@getyourshare.com"
]

success_count = 0
error_count = 0

for email in accounts:
    try:
        # Mettre à jour le mot de passe
        result = supabase.table("users")\
            .update({"password_hash": password_hash})\
            .eq("email", email)\
            .execute()

        if result.data:
            logger.info(f"✅ {email:45} - Mot de passe mis à jour")
            success_count += 1
        else:
            logger.info(f"⚠️  {email:45} - Compte non trouvé (sera créé si nécessaire)")
            error_count += 1
    except Exception as e:
        logger.info(f"❌ {email:45} - Erreur: {e}")
        error_count += 1

# Résumé
logger.info("\n" + "="*70)
logger.info("📊 RÉSUMÉ DE LA MISE À JOUR")
logger.info("="*70)
logger.info(f"✅ Comptes mis à jour avec succès: {success_count}")
logger.info(f"❌ Erreurs ou comptes non trouvés: {error_count}")
logger.info(f"\n🔑 MOT DE PASSE UNIVERSEL: {NEW_PASSWORD}")
logger.info("\n📝 COMPTES DISPONIBLES:")
logger.info("-" * 70)
logger.info("Email                                         | Rôle")
logger.info("-" * 70)
logger.info("admin@getyourshare.com                        | ADMIN")
logger.info("hassan.oudrhiri@getyourshare.com              | INFLUENCER (Starter)")
logger.info("sarah.benali@getyourshare.com                 | INFLUENCER (Pro)")
logger.info("karim.benjelloun@getyourshare.com             | INFLUENCER (Pro)")
logger.info("boutique.maroc@getyourshare.com               | MERCHANT (Starter)")
logger.info("luxury.crafts@getyourshare.com                | MERCHANT (Pro)")
logger.info("electro.maroc@getyourshare.com                | MERCHANT (Enterprise)")
logger.info("sofia.chakir@getyourshare.com                 | ADMIN/COMMERCIAL")
logger.info("-" * 70)
logger.info(f"\n🚀 Connexion rapide: Utilise n'importe quel email ci-dessus avec le mot de passe: {NEW_PASSWORD}")
logger.info("="*70)
