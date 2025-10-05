# app/utils/validators.py
"""
Validation utilities for Clash Finder.
Validates user inputs, API responses, and data integrity.
"""

import re
from typing import Optional, Tuple, List, Dict, Any

from config.logging_config import get_logger

logger = get_logger('utils.validators')


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_riot_id(game_name: str, tag_line: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Riot ID format.

    Args:
        game_name: Summoner game name
        tag_line: Summoner tag line

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_riot_id('PlayerName', 'EUW1')
        (True, None)
        >>> validate_riot_id('', 'TAG')
        (False, 'Game name cannot be empty')
    """
    # Check game name
    if not game_name or not game_name.strip():
        return False, "Game name cannot be empty"

    # Game name length (Riot limits: 3-16 characters)
    if len(game_name) < 3:
        return False, "Game name must be at least 3 characters"

    if len(game_name) > 16:
        return False, "Game name must be at most 16 characters"

    # Check for invalid characters in game name
    # Riot allows alphanumeric and spaces
    if not re.match(r'^[a-zA-Z0-9\s]+$', game_name):
        return False, "Game name contains invalid characters"

    # Check tag line (optional but validated if present)
    if tag_line:
        if len(tag_line) < 3:
            return False, "Tag line must be at least 3 characters"

        if len(tag_line) > 5:
            return False, "Tag line must be at most 5 characters"

        # Tag line should be alphanumeric
        if not re.match(r'^[a-zA-Z0-9]+$', tag_line):
            return False, "Tag line contains invalid characters"

    return True, None


def validate_server(server: str) -> Tuple[bool, Optional[str]]:
    """
    Validate server name.

    Args:
        server: Server code (e.g., 'EUW', 'NA')

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_server('EUW')
        (True, None)
        >>> validate_server('INVALID')
        (False, 'Invalid server: INVALID')
    """
    from app.services.riot_api import servers_to_region

    if not server or not server.strip():
        return False, "Server cannot be empty"

    server_upper = server.upper()

    if server_upper not in servers_to_region:
        return False, f"Invalid server: {server}"

    return True, None


def validate_match_count(count: int, max_count: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate match count parameter.

    Args:
        count: Number of matches requested
        max_count: Maximum allowed matches

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_match_count(20)
        (True, None)
        >>> validate_match_count(150)
        (False, 'Match count cannot exceed 100')
    """
    if count <= 0:
        return False, "Match count must be positive"

    if count > max_count:
        return False, f"Match count cannot exceed {max_count}"

    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.

    Args:
        email: Email address

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_email('user@example.com')
        (True, None)
        >>> validate_email('invalid-email')
        (False, 'Invalid email format')
    """
    if not email or not email.strip():
        return False, "Email cannot be empty"

    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_puuid(puuid: str) -> Tuple[bool, Optional[str]]:
    """
    Validate PUUID format.

    Args:
        puuid: Player Universal Unique Identifier

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_puuid('abcd1234-ef56-7890-abcd-1234567890ab')
        (True, None)
    """
    if not puuid or not puuid.strip():
        return False, "PUUID cannot be empty"

    # PUUID should be a valid UUID format or Riot's encrypted ID
    # Basic check for reasonable length and characters
    if len(puuid) < 10:
        return False, "PUUID too short"

    if len(puuid) > 100:
        return False, "PUUID too long"

    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', puuid):
        return False, "PUUID contains invalid characters"

    return True, None


def validate_json_structure(data: Any, required_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON data structure.

    Args:
        data: JSON data to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_json_structure({'name': 'test'}, ['name'])
        (True, None)
        >>> validate_json_structure({'name': 'test'}, ['name', 'id'])
        (False, 'Missing required field: id')
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    return True, None


def validate_api_response(response: Dict[str, Any], expected_keys: List[str]) -> bool:
    """
    Validate API response contains expected keys.

    Args:
        response: API response dictionary
        expected_keys: List of expected keys

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_api_response({'puuid': 'abc', 'gameName': 'test'}, ['puuid'])
        True
    """
    if not response or not isinstance(response, dict):
        logger.warning("Invalid API response: not a dictionary")
        return False

    for key in expected_keys:
        if key not in response:
            logger.warning(f"Missing key in API response: {key}")
            return False

    return True


def validate_champion_id(champion_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate champion ID.

    Args:
        champion_id: Champion identifier

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_champion_id(1)
        (True, None)
        >>> validate_champion_id(-1)
        (False, 'Champion ID must be positive')
    """
    if champion_id <= 0:
        return False, "Champion ID must be positive"

    if champion_id > 1000:
        return False, "Champion ID out of range"

    return True, None


def validate_item_id(item_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate item ID.

    Args:
        item_id: Item identifier

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_item_id(1001)
        (True, None)
        >>> validate_item_id(-1)
        (False, 'Item ID must be non-negative')
    """
    if item_id < 0:
        return False, "Item ID must be non-negative"

    if item_id > 10000:
        return False, "Item ID out of range"

    return True, None


def validate_queue_id(queue_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate queue ID.

    Args:
        queue_id: Queue identifier

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_queue_id(420)
        (True, None)
    """
    # Common queue IDs (not exhaustive)
    valid_queues = {
        0, 2, 4, 6, 7, 8, 9, 14, 16, 17, 25, 31, 32, 33, 41, 42, 52,
        61, 65, 67, 72, 73, 75, 76, 78, 83, 84, 90, 91, 92, 93, 96, 98,
        100, 300, 310, 313, 315, 317, 318, 325, 400, 410, 420, 430, 440,
        450, 460, 470, 490, 700, 720, 800, 810, 820, 830, 840, 850, 900,
        910, 920, 940, 950, 960, 980, 990, 1000, 1010, 1020, 1030, 1040,
        1050, 1060, 1070, 1090, 1100, 1110, 1111, 1200, 1300, 1400, 1900,
        2000, 2010, 2020
    }

    if queue_id < 0:
        return False, "Queue ID must be non-negative"

    # Allow all queue IDs but log warning for unknown ones
    if queue_id not in valid_queues:
        logger.debug(f"Unknown queue ID: {queue_id}")

    return True, None


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitize user input.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Examples:
        >>> sanitize_input('  Test Input  ')
        'Test Input'
        >>> sanitize_input('<script>alert("xss")</script>')
        'scriptalert("xss")/script'
    """
    # Strip whitespace
    text = text.strip()

    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Remove special characters that could be problematic
    text = re.sub(r'[<>\"\'`]', '', text)

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def validate_pagination(start: int, count: int, max_count: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.

    Args:
        start: Starting index
        count: Number of items
        max_count: Maximum items per page

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_pagination(0, 20)
        (True, None)
        >>> validate_pagination(-1, 20)
        (False, 'Start index must be non-negative')
    """
    if start < 0:
        return False, "Start index must be non-negative"

    if count <= 0:
        return False, "Count must be positive"

    if count > max_count:
        return False, f"Count cannot exceed {max_count}"

    return True, None


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date range.

    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)

    Returns:
        Tuple of (is_valid, error_message)
    """
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        if start > end:
            return False, "Start date must be before end date"

        # Check if range is reasonable (e.g., not more than 1 year)
        if (end - start).days > 365:
            return False, "Date range too large (max 1 year)"

        return True, None

    except ValueError as e:
        return False, f"Invalid date format: {e}"


def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL.

    Args:
        url: URL to validate

    Returns:
        True if valid URL, False otherwise

    Examples:
        >>> is_valid_url('https://example.com')
        True
        >>> is_valid_url('not-a-url')
        False
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    return bool(url_pattern.match(url))


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate file extension.

    Args:
        filename: Name of file
        allowed_extensions: List of allowed extensions (e.g., ['.json', '.csv'])

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_file_extension('data.json', ['.json', '.csv'])
        (True, None)
        >>> validate_file_extension('data.exe', ['.json'])
        (False, 'Invalid file extension: .exe')
    """
    import os

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in allowed_extensions:
        return False, f"Invalid file extension: {ext}"

    return True, None