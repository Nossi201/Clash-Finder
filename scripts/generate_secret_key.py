# scripts/generate_secret_key.py
"""
Generate a secure secret key for Flask application.
"""

import secrets
import sys


def generate_secret_key(length=32):
    """
    Generate a cryptographically secure secret key.

    Args:
        length: Length of the key in bytes

    Returns:
        Hex string of the secret key
    """
    return secrets.token_hex(length)


def main():
    """Main function."""
    print("=" * 60)
    print("Flask Secret Key Generator")
    print("=" * 60)
    print()

    # Generate keys
    secret_key = generate_secret_key(32)
    admin_token = generate_secret_key(16)
    api_key = generate_secret_key(24)

    print("Generated keys:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"ADMIN_TOKEN={admin_token}")
    print(f"API_KEY={api_key}")
    print()
    print("=" * 60)
    print("Add these to your .env file")
    print("=" * 60)
    print()
    print("SECURITY WARNING:")
    print("  - Keep these keys secret!")
    print("  - Never commit .env to version control")
    print("  - Use different keys for different environments")
    print()


if __name__ == '__main__':
    main()