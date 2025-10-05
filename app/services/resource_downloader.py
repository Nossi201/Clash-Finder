# app/services/resource_downloader.py
"""
Resource downloader for Data Dragon assets.
Downloads and updates champion, item, spell, and rune data.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from config.logging_config import get_logger
from config.cdn_config import (
    CDN_BASE_URL,
    DDRAGON_VERSION,
    RESOURCE_PATHS
)

logger = get_logger('services.resource_downloader')


class ResourceDownloader:
    """Downloads game resources from Data Dragon CDN."""

    def __init__(self, data_dir: str = 'app/static/data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.version = DDRAGON_VERSION

        logger.info(f"Resource downloader initialized | Version: {self.version}")

    def _download_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON from URL.

        Args:
            url: URL to download from

        Returns:
            Parsed JSON data or None on error
        """
        try:
            logger.debug(f"Downloading: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Successfully downloaded: {url}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {url}: {e}")
            return None

    def _save_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        Save JSON data to file.

        Args:
            filename: Name of file to save
            data: Data to save

        Returns:
            True if successful, False otherwise
        """
        filepath = self.data_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
            return False

    def download_champions(self) -> bool:
        """
        Download champion data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Downloading champion data")

        url = f"{CDN_BASE_URL}/{self.version}/data/en_US/champion.json"
        data = self._download_json(url)

        if data:
            return self._save_json('champions.json', data)

        return False

    def download_items(self) -> bool:
        """
        Download item data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Downloading item data")

        url = f"{CDN_BASE_URL}/{self.version}/data/en_US/item.json"
        data = self._download_json(url)

        if data:
            return self._save_json('items.json', data)

        return False

    def download_summoner_spells(self) -> bool:
        """
        Download summoner spell data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Downloading summoner spell data")

        url = f"{CDN_BASE_URL}/{self.version}/data/en_US/summoner.json"
        data = self._download_json(url)

        if data:
            return self._save_json('summoner_spells.json', data)

        return False

    def download_runes(self) -> bool:
        """
        Download rune data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Downloading rune data")

        url = f"{CDN_BASE_URL}/{self.version}/data/en_US/runesReforged.json"
        data = self._download_json(url)

        if data:
            return self._save_json('runes.json', data)

        return False

    def download_profile_icons(self) -> bool:
        """
        Download profile icon data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Downloading profile icon data")

        url = f"{CDN_BASE_URL}/{self.version}/data/en_US/profileicon.json"
        data = self._download_json(url)

        if data:
            return self._save_json('profile_icons.json', data)

        return False

    def download_all(self) -> Dict[str, bool]:
        """
        Download all game resources.

        Returns:
            Dictionary with download status for each resource
        """
        logger.info("Starting download of all resources")

        results = {
            'champions': self.download_champions(),
            'items': self.download_items(),
            'summoner_spells': self.download_summoner_spells(),
            'runes': self.download_runes(),
            'profile_icons': self.download_profile_icons()
        }

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        logger.info(
            f"Download complete | Successful: {successful}/{total} | "
            f"Results: {results}"
        )

        return results

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest Data Dragon version.

        Returns:
            Latest version string or None on error
        """
        try:
            url = "https://ddragon.leagueoflegends.com/api/versions.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            versions = response.json()
            if versions and len(versions) > 0:
                latest = versions[0]
                logger.info(f"Latest Data Dragon version: {latest}")
                return latest

            return None

        except Exception as e:
            logger.error(f"Error getting latest version: {e}")
            return None

    def update_version(self, new_version: Optional[str] = None) -> bool:
        """
        Update to a new Data Dragon version.

        Args:
            new_version: Version to update to (or None for latest)

        Returns:
            True if successful, False otherwise
        """
        if new_version is None:
            new_version = self.get_latest_version()

        if not new_version:
            logger.error("Could not determine version to update to")
            return False

        logger.info(f"Updating from version {self.version} to {new_version}")

        old_version = self.version
        self.version = new_version

        # Try to download all resources with new version
        results = self.download_all()

        if all(results.values()):
            logger.info(f"Successfully updated to version {new_version}")
            return True
        else:
            logger.error(f"Failed to update to version {new_version}, reverting")
            self.version = old_version
            return False

    def verify_downloads(self) -> Dict[str, bool]:
        """
        Verify that all required files exist and are valid.

        Returns:
            Dictionary with verification status for each file
        """
        required_files = [
            'champions.json',
            'items.json',
            'summoner_spells.json',
            'runes.json'
        ]

        status = {}

        for filename in required_files:
            filepath = self.data_dir / filename

            # Check if file exists
            if not filepath.exists():
                status[filename] = False
                continue

            # Check if file is valid JSON
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    json.load(f)
                status[filename] = True
            except Exception as e:
                logger.error(f"Invalid JSON in {filename}: {e}")
                status[filename] = False

        logger.debug(f"Verification results: {status}")
        return status


# Global downloader instance
resource_downloader = ResourceDownloader()