import time
import functools
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Simple in-memory cache: {key: (value, expiry_timestamp)}
_cache: Dict[str, Tuple[Any, float]] = {}

def cache(ttl_seconds: int = 300):
    """
    Simple in-memory cache decorator.
    :param ttl_seconds: Time to live in seconds (default 5 minutes)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate key
            key_parts = [func.__name__]
            
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
            
            now = time.time()
            if cache_key in _cache:
                value, expiry = _cache[cache_key]
                if now < expiry:
                    # logger.debug(f"⚡ Cache hit for {cache_key}")
                    return value
                else:
                    del _cache[cache_key]
            
            result = await func(*args, **kwargs)
            
            _cache[cache_key] = (result, now + ttl_seconds)
            return result
        return wrapper
    return decorator

def clear_cache():
    _cache.clear()
    logger.info("🧹 Cache cleared")
