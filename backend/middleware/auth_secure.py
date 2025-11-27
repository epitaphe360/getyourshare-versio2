"""
Middleware d'authentification sécurisé
- JWT avec httpOnly cookies (au lieu de localStorage)
- CSRF protection
- Rate limiting
- Session management
"""
from fastapi import Request, HTTPException, status, Response
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import secrets

from config.security import get_jwt_secret, get_jwt_secret_key
from utils.logger import logger


security = HTTPBearer()


class AuthManager:
    """Gestionnaire d'authentification sécurisé"""

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token court (15 min au lieu de 24h)
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    CSRF_TOKEN_LENGTH = 32

    def __init__(self):
        self.jwt_secret = get_jwt_secret()
        self.jwt_secret_key = get_jwt_secret_key()

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crée un JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.jwt_secret,
            algorithm=self.ALGORITHM
        )

        logger.info(f"Access token created for user {data.get('sub')}")
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crée un JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.jwt_secret_key,
            algorithm=self.ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Vérifie et décode un JWT token"""
        try:
            secret = self.jwt_secret if token_type == "access" else self.jwt_secret_key

            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.ALGORITHM]
            )

            # Vérifier le type de token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        csrf_token: Optional[str] = None
    ):
        """Configure les cookies d'authentification httpOnly"""

        # Cookie pour access token (httpOnly, secure, sameSite)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # HTTPS uniquement
            samesite="strict",
            max_age=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        # Cookie pour refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        # CSRF token (pas httpOnly car lu par JavaScript)
        if not csrf_token:
            csrf_token = secrets.token_urlsafe(self.CSRF_TOKEN_LENGTH)

        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # Accessible par JS
            secure=True,
            samesite="strict",
            max_age=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        logger.info("Auth cookies set successfully")

    def clear_auth_cookies(self, response: Response):
        """Supprime les cookies d'authentification (logout)"""
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("csrf_token")

        logger.info("Auth cookies cleared")

    def generate_csrf_token(self) -> str:
        """Génère un token CSRF"""
        return secrets.token_urlsafe(self.CSRF_TOKEN_LENGTH)

    def verify_csrf_token(self, token_from_header: str, token_from_cookie: str):
        """Vérifie le token CSRF (double submit cookie)"""
        if not token_from_header or not token_from_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )

        if not secrets.compare_digest(token_from_header, token_from_cookie):
            logger.warning("CSRF token mismatch")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed"
            )


# Instance globale
auth_manager = AuthManager()


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Récupère l'utilisateur courant depuis le cookie httpOnly
    Remplace l'ancienne méthode qui lisait depuis localStorage
    """
    # Récupérer access token depuis cookie
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Vérifier le token
    payload = auth_manager.verify_token(access_token, "access")

    return payload


async def require_csrf(request: Request):
    """
    Middleware CSRF pour les requêtes POST/PUT/DELETE
    Vérifie le double submit cookie pattern
    """
    # Ignorer GET, HEAD, OPTIONS
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return

    # Récupérer tokens
    csrf_header = request.headers.get("X-CSRF-Token")
    csrf_cookie = request.cookies.get("csrf_token")

    # Vérifier
    auth_manager.verify_csrf_token(csrf_header, csrf_cookie)


async def require_role(request: Request, required_role: str):
    """Vérifie que l'utilisateur a le rôle requis"""
    user = await get_current_user(request)

    user_role = user.get("role")

    if user_role != required_role:
        logger.warning(f"Access denied: user {user.get('sub')} has role {user_role}, required {required_role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {required_role}"
        )

    return user
