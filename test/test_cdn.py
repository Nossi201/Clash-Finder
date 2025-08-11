# test_cdn.py
# Tests for Riot CDN helpers (Data Dragon / Community Dragon).
# Keep code in English (project convention).

import time
import pytest

from cdn_config import (
    get_image_url,
    get_champion_image_url,
    get_item_image_url,
    get_rune_image_url,
    get_rune_style_image_url,
    get_summoner_spell_image_url,
    get_stat_shard_image_url,
    get_item_name,
    get_rune_name,
    get_rune_style_name,
    get_summoner_spell_name,
    get_stat_shard_name,
    set_language,  # available in cdn_config
)

# -------------------------------
# Global
# -------------------------------

@pytest.fixture(autouse=True, scope="function")
def _throttle_between_tests():
    # Be gentle in case helpers fetch manifests on first call
    time.sleep(0.2)


def _skip_if_empty(value, *, where: str):
    """
    Skip gracefully when CDN helpers cannot build a URL or name (offline/missing maps).
    """
    if value is None:
        pytest.skip(f"{where}: got None (possibly offline / missing mapping)")
    if isinstance(value, str) and value.strip() == "":
        pytest.skip(f"{where}: got empty string (possibly offline / missing mapping)")


# -------------------------------
# Happy-path URL generation
# -------------------------------

def test_champion_url_variants():
    for champion in ["Ashe", "Aatrox", 103, 266, "Miss Fortune"]:
        url1 = get_champion_image_url(champion)
        _skip_if_empty(url1, where=f"champion url ({champion})")
        url2 = get_champion_image_url(champion)  # idempotency
        assert url1 == url2
        assert url1.startswith("http") and url1.lower().endswith(".png")


def test_core_asset_urls_valid_ids():
    # Known-good numeric IDs (these helpers expect numeric IDs, not names).
    item_url = get_item_image_url(1001)              # Boots
    spell_url = get_summoner_spell_image_url(4)      # Flash
    rune_url = get_rune_image_url(8005)              # Press the Attack
    style_url = get_rune_style_image_url(8000)       # Precision
    shard_url = get_stat_shard_image_url(5008)       # Adaptive Force

    for label, url in [
        ("item", item_url),
        ("spell", spell_url),
        ("rune", rune_url),
        ("style", style_url),
        ("shard", shard_url),
    ]:
        _skip_if_empty(url, where=f"{label} url")
        assert url.startswith("http") and url.lower().endswith(".png")


# -------------------------------
# Name lookups (non-empty smoke)
# -------------------------------

def test_basic_name_maps_smoke():
    # We do not assert exact strings; only that mappings are non-empty
    i_name = get_item_name(1001)           # Boots of Speed
    s_name = get_summoner_spell_name(4)    # Flash
    r_name = get_rune_name(8005)           # Press the Attack
    rs_name = get_rune_style_name(8000)    # Precision
    sh_name = get_stat_shard_name(5008)    # Adaptive Force

    for label, name in [
        ("item", i_name),
        ("spell", s_name),
        ("rune", r_name),
        ("style", rs_name),
        ("shard", sh_name),
    ]:
        _skip_if_empty(name, where=f"{label} name")
        assert isinstance(name, str)


# -------------------------------
# Unknown inputs should not crash
# -------------------------------

@pytest.mark.parametrize("kind, value, expect_empty", [
    ("item", 999999, False),          # item ma fallback -> oczekujemy pełnego URL
    ("rune", "PressTheAttack", True), # nazwa nie jest wspierana -> oczekujemy ""
    ("style", 999999, True),          # nieznane ID -> oczekujemy ""
    ("spell", 999999, True),          # nieznane ID -> oczekujemy ""
    ("shard", 999999, True),          # nieznane ID -> oczekujemy ""
])
def test_unknown_ids_contract(kind, value, expect_empty):
    if kind == "item":
        url = get_item_image_url(value)
    elif kind == "rune":
        url = get_rune_image_url(value)
    elif kind == "style":
        url = get_rune_style_image_url(value)
    elif kind == "spell":
        url = get_summoner_spell_image_url(value)
    else:
        url = get_stat_shard_image_url(value)

    assert isinstance(url, str)

    if expect_empty:
        # Kontrakt helperów: dla nieznanych/niewspieranych wejść zwracają pusty string
        assert url == ""
    else:
        # Dla itemów z nieznanym ID mamy fallback na URL .../<id>.png
        assert url.startswith("http") and url.lower().endswith(".png")





# -------------------------------
# Generic pass-through
# -------------------------------

def test_get_image_url_pass_through():
    relative = "perk-images/Styles/Precision/Precision.png"
    url = get_image_url(relative)
    _skip_if_empty(url, where="get_image_url")
    assert url.startswith("http") and url.lower().endswith(".png")


# -------------------------------
# Optional: language switch smoke
# -------------------------------

def test_language_switch_smoke():
    """
    set_language exists in cdn_config; images usually identical across locales.
    We only ensure calls don't break and still return non-empty URLs.
    """
    try:
        set_language("en_US")
        url_en = get_item_image_url(1001)
        _skip_if_empty(url_en, where="item url (en_US)")
        set_language("pl_PL")
        url_pl = get_item_image_url(1001)
        _skip_if_empty(url_pl, where="item url (pl_PL)")
    finally:
        set_language("en_US")
    assert isinstance(url_en, str) and isinstance(url_pl, str)
