# scripts/update_resources.py
"""
Script to manually update game resources from Data Dragon.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.resource_downloader import resource_downloader
from config.logging_config import get_logger

logger = get_logger('scripts.update_resources')


def main():
    """Main function."""
    print("=" * 60)
    print("Clash Finder - Resource Updater")
    print("=" * 60)
    print()

    # Check for latest version
    print("Checking for latest Data Dragon version...")
    latest_version = resource_downloader.get_latest_version()

    if latest_version:
        print(f"✓ Latest version: {latest_version}")
        current_version = resource_downloader.version
        print(f"  Current version: {current_version}")

        if latest_version != current_version:
            print(f"\n⚠️  New version available: {latest_version}")
            response = input("Update to latest version? (y/n): ")

            if response.lower() == 'y':
                print("\nUpdating to latest version...")
                success = resource_downloader.update_version(latest_version)

                if success:
                    print("✓ Update successful!")
                else:
                    print("✗ Update failed")
                    return 1
            else:
                print("Keeping current version.")
        else:
            print("✓ Already on latest version")
    else:
        print("✗ Could not retrieve latest version")
        print("Continuing with current version...")

    # Download resources
    print("\n" + "-" * 60)
    print("Downloading game resources...")
    print("-" * 60)

    results = resource_downloader.download_all()

    # Display results
    print("\nDownload Results:")
    for resource, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {resource}")

    # Verify downloads
    print("\n" + "-" * 60)
    print("Verifying downloads...")
    print("-" * 60)

    verification = resource_downloader.verify_downloads()

    all_valid = all(verification.values())

    print("\nVerification Results:")
    for filename, valid in verification.items():
        status = "✓" if valid else "✗"
        print(f"  {status} {filename}")

    # Summary
    print("\n" + "=" * 60)
    if all(results.values()) and all_valid:
        print("SUCCESS: All resources downloaded and verified!")
        print("=" * 60)
        return 0
    else:
        print("WARNING: Some resources failed to download or verify.")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())