# app/routes/__init__.py
"""
Routes package.
Contains all Flask route blueprints.
"""

from .main import main_bp
from .player import player_bp
from .clash import clash_bp
from .debug import debug_bp
from .errors import handle_404, handle_429, handle_500

__all__ = [
    'main_bp',
    'player_bp',
    'clash_bp',
    'debug_bp',
    'handle_404',
    'handle_429',
    'handle_500',
]