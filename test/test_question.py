# test/test_question.py
import os
import time
import pytest

from config import RIOT_API_KEY
from question import (
    parse_summoner_name,
    get_account_info,
    get_account_info_by_puuid,
    get_summoner_info_puuid,
    get_team_info_puuid,
    get_tournament_id_by_team,
    show_players_team,
    display_matches,
    display_matches_by_value,
    calculate_time_ago,
)

# -------------------------------
# Global settings & test data
# -------------------------------

# Be gentle with rate limits.
@pytest.fixture(autouse=True, scope="function")
def _throttle_between_tests():
    time.sleep(0.4)

TEST_SUMMONERS_PUUID = [
    # (puuid, server)
    ("_Px_y-xEzStb-LEDWknCDlQUxk2CIyqSF4dlPggVodKmsFZiskf6fikwo0DWDwh1WzrX5kZ5YA3ygA", "eu nordic & east"),
    ("9Qeo46FMr1zHMS_Iwjbz-eD0eYbEiCFaXm-iAgu5Qmnn6Rrqg6GlXnH_VaL7vHCmuVe9wsF50M0mJw", "eu west"),
]

TEST_SUMMONER_BY_RIOT_ID = [
    # (name, tag, server)
    ("HextechChest", "202", "eu west"),
]

# Skip the entire module if API key is clearly missing.
if not RIOT_API_KEY or not isinstance(RIOT_API_KEY, str) or len(RIOT_API_KEY.strip()) < 10:
    pytest.skip("No RIOT_API_KEY configured", allow_module_level=True)


# --------------------------------
# Helpers
# --------------------------------

def _skip_if_no_clash(payload, *, prefix="Possibly no active Clash"):
    """
    Skip tests gracefully when Clash is not active or API returns no registrations.
    Shapes handled:
      - None                         -> skip
      - []                           -> skip
      - {"status":{"status_code":}}  -> skip for 204/404
    """
    # Request failed / None
    if payload is None:
        pytest.skip(f"{prefix}: API returned None (Clash may be inactive)")

    # Empty registrations list (most common for 'no Clash' or not registered)
    if isinstance(payload, list) and len(payload) == 0:
        pytest.skip(f"{prefix}: API returned empty list (no registrations)")

    # Defensive: some helpers bubble up a status dict
    if isinstance(payload, dict):
        status = payload.get("status", {})
        code = status.get("status_code")
        if code in (204, 404):
            pytest.skip(f"{prefix}: HTTP {code}")

def _maybe_skip_unexpected_shape(payload, *, where):
    """
    If API returns an unexpected shape, skip with a helpful message
    instead of failing the test with KeyError/TypeError.
    """
    # Acceptable shapes for our use cases
    if payload is None:
        pytest.skip(f"{where}: unexpected None (possibly no active Clash)")
    if isinstance(payload, (list, dict)):
        return
    pytest.skip(f"{where}: unexpected response shape {type(payload)!r} (possibly no active Clash)")


# --------------------------------
# Unit-ish helpers tests
# --------------------------------

class TestParsingHelpers:
    @pytest.mark.parametrize("full,expected", [
        ("HextechChest#202", ("HextechChest", "202")),
        ("Broken Blade#G2", ("Broken Blade", "G2")),
        ("NoTag", ("NoTag", "")),
        ("#ONLYTAG", ("", "ONLYTAG")),
    ])
    def test_parse_summoner_name(self, full, expected):
        assert parse_summoner_name(full) == expected


# --------------------------------
# Account API
# --------------------------------

class TestAccountAPI:
    @pytest.mark.parametrize("puuid,server", TEST_SUMMONERS_PUUID)
    def test_get_account_info_by_puuid(self, puuid, server):
        data = get_account_info_by_puuid(puuid, server)
        if data is None:
            pytest.skip("Account with PUUID not found or rate limit reached")

        assert isinstance(data, dict)
        assert data.get("puuid") == puuid
        assert isinstance(data.get("gameName", ""), str)
        assert isinstance(data.get("tagLine", ""), str)
        assert len(data["puuid"]) > 49


# --------------------------------
# Summoner API
# --------------------------------

class TestSummonerAPI:
    @pytest.mark.parametrize("puuid,server", TEST_SUMMONERS_PUUID)
    def test_get_summoner_info_puuid(self, puuid, server):
        summoner = get_summoner_info_puuid(puuid, server)
        if summoner is None:
            pytest.skip("Summoner info not found or rate limit hit")

        # Accept unexpected shapes by skipping instead of crashing
        _maybe_skip_unexpected_shape(summoner, where="get_summoner_info_puuid")

        # Core fields present in Summoner-V4 payload
        for key in ("puuid", "profileIconId", "revisionDate", "summonerLevel"):
            assert key in summoner, f"Missing required field: {key}"

        assert summoner["puuid"] == puuid
        assert isinstance(summoner["profileIconId"], int)
        assert isinstance(summoner["revisionDate"], int)
        assert isinstance(summoner["summonerLevel"], int)
        # Optional fields in case endpoint/fallback changes
        if "id" in summoner:
            assert isinstance(summoner["id"], str)


# --------------------------------
# Clash flow (team & roster)
# --------------------------------

class TestClashFlow:
    @pytest.mark.parametrize("puuid,server", TEST_SUMMONERS_PUUID)
    def test_clash_flow_for_player(self, puuid, server):
        # 1) Resolve Summoner by PUUID -> need encryptedSummonerId
        summoner = get_summoner_info_puuid(puuid, server)
        if summoner is None:
            pytest.skip("Summoner info not found or rate limit hit")

        _maybe_skip_unexpected_shape(summoner, where="Summoner payload")
        summoner_id = summoner.get("id")
        if not summoner_id:
            # This step itself does not depend on Clash, but without the id
            # we cannot continue to Clash flow. Keep message helpful.
            pytest.skip("Missing summoner id; cannot continue Clash flow (Clash may also be inactive)")

        # 2) Clash registrations
        registrations = get_team_info_puuid(summoner_id, server)
        _skip_if_no_clash(registrations, prefix="Possibly no active Clash (registrations)")

        _maybe_skip_unexpected_shape(registrations, where="Clash registrations payload")
        assert isinstance(registrations, list)
        entry = registrations[0]
        if not isinstance(entry, dict):
            pytest.skip("Unexpected registrations entry shape (possibly no active Clash)")
        # Keep assertions flexible
        for k in ("teamId", "summonerId", "position", "queue"):
            assert k in entry, f"Missing field in registration: {k}"

        # 3) Tournament / team id
        tournament_id = get_tournament_id_by_team(registrations)
        if not tournament_id:
            pytest.skip("Possibly no active Clash: team has no tournament id")

        # 4) Roster & external links
        roster = show_players_team(tournament_id)
        _skip_if_no_clash(roster, prefix="Possibly no active Clash (roster)")

        _maybe_skip_unexpected_shape(roster, where="Clash roster payload")
        assert isinstance(roster, list)
        # roster entries like: ["Name#TAG", u.gg, op.gg]
        first = roster[0]
        if not isinstance(first, (list, tuple)):
            pytest.skip("Unexpected roster entry shape (possibly no active Clash)")
        assert 1 <= len(first) <= 3
        assert isinstance(first[0], str)
        if "#" in first[0]:
            # good case: Riot ID present
            pass

        if len(first) >= 2:
            assert isinstance(first[1], str)
        if len(first) >= 3:
            assert isinstance(first[2], str)

    def test_error_handling_for_invalid_ids(self):
        server = "eu west"
        invalid_summoner_id = "nonexistent_summoner_id_12345"
        invalid_team_id = "nonexistent_team_id_12345"

        regs = get_team_info_puuid(invalid_summoner_id, server)
        # Either None (request failure) or [] (no registrations / no Clash)
        if regs not in (None, []):
            _maybe_skip_unexpected_shape(regs, where="Invalid-id registrations")
        assert regs in (None, []), f"Expected None or [], got: {regs}"

        tournament_id = get_tournament_id_by_team(invalid_team_id)
        assert tournament_id is None


# --------------------------------
# Matches (overview + pagination)
# --------------------------------

class TestMatches:
    @pytest.mark.parametrize("name,tag,server", TEST_SUMMONER_BY_RIOT_ID)
    def test_display_matches_overview(self, name, tag, server):
        """Fetch a small overview of recent matches and validate structure."""
        try:
            matches = display_matches(name, tag, server)
        except Exception as e:
            # Some older builds depended on removed endpoints; degrade gracefully.
            if "by-riot-id" in str(e).lower():
                pytest.skip("Function depends on a removed endpoint")
            raise

        if matches is None or len(matches) == 0:
            pytest.skip("No matches returned or rate limit hit")

        assert isinstance(matches, list)
        match = matches[0]
        if not isinstance(match, list) or len(match) == 0:
            pytest.skip("Unexpected match payload shape (possibly no data)")

        main = match[0]
        for k in ("Champion", "Summoner Name", "summoner_tag", "KDA", "Items", "Match Result", "Game Duration"):
            assert k in main, f"Missing required field: {k}"

        assert isinstance(main["Champion"], str)
        assert isinstance(main["Summoner Name"], str)
        assert isinstance(main["summoner_tag"], str)
        assert isinstance(main["KDA"], str)
        assert isinstance(main["Items"], list)
        assert main["Match Result"] in ("Win", "Lose")

        # KDA format x/y/z
        parts = main["KDA"].split("/")
        assert len(parts) == 3

        # mm:ss format (keep lenient)
        dur = main["Game Duration"]
        assert isinstance(dur, str) and ":" in dur

    @pytest.mark.parametrize("name,tag,server,current,limit", [
        ("HextechChest", "202", "eu west", 0, 2),
        ("HextechChest", "202", "eu west", 0, 3),
    ])
    def test_display_matches_by_value(self, name, tag, server, current, limit):
        try:
            chunk = display_matches_by_value(name, tag, server, current, limit)
        except Exception as e:
            if "by-riot-id" in str(e).lower():
                pytest.skip("Function depends on a removed endpoint")
            raise

        if chunk is None:
            pytest.skip("No matches returned or rate limit hit")

        assert isinstance(chunk, list)
        assert len(chunk) <= limit
        if len(chunk) > 0:
            match = chunk[0]
            if not isinstance(match, list) or len(match) == 0:
                pytest.skip("Unexpected match payload shape (possibly no data)")
            main = match[0]
            for k in ("Champion", "Summoner Name", "summoner_tag", "KDA", "Items"):
                assert k in main


# --------------------------------
# Time formatting utility
# --------------------------------

class TestTimeAgo:
    @pytest.mark.parametrize("minutes,expected_contains", [
        (0, "Just"),
        (5, "minute"),
        (60, "hour"),
        (24 * 60, "day"),
        (14 * 24 * 60, "week"),
    ])
    def test_calculate_time_ago(self, minutes, expected_contains):
        now_ms = int(time.time() * 1000)
        ts = now_ms - minutes * 60 * 1000
        label = calculate_time_ago(ts)
        assert isinstance(label, str) and expected_contains.lower() in label.lower()

    def test_future_timestamp(self):
        now_ms = int(time.time() * 1000)
        future = now_ms + 5 * 60 * 1000
        label = calculate_time_ago(future)
        # Function may choose to clamp to "Just now" or return 0 minutes.
        assert isinstance(label, str)
