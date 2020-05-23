import json
from pathlib import Path

from amwal.log import logger
from amwal.exceptions import DontCacheException

from cachetools import LRUCache,keys


class DiskCache:

    def __init__(
        self, cache_path="amwal_cache"
    ):
        self._cache_path = Path(cache_path)
        self._serialize = json.dumps
        self._deserialize = json.loads
        self._file_extension = ".json"
        self.enabled = True

    def __repr__(self):
      return f"DiskCache {self._cache_path}"

    def __getitem__(self, key):
        if not self.enabled:
            return None
        if not self._cache_path.exists():
            self._cache_path.mkdir()
        if not list(self._cache_path.glob(key + self._file_extension)):
            logger.info(f"Cache miss for {key}")
            return None
        with (self._cache_path / (key + self._file_extension)).open() as file:
            logger.info(f"Cache hit for {key}")
            return self._deserialize(file.read())

    def __setitem__(self, key,value):
        if not self.enabled:
            return
        with (self._cache_path / (key + self._file_extension)).open("w+") as file:
            logger.info(f"Add {key} to cache")
            file.write(self._serialize(value))

def cached_recomputable(cache, key=keys.hashkey):
    def decorator(func):
        def wrapper(*args, **kwargs):
            k = key(*args, **kwargs)
            if "recompute" not in kwargs or not kwargs['recompute']:
                try:
                    return cache[k]
                except KeyError:
                    pass  # key not found
            try: 
                v = func(*args, **kwargs)
            except DontCacheException:
                pass
            else:
                cache[k] = v
                return v
        return wrapper
    return decorator