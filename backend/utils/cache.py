import time
import functools
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Simple in-memory cache: {key: (value, expiry_timestamp)}
_cache: Dict[str, Tuple[Any, float]] = {}

def cache(ttl_seconds: int = 300):
    """
    Simple in-memory cache decorator with error handling.
    :param ttl_seconds: Time to live in seconds (default 5 minutes)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = None
            try:
                # Generate key
                key_parts = [func.__name__]

                # Handle positional args (important pour différencier les appels)
                for i, arg in enumerate(args):
                    # Skip 'self' parameter (first arg of instance methods)
                    # Check if it looks like a self parameter (has methods but isn't a basic type)
                    if i == 0 and hasattr(arg, '__dict__') and not isinstance(arg, (str, int, float, bool, list, dict, tuple)):
                        continue
                    # Ajouter les args simples à la clé
                    if isinstance(arg, (str, int, float, bool)):
                        key_parts.append(str(arg))
                    elif isinstance(arg, (list, tuple)):
                        key_parts.append(str(sorted(arg) if isinstance(arg, list) else arg))
                    elif isinstance(arg, dict):
                        key_parts.append(str(sorted(arg.items())))

                # Handle kwargs
                for k, v in sorted(kwargs.items()):
                    if k == 'request':
                        # Skip Request object or use path/query
                        if hasattr(v, 'url'):
                            key_parts.append(str(v.url))
                    elif k == 'response':
                        continue
                    elif k == 'payload' and isinstance(v, dict):
                        # Include user_id from payload if present
                        if 'id' in v:
                            key_parts.append(f"user:{v['id']}")
                        elif 'sub' in v:
                            key_parts.append(f"user:{v['sub']}")
                    else:
                        key_parts.append(f"{k}:{str(v)}")

                cache_key = "|".join(key_parts)

                # Try to get from cache
                now = time.time()
                if cache_key in _cache:
                    try:
                        value, expiry = _cache[cache_key]
                        if now < expiry:
                            logger.debug(f"Cache hit: {func.__name__}")
                            return value
                        else:
                            # Expired, remove it
                            del _cache[cache_key]
                    except Exception as e:
                        logger.warning(f"Cache read error for {cache_key}: {e}")
                        # If cache read fails, just continue to execute function
                        pass

            except Exception as e:
                logger.warning(f"Cache key generation error: {e}")
                # If key generation fails, execute function without caching
                cache_key = None

            # Execute the actual function
            try:
                result = await func(*args, **kwargs)

                # Try to cache the result
                if cache_key:
                    try:
                        now = time.time()
                        _cache[cache_key] = (result, now + ttl_seconds)
                    except Exception as e:
                        logger.warning(f"Cache write error for {cache_key}: {e}")
                        # If cache write fails, just return result without caching
                        pass

                return result

            except Exception as e:
                # Don't catch function errors, let them propagate
                raise

        return wrapper
    return decorator

def clear_cache():
    """Clear all cached values"""
    _cache.clear()
    logger.info("🧹 Cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    try:
        now = time.time()
        total_entries = len(_cache)
        expired_entries = sum(1 for _, (_, expiry) in _cache.items() if now >= expiry)
        active_entries = total_entries - expired_entries

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_size_bytes": sum(
                len(str(k)) + len(str(v[0]))
                for k, v in _cache.items()
            )
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "error": str(e),
            "total_entries": 0,
            "active_entries": 0
        }


def cleanup_expired():
    """Remove expired entries from cache"""
    try:
        now = time.time()
        expired_keys = [k for k, (_, expiry) in _cache.items() if now >= expiry]

        for key in expired_keys:
            del _cache[key]

        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
        return 0
