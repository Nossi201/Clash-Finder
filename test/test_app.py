# test_app.py
# Tests for lightweight parts of the Flask app (no external Riot API calls).
# Keep code in English (project convention).

import re
import pytest
from urllib.parse import urlparse

from app import app as flask_app, slugify_server, unslugify_server
from question import servers_to_region, parse_summoner_name


# -------------------------------
# Fixtures
# -------------------------------

@pytest.fixture(scope="module")
def client():
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c


# -------------------------------
# parse_summoner_name (rich coverage)
# -------------------------------

@pytest.mark.parametrize("full,expected", [
    ("HextechChest#202", ("HextechChest", "202")),
    ("Broken Blade#G2", ("Broken Blade", "G2")),
    ("NoTag", ("NoTag", "")),              # no '#'
    ("#ONLYTAG", ("", "ONLYTAG")),         # empty name
    ("Player#", ("Player", "")),           # empty tag
    ("", ("", "")),                        # both empty
    ("  spaced  #  tag ", ("  spaced  ", "  tag ")),  # no trimming by design
    ("emoji😀#🔥", ("emoji😀", "🔥")),      # unicode ok
    ("multi#hash#rest", ("multi", "hash#rest")),      # split once
    ("\tTabbed Name#New\nLine", ("\tTabbed Name", "New\nLine")),
    ("Имя#Тег", ("Имя", "Тег")),           # Cyrillic
    ("名字#标签", ("名字", "标签")),        # CJK
])
def test_parse_summoner_name_cases(full, expected):
    assert parse_summoner_name(full) == expected


# -------------------------------
# slugify_server / unslugify_server
# -------------------------------

@pytest.mark.parametrize("server,expected_slug", [
    ("eu west", "eu-west"),
    ("eu nordic & east", "eu-nordic-and-east"),
    ("north america", "north-america"),
    ("turkey", "turkey"),
    ("Latin America South", "latin-america-south"),
])
def test_slugify_known_servers(server, expected_slug):
    assert slugify_server(server) == expected_slug


@pytest.mark.parametrize("slug,expected_server", [
    ("eu-west", "eu west"),
    ("eu-nordic-and-east", "eu nordic & east"),
    ("north-america", "north america"),
    ("turkey", "turkey"),
])
def test_unslugify_known_servers(slug, expected_server):
    assert unslugify_server(slug) == expected_server


def test_unslugify_and_is_word_not_substring():
    # "and" must be treated as a standalone word
    s = unslugify_server("finland-and-sweden")
    assert s == "finland & sweden"
    assert "finl&" not in s  # no accidental substitution inside "finland"


@pytest.mark.parametrize("raw,expected", [
    ("EU  WEST", "eu--west"),                       # multiple spaces -> multiple hyphens
    ("Türkiye", "türkiye"),                         # non-ascii preserved and lowercased
    ("  north   america  ", "--north---america--"), # leading/trailing/multiple spaces
    ("A&B", "aandb"),                               # '&' -> 'and'
])
def test_slugify_edge_cases(raw, expected):
    assert slugify_server(raw) == expected


@pytest.mark.parametrize("s", [
    "", " ", "   ", "\n", "\t", "   \t  ",
])
def test_slugify_emptyish_inputs(s):
    slug = slugify_server(s)
    # Output is lowercase with spaces->'-'; not asserting exact text
    assert isinstance(slug, str)


@pytest.mark.parametrize("weird", [
    "! ? | \\ / : ; ' \" < > { } [ ] ( ) ^ $ * + = , .",
    "N\0ULL byte not literal",   # ensure function doesn't crash
    "ąężźćł ó",                  # Polish diacritics
])
def test_slugify_dangerous_characters_dont_crash(weird):
    out = slugify_server(weird)
    assert isinstance(out, str) and len(out) >= 0  # no exception is the goal


def test_slugify_all_configured_servers_smoke():
    # Ensure slugify doesn't crash on any configured server name
    for s in servers_to_region.keys():
        slug = slugify_server(s)
        assert isinstance(slug, str) and len(slug) > 0


# -------------------------------
# Round-trip tests (documented limitations)
# -------------------------------

@pytest.mark.parametrize("original", [
    "eu west",
    "north america",
    "turkey",
])
def test_slug_unslug_roundtrip_lenient(original):
    slug = slugify_server(original)
    recovered = unslugify_server(slug)
    # Case-insensitive equality is good enough for UI usage
    assert recovered.lower() == original.lower()


@pytest.mark.xfail(reason="Multiple spaces cannot be losslessly recovered", strict=False)
@pytest.mark.parametrize("original", [
    "EU  WEST",
    "  north   america  ",
])
def test_slug_unslug_roundtrip_preserves_spaces_normalizes_case(original):
    slug = slugify_server(original)
    recovered = unslugify_server(slug)
    # Spaces count is preserved through slug->unslug
    assert recovered.count(" ") == original.count(" ")
    # Case is normalized to lower-case (expected behavior)
    assert recovered == original.lower()


@pytest.mark.xfail(reason="Ampersand replaced by 'and' loses exact form", strict=False)
def test_slug_unslug_roundtrip_ampersand():
    original = "eu nordic & east"
    slug = slugify_server(original)
    recovered = unslugify_server(slug)
    assert recovered == original  # expected to fail (documenting limitation)


# -------------------------------
# Jinja filter exposure (template helpers)
# -------------------------------

def test_jinja_slugify_filter_exposed():
    assert "slugify_server" in flask_app.jinja_env.filters
    f = flask_app.jinja_env.filters["slugify_server"]
    assert callable(f)
    assert f("eu west") == "eu-west"


# -------------------------------
# Routes that don't call Riot API
# -------------------------------

def test_home_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # Should render HTML (don't assert body text to avoid template coupling)
    assert "text/html" in resp.headers.get("Content-Type", "")


def test_404_for_unknown_path(client):
    resp = client.get("/this-path-does-not-exist")
    assert resp.status_code == 404


@pytest.mark.parametrize("option,endpoint_segment", [
    ("clashTeam", "/clash_team/"),     # form option selects clash flow
    ("playerStats", "/player_stats/"), # any other option -> player stats
])
def test_Cheker_redirects_with_encoded_inputs(client, option, endpoint_segment):
    data = {
        "option": option,
        # Riot ID with spaces and '#'; app should encode into path segments safely
        "tekst": "A B#C",
        "lista": "eu west",
    }
    resp = client.post("/Cheker", data=data, follow_redirects=False)
    assert resp.status_code in (301, 302), f"Expected redirect, got {resp.status_code}"
    loc = resp.headers.get("Location", "")
    assert endpoint_segment in loc, f"Expected redirect to contain '{endpoint_segment}', got '{loc}'"
    # Path should end with server slug
    assert loc.rstrip("/").endswith("eu-west")
    # '#' should be encoded in the Riot ID segment; we expect a double dash convention or similar
    assert "--" in loc, "Expected encoded Riot ID to contain a separator for '#'"


@pytest.mark.parametrize("text_input", [
    "PlayerOnly",          # no '#': tag assumed empty
    "#OnlyTag",            # no name
    "   spaced  #  tag ",  # extra spaces preserved
    "emoji😀#🔥",
    "\tTabbed Name#New\nLine",
])
def test_Cheker_accepts_odd_riot_id_inputs(client, text_input):
    data = {
        "option": "playerStats",
        "tekst": text_input,
        "lista": "eu west",
    }
    resp = client.post("/Cheker", data=data, follow_redirects=False)
    # The handler should not 5xx on messy inputs; allow redirect or bad request
    assert resp.status_code in (301, 302, 400)


def test_methods_on_Cheker(client):
    # GET should be method-not-allowed or handled explicitly as 405/200
    resp = client.get("/Cheker")
    assert resp.status_code in (200, 405)


def test_debug_check_static_ok(client):
    resp = client.get("/debug/check-static")
    assert resp.status_code == 200
    payload = resp.get_json(silent=True)
    assert isinstance(payload, dict)
    # minimal keys present
    assert "static_folder" in payload
    assert "files_in_static" in payload
    # basic shape checks
    assert isinstance(payload.get("files_in_static", []), list)


def test_redirect_urls_are_valid_paths(client):
    # sanity: parse redirect URL structure
    data = {"option": "clashTeam", "tekst": "A B#C", "lista": "eu west"}
    resp = client.post("/Cheker", data=data, follow_redirects=False)
    assert resp.status_code in (301, 302)
    loc = resp.headers.get("Location", "")
    parsed = urlparse(loc)
    assert parsed.path.startswith("/clash_team/")
    # Expect at least 3 segments: /clash_team/<riot-id>/<server>
    segments = [seg for seg in parsed.path.split("/") if seg]
    assert len(segments) >= 3
