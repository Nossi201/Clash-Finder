# app/utils/helpers.py
"""
Helper utilities for Clash Finder.
General-purpose utility functions.
"""

import os
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

from config.logging_config import get_logger

logger = get_logger('utils.helpers')


def generate_hash(text: str, algorithm: str = 'sha256') -> str:
    """
    Generate hash of text.

    Args:
        text: Text to hash
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

    Returns:
        Hex digest of hash

    Examples:
        >>> generate_hash('test')
        '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'
    """
    hash_func = hashlib.new(algorithm)
    hash_func.update(text.encode('utf-8'))
    return hash_func.hexdigest()


def safe_get(dictionary: Dict[str, Any], *keys, default=None) -> Any:
    """
    Safely get nested dictionary value.

    Args:
        dictionary: Dictionary to search
        *keys: Nested keys to access
        default: Default value if key not found

    Returns:
        Value or default

    Examples:
        >>> data = {'a': {'b': {'c': 'value'}}}
        >>> safe_get(data, 'a', 'b', 'c')
        'value'
        >>> safe_get(data, 'a', 'x', 'y', default='not found')
        'not found'
    """
    current = dictionary

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten nested list.

    Args:
        nested_list: List of lists

    Returns:
        Flattened list

    Examples:
        >>> flatten_list([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested_list for item in sublist]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary

    Examples:
        >>> merge_dicts({'a': 1}, {'b': 2}, {'c': 3})
        {'a': 1, 'b': 2, 'c': 3}
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def remove_none_values(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from dictionary.

    Args:
        dictionary: Dictionary to clean

    Returns:
        Dictionary without None values

    Examples:
        >>> remove_none_values({'a': 1, 'b': None, 'c': 3})
        {'a': 1, 'c': 3}
    """
    return {k: v for k, v in dictionary.items() if v is not None}


def get_file_size(filepath: Union[str, Path]) -> int:
    """
    Get file size in bytes.

    Args:
        filepath: Path to file

    Returns:
        File size in bytes

    Examples:
        >>> get_file_size('data.json')
        1024
    """
    try:
        return os.path.getsize(filepath)
    except OSError as e:
        logger.error(f"Error getting file size for {filepath}: {e}")
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Examples:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if not.

    Args:
        directory: Directory path

    Returns:
        Path object

    Examples:
        >>> ensure_dir('data/cache')
        Path('data/cache')
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {path}")
    return path


def read_json_file(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Read JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data or None on error

    Examples:
        >>> read_json_file('config.json')
        {'key': 'value'}
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return None


def write_json_file(filepath: Union[str, Path], data: Dict[str, Any], pretty: bool = True) -> bool:
    """
    Write data to JSON file.

    Args:
        filepath: Path to JSON file
        data: Data to write
        pretty: Whether to format with indentation

    Returns:
        True if successful, False otherwise

    Examples:
        >>> write_json_file('output.json', {'key': 'value'})
        True
    """
    try:
        ensure_dir(Path(filepath).parent)

        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        logger.debug(f"Written JSON to {filepath}")
        return True

    except Exception as e:
        logger.error(f"Error writing to {filepath}: {e}")
        return False


def timestamp_to_datetime(timestamp: int, milliseconds: bool = True) -> datetime:
    """
    Convert Unix timestamp to datetime.

    Args:
        timestamp: Unix timestamp
        milliseconds: Whether timestamp is in milliseconds

    Returns:
        Datetime object

    Examples:
        >>> timestamp_to_datetime(1609459200000)
        datetime.datetime(2021, 1, 1, 0, 0)
    """
    if milliseconds:
        timestamp = timestamp / 1000

    return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt: datetime, milliseconds: bool = True) -> int:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: Datetime object
        milliseconds: Whether to return milliseconds

    Returns:
        Unix timestamp

    Examples:
        >>> dt = datetime(2021, 1, 1)
        >>> datetime_to_timestamp(dt)
        1609459200000
    """
    timestamp = int(dt.timestamp())

    if milliseconds:
        timestamp *= 1000

    return timestamp


def get_champion_icon(champion_name: str, version: str = '14.1.1') -> str:
    """
    Get champion icon URL with proper name mapping.

    Args:
        champion_name: Champion name from API
        version: Data Dragon version

    Returns:
        URL to champion icon
    """
    from config.champion_mapping import get_champion_icon_url
    return get_champion_icon_url(champion_name, version)

def time_ago(timestamp) -> str:
    """
    Convert timestamp to 'time ago' format.

    Args:
        timestamp: Unix timestamp in milliseconds, seconds, or datetime object

    Returns:
        Human-readable time string
    """
    from datetime import datetime

    try:
        if not timestamp or timestamp == 0:
            return 'N/A'

        # If already a datetime object
        if isinstance(timestamp, datetime):
            dt = timestamp
        # If it's a number (timestamp)
        elif isinstance(timestamp, (int, float)):
            # Convert from milliseconds to seconds if needed
            ts = float(timestamp)
            if ts > 10000000000:  # Milliseconds (Riot API format)
                ts = ts / 1000
            dt = datetime.fromtimestamp(ts)
        else:
            return 'N/A'

        # Calculate difference
        now = datetime.now()
        diff = now - dt
        seconds = diff.total_seconds()

        # Format based on time difference
        if seconds < 0:
            return 'w przyszłości'
        elif seconds < 60:
            return 'przed chwilą'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} min temu'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} godz. temu'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days} dni temu'
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f'{weeks} tyg. temu'
        else:
            return dt.strftime('%d.%m.%Y')

    except Exception as e:
        from config.logging_config import get_logger
        logger = get_logger('utils.helpers')
        logger.error(f"Error in time_ago with timestamp {timestamp}: {e}")
        return 'N/A'


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds

    Usage:
        @retry_on_failure(max_attempts=3, delay=2.0)
        def unstable_function():
            # May fail sometimes
            return result
    """
    import time
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        time.sleep(delay)

            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception

        return wrapper

    return decorator


def clamp(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        Clamped value

    Examples:
        >>> clamp(5, 0, 10)
        5
        >>> clamp(-5, 0, 10)
        0
        >>> clamp(15, 0, 10)
        10
    """
    return max(min_value, min(value, max_value))


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """
    Calculate percentage.

    Args:
        part: Part value
        total: Total value

    Returns:
        Percentage (0-100)

    Examples:
        >>> calculate_percentage(25, 100)
        25.0
        >>> calculate_percentage(1, 3)
        33.33
    """
    if total == 0:
        return 0.0

    return round((part / total) * 100, 2)


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get configuration value from Flask app config.

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value or default

    Examples:
        >>> get_config_value('DEBUG', False)
        True
    """
    from flask import current_app

    try:
        return current_app.config.get(key, default)
    except RuntimeError:
        # Not in app context
        logger.warning(f"Attempted to get config outside app context: {key}")
        return default


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary

    Examples:
        >>> deep_merge({'a': {'b': 1}}, {'a': {'c': 2}})
        {'a': {'b': 1, 'c': 2}}
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def is_production() -> bool:
    """
    Check if running in production environment.

    Returns:
        True if production, False otherwise
    """
    env = os.getenv('FLASK_ENV', 'production')
    return env.lower() == 'production'


def is_development() -> bool:
    """
    Check if running in development environment.

    Returns:
        True if development, False otherwise
    """
    env = os.getenv('FLASK_ENV', 'production')
    return env.lower() in ('development', 'dev')


def get_version() -> str:
    """
    Get application version.

    Returns:
        Version string
    """
    return get_config_value('VERSION', '1.0.0')