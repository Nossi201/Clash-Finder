# app/services/player_service.py
"""
Player service for handling player-related business logic.
Uses RiotAPIClient for API calls and adds caching, processing, etc.
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.services.api.riot_api_client import RiotAPIClient
from app.services.cache import cache
from app.services.match_processor import MatchProcessor
from config.logging_config import get_logger

logger = get_logger('services.player_service')


class PlayerService:
    """Service for player-related operations."""

    def __init__(self, api_key: str):
        """Initialize player service with API client."""
        self.client = RiotAPIClient(api_key)
        self.match_processor = MatchProcessor()

    def get_player_info(
            self,
            game_name: str,
            tag_line: str,
            server: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive player information.

        Args:
            game_name: Player's game name
            tag_line: Player's tag line
            server: Server/platform

        Returns:
            Player info dict with account and summoner data
        """
        # Check cache first
        cache_key = f"player_info:{game_name}:{tag_line}:{server}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for player info: {game_name}#{tag_line}")
            return cached_data

        logger.info(f"Fetching player info: {game_name}#{tag_line} on {server}")

        # Get region for account API
        region = self._get_region_from_server(server)

        # Get account info
        account_data = self.client.get_account_by_riot_id(
            game_name, tag_line, region
        )

        if not account_data:
            logger.warning(f"Account not found: {game_name}#{tag_line}")
            return None

        # Get summoner info
        summoner_data = self.client.get_summoner_by_puuid(
            account_data['puuid'], server
        )

        # Get ranked stats
        ranked_stats = None
        if summoner_data:
            ranked_stats = self.client.get_league_entries_by_summoner(
                summoner_data['id'], server
            )

        # Combine all data
        player_info = {
            'puuid': account_data['puuid'],
            'game_name': account_data['gameName'],
            'tag_line': account_data['tagLine'],
            'summoner_level': summoner_data.get('summonerLevel', 0) if summoner_data else 0,
            'profile_icon_id': summoner_data.get('profileIconId', 0) if summoner_data else 0,
            'summoner_id': summoner_data.get('id') if summoner_data else None,
            'account_id': summoner_data.get('accountId') if summoner_data else None,
            'ranked_stats': self._process_ranked_stats(ranked_stats),
            'server': server,
            'region': region,
            'last_updated': datetime.now().isoformat()
        }

        # Cache for 1 hour
        cache.set(cache_key, player_info, timeout=3600)

        return player_info

    def get_match_history(
            self,
            game_name: str,
            tag_line: str,
            server: str,
            offset: int = 0,
            limit: int = 10,
            queue_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get processed match history for a player.

        Args:
            game_name: Player's game name
            tag_line: Player's tag line
            server: Server/platform
            offset: Starting index
            limit: Number of matches
            queue_id: Optional queue filter

        Returns:
            Dict with matches and metadata
        """
        # Get player info first
        player_info = self.get_player_info(game_name, tag_line, server)
        if not player_info:
            return {
                'success': False,
                'error': 'Player not found',
                'matches': [],
                'has_more': False
            }

        puuid = player_info['puuid']
        region = player_info['region']

        # Check cache for match IDs
        cache_key = f"match_ids:{puuid}:{offset}:{limit}:{queue_id}"
        cached_match_ids = cache.get(cache_key)

        if not cached_match_ids:
            # Get match IDs from API
            match_ids = self.client.get_match_list(
                puuid=puuid,
                region=region,
                start=offset,
                count=limit + 1,  # Get one extra to check if there are more
                queue=queue_id
            )

            if match_ids:
                # Cache for 5 minutes
                cache.set(cache_key, match_ids, timeout=300)
                cached_match_ids = match_ids

        if not cached_match_ids:
            return {
                'success': True,
                'matches': [],
                'has_more': False,
                'total_loaded': offset
            }

        # Check if there are more matches
        has_more = len(cached_match_ids) > limit
        match_ids_to_process = cached_match_ids[:limit]

        # Process matches
        matches = []
        for match_id in match_ids_to_process:
            match_data = self._get_match_with_cache(match_id, region)
            if match_data:
                processed_match = self.match_processor.process_match(
                    match_data, puuid, game_name, tag_line, server
                )
                if processed_match:
                    matches.append(processed_match)

            # Small delay to avoid rate limiting
            time.sleep(0.05)

        return {
            'success': True,
            'matches': matches,
            'has_more': has_more,
            'total_loaded': offset + len(matches),
            'player_info': player_info
        }

    def get_live_game(
            self,
            game_name: str,
            tag_line: str,
            server: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current live game for a player.

        Returns:
            Live game data or None if not in game
        """
        player_info = self.get_player_info(game_name, tag_line, server)
        if not player_info:
            return None

        return self.client.get_active_game(
            player_info['puuid'], server
        )

    def get_champion_mastery(
            self,
            game_name: str,
            tag_line: str,
            server: str,
            top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top champion masteries for a player.

        Returns:
            List of champion mastery data
        """
        player_info = self.get_player_info(game_name, tag_line, server)
        if not player_info:
            return []

        masteries = self.client.get_champion_mastery(
            player_info['puuid'], server
        )

        if masteries:
            # Sort by mastery points and get top N
            masteries.sort(key=lambda x: x.get('championPoints', 0), reverse=True)
            return masteries[:top_n]

        return []

    def _get_match_with_cache(
            self,
            match_id: str,
            region: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get match data with caching.

        Args:
            match_id: Match ID
            region: Region for API

        Returns:
            Match data or None
        """
        # Check cache
        cache_key = f"match:{match_id}"
        cached_match = cache.get(cache_key)
        if cached_match:
            return cached_match

        # Get from API
        match_data = self.client.get_match_by_id(match_id, region)

        if match_data:
            # Cache for 1 day (matches don't change)
            cache.set(cache_key, match_data, timeout=86400)

        return match_data

    def _get_region_from_server(self, server: str) -> str:
        """
        Map server to region for routing.

        Args:
            server: Server code (EUW, NA, etc.)

        Returns:
            Region for API routing
        """
        region_mapping = {
            'EUW': 'europe',
            'EUNE': 'europe',
            'TR': 'europe',
            'RU': 'europe',
            'NA': 'americas',
            'BR': 'americas',
            'LAN': 'americas',
            'LAS': 'americas',
            'KR': 'asia',
            'JP': 'asia',
            'OCE': 'sea',
            'PH': 'sea',
            'SG': 'sea',
            'TH': 'sea',
            'TW': 'sea',
            'VN': 'sea'
        }
        return region_mapping.get(server, 'europe')

    def _process_ranked_stats(
            self,
            ranked_entries: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """
        Process ranked statistics.

        Args:
            ranked_entries: List of league entries

        Returns:
            Processed ranked stats
        """
        if not ranked_entries:
            return {}

        stats = {}
        for entry in ranked_entries:
            queue_type = entry.get('queueType', 'UNKNOWN')
            stats[queue_type] = {
                'tier': entry.get('tier', 'UNRANKED'),
                'rank': entry.get('rank', ''),
                'league_points': entry.get('leaguePoints', 0),
                'wins': entry.get('wins', 0),
                'losses': entry.get('losses', 0),
                'win_rate': round(
                    entry.get('wins', 0) / max(entry.get('wins', 0) + entry.get('losses', 0), 1) * 100,
                    1
                )
            }

        return stats