# ssl_env_config.py - Dodatkowa konfiguracja SSL
import os
import certifi
import ssl

# Ustawienia środowiskowe dla SSL
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Jeśli używasz macOS, może być potrzebne:
# os.environ['CERT_PATH'] = certifi.where()

# Globalne ustawienie kontekstu SSL
ssl._create_default_https_context = ssl._create_unverified_context