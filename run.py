#!/usr/bin/env python3
# run.py
"""
Entry point for Clash Finder application.
Starts the Flask development server.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from config.logging_config import get_logger
from config.ssl_config import SSLConfig

logger = get_logger('run')


def main():
    """Main entry point."""
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')

    # Create application
    app = create_app(env)

    # Get configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = app.config.get('DEBUG', False)

    # SSL context
    ssl_context = None
    if SSLConfig.SSL_ENABLED:
        try:
            ssl_context = SSLConfig.get_ssl_context()
            logger.info("SSL enabled")
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            logger.warning("Running without SSL")

    # Log startup info
    protocol = 'https' if ssl_context else 'http'
    logger.info(f"Starting server on {protocol}://{host}:{port}")
    logger.info(f"Environment: {env}")
    logger.info(f"Debug mode: {debug}")

    # Run application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            ssl_context=ssl_context,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()