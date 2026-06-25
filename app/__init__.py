# app/__init__.py
"""
Flask application factory for Clash Finder.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import get_config
from config.logging_config import setup_logging, get_logger
from config.ssl_config import SSLConfig
from app.template_filters import register_template_filters

csrf = CSRFProtect()

logger = get_logger('app.factory')


def create_app(config_name=None):
    """
    Application factory pattern.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize configuration
    config_class.init_app(app)

    # Setup logging
    setup_logging(
        app=app,
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        enable_console=True,
        enable_file=True
    )

    logger.info(f"Starting Clash Finder | Environment: {config_name or 'default'}")

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Setup SSL/Security
    SSLConfig.init_app(app)

    # Setup context processors
    register_context_processors(app)

    # Register template filters
    register_template_filters(app)

    # Setup request/response handlers
    register_request_handlers(app)

    logger.info("Application initialized successfully")

    return app


def initialize_extensions(app):
    """
    Initialize Flask extensions.

    Args:
        app: Flask application instance
    """
    from app.services import cache, rate_limiter, auto_updater, init_updater

    # Initialize CSRF protection
    csrf.init_app(app)
    logger.info("CSRF protection initialized")

    # Initialize cache
    cache.init_app(app)
    logger.info("Cache initialized")

    # Initialize rate limiter
    rate_limiter.init_app(app)
    logger.info("Rate limiter initialized")

    # Initialize auto updater
    if app.config.get('AUTO_UPDATE_RESOURCES', True):
        init_updater(
            app,
            check_interval_hours=app.config.get('UPDATE_CHECK_INTERVAL_HOURS', 24),
            auto_update=True,
            start_immediately=not app.config.get('TESTING', False)
        )
        logger.info("Auto updater initialized")


def register_blueprints(app):
    """
    Register Flask blueprints.

    Args:
        app: Flask application instance
    """
    from app.routes.main import main_bp
    from app.routes.player import player_bp
    from app.routes.clash import clash_bp
    from app.routes.debug import debug_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(clash_bp)

    # Exempt JSON API endpoints — they are stateless (no session auth) and
    # clients include X-CSRFToken header via the JS fetch patch instead.
    csrf.exempt(player_bp)

    # Register debug blueprint only in debug mode
    if app.config.get('DEBUG') or app.config.get('TESTING'):
        app.register_blueprint(debug_bp)
        logger.info("Debug blueprint registered")

    logger.info("Blueprints registered")


def register_error_handlers(app):
    """
    Register error handlers.

    Args:
        app: Flask application instance
    """
    from app.routes.errors import (
        handle_404,
        handle_429,
        handle_500,
        handle_400,
        handle_403
    )

    app.register_error_handler(400, handle_400)
    app.register_error_handler(403, handle_403)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(429, handle_429)
    app.register_error_handler(500, handle_500)

    logger.info("Error handlers registered")


def register_context_processors(app):
    """Register template context processors."""
    from config import DDRAGON_VERSION
    from config.game_constants import get_queue_name, get_game_mode_name
    from config.champion_mapping import get_champion_icon_url  # DODAJ
    from app.utils.formatters import (
        format_game_duration,
        format_kda,
        calculate_kda_ratio,
        format_gold,
        format_damage,
        format_percentage
    )
    from app.utils.helpers import time_ago

    @app.context_processor
    def inject_utilities():
        """Inject utility functions into templates."""
        return {
            'ddragon_version': DDRAGON_VERSION,
            'get_queue_name': get_queue_name,
            'get_game_mode_name': get_game_mode_name,
            'get_champion_icon_url': get_champion_icon_url,  # DODAJ
            'format_game_duration': format_game_duration,
            'format_kda': format_kda,
            'calculate_kda_ratio': calculate_kda_ratio,
            'format_gold': format_gold,
            'format_damage': format_damage,
            'format_percentage': format_percentage,
            'time_ago': time_ago,
        }

    @app.context_processor
    def inject_config():
        """Inject configuration values into templates."""
        return {
            'app_name': app.config.get('APP_NAME', 'Clash Finder'),
            'app_version': app.config.get('VERSION', '1.0.0'),
            'debug': app.config.get('DEBUG', False),
            'time_ago': time_ago,
        }

    logger.info("Context processors registered")


def register_request_handlers(app):
    """
    Register request/response handlers.

    Args:
        app: Flask application instance
    """
    from flask import request
    from app.utils.helpers import time_ago
    from datetime import datetime

    @app.before_request
    def before_request():
        """Before request handler."""
        # Store request start time for timing
        request.start_time = datetime.now()

    @app.after_request
    def after_request(response):
        """After request handler."""
        # Add CORS headers if needed
        if app.config.get('ENABLE_CORS', False):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        # Add custom headers
        response.headers['X-App-Version'] = app.config.get('VERSION', '1.0.0')

        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = (datetime.now() - request.start_time).total_seconds()
            response.headers['X-Request-Duration'] = f"{duration:.3f}"

        return response

    @app.teardown_appcontext
    def teardown_appcontext(error=None):
        """Teardown app context handler."""
        if error:
            logger.error(f"Error during request teardown: {error}")

    logger.info("Request handlers registered")


def register_cli_commands(app):
    """
    Register CLI commands.

    Args:
        app: Flask application instance
    """
    import click
    from app.services import resource_downloader

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        click.echo("Initializing database...")
        # Add database initialization here if needed
        click.echo("Database initialized.")

    @app.cli.command()
    def download_resources():
        """Download game resources from Data Dragon."""
        click.echo("Downloading game resources...")
        results = resource_downloader.download_all()

        for resource, success in results.items():
            status = "✓" if success else "✗"
            click.echo(f"{status} {resource}")

        if all(results.values()):
            click.echo("All resources downloaded successfully!")
        else:
            click.echo("Some resources failed to download.")

    @app.cli.command()
    def check_config():
        """Check configuration status."""
        click.echo("Configuration Status:")
        click.echo(f"Environment: {app.config.get('ENV', 'unknown')}")
        click.echo(f"Debug: {app.config.get('DEBUG', False)}")
        click.echo(f"Riot API Key: {'✓ Set' if app.config.get('RIOT_API_KEY') else '✗ Not set'}")
        click.echo(f"Redis URL: {'✓ Set' if app.config.get('REDIS_URL') else '✗ Not set'}")
        click.echo(f"Rate Limiting: {'✓ Enabled' if app.config.get('RATE_LIMIT_ENABLED') else '✗ Disabled'}")

    @app.cli.command()
    def routes():
        """List all registered routes."""
        import urllib

        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
            output.append(line)

        for line in sorted(output):
            click.echo(line)

    logger.info("CLI commands registered")


# Application instance for imports
def get_app():
    """Get or create application instance."""
    import os
    env = os.getenv('FLASK_ENV', 'development')
    return create_app(env)