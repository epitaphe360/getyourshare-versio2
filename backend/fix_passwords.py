"""
Script pour corriger les mots de passe des utilisateurs dans Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import bcrypt
from utils.logger import logger

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

logger.info("🔧 Correction des mots de passe...")
logger.info("=" * 60)

# Liste des comptes à corriger avec leurs mots de passe en clair
accounts = [
    ("admin@shareyoursales.com", "admin123"),
    ("contact@techstyle.fr", "merchant123"),
    ("hello@beautypro.com", "merchant123"),
    ("emma.style@instagram.com", "influencer123"),
    ("lucas.tech@youtube.com", "influencer123"),
    ("julie.beauty@tiktok.com", "influencer123"),
    ("test@example.com", "influencer123"),
]

for email, password in accounts:
    try:
        # Générer le hash bcrypt
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Mettre à jour l'utilisateur
        result = (
            supabase.table("users")
            .update({"password_hash": password_hash})
            .eq("email", email)
            .execute()
        )

        if result.data:
            logger.info(f"✅ {email} - mot de passe mis à jour")
        else:
            logger.info(f"⚠️  {email} - utilisateur introuvable")

    except Exception as e:
        logger.info(f"❌ {email} - erreur: {str(e)}")

logger.info("=" * 60)
logger.info("✅ Correction terminée !")
logger.info("\nVous pouvez maintenant vous connecter avec:")
logger.info("  - admin@shareyoursales.com / admin123")
logger.info("  - contact@techstyle.fr / merchant123")
logger.info("  - emma.style@instagram.com / influencer123")
