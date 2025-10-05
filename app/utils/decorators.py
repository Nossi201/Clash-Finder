# app/utils/decorators.py
"""
Custom decorators for Flask routes.
Includes rate limiting, logging, and utility decorators.
"""

import time
import functools
from typing import Callable, Any
from flask import request, current_app

from config.logging_config import get_logger
from app.services.rate_limiter import rate_limit as rate_limit_decorator

logger = get_logger('utils.decorators')


def log_request_time(f: Callable) -> Callable:
    """
    Decorator to log request execution time.

    Usage:
        @app.route('/endpoint')
        @log_request_time
        def my_endpoint():
            return 'response'
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Execute the function
        response = f(*args, **kwargs)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log the request
        logger.info(
            f"Request: {request.method} {request.path} | "
            f"Endpoint: {f.__name__} | "
            f"Time: {execution_time:.3f}s | "
            f"Status: {getattr(response, 'status_code', 200)}"
        )

        return response

    return decorated_function


def conditional_rate_limit(per_minute: int = 60, per_hour: int = 600):
    """
    Apply rate limiting only if enabled in config.

    Args:
        per_minute: Requests per minute
        per_hour: Requests per hour

    Usage:
        @app.route('/endpoint')
        @conditional_rate_limit(per_minute=30, per_hour=300)
        def my_endpoint():
            return 'response'
    """

    def decorator(f: Callable) -> Callable:
        # Apply rate limit decorator
        rate_limited = rate_limit_decorator(
            per_minute=per_minute,
            per_hour=per_hour
        )(f)

        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if rate limiting is enabled
            if current_app.config.get('RATE_LIMIT_ENABLED', True):
                return rate_limited(*args, **kwargs)
            else:
                # Rate limiting disabled, call function directly
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_server(f: Callable) -> Callable:
    """
    Decorator to validate server parameter.

    Usage:
        @app.route('/player/<server>')
        @validate_server
        def get_player(server):
            return f'Server: {server}'
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        from app.services.riot_api import servers_to_region

        # Get server from kwargs or args
        server = kwargs.get('server')

        if not server:
            logger.warning("No server parameter provided")
            return {'error': 'Server parameter required'}, 400

        # Validate server
        from app.utils.formatters import unslugify_server
        actual_server = unslugify_server(server)

        if actual_server.upper() not in servers_to_region:
            logger.warning(f"Invalid server: {server}")
            return {'error': f'Invalid server: {server}'}, 400

        return f(*args, **kwargs)

    return decorated_function


def validate_riot_id(f: Callable) -> Callable:
    """
    Decorator to validate Riot ID parameter.

    Usage:
        @app.route('/player/<riot_id>')
        @validate_riot_id
        def get_player(riot_id):
            return f'Riot ID: {riot_id}'
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        riot_id = kwargs.get('riot_id')

        if not riot_id:
            logger.warning("No riot_id parameter provided")
            return {'error': 'Riot ID parameter required'}, 400

        # Check format (should contain '--' separator)
        if '--' not in riot_id:
            logger.warning(f"Invalid Riot ID format: {riot_id}")
            return {'error': 'Invalid Riot ID format'}, 400

        from app.utils.formatters import decode_riot_id

        try:
            game_name, tag_line = decode_riot_id(riot_id)

            if not game_name:
                logger.warning(f"Empty game name in Riot ID: {riot_id}")
                return {'error': 'Invalid Riot ID: empty name'}, 400

        except Exception as e:
            logger.error(f"Error decoding Riot ID {riot_id}: {e}")
            return {'error': 'Invalid Riot ID format'}, 400

        return f(*args, **kwargs)

    return decorated_function


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key in request headers.

    Usage:
        @app.route('/api/endpoint')
        @require_api_key
        def api_endpoint():
            return {'data': 'value'}
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('API_KEY')

        if not expected_key:
            # No API key configured, allow access
            return f(*args, **kwargs)

        if not api_key:
            logger.warning(f"API request without key | Path: {request.path}")
            return {'error': 'API key required'}, 401

        if api_key != expected_key:
            logger.warning(f"Invalid API key | Path: {request.path}")
            return {'error': 'Invalid API key'}, 403

        return f(*args, **kwargs)

    return decorated_function


def cache_response(timeout: int = 300):
    """
    Decorator to cache response for specified timeout.

    Args:
        timeout: Cache timeout in seconds

    Usage:
        @app.route('/endpoint')
        @cache_response(timeout=600)
        def cached_endpoint():
            return {'data': 'value'}
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            from app.services.cache import cache

            # Build cache key from route and args
            cache_key = f"response:{request.path}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit for {request.path}")
                return cached_response

            # Execute function
            response = f(*args, **kwargs)

            # Cache the response
            cache.set(cache_key, response, timeout)
            logger.debug(f"Cached response for {request.path}")

            return response

        return decorated_function

    return decorator


def json_required(f: Callable) -> Callable:
    """
    Decorator to require JSON content in request.

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @json_required
        def create_resource():
            data = request.get_json()
            return {'success': True}
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            logger.warning(f"Non-JSON request to {request.path}")
            return {'error': 'Content-Type must be application/json'}, 400

        return f(*args, **kwargs)

    return decorated_function


def handle_errors(f: Callable) -> Callable:
    """
    Decorator to handle common errors and return JSON responses.

    Usage:
        @app.route('/endpoint')
        @handle_errors
        def my_endpoint():
            # May raise exceptions
            return {'data': 'value'}
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except ValueError as e:
            logger.warning(f"ValueError in {f.__name__}: {e}")
            return {'error': 'Invalid input', 'message': str(e)}, 400

        except KeyError as e:
            logger.warning(f"KeyError in {f.__name__}: {e}")
            return {'error': 'Missing required field', 'message': str(e)}, 400

        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}", exc_info=True)
            return {'error': 'Internal server error', 'message': str(e)}, 500

    return decorated_function


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin authentication.

    Usage:
        @app.route('/admin/endpoint')
        @admin_required
        def admin_endpoint():
            return 'Admin page'
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for admin session or token
        # This is a basic example - implement proper auth
        is_admin = request.headers.get('X-Admin-Token') == current_app.config.get('ADMIN_TOKEN')

        if not is_admin:
            logger.warning(f"Unauthorized admin access attempt | Path: {request.path}")
            return {'error': 'Admin access required'}, 403

        return f(*args, **kwargs)

    return decorated_function


def timing_stats(f: Callable) -> Callable:
    """
    Decorator to collect timing statistics.

    Usage:
        @app.route('/endpoint')
        @timing_stats
        def timed_endpoint():
            return 'response'
    """

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        try:
            response = f(*args, **kwargs)

            execution_time = time.time() - start_time

            # Log to metrics system if available
            logger.debug(
                f"Timing | Endpoint: {f.__name__} | "
                f"Time: {execution_time:.3f}s"
            )

            # Add timing header to response
            if hasattr(response, 'headers'):
                response.headers['X-Response-Time'] = f"{execution_time:.3f}"

            return response

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Error in {f.__name__} after {execution_time:.3f}s: {e}"
            )
            raise

    return decorated_function