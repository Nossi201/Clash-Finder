# app/services/riot_api.py
"""
Riot API service for Clash Finder.
Handles all interactions with Riot Games API endpoints.
"""

import time
import requests
from typing import Optional, List, Dict, Any, Tuple
from flask import current_app

from config.logging_config import get_logger
from app.services.cache import cached, cache
from app.models.game_models import Account, Summoner, Match, ClashTeam
from app.utils.formatters import slugify_server
logger = get_logger('services.riot_api')

# Server to region mapping
servers_to_region = {
    'BR': 'americas',
    'EUNE': 'europe',
    'EUW': 'europe',
    'JP': 'asia',
    'KR': 'asia',
    'LAN': 'americas',
    'LAS': 'americas',
    'NA': 'americas',
    'OCE': 'sea',
    'TR': 'europe',
    'RU': 'europe',
    'PH': 'asia',
    'SG': 'asia',
    'TH': 'asia',
    'TW': 'asia',
    'VN': 'asia'
}

# Server code mapping
server_codes = {
    'BR': 'br1',
    'EUNE': 'eun1',
    'EUW': 'euw1',
    'JP': 'jp1',
    'KR': 'kr',
    'LAN': 'la1',
    'LAS': 'la2',
    'NA': 'na1',
    'OCE': 'oc1',
    'TR': 'tr1',
    'RU': 'ru',
    'PH': 'ph2',
    'SG': 'sg2',
    'TH': 'th2',
    'TW': 'tw2',
    'VN': 'vn2'
}


class RiotAPIError(Exception):
    """Custom exception for Riot API errors."""
    pass


class RateLimitError(RiotAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class NotFoundError(RiotAPIError):
    """Raised when resource is not found."""
    pass


def get_api_key() -> str:
    """Get Riot API key from config."""
    api_key = current_app.config.get('RIOT_API_KEY')
    if not api_key:
        raise ValueError("RIOT_API_KEY not configured")
    return api_key


def get_server_code(server: str) -> str:
    """Convert server name to server code."""
    return server_codes.get(server.upper(), server.lower())


def get_region(server: str) -> str:
    """Get region from server name."""
    return servers_to_region.get(server.upper(), 'americas')


def make_api_request(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 10
) -> Optional[Dict[str, Any]]:
    """Make HTTP request to Riot API with error handling."""

    # TEMPORARY DEBUG
    logger.warning(f" Making request:")
    logger.warning(f"   URL: {url}")
    logger.warning(f"   Headers: {headers}")
    logger.warning(f"   Params: {params}")

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout
        )

        # DEBUG response
        logger.warning(f" Response:")
        logger.warning(f"   Status: {response.status_code}")
        logger.warning(f"   Headers: {dict(response.headers)}")
        if response.status_code == 401:
            logger.warning(f"   Body: {response.text}")

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            logger.warning(f"Rate limit hit | Retry after: {retry_after}s | URL: {url}")
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")

        # Handle not found
        if response.status_code == 404:
            logger.debug(f"Resource not found | URL: {url}")
            raise NotFoundError("Resource not found")

        # Handle forbidden (invalid API key)
        if response.status_code == 403:
            logger.error(f"Forbidden - check API key | URL: {url}")
            raise RiotAPIError("Invalid API key or forbidden access")

        # Raise for other HTTP errors
        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"Request timeout | URL: {url}")
        raise RiotAPIError("Request timeout")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error | URL: {url} | Error: {e}")
        raise RiotAPIError(f"Request failed: {str(e)}")


@cached(ttl=3600, key_prefix='account')
def get_account_info(game_name: str, tag_line: str, server: str) -> Optional[Dict[str, Any]]:
    """
    Get account information by Riot ID.

    Args:
        game_name: Summoner game name
        tag_line: Summoner tag line
        server: Server name (e.g., 'EUW')

    Returns:
        Account data dictionary or None
    """
    region = get_region(server)
    api_key = get_api_key()

    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}

    logger.debug(f"Fetching account info | {game_name}#{tag_line} | Region: {region}")

    try:
        return make_api_request(url, headers=headers)
    except NotFoundError:
        return None
    except RiotAPIError as e:
        logger.error(f"Failed to get account info: {e}")
        return None


@cached(ttl=1800, key_prefix='summoner')
def get_summoner_info_puuid(puuid: str, server: str) -> Optional[Dict[str, Any]]:
    """
    Get summoner information by PUUID.

    Args:
        puuid: Player Universal Unique Identifier
        server: Server name

    Returns:
        Summoner data dictionary or None
    """
    server_code = get_server_code(server)
    api_key = get_api_key()

    url = f"https://{server_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}

    logger.debug(f"Fetching summoner info | PUUID: {puuid[:8]}... | Server: {server_code}")

    try:
        return make_api_request(url, headers=headers)
    except NotFoundError:
        return None
    except RiotAPIError as e:
        logger.error(f"Failed to get summoner info: {e}")
        return None


@cached(ttl=300, key_prefix='matches')
def get_match_ids(
        puuid: str,
        server: str,
        start: int = 0,
        count: int = 20,
        queue: Optional[int] = None
) -> List[str]:
    """
    Get list of match IDs for a player.

    Args:
        puuid: Player UUID
        server: Server name
        start: Starting index
        count: Number of matches to retrieve
        queue: Queue ID filter (optional)

    Returns:
        List of match IDs
    """
    region = get_region(server)
    api_key = get_api_key()

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    headers = {"X-Riot-Token": api_key}
    params = {
        "start": start,
        "count": count
    }

    if queue is not None:
        params["queue"] = queue

    logger.debug(f"Fetching match IDs | PUUID: {puuid[:8]}... | Start: {start} | Count: {count}")

    try:
        result = make_api_request(url, headers=headers, params=params)
        return result if result else []
    except RiotAPIError as e:
        logger.error(f"Failed to get match IDs: {e}")
        return []


@cached(ttl=3600, key_prefix='match')
def get_match_details(match_id: str, server: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed match information.

    Args:
        match_id: Match ID
        server: Server name

    Returns:
        Match data dictionary or None
    """
    region = get_region(server)
    api_key = get_api_key()

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}

    logger.debug(f"Fetching match details | ID: {match_id}")

    try:
        return make_api_request(url, headers=headers)
    except NotFoundError:
        return None
    except RiotAPIError as e:
        logger.error(f"Failed to get match details: {e}")
        return None


@cached(ttl=300, key_prefix='clash_team')
def get_team_info_puuid(summoner_id: str, server: str) -> Optional[Dict[str, Any]]:
    """
    Get clash team information for a summoner.

    Args:
        summoner_id: Summoner ID
        server: Server name

    Returns:
        Clash team data or None
    """
    server_code = get_server_code(server)
    api_key = get_api_key()

    url = f"https://{server_code}.api.riotgames.com/lol/clash/v1/players/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": api_key}

    logger.debug(f"Fetching clash team | Summoner ID: {summoner_id[:8]}...")

    try:
        teams = make_api_request(url, headers=headers)
        # Return first active team
        if teams and len(teams) > 0:
            return teams[0]
        return None
    except NotFoundError:
        return None
    except RiotAPIError as e:
        logger.error(f"Failed to get clash team: {e}")
        return None


def get_tournament_id_by_team(team_info: Dict[str, Any]) -> Optional[int]:
    """Extract tournament ID from team info."""
    return team_info.get('tournamentId')


@cached(ttl=600, key_prefix='clash_tournament')
def get_tournament_team_details(team_id: str, server: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed clash team information.

    Args:
        team_id: Clash team ID
        server: Server name

    Returns:
        Team details or None
    """
    server_code = get_server_code(server)
    api_key = get_api_key()

    url = f"https://{server_code}.api.riotgames.com/lol/clash/v1/teams/{team_id}"
    headers = {"X-Riot-Token": api_key}

    logger.debug(f"Fetching tournament team | Team ID: {team_id}")

    try:
        return make_api_request(url, headers=headers)
    except NotFoundError:
        return None
    except RiotAPIError as e:
        logger.error(f"Failed to get tournament team: {e}")
        return None


def show_players_team(tournament_id: int) -> Optional[List[Dict[str, Any]]]:
    """
    Get all players in a clash tournament team.

    Args:
        tournament_id: Tournament ID

    Returns:
        List of player data dictionaries
    """
    # This is a placeholder - actual implementation depends on your data structure
    # You might need to fetch team details and extract player info
    logger.debug(f"Fetching players for tournament: {tournament_id}")

    # Implementation would involve fetching team data and player details
    # For now, returning None to indicate not implemented
    return None


def display_matches(
        game_name: str,
        tag_line: str,
        server: str,
        count: int = 10
) -> Optional[List[Dict[str, Any]]]:
    """
    Get and format match history for a player.
    """
    logger.info(f"Fetching matches | Player: {game_name}#{tag_line} | Count: {count}")

    # Get account info
    account_info = get_account_info(game_name, tag_line, server)
    if not account_info:
        logger.warning(f"Account not found: {game_name}#{tag_line}")
        return None

    puuid = account_info['puuid']

    # Get match IDs
    match_ids = get_match_ids(puuid, server, start=0, count=count)
    if not match_ids:
        logger.warning(f"No matches found for PUUID: {puuid[:8]}...")
        return None

    # Fetch and PROCESS match details
    matches = []
    for match_id in match_ids:
        match_data = get_match_details(match_id, server)
        if match_data:
            # PROCESS THE RAW MATCH DATA
            processed_match = process_match_for_player(match_data, puuid, game_name, tag_line, server)
            if processed_match:
                matches.append(processed_match)

        # Small delay to avoid rate limiting
        time.sleep(0.05)

    logger.info(f"Retrieved {len(matches)} matches for {game_name}#{tag_line}")

    return matches


def process_match_for_player(
        match_data: dict[str, Any],
        puuid: str,
        game_name: str,
        tag_line: str,
        server: str
) -> Optional[dict[str, Any]]:
    """
    Process raw match data to extract ALL participants and highlight the searched player.
    """
    try:
        info = match_data.get('info', {})
        metadata = match_data.get('metadata', {})

        participants = info.get('participants', [])
        teams = info.get('teams', [])

        # Find the searched player
        searched_player = None
        for participant in participants:
            if participant.get('puuid') == puuid:
                searched_player = participant
                break

        if not searched_player:
            logger.warning(f"Player not found in match {metadata.get('matchId')}")
            return None

        # Process all participants
        all_participants = []
        for participant in participants:
            all_participants.append({
                'puuid': participant.get('puuid', ''),
                'summonerName': participant.get('riotIdGameName', participant.get('summonerName', 'Unknown')),
                'summonerTag': participant.get('riotIdTagline', ''),
                'championName': participant.get('championName', 'Unknown'),
                'championId': participant.get('championId', 0),
                'champLevel': participant.get('champLevel', 1),
                'teamId': participant.get('teamId', 0),
                'teamPosition': participant.get('teamPosition', ''),
                'individualPosition': participant.get('individualPosition', ''),

                # KDA
                'kills': participant.get('kills', 0),
                'deaths': participant.get('deaths', 0),
                'assists': participant.get('assists', 0),
                'win': participant.get('win', False),

                # CS
                'totalMinionsKilled': participant.get('totalMinionsKilled', 0),
                'neutralMinionsKilled': participant.get('neutralMinionsKilled', 0),

                # Combat stats
                'totalDamageDealtToChampions': participant.get('totalDamageDealtToChampions', 0),
                'totalDamageTaken': participant.get('totalDamageTaken', 0),
                'goldEarned': participant.get('goldEarned', 0),
                'visionScore': participant.get('visionScore', 0),

                # Items
                'item0': participant.get('item0', 0),
                'item1': participant.get('item1', 0),
                'item2': participant.get('item2', 0),
                'item3': participant.get('item3', 0),
                'item4': participant.get('item4', 0),
                'item5': participant.get('item5', 0),
                'item6': participant.get('item6', 0),

                # Summoner spells
                'summoner1Id': participant.get('summoner1Id', 0),
                'summoner2Id': participant.get('summoner2Id', 0),

                # Flag if this is the searched player
                'isSearchedPlayer': participant.get('puuid') == puuid
            })

        # Split into teams
        team_100 = [p for p in all_participants if p['teamId'] == 100]
        team_200 = [p for p in all_participants if p['teamId'] == 200]

        # Get team stats
        team_100_stats = next((t for t in teams if t.get('teamId') == 100), {})
        team_200_stats = next((t for t in teams if t.get('teamId') == 200), {})

        # Build complete match data
        processed = {
            # Player info (searched player)
            'summoner_name': game_name,
            'summoner_tag': tag_line,
            'SERVER': server,
            'server_slug': slugify_server(server),
            'puuid': puuid,

            # Match info
            'matchId': metadata.get('matchId', ''),
            'gameCreation': info.get('gameCreation', 0),
            'gameDuration': info.get('gameDuration', 0),
            'gameMode': info.get('gameMode', ''),
            'queueId': info.get('queueId', 0),

            # Searched player stats (for compatibility)
            'championName': searched_player.get('championName', 'Unknown'),
            'champLevel': searched_player.get('champLevel', 1),
            'championId': searched_player.get('championId', 0),
            'kills': searched_player.get('kills', 0),
            'deaths': searched_player.get('deaths', 0),
            'assists': searched_player.get('assists', 0),
            'win': searched_player.get('win', False),
            'totalMinionsKilled': searched_player.get('totalMinionsKilled', 0),
            'neutralMinionsKilled': searched_player.get('neutralMinionsKilled', 0),
            'totalDamageDealtToChampions': searched_player.get('totalDamageDealtToChampions', 0),
            'totalDamageTaken': searched_player.get('totalDamageTaken', 0),
            'totalHeal': searched_player.get('totalHeal', 0),
            'goldEarned': searched_player.get('goldEarned', 0),
            'visionScore': searched_player.get('visionScore', 0),
            'item0': searched_player.get('item0', 0),
            'item1': searched_player.get('item1', 0),
            'item2': searched_player.get('item2', 0),
            'item3': searched_player.get('item3', 0),
            'item4': searched_player.get('item4', 0),
            'item5': searched_player.get('item5', 0),
            'item6': searched_player.get('item6', 0),
            'summoner1Id': searched_player.get('summoner1Id', 0),
            'summoner2Id': searched_player.get('summoner2Id', 0),
            'profileIconId': searched_player.get('profileIconId', 0),

            # ALL PARTICIPANTS (both teams)
            'all_participants': all_participants,
            'team_100': team_100,
            'team_200': team_200,
            'team_100_win': team_100_stats.get('win', False),
            'team_200_win': team_200_stats.get('win', False),
        }

        return processed

    except Exception as e:
        logger.error(f"Error processing match data: {e}")
        return None


def display_matches_by_value(
        game_name: str,
        tag_line: str,
        server: str,
        start: int = 0,
        count: int = 5
) -> Optional[List[Dict[str, Any]]]:
    """
    Get matches starting from a specific index.

    Args:
        game_name: Summoner game name
        tag_line: Summoner tag line
        server: Server name
        start: Starting index
        count: Number of matches to retrieve

    Returns:
        List of match data or None
    """
    logger.debug(f"Fetching matches by value | Start: {start} | Count: {count}")

    # Get account info
    account_info = get_account_info(game_name, tag_line, server)
    if not account_info:
        return None

    puuid = account_info['puuid']

    # Get match IDs
    match_ids = get_match_ids(puuid, server, start=start, count=count)
    if not match_ids:
        return None

    # Fetch match details
    matches = []
    for match_id in match_ids:
        match_data = get_match_details(match_id, server)
        if match_data:
            matches.append([match_data])  # Wrap in list for compatibility

        time.sleep(0.05)

    return matches


def invalidate_player_cache(game_name: str, tag_line: str, server: str):
    """
    Invalidate all cached data for a player.

    Args:
        game_name: Summoner game name
        tag_line: Summoner tag line
        server: Server name
    """
    cache_keys = [
        f"account:{game_name}:{tag_line}:{server}",
        f"matches:{game_name}:{tag_line}:{server}"
    ]

    for key in cache_keys:
        cache.delete(key)

    logger.info(f"Invalidated cache for {game_name}#{tag_line}")