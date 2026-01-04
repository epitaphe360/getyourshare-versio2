"""
Utilitaire de gestion d'erreurs centralisé pour ShareYourSales

Usage:
    from utils.error_handler import handle_error, log_error, ErrorCategory

    try:
        # Code
    except Exception as e:
        handle_error(e, ErrorCategory.DATABASE, user_id=user_id)
"""

import logging
import traceback
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Catégories d'erreurs pour classification"""
    DATABASE = "database"
    PAYMENT = "payment"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    EXTERNAL_API = "external_api"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    FILE_UPLOAD = "file_upload"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    """Niveaux de sévérité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

def log_error(
    error: Exception,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Log une erreur avec contexte complet

    Args:
        error: Exception à logger
        category: Catégorie de l'erreur
        severity: Niveau de sévérité
        context: Contexte additionnel (params, data, etc.)
        user_id: ID utilisateur concerné

    Returns:
        error_id: ID unique de l'erreur pour tracking
    """
    import secrets

    error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

    error_data = {
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "category": category.value,
        "severity": severity.value,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "user_id": user_id,
        "context": context or {},
        "traceback": traceback.format_exc()
    }

    # Log selon la sévérité
    log_message = f"[{error_id}] {category.value.upper()}: {str(error)}"

    if severity == ErrorSeverity.CRITICAL:
        logger.critical(log_message, extra=error_data)
    elif severity == ErrorSeverity.HIGH:
        logger.error(log_message, extra=error_data)
    elif severity == ErrorSeverity.MEDIUM:
        logger.warning(log_message, extra=error_data)
    else:
        logger.info(log_message, extra=error_data)

    # TODO: Envoyer à Sentry en production
    # if os.getenv("ENVIRONMENT") == "production":
    #     sentry_sdk.capture_exception(error)

    return error_id

def handle_error(
    error: Exception,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_friendly_message: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    raise_error: bool = False
) -> Dict[str, Any]:
    """
    Gère une erreur de manière centralisée

    Args:
        error: Exception à gérer
        category: Catégorie de l'erreur
        severity: Niveau de sévérité
        user_friendly_message: Message à retourner à l'utilisateur
        context: Contexte additionnel
        user_id: ID utilisateur concerné
        raise_error: Si True, re-raise l'exception après logging

    Returns:
        Dict avec error_id, message, et details

    Raises:
        Exception: Si raise_error=True
    """
    error_id = log_error(error, category, severity, context, user_id)

    # Message par défaut selon la catégorie
    default_messages = {
        ErrorCategory.DATABASE: "Erreur lors de l'accès à la base de données",
        ErrorCategory.PAYMENT: "Erreur lors du traitement du paiement",
        ErrorCategory.AUTHENTICATION: "Erreur d'authentification",
        ErrorCategory.VALIDATION: "Données invalides",
        ErrorCategory.EXTERNAL_API: "Erreur de communication avec un service externe",
        ErrorCategory.SOCIAL_MEDIA: "Erreur lors de l'accès aux réseaux sociaux",
        ErrorCategory.EMAIL: "Erreur lors de l'envoi de l'email",
        ErrorCategory.FILE_UPLOAD: "Erreur lors du téléchargement du fichier",
        ErrorCategory.BUSINESS_LOGIC: "Erreur de traitement",
        ErrorCategory.UNKNOWN: "Une erreur s'est produite"
    }

    response = {
        "error_id": error_id,
        "message": user_friendly_message or default_messages.get(category, default_messages[ErrorCategory.UNKNOWN]),
        "category": category.value,
        "severity": severity.value
    }

    # Inclure détails en développement
    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        response["details"] = str(error)
        response["type"] = type(error).__name__

    if raise_error:
        raise error

    return response

def safe_db_operation(func):
    """
    Décorateur pour wrapper les opérations DB avec gestion d'erreurs

    Usage:
        @safe_db_operation
        def get_user(user_id):
            return supabase.table("users").select().eq("id", user_id).execute()
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = handle_error(
                e,
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.HIGH,
                context={"function": func.__name__, "args": str(args)[:200]}
            )
            logger.error(f"Database operation failed: {func.__name__}")
            return None

    return wrapper

def safe_api_call(func):
    """
    Décorateur pour wrapper les appels API externes avec gestion d'erreurs

    Usage:
        @safe_api_call
        def call_stripe_api():
            return stripe.Customer.create(...)
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = handle_error(
                e,
                category=ErrorCategory.EXTERNAL_API,
                severity=ErrorSeverity.MEDIUM,
                context={"function": func.__name__}
            )
            logger.error(f"External API call failed: {func.__name__}")
            return None

    return wrapper

# Utilitaires pour erreurs spécifiques

class DatabaseError(Exception):
    """Erreur base de données"""
    pass

class PaymentError(Exception):
    """Erreur paiement"""
    pass

class ValidationError(Exception):
    """Erreur validation"""
    pass

class ExternalAPIError(Exception):
    """Erreur API externe"""
    pass

class SocialMediaError(Exception):
    """Erreur réseaux sociaux"""
    pass

def create_error_response(
    message: str,
    error_code: str,
    details: Optional[Dict] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Crée une réponse d'erreur standardisée pour FastAPI

    Args:
        message: Message d'erreur
        error_code: Code d'erreur (ex: INVALID_EMAIL, PAYMENT_FAILED)
        details: Détails additionnels
        status_code: Code HTTP

    Returns:
        Dict formaté pour HTTPException
    """
    return {
        "status_code": status_code,
        "detail": {
            "message": message,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    }
