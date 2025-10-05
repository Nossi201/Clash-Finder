# app/routes/debug.py
"""
Debug endpoints for development and troubleshooting.
Should be disabled or protected in production.
"""

import os
from flask import Blueprint, jsonify, current_app
from config.logging_config import get_logger
from app.utils.decorators import conditional_rate_limit

logger = get_logger('routes.debug')

# Create blueprint
debug_bp = Blueprint('debug', __name__, url_prefix='/debug')


@debug_bp.route('/check-static')
@conditional_rate_limit(per_minute=60, per_hour=300)
def check_static():
    """
    Debug endpoint to check static files configuration.

    Returns:
        JSON with static folder info and file list
    """
    logger.debug("Debug check-static endpoint accessed")

    static_folder = current_app.static_folder

    # List files in static folder
    files_in_static = []
    if static_folder and os.path.exists(static_folder):
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                rel_path = os.path.relpath(
                    os.path.join(root, file),
                    static_folder
                )
                files_in_static.append(rel_path)

    # Check specific important files
    js_path = os.path.join(static_folder, 'js', 'player_history.js') if static_folder else None

    result = {
        'static_folder': static_folder,
        'static_folder_exists': os.path.exists(static_folder) if static_folder else False,
        'files_in_static': sorted(files_in_static),
        'file_count': len(files_in_static),
        'js_file_exists': os.path.exists(js_path) if js_path else False,
        'js_path': js_path,
    }

    logger.info(f"Static files check | Folder: {static_folder} | Files: {len(files_in_static)}")

    return jsonify(result)


@debug_bp.route('/config')
@conditional_rate_limit(per_minute=30, per_hour=100)
def check_config():
    """
    Show current configuration (safe values only).

    Returns:
        JSON with configuration info
    """
    logger.debug("Debug config endpoint accessed")

    # Only show safe config values (no secrets!)
    safe_config = {
        'DEBUG': current_app.config.get('DEBUG'),
        'TESTING': current_app.config.get('TESTING'),
        'RATE_LIMIT_ENABLED': current_app.config.get('RATE_LIMIT_ENABLED'),
        'LOG_LEVEL': current_app.config.get('LOG_LEVEL'),
        'MATCHES_PER_PAGE': current_app.config.get('MATCHES_PER_PAGE'),
        'INITIAL_MATCH_LOAD': current_app.config.get('INITIAL_MATCH_LOAD'),
        'RIOT_API_KEY_SET': bool(current_app.config.get('RIOT_API_KEY')),
        'SECRET_KEY_SET': bool(current_app.config.get('SECRET_KEY')),
    }

    return jsonify(safe_config)


@debug_bp.route('/rate-limit-status')
@conditional_rate_limit(per_minute=60, per_hour=300)
def rate_limit_status():
    """
    Get current rate limit status for the requesting IP.

    Returns:
        JSON with rate limit info
    """
    try:
        from app.services.rate_limiter import get_rate_limit_status

        status = get_rate_limit_status()
        logger.debug(f"Rate limit status check | IP: {status.get('ip')}")

        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return jsonify({
            'error': 'Could not get rate limit status',
            'message': str(e)
        }), 500


@debug_bp.route('/health')
def health_check():
    """
    Simple health check endpoint.

    Returns:
        JSON with health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'clash-finder',
        'version': '1.0.0'
    })


@debug_bp.route('/routes')
@conditional_rate_limit(per_minute=30, per_hour=100)
def list_routes():
    """
    List all registered routes in the application.

    Returns:
        JSON with route list
    """
    routes = []

    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })

    # Sort by endpoint
    routes.sort(key=lambda x: x['endpoint'])

    logger.debug(f"Routes list requested | Total: {len(routes)}")

    return jsonify({
        'total_routes': len(routes),
        'routes': routes
    })


# Disable debug routes in production
@debug_bp.before_request
def check_debug_mode():
    """Ensure debug endpoints are only accessible in debug mode."""
    if not current_app.config.get('DEBUG') and not current_app.config.get('TESTING'):
        logger.warning("Debug endpoint accessed in production mode")
        return jsonify({
            'error': 'Debug endpoints are disabled in production'
        }), 403