# config/champion_mapping.py
"""
Champion name mapping between Riot API and Data Dragon.
Some champions have different names in the API vs. image URLs.
"""

CHAMPION_NAME_MAPPING = {
    # API Name -> Data Dragon Name
    'Wukong': 'MonkeyKing',
    'LeBlanc': 'Leblanc',
    'Nunu': 'Nunu',  # Nunu & Willump
    'Renata': 'Renata',  # Renata Glasc
    'KSante': 'KSante',
    'BelVeth': 'Belveth',
    'RenataGlasc': 'Renata',
    'Fiddlesticks': 'FiddleSticks',
    'Kaisa': 'Kaisa',  # Kai'Sa
    'KhaZix': 'Khazix',  # Kha'Zix
    'KogMaw': 'KogMaw',  # Kog'Maw
    'VelKoz': 'Velkoz',  # Vel'Koz
    'ChoGath': 'Chogath',  # Cho'Gath
    'RekSai': 'RekSai',  # Rek'Sai
}


def get_champion_image_name(champion_name: str) -> str:
    """
    Get the correct champion name for Data Dragon images.

    Args:
        champion_name: Champion name from API

    Returns:
        Corrected champion name for image URLs
    """
    if not champion_name:
        return 'Unknown'

    # Check if we have a mapping
    return CHAMPION_NAME_MAPPING.get(champion_name, champion_name)


def get_champion_icon_url(champion_name: str, version: str = '14.1.1') -> str:
    """
    Get champion icon URL with fallback.

    Args:
        champion_name: Champion name from API
        version: Data Dragon version

    Returns:
        Full URL to champion icon
    """
    mapped_name = get_champion_image_name(champion_name)
    return f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{mapped_name}.png"