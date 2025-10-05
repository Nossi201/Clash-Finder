# tests/conftest.py
"""
Pytest configuration and fixtures for Clash Finder tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')

    # Override config for tests
    app.config.update({
        'TESTING': True,
        'RATE_LIMIT_ENABLED': False,
        'WTF_CSRF_ENABLED': False,
    })

    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield


@pytest.fixture(scope='function')
def request_context(app):
    """Create request context."""
    with app.test_request_context():
        yield


# Mock data fixtures
@pytest.fixture
def mock_account_data():
    """Mock Riot account data."""
    return {
        'puuid': 'test-puuid-123456',
        'gameName': 'TestPlayer',
        'tagLine': 'EUW1'
    }


@pytest.fixture
def mock_summoner_data():
    """Mock summoner data."""
    return {
        'id': 'summoner-id-123',
        'accountId': 'account-id-123',
        'puuid': 'test-puuid-123456',
        'profileIconId': 29,
        'summonerLevel': 150,
        'revisionDate': 1640000000000
    }


@pytest.fixture
def mock_match_data():
    """Mock match data."""
    return {
        'metadata': {
            'matchId': 'EUW1_1234567890',
            'participants': ['puuid1', 'puuid2']
        },
        'info': {
            'gameCreation': 1640000000000,
            'gameDuration': 1800,
            'gameMode': 'CLASSIC',
            'gameType': 'MATCHED_GAME',
            'queueId': 420,
            'participants': [
                {
                    'puuid': 'puuid1',
                    'summonerName': 'Player1',
                    'riotIdGameName': 'Player1',
                    'riotIdTagline': 'EUW1',
                    'championName': 'Aatrox',
                    'championId': 266,
                    'champLevel': 18,
                    'kills': 10,
                    'deaths': 3,
                    'assists': 7,
                    'totalMinionsKilled': 180,
                    'neutralMinionsKilled': 20,
                    'goldEarned': 15000,
                    'totalDamageDealtToChampions': 25000,
                    'totalDamageTaken': 18000,
                    'visionScore': 45,
                    'win': True,
                    'teamId': 100,
                    'item0': 3153,
                    'item1': 3074,
                    'item2': 3071,
                    'item3': 3111,
                    'item4': 3065,
                    'item5': 3143,
                    'item6': 3340,
                    'summoner1Id': 4,
                    'summoner2Id': 14,
                }
            ],
            'teams': [
                {
                    'teamId': 100,
                    'win': True,
                    'objectives': {
                        'baron': {'kills': 1},
                        'dragon': {'kills': 3},
                        'tower': {'kills': 9}
                    },
                    'bans': [
                        {'championId': 157},
                        {'championId': 238}
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_clash_team_data():
    """Mock clash team data."""
    return {
        'id': 'team-id-123',
        'tournamentId': 5001,
        'name': 'Test Team',
        'abbreviation': 'TT',
        'tier': 1,
        'captain': 'summoner-id-1',
        'iconId': 123,
        'players': [
            {
                'summonerId': 'summoner-id-1',
                'summonerName': 'Player1',
                'summonerTag': 'EUW1',
                'position': 'TOP',
                'role': 'CAPTAIN'
            },
            {
                'summonerId': 'summoner-id-2',
                'summonerName': 'Player2',
                'summonerTag': 'EUW1',
                'position': 'JUNGLE',
                'role': 'MEMBER'
            }
        ]
    }


@pytest.fixture
def mock_match_ids():
    """Mock match ID list."""
    return [
        'EUW1_1234567890',
        'EUW1_1234567891',
        'EUW1_1234567892',
        'EUW1_1234567893',
        'EUW1_1234567894'
    ]


# Helper functions
@pytest.fixture
def make_request(client):
    """Helper to make requests."""

    def _make_request(method, url, **kwargs):
        method_func = getattr(client, method.lower())
        return method_func(url, **kwargs)

    return _make_request


@pytest.fixture
def login_user(client):
    """Helper to login user (if authentication is added)."""

    def _login(username='testuser', password='testpass'):
        return client.post('/login', data={
            'username': username,
            'password': password
        })

    return _login


# Mock external API calls
@pytest.fixture
def mock_riot_api(mocker):
    """Mock Riot API calls."""

    class MockRiotAPI:
        def __init__(self):
            self.get_account_info = mocker.MagicMock()
            self.get_summoner_info_puuid = mocker.MagicMock()
            self.get_match_ids = mocker.MagicMock()
            self.get_match_details = mocker.MagicMock()
            self.get_team_info_puuid = mocker.MagicMock()

    return MockRiotAPI()


@pytest.fixture(autouse=True)
def reset_caches():
    """Reset caches between tests."""
    from app.services.cache import cache
    from app.services.rate_limiter import rate_limiter

    if hasattr(cache, 'backend') and cache.backend:
        cache.clear()

    yield

    # Cleanup after test
    if hasattr(cache, 'backend') and cache.backend:
        cache.clear()


@pytest.fixture
def sample_riot_id():
    """Sample Riot ID for testing."""
    return {
        'game_name': 'TestPlayer',
        'tag_line': 'EUW1',
        'encoded': 'TestPlayer--EUW1'
    }


@pytest.fixture
def sample_servers():
    """Sample server list."""
    return ['EUW', 'EUNE', 'NA', 'KR']


# Performance testing helpers
@pytest.fixture
def benchmark_timer():
    """Simple benchmark timer."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()
            return self.elapsed()

        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()


# Database fixtures (if database is added later)
@pytest.fixture
def init_database(app):
    """Initialize test database."""
    # This would set up test database
    # For now, it's a placeholder
    yield
    # Cleanup database


# CLI testing helpers
@pytest.fixture
def cli_runner(app):
    """CLI runner for testing commands."""
    return app.test_cli_runner()


# Marker definitions
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API calls"
    )