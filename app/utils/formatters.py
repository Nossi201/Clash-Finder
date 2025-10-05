# app/utils/formatters.py
"""
Formatting utilities for Clash Finder.
Handles URL slugs, Riot IDs, server names, and data formatting.
"""

import re
from typing import Tuple, Optional
from urllib.parse import quote, unquote

from config.logging_config import get_logger

logger = get_logger('utils.formatters')

# Server name mappings
SERVER_SLUGS = {
    'BR': 'brazil',
    'EUNE': 'eu-nordic-east',
    'EUW': 'eu-west',
    'JP': 'japan',
    'KR': 'korea',
    'LAN': 'latin-america-north',
    'LAS': 'latin-america-south',
    'NA': 'north-america',
    'OCE': 'oceania',
    'TR': 'turkey',
    'RU': 'russia',
    'PH': 'philippines',
    'SG': 'singapore',
    'TH': 'thailand',
    'TW': 'taiwan',
    'VN': 'vietnam'
}

SERVER_UNSLUG = {v: k for k, v in SERVER_SLUGS.items()}


def slugify_server(server: str) -> str:
    """
    Convert server name to URL-friendly slug.

    Args:
        server: Server code (e.g., 'EUW', 'NA')

    Returns:
        URL slug (e.g., 'eu-west', 'north-america')

    Examples:
        >>> slugify_server('EUW')
        'eu-west'
        >>> slugify_server('NA')
        'north-america'
    """
    server_upper = server.upper()
    slug = SERVER_SLUGS.get(server_upper, server.lower())

    logger.debug(f"Slugified server: {server} -> {slug}")
    return slug


def unslugify_server(slug: str) -> str:
    """
    Convert URL slug back to server code.

    Args:
        slug: URL slug (e.g., 'eu-west')

    Returns:
        Server code (e.g., 'EUW')

    Examples:
        >>> unslugify_server('eu-west')
        'EUW'
        >>> unslugify_server('north-america')
        'NA'
    """
    slug_lower = slug.lower()
    server = SERVER_UNSLUG.get(slug_lower, slug.upper())

    logger.debug(f"Unslugified server: {slug} -> {server}")
    return server


def encode_riot_id(game_name: str, tag_line: str) -> str:
    """
    Encode Riot ID for URL.

    Uses '--' separator to avoid conflicts with '#'.

    Args:
        game_name: Summoner game name
        tag_line: Summoner tag line

    Returns:
        URL-encoded Riot ID (e.g., 'PlayerName--EUW1')

    Examples:
        >>> encode_riot_id('Player Name', 'EUW1')
        'Player%20Name--EUW1'
    """
    # URL encode the parts separately
    encoded_name = quote(game_name, safe='')
    encoded_tag = quote(tag_line, safe='')

    riot_id = f"{encoded_name}--{encoded_tag}"

    logger.debug(f"Encoded Riot ID: {game_name}#{tag_line} -> {riot_id}")
    return riot_id


def decode_riot_id(riot_id: str) -> Tuple[str, str]:
    """
    Decode Riot ID from URL format.

    Args:
        riot_id: Encoded Riot ID (e.g., 'PlayerName--EUW1')

    Returns:
        Tuple of (game_name, tag_line)

    Examples:
        >>> decode_riot_id('Player%20Name--EUW1')
        ('Player Name', 'EUW1')
    """
    # Split on '--' separator
    parts = riot_id.split('--', 1)

    if len(parts) != 2:
        logger.warning(f"Invalid Riot ID format: {riot_id}")
        # Fallback: treat entire string as name with empty tag
        return unquote(riot_id), ''

    game_name = unquote(parts[0])
    tag_line = unquote(parts[1])

    logger.debug(f"Decoded Riot ID: {riot_id} -> {game_name}#{tag_line}")
    return game_name, tag_line


def parse_summoner_input(summoner_input: str) -> Tuple[str, str]:
    """
    Parse summoner input from form.

    Handles formats:
    - 'Name#TAG' - Standard Riot ID
    - 'Name' - Name only (empty tag)

    Args:
        summoner_input: Raw summoner input from form

    Returns:
        Tuple of (game_name, tag_line)

    Examples:
        >>> parse_summoner_input('Player#EUW1')
        ('Player', 'EUW1')
        >>> parse_summoner_input('Player Name#TAG')
        ('Player Name', 'TAG')
    """
    summoner_input = summoner_input.strip()

    # Split on '#'
    if '#' in summoner_input:
        parts = summoner_input.rsplit('#', 1)
        game_name = parts[0].strip()
        tag_line = parts[1].strip() if len(parts) > 1 else ''
    else:
        # No tag provided
        game_name = summoner_input
        tag_line = ''

    logger.debug(f"Parsed summoner input: {summoner_input} -> {game_name}#{tag_line}")
    return game_name, tag_line


def format_game_duration(duration_seconds: int) -> str:
    """
    Format game duration as MM:SS.

    Args:
        duration_seconds: Game duration in seconds

    Returns:
        Formatted duration string (e.g., '25:34')

    Examples:
        >>> format_game_duration(1534)
        '25:34'
        >>> format_game_duration(3661)
        '61:01'
    """
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60

    return f"{minutes}:{seconds:02d}"


def format_kda(kills: int, deaths: int, assists: int) -> str:
    """
    Format KDA as 'K/D/A'.

    Args:
        kills: Number of kills
        deaths: Number of deaths
        assists: Number of assists

    Returns:
        Formatted KDA string (e.g., '10/3/7')

    Examples:
        >>> format_kda(10, 3, 7)
        '10/3/7'
    """
    return f"{kills}/{deaths}/{assists}"


def calculate_kda_ratio(kills: int, deaths: int, assists: int) -> float:
    """
    Calculate KDA ratio.

    Formula: (kills + assists) / deaths
    If deaths = 0, returns kills + assists

    Args:
        kills: Number of kills
        deaths: Number of deaths
        assists: Number of assists

    Returns:
        KDA ratio as float

    Examples:
        >>> calculate_kda_ratio(10, 3, 7)
        5.67
        >>> calculate_kda_ratio(5, 0, 3)
        8.0
    """
    if deaths == 0:
        return float(kills + assists)

    return round((kills + assists) / deaths, 2)


def format_cs(total_minions: int, neutral_minions: int) -> str:
    """
    Format CS (creep score).

    Args:
        total_minions: Lane minions killed
        neutral_minions: Jungle monsters killed

    Returns:
        Formatted CS string (e.g., '234 CS')

    Examples:
        >>> format_cs(180, 54)
        '234 CS'
    """
    total_cs = total_minions + neutral_minions
    return f"{total_cs} CS"


def calculate_cs_per_min(total_cs: int, duration_minutes: float) -> float:
    """
    Calculate CS per minute.

    Args:
        total_cs: Total creep score
        duration_minutes: Game duration in minutes

    Returns:
        CS per minute as float

    Examples:
        >>> calculate_cs_per_min(234, 25.5)
        9.18
    """
    if duration_minutes == 0:
        return 0.0

    return round(total_cs / duration_minutes, 2)


def format_gold(gold: int) -> str:
    """
    Format gold with 'k' suffix for thousands.

    Args:
        gold: Gold amount

    Returns:
        Formatted gold string (e.g., '12.5k')

    Examples:
        >>> format_gold(12543)
        '12.5k'
        >>> format_gold(987)
        '987'
    """
    if gold >= 1000:
        return f"{gold / 1000:.1f}k"
    return str(gold)


def format_damage(damage: int) -> str:
    """
    Format damage with 'k' suffix for thousands.

    Args:
        damage: Damage amount

    Returns:
        Formatted damage string (e.g., '45.2k')

    Examples:
        >>> format_damage(45234)
        '45.2k'
        >>> format_damage(987)
        '987'
    """
    return format_gold(damage)  # Same formatting


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Examples:
        >>> sanitize_filename('player/name#tag.json')
        'player_name_tag.json'
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*#]', '_', filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')

    logger.debug(f"Sanitized filename: {filename} -> {sanitized}")
    return sanitized


def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        Truncated text

    Examples:
        >>> truncate_text('This is a very long text', 15)
        'This is a ve...'
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.

    Args:
        value: Value to format (0.0 - 1.0 or 0 - 100)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string

    Examples:
        >>> format_percentage(0.567)
        '56.7%'
        >>> format_percentage(75.5)
        '75.5%'
    """
    # Auto-detect if value is already in percentage (0-100) or ratio (0-1)
    if value <= 1.0:
        value = value * 100

    return f"{value:.{decimals}f}%"


def format_number(number: int) -> str:
    """
    Format large numbers with thousand separators.

    Args:
        number: Number to format

    Returns:
        Formatted number string

    Examples:
        >>> format_number(1234567)
        '1,234,567'
    """
    return f"{number:,}"