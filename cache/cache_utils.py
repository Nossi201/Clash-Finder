# cache/cache_utils.py
import json, hashlib
from typing import Any, Callable
from functools import wraps
import redis
from config import REDIS_URL

_redis = None
def get_redis():
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis

def _make_key(ns: str, *parts: Any) -> str:
    raw = ns + "|" + "|".join(map(lambda x: json.dumps(x, sort_keys=True, default=str), parts))
    return "app:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

def redis_cached(ns: str, ttl: int):
    """Simple Redis-backed caching by function args."""
    def deco(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            r = get_redis()
            key = _make_key(ns, args, kwargs)
            val = r.get(key)
            if val is not None:
                return json.loads(val)
            res = fn(*args, **kwargs)
            try:
                r.setex(key, ttl, json.dumps(res, default=str))
            except Exception:
                pass
            return res
        return wrapper
    return deco
