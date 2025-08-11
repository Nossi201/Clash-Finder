# question.py — full, app.py‑compatible version
# NOTE: Keep code in English. Polish only in chat.

import datetime
import aiohttp
import asyncio
import requests
import functools
import time
import ssl
import certifi
import random
from urllib.parse import quote as url_quote  # avoid name clashes

from config import RIOT_API_KEY
from cdn_config import (
    get_item_name,
    get_rune_name,
    get_rune_style_name,
    get_summoner_spell_name,
    get_stat_shard_name,
)

# =====================================
# Global / constants
# =====================================
# ---- rate limit config (safe defaults for dev key) ----
MAX_MATCH_CONCURRENCY = 3     # how many matches fetched in parallel
ASYNC_MAX_RETRIES = 3         # total tries per request (initial + retries)
BACKOFF_BASE = 0.6            # seconds
BACKOFF_MAX = 8.0             # cap
JITTER = 0.35                 # add up to ±JITTER seconds

# Mapping: human server label -> [platformRoute, regionalRoute, shortSlug]
# Must match labels used in the UI and app.py
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

# Holds the most recently used SERVER so functions that app.py calls
# without SERVER can still work (e.g., show_players_team).
_last_server: str | None = None


# =====================================
# Utilities
# =====================================

def create_ssl_context() -> ssl.SSLContext:
    """Create SSL context using certifi CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def timed_cache(seconds: int = 300):
    """Tiny TTL cache decorator for sync functions."""
    def decorator(func):
        cache: dict[str, tuple[object, float]] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                value, ts = cache[key]
                if time.time() - ts < seconds:
                    return value
            value = func(*args, **kwargs)
            cache[key] = (value, time.time())
            return value
        return wrapper
    return decorator


def send_get_request(url: str):
    """Synchronous GET wrapper with Riot headers and SSL verification."""
    resp = requests.get(url, headers=HEADERS, verify=certifi.where())
    if resp.status_code == 200:
        return resp.json()
    print(f"Request failed: {url} -> {resp.status_code}")
    return None


# Async version of send_get_request with retries and backoff
async def async_get_request(session, url):
    """
    Perform an asynchronous GET request with Riot API headers.
    Retries on 429/5xx with exponential backoff + jitter.
    """
    for attempt in range(1, ASYNC_MAX_RETRIES + 1):
        try:
            async with session.get(url, headers=HEADERS) as response:
                # Success
                if response.status == 200:
                    return await response.json()

                # Too Many Requests: respect Retry-After if present
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except Exception:
                            delay = BACKOFF_BASE * (2 ** (attempt - 1))
                    else:
                        delay = BACKOFF_BASE * (2 ** (attempt - 1))

                    delay = min(delay + random.uniform(0, JITTER), BACKOFF_MAX)
                    if attempt < ASYNC_MAX_RETRIES:
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"[429] Giving up after {attempt} attempts: {url}")
                        return None

                # Server errors: 5xx -> exponential backoff
                if 500 <= response.status < 600:
                    delay = min(BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, JITTER), BACKOFF_MAX)
                    if attempt < ASYNC_MAX_RETRIES:
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"[{response.status}] Server error after {attempt} attempts: {url}")
                        return None

                # Other 4xx (not retrying)
                print(f"[{response.status}] Non-retryable status for {url}")
                return None

        except aiohttp.ClientConnectorSSLError as e:
            # One-time SSL fallback (debug)
            try:
                async with session.get(url, headers=HEADERS, ssl=False) as response:
                    if response.status == 200:
                        return await response.json()
                    elif 500 <= response.status < 600 or response.status == 429:
                        delay = min(BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, JITTER), BACKOFF_MAX)
                        if attempt < ASYNC_MAX_RETRIES:
                            await asyncio.sleep(delay)
                            continue
                    print(f"[SSL Fallback {response.status}] {url}")
                    return None
            except Exception as inner_e:
                delay = min(BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, JITTER), BACKOFF_MAX)
                if attempt < ASYNC_MAX_RETRIES:
                    await asyncio.sleep(delay)
                    continue
                print(f"[SSL Error] {url} -> {inner_e}")
                return None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Network hiccups: retry with backoff
            delay = min(BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, JITTER), BACKOFF_MAX)
            if attempt < ASYNC_MAX_RETRIES:
                await asyncio.sleep(delay)
                continue
            print(f"[Network Error] {url} -> {e}")
            return None

    return None



# =====================================
# Small helpers used by app.py
# =====================================

def parse_summoner_name(full_name: str) -> tuple[str, str]:
    """Split "Name#TAG" into (Name, TAG). Returns (Name, "") if no tag."""
    if "#" in full_name:
        name, tag = full_name.split("#", 1)
        return name, tag
    return full_name, ""


# =====================================
# Riot API calls
# =====================================

@timed_cache(300)
def get_account_info(summoner_name: str, summoner_tag: str, SERVER: str):
    """Account-V1: by Riot ID (regional route)."""
    global _last_server
    _last_server = SERVER  # remember for later calls that don't pass SERVER
    name_q = url_quote(str(summoner_name), safe="")
    tag_q = url_quote(str(summoner_tag), safe="")
    url = (
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/"
        f"account/v1/accounts/by-riot-id/{name_q}/{tag_q}"
    )
    return send_get_request(url)


def get_account_info_by_puuid(puuid: str, SERVER: str):
    url = (
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/"
        f"account/v1/accounts/by-puuid/{puuid}"
    )
    return send_get_request(url)


@timed_cache(300)
def get_summoner_info_puuid(puuid: str, SERVER: str):
    """
    Resolve a Summoner by PUUID with multiple fallbacks.

    Order:
      1) /lol/summoner/v4/summoners/by-puuid (platform)
      2) /lol/league/v4/entries/by-puuid -> take summonerId -> /lol/summoner/v4/summoners/{id}
      3) EU neighbor hop (euw1 <-> eun1)
      4) /lol/match/v5/matches/by-puuid (regional) -> infer platform from matchId prefix
         then retry (1) or fetch the match to read summonerId from participants and
         call /lol/summoner/v4/summoners/{id}.

    Returns full Summoner-V4 payload (dict) or None.
    """
    platform = servers_to_region[SERVER][0]   # e.g. "euw1"
    regional = servers_to_region[SERVER][1]   # e.g. "europe"

    # 1) Summoner by PUUID (platform route)
    url = (
        f"https://{platform}.api.riotgames.com/"
        f"lol/summoner/v4/summoners/by-puuid/{puuid}"
    )
    data = send_get_request(url)
    if data:
        return data

    # 2) League entries by PUUID -> summonerId -> full summoner
    url_league = (
        f"https://{platform}.api.riotgames.com/"
        f"lol/league/v4/entries/by-puuid/{puuid}"
    )
    entries = send_get_request(url_league)
    if isinstance(entries, list) and entries:
        for e in entries:
            sid = e.get("summonerId")
            if sid:
                url_sid = (
                    f"https://{platform}.api.riotgames.com/"
                    f"lol/summoner/v4/summoners/{sid}"
                )
                full = send_get_request(url_sid)
                if full:
                    return full

    # 2b) EU neighbor hop (helps when wrong platform was chosen)
    neighbor = "eun1" if platform == "euw1" else "euw1" if platform == "eun1" else None
    if neighbor:
        # try summoner-by-puuid on neighbor
        n_url = (
            f"https://{neighbor}.api.riotgames.com/"
            f"lol/summoner/v4/summoners/by-puuid/{puuid}"
        )
        n_data = send_get_request(n_url)
        if n_data:
            return n_data
        # try league entries on neighbor
        n_league = (
            f"https://{neighbor}.api.riotgames.com/"
            f"lol/league/v4/entries/by-puuid/{puuid}"
        )
        n_entries = send_get_request(n_league)
        if isinstance(n_entries, list) and n_entries:
            for e in n_entries:
                sid = e.get("summonerId")
                if sid:
                    n_sid = (
                        f"https://{neighbor}.api.riotgames.com/"
                        f"lol/summoner/v4/summoners/{sid}"
                    )
                    full = send_get_request(n_sid)
                    if full:
                        return full

    # 3) Match-V5 fallback: infer platform from last match
    ids_url = (
        f"https://{regional}.api.riotgames.com/"
        f"lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1"
    )
    ids = send_get_request(ids_url)
    if isinstance(ids, list) and ids:
        match_id = ids[0]  # e.g. "EUN1_1234567890"
        try:
            inferred = str(match_id).split("_", 1)[0].lower()
        except Exception:
            inferred = platform

        # try again: summoner by puuid on inferred platform
        i_url = (
            f"https://{inferred}.api.riotgames.com/"
            f"lol/summoner/v4/summoners/by-puuid/{puuid}"
        )
        i_data = send_get_request(i_url)
        if i_data:
            return i_data

        # fetch the match and read summonerId from participants
        match_url = (
            f"https://{regional}.api.riotgames.com/"
            f"lol/match/v5/matches/{match_id}"
        )
        match = send_get_request(match_url)
        parts = match.get("info", {}).get("participants", []) if isinstance(match, dict) else []
        for p in parts:
            if p.get("puuid") == puuid:
                sid = p.get("summonerId")
                if sid:
                    by_id_url = (
                        f"https://{inferred}.api.riotgames.com/"
                        f"lol/summoner/v4/summoners/{sid}"
                    )
                    full = send_get_request(by_id_url)
                    if full:
                        return full

    return None




def get_team_info_puuid(player_key: str, SERVER: str):
    """
    Clash-V1: player registrations for a given player.

    Accepts either an encryptedSummonerId OR a PUUID (auto-detected).
    Primary: /lol/clash/v1/players/by-puuid if input looks like a PUUID,
             otherwise /lol/clash/v1/players/by-summoner.
    Fallbacks: switch endpoint type; EU neighbor hop (euw1 <-> eun1).

    Returns:
        list (possibly empty if player not registered) or None on request failure.
    """
    platform = servers_to_region[SERVER][0]

    def _by_summoner(_platform: str, key: str):
        url = (
            f"https://{_platform}.api.riotgames.com/"
            f"lol/clash/v1/players/by-summoner/{key}"
        )
        return send_get_request(url)

    def _by_puuid(_platform: str, key: str):
        url = (
            f"https://{_platform}.api.riotgames.com/"
            f"lol/clash/v1/players/by-puuid/{key}"
        )
        return send_get_request(url)

    key = player_key or ""
    # Heuristic: PUUIDs are long (~78 chars) and often contain '-'
    is_puuid = len(key) >= 70 or "-" in key

    primary = _by_puuid if is_puuid else _by_summoner
    secondary = _by_summoner if is_puuid else _by_puuid

    # 1) Primary attempt on requested platform
    data = primary(platform, key)
    if isinstance(data, list):
        return data

    # 2) Fallback to the other endpoint type
    data2 = secondary(platform, key)
    if isinstance(data2, list):
        return data2

    # 3) EU neighbor hop (helps if platform was mismatched)
    neighbor = "eun1" if platform == "euw1" else "euw1" if platform == "eun1" else None
    if neighbor:
        data3 = primary(neighbor, key)
        if isinstance(data3, list):
            return data3
        data4 = secondary(neighbor, key)
        if isinstance(data4, list):
            return data4

    return None



def get_tournament_id_by_team(team_info):
    """Extract teamId from a Clash membership payload (list or dict)."""
    if isinstance(team_info, list) and team_info:
        entry = team_info[0]
        return entry.get("teamId")
    if isinstance(team_info, dict):
        return team_info.get("teamId")
    return None


# ---------- Team roster → external profile links ----------
async def _fetch_profiles_async(players: list[dict], SERVER: str):
    """Given a list of {'summonerId': ...}, return [ ["Name#Tag", u.gg, op.gg], ... ]."""
    ssl_ctx = create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 1) Summoner by encryptedSummonerId (platform route)
        summoner_tasks = []
        for p in players:
            summoner_url = (
                f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/"
                f"lol/summoner/v4/summoners/{p['summonerId']}"
            )
            summoner_tasks.append(async_get_request(session, summoner_url))
        summoners = await asyncio.gather(*summoner_tasks)

        # 2) Account by PUUID (regional route)
        account_tasks = []
        for s in summoners:
            if s and s.get("puuid"):
                account_url = (
                    f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/"
                    f"riot/account/v1/accounts/by-puuid/{s['puuid']}"
                )
                account_tasks.append(async_get_request(session, account_url))
        accounts = await asyncio.gather(*account_tasks)

        # 3) Compose external links
        out: list[list[str]] = []
        for acc in accounts:
            if not acc:
                continue
            game_name = (acc.get("gameName") or "").replace(" ", "")
            tag_line = acc.get("tagLine") or ""
            if not game_name or not tag_line:
                continue
            ugg = (
                f"https://u.gg/lol/profile/{servers_to_region[SERVER][0]}/"
                f"{game_name}-{tag_line}/overview"
            )
            opgg = (
                f"https://www.op.gg/summoners/{servers_to_region[SERVER][2]}/"
                f"{game_name}-{tag_line}"
            )
            out.append([f"{game_name}#{tag_line}", ugg, opgg])
        return out


def show_players_team(tournament_id: str):
    """Public API used by app.py: take a tournament/team id, return external links.

    app.py currently calls this with a single argument. We derive the last
    SERVER from the earlier get_account_info() call within the same request.
    """
    if not tournament_id:
        return []
    server = _last_server
    if not server:
        # As a safety net, return empty rather than crashing.
        return []

    # Fetch team to obtain players (list of encrypted summoner IDs)
    team_url = (
        f"https://{servers_to_region[server][0]}.api.riotgames.com/"
        f"lol/clash/v1/teams/{tournament_id}"
    )
    team = send_get_request(team_url) or {}
    players = team.get("players") or []

    # Run async batch to build profile links
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_fetch_profiles_async(players, server))
    finally:
        loop.close()
    return result


# =====================================
# Match history (uses CDN names instead of game_constants)
# =====================================

def calculate_time_ago(game_start_timestamp_ms: int) -> str:
    dt = datetime.datetime.fromtimestamp(game_start_timestamp_ms / 1000)
    now = datetime.datetime.now()
    diff = now - dt
    days = diff.days
    seconds = diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if days >= 7:
        return f"{days // 7} weeks ago"
    if days >= 1:
        return f"{days} days ago"
    if hours >= 1:
        return f"{hours} hours ago"
    if minutes >= 1:
        return f"{minutes} minutes ago"
    return "Just now"


def get_match_participant_details(match_details: dict, puuid: str, SERVER: str):
    participants_out: list[dict] = []
    flag = True

    for participant in match_details["info"]["participants"]:
        game_start_ts = match_details["info"].get("gameStartTimestamp", 0)

        # Riot now may return both legacy and Riot ID fields
        summoner_name = (
            participant.get("summonerName")
            or participant.get("riotIdGameName")
            or ""
        )
        summoner_tag = (
            participant.get("riotIdTagline")
            or participant.get("tagLine")
            or ""
        )
        # Back-compat for payloads containing "Name#TAG"
        if not summoner_tag and "#" in summoner_name:
            base, tag = parse_summoner_name(summoner_name)
            summoner_name, summoner_tag = base, tag

        # Build details
        details = {
            "Champion": participant.get("championName", ""),
            "Summoner Name": summoner_name,
            "summoner_tag": summoner_tag,
            "KDA": f"{participant.get('kills', 0)}/" \
                    f"{participant.get('deaths', 0)}/" \
                    f"{participant.get('assists', 0)}",
            # Items (0..6)
            "Items": [
                (
                    (item_id := participant.get(f"item{i}", 0)),
                    get_item_name(item_id) if item_id else "",
                )
                for i in range(7)
            ],
            # Rune paths & first rune
            "Primary Rune Path": (
                (primary_style := participant["perks"]["styles"][0].get("style")),
                get_rune_style_name(primary_style),
            ),
            "Primary Rune": (
                (primary_rune := participant["perks"]["styles"][0]["selections"][0].get("perk")),
                get_rune_name(primary_rune),
            ),
            "Secondary Rune Path": (
                (secondary_style := participant["perks"]["styles"][1].get("style")),
                get_rune_style_name(secondary_style),
            ),
            # Rune lists
            "Primary Runes": [
                (perk := sel.get("perk"), get_rune_name(perk))
                for sel in participant["perks"]["styles"][0].get("selections", [])
            ],
            "Secondary Runes": [
                (perk := sel.get("perk"), get_rune_name(perk))
                for sel in participant["perks"]["styles"][1].get("selections", [])
            ],
            # Stat shards
            "Shards": [
                (shard, get_stat_shard_name(shard))
                for shard in participant["perks"]["statPerks"].values()
            ],
            # Summoner spells
            "Summoner Spells": [
                ((s1 := participant.get("summoner1Id")), get_summoner_spell_name(s1)),
                ((s2 := participant.get("summoner2Id")), get_summoner_spell_name(s2)),
            ],
            "CS": participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
            "Team ID": participant.get("teamId", "Unknown"),
        }
        details["Control Wards"] = participant.get('visionWardsBoughtInGame', 0)

        # Extra fields for the main player
        if participant.get("puuid") == puuid:
            if flag:
                details["summonerId"] = participant.get("summonerId")
            details["gameStartTimestamp"] = game_start_ts
            details["Match Result"] = 'Win' if participant.get('win', False) else 'Lose'
            details["Start Date"] = datetime.datetime.fromtimestamp(game_start_ts / 1000).strftime('%d/%m/%Y %H:%M')
            details["Start Game Ago"] = calculate_time_ago(game_start_ts)
            gd_m, gd_s = divmod(match_details['info'].get('gameDuration', 0), 60)
            details["Game Duration"] = f"{gd_m}:{gd_s:02d}"
            details["Kill Participation"] = f"{participant['challenges'].get('killParticipation', 0) * 100:.0f}%"
            participants_out.insert(0, details)
            flag = False
        else:
            gd_m, gd_s = divmod(match_details['info'].get('gameDuration', 0), 60)
            details["Game Duration"] = f"{gd_m}:{gd_s:02d}"
            participants_out.append(details)

    return participants_out


def sort_participants(participants: list[dict], main_player_team_id: int):
    team_members = [p for p in participants[1:] if p['Team ID'] == main_player_team_id]
    opponents = [p for p in participants[1:] if p['Team ID'] != main_player_team_id]
    return [participants[0]] + team_members + opponents


async def fetch_match_details_async(match_ids, puuid, SERVER):
    """
    Fetch multiple match details concurrently with a safe concurrency limit.
    Preserves the order of match_ids in the returned list.
    """
    ssl_context = create_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    semaphore = asyncio.Semaphore(MAX_MATCH_CONCURRENCY)

    async with aiohttp.ClientSession(connector=connector) as session:

        async def fetch_one(mid: str):
            url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/{mid}"
            async with semaphore:
                return await async_get_request(session, url)

        # keep task order same as match_ids to preserve sort
        tasks = [asyncio.create_task(fetch_one(mid)) for mid in match_ids]
        match_results = await asyncio.gather(*tasks)

        match_history_list = []
        for match_details in match_results:
            if match_details:
                participant_details = get_match_participant_details(match_details, puuid, SERVER)
                match_history_list.append(participant_details)

        return match_history_list


def display_matches(summoner_name, summoner_tag, SERVER):
    account_info = get_account_info(summoner_name, summoner_tag, SERVER)
    if not account_info:
        return None

    puuid = account_info["puuid"]

    # Get match IDs (still fetch 20 IDs)
    match_ids_url = (
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/"
        f"lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20"
    )
    match_ids_list = send_get_request(match_ids_url)
    if not match_ids_list:
        return None

    # Fetch only first 5 matches to speed up first paint
    initial_count = min(5, len(match_ids_list))
    initial_ids = match_ids_list[:initial_count]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    match_history_list = loop.run_until_complete(
        fetch_match_details_async(initial_ids, puuid, SERVER)
    )
    loop.close()

    # Sort and attach meta as before
    match_history_list_sorted = []
    for match in match_history_list:
        match_history_list_sorted.append(sort_participants(match, match[0]['Team ID']))

    if match_history_list_sorted:
        match_history_list_sorted[0][0]["SERVER"] = SERVER
        match_history_list_sorted[0][0]["summoner_name"] = summoner_name
        match_history_list_sorted[0][0]["summoner_tag"] = summoner_tag

    return match_history_list_sorted



def display_matches_by_value(summoner_name: str, summoner_tag: str, SERVER: str, current_count: int, limit: int):
    account = get_account_info(summoner_name, summoner_tag, SERVER)
    if not account:
        return None
    puuid = account.get("puuid")
    if not puuid:
        return None

    ids_url = (
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/"
        f"lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={current_count}&count={limit}"
    )
    match_ids = send_get_request(ids_url)
    if not match_ids:
        return None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        matches = loop.run_until_complete(fetch_match_details_async(match_ids, puuid, SERVER))
    finally:
        loop.close()

    return [sort_participants(m, m[0]['Team ID']) for m in matches]
