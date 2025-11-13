from supabase_client import supabase
from utils.logger import logger

logger.info("🔧 Activation de la 2FA pour tous les utilisateurs...")
logger.info("=" * 60)

# Activer la 2FA pour tous les utilisateurs
try:
    # Mettre à jour tous les utilisateurs
    result = (
        supabase.table("users")
        .update({"two_fa_enabled": True})
        .neq("id", "00000000-0000-0000-0000-000000000000")
        .execute()
    )  # Update tous sauf un ID fictif

    if result.data:
        logger.info(f"✅ 2FA activée pour {len(result.data)} utilisateurs")

        # Afficher les utilisateurs mis à jour
        users = supabase.table("users").select("email, role, two_fa_enabled").execute()

        logger.info("\n📋 État actuel des utilisateurs:")
        logger.info("-" * 60)

        for user in users.data:
            two_fa_icon = "✅" if user.get("two_fa_enabled") else "❌"
            logger.info(
                f"{two_fa_icon} {user['email']:<35} | Rôle: {user['role']:<12} | 2FA: {user.get('two_fa_enabled')}"
            )

        logger.info("\n" + "=" * 60)
        logger.info("✅ Configuration terminée!")
        logger.info("\n💡 Vous pouvez maintenant vous connecter avec:")
        logger.info("   - Code 2FA: 123456 (pour tous les comptes)")

    else:
        logger.info("⚠️ Aucune mise à jour effectuée")
        logger.info("\n💡 Essayons une approche différente...")

        # Récupérer tous les utilisateurs
        all_users = supabase.table("users").select("id, email, role").execute()

        if all_users.data:
            logger.info(f"\nMise à jour individuelle de {len(all_users.data)} utilisateurs...")
            updated_count = 0

            for user in all_users.data:
                try:
                    update_result = (
                        supabase.table("users")
                        .update({"two_fa_enabled": True})
                        .eq("id", user["id"])
                        .execute()
                    )

                    if update_result.data:
                        logger.info(f"  ✅ {user['email']}")
                        updated_count += 1
                    else:
                        logger.info(f"  ⚠️ {user['email']} (pas de changement)")

                except Exception as e:
                    logger.info(f"  ❌ {user['email']}: {e}")

            logger.info(f"\n✅ {updated_count} utilisateurs mis à jour avec succès!")

except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    logger.info("\n💡 Vérifiez que:")
    logger.info("   1. La colonne 'two_fa_enabled' existe dans la table 'users'")
    logger.info("   2. Vous avez les permissions nécessaires")
    logger.info("   3. La connexion Supabase est fonctionnelle")
