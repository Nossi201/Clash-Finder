# ssl_env_config.py
import os, certifi, ssl
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
if os.getenv("ALLOW_INSECURE_SSL") == "1":
    ssl._create_default_https_context = ssl._create_unverified_context