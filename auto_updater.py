# auto_updater.py
import schedule
import time
import json
from datetime import datetime
from pathlib import Path
from resource_downloader import LoLResourceDownloader


class LoLAutoUpdater:
    """Automatically update League of Legends resources by version checking."""

    def __init__(self):
        """Initialize the version file path and resource downloader."""
        self.version_file = Path("lol_version.json")
        self.downloader = LoLResourceDownloader()

    def load_current_version(self):
        """Load the current version from the version file."""
        if self.version_file.exists():
            with open(self.version_file, "r") as f:
                data = json.load(f)
                return data.get("version", "")
        return ""

    def save_current_version(self, version):
        """Save the given version and timestamp to the version file."""
        with open(self.version_file, "w") as f:
            json.dump({"version": version, "updated_at": datetime.utcnow().isoformat()}, f)

    def update_resources(self):
        """Check for a new version and download resources if it differs."""
        current = self.load_current_version()
        latest = self.downloader.get_latest_version()

        if latest != current:
            print(f"Starting update to version {latest}...")
            self.downloader.download_all()
            self.save_current_version(latest)
            print(f"Successfully updated to version {latest}")

        return latest != current


def force_update():
    """Force-download all resources and update the version file immediately."""
    updater = LoLAutoUpdater()
    updater.downloader.download_all()
    version = updater.downloader.get_latest_version()
    updater.save_current_version(version)


def check_version():
    """Perform a version check and update resources if needed."""
    LoLAutoUpdater().update_resources()


def start_auto_updater():
    """Start the auto-updater loop, checking for updates every 6 hours."""
    updater = LoLAutoUpdater()
    schedule.every(6).hours.do(updater.update_resources)
    print("Auto-updater started. Checking for updates every 6 hours...")

    while True:
        schedule.run_pending()
        time.sleep(60)


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
