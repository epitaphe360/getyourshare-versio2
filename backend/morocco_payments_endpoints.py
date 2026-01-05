"""
MOROCCO PAYMENTS API ENDPOINTS
Endpoints pour tous les gateways de paiement marocains
Tables: transactions, payment_logs
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from supabase_config import get_supabase_client
from auth import get_current_user_from_cookie
from services.morocco_payments_service import MoroccoPaymentService
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# MODELS
# ============================================

class PaymentInitRequest(BaseModel):
    provider: str  # cmi, payzen, orange_money, inwi_money, maroc_telecom
    amount: float
    currency: str = "504"  # MAD par défaut
    order_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    description: Optional[str] = None
    callback_success_url: Optional[str] = None
    callback_failure_url: Optional[str] = None

class PaymentStatusRequest(BaseModel):
    transaction_id: str
    provider: str

# ============================================
# Configuration du service
# ============================================

def get_morocco_payment_service() -> MoroccoPaymentService:
    """
    Initialise le service de paiement Maroc avec config depuis ENV
    """
    config = {}

    # CMI Configuration
    if os.getenv("CMI_STORE_KEY") and os.getenv("CMI_CLIENT_ID"):
        config["cmi"] = {
            "store_key": os.getenv("CMI_STORE_KEY"),
            "client_id": os.getenv("CMI_CLIENT_ID"),
            "environment": os.getenv("CMI_ENVIRONMENT", "test")
        }

    # PayZen Configuration
    if os.getenv("PAYZEN_SHOP_ID") and os.getenv("PAYZEN_SECRET_KEY"):
        config["payzen"] = {
            "shop_id": os.getenv("PAYZEN_SHOP_ID"),
            "secret_key": os.getenv("PAYZEN_SECRET_KEY"),
            "environment": os.getenv("PAYZEN_ENVIRONMENT", "test")
        }

    # Orange Money Configuration
    if os.getenv("ORANGE_MONEY_MERCHANT_CODE") and os.getenv("ORANGE_MONEY_API_KEY"):
        config["orange_money"] = {
            "merchant_code": os.getenv("ORANGE_MONEY_MERCHANT_CODE"),
            "api_key": os.getenv("ORANGE_MONEY_API_KEY"),
            "environment": os.getenv("ORANGE_MONEY_ENVIRONMENT", "test")
        }

    # Inwi Money Configuration
    if os.getenv("INWI_MONEY_MERCHANT_ID") and os.getenv("INWI_MONEY_API_KEY"):
        config["inwi_money"] = {
            "merchant_id": os.getenv("INWI_MONEY_MERCHANT_ID"),
            "api_key": os.getenv("INWI_MONEY_API_KEY"),
            "environment": os.getenv("INWI_MONEY_ENVIRONMENT", "test")
        }

    # Maroc Telecom Cash Configuration
    if os.getenv("MTCASH_MERCHANT_CODE") and os.getenv("MTCASH_API_KEY") and os.getenv("MTCASH_SECRET_KEY"):
        config["maroc_telecom"] = {
            "merchant_code": os.getenv("MTCASH_MERCHANT_CODE"),
            "api_key": os.getenv("MTCASH_API_KEY"),
            "secret_key": os.getenv("MTCASH_SECRET_KEY"),
            "environment": os.getenv("MTCASH_ENVIRONMENT", "test")
        }

    return MoroccoPaymentService(config)

# ============================================
# GET /api/payments/morocco/providers
# Liste des providers disponibles
# ============================================
@router.get("/providers")
async def get_available_providers():
    """Retourne la liste des providers de paiement configurés et disponibles"""
    try:
        service = get_morocco_payment_service()
        providers = service.get_available_providers()

        # Détails de chaque provider
        provider_details = {
            "cmi": {
                "name": "CMI (Centre Monétique Interbancaire)",
                "type": "card",
                "countries": ["MA"],
                "currencies": ["MAD"],
                "features": ["3d_secure", "preauth"]
            },
            "payzen": {
                "name": "PayZen (Lyra)",
                "type": "card",
                "countries": ["MA", "FR", "EU"],
                "currencies": ["MAD", "EUR"],
                "features": ["3d_secure", "recurring"]
            },
            "orange_money": {
                "name": "Orange Money Maroc",
                "type": "mobile_money",
                "countries": ["MA"],
                "currencies": ["MAD"],
                "features": ["instant", "mobile"]
            },
            "inwi_money": {
                "name": "Inwi Money",
                "type": "mobile_money",
                "countries": ["MA"],
                "currencies": ["MAD"],
                "features": ["instant", "mobile", "wallet"]
            },
            "maroc_telecom": {
                "name": "Maroc Telecom Cash",
                "type": "mobile_money",
                "countries": ["MA"],
                "currencies": ["MAD"],
                "features": ["instant", "mobile", "qr_code"]
            }
        }

        available = [
            {
                "id": provider,
                **provider_details.get(provider, {"name": provider, "type": "unknown"})
            }
            for provider in providers
        ]

        return {
            "success": True,
            "providers": available,
            "total": len(available)
        }

    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la récupération des providers"
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# POST /api/payments/morocco/create
# Créer un paiement
# ============================================
@router.post("/create")
async def create_morocco_payment(
    payment: PaymentInitRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Crée un paiement avec un provider marocain
    """
    try:
        service = get_morocco_payment_service()
        supabase = get_supabase_client()

        # Préparer les paramètres selon le provider
        kwargs = {}

        if payment.provider in ["cmi", "payzen"]:
            # Paiements carte bancaire
            kwargs = {
                "currency": payment.currency,
                "order_id": payment.order_id,
                "customer_email": payment.customer_email,
                "customer_name": payment.customer_name,
                "description": payment.description,
                "callback_success_url": payment.callback_success_url or "",
                "callback_failure_url": payment.callback_failure_url or ""
            }

        elif payment.provider in ["orange_money", "inwi_money", "maroc_telecom"]:
            # Paiements mobile money
            if not payment.customer_phone:
                raise HTTPException(
                    status_code=400,
                    detail="Le numéro de téléphone est requis pour les paiements mobile money"
                )

            kwargs = {
                "phone_number": payment.customer_phone,
                "order_id": payment.order_id,
                "description": payment.description,
                "callback_url": payment.callback_success_url or ""
            }

        # Créer le paiement
        result = service.create_payment(
            provider=payment.provider,
            amount=payment.amount,
            **kwargs
        )

        if not result.get("success", True):
            # Log l'échec
            log_payment_transaction(
                supabase,
                user_id=current_user["id"],
                provider=payment.provider,
                amount=payment.amount,
                status="failed",
                error=result.get("error")
            )

            raise HTTPException(status_code=400, detail=result.get("error", "Échec de création du paiement"))

        # Log le succès
        transaction_id = log_payment_transaction(
            supabase,
            user_id=current_user["id"],
            provider=payment.provider,
            amount=payment.amount,
            status="initiated",
            provider_transaction_id=result.get("transaction_id") or result.get("order_id"),
            payment_data=result
        )

        # Ajouter l'ID de notre transaction
        result["internal_transaction_id"] = transaction_id

        return {
            "success": True,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.HIGH,
            user_friendly_message="Erreur lors de la création du paiement",
            context={
                "provider": payment.provider,
                "amount": payment.amount
            },
            user_id=current_user.get("id")
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# POST /api/payments/morocco/callback/{provider}
# Callback de paiement
# ============================================
@router.post("/callback/{provider}")
async def payment_callback(provider: str, request: Request):
    """
    Endpoint de callback pour les providers de paiement
    """
    try:
        service = get_morocco_payment_service()
        supabase = get_supabase_client()

        # Récupérer les données du callback
        if request.headers.get("content-type") == "application/json":
            callback_data = await request.json()
        else:
            # Form data
            form_data = await request.form()
            callback_data = dict(form_data)

        # Vérifier le callback
        verification = service.verify_callback(provider, callback_data)

        if not verification.get("valid", False):
            logger.error(f"Invalid callback from {provider}: {callback_data}")
            return {"success": False, "error": "Invalid signature"}

        # Mettre à jour la transaction
        order_id = verification.get("order_id")
        transaction_id = verification.get("transaction_id")

        if order_id:
            update_payment_status(
                supabase,
                order_id=order_id,
                provider_transaction_id=transaction_id,
                status="completed" if verification.get("success") else "failed",
                callback_data=callback_data
            )

        logger.info(f"Payment callback processed: {provider} - Order {order_id} - Status: {verification.get('status')}")

        return {
            "success": True,
            "status": "processed"
        }

    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.CRITICAL,
            user_friendly_message="Erreur lors du traitement du callback",
            context={"provider": provider}
        )
        logger.error(f"Payment callback error: {e}")
        return {"success": False, "error": str(e)}

# ============================================
# GET /api/payments/morocco/status/{transaction_id}
# Vérifier le statut d'un paiement
# ============================================
@router.get("/status/{transaction_id}")
async def check_payment_status(
    transaction_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Vérifie le statut d'une transaction de paiement"""
    try:
        supabase = get_supabase_client()

        # Récupérer la transaction
        result = supabase.table("payment_transactions")\
            .select("*")\
            .eq("id", transaction_id)\
            .eq("user_id", current_user["id"])\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        transaction = result.data

        # Pour Inwi Money, vérifier le statut en temps réel
        if transaction["provider"] == "inwi_money" and transaction["status"] == "initiated":
            service = get_morocco_payment_service()
            if service.inwi_money:
                status_check = service.inwi_money.check_payment_status(
                    transaction["provider_transaction_id"]
                )
                if status_check.get("success"):
                    # Mettre à jour le statut
                    transaction["status"] = status_check.get("status")
                    update_payment_status(
                        supabase,
                        order_id=transaction["order_id"],
                        status=status_check.get("status"),
                        callback_data=status_check
                    )

        return {
            "success": True,
            "transaction": transaction
        }

    except HTTPException:
        raise
    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la vérification du statut",
            context={"transaction_id": transaction_id},
            user_id=current_user.get("id")
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# GET /api/payments/morocco/history
# Historique des paiements
# ============================================
@router.get("/history")
async def get_payment_history(
    current_user: dict = Depends(get_current_user_from_cookie),
    limit: int = 50,
    offset: int = 0
):
    """Récupère l'historique des paiements de l'utilisateur"""
    try:
        supabase = get_supabase_client()

        result = supabase.table("payment_transactions")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        transactions = result.data or []

        # Statistiques
        total_amount = sum([t.get("amount", 0) for t in transactions if t.get("status") == "completed"])
        completed_count = len([t for t in transactions if t.get("status") == "completed"])
        pending_count = len([t for t in transactions if t.get("status") == "initiated"])

        return {
            "success": True,
            "transactions": transactions,
            "total": len(transactions),
            "stats": {
                "total_amount": total_amount,
                "completed": completed_count,
                "pending": pending_count
            }
        }

    except Exception as e:
        error_response = handle_error(
            e,
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Erreur lors de la récupération de l'historique",
            user_id=current_user.get("id")
        )
        raise HTTPException(status_code=500, detail=error_response["message"])

# ============================================
# HELPER FUNCTIONS
# ============================================

def log_payment_transaction(
    supabase,
    user_id: str,
    provider: str,
    amount: float,
    status: str,
    provider_transaction_id: Optional[str] = None,
    payment_data: Optional[dict] = None,
    error: Optional[str] = None
) -> str:
    """Log une transaction de paiement dans la DB"""
    transaction_data = {
        "user_id": user_id,
        "provider": provider,
        "amount": amount,
        "currency": "MAD",
        "status": status,
        "provider_transaction_id": provider_transaction_id,
        "payment_data": payment_data or {},
        "error_message": error,
        "created_at": datetime.now().isoformat()
    }

    try:
        result = supabase.table("payment_transactions").insert(transaction_data).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        logger.error(f"Error logging payment transaction: {e}")
        return None

def update_payment_status(
    supabase,
    order_id: str,
    status: str,
    provider_transaction_id: Optional[str] = None,
    callback_data: Optional[dict] = None
):
    """Met à jour le statut d'une transaction"""
    update_data = {
        "status": status,
        "updated_at": datetime.now().isoformat()
    }

    if provider_transaction_id:
        update_data["provider_transaction_id"] = provider_transaction_id

    if callback_data:
        update_data["callback_data"] = callback_data

    try:
        supabase.table("payment_transactions")\
            .update(update_data)\
            .eq("order_id", order_id)\
            .execute()
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")
