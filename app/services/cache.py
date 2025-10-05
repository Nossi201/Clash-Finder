# app/services/cache.py
"""
Caching service for Clash Finder.
Provides in-memory caching without Redis dependency.
"""

import time
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta

from config.logging_config import get_logger

logger = get_logger('services.cache')


class InMemoryCache:
    """Simple in-memory cache implementation."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize in-memory cache.

        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._initialized = True

        logger.info(f"In-memory cache initialized | Max size: {max_size} | Default TTL: {default_ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

        entry = self._cache[key]
        if entry['expires_at'] < time.time():
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        self._hits += 1
        logger.debug(f"Cache hit: {key}")
        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if ttl is None:
            ttl = self._default_ttl

        # Evict oldest if at max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_oldest()

        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }

        logger.debug(f"Cache set: {key} | TTL: {ttl}s")
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache cleared | Removed {count} entries")
        return True

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        if entry['expires_at'] < time.time():
            del self._cache[key]
            return False

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'size': len(self._cache),
            'max_size': self._max_size
        }

    def _evict_oldest(self):
        """Evict oldest cache entry."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]['created_at']
        )
        del self._cache[oldest_key]
        logger.debug(f"Evicted oldest entry: {oldest_key}")


class CacheManager:
    """Central cache manager."""

    def __init__(self):
        """Initialize cache manager."""
        self.backend: Optional[InMemoryCache] = None
        self._initialized = False

    def init_app(self, app):
        """Initialize cache with Flask app."""
        cache_type = app.config.get('CACHE_TYPE', 'simple')

        if cache_type == 'simple':
            max_size = app.config.get('CACHE_MAX_SIZE', 1000)
            default_ttl = app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            self.backend = InMemoryCache(max_size, default_ttl)
            logger.info("Cache initialized with in-memory backend")
        else:
            logger.warning(f"Unknown cache type: {cache_type}, using in-memory")
            self.backend = InMemoryCache()

        self._initialized = True

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.backend:
            return None
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.backend:
            return False
        return self.backend.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.backend:
            return False
        return self.backend.delete(key)

    def clear(self) -> bool:
        """Clear all cache."""
        if not self.backend:
            return False
        return self.backend.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.backend:
            return False
        return self.backend.exists(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self.backend:
            return {}
        return self.backend.get_stats()


# Global cache instance
cache = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ''):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=600, key_prefix='user')
        def get_user(user_id):
            return fetch_user(user_id)
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, f.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ':'.join(filter(None, key_parts))

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = f(*args, **kwargs)

            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result

        return decorated_function

    return decorator


def invalidate_cache(pattern: str = None):
    """
    Invalidate cache entries.

    Args:
        pattern: Pattern to match keys (None = clear all)
    """
    if pattern:
        # In-memory cache doesn't support pattern matching
        # Just log a warning
        logger.warning(f"Pattern-based invalidation not supported in in-memory cache: {pattern}")
    else:
        cache.clear()
        logger.info("Cache cleared")


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    return cache.get_stats()