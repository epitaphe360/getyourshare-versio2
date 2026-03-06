"""
Endpoints d'authentification avancÃ©s
- RÃ©initialisation de mot de passe
- VÃ©rification d'email
- 2FA (Two-Factor Authentication)
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime, timedelta
from typing import Optional
import secrets
import pyotp
import qrcode
from io import BytesIO
import base64
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Auth & DB
from auth import get_current_user_from_cookie
from supabase_client import supabase
from db_helpers import hash_password

router = APIRouter(prefix="/api/auth", tags=["Authentication Advanced"])
limiter = Limiter(key_func=get_remote_address)

# Store temporaire pour les tokens de reset/verification (Redis recommandÃ© en production)
# Ces tokens NE contiennent PAS de donnÃ©es sensibles, seulement des tokens alÃ©atoires
PASSWORD_RESET_TOKENS: dict = {}
EMAIL_VERIFICATION_TOKENS: dict = {}

# ============================================
# MODELS
# ============================================

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: constr(min_length=32, max_length=256)
    new_password: constr(min_length=8, max_length=128)

class EmailVerification(BaseModel):
    token: constr(min_length=32, max_length=256)

class TwoFactorSetup(BaseModel):
    pass

class TwoFactorVerify(BaseModel):
    code: constr(min_length=6, max_length=6, pattern="^[0-9]{6}$")

class TwoFactorDisable(BaseModel):
    password: str
    code: constr(min_length=6, max_length=6, pattern="^[0-9]{6}$")

# ============================================
# PASSWORD RESET ENDPOINTS
# ============================================

@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, data: PasswordResetRequest):
    """
    Demander une rÃ©initialisation de mot de passe.
    Envoie un email avec un lien de rÃ©initialisation.
    """
    email = data.email

    # VÃ©rifier que l'utilisateur existe (sans rÃ©vÃ©ler si l'email existe)
    try:
        result = supabase.table("users").select("id, email").eq("email", email).execute()
        user_exists = bool(result.data)
    except Exception:
        user_exists = False

    # GÃ©nÃ©rer un token unique (mÃªme si l'utilisateur n'existe pas pour Ã©viter l'Ã©numÃ©ration)
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=1)

    if user_exists:
        # Stocker le token en mÃ©moire
        PASSWORD_RESET_TOKENS[token] = {
            "email": email,
            "expires_at": expiration,
            "used": False
        }

        # Persister aussi en base pour rÃ©sistance au redÃ©marrage
        try:
            supabase.table("password_reset_tokens").upsert({
                "email": email,
                "token": token,
                "expires_at": expiration.isoformat(),
                "used": False
            }).execute()
        except Exception:
            pass  # La table peut ne pas exister â€” le token en mÃ©moire suffit

        # Envoyer l'email via Resend si configurÃ©
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/reset-password?token={token}"
        try:
            import resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            resend.Emails.send({
                "from": "noreply@shareyoursales.ma",
                "to": email,
                "subject": "RÃ©initialisation de votre mot de passe",
                "html": f"<p>Cliquez sur ce lien pour rÃ©initialiser votre mot de passe (valable 1h) :</p>"
                        f"<p><a href='{reset_link}'>{reset_link}</a></p>"
            })
        except Exception:
            pass  # L'email ne part pas si Resend n'est pas configurÃ©

    return {
        "message": "Si cet email existe, un lien de rÃ©initialisation a Ã©tÃ© envoyÃ©",
        "success": True,
        # Dev only â€” retirÃ© automatiquement en production
        "dev_token": token if os.getenv("DEBUG") == "True" and user_exists else None
    }


@router.post("/reset-password")
@limiter.limit("5/hour")
async def reset_password(request: Request, data: PasswordReset):
    """
    RÃ©initialiser le mot de passe avec un token valide.
    """
    token = data.token

    # Chercher d'abord en mÃ©moire, puis en base
    token_data = PASSWORD_RESET_TOKENS.get(token)

    if token_data is None:
        try:
            result = supabase.table("password_reset_tokens") \
                .select("*").eq("token", token).eq("used", False).execute()
            if result.data:
                row = result.data[0]
                token_data = {
                    "email": row["email"],
                    "expires_at": datetime.fromisoformat(row["expires_at"]),
                    "used": row["used"]
                }
        except Exception:
            pass

    if not token_data:
        raise HTTPException(status_code=400, detail="Token invalide ou expirÃ©")

    # VÃ©rifier l'expiration
    if datetime.utcnow() > token_data["expires_at"]:
        PASSWORD_RESET_TOKENS.pop(token, None)
        raise HTTPException(status_code=400, detail="Token expirÃ©")

    if token_data["used"]:
        raise HTTPException(status_code=400, detail="Token dÃ©jÃ  utilisÃ©")

    # Mettre Ã  jour le mot de passe dans la DB
    email = token_data["email"]
    new_hash = hash_password(data.new_password)
    try:
        supabase.table("users").update({"password": new_hash}).eq("email", email).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise Ã  jour mot de passe : {e}")

    # Marquer le token comme utilisÃ©
    PASSWORD_RESET_TOKENS.pop(token, None)
    try:
        supabase.table("password_reset_tokens").update({"used": True}).eq("token", token).execute()
    except Exception:
        pass

    return {
        "message": "Mot de passe rÃ©initialisÃ© avec succÃ¨s",
        "success": True
    }

# ============================================
# EMAIL VERIFICATION ENDPOINTS
# ============================================

@router.post("/verify-email")
async def verify_email(data: EmailVerification):
    """
    VÃ©rifier l'adresse email avec un token.
    """
    token = data.token

    # Chercher en mÃ©moire puis en base
    token_data = EMAIL_VERIFICATION_TOKENS.get(token)

    if token_data is None:
        try:
            result = supabase.table("email_verification_tokens") \
                .select("*").eq("token", token).execute()
            if result.data:
                row = result.data[0]
                token_data = {
                    "email": row["email"],
                    "expires_at": datetime.fromisoformat(row["expires_at"])
                }
        except Exception:
            pass

    if not token_data:
        raise HTTPException(status_code=400, detail="Token invalide ou expirÃ©")

    if datetime.utcnow() > token_data["expires_at"]:
        EMAIL_VERIFICATION_TOKENS.pop(token, None)
        raise HTTPException(status_code=400, detail="Token expirÃ©")

    # Marquer l'email comme vÃ©rifiÃ© dans la DB
    email = token_data["email"]
    try:
        supabase.table("users").update({"email_verified": True}).eq("email", email).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur vÃ©rification email : {e}")

    EMAIL_VERIFICATION_TOKENS.pop(token, None)
    try:
        supabase.table("email_verification_tokens").delete().eq("token", token).execute()
    except Exception:
        pass

    return {
        "message": "Email vÃ©rifiÃ© avec succÃ¨s",
        "success": True
    }


@router.post("/resend-verification")
@limiter.limit("3/hour")
async def resend_verification(request: Request, data: PasswordResetRequest):
    """
    Renvoyer l'email de vÃ©rification.
    """
    email = data.email

    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=24)

    EMAIL_VERIFICATION_TOKENS[token] = {
        "email": email,
        "expires_at": expiration
    }

    try:
        supabase.table("email_verification_tokens").upsert({
            "email": email,
            "token": token,
            "expires_at": expiration.isoformat()
        }).execute()
    except Exception:
        pass

    # Envoyer l'email
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/verify-email?token={token}"
    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")
        resend.Emails.send({
            "from": "noreply@shareyoursales.ma",
            "to": email,
            "subject": "VÃ©rifiez votre adresse email",
            "html": f"<p>Cliquez sur ce lien pour vÃ©rifier votre email (valable 24h) :</p>"
                    f"<p><a href='{verification_link}'>{verification_link}</a></p>"
        })
    except Exception:
        pass

    return {
        "message": "Email de vÃ©rification envoyÃ©",
        "success": True,
        "dev_token": token if os.getenv("DEBUG") == "True" else None
    }

# ============================================
# 2FA (TWO-FACTOR AUTHENTICATION) ENDPOINTS
# SÃ©curisÃ©s : user_id extrait du JWT, jamais en query param
# ============================================

@router.post("/2fa/setup")
async def setup_2fa(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Configurer l'authentification Ã  deux facteurs.
    Retourne un QR code Ã  scanner avec Google Authenticator.
    """
    user_id = current_user["id"]

    # RÃ©cupÃ©rer l'email rÃ©el de l'utilisateur
    try:
        result = supabase.table("users").select("email").eq("id", user_id).execute()
        user_email = result.data[0]["email"] if result.data else f"user_{user_id}@shareyoursales.ma"
    except Exception:
        user_email = f"user_{user_id}@shareyoursales.ma"

    # GÃ©nÃ©rer un secret unique
    secret = pyotp.random_base32()
    backup_codes = [secrets.token_hex(4) for _ in range(10)]

    # Persister le secret en base (pending = non encore activÃ©)
    try:
        supabase.table("users").update({
            "two_fa_secret": secret,
            "two_fa_enabled": False,
            "two_fa_backup_codes": backup_codes
        }).eq("id", user_id).execute()
    except Exception:
        pass  # Colonnes peut-Ãªtre absentes â€” le secret reste temporaire

    # GÃ©nÃ©rer le QR code
    app_name = "ShareYourSales"
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name=app_name
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "message": "2FA setup initiated",
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "backup_codes": backup_codes,
        "manual_entry": secret
    }


@router.post("/2fa/verify")
async def verify_2fa(
    data: TwoFactorVerify,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    VÃ©rifier le code 2FA et activer la fonctionnalitÃ©.
    """
    user_id = current_user["id"]

    # Charger le secret depuis la DB
    try:
        result = supabase.table("users").select("two_fa_secret, two_fa_backup_codes").eq("id", user_id).execute()
        if not result.data or not result.data[0].get("two_fa_secret"):
            raise HTTPException(status_code=400, detail="2FA non configurÃ© â€” appelez /2fa/setup d'abord")
        secret = result.data[0]["two_fa_secret"]
        backup_codes = result.data[0].get("two_fa_backup_codes", [])
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur lecture configuration 2FA")

    totp = pyotp.TOTP(secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Code invalide")

    # Activer 2FA en base
    try:
        supabase.table("users").update({"two_fa_enabled": True}).eq("id", user_id).execute()
    except Exception:
        pass

    return {
        "message": "2FA activÃ© avec succÃ¨s",
        "success": True,
        "backup_codes": backup_codes
    }


@router.post("/2fa/disable")
async def disable_2fa(
    data: TwoFactorDisable,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    DÃ©sactiver l'authentification Ã  deux facteurs.
    NÃ©cessite le mot de passe et un code 2FA valide.
    """
    user_id = current_user["id"]

    # Charger les donnÃ©es utilisateur
    try:
        result = supabase.table("users").select("password, two_fa_secret, two_fa_enabled").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        user_row = result.data[0]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur lecture utilisateur")

    if not user_row.get("two_fa_enabled"):
        raise HTTPException(status_code=400, detail="2FA non activÃ©")

    # VÃ©rifier le mot de passe
    from db_helpers import verify_password
    if not verify_password(data.password, user_row.get("password", "")):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    # VÃ©rifier le code 2FA
    secret = user_row.get("two_fa_secret", "")
    if not secret:
        raise HTTPException(status_code=400, detail="Secret 2FA introuvable")

    totp = pyotp.TOTP(secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Code 2FA invalide")

    # DÃ©sactiver 2FA en base
    try:
        supabase.table("users").update({
            "two_fa_enabled": False,
            "two_fa_secret": None,
            "two_fa_backup_codes": []
        }).eq("id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dÃ©sactivation 2FA : {e}")

    return {
        "message": "2FA dÃ©sactivÃ© avec succÃ¨s",
        "success": True
    }


@router.post("/2fa/verify-login")
async def verify_2fa_login(user_id: str, data: TwoFactorVerify):
    """
    VÃ©rifier le code 2FA lors de la connexion.
    user_id est passÃ© ici car c'est une Ã©tape intermÃ©diaire (pas encore authentifiÃ©).
    """
    try:
        result = supabase.table("users").select("two_fa_secret, two_fa_enabled, two_fa_backup_codes").eq("id", user_id).execute()
        if not result.data or not result.data[0].get("two_fa_enabled"):
            raise HTTPException(status_code=400, detail="2FA non activÃ©")
        user_row = result.data[0]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur lecture 2FA")

    secret = user_row["two_fa_secret"]
    backup_codes = user_row.get("two_fa_backup_codes", []) or []
    totp = pyotp.TOTP(secret)

    if totp.verify(data.code, valid_window=1):
        return {"message": "Code valide", "success": True}

    # VÃ©rifier backup code
    if data.code in backup_codes:
        backup_codes.remove(data.code)
        try:
            supabase.table("users").update({"two_fa_backup_codes": backup_codes}).eq("id", user_id).execute()
        except Exception:
            pass
        return {
            "message": "Backup code valide",
            "success": True,
            "warning": "Ce code de secours ne peut Ãªtre utilisÃ© qu'une seule fois"
        }

    raise HTTPException(status_code=400, detail="Code invalide")

# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """
    VÃ©rifier si un email est disponible.
    """
    try:
        result = supabase.table("users").select("id").eq("email", email).execute()
        available = not bool(result.data)
    except Exception:
        available = True

    return {
        "email": email,
        "available": available,
        "suggestions": [
            f"{email.split('@')[0]}.pro@{email.split('@')[1]}",
            f"{email.split('@')[0]}_ma@{email.split('@')[1]}"
        ] if not available else []
    }


@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    VÃ©rifier si un nom d'utilisateur est disponible.
    """
    try:
        result = supabase.table("users").select("id").eq("username", username).execute()
        available = not bool(result.data)
    except Exception:
        available = True

    return {
        "username": username,
        "available": available,
        "suggestions": [
            f"{username}_ma",
            f"{username}_pro",
            f"{username}2025"
        ] if not available else []
    }
