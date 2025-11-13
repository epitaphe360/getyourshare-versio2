"""
Advanced Caching Strategy - Multi-niveaux
Redis + Memory + CDN avec invalidation intelligente
"""
import os
import json
import hashlib
from typing import Any, Optional, Callable, List
from datetime import timedelta
from functools import wraps
import redis
from cachetools import TTLCache, LRUCache

from utils.logger import logger


class AdvancedCachingStrategy:
    """Système de cache multi-niveaux avec stratégies avancées"""

    def __init__(self):
        # Niveau 1: Cache mémoire (le plus rapide)
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min
        self.lru_cache = LRUCache(maxsize=5000)

        # Niveau 2: Redis (partagé entre instances)
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            self.redis_available = self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.warning(f"❌ Redis not available: {e}")
            self.redis_available = False

        # Configuration TTL par type de données
        self.ttl_config = {
            'static': 86400 * 7,      # 7 jours (images, CSS, JS)
            'product': 3600,           # 1 heure (produits)
            'user': 1800,              # 30 min (profils utilisateurs)
            'analytics': 300,          # 5 min (analytics)
            'api': 60,                 # 1 min (API responses)
            'session': 86400,          # 24h (sessions)
            'permanent': 86400 * 30    # 30 jours
        }

    def cache(
        self,
        key: str,
        ttl: int = 300,
        cache_type: str = 'api',
        use_memory: bool = True,
        use_redis: bool = True
    ):
        """
        Décorateur de cache multi-niveaux

        Usage:
            @cache_service.cache(key='product:{product_id}', cache_type='product')
            def get_product(product_id):
                return expensive_db_query(product_id)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Générer clé de cache unique
                cache_key = self._generate_cache_key(key, args, kwargs)

                # Niveau 1: Chercher en mémoire (le plus rapide)
                if use_memory:
                    cached_value = self._get_from_memory(cache_key)
                    if cached_value is not None:
                        logger.debug(f"Cache HIT (memory): {cache_key}")
                        return cached_value

                # Niveau 2: Chercher dans Redis
                if use_redis and self.redis_available:
                    cached_value = self._get_from_redis(cache_key)
                    if cached_value is not None:
                        logger.debug(f"Cache HIT (redis): {cache_key}")
                        # Promouvoir vers mémoire
                        if use_memory:
                            self._set_in_memory(cache_key, cached_value, ttl)
                        return cached_value

                # Cache MISS: Exécuter fonction
                logger.debug(f"Cache MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Stocker dans les caches
                actual_ttl = self.ttl_config.get(cache_type, ttl)

                if use_redis and self.redis_available:
                    self._set_in_redis(cache_key, result, actual_ttl)

                if use_memory:
                    self._set_in_memory(cache_key, result, actual_ttl)

                return result

            return wrapper
        return decorator

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Récupérer une valeur du cache (memory → redis)"""
        # Mémoire d'abord
        value = self._get_from_memory(key)
        if value is not None:
            return value

        # Redis ensuite
        if self.redis_available:
            value = self._get_from_redis(key)
            if value is not None:
                # Promouvoir vers mémoire
                self._set_in_memory(key, value, 300)
                return value

        return default

    def set(self, key: str, value: Any, ttl: int = 300, cache_type: str = 'api'):
        """Stocker une valeur dans le cache"""
        actual_ttl = self.ttl_config.get(cache_type, ttl)

        # Stocker dans les deux niveaux
        self._set_in_memory(key, value, actual_ttl)

        if self.redis_available:
            self._set_in_redis(key, value, actual_ttl)

        logger.debug(f"Cache SET: {key} (TTL: {actual_ttl}s)")

    def delete(self, key: str):
        """Supprimer une clé du cache (tous niveaux)"""
        # Mémoire
        if key in self.memory_cache:
            del self.memory_cache[key]
        if key in self.lru_cache:
            del self.lru_cache[key]

        # Redis
        if self.redis_available:
            self.redis_client.delete(key)

        logger.debug(f"Cache DELETE: {key}")

    def invalidate_pattern(self, pattern: str):
        """
        Invalider toutes les clés correspondant à un pattern

        Example: invalidate_pattern('product:*')
        """
        # Mémoire (scan manuel)
        keys_to_delete = [
            k for k in self.memory_cache.keys()
            if self._match_pattern(k, pattern)
        ]
        for key in keys_to_delete:
            del self.memory_cache[key]

        # Redis (scan avec MATCH)
        if self.redis_available:
            cursor = 0
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    self.redis_client.delete(*keys)

                if cursor == 0:
                    break

        logger.info(f"Cache INVALIDATE pattern: {pattern}")

    def clear_all(self):
        """Vider tout le cache"""
        self.memory_cache.clear()
        self.lru_cache.clear()

        if self.redis_available:
            self.redis_client.flushdb()

        logger.warning("Cache CLEARED (all levels)")

    def get_stats(self) -> dict:
        """Statistiques de cache"""
        stats = {
            'memory_cache': {
                'size': len(self.memory_cache),
                'maxsize': self.memory_cache.maxsize,
                'hits': getattr(self.memory_cache, 'hits', 0),
                'misses': getattr(self.memory_cache, 'misses', 0)
            },
            'lru_cache': {
                'size': len(self.lru_cache),
                'maxsize': self.lru_cache.maxsize
            }
        }

        if self.redis_available:
            redis_info = self.redis_client.info('stats')
            stats['redis'] = {
                'hits': redis_info.get('keyspace_hits', 0),
                'misses': redis_info.get('keyspace_misses', 0),
                'keys': self.redis_client.dbsize(),
                'memory': redis_info.get('used_memory_human', 'N/A')
            }

        return stats

    # Cache warming (préchauffage)
    def warm_cache(self, keys_and_functions: List[tuple]):
        """
        Préchauffer le cache avec des données fréquemment accédées

        Usage:
            cache_service.warm_cache([
                ('top_products', get_top_products),
                ('featured_deals', get_featured_deals)
            ])
        """
        logger.info(f"Warming cache with {len(keys_and_functions)} entries...")

        for key, func in keys_and_functions:
            try:
                result = func()
                self.set(key, result, cache_type='permanent')
                logger.debug(f"Cache warmed: {key}")
            except Exception as e:
                logger.error(f"Cache warm failed for {key}: {e}")

    # Méthodes privées
    def _generate_cache_key(self, template: str, args: tuple, kwargs: dict) -> str:
        """Générer une clé de cache unique"""
        # Remplacer placeholders avec args/kwargs
        key = template

        # Remplacer {arg_name} avec valeurs kwargs
        for k, v in kwargs.items():
            key = key.replace(f'{{{k}}}', str(v))

        # Si encore des placeholders, utiliser args
        if '{' in key:
            # Fallback: hash des arguments
            args_str = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            key = f"{key}:{args_hash}"

        return key

    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Récupérer de la mémoire"""
        # TTL cache d'abord
        if key in self.memory_cache:
            return self.memory_cache[key]

        # LRU cache ensuite
        if key in self.lru_cache:
            return self.lru_cache[key]

        return None

    def _set_in_memory(self, key: str, value: Any, ttl: int):
        """Stocker en mémoire"""
        # TTL cache pour données temporaires
        if ttl < 3600:  # < 1h
            self.memory_cache[key] = value
        else:
            # LRU cache pour données plus persistantes
            self.lru_cache[key] = value

    def _get_from_redis(self, key: str) -> Optional[Any]:
        """Récupérer de Redis"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")

        return None

    def _set_in_redis(self, key: str, value: Any, ttl: int):
        """Stocker dans Redis"""
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Matcher un pattern (simple wildcard)"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


# CDN Cache Headers Helper
class CDNCacheHeaders:
    """Génération de headers HTTP pour cache CDN"""

    @staticmethod
    def get_headers(cache_type: str = 'static', max_age: int = None) -> dict:
        """
        Générer headers Cache-Control optimaux pour CDN

        Types:
            - static: Images, CSS, JS (immutable)
            - dynamic: HTML, API responses
            - private: Données utilisateur
            - no-cache: Données sensibles
        """
        presets = {
            'static': {
                'Cache-Control': 'public, max-age=31536000, immutable',
                'Expires': '1 year',
                'Vary': 'Accept-Encoding'
            },
            'dynamic': {
                'Cache-Control': 'public, max-age=3600, must-revalidate',
                'Expires': '1 hour',
                'Vary': 'Accept-Encoding, Accept'
            },
            'private': {
                'Cache-Control': 'private, max-age=300',
                'Expires': '5 minutes',
                'Vary': 'Cookie'
            },
            'no-cache': {
                'Cache-Control': 'no-store, no-cache, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            'api': {
                'Cache-Control': 'public, max-age=60, stale-while-revalidate=300',
                'Vary': 'Accept, Accept-Encoding'
            }
        }

        headers = presets.get(cache_type, presets['dynamic'])

        # Override max-age si spécifié
        if max_age is not None:
            headers['Cache-Control'] = f"public, max-age={max_age}"

        return headers


# Instances globales
cache_service = AdvancedCachingStrategy()
cdn_headers = CDNCacheHeaders()


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple 1: Décorateur
    @cache_service.cache(key='product:{product_id}', cache_type='product')
    def get_product(product_id):
        logger.info(f"Fetching product {product_id} from database...")
        return {'id': product_id, 'name': 'iPhone 15'}

    # Exemple 2: Get/Set manuel
    cache_service.set('user:123', {'name': 'John'}, cache_type='user')
    user = cache_service.get('user:123')

    # Exemple 3: Invalidation
    cache_service.invalidate_pattern('product:*')

    # Exemple 4: Stats
    logger.info(cache_service.get_stats())
