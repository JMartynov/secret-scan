import json
import os
import hashlib

CACHE_FILE = ".secretscan_cache"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception:
        pass

def is_commit_clean(sha, cache):
    return cache.get(sha) == "clean"

def mark_commit_clean(sha, cache):
    cache[sha] = "clean"
