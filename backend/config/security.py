"""
Configuration Sécurité - JWT et Secrets
Génération automatique de secrets cryptographiques sécurisés
"""
import os
import sys
import secrets
import logging
from pathlib import Path
from utils.logger import logger

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Configuration centralisée de la sécurité"""

    def __init__(self):
        self.jwt_secret = self._get_jwt_secret()
        self.jwt_secret_key = self._get_jwt_secret_key()
        self.session_secret = self._get_session_secret()
        self.encryption_key = self._get_encryption_key()

    def _get_jwt_secret(self) -> str:
        """Récupère JWT_SECRET avec validation stricte"""
        secret = os.getenv("JWT_SECRET")

        if not secret:
            logger.critical("❌ JWT_SECRET not found in environment variables")
            logger.critical("Generate one with: python -c \"import secrets; logger.info(secrets.token_urlsafe(64))\"")
            sys.exit(1)

        if len(secret) < 32:
            logger.critical(f"❌ JWT_SECRET too short ({len(secret)} chars). Minimum: 32 chars")
            sys.exit(1)

        logger.info(f"✅ JWT_SECRET loaded ({len(secret)} chars)")
        return secret

    def _get_jwt_secret_key(self) -> str:
        """Récupère JWT_SECRET_KEY avec fallback sur JWT_SECRET"""
        secret = os.getenv("JWT_SECRET_KEY")

        if not secret:
            logger.warning("⚠️ JWT_SECRET_KEY not set, using JWT_SECRET as fallback")
            secret = self.jwt_secret

        if len(secret) < 32:
            logger.critical(f"❌ JWT_SECRET_KEY too short ({len(secret)} chars)")
            sys.exit(1)

        logger.info(f"✅ JWT_SECRET_KEY loaded ({len(secret)} chars)")
        return secret

    def _get_session_secret(self) -> str:
        """Récupère SESSION_SECRET"""
        secret = os.getenv("SESSION_SECRET", "")

        if not secret or len(secret) < 32:
            logger.warning("⚠️ SESSION_SECRET not set or too short, generating new one")
            secret = secrets.token_urlsafe(64)

        return secret

    def _get_encryption_key(self) -> str:
        """Récupère ENCRYPTION_KEY"""
        key = os.getenv("ENCRYPTION_KEY", "")

        if not key or len(key) < 32:
            logger.warning("⚠️ ENCRYPTION_KEY not set or too short")

        return key

    @staticmethod
    def generate_secret(length: int = 64) -> str:
        """Génère un secret cryptographiquement sécurisé"""
        return secrets.token_urlsafe(length)


# Instance globale
security_config = SecurityConfig()


def get_jwt_secret() -> str:
    """Retourne JWT_SECRET sécurisé"""
    return security_config.jwt_secret


def get_jwt_secret_key() -> str:
    """Retourne JWT_SECRET_KEY sécurisé"""
    return security_config.jwt_secret_key


def get_session_secret() -> str:
    """Retourne SESSION_SECRET"""
    return security_config.session_secret
