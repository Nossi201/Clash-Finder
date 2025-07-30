# ssl_env_config.py – Additional SSL configuration
import os
import certifi
import ssl

# SSL environment settings
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# If you're on macOS, you may need:
# os.environ['CERT_PATH'] = certifi.where()

# Global SSL context configuration
ssl._create_default_https_context = ssl._create_unverified_context