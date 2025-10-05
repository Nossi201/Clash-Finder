# config/cdn_config.py
"""
CDN configuration for Data Dragon resources.
Manages URLs for champion icons, items, spells, and runes.
"""

import os

# Data Dragon version
DDRAGON_VERSION = os.getenv('DDRAGON_VERSION', '15.19.1')

# CDN Base URLs
CDN_BASE_URL = 'https://ddragon.leagueoflegends.com/cdn'
COMMUNITY_DRAGON_URL = 'https://raw.communitydragon.org/latest'

# Resource paths
RESOURCE_PATHS = {
    'champion': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/champion',
    'item': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/item',
    'spell': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/spell',
    'passive': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/passive',
    'profileicon': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/profileicon',
    'sprite': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/sprite',
    'ui': f'{CDN_BASE_URL}/{DDRAGON_VERSION}/img/ui',
}

# Community Dragon paths (for runes and newer assets)
COMMUNITY_PATHS = {
    'rune': f'{COMMUNITY_DRAGON_URL}/plugins/rcp-be-lol-game-data/global/default/v1/perk-images',
    'perkstyle': f'{COMMUNITY_DRAGON_URL}/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles',
}


def get_champion_icon_url(champion_image: str) -> str:
    """
    Get champion icon URL.

    Args:
        champion_image: Champion image filename (e.g., 'Aatrox.png')

    Returns:
        Full CDN URL

    Examples:
        >>> get_champion_icon_url('Aatrox.png')
        'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'
    """
    return f"{RESOURCE_PATHS['champion']}/{champion_image}"


def get_item_icon_url(item_image: str) -> str:
    """
    Get item icon URL.

    Args:
        item_image: Item image filename (e.g., '1001.png')

    Returns:
        Full CDN URL

    Examples:
        >>> get_item_icon_url('1001.png')
        'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/item/1001.png'
    """
    return f"{RESOURCE_PATHS['item']}/{item_image}"


def get_summoner_spell_icon_url(spell_image: str) -> str:
    """
    Get summoner spell icon URL.

    Args:
        spell_image: Spell image filename (e.g., 'SummonerFlash.png')

    Returns:
        Full CDN URL

    Examples:
        >>> get_summoner_spell_icon_url('SummonerFlash.png')
        'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/spell/SummonerFlash.png'
    """
    return f"{RESOURCE_PATHS['spell']}/{spell_image}"


def get_profile_icon_url(icon_id: int) -> str:
    """
    Get profile icon URL.

    Args:
        icon_id: Profile icon ID

    Returns:
        Full CDN URL

    Examples:
        >>> get_profile_icon_url(29)
        'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/29.png'
    """
    return f"{RESOURCE_PATHS['profileicon']}/{icon_id}.png"


def get_rune_icon_url(icon_path: str) -> str:
    """
    Get rune icon URL from Community Dragon.

    Args:
        icon_path: Rune icon path from API

    Returns:
        Full CDN URL

    Examples:
        >>> get_rune_icon_url('perk-images/Styles/Domination/Electrocute/Electrocute.png')
        'https://raw.communitydragon.org/latest/plugins/...'
    """
    # Remove leading slash if present
    icon_path = icon_path.lstrip('/')

    # Check if path already includes 'perk-images'
    if 'perk-images' in icon_path:
        # Extract the part after 'perk-images'
        parts = icon_path.split('perk-images/')
        if len(parts) > 1:
            icon_path = parts[1]

    return f"{COMMUNITY_PATHS['rune']}/{icon_path}"


def get_perk_style_icon_url(style_id: int) -> str:
    """
    Get perk style (rune tree) icon URL.

    Args:
        style_id: Perk style ID (e.g., 8000 for Precision)

    Returns:
        Full CDN URL

    Examples:
        >>> get_perk_style_icon_url(8000)
        'https://raw.communitydragon.org/latest/.../8000/8000.png'
    """
    return f"{COMMUNITY_PATHS['perkstyle']}/{style_id}/{style_id}.png"


def get_champion_splash_url(champion_key: str, skin_num: int = 0) -> str:
    """
    Get champion splash art URL.

    Args:
        champion_key: Champion key (e.g., 'Aatrox')
        skin_num: Skin number (0 = default)

    Returns:
        Full CDN URL

    Examples:
        >>> get_champion_splash_url('Aatrox', 0)
        'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aatrox_0.jpg'
    """
    return f"{CDN_BASE_URL}/img/champion/splash/{champion_key}_{skin_num}.jpg"


def get_champion_loading_url(champion_key: str, skin_num: int = 0) -> str:
    """
    Get champion loading screen art URL.

    Args:
        champion_key: Champion key (e.g., 'Aatrox')
        skin_num: Skin number (0 = default)

    Returns:
        Full CDN URL

    Examples:
        >>> get_champion_loading_url('Aatrox', 0)
        'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Aatrox_0.jpg'
    """
    return f"{CDN_BASE_URL}/img/champion/loading/{champion_key}_{skin_num}.jpg"


def get_data_dragon_json_url(data_type: str, language: str = 'en_US') -> str:
    """
    Get Data Dragon JSON data URL.

    Args:
        data_type: Type of data ('champion', 'item', 'summoner', 'runesReforged')
        language: Language code (e.g., 'en_US', 'pl_PL')

    Returns:
        Full CDN URL

    Examples:
        >>> get_data_dragon_json_url('champion')
        'https://ddragon.leagueoflegends.com/cdn/14.1.1/data/en_US/champion.json'
    """
    return f"{CDN_BASE_URL}/{DDRAGON_VERSION}/data/{language}/{data_type}.json"


def get_version_list_url() -> str:
    """
    Get URL for Data Dragon version list.

    Returns:
        Full API URL

    Examples:
        >>> get_version_list_url()
        'https://ddragon.leagueoflegends.com/api/versions.json'
    """
    return f"{CDN_BASE_URL.replace('/cdn', '')}/api/versions.json"


# Perk style IDs (rune trees)
PERK_STYLES = {
    8000: 'Precision',
    8100: 'Domination',
    8200: 'Sorcery',
    8300: 'Inspiration',
    8400: 'Resolve'
}


def get_perk_style_name(style_id: int) -> str:
    """
    Get perk style name from ID.

    Args:
        style_id: Perk style ID

    Returns:
        Style name

    Examples:
        >>> get_perk_style_name(8000)
        'Precision'
    """
    return PERK_STYLES.get(style_id, f'Unknown ({style_id})')


# Default images for missing assets
DEFAULT_CHAMPION_ICON = f"{RESOURCE_PATHS['champion']}/Unknown.png"
DEFAULT_ITEM_ICON = f"{RESOURCE_PATHS['item']}/0.png"
DEFAULT_SPELL_ICON = f"{RESOURCE_PATHS['spell']}/SummonerBlank.png"
DEFAULT_PROFILE_ICON = f"{RESOURCE_PATHS['profileicon']}/0.png"


def get_default_icon(icon_type: str) -> str:
    """
    Get default icon URL for missing assets.

    Args:
        icon_type: Type of icon ('champion', 'item', 'spell', 'profile')

    Returns:
        Default icon URL
    """
    defaults = {
        'champion': DEFAULT_CHAMPION_ICON,
        'item': DEFAULT_ITEM_ICON,
        'spell': DEFAULT_SPELL_ICON,
        'profile': DEFAULT_PROFILE_ICON
    }

    return defaults.get(icon_type, DEFAULT_CHAMPION_ICON)