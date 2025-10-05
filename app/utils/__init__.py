# app/utils/__init__.py
"""
Utility functions for Clash Finder application.
"""

from app.utils.formatters import (
    slugify_server,
    unslugify_server,
    encode_riot_id,
    decode_riot_id,
    parse_summoner_input,
    format_game_duration,
    format_kda,
    calculate_kda_ratio,
    format_cs,
    calculate_cs_per_min,
    format_gold,
    format_damage,
    sanitize_filename,
    truncate_text,
    format_percentage,
    format_number
)

from app.utils.decorators import (
    log_request_time,
    conditional_rate_limit,
    validate_server,
    validate_riot_id,
    require_api_key,
    cache_response,
    json_required,
    handle_errors,
    admin_required,
    timing_stats
)

from app.utils.validators import (
    ValidationError,
    validate_riot_id as validate_riot_id_format,
    validate_server as validate_server_name,
    validate_match_count,
    validate_email,
    validate_puuid,
    validate_json_structure,
    validate_api_response,
    validate_champion_id,
    validate_item_id,
    validate_queue_id,
    sanitize_input,
    validate_pagination,
    validate_date_range,
    is_valid_url,
    validate_file_extension
)

from app.utils.helpers import (
    generate_hash,
    safe_get,
    chunk_list,
    flatten_list,
    merge_dicts,
    remove_none_values,
    get_file_size,
    format_file_size,
    ensure_dir,
    read_json_file,
    write_json_file,
    timestamp_to_datetime,
    datetime_to_timestamp,
    time_ago,
    retry_on_failure,
    clamp,
    calculate_percentage,
    get_config_value,
    deep_merge,
    is_production,
    is_development,
    get_version
)

__all__ = [
    # Formatters
    'slugify_server',
    'unslugify_server',
    'encode_riot_id',
    'decode_riot_id',
    'parse_summoner_input',
    'format_game_duration',
    'format_kda',
    'calculate_kda_ratio',
    'format_cs',
    'calculate_cs_per_min',
    'format_gold',
    'format_damage',
    'sanitize_filename',
    'truncate_text',
    'format_percentage',
    'format_number',

    # Decorators
    'log_request_time',
    'conditional_rate_limit',
    'validate_server',
    'validate_riot_id',
    'require_api_key',
    'cache_response',
    'json_required',
    'handle_errors',
    'admin_required',
    'timing_stats',

    # Validators
    'ValidationError',
    'validate_riot_id_format',
    'validate_server_name',
    'validate_match_count',
    'validate_email',
    'validate_puuid',
    'validate_json_structure',
    'validate_api_response',
    'validate_champion_id',
    'validate_item_id',
    'validate_queue_id',
    'sanitize_input',
    'validate_pagination',
    'validate_date_range',
    'is_valid_url',
    'validate_file_extension',

    # Helpers
    'generate_hash',
    'safe_get',
    'chunk_list',
    'flatten_list',
    'merge_dicts',
    'remove_none_values',
    'get_file_size',
    'format_file_size',
    'ensure_dir',
    'read_json_file',
    'write_json_file',
    'timestamp_to_datetime',
    'datetime_to_timestamp',
    'time_ago',
    'retry_on_failure',
    'clamp',
    'calculate_percentage',
    'get_config_value',
    'deep_merge',
    'is_production',
    'is_development',
    'get_version'
]