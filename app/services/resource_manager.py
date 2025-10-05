# app/services/resource_manager.py
"""
Resource manager for game assets.
Handles champion icons, items, summoner spells, and runes.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from config.logging_config import get_logger
from config.cdn_config import (
    CDN_BASE_URL,
    DDRAGON_VERSION,
    RESOURCE_PATHS,
    get_champion_icon_url,
    get_item_icon_url,
    get_summoner_spell_icon_url,
    get_rune_icon_url
)

logger = get_logger('services.resource_manager')


class ResourceManager:
    """Manages game resource data and URLs."""

    def __init__(self, data_dir: str = 'app/static/data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Cache for loaded JSON data
        self._champions: Optional[Dict[str, Any]] = None
        self._items: Optional[Dict[str, Any]] = None
        self._summoner_spells: Optional[Dict[str, Any]] = None
        self._runes: Optional[Dict[str, Any]] = None

        logger.info(f"Resource manager initialized | Data dir: {self.data_dir}")

    def _load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load JSON file from data directory."""
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.warning(f"Resource file not found: {filename}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded resource: {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def _save_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to file."""
        filepath = self.data_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved resource: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            return False

    # Champions

    def load_champions(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load champion data."""
        if self._champions is not None and not force_reload:
            return self._champions

        self._champions = self._load_json('champions.json') or {'data': {}}
        return self._champions

    def get_champion_by_id(self, champion_id: int) -> Optional[Dict[str, Any]]:
        """Get champion data by ID."""
        champions = self.load_champions()

        for champ_key, champ_data in champions.get('data', {}).items():
            if int(champ_data.get('key', -1)) == champion_id:
                return champ_data

        return None

    def get_champion_name(self, champion_id: int) -> str:
        """Get champion name by ID."""
        champ = self.get_champion_by_id(champion_id)
        return champ.get('name', f'Champion{champion_id}') if champ else f'Champion{champion_id}'

    def get_champion_icon(self, champion_id: int) -> str:
        """Get champion icon URL."""
        champ = self.get_champion_by_id(champion_id)

        if champ:
            image_name = champ.get('image', {}).get('full', '')
            if image_name:
                return get_champion_icon_url(image_name)

        return get_champion_icon_url('Unknown.png')

    # Items

    def load_items(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load item data."""
        if self._items is not None and not force_reload:
            return self._items

        self._items = self._load_json('items.json') or {'data': {}}
        return self._items

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get item data by ID."""
        items = self.load_items()
        return items.get('data', {}).get(str(item_id))

    def get_item_name(self, item_id: int) -> str:
        """Get item name by ID."""
        item = self.get_item_by_id(item_id)
        return item.get('name', f'Item{item_id}') if item else f'Item{item_id}'

    def get_item_icon(self, item_id: int) -> str:
        """Get item icon URL."""
        item = self.get_item_by_id(item_id)

        if item:
            image_name = item.get('image', {}).get('full', '')
            if image_name:
                return get_item_icon_url(image_name)

        return get_item_icon_url(f'{item_id}.png')

    # Summoner Spells

    def load_summoner_spells(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load summoner spell data."""
        if self._summoner_spells is not None and not force_reload:
            return self._summoner_spells

        self._summoner_spells = self._load_json('summoner_spells.json') or {'data': {}}
        return self._summoner_spells

    def get_summoner_spell_by_id(self, spell_id: int) -> Optional[Dict[str, Any]]:
        """Get summoner spell data by ID."""
        spells = self.load_summoner_spells()

        for spell_key, spell_data in spells.get('data', {}).items():
            if int(spell_data.get('key', -1)) == spell_id:
                return spell_data

        return None

    def get_summoner_spell_name(self, spell_id: int) -> str:
        """Get summoner spell name by ID."""
        spell = self.get_summoner_spell_by_id(spell_id)
        return spell.get('name', f'Spell{spell_id}') if spell else f'Spell{spell_id}'

    def get_summoner_spell_icon(self, spell_id: int) -> str:
        """Get summoner spell icon URL."""
        spell = self.get_summoner_spell_by_id(spell_id)

        if spell:
            image_name = spell.get('image', {}).get('full', '')
            if image_name:
                return get_summoner_spell_icon_url(image_name)

        return get_summoner_spell_icon_url(f'{spell_id}.png')

    # Runes

    def load_runes(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load rune data."""
        if self._runes is not None and not force_reload:
            return self._runes

        self._runes = self._load_json('runes.json') or []
        return self._runes

    def get_rune_by_id(self, rune_id: int) -> Optional[Dict[str, Any]]:
        """Get rune data by ID."""
        runes = self.load_runes()

        # Search in all rune trees
        for tree in runes:
            if tree.get('id') == rune_id:
                return tree

            # Search in slots
            for slot in tree.get('slots', []):
                for rune in slot.get('runes', []):
                    if rune.get('id') == rune_id:
                        return rune

        return None

    def get_rune_name(self, rune_id: int) -> str:
        """Get rune name by ID."""
        rune = self.get_rune_by_id(rune_id)
        return rune.get('name', f'Rune{rune_id}') if rune else f'Rune{rune_id}'

    def get_rune_icon(self, rune_id: int) -> str:
        """Get rune icon URL."""
        rune = self.get_rune_by_id(rune_id)

        if rune:
            icon_path = rune.get('icon', '')
            if icon_path:
                return get_rune_icon_url(icon_path)

        return get_rune_icon_url('')

    # Utility methods

    def reload_all(self):
        """Reload all resource data."""
        logger.info("Reloading all resource data")
        self.load_champions(force_reload=True)
        self.load_items(force_reload=True)
        self.load_summoner_spells(force_reload=True)
        self.load_runes(force_reload=True)

    def get_data_version(self) -> str:
        """Get current Data Dragon version."""
        return DDRAGON_VERSION

    def check_resources_exist(self) -> Dict[str, bool]:
        """Check if all required resource files exist."""
        required_files = [
            'champions.json',
            'items.json',
            'summoner_spells.json',
            'runes.json'
        ]

        status = {}
        for filename in required_files:
            filepath = self.data_dir / filename
            status[filename] = filepath.exists()

        return status

    def get_missing_resources(self) -> List[str]:
        """Get list of missing resource files."""
        status = self.check_resources_exist()
        return [filename for filename, exists in status.items() if not exists]


# Global resource manager instance
resource_manager = ResourceManager()