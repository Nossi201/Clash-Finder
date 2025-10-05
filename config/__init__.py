# config/__init__.py
"""
Configuration module for Clash Finder application.
"""

from config.base import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    config,
    get_config
)

from config.cdn_config import (
    DDRAGON_VERSION,
    CDN_BASE_URL,
    COMMUNITY_DRAGON_URL,
    RESOURCE_PATHS,
    COMMUNITY_PATHS,
    get_champion_icon_url,
    get_item_icon_url,
    get_summoner_spell_icon_url,
    get_profile_icon_url,
    get_rune_icon_url,
    get_perk_style_icon_url,
    get_champion_splash_url,
    get_champion_loading_url,
    get_data_dragon_json_url,
    get_version_list_url,
    get_default_icon,
    PERK_STYLES,
    get_perk_style_name
)

from config.game_constants import (
    QUEUE_TYPES,
    get_queue_name,
    is_ranked_queue,
    is_aram_queue,
    is_urf_queue,
    is_clash_queue,
    GAME_MODES,
    get_game_mode_name,
    TEAM_BLUE,
    TEAM_RED,
    get_team_color,
    POSITIONS,
    get_position_name,
    SUMMONER_SPELLS,
    get_summoner_spell_name,
    TIERS,
    DIVISIONS,
    get_rank_display,
    MAP_IDS,
    get_map_name,
    MAX_CHAMPION_LEVEL,
    MAX_ITEM_SLOTS,
    can_early_surrender,
    can_normal_surrender
)

from config.ssl_config import (
    SSLConfig,
    generate_self_signed_cert,
    check_ssl_configuration
)

from config.logging_config import (
    setup_logging,
    get_logger,
    log_error_with_context,
    log_request_info,
    log_player_search,
    log_api_call,
    setup_request_logging,
    get_app_logger,
    get_api_logger,
    get_db_logger,
    get_cache_logger,
    log_execution_time,
    log_cache_hit,
    log_cache_miss,
    log_rate_limit_exceeded
)

__all__ = [
    # Base Config
    'Config',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'config',
    'get_config',

    # CDN Config
    'DDRAGON_VERSION',
    'CDN_BASE_URL',
    'COMMUNITY_DRAGON_URL',
    'RESOURCE_PATHS',
    'COMMUNITY_PATHS',
    'get_champion_icon_url',
    'get_item_icon_url',
    'get_summoner_spell_icon_url',
    'get_profile_icon_url',
    'get_rune_icon_url',
    'get_perk_style_icon_url',
    'get_champion_splash_url',
    'get_champion_loading_url',
    'get_data_dragon_json_url',
    'get_version_list_url',
    'get_default_icon',
    'PERK_STYLES',
    'get_perk_style_name',

    # Game Constants
    'QUEUE_TYPES',
    'get_queue_name',
    'is_ranked_queue',
    'is_aram_queue',
    'is_urf_queue',
    'is_clash_queue',
    'GAME_MODES',
    'get_game_mode_name',
    'TEAM_BLUE',
    'TEAM_RED',
    'get_team_color',
    'POSITIONS',
    'get_position_name',
    'SUMMONER_SPELLS',
    'get_summoner_spell_name',
    'TIERS',
    'DIVISIONS',
    'get_rank_display',
    'MAP_IDS',
    'get_map_name',
    'MAX_CHAMPION_LEVEL',
    'MAX_ITEM_SLOTS',
    'can_early_surrender',
    'can_normal_surrender',

    # SSL Config
    'SSLConfig',
    'generate_self_signed_cert',
    'check_ssl_configuration',

    # Logging Config
    'setup_logging',
    'get_logger',
    'log_error_with_context',
    'log_request_info',
    'log_player_search',
    'log_api_call',
    'setup_request_logging',
    'get_app_logger',
    'get_api_logger',
    'get_db_logger',
    'get_cache_logger',
    'log_execution_time',
    'log_cache_hit',
    'log_cache_miss',
    'log_rate_limit_exceeded'
]