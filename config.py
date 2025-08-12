# config.py
import os
RIOT_API_KEY = os.getenv("RIOT_API_KEY", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", os.urandom(32).hex())
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DEFAULT_CACHE_TTL = int(os.getenv("DEFAULT_CACHE_TTL", "60"))