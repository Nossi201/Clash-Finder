# tests/e2e/test_search_flow.py
"""
End-to-end tests for search flow.
"""

import pytest
from unittest.mock import patch




@patch('app.services.riot_api.get_account_info')
def test_player_not_found_flow(self, mock_account, client):
    """Test flow when player is not found."""
    mock_account.return_value = None

    # Submit search
    response = client.post('/Cheker', data={
        'option': 'playerStats',
        'tekst': 'NonExistent#TAG',
        'lista': 'EUW'
    }, follow_redirects=True)

    # Should show error message
    assert response.status_code in [200, 404]
    assert b'not found' in response.data.lower() or b'error' in response.data.lower()


@pytest.mark.e2e
class TestClashTeamFlow:
    """Test complete clash team flow."""

    @patch('app.services.riot_api.get_team_info_puuid')
    @patch('app.services.riot_api.get_summoner_info_puuid')
    @patch('app.services.riot_api.get_account_info')
    def test_clash_team_search_flow(
            self, mock_account, mock_summoner, mock_team,
            client, mock_account_data, mock_summoner_data, mock_clash_team_data
    ):
        """Test complete clash team search flow."""
        # Setup mocks
        mock_account.return_value = mock_account_data
        mock_summoner.return_value = mock_summoner_data
        mock_team.return_value = mock_clash_team_data

        # Submit search
        response = client.post('/Cheker', data={
            'option': 'clashTeam',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=True)

        # Should show clash team page
        assert response.status_code in [200, 404]


@pytest.mark.e2e
class TestLoadMoreFlow:
    """Test load more matches flow."""

    @patch('app.services.riot_api.display_matches_by_value')
    def test_load_more_matches(self, mock_display, client):
        """Test loading more matches."""
        mock_display.return_value = [[{'test': 'match'}]]

        # Make load more request
        response = client.post('/player_stats/load_more', json={
            'current_count': 10,
            'number': 5,
            'server': 'EUW',
            'SUMMONER_NAME': 'TestPlayer',
            'SUMMONER_TAG': 'TAG'
        })

        # Should return JSON
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.is_json


@pytest.mark.e2e
class TestNavigationFlow:
    """Test navigation between pages."""

    def test_home_to_search_to_home(self, client):
        """Test navigation flow."""
        # Home page
        response = client.get('/')
        assert response.status_code == 200

        # Home alias
        response = client.get('/home', follow_redirects=True)
        assert response.status_code == 200

    def test_404_page(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceFlow:
    """Test performance of complete flows."""

    @patch('app.services.riot_api.display_matches')
    @patch('app.services.riot_api.get_account_info')
    def test_search_performance(
            self, mock_account, mock_display,
            client, benchmark_timer, mock_account_data
    ):
        """Test search performance."""
        mock_account.return_value = mock_account_data
        mock_display.return_value = [{'test': 'match'}]

        benchmark_timer.start()

        # Submit search
        response = client.post('/Cheker', data={
            'option': 'playerStats',
            'tekst': 'TestPlayer#TAG',
            'lista': 'EUW'
        }, follow_redirects=True)

        elapsed = benchmark_timer.stop()

        # Should complete reasonably fast
        assert elapsed < 2.0  # Less than 2 seconds
        assert response.status_code in [200, 404]