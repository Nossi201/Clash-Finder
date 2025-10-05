# config/logging_config.py
"""
Logging configuration for Clash Finder application.
Provides structured logging with rotation and multiple handlers.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# Log directory
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Default log level from environment
DEFAULT_LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        # Format the message
        result = super().format(record)

        # Reset levelname for other formatters
        record.levelname = levelname

        return result


def setup_logging(
        app=None,
        log_level: str = DEFAULT_LOG_LEVEL,
        log_file: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = True
):
    """
    Setup application logging.

    Args:
        app: Flask application instance (optional)
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Path to log file (default: logs/app.log)
        enable_console: Enable console logging
        enable_file: Enable file logging
    """
    # Get log level
    level = LOG_LEVELS.get(log_level, logging.INFO)

    # Default log file
    if log_file is None:
        log_file = str(LOG_DIR / 'app.log')

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Use colored formatter for console
        console_formatter = ColoredFormatter(
            '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if enable_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)

        # Detailed formatter for file
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Error file handler (only errors and above)
    if enable_file:
        error_file = str(LOG_DIR / 'errors.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

    # Configure Flask app logger if provided
    if app:
        app.logger.setLevel(level)

        # Disable werkzeug request logging in production
        if not app.debug:
            logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Log startup message
    root_logger.info(f"Logging initialized | Level: {log_level} | File: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a module.

    Args:
        name: Logger name (usually module name)

    Returns:
        Logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("Message")
    """
    return logging.getLogger(name)


def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log error with context and stack trace.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    if context:
        logger.error(f"Error in {context}: {error}", exc_info=True)
    else:
        logger.error(f"Error: {error}", exc_info=True)


def log_request_info(logger: logging.Logger):
    """
    Log current request information.

    Args:
        logger: Logger instance
    """
    from flask import request

    try:
        logger.info(
            f"Request | Method: {request.method} | "
            f"Path: {request.path} | "
            f"IP: {request.remote_addr} | "
            f"User-Agent: {request.user_agent}"
        )
    except RuntimeError:
        # Not in request context
        pass


def log_player_search(logger: logging.Logger, player: str, server: str, found: bool = True):
    """
    Log player search event.

    Args:
        logger: Logger instance
        player: Player name/ID
        server: Server name
        found: Whether player was found
    """
    status = "found" if found else "not found"
    logger.info(f"Player search | Player: {player} | Server: {server} | Status: {status}")


def log_api_call(logger: logging.Logger, endpoint: str, params: dict = None, success: bool = True):
    """
    Log API call event.

    Args:
        logger: Logger instance
        endpoint: API endpoint
        params: Request parameters
        success: Whether call was successful
    """
    status = "success" if success else "failed"
    param_str = f" | Params: {params}" if params else ""
    logger.debug(f"API call | Endpoint: {endpoint}{param_str} | Status: {status}")


class RequestFormatter(logging.Formatter):
    """Formatter that includes Flask request context."""

    def format(self, record):
        """Format record with request context."""
        try:
            from flask import request, has_request_context

            if has_request_context():
                record.url = request.url
                record.method = request.method
                record.ip = request.remote_addr
            else:
                record.url = '-'
                record.method = '-'
                record.ip = '-'
        except Exception:
            record.url = '-'
            record.method = '-'
            record.ip = '-'

        return super().format(record)


def setup_request_logging(app):
    """
    Setup request-specific logging.

    Args:
        app: Flask application instance
    """
    request_logger = get_logger('requests')

    @app.before_request
    def log_request():
        """Log incoming request."""
        from flask import request
        request_logger.debug(
            f"Incoming request | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"IP: {request.remote_addr}"
        )

    @app.after_request
    def log_response(response):
        """Log response."""
        from flask import request
        request_logger.debug(
            f"Outgoing response | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"Status: {response.status_code}"
        )
        return response


def create_timed_rotating_handler(
        filename: str,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 7
) -> TimedRotatingFileHandler:
    """
    Create time-based rotating file handler.

    Args:
        filename: Log file path
        when: When to rotate ('midnight', 'H', 'D', 'W0'-'W6')
        interval: Interval for rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured handler
    """
    handler = TimedRotatingFileHandler(
        filename,
        when=when,
        interval=interval,
        backupCount=backup_count
    )

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    return handler


# Pre-configured loggers for different components
def get_app_logger() -> logging.Logger:
    """Get application logger."""
    return get_logger('app')


def get_api_logger() -> logging.Logger:
    """Get API logger."""
    return get_logger('api')


def get_db_logger() -> logging.Logger:
    """Get database logger."""
    return get_logger('database')


def get_cache_logger() -> logging.Logger:
    """Get cache logger."""
    return get_logger('cache')


# Utility functions for common log patterns
def log_execution_time(logger: logging.Logger, function_name: str, duration: float):
    """Log function execution time."""
    logger.debug(f"Execution time | Function: {function_name} | Duration: {duration:.3f}s")


def log_cache_hit(logger: logging.Logger, key: str):
    """Log cache hit."""
    logger.debug(f"Cache hit | Key: {key}")


def log_cache_miss(logger: logging.Logger, key: str):
    """Log cache miss."""
    logger.debug(f"Cache miss | Key: {key}")


def log_rate_limit_exceeded(logger: logging.Logger, ip: str, endpoint: str):
    """Log rate limit exceeded."""
    logger.warning(f"Rate limit exceeded | IP: {ip} | Endpoint: {endpoint}")