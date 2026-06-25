# config/base.py
"""
Base configuration for Clash Finder application.
Contains settings shared across all environments.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Application
    APP_NAME = 'Clash Finder'
    VERSION = '1.0.0'

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Debug mode (override in environment configs)
    DEBUG = False
    TESTING = False

    # Riot API
    RIOT_API_KEY = os.getenv('RIOT_API_KEY', '')
    RIOT_API_TIMEOUT = int(os.getenv('RIOT_API_TIMEOUT', '10'))

    # Redis (for caching and rate limiting)
    REDIS_URL = os.getenv('REDIS_URL', None)

    # Cache settings
    CACHE_TYPE = 'simple'  # 'simple' for in-memory, 'redis' for Redis
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_MAX_SIZE = 1000  # Max items in in-memory cache

    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_STORAGE_URL = REDIS_URL

    # Rate limits per endpoint (per minute, per hour)
    RATE_LIMIT_HOME_MINUTE = 100
    RATE_LIMIT_HOME_HOUR = 1000

    RATE_LIMIT_SEARCH_MINUTE = 30
    RATE_LIMIT_SEARCH_HOUR = 300

    RATE_LIMIT_PLAYER_STATS_MINUTE = 15
    RATE_LIMIT_PLAYER_STATS_HOUR = 150

    RATE_LIMIT_CLASH_TEAM_MINUTE = 15
    RATE_LIMIT_CLASH_TEAM_HOUR = 150

    RATE_LIMIT_LOAD_MORE_MINUTE = 20
    RATE_LIMIT_LOAD_MORE_HOUR = 200

    # Match loading
    INITIAL_MATCH_LOAD = 10  # Initial matches to load
    MATCHES_PER_PAGE = 5  # Matches to load on "load more"
    MAX_MATCHES = 100  # Maximum matches to fetch

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # Static files
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'

    # Templates
    TEMPLATES_FOLDER = 'templates'
    TEMPLATES_AUTO_RELOAD = True

    # Session
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Resource updates
    AUTO_UPDATE_RESOURCES = True
    UPDATE_CHECK_INTERVAL_HOURS = 24


    # File upload (if needed)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'json', 'csv', 'txt'}

    # Pagination
    ITEMS_PER_PAGE = 20

    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=12)

    # Timezone
    TIMEZONE = 'UTC'

    # Languages
    LANGUAGES = ['en', 'pl']
    DEFAULT_LANGUAGE = 'en'

    # API settings
    API_TITLE = 'Clash Finder API'
    API_VERSION = 'v1'

    # Error handling
    PROPAGATE_EXCEPTIONS = False
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False

    # Development tools
    EXPLAIN_TEMPLATE_LOADING = False

    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        # Create necessary directories
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # Set timezone
        os.environ['TZ'] = Config.TIMEZONE


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEVELOPMENT = True

    # Less strict rate limiting in development
    RATE_LIMIT_ENABLED = False

    # More verbose logging
    LOG_LEVEL = 'DEBUG'

    # Template auto-reload
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True

    # Pretty print JSON
    JSONIFY_PRETTYPRINT_REGULAR = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Require HTTPS
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

    # Stricter security
    WTF_CSRF_ENABLED = True

    # Production logging
    LOG_LEVEL = 'WARNING'

    # Disable template auto-reload
    TEMPLATES_AUTO_RELOAD = False

    @staticmethod
    def init_app(app):
        """Initialize production application."""
        Config.init_app(app)

        secret = app.config.get('SECRET_KEY', '')
        if not secret or secret == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in production. "
                "Generate one with: python scripts/generate_secret_key.py"
            )

        # Log to syslog or external service in production
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

    # Disable rate limiting for tests
    RATE_LIMIT_ENABLED = False

    # Use in-memory cache for tests
    CACHE_TYPE = 'simple'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Fast resource updates for tests
    UPDATE_CHECK_INTERVAL_HOURS = 1

    # Use test database/cache if needed
    REDIS_URL = None

    # More verbose logging for tests
    LOG_LEVEL = 'DEBUG'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """
    Get configuration for environment.

    Args:
        env: Environment name ('development', 'production', 'testing')

    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    return config.get(env, config['default'])