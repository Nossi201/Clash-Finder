# app/services/__init__.py
"""
Services for Clash Finder application.
Contains business logic and external API interactions.
"""

from app.services.riot_api import (
    get_account_info,
    get_summoner_info_puuid,
    get_match_ids,
    get_match_details,
    get_team_info_puuid,
    get_tournament_id_by_team,
    get_tournament_team_details,
    show_players_team,
    display_matches,
    display_matches_by_value,
    invalidate_player_cache,
    servers_to_region,
    server_codes,
    RiotAPIError,
    RateLimitError,
    NotFoundError
)

from app.services.cache import (
    cache,
    cached,
    invalidate_cache,
    get_cache_stats
)

from app.services.rate_limiter import (
    rate_limiter,
    rate_limit,
    get_client_ip,
    get_rate_limit_status
)

from app.services.resource_manager import (
    resource_manager,
    ResourceManager
)

from app.services.resource_downloader import (
    resource_downloader,
    ResourceDownloader
)

from app.services.auto_updater import (
    auto_updater,
    init_updater,
    AutoUpdater
)

__all__ = [
    # Riot API
    'get_account_info',
    'get_summoner_info_puuid',
    'get_match_ids',
    'get_match_details',
    'get_team_info_puuid',
    'get_tournament_id_by_team',
    'get_tournament_team_details',
    'show_players_team',
    'display_matches',
    'display_matches_by_value',
    'invalidate_player_cache',
    'servers_to_region',
    'server_codes',
    'RiotAPIError',
    'RateLimitError',
    'NotFoundError',

    # Cache
    'cache',
    'cached',
    'invalidate_cache',
    'get_cache_stats',

    # Rate Limiter
    'rate_limiter',
    'rate_limit',
    'get_client_ip',
    'get_rate_limit_status',

    # Resource Manager
    'resource_manager',
    'ResourceManager',

    # Resource Downloader
    'resource_downloader',
    'ResourceDownloader',

    # Auto Updater
    'auto_updater',
    'init_updater',
    'AutoUpdater'
]