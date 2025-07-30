# question.py
import datetime
import concurrent.futures
import aiohttp
import asyncio
import requests
import functools
import time
import ssl
import certifi
from config import RIOT_API_KEY
from game_constants import RUNES_AND_SHARDS, ITEMS, SUMMONER_SPELLS

# A dictionary mapping server names to their regions and domains
servers_to_region = {
    'brazil': ['br1', 'americas', 'br'],
    'latin america north': ['la1', 'americas', 'lan'],
    'latin america south': ['la2', 'americas', 'las'],
    'north america': ['na1', 'americas', 'na'],
    'japan': ['jp1', 'asia', 'jp'],
    'korea': ['kr', 'asia', 'kr'],
    'philippines': ['ph2', 'asia', 'ph'],
    'singapore': ['sg2', 'asia', 'sg'],
    'thailand': ['th2', 'asia', 'th'],
    'taiwan': ['tw2', 'asia', 'tw'],
    'vietnam': ['vn2', 'asia', 'vn'],
    'eu nordic & east': ['eun1', 'europe', 'eune'],
    'eu west': ['euw1', 'europe', 'euw'],
    'russia': ['ru', 'europe', 'ru'],
    'turkey': ['tr1', 'europe', 'tr']
}

HEADERS = {"X-Riot-Token": RIOT_API_KEY}


# SSL Context creation
def create_ssl_context():
    """
    Create an SSL context using certifi certificates.

    Returns:
        ssl.SSLContext: Configured SSL context for secure HTTP requests.
    """
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context


# Caching decorator
def timed_cache(seconds=300):
    """
    Decorator to cache function results for a specified duration.

    Args:
        seconds (int): Time in seconds to keep results in cache.
    """

    # 5 minute cache
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        return wrapper

    return decorator


def send_get_request(url):
    """
    Perform a synchronous GET request with Riot API headers.

    Args:
        url (str): Full API endpoint URL.
    Returns:
        dict or None: Parsed JSON response if status is 200, else None.
    """
    response = requests.get(url, headers=HEADERS, verify=certifi.where())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Nie udało się uzyskać informacji. URL: {url}, Status Code: {response.status_code}")
        return None

def parse_summoner_name(full_name: str) -> tuple[str, str]:
    """
    Split a full summoner name into its base name and tag components.

    Args:
        full_name (str): Full summoner identifier, e.g. "Name#TAG" or "Name".
    Returns:
        tuple[str, str]: A two-element tuple (base_name, tag). Tag is empty if none.
    """
    if "#" in full_name:
        name, tag = full_name.split("#", 1)
        return name, tag
    else:
        return full_name, ""

# Async version of send_get_request with SSL fix
async def async_get_request(session, url):
    """
    Perform an asynchronous GET request with Riot API headers.

    Args:
        session (aiohttp.ClientSession): Active HTTP session.
        url (str): Full API endpoint URL.
    Returns:
        dict or None: Parsed JSON response if status is 200, else None.
    """
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Nie udało się uzyskać informacji. URL: {url}, Status Code: {response.status}")
                return None
    except aiohttp.ClientConnectorSSLError as e:
        print(f"SSL Error for {url}: {e}")
        # Try with SSL disabled (only for debugging)
        try:
            async with session.get(url, headers=HEADERS, ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Nie udało się uzyskać informacji. URL: {url}, Status Code: {response.status}")
                    return None
        except Exception as e:
            print(f"Error even with SSL disabled: {e}")
            return None

# Deleted in RIOT API
@timed_cache(300)
def get_account_info(summoner_name, summoner_tag, SERVER):
    """
    Retrieve account information using a player's Riot ID (name and tag).

    Args:
        summoner_name (str): Player's in-game name.
        summoner_tag (str): Player's tag or region suffix.
        SERVER (str): Key from servers_to_region mapping.
    Returns:
        dict or None: Account info JSON if successful, otherwise None.
    """

    url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    return send_get_request(url)


def get_account_info_by_puuid(puuid, SERVER):
    """
    Retrieve account information using a player's PUUID.

    Args:
        puuid (str): Player Unique Identifier.
        SERVER (str): Server key from servers_to_region.
    Returns:
        dict or None: Account info JSON or None if request fails.
    """
    url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    return send_get_request(url)


@timed_cache(300)
def get_summoner_info_puuid(puuid, SERVER):
    """
    Retrieve summoner data by PUUID.

    Args:
        puuid (str): Player Unique Identifier.
        SERVER (str): Server key from servers_to_region.
    Returns:
        dict or None: Summoner info JSON or None if request fails.
    """
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return send_get_request(url)


def get_team_info_puuid(summoner_id, SERVER):
    """
    Get Clash team membership info by summoner ID.

    Args:
        summoner_id (str): Summoner ID from summoner info.
        SERVER (str): Server key from servers_to_region.
    Returns:
        list or None: List of team entries or None on failure.
    """
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/players/by-summoner/{summoner_id}"
    return send_get_request(url)


def get_tournament_id_by_team(team_id, SERVER):
    """
    Fetch tournament info for a Clash team.

    Args:
        team_id (str): Unique team ID.
        SERVER (str): Server key from servers_to_region.
    Returns:
        dict or None: Tournament JSON data or None if request fails.
    """
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/teams/{team_id}"
    return send_get_request(url)


# Batch process players in a team
async def show_players_team_async(players, SERVER):
    """
    Concurrently retrieve profile links for team members.

    Args:
        players (list): List of dicts containing 'summonerId'.
        SERVER (str): Server key from servers_to_region.
    Returns:
        list: List of ["Name#Tag", UGG link, OP.GG link] entries.
    """
    ssl_context = create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for player in players:
            summoner_url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/summoner/v4/summoners/{player['summonerId']}"
            tasks.append(async_get_request(session, summoner_url))

        summoner_results = await asyncio.gather(*tasks)

        # Now fetch account info for all players
        account_tasks = []
        for summoner in summoner_results:
            if summoner:
                account_url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{summoner['puuid']}"
                account_tasks.append(async_get_request(session, account_url))

        account_results = await asyncio.gather(*account_tasks)

        players_info = []
        for i, account_info in enumerate(account_results):
            if account_info:
                game_name = account_info['gameName']
                tag_line = account_info['tagLine']
                profile_link = f"https://u.gg/lol/profile/{servers_to_region[SERVER][0]}/{game_name}-{tag_line}/overview"
                op_gg_link = f"https://www.op.gg/summoners/{servers_to_region[SERVER][2]}/{game_name}-{tag_line}"
                players_info.append([f"{game_name}#{tag_line}", profile_link, op_gg_link])

        return players_info


def show_players_team(players, SERVER):
    """
    Synchronously run async player info fetch.

    Args:
        players (list): Team player list.
        SERVER (str): Server key.
    Returns:
        list: Profile link entries.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(show_players_team_async(players, SERVER))
    loop.close()
    return result


def calculate_time_ago(game_start_timestamp_ms):
    """
    Convert a past timestamp to a human-readable "time ago" string.

    Args:
        timestamp_ms (int): Unix milliseconds.
    Returns:
        str: Formatted time difference, e.g. "5m ago" or "2h ago".
    """
    game_start_date = datetime.datetime.fromtimestamp(game_start_timestamp_ms / 1000)
    now = datetime.datetime.now()
    time_diff = now - game_start_date
    days_ago = time_diff.days
    seconds_ago = time_diff.seconds
    hours_ago = seconds_ago // 3600
    minutes_ago = (seconds_ago % 3600) // 60

    if days_ago >= 7:
        weeks_ago = days_ago // 7
        return f"{weeks_ago} weeks ago"
    elif days_ago >= 1:
        return f"{days_ago} days ago"
    elif hours_ago >= 1:
        return f"{hours_ago} hours ago"
    elif minutes_ago >= 1:
        return f"{minutes_ago} minutes ago"
    else:
        return "Just now"


def get_match_participant_details(match_details, puuid, SERVER):
    """
    Extract and format participant stats from match details.

    Args:
        match_details (dict): Raw match info JSON.
        puuid (str): Main player PUUID.
        SERVER (str): Key from servers_to_region.
    Returns:
        list: Participant detail dicts, main player first.
    """
    participant_details_list = []
    flag = 1
    for participant in match_details["info"]["participants"]:
        game_start_timestamp_ms = match_details["info"].get("gameStartTimestamp", 0)

        # Nowa obsługa nazw graczy - sprawdzamy różne klucze
        summoner_name = participant.get("summonerName") or participant.get("riotIdGameName") or ""
        summoner_tag = participant.get("riotIdTagline") or participant.get("tagLine") or ""

        # Jeśli nazwa jest w starym formacie z #, rozdziel ją
        if "#" in summoner_name and not summoner_tag:
            parts = summoner_name.split("#", 1)
            summoner_name = parts[0]
            summoner_tag = parts[1] if len(parts) > 1 else ""

        participant_details = {
            "Champion": participant.get("championName", ""),
            "Summoner Name": summoner_name,
            "summoner_tag": summoner_tag,
            "KDA": f'{participant.get("kills", 0)}/{participant.get("deaths", 0)}/{participant.get("assists", 0)}',
            "Items": [(participant.get(f'item{i}'), ITEMS.get(participant.get(f'item{i}'), "")) for i in range(7) if
                      participant.get(f'item{i}', 0) in ITEMS],
            "Primary Rune Path": (participant["perks"]["styles"][0].get("style"),
                                  RUNES_AND_SHARDS.get(participant["perks"]["styles"][0].get("style"), "")),
            "Primary Rune": (participant["perks"]["styles"][0]["selections"][0].get("perk"),
                             RUNES_AND_SHARDS.get(participant["perks"]["styles"][0]["selections"][0].get("perk"), "")),
            "Secondary Rune Path": (participant["perks"]["styles"][1].get("style"),
                                    RUNES_AND_SHARDS.get(participant["perks"]["styles"][1].get("style"), "")),
            "Primary Runes": [(selection.get("perk"), RUNES_AND_SHARDS.get(selection.get("perk"), "")) for selection in
                              participant["perks"]["styles"][0].get("selections", [])],
            "Secondary Runes": [(selection.get("perk"), RUNES_AND_SHARDS.get(selection.get("perk"), "")) for selection
                                in participant["perks"]["styles"][1].get("selections", [])],
            "Shards": [(shard, RUNES_AND_SHARDS.get(shard, "")) for shard in
                       participant["perks"]["statPerks"].values()],
            "CS": participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
            "Team ID": participant.get("teamId", "Unknown")
        }
        participant_details["Control Wards"] = participant.get('visionWardsBoughtInGame', 0)
        participant_details["Summoner Spells"] = [
            (participant.get('summoner1Id'), SUMMONER_SPELLS.get(participant.get('summoner1Id'), "")),
            (participant.get('summoner2Id'), SUMMONER_SPELLS.get(participant.get('summoner2Id'), ""))
        ]
        game_duration = divmod(match_details['info'].get('gameDuration', 0), 60)
        participant_details["Game Duration"] = f"{game_duration[0]}:{game_duration[1]:02d}"

        # Dodatkowe pola dla uczestnika, który jest głównym graczem
        if participant.get("puuid") == puuid:
            if flag:
                participant_details["summonerId"] = participant.get("summonerId")
            participant_details["gameStartTimestamp"] = match_details["info"].get("gameStartTimestamp", 0)
            participant_details["Match Result"] = 'Win' if participant.get('win', False) else 'Lose'
            participant_details["Start Date"] = datetime.datetime.fromtimestamp(
                game_start_timestamp_ms / 1000).strftime('%d/%m/%Y %H:%M')
            participant_details["Start Game Ago"] = calculate_time_ago(game_start_timestamp_ms)
            game_duration = divmod(match_details['info'].get('gameDuration', 0), 60)
            participant_details["Game Duration"] = f"{game_duration[0]}:{game_duration[1]:02d}"
            participant_details[
                "Kill Participation"] = f"{participant['challenges'].get('killParticipation', 0) * 100:.0f}%"
            participant_details_list.insert(0, participant_details)
        else:
            participant_details_list.append(participant_details)

    return participant_details_list


def sort_participants(participants, main_player_team_id):
    """
    Sort participants by team, placing the main player first.

    Args:
        participants (list): Raw participant detail dicts.
        main_player_team_id (int): Team ID of main player.
    Returns:
        list: Ordered participant details with main player first.
    """
    team_members = [p for p in participants[1:] if p['Team ID'] == main_player_team_id]
    opposite_team_members = [p for p in participants[1:] if p['Team ID'] != main_player_team_id]
    sorted_participants = [participants[0]] + team_members + opposite_team_members
    return sorted_participants


# Optimized match fetching
async def fetch_match_details_async(match_ids, puuid, SERVER):
    """
    Fetch multiple match details concurrently.

    Args:
        match_ids (list): List of match ID strings.
        puuid (str): Player Unique ID.
        SERVER (str): Server key.
    Returns:
        list: Raw participant detail lists for each match.
    """
    ssl_context = create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for match_id in match_ids:
            url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            tasks.append(async_get_request(session, url))

        match_results = await asyncio.gather(*tasks)

        match_history_list = []
        for match_details in match_results:
            if match_details:
                participant_details = get_match_participant_details(match_details, puuid, SERVER)
                match_history_list.append(participant_details)

        return match_history_list


def display_matches(summoner_name, summoner_tag, SERVER):
    """
    Retrieve and format the latest 20 match histories for a player.

    Args:
        summoner_name (str): Player name.
        summoner_tag (str): Player tag.
        SERVER (str): Server key.
    Returns:
        list or None: Sorted match history or None if not found.
    """
    account_info = get_account_info(summoner_name, summoner_tag, SERVER)
    if not account_info:
        return None

    puuid = account_info["puuid"]

    # Get match IDs
    match_ids_url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20"
    match_ids_list = send_get_request(match_ids_url)

    if not match_ids_list:
        return None

    # Fetch all matches asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    match_history_list = loop.run_until_complete(fetch_match_details_async(match_ids_list, puuid, SERVER))
    loop.close()

    # Sort participants
    match_history_list_sorted = []
    for match in match_history_list:
        match_history_list_sorted.append(sort_participants(match, match[0]['Team ID']))

    if match_history_list_sorted:
        match_history_list_sorted[0][0]["SERVER"] = SERVER
        match_history_list_sorted[0][0]["summoner_name"] = summoner_name
        match_history_list_sorted[0][0]["summoner_tag"] = summoner_tag

    return match_history_list_sorted


def display_matches_by_value(summoner_name, summoner_tag, SERVER, current_count, limit):
    """
   Retrieve additional matches beyond initial set.

   Args:
       summoner_name (str): Player name.
       summoner_tag (str): Player tag.
       SERVER (str): Server key.
       start (int): Starting index.
       count (int): Number of matches to fetch.
   Returns:
       list or None: Additional match entries or None.
   """
    account_info = get_account_info(summoner_name, summoner_tag, SERVER)
    if not account_info:
        return None

    puuid = account_info["puuid"]

    # Get match IDs
    match_ids_url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={current_count}&count={limit}"
    match_ids_list = send_get_request(match_ids_url)

    if not match_ids_list:
        return None

    # Fetch all matches asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    match_history_list = loop.run_until_complete(fetch_match_details_async(match_ids_list, puuid, SERVER))
    loop.close()

    # Sort participants
    match_history_list_sorted = []
    for match in match_history_list:
        match_history_list_sorted.append(sort_participants(match, match[0]['Team ID']))

    return match_history_list_sorted