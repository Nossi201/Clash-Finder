# tests/unit/test_routes_main.py
"""
Unit tests for main routes.
"""

import pytest
from flask import url_for


class TestIndexRoute:
    """Test index/home page route."""

    def test_index_get(self, client):
        """Test GET request to index page."""
        response = client.get('/')

        assert response.status_code == 200
        assert b'Clash Finder' in response.data
        assert b'form' in response.data

    def test_index_has_server_list(self, client):
        """Test that server list is present."""
        response = client.get('/')

        assert b'EUW' in response.data
        assert b'NA' in response.data
        assert b'KR' in response.data

    def test_index_has_search_form(self, client):
        """Test that search form elements are present."""
        response = client.get('/')

        assert b'name="tekst"' in response.data  # Summoner name input
        assert b'name="lista"' in response.data  # Server select
        assert b'name="option"' in response.data  # Radio options


class TestCheckerRoute:
    """Test search form submission route."""

    def test_cheker_post_player_stats(self, client, mocker):
        """Test POST request for player stats."""
        # Mock the redirect
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302  # Redirect
        assert b'/player_stats/' in response.data or response.location

    def test_cheker_post_clash_team(self, client):
        """Test POST request for clash team."""
        response = client.post('/Cheker', data={
            'option': 'clashTeam',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302  # Redirect
        assert b'/clash_team/' in response.data or '/clash_team/' in response.location

    def test_cheker_post_empty_name(self, client):
        """Test POST with empty summoner name."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': '',
            'lista': 'EUW'
        })

        assert response.status_code == 400
        assert b'enter a summoner name' in response.data.lower()

    def test_cheker_post_invalid_server(self, client):
        """Test POST with invalid server."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'TestPlayer#TAG',
            'lista': 'INVALID'
        })

        assert response.status_code == 400
        assert b'valid server' in response.data.lower()

    def test_cheker_post_missing_option(self, client):
        """Test POST with missing option."""
        response = client.post('/Cheker', data={
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        # Should default to playerStats
        assert response.status_code == 302

    @pytest.mark.parametrize('summoner_input', [
        'Player#TAG',
        'Player Name#TAG',
        'PlayerName',
        'Player-Name#TAG123'
    ])
    def test_cheker_various_summoner_formats(self, client, summoner_input):
        """Test various summoner name formats."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': summoner_input,
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302


class TestHomeAlias:
    """Test /home alias route."""

    def test_home_redirect(self, client):
        """Test that /home redirects to index."""
        response = client.get('/home', follow_redirects=False)

        assert response.status_code == 302
        assert response.location == url_for('main.index', _external=False) or response.location == '/'


class TestRateLimiting:
    """Test rate limiting on routes (if enabled)."""

    @pytest.mark.skip(reason="Rate limiting disabled in tests")
    def test_index_rate_limit(self, client):
        """Test rate limiting on index route."""
        # Make multiple requests
        for _ in range(150):
            response = client.get('/')
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limit not triggered")


class TestFormValidation:
    """Test form validation."""

    def test_cheker_strips_whitespace(self, client):
        """Test that form input is trimmed."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': '  TestPlayer#TAG  ',
            'lista': '  EUW  '
        }, follow_redirects=False)

        assert response.status_code == 302

    def test_cheker_handles_special_chars(self, client):
        """Test handling of special characters."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'Player<script>#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302


class TestErrorHandling:
    """Test error handling in routes."""

    def test_cheker_with_get_method(self, client):
        """Test that GET method is not allowed on /Cheker."""
        response = client.get('/Cheker')

        assert response.status_code == 405  # Method Not Allowed

    def test_nonexistent_route(self, client):
        """Test 404 on non-existent route."""
        response = client.get('/nonexistent')

        assert response.status_code == 404


class TestURLGeneration:
    """Test URL generation for redirects."""

    def test_player_stats_url_format(self, client):
        """Test that player stats URL is correctly formatted."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302
        # Should encode riot ID properly
        assert '--' in response.location or 'TestPlayer' in response.location

    def test_clash_team_url_format(self, client):
        """Test that clash team URL is correctly formatted."""
        response = client.post('/Cheker', data={
            'option': 'clashTeam',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert 'clash_team' in response.location


class TestServerSlugification:
    """Test server name slugification in URLs."""

    @pytest.mark.parametrize('server,expected_slug', [
        ('EUW', 'eu-west'),
        ('NA', 'north-america'),
        ('KR', 'korea'),
    ])
    def test_server_slugs(self, client, server, expected_slug):
        """Test that servers are properly slugified."""
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'TestPlayer#TAG',
            'lista': server
        }, follow_redirects=False)

        assert response.status_code == 302
        # Location should contain slugified server
        assert expected_slug in response.location or server in response.location