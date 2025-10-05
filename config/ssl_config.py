# config/ssl_config.py
"""
SSL/TLS configuration for Flask application.
Handles HTTPS setup and certificate management.
"""

import os
import ssl
from pathlib import Path


class SSLConfig:
    """SSL/TLS configuration."""

    # SSL enabled
    SSL_ENABLED = os.getenv('SSL_ENABLED', 'False').lower() == 'true'

    # Certificate paths
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', 'certs/cert.pem')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', 'certs/key.pem')
    SSL_CA_BUNDLE = os.getenv('SSL_CA_BUNDLE', None)

    # SSL protocol version
    SSL_PROTOCOL = ssl.PROTOCOL_TLS_SERVER

    # Cipher suites (strong ciphers only)
    SSL_CIPHERS = (
        'ECDHE-RSA-AES256-GCM-SHA384:'
        'ECDHE-RSA-AES128-GCM-SHA256:'
        'ECDHE-RSA-AES256-SHA384:'
        'ECDHE-RSA-AES128-SHA256'
    )

    # TLS versions
    SSL_MIN_VERSION = ssl.TLSVersion.TLSv1_2
    SSL_MAX_VERSION = ssl.TLSVersion.TLSv1_3

    # Certificate verification
    SSL_VERIFY_MODE = ssl.CERT_REQUIRED if SSL_ENABLED else ssl.CERT_NONE

    # HSTS (HTTP Strict Transport Security)
    HSTS_ENABLED = True
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = False

    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }

    @staticmethod
    def get_ssl_context():
        """
        Create SSL context for Flask application.

        Returns:
            SSL context or None if SSL is disabled
        """
        if not SSLConfig.SSL_ENABLED:
            return None

        # Check if certificate files exist
        cert_path = Path(SSLConfig.SSL_CERT_PATH)
        key_path = Path(SSLConfig.SSL_KEY_PATH)

        if not cert_path.exists():
            raise FileNotFoundError(f"SSL certificate not found: {cert_path}")

        if not key_path.exists():
            raise FileNotFoundError(f"SSL key not found: {key_path}")

        # Create SSL context
        context = ssl.SSLContext(SSLConfig.SSL_PROTOCOL)

        # Set cipher suites
        context.set_ciphers(SSLConfig.SSL_CIPHERS)

        # Set TLS version range
        context.minimum_version = SSLConfig.SSL_MIN_VERSION
        context.maximum_version = SSLConfig.SSL_MAX_VERSION

        # Load certificate and key
        context.load_cert_chain(
            certfile=str(cert_path),
            keyfile=str(key_path)
        )

        # Load CA bundle if provided
        if SSLConfig.SSL_CA_BUNDLE:
            ca_path = Path(SSLConfig.SSL_CA_BUNDLE)
            if ca_path.exists():
                context.load_verify_locations(cafile=str(ca_path))

        # Set verification mode
        context.verify_mode = SSLConfig.SSL_VERIFY_MODE

        return context

    @staticmethod
    def apply_security_headers(response):
        """
        Apply security headers to Flask response.

        Args:
            response: Flask response object

        Returns:
            Modified response with security headers
        """
        # Add HSTS header if enabled
        if SSLConfig.HSTS_ENABLED and SSLConfig.SSL_ENABLED:
            hsts_value = f'max-age={SSLConfig.HSTS_MAX_AGE}'

            if SSLConfig.HSTS_INCLUDE_SUBDOMAINS:
                hsts_value += '; includeSubDomains'

            if SSLConfig.HSTS_PRELOAD:
                hsts_value += '; preload'

            response.headers['Strict-Transport-Security'] = hsts_value

        # Add other security headers
        for header, value in SSLConfig.SECURITY_HEADERS.items():
            response.headers[header] = value

        return response

    @staticmethod
    def init_app(app):
        """
        Initialize SSL configuration with Flask app.

        Args:
            app: Flask application instance
        """

        # Apply security headers to all responses
        @app.after_request
        def add_security_headers(response):
            return SSLConfig.apply_security_headers(response)

        # Force HTTPS in production
        if app.config.get('ENV') == 'production' and SSLConfig.SSL_ENABLED:
            @app.before_request
            def force_https():
                from flask import request, redirect, url_for

                if not request.is_secure:
                    url = request.url.replace('http://', 'https://', 1)
                    return redirect(url, code=301)


def generate_self_signed_cert(cert_path: str = 'certs/cert.pem', key_path: str = 'certs/key.pem'):
    """
    Generate self-signed certificate for development.

    Args:
        cert_path: Path to save certificate
        key_path: Path to save private key

    Note:
        Requires pyOpenSSL package
    """
    try:
        from OpenSSL import crypto
    except ImportError:
        raise ImportError("pyOpenSSL is required to generate self-signed certificates")

    # Create directories if they don't exist
    cert_dir = Path(cert_path).parent
    cert_dir.mkdir(parents=True, exist_ok=True)

    # Create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "Organization"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"

    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Save certificate
    with open(cert_path, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    # Save private key
    with open(key_path, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    print(f"Self-signed certificate generated:")
    print(f"  Certificate: {cert_path}")
    print(f"  Private Key: {key_path}")
    print("\nWARNING: This is a self-signed certificate for development only!")


def check_ssl_configuration() -> dict:
    """
    Check SSL configuration status.

    Returns:
        Dictionary with SSL status information
    """
    status = {
        'ssl_enabled': SSLConfig.SSL_ENABLED,
        'cert_exists': Path(SSLConfig.SSL_CERT_PATH).exists(),
        'key_exists': Path(SSLConfig.SSL_KEY_PATH).exists(),
        'hsts_enabled': SSLConfig.HSTS_ENABLED,
    }

    if SSLConfig.SSL_CA_BUNDLE:
        status['ca_bundle_exists'] = Path(SSLConfig.SSL_CA_BUNDLE).exists()

    return status