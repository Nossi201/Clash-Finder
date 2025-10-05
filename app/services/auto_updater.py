# app/services/auto_updater.py
"""
Automatic resource updater.
Periodically checks for and downloads new Data Dragon versions.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable

from config.logging_config import get_logger
from app.services.resource_downloader import resource_downloader
from app.services.resource_manager import resource_manager

logger = get_logger('services.auto_updater')


class AutoUpdater:
    """Automatic resource updater with scheduled checks."""

    def __init__(
            self,
            check_interval_hours: int = 24,
            auto_update: bool = True,
            on_update_callback: Optional[Callable] = None
    ):
        """
        Initialize auto updater.

        Args:
            check_interval_hours: Hours between update checks
            auto_update: Whether to automatically download updates
            on_update_callback: Function to call after successful update
        """
        self.check_interval = timedelta(hours=check_interval_hours)
        self.auto_update = auto_update
        self.on_update_callback = on_update_callback

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_check: Optional[datetime] = None
        self._current_version: Optional[str] = None

        logger.info(
            f"Auto updater initialized | "
            f"Check interval: {check_interval_hours}h | "
            f"Auto update: {auto_update}"
        )

    def _check_for_updates(self) -> Optional[str]:
        """
        Check if a new version is available.

        Returns:
            New version string if available, None otherwise
        """
        try:
            latest_version = resource_downloader.get_latest_version()

            if not latest_version:
                logger.warning("Could not retrieve latest version")
                return None

            current_version = resource_downloader.version

            if latest_version != current_version:
                logger.info(
                    f"New version available | "
                    f"Current: {current_version} | Latest: {latest_version}"
                )
                return latest_version

            logger.debug("Already on latest version")
            return None

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None

    def _perform_update(self, new_version: str) -> bool:
        """
        Download and apply update.

        Args:
            new_version: Version to update to

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting update to version {new_version}")

        try:
            # Download new resources
            success = resource_downloader.update_version(new_version)

            if success:
                # Verify downloads
                verification = resource_downloader.verify_downloads()

                if all(verification.values()):
                    # Reload resources in manager
                    resource_manager.reload_all()

                    logger.info(f"Successfully updated to version {new_version}")

                    # Call callback if provided
                    if self.on_update_callback:
                        try:
                            self.on_update_callback(new_version)
                        except Exception as e:
                            logger.error(f"Error in update callback: {e}")

                    return True
                else:
                    logger.error(f"Verification failed after update: {verification}")
                    return False

            logger.error("Update download failed")
            return False

        except Exception as e:
            logger.error(f"Error performing update: {e}")
            return False

    def check_and_update(self) -> bool:
        """
        Check for updates and apply if available.

        Returns:
            True if update was applied, False otherwise
        """
        self._last_check = datetime.now()

        new_version = self._check_for_updates()

        if new_version and self.auto_update:
            return self._perform_update(new_version)
        elif new_version:
            logger.info(
                f"Update available ({new_version}) but auto-update is disabled"
            )

        return False

    def _update_loop(self):
        """Main update loop running in background thread."""
        logger.info("Auto updater loop started")

        # Initial check on startup
        self.check_and_update()

        while self._running:
            try:
                # Sleep for check interval
                time.sleep(self.check_interval.total_seconds())

                if self._running:
                    self.check_and_update()

            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                # Continue running despite errors
                time.sleep(60)  # Brief pause before continuing

        logger.info("Auto updater loop stopped")

    def start(self):
        """Start the auto updater background thread."""
        if self._running:
            logger.warning("Auto updater already running")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._update_loop,
            daemon=True,
            name="AutoUpdater"
        )
        self._thread.start()

        logger.info("Auto updater started")

    def stop(self):
        """Stop the auto updater background thread."""
        if not self._running:
            logger.warning("Auto updater not running")
            return

        logger.info("Stopping auto updater")
        self._running = False

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("Auto updater stopped")

    def force_update(self) -> bool:
        """
        Force an immediate update check and download.

        Returns:
            True if update was applied, False otherwise
        """
        logger.info("Forcing immediate update check")
        return self.check_and_update()

    def get_status(self) -> dict:
        """
        Get current updater status.

        Returns:
            Dictionary with status information
        """
        return {
            'running': self._running,
            'auto_update_enabled': self.auto_update,
            'check_interval_hours': self.check_interval.total_seconds() / 3600,
            'last_check': self._last_check.isoformat() if self._last_check else None,
            'current_version': resource_downloader.version,
            'next_check': (
                (self._last_check + self.check_interval).isoformat()
                if self._last_check else None
            )
        }


# Global auto updater instance
auto_updater = AutoUpdater()


def init_updater(
        app,
        check_interval_hours: int = 24,
        auto_update: bool = True,
        start_immediately: bool = True
):
    """
    Initialize and optionally start the auto updater.

    Args:
        app: Flask application instance
        check_interval_hours: Hours between update checks
        auto_update: Whether to automatically download updates
        start_immediately: Whether to start the updater immediately
    """
    global auto_updater

    auto_updater = AutoUpdater(
        check_interval_hours=check_interval_hours,
        auto_update=auto_update
    )

    if start_immediately:
        auto_updater.start()

    logger.info("Auto updater initialized with Flask app")