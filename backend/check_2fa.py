from supabase_client import supabase
import json
from utils.logger import logger

# Vérifier les utilisateurs et leur statut 2FA
logger.info("🔍 Vérification de la configuration 2FA...")
logger.info("=" * 50)

result = supabase.table("users").select("email, two_fa_enabled, role").execute()

if result.data:
    logger.info(f"\n✅ Trouvé {len(result.data)} utilisateurs:\n")
    for user in result.data:
        two_fa_status = "✅ Activée" if user.get("two_fa_enabled") else "❌ Désactivée"
        logger.info(f"  Email: {user['email']}")
        logger.info(f"  Rôle: {user['role']}")
        logger.info(f"  2FA: {two_fa_status}")
        print()
else:
    logger.info("❌ Aucun utilisateur trouvé")

logger.info("\n💡 Solution pour activer la 2FA:")
logger.info("   Exécutez update_2fa.py pour activer la 2FA pour tous les utilisateurs")
