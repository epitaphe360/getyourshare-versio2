"""
Cache Decorators - Application automatique du cache sur les endpoints
Usage:
    from utils.cache_decorator import cached_endpoint, cache_invalidate

    @router.get("/stats")
    @cached_endpoint(ttl=300, key_prefix="stats")
    async def get_stats(current_user = Depends(get_current_user)):
        ...
"""

import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def _make_cache_key(prefix: str, *args, **kwargs) -> str:
    """Génère une clé de cache unique et déterministe"""
    try:
        key_data = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
        suffix = hashlib.md5(key_data.encode()).hexdigest()[:12]
    except Exception:
        suffix = "default"
    return f"gys:{prefix}:{suffix}"


def cached_endpoint(ttl: int = 300, key_prefix: str = "endpoint", per_user: bool = True):
    """
    Décorateur qui met en cache la réponse d'un endpoint FastAPI.

    Args:
        ttl: Durée de vie du cache en secondes (défaut: 5 min)
        key_prefix: Préfixe de la clé de cache
        per_user: Si True, cache séparé par user_id
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from cache_service import CacheService
            cache = CacheService.get_instance()

            # Extraire user_id si per_user=True
            user_suffix = ""
            if per_user:
                current_user = kwargs.get("current_user", {})
                if isinstance(current_user, dict):
                    user_suffix = current_user.get("id", "anon")

            # Construire la clé de cache (exclure l'objet `request` non-sérialisable)
            safe_kwargs = {k: v for k, v in kwargs.items()
                          if k not in ("current_user", "request", "db", "background_tasks")}
            cache_key = _make_cache_key(f"{key_prefix}:{user_suffix}", **safe_kwargs)

            # Tenter de lire depuis le cache
            cached = await cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached

            # Appeler la fonction réelle
            result = await func(*args, **kwargs)

            # Stocker le résultat (sérialiser si nécessaire)
            try:
                await cache.set(cache_key, result, ttl=ttl)
            except Exception as e:
                logger.debug(f"Cache SET failed for {cache_key}: {e}")

            return result
        return wrapper
    return decorator


def cached_value(ttl: int = 60):
    """
    Décorateur pour fonctions synchrones ou async qui retournent une valeur simple.
    Utile pour les calculs lourds (agrégations, stats...).
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from cache_service import CacheService
            cache = CacheService.get_instance()
            key = _make_cache_key(f"fn:{func.__name__}", *args, **kwargs)

            cached = await cache.get(key)
            if cached is not None:
                return cached

            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(key, result, ttl=ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Version synchrone — pas de cache async, appel direct
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


async def cache_invalidate_pattern(pattern: str):
    """
    Invalide toutes les clés correspondant au pattern dans Redis.
    Exemple: cache_invalidate_pattern("gys:stats:*")
    """
    try:
        from cache_service import CacheService
        cache = CacheService.get_instance()
        if cache.use_redis and cache.redis_client:
            keys = await cache.redis_client.keys(f"gys:{pattern}:*")
            if keys:
                await cache.redis_client.delete(*keys)
                logger.info(f"Cache invalidé: {len(keys)} clés supprimées (pattern={pattern})")
        else:
            # Fallback mémoire : supprimer les clés correspondantes
            prefix = f"gys:{pattern}"
            keys_to_remove = [k for k in cache._memory_cache if k.startswith(prefix)]
            for k in keys_to_remove:
                del cache._memory_cache[k]
            if keys_to_remove:
                logger.info(f"Memory cache invalidé: {len(keys_to_remove)} clés (pattern={pattern})")
    except Exception as e:
        logger.error(f"Erreur invalidation cache pattern={pattern}: {e}")


# ====================================================
# CLÉS DE CACHE PRÉDÉFINIS (TTL optimaux par type)
# ====================================================
CACHE_TTL = {
    "subscription_plans": 3600,    # 1h — changent rarement
    "products_list": 300,          # 5 min
    "product_detail": 600,         # 10 min
    "dashboard_stats": 180,        # 3 min
    "analytics_charts": 300,       # 5 min
    "influencer_list": 600,        # 10 min
    "merchant_list": 600,          # 10 min
    "notifications_count": 30,     # 30 sec
    "user_profile": 300,           # 5 min
    "top_products": 900,           # 15 min
}
