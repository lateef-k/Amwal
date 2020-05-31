import json
from pathlib import Path
from cachetools import LRUCache
from sqlitedict import SqliteDict

from amwal.log import logger


class MemoryCache(LRUCache):
    enabled = True

    def __repr__(self):
        return f"MemoryCache"


class JsonCache:

    enabled = True
    __slots__ = ("_cache_path", "_serialize", "_deserialize", "_file_extension")

    def __init__(self, cache_path="amwal_cache"):
        self._cache_path = Path(cache_path)
        self._serialize = json.dumps
        self._deserialize = json.loads
        self._file_extension = ".json"

    def __repr__(self):
        return f"DiskCache {self._cache_path}"

    def __getitem__(self, key):
        with (self._cache_path / (key + self._file_extension)).open() as file:
            logger.info(f"Loaded {key} from disk")
            return self._deserialize(file.read())

    def __setitem__(self, key, value):
        if not self._cache_path.exists():
            self._cache_path.mkdir()
        with (self._cache_path / (key + self._file_extension)).open("w+") as file:
            logger.info(f"Saved {key} to disk")
            file.write(self._serialize(value))

    def __contains__(self, key):
        return bool(list(self._cache_path.glob(key + self._file_extension)))


class SqliteCache(SqliteDict):
    enabled = True


def cached(caches):
    def decorator(func):
        def wrapper(*args, recompute=False, **kwargs):
            val = None
            key = func.__name__
            for arg in args:
                if isinstance(arg, str):
                    key += "_" + arg
                elif isinstance(arg, int):
                    key += "_" + str(arg)
            for cache in caches:
                enabled = cache.__class__.enabled
                if not enabled:
                    continue
                if key in cache and not recompute:
                    logger.debug(f"Cache hit in {cache} for {key}")
                    val = cache[key]
                    break
            if val == None:
                val = func(*args, **kwargs)
            for cache in caches:
                enabled = cache.__class__.enabled
                if not enabled:
                    continue
                if key not in cache or recompute:
                    cache[key] = val
            return val

        return wrapper

    return decorator
