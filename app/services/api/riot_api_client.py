# app/services/api/riot_api_client.py
"""
Low-level Riot API client for making direct API calls.
Handles authentication, rate limiting, and raw API requests.
"""

import time
import requests
from typing import Optional, Dict, Any, List
from config.logging_config import get_logger

logger = get_logger('services.api.riot_api_client')


class RiotAPIClient:
    """Direct Riot API client for raw API calls."""

    # API Endpoints
    BASE_URLS = {
        'europe': 'https://europe.api.riotgames.com',
        'americas': 'https://americas.api.riotgames.com',
        'asia': 'https://asia.api.riotgames.com',
        'sea': 'https://sea.api.riotgames.com',
        'EUW': 'https://euw1.api.riotgames.com',
        'EUNE': 'https://eun1.api.riotgames.com',
        'NA': 'https://na1.api.riotgames.com',
        'KR': 'https://kr.api.riotgames.com',
        'JP': 'https://jp1.api.riotgames.com',
        'BR': 'https://br1.api.riotgames.com',
        'LAN': 'https://la1.api.riotgames.com',
        'LAS': 'https://la2.api.riotgames.com',
        'OCE': 'https://oc1.api.riotgames.com',
        'TR': 'https://tr1.api.riotgames.com',
        'RU': 'https://ru.api.riotgames.com',
        'PH': 'https://ph2.api.riotgames.com',
        'SG': 'https://sg2.api.riotgames.com',
        'TH': 'https://th2.api.riotgames.com',
        'TW': 'https://tw2.api.riotgames.com',
        'VN': 'https://vn2.api.riotgames.com'
    }

    def __init__(self, api_key: str):
        """
        Initialize Riot API client.

        Args:
            api_key: Riot API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-Riot-Token': api_key
        })

    def _make_request(
            self,
            url: str,
            params: Optional[Dict] = None,
            retry_count: int = 3,
            retry_delay: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Riot API with retry logic.

        Args:
            url: Full API URL
            params: Query parameters
            retry_count: Number of retries
            retry_delay: Delay between retries in seconds

        Returns:
            Response JSON or None if failed
        """
        for attempt in range(retry_count):
            try:
                response = self.session.get(url, params=params, timeout=10)

                # Success
                if response.status_code == 200:
                    return response.json()

                # Rate limit
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"Rate limited. Waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue

                # Not found
                if response.status_code == 404:
                    logger.debug(f"Not found: {url}")
                    return None

                # Other errors
                logger.error(f"API error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")

            # Retry delay
            if attempt < retry_count - 1:
                time.sleep(retry_delay * (attempt + 1))

        return None

    # ============= ACCOUNT API =============

    def get_account_by_riot_id(
            self,
            game_name: str,
            tag_line: str,
            region: str = 'europe'
    ) -> Optional[Dict[str, Any]]:
        """
        Get account info by Riot ID.

        Endpoint: /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
        """
        url = f"{self.BASE_URLS[region]}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._make_request(url)

    def get_account_by_puuid(
            self,
            puuid: str,
            region: str = 'europe'
    ) -> Optional[Dict[str, Any]]:
        """
        Get account info by PUUID.

        Endpoint: /riot/account/v1/accounts/by-puuid/{puuid}
        """
        url = f"{self.BASE_URLS[region]}/riot/account/v1/accounts/by-puuid/{puuid}"
        return self._make_request(url)

    # ============= SUMMONER API =============

    def get_summoner_by_puuid(
            self,
            puuid: str,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get summoner info by PUUID.

        Endpoint: /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
        """
        url = f"{self.BASE_URLS[platform]}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return self._make_request(url)

    def get_summoner_by_summoner_id(
            self,
            summoner_id: str,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get summoner by summoner ID.

        Endpoint: /lol/summoner/v4/summoners/{encryptedSummonerId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/summoner/v4/summoners/{summoner_id}"
        return self._make_request(url)

    # ============= MATCH API =============

    def get_match_list(
            self,
            puuid: str,
            region: str = 'europe',
            start: int = 0,
            count: int = 20,
            queue: Optional[int] = None,
            type: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None
    ) -> Optional[List[str]]:
        """
        Get list of match IDs for a player.

        Endpoint: /lol/match/v5/matches/by-puuid/{puuid}/ids
        """
        url = f"{self.BASE_URLS[region]}/lol/match/v5/matches/by-puuid/{puuid}/ids"

        params = {
            'start': start,
            'count': count
        }

        if queue is not None:
            params['queue'] = queue
        if type is not None:
            params['type'] = type
        if start_time is not None:
            params['startTime'] = start_time
        if end_time is not None:
            params['endTime'] = end_time

        return self._make_request(url, params)

    def get_match_by_id(
            self,
            match_id: str,
            region: str = 'europe'
    ) -> Optional[Dict[str, Any]]:
        """
        Get match details by match ID.

        Endpoint: /lol/match/v5/matches/{matchId}
        """
        url = f"{self.BASE_URLS[region]}/lol/match/v5/matches/{match_id}"
        return self._make_request(url)

    def get_match_timeline(
            self,
            match_id: str,
            region: str = 'europe'
    ) -> Optional[Dict[str, Any]]:
        """
        Get match timeline by match ID.

        Endpoint: /lol/match/v5/matches/{matchId}/timeline
        """
        url = f"{self.BASE_URLS[region]}/lol/match/v5/matches/{match_id}/timeline"
        return self._make_request(url)

    # ============= LEAGUE API =============

    def get_league_entries_by_summoner(
            self,
            summoner_id: str,
            platform: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get league entries for summoner.

        Endpoint: /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/league/v4/entries/by-summoner/{summoner_id}"
        return self._make_request(url)

    def get_challenger_league(
            self,
            platform: str,
            queue: str = 'RANKED_SOLO_5x5'
    ) -> Optional[Dict[str, Any]]:
        """
        Get challenger league.

        Endpoint: /lol/league/v4/challengerleagues/by-queue/{queue}
        """
        url = f"{self.BASE_URLS[platform]}/lol/league/v4/challengerleagues/by-queue/{queue}"
        return self._make_request(url)

    # ============= CHAMPION MASTERY API =============

    def get_champion_mastery(
            self,
            puuid: str,
            platform: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all champion mastery entries.

        Endpoint: /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}
        """
        url = f"{self.BASE_URLS[platform]}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._make_request(url)

    def get_champion_mastery_by_champion(
            self,
            puuid: str,
            champion_id: int,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get champion mastery for specific champion.

        Endpoint: /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/by-champion/{championId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
        return self._make_request(url)

    # ============= CLASH API =============

    def get_clash_players_by_summoner(
            self,
            summoner_id: str,
            platform: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get clash players by summoner ID.

        Endpoint: /lol/clash/v1/players/by-summoner/{summonerId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/clash/v1/players/by-summoner/{summoner_id}"
        return self._make_request(url)

    def get_clash_team_by_id(
            self,
            team_id: str,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get clash team by team ID.

        Endpoint: /lol/clash/v1/teams/{teamId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/clash/v1/teams/{team_id}"
        return self._make_request(url)

    def get_clash_tournaments(
            self,
            platform: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all active clash tournaments.

        Endpoint: /lol/clash/v1/tournaments
        """
        url = f"{self.BASE_URLS[platform]}/lol/clash/v1/tournaments"
        return self._make_request(url)

    def get_clash_tournament_by_team(
            self,
            team_id: str,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get tournament by team ID.

        Endpoint: /lol/clash/v1/tournaments/by-team/{teamId}
        """
        url = f"{self.BASE_URLS[platform]}/lol/clash/v1/tournaments/by-team/{team_id}"
        return self._make_request(url)

    # ============= SPECTATOR API =============

    def get_active_game(
            self,
            puuid: str,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current game information for summoner.

        Endpoint: /lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}
        """
        url = f"{self.BASE_URLS[platform]}/lol/spectator/v5/active-games/by-summoner/{puuid}"
        return self._make_request(url)

    def get_featured_games(
            self,
            platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get list of featured games.

        Endpoint: /lol/spectator/v4/featured-games
        """
        url = f"{self.BASE_URLS[platform]}/lol/spectator/v4/featured-games"
        return self._make_request(url)