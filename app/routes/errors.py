# app/routes/errors.py
"""
Error handlers for Flask application.
Handles 404, 429, 500, and other HTTP errors.
"""

from flask import render_template, jsonify, request
from config.logging_config import get_logger
from app.services.riot_api import servers_to_region

logger = get_logger('errors')


def handle_404(error):
    """
    Handle 404 Not Found errors.

    Args:
        error: Flask error object

    Returns:
        Rendered error page or JSON response
    """
    logger.warning(f"404 error | Path: {request.path} | IP: {request.remote_addr}")

    # Return JSON for API requests
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'path': request.path
        }), 404

    # Return HTML page for regular requests
    return render_template(
        'index.html',
        error_message="Page not found.",
        servers=servers_to_region.keys()
    ), 404


def handle_429(error):
    """
    Handle 429 Rate Limit Exceeded errors.

    Args:
        error: Flask error object

    Returns:
        JSON response with rate limit info
    """
    logger.warning(f"429 rate limit | Path: {request.path} | IP: {request.remote_addr}")

    return jsonify({
        'error': 'Too Many Requests',
        'message': 'You have exceeded the rate limit. Please wait before trying again.',
        'retry_after': error.description if hasattr(error, 'description') else 60
    }), 429


def handle_500(error):
    """
    Handle 500 Internal Server Error.

    Args:
        error: Flask error object

    Returns:
        Rendered error page or JSON response
    """
    logger.error(f"500 error | Path: {request.path} | Error: {error}", exc_info=True)

    # Return JSON for API requests
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500

    # Return HTML page for regular requests
    return render_template(
        'index.html',
        error_message="Internal server error. Please try again later.",
        servers=servers_to_region.keys()
    ), 500


def handle_400(error):
    """
    Handle 400 Bad Request errors.

    Args:
        error: Flask error object

    Returns:
        JSON response with error details
    """
    logger.warning(f"400 error | Path: {request.path} | IP: {request.remote_addr}")

    return jsonify({
        'error': 'Bad Request',
        'message': 'Invalid request data',
        'details': str(error.description) if hasattr(error, 'description') else None
    }), 400


def handle_403(error):
    """
    Handle 403 Forbidden errors.

    Args:
        error: Flask error object

    Returns:
        JSON response
    """
    logger.warning(f"403 error | Path: {request.path} | IP: {request.remote_addr}")

    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403