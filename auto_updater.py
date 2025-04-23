# auto_updater.py
import schedule
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from resource_downloader import LoLResourceDownloader


class LoLAutoUpdater:
    def __init__(self):
        self.version_file = Path("lol_version.json")
        self.downloader = LoLResourceDownloader()

    def load_current_version(self):
        """Load the current version from file"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return data.get('version')
        return None

    def save_current_version(self, version):
        """Save the current version to file"""
        with open(self.version_file, 'w') as f:
            json.dump({
                'version': version,
                'last_updated': datetime.now().isoformat()
            }, f)

    def check_for_updates(self):
        """Check if there's a new version available"""
        try:
            current_version = self.load_current_version()
            latest_version = self.downloader.get_latest_version()

            if current_version != latest_version:
                print(f"New version detected: {latest_version} (previous: {current_version})")
                return True, latest_version
            else:
                print(f"No update needed. Current version: {current_version}")
                return False, latest_version
        except Exception as e:
            print(f"Error checking for updates: {str(e)}")
            return False, None

    def update_resources(self):
        """Update resources if a new version is available"""
        needs_update, latest_version = self.check_for_updates()

        if needs_update:
            print(f"Starting update to version {latest_version}...")
            self.downloader.download_all()
            self.save_current_version(latest_version)
            print(f"Successfully updated to version {latest_version}")

        return needs_update


# Funkcja do ręcznego uruchomienia aktualizacji
def force_update():
    updater = LoLAutoUpdater()
    updater.downloader.download_all()
    version = updater.downloader.get_latest_version()
    updater.save_current_version(version)
    print(f"Forced update completed. Version: {version}")


# Funkcja do sprawdzenia aktualnej wersji
def check_version():
    updater = LoLAutoUpdater()
    current = updater.load_current_version()
    latest = updater.downloader.get_latest_version()
    print(f"Current version: {current}")
    print(f"Latest version: {latest}")
    print(f"Update needed: {current != latest}")


# Automatyczne sprawdzanie co 6 godzin
def start_auto_updater():
    updater = LoLAutoUpdater()

    # Sprawdź przy starcie
    updater.update_resources()

    # Sprawdzaj co 6 godzin
    schedule.every(6).hours.do(updater.update_resources)

    print("Auto-updater started. Checking for updates every 6 hours...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę czy nie ma zadań do wykonania


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "force":
            force_update()
        elif sys.argv[1] == "check":
            check_version()
        else:
            print("Unknown command. Use 'force' or 'check'")
    else:
        start_auto_updater()