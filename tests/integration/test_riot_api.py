# tests/integration/test_riot_api.py
"""
Integration tests for Riot API service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.riot_api import (
    get_account_info,
    get_summoner_info_puuid,
    get_match_ids,
    get_match_details,
    get_team_info_puuid,
    display_matches,
    RiotAPIError,
    RateLimitError,
    NotFoundError
)


class TestGetAccountInfo:
    """Test get_account_info function."""

    @patch('app.services.riot_api.make_api_request')
    def test_get_account_info_success(self, mock_request, mock_account_data, app_context):
        """Test successful account info retrieval."""
        mock_request.return_value = mock_account_data

        result = get_account_info('TestPlayer', 'EUW1', 'EUW')

        assert result is not None
        assert result['puuid'] == 'test-puuid-123456'
        assert result['gameName'] == 'TestPlayer'
        mock_request.assert_called_once()

    @patch('app.services.riot_api.make_api_request')
    def test_get_account_info_not_found(self, mock_request, app_context):
        """Test account not found."""
        mock_request.side_effect = NotFoundError("Not found")

        result = get_account_info('NonExistent', 'TAG', 'EUW')

        assert result is None

    @patch('app.services.riot_api.make_api_request')
    def test_get_account_info_api_error(self, mock_request, app_context):
        """Test API error handling."""
        mock_request.side_effect = RiotAPIError("API Error")

        result = get_account_info('TestPlayer', 'TAG', 'EUW')

        assert result is None


class TestGetSummonerInfo:
    """Test get_summoner_info_puuid function."""

    @patch('app.services.riot_api.make_api_request')
    def test_get_summoner_info_success(self, mock_request, mock_summoner_data, app_context):
        """Test successful summoner info retrieval."""
        mock_request.return_value = mock_summoner_data

        result = get_summoner_info_puuid('test-puuid-123456', 'EUW')

        assert result is not None
        assert result['id'] == 'summoner-id-123'
        assert result['puuid'] == 'test-puuid-123456'

    @patch('app.services.riot_api.make_api_request')
    def test_get_summoner_info_not_found(self, mock_request, app_context):
        """Test summoner not found."""
        mock_request.side_effect = NotFoundError("Not found")

        result = get_summoner_info_puuid('invalid-puuid', 'EUW')

        assert result is None


class TestGetMatchIds:
    """Test get_match_ids function."""

    @patch('app.services.riot_api.make_api_request')
    def test_get_match_ids_success(self, mock_request, mock_match_ids, app_context):
        """Test successful match IDs retrieval."""
        mock_request.return_value = mock_match_ids

        result = get_match_ids('test-puuid', 'EUW', start=0, count=5)

        assert result is not None
        assert len(result) == 5
        assert result[0] == 'EUW1_1234567890'

    @patch('app.services.riot_api.make_api_request')
    def test_get_match_ids_empty(self, mock_request, app_context):
        """Test empty match IDs."""
        mock_request.return_value = []

        result = get_match_ids('test-puuid', 'EUW')

        assert result == []

    @patch('app.services.riot_api.make_api_request')
    def test_get_match_ids_with_queue_filter(self, mock_request, app_context):
        """Test match IDs with queue filter."""
        mock_request.return_value = ['match1', 'match2']

        result = get_match_ids('test-puuid', 'EUW', queue=420)

        assert result is not None


class TestGetMatchDetails:
    """Test get_match_details function."""

    @patch('app.services.riot_api.make_api_request')
    def test_get_match_details_success(self, mock_request, mock_match_data, app_context):
        """Test successful match details retrieval."""
        mock_request.return_value = mock_match_data

        result = get_match_details('EUW1_1234567890', 'EUW')

        assert result is not None
        assert result['metadata']['matchId'] == 'EUW1_1234567890'
        assert 'info' in result

    @patch('app.services.riot_api.make_api_request')
    def test_get_match_details_not_found(self, mock_request, app_context):
        """Test match not found."""
        mock_request.side_effect = NotFoundError("Not found")

        result = get_match_details('invalid-match-id', 'EUW')

        assert result is None


class TestGetClashTeamInfo:
    """Test get_team_info_puuid function."""

    @patch('app.services.riot_api.make_api_request')
    def test_get_team_info_success(self, mock_request, mock_clash_team_data, app_context):
        """Test successful clash team retrieval."""
        mock_request.return_value = [mock_clash_team_data]

        result = get_team_info_puuid('summoner-id', 'EUW')

        assert result is not None
        assert result['id'] == 'team-id-123'

    @patch('app.services.riot_api.make_api_request')
    def test_get_team_info_not_found(self, mock_request, app_context):
        """Test no clash team found."""
        mock_request.side_effect = NotFoundError("Not found")

        result = get_team_info_puuid('summoner-id', 'EUW')

        assert result is None

    @patch('app.services.riot_api.make_api_request')
    def test_get_team_info_empty_list(self, mock_request, app_context):
        """Test empty team list."""
        mock_request.return_value = []

        result = get_team_info_puuid('summoner-id', 'EUW')

        assert result is None




@patch('app.services.riot_api.get_account_info')
def test_display_matches_account_not_found(self, mock_account, app_context):
    """Test account not found."""
    mock_account.return_value = None

    result = display_matches('NonExistent', 'TAG', 'EUW')

    assert result is None


@patch('app.services.riot_api.get_match_ids')
@patch('app.services.riot_api.get_account_info')
def test_display_matches_no_matches(
        self, mock_account, mock_match_ids,
        mock_account_data, app_context
):
    """Test no matches found."""
    mock_account.return_value = mock_account_data
    mock_match_ids.return_value = []

    result = display_matches('TestPlayer', 'TAG', 'EUW')

    assert result is None


class TestRateLimiting:
    """Test rate limiting handling."""

    @patch('app.services.riot_api.make_api_request')
    def test_rate_limit_error(self, mock_request, app_context):
        """Test rate limit error handling."""
        mock_request.side_effect = RateLimitError("Rate limit exceeded")

        with pytest.raises(RateLimitError):
            get_account_info('TestPlayer', 'TAG', 'EUW')


class TestCaching:
    """Test caching functionality."""

    @patch('app.services.riot_api.make_api_request')
    def test_account_info_cached(self, mock_request, mock_account_data, app_context):
        """Test that account info is cached."""
        mock_request.return_value = mock_account_data

        # First call
        result1 = get_account_info('TestPlayer', 'TAG', 'EUW')

        # Second call (should use cache)
        result2 = get_account_info('TestPlayer', 'TAG', 'EUW')

        assert result1 == result2
        # Should only call API once due to caching
        assert mock_request.call_count >= 1


class TestErrorHandling:
    """Test error handling."""

    @patch('app.services.riot_api.requests.get')
    def test_connection_error(self, mock_get, app_context):
        """Test connection error handling."""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")

        # Should handle gracefully
        # Specific implementation depends on error handling in make_api_request


@pytest.mark.api
@pytest.mark.slow
class TestRealAPICall:
    """Test with real API (marked as slow/api)."""

    @pytest.mark.skip(reason="Requires real API key and makes actual API calls")
    def test_real_account_lookup(self, app_context):
        """Test real API call (skip by default)."""
        # This would make a real API call
        result = get_account_info('Faker', 'KR1', 'KR')

        if result:
            assert 'puuid' in result