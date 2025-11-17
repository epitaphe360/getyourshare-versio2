import sys
from utils.logger import logger

sys.path.insert(0, "C:\\Users\\Admin\\Desktop\\shareyoursales\\Getyourshare1\\backend")

try:
    from supabase_client import supabase

    logger.info("🔍 Test du statut 2FA...")
    logger.info("=" * 60)

    # Vérifier l'utilisateur admin
    result = (
        supabase.table("users")
        .select("email, two_fa_enabled")
        .eq("email", "admin@shareyoursales.com")
        .execute()
    )

    if result.data:
        user = result.data[0]
        logger.info(f"✅ Utilisateur trouvé: {user['email']}")
        logger.info(f"   2FA activée: {user.get('two_fa_enabled', False)}")

        if not user.get("two_fa_enabled"):
            logger.info("\n⚠️ 2FA n'est PAS activée! Activation...")
            update_result = (
                supabase.table("users")
                .update({"two_fa_enabled": True})
                .eq("email", "admin@shareyoursales.com")
                .execute()
            )
            logger.info("✅ 2FA activée avec succès!")
    else:
        logger.info("❌ Utilisateur non trouvé")

except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
