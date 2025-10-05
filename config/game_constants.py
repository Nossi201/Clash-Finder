# config/game_constants.py
"""
League of Legends game constants.
Queue IDs, game modes, and other static game data.
"""

# Queue IDs and their descriptions
QUEUE_TYPES = {
    0: "Custom Game",
    2: "Blind Pick 5v5",
    4: "Ranked Solo 5v5",
    6: "Ranked Premade 5v5",
    7: "Co-op vs AI 5v5",
    8: "Normal 3v3",
    9: "Ranked Premade 3v3",
    14: "Normal 5v5 Draft Pick",
    16: "Dominion 5v5 Blind Pick",
    17: "Dominion 5v5 Draft Pick",
    25: "Dominion Co-op vs AI",
    31: "Co-op vs AI Intro Bot 5v5",
    32: "Co-op vs AI Beginner Bot 5v5",
    33: "Co-op vs AI Intermediate Bot 5v5",
    41: "Ranked Team 3v3",
    42: "Ranked Team 5v5",
    52: "Co-op vs AI 3v3",
    61: "Team Builder 5v5",
    65: "ARAM 5v5",
    67: "ARAM Co-op vs AI 5v5",
    70: "One for All 5v5",
    72: "Snowdown Showdown 1v1",
    73: "Snowdown Showdown 2v2",
    75: "Hexakill 6v6",
    76: "Ultra Rapid Fire",
    78: "One For All: Mirror Mode",
    83: "Co-op vs AI Ultra Rapid Fire",
    91: "Doom Bots Rank 1",
    92: "Doom Bots Rank 2",
    93: "Doom Bots Rank 5",
    96: "Ascension",
    98: "Hexakill 6v6",
    100: "Butcher's Bridge 5v5",
    300: "Legend of the Poro King",
    310: "Nemesis Draft",
    313: "Black Market Brawlers",
    315: "Nexus Siege",
    317: "Definitely Not Dominion",
    318: "ARURF",
    325: "All Random Summoner's Rift",
    400: "Normal Draft Pick",
    410: "Ranked Dynamic",
    420: "Ranked Solo/Duo",
    430: "Normal Blind Pick",
    440: "Ranked Flex",
    450: "ARAM",
    460: "Blind Pick 3v3",
    470: "Ranked Flex 3v3",
    490: "Normal Quickplay",
    600: "Blood Hunt Assassin",
    610: "Dark Star: Singularity",
    700: "Clash",
    720: "Clash ARAM",
    800: "Co-op vs. AI Intermediate Bot",
    810: "Co-op vs. AI Intro Bot",
    820: "Co-op vs. AI Beginner Bot",
    830: "Co-op vs. AI Intro Bot",
    840: "Co-op vs. AI Beginner Bot",
    850: "Co-op vs. AI Intermediate Bot",
    900: "ARURF",
    910: "Ascension",
    920: "Legend of the Poro King",
    940: "Nexus Siege",
    950: "Doom Bots Voting",
    960: "Doom Bots Standard",
    980: "Star Guardian Invasion: Normal",
    990: "Star Guardian Invasion: Onslaught",
    1000: "PROJECT: Hunters",
    1010: "Snow ARURF",
    1020: "One for All",
    1030: "Odyssey Extraction: Intro",
    1040: "Odyssey Extraction: Cadet",
    1050: "Odyssey Extraction: Crewmember",
    1060: "Odyssey Extraction: Captain",
    1070: "Odyssey Extraction: Onslaught",
    1090: "Teamfight Tactics",
    1100: "Ranked Teamfight Tactics",
    1110: "Teamfight Tactics Tutorial",
    1111: "Teamfight Tactics Test",
    1200: "Nexus Blitz",
    1300: "Nexus Blitz",
    1400: "Ultimate Spellbook",
    1900: "URF",
    2000: "Tutorial 1",
    2010: "Tutorial 2",
    2020: "Tutorial 3",
}


def get_queue_name(queue_id: int) -> str:
    """Get queue name from ID."""
    return QUEUE_TYPES.get(queue_id, f"Unknown Queue ({queue_id})")


# Ranked queues
RANKED_QUEUES = {420, 440, 470}

# ARAM queues
ARAM_QUEUES = {65, 450, 720}

# URF queues
URF_QUEUES = {76, 318, 900, 1010, 1900}

# Clash queues
CLASH_QUEUES = {700, 720}


def is_ranked_queue(queue_id: int) -> bool:
    """Check if queue is ranked."""
    return queue_id in RANKED_QUEUES


def is_aram_queue(queue_id: int) -> bool:
    """Check if queue is ARAM."""
    return queue_id in ARAM_QUEUES


def is_urf_queue(queue_id: int) -> bool:
    """Check if queue is URF."""
    return queue_id in URF_QUEUES


def is_clash_queue(queue_id: int) -> bool:
    """Check if queue is Clash."""
    return queue_id in CLASH_QUEUES


# Game modes
GAME_MODES = {
    'CLASSIC': 'Summoner\'s Rift',
    'ARAM': 'ARAM',
    'TUTORIAL': 'Tutorial',
    'URF': 'Ultra Rapid Fire',
    'DOOMBOTSTEEMO': 'Doom Bots',
    'ONEFORALL': 'One for All',
    'ASCENSION': 'Ascension',
    'FIRSTBLOOD': 'Snowdown Showdown',
    'KINGPORO': 'Legend of the Poro King',
    'SIEGE': 'Nexus Siege',
    'ASSASSINATE': 'Blood Hunt Assassin',
    'ARSR': 'All Random Summoner\'s Rift',
    'DARKSTAR': 'Dark Star: Singularity',
    'STARGUARDIAN': 'Star Guardian Invasion',
    'PROJECT': 'PROJECT: Hunters',
    'GAMEMODEX': 'Nexus Blitz',
    'ODYSSEY': 'Odyssey: Extraction',
    'NEXUSBLITZ': 'Nexus Blitz',
    'ULTBOOK': 'Ultimate Spellbook',
    'CHERRY': 'Arena',
}


def get_game_mode_name(game_mode: str) -> str:
    """Get game mode display name."""
    return GAME_MODES.get(game_mode, game_mode)


# Game types
GAME_TYPES = {
    'CUSTOM_GAME': 'Custom',
    'MATCHED_GAME': 'Matchmade',
    'TUTORIAL_GAME': 'Tutorial',
}

# Team IDs
TEAM_BLUE = 100
TEAM_RED = 200


def get_team_color(team_id: int) -> str:
    """Get team color name."""
    return 'Blue' if team_id == TEAM_BLUE else 'Red'


# Positions/Roles
POSITIONS = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MIDDLE': 'Mid',
    'BOTTOM': 'Bot',
    'UTILITY': 'Support',
}


def get_position_name(position: str) -> str:
    """Get position display name."""
    return POSITIONS.get(position.upper(), position)


# Summoner Spell IDs
SUMMONER_SPELLS = {
    1: 'Cleanse',
    3: 'Exhaust',
    4: 'Flash',
    6: 'Ghost',
    7: 'Heal',
    11: 'Smite',
    12: 'Teleport',
    13: 'Clarity',
    14: 'Ignite',
    21: 'Barrier',
    30: 'To the King!',
    31: 'Poro Toss',
    32: 'Mark',
    39: 'Ultra (URF Cannon)',
}


def get_summoner_spell_name(spell_id: int) -> str:
    """Get summoner spell name from ID."""
    return SUMMONER_SPELLS.get(spell_id, f'Unknown Spell ({spell_id})')


# Tier ranks
TIERS = {
    'IRON': 'Iron',
    'BRONZE': 'Bronze',
    'SILVER': 'Silver',
    'GOLD': 'Gold',
    'PLATINUM': 'Platinum',
    'EMERALD': 'Emerald',
    'DIAMOND': 'Diamond',
    'MASTER': 'Master',
    'GRANDMASTER': 'Grandmaster',
    'CHALLENGER': 'Challenger',
}

DIVISIONS = {
    'I': '1',
    'II': '2',
    'III': '3',
    'IV': '4',
}


def get_rank_display(tier: str, division: str = None) -> str:
    """Get formatted rank display."""
    tier_name = TIERS.get(tier.upper(), tier)

    if division and tier.upper() not in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
        div_num = DIVISIONS.get(division.upper(), division)
        return f"{tier_name} {div_num}"

    return tier_name


# Map IDs
MAP_IDS = {
    1: "Summoner's Rift (Original Summer)",
    2: "Summoner's Rift (Original Autumn)",
    3: "The Proving Grounds",
    4: "Twisted Treeline (Original)",
    8: "The Crystal Scar",
    10: "Twisted Treeline",
    11: "Summoner's Rift",
    12: "Howling Abyss",
    14: "Butcher's Bridge",
    16: "Cosmic Ruins",
    18: "Valoran City Park",
    19: "Substructure 43",
    20: "Crash Site",
    21: "Nexus Blitz",
    22: "Convergence",
    30: "Rings of Wrath",
}


def get_map_name(map_id: int) -> str:
    """Get map name from ID."""
    return MAP_IDS.get(map_id, f"Unknown Map ({map_id})")


# Item categories
ITEM_CATEGORIES = {
    'BOOTS': 'Boots',
    'MYTHIC': 'Mythic Item',
    'LEGENDARY': 'Legendary Item',
    'EPIC': 'Epic Item',
    'BASIC': 'Basic Item',
    'CONSUMABLE': 'Consumable',
    'TRINKET': 'Trinket',
}

# Maximum values
MAX_CHAMPION_LEVEL = 18
MAX_ITEM_SLOTS = 7  # 6 items + 1 trinket
MAX_SUMMONER_LEVEL = 500  # No actual max, but practical limit

# Game duration limits (seconds)
MIN_GAME_DURATION = 180  # 3 minutes
EARLY_SURRENDER_TIME = 900  # 15 minutes
NORMAL_SURRENDER_TIME = 1200  # 20 minutes


def can_early_surrender(duration: int) -> bool:
    """Check if early surrender is possible."""
    return duration >= EARLY_SURRENDER_TIME


def can_normal_surrender(duration: int) -> bool:
    """Check if normal surrender is possible."""
    return duration >= NORMAL_SURRENDER_TIME