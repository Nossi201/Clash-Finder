# app/services/rate_limiter.py
"""
Rate limiting service for Clash Finder.
Provides in-memory rate limiting without Redis dependency.
"""

import time
from typing import Optional, Callable, Any
from functools import wraps
from collections import defaultdict
from threading import Lock
from flask import request, jsonify, current_app

from config.logging_config import get_logger

logger = get_logger('services.rate_limiter')


class InMemoryRateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        """Initialize in-memory rate limiter."""
        self.storage: dict[str, dict[str, Any]] = defaultdict(dict)
        self.lock = Lock()
        self._initialized = True

        logger.info("In-memory rate limiter initialized")

    def _cleanup_old_entries(self):
        """Remove expired entries to prevent memory leak."""
        current_time = time.time()
        with self.lock:
            keys_to_delete = []
            for key, data in self.storage.items():
                if data.get('reset_time', 0) < current_time:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del self.storage[key]

    def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is within rate limit.

        Args:
            key: Unique identifier for rate limit (e.g., IP address)
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, info_dict)
        """
        current_time = time.time()

        # Periodic cleanup
        if len(self.storage) > 10000:
            self._cleanup_old_entries()

        with self.lock:
            if key not in self.storage:
                self.storage[key] = {
                    'count': 1,
                    'reset_time': current_time + window,
                    'window': window
                }
                return True, {
                    'limit': limit,
                    'remaining': limit - 1,
                    'reset': int(current_time + window)
                }

            data = self.storage[key]

            # Check if window expired
            if current_time >= data['reset_time']:
                self.storage[key] = {
                    'count': 1,
                    'reset_time': current_time + window,
                    'window': window
                }
                return True, {
                    'limit': limit,
                    'remaining': limit - 1,
                    'reset': int(current_time + window)
                }

            # Within window
            if data['count'] < limit:
                data['count'] += 1
                return True, {
                    'limit': limit,
                    'remaining': limit - data['count'],
                    'reset': int(data['reset_time'])
                }

            # Rate limit exceeded
            return False, {
                'limit': limit,
                'remaining': 0,
                'reset': int(data['reset_time']),
                'retry_after': int(data['reset_time'] - current_time)
            }

    def get_status(self, key: str) -> dict[str, Any]:
        """Get current rate limit status for a key."""
        current_time = time.time()

        with self.lock:
            if key not in self.storage:
                return {
                    'count': 0,
                    'reset_time': None,
                    'is_active': False
                }

            data = self.storage[key]

            if current_time >= data['reset_time']:
                return {
                    'count': 0,
                    'reset_time': None,
                    'is_active': False
                }

            return {
                'count': data['count'],
                'reset_time': data['reset_time'],
                'is_active': True,
                'seconds_remaining': int(data['reset_time'] - current_time)
            }

    def reset(self, key: str):
        """Reset rate limit for key."""
        with self.lock:
            if key in self.storage:
                del self.storage[key]
        logger.debug(f"Rate limit reset: {key}")

    def clear(self):
        """Clear all rate limit data."""
        with self.lock:
            self.storage.clear()
        logger.info("Rate limiter cleared")


class RateLimiterManager:
    """Central rate limiter manager."""

    def __init__(self):
        """Initialize rate limiter manager."""
        self.backend: Optional[InMemoryRateLimiter] = None
        self._initialized = False
        self.enabled = True

    def init_app(self, app):
        """Initialize rate limiter with Flask app."""
        self.enabled = app.config.get('RATE_LIMIT_ENABLED', True)

        if self.enabled:
            self.backend = InMemoryRateLimiter()
            logger.info("Rate limiter initialized with in-memory backend")
        else:
            logger.info("Rate limiting disabled")

        self._initialized = True

    def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, dict[str, Any]]:
        """Check rate limit."""
        if not self.enabled or not self.backend:
            return True, {'limit': limit, 'remaining': limit, 'reset': 0}

        return self.backend.check_rate_limit(key, limit, window)

    def reset(self, key: str):
        """Reset rate limit."""
        if self.backend:
            self.backend.reset(key)

    def clear(self):
        """Clear all rate limits."""
        if self.backend:
            self.backend.clear()

    def get_status(self, key: str) -> dict[str, Any]:
        """Get status."""
        if not self.backend:
            return {}
        return self.backend.get_status(key)


# Global rate limiter instance
rate_limiter = RateLimiterManager()


def get_client_ip() -> str:
    """
    Get client IP address from request.
    Handles X-Forwarded-For for proxies.
    """
    if request.headers.get('X-Forwarded-For'):
        # Get first IP from X-Forwarded-For chain
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()

    return request.remote_addr or 'unknown'


def rate_limit(per_minute: int = 60, per_hour: int = 600):
    """
    Decorator to apply rate limiting to routes.

    Args:
        per_minute: Requests allowed per minute
        per_hour: Requests allowed per hour

    Usage:
        @app.route('/api/data')
        @rate_limit(per_minute=30, per_hour=300)
        def get_data():
            return {'data': 'value'}
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)

            client_ip = get_client_ip()

            # Check minute limit
            minute_key = f"{client_ip}:{request.endpoint}:minute"
            allowed, info = rate_limiter.check_rate_limit(minute_key, per_minute, 60)

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded (minute) | IP: {client_ip} | "
                    f"Endpoint: {request.endpoint}"
                )
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': info.get('retry_after', 60)
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(per_minute)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(info.get('reset', ''))
                response.headers['Retry-After'] = str(info.get('retry_after', 60))
                return response

            # Check hour limit
            hour_key = f"{client_ip}:{request.endpoint}:hour"
            allowed, info = rate_limiter.check_rate_limit(hour_key, per_hour, 3600)

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded (hour) | IP: {client_ip} | "
                    f"Endpoint: {request.endpoint}"
                )
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': info.get('retry_after', 3600)
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(per_hour)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(info.get('reset', ''))
                response.headers['Retry-After'] = str(info.get('retry_after', 3600))
                return response

            # Add rate limit headers to successful response
            response = f(*args, **kwargs)

            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit-Minute'] = str(per_minute)
                response.headers['X-RateLimit-Remaining-Minute'] = str(info.get('remaining', per_minute))
                response.headers['X-RateLimit-Limit-Hour'] = str(per_hour)

            return response

        return decorated_function

    return decorator


def get_rate_limit_status() -> dict[str, Any]:
    """
    Get current rate limit status for the requesting client.

    Returns:
        Dictionary with rate limit information
    """
    client_ip = get_client_ip()

    # Get status for common endpoints
    endpoints_to_check = [
        'player.player_stats',
        'clash.clash_team',
        'main.cheker',
        'player.load_more_matches'
    ]

    status = {
        'ip': client_ip,
        'endpoints': {}
    }

    for endpoint in endpoints_to_check:
        minute_key = f"{client_ip}:{endpoint}:minute"
        hour_key = f"{client_ip}:{endpoint}:hour"

        status['endpoints'][endpoint] = {
            'minute': rate_limiter.get_status(minute_key),
            'hour': rate_limiter.get_status(hour_key)
        }

    return status