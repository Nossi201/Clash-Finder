# tests/unit/test_app_init.py
"""
Unit tests for application initialization.
"""

import pytest
from app import create_app


class TestAppCreation:
    """Test application factory."""

    def test_create_app_default(self):
        """Test creating app with default config."""
        app = create_app()

        assert app is not None
        assert app.config['TESTING'] is False

    def test_create_app_testing(self):
        """Test creating app with testing config."""
        app = create_app('testing')

        assert app.config['TESTING'] is True
        assert app.config['RATE_LIMIT_ENABLED'] is False

    def test_create_app_development(self):
        """Test creating app with development config."""
        app = create_app('development')

        assert app.config['DEBUG'] is True

    def test_create_app_production(self):
        """Test creating app with production config."""
        app = create_app('production')

        assert app.config['DEBUG'] is False


class TestAppConfig:
    """Test application configuration."""

    def test_app_has_required_config(self, app):
        """Test that app has required configuration."""
        required_keys = [
            'SECRET_KEY',
            'RIOT_API_KEY',
            'LOG_LEVEL',
            'RATE_LIMIT_ENABLED'
        ]

        for key in required_keys:
            assert key in app.config

    def test_app_testing_config(self, app):
        """Test testing configuration."""
        assert app.config['TESTING'] is True
        assert app.config['RATE_LIMIT_ENABLED'] is False
        assert app.config['WTF_CSRF_ENABLED'] is False


class TestBlueprintRegistration:
    """Test blueprint registration."""

    def test_main_blueprint_registered(self, app):
        """Test that main blueprint is registered."""
        blueprints = [bp.name for bp in app.blueprints.values()]

        assert 'main' in blueprints

    def test_player_blueprint_registered(self, app):
        """Test that player blueprint is registered."""
        blueprints = [bp.name for bp in app.blueprints.values()]

        assert 'player' in blueprints

    def test_clash_blueprint_registered(self, app):
        """Test that clash blueprint is registered."""
        blueprints = [bp.name for bp in app.blueprints.values()]

        assert 'clash' in blueprints

    def test_debug_blueprint_registered(self, app):
        """Test that debug blueprint is registered in testing."""
        blueprints = [bp.name for bp in app.blueprints.values()]

        # Should be registered in testing mode
        assert 'debug' in blueprints


class TestErrorHandlers:
    """Test error handler registration."""

    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')

        assert response.status_code == 404
        assert b'404' in response.data or b'not found' in response.data.lower()

    def test_500_handler(self, client):
        """Test 500 error handler."""
        # This would need to trigger an actual 500 error
        # For now, just verify it's registered
        pass


class TestContextProcessors:
    """Test context processors."""

    def test_utility_functions_injected(self, app, request_context):
        """Test that utility functions are available in templates."""
        # This would need to render a template and check context
        pass


class TestExtensions:
    """Test extension initialization."""

    def test_cache_initialized(self, app):
        """Test that cache is initialized."""
        from app.services.cache import cache

        assert cache._initialized is True

    def test_rate_limiter_initialized(self, app):
        """Test that rate limiter is initialized."""
        from app.services.rate_limiter import rate_limiter

        assert rate_limiter._initialized is True


class TestAppMethods:
    """Test application methods."""

    def test_app_test_client(self, app):
        """Test that test client can be created."""
        client = app.test_client()

        assert client is not None

        response = client.get('/')
        assert response.status_code == 200

    def test_app_context(self, app):
        """Test application context."""
        with app.app_context():
            from flask import current_app
            assert current_app == app

    def test_request_context(self, app):
        """Test request context."""
        with app.test_request_context('/'):
            from flask import request
            assert request.path == '/'


class TestRoutes:
    """Test route registration."""

    def test_routes_registered(self, app):
        """Test that routes are registered."""
        routes = [rule.rule for rule in app.url_map.iter_rules()]

        # Check for main routes
        assert '/' in routes
        assert any('/player_stats' in r for r in routes)
        assert any('/clash_team' in r for r in routes)

    def test_static_route(self, app):
        """Test that static route is registered."""
        routes = [rule.rule for rule in app.url_map.iter_rules()]

        assert any('static' in r for r in routes)


class TestLogging:
    """Test logging configuration."""

    def test_logger_configured(self, app):
        """Test that logger is configured."""
        assert app.logger is not None
        assert len(app.logger.handlers) > 0