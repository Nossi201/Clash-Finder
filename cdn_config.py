# cdn_config.py
# Riot Data Dragon / Community Dragon helpers (names + images)
# NOTE: keep code in English (project convention).

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

import requests


class RiotCDNConfig:
    """
    Helpers around Riot's Data Dragon (and a bit of Community Dragon) to:
    - fetch current patch
    - read manifests (items, runes, summoner spells, champions)
    - provide ID→name maps (lazy, cached)
    - build image URLs (items, runes, rune styles, summoner spells, stat shards, champions)
    """

    DDRAGON_BASE = "https://ddragon.leagueoflegends.com"
    CDRAGON_BASE = "https://raw.communitydragon.org"  # not required for now, but kept if needed later

    def __init__(self, language: str = "en_US") -> None:
        self.language: str = language
        self._current_version: Optional[str] = None

        # raw manifests
        self._items_data: Optional[Dict[str, Any]] = None
        self._runes_data: Optional[list[dict]] = None
        self._summoner_data: Optional[Dict[str, Any]] = None
        self._champion_data: Optional[Dict[str, Any]] = None

        # derived maps: ID -> name / icon / etc.
        self._item_name_by_id: Optional[Dict[int, str]] = None
        self._item_image_by_id: Optional[Dict[int, str]] = None  # image.full (e.g., "1001.png")

        self._summoner_name_by_id: Optional[Dict[int, str]] = None
        self._summoner_imagefull_by_id: Optional[Dict[int, str]] = None  # e.g., "SummonerFlash.png"

        self._rune_name_by_id: Optional[Dict[int, str]] = None
        self._rune_icon_by_id: Optional[Dict[int, str]] = None  # e.g., "perk-images/Styles/.../Conqueror.png"
        self._rune_style_name_by_id: Optional[Dict[int, str]] = None
        self._rune_style_icon_by_id: Optional[Dict[int, str]] = None  # e.g., "perk-images/Styles/Precision/Precision.png"

        # champions: mapping tricks between API display names and DDragon ids
        self._champion_name_by_numeric_id: Optional[Dict[int, str]] = None  # e.g., 266 -> "Aatrox"
        self._champion_normalized_to_id: Optional[Dict[str, str]] = None   # "wukong" -> "MonkeyKing"

        # stat shards (local map: DDragon doesn't provide names)
        self._stat_shard_name_by_id: Dict[int, str] = {
            5001: "Health",
            5002: "Armor",
            5003: "Magic Resist",
            5005: "Attack Speed",
            5007: "Ability Haste",
            5008: "Adaptive Force",
        }
        # corresponding filenames under /cdn/img/perk-images/StatMods/
        self._stat_shard_icon_by_id: Dict[int, str] = {
            5001: "StatModsHealthScalingIcon.png",
            5002: "StatModsArmorIcon.png",
            5003: "StatModsMagicResIcon.png",
            5005: "StatModsAttackSpeedIcon.png",
            5007: "StatModsAbilityHasteIcon.png",   # older clients may use StatModsCDRScalingIcon.png
            5008: "StatModsAdaptiveForceIcon.png",
        }

    # ------------------------------- Utilities -------------------------------

    def set_language(self, language: str) -> None:
        if language != self.language:
            self.language = language
            self._invalidate_all_caches()

    def _invalidate_all_caches(self) -> None:
        self._items_data = None
        self._runes_data = None
        self._summoner_data = None
        self._champion_data = None

        self._item_name_by_id = None
        self._item_image_by_id = None
        self._summoner_name_by_id = None
        self._summoner_imagefull_by_id = None
        self._rune_name_by_id = None
        self._rune_icon_by_id = None
        self._rune_style_name_by_id = None
        self._rune_style_icon_by_id = None
        self._champion_name_by_numeric_id = None
        self._champion_normalized_to_id = None

    def _fetch_json(self, url: str) -> Optional[Any]:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[CDN] fetch error: {e} // url={url}")
        return None

    def get_current_version(self) -> str:
        if not self._current_version:
            url = f"{self.DDRAGON_BASE}/api/versions.json"
            data = self._fetch_json(url) or []
            self._current_version = (data[0] if data else "15.15.1")
        return self._current_version

    def _normalize_key(self, s: str) -> str:
        """Lowercase and strip non-alphanumeric; helps match 'Kai'Sa' -> 'kaisa'."""
        return re.sub(r"[^a-z0-9]", "", str(s).lower())

    # ------------------------------- Manifests -------------------------------

    def _fetch_manifest(self, manifest: str) -> Optional[Any]:
        """manifest in {'item','runesReforged','summoner','champion'}"""
        ver = self.get_current_version()
        lang = self.language
        url = f"{self.DDRAGON_BASE}/cdn/{ver}/data/{lang}/{manifest}.json"
        # special case: runes images paths are versionless, but JSON is under version; that's fine.
        return self._fetch_json(url)

    def get_item_data(self) -> Dict[str, Any]:
        if self._items_data is None:
            data = self._fetch_manifest("item") or {}
            self._items_data = data.get("data", {}) or {}
            self._item_name_by_id = None
            self._item_image_by_id = None
        return self._items_data

    def get_runes_reforged_data(self) -> list[dict]:
        if self._runes_data is None:
            self._runes_data = self._fetch_manifest("runesReforged") or []
            self._rune_name_by_id = None
            self._rune_icon_by_id = None
            self._rune_style_name_by_id = None
            self._rune_style_icon_by_id = None
        return self._runes_data

    def get_summoner_data(self) -> Dict[str, Any]:
        if self._summoner_data is None:
            data = self._fetch_manifest("summoner") or {}
            self._summoner_data = data.get("data", {}) or {}
            self._summoner_name_by_id = None
            self._summoner_imagefull_by_id = None
        return self._summoner_data

    def get_champion_data(self) -> Dict[str, Any]:
        if self._champion_data is None:
            data = self._fetch_manifest("champion") or {}
            self._champion_data = data.get("data", {}) or {}
            self._champion_name_by_numeric_id = None
            self._champion_normalized_to_id = None
        return self._champion_data

    # ------------------------------ Name lookups -----------------------------

    def _ensure_item_maps(self) -> None:
        if self._item_name_by_id is not None:
            return
        names: Dict[int, str] = {}
        icons: Dict[int, str] = {}
        for id_str, meta in self.get_item_data().items():
            try:
                iid = int(id_str)
            except Exception:
                continue
            names[iid] = str(meta.get("name", ""))
            img = (meta.get("image") or {}).get("full")
            if img:
                icons[iid] = str(img)
        self._item_name_by_id = names
        self._item_image_by_id = icons

    def _ensure_summoner_maps(self) -> None:
        if self._summoner_name_by_id is not None:
            return
        names: Dict[int, str] = {}
        icons: Dict[int, str] = {}
        for _, meta in self.get_summoner_data().items():
            key_str = str((meta or {}).get("key", ""))
            if not key_str.isdigit():
                continue
            sid = int(key_str)
            names[sid] = str(meta.get("name", ""))
            img_full = (meta.get("image") or {}).get("full")
            if img_full:
                icons[sid] = str(img_full)
        self._summoner_name_by_id = names
        self._summoner_imagefull_by_id = icons

    def _ensure_rune_maps(self) -> None:
        if self._rune_name_by_id is not None:
            return
        r_names: Dict[int, str] = {}
        r_icons: Dict[int, str] = {}
        s_names: Dict[int, str] = {}
        s_icons: Dict[int, str] = {}
        for style in self.get_runes_reforged_data():
            style_id = int(style.get("id", 0))
            s_names[style_id] = str(style.get("name", ""))
            icon = str(style.get("icon", ""))
            if icon:
                s_icons[style_id] = icon  # e.g., "perk-images/Styles/Precision/Precision.png"
            for slot in style.get("slots", []):
                for rune in slot.get("runes", []):
                    rid = int(rune.get("id", 0))
                    r_names[rid] = str(rune.get("name", ""))
                    r_icon = str(rune.get("icon", ""))
                    if r_icon:
                        r_icons[rid] = r_icon
        self._rune_name_by_id = r_names
        self._rune_icon_by_id = r_icons
        self._rune_style_name_by_id = s_names
        self._rune_style_icon_by_id = s_icons

    def _get_champion_name_by_numeric_id(self) -> Dict[int, str]:
        if self._champion_name_by_numeric_id is None:
            cmap: Dict[int, str] = {}
            for dd_id, meta in self.get_champion_data().items():
                key_str = str((meta or {}).get("key", ""))
                if key_str.isdigit():
                    cmap[int(key_str)] = dd_id  # dd_id is the DDragon id (e.g., "MonkeyKing")
            self._champion_name_by_numeric_id = cmap
        return self._champion_name_by_numeric_id

    def _get_champion_normalized_to_id(self) -> Dict[str, str]:
        if self._champion_normalized_to_id is None:
            m: Dict[str, str] = {}
            for dd_id, meta in self.get_champion_data().items():
                disp = str((meta or {}).get("name", ""))  # e.g., "Wukong"
                n_id = self._normalize_key(dd_id)         # "monkeyking"
                n_disp = self._normalize_key(disp)        # "wukong"
                if n_id:
                    m[n_id] = dd_id
                if n_disp:
                    m[n_disp] = dd_id
            self._champion_normalized_to_id = m
        return self._champion_normalized_to_id

    # Public name getters

    def get_item_name(self, item_id: int | str | None) -> str:
        if item_id in (None, "", 0, "0"):
            return ""
        try:
            iid = int(item_id)
        except Exception:
            return ""
        self._ensure_item_maps()
        return self._item_name_by_id.get(iid, "") if self._item_name_by_id else ""

    def get_summoner_spell_name(self, spell_id: int | str | None) -> str:
        if spell_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(spell_id)
        except Exception:
            return ""
        self._ensure_summoner_maps()
        return self._summoner_name_by_id.get(sid, "") if self._summoner_name_by_id else ""

    def get_rune_name(self, rune_id: int | str | None) -> str:
        if rune_id in (None, "", 0, "0"):
            return ""
        try:
            rid = int(rune_id)
        except Exception:
            return ""
        self._ensure_rune_maps()
        return self._rune_name_by_id.get(rid, "") if self._rune_name_by_id else ""

    def get_rune_style_name(self, style_id: int | str | None) -> str:
        if style_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(style_id)
        except Exception:
            return ""
        self._ensure_rune_maps()
        return self._rune_style_name_by_id.get(sid, "") if self._rune_style_name_by_id else ""

    def get_stat_shard_name(self, shard_id: int | str | None) -> str:
        if shard_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(shard_id)
        except Exception:
            return ""
        return self._stat_shard_name_by_id.get(sid, "")

    # ------------------------------- Image URLs ------------------------------

    def _ddragon_img(self, path: str) -> str:
        """Versionless images under /cdn/img/, such as runes and stat mods."""
        p = path.lstrip("/")
        return f"{self.DDRAGON_BASE}/cdn/img/{p}"

    def _ddragon_versioned_img(self, folder: str, filename: str) -> str:
        ver = self.get_current_version()
        return f"{self.DDRAGON_BASE}/cdn/{ver}/img/{folder}/{filename}"

    def get_image_url(self, path: str) -> str:
        """
        General helper: if you pass a 'perk-images/...' path from manifest,
        returns the absolute CDN URL. If it's already absolute, returns as-is.
        """
        if not path:
            return ""
        if path.startswith("http://") or path.startswith("https://"):
            return path
        p = path.lstrip("/")
        if p.startswith("perk-images/"):
            return self._ddragon_img(p)
        return f"{self.DDRAGON_BASE}/{p}"

    def get_item_url(self, item_id: int | str | None) -> str:
        if item_id in (None, "", 0, "0"):
            return ""
        try:
            iid = int(item_id)
        except Exception:
            return ""
        self._ensure_item_maps()
        filename = self._item_image_by_id.get(iid, "") if self._item_image_by_id else ""
        if not filename:
            # fallback to conventional "{id}.png"
            filename = f"{iid}.png"
        return self._ddragon_versioned_img("item", filename)

    def get_summoner_spell_url(self, spell_id: int | str | None) -> str:
        if spell_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(spell_id)
        except Exception:
            return ""
        self._ensure_summoner_maps()
        filename = self._summoner_imagefull_by_id.get(sid, "") if self._summoner_imagefull_by_id else ""
        if not filename:
            return ""
        return self._ddragon_versioned_img("spell", filename)

    def get_rune_url(self, rune_id: int | str | None) -> str:
        if rune_id in (None, "", 0, "0"):
            return ""
        try:
            rid = int(rune_id)
        except Exception:
            return ""
        self._ensure_rune_maps()
        icon = self._rune_icon_by_id.get(rid, "") if self._rune_icon_by_id else ""
        return self._ddragon_img(icon) if icon else ""

    def get_rune_style_url(self, style_id: int | str | None) -> str:
        if style_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(style_id)
        except Exception:
            return ""
        self._ensure_rune_maps()
        icon = self._rune_style_icon_by_id.get(sid, "") if self._rune_style_icon_by_id else ""
        return self._ddragon_img(icon) if icon else ""

    def get_stat_shard_url(self, shard_id: int | str | None) -> str:
        if shard_id in (None, "", 0, "0"):
            return ""
        try:
            sid = int(shard_id)
        except Exception:
            return ""
        filename = self._stat_shard_icon_by_id.get(sid, "")
        if not filename:
            return ""
        return self._ddragon_img(f"perk-images/StatMods/{filename}")

    # Champions (handle API vs DDragon naming differences)

    def _get_champion_image_full_by_id(self, dd_id: str) -> Optional[str]:
        meta = self.get_champion_data().get(dd_id)
        if not meta:
            return None
        image = meta.get("image") or {}
        return image.get("full")

    def get_champion_url(self, champion: int | str) -> str:
        """
        Accepts:
          - numeric key (int or numeric str), e.g., 266
          - API display name, e.g., "Wukong"
          - DDragon id, e.g., "MonkeyKing"
        Returns square icon URL.
        """
        dd_id: Optional[str] = None

        # numeric path
        if isinstance(champion, int) or (isinstance(champion, str) and champion.isdigit()):
            try:
                key = int(champion)
            except Exception:
                key = None
            if key is not None:
                dd_id = self._get_champion_name_by_numeric_id().get(key)

        # string path (id or display name)
        if dd_id is None and isinstance(champion, str):
            s = champion.strip()
            # direct DDragon id
            if s in self.get_champion_data():
                dd_id = s
            else:
                n = self._normalize_key(s)
                dd_id = self._get_champion_normalized_to_id().get(n)

        if not dd_id:
            return ""
        img_full = self._get_champion_image_full_by_id(dd_id)
        if not img_full:
            return ""
        return self._ddragon_versioned_img("champion", img_full)


# ---------------------------- Module-level helpers ---------------------------

riot_cdn = RiotCDNConfig()

def set_language(lang: str) -> None:
    riot_cdn.set_language(lang)

# Simple passthrough when templates provide relative icon paths
def get_image_url(path: str) -> str:
    return riot_cdn.get_image_url(path)

# Names
def get_item_name(item_id: int | str | None) -> str:
    return riot_cdn.get_item_name(item_id)

def get_rune_name(rune_id: int | str | None) -> str:
    return riot_cdn.get_rune_name(rune_id)

def get_rune_style_name(style_id: int | str | None) -> str:
    return riot_cdn.get_rune_style_name(style_id)

def get_summoner_spell_name(spell_id: int | str | None) -> str:
    return riot_cdn.get_summoner_spell_name(spell_id)

def get_stat_shard_name(shard_id: int | str | None) -> str:
    return riot_cdn.get_stat_shard_name(shard_id)

# Images
def get_item_image_url(item_id: int | str | None) -> str:
    return riot_cdn.get_item_url(item_id)

def get_rune_image_url(rune_id: int | str | None) -> str:
    return riot_cdn.get_rune_url(rune_id)

def get_rune_style_image_url(style_id: int | str | None) -> str:
    return riot_cdn.get_rune_style_url(style_id)

def get_summoner_spell_image_url(spell_id: int | str | None) -> str:
    return riot_cdn.get_summoner_spell_url(spell_id)

def get_stat_shard_image_url(shard_id: int | str | None) -> str:
    return riot_cdn.get_stat_shard_url(shard_id)

def get_champion_image_url(champion: int | str) -> str:
    return riot_cdn.get_champion_url(champion)
