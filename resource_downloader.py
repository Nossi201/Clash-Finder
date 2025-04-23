# resource_downloader.py
import os
import requests
import json
from pathlib import Path
import urllib.request
from PIL import Image
import io


class LoLResourceDownloader:
    def __init__(self, base_path="static/img"):
        self.base_path = Path(base_path)
        self.version = self.get_latest_version()
        self.data_dragon_base = f"https://ddragon.leagueoflegends.com/cdn/{self.version}"
        self.community_dragon_base = "https://raw.communitydragon.org/latest"

    def get_latest_version(self):
        """Get the latest version of League of Legends"""
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(versions_url)
        versions = response.json()
        return versions[0]  # Latest version is the first in the list

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.base_path / "champion",
            self.base_path / "item",
            self.base_path / "spells/summoner",
            self.base_path / "runes_and_shards",
            self.base_path / "Logo"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def download_file(self, url, save_path):
        """Download a file from URL to save_path"""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                print(f"Failed to download {url}: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return False

    def download_champions(self):
        """Download all champion icons"""
        print("Downloading champion icons...")
        champion_data_url = f"{self.data_dragon_base}/data/en_US/champion.json"
        response = requests.get(champion_data_url)
        champions = response.json()['data']

        for champion_key, champion_data in champions.items():
            champion_id = champion_data['id']
            image_url = f"{self.data_dragon_base}/img/champion/{champion_id}.png"
            save_path = self.base_path / f"champion/{champion_id}.png"

            if not save_path.exists():
                print(f"Downloading {champion_id}.png...")
                self.download_file(image_url, save_path)

    def download_items(self):
        """Download all item icons"""
        print("Downloading item icons...")
        item_data_url = f"{self.data_dragon_base}/data/en_US/item.json"
        response = requests.get(item_data_url)
        items = response.json()['data']

        for item_id, item_data in items.items():
            image_url = f"{self.data_dragon_base}/img/item/{item_id}.png"
            save_path = self.base_path / f"item/{item_id}.png"

            if not save_path.exists():
                print(f"Downloading item {item_id}.png...")
                self.download_file(image_url, save_path)

    def download_summoner_spells(self):
        """Download all summoner spell icons"""
        print("Downloading summoner spell icons...")
        summoner_data_url = f"{self.data_dragon_base}/data/en_US/summoner.json"
        response = requests.get(summoner_data_url)
        spells = response.json()['data']

        for spell_name, spell_data in spells.items():
            spell_id = spell_data['key']
            image_name = spell_data['image']['full']
            image_url = f"{self.data_dragon_base}/img/spell/{image_name}"
            save_path = self.base_path / f"spells/summoner/{spell_id}.png"

            if not save_path.exists():
                print(f"Downloading spell {spell_id}.png...")
                self.download_file(image_url, save_path)

    def download_runes(self):
        """Download all rune icons"""
        print("Downloading rune icons...")
        runes_data_url = f"{self.data_dragon_base}/data/en_US/runesReforged.json"
        response = requests.get(runes_data_url)
        rune_paths = response.json()

        for path in rune_paths:
            # Download path icon
            path_icon_url = f"{self.data_dragon_base}/img/{path['icon']}"
            path_save_path = self.base_path / f"runes_and_shards/{path['id']}.png"

            if not path_save_path.exists():
                print(f"Downloading rune path {path['id']}.png...")
                self.download_file(path_icon_url, path_save_path)

            # Download individual runes
            for slot in path['slots']:
                for rune in slot['runes']:
                    rune_icon_url = f"{self.data_dragon_base}/img/{rune['icon']}"
                    rune_save_path = self.base_path / f"runes_and_shards/{rune['id']}.png"

                    if not rune_save_path.exists():
                        print(f"Downloading rune {rune['id']}.png...")
                        self.download_file(rune_icon_url, rune_save_path)

    def download_stat_shards(self):
        """Download stat shard icons from Community Dragon"""
        print("Downloading stat shard icons...")
        stat_shards = {
            5001: "StatModsHealthScalingIcon",
            5002: "StatModsArmorIcon",
            5003: "StatModsMagicResIcon",
            5005: "StatModsAttackSpeedIcon",
            5007: "StatModsCDRScalingIcon",
            5008: "StatModsAdaptiveForceIcon",
            5010: "StatModsMovementSpeedIcon",
            5011: "StatModsHealthPlusIcon",
            5012: "StatModsArmorIcon",
            5013: "StatModsMagicResIcon"
        }

        for shard_id, icon_name in stat_shards.items():
            icon_url = f"{self.community_dragon_base}/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/statmods/{icon_name.lower()}.png"
            save_path = self.base_path / f"runes_and_shards/{shard_id}.png"

            if not save_path.exists():
                print(f"Downloading stat shard {shard_id}.png...")
                self.download_file(icon_url, save_path)

    def download_all(self):
        """Download all resources"""
        self.create_directories()
        self.download_champions()
        self.download_items()
        self.download_summoner_spells()
        self.download_runes()
        self.download_stat_shards()
        print("All resources downloaded successfully!")


# Skrypt do automatycznej aktualizacji
if __name__ == "__main__":
    downloader = LoLResourceDownloader()
    downloader.download_all()