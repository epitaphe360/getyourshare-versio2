"""
Cache Service - Redis caching pour optimisation performances avec Singleton Pattern
"""

import os
import json
import logging
from typing import Optional, Any, Callable, Dict
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

# Configuration Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"


class CacheService:
    """
    Service de cache avec fallback mémoire si Redis indisponible
    Utilise le pattern Singleton pour une instance unique
    """

    _instance: Optional['CacheService'] = None
    _memory_cache: Dict[str, Any] = {}

    def __new__(cls):
        """Singleton pattern - garantit une seule instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # N'initialiser qu'une seule fois
        if self._initialized:
            return

        self.redis_client = None
        self.use_redis = CACHE_ENABLED

        if self.use_redis:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(
                    REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("✅ Redis cache activé")
            except ImportError:
                logger.warning("⚠️ redis package non installé - utilisation cache mémoire")
                self.use_redis = False
            except Exception as e:
                logger.warning(f"⚠️ Redis non disponible: {e} - utilisation cache mémoire")
                self.use_redis = False
        else:
            logger.info("ℹ️ Cache désactivé par configuration")

        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'CacheService':
        """Obtenir l'instance unique du service de cache"""
        if cls._instance is None:
            cls._instance = CacheService()
        return cls._instance
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""

        if not CACHE_ENABLED:
            return None

        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"✅ Cache HIT: {key}")
                    return json.loads(value)
            else:
                # Fallback mémoire
                if key in self._memory_cache:
                    logger.debug(f"✅ Memory cache HIT: {key}")
                    return self._memory_cache[key]

            logger.debug(f"❌ Cache MISS: {key}")
            return None

        except Exception as e:
            logger.error(f"❌ Erreur lecture cache {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """
        Enregistre une valeur dans le cache

        Args:
            key: Clé du cache
            value: Valeur à cacher (sera JSON-encodée)
            ttl: Durée de vie en secondes (défaut: 5 minutes)
        """

        if not CACHE_ENABLED:
            return

        try:
            json_value = json.dumps(value)

            if self.use_redis and self.redis_client:
                await self.redis_client.setex(key, ttl, json_value)
                logger.debug(f"✅ Cache SET: {key} (TTL: {ttl}s)")
            else:
                # Fallback mémoire (pas de TTL automatique)
                self._memory_cache[key] = value
                logger.debug(f"✅ Memory cache SET: {key}")

                # Limiter taille cache mémoire
                if len(self._memory_cache) > 1000:
                    # Supprimer les 200 premières entrées
                    keys_to_remove = list(self._memory_cache.keys())[:200]
                    for k in keys_to_remove:
                        del self._memory_cache[k]

        except Exception as e:
            logger.error(f"❌ Erreur écriture cache {key}: {e}")
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""

        if not CACHE_ENABLED:
            return

        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(key)
                logger.debug(f"✅ Cache DELETE: {key}")
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    logger.debug(f"✅ Memory cache DELETE: {key}")

        except Exception as e:
            logger.error(f"❌ Erreur suppression cache {key}: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Supprime toutes les clés matchant un pattern (ex: 'user:123:*')"""

        if not CACHE_ENABLED:
            return

        try:
            if self.use_redis and self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"✅ Cache cleared: {len(keys)} keys matching {pattern}")
            else:
                # Fallback mémoire
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                for k in keys_to_delete:
                    del self._memory_cache[k]
                logger.info(f"✅ Memory cache cleared: {len(keys_to_delete)} keys")

        except Exception as e:
            logger.error(f"❌ Erreur clear pattern {pattern}: {e}")
    
    async def close(self):
        """Ferme la connexion Redis"""
        if self.redis_client:
            await self.redis_client.close()


def get_cache_instance() -> CacheService:
    """
    Fonction helper pour obtenir l'instance unique du cache
    Remplace l'ancienne variable globale 'cache'
    """
    return CacheService.get_instance()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Décorateur pour cacher le résultat d'une fonction

    Usage:
        @cached(ttl=600, key_prefix="analytics")
        async def get_analytics(user_id: str):
            return {"data": "..."}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtenir instance du cache
            cache_instance = get_cache_instance()

            # Générer clé de cache
            cache_key_parts = [key_prefix or func.__name__]

            # Ajouter arguments à la clé
            for arg in args:
                if isinstance(arg, (str, int)):
                    cache_key_parts.append(str(arg))

            for k, v in kwargs.items():
                if isinstance(v, (str, int)):
                    cache_key_parts.append(f"{k}:{v}")

            cache_key = ":".join(cache_key_parts)

            # Vérifier cache
            cached_result = await cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Exécuter fonction
            result = await func(*args, **kwargs)

            # Cacher résultat
            await cache_instance.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Helper pour invalidation cache user
async def invalidate_user_cache(user_id: str):
    """Invalide tout le cache pour un utilisateur"""
    cache_instance = get_cache_instance()
    await cache_instance.clear_pattern(f"*:{user_id}:*")
    await cache_instance.clear_pattern(f"user:{user_id}:*")
    logger.info(f"✅ Cache invalidé pour user {user_id}")


# Helper pour invalidation cache analytics
async def invalidate_analytics_cache(user_id: str = None):
    """Invalide le cache analytics (optionnellement pour un user)"""
    cache_instance = get_cache_instance()
    if user_id:
        await cache_instance.clear_pattern(f"analytics:*:{user_id}:*")
    else:
        await cache_instance.clear_pattern("analytics:*")
    logger.info(f"✅ Cache analytics invalidé")
