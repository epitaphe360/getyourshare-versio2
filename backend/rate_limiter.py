"""
Rate Limiting Service - Protection contre abus et surcharge
"""

import os
import logging
from typing import Optional
from functools import wraps
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)

# Configuration rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Dictionnaire pour tracking requests (fallback si Redis indisponible)
_request_tracking: dict = {}


class RateLimiter:
    """Rate limiter avec support Redis et fallback mémoire"""
    
    def __init__(self):
        self.enabled = RATE_LIMIT_ENABLED
        self.redis_client = None
        self.use_redis = False
        
        if self.enabled:
            try:
                import redis
                self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
                self.redis_client.ping()
                self.use_redis = True
                logger.info("✅ Rate limiting avec Redis activé")
            except Exception as e:
                logger.warning(f"⚠️ Redis non disponible pour rate limiting: {e} - utilisation mémoire")
        else:
            logger.info("ℹ️ Rate limiting désactivé par configuration")
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, int, int]:
        """
        Vérifie si la limite est dépassée
        
        Args:
            key: Identifiant unique (IP, user_id, etc.)
            limit: Nombre maximum de requêtes
            window: Fenêtre de temps en secondes
        
        Returns:
            (allowed, current_count, remaining)
        """
        
        if not self.enabled:
            return (True, 0, limit)
        
        try:
            if self.use_redis and self.redis_client:
                # Utiliser Redis
                current = self.redis_client.get(key)
                if current is None:
                    self.redis_client.setex(key, window, 1)
                    return (True, 1, limit - 1)
                
                current_count = int(current)
                if current_count >= limit:
                    return (False, current_count, 0)
                
                self.redis_client.incr(key)
                return (True, current_count + 1, limit - current_count - 1)
            
            else:
                # Fallback mémoire (simplifié, pas de TTL automatique)
                import time
                current_time = int(time.time())
                window_key = f"{key}:{current_time // window}"
                
                if window_key not in _request_tracking:
                    _request_tracking[window_key] = 1
                    # Nettoyer anciennes fenêtres
                    old_keys = [k for k in _request_tracking.keys() if not k.startswith(key)]
                    for old_key in old_keys:
                        if len(_request_tracking) > 10000:  # Limite taille
                            del _request_tracking[old_key]
                    return (True, 1, limit - 1)
                
                current_count = _request_tracking[window_key]
                if current_count >= limit:
                    return (False, current_count, 0)
                
                _request_tracking[window_key] += 1
                return (True, current_count + 1, limit - current_count - 1)
        
        except Exception as e:
            logger.error(f"Erreur rate limiting: {e}")
            return (True, 0, limit)  # Autoriser en cas d'erreur
    
    def get_client_identifier(self, request: Request) -> str:
        """Récupère identifiant client (IP ou user_id)"""
        
        # Essayer d'obtenir user_id si authentifié
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.get('id', 'anonymous')}"
        
        # Sinon utiliser IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"


# Instance globale
rate_limiter = RateLimiter()


def rate_limit(limit: int = 60, window: int = 60):
    """
    Décorateur pour limiter nombre de requêtes
    
    Usage:
        @rate_limit(limit=10, window=60)  # Max 10 req/minute
        async def my_endpoint():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            if not rate_limiter.enabled:
                return await func(*args, request=request, **kwargs)
            
            # Trouver l'objet Request dans les arguments
            req = request
            if req is None:
                for arg in args:
                    if isinstance(arg, Request):
                        req = arg
                        break
            
            if req is None:
                # Pas de Request trouvée, autoriser
                return await func(*args, request=request, **kwargs)
            
            # Vérifier rate limit
            client_id = rate_limiter.get_client_identifier(req)
            endpoint_key = f"ratelimit:{func.__name__}:{client_id}"
            
            allowed, current, remaining = rate_limiter.check_rate_limit(
                endpoint_key,
                limit,
                window
            )
            
            if not allowed:
                logger.warning(f"🚫 Rate limit exceeded for {client_id} on {func.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(window)
                    }
                )
            
            # Ajouter headers de rate limit à la réponse
            logger.debug(f"Rate limit: {current}/{limit} for {client_id}")
            
            return await func(*args, request=request, **kwargs)
        
        return wrapper
    return decorator


# Rate limits prédéfinis pour différents types d'endpoints
def rate_limit_auth():
    """Rate limit strict pour authentification (anti-bruteforce)"""
    return rate_limit(limit=5, window=60)  # 5 tentatives/minute


def rate_limit_api():
    """Rate limit standard pour API endpoints"""
    return rate_limit(limit=100, window=60)  # 100 req/minute


def rate_limit_public():
    """Rate limit permissif pour endpoints publics"""
    return rate_limit(limit=300, window=60)  # 300 req/minute


def rate_limit_heavy():
    """Rate limit strict pour opérations lourdes"""
    return rate_limit(limit=10, window=60)  # 10 req/minute
