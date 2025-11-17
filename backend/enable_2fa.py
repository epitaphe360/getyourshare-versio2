"""
Script pour activer la 2FA pour tous les utilisateurs
"""

from supabase_client import supabase

logger.info("\n" + "=" * 60)
logger.info("ACTIVATION DE LA 2FA POUR TOUS LES UTILISATEURS")
logger.info("=" * 60 + "\n")

try:
    # 1. Récupérer tous les utilisateurs
    logger.info("1. Récupération des utilisateurs...")
    users_response = supabase.table("users").select("id, email, role, two_fa_enabled").execute()

    if not users_response.data:
        logger.info("   ERREUR: Aucun utilisateur trouvé dans la base de données")
        exit(1)

    logger.info(f"   OK: {len(users_response.data)} utilisateurs trouvés\n")

    # 2. Afficher l'état actuel
    logger.info("2. État actuel de la 2FA:")
    logger.info("-" * 60)
    for user in users_response.data:
        status = "ACTIVEE" if user.get("two_fa_enabled") else "DESACTIVEE"
        logger.info(f"   {user['email']:<35} | {status}")
    print()

    # 3. Activer la 2FA pour tous
    logger.info("3. Activation de la 2FA pour tous les utilisateurs...")
    updated_count = 0

    for user in users_response.data:
        if not user.get("two_fa_enabled"):
            try:
                update_response = (
                    supabase.table("users")
                    .update({"two_fa_enabled": True})
                    .eq("id", user["id"])
                    .execute()
                )

                if update_response.data:
                    logger.info(f"   OK: {user['email']}")
                    updated_count += 1
                else:
                    logger.info(f"   ERREUR: {user['email']} - Aucune mise à jour")
            except Exception as e:
                logger.info(f"   ERREUR: {user['email']} - {str(e)}")
        else:
            logger.info(f"   SKIP: {user['email']} (déjà activée)")

    print()
    logger.info("=" * 60)
    logger.info(f"SUCCÈS: 2FA activée pour {updated_count} utilisateur(s)")
    logger.info("=" * 60)
    logger.info("\nVous pouvez maintenant vous connecter avec:")
    logger.info("   Email: admin@shareyoursales.com")
    logger.info("   Password: admin123")
    logger.info("   Code 2FA: 123456")
    print()

except Exception as e:
    logger.info(f"\nERREUR CRITIQUE: {str(e)}")
    import traceback

    traceback.print_exc()
    exit(1)
