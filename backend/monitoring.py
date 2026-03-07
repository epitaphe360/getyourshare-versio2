"""
Monitoring - Sentry + Métriques de performance
Initialiser AVANT de démarrer le serveur FastAPI
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def init_sentry():
    """
    Initialise Sentry pour le backend.
    Variables d'environnement requises:
      SENTRY_DSN       → URL DSN du projet Sentry
      ENVIRONMENT      → production / staging / development
      APP_VERSION      → version de l'app (ex: 1.2.0)
    """
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        logger.info("Sentry DSN non configuré — monitoring désactivé")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        environment = os.getenv("ENVIRONMENT", "development")
        release = os.getenv("APP_VERSION", "1.0.0")

        # Ne pas capturer les erreurs 4xx (attendues) — uniquement 5xx et exceptions
        def before_send(event, hint):
            # Filtrer les erreurs attendues (auth, validation)
            if "exc_info" in hint:
                exc_type, exc_value, _ = hint["exc_info"]
                exc_name = getattr(exc_type, "__name__", "")
                # Ignorer HTTPException avec status 4xx
                if exc_name == "HTTPException":
                    status_code = getattr(exc_value, "status_code", 500)
                    if status_code < 500:
                        return None
            return event

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=f"getyourshare@{release}",
            traces_sample_rate=0.1 if environment == "production" else 1.0,
            profiles_sample_rate=0.05 if environment == "production" else 0.2,
            before_send=before_send,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
                CeleryIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.WARNING,
                    event_level=logging.ERROR,
                ),
            ],
            # Données PII masquées
            send_default_pii=False,
        )

        logger.info(f"✅ Sentry initialisé — env={environment} release={release}")

    except ImportError:
        logger.warning("sentry-sdk non installé — pip install sentry-sdk")
    except Exception as e:
        logger.error(f"Erreur initialisation Sentry: {e}")


def capture_exception(error: Exception, context: Optional[dict] = None):
    """Capture une exception avec contexte additionnel"""
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    except Exception:
        logger.error(f"Exception non capturée par Sentry: {error}")


def capture_message(message: str, level: str = "info", context: Optional[dict] = None):
    """Capture un message dans Sentry"""
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    except Exception:
        pass


def set_user_context(user_id: str, email: str = "", role: str = ""):
    """Associe l'utilisateur courant aux événements Sentry"""
    try:
        import sentry_sdk
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "role": role,
        })
    except Exception:
        pass
